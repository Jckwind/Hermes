from dataclasses import dataclass
from datetime import datetime, timedelta
from ..contacts_collection.contact import Contact

@dataclass
class Message:
    """Represents an individual text message.

    Attributes:
        date: A datetime object representing when the message was sent.
        body: A string containing the content of the message.
        sender: A Contact object representing the sender of the message.
        isFromMe: A boolean indicating whether the message was sent by the user.
        hasAttachments: A boolean indicating whether the message has any attachments.
    """

    date: datetime
    body: str
    sender: Contact
    isFromMe: bool
    hasAttachments: bool

    @property
    def formattedDate(self) -> str:
        """Returns the date formatted as a string."""
        return self.date.strftime('%Y-%m-%d %H:%M')

    @classmethod
    def fromDatabaseResult(cls, result: tuple, selfContact: Contact):
        """
        Create a Message instance from a database query result.

        Args:
            result: A tuple containing the database query result.
            selfContact: The Contact object representing the user.

        Returns:
            A Message instance.
        """
        _, date, text, attributedBody, handleID, isFromMe, cacheHasAttachments = result

        # Convert the Apple epoch timestamp to a datetime object
        messageDate = cls.format_time(date)

        # Extract the message body
        body = text if text else cls._extractAttributedBody(attributedBody)

        # Determine the sender
        sender = selfContact if isFromMe else Contact(phone_number=handleID, name=handleID)

        return cls(
            date=messageDate,
            body=body,
            sender=sender,
            isFromMe=bool(isFromMe),
            hasAttachments=bool(cacheHasAttachments)
        )

    @staticmethod
    def format_time(time_sent: int) -> str:
        """Format a timestamp into a human-readable date string.

        Args:
            time_sent: The timestamp to format.

        Returns:
            A formatted date string.
        """
        apple_epoch = datetime(2001, 1, 1)
        time_sent_seconds = time_sent / 1_000_000_000
        time_sent_datetime = apple_epoch + timedelta(seconds=time_sent_seconds)
        return time_sent_datetime.strftime('%Y-%m-%d %H:%M')

    @staticmethod
    def _extractAttributedBody(attributedBody: bytes) -> str:
        """Extract the message body from attributed body."""
        if not attributedBody:
            return ""

        try:
            decodedBody = attributedBody.split(b"NSString")[1]
            text = decodedBody[5:]
            if text[0] == 129:
                length = int.from_bytes(text[1:3], "little")
                text = text[3:length+3]
            else:
                length = text[0]
                text = text[1:length+1]
            return text.decode()
        except (IndexError, UnicodeDecodeError):
            return ""
