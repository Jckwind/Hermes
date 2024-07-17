import tkinter as tk
from tkinter import ttk

class SearchBar(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, style='Toolbar.TFrame', *args, **kwargs)
        self.create_widgets()

    def create_widgets(self):
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search_change)

        self.search_entry = ttk.Entry(
            self,
            textvariable=self.search_var,
            style='Search.TEntry',
            font=('Helvetica', 12)
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Add a clear button
        self.clear_button = ttk.Button(
            self,
            text="✕",
            style="Clear.TButton",
            command=self.clear_search,
            width=3
        )
        self.clear_button.pack(side=tk.LEFT, padx=(5, 0))

        # Bind events
        self.search_entry.bind("<FocusIn>", self.on_search_focus_in)
        self.search_entry.bind("<FocusOut>", self.on_search_focus_out)

        # Set initial state
        self.on_search_focus_out(None)

    def on_search_change(self, *args):
        if self.search_var.get() != "Search...":
            self.event_generate("<<SearchChanged>>")

    def on_search_focus_in(self, event):
        if self.search_var.get() == "Search...":
            self.search_var.set("")
            self.search_entry.config(foreground='white')

    def on_search_focus_out(self, event):
        if not self.search_var.get():
            self.search_var.set("Search...")
            self.search_entry.config(foreground='gray')

    def clear_search(self):
        self.search_var.set("")
        self.search_entry.focus_set()
        self.event_generate("<<SearchChanged>>")

    def set_width(self, width):
        self.search_entry.config(width=width)

    def get_search_var(self):
        return self.search_var