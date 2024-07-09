#pip install google-api-python-client
from googleapiclient.discovery import build
from google.oauth2 import service_account 
import sys
import os

SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), 'hermes-428815-234058a83f81.json')
PARENT_FOLDER_ID = "1IiTu6nJrqYrtAKBAYUiVo85VhiND-1c3"

def authenticate(): 
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
    return creds

def upload_file(file_path):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)
    
    file_metadata = {
        'name': os.path.basename(file_path),  
        'parents': [PARENT_FOLDER_ID]
    }

    file = service.files().create(
        body=file_metadata,
        media_body=file_path
    ).execute()

def upload_folder(folder_path):
    """Upload all files in a folder to Google Drive."""
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            upload_file(file_path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python google_drive_upload.py <file_path_or_folder_path>")
        sys.exit(1)
    
    path = sys.argv[1]
    if os.path.isfile(path):
        upload_file(path)
    elif os.path.isdir(path):
        upload_folder(path)
    else:
        print("Invalid path. Please provide a valid file or folder path.")
        sys.exit(1)
