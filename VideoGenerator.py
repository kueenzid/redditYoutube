import os
import wave
import ffmpeg
import random

# Define file paths
input_video = 'assets/backgroundVideos/Minecraft_1080p_vertical.mp4'

# Define the duration and position for the overlay image
title_start = 0.5  # overlay starts at 0.5 seconds
overlay_position = (10, 10)  # position of the overlay image (x, y)

def get_audio_duration(file_path):
    with wave.open(file_path, 'rb') as audio_file:
        frames = audio_file.getnframes()
        rate = audio_file.getframerate()
        duration = frames / float(rate)
    return duration

def get_video_duration(file_path):
    probe = ffmpeg.probe(file_path)
    duration = float(probe['format']['duration'])
    return duration

def concatenate_audio_files(total_audio_path, title_audio, comment_audios):
    # Load the title audio
    concatenated_audio = ffmpeg.input(title_audio)
    silent = ffmpeg.input('anullsrc=r=44100:cl=stereo', f='lavfi', t=0.5)
    concatenated_audio.concat(concatenated_audio, silent, v=0, a=1)

# Load and concatenate the comment audios
    for audio_file in comment_audios:
        audio = ffmpeg.input(audio_file)
        concatenated_audio.concat(concatenated_audio, audio, v=0, a=1)
        concatenated_audio.concat(concatenated_audio, silent, v=0, a=1)

    # Concatenate the audio files
    ffmpeg.run(ffmpeg.output(concatenated_audio, total_audio_path))

def generate_video(path):
    post_screenshot_image = os.path.join(path, 'post_screenshot.png')
    title_audio = os.path.join(path, 'title.wav')
    total_audio_path = os.path.join(path, 'concatenated_audio.wav')
    output_video = os.path.join(path, 'output.mp4')

    # Get comment audio files
    comment_files = [f for f in os.listdir(path) if f.startswith('comment_')]
    comment_audios = [os.path.join(path, f) for f in comment_files]

    concatenate_audio_files(total_audio_path, title_audio, comment_audios)

    # Calculate the total duration of all audio files
    title_duration = get_audio_duration(title_audio)
    total_duration = get_audio_duration(total_audio_path)

    # Determine video section
    input_video_duration = get_video_duration(input_video)
    start_time = random.randint(0, int(input_video_duration - total_duration))

    # Load the video and trim it
    video = ffmpeg.input(input_video, ss=start_time, t=total_duration)

    # title overlay
    title_overlay = ffmpeg.input(post_screenshot_image, t=title_duration)
    video = ffmpeg.overlay(video, title_overlay, x=overlay_position[0], y=overlay_position[1], enable=f'between(t,{title_start},{title_start + title_duration})')

    # audio overlay
    audio_overlay = ffmpeg.input(total_audio_path)
    video = ffmpeg.overlay(video, audio_overlay)

    # Output the final video
    video = ffmpeg.output(video, output_video)
    ffmpeg.run(video)