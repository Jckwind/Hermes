"""Module for collecting and managing text messages from a SQLite database."""

import sqlite3
import subprocess
import os
import shutil
import threading
import queue
from typing import List, Dict, Optional, Tuple
from .chat import Chat
from .message import Message
from ..contacts_collection.contact import Contact

class TextCollector:
    """A class for collecting and managing text messages from a SQLite database."""

    def __init__(self, db_path: str):
        """Initialize the TextCollector."""
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self.chat_cache: Dict[str, Chat] = {}
        self.output_file = os.path.join(os.path.dirname(__file__), 'contacts.txt')
        self._connect_database()

    def _connect_database(self) -> None:
        """Establish a connection to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
        except sqlite3.OperationalError:
            raise

    def get_all_chat_ids_with_labels(self, contacts_cache: Dict[str, Contact]) -> List[Chat]:
        """Retrieve all chat IDs with their corresponding labels."""
        try:
            if not self.chat_cache:
                chats = self._query_chats()
                enriched_chats = self._enrich_chats_with_contacts(chats, contacts_cache)
                self.chat_cache = {chat.chat_name: chat for chat in enriched_chats}
            return list(self.chat_cache.values())
        except sqlite3.Error:
            raise

    def _query_chats(self) -> List[Tuple[int, str, str]]:
        """Execute the database query to fetch chats."""
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT cmj.chat_id,
                       COALESCE(c.display_name, c.chat_identifier) AS display_name,
                       c.chat_identifier
                FROM chat_message_join AS cmj
                JOIN message AS m ON cmj.message_id = m.ROWID
                INNER JOIN chat AS c ON cmj.chat_id = c.ROWID
                GROUP BY cmj.chat_id
                ORDER BY MAX(m.date) DESC;
            """)
            return cursor.fetchall()

    def _enrich_chats_with_contacts(self, chats: List[Tuple[int, str, str]], contacts_cache: Dict[str, Contact]) -> List[Chat]:
        """Enrich chat data with contact information and return Chat objects."""
        enriched_chats = []
        for chat_id, display_name, chat_identifier in chats:
            if display_name == '' or display_name is None:
                contact = contacts_cache.get(chat_identifier, Contact(phone_number=chat_identifier, name=chat_identifier))
                if contact.name is not None:
                    display_name = contact.name
                else:
                    display_name = chat_identifier

            members = self.get_chat_members(chat_id, contacts_cache)
            chat = Chat(
                    chat_id=chat_id,
                    display_name=display_name,
                    chat_identifier=chat_identifier,
                    members=members
                )
            chat.display_name = chat.chat_name
            enriched_chats.append(chat)
        return enriched_chats

    def read_messages(self, chat_identifier: str, contacts_cache: Dict[str, Contact]) -> None:
        """Read messages for a specific chat."""
        try:
            self._fetch_messages_from_database(chat_identifier, contacts_cache)
        except sqlite3.Error:
            raise

    def _fetch_messages_from_database(self, chat_identifier: str, contacts_cache: Dict[str, Contact]) -> None:
        """Fetch raw message data from the database using imessage-exporter."""
        imessage_exporter_path = "lib/imessage-exporter/target/release/imessage-exporter"
        output_path = "./dump"
        args = [
            "-f", "txt",
            "-o", output_path,
            "-c", "compatible",
            "-g", chat_identifier,
        ]
        command = [imessage_exporter_path] + args

        def run_command(cmd: List[str], output_queue: queue.Queue) -> None:
            try:
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                output_queue.put(("success", result.stdout, result.stderr))
            except subprocess.CalledProcessError as e:
                output_queue.put(("error", e.returncode, e.stdout, e.stderr))

        output_queue = queue.Queue()
        thread = threading.Thread(target=run_command, args=(command, output_queue))
        thread.start()
        thread.join()

        result = output_queue.get()
        if result[0] == "success":
            self._process_message_results(chat_identifier, contacts_cache)
        else:
            raise subprocess.CalledProcessError(result[1], command, result[2], result[3])

    def _process_message_results(self, chat_identifier: str, contacts_cache: Dict[str, Contact]) -> None:
        """Process the results of the imessage-exporter command."""
        output_path = "./dump"
        conversations_folder = "./conversations_selected"

        chat = next((c for c in self.chat_cache.values() if c.chat_identifier == chat_identifier), None)

        if chat:
            folder_name = self._sanitize_folder_name(chat.chat_name)
            is_group_chat = len(chat.members) > 1
        else:
            contact = contacts_cache.get(chat_identifier, Contact(phone_number=chat_identifier, name=chat_identifier))
            folder_name = self._sanitize_folder_name(contact.name)
            is_group_chat = False

        new_chat_folder = os.path.join(conversations_folder, folder_name)
        os.makedirs(new_chat_folder, exist_ok=True)

        if is_group_chat:
            possible_files = [f for f in os.listdir(output_path) if f.endswith('.txt')]
            matching_file = next((f for f in possible_files if f.replace(' ', '_').startswith(folder_name)), None)
            if matching_file:
                src_txt = os.path.join(output_path, matching_file)
            else:
                src_txt = os.path.join(output_path, f"{chat_identifier}.txt")
        else:
            src_txt = os.path.join(output_path, f"{chat_identifier}.txt")

        dst_txt = os.path.join(new_chat_folder, f"{folder_name}.txt")

        if os.path.exists(src_txt):
            shutil.move(src_txt, dst_txt)
        else:
            pass

        self._cleanup_dump_folder(output_path)

    def _sanitize_folder_name(self, name):
        sanitized = name.replace(', ', '_').replace(' ', '_')
        if sanitized.endswith('...'):
            sanitized = sanitized[:-3]
        return sanitized

    def _cleanup_dump_folder(self, output_path: str) -> None:
        """Delete the original ./dump folder after processing."""
        try:
            shutil.rmtree(output_path, ignore_errors=True)
        except Exception:
            pass

    def get_chat_members(self, chat_id: int, contacts_cache: Dict[str, Contact]) -> List[Contact]:
        """Get the members of a specific chat."""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                query = """
                SELECT handle.id
                FROM chat_handle_join
                JOIN handle ON chat_handle_join.handle_id = handle.ROWID
                WHERE chat_handle_join.chat_id = ?
                """
                cursor.execute(query, (chat_id,))
                members = cursor.fetchall()

            return [contacts_cache.get(member[0], Contact(phone_number=member[0], name=member[0])) for member in members]
        except sqlite3.Error:
            raise

    def search_chats(self, search_term: str) -> List[Chat]:
        """Search for chats based on a search term."""
        lowercase_search_term = search_term.lower()
        return [chat for chat in self.chat_cache.values() if lowercase_search_term in chat.chat_name.lower().rstrip('...')]

    def rename_existing_files(self):
        conversations_folder = "./conversations_selected"
        for folder_name in os.listdir(conversations_folder):
            if folder_name.endswith("-conversation"):
                folder_path = os.path.join(conversations_folder, folder_name)
                for file_name in os.listdir(folder_path):
                    if file_name.endswith(".txt"):
                        old_file_path = os.path.join(folder_path, file_name)
                        new_file_path = os.path.join(folder_path, f"{folder_name}.txt")
                        os.rename(old_file_path, new_file_path)

    def __del__(self):
        """Close the database connection when the object is destroyed."""
        if self.conn:
            self.conn.close()