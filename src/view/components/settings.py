import tkinter as tk
from tkinter import ttk
from typing import List

class Settings(ttk.Frame):
    def __init__(self, parent, view, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.view = view
        self.create_widgets()

    def create_widgets(self):
        """Create and arrange settings widgets."""
        self._configure_styles()

        self.settings_frame = ttk.Frame(self, style="SettingsFrame.TFrame")
        self.settings_frame.pack(pady=10, padx=10, fill='x')

        self.inner_frame = ttk.Frame(self.settings_frame)
        self.inner_frame.pack(padx=2, pady=2, fill='x')

        self.label = ttk.Label(self.inner_frame, text="Settings", style="Heading.TLabel")
        self.label.pack(pady=10, anchor='center')

        self.export_button = ttk.Button(self.inner_frame, text="Export Chats", command=self.start_export, style="Settings.TButton")
        self.export_button.pack(pady=10, padx=10)

        self.upload_button = ttk.Button(self.inner_frame, text="Upload to Google Drive", command=self.start_upload, style="Settings.TButton")
        self.upload_button.pack(pady=10, padx=10)

        self.reset_button = ttk.Button(self.inner_frame, text="Reset Application", command=self.reset_application, style="Settings.TButton")
        self.reset_button.pack(pady=10, padx=10)

        # Add the chat view functionality
        self.create_chat_view()

    def create_chat_view(self):
        """Create and configure the chat view widgets."""
        self.chat_frame = ttk.Frame(self.inner_frame)
        self.chat_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(self.chat_frame, columns=("ChatName"), show="headings", selectmode="browse")
        self.tree.heading("ChatName", text="Selected Chats")
        self.tree.column("ChatName", anchor="w", width=200)
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        self.scrollbar = ttk.Scrollbar(self.chat_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill="y")

        self._bind_chat_events()

    def _bind_chat_events(self):
        """Bind events for the chat view."""
        self.tree.bind("<Double-1>", self.on_message_double_click)
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
            self.tree.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_shift_mousewheel(self, event):
        """Handle horizontal scrolling with Shift + mousewheel."""
        if event.delta > 0:
            self.tree.xview_scroll(-1, "units")
        elif event.delta < 0:
            self.tree.xview_scroll(1, "units")
        
    def get_displayed_chats(self) -> List[str]:
        """Retrieve the list of chat names currently displayed in the Treeview."""
        return [self.tree.item(item, "values")[0] for item in self.tree.get_children()]

    def clear_messages(self):
        """Clear all messages in the chat view."""
        for item in self.tree.get_children():
            self.tree.delete(item)

    def _configure_styles(self):
        """Configure custom styles for widgets."""
        style = ttk.Style()
        style.configure("Heading.TLabel", font=('Helvetica', 16, 'bold'), foreground='#4CAF50', padding=10)
        style.configure("Settings.TButton", font=('Helvetica', 10, 'bold'), padding=5, background='#4CAF50', foreground='white')

    def start_export(self):
        """Start the export process."""
        self.view.event_generate("<<StartExport>>")

    def start_upload(self):
        """Start the Google Drive upload process."""
        self.view.event_generate("<<StartGoogleDriveUpload>>")

    def reset_application(self):
        """Reset the application."""
        self.view.event_generate("<<ResetApplication>>")

    def display_chat_name(self, chat_name: str):
        """Display the chat name in the message area."""
        if not self.tree.exists(chat_name):
            self.tree.insert("", "end", iid=chat_name, values=(chat_name,))

    def remove_chat_name(self, chat_name: str):
        """Remove the chat name from the message area."""
        if self.tree.exists(chat_name):
            self.tree.delete(chat_name)

    def display_chats(self, chat_names: List[str]):
        """Display the list of chat names in the Treeview."""
        self.clear_messages()
        for chat_name in chat_names:
            self.display_chat_name(chat_name)
