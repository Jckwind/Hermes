"""Module for collecting and managing text messages from a SQLite database."""

import sqlite3
import datetime
import logging
from typing import List, Dict, Optional
from .chat import Chat
from ..contacts_collection.contact import Contact

class TextCollector:
    """A class for collecting and managing text messages from a SQLite database."""

    def __init__(self, db_path: str):
        """Initialize the TextCollector.

        Args:
            db_path: Path to the SQLite database file.

        Raises:
            sqlite3.OperationalError: If unable to connect to the database.
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self.chat_cache: Dict[str, Chat] = {}
        self._connect_database()

    def _connect_database(self) -> None:
        """Establish a connection to the SQLite database.

        Raises:
            sqlite3.OperationalError: If unable to connect to the database.
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
        except sqlite3.OperationalError as error:
            logging.error("Failed to connect to the database at %s. Error: %s", self.db_path, error)
            raise

    def get_all_chat_ids_with_labels(self, contacts_cache: Dict[str, Contact]) -> List[Chat]:
        """Retrieve all chat IDs with their corresponding labels.

        Args:
            contacts_cache: A dictionary of contacts, keyed by phone number.

        Returns:
            A list of Chat objects containing chat ID, display name, chat identifier, and members.

        Raises:
            sqlite3.Error: If a database error occurs.
        """
        try:
            if not self.chat_cache:
                chats = self._query_chats()
                enriched_chats = self._enrich_chats_with_contacts(chats, contacts_cache)
                self.chat_cache = {
                    chat.chat_name: chat
                    for chat in [
                        Chat(
                            chat_id=chat_id,
                            display_name=display_name,
                            chat_identifier=chat_identifier,
                            members=self.get_chat_members(chat_id, contacts_cache)
                        )
                        for chat_id, display_name, chat_identifier in enriched_chats
                    ]
                }
            return list(self.chat_cache.values())
        except sqlite3.Error as e:
            self._log_database_error(e)
            raise

    def _query_chats(self) -> List[tuple]:
        """Execute the database query to fetch chats.

        Returns:
            A list of tuples containing chat information.
        """
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

    def _enrich_chats_with_contacts(self, chats: List[tuple], contacts_cache: Dict[str, Contact]) -> List[tuple]:
        """Enrich chat data with contact information.

        Args:
            chats: A list of tuples containing chat information.
            contacts_cache: A dictionary of contacts, keyed by phone number.

        Returns:
            A list of tuples with enriched chat information.
        """
        return [
            (chat_id, contacts_cache.get(chat_identifier, Contact(phone_number=chat_identifier, name=display_name)).name if display_name == '' else display_name, chat_identifier)
            for chat_id, display_name, chat_identifier in chats
        ]

    def _log_database_error(self, error: sqlite3.Error) -> None:
        """Log database errors.

        Args:
            error: The SQLite error to log.
        """
        logging.error("Database error occurred: %s", error)

    def read_messages(self, chat_id: int, contacts_cache: Dict[str, Contact], self_number: str = 'Me', human_readable_date: bool = True) -> List[Dict[str, str]]:
        """Read messages for a specific chat.

        Args:
            chat_id: The ID of the chat to read messages from.
            contacts_cache: A dictionary of contacts, keyed by phone number.
            self_number: The identifier for the user's own messages. Defaults to 'Me'.
            human_readable_date: Whether to format dates as human-readable. Defaults to True.

        Returns:
            A list of dictionaries containing message details.

        Raises:
            sqlite3.Error: If a database error occurs.
        """
        try:
            with self.conn:
                cursor = self.conn.cursor()
                query = """
                SELECT message.ROWID, message.date, message.text, message.attributedBody, handle.id, message.is_from_me, message.cache_has_attachments
                FROM message
                LEFT JOIN handle ON message.handle_id = handle.ROWID
                WHERE message.ROWID IN (SELECT message_id FROM chat_message_join WHERE chat_id = ?)
                ORDER BY message.date
                """
                cursor.execute(query, (chat_id,))
                results = cursor.fetchall()

            messages = []
            for result in results:
                rowid, date, text, attributed_body, handle_id, is_from_me, cache_has_attachments = result
                phone_number = self_number if is_from_me else contacts_cache.get(handle_id, Contact(phone_number=handle_id, name=handle_id)).name

                body = self.extract_message_body(text, attributed_body)
                date = self.format_time(date) if human_readable_date else date

                if phone_number:
                    messages.append({"date": date, "body": body, "phone_number": phone_number})

            return messages
        except sqlite3.Error as e:
            logging.error("Error reading messages: %s", e)
            raise

    def extract_message_body(self, text: str, attributed_body: bytes) -> str:
        """Extract the message body from either text or attributed body.

        Args:
            text: The text of the message.
            attributed_body: The attributed body of the message.

        Returns:
            The extracted message body.
        """
        if text:
            return text

        if attributed_body:
            try:
                decoded_body = attributed_body.split(b"NSString")[1]
                text = decoded_body[5:]
                if text[0] == 129:
                    length = int.from_bytes(text[1:3], "little")
                    text = text[3:length+3]
                else:
                    length = text[0]
                    text = text[1:length+1]
                return text.decode()
            except (IndexError, UnicodeDecodeError) as e:
                logging.error("Error extracting message body: %s", e)
                return ""

        return ""

    def format_time(self, time_sent: int) -> str:
        """Format a timestamp into a human-readable date string.

        Args:
            time_sent: The timestamp to format.

        Returns:
            A formatted date string.
        """
        apple_epoch = datetime.datetime(2001, 1, 1)
        time_sent_seconds = time_sent / 1_000_000_000
        time_sent_datetime = apple_epoch + datetime.timedelta(seconds=time_sent_seconds)
        return time_sent_datetime.strftime('%Y-%m-%d %H:%M')

    def get_chat_members(self, chat_id: int, contacts_cache: Dict[str, Contact]) -> List[Contact]:
        """Get the members of a specific chat.

        Args:
            chat_id: The ID of the chat to get members from.
            contacts_cache: A dictionary of contacts, keyed by phone number.

        Returns:
            A list of Contact objects representing chat members.

        Raises:
            sqlite3.Error: If a database error occurs.
        """
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
        except sqlite3.Error as e:
            logging.error("Error getting chat members: %s", e)
            raise

    def search_chats(self, search_term: str) -> List[Chat]:
        """Search for chats based on a search term.

        Args:
            search_term: The term to search for in chat names, identifiers, or member information.

        Returns:
            A list of Chat objects that match the search term.
        """
        lowercase_search_term = search_term.lower()
        matching_chats = []

        for chat in self.chat_cache.values():
            if lowercase_search_term in chat.chat_name.lower():
                matching_chats.append(chat)
                continue

        return matching_chats

    def __del__(self):
        """Close the database connection when the object is destroyed."""
        if self.conn:
            self.conn.close()
