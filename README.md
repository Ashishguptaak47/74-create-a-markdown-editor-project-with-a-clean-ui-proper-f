# PyMark: Desktop Markdown Editor

A lightweight, distraction-free Markdown Editor built with Python and Tkinter. Features real-time split-pane preview, syntax highlighting, document statistics, table-of-contents extraction, and one-click HTML export.

## Features

- **Live Split-Pane Rendering**: Write on the left, inspect formatted output on the right.
- **Syntax Colorization**: Real-time highlighting for headings, bold, italic, code blocks, blockquotes, and links.
- **Document Analytics**: Real-time word count, character count, line count, and estimated reading time.
- **HTML Export**: Export styled standalone HTML documents with clean typography.
- **CLI Conversion Mode**: Headless Markdown-to-HTML conversion suitable for pipelines.
- **Minimal Dependencies**: Runs with standard library Tkinter and the `markdown` package.

## Installation

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

### Graphical User Interface

Launch the editor:

```bash
python main.py
```

Open a specific file directly:

```bash
python main.py path/to/document.md
```

### Headless CLI Mode

Convert markdown files to standalone HTML without opening the GUI:

```bash
python main.py input.md --export output.html
```

View document statistics via CLI:

```bash
python main.py input.md --stats
```

## Running Tests

```bash
pytest
```
