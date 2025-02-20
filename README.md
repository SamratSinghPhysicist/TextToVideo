# Text-to-Video Generation App

This project is a fully automated text-to-video generator that creates videos from generated scripts, voiceovers, and images. The app handles tasks including script generation, voiceover creation, image fetching, video generation (with background panning and transitions), and even YouTube upload scheduling. It is built using Python along with several third-party libraries and tools.

**Note:**
This repository contains multiple modules:
- `script_generator.py`
- `voiceover_generator.py`
- `image_generator.py`
- `video_generator.py`
- `topic_fetcher.py`
- `main.py` (the scheduled entry point)

Ensure that all files are in your repository.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the App Locally](#running-the-app-locally)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Prerequisites

- **Operating System:** Windows (the current setup instructions are tailored for Windows)
- **Python:** Python 3.8 or later
- **FFmpeg:**
  - Download a Windows build of FFmpeg (do not download the source code)
  - Extract FFmpeg and ensure the `ffmpeg.exe` binary is located (e.g., `C:\ffmpeg\bin\ffmpeg.exe`)
- **ImageMagick:**
  - Download and install ImageMagick (ensure you choose a version that installs the `magick.exe` executable)
  - Example installation path: `C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe`
- **Other Dependencies:**
  - The app uses several Python libraries (see [Installation](#installation) below)

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```

2. **Create a Virtual Environment (Optional but Recommended):**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On Linux/macOS
   ```

3. **Install Python Dependencies:**

   Create a `requirements.txt` file with the following dependencies:
   ```plaintext
   google_api_python_client==2.160.0
   google_auth_oauthlib==1.2.1
   moviepy==1.0.3
   numpy==2.2.3
   protobuf==5.29.3
   python-dotenv==1.0.1
   Requests==2.32.3
   schedule==1.2.2

   ```

   Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. **System Dependencies:**
   - **FFmpeg**: Add the FFmpeg directory to your system PATH or update the `FFMPEG_BINARY` variable in the code to point to your `ffmpeg.exe`
   - **ImageMagick**: Ensure ImageMagick is installed and the `IMAGEMAGICK_BINARY` environment variable points to the full executable path (e.g., `C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe`)

## Configuration

1. **Environment Variables:**

   Create a `.env` file in the root directory with your API keys and settings:

   ```plaintext
   # Gemini API Keys
   GEMINI_API_KEY_1=your_gemini_api_key_1
   GEMINI_API_KEY_2=your_gemini_api_key_2
   GEMINI_API_KEY_3=your_gemini_api_key_3

   # ElevenLabs API Keys and Voice IDs
   ELEVENLABS_API_KEY_1=your_elevenlabs_api_key_1
   VOICE_ID_1=your_voice_id_1
   
   ELEVENLABS_API_KEY_2=your_elevenlabs_api_key_2
   VOICE_ID_2=your_voice_id_2
   
   ELEVENLABS_API_KEY_3=your_elevenlabs_api_key_3
   VOICE_ID_3=your_voice_id_3
   
   ELEVENLABS_API_KEY_4=your_elevenlabs_api_key_4
   VOICE_ID_4=your_voice_id_4
   
   ELEVENLABS_API_KEY_5=your_elevenlabs_api_key_5
   VOICE_ID_5=your_voice_id_5
   
   ELEVENLABS_API_KEY_6=your_elevenlabs_api_key_6
   VOICE_ID_6=your_voice_id_6

   # YouTube API Key
   YOUTUBE_API_KEY=your_youtube_api_key
   ```

## Running the App Locally

The main entry point is `main.py`, which handles video generation and upload scheduling.

1. **Run the Main Script:**
   ```bash
   python main.py
   ```

2. **Process Overview:**
   - Loads API keys from the `.env` file
   - Generates script using `script_generator.py`
   - Creates voiceover using `voiceover_generator.py`
   - Processes images with `image_generator.py`
   - Combines everything into a video using `video_generator.py`
   - Saves the output as `final_video.mp4`
   - Optionally uploads to YouTube
   - Runs on a schedule (default: 2:00 PM and 6:00 PM daily)

## Troubleshooting

Common issues and solutions:

1. **FFmpeg Issues:**
   - Ensure FFmpeg directory is in your system PATH
   - Verify `FFMPEG_BINARY` variable points to correct location

2. **ImageMagick Problems:**
   - Confirm `IMAGEMAGICK_BINARY` points to full path including `magick.exe`
   - Check installation is complete with all required components

3. **Dependency Errors:**
   - Run `pip install -r requirements.txt`
   - Ensure Python version compatibility (3.8 or later)

4. **API Key Issues:**
   - Verify `.env` file exists in root directory
   - Check all API keys are valid and active
   - Ensure no spaces around the equal signs in `.env` file

5. **Scheduling Issues:**
   - Check system time and timezone settings
   - Modify scheduling in `main.py` for testing
   - Disable scheduling by commenting out relevant code

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
