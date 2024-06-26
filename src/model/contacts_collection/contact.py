"""Module containing the Contact class for representing contact information."""

from dataclasses import dataclass


@dataclass
class Contact:
    """Represents a contact with a phone number and name.

    Attributes:
        phone_number: The contact's phone number as a string.
        name: The contact's name as a string.
    """

    phone_number: str
    name: str
