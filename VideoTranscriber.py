import os
import whisper
from PIL import ImageFont

# Subtitle style, ASS colours are &HAABBGGRR
subtitle_font = "Archivo Black"  # from assets/fonts
subtitle_font_file = os.path.join("assets", "fonts", "ArchivoBlack-Regular.ttf")
subtitle_font_size = 120
subtitle_color = "&H00FFFFFF"  # white
highlight_color = "&H00D4FF"  # yellow (#FFD400) for the spoken word, only used with more than one word per line
glow_color = "&H0000D4FF"  # yellow (#FFD400)
glow_size = 6  # 0 for no glow
glow_blur = 12
words_per_line = 1
max_gap = 0.5  # keep a word on screen until the next one if the pause is shorter (seconds)

def transcribe_audio_with_whisper(audio_path, language=None):
    model = whisper.load_model("base")  # Choose between "small", "medium", "large", depending on your needs
    result = model.transcribe(audio_path, language=language, word_timestamps=True)
    return result['text'], result['segments']

def format_time(seconds):
    """Converts seconds to ASS timestamp format (H:MM:SS.cc)."""
    centiseconds = int(round(seconds * 100))
    hours, centiseconds = divmod(centiseconds, 360000)
    minutes, centiseconds = divmod(centiseconds, 6000)
    seconds, centiseconds = divmod(centiseconds, 100)
    return f"{hours}:{minutes:02}:{seconds:02}.{centiseconds:02}"

def clean_word(word):
    # Braces and backslashes would be read as ASS override tags
    return word.strip().replace("{", "").replace("}", "").replace("\\", "").upper()

def font_size_for(words):
    # Long words get a smaller font so they fit into the 1080 px wide video (minus margins)
    font = ImageFont.truetype(subtitle_font_file, subtitle_font_size)
    widest = max(font.getlength(clean_word(w['word'])) for w in words)
    return min(subtitle_font_size, int(subtitle_font_size * 960 / widest))

def generate_ass(segments, offset):
    """Shows a few words at a time (one by default) with a glow."""
    ass_output = (
        "[Script Info]\n"
        "ScriptType: v4.00+\n"
        "PlayResX: 1080\n"
        "PlayResY: 1920\n"
        "WrapStyle: 0\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Default,{subtitle_font},{subtitle_font_size},{subtitle_color},{subtitle_color},{glow_color},&H00000000,0,0,0,0,100,100,0,0,1,{glow_size},0,5,60,60,0,1\n\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )
    words = [w for segment in segments for w in segment.get('words', []) if clean_word(w['word'])]
    chunks = [words[i:i + words_per_line] for i in range(0, len(words), words_per_line)]
    for chunk_index, chunk in enumerate(chunks):
        style = f"\\blur{glow_blur}\\fs{font_size_for(chunk)}"
        for i, word in enumerate(chunk):
            if i + 1 < len(chunk):
                end = chunk[i + 1]['start']
            elif chunk_index + 1 < len(chunks) and chunks[chunk_index + 1][0]['start'] - word['end'] < max_gap:
                # Avoid flicker: keep the word until the next one appears
                end = chunks[chunk_index + 1][0]['start']
            else:
                end = word['end']
            if len(chunk) > 1:
                text = " ".join(
                    f"{{\\c{highlight_color}&\\fscx115\\fscy115}}{clean_word(w['word'])}{{\\r{style}}}" if j == i else clean_word(w['word'])
                    for j, w in enumerate(chunk)
                )
            else:
                text = clean_word(word['word'])
            ass_output += f"Dialogue: 0,{format_time(word['start'] + offset)},{format_time(end + offset)},Default,,0,0,0,,{{{style}}}{text}\n"
    return ass_output

def save_subtitle_file(content, output_path):
    with open(output_path, 'w', encoding='utf-8') as subtitle_file:
        subtitle_file.write(content)

def transcribe_comments(audio_path, transcription_path, offset, language=None):
    # 1. Transcribe the audio using Whisper, with a timestamp for every word
    transcription_text, transcription_segments = transcribe_audio_with_whisper(audio_path, language)

    # 2. Generate ASS subtitles, shifted by the time before the comments start
    ass_text = generate_ass(transcription_segments, offset)

    # 3. Save as an ASS file
    save_subtitle_file(ass_text, transcription_path)
    print(f"Subtitle file saved as {transcription_path}")
