import sqlite3
import datetime
import json
from typing import List, Dict, Union
from glob import glob
import re  # Add this import at the top of your file if not already present

class TextCollector:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = self._connect_database()

    def _connect_database(self) -> Union[sqlite3.Connection, None]:
        try:
            connection = sqlite3.connect(self.db_path)
            return connection
        except sqlite3.OperationalError as error:
            print(f"Failed to connect to the database at {self.db_path}. Error: {error}")
            return None

    def get_all_chat_ids_with_labels(self) -> List[tuple]:
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
        chats = cursor.fetchall()
        cursor.close()

        # Load contacts to map phone numbers to names
        contacts = self.load_contacts()

        # Enrich chats with contact names where display_name is a phone number
        enriched_chats = []
        for chat_id, display_name, chat_identifier in chats:
            if display_name == '' and chat_identifier in contacts:
                display_name = contacts[chat_identifier]
            enriched_chats.append((chat_id, display_name, chat_identifier))

        return enriched_chats



    def load_contacts(self) -> Dict[str, str]:
        
        try:
            # Adjust the path to your specific setup
            path_pattern = '/Users/*/Library/Application Support/AddressBook/Sources/*/AddressBook-v22.abcddb'
            database_paths = glob(path_pattern)
            
            if not database_paths:
                print("No AddressBook database found.")
                return {}
            
            database_path = database_paths[0]
           
            conn = sqlite3.connect(database_path)
            cursor = conn.cursor()
           
            query = '''
            SELECT p.ZFULLNUMBER, 
                   TRIM(COALESCE(r.ZFIRSTNAME || ' ' || NULLIF(r.ZLASTNAME, ''), r.ZFIRSTNAME, r.ZLASTNAME)) AS FullName
            FROM ZABCDPHONENUMBER p
            JOIN ZABCDRECORD r ON p.ZOWNER = r.Z_PK
            ORDER BY r.ZLASTNAME ASC, r.ZFIRSTNAME ASC
            '''
            cursor.execute(query)
            contacts_data = cursor.fetchall()
            
            contacts = {
                '+1' + re.sub(r'[^\d]', '', str(phone))[-10:]: name 
                for phone, name in contacts_data
            }            

            # Close connection
            cursor.close()
            conn.close()
            

            return contacts
        except sqlite3.Error as e:
            return {}



    def read_messages(self, chat_id: int, self_number='Me', human_readable_date=True) -> List[Dict[str, str]]:
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
        contacts = self.load_contacts()
        for result in results:
            rowid, date, text, attributed_body, handle_id, is_from_me, cache_has_attachments = result
            phone_number = self_number if is_from_me else contacts.get(handle_id, handle_id)
            
            body = self.extract_message_body(text, attributed_body)
            date = self.format_time(date) if human_readable_date else date
            
            if phone_number:
                messages.append({"date": date, "body": body, "phone_number": phone_number})
        
        cursor.close()
        return messages

    def extract_message_body(self, text: str, attributed_body: bytes) -> str:
        if text:
            return text
        
        if attributed_body:
            decoded_body = attributed_body.split(b"NSString")[1]
            text = decoded_body[5:]
            if text[0] == 129:
                length = int.from_bytes(text[1:3], "little") 
                text = text[3:length+3]
            else:
                length = text[0]
                text = text[1:length+1]
            return text.decode()
        
        return ""

    def format_time(self, time_sent: int) -> str:
        apple_epoch = datetime.datetime(2001, 1, 1)
        time_sent_seconds = time_sent / 1_000_000_000
        time_sent_datetime = apple_epoch + datetime.timedelta(seconds=time_sent_seconds)
        return time_sent_datetime.strftime('%Y-%m-%d %H:%M')
