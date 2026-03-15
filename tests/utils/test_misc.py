from pathlib import Path

from cli_app.utils.misc import find_project_root


def test_find_project_root_returns_path() -> None:
    root = find_project_root()
    assert isinstance(root, Path)


def test_find_project_root_contains_pyproject_toml() -> None:
    root = find_project_root()
    assert (root / "pyproject.toml").exists()


def test_find_project_root_unknown_marker_returns_path() -> None:
    # When no ancestor has the marker, falls back to file's parent directory.
    root = find_project_root(marker="_nonexistent_marker_xyz_")
    assert isinstance(root, Path)
