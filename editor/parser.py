"""Markdown parsing and document analysis utilities."""

from __future__ import annotations
import re
from typing import Dict, List, Tuple
import markdown


DEFAULT_CSS = """
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    line-height: 1.6;
    color: #24292e;
    max-width: 860px;
    margin: 40px auto;
    padding: 0 20px;
}
pre, code {
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    background-color: #f6f8fa;
    border-radius: 4px;
}
code { padding: 0.2em 0.4em; font-size: 85%; }
pre { padding: 16px; overflow: auto; }
blockquote {
    margin: 0;
    padding: 0 1em;
    color: #6a737d;
    border-left: 0.25em solid #dfe2e5;
}
table {
    border-collapse: collapse;
    width: 100%;
    margin: 16px 0;
}
table th, table td {
    border: 1px solid #dfe2e5;
    padding: 6px 13px;
}
table tr:nth-child(2n) { background-color: #f6f8fa; }
h1, h2 { border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
"""


def calculate_stats(text: str) -> Dict[str, int]:
    """Calculate basic text metrics (words, chars, lines, reading time)."""
    words = re.findall(r"\b\w+\b", text)
    word_count = len(words)
    char_count = len(text)
    lines = text.splitlines()
    line_count = len(lines) if text else 0
    # Average reading speed is ~200 words per minute
    reading_time_mins = max(1, (word_count + 199) // 200) if word_count > 0 else 0

    return {
        "words": word_count,
        "characters": char_count,
        "lines": line_count,
        "read_time_mins": reading_time_mins,
    }


def extract_toc(text: str) -> List[Tuple[int, str]]:
    """Extract Table of Contents as list of (heading_level, title)."""
    toc = []
    for line in text.splitlines():
        match = re.match(r"^(#{1,6})\s+(.+)$", line.strip())
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            toc.append((level, title))
    return toc


def to_html(text: str, standalone: bool = True, title: str = "Document") -> str:
    """Convert markdown string to HTML."""
    md = markdown.Markdown(extensions=["extra", "nl2br", "sane_lists"])
    body = md.convert(text)
    if not standalone:
        return body

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>{DEFAULT_CSS}</style>
</head>
<body>
{body}
</body>
</html>"""
