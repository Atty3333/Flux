from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip
from utils import notify

import os
import random

def concatenate_videoclips(clips):
    """Concatenate clips sequentially by setting start times and combine into one CompositeVideoClip."""
    start = 0
    new_clips = []
    for clip in clips:
        new_clips.append(clip.set_start(start))
        start += clip.duration
    return CompositeVideoClip(new_clips).set_duration(start)

class VideoEditor:
    def create_type_beat_video(self, beat_path, download_video_path, title_file):

        title = title_file
        beat = AudioFileClip(beat_path)

        # Select a random video file from clips_dir
        selected_file = download_video_path
        video = VideoFileClip(selected_file)

        
        # Choose 4 random 5-second clips
        clip_duration = 5
        clips = []
        max_start = video.duration - clip_duration - 1
        for _ in range(4):
            start = random.uniform(0, max_start)
            clips.append(video.subclip(start, start + clip_duration))

        # Loop clips to match beat length
        loop_count = int(beat.duration // (clip_duration * 4)) + 1
        looped = concatenate_videoclips(clips * loop_count).subclip(0, beat.duration)
        final = looped.set_audio(beat)

        # Ensure output directory exists
        os.makedirs("output", exist_ok=True)

        # Write final video
        output_path = f"output/{title}.mp4"
        final.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            preset="slow",      # better compression/quality
            ffmpeg_params=["-crf", "18"]  # lower CRF = higher quality (range 18-28)
        )



        return output_path,  title
