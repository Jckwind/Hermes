import tkinter as tk
from tkinter import ttk
from typing import List
from model.text_collection.message import Message
from .message_bubble import MessageBubble

class ChatView(ttk.Frame):
    """A custom widget for displaying chat messages with smooth scrolling."""

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self._messages = []
        self._create_widgets()
        self._bind_events()

    def _create_widgets(self):
        """Create and configure the widgets for the chat view."""
        self._canvas = tk.Canvas(self, bg='#2d2d2d', highlightthickness=0)
        self._scrollbar = ttk.Scrollbar(self, orient="vertical", command=self._canvas.yview)
        self._message_frame = ttk.Frame(self._canvas)

        self._canvas.configure(yscrollcommand=self._scrollbar.set)
        self._canvas_frame = self._canvas.create_window((0, 0), window=self._message_frame, anchor="nw")

        self._canvas.pack(side="left", fill="both", expand=True)
        self._scrollbar.pack(side="right", fill="y")

    def _bind_events(self):
        """Bind events for smooth scrolling and resizing."""
        self._canvas.bind('<Configure>', self._on_canvas_configure)
        self._message_frame.bind('<Configure>', self._on_frame_configure)
        self.bind_all('<MouseWheel>', self._on_mousewheel)
        self.bind_all('<Button-4>', self._on_mousewheel)
        self.bind_all('<Button-5>', self._on_mousewheel)
        self.bind_all('<Shift-MouseWheel>', self._on_shift_mousewheel)

    def _on_canvas_configure(self, event):
        """Adjust the canvas frame width when the canvas is resized."""
        self._canvas.itemconfig(self._canvas_frame, width=event.width)

    def _on_frame_configure(self, event):
        """Update the scroll region when the frame size changes."""
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_mousewheel(self, event):
        """Handle mousewheel and trackpad scrolling."""
        if event.num == 4 or event.delta > 0:
            self._canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self._canvas.yview_scroll(1, "units")
        else:
            # For macOS, event.delta is much larger, so we need to scale it down
            self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_shift_mousewheel(self, event):
        """Handle horizontal scrolling with Shift + mousewheel."""
        if event.delta > 0:
            self._canvas.xview_scroll(-1, "units")
        elif event.delta < 0:
            self._canvas.xview_scroll(1, "units")

    def display_messages(self, messages: List[Message]):
        """Display a list of messages in the chat view."""
        self._clear_messages()
        for message in messages:
            self._add_message(message)
        self._scroll_to_bottom()

    def _clear_messages(self):
        """Remove all existing messages from the view."""
        for widget in self._message_frame.winfo_children():
            widget.destroy()

    def _add_message(self, message: Message):
        """Add a single message to the chat view."""
        bubble = MessageBubble(self._message_frame, message)
        bubble.pack(pady=(0, 10), padx=10, anchor='e' if message.is_from_me else 'w')
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _scroll_to_bottom(self):
        """Scroll the chat view to the bottom."""
        self._canvas.yview_moveto(1.0)
