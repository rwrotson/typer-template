import pytest
from rich.progress import Progress

from cli_app.utils.console import get_console
from cli_app.utils.progress import generate_progress_bar


def test_generate_progress_bar_returns_progress_instance() -> None:
    bar = generate_progress_bar()
    assert isinstance(bar, Progress)


def test_generate_progress_bar_project_console_uses_shared_console() -> None:
    bar = generate_progress_bar(console="project")
    assert bar.console is get_console()


def test_generate_progress_bar_internal_console_does_not_use_shared_console() -> None:
    bar = generate_progress_bar(console="internal")
    assert isinstance(bar, Progress)
    assert bar.console is not get_console()


def test_generate_progress_bar_invalid_console_raises() -> None:
    with pytest.raises(RuntimeError, match="Incorrect console type"):
        generate_progress_bar(console="invalid")  # type: ignore[arg-type]
