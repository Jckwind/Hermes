import tkinter as tk
from tkinter import messagebox, filedialog
from pathlib import Path
from text_collector import TextCollector

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

    def export_conversation(self):
        selection = self.chat_list.curselection()
        if not selection:
            return

        index = selection[0]
        chat_id, chat_name, chat_identifier = self.chats[index]
        messages = self.collector.read_messages(chat_id)

        # Create formatted text for export
        export_text = ""
        for message in messages:
            sender = message['phone_number']
            content = message['body']
            time_sent = message['date']
            export_text += f"{sender}: {content} ({time_sent})\n"

        # Save file dialog
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", 
                                                initialfile=f"{chat_name}.txt")
        if file_path:
            with open(file_path, 'w') as f:
                f.write(export_text)
            messagebox.showinfo("Conversation Exported", f"Conversation saved to {file_path}")

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
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        filename = f"{chat_name}_{timestamp}.txt"
        with open(filename, 'w') as f:
            f.writelines(messages)
        messagebox.showinfo("Conversation Saved", f"Conversation saved to {filename}")

if __name__ == "__main__":
    db_path = Path.home() / 'Library' / 'Messages' / 'chat.db'
    app = iMessageViewer(db_path)
    app.mainloop()