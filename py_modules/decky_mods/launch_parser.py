"""Parse a deliberately small, literal subset of Steam's shell launch syntax."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .errors import ModsError

_ASSIGNMENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=")
_ENTRY = re.compile(r"([A-Za-z0-9_.-]+)=([A-Za-z]+(?:,[A-Za-z]+)*)")
_WRAPPERS = {"mangohud", "gamemoderun"}
_REQUIRED = "dinput8.dll=n,b"
_ERROR = "启动选项含复杂命令、重复配置或不兼容 DLL 设置，请先手动检查；原设置未更改。"


@dataclass(frozen=True)
class _Token:
    start: int
    end: int
    raw: str
    value: str


def validate_text(value: str) -> None:
    """Reject oversized and control-character input before storing private options."""
    try:
        valid = (
            isinstance(value, str)
            and len(value.encode("utf-8")) <= 16384
            and not any(ord(char) < 32 or ord(char) == 127 for char in value)
        )
    except UnicodeError:
        valid = False
    if not valid:
        raise ModsError("启动选项文本无效，请在 Steam 属性中检查设置。")


def _tokens(text: str) -> list[_Token]:
    result: list[_Token] = []
    index = 0
    while index < len(text):
        if text[index] == " ":
            index += 1
            continue
        start = index
        quote = ""
        decoded: list[str] = []
        while index < len(text):
            char = text[index]
            if char in "$`\\":
                raise ModsError(_ERROR)
            if quote:
                if char == quote:
                    quote = ""
                else:
                    decoded.append(char)
            elif char in "\"'":
                quote = char
            elif char == " ":
                break
            elif char in ";|&<>(){}[]*?!#~":
                raise ModsError(_ERROR)
            else:
                decoded.append(char)
            index += 1
        if quote:
            raise ModsError(_ERROR)
        result.append(_Token(start, index, text[start:index], "".join(decoded)))
    return result


def _override(token: _Token) -> str:
    raw = token.raw.removeprefix("WINEDLLOVERRIDES=")
    quote = raw[:1] if raw[:1] in {"'", '"'} else ""
    if quote:
        if len(raw) < 2 or not raw.endswith(quote) or quote in raw[1:-1]:
            raise ModsError(_ERROR)
        value = raw[1:-1]
    else:
        if "'" in raw or '"' in raw:
            raise ModsError(_ERROR)
        value = raw
    aliases: set[str] = set()
    compatible = False
    for entry in value.split(";") if value else []:
        match = _ENTRY.fullmatch(entry)
        if match is None:
            raise ModsError(_ERROR)
        name, modes = match.groups()
        alias = name.lower().removesuffix(".dll")
        if alias in aliases:
            raise ModsError(_ERROR)
        aliases.add(alias)
        if alias == "dinput8":
            if modes.lower() not in {"n,b", "native,builtin"}:
                raise ModsError(_ERROR)
            compatible = True
    if compatible:
        return token.raw
    updated = value + (";" if value else "") + _REQUIRED
    delimiter = quote or '"'
    return f"WINEDLLOVERRIDES={delimiter}{updated}{delimiter}"


def merge_options(current: str) -> str:
    """Add the reviewed REFramework DLL override, retaining all other bytes."""
    validate_text(current)
    if not current.strip():
        return f'WINEDLLOVERRIDES="{_REQUIRED}" %command%{current}'
    tokens = _tokens(current)
    commands = [token for token in tokens if token.value == "%command%"]
    if len(commands) != 1 or commands[0].raw != "%command%" or current.count("%command%") != 1:
        raise ModsError("未找到唯一的 %command% 占位符，请先在 Steam 属性中检查启动选项。")
    command = commands[0]
    if any(
        token.value.startswith("WINEDLLOVERRIDES=") and token.start > command.start
        for token in tokens
    ):
        raise ModsError(_ERROR)
    prefix = [token for token in tokens if token.start < command.start]
    if prefix and prefix[0].raw == "env":
        prefix = prefix[1:]
    insertion = command.start
    wrappers = False
    assignment: _Token | None = None
    for token in prefix:
        if token.raw in _WRAPPERS:
            if not wrappers:
                insertion = token.start
            wrappers = True
        elif not wrappers and _ASSIGNMENT.match(token.raw):
            if token.raw.startswith("WINEDLLOVERRIDES="):
                if assignment is not None:
                    raise ModsError(_ERROR)
                assignment = token
        else:
            raise ModsError(_ERROR)
    if assignment is not None:
        replacement = _override(assignment)
        return current[: assignment.start] + replacement + current[assignment.end :]
    return current[:insertion] + f'WINEDLLOVERRIDES="{_REQUIRED}" ' + current[insertion:]
