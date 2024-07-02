import tkinter as tk
from tkinter import ttk
from model.text_collection.message import Message


class MessageBubble(ttk.Frame):
    """A custom widget to display a message bubble in a chat interface."""

    def __init__(self, master, message: Message):
        """Initialize the MessageBubble widget.

        Args:
            master: The parent widget.
            message: The Message object to display.
        """
        super().__init__(master)
        self._message = message
        self._create_widgets()

    def _create_widgets(self):
        """Create and configure the widgets for the message bubble."""
        style = ttk.Style()
        self._configure_styles(style)

        self._create_sender_label()
        self._create_body_label()
        self._create_date_label()

    def _configure_styles(self, style):
        """Configure the styles for the message bubble.

        Args:
            style: The ttk.Style object to configure.
        """
        if self._message.is_from_me:
            bg_color = '#1E90FF'
            fg_color = '#F0F0F0'
        else:
            bg_color = '#E0E0E0'
            fg_color = '#333333'

        style_name = f'MessageBubble_{id(self)}.TFrame'
        style.configure(style_name, background=bg_color)
        style.configure(style_name, relief='solid')
        style.configure(style_name, borderwidth=1)
        style.configure(style_name, borderradius=10)
        style.configure(f'SenderLabel_{id(self)}.TLabel', foreground=fg_color, background=bg_color, font=("Helvetica", 14))
        style.configure(f'BodyLabel_{id(self)}.TLabel', foreground=fg_color, background=bg_color, font=("Helvetica", 16))
        style.configure(f'DateLabel_{id(self)}.TLabel', foreground=fg_color, background=bg_color, font=("Helvetica", 12))

        self.configure(style=style_name)

    def _create_sender_label(self):
        """Create and pack the sender label."""
        sender_label = ttk.Label(self, text=self._message.sender.name, style=f'SenderLabel_{id(self)}.TLabel')
        sender_label.pack(anchor='e' if self._message.is_from_me else 'w', padx=5, pady=(5, 0))

    def _create_body_label(self):
        """Create and pack the message body label."""
        body_text = self._message.body if not self._message.is_attachment_only else "(Image Attachment)"
        body_label = ttk.Label(self, text=body_text, style=f'BodyLabel_{id(self)}.TLabel', wraplength=300, justify='left')
        body_label.pack(fill='x', padx=5, pady=(5, 0))

    def _create_date_label(self):
        """Create and pack the date label."""
        date_label = ttk.Label(self, text=self._message.formatted_date, style=f'DateLabel_{id(self)}.TLabel')
        date_label.pack(anchor='e', padx=5, pady=(5, 5))
