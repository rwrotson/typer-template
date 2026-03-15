import io
import sys

import pytest

from cli_app.utils.stdin import (
    is_stdin_piped,
    iter_stdin_lines,
    read_stdin,
    read_stdin_if_piped,
)


def test_is_stdin_piped_returns_false_for_tty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    assert is_stdin_piped() is False


def test_is_stdin_piped_returns_true_for_pipe(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    assert is_stdin_piped() is True


def test_read_stdin(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("hello world"))
    assert read_stdin() == "hello world"


def test_iter_stdin_lines(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("line1\nline2\nline3\n"))
    lines = list(iter_stdin_lines())
    assert lines == ["line1", "line2", "line3"]


def test_read_stdin_if_piped_returns_content_when_piped(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("piped content"))
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    result = read_stdin_if_piped()
    assert result == "piped content"


def test_read_stdin_if_piped_returns_none_for_tty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    assert read_stdin_if_piped() is None
