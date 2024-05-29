import tkinter as tk
from tkinter import messagebox, filedialog, font  
from pathlib import Path
import zipfile
from text_collector import TextCollector
import re  
import webbrowser  

class iMessageViewer(tk.Tk):
    """
    Main application class for viewing iMessages.

    Attributes:
        collector (TextCollector): Object to interact with the iMessage database.
        chats (list): List of chat IDs and names.
        custom_font (tk.Font): Font used for the application.

    Methods:
        show_introduction_window(): Displays an introduction window with instructions.
        create_widgets(): Creates all the UI elements (widgets) of the application.
        analyze_conversation(): Opens the Hermes AI analysis link in a browser.
        toggle_links(): Shows/hides the pane containing extracted links from the chat.
        export_chat_and_links(): Exports the selected chat and its links to a ZIP file.
        format_messages_for_export(): Formats messages for saving to a file.
        save_messages_to_file(): Saves the given text to a file.
        filter_chats(): Filters the chat list based on the search term.
        load_chats(): Loads chats from the database and displays them in the listbox.
        display_messages(): Displays messages of the selected chat and extracts links.
        click_link(): Opens the clicked link in a browser.
        filter_links(): Filters the displayed links based on the search term.
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
        self.create_widgets()

        # Automatically load chats upon initialization
        self.load_chats()

        self.show_introduction_window()  

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

    def create_widgets(self):
        """Creates and arranges all the UI elements (widgets) of the application."""
        # Top Bar
        self.top_bar = tk.Frame(self, pady=10)
        self.top_bar.pack(fill=tk.X)

        self.export_button = tk.Button(self.top_bar, text="Export", command=self.export_chat_and_links, font=self.custom_font)
        self.export_button.pack(side=tk.LEFT)

        # Separate frame for search bars
        self.search_frame = tk.Frame(self.top_bar)
        self.search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Search bar for chats
        self.search_bar = tk.Entry(self.search_frame, font=self.custom_font)
        self.search_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_bar.bind("<KeyRelease>", self.filter_chats)

        # Analyze button
        self.analyze_button = tk.Button(self.top_bar, text="Analyze Conversation", command=self.analyze_conversation, font=self.custom_font)
        self.analyze_button.pack(side=tk.RIGHT)

        # Links button
        self.links_button = tk.Button(self.top_bar, text="Links", command=self.toggle_links, font=self.custom_font)
        self.links_button.pack(side=tk.RIGHT)

        # Main Content
        self.paned_window = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, width=50)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Chat list
        self.chat_list = tk.Listbox(self.paned_window, width=40, height=20, font=self.custom_font)
        self.chat_list.bind('<<ListboxSelect>>', self.display_messages)

        # Message area
        self.message_text = tk.Text(self.paned_window, wrap=tk.WORD, font=self.custom_font, state=tk.DISABLED)

        # Links area (initially hidden)
        self.links_frame = tk.Frame(self.paned_window)
        self.links_text = tk.Text(self.links_frame, wrap=tk.WORD, font=self.custom_font, cursor="arrow", state=tk.DISABLED)
        self.links_text.tag_configure("link", foreground="blue", underline=True)
        self.links_text.pack(fill=tk.BOTH, expand=True)

        # Add chat list and message area to the paned window
        self.paned_window.add(self.chat_list, minsize=250)
        self.paned_window.add(self.message_text, minsize=550)

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

    def load_chats(self):
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

        self.message_text.configure(state=tk.NORMAL)
        self.message_text.delete('1.0', tk.END)

        self.links_text.configure(state=tk.NORMAL)
        self.links_text.delete('1.0', tk.END) 
        url_pattern = re.compile(r'https?://\S+')
        links = set()  

        for message in messages:
            sender = message['phone_number']
            content = message['body']
            time_sent = message['date']
            message_links = url_pattern.findall(content)
            links.update(message_links)

            self.message_text.insert(tk.END, f"{sender}: {content} ({time_sent})\n\n")

        for link in links:
            self.links_text.insert(tk.END, "- " + link + "\n", "link")
            self.links_text.tag_bind("link", "<Button-1>", lambda e, url=link: self.click_link(url))

        self.message_text.configure(state=tk.DISABLED)
        self.links_text.configure(state=tk.DISABLED)

    def click_link(self, url):
        """Opens the provided URL in the default web browser."""
        webbrowser.open(url)

if __name__ == "__main__":
    db_path = Path.home() / 'Library' / 'Messages' / 'chat.db'
    app = iMessageViewer(db_path)
    app.mainloop()