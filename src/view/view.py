import tkinter as tk
from tkinter import ttk
from pathlib import Path
import json
import logging
from ttkthemes import ThemedTk
from typing import List, Dict, Any
from model.text_collection.chat import Chat
from model.text_collection.message import Message
from view.components.toolbar import Toolbar
from view.components.welcome_message import WelcomeMessage
from view.components.settings import Settings
from view.components.chat_view import ChatView  # Add this import
from tkinter import filedialog, simpledialog, messagebox

class View(ThemedTk):
    """Main GUI class for Hermes iMessage Viewer."""

    def __init__(self):
        super().__init__(theme="equilux")
        self.title("Hermes iMessage Viewer")
        self.geometry("1400x900")  # Increased window size
        self.minsize(800, 600)  # Set minimum window size

        self.create_styles()
        self.create_widgets()

        self.show_intro = True
        self.load_intro_decision()
        if self.show_intro:
            self.show_introduction_window()

        self.selected_exported_file = None  # Add this line

    def create_styles(self):
        """Create and configure styles for widgets."""
        self.style = ttk.Style(self)
        self.style.configure('TFrame', background='#2d2d2d')
        self.style.configure('TButton', font=('Helvetica', 12))
        self.style.configure('TLabel', font=('Helvetica', 12))
        self.style.configure('Chat.TFrame', background='#2d2d2d')
        self.style.configure('Message.TFrame', background='#3d3d3d')
        self.style.configure('ChatItem.TFrame', background='#2d2d2d', relief='raised')
        self.style.configure('ChatItem.TLabel', background='#2d2d2d', font=('Helvetica', 12))

        self.style.configure('Toolbar.TFrame', background='#1c1c1c')
        self.style.configure('Toolbar.TButton', background='#3d3d3d', foreground='white', font=('Helvetica', 12, 'bold'))
        self.style.configure('Toolbar.TLabel', background='#1c1c1c', foreground='white', font=('Helvetica', 12))
        self.style.configure('Search.TEntry', font=('Helvetica', 12))
        self.style.configure("Settings.TButton", font=('Helvetica', 10, 'bold'), padding=5, background='#4CAF50', foreground='white')

    def create_widgets(self):
        """Create and arrange main widgets."""
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.create_toolbar()
        self.create_paned_window()

        # Bind the exported file selected event
        self.bind("<<ExportedFileSelected>>", self.on_exported_file_selected)

    def create_toolbar(self):
        """Create toolbar with search functionality and buttons."""
        self.toolbar = Toolbar(self.main_frame)
        self.toolbar.pack(fill=tk.X)

        # Create a frame to hold the buttons
        button_frame = ttk.Frame(self.toolbar)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.export_button = ttk.Button(button_frame, text="Export Chats", command=self.start_export, style="Settings.TButton")
        self.export_button.pack(side=tk.RIGHT, pady=10, padx=(5, 10))

        self.upload_button = ttk.Button(button_frame, text="Upload to Google Drive", command=self.start_upload, style="Settings.TButton")
        self.upload_button.pack(side=tk.RIGHT, pady=10, padx=5)

        self.reset_button = ttk.Button(button_frame, text="Reset Application", command=self.reset_application, style="Settings.TButton")
        self.reset_button.pack(side=tk.RIGHT, pady=10, padx=(10, 5))

    def create_paned_window(self):
        """Create paned window for chat list, chat view, and settings."""
        paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.create_chat_list(paned_window)
        self.create_chat_view(paned_window)
        self.create_settings_area(paned_window)

    def create_chat_list(self, parent):
        """Create scrollable chat list area using Listbox."""
        chat_frame = ttk.Frame(parent)
        parent.add(chat_frame, weight=1)

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(chat_frame, textvariable=self.search_var, style='Search.TEntry')
        search_entry.pack(fill=tk.X, padx=5, pady=5)

        self.chat_listbox = tk.Listbox(chat_frame,
                                       width=25,
                                       selectmode=tk.SINGLE,
                                       activestyle='none',
                                       highlightthickness=0,
                                       bd=0,
                                       relief=tk.FLAT,
                                       exportselection=0,
                                       bg='#2d2d2d',
                                       fg='white',
                                       selectbackground='#4d4d4d',
                                       selectforeground='white',
                                       font=('Helvetica', 20))
        self.chat_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        chat_scrollbar = ttk.Scrollbar(chat_frame, orient=tk.VERTICAL, command=self.chat_listbox.yview)
        chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.chat_listbox.config(yscrollcommand=chat_scrollbar.set)
        self.chat_listbox.bind('<<ListboxSelect>>', self.on_chat_selected)

    def create_chat_view(self, parent):
        """Create chat view area with an empty canvas."""
        self.chat_view = ChatView(parent)
        parent.add(self.chat_view, weight=4)  # Give 4/6 of the space to chat view

    def create_settings_area(self, parent):
        """Create settings area."""
        self.settings = Settings(parent, self)
        parent.add(self.settings, weight=1)  # Give 1/6 of the space to settings

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
        self.load_intro_decision()  # Reload the decision after closing the window

    def on_chat_selected(self, event):
        """Handle chat selection event."""
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            chat_name = self.chat_listbox.get(index)
            self.settings.display_chat_name(chat_name)

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
        """Display the list of chats in the Listbox only."""
        self.chat_listbox.delete(0, tk.END)
        for chat_name in chats:
            self.chat_listbox.insert(tk.END, chat_name)
        self.chat_listbox.update_idletasks()

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
        self.chat_view.clear()  # Assuming you have a clear method in ChatView
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