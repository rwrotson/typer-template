from functools import cache

from rich.style import Style
from rich.theme import Theme


@cache
def get_theme() -> Theme:
    return Theme(
        {
            "info": Style(
                color="dim cyan",
                blink=True,
                bold=True,
            ),
            "warning": Style(
                color="magenta",
                blink=True,
                bold=True,
            ),
            "danger": Style(
                color="red",
                blink=True,
                bold=True,
            ),
        }
    )
