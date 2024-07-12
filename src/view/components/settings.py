import tkinter as tk
from tkinter import ttk

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