import os
import logging
from core.video_editor import VideoEditor
from core.uploader import Uploader
from core.organizer import Organizer
from core.account_manager import AccountManager
from core.select_beat import select_beat
from core.select_beat import channel_content_extractor
from core.select_beat import title_extract
from core.download_video import download_video


from core.thumbnail_generator import download_thumbnail
import traceback


from utils import notify
from utils import schedule
from utils import log_error_to_file
from pathlib import Path
import json

import pytz
from datetime import datetime, time, timedelta






# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    manager = AccountManager()

    for channel_name, account in manager.get_all_accounts():
        try:

            
           
            notify("Youtube Bot",f"Uploading for {channel_name}...")
            logging.warning(f"Uploading for {channel_name}...")

            #takes the channel content
            channels_json = "config\channels.json"
            beats_dir = channel_content_extractor(channel_name,channels_json)
           

            # Beat selection
            beat_file,Video_keyword,thumbnail_keyword = select_beat(beats_dir)
            #creates the beat path using the beats_dir and the beat file
            beat_path = os.path.join(beats_dir, beat_file)


            # file config 
            title_file = beat_file
            tags_file = f"config/{channel_name}" +"/tags.txt"
            print(tags_file)

            # Download video
            logging.error("Download starting......")
            try:
                #Video_keyword="21 savage music video"
                print("Video keyword is : "+Video_keyword)
                download_video_path = download_video(Video_keyword,channel_name)
                if not os.path.exists(download_video_path):
                    logging.error("Downloaded video not found. Skipping this account.")
                    notify("Youtube Bot","Downloaded video not found. Skipping this account.")
                    continue
            except Exception as e:
                logging.error(f"Download failed: {e}")
                notify("Youtube Bot",f"Download failed: {e}")
                continue

            # Video creation
            logging.error("Video Creation is starting.........")
            editor = VideoEditor()
            try:
                final_video_path,  title = editor.create_type_beat_video(
                    beat_path=beat_path,
                    download_video_path=download_video_path,  # ✅ Correct
                    title_file=title_file
                )
            except Exception as e:
                logging.error(f"Video creation failed: {e}")
                notify("Youtube Bot",f"Video creation failed: {e}")
                traceback.print_exc()
                continue
            
            # Thumbnail
            try:
                print("Thumbnail keyword is"+thumbnail_keyword)
                thumbnail_path =download_thumbnail(thumbnail_keyword)
                
            except Exception as e:
                logging.warning(f"Thumbnail generation failed, using default thumbnail. Error: {e}")
                notify("Youtube Bot",f"Thumbnail generation failed, using default thumbnail. Error: {e}")

               
            logging.error("Video Uploading starting......")

            # Upload
            try:
                title,description,beat_number=title_extract(title,channel_name)
                publish_time_utc=schedule()
                uploader = Uploader(account)
                
                tags = open(tags_file).read().split(",")
                uploader.schedule_upload_video(
                    video_path=final_video_path,
                    title=title,
                    description=description,
                    tags=tags,
                    thumbnail_path=thumbnail_path,
                    
                )
            except Exception as e:
                logging.error(f"Upload failed: {e}")
                notify("Youtube Bot",f"Upload failed: {e}")
                traceback.print_exc()
                continue
            logging.error("organizing starting.......")           
            
            Organizer.setup_beat_folder(channel_name,title,description,beat_number,thumbnail_path)
           
            Organizer.clear(thumbnail_path,final_video_path,download_video_path)
            
            notify("Youtube Bot","Bot done with uploading the video!!!!!!")
        except Exception as e:
            error_trace = traceback.format_exc()
            logging.exception(f"Unexpected error for {channel_name}: {error_trace}")
            notify("Youtube Bot",f"Unexpected error for {channel_name}: {error_trace}")
            
            log_error_to_file(error_trace)
           

if __name__ == "__main__":
    main()



#future update:

 
#loging of the errors

