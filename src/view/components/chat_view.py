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
        self.tree = ttk.Treeview(self, columns=("ChatName"), show="headings", selectmode="browse")
        self.tree.heading("ChatName", text="Chat Name")
        self.tree.column("ChatName", anchor="w", width=200)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add a scrollbar
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

    def _bind_events(self):
        """Bind events for smooth scrolling and resizing."""
        self.tree.bind("<Double-1>", self.on_message_double_click)  # Bind double-click event
        self.bind_all('<MouseWheel>', self._on_mousewheel)
        self.bind_all('<Button-4>', self._on_mousewheel)
        self.bind_all('<Button-5>', self._on_mousewheel)
        self.bind_all('<Shift-MouseWheel>', self._on_shift_mousewheel)

    def on_message_double_click(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            self.tree.delete(selected_item[0])

    def _on_mousewheel(self, event):
        """Handle mousewheel and trackpad scrolling."""
        if event.num == 4 or event.delta > 0:
            self.tree.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.tree.yview_scroll(1, "units")
        else:
            # For macOS, event.delta is much larger, so we need to scale it down
            self.tree.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_shift_mousewheel(self, event):
        """Handle horizontal scrolling with Shift + mousewheel."""
        if event.delta > 0:
            self.tree.xview_scroll(-1, "units")
        elif event.delta < 0:
            self.tree.xview_scroll(1, "units")

    def display_chat_name(self, chat_name: str):
        """Display the chat name in the message area."""
        if not self.tree.exists(chat_name):
            self.tree.insert("", "end", iid=chat_name, values=(chat_name,))

    def get_displayed_chats(self) -> List[str]:
        """Retrieve the list of chat names currently displayed in the Treeview."""
        return [self.tree.item(item, "values")[0] for item in self.tree.get_children()]

    def clear_messages(self):
        """Clear all messages in the chat view."""
        for item in self.tree.get_children():
            self.tree.delete(item)
