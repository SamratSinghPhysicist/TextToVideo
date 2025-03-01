import os
import sys
import subprocess

# Cross-platform environment setup for FFmpeg and ImageMagick (for moviepy==1.0.3)
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

print("ImageMagick path MoviePy will use:", os.environ["IMAGEMAGICK_BINARY"])

from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": os.environ["IMAGEMAGICK_BINARY"]})



from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    concatenate_videoclips,
    CompositeVideoClip,
    TextClip,
    vfx
)
from moviepy.video.fx.all import crop, resize

# Verify ImageMagick
try:
    if sys.platform.startswith("win"):
        subprocess.run([os.environ["IMAGEMAGICK_BINARY"], "--version"], check=True, capture_output=True, text=True)
    else:
        subprocess.run(["convert", "--version"], check=True, capture_output=True, text=True)
    print("ImageMagick is installed and accessible.")
except Exception as e:
    print("ImageMagick not found or not executable:", e)

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
    print("Starting enhanced video generation for YouTube Shorts...")
    try:
        # Load audio
        audio_clip = AudioFileClip(audio_path)
        print("Audio loaded successfully.")
        total_audio_duration = audio_clip.duration

        # Calculate scene timing
        scene_keys = sorted(images_mapping.keys())
        num_scenes = len(scene_keys)
        scene_duration = total_audio_duration / num_scenes
        print(f"Number of scenes: {num_scenes}, Scene duration: {scene_duration}s")

        # Define Shorts resolution (vertical format)
        final_width, final_height = 1080, 1920
        zoom_factor_start = 1.0  # Starting zoom level
        zoom_factor_end = 1.2    # Ending zoom level for dynamic effect

        scene_clips = []
        for i, key in enumerate(scene_keys):
            image_path = images_mapping[key]
            if not os.path.exists(image_path):
                print(f"Error: Image file not found: {image_path}")
                return
            print(f"Processing scene {key} with image: {image_path}")

            # Create base image clip
            clip = ImageClip(image_path).set_duration(scene_duration)

            # Apply zoom-in effect (Ken Burns style)
            zoomed_clip = clip.fx(vfx.resize, lambda t: zoom_factor_start + (zoom_factor_end - zoom_factor_start) * (t / scene_duration))

            # Ensure the clip fills the Shorts frame (crop if necessary)
            if zoomed_clip.w < final_width or zoomed_clip.h < final_height:
                zoomed_clip = zoomed_clip.resize(height=final_height * zoom_factor_end)
            cropped_clip = crop(zoomed_clip, width=final_width, height=final_height, 
                               x_center=zoomed_clip.w / 2, y_center=zoomed_clip.h / 2)

            # Add subtle pan effect (horizontal movement)
            max_offset_x = 20  # Reduced offset for smoother panning
            panned_clip = cropped_clip.set_position(
                lambda t, d=scene_duration: (-int(max_offset_x * (t / d)), 0)
            )

            # Combine image and text into a composite clip
            final_scene = CompositeVideoClip([panned_clip, text], size=(final_width, final_height))\
                          .set_duration(scene_duration)

            # Ensure RGB format (fix potential RGBA issues)
            final_scene = final_scene.fl_image(lambda im: im if im.shape[2] == 3 else im[:, :, :3])
            scene_clips.append(final_scene)

        if not scene_clips:
            print("No valid scene clips created.")
            return

        # Add transitions between clips (crossfade + slide)
        clips_with_transitions = [scene_clips[0]]
        for clip in scene_clips[1:]:
            # Slide transition from right to left
            sliding_clip = clip.set_position(lambda t: (final_width * (1 - t / transition_duration), 0))\
                              .crossfadein(transition_duration)
            clips_with_transitions.append(sliding_clip)

        # Concatenate clips and set audio
        final_video = concatenate_videoclips(clips_with_transitions, method="compose")\
                     .set_audio(audio_clip)

        # Apply global effects (e.g., slight brightness boost for vibrancy)
        final_video = final_video.fx(vfx.colorx, 1.1)

        print("Writing video file...")
        final_video.write_videofile(output_filename, fps=30, codec='libx264', audio_codec='aac',
                                   bitrate="8000k", preset="medium")
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