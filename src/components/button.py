import tkinter as tk

class ToolbarButton(tk.Button):
    def __init__(self, parent, text, command, *args, **kwargs):
        super().__init__(parent, text=text, command=command, *args, **kwargs)
        self.pack(side=tk.LEFT, padx=2, pady=2)