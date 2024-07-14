import tkinter as tk
from tkinter import ttk

class ChatList(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, style='ChatList.TFrame', *args, **kwargs)
        self.create_widgets()

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

        # Bind events for better selection experience
        self.chat_listbox.bind('<Button-1>', self.on_click)
        self.chat_listbox.bind('<B1-Motion>', self.on_drag)
        self.chat_listbox.bind('<ButtonRelease-1>', self.on_release)

    def on_click(self, event):
        self.start_index = self.chat_listbox.nearest(event.y)
        if self.chat_listbox.selection_includes(self.start_index):
            self.chat_listbox.selection_clear(self.start_index)
        else:
            self.chat_listbox.selection_set(self.start_index)

    def on_drag(self, event):
        cur_index = self.chat_listbox.nearest(event.y)
        if cur_index != self.start_index:
            if self.chat_listbox.selection_includes(self.start_index):
                self.chat_listbox.selection_set(min(self.start_index, cur_index), max(self.start_index, cur_index))
            else:
                self.chat_listbox.selection_clear(min(self.start_index, cur_index), max(self.start_index, cur_index))
            self.start_index = cur_index

    def on_release(self, event):
        pass  # You can add any additional logic here if needed

    def bind_select(self, callback):
        self.chat_listbox.bind('<<ListboxSelect>>', callback)

    def display_chats(self, chats):
        self.chat_listbox.delete(0, tk.END)
        for chat_name in chats:
            self.chat_listbox.insert(tk.END, chat_name)
        self.chat_listbox.update_idletasks()

    def get_selected_chats(self):
        selection = self.chat_listbox.curselection()
        return [self.chat_listbox.get(index) for index in selection]
