import os
import time
import subprocess
import shutil
from typing import List, Dict
from pathlib import Path
from model.model import Model
from view.view import View
from model.text_collection.chat import Chat
import threading
import logging

class Controller:
    """Controller class for managing interactions between Model and View."""

    def __init__(self, model: Model, view: View):
        """Initialize the Controller."""
        self._model = model
        self._view = view
        self._setup_event_handlers()
        self.export_dir = self._get_export_directory()
        self.all_chats = []
        self.current_export_files = []

    def _get_export_directory(self) -> Path:
        """Get the path to the export directory in the user's Documents folder."""
        documents_path = Path.home() / "Documents"
        export_dir = documents_path / "exported_chats"
        export_dir.mkdir(parents=True, exist_ok=True)
        return export_dir

    def _setup_event_handlers(self) -> None:
        """Set up event handlers for the view."""
        self._view.bind("<<StartExport>>", self._on_export_chat)
        self._view.bind("<<StartGoogleDriveUpload>>", self._on_start_google_drive_upload)
        self._view.bind("<<ResetApplication>>", self._on_reset)
        self._view.bind("<<ToggleDumpWindow>>", self._on_toggle_dump_window)
        self._view.bind("<<LoadExportedFile>>", self._on_load_exported_file)
        self._view.bind("<<ExportedFileSelected>>", self._on_load_exported_file)
        self._view.bind("<<SaveExport>>", self._on_save_export)
        self._view.bind("<<SearchChanged>>", self._on_search)
        self._view.bind("<<SelectionComplete>>", self._on_selection_complete)

    def _on_search(self, event):
        """Handle search bar input event."""
        search_term = self._view.toolbar.get_search_var().get().lower()
        if search_term:
            filtered_chats = [chat for chat in self.all_chats if search_term in chat.lower()]
        else:
            filtered_chats = self.all_chats.copy()
        
        self._view.chat_list.display_chats(filtered_chats)

    def _on_selection_complete(self, event):
        """Handle selection complete event."""
        selected_chats = self._view.chat_list.get_selected_chats()
        self._view.settings.update_selected_chats(selected_chats)

    def _on_export_chat(self, event=None) -> None:
        """Handle export chats process."""
        self._view.after(0, self._view.chat_view.start_loading_animation)

        # Show the folder name input in settings
        self._view.settings.show_folder_name_input()

        # Run the export process in a separate thread
        export_thread = threading.Thread(target=self._run_export_process)
        export_thread.start()

    def _run_export_process(self):
        displayed_chats = self._view.settings.get_displayed_chats()
        logging.info(f"Starting export process for chats: {displayed_chats}")

        # Fetch messages for all displayed chats
        for chat_name in displayed_chats:
            chat = self._model.get_chat(chat_name)
            if chat:
                logging.info(f"Fetching messages for chat: {chat_name}")
                self._model.text_collector.read_messages(
                    chat.chat_identifier,
                    self._model.contacts_collector.contacts_cache
                )
            else:
                logging.warning(f"Chat not found: {chat_name}")

        # Wait for conversations to be populated
        timeout = 120  # Increase timeout to 2 minutes
        logging.info(f"Waiting for conversations to be populated (timeout: {timeout} seconds)")
        self._wait_for_conversations(displayed_chats, timeout)

        # After fetching messages, show the folder name input and enable the save button
        self._view.after(0, self._view.settings.show_folder_name_input)
        self._view.after(0, self._view.settings.enable_save_button)
        logging.info("Export process completed")

    def _on_save_export(self, event=None) -> None:
        """Handle saving the exported chats."""
        folder_name = self._view.settings.folder_name_var.get()
        output_dir = self.export_dir / folder_name
        output_dir.mkdir(parents=True, exist_ok=True)

        # Get the selected chats directly from the chat list
        selected_chats = self._view.chat_list.get_selected_chats()
        logging.info(f"Selected chats: {selected_chats}")

        self.current_export_files = []  # Reset the list of current export files

        # Export all selected chats
        for chat_name in selected_chats:
            chat = self._model.get_chat(chat_name)
            if chat:
                logging.info(f"Exporting chat: {chat_name}")
                exported_file = self._export_chat(chat, output_dir)
                if exported_file:
                    self.current_export_files.append((folder_name, exported_file.name))
                    logging.info(f"Exported file: {exported_file}")
            else:
                logging.warning(f"Chat not found in model: {chat_name}")

        logging.info(f"Total exported files: {len(self.current_export_files)}")

        # Use after to schedule UI updates on the main thread
        self._view.after(0, self._view.chat_view.stop_loading_animation)
        self._view.after(0, lambda: self._view.notify_export_complete(str(output_dir)))

        # After export is complete, update the exported files list
        self._refresh_exported_files_list()

        # Hide the folder name input and disable the save button
        self._view.after(0, self._view.settings.hide_folder_name_input)
        self._view.after(0, self._view.settings.disable_save_button)

        # Display the first exported file
        if self.current_export_files:
            first_file = self.current_export_files[0]
            self._view.after(0, lambda: self._display_exported_file(first_file))

    def _display_exported_file(self, file_info):
        """Display the content of an exported file."""
        subdir, filename = file_info
        file_path = self.export_dir / subdir / filename
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            self._view.chat_view.show_file_content(content)
            self._view.selected_exported_file = file_info
            self._view.settings.select_exported_file(file_info)

    def _on_start_google_drive_upload(self, event=None) -> None:
        """Handle Google Drive upload process."""
        self._view.after(0, self._view.chat_view.start_loading_animation)

        # Run the upload process in a separate thread
        upload_thread = threading.Thread(target=self._run_upload_process)
        upload_thread.start()

    def _run_upload_process(self):
        """Run the Google Drive upload process."""
        # Get the currently displayed chats
        displayed_chat_names = self._view.settings.get_displayed_chats()
        displayed_chats = self._model.get_displayed_chats(displayed_chat_names)

        # Create a temporary directory for the files to be uploaded
        temp_dir = Path(self.export_dir) / "temp_upload"
        temp_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Export the displayed chats to the temporary directory
            self._model.export_chats(displayed_chats, str(temp_dir))

            # Upload the exported files to Google Drive
            success = self._upload_to_google_drive(temp_dir)

            # Use after to schedule UI updates on the main thread
            self._view.after(0, self._view.chat_view.stop_loading_animation)
            if success:
                self._view.after(0, lambda: self._view.chat_view.show_completion_message("Upload Complete!"))
                self._view.after(0, self._view.notify_upload_complete)
            else:
                self._view.after(0, lambda: self._view.chat_view.show_completion_message("Upload Failed. Check console for details."))
        finally:
            # Clean up the temporary directory
            shutil.rmtree(temp_dir)

    def _upload_to_google_drive(self, directory: Path) -> bool:
        """Upload exported chats to Google Drive."""
        google_drive_upload_script = Path(__file__).parent.parent / "model" / "google_drive_upload" / "google_drive_upload.py"
        
        all_uploads_successful = True
        for file_path in directory.glob('*.txt'):
            print(f"Uploading file: {file_path}")
            result = subprocess.run(["python", str(google_drive_upload_script), str(file_path)], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Error uploading {file_path} to Google Drive:")
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}")
                all_uploads_successful = False
            else:
                print(f"Successfully uploaded {file_path}")
                print(f"STDOUT: {result.stdout}")

        return all_uploads_successful

    def _on_reset(self, event=None) -> None:
        """Handle reset event."""
        # Clear only the selected chats in the settings area
        self._view.settings.clear_messages()

        # Delete only the conversations_selected folder
        self._delete_folder("./conversations_selected")

        # Reset the chat list and chat view
        self._view.chat_list.clear_selection()
        self._view.chat_view.clear()

        # Clear the exported files list
        self._view.settings.clear_exported_files_list()

        # Show the folder name input
        self._view.settings.show_folder_name_input()

        # Clear the current export files
        self.current_export_files = []

    def _on_toggle_dump_window(self, event: object) -> None:
        """Handle toggle dump window event."""
        # Implement the logic for toggling the dump window
        pass

    def _on_load_exported_file(self, event=None) -> None:
        """Handle loading of selected exported file."""
        selected_file = self._view.selected_exported_file
        if selected_file:
            subdir_name, filename = selected_file
            file_path = self.export_dir / subdir_name / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                self._view.chat_view.show_file_content(content)
            else:
                print(f"File not found: {file_path}")

    def _wait_for_conversations(self, chat_names: List[str], timeout: int = 120) -> None:
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
                    logging.info(f"Waiting for file: {chat_file}")
                    break
                else:
                    logging.info(f"File ready: {chat_file}")

            if all_conversations_ready:
                logging.info("All conversations are ready")
                return

            time.sleep(1)  # Wait for 1 second before checking again

        logging.warning(f"Timeout reached after {timeout} seconds. Some files may not be ready.")

    def _sanitize_folder_name(self, name: str) -> str:
        """Sanitize the folder name to match the one created by the text collector."""
        return name.replace(', ', '_').replace(' ', '_').rstrip('...')

    def _export_chat(self, chat: Chat, output_dir: Path) -> Path:
        """Export a single chat to a text file."""
        chat_filename = f"{chat.chat_name}.txt"
        chat_filepath = output_dir / chat_filename

        # Use the sanitized name to find the correct file in conversations_selected
        sanitized_name = self._sanitize_folder_name(chat.chat_name)
        source_file = Path("./conversations_selected") / sanitized_name / f"{sanitized_name}.txt"

        logging.info(f"Attempting to export chat: {chat.chat_name}")
        logging.info(f"Looking for source file: {source_file}")

        if source_file.exists():
            shutil.copy(source_file, chat_filepath)
            logging.info(f"Copied file from {source_file} to {chat_filepath}")
            return chat_filepath
        else:
            logging.warning(f"Source file not found: {source_file}")
            logging.info(f"Contents of conversations_selected folder: {os.listdir('./conversations_selected')}")
            return None

    def _delete_folder(self, folder_path: str) -> None:
        """Delete a folder and its contents."""
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

    def _refresh_exported_files_list(self):
        """Refresh the list of exported files in the settings area."""
        self._view.update_exported_files_list(self.current_export_files)

    def run(self) -> None:
        """Load chats and start the main event loop."""
        logging.basicConfig(level=logging.INFO)
        chats = self._model.get_chats()
        self.all_chats = [chat.chat_name for chat in chats]  # Store all chat names
        logging.info(f"All chats: {self.all_chats}")
        self._view.chat_list.set_all_chats(self.all_chats)
        self._view.chat_list.display_chats(self.all_chats)  # Display all chats initially
        self._model.load_contacts()

        self._view.mainloop()