import os
import wave
import ffmpeg
import random
from VideoTranscriber import transcribe_comments

# Define file path for background video
background_video_path = 'assets/backgroundVideos/Minecraft_1080p_vertical.mp4'
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

def concatenate_comment_files(comment_audios, concatenated_comments_path):
    # Create a silent audio segment
    silent = ffmpeg.input('anullsrc=r=44100:cl=stereo', f='lavfi', t=0.5)

    # List to hold all the input segments
    input_segments = []

    # Add each comment audio followed by a silent segment
    for audio_file in comment_audios:
        audio = ffmpeg.input(audio_file)
        input_segments.extend([audio, silent])

    # Concatenate all audio segments
    concatenated = ffmpeg.concat(*input_segments, v=0, a=1).node

    # Output the concatenated audio
    output = ffmpeg.output(concatenated[0], concatenated_comments_path)

    # Run the ffmpeg command
    ffmpeg.run(output)


def concatenate_audio_files(total_audio_path, title_audio, concatenated_comments_path):
    # Start with the title audio
    concatenated_audio = ffmpeg.input(title_audio)

    # Create a silent audio segment
    silent = ffmpeg.input('anullsrc=r=44100:cl=stereo', f='lavfi', t=0.5)

    # List to hold all the input segments
    input_segments = [concatenated_audio, silent]

    # Add the concatenated comments audio
    comments_audio = ffmpeg.input(concatenated_comments_path)
    input_segments.extend([comments_audio, silent])

    # Concatenate all audio segments
    concatenated = ffmpeg.concat(*input_segments, v=0, a=1).node

    # Output the concatenated audio
    output = ffmpeg.output(concatenated[0], total_audio_path)

    # Run the ffmpeg command
    ffmpeg.run(output)

def generate_video(path):
    post_screenshot_image = os.path.join(path, 'post_screenshot.png')
    title_audio = os.path.join(path, 'title.wav')
    total_comments_audio_path = os.path.join(path, 'comments_audio.wav')
    total_audio_path = os.path.join(path, 'concatenated_audio.wav')
    transcription_file_path = os.path.join(path, 'transcription.srt')
    post_info_path = os.path.join(path, 'post_info.txt')
    output_video = os.path.join(path, 'output.mp4')

    # Get comment audio files
    comment_files = [f for f in os.listdir(path) if f.startswith('comment_')]
    comment_audios = [os.path.join(path, f) for f in comment_files]

    concatenate_comment_files(comment_audios, total_comments_audio_path)
    concatenate_audio_files(total_audio_path, title_audio, total_comments_audio_path)

    # Calculate the total duration of all audio files
    title_duration = get_audio_duration(title_audio)
    total_duration = get_audio_duration(total_audio_path)

    transcribe_comments(total_comments_audio_path, transcription_file_path, title_duration)

# Determine video section
    input_video_duration = get_video_duration(background_video_path)
    start_time = random.randint(0, int(input_video_duration - total_duration))

    # Load the video and trim it
    video = ffmpeg.input(background_video_path, ss=start_time, t=total_duration)

    # Get dimensions of video and image to center the image
    video_stream_info = ffmpeg.probe(background_video_path)['streams'][0]
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

    # Apply the subtitles filter with centered alignment
    video = video.filter('subtitles', transcription_file_path, force_style='Alignment=10,PrimaryColour=&H0011BEFC,OutlineColour=&H00000000,BoderStyle=1,Outline=1')

    # Audio overlay
    audio_overlay = ffmpeg.input(total_audio_path)

    # Output the final video with audio and subtitles baked in
    output = ffmpeg.output(video, audio_overlay, output_video)

    # Run the ffmpeg command
    ffmpeg.run(output)
