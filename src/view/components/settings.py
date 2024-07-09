import tkinter as tk
from tkinter import ttk

class Settings(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.create_widgets()

    def create_widgets(self):
        """Create and arrange settings widgets."""
        self.label = ttk.Label(self, text="Settings", font=('Helvetica', 16))
        self.label.pack(pady=10)

        self.theme_label = ttk.Label(self, text="Choose Theme:", font=('Helvetica', 12))
        self.theme_label.pack(pady=5)

        self.theme_var = tk.StringVar(value="equilux")
        self.theme_combobox = ttk.Combobox(self, textvariable=self.theme_var, values=["equilux", "arc", "radiance"])
        self.theme_combobox.pack(pady=5)

        self.apply_button = ttk.Button(self, text="Apply", command=self.apply_settings)
        self.apply_button.pack(pady=10)

    def apply_settings(self):
        """Apply the selected settings."""
        selected_theme = self.theme_var.get()
        self.parent.apply_theme(selected_theme)
