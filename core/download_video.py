



import os
import json
import random
import io
import logging
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request



# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_path = os.path.join(PROJECT_ROOT, 'clips')
output_file=os.path.join(output_path, 'output.mp4')
config_folder=os.path.join(PROJECT_ROOT, 'config')




# Scopes - readonly is enough to list & download files
DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

def get_drive_service(secret_path, token_path, scopes=DRIVE_SCOPES):
    """
    Returns an authorized Google Drive v3 service.
    Creates or refreshes token_path (token.json) as needed.
    """
    creds = None

    # Try load existing token.json
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, scopes)
        except Exception as e:
            # e.g. file exists but not the expected JSON format
            print("⚠️ Existing token file invalid; will re-authenticate.", e)
            creds = None

    # If no valid creds, refresh or do full OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print("⚠️ Refresh failed; will run full auth flow.", e)
                creds = None

        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(secret_path, scopes)
            creds = flow.run_local_server(port=0)

        # Save credentials to token_path (overwrites old formats)
        with open(token_path, "w") as token_file:
            token_file.write(creds.to_json())

    return build("drive", "v3", credentials=creds)


def download_video(keyword, channel_name):
    """
    Search a Google Drive folder (configured per channel) for a file that contains
    the keyword words and download the first random match to output_file.
    - config_folder: path to directory containing channels.json
    - output_file: full path where the file will be saved
    Returns output_file or None if nothing matched.
    """
    # Load channel config from channels.json
    channels_json_path = os.path.join(config_folder, "channels.json")
    with open(channels_json_path, "r", encoding="utf-8") as f:
        channels = json.load(f)

    channel_config = channels.get(channel_name)
    if not channel_config:
        raise ValueError(f"Channel '{channel_name}' not found in channels.json")

    folder_id = channel_config["folder_id"]
    client_secret_path = channel_config["drive_secret_path"]   # client_secret.json
    token_path = channel_config["drive_token_path"]            # token.json (will be created)

    # Build Drive service (this will open browser only if token missing/invalid)
    drive = get_drive_service(client_secret_path, token_path)

    # List files in the folder
    query = f"'{folder_id}' in parents and trashed = false"
    results = drive.files().list(q=query, pageSize=1000, fields="files(id,name,mimeType)").execute()
    file_list = results.get("files", [])

    if not file_list:
        print(f"No files found in folder {folder_id}")
        return None

    keyword_parts = keyword.lower().split()

    # Filter files whose names contain ANY keyword part
    matched_files = [
        f for f in file_list
        if any(part in (f.get("name") or "").lower() for part in keyword_parts)
    ]

    if not matched_files:
        print(f"No files found containing the keyword: {keyword}")
        return None

    # Randomize and pick first
    random.shuffle(matched_files)
    file_to_download = matched_files[0]
    print(f"Downloading: {file_to_download['name']} (id={file_to_download['id']})")

    # Download file content
    request = drive.files().get_media(fileId=file_to_download["id"])
    fh = io.FileIO(output_file, mode="wb")
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    try:
        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"Download {int(status.progress() * 100)}%")
    finally:
        fh.close()

    return output_file















