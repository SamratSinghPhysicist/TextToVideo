FROM python:3.9-slim

# Install system dependencies for ffmpeg, imagemagick, and Pillow
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY . /workspace

RUN pip install --no-cache-dir -r requirements.txt

ENV FFMPEG_BINARY="ffmpeg"
ENV IMAGEMAGICK_BINARY="/usr/bin/convert"

CMD ["python", "main.py"]
