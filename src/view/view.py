import tkinter as tk
from tkinter import ttk
from pathlib import Path
import json
import logging
from ttkthemes import ThemedTk
from typing import List, Dict, Any, Set
from model.text_collection.chat import Chat
from model.text_collection.message import Message
from view.components.toolbar import Toolbar
from view.components.welcome_message import WelcomeMessage
from view.components.settings import Settings
from view.components.chat_view import ChatView
from view.components.chat_list import ChatList
from tkinter import filedialog, simpledialog, messagebox

class View(ThemedTk):
    """Main GUI class for Hermes iMessage Viewer."""

    def __init__(self):
        super().__init__(theme="equilux")
        self.title("Hermes iMessage Viewer")
        self.geometry("1400x900")
        self.minsize(800, 600)

        self.create_styles()
        self.create_widgets()

        self.pack_propagate(False)

        self.show_intro = True
        self.load_intro_decision()
        if self.show_intro:
            self.show_introduction_window()

        self.selected_exported_file = None

    def create_styles(self):
        """Create and configure styles for widgets."""
        self.style = ttk.Style(self)

        # Define common colors
        bg_color = '#2d2d2d'
        fg_color = 'white'
        accent_color = '#4CAF50'

        # Configure common styles
        self.style.configure('TFrame', background=bg_color)
        self.style.configure('TLabel', background=bg_color, foreground=fg_color, font=('Helvetica', 12))
        self.style.configure('TButton', font=('Helvetica', 12), background=accent_color, foreground=fg_color)

        # Configure specific styles
        self.style.configure('Toolbar.TFrame', background='#1c1c1c')
        self.style.configure('Toolbar.TButton', background='#3d3d3d', foreground=fg_color, font=('Helvetica', 12, 'bold'))
        self.style.configure('Toolbar.TLabel', background='#1c1c1c', foreground=fg_color, font=('Helvetica', 12))

        self.style.configure('Search.TEntry',
                             font=('Helvetica', 12),
                             fieldbackground='#3d3d3d',
                             foreground=fg_color,
                             insertcolor=fg_color,
                             borderwidth=2,
                             relief='solid')

        self.style.configure('Clear.TButton',
                             font=('Helvetica', 10, 'bold'),
                             background='#3d3d3d',
                             foreground=fg_color,
                             borderwidth=2,
                             relief='solid')

        self.style.map('Clear.TButton',
                       background=[('active', '#4d4d4d')])

        self.style.configure('ChatList.TFrame', background=bg_color, borderwidth=2, relief='solid')
        self.style.configure('ChatView.TFrame', background=bg_color, borderwidth=2, relief='solid')
        self.style.configure('Settings.TFrame', background=bg_color, borderwidth=2, relief='solid')

        self.style.configure('Settings.TButton',
                             font=('Helvetica', 10, 'bold'),
                             padding=5,
                             background=accent_color,
                             foreground=fg_color,
                             borderwidth=2,
                             relief='solid')

        self.style.configure('Settings.TEntry',
                             font=('Helvetica', 10),
                             padding=5,
                             background='#3d3d3d',
                             foreground=fg_color,
                             borderwidth=2,
                             relief='solid')

        self.style.configure('Treeview',
                             background=bg_color,
                             foreground=fg_color,
                             fieldbackground=bg_color,
                             borderwidth=2,
                             relief='solid')

        self.style.map('Treeview',
                       background=[('selected', accent_color)],
                       foreground=[('selected', fg_color)])

    def create_widgets(self):
        """Create and arrange main widgets."""
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.create_toolbar()
        self.create_paned_window()

        self.bind("<<ExportedFileSelected>>", self.on_exported_file_selected)

        # Set the search bar width after creating all widgets
        self.after(100, self.set_search_bar_width)

    def create_toolbar(self):
        """Create toolbar with search functionality and buttons."""
        self.toolbar = Toolbar(self.main_frame)
        self.toolbar.pack(fill=tk.X, pady=(0, 5))

        button_frame = ttk.Frame(self.toolbar)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.export_button = ttk.Button(button_frame, text="Export Chats", command=self.start_export, style="Settings.TButton")
        self.export_button.pack(side=tk.RIGHT, pady=10, padx=(5, 10))

        self.upload_button = ttk.Button(button_frame, text="Upload to Google Drive", command=self.start_upload, style="Settings.TButton")
        self.upload_button.pack(side=tk.RIGHT, pady=10, padx=5)

        self.reset_button = ttk.Button(button_frame, text="Reset Application", command=self.reset_application, style="Settings.TButton")
        self.reset_button.pack(side=tk.RIGHT, pady=10, padx=(10, 5))

    def set_search_bar_width(self):
        """Set the search bar width to match the chat list width."""
        chat_list_width = self.chat_list.winfo_width()
        char_width = int(chat_list_width / 10)  # Approximate character width
        self.toolbar.set_search_width(char_width)

    def create_paned_window(self):
        """Create paned window for chat list, chat view, and settings."""
        paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        self.create_chat_list(paned_window)
        self.create_chat_view(paned_window)
        self.create_settings_area(paned_window)

    def create_chat_list(self, parent):
        """Create scrollable chat list area using ChatList component."""
        self.chat_list = ChatList(parent)
        parent.add(self.chat_list, weight=1)
        self.chat_list.bind_select(self.on_chat_selected)

    def create_chat_view(self, parent):
        """Create chat view area with an empty canvas."""
        self.chat_view = ChatView(parent)
        parent.add(self.chat_view, weight=4)

    def create_settings_area(self, parent):
        """Create settings area."""
        self.settings = Settings(parent, self)
        parent.add(self.settings, weight=1)

    def load_intro_decision(self):
        """Load user's decision about showing the intro window."""
        config_file = Path(__file__).parent.parent / ".hermes_config.json"
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    data = json.load(f)
                    self.show_intro = data.get("show_intro", True)
            except Exception as e:
                logging.error(f"Error loading intro decision: {e}")

    def show_introduction_window(self):
        """Display the introduction window using WelcomeMessage component."""
        self.threadsafe_call(self._show_introduction_window)

    def _show_introduction_window(self):
        config_file = Path(__file__).parent.parent / ".hermes_config.json"
        welcome_message = WelcomeMessage(self, config_file)
        welcome_message.protocol("WM_DELETE_WINDOW", welcome_message.close)
        welcome_message.grab_set()
        welcome_message.wait_window()
        self.load_intro_decision()

    def on_chat_selected(self, event):
        """Handle chat selection event."""
        selected_chats = self.chat_list.get_selected_chats()
        self.settings.update_selected_chats(selected_chats)

    def threadsafe_call(self, callback, *args):
        """Execute a callback in a thread-safe manner."""
        self.after(0, callback, *args)

    def notify_export_complete(self, output_dir):
        """Show a notification when the export is complete."""
        self.chat_view.show_completion_message(f"Export Complete!\nChats exported to:\n{output_dir}")
        messagebox.showinfo("Export Complete", f"Chats have been exported to:\n{output_dir}")

    def notify_upload_complete(self):
        """Show a notification when the upload to Google Drive is complete."""
        messagebox.showinfo("Upload Complete", "Chats have been uploaded to Google Drive.")

    def show_error(self, title, message):
        """Show an error message to the user."""
        messagebox.showerror(title, message)

    def display_chats(self, chats: List[str]):
        """Display the list of chats in the ChatList component."""
        self.chat_list.display_chats(chats)

    def start_export(self):
        """Start the export process."""
        self.event_generate("<<StartExport>>")

    def start_upload(self):
        """Start the Google Drive upload process."""
        self.event_generate("<<StartGoogleDriveUpload>>")

    def reset_application(self):
        """Reset the application."""
        self.event_generate("<<ResetApplication>>")
        self.settings.clear_exported_files_list()
        self.chat_view.clear()
        self.selected_exported_file = None

    def on_exported_file_selected(self, event):
        """Handle exported file selection event."""
        if self.selected_exported_file:
            self.event_generate("<<LoadExportedFile>>")

    def update_exported_files_list(self, filenames):
        """Update the list of exported files in the settings area."""
        self.settings.update_exported_files_list(filenames)

    def display_file_content(self, content):
        """Display the content of a file in the chat view."""
        self.chat_view.show_file_content(content)

if __name__ == "__main__":
    app = View()
    app.mainloop()