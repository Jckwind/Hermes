import tkinter as tk
from tkinter import ttk
from typing import List, Set

class ChatList(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, style='ChatList.TFrame', *args, **kwargs)
        self.create_widgets()
        self.selected_chats: Set[str] = set()
        self.all_chats: List[str] = []
        self.displayed_chats: List[str] = []

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
        self.chat_listbox.bind('<<ListboxSelect>>', self.on_select)

    def on_select(self, event):
        selection = self.chat_listbox.curselection()
        newly_selected = set(self.displayed_chats[i] for i in selection)
        
        # Toggle selection status
        for chat in self.displayed_chats:
            if chat in newly_selected and chat not in self.selected_chats:
                self.selected_chats.add(chat)
            elif chat not in newly_selected and chat in self.selected_chats:
                self.selected_chats.remove(chat)
        
        self.selected_chats.intersection_update(set(self.all_chats))
        
        # Update the listbox selection to reflect the current state
        self.update_listbox_selection()
        
        self.event_generate("<<SelectionComplete>>")

    def update_listbox_selection(self):
        self.chat_listbox.selection_clear(0, tk.END)
        for i, chat in enumerate(self.displayed_chats):
            if chat in self.selected_chats:
                self.chat_listbox.selection_set(i)

    def display_chats(self, chats: List[str]):
        self.displayed_chats = chats
        self.chat_listbox.delete(0, tk.END)
        for chat in chats:
            self.chat_listbox.insert(tk.END, chat)
        self.update_listbox_selection()

    def set_all_chats(self, chats: List[str]):
        self.all_chats = chats
        self.display_chats(chats)

    def get_selected_chats(self) -> List[str]:
        return list(self.selected_chats)

    def clear_selection(self):
        self.chat_listbox.selection_clear(0, tk.END)
        self.selected_chats.clear()
        self.event_generate("<<SelectionComplete>>")