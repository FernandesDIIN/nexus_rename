from pathlib import Path


class AlignmentModel:
    """Small, UI-independent model for instant destination reordering."""

    def __init__(self, mapping):
        self.origins = [Path(origin) if origin else None for origin, _ in mapping]
        self.destinations = [Path(destination) if destination else None for _, destination in mapping]
        self._undo_stack: list[tuple[int, int]] = []

    def __len__(self) -> int:
        return len(self.origins)

    def pair(self, index: int):
        return self.origins[index], self.destinations[index]

    def swap(self, first: int, second: int, *, remember: bool = True) -> None:
        if first == second:
            return
        self.destinations[first], self.destinations[second] = (
            self.destinations[second],
            self.destinations[first],
        )
        if remember:
            self._undo_stack.append((first, second))

    def undo(self) -> tuple[int, int] | None:
        if not self._undo_stack:
            return None
        first, second = self._undo_stack.pop()
        self.swap(first, second, remember=False)
        return first, second

    @property
    def can_undo(self) -> bool:
        return bool(self._undo_stack)

    def final_mapping(self) -> list[tuple[str, str]]:
        result = []
        for origin, destination in zip(self.origins, self.destinations):
            if origin and destination:
                result.append((str(destination), str(destination.parent / origin.name)))
        return result
