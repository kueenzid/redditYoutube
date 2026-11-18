import os
import whisper
from PIL import ImageFont

# Subtitle style, ASS colours are &HAABBGGRR
subtitle_font = "Archivo Black"  # from assets/fonts
subtitle_font_file = os.path.join("assets", "fonts", "ArchivoBlack-Regular.ttf")
subtitle_font_size = 96
# libass sizes a font by its OS/2 line height, so text is narrower than Pillow measures it (measured for Archivo Black)
ass_font_scale = 0.74
subtitle_color = "&H00FFFFFF"  # white
highlight_color = "&H00D4FF"  # yellow (#FFD400) for the spoken word
outline_color = "&H00000000"  # black, the yellow word would not be readable on a yellow glow
outline_size = 6  # 0 for no outline
outline_blur = 4
max_line_width = 920  # the video is 1080 px wide, a line gets as many words as fit
max_gap = 0.5  # a longer pause starts a new line, a shorter one keeps the line on screen (seconds)

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

def line_width(words):
    font = ImageFont.truetype(subtitle_font_file, subtitle_font_size)
    return font.getlength(" ".join(clean_word(w['word']) for w in words)) * ass_font_scale

def split_into_lines(words):
    """Fills every line with as many words as fit, a pause of max_gap or more starts a new line."""
    lines = []
    for word in words:
        if lines and word['start'] - lines[-1][-1]['end'] < max_gap and line_width(lines[-1] + [word]) <= max_line_width:
            lines[-1].append(word)
        else:
            lines.append([word])
    return lines

def font_size_for(words):
    # A single word longer than the line gets a smaller font so it fits
    return min(subtitle_font_size, int(subtitle_font_size * max_line_width / line_width(words)))

def generate_ass(segments, offset):
    """Shows one line of words at a time with an outline, the spoken word is highlighted."""
    ass_output = (
        "[Script Info]\n"
        "ScriptType: v4.00+\n"
        "PlayResX: 1080\n"
        "PlayResY: 1920\n"
        "WrapStyle: 0\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Default,{subtitle_font},{subtitle_font_size},{subtitle_color},{subtitle_color},{outline_color},&H00000000,0,0,0,0,100,100,0,0,1,{outline_size},0,5,60,60,0,1\n\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )
    words = [w for segment in segments for w in segment.get('words', []) if clean_word(w['word'])]
    lines = split_into_lines(words)
    for line_index, line in enumerate(lines):
        style = f"\\blur{outline_blur}\\fs{font_size_for(line)}"
        for i, word in enumerate(line):
            if i + 1 < len(line):
                end = line[i + 1]['start']
            elif line_index + 1 < len(lines) and lines[line_index + 1][0]['start'] - word['end'] < max_gap:
                # Avoid flicker: keep the line until the next one appears
                end = lines[line_index + 1][0]['start']
            else:
                end = word['end']
            text = " ".join(
                f"{{\\c{highlight_color}&}}{clean_word(w['word'])}{{\\c{subtitle_color}&}}" if j == i else clean_word(w['word'])
                for j, w in enumerate(line)
            )
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
