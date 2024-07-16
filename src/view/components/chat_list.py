import tkinter as tk
from tkinter import ttk
from collections import OrderedDict

class ChatList(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, style='ChatList.TFrame', *args, **kwargs)
        self.create_widgets()
        self.selected_chats = OrderedDict()

    def create_widgets(self):
        self.chat_listbox = tk.Listbox(
            self,
            width=25,
            selectmode=tk.MULTIPLE,
            activestyle='none',
            highlightthickness=0,
            bd=0,
            relief=tk.FLAT,
            exportselection=0,
            bg='#2d2d2d',
            fg='white',
            selectbackground='#4CAF50',
            selectforeground='white',
            font=('Helvetica', 14)
        )

        self.chat_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        chat_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.chat_listbox.yview)
        chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.chat_listbox.config(yscrollcommand=chat_scrollbar.set)

        self.chat_listbox.bind('<ButtonRelease-1>', self.on_select)

    def on_select(self, event):
        selection = self.chat_listbox.curselection()
        self.selected_chats.clear()
        for index in selection:
            chat_name = self.chat_listbox.get(index)
            self.selected_chats[chat_name] = True
        self.event_generate("<<SelectionComplete>>")

    def bind_select(self, callback):
        self.bind('<<SelectionComplete>>', callback)

    def display_chats(self, chats):
        self.chat_listbox.delete(0, tk.END)
        for chat_name in chats:
            self.chat_listbox.insert(tk.END, chat_name)
        self.selected_chats.clear()

    def get_selected_chats(self):
        return list(self.selected_chats.keys())

    def clear_selection(self):
        self.chat_listbox.selection_clear(0, tk.END)
        self.selected_chats.clear()
        self.event_generate("<<SelectionComplete>>")