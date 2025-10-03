# core/select_beat.py
import traceback
import os
import json
import random

import re
import logging
from pathlib import Path

def select_beat(beats_dir, used_beats_file="used_beats.json"):
    """
    Selects a new beat (if available), or reuses an old one.
    Returns (beat_file_name, full_path_to_beat).
    """
    # Load previously used beats
    if os.path.exists(used_beats_file):
        with open(used_beats_file, "r") as f:
            used_beats = json.load(f)
    else:
        used_beats = []

    # List all mp3 files in the beats directory
    all_beats = [f for f in os.listdir(beats_dir) if f.endswith(".mp3")]

    # Filter unused beats
    unused_beats = [b for b in all_beats if b not in used_beats]

    # Choose a beat
    if unused_beats:
        beat_file = random.choice(unused_beats)
        print(f"🎵 Using NEW beat: {beat_file}")
        used_beats.append(beat_file)
        with open(used_beats_file, "w") as f:
            json.dump(used_beats, f, indent=2)
    else:
        beat_file = random.choice(all_beats)
        print("Youtube Bot",f"🎵 All beats used — reusing OLD beat: {beat_file}")
    thumbnail_keyword,video_keyword=extract_video_keyword(beat_file)

    return beat_file,video_keyword,thumbnail_keyword

def youtube_title(filename):
    # Remove file extension
    name = re.sub(r'\.mp3$', '', filename, flags=re.IGNORECASE)

    # Remove "(beat 90)" or similar patterns
    name = re.sub(r'\(.*?beat.*?\)', '', name, flags=re.IGNORECASE)   

    name= re.sub(r"\(bpm\s*\d+\)", "", name, flags=re.IGNORECASE).strip() 
    name = re.sub(r'\btype beat\b', '', name, flags=re.IGNORECASE)

    name=name+" type beat"
    return name





def title_extract(title, channel_name):
    try:
        # Get filename only
        title = os.path.basename(title).replace(".mp3", "")
        description_title = title

        bpm = ""
        beat_number = ""

        # Extract BPM (case-insensitive)
        bpm_match = re.search(r"(\d+)\s*BPM", title, re.IGNORECASE)
        if bpm_match:
            bpm = bpm_match.group(1)

        # Extract beat number if present
        beat_match = re.search(r"\(beat\s*(\d+)\)", title, re.IGNORECASE)
        if beat_match:
            beat_number = beat_match.group(1)
            # Extract @mention
        mention_match = re.search(r'@(\S+)', title)
        mention = mention_match.group(1) if mention_match else None

        # Remove @mention from title
        title = re.sub(r'@\S+', '', title)
        # Remove extra info in parentheses from main title
        cleaned_title = youtube_title(title)
        
        return description_editor(cleaned_title, description_title, beat_number, channel_name,mention)

    except Exception as e:
        print("Error extracting title data:", e)
        return None
  
def description_editor(title,description_title,beat_number ,channel_name,mention="@madebyletsoo"):
    try:  
        
        description_file = f"config/{channel_name}" +"/description.txt"


        with open(description_file, 'r', encoding='utf-8') as f:
            description = f.read()
            
            
            if mention:
                mention=mention
                

                
            else:
                mention=""
            description=description_title+description
   
        return title,description,beat_number    
    except Exception as e:
        traceback.print_exc()

def channel_content_extractor(channel_name,channels_json):
                # Get the path to the default Music/beats folder

            with open(channels_json, "r") as f:
                channels = json.load(f)

            if channel_name not in channels:
                raise ValueError(f"Channel '{channel_name}' not found in channels.json")

            # Get the channel content (e.g., "21 savage")
            content_folder = channels[channel_name]["Channel_content"]            
            beats_dir = Path.home() / "OneDrive" / "work" / "beats" / "semi_finished" / "type beat"
            beats_dir = beats_dir/content_folder


            beat_files = [f for f in os.listdir(beats_dir) if f.endswith(".mp3")]
     
            if not beat_files:
                logging.warning("No beat files found in the 'beats' folder. Skipping this account.")
                print("Youtube Bot","No beat files found in the 'beats' folder. Skipping this account.")
            return beats_dir    

def extract_video_keyword(filename):
    # Remove file extension
    name = re.sub(r'\.mp3$', '', filename, flags=re.IGNORECASE)

    # Remove "(beat 90)" or similar patterns
    name = re.sub(r'\(.*?beat.*?\)', '', name, flags=re.IGNORECASE)

    # Remove "[Free]" and similar brackets
    name = re.sub(r'\[.*?\]', '', name)

    name2=name

    # Remove all instances of "type beat"
    name = re.sub(r'\btype beat\b', '', name, flags=re.IGNORECASE)
   

    
    video_keyword=name + "music video"
    video_keyword= re.sub(r"\(bpm\s*\d+\)", "", video_keyword, flags=re.IGNORECASE).strip()
    video_keyword=clean_title(video_keyword)
    
    thumbnail_keyword=name2
    thumbnail_keyword= re.sub(r"\(bpm\s*\d+\)", "", video_keyword, flags=re.IGNORECASE).strip()
    thumbnail_keyword=clean_title(name)   
    thumbnail_keyword=thumbnail_keyword+" type beat"

    print("thumbnail: "+thumbnail_keyword)
    print("video: "+video_keyword)


    return thumbnail_keyword,video_keyword









def clean_title(title):
    """
    Removes unwanted words like 'dark', 'hard' (case-insensitive)
    and strips extra spaces from a video title.
    """
    # Words you want to remove
    unwanted = ["dark", "hard"]

    # Regex to remove whole words, ignoring case
    pattern = r"\b(" + "|".join(unwanted) + r")\b"
    cleaned = re.sub(pattern, "", title, flags=re.IGNORECASE)

    # Collapse multiple spaces and trim
    return re.sub(r"\s+", " ", cleaned).strip()