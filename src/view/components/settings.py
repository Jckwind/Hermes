import tkinter as tk
from tkinter import ttk
from typing import List

class Settings(ttk.Frame):
    def __init__(self, parent, view, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.view = view
        self.create_widgets()

    def create_widgets(self):
        """Create and arrange settings widgets."""
        self._configure_styles()

        self.settings_frame = ttk.Frame(self, style="SettingsFrame.TFrame")
        self.settings_frame.pack(pady=10, padx=10, fill='x')

        self.inner_frame = ttk.Frame(self.settings_frame)
        self.inner_frame.pack(padx=2, pady=2, fill='x')

        self.label = ttk.Label(self.inner_frame, text="Settings", style="Heading.TLabel")
        self.label.pack(pady=10, anchor='center')

        # Add the folder name input section
        self.create_folder_name_input()

        # Add the chat view functionality
        self.create_chat_view()

        # Add the exported files list
        self.create_exported_files_list()

    def create_folder_name_input(self):
        """Create and configure the folder name input section."""
        folder_frame = ttk.Frame(self.inner_frame)
        folder_frame.pack(pady=10, padx=10, fill='x')

        folder_label = ttk.Label(folder_frame, text="Name your folder here:", style="SubHeading.TLabel")
        folder_label.pack(anchor='w', pady=(0, 5))

        self.folder_name_var = tk.StringVar()
        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_name_var, style='Settings.TEntry')
        folder_entry.pack(fill='x')

        # Add the submit button
        submit_button = ttk.Button(folder_frame, text="Submit", style="Settings.TButton", command=self.on_submit)
        submit_button.pack(pady=(10, 0), anchor='center')

    def create_chat_view(self):
        """Create and configure the chat view widgets."""
        self.chat_frame = ttk.Frame(self.inner_frame)
        self.chat_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(self.chat_frame, columns=("ChatName"), show="headings", selectmode="browse")
        self.tree.heading("ChatName", text="Selected Chats")
        self.tree.column("ChatName", anchor="w", width=200)
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        self.scrollbar = ttk.Scrollbar(self.chat_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill="y")

        self._bind_chat_events()

    def create_exported_files_list(self):
        """Create and configure the exported files list section."""
        exported_frame = ttk.Frame(self.inner_frame)
        exported_frame.pack(pady=10, padx=10, fill='x')

        exported_label = ttk.Label(exported_frame, text="Exported Files:", style="SubHeading.TLabel")
        exported_label.pack(anchor='w', pady=(0, 5))

        self.exported_listbox = tk.Listbox(exported_frame, selectmode=tk.SINGLE, bg='#3d3d3d', fg='white')
        self.exported_listbox.pack(fill='x', expand=True)

        self.exported_listbox.bind('<<ListboxSelect>>', self.on_exported_file_selected)

    def _bind_chat_events(self):
        """Bind events for the chat view."""
        self.tree.bind("<Double-1>", self.on_message_double_click)
        self.bind_all('<MouseWheel>', self._on_mousewheel)
        self.bind_all('<Button-4>', self._on_mousewheel)
        self.bind_all('<Button-5>', self._on_mousewheel)
        self.bind_all('<Shift-MouseWheel>', self._on_shift_mousewheel)

    def on_message_double_click(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            self.tree.delete(selected_item[0])

    def _on_mousewheel(self, event):
        """Handle mousewheel and trackpad scrolling."""
        if event.num == 4 or event.delta > 0:
            self.tree.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.tree.yview_scroll(1, "units")
        else:
            self.tree.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_shift_mousewheel(self, event):
        """Handle horizontal scrolling with Shift + mousewheel."""
        if event.delta > 0:
            self.tree.xview_scroll(-1, "units")
        elif event.delta < 0:
            self.tree.xview_scroll(1, "units")
        
    def get_displayed_chats(self) -> List[str]:
        """Retrieve the list of chat names currently displayed in the Treeview."""
        return [self.tree.item(item, "values")[0] for item in self.tree.get_children()]

    def clear_messages(self):
        """Clear all messages in the chat view."""
        for item in self.tree.get_children():
            self.tree.delete(item)

    def _configure_styles(self):
        """Configure custom styles for widgets."""
        style = ttk.Style()
        style.configure("Heading.TLabel", font=('Helvetica', 16, 'bold'), foreground='#4CAF50', padding=10, background='#2d2d2d')
        style.configure("SubHeading.TLabel", font=('Helvetica', 12, 'bold'), foreground='white', background='#2d2d2d')
        style.configure("Settings.TButton", font=('Helvetica', 10, 'bold'), padding=5, background='#4CAF50', foreground='white')
        style.configure("Settings.TEntry", font=('Helvetica', 10), padding=5, background='#3d3d3d', foreground='white')

    def on_submit(self):
        """Handle submit button click."""
        # This method is a placeholder for future functionality
        folder_name = self.folder_name_var.get()
        print(f"Submitted folder name: {folder_name}")

    def start_export(self):
        """Start the export process."""
        self.view.event_generate("<<StartExport>>")

    def start_upload(self):
        """Start the Google Drive upload process."""
        self.view.event_generate("<<StartGoogleDriveUpload>>")

    def reset_application(self):
        """Reset the application."""
        self.view.event_generate("<<ResetApplication>>")

    def display_chat_name(self, chat_name: str):
        """Display the chat name in the message area."""
        if not self.tree.exists(chat_name):
            self.tree.insert("", "end", iid=chat_name, values=(chat_name,))

    def remove_chat_name(self, chat_name: str):
        """Remove the chat name from the message area."""
        if self.tree.exists(chat_name):
            self.tree.delete(chat_name)

    def display_chats(self, chat_names: List[str]):
        """Display the list of chat names in the Treeview."""
        self.clear_messages()
        for chat_name in chat_names:
            self.display_chat_name(chat_name)

    def on_exported_file_selected(self, event):
        """Handle exported file selection event."""
        selection = self.exported_listbox.curselection()
        if selection:
            index = selection[0]
            filename = self.exported_listbox.get(index)
            self.view.event_generate("<<ExportedFileSelected>>")
            self.view.selected_exported_file = filename

    def update_exported_files_list(self, filenames):
        """Update the list of exported files."""
        self.exported_listbox.delete(0, tk.END)
        for filename in filenames:
            self.exported_listbox.insert(tk.END, filename)