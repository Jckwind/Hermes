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

        # Create a frame with a dark border
        self.settings_frame = ttk.Frame(self, style="SettingsFrame.TFrame")
        self.settings_frame.pack(pady=10, padx=10, fill='x')

        # Create an inner frame to hold the content
        self.inner_frame = ttk.Frame(self.settings_frame)
        self.inner_frame.pack(padx=2, pady=2, fill='x')

        self.label = ttk.Label(self.inner_frame, text="Settings", style="Heading.TLabel")
        self.label.pack(pady=10, anchor='center')

        self.folder_label = ttk.Label(self.inner_frame, text="Folder Name:", style="SubHeading.TLabel")
        self.folder_var = tk.StringVar()
        self.folder_entry = ttk.Entry(self.inner_frame, textvariable=self.folder_var, style="Settings.TEntry")
        self.apply_button = ttk.Button(self.inner_frame, text="Apply", command=self.apply_settings, style="Settings.TButton")

        # Configure the frame style with a dark border
        style = ttk.Style()
        style.configure("SettingsFrame.TFrame", borderwidth=2, relief="solid", bordercolor="#2E2E2E")

        # Initially hide the folder naming widgets
        self.folder_label.pack_forget()
        self.folder_entry.pack_forget()
        self.apply_button.pack_forget()

    def _configure_styles(self):
        """Configure custom styles for widgets."""
        style = ttk.Style()
        style.configure("Heading.TLabel", font=('Helvetica', 16, 'bold'), foreground='#4CAF50', padding=10)
        style.configure("SubHeading.TLabel", font=('Helvetica', 12), foreground='#4CAF50', padding=5)
        style.configure("Settings.TEntry", font=('Helvetica', 10), padding=5)
        style.configure("Settings.TButton", font=('Helvetica', 10, 'bold'), padding=5, background='#4CAF50', foreground='white')

    def show_folder_naming(self):
        """Show the folder naming widgets."""
        self.folder_label.pack(pady=5, padx=10, anchor='w')
        self.folder_entry.pack(pady=5, padx=10, fill='x')
        self.apply_button.pack(pady=10, padx=10)

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
