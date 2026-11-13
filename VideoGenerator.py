import json
import os
import ffmpeg
import random
from VideoTranscriber import transcribe_comments, save_word_subtitles
from pydub import AudioSegment

# Every video gets a random background video from this folder
background_video_folder = 'assets/backgroundVideos'
title_start = 0  # overlay starts at 0.5 seconds

def pick_background_video():
    videos = [f for f in os.listdir(background_video_folder) if f.lower().endswith(('.mp4', '.mov', '.webm', '.mkv'))]
    if not videos:
        raise FileNotFoundError(f"No background video in {background_video_folder}")
    return os.path.join(background_video_folder, random.choice(videos))

def get_audio_duration(file_path):
    audio = AudioSegment.from_file(file_path)
    return len(audio) / 1000.0

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

def concatenate_audio_files(total_audio_path, title_audio, concatenated_comments_path=None):
    # Start with the title audio
    concatenated_audio = ffmpeg.input(title_audio)

    # Create a silent audio segment
    silent = ffmpeg.input('anullsrc=r=44100:cl=stereo', f='lavfi', t=0.5)

    # List to hold all the input segments
    input_segments = [concatenated_audio, silent]

    # Add the concatenated comments audio if it exists
    if concatenated_comments_path and os.path.exists(concatenated_comments_path):
        comments_audio = ffmpeg.input(concatenated_comments_path)
        input_segments.extend([comments_audio, silent])

    # Concatenate all audio segments
    concatenated = ffmpeg.concat(*input_segments, v=0, a=1).node

    # Output the concatenated audio
    output = ffmpeg.output(concatenated[0], total_audio_path)

    # Run the ffmpeg command
    ffmpeg.run(output)

def load_comment_words(comment_audios):
    """Word times written by the TTS, shifted to their place in the concatenated comments. None if a comment has none."""
    words = []
    comment_start = 0
    for comment_audio in comment_audios:
        words_file = os.path.splitext(comment_audio)[0] + '.json'
        if not os.path.exists(words_file):
            return None
        with open(words_file, encoding='utf-8') as f:
            words += [{**w, 'start': w['start'] + comment_start, 'end': w['end'] + comment_start} for w in json.load(f)]
        comment_start += get_audio_duration(comment_audio) + 0.5
    return words

def extract_first_frame(video_file, image_file):
    """Saves the first frame of the video as image, used as YouTube thumbnail."""
    ffmpeg.input(video_file).output(image_file, vframes=1, **{'q:v': 2}).run(overwrite_output=True, quiet=True)

def generate_video(path, comment_count, language=None):
    post_screenshot_image = os.path.join(path, 'post_screenshot.png')
    title_audio = os.path.join(path, 'title.wav')
    total_comments_audio_path = os.path.join(path, 'comments_audio.wav')
    total_audio_path = os.path.join(path, 'concatenated_audio.wav')
    transcription_file_path = os.path.join(path, 'transcription.ass')
    output_video = os.path.join(path, 'output.mp4')

    # Get comment audio files in order (os.listdir order is arbitrary)
    comment_audios = [os.path.join(path, f'comment_{i}.wav') for i in range(comment_count)]
    comment_audios = [f for f in comment_audios if os.path.exists(f)]

    if comment_count > 0 and comment_audios:
        concatenate_comment_files(comment_audios, total_comments_audio_path)
        # The comments start after the title and a 0.5 s pause
        comments_start = get_audio_duration(title_audio) + 0.5
        words = load_comment_words(comment_audios)
        if words is not None:
            save_word_subtitles(words, transcription_file_path, comments_start)
        else:
            # The TTS engine returned no word times, so Whisper has to find them
            transcribe_comments(total_comments_audio_path, transcription_file_path, comments_start, language)
    else:
        total_comments_audio_path = None
        transcription_file_path = None

    concatenate_audio_files(total_audio_path, title_audio, total_comments_audio_path)

    # Calculate the total duration of all audio files
    title_duration = get_audio_duration(title_audio)
    total_duration = get_audio_duration(total_audio_path)

    # Determine video section
    background_video_path = pick_background_video()
    print(f"Background video: {background_video_path}")
    input_video_duration = get_video_duration(background_video_path)
    if total_duration <= input_video_duration:
        start_time = random.randint(0, int(input_video_duration - total_duration))

        # Load the video and trim it
        video = ffmpeg.input(background_video_path, ss=start_time, t=total_duration)
    else:
        # Audio is longer than the background video, so loop it
        video = ffmpeg.input(background_video_path, stream_loop=-1, t=total_duration)

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

    # Overlay the card of each comment while it is read, above the subtitles
    comment_start = title_start + title_duration + 0.5
    for i, comment_audio in enumerate(comment_audios):
        comment_duration = get_audio_duration(comment_audio)
        comment_card_image = os.path.join(path, f'comment_card_{i}.png')
        if os.path.exists(comment_card_image):
            comment_overlay = ffmpeg.input(comment_card_image).filter('scale', target_width, target_height)
            video = ffmpeg.overlay(video, comment_overlay, x=x_position, y=int(video_height * 0.2), enable=f'between(t,{comment_start},{comment_start + comment_duration})')
        comment_start += comment_duration + 0.5

    # Apply the subtitles filter only if a transcription file exists
    if transcription_file_path and os.path.exists(transcription_file_path):
        # The style is defined in the ASS file (see VideoTranscriber.py)
        video = video.filter('subtitles', transcription_file_path, fontsdir=os.path.join('assets', 'fonts'))

    # Audio overlay
    audio_overlay = ffmpeg.input(total_audio_path)

    # Output the final video with audio and subtitles baked in
    output = ffmpeg.output(video, audio_overlay, output_video)

    # Run the ffmpeg command
    ffmpeg.run(output)
