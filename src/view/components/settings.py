import tkinter as tk
from tkinter import ttk
from typing import List, Tuple
from collections import OrderedDict

class Settings(ttk.Frame):
    def __init__(self, parent, view, *args, **kwargs):
        super().__init__(parent, style='Settings.TFrame', *args, **kwargs)
        self.view = view
        self.create_widgets()
        self.chat_cache = OrderedDict()

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
        self.folder_frame = ttk.Frame(self.inner_frame)
        self.folder_frame.pack(pady=10, padx=10, fill='x')

        folder_label = ttk.Label(self.folder_frame, text="Name your folder here:", style="SubHeading.TLabel")
        folder_label.pack(anchor='w', pady=(0, 5))

        self.folder_name_var = tk.StringVar(value="")
        self.folder_entry = ttk.Entry(self.folder_frame, textvariable=self.folder_name_var, style='Settings.TEntry')
        self.folder_entry.pack(fill='x')

        self.save_button = ttk.Button(self.folder_frame, text="Save", style="Settings.TButton", command=self.on_save)
        self.save_button.pack(pady=(10, 0), anchor='center')

        # Initially hide the folder name input
        self.folder_frame.pack_forget()

    def show_folder_name_input(self):
        """Show the folder name input section."""
        self.folder_frame.pack(pady=10, padx=10, fill='x')

    def hide_folder_name_input(self):
        """Hide the folder name input section."""
        self.folder_frame.pack_forget()

    def on_save(self):
        """Handle save button click."""
        folder_name = self.folder_name_var.get()
        if folder_name:
            self.view.event_generate("<<SaveExport>>")
        else:
            # Show an error message if the folder name is empty
            self.view.show_error("Invalid Folder Name", "Please enter a valid folder name.")

    def create_chat_view(self):
        """Create and configure the chat view widgets."""
        self.chat_frame = ttk.Frame(self.inner_frame)
        self.chat_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(self.chat_frame, columns=("ChatName"), show="headings", selectmode="none")
        self.tree.heading("ChatName", text="Selected Chats")
        self.tree.column("ChatName", anchor="w", width=200)
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        self.scrollbar = ttk.Scrollbar(self.chat_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill="y")

    def update_selected_chats(self, chat_names: List[str]):
        """Update the list of selected chats efficiently."""
        new_chats = OrderedDict((name, True) for name in chat_names)
        
        # Remove chats that are no longer selected
        for chat_name in list(self.chat_cache.keys()):
            if chat_name not in new_chats:
                self.tree.delete(chat_name)
                del self.chat_cache[chat_name]
        
        # Add newly selected chats
        for chat_name in new_chats:
            if chat_name not in self.chat_cache:
                self.tree.insert("", "end", iid=chat_name, values=(chat_name,))
                self.chat_cache[chat_name] = True

    def get_displayed_chats(self) -> List[str]:
        """Retrieve the list of chat names currently displayed in the Treeview."""
        return list(self.chat_cache.keys())

    def clear_messages(self):
        """Clear all messages in the chat view."""
        self.tree.delete(*self.tree.get_children())
        self.chat_cache.clear()

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

    def on_exported_file_selected(self, event):
        """Handle exported file selection event."""
        selection = self.exported_listbox.curselection()
        if selection:
            index = selection[0]
            full_path = self.exported_listbox.get(index)
            subdir, filename = full_path.split(" / ")
            self.view.selected_exported_file = (subdir, filename)
            self.view.event_generate("<<ExportedFileSelected>>")

    def update_exported_files_list(self, filenames: List[Tuple[str, str]]):
        """Update the list of exported files."""
        self.exported_listbox.delete(0, tk.END)
        for subdir, filename in filenames:
            self.exported_listbox.insert(tk.END, f"{subdir} / {filename}")

    def clear_exported_files_list(self):
        """Clear the exported files list."""
        self.exported_listbox.delete(0, tk.END)

    def create_exported_files_list(self):
        """Create and configure the exported files list section."""
        exported_frame = ttk.Frame(self.inner_frame)
        exported_frame.pack(pady=10, padx=10, fill='x')

        exported_label = ttk.Label(exported_frame, text="Exported Files:", style="SubHeading.TLabel")
        exported_label.pack(anchor='w', pady=(0, 5))

        self.exported_listbox = tk.Listbox(exported_frame, selectmode=tk.SINGLE, bg='#3d3d3d', fg='white')
        self.exported_listbox.pack(fill='x', expand=True)

        self.exported_listbox.bind('<<ListboxSelect>>', self.on_exported_file_selected)