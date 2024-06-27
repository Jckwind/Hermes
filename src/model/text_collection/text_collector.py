"""Module for collecting and managing text messages from a SQLite database."""

import sqlite3
import logging
from typing import List, Dict, Optional
from .chat import Chat
from .message import Message
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
                    for chat in enriched_chats
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

    def _enrich_chats_with_contacts(self, chats: List[tuple], contacts_cache: Dict[str, Contact]) -> List[Chat]:
        """Enrich chat data with contact information and return Chat objects.

        Args:
            chats: A list of tuples containing chat information.
            contacts_cache: A dictionary of contacts, keyed by phone number.

        Returns:
            A list of Chat objects with enriched chat information.
        """
        enriched_chats = []
        for chat_id, display_name, chat_identifier in chats:
            if display_name == '':
                # If display_name is empty, try to get the name from contacts_cache
                contact = contacts_cache.get(chat_identifier, Contact(phone_number=chat_identifier, name=chat_identifier))
                display_name = contact.name

            members = self.get_chat_members(chat_id, contacts_cache)
            enriched_chats.append(Chat(
                chat_id=chat_id,
                display_name=display_name,
                chat_identifier=chat_identifier,
                members=members
            ))

        return enriched_chats

    def _log_database_error(self, error: sqlite3.Error) -> None:
        """Log database errors.

        Args:
            error: The SQLite error to log.
        """
        logging.error("Database error occurred: %s", error)

    def read_messages(self, chat_id: int, contacts_cache: Dict[str, Contact], self_contact: Contact) -> List[Message]:
        """Read messages for a specific chat.

        Args:
            chat_id: The ID of the chat to read messages from.
            contacts_cache: A dictionary of contacts, keyed by phone number.
            self_number: The identifier for the user's own messages. Defaults to 'Me'.

        Returns:
            A list of Message objects containing message details.

        Raises:
            sqlite3.Error: If a database error occurs.
        """
        try:
            results = self._fetch_messages_from_database(chat_id)
            return self._process_message_results(results, contacts_cache, self_contact)
        except sqlite3.Error as e:
            self._log_database_error(e)
            raise

    def _fetch_messages_from_database(self, chat_id: int) -> List[tuple]:
        """Fetch raw message data from the database.

        Args:
            chat_id: The ID of the chat to fetch messages for.

        Returns:
            A list of tuples containing raw message data.

        Raises:
            sqlite3.Error: If a database error occurs.
        """
        query = """
        SELECT message.ROWID, message.date, message.text, message.attributedBody,
               handle.id, message.is_from_me, message.cache_has_attachments
        FROM message
        LEFT JOIN handle ON message.handle_id = handle.ROWID
        WHERE message.ROWID IN (SELECT message_id FROM chat_message_join WHERE chat_id = ?)
        ORDER BY message.date
        """
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(query, (chat_id,))
            return cursor.fetchall()

    def _process_message_results(self, results: List[tuple], contacts_cache: Dict[str, Contact], self_contact: Contact) -> List[Message]:
        """Process raw message data into Message objects.

        Args:
            results: A list of tuples containing raw message data.
            contacts_cache: A dictionary of contacts, keyed by phone number.
            self_number: The identifier for the user's own messages.

        Returns:
            A list of Message objects.
        """
        messages = []
        for result in results:
            message = Message.fromDatabaseResult(result, self_contact)
            if not message.isFromMe:
                message.sender = contacts_cache.get(message.sender.phone_number, message.sender)
            messages.append(message)
        return messages

    def _log_database_error(self, error: sqlite3.Error) -> None:
        """Log database errors.

        Args:
            error: The SQLite error to log.
        """
        logging.error("Database error occurred: %s", error)

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
