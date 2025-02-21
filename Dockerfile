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

# Set environment variables for FFmpeg, ImageMagick, and unbuffered Python output
ENV FFMPEG_BINARY="ffmpeg"
ENV IMAGEMAGICK_BINARY="/usr/bin/convert"
ENV PYTHONUNBUFFERED=1

# Expose the port that the Flask server will listen on (default: 5000)
EXPOSE 5000

# Run main.py in unbuffered mode
CMD ["python", "-u", "main.py"]
