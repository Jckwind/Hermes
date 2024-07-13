from typing import List
from .text_collection.text_collector import TextCollector
from .text_collection.chat import Chat
from .text_collection.message import Message
from .contacts_collection.contacts import ContactsCollector
from .contacts_collection.contact import Contact
import json
from pathlib import Path
import os

class Model:
    """Model class for the Hermes iMessage Viewer application.

    This class encapsulates the TextCollector and ContactsCollector, providing methods
    that the view can call to interact with the underlying data.

    Attributes:
        text_collector: An instance of TextCollector for managing text messages.
        contacts_collector: An instance of ContactsCollector for managing contacts.
        self_contact: The contact for the current user.
    """

    def __init__(self, db_path: str):
        """Initialize the Model with a database path.

        Args:
            db_path: Path to the SQLite database file.
        """
        self.text_collector = TextCollector(db_path)
        self.contacts_collector = ContactsCollector()
        # Read self contact information from .hermes_config.json
        config_path = Path(__file__).parent.parent / ".hermes_config.json"
        with open(config_path, "r") as configFile:
            config = json.load(configFile)
            self_phone_number = config["self"]["phone_number"]
            self_name = config["self"]["name"]
            self.self_contact = Contact(phone_number=self_phone_number, name=self_name)
        # Load all contacts
        self.load_contacts()

    def get_chats(self) -> list[Chat]:
        """Retrieve all chat IDs with their corresponding labels.

        Returns:
            A list of Chat objects containing chat ID, display name, and chat identifier.
        """
        self.contacts_collector.load_contacts()  # Ensure contacts are loaded
        return self.text_collector.get_all_chat_ids_with_labels(
            self.contacts_collector.contacts_cache)

    def get_messages(self, chat_identifier: str) -> List[Message]:
        """Read messages for a specific chat.

        Args:
            chat_identifier: The identifier of the chat to read messages from.

        Returns:
            A list of Message objects containing message details.
        """
        try:
            messages = self.text_collector.read_messages(
                chat_identifier,
                self.contacts_collector.contacts_cache,
                self.self_contact
            )
            
            print(f"Retrieved {len(messages)} messages for chat identifier: {chat_identifier}")
            return messages
        except Exception as e:
            print(f"Error retrieving messages for chat {chat_identifier}: {e}")
            return []

    def get_chat_members(self, chat_identifier: str) -> List[Contact]:
        """Get the members of a specific chat.

        Args:
            chat_id: The ID of the chat to get members from.

        Returns:
            A list of chat member names or phone numbers.
        """
        return self.text_collector.get_chat_members(
            chat_identifier, self.contacts_collector.contacts_cache)

    def load_contacts(self) -> list:
        """Load contacts from the AddressBook database.

        Returns:
            A list of Contact objects.
        """
        return self.contacts_collector.load_contacts()

    def get_contact_name(self, phone_number: str) -> str:
        """Get the contact name for a given phone number.

        Args:
            phone_number: The phone number to look up.

        Returns:
            The contact name if found, otherwise the original phone number.
        """
        return self.contacts_collector.get_contact_name(phone_number)

    def get_chat(self, chat_name: str) -> Chat:
        """Get a Chat object for a given chat_name.

        Args:
            chat_name: The name of the chat to retrieve.

        Returns:
            The Chat object if found in the cache, otherwise None.
        """
        chat = self.text_collector.chat_cache.get(chat_name)
        if chat is None:
            print(f"Chat not found: {chat_name}")
        return chat

    def get_displayed_chats(self, chat_names: List[str]) -> List[Chat]:
        """
        Get Chat objects for the displayed chat names.
        
        Args:
            chat_names: List of chat names to retrieve.
        
        Returns:
            List of Chat objects for the given chat names.
        """
        return [self.get_chat(chat_name) for chat_name in chat_names if self.get_chat(chat_name)]

    def export_chats(self, chats: List[Chat], output_dir: str) -> None:
        """
        Export the given chats to text files in the specified output directory.
        
        Args:
            chats: List of Chat objects to export.
            output_dir: Directory to save the exported chat files.
        """
        for chat in chats:
            messages = self.get_messages(chat.chat_identifier)
            file_name = f"{chat.chat_name}.txt"
            file_path = Path(output_dir) / file_name
            
            with open(file_path, 'w', encoding='utf-8') as f:
                for message in messages:
                    f.write(f"{message.timestamp} - {message.sender}: {message.text}\n")
            
            print(f"Exported chat {chat.chat_name} to {file_path}")

    def get_exported_files(self) -> List[str]:
        """Get a list of exported chat files."""
        export_dir = os.path.join(os.getcwd(), "exported_chats")
        if os.path.exists(export_dir):
            return [f for f in os.listdir(export_dir) if f.endswith('.txt')]
        return []