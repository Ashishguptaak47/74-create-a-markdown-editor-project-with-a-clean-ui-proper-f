"""File operations and auto-save management."""

from __future__ import annotations
from pathlib import Path
from typing import Optional
from editor.parser import to_html


class FileManager:
    """Handles document persistence, recent states, and export actions."""

    def __init__(self, current_file: Optional[Path] = None):
        self.current_file: Optional[Path] = current_file
        self.is_dirty: bool = False

    def load(self, path: str | Path) -> str:
        """Read file contents and track current target."""
        p = Path(path).resolve()
        content = p.read_text(encoding="utf-8")
        self.current_file = p
        self.is_dirty = False
        return content

    def save(self, content: str, path: Optional[str | Path] = None) -> Path:
        """Save markdown text to disk."""
        target = Path(path).resolve() if path else self.current_file
        if not target:
            raise ValueError("No file path provided to save.")

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        self.current_file = target
        self.is_dirty = False
        return target

    def export_html(self, content: str, target_path: str | Path) -> Path:
        """Export markdown content as styled standalone HTML."""
        target = Path(target_path).resolve()
        title = self.current_file.stem if self.current_file else "Exported Document"
        html_data = to_html(content, standalone=True, title=title)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html_data, encoding="utf-8")
        return target
