import tkinter as tk
from tkinter import ttk
from collections import OrderedDict

class ChatList(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, style='ChatList.TFrame', *args, **kwargs)
        self.create_widgets()
        self.selected_chats = OrderedDict()  # Use OrderedDict to maintain order
        self.is_selecting = False

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

        self.chat_listbox.bind('<ButtonPress-1>', self.on_press)
        self.chat_listbox.bind('<B1-Motion>', self.on_motion)
        self.chat_listbox.bind('<ButtonRelease-1>', self.on_release)

    def on_press(self, event):
        self.is_selecting = True
        self.toggle_selection(self.chat_listbox.nearest(event.y))

    def on_motion(self, event):
        if self.is_selecting:
            self.toggle_selection(self.chat_listbox.nearest(event.y))

    def on_release(self, event):
        self.is_selecting = False
        self.event_generate("<<SelectionComplete>>")

    def toggle_selection(self, index):
        chat_name = self.chat_listbox.get(index)
        if chat_name in self.selected_chats:
            del self.selected_chats[chat_name]
            self.chat_listbox.selection_clear(index)
        else:
            self.selected_chats[chat_name] = True
            self.chat_listbox.selection_set(index)

    def bind_select(self, callback):
        self.bind('<<SelectionComplete>>', callback)

    def display_chats(self, chats):
        self.chat_listbox.delete(0, tk.END)
        for chat_name in chats:
            self.chat_listbox.insert(tk.END, chat_name)
        self.selected_chats.clear()
        self.chat_listbox.selection_clear(0, tk.END)

    def get_selected_chats(self):
        return list(self.selected_chats.keys())