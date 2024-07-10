from typing import List, Dict
from model.model import Model
from view.view import View
from model.text_collection.chat import Chat
import os
import time
from tkinter import filedialog, simpledialog
import subprocess  # Add this import

class Controller:
    """Controller class for managing interactions between Model and View."""

    def __init__(self, model: Model, view: View):
        """Initialize the Controller.

        Args:
            model: The Model instance.
            view: The View instance.
        """
        self._model = model
        self._view = view
        self._setup_event_handlers()
        self._on_reset()  # Call reset when the application starts

    def _setup_event_handlers(self) -> None:
        """Set up event handlers for the view."""
        self._view.chat_listbox.bind("<<ListboxSelect>>", self._on_chat_selected)
        self._view.bind("<<ExportChat>>", self._on_export_chat)
        self._view.bind("<<ToggleDumpWindow>>", self._on_toggle_dump_window)
        self._view.bind("<<Reset>>", self._on_reset)  # Add Reset event handler
        self._view.bind("<<StartNewProcess>>", self._on_start_new_process)  # Add StartNewProcess event handler
        self._view.search_var.trace("w", self._on_search)

    def _on_reset(self, event: object = None) -> None:
        """Handle reset event.

        Args:
            event: The event object (unused).
        """
        # Clear the chat view
        self._view.clear_chat_view()  # Correct method name

        # Delete the specified folders
        self._delete_folder("./conversations_selected")
        self._delete_folder(os.path.join(os.path.dirname(__file__), '../model/google_drive_upload/exported_chats'))

        # Hide the folder naming widgets
        self._view.settings.hide_folder_naming()

        # Reset the folder name to an empty string
        self._view.folder_name = ""
        self._view.settings.folder_var.set("")  # Clear the StringVar associated with the entry widget

    def _on_start_new_process(self, event: object) -> None:
        """Handle start new process event.

        Args:
            event: The event object (unused).
        """
        # Use the folder name from the settings
        folder_name = self._view.folder_name
        if not folder_name:
            return  # No folder name set

        # Create a directory for the conversation text files
        output_dir = os.path.join(os.getcwd(), folder_name)
        os.makedirs(output_dir, exist_ok=True)

        # Wait for the conversations_selected folder to be populated
        self._wait_for_folder_population()

        # Retrieve the list of chat names currently displayed in the ChatView
        displayed_chats = self._view.chat_view.get_displayed_chats()

        # Process only the displayed chats and generate .txt files
        for chat_name in displayed_chats:
            self._process_chat(chat_name, output_dir)

        # Notify the user that the dump is complete
        self._view.notify_dump_complete(output_dir)

        # Call reset at the end
        self._on_reset()

    def _delete_folder(self, folder_path: str) -> None:
        """Delete a folder and its contents.

        Args:
            folder_path: Path to the folder to be deleted.
        """
        if os.path.exists(folder_path):
            for root, dirs, files in os.walk(folder_path, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(folder_path)

    def run(self) -> None:
        """Load chats and start the main event loop."""
        self._load_chats()
        self._view.mainloop()

    def _load_chats(self) -> None:
        """Load chats from the model and display them in the view."""
        chats = self._model.get_chats()
        self._view.display_chats(chats)
        self._model.load_contacts()

    def _on_chat_selected(self, event: object) -> None:
        """Handle chat selection event.

        Args:
            event: The event object containing the selected chat's ID.
        """
        chat_index = event.widget.curselection()
        if chat_index:
            chat_name = self._view.chat_listbox.get(chat_index)
            self._view.display_chat_name(chat_name)

    def _on_export_chat(self, event: object) -> None:
        """Handle chat export event.

        Args:
            event: The event object (unused).
        """
        # Collect the displayed conversations
        self._collect_displayed_conversations()

        # Create a directory for the exported chats in ../model/google_drive_upload
        output_dir = os.path.join(os.path.dirname(__file__), '../model/google_drive_upload/exported_chats')
        os.makedirs(output_dir, exist_ok=True)

        # Retrieve the list of chat names currently displayed in the ChatView
        displayed_chats = self._view.chat_view.get_displayed_chats()

        # Process only the displayed chats and generate .txt files
        for chat_name in displayed_chats:
            self._process_chat(chat_name, output_dir)

        # Call the google_drive_upload.py script for each file in the directory
        google_drive_upload_script = os.path.join(os.path.dirname(__file__), '../model/google_drive_upload/google_drive_upload.py')
        for filename in os.listdir(output_dir):
            file_path = os.path.join(output_dir, filename)
            subprocess.run(["python", google_drive_upload_script, file_path])

        # Call reset at the end
        self._on_reset()

    def _on_toggle_dump_window(self, event: object) -> None:
        """Handle toggle dump window event.

        Args:
            event: The event object (unused).
        """
        # Trigger the backend process to populate the conversations_selected folder
        self._collect_displayed_conversations()

        # Show the folder naming widgets
        self._view.settings.show_folder_naming()

    def _collect_displayed_conversations(self) -> None:
        """Collect conversations for the chats currently displayed in the ChatView."""
        displayed_chats = self._view.chat_view.get_displayed_chats()
        for chat_name in displayed_chats:
            chat = self._model.get_chat(chat_name)
            if chat:
                self._model.text_collector._fetch_messages_from_database(chat.chat_identifier, self._model.contacts_collector.contacts_cache)

    def _wait_for_folder_population(self, timeout=30, interval=1) -> None:
        """Wait for the conversations_selected folder to be populated.

        Args:
            timeout: Maximum time to wait in seconds.
            interval: Time interval between checks in seconds.
        """
        conversations_folder = "./conversations_selected"
        start_time = time.time()

        while time.time() - start_time < timeout:
            if os.path.exists(conversations_folder) and any(os.scandir(conversations_folder)):
                return
            time.sleep(interval)

        raise TimeoutError("Timeout waiting for conversations_selected folder to be populated.")

    def _process_chat(self, chat_name, output_dir):
        """Process a single chat and save its messages to a .txt file."""
        # Format the folder name to match the format used in conversations_selected
        formatted_chat_name = chat_name.replace(" ", "_")
        base_dir = os.path.join(os.getcwd(), "conversations_selected")
        chat_folder = os.path.join(base_dir, f"{formatted_chat_name}-conversation")
        if not os.path.exists(chat_folder):
            print(f"Chat folder not found: {chat_folder}")
            return

        # Read the .txt file within the chat folder
        txt_file_path = os.path.join(chat_folder, f"{formatted_chat_name}.txt")
        if not os.path.exists(txt_file_path):
            print(f"Message file not found: {txt_file_path}")
            return

        with open(txt_file_path, "r", encoding="utf-8") as f:
            messages = f.read()

        # Write the contents to the new folder
        chat_filename = f"{chat_name}.txt"
        chat_filepath = os.path.join(output_dir, chat_filename)
        with open(chat_filepath, "w", encoding="utf-8") as f:
            f.write(messages)
        print(f"Saved messages for {chat_name} to {chat_filepath}")

    def _on_search(self, *args) -> None:
        """Handle search bar input event."""
        search_term = self._view.search_var.get().lower()
        filtered_chats = self._model.text_collector.search_chats(search_term)
        self._view.display_chats(filtered_chats)
