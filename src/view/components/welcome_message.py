import tkinter as tk
from tkinter import messagebox

class WelcomeMessage(tk.Toplevel):
    def __init__(self, master, custom_font):
        super().__init__(master)
        self.title("Welcome to Hermes iMessage Viewer")

        instructions_label = tk.Label(
            self,
            text="Instructions:\n"
            "1. Click on a conversation (either a group chat or a single chat) to view past iMessages.\n"
            "2. Click on the 'Links' button to view links sent within that chat.\n"
            "3. Click on the 'Export' button to save the selected conversation to .txt files on your computer.\n"
            "   Two files will be saved: one for the conversation and one for the links.\n"
            "4. Click the 'Analyze Conversation' button to be redirected to Google Gemini,\n"
            "   an AI powered by Google. You can analyze conversations there.",
            font=custom_font,
            wraplength=400,
        )
        instructions_label.pack(padx=20, pady=20)

        self.dont_show_again_var = tk.BooleanVar(value=False)
        dont_show_again_checkbox = tk.Checkbutton(
            self,
            text="Do not show this again",
            variable=self.dont_show_again_var,
            font=custom_font,
        )
        dont_show_again_checkbox.pack(pady=10)

        close_button = tk.Button(
            self, text="Close", command=self.close, font=custom_font
        )
        close_button.pack(pady=10)

    def close(self):
        self.master.show_intro = not self.dont_show_again_var.get()
        self.master.save_intro_decision()
        self.destroy()
