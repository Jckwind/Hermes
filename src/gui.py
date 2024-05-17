import tkinter as tk
from tkinter import messagebox, filedialog, font  # Import font module
from pathlib import Path
import zipfile
from text_collector import TextCollector
from components.toolbar import Toolbar
import re  # Add this at the beginning of the file if not already present

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

    def create_widgets(self):
        # Top Bar
        self.top_bar = tk.Frame(self)
        self.top_bar.pack(fill=tk.X)

        # Move the Export button to the top left
        self.export_button = tk.Button(self.top_bar, text="Export", command=self.export_conversation)
        self.export_button.pack(side=tk.LEFT)

        self.connect_button = tk.Button(self.top_bar, text="Connect", command=self.load_chats)
        self.connect_button.pack(side=tk.LEFT)

        # Entry and Listbox widgets use the custom font
        self.search_bar = tk.Entry(self.top_bar, font=self.custom_font)
        self.search_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_bar.bind("<KeyRelease>", self.filter_chats)

        # New button for exporting links
        self.export_links_button = tk.Button(self.top_bar, text="Export Links", command=self.export_links)
        self.export_links_button.pack(side=tk.LEFT)

        self.links_button = tk.Button(self.top_bar, text="Links", command=self.toggle_links)
        self.links_button.pack(side=tk.RIGHT)

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
        self.links_list = tk.Listbox(self.links_frame, width=1, height=10, font=self.custom_font)  # Width=1 because width is controlled by frame
        self.links_list.pack(fill=tk.BOTH, expand=True)

        # Add widgets to the paned window
        self.paned_window.add(self.chat_list, minsize=200)
        self.paned_window.add(self.message_text, minsize=400)
        self.paned_window.add(self.links_frame, minsize=300)

        # Initially hide the links frame
        self.paned_window.forget(self.links_frame)

        self.create_toolbar()

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

        toolbar.add_button("Export All", self.export_all_conversations)
        toolbar.add_button("Export My Texts", self.export_my_texts)

    def export_all_conversations(self):
        zip_path = filedialog.asksaveasfilename(defaultextension=".zip", initialfile="all_conversations.zip")
        if zip_path:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for chat_id, _, _ in self.chats:
                    messages = self.collector.read_messages(chat_id)
                    export_text = self.format_messages_for_export(messages)
                    zipf.writestr(f"{chat_id}.txt", export_text)
            messagebox.showinfo("Conversations Exported", f"All conversations exported to {zip_path}")

    def export_my_texts(self):
        zip_path = filedialog.asksaveasfilename(defaultextension=".zip", initialfile="my_texts.zip")
        if zip_path:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for chat_id, _, _ in self.chats:
                    messages = self.collector.read_messages(chat_id)
                    my_texts = [msg for msg in messages if msg['phone_number'] == 'Jack']
                    export_text = self.format_messages_for_export(my_texts)
                    zipf.writestr(f"{chat_id}_my_texts.txt", export_text)
            messagebox.showinfo("My Texts Exported", f"All your texts exported to {zip_path}")

    def export_conversation(self):
        selection = self.chat_list.curselection()
        if not selection:
            return

        index = selection[0]
        chat_id, chat_name, chat_identifier = self.chats[index]
        messages = self.collector.read_messages(chat_id)

        export_text = self.format_messages_for_export(messages)

        default_filename = f"{chat_name or chat_identifier}.txt"
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=default_filename)
        if file_path:
            self.save_messages_to_file(file_path, export_text)
            messagebox.showinfo("Conversation Exported", f"Conversation saved to {file_path}")

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
        print(self.chats)
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

        self.links_list.delete(0, tk.END)  # Clear previous links
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
            self.links_list.insert(tk.END, link)

        self.message_text.configure(state=tk.DISABLED)

    def export_links(self):
        selection = self.chat_list.curselection()
        if not selection:
            messagebox.showerror("Selection Error", "No chat selected.")
            return

        index = selection[0]
        chat_id, chat_name, chat_identifier = self.chats[index]

        zip_path = filedialog.asksaveasfilename(defaultextension=".zip", initialfile=f"{chat_name or chat_identifier}_links.zip")
        if zip_path:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                messages = self.collector.read_messages(chat_id)
                links = []
                url_pattern = re.compile(r'https?://\S+')
                for message in messages:
                    links.extend(url_pattern.findall(message['body']))

                if links:
                    export_text = '\n'.join(set(links))  # Use set to remove duplicates
                    zipf.writestr(f"{chat_id}_links.txt", export_text)
                else:
                    messagebox.showinfo("No Links Found", "No links found in the selected chat.")

            messagebox.showinfo("Links Exported", f"Links from {chat_name or chat_identifier} exported to {zip_path}")

if __name__ == "__main__":
    db_path = Path.home() / 'Library' / 'Messages' / 'chat.db'
    app = iMessageViewer(db_path)
    app.mainloop()
