import os
# Prepend ffmpeg directory to PATH so that ffmpeg is found
os.environ["PATH"] = r"C:\ffmpeg\bin;" + os.environ["PATH"]
# Set ImageMagick binary (include the executable name)
os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"

from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": os.environ["IMAGEMAGICK_BINARY"]})

# Now import other modules
from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    concatenate_videoclips,
    CompositeVideoClip
)
import numpy as np

# Set FFmpeg binary path (if needed)
FFMPEG_BINARY = r"C:\ffmpeg\bin\ffmpeg.exe"  # Adjust if necessary

#####################################
# FINAL VIDEO GENERATION (NO SUBS)  #
#####################################
def generate_final_video(audio_path, images_mapping,
                                      output_filename="final_video.mp4",
                                      transition_duration=0.5):
    """
    Generates the final video with background image panning and crossfade transitions,
    and sets the voiceover audio. No subtitles are added.
    """
    # Load the voiceover audio to get total duration.
    audio_clip = AudioFileClip(audio_path)
    total_audio_duration = audio_clip.duration

    # Divide video into scenes based on the number of images.
    scene_keys = sorted(images_mapping.keys())  # e.g., "scene1", "scene2", ...
    num_scenes = len(scene_keys)
    scene_duration = total_audio_duration / num_scenes

    # Set final video dimensions.
    final_width = 1080
    final_height = 1920

    # For a subtle pan effect, zoom in a little.
    zoom_factor = 1.1
    max_offset_x = int(final_width * (zoom_factor - 1))

    scene_clips = []
    for i, key in enumerate(scene_keys):
        image_path = images_mapping[key]
        # Create background image clip.
        clip = ImageClip(image_path).set_duration(scene_duration)
        # Resize (zoom in) to allow room for panning.
        scaled_clip = clip.resize(zoom_factor)
        # Compute vertical offset to center the image.
        v_offset = int((scaled_clip.h - final_height) / 2)
        # Animate the position: pan from left to right over the scene duration.
        moving_clip = scaled_clip.set_position(
            lambda t, d=scene_duration: (-int(max_offset_x * t / d), -v_offset)
        )
        panned_clip = CompositeVideoClip([moving_clip], size=(final_width, final_height)).set_duration(scene_duration)
        # Ensure frame is RGB (drop alpha if any).
        panned_clip = panned_clip.fl_image(lambda im: im if im.shape[2] == 3 else im[:, :, :3])
        scene_clips.append(panned_clip)

    if not scene_clips:
        print("No valid scene clips were created. Aborting video generation.")
        return

    # Apply manual crossfade transitions.
    clips_with_transitions = [scene_clips[0]]
    for clip in scene_clips[1:]:
        clips_with_transitions.append(clip.crossfadein(transition_duration))
    
    final_video = concatenate_videoclips(clips_with_transitions, method="chain")
    final_video = final_video.set_audio(audio_clip)

    # Write the final video file.
    final_video.write_videofile(output_filename, fps=24, codec='libx264', audio_codec='aac')
    print("Final video generated and saved as:", output_filename)















#####################################
# MAIN EXECUTION                    #
#####################################

"""
if __name__ == "__main__":
    # Define your images mapping (ensure these paths are correct)
    images_mapping = {
        "scene1": "video_assets/Close-up_por.jpg",
        "scene2": "video_assets/_A_serene_co.jpg",
        "scene3": "video_assets/A_surreal_pl.jpg",
        "scene4": "video_assets/A_surreal__e.jpg",
        "scene5": "video_assets/Vast__star-s.jpg",
        "scene6": "video_assets/A_serene_mou.jpg",
        "scene7": "video_assets/A_wide-eyed_.jpg",
        "scene8": "video_assets/A_concerned_.jpg",
        "scene9": "video_assets/A_young_woma.jpg",
        "scene10": "video_assets/A_retro-futu.jpg"
    }
    # Provide the voiceover audio path (MP3 file)
    audio_path = "video_assets/output_speech.mp3"
    # Generate the final video with no subtitles.
    generate_final_video_no_subtitles(audio_path, images_mapping,
                                      output_filename="final_video.mp4",
                                      transition_duration=0.5)
"""