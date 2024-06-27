import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import json
import logging
from ttkthemes import ThemedTk
from typing import List, Dict, Any
from model.text_collection.chat import Chat
from view.components.toolbar import Toolbar
from view.components.message_bubble import MessageBubble
from view.components.welcome_message import WelcomeMessage


class View(ThemedTk):
    """Main GUI class for Hermes iMessage Viewer."""

    def __init__(self):
        super().__init__(theme="equilux")
        self.title("Hermes iMessage Viewer")
        self.geometry("1200x800")
        self.minsize(800, 600)  # Set minimum window size

        self.create_styles()
        self.create_widgets()

        self.show_intro = True
        self.load_intro_decision()
        if self.show_intro:
            self.show_introduction_window()

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

        # New styles for improved UI
        self.style.configure('Toolbar.TFrame', background='#1c1c1c')
        self.style.configure('Toolbar.TButton', background='#3d3d3d', foreground='white', font=('Helvetica', 12, 'bold'))
        self.style.configure('Toolbar.TLabel', background='#1c1c1c', foreground='white', font=('Helvetica', 12))
        self.style.configure('Search.TEntry', font=('Helvetica', 12))

    def create_widgets(self):
        """Create and arrange main widgets."""
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.create_toolbar()
        self.create_paned_window()

    def create_toolbar(self):
        """Create toolbar with buttons and search functionality."""
        self.toolbar = Toolbar(self.main_frame)
        self.toolbar.pack(fill=tk.X)

        self.toolbar.add_button("Export", self.export_chat, position=tk.RIGHT)
        self.toolbar.add_button("Dump", self.toggle_dump_window, position=tk.RIGHT)

    def create_paned_window(self):
        """Create paned window for chat list and message area."""
        paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.create_chat_list(paned_window)
        self.create_message_area(paned_window)

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

    def create_message_area(self, parent):
        """Create scrollable message display area."""
        message_frame = ttk.Frame(parent, style='Chat.TFrame')
        parent.add(message_frame, weight=3)

        self.message_canvas = tk.Canvas(message_frame, bg='#2d2d2d')
        self.message_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.message_scrollbar = ttk.Scrollbar(message_frame, orient=tk.VERTICAL, command=self.message_canvas.yview)
        self.message_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.message_canvas.configure(yscrollcommand=self.message_scrollbar.set)
        self.message_canvas.bind('<Configure>', self.on_message_canvas_configure)

        self.message_inner_frame = ttk.Frame(self.message_canvas)
        self.message_canvas.create_window((0, 0), window=self.message_inner_frame, anchor="nw")

    def display_chats(self, chats: List[Chat]):
        """Display the list of chats in the Listbox."""
        self.threadsafe_call(self._display_chats, chats)

    def _display_chats(self, chats: List[Chat]):
        self.chat_listbox.delete(0, tk.END)
        for chat in chats:
            display_text = chat.chat_name
            self.chat_listbox.insert(tk.END, display_text)
        self.chat_listbox.update_idletasks()

    def display_messages(self, messages: List[Dict[str, Any]]):
        """Display messages for the selected chat."""
        self.threadsafe_call(self._display_messages, messages)
        self.print_conversation(messages) 

    def _display_messages(self, messages: List[Dict[str, Any]]):
        for widget in self.message_inner_frame.winfo_children():
            widget.destroy()

        for message in messages:
            self.create_message_item(message)

        self.message_inner_frame.update_idletasks()
        self.message_canvas.configure(scrollregion=self.message_canvas.bbox("all"))
        self.message_canvas.yview_moveto(1.0)  # Scroll to the bottom

    def print_conversation(self, messages: List[Dict[str, Any]]):
        """Print the entire conversation in the console."""
        print("\n--- Conversation ---")
        for message in messages:
            sender = message['phone_number']
            body = message['body']
            date = message.get('date', 'Unknown date')
            print(f"{date} - {sender}: {body}")
        print("--- End of Conversation ---\n")

    def create_message_item(self, message: Dict[str, Any]):
        """Create a single message item widget using MessageBubble."""
        # Print all string values in the message dictionary
        for key, value in message.items():
            if isinstance(value, str):
                print(f"{key}: {value}")
        is_from_me = message['phone_number'] == 'Me'  # Changed condition
        bubble_color = '#3d3d3d' if is_from_me else '#1c1c1c'  # Adjust colors as needed
        message_bubble = MessageBubble(
            self.message_inner_frame,
            sender=message['phone_number'],
            message=message['body'],
            bubble_color=bubble_color,
            y_offset=0,
            is_user=is_from_me
        )
       
        message_bubble.pack(fill=tk.X, padx=10, pady=5, anchor='e' if is_from_me else 'w')

    def on_message_canvas_configure(self, event):
        """Handle message canvas configuration event."""
        self.message_canvas.configure(scrollregion=self.message_canvas.bbox("all"))
        self.message_canvas.itemconfig(self.message_canvas.find_withtag("all")[0], width=event.width)

    def load_intro_decision(self):
        """Load user's decision about showing the intro window."""
        config_file = Path(__file__).parent / ".hermes_config.json"
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
        intro_window = tk.Toplevel(self)
        intro_window.title("Welcome to Hermes iMessage Viewer")

        welcome_message = WelcomeMessage(intro_window)
        welcome_message.pack(padx=20, pady=20)

        self.dont_show_again_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(intro_window, text="Do not show this again", variable=self.dont_show_again_var).pack(pady=10)

        ttk.Button(intro_window, text="Close", command=lambda: self.close_intro_window(intro_window)).pack(pady=10)

    def close_intro_window(self, window):
        """Close the introduction window and save user's decision."""
        self.show_intro = not self.dont_show_again_var.get()
        self.save_intro_decision()
        window.destroy()

    def save_intro_decision(self):
        """Save user's decision about showing the intro window."""
        config_file = Path(__file__).parent / ".hermes_config.json"
        try:
            with open(config_file, "w") as f:
                json.dump({"show_intro": self.show_intro}, f)
        except Exception as e:
            logging.error(f"Error saving intro decision: {e}")
            self.threadsafe_call(messagebox.showerror, "Error", "Failed to save your preference. Please try again.")

    def export_chat(self):
        """Trigger chat export event."""
        self.event_generate("<<ExportChat>>")

    def toggle_dump_window(self):
        """Trigger dump window toggle event."""
        self.event_generate("<<ToggleDumpWindow>>")

    def on_chat_selected(self, event):
        """Handle chat selection event."""
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            chat_id = index
            self.event_generate("<<ChatSelected>>", data=chat_id)

    def threadsafe_call(self, callback, *args):
        """Execute a callback in a thread-safe manner."""
        self.after(0, callback, *args)

if __name__ == "__main__":
    app = View()
    app.mainloop()
