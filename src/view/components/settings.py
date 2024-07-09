import tkinter as tk
from tkinter import ttk

class Settings(ttk.Frame):
    def __init__(self, parent, view, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.view = view
        self.create_widgets()

    def create_widgets(self):
        """Create and arrange settings widgets."""
        self.label = ttk.Label(self, text="Settings", font=('Helvetica', 16))
        self.label.pack(pady=10)

        self.folder_label = ttk.Label(self, text="Folder Name:", font=('Helvetica', 12))
        self.folder_var = tk.StringVar()
        self.folder_entry = ttk.Entry(self, textvariable=self.folder_var)
        self.apply_button = ttk.Button(self, text="Apply", command=self.apply_settings)

        # Initially hide the folder naming widgets
        self.folder_label.pack_forget()
        self.folder_entry.pack_forget()
        self.apply_button.pack_forget()

    def show_folder_naming(self):
        """Show the folder naming widgets."""
        self.folder_label.pack(pady=5)
        self.folder_entry.pack(pady=5)
        self.apply_button.pack(pady=10)

    def hide_folder_naming(self):
        """Hide the folder naming widgets."""
        self.folder_label.pack_forget()
        self.folder_entry.pack_forget()
        self.apply_button.pack_forget()

    def apply_settings(self):
        """Apply the selected settings."""
        folder_name = self.folder_var.get()
        self.view.set_folder_name(folder_name)
        self.hide_folder_naming()  # Hide the widgets after applying the settings

        # Start the dump process
        self.view.event_generate("<<StartNewProcess>>")
