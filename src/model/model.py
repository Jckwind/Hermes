from .text_collection.text_collector import TextCollector
from .text_collection.chat import Chat
from .contacts_collection.contacts import ContactsCollector

class Model:
    """Model class for the Hermes iMessage Viewer application.

    This class encapsulates the TextCollector and ContactsCollector, providing methods
    that the view can call to interact with the underlying data.

    Attributes:
        text_collector: An instance of TextCollector for managing text messages.
        contacts_collector: An instance of ContactsCollector for managing contacts.
    """

    def __init__(self, db_path: str):
        """Initialize the Model with a database path.

        Args:
            db_path: Path to the SQLite database file.
        """
        self.text_collector = TextCollector(db_path)
        self.contacts_collector = ContactsCollector()
        self.load_contacts()

    def get_chats(self) -> list[Chat]:
        """Retrieve all chat IDs with their corresponding labels.

        Returns:
            A list of Chat objects containing chat ID, display name, and chat identifier.
        """
        self.contacts_collector.load_contacts()  # Ensure contacts are loaded
        return self.text_collector.get_all_chat_ids_with_labels(
            self.contacts_collector.contacts_cache)

    def get_messages(self, chat_id: int) -> list:
        """Read messages for a specific chat.

        Args:
            chat_id: The ID of the chat to read messages from.

        Returns:
            A list of dictionaries containing message details.
        """
        return self.text_collector.read_messages(
            chat_id, self.contacts_collector.contacts_cache)

    def get_chat_members(self, chat_id: int) -> list:
        """Get the members of a specific chat.

        Args:
            chat_id: The ID of the chat to get members from.

        Returns:
            A list of chat member names or phone numbers.
        """
        return self.text_collector.get_chat_members(
            chat_id, self.contacts_collector.contacts_cache)

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
