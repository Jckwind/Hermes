import tkinter as tk
from tkinter import ttk
from .button import ToolbarButton

class Toolbar(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.pack(side=tk.TOP, fill=tk.X)
        self.buttons = []

    def add_button(self, text, command, icon=None, position=tk.LEFT):
        button = ToolbarButton(self, text=text, command=command, icon=icon)
        button.pack(side=position, padx=2, pady=2)
        self.buttons.append(button)
        return button

    def add_separator(self, position=tk.LEFT):
        separator = ttk.Separator(self, orient=tk.VERTICAL)
        separator.pack(side=position, padx=5, pady=2, fill=tk.Y)

    def add_spacer(self, position=tk.LEFT):
        spacer = ttk.Frame(self)
        spacer.pack(side=position, padx=10)

    def enable_all_buttons(self):
        for button in self.buttons:
            button.config(state=tk.NORMAL)

    def disable_all_buttons(self):
        for button in self.buttons:
            button.config(state=tk.DISABLED)
