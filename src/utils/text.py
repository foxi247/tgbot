from __future__ import annotations


def escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def truncate(text: str, max_len: int = 200, suffix: str = "…") -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len].rstrip() + suffix
