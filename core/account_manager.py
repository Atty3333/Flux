
import json
from utils import *
import os
class AccountManager:
    def __init__(self):


        # Build the path to clips/source_video.mp4
        file_location = get_path( "config", "channels.json")
        print(file_location)
        with open(file_location) as f:
            self.accounts = json.load(f)

    def get_all_accounts(self):
        return self.accounts.items()
