import os
import sys
import subprocess

# Cross-platform environment setup for FFmpeg and ImageMagick
if sys.platform.startswith("win"):
    # Windows-specific settings
    os.environ["PATH"] = r"C:\ffmpeg\bin;" + os.environ["PATH"]
    os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
    FFMPEG_BINARY = r"C:\ffmpeg\bin\ffmpeg.exe"
else:
    # For Linux/macOS, assume ffmpeg is installed in PATH.
    FFMPEG_BINARY = "ffmpeg"
    # On many Linux systems (like Railway's container), ImageMagick is installed with 'convert' at /usr/bin/convert
    os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"

from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": os.environ["IMAGEMAGICK_BINARY"]})

from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    concatenate_videoclips,
    CompositeVideoClip
)


try:
    subprocess.run([FFMPEG_BINARY, "-version"], check=True, capture_output=True, text=True)
    print("FFmpeg is installed and accessible.")
except Exception as e:
    print("FFmpeg not found or not executable:", e)



#####################################
# FINAL VIDEO GENERATION (NO SUBS)  #
#####################################
def generate_final_video(audio_path, images_mapping, output_filename="final_video.mp4", transition_duration=0.5):
    print("Starting video generation...")
    try:
        audio_clip = AudioFileClip(audio_path)
        print("Audio loaded successfully.")
        total_audio_duration = audio_clip.duration

        scene_keys = sorted(images_mapping.keys())
        num_scenes = len(scene_keys)
        scene_duration = total_audio_duration / num_scenes
        print(f"Number of scenes: {num_scenes}, Scene duration: {scene_duration}s")

        final_width, final_height = 1080, 1920
        zoom_factor = 1.1
        max_offset_x = int(final_width * (zoom_factor - 1))

        scene_clips = []
        for i, key in enumerate(scene_keys):
            image_path = images_mapping[key]
            if not os.path.exists(image_path):
                print(f"Error: Image file not found: {image_path}")
                return
            print(f"Processing scene {key} with image: {image_path}")
            clip = ImageClip(image_path).set_duration(scene_duration)
            scaled_clip = clip.resize(zoom_factor)
            v_offset = int((scaled_clip.h - final_height) / 2)
            moving_clip = scaled_clip.set_position(
                lambda t, d=scene_duration: (-int(max_offset_x * t / d), -v_offset)
            )
            panned_clip = CompositeVideoClip([moving_clip], size=(final_width, final_height)).set_duration(scene_duration)
            panned_clip = panned_clip.fl_image(lambda im: im if im.shape[2] == 3 else im[:, :, :3])
            scene_clips.append(panned_clip)

        if not scene_clips:
            print("No valid scene clips created.")
            return

        clips_with_transitions = [scene_clips[0]]
        for clip in scene_clips[1:]:
            clips_with_transitions.append(clip.crossfadein(transition_duration))

        final_video = concatenate_videoclips(clips_with_transitions, method="chain").set_audio(audio_clip)
        print("Writing video file...")
        final_video.write_videofile(output_filename, fps=24, codec='libx264', audio_codec='aac')
        print("Final video generated and saved as:", output_filename)
    except Exception as e:
        print("Error in video generation:", e)













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