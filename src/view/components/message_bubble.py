import tkinter as tk
from tkinter import Frame, Label
from model.text_collection.message import Message

class MessageBubble:
    """Represents a message bubble on the canvas."""

    def __init__(self, master, message: Message, y_offset):
        """
        Initializes a MessageBubble object.

        Args:
            master (tk.Widget): The parent widget (preferably a Canvas).
            message (Message): The Message object containing message details.
            bubble_color (str): The color of the bubble.
            y_offset (int): The vertical offset of the bubble.
        """
        self.master = self.find_canvas_parent(master)
        if not self.master:
            raise ValueError("MessageBubble requires a Canvas or a widget with a Canvas parent")

        bubble_color = '#3d3d3d' if message.isFromMe else '#1c1c1c'
        self.frame = Frame(self.master, bg=bubble_color)
        self.i = self.master.create_window(10, y_offset, anchor="nw", window=self.frame)

        Label(self.frame, text=message.sender.name, font=("Helvetica", 20, "italic"), bg=bubble_color).grid(
            row=0, column=0, sticky="w", padx=5
        )

        # Split message into lines if it exceeds 200 units
        wrapped_message = self.wrap_text(message.body, 100)

        # Right-align user's messages, otherwise left align
        if message.isFromMe:
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
