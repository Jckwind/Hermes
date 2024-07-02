from typing import List
from .text_collection.text_collector import TextCollector
from .text_collection.chat import Chat
from .text_collection.message import Message
from .contacts_collection.contacts import ContactsCollector
from .contacts_collection.contact import Contact
import json
from pathlib import Path

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
            chat_id: The ID of the chat to read messages from.

        Returns:
            A list of dictionaries containing message details.
        """
        return self.text_collector.read_messages(
            chat_identifier,
            self.contacts_collector.contacts_cache,
            self.self_contact
        )

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
        return self.text_collector.chat_cache.get(chat_name)
