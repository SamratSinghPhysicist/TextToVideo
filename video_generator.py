import os
from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    concatenate_videoclips,
    CompositeVideoClip,
    VideoClip
)
from moviepy.config import change_settings
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Set the ImageMagick binary path (update if needed)
change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})

def make_subtitle_frame(t, scene_text, scene_duration, clip_width, max_subtitle_height):
    """
    Creates an RGB image (as a NumPy array) for the subtitle at time t.
    The full scene_text is wrapped into multiple lines if needed and the word
    corresponding to the current time is highlighted in bright green.
    """
    font_size = 40
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    margin = 20
    available_width = clip_width - 2 * margin

    words = scene_text.split()
    nwords = len(words)
    if nwords == 0:
        # Create a blank RGB image (black background)
        img = Image.new("RGB", (clip_width, max_subtitle_height), (0, 0, 0))
        return np.array(img)

    # Determine the current word index (each word gets an equal portion of scene_duration)
    segment_duration = scene_duration / nwords
    current_word_index = int(t / segment_duration)
    if current_word_index >= nwords:
        current_word_index = nwords - 1

    # Create a temporary image for text measurement.
    temp_img = Image.new("RGB", (clip_width, max_subtitle_height))
    draw = ImageDraw.Draw(temp_img)
    space_width, _ = draw.textsize(" ", font=font)

    # Wrap text manually into lines.
    lines = []
    current_line = []
    current_line_width = 0
    for i, word in enumerate(words):
        word_width, _ = draw.textsize(word, font=font)
        if not current_line:
            current_line.append((word, i))
            current_line_width = word_width
        else:
            if current_line_width + space_width + word_width <= available_width:
                current_line.append((word, i))
                current_line_width += space_width + word_width
            else:
                lines.append(current_line)
                current_line = [(word, i)]
                current_line_width = word_width
    if current_line:
        lines.append(current_line)

    # Calculate total text block height.
    line_height = font.getsize("Ay")[1] + 10  # add spacing
    text_block_height = line_height * len(lines)

    # If the text block is too tall, reduce font size until it fits.
    while text_block_height > max_subtitle_height and font_size > 10:
        font_size -= 2
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()
        draw = ImageDraw.Draw(temp_img)
        lines = []
        current_line = []
        current_line_width = 0
        space_width, _ = draw.textsize(" ", font=font)
        for i, word in enumerate(words):
            word_width, _ = draw.textsize(word, font=font)
            if not current_line:
                current_line.append((word, i))
                current_line_width = word_width
            else:
                if current_line_width + space_width + word_width <= available_width:
                    current_line.append((word, i))
                    current_line_width += space_width + word_width
                else:
                    lines.append(current_line)
                    current_line = [(word, i)]
                    current_line_width = word_width
        if current_line:
            lines.append(current_line)
        line_height = font.getsize("Ay")[1] + 10
        text_block_height = line_height * len(lines)

    # Create a new RGB image for the subtitle (black background)
    img = Image.new("RGB", (clip_width, max_subtitle_height), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Center the text block vertically.
    y_start = (max_subtitle_height - text_block_height) // 2

    # Draw each line, centering it horizontally.
    for line in lines:
        line_width = sum(draw.textsize(word, font=font)[0] for word, _ in line) + space_width * (len(line) - 1)
        x_start = (clip_width - line_width) // 2
        x = x_start
        for word, idx in line:
            # Highlight the current word in bright green ("lime"); others in white.
            color = "lime" if idx == current_word_index else "white"
            draw.text((x, y_start), word, font=font, fill=color)
            w, _ = draw.textsize(word, font=font)
            x += w + space_width
        y_start += line_height

    return np.array(img)

def generate_final_video(script, images_mapping, audio_path,
                         output_filename="final_video.mp4",
                         transition_duration=0.5):
    """
    Combines images, voiceover audio, and dynamic RGB subtitles with realtime word highlighting,
    along with animations and crossfade transitions to generate the final video.
    """
    # Split the script into scenes (each scene corresponds to one image and subtitle).
    scenes = [scene.strip() for scene in script.split("\n\n") if scene.strip() != ""]
    num_scenes = len(scenes)
    if num_scenes == 0:
        print("No scenes found in script. Aborting video generation.")
        return

    # Load the voiceover audio.
    audio_clip = AudioFileClip(audio_path)
    total_audio_duration = audio_clip.duration

    # Calculate duration for each scene.
    scene_duration = total_audio_duration / num_scenes

    # Set final video dimensions.
    final_width = 1080
    final_height = 1920

    # For a subtle pan effect, zoom in a little (e.g., 10% larger).
    zoom_factor = 1.1
    max_offset_x = int(final_width * (zoom_factor - 1))  # extra width for panning

    scene_clips = []

    for i, scene_text in enumerate(scenes):
        image_key = f"scene{i+1}"
        if image_key in images_mapping:
            image_path = images_mapping[image_key]
        else:
            print(f"Image for {image_key} not found. Skipping this scene.")
            continue

        # Create an ImageClip with the given duration.
        clip = ImageClip(image_path).set_duration(scene_duration)
        # Resize (zoom in) to allow room for panning.
        scaled_clip = clip.resize(zoom_factor)
        # Compute vertical offset to center the image.
        v_offset = int((scaled_clip.h - final_height) / 2)
        # Animate the position: pan horizontally from left to right.
        moving_clip = scaled_clip.set_position(lambda t: (-int(max_offset_x * t / scene_duration), -v_offset))
        # Create a composite clip (the background) of fixed size.
        panned_clip = CompositeVideoClip([moving_clip], size=(final_width, final_height)).set_duration(scene_duration)
        # Create a dynamic subtitle clip as an RGB VideoClip.
        subtitle_clip = VideoClip(
            lambda t: make_subtitle_frame(t, scene_text, scene_duration, final_width, max_subtitle_height=200),
            duration=scene_duration
        ).set_position(('center', 'center'))
        # Overlay the subtitle on the background.
        composite_clip = CompositeVideoClip([panned_clip, subtitle_clip]).set_duration(scene_duration)
        composite_clip = composite_clip.set_fps(24)
        scene_clips.append(composite_clip)

    if not scene_clips:
        print("No valid scene clips were created. Aborting video generation.")
        return

    # Apply manual crossfade transitions.
    clips_with_transitions = [scene_clips[0]]
    for clip in scene_clips[1:]:
        clips_with_transitions.append(clip.crossfadein(transition_duration))
    
    # Concatenate the clips.
    final_video = concatenate_videoclips(clips_with_transitions, method="chain")
    final_video = final_video.set_audio(audio_clip)

    # Write the final video (RGB frames).
    final_video.write_videofile(output_filename, fps=24, codec='libx264', audio_codec='aac')
    print("Final video generated and saved as:", output_filename)

# For testing the function independently:
if __name__ == "__main__":
    sample_script = (
        "Kya aapko pata h?\n\n"
        "Iceberg se collision toh hua, woh toh sabko pata h\n\n"
        "But real reason is steel"
    )
    images_mapping = {
        "scene1": "video_assets/A_group_of_I.jpg",
        "scene2": "video_assets/A_lone_astro.jpg",
        "scene3": "video_assets/A_vibrant__o.jpg",
    }
    audio_path = "video_assets/output_speech.mp3"
    generate_final_video(sample_script, images_mapping, audio_path,
                         output_filename="final_video.mp4", transition_duration=0.5)
