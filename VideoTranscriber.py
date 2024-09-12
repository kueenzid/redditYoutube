import whisper
import ffmpeg
from datetime import timedelta

def transcribe_audio_with_whisper(audio_path):
    model = whisper.load_model("base")  # Choose between "small", "medium", "large", depending on your needs
    result = model.transcribe(audio_path)
    return result['text'], result['segments']

def generate_srt(segments, title_duration):
    srt_output = ""
    for i, segment in enumerate(segments):
        start_time = format_time(segment['start'] + title_duration)
        end_time = format_time(segment['end'] + title_duration)
        srt_output += f"{i+1}\n"
        srt_output += f"{start_time} --> {end_time}\n"
        srt_output += segment['text'].strip() + "\n\n"
    return srt_output

def format_time(seconds):
    """Converts seconds to SRT timestamp format."""
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int(td.microseconds / 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def save_srt_file(srt_content, output_path):
    with open(output_path, 'w') as srt_file:
        srt_file.write(srt_content)

def transcribe_comments(audio_path, transcription_path, title_duration):

    # Example usage
    audio_path = audio_path  # Path to your existing audio file
    srt_output_path = transcription_path

    # 1. Transcribe the audio using Whisper
    transcription_text, transcription_segments = transcribe_audio_with_whisper(audio_path)

    # 2. Generate SRT format text using the segments returned by Whisper
    srt_text = generate_srt(transcription_segments, title_duration)

    # 3. Save as an SRT file
    save_srt_file(srt_text, srt_output_path)
    print(f"SRT file saved as {srt_output_path}")
