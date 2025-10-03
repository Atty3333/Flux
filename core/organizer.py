
import shutil
import os
from datetime import datetime
import traceback
import os
from pathlib import Path
from PIL import Image  # optional if you're handling image saving
import shutil
from utils import notify

class Organizer:
    @staticmethod
    def clear(thumbnail_path=None, output_video_path=None, source_video_path=None):
        paths = [thumbnail_path, output_video_path, source_video_path]
        try:
            for file_path in paths:
                if file_path:
                    path = Path(file_path)
                    if path.exists():
                        try:
                            path.unlink()
                            print(f"Deleted: {path}")
                        except Exception as e:
                            print(f"Failed to delete {path}: {e}")
                    else:
                        print(f"File not found: {path}")
        except Exception as e:
            
            traceback.print_exc()        
    def setup_beat_folder(channel_name, title, description , beat_title, thumbnail_path=None):
        try:    

            base_path  = Path.home() / "OneDrive" / "work" / "Beatstar_to_be" / channel_name / beat_title
         
            
            base_path.mkdir(parents=True, exist_ok=True)

            # Save title + description
            description_file = base_path / "description.txt"
            with open(description_file, "w", encoding="utf-8") as f:
                f.write(f"{title}\n\n{description}")

            # Save or copy thumbnail
            if thumbnail_path:
                # If you're copying an existing thumbnail file
                thumbnail_dest = base_path / "thumbnail.jpg"
                shutil.copy(thumbnail_path, thumbnail_dest)
                print(f"Thumbnail copied to: {thumbnail_dest}")
            else:
                print("No thumbnail provided — skipped saving it.")

            notify("Youtube Bot",f"Folder structure created under: {base_path}")
            print(f"Folder structure created under: {base_path}")
            
        except Exception as e:
           
            traceback.print_exc()

#delete thubnail
# delete source_video
# delete output
           