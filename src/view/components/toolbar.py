import tkinter as tk
from tkinter import ttk
from .button import ToolbarButton
from .search_bar import SearchBar

class Toolbar(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.pack(side=tk.TOP, fill=tk.X)
        self.buttons = []

        # Configure the style for the toolbar
        self.style = ttk.Style()
        self.style.configure("Toolbar.TFrame", background="#2d2d2d")
        self.configure(style="Toolbar.TFrame")

        self.create_search_bar()

    def create_search_bar(self):
        search_frame = ttk.Frame(self, style="Toolbar.TFrame")
        search_frame.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.X, expand=True)

        self.search_bar = SearchBar(search_frame)
        self.search_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def set_search_width(self, width):
        self.search_bar.set_width(width)

    def get_search_var(self):
        return self.search_bar.get_search_var()

    def add_button(self, text, command, icon=None, position=tk.LEFT):
        button = ToolbarButton(self, text=text, command=command, icon=icon)
        button.pack(side=position, padx=2, pady=2)
        self.buttons.append(button)
        return button

    def add_separator(self, position=tk.LEFT):
        separator = ttk.Separator(self, orient=tk.VERTICAL)
        separator.pack(side=position, padx=5, pady=2, fill=tk.Y)

    def add_spacer(self, position=tk.LEFT):
        spacer = ttk.Frame(self, style="Toolbar.TFrame")
        spacer.pack(side=position, padx=10)

    def enable_all_buttons(self):
        for button in self.buttons:
            button.config(state=tk.NORMAL)

    def disable_all_buttons(self):
        for button in self.buttons:
            button.config(state=tk.DISABLED)
