"""Small, strict reader for Steam's quoted-text KeyValues manifests."""

from __future__ import annotations

import re
from pathlib import Path

_TOKEN = re.compile(r'\s+|//[^\n]*(?:\n|$)|"(?:[^"\\]|\\.)*"|[{}]')


def read_vdf(path: Path) -> dict:
    """Read ordinary Steam KeyValues without interpreting code or arbitrary escapes."""
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 2 * 1024 * 1024:
        raise ValueError("unsafe Steam manifest")
    text = path.read_text(encoding="utf-8-sig")
    tokens: list[str] = []
    offset = 0
    for match in _TOKEN.finditer(text):
        if match.start() != offset:
            raise ValueError("invalid Steam manifest")
        token = match.group()
        offset = match.end()
        if not token.isspace() and not token.startswith("//"):
            tokens.append(token)
    if offset != len(text):
        raise ValueError("invalid Steam manifest")
    index = 0

    def quoted(token: str) -> str:
        if not token.startswith('"'):
            raise ValueError("expected quoted string")
        return re.sub(r'\\([\\"])', r"\1", token[1:-1])

    def parse(nested: bool = False, depth: int = 0) -> dict:
        nonlocal index
        if depth > 12:
            raise ValueError("Steam manifest too deep")
        result: dict = {}
        while index < len(tokens):
            token = tokens[index]
            index += 1
            if token == "}":
                if not nested:
                    raise ValueError("unexpected closing brace")
                return result
            key = quoted(token)
            if index >= len(tokens) or key in result:
                raise ValueError("missing or duplicate value")
            value = tokens[index]
            index += 1
            result[key] = parse(True, depth + 1) if value == "{" else quoted(value)
        if nested:
            raise ValueError("unclosed Steam manifest")
        return result

    return parse()
