"""Module for collecting and managing contacts from the AddressBook database."""

import sqlite3
import logging
from typing import List, Optional, Tuple, Dict
from glob import glob
import re
from pathlib import Path
from .contact import Contact


class ContactsCollector:
    """A class for collecting and managing contacts from the AddressBook database."""

    def __init__(self):
        """Initialize the ContactsCollector."""
        self.contacts = []  # type: List[Contact]
        self.contacts_cache = {}  # type: Dict[str, Contact]

    def load_contacts(self) -> List[Contact]:
        """
        Load contacts from the AddressBook database.

        Returns:
            A list of Contact objects.

        Raises:
            Exception: If there's an error loading contacts.
        """
        try:
            if self.contacts:
                return self.contacts

            database_path = self._find_address_book_database()
            if not database_path:
                return []

            contacts_data = self._query_address_book_database(database_path)
            self.contacts = self._create_contact_objects(contacts_data)
            self._cache_contacts()
            return self.contacts
        except Exception as e:
            logging.error("Error loading contacts: %s", e)
            return []

    def _find_address_book_database(self) -> Optional[str]:
        """
        Find the AddressBook database file.

        Returns:
            The path to the AddressBook database file, or None if not found.
        """
        path_pattern = str(Path.home() / "Library" / "Application Support" / "AddressBook" / "Sources" / "*" / "AddressBook-v22.abcddb")
        database_paths = glob(path_pattern)

        if not database_paths:
            logging.warning("No AddressBook database found.")
            return None

        return database_paths[0]

    def _query_address_book_database(self, database_path: str) -> List[Tuple[str, str]]:
        """
        Query the AddressBook database for contact information.

        Args:
            database_path: The path to the AddressBook database.

        Returns:
            A list of tuples containing phone numbers and full names.
        """
        query = '''
        SELECT p.ZFULLNUMBER,
               TRIM(COALESCE(r.ZFIRSTNAME || ' ' || NULLIF(r.ZLASTNAME, ''), r.ZFIRSTNAME, r.ZLASTNAME)) AS FullName
        FROM ZABCDPHONENUMBER p
        JOIN ZABCDRECORD r ON p.ZOWNER = r.Z_PK
        ORDER BY r.ZLASTNAME ASC, r.ZFIRSTNAME ASC
        '''

        with sqlite3.connect(database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            return cursor.fetchall()

    def _create_contact_objects(self, contacts_data: List[Tuple[str, str]]) -> List[Contact]:
        """
        Create Contact objects from raw database data.

        Args:
            contacts_data: A list of tuples containing phone numbers and full names.

        Returns:
            A list of Contact objects.
        """
        return [
            Contact(
                phone_number=self._format_phone_number(phone),
                name=name
            )
            for phone, name in contacts_data
        ]

    def _format_phone_number(self, phone: str) -> str:
        """
        Format the phone number to a standard format.

        Args:
            phone: The raw phone number string.

        Returns:
            A formatted phone number string.
        """
        return '+1' + re.sub(r'[^\d]', '', str(phone))[-10:]

    def _cache_contacts(self) -> None:
        """Cache contacts using phone number as key."""
        self.contacts_cache = {contact.phone_number: contact for contact in self.contacts}

    def get_contact_name(self, phone_number: str) -> str:
        """
        Get the contact name for a given phone number.

        Args:
            phone_number: The phone number to look up.

        Returns:
            The contact name if found, otherwise the original phone number.

        Raises:
            ValueError: If the contacts cache is empty.
        """
        if not self.contacts_cache:
            raise ValueError("Contacts cache is empty. Please load contacts before calling get_contact_name.")

        contact = self.contacts_cache.get(phone_number)
        return contact.name if contact else phone_number
