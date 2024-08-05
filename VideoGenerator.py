import os
import wave
import ffmpeg
import random

# Define file paths
input_video_path = 'assets/backgroundVideos/Minecraft_1080p_vertical.mp4'

# Define the duration for the overlay image
title_start = 0  # overlay starts at 0.5 seconds

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
    # Start with the title audio
    concatenated_audio = ffmpeg.input(title_audio)

    # Create a silent audio segment
    silent = ffmpeg.input('anullsrc=r=44100:cl=stereo', f='lavfi', t=0.5)

    # List to hold all the input segments
    input_segments = [concatenated_audio, silent]

    # Add each comment audio followed by a silent segment
    for audio_file in comment_audios:
        audio = ffmpeg.input(audio_file)
        input_segments.extend([audio, silent])

    # Concatenate all audio segments
    concatenated = ffmpeg.concat(*input_segments, v=0, a=1).node

    # Output the concatenated audio
    output = ffmpeg.output(concatenated[0], total_audio_path)

    # Run the ffmpeg command
    ffmpeg.run(output)

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
    input_video_duration = get_video_duration(input_video_path)
    start_time = random.randint(0, int(input_video_duration - total_duration))

    # Load the video and trim it
    video = ffmpeg.input(input_video_path, ss=start_time, t=total_duration)

    # Get dimensions of video and image to center the image
    video_stream_info = ffmpeg.probe(input_video_path)['streams'][0]
    video_width = int(video_stream_info['width'])
    video_height = int(video_stream_info['height'])

    image_stream_info = ffmpeg.probe(post_screenshot_image)['streams'][0]
    image_width = int(image_stream_info['width'])
    image_height = int(image_stream_info['height'])

    # Calculate target width and height for scaling
    target_width = int(video_width * 0.8)
    target_height = -1  # Preserve aspect ratio

    # Scale and overlay title image centered
    title_overlay = (
        ffmpeg
        .input(post_screenshot_image, t=title_duration)
        .filter('scale', target_width, target_height)
    )

    x_position = (video_width - target_width) // 2
    y_position = (video_height - image_height * (target_width / image_width)) // 2

    video = ffmpeg.overlay(video, title_overlay, x=x_position, y=y_position, enable=f'between(t,{title_start},{title_start + title_duration})')

    # audio overlay
    audio_overlay = ffmpeg.input(total_audio_path)

    # Output the final video
    video = ffmpeg.output(video, audio_overlay, output_video)
    ffmpeg.run(video)