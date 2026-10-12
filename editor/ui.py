"""Desktop UI built with Tkinter for markdown editing and preview."""

from __future__ import annotations
import re
import tempfile
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from editor.file_manager import FileManager
from editor.highlighter import MarkdownHighlighter
from editor.parser import calculate_stats, to_html


class MarkdownEditorApp(tk.Tk):
    """Main application window providing split editor and formatted preview."""

    def __init__(self, initial_path: str | None = None):
        super().__init__()
        self.title("PyMark - Markdown Editor")
        self.geometry("1100x700")
        self.minsize(640, 480)

        self.file_mgr = FileManager()
        self._after_id = None

        self._setup_style()
        self._create_widgets()
        self._setup_menus()
        self._bind_events()

        if initial_path and Path(initial_path).exists():
            self.open_file(initial_path)
        else:
            self._load_sample_text()

    def _setup_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        self.configure(bg="#f6f8fa")

    def _create_widgets(self) -> None:
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=5, pady=3)

        actions = [
            ("Bold", lambda: self._insert_wrapper("**", "**")),
            ("Italic", lambda: self._insert_wrapper("*", "*")),
            ("Heading", lambda: self._insert_line_prefix("# ")),
            ("Quote", lambda: self._insert_line_prefix("> ")),
            ("Code", lambda: self._insert_wrapper("`", "`")),
            ("Link", self._insert_link),
            ("Browser Preview", self.preview_in_browser),
            ("Export HTML", self.export_html),
        ]
        for label, cmd in actions:
            btn = ttk.Button(toolbar, text=label, command=cmd)
            btn.pack(side=tk.LEFT, padx=2)

        # Paned container for split-view
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)

        # Left Pane: Source Editor
        editor_frame = ttk.Frame(paned)
        self.editor = tk.Text(
            editor_frame,
            wrap=tk.WORD,
            undo=True,
            font=("Courier", 11),
            bg="#ffffff",
            fg="#24292f",
            padx=8,
            pady=8,
            relief=tk.FLAT,
        )
        editor_scroll = ttk.Scrollbar(editor_frame, orient=tk.VERTICAL, command=self.editor.yview)
        self.editor.configure(yscrollcommand=editor_scroll.set)
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        editor_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        paned.add(editor_frame, weight=1)

        # Right Pane: Formatted Preview (Rich text rendering)
        preview_frame = ttk.Frame(paned)
        self.preview = tk.Text(
            preview_frame,
            wrap=tk.WORD,
            font=("Helvetica", 11),
            bg="#fafbfc",
            fg="#24292f",
            padx=12,
            pady=8,
            relief=tk.FLAT,
            state=tk.DISABLED,
        )
        preview_scroll = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview.yview)
        self.preview.configure(yscrollcommand=preview_scroll.set)
        self.preview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        paned.add(preview_frame, weight=1)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding=3)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.highlighter = MarkdownHighlighter(self.editor)
        self._setup_preview_tags()

    def _setup_preview_tags(self) -> None:
        self.preview.tag_configure("p_h1", font=("Helvetica", 16, "bold"), spacing3=8, foreground="#1f2328")
        self.preview.tag_configure("p_h2", font=("Helvetica", 14, "bold"), spacing3=6, foreground="#24292f")
        self.preview.tag_configure("p_h3", font=("Helvetica", 12, "bold"), spacing3=4, foreground="#32383f")
        self.preview.tag_configure("p_quote", font=("Helvetica", 10, "italic"), foreground="#57606a", lmargin1=15, lmargin2=15)
        self.preview.tag_configure("p_code", font=("Courier", 10), background="#eff1f3")
        self.preview.tag_configure("p_bold", font=("Helvetica", 11, "bold"))
        self.preview.tag_configure("p_bullet", font=("Helvetica", 11), lmargin1=10, lmargin2=20)

    def _setup_menus(self) -> None:
        menu = tk.Menu(self)
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="New", accelerator="Ctrl+N", command=self.new_file)
        file_menu.add_command(label="Open...", accelerator="Ctrl+O", command=self.open_file_dialog)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_file)
        file_menu.add_command(label="Save As...", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Export HTML...", command=self.export_html)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menu.add_cascade(label="File", menu=file_menu)
        self.config(menu=menu)

    def _bind_events(self) -> None:
        self.editor.bind("<KeyRelease>", self._on_content_changed)
        self.bind("<Control-s>", lambda _: self.save_file())
        self.bind("<Control-o>", lambda _: self.open_file_dialog())
        self.bind("<Control-n>", lambda _: self.new_file())

    def _load_sample_text(self) -> None:
        sample = (
            "# Welcome to PyMark\n\n"
            "PyMark is a **fast** and clean Markdown editor.\n\n"
            "## Features\n"
            "- Real-time split preview\n"
            "- Instant syntax colorization\n"
            "- One-click HTML export\n\n"
            "> Good markdown keeps writing simple.\n\n"
            "```python\n"
            "print('Hello from PyMark!')\n"
            "```\n"
        )
        self.editor.insert("1.0", sample)
        self._refresh_all()

    def _on_content_changed(self, _event: tk.Event | None = None) -> None:
        self.file_mgr.is_dirty = True
        if self._after_id:
            self.after_cancel(self._after_id)
        self._after_id = self.after(150, self._refresh_all)

    def _refresh_all(self) -> None:
        self.highlighter.highlight()
        self._render_preview()
        self._update_status()

    def _render_preview(self) -> None:
        """Render simple markdown tokens into the preview Text widget."""
        text = self.editor.get("1.0", tk.END)
        self.preview.configure(state=tk.NORMAL)
        self.preview.delete("1.0", tk.END)

        for line in text.splitlines():
            clean_line = line.strip()
            if clean_line.startswith("# "):
                self.preview.insert(tk.END, clean_line[2:] + "\n", "p_h1")
            elif clean_line.startswith("## "):
                self.preview.insert(tk.END, clean_line[3:] + "\n", "p_h2")
            elif clean_line.startswith("### "):
                self.preview.insert(tk.END, clean_line[4:] + "\n", "p_h3")
            elif clean_line.startswith("> "):
                self.preview.insert(tk.END, clean_line[2:] + "\n", "p_quote")
            elif clean_line.startswith(("- ", "* ", "+ ")):
                self.preview.insert(tk.END, "• " + clean_line[2:] + "\n", "p_bullet")
            elif clean_line.startswith("```"):
                self.preview.insert(tk.END, "  " + clean_line + "\n", "p_code")
            else:
                # Inline formatting for bold
                parts = re.split(r"(\*\*.*?\*\*)", line)
                for part in parts:
                    if part.startswith("**") and part.endswith("**") and len(part) >= 4:
                        self.preview.insert(tk.END, part[2:-2], "p_bold")
                    else:
                        self.preview.insert(tk.END, part)
                self.preview.insert(tk.END, "\n")

        self.preview.configure(state=tk.DISABLED)

    def _update_status(self) -> None:
        content = self.editor.get("1.0", tk.END).strip()
        stats = calculate_stats(content)
        fname = self.file_mgr.current_file.name if self.file_mgr.current_file else "Untitled"
        status_indicator = "*" if self.file_mgr.is_dirty else ""
        self.status_var.set(
            f"{fname}{status_indicator} | Lines: {stats['lines']} | "
            f"Words: {stats['words']} | Characters: {stats['characters']} | "
            f"Est. Read: ~{stats['read_time_mins']}m"
        )

    def _insert_wrapper(self, prefix: str, suffix: str) -> None:
        try:
            sel_first = self.editor.index(tk.SEL_FIRST)
            sel_last = self.editor.index(tk.SEL_LAST)
            selected = self.editor.get(sel_first, sel_last)
            self.editor.delete(sel_first, sel_last)
            self.editor.insert(sel_first, f"{prefix}{selected}{suffix}")
        except tk.TclError:
            pos = self.editor.index(tk.INSERT)
            self.editor.insert(pos, f"{prefix}{suffix}")
            self.editor.mark_set(tk.INSERT, f"{pos} + {len(prefix)} chars")
        self._on_content_changed()

    def _insert_line_prefix(self, prefix: str) -> None:
        insert_idx = self.editor.index(tk.INSERT)
        line_num = insert_idx.split(".")[0]
        self.editor.insert(f"{line_num}.0", prefix)
        self._on_content_changed()

    def _insert_link(self) -> None:
        self._insert_wrapper("[", "](https://example.com)")

    def new_file(self) -> None:
        self.editor.delete("1.0", tk.END)
        self.file_mgr = FileManager()
        self._refresh_all()

    def open_file_dialog(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("Markdown", "*.md"), ("All Files", "*.*")])
        if path:
            self.open_file(path)

    def open_file(self, path: str) -> None:
        try:
            content = self.file_mgr.load(path)
            self.editor.delete("1.0", tk.END)
            self.editor.insert("1.0", content)
            self._refresh_all()
        except Exception as exc:
            messagebox.showerror("Open Error", f"Failed to open file:\n{exc}")

    def save_file(self) -> bool:
        if not self.file_mgr.current_file:
            return self.save_file_as()
        try:
            self.file_mgr.save(self.editor.get("1.0", tk.END))
            self._update_status()
            return True
        except Exception as exc:
            messagebox.showerror("Save Error", f"Failed to save file:\n{exc}")
            return False

    def save_file_as(self) -> bool:
        path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown", "*.md"), ("All Files", "*.*")],
        )
        if path:
            self.file_mgr.save(self.editor.get("1.0", tk.END), path)
            self._update_status()
            return True
        return False

    def export_html(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML Files", "*.html"), ("All Files", "*.*")],
        )
        if path:
            self.file_mgr.export_html(self.editor.get("1.0", tk.END), path)
            messagebox.showinfo("Exported", f"Document exported successfully to:\n{path}")

    def preview_in_browser(self) -> None:
        content = self.editor.get("1.0", tk.END)
        html = to_html(content, standalone=True, title="PyMark Browser Preview")
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
            f.write(html)
            temp_path = f.name
        webbrowser.open(f"file://{Path(temp_path).resolve()}")
