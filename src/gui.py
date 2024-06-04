import tkinter as tk
from tkinter import messagebox, filedialog, font, ttk, Canvas, Text, Frame, Label
from pathlib import Path
import zipfile
from text_collector import TextCollector
import re
import json
import webbrowser

class iMessageViewer(tk.Tk):
    """
    Main application class for viewing iMessages.

    Attributes:
        collector (TextCollector): Object to interact with the iMessage database.
        chats (list): List of chat IDs and names.
        custom_font (tk.Font): Font used for the application.
        show_intro (bool): Flag to control whether to show the introduction window.

    Methods:
        show_introduction_window(): Displays an introduction window with instructions.
        create_widgets(): Creates all the UI elements (widgets) of the application.
        analyze_conversation(): Opens the Hermes AI analysis link in a browser.
        toggle_links(): Shows/hides the pane containing extracted links from the chat.
        export_chat_and_links(): Exports the selected chat and its links to a ZIP file.
        format_messages_for_export(): Formats messages for saving to a file.
        save_messages_to_file(): Saves the given text to a file.
        filter_chats(): Filters the chat list based on the search term.
        load_contacts(): Loads contacts from the database and displays them in the listbox.
        display_messages(): Displays messages of the selected chat and extracts links.
        click_link(): Opens the clicked link in a browser.
        filter_links(): Filters the displayed links based on the search term.
        create_message_bubble(text_area, text, sender, x, y, bubble_color): Creates a message bubble on the canvas.
    """
    def __init__(self, db_path):
        super().__init__()
        self.title('Hermes iMessage Viewer')
        self.geometry('1200x700')  # Increased window size

        # Set up the font
        self.custom_font = font.Font(family="Arial", size=14)  # Modern font, larger size

        self.collector = TextCollector(db_path)
        if not self.collector.conn:
            messagebox.showerror("Database Error", "Cannot connect to the iMessage database.")
            self.destroy()
            return

        self.chats = []
        self.show_intro = True  # Initialize the flag
        self.create_widgets()

        # Automatically load chats upon initialization
        self.load_contacts()

        self.load_intro_decision()  # Load the stored decision
        if self.show_intro:
            self.show_introduction_window()

    def load_intro_decision(self):
        """Loads the "Do not show again" decision from a configuration file."""
        config_file = Path(__file__).parent / ".hermes_config.json"  # Use the script's directory
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    data = json.load(f)
                    self.show_intro = not data.get("show_intro", True)  # Default to True if key not found
            except Exception as e:
                print(f"Error loading intro decision: {e}")

    def show_introduction_window(self):
        """Displays a window with instructions on how to use the application."""
        introduction_window = tk.Toplevel(self)
        introduction_window.title("Welcome to Hermes iMessage Viewer")

        instructions_label = tk.Label(introduction_window,
                                       text="Instructions:\n"
                                            "1. Click on a conversation (either a group chat or a single chat) to view past iMessages.\n"
                                            "2. Click on the 'Links' button to view links sent within that chat.\n"
                                            "3. Click on the 'Export' button to save the selected conversation to .txt files on your computer.\n"
                                            "   Two files will be saved: one for the conversation and one for the links.\n"
                                            "4. Click the 'Analyze Conversation' button to be redirected to Google Gemini,\n"
                                            "   an AI powered by Google. You can analyze conversations there.",
                                       font=self.custom_font,  # Use the custom font
                                       wraplength=400)  # Wrap long lines
        instructions_label.pack(padx=20, pady=20)

        # "Do not show again" checkbox
        self.dont_show_again_var = tk.BooleanVar(value=False)
        dont_show_again_checkbox = tk.Checkbutton(introduction_window,
                                                 text="Do not show this again",
                                                 variable=self.dont_show_again_var,
                                                 font=self.custom_font)
        dont_show_again_checkbox.pack(pady=10)

        def close_intro_window():
            self.show_intro = not self.dont_show_again_var.get()  # Update the flag
            self.save_intro_decision()  # Save the decision
            introduction_window.destroy()

        close_button = tk.Button(introduction_window, text="Close", command=close_intro_window, font=self.custom_font)
        close_button.pack(pady=10)

    def save_intro_decision(self):
        """Saves the "Do not show again" decision to a configuration file."""
        config_file = Path(__file__).parent / ".hermes_config.json"  # Use the script's directory
        try:
            with open(config_file, "w") as f:
                json.dump({"show_intro": not self.show_intro}, f)  # Write "true" or "false"
        except Exception as e:
            print(f"Error saving intro decision: {e}")

    def create_widgets(self):
        """Creates and arranges all the UI elements (widgets) of the application."""
        # Top Bar
        self.top_bar = tk.Frame(self, pady=10)
        self.top_bar.pack(fill=tk.X)

        # Create a style for the buttons
        style = ttk.Style()
        style.configure("TButton", font=self.custom_font, padding=10)

        # Export Button
        self.export_button = ttk.Button(self.top_bar, text="Export", command=self.export_chat_and_links, style="TButton")
        self.export_button.pack(side=tk.LEFT, padx=5)

        # Separate frame for search bars
        self.search_frame = tk.Frame(self.top_bar)
        self.search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Search bar for chats
        self.search_bar = tk.Entry(self.search_frame, font=self.custom_font)
        self.search_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_bar.bind("<KeyRelease>", self.filter_chats)  # Bind to KeyRelease event

        # Analyze Button
        self.analyze_button = ttk.Button(self.top_bar, text="Analyze Conversation", command=self.analyze_conversation, style="TButton")
        self.analyze_button.pack(side=tk.RIGHT, padx=5)

        # Links Button
        self.links_button = ttk.Button(self.top_bar, text="Links", command=self.toggle_links, style="TButton")
        self.links_button.pack(side=tk.RIGHT, padx=5)

        # Main Content
        self.paned_window = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, width=50)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Immesage Windo
        self.chat_list = tk.Listbox(self.paned_window, width=40, height=20, font=self.custom_font)
        self.chat_list.bind('<<ListboxSelect>>', self.display_messages)
        self.chat_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Message area
        self.message_frame = tk.Frame(self.paned_window)
        self.message_canvas = tk.Canvas(self.message_frame, width=600, height=400, bg="lightgray")
        
        self.message_canvas.pack(fill=tk.BOTH, expand=True)

        # Links area (initially hidden)
        self.links_frame = tk.Frame(self.paned_window)
        self.links_text = tk.Text(self.links_frame, wrap=tk.WORD, font=self.custom_font, cursor="arrow", state=tk.DISABLED)
        self.links_text.tag_configure("link", foreground="white", underline=True, background="blue")  # White text on blue background
        self.links_text.pack(fill=tk.BOTH, expand=True)

        # Add chat list and message area to the paned window
        self.paned_window.add(self.chat_list, minsize=250)
        self.paned_window.add(self.message_frame, minsize=550)

    def analyze_conversation(self):
        """Opens the Google Gemini webpage in the default web browser."""
        webbrowser.open("https://gemini.google.com/app")

    def toggle_links(self):
        """
        Toggles the visibility of the links frame in the paned window.
        If visible, it hides the frame; otherwise, it adds the frame.
        """
        if self.links_frame.winfo_ismapped():
            self.paned_window.forget(self.links_frame)
        else:
            self.paned_window.add(self.links_frame, minsize=250)

    def export_chat_and_links(self):
        """
        Exports the selected chat messages and extracted links to separate .txt files
        within a .zip archive.
        """
        selection = self.chat_list.curselection()
        if not selection:
            messagebox.showerror("Selection Error", "No chat selected.")
            return

        index = selection[0]
        chat_id, chat_name, chat_identifier = self.chats[index]

        default_filename = f"{chat_name or chat_identifier}_chat_and_links.zip"
        zip_path = filedialog.asksaveasfilename(
            defaultextension=".zip", initialfile=default_filename,
            filetypes=(("ZIP files", "*.zip"), ("all files", "*.*"))
        )

        if zip_path:
            try:
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    messages = self.collector.read_messages(chat_id)
                    export_text = self.format_messages_for_export(messages)
                    zipf.writestr(f"{chat_id}_chat.txt", export_text)

                    links = []
                    url_pattern = re.compile(r'https?://\S+')
                    for message in messages:
                        links.extend(url_pattern.findall(message['body']))

                    if links:
                        export_links_text = '\n'.join(set(links))
                        zipf.writestr(f"{chat_id}_links.txt", export_links_text)
                    else:
                        messagebox.showinfo("No Links Found", "No links found in the selected chat.")

                messagebox.showinfo("Export Successful", f"Chat and links from {chat_name or chat_identifier} exported to {zip_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"An error occurred during export: {str(e)}")

    def format_messages_for_export(self, messages):
        """Formats a list of messages into a string suitable for saving to a text file."""
        export_text = ""
        for message in messages:
            sender = message['phone_number']
            content = message['body']
            time_sent = message['date']
            export_text += f"{sender}: {content} ({time_sent})\n"
        return export_text

    def filter_chats(self, event=None):
        """
        Filters the chat list based on the text entered in the search bar.
        """
        search_term = self.search_bar.get().lower()
        self.chat_list.delete(0, tk.END)

        for _, chat_name, chat_identifier in self.chats:
            display_name = f'{chat_identifier}' if not chat_name else f'{chat_name}'
            if search_term in display_name.lower():
                self.chat_list.insert(tk.END, display_name)

    def load_contacts(self):
        """Loads chats from the database and populates the chat listbox."""
        self.chat_list.delete(0, tk.END)
        
        self.chats = self.collector.get_all_chat_ids_with_labels()
       
        self.filter_chats()

    def display_messages(self, event):
        """
        Displays messages of the selected chat and extracts links, making them clickable.
        """
        selection = self.chat_list.curselection()
        if not selection:
            return

        index = selection[0]
        chat_id, chat_name, chat_identifier = self.chats[index]
        messages = self.collector.read_messages(chat_id)

        # Clear previous messages from a different conversation 
        for widget in self.message_frame.winfo_children():
            widget.destroy()

        self.links_text.configure(state=tk.NORMAL)
        self.links_text.delete('1.0', tk.END)
        url_pattern = re.compile(r'https?://\S+')
        links = set()

        # --- Create Scrollbar (outside the canvas) ---
        self.scrollbar = tk.Scrollbar(self.message_frame, orient="vertical")
        self.scrollbar.pack(side="right", fill="y")

        # --- Create Message Canvas (with scrollbar tied to it) ---
        self.message_canvas = Canvas(self.message_frame, width=600, height=400, bg="lightgray")
        self.message_canvas.pack(side="left", fill="both", expand=True)
        self.message_canvas.config(yscrollcommand=self.scrollbar.set)

        self.scrollbar.config(command=self.message_canvas.yview)

        # --- Insert Messages with Canvas Bubbles ---
        y_offset = 10  # Initial vertical offset
        message_height = 30  # Approximate height of a message
        bubbles = []  # List to store BotBubble objects

        for message in messages:
            sender = message['phone_number']
            content = message['body']
            time_sent = message['date']
            message_links = url_pattern.findall(content)
            links.update(message_links)

            # Determine the bubble tag based on sender
            if sender == "Me":
                bubble_color = "lightblue"
            else:
                bubble_color = "lightgray"

            # Create a BotBubble object
            bubble = BotBubble(self.message_canvas, sender, content, bubble_color, y_offset)
            bubbles.append(bubble)

            # Update the vertical offset for the next message
            y_offset += bubble.height + 10  # Add space between messages

        # --- Handle Links ---
        for link in links:
            self.links_text.insert(tk.END, "- " + link + "\n", "link")
            self.links_text.tag_bind("link", "<Button-1>", lambda e, url=link: self.click_link(url))

        self.links_text.configure(state=tk.DISABLED)

        # --- Update Canvas Height ---
        self.message_canvas.config(height=y_offset)  # Update height based on y_offset

        # --- Enable Scrolling ---
        self.message_canvas.configure(scrollregion=self.message_canvas.bbox("all"))

        # --- Wrap Text (ONLY THE LINKS TEXT) ---
        # Wrap the text in the message area
        self.links_text.tag_configure("all", wrap=tk.WORD)

    def click_link(self, url):
        """Opens the provided URL in the default web browser."""
        webbrowser.open(url)

    def _scroll_canvas(self, *args):
        """Scrolls the canvas based on the scrollbar's position."""
        self.message_canvas.yview(*args)

class BotBubble:
    def __init__(self, master, sender, message, bubble_color, y_offset):
        self.master = master
        self.frame = Frame(master, bg=bubble_color)
        self.i = self.master.create_window(10, y_offset, anchor="nw", window=self.frame)
        Label(self.frame, text=sender, font=("Helvetica", 9), bg=bubble_color).grid(row=0, column=0, sticky="w", padx=5)
        Label(self.frame, text=message, font=("Helvetica", 9), bg=bubble_color).grid(row=1, column=0, sticky="w", padx=5, pady=3)
        self.master.update_idletasks()  # Update to get accurate dimensions
        self.height = self.master.bbox(self.i)[3] - self.master.bbox(self.i)[1]  # Calculate height after creation

    def draw_triangle(self, widget):
        x1, y1, x2, y2 = self.master.bbox(widget)
        return x1, y2 - 10, x1 - 15, y2 + 10, x1, y2

if __name__ == "__main__":
    db_path = Path.home() / 'Library' / 'Messages' / 'chat.db'
    app = iMessageViewer(db_path)
    app.mainloop()