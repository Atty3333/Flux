import cv2
import os
import numpy as np
import random
import requests
from youtubesearchpython import VideosSearch
import traceback
import re

import requests
import os
import random
from io import BytesIO
from PIL import Image
import yt_dlp
from yt_dlp import YoutubeDL

import time


def safe_thumbnail_path(output_dir, title, video_id):
    os.makedirs(output_dir, exist_ok=True)
    title_clean = re.sub(r'[\\/*?:"<>|]', '', title)
    filename = f"{title_clean}_{video_id}_{int(time.time())}.jpg"  # timestamp ensures unique
    return os.path.join(output_dir, filename)








def download_thumbnail(keyword, thumbnails_dir="thumbnails"):
    import os, re, time, random, requests
    from yt_dlp import YoutubeDL

    try:
        PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cookies_path = os.path.join(PROJECT_ROOT, 'config', 'cookies.txt')
        folder_path = os.path.join(PROJECT_ROOT, thumbnails_dir)
        os.makedirs(folder_path, exist_ok=True)  # create folder, not file

        cookiefile = cookies_path if os.path.exists(cookies_path) else None
        print(f"Output folder: {folder_path}")
        print(f"Using cookies: {cookiefile if cookiefile else 'None'}")

        ydl_opts = {
            'quiet': False,
            'skip_download': True,
            'noplaylist': True,
            'ignoreerrors': True,
            'cookiefile': cookiefile,
            'extract_flat': True,
        }

        search_query = f"ytsearch5:{keyword}"
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)

        entries = info.get('entries', [])
        if not entries:
            print("❌ No results found.")
            return None

        random.shuffle(entries)

        for entry in entries:
            if not entry:
                continue

            thumbnail_url = entry.get("thumbnail")
            if not thumbnail_url and "thumbnails" in entry:
                thumbnails = entry["thumbnails"]
                if thumbnails:
                    thumbnails.sort(key=lambda x: x.get("width", 0), reverse=True)
                    thumbnail_url = thumbnails[0].get("url")
            if not thumbnail_url:
                continue

            # Safe filename
            title = re.sub(r'[\\/*?:"<>|]', '', entry.get('title', 'video'))
            video_id = entry.get("id", "")
            filename = f"{title}_{video_id}_{int(time.time())}.jpg"
            thumb_path = os.path.join(folder_path, filename)

            # Download
            response = requests.get(thumbnail_url, timeout=10)
            response.raise_for_status()
            with open(thumb_path, "wb") as f:
                f.write(response.content)

            print(f"✅ Downloaded thumbnail: {thumb_path}")
            return thumb_path  # Return the actual file path

        print("❌ No valid thumbnails found.")
        return None

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

