import tkinter as tk
from tkinter import ttk

class ChatView(ttk.Frame):
    """A custom widget for displaying an empty canvas."""

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.parent = master
        self._create_widgets()

    def _create_widgets(self):
        """Create and configure the widgets for the chat view."""
        self.canvas = tk.Canvas(self, bg='#2d2d2d')
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def clear(self):
        """Clear the canvas."""
        self.canvas.delete("all")