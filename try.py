import os

folder = r"c:\Users\windows 10 pro\Documents\Work\youtube_beat_bot_v2\youtube_beat_bot_v2\youtube_beat_bot\thumbnails"

try:
    os.makedirs(folder, exist_ok=True)  # ensure folder exists
    test_file = os.path.join(folder, "test.txt")
    with open(test_file, "w") as f:
        f.write("test")
    os.remove(test_file)
    print("✅ Folder is writable")
except PermissionError:
    print("❌ Permission denied: cannot write to this folder")
except Exception as e:
    print(f"⚠️ Unexpected error: {e}")
