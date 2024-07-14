from dataclasses import dataclass
from typing import List
from ..contacts_collection.contact import Contact

@dataclass
class Chat:
    """Represents a chat conversation.

    Attributes:
        chat_id: An integer representing the unique identifier of the chat.
        display_name: A string representing the display name of the chat.
        chat_identifier: A string representing the identifier of the chat.
        members: A list of Contact objects representing the chat members.
        chat_name: A string representing the definitive name of the chat.
    """

    chat_id: int
    display_name: str
    chat_identifier: str
    members: List[Contact]

    @property
    def chat_name(self) -> str:
        """Returns the definitive name of the chat."""

        if not self.display_name.startswith("chat"):
            return self.display_name
        elif len(self.members) > 1:
            member_names = [member.name for member in self.members[:3]]
            x = ", ".join(member_names) + ("..." if len(self.members) > 3 else "")

            return x
        elif len(self.members) == 1:
            return self.members[0].name
        else:
            return self.chat_identifier
