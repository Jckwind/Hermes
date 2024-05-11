import tkinter as tk
from tkinter import messagebox, filedialog
from pathlib import Path
import zipfile
from text_collector import TextCollector
from components.toolbar import Toolbar

class iMessageViewer(tk.Tk):
    def __init__(self, db_path):
        super().__init__()
        self.title('Hermes iMessage Viewer')
        self.geometry('1000x600')

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

        self.connect_button = tk.Button(self.top_bar, text="Connect", command=self.load_chats)
        self.connect_button.pack(side=tk.LEFT)

        self.search_bar = tk.Entry(self.top_bar)
        self.search_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_bar.bind("<KeyRelease>", self.filter_chats)

        # Main Content
        self.paned_window = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=1)

        self.chat_list = tk.Listbox(self, width=50, height=2)
        self.chat_list.bind('<<ListboxSelect>>', self.display_messages)
        self.paned_window.add(self.chat_list)

        self.message_text = tk.Text(self, wrap=tk.WORD)
        self.paned_window.add(self.message_text)

        self.export_button = tk.Button(self.top_bar, text="Export", command=self.export_conversation)
        self.export_button.pack(side=tk.LEFT)

        # Configure Listbox for easier selection
        self.chat_list.configure(exportselection=False)
        self.create_toolbar()

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

        self.message_text.configure(state=tk.NORMAL)  # Make the Text widget editable
        self.message_text.delete('1.0', tk.END)

        # Improved formatting with tags for sender and time
        if chat_name == "":
            self.message_text.insert(tk.END, f"chat id: {chat_identifier}\n")  
        else:
            self.message_text.insert(tk.END, f"{chat_name}\n")  
        for message in messages:
            sender = message['phone_number']
            content = message['body']
            time_sent = message['date']

            # Add sender with bold tag
            self.message_text.insert(tk.END, f"{sender}: ", 'sender')  
            
            # Add content 
            self.message_text.insert(tk.END, f"{content}\n", 'body')

            # Add time sent with gray tag on a new line
            self.message_text.insert(tk.END, f"\t{time_sent}\n", 'time')  

        self.message_text.configure(state=tk.DISABLED)  # Make the Text widget read-only

        # Define tags for styling 
        self.message_text.tag_config('body', font=('Arial', 15, 'bold'))
        self.message_text.tag_config('time', foreground='gray', font=('Arial', 10, 'italic'))

    def save_conversation(self, chat_name, messages):
        """Saves the conversation to a .txt file with a timestamp to differentiate versions."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%m-%Y_%H-M")
        filename = f"{chat_name}_{timestamp}.dump.txt"
        with open(filename, 'w') as f:
            f.writelines(messages)
        messagebox.showinfo("Conversation Saved", f"Conversation saved to {filename}")

if __name__ == "__main__":
    db_path = Path.home() / 'Library' / 'Messages' / 'chat.db'
    app = iMessageViewer(db_path)
    app.mainloop()