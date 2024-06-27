import tkinter as tk
from tkinter import ttk
import json
from pathlib import Path

class WelcomeMessage(tk.Toplevel):
    def __init__(self, master, config_path):
        super().__init__(master)
        self.title("Welcome to Hermes iMessage Viewer")
        self.geometry("500x400")
        self.configure(bg='#f0f0f0')
        self.config_path = Path(config_path)

        title_label = tk.Label(
            self,
            text="Welcome to Hermes iMessage Viewer",
            font=('Helvetica', 16, 'bold'),
            bg='#f0f0f0',
            fg='#333333'
        )
        title_label.pack(pady=(20, 10))

        instructions = [
            "1. Select a conversation to view past iMessages.",
            "2. Use the 'Links' button to see shared links.",
            "3. 'Export' saves conversations as text files.",
            "4. 'Analyze Conversation' uses Google Gemini AI for insights."
        ]

        for instruction in instructions:
            instruction_label = tk.Label(
                self,
                text=instruction,
                font=('Helvetica', 12),
                bg='#f0f0f0',
                fg='#555555',
                wraplength=400,
                justify='left'
            )
            instruction_label.pack(padx=20, pady=5, anchor='w')

        self.dont_show_again_var = tk.BooleanVar(value=False)
        dont_show_again_checkbox = ttk.Checkbutton(
            self,
            text="Do not show this again",
            variable=self.dont_show_again_var,
            style='TCheckbutton'
        )
        dont_show_again_checkbox.pack(pady=(20, 10))

        close_button = ttk.Button(
            self,
            text="Get Started",
            command=self.close,
            style='TButton'
        )
        close_button.pack(pady=10)

        self.style = ttk.Style()
        self.style.configure('TCheckbutton', background='#f0f0f0')
        self.style.configure('TButton')

    def close(self):
        self.update_config()
        self.destroy()

    def update_config(self):
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)

            # Only update the 'show_intro' key, preserving other values
            config['show_intro'] = not self.dont_show_again_var.get()

            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error updating config: {e}")
