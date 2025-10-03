
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle
import os

from google_auth_oauthlib.flow import InstalledAppFlow
from utils import notify
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
import time
from google.oauth2.credentials import Credentials
class Uploader:
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_folder=os.path.join(PROJECT_ROOT, 'config')
    def __init__(self, account):
        self.service = self.authenticate(account)

    def authenticate(self, account):
        """
        Authenticates a YouTube account with JSON-based tokens.
        """
        scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        token_path = account['youtube_token_path']
        secret_path = account['youtube_secret_path']

        creds = None

        # Try to load JSON token if it exists
        if os.path.exists(token_path):
            try:
                creds = Credentials.from_authorized_user_file(token_path, scopes)
            except Exception as e:
                print(f"⚠️ Existing token file invalid; will re-authenticate. {e}")
                creds = None

        # Refresh expired token
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print("🔁 Refresh failed, forcing re-authentication:", e)
                creds = None

        # If still no valid credentials, re-authenticate
        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(secret_path, scopes)
            creds = flow.run_local_server(port=0)

            # Save JSON token
            with open(token_path, "w") as token_file:
                token_file.write(creds.to_json())

        return build('youtube', 'v3', credentials=creds)
    
    
    
   
    def schedule_upload_video(self, video_path, title, description, tags, thumbnail_path, publish_time_utc=None):
        import os
        from googleapiclient.http import MediaFileUpload

        # 1️⃣ Prepare status
        status = {}
        if publish_time_utc:
            status['privacyStatus'] = 'private'
            # Convert to RFC3339 without double UTC info
            status['publishAt'] = publish_time_utc.replace(tzinfo=None).isoformat() + 'Z'
        else:
            status['privacyStatus'] = 'public'

        # 2️⃣ Build request body
        request_body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags
            },
            'status': status
        }

        # 3️⃣ Upload video
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        request = self.service.videos().insert(
            part='snippet,status',
            body=request_body,
            media_body=media
        )
        response = request.execute()
        video_id = response['id']



        # 5️⃣ Safely write thumbnail if needed
        if os.path.exists(thumbnail_path):
            # Ensure no other program has it open
            try:
                with open(thumbnail_path, "rb") as f:
                    f.read(1)  # test read access
            except PermissionError:
                raise PermissionError(f"Cannot access thumbnail: {thumbnail_path}. Close any program using it.")

            # Upload thumbnail
            self.service.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
        else:
            print(f"❌ Thumbnail not found: {thumbnail_path}")

        # 6️⃣ Notify
        notify("Youtube Bot", f"Video uploaded with ID: {video_id}")
        if publish_time_utc:
            notify("Youtube Bot", f"Scheduled to publish at {publish_time_utc.isoformat()} UTC")
        else:
            notify("Youtube Bot", "Published immediately")

        return video_id


    

