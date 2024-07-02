from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from ..contacts_collection.contact import Contact


@dataclass
class Message:
    """Represents an individual text message.

    Attributes:
        row_id: The unique identifier for the message in the database.
        guid: A globally unique identifier for the message.
        date: A datetime object representing when the message was sent.
        body: A string containing the content of the message.
        sender: A Contact object representing the sender of the message.
        is_from_me: A boolean indicating whether the message was sent by the user.
        has_attachments: A boolean indicating whether the message has any attachments.
        associated_message_guid: The GUID of an associated message, if any.
        associated_message_type: The type of the associated message, if any.
    """

    row_id: int
    guid: str
    date: datetime
    body: str
    sender: Contact
    is_from_me: bool
    has_attachments: bool
    associated_message_guid: Optional[str] = None
    associated_message_type: Optional[int] = None

    @property
    def formatted_date(self) -> str:
        """Returns the date formatted as a string."""
        return self.date.strftime('%Y-%m-%d %H:%M')

    @property
    def is_attachment_only(self) -> bool:
        """Returns True if the message is only an attachment."""
        return self.has_attachments and not self.body

    @classmethod
    def from_database_result(cls, result: tuple, self_contact: Contact) -> 'Message':
        """
        Create a Message instance from a database query result.

        Args:
            result: A tuple containing the database query result.
            self_contact: The Contact object representing the user.

        Returns:
            A Message instance.
        """
        (row_id, guid, date, text, attributed_body, handle_id, is_from_me,
         cache_has_attachments, associated_message_guid, associated_message_type) = result

        # Convert the Apple epoch timestamp to a datetime object
        message_date = cls.format_time(date)

        # Extract the message body or set placeholder for image
        if cache_has_attachments and not text:
            body = "(Image Attachment)"
        else:
            body = text if text else cls._extract_attributed_body(attributed_body)

        # Determine the sender
        sender = self_contact if is_from_me else Contact(phone_number=handle_id, name=handle_id)

        return cls(
            row_id=row_id,
            guid=guid,
            date=message_date,
            body=body,
            sender=sender,
            is_from_me=bool(is_from_me),
            has_attachments=bool(cache_has_attachments),
            associated_message_guid=associated_message_guid,
            associated_message_type=associated_message_type
        )

    @staticmethod
    def format_time(timestamp: int) -> Optional[datetime]:
        """Format a timestamp into a datetime object.

        Args:
            timestamp: The timestamp to format.

        Returns:
            A datetime object or None if timestamp is None.
        """
        if timestamp is None:
            return None
        apple_epoch = datetime(2001, 1, 1)
        time_sent_seconds = timestamp / 1_000_000_000
        return apple_epoch + timedelta(seconds=time_sent_seconds)

    @staticmethod
    def _extract_attributed_body(attributed_body: bytes) -> str:
        """Extract the message body from attributed body."""
        if not attributed_body:
            return ""

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
        except (IndexError, UnicodeDecodeError):
            return ""
