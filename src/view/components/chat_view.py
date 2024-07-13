import tkinter as tk
from tkinter import ttk
import math

class ChatView(ttk.Frame):
    """A custom widget for displaying an empty canvas with loading animation."""

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.parent = master
        self._create_widgets()
        self.is_animating = False
        self.angle = 0
        self.angle_increment = 15  # Increased from 10 to 15
        self.animation_delay = 30  # Decreased from 50 to 30 milliseconds

    def _create_widgets(self):
        """Create and configure the widgets for the chat view."""
        self.canvas = tk.Canvas(self, bg='#2d2d2d')
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def clear(self):
        """Clear the canvas."""
        self.canvas.delete("all")

    def start_loading_animation(self):
        """Start the loading animation."""
        print("Starting loading animation")
        self.is_animating = True
        self.clear()
        self._animate_loading()

    def stop_loading_animation(self):
        """Stop the loading animation."""
        self.is_animating = False

    def _animate_loading(self):
        """Animate the loading circle."""
      
        if not self.is_animating:
           
            return

        self.clear()
        center_x = self.canvas.winfo_width() // 2
        center_y = self.canvas.winfo_height() // 2
        radius = 50
        start_angle = self.angle
        extent = 300

        self.canvas.create_arc(center_x - radius, center_y - radius,
                               center_x + radius, center_y + radius,
                               start=start_angle, extent=extent,
                               outline="#4CAF50", width=10, style=tk.ARC)

        self.angle = (self.angle + self.angle_increment) % 360
        self.after(self.animation_delay, self._animate_loading)  # Use the new animation_delay

    def show_completion_message(self, message):
        """Display a completion message on the canvas."""
        self.clear()
        center_x = self.canvas.winfo_width() // 2
        center_y = self.canvas.winfo_height() // 2
        self.canvas.create_text(center_x, center_y, text=message, fill="white", font=("Helvetica", 16, "bold"))