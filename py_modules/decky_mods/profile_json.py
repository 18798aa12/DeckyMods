"""Bounded manifest JSON with inert comments and unambiguous object keys."""

import json

from .errors import ModsError


def _without_comments(text: str) -> str:
    output = []
    index, quoted, escaped = 0, False, False
    while index < len(text):
        char = text[index]
        if quoted:
            output.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
            index += 1
        elif char == '"':
            output.append(char)
            quoted = True
            index += 1
        elif text.startswith("//", index):
            end = text.find("\n", index + 2)
            index = len(text) if end < 0 else end
            output.append(" ")
        elif text.startswith("/*", index):
            end = text.find("*/", index + 2)
            if end < 0:
                raise ValueError("Unterminated manifest comment")
            output.append(" ")
            index = end + 2
        else:
            output.append(char)
            index += 1
    return "".join(output)


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate manifest key")
        result[key] = value
    return result


def _invalid_constant(_value: str) -> None:
    raise ValueError("Non-finite JSON number")


def manifest_object(raw: bytes) -> dict:
    """Read UTF-8 JSON comments without evaluating code or changing the source."""
    try:
        value = json.loads(
            _without_comments(raw.decode("utf-8-sig")),
            object_pairs_hook=_unique_object,
            parse_constant=_invalid_constant,
        )
        if not isinstance(value, dict):
            raise ValueError("Manifest is not an object")
        return value
    except (ValueError, UnicodeError, RecursionError):
        raise ModsError("SMAPI 清单 JSON 无效、注释未闭合或包含重复键") from None
