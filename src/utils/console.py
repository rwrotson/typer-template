from dataclasses import dataclass
from typing import IO, Callable, Literal, Self

from rich.console import Console, EmojiVariant, HighlighterType, ReprHighlighter, Theme


@dataclass(slots=True, frozen=True)
class ConsoleConfig:
    color_system: Literal["auto", "standard", "256", "truecolor", "windows"] | None = "auto"
    force_terminal: bool | None = None
    force_jupyter: bool | None = None
    force_interactive: bool | None = None
    soft_wrap: bool | None = None
    theme: Theme | None = None
    stderr: bool | None = None
    file: IO[str] | None = None
    quiet: bool | None = None
    width: int | None = None
    height: int | None = None
    style: str | None = None
    no_color: bool | None = None
    tab_size: int | None = None
    record: bool | None = None
    markup: bool | None = None
    emoji: bool | None = None
    emoji_variant: EmojiVariant | None = None
    highlight: bool | None = None
    log_time: bool | None = None
    log_path: bool | None = None
    highlighter: HighlighterType | None = ReprHighlighter()
    legacy_windows: bool | None = None
    safe_box: bool | None = True
    get_datetime: Callable[[], float] | None = None

    @classmethod
    def from_env_file(cls) -> Self:
        pass

    @classmethod
    def from_env(cls) -> Self:
        pass

    def merge(self, other: Self) -> Self:
        return self.__class__()


console = Console()

def create_console():
    global console
    config = ConsoleConfig.from_env()
    console = Console()

def get_console() -> Console:
    return console
