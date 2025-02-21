# Use a slim Python base image
FROM python:3.9-slim

# Install system dependencies: FFmpeg and ImageMagick
RUN apt-get update && \
    apt-get install -y ffmpeg imagemagick && \
    rm -rf /var/lib/apt/lists/*

# Set working directory to /workspace
WORKDIR /workspace

# Copy all files from the current directory into the container
COPY . /workspace

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables for ImageMagick and FFmpeg
ENV IMAGEMAGICK_BINARY="magick"
ENV FFMPEG_BINARY="ffmpeg"

# Command to run your main script
CMD ["python", "main.py"]
