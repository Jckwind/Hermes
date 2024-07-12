import os
import time
import subprocess
import shutil
from typing import List, Dict
from model.model import Model
from view.view import View
from model.text_collection.chat import Chat

class Controller:
    """Controller class for managing interactions between Model and View."""

    def __init__(self, model: Model, view: View):
        """Initialize the Controller."""
        self._model = model
        self._view = view
        self._setup_event_handlers()

    def _setup_event_handlers(self) -> None:
        """Set up event handlers for the view."""
        self._view.bind("<<ExportChat>>", self._on_export_chat)
        self._view.bind("<<StartGoogleDriveUpload>>", self._on_start_google_drive_upload)
        self._view.bind("<<Reset>>", self._on_reset)
        self._view.bind("<<ToggleDumpWindow>>", self._on_toggle_dump_window)
        self._view.search_var.trace("w", self._on_search)

    def _on_export_chat(self, event: object) -> None:
        """Handle export chats process."""
        print("Export event received")  # Add this line
        folder_name = "exported_chats"
        output_dir = os.path.join(os.getcwd(), folder_name)
        os.makedirs(output_dir, exist_ok=True)

        displayed_chats = self._view.settings.get_displayed_chats()
        
        # Fetch messages for all displayed chats
        for chat_name in displayed_chats:
            chat = self._model.get_chat(chat_name)
            if chat:
                self._model.text_collector.read_messages(
                    chat.chat_identifier,
                    self._model.contacts_collector.contacts_cache
                )

        # Wait for conversations to be populated
        self._wait_for_conversations(displayed_chats)

        # Export the chats
        for chat_name in displayed_chats:
            chat = self._model.get_chat(chat_name)
            if chat:
                self._export_chat(chat, output_dir)

        self._view.notify_export_complete(output_dir)

    def _on_start_google_drive_upload(self, event: object) -> None:
        """Handle Google Drive upload process."""
        folder_name = "exported_chats"
        output_dir = os.path.join(os.getcwd(), folder_name)

        if not os.path.exists(output_dir):
            self._view.show_error("Export folder not found", "Please export chats before uploading to Google Drive.")
            return

        self._upload_to_google_drive(output_dir)
        self._view.notify_upload_complete()

    def _on_reset(self, event: object) -> None:
        """Handle reset event."""
        # Clear the chat view
        self._view.settings.clear_messages()

        # Delete the specified folders
        self._delete_folder("./conversations_selected")
        self._delete_folder("./exported_chats")

        # Reload chats
        self._load_chats()

        # Clear the search bar
        self._view.search_var.set("")

        print("Application reset complete")

    def _on_toggle_dump_window(self, event: object) -> None:
        """Handle toggle dump window event."""
        # Implement the logic for toggling the dump window
        pass

    def _on_search(self, *args) -> None:
        """Handle search bar input event."""
        search_term = self._view.search_var.get().lower()
        filtered_chats = self._model.text_collector.search_chats(search_term)
        self._view.display_chats(filtered_chats)

    def _wait_for_conversations(self, chat_names: List[str], timeout: int = 60) -> None:
        """Wait for conversations to be populated in the conversations_selected folder."""
        start_time = time.time()
        conversations_folder = "./conversations_selected"

        while time.time() - start_time < timeout:
            all_conversations_ready = True
            for chat_name in chat_names:
                sanitized_name = self._sanitize_folder_name(chat_name)
                chat_folder = os.path.join(conversations_folder, sanitized_name)
                chat_file = os.path.join(chat_folder, f"{sanitized_name}.txt")
                
                if not os.path.exists(chat_file):
                    all_conversations_ready = False
                    break

            if all_conversations_ready:
                print("All conversations are ready for export.")
                return

            time.sleep(1)  # Wait for 1 second before checking again

        print("Timeout waiting for conversations to be populated.")

    def _sanitize_folder_name(self, name: str) -> str:
        """Sanitize the folder name to match the one created by the text collector."""
        return name.replace(', ', '_').replace(' ', '_').rstrip('...')

    def _export_chat(self, chat: Chat, output_dir: str) -> None:
        """Export a single chat to a text file."""
        chat_filename = f"{chat.chat_name}.txt"
        chat_filepath = os.path.join(output_dir, chat_filename)

        # Use the sanitized name to find the correct file in conversations_selected
        sanitized_name = self._sanitize_folder_name(chat.chat_name)
        source_file = os.path.join("./conversations_selected", sanitized_name, f"{sanitized_name}.txt")

        if os.path.exists(source_file):
            shutil.copy(source_file, chat_filepath)
            print(f"Exported chat {chat.chat_name} to {chat_filepath}")
        else:
            print(f"Source file not found for chat {chat.chat_name}")

    def _upload_to_google_drive(self, output_dir: str) -> None:
        """Upload exported chats to Google Drive."""
        google_drive_upload_script = os.path.join(os.path.dirname(__file__), '../model/google_drive_upload/google_drive_upload.py')
        for filename in os.listdir(output_dir):
            file_path = os.path.join(output_dir, filename)
            subprocess.run(["python", google_drive_upload_script, file_path])

    def _delete_folder(self, folder_path: str) -> None:
        """Delete a folder and its contents."""
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            print(f"Deleted folder: {folder_path}")

    def run(self) -> None:
        """Load chats and start the main event loop."""
        self._load_chats()
        self._view.mainloop()

    def _load_chats(self) -> None:
        """Load chats from the model and display them in the view."""
        chats = self._model.get_chats()
        chat_names = [chat.chat_name for chat in chats]  # Extract chat names
        self._view.display_chats(chat_names)
        self._model.load_contacts()
