# Use a slim Python base image
FROM python:3.9-slim

# Install system dependencies: FFmpeg and ImageMagick
RUN apt-get update && \
    apt-get install -y ffmpeg imagemagick && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory to the repository root
WORKDIR /workspace

# Copy all files into the container
COPY . /workspace

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables for FFmpeg and ImageMagick
ENV FFMPEG_BINARY="ffmpeg"
ENV IMAGEMAGICK_BINARY="convert"

# Command to run your main script
CMD ["python", "main.py"]
