# whitelist.py — vulture false-positive suppressions for the template skeleton.
# Regenerate candidates with: uv run vulture src/cli_app/ --make-whitelist
# ruff: noqa: F821, B018
from cli_app.cli.callbacks.meta import summary_cb
from cli_app.cli.commands.command import console, log
from cli_app.utils.emoji import Emoji
from cli_app.utils.output import render_output
from cli_app.utils.stdin import iter_stdin_lines, read_stdin

summary_cb  # template callback — wire to app.py when needed

console  # template boilerplate in example command
log  # template boilerplate in example command

_.argument  # template parameter in example_command
_.option  # template parameter in example_command

render_output  # output helper — used by commands
read_stdin  # stdin helper — used by commands
iter_stdin_lines  # stdin helper — used by commands

Emoji.ROCKET
Emoji.STOP_SIGN
Emoji.SUNGLASSES
Emoji.PRAY
