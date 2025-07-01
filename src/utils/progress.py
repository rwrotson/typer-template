from typing import Callable, Literal, Sequence

from rich.console import Console
from rich.progress import Progress, ProgressColumn

from utils.console import get_console


def generate_progress_bar(
    *columns: Sequence[str | ProgressColumn],
    console: Literal["internal", "project"] | Console = "project",
    auto_refresh: bool = True,
    refresh_per_second: float = 1,
    speed_estimate_period: float = 30.0,
    transient: bool = False,
    redirect_stdout: bool = True,
    redirect_stderr: bool = True,
    get_time: Callable[[], float] | None = None,
    disable: bool = False,
    expand: bool = False,
    **kwargs,
) -> Progress:
    if console == "project":
        console = get_console()
    elif console == "internal":
        console = None
    else:
        raise RuntimeError()

    console: Console | None
    return Progress(
        *columns,
        console=console,
        auto_refresh=auto_refresh,
        refresh_per_second=refresh_per_second,
        speed_estimate_period=speed_estimate_period,
        transient=transient,
        redirect_stdout=redirect_stdout,
        redirect_stderr=redirect_stderr,
        get_time=get_time,
        disable=disable,
        expand=expand,
    )
