import tkinter as tk
from .button import ToolbarButton

class Toolbar(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.pack(side=tk.TOP, fill=tk.X)

    def add_button(self, text, command):
        button = ToolbarButton(self, text=text, command=command)
        return button