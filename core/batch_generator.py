import re
from pathlib import Path
from datetime import datetime

INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
RESERVED_NAMES = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}


def _validate_name(name: str) -> None:
    if not name or name in {".", ".."}:
        raise ValueError("O padrão gera um nome vazio ou inválido.")
    if INVALID_FILENAME_CHARS.search(name) or name.endswith((" ", ".")):
        raise ValueError(f'O padrão gera um nome inválido no Windows: "{name}".')
    if name.split(".", 1)[0].upper() in RESERVED_NAMES:
        raise ValueError(f'O nome "{name}" é reservado pelo Windows.')

def generate_batch_mapping(
    files: list[Path],
    pattern: str,
    start_index: int = 1,
    increment: int = 1,
) -> list[tuple[str, str]]:
    """
    Gera o mapeamento de renomeação baseado em padrões de string digitados pelo usuário.
    Suporta wildcards como #, ##, [NOME] e [DATA].
    Agora substitui TODOS os blocos de '#' encontrados no padrão (ex: "##_Projeto_##").
    """
    pattern = pattern.strip()
    if not pattern:
        raise ValueError("Informe um padrão de nome.")
    if start_index < 0:
        raise ValueError("O índice inicial não pode ser negativo.")
    if increment == 0:
        raise ValueError("O incremento não pode ser zero.")
    if not files:
        raise ValueError("A pasta não contém imagens válidas.")
    mapping = []
    current_index = start_index
    today_str = datetime.now().strftime("%Y%m%d")

    for file_path in files:
        new_name = pattern

        # 1. Substituição de Tags Estáticas
        new_name = new_name.replace("[NOME]", file_path.stem)
        new_name = new_name.replace("[DATA]", today_str)
        new_name = new_name.replace("[PASTA]", file_path.parent.name)
        new_name = new_name.replace("[EXT]", file_path.suffix.lstrip(".").lower())
        if "[MODIFICADO]" in new_name:
            modified_str = datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y%m%d")
            new_name = new_name.replace("[MODIFICADO]", modified_str)

        # 2. Substituição de todos os blocos de '#'
        # Encontra cada sequência de # e substitui pelo número atual com o mesmo padding
        new_name = re.sub(r'#+', lambda m: str(current_index).zfill(len(m.group())), new_name)
        _validate_name(new_name)

        # 3. Montagem do Caminho Final
        new_dest_path = file_path.parent / f"{new_name}{file_path.suffix}"
        
        mapping.append((str(file_path), str(new_dest_path)))
        
        current_index += increment

    return mapping
