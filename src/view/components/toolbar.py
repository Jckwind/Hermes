import tkinter as tk
from tkinter import ttk
from .button import ToolbarButton

class Toolbar(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.pack(side=tk.TOP, fill=tk.X)
        self.buttons = []
        
        # Add a gradient background
        self.canvas = tk.Canvas(self, height=40, highlightthickness=0)
        self.canvas.pack(fill=tk.X)
        self.canvas.bind("<Configure>", self._draw_gradient)

    def _draw_gradient(self, event):
        width = event.width
        height = event.height
        self.canvas.delete("gradient")
        self.canvas.create_rectangle(0, 0, width, height, fill="#1c1c1c", tags=("gradient",))
        for i in range(height):
            color = self._interpolate_color("#1c1c1c", "#2d2d2d", i / height)
            self.canvas.create_line(0, i, width, i, fill=color, tags=("gradient",))

    def _interpolate_color(self, color1, color2, factor):
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        r = int(r1 + factor * (r2 - r1))
        g = int(g1 + factor * (g2 - g1))
        b = int(b1 + factor * (b2 - b1))
        return f"#{r:02x}{g:02x}{b:02x}"

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