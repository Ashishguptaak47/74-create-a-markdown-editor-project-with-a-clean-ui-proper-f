"""Unit test suite for parsing, file management, and CLI operations."""

import tempfile
from pathlib import Path
import pytest
from editor.file_manager import FileManager
from editor.parser import calculate_stats, extract_toc, to_html
from main import run_cli
import argparse


SAMPLE_MD = """# Main Title

Welcome to **PyMark**. Here is a [link](https://python.org).

## Sub Heading

- Point 1
- Point 2

> Quotation block

```python
print('code')
```
"""


def test_calculate_stats():
    stats = calculate_stats(SAMPLE_MD)
    assert stats["words"] > 10
    assert stats["characters"] > 50
    assert stats["lines"] >= 10
    assert stats["read_time_mins"] >= 1


def test_extract_toc():
    toc = extract_toc(SAMPLE_MD)
    assert len(toc) == 2
    assert toc[0] == (1, "Main Title")
    assert toc[1] == (2, "Sub Heading")


def test_to_html():
    html = to_html(SAMPLE_MD, standalone=True, title="Test Doc")
    assert "<!DOCTYPE html>" in html
    assert "<title>Test Doc</title>" in html
    assert "<h1>Main Title</h1>" in html
    assert "<strong>PyMark</strong>" in html


def test_file_manager_save_and_load(tmp_path: Path):
    mgr = FileManager()
    file_path = tmp_path / "doc.md"
    content = "# Saved Content\n\nTest line."

    saved = mgr.save(content, file_path)
    assert saved.exists()
    assert mgr.is_dirty is False

    loaded = mgr.load(file_path)
    assert loaded == content
    assert mgr.current_file == file_path.resolve()


def test_file_manager_export_html(tmp_path: Path):
    mgr = FileManager()
    html_path = tmp_path / "export.html"
    mgr.export_html("# Export Test", html_path)

    assert html_path.exists()
    text = html_path.read_text(encoding="utf-8")
    assert "<h1>Export Test</h1>" in text


def test_cli_stats(capsys, tmp_path: Path):
    doc = tmp_path / "test.md"
    doc.write_text("# CLI Title\nWord one word two.", encoding="utf-8")

    args = argparse.Namespace(file=str(doc), stats=True, export=None, no_gui=True)
    ret = run_cli(args)
    assert ret == 0

    captured = capsys.readouterr()
    assert "Words:" in captured.out
    assert "Document: test.md" in captured.out


def test_cli_export(tmp_path: Path):
    doc = tmp_path / "test.md"
    doc.write_text("# Convert\nThis is a test.", encoding="utf-8")
    out_html = tmp_path / "converted.html"

    args = argparse.Namespace(file=str(doc), stats=False, export=str(out_html), no_gui=True)
    ret = run_cli(args)
    assert ret == 0
    assert out_html.exists()
    assert "<h1>Convert</h1>" in out_html.read_text(encoding="utf-8")
