import sqlite3
import datetime
import json

class TextCollector:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = self._connect_database()

    def _connect_database(self):
        """Establishes a connection to the SQLite database."""
        try:
            connection = sqlite3.connect(self.db_path)
            return connection
        except sqlite3.OperationalError as error:
            print(f"Failed to connect to the database at {self.db_path}. Error: {error}")
            return None

    def get_all_chat_ids_with_labels(self):
        """Retrieves chat IDs and associated labels, prioritizing group chat names over phone numbers."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT cmj.chat_id, c.display_name, c.chat_identifier
            FROM chat_message_join AS cmj
            JOIN message AS m ON cmj.message_id = m.ROWID
            INNER JOIN chat AS c ON cmj.chat_id = c.ROWID
            GROUP BY cmj.chat_id
            ORDER BY MAX(m.date) DESC;
        """)
        chats = cursor.fetchall()
        chats = [chat for chat in chats if chat[1] is not None or chat[2] is not None]
        cursor.close()
        return chats
    
    def load_contacts(self):
        try:
            with open("contacts.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def read_messages(self, chat_id, self_number='Jack', human_readable_date=True):
        cursor = self.conn.cursor()

        query = """
        SELECT message.ROWID, message.date, message.text, message.attributedBody, handle.id, message.is_from_me, message.cache_has_attachments 
        FROM message
        LEFT JOIN handle ON message.handle_id = handle.ROWID
        WHERE message.ROWID IN (SELECT message_id FROM chat_message_join WHERE chat_id = ?)
        ORDER BY message.date
        """

        results = cursor.execute(query, (chat_id,)).fetchall()
        messages = []
        contacts = self.load_contacts()  # Load contacts

        for result in results:
            rowid, date, text, attributed_body, handle_id, is_from_me, cache_has_attachments = result
            if is_from_me:
                phone_number = self_number
            else:
                phone_number = contacts.get(handle_id, handle_id)

            body = text if text is not None else ""
            if attributed_body and not body:
                decoded_body = attributed_body.split(b"NSString")[1]
                text = decoded_body[5:]  # stripping some preamble which generally looks like this: b'\x01\x94\x84\x01+'

                # this 129 is b'\x81, python indexes byte strings as ints,
                # this is equivalent to text[0:1] == b'\x81'
                if text[0] == 129:
                    length = int.from_bytes(text[1:3], "little")
                    text = text[3: length + 3]
                else:
                    length = text[0]
                    text = text[1: length + 1]
                body = text.decode()

            if human_readable_date:
                date = self.format_time(date)

            if phone_number is None:
                continue

            messages.append({"date": date, "body": body, "phone_number": phone_number})

        cursor.close()
        return messages

    def format_time(self, time_sent):
        """Formats a timestamp (in nanoseconds since 2001-01-01) into a human-readable date and time string."""
        apple_epoch = datetime.datetime(2001, 1, 1)
        # Convert nanoseconds to seconds to avoid overflow
        time_sent_seconds = time_sent / 1_000_000_000  # Convert from nanoseconds to seconds
        time_sent_datetime = apple_epoch + datetime.timedelta(seconds=time_sent_seconds)
        return time_sent_datetime.strftime('%Y-%m-%d %H:%M')
