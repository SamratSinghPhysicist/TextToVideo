FROM python:3.9-slim
RUN apt-get update && apt-get install -y ffmpeg imagemagick && rm -rf /var/lib/apt/lists/*
WORKDIR /workspace
COPY . /workspace
RUN pip install --no-cache-dir -r requirements.txt
ENV FFMPEG_BINARY="ffmpeg"
ENV IMAGEMAGICK_BINARY="/usr/bin/convert"
CMD ["python", "main.py"]
