"""Entry point for PyMark: Markdown Editor & Document Processor."""

import argparse
import sys
from pathlib import Path
from editor.file_manager import FileManager
from editor.parser import calculate_stats


def run_cli(args: argparse.Namespace) -> int:
    """Handle headless CLI flags (stats or export) without opening GUI."""
    input_path = Path(args.file)
    if not input_path.exists():
        print(f"Error: File '{input_path}' not found.", file=sys.stderr)
        return 1

    content = input_path.read_text(encoding="utf-8")
    mgr = FileManager(input_path)

    if args.stats:
        stats = calculate_stats(content)
        print(f"Document: {input_path.name}")
        print(f"- Words:        {stats['words']}")
        print(f"- Characters:   {stats['characters']}")
        print(f"- Lines:        {stats['lines']}")
        print(f"- Est. Reading: {stats['read_time_mins']} min(s)")

    if args.export:
        out = mgr.export_html(content, args.export)
        print(f"Exported HTML to: {out}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="PyMark - Desktop Markdown Editor & CLI Tool")
    parser.add_argument("file", nargs="?", help="Markdown file to open or process")
    parser.add_argument("--stats", action="store_true", help="Print document metrics without GUI")
    parser.add_argument("--export", metavar="OUTPUT_HTML", help="Convert input to HTML file and exit")
    parser.add_argument("--no-gui", action="store_true", help="Do not launch GUI")

    args = parser.parse_args()

    if args.stats or args.export or args.no_gui:
        if not args.file:
            print("Error: A markdown file must be provided for CLI operations.", file=sys.stderr)
            return 1
        return run_cli(args)

    # Launch Desktop GUI
    from editor.ui import MarkdownEditorApp

    app = MarkdownEditorApp(initial_path=args.file)
    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
