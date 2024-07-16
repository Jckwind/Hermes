import tkinter as tk
from tkinter import ttk
import math

class ChatView(ttk.Frame):
    """A custom widget for displaying an empty canvas with loading animation."""

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, style='ChatView.TFrame', *args, **kwargs)
        self.parent = master
        self._create_widgets()
        self.is_animating = False
        self.angle = 0
        self.angle_increment = 15  # Increased from 10 to 15
        self.animation_delay = 10  # Decreased from 50 to 30 milliseconds
        self.highlighted_names = set()
        self.content = ""

    def _create_widgets(self):
        """Create and configure the widgets for the chat view."""
        self.canvas = tk.Canvas(self, bg='#2d2d2d', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.text_widget = tk.Text(self, wrap=tk.WORD, bg='#2d2d2d', fg='white', font=('Helvetica', 12))
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        self.text_widget.pack_forget()  # Hide it initially

        # Configure text tags for highlighting
        self.text_widget.tag_configure("highlighted", background="#4CAF50", foreground="white")

        # Add a custom scrollbar
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=self.scrollbar.set)

    def clear(self):
        """Clear the canvas."""
        self.canvas.delete("all")
        self.text_widget.delete(1.0, tk.END)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.text_widget.pack_forget()
        self.highlighted_names.clear()

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

        # Draw multiple arcs for a more interesting animation
        for i in range(3):
            color = self._interpolate_color("#4CAF50", "#2196F3", i / 2)
            self.canvas.create_arc(center_x - radius + i*10, center_y - radius + i*10,
                                   center_x + radius - i*10, center_y + radius - i*10,
                                   start=start_angle + i*20, extent=extent - i*40,
                                   outline=color, width=5, style=tk.ARC)

        self.angle = (self.angle + self.angle_increment) % 360
        self.after(self.animation_delay, self._animate_loading)

    def _interpolate_color(self, color1, color2, factor):
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        r = int(r1 + factor * (r2 - r1))
        g = int(g1 + factor * (g2 - g1))
        b = int(b1 + factor * (b2 - b1))
        return f"#{r:02x}{g:02x}{b:02x}"

    def show_completion_message(self, message):
        """Display a completion message on the canvas."""
        self.clear()
        center_x = self.canvas.winfo_width() // 2
        center_y = self.canvas.winfo_height() // 2
        self.canvas.create_text(center_x, center_y, text=message, fill="white", font=("Helvetica", 16, "bold"))

    def show_file_content(self, content):
        """Display the content of a file in the text widget."""
        self.content = content
        self.clear()
        self.canvas.pack_forget()
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(tk.END, content)
        self.apply_highlighting()

    def apply_highlighting(self):
        self.text_widget.tag_remove("highlighted", "1.0", tk.END)
        for name in self.highlighted_names:
            self.highlight_name(name)

    def highlight_name(self, name):
        start = "1.0"
        while True:
            start = self.text_widget.search(name, start, stopindex=tk.END, nocase=True)
            if not start:
                break
            end = f"{start}+{len(name)}c"
            self.text_widget.tag_add("highlighted", start, end)
            start = end

    def update_highlighted_names(self, selected_names):
        self.highlighted_names = set(selected_names)
        if self.content:
            self.apply_highlighting()

    def reset_highlights(self):
        """Reset only the highlighted names without clearing the content."""
        self.highlighted_names.clear()
        self.text_widget.tag_remove("highlighted", "1.0", tk.END)

    def hide_file_content(self):
        """Hide the text widget and show the canvas."""
        self.text_widget.pack_forget()
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def reset(self):
        """Reset the chat view."""
        self.clear()
        self.hide_file_content()