"""Real-time markdown syntax highlighting for Tkinter Text widget."""

import re
import tkinter as tk


class MarkdownHighlighter:
    """Applies tag styles and highlights markdown patterns in Tkinter Text."""

    STYLES = {
        "h1": {"font": ("Helvetica", 16, "bold"), "foreground": "#1f2328"},
        "h2": {"font": ("Helvetica", 14, "bold"), "foreground": "#24292f"},
        "h3": {"font": ("Helvetica", 12, "bold"), "foreground": "#32383f"},
        "bold": {"font": ("Helvetica", 11, "bold")},
        "italic": {"font": ("Helvetica", 11, "italic")},
        "code": {"font": ("Courier", 10), "background": "#f0f2f5"},
        "quote": {"foreground": "#57606a", "font": ("Helvetica", 11, "italic")},
        "bullet": {"foreground": "#0969da", "font": ("Helvetica", 11, "bold")},
        "link": {"foreground": "#0969da", "underline": True},
    }

    PATTERNS = [
        ("h1", r"^#\s+.*$"),
        ("h2", r"^##\s+.*$"),
        ("h3", r"^###\s+.*$"),
        ("quote", r"^>\s+.*$"),
        ("bullet", r"^\s*[-*+]\s+"),
        ("bold", r"(\*\*|__)(.*?)\1"),
        ("italic", r"(\*|_)(.*?)\1"),
        ("code", r"(`+)(.*?)\1"),
        ("link", r"\[[^\]]+\]\([^\)]+\)"),
    ]

    def __init__(self, text_widget: tk.Text):
        self.text_widget = text_widget
        self._setup_tags()

    def _setup_tags(self) -> None:
        for tag, kwargs in self.STYLES.items():
            self.text_widget.tag_configure(tag, **kwargs)

    def highlight(self) -> None:
        """Scan and highlight tokens across entire text widget."""
        for tag in self.STYLES:
            self.text_widget.tag_remove(tag, "1.0", tk.END)

        content = self.text_widget.get("1.0", tk.END)
        lines = content.splitlines()

        # Line-level patterns (headers, quotes, bullets)
        for line_idx, line in enumerate(lines, start=1):
            for tag, regex in self.PATTERNS[:5]:
                match = re.match(regex, line)
                if match:
                    start = f"{line_idx}.{match.start()}"
                    end = f"{line_idx}.{match.end()}"
                    self.text_widget.tag_add(tag, start, end)
                    break

        # Inline patterns (bold, italic, code, link)
        for tag, regex in self.PATTERNS[5:]:
            for match in re.finditer(regex, content):
                start = f"1.0 + {match.start()} chars"
                end = f"1.0 + {match.end()} chars"
                self.text_widget.tag_add(tag, start, end)
