from rich.style import Style
from rich.theme import Theme

from cli_app.utils.format import get_theme


def test_get_theme_returns_theme() -> None:
    assert isinstance(get_theme(), Theme)


def test_get_theme_has_info_warning_danger() -> None:
    styles = get_theme().styles
    assert "info" in styles
    assert "warning" in styles
    assert "danger" in styles


def test_get_theme_styles_are_style_instances() -> None:
    styles = get_theme().styles
    for name in ("info", "warning", "danger"):
        assert isinstance(styles[name], Style)


def test_get_theme_is_cached() -> None:
    assert get_theme() is get_theme()
