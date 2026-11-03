FROM python:3.14-slim

# FFmpeg with libass for the subtitles, also used by Whisper and torchcodec
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# The CPU builds of torch are much smaller than the default CUDA builds, which also need
# several GB of NVIDIA packages that requirements.txt lists for Linux
COPY requirements.txt build-constraints.txt ./
RUN grep -vE '^(nvidia-|cuda-)' requirements.txt > requirements-cpu.txt \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements-cpu.txt --build-constraint build-constraints.txt \
        --extra-index-url https://download.pytorch.org/whl/cpu \
    && rm requirements-cpu.txt

# Headless Chromium for the screenshots, with the system libraries it needs
RUN playwright install --with-deps --only-shell chromium

COPY . .

# config.py holds the Reddit credentials and is mounted for source = "reddit",
# for 20min an empty one is enough
RUN touch config.py

CMD ["python", "main.py"]
