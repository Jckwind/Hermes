import tkinter as tk
from tkinter import messagebox, filedialog, font  
from pathlib import Path
import zipfile
from text_collector import TextCollector
from components.toolbar import Toolbar
import re  
import webbrowser  

class iMessageViewer(tk.Tk):
    def __init__(self, db_path):
        super().__init__()
        self.title('Hermes iMessage Viewer')
        self.geometry('1000x600')

        # Set up the font
        self.custom_font = font.Font(family="Times New Roman", size=12)  # Define the font

        self.collector = TextCollector(db_path)
        if not self.collector.conn:
            messagebox.showerror("Database Error", "Cannot connect to the iMessage database.")
            self.destroy()
            return

        self.chats = []
        self.create_widgets()

        # Automatically load chats upon initialization
        self.load_chats()

    def create_widgets(self):
        # Top Bar
        self.top_bar = tk.Frame(self)
        self.top_bar.pack(fill=tk.X)

        # Update the remaining button to handle both export functionalities
        self.export_button = tk.Button(self.top_bar, text="Export", command=self.export_chat_and_links)
        self.export_button.pack(side=tk.LEFT)

        # Entry and Listbox widgets use the custom font
        self.search_bar = tk.Entry(self.top_bar, font=self.custom_font)
        self.search_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_bar.bind("<KeyRelease>", self.filter_chats)
        
        self.search_bar_links = tk.Entry(self.top_bar, font=self.custom_font)
        self.search_bar_links.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_bar_links.bind("<KeyRelease>", self.filter_links)
        
        self.links_button = tk.Button(self.top_bar, text="Links", command=self.toggle_links)
        self.links_button.pack(side=tk.RIGHT)

        # New button for analyzing conversation
        self.analyze_button = tk.Button(self.top_bar, text="Analyze Conversation", command=self.analyze_conversation)
        self.analyze_button.pack(side=tk.RIGHT)

        # Main Content
        self.paned_window = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        self.paned_window.pack(fill=tk.BOTH, expand=1)

        # Chat list and links list use the custom font
        self.chat_list = tk.Listbox(self, width=50, height=2, font=self.custom_font)
        self.chat_list.bind('<<ListboxSelect>>', self.display_messages)

        # Define the message text area
        self.message_text = tk.Text(self, wrap=tk.WORD, font=self.custom_font)  # Apply the font here

        # Define the links list frame
        self.links_frame = tk.Frame(self, width=300)  # Set a fixed width for the links frame
        self.links_text = tk.Text(self.links_frame, width=1, height=10, font=self.custom_font, cursor="arrow")
        self.links_text.tag_configure("link", foreground="white", underline=True)
        self.links_text.pack(fill=tk.BOTH, expand=True)

        # Add widgets to the paned window
        self.paned_window.add(self.chat_list, minsize=200)
        self.paned_window.add(self.message_text, minsize=400)
        self.paned_window.add(self.links_frame, minsize=300)

        # Initially hide the links frame
        self.paned_window.forget(self.links_frame)

        self.create_toolbar()

    def analyze_conversation(self):
        """Open the analysis link."""
        webbrowser.open("https://gemini.google.com/app")

    def toggle_links(self):
        if self.links_frame.winfo_ismapped():
            self.paned_window.forget(self.links_frame)
            # Increase the minsize of other panes if necessary
            self.paned_window.paneconfigure(self.chat_list, minsize=250)
            self.paned_window.paneconfigure(self.message_text, minsize=550)
        else:
            self.paned_window.add(self.links_frame)
            # Adjust back when links are shown
            self.paned_window.paneconfigure(self.chat_list, minsize=200)
            self.paned_window.paneconfigure(self.message_text, minsize=400)
            self.paned_window.paneconfigure(self.links_frame, minsize=300)

    def create_toolbar(self):
        toolbar = Toolbar(self)

    def export_chat_and_links(self):
        selection = self.chat_list.curselection()
        if not selection:
            messagebox.showerror("Selection Error", "No chat selected.")
            return

        index = selection[0]
        chat_id, chat_name, chat_identifier = self.chats[index]

        zip_path = filedialog.asksaveasfilename(defaultextension=".zip", initialfile=f"{chat_name or chat_identifier}_chat_and_links.zip")
        if zip_path:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                messages = self.collector.read_messages(chat_id)
                export_text = self.format_messages_for_export(messages)
                zipf.writestr(f"{chat_id}_chat.txt", export_text)

                links = []
                url_pattern = re.compile(r'https?://\S+')
                for message in messages:
                    links.extend(url_pattern.findall(message['body']))

                if links:
                    export_links_text = '\n'.join(set(links))  # Use set to remove duplicates
                    zipf.writestr(f"{chat_id}_links.txt", export_links_text)
                else:
                    messagebox.showinfo("No Links Found", "No links found in the selected chat.")

            messagebox.showinfo("Chat and Links Exported", f"Chat and links from {chat_name or chat_identifier} exported to {zip_path}")

    def format_messages_for_export(self, messages):
        export_text = ""
        for message in messages:
            sender = message['phone_number']
            content = message['body']
            time_sent = message['date']
            export_text += f"{sender}: {content} ({time_sent})\n"
        return export_text

    def save_messages_to_file(self, file_path, export_text):
        with open(file_path, 'w') as f:
            f.write(export_text)

    def filter_chats(self, event=None):
        """Filters the chat list based on search input."""
        search_term = self.search_bar.get().lower()
        self.chat_list.delete(0, tk.END)
        
        for _, chat_name, chat_identifier in self.chats:
            display_name = f'{chat_identifier}' if chat_name == "" else f'{chat_name}'
            if chat_name is None and chat_identifier is None:
                continue
            if search_term == "" or search_term in display_name.lower():
                self.chat_list.insert(tk.END, display_name)

    def load_chats(self):
        """Loads chats ordered by recent activity and updates listbox with contact name or chat ID."""
        self.chat_list.delete(0, tk.END)  
        self.chats = self.collector.get_all_chat_ids_with_labels()
    
        self.filter_chats()  # Apply filtering after loading

    def display_messages(self, event):
        selection = self.chat_list.curselection()
        if not selection:
            return

        index = selection[0]
        chat_id, chat_name, chat_identifier = self.chats[index]
        messages = self.collector.read_messages(chat_id)

        self.message_text.configure(state=tk.NORMAL)
        self.message_text.delete('1.0', tk.END)

        self.links_text.configure(state=tk.NORMAL)
        self.links_text.delete('1.0', tk.END)  # Clear previous links
        url_pattern = re.compile(r'https?://\S+')
        links = set()  # Use a set to avoid duplicate links

        for message in messages:
            sender = message['phone_number']
            content = message['body']
            time_sent = message['date']
            message_links = url_pattern.findall(content)
            links.update(message_links)

            # Display message in the main text widget with an extra newline for spacing
            self.message_text.insert(tk.END, f"{sender}: {content} ({time_sent})\n\n")

        # Add links to the links list
        for link in links:
            print(f"Adding link: {link}")  # Debugging print
            start_index = self.links_text.index(tk.END)
            self.links_text.insert(tk.END, link + "\n\n", "link")  # Two newlines for separation
            end_index = self.links_text.index(tk.END)
            self.links_text.tag_add(link, start_index, end_index)
            self.links_text.tag_bind(link, "<Button-1>", lambda e, url=link: self.click_link(url))

        self.message_text.configure(state=tk.DISABLED)
        self.links_text.configure(state=tk.DISABLED)

    def click_link(self, url):
        """Open the link if clicked."""
        webbrowser.open(url)

    def filter_links(self, event=None):
        """Filters the links list based on search input."""
        search_term = self.search_bar_links.get().lower()
        self.links_text.configure(state=tk.NORMAL)
        self.links_text.delete('1.0', tk.END)

        selection = self.chat_list.curselection()
        if not selection:
            return

        index = selection[0]
        chat_id, chat_name, chat_identifier = self.chats[index]
        messages = self.collector.read_messages(chat_id)

        url_pattern = re.compile(r'https?://\S+')
        links = set()  # Use a set to avoid duplicate links

        for message in messages:
            content = message['body']
            message_links = url_pattern.findall(content)
            links.update(message_links)

        for link in links:
            if search_term in link.lower():
                start_index = self.links_text.index(tk.END)
                self.links_text.insert(tk.END, link + "\n\n", "link")  
                end_index = self.links_text.index(tk.END)
                self.links_text.tag_add(link, start_index, end_index)
                self.links_text.tag_bind(link, "<Button-1>", lambda e, url=link: self.click_link(url))

        self.links_text.configure(state=tk.DISABLED)

if __name__ == "__main__":
    db_path = Path.home() / 'Library' / 'Messages' / 'chat.db'
    app = iMessageViewer(db_path)
    app.mainloop()
