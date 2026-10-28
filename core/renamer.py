import json
import os
import uuid
from pathlib import Path


def _path_key(path: Path) -> str:
    """Return a comparison key that also behaves correctly on Windows."""
    return os.path.normcase(os.path.abspath(path))


def _same_spelling(first: Path, second: Path) -> bool:
    """Distinguish a no-op from a case-only rename on case-insensitive systems."""
    return os.path.abspath(first) == os.path.abspath(second)


def _available_path(requested: Path, reserved: set[str]) -> Path:
    candidate = requested
    counter = 1
    while candidate.exists() or _path_key(candidate) in reserved:
        candidate = requested.with_name(f"{requested.stem}_{counter}{requested.suffix}")
        counter += 1
    return candidate


def execute_rename(aligned_mapping: list[tuple[str | None, str | None]]) -> tuple[dict, list[tuple[str, str]]]:
    """Rename files safely, including swaps and other rename cycles.

    Every source is first moved to a unique temporary name. Only after that succeeds
    are the final names applied. This prevents a file renamed earlier in the batch
    from occupying a name needed by a later file.
    """
    results = {"success": 0, "skipped": 0, "errors": []}
    prepared: list[tuple[Path, Path]] = []
    source_keys: set[str] = set()
    requested_keys: set[str] = set()

    for source_value, target_value in aligned_mapping:
        if not source_value or not target_value:
            results["skipped"] += 1
            continue
        source = Path(source_value)
        target = Path(target_value)
        source_key = _path_key(source)
        target_key = _path_key(target)
        if source_key in source_keys:
            results["errors"].append(f"Arquivo repetido na operação: {source.name}")
            continue
        if target_key in requested_keys:
            results["errors"].append(f"Nome de destino duplicado: {target.name}")
            continue
        if not source.is_file():
            results["errors"].append(f"Arquivo não encontrado: {source.name}")
            continue
        source_keys.add(source_key)
        requested_keys.add(target_key)
        prepared.append((source, target))

    if results["errors"]:
        return results, []

    # Existing files that are themselves part of this batch will be vacated in phase 1.
    reserved = set(requested_keys)
    final_pairs: list[tuple[Path, Path]] = []
    for source, requested in prepared:
        if _same_spelling(source, requested):
            final_pairs.append((source, source))
            continue
        if requested.exists() and _path_key(requested) not in source_keys:
            target = _available_path(requested, reserved)
            reserved.add(_path_key(target))
        else:
            target = requested
        final_pairs.append((source, target))

    staged: list[tuple[Path, Path, Path]] = []
    try:
        for source, target in final_pairs:
            if _same_spelling(source, target):
                continue
            temporary = source.with_name(f".nexusrename-{uuid.uuid4().hex}.tmp")
            os.replace(source, temporary)
            staged.append((source, temporary, target))
    except OSError as exc:
        for source, temporary, _ in reversed(staged):
            try:
                os.replace(temporary, source)
            except OSError:
                pass
        results["errors"].append(f"Não foi possível preparar a renomeação: {exc}")
        return results, []

    completed: list[tuple[Path, Path]] = []
    try:
        staged_by_source = {_path_key(source): (source, temporary, target) for source, temporary, target in staged}
        for source, target in final_pairs:
            if _same_spelling(source, target):
                completed.append((source, target))
                continue
            _, temporary, target = staged_by_source[_path_key(source)]
            target.parent.mkdir(parents=True, exist_ok=True)
            os.replace(temporary, target)
            completed.append((source, target))
    except OSError as exc:
        # Best-effort restoration of both completed and still staged entries.
        for source, target in reversed(completed):
            if not _same_spelling(source, target) and target.exists():
                try:
                    os.replace(target, source)
                except OSError:
                    pass
        for source, temporary, _ in reversed(staged):
            if temporary.exists():
                try:
                    os.replace(temporary, source)
                except OSError:
                    pass
        results["errors"].append(f"A operação foi revertida após uma falha: {exc}")
        return results, []

    real_pairs = [(str(source), str(target)) for source, target in completed]
    results["success"] = len(real_pairs)
    return results, real_pairs


def execute_rollback(log_file_path: str) -> dict:
    """Reverse a logged operation using the same cycle-safe rename engine."""
    results = {"success": 0, "skipped": 0, "errors": []}
    try:
        with open(log_file_path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        history = data.get("history")
        if not isinstance(history, dict) or not history:
            raise ValueError("o log não contém um histórico válido")
        mapping = [(current, original) for current, original in reversed(list(history.items()))]
        rename_results, _ = execute_rename(mapping)
        results.update(rename_results)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        results["errors"].append(f"Erro ao ler o arquivo de log: {exc}")
    return results
