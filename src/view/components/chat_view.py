import tkinter as tk
from tkinter import ttk
from typing import List

class ChatView(ttk.Frame):
    """A custom widget for displaying chat names."""

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.parent = master
        self._create_widgets()
        self._bind_events()

    def _create_widgets(self):
        """Create and configure the widgets for the chat view."""
        self.chat_name_listbox = tk.Listbox(self, bg='#2d2d2d', fg='white', font=('Helvetica', 12))
        self.chat_name_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.chat_name_listbox.bind("<Button-1>", self.on_message_click)  # Bind left mouse click event

    def _bind_events(self):
        """Bind events for smooth scrolling and resizing."""
        self.bind_all('<MouseWheel>', self._on_mousewheel)
        self.bind_all('<Button-4>', self._on_mousewheel)
        self.bind_all('<Button-5>', self._on_mousewheel)
        self.bind_all('<Shift-MouseWheel>', self._on_shift_mousewheel)

    def on_message_click(self, event):
        selected_index = self.chat_name_listbox.curselection()
        if selected_index:
            self.chat_name_listbox.delete(selected_index)

    def _on_mousewheel(self, event):
        """Handle mousewheel and trackpad scrolling."""
        if event.num == 4 or event.delta > 0:
            self.chat_name_listbox.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.chat_name_listbox.yview_scroll(1, "units")
        else:
            # For macOS, event.delta is much larger, so we need to scale it down
            self.chat_name_listbox.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_shift_mousewheel(self, event):
        """Handle horizontal scrolling with Shift + mousewheel."""
        if event.delta > 0:
            self.chat_name_listbox.xview_scroll(-1, "units")
        elif event.delta < 0:
            self.chat_name_listbox.xview_scroll(1, "units")

    def display_chat_name(self, chat_name: str):
        """Display the chat name in the message area."""
        if chat_name not in self.chat_name_listbox.get(0, tk.END):
            self.chat_name_listbox.insert(tk.END, chat_name)
        else:
            self.chat_name_listbox.delete(self.chat_name_listbox.get(0, tk.END).index(chat_name))

    def get_displayed_chats(self) -> List[str]:
        """Retrieve the list of chat names currently displayed in the Listbox."""
        return self.chat_name_listbox.get(0, tk.END)

    def clear_messages(self):
        """Clear all messages in the chat view."""
        self.chat_name_listbox.delete(0, tk.END)
