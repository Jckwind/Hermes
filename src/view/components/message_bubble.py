import tkinter as tk
from tkinter import Frame, Label

class MessageBubble:
    """Represents a message bubble on the canvas."""

    def __init__(self, master, sender, message, bubble_color, y_offset, is_user):
        """
        Initializes a MessageBubble object.

        Args:
            master (tk.Widget): The parent widget (preferably a Canvas).
            sender (str): The sender of the message.
            message (str): The message content.
            bubble_color (str): The color of the bubble.
            y_offset (int): The vertical offset of the bubble.
            is_user (bool): Whether the message is from the user.
        """
        self.master = self.find_canvas_parent(master)
        if not self.master:
            raise ValueError("MessageBubble requires a Canvas or a widget with a Canvas parent")

        self.frame = Frame(self.master, bg=bubble_color)
        self.i = self.master.create_window(10, y_offset, anchor="nw", window=self.frame)

        Label(self.frame, text=sender, font=("Helvetica", 20, "italic"), bg=bubble_color).grid(
            row=0, column=0, sticky="w", padx=5
        )

        # Split message into lines if it exceeds 200 units
        wrapped_message = self.wrap_text(message, 100)

        # Right-align user's messages, otherwise left align
        if is_user:
            Label(
                self.frame,
                text=wrapped_message,
                font=("Helvetica", 18, "bold"),
                bg=bubble_color,
                anchor="w",
                justify="left",
            ).grid(row=1, column=0, sticky="e", padx=5, pady=3)
        else:
            Label(
                self.frame,
                text=wrapped_message,
                font=("Helvetica", 18, "bold"),
                bg=bubble_color,
                anchor="w",
            ).grid(row=1, column=0, sticky="w", padx=5, pady=3)

        self.master.update_idletasks()  # Update to get accurate dimensions
        self.height = (
            self.master.bbox(self.i)[3] - self.master.bbox(self.i)[1]
        )  # Calculate height after creation

    def find_canvas_parent(self, widget):
        """Recursively search for a Canvas parent"""
        if widget is None:
            return None
        if isinstance(widget, tk.Canvas):
            return widget
        return self.find_canvas_parent(widget.master)

    def wrap_text(self, text, max_length):
        """Wraps text to a new line if it exceeds the max_length."""
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            if len(current_line) + len(word) + 1 > max_length:
                lines.append(current_line)
                current_line = word
            else:
                current_line += " " + word if current_line else word

        if current_line:
            lines.append(current_line)

        return "\n".join(lines)

    def draw_triangle(self):
        """Draws a triangle pointing towards the message bubble."""
        x1, y1, x2, y2 = self.master.bbox(self.i)
        return self.master.create_polygon(x1, y2 - 10, x1 - 15, y2 + 10, x1, y2, fill=self.frame.cget("bg"))
