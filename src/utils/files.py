from pathlib import Path


def read_from_file(path: Path) -> bytes:
    with path.open(mode="rb", encoding="utf-8") as file:
        return file.read()
