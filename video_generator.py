import os
import subprocess
import json
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

#Download ffmpeg (Note: Don't download source code instead go for windows)
# Set FFmpeg binary path. If FFmpeg is in your system's PATH, you can leave it as "ffmpeg".
FFMPEG_BINARY = r"C:\ffmpeg\bin\ffmpeg.exe"  # <-- Update this if necessary

##############################
# 1. TRANSCRIBE THE AUDIO    #
##############################

def transcribe_audio(audio_path, model_path="model"):
    """
    Transcribes the given audio file using VOSK and returns a list of words.
    Each word is a dict with keys: "word", "start", "end".
    The audio is converted on the fly to 16kHz mono.
    """
    if not os.path.exists(model_path):
        print("VOSK model not found. Please download a model and place it in the 'model' folder.")
        return []
    try:
        from vosk import Model, KaldiRecognizer
    except ImportError:
        print("Please install vosk (`pip install vosk`) to enable speech-to-text transcription.")
        return []
    
    model = Model(model_path)
    # Run FFmpeg to convert audio to 16kHz mono PCM s16le.
    process = subprocess.Popen(
        [FFMPEG_BINARY, "-loglevel", "quiet", "-i", audio_path, "-ar", "16000", "-ac", "1", "-f", "s16le", "-"],
        stdout=subprocess.PIPE
    )
    rec = KaldiRecognizer(model, 16000)
    rec.SetWords(True)
    transcript_words = []
    while True:
        data = process.stdout.read(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            if "result" in res:
                transcript_words.extend(res["result"])
    final_res = json.loads(rec.FinalResult())
    if "result" in final_res:
        transcript_words.extend(final_res["result"])
    return transcript_words

#####################################
# 2. DYNAMIC SUBTITLE FRAME (TRANSCRIPT)  #
#####################################

def make_subtitle_frame_transcript(global_t, transcript_words, clip_width, max_subtitle_height):
    """
    Creates an RGB image (as a NumPy array) for the subtitles at a given global time.
    It shows a sliding window of words (e.g. 11 words: 5 before and 5 after the current word)
    and highlights the current word in bright green ("lime").
    """
    if not transcript_words:
        # Fallback: blank black frame.
        img = Image.new("RGB", (clip_width, max_subtitle_height), (0, 0, 0))
        return np.array(img)
    
    # Find current word index based on global time.
    current_index = None
    for i, w in enumerate(transcript_words):
        if w["start"] <= global_t <= w["end"]:
            current_index = i
            break
        if global_t < w["start"]:
            current_index = i - 1
            break
    if current_index is None:
        current_index = len(transcript_words) - 1
    if current_index < 0:
        current_index = 0

    # Define a window (e.g., 5 words before and 5 words after).
    start_index = max(0, current_index - 5)
    end_index = min(len(transcript_words), current_index + 6)
    window_words = [w["word"] for w in transcript_words[start_index:end_index]]
    window_indices = list(range(start_index, end_index))
    
    # Create a new RGB image (black background).
    img = Image.new("RGB", (clip_width, max_subtitle_height), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    margin = 20
    available_width = clip_width - 2 * margin
    font_size = 40
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    # Wrap the window words into lines.
    space_width, _ = draw.textsize(" ", font=font)
    lines = []
    current_line = []
    current_line_width = 0
    for i, word in enumerate(window_words):
        word_width, _ = draw.textsize(word, font=font)
        if current_line_width + word_width <= available_width:
            current_line.append((word, window_indices[i]))
            current_line_width += word_width + space_width
        else:
            lines.append(current_line)
            current_line = [(word, window_indices[i])]
            current_line_width = word_width + space_width
    if current_line:
        lines.append(current_line)

    # Calculate total text block height.
    line_height = font.getsize("Ay")[1] + 10
    text_block_height = line_height * len(lines)
    y_start = (max_subtitle_height - text_block_height) // 2

    # Draw each line; highlight the current word.
    for line in lines:
        line_width = sum(draw.textsize(word, font=font)[0] for word, _ in line) + space_width * (len(line)-1)
        x_start = (clip_width - line_width) // 2
        x = x_start
        for word, idx in line:
            color = "lime" if idx == current_index else "white"
            draw.text((x, y_start), word, font=font, fill=color)
            w, _ = draw.textsize(word, font=font)
            x += w + space_width
        y_start += line_height

    return np.array(img)

#####################################
# 3. FINAL VIDEO GENERATION         #
#####################################

def generate_final_video(audio_path, images_mapping,
                         output_filename="final_video.mp4",
                         transition_duration=0.5):
    """
    Generates the final video by:
      - Transcribing the voiceover audio using VOSK.
      - Dividing the video into scenes (one per image).
      - For each scene, applying a pan effect on the background image.
      - Creating a dynamic subtitle clip using the transcript (synchronized to the audio).
      - Concatenating scenes with crossfade transitions and setting the voiceover audio.
    """
    # Transcribe the audio.
    print("Transcribing audio... (this may take a few moments)")
    transcript_words = transcribe_audio(audio_path, model_path="model")
    if not transcript_words:
        print("Transcription failed or returned no results.")
        return

    # Load the voiceover audio to get total duration.
    audio_clip = AudioFileClip(audio_path)
    total_audio_duration = audio_clip.duration

    # Divide the video into scenes based on the number of images.
    scene_keys = sorted(images_mapping.keys())  # e.g., scene1, scene2, ...
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
        scaled_clip = clip.resize(zoom_factor)
        v_offset = int((scaled_clip.h - final_height) / 2)
        moving_clip = scaled_clip.set_position(
            lambda t, d=scene_duration: (-int(max_offset_x * t / d), -v_offset)
        )
        panned_clip = CompositeVideoClip([moving_clip], size=(final_width, final_height)).set_duration(scene_duration)

        # Create a dynamic subtitle clip for this scene.
        scene_start_time = i * scene_duration
        subtitle_clip = VideoClip(
            lambda t, offset=scene_start_time: make_subtitle_frame_transcript(t + offset, transcript_words, final_width, max_subtitle_height=200),
            duration=scene_duration
        ).set_position(('center', 'center'))
        
        # Composite the background and subtitle.
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
    
    final_video = concatenate_videoclips(clips_with_transitions, method="chain")
    final_video = final_video.set_audio(audio_clip)

    # Write the final video file.
    final_video.write_videofile(output_filename, fps=24, codec='libx264', audio_codec='aac')
    print("Final video generated and saved as:", output_filename)

#####################################
# 4. MAIN EXECUTION                 #
#####################################


"""
if __name__ == "__main__":
    # Define your images mapping (ensure these paths are correct)
    images_mapping = {
        "scene1": "video_assets/A_group_of_I.jpg",
        "scene2": "video_assets/A_lone_astro.jpg",
        "scene3": "video_assets/A_vibrant__o.jpg",
    }
    # Provide the voiceover audio path (MP3 file)
    audio_path = "video_assets/output_speech.mp3"
    # Generate the final video
    generate_final_video(audio_path, images_mapping,
                         output_filename="final_video.mp4", transition_duration=0.5)
"""