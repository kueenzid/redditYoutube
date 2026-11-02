import whisper

# Subtitle style, ASS colours are &HAABBGGRR
subtitle_font = "Arial"
subtitle_font_size = 110
subtitle_color = "&H00FFFFFF"  # white
highlight_color = "&H00D4FF"  # yellow (#FFD400) for the word that is spoken
outline_color = "&H00000000"  # black
words_per_line = 3

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

def generate_ass(segments, offset):
    """Shows a few words at a time and highlights the word that is spoken."""
    ass_output = (
        "[Script Info]\n"
        "ScriptType: v4.00+\n"
        "PlayResX: 1080\n"
        "PlayResY: 1920\n"
        "WrapStyle: 0\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Default,{subtitle_font},{subtitle_font_size},{subtitle_color},{subtitle_color},{outline_color},&H80000000,-1,0,0,0,100,100,0,0,1,8,4,5,60,60,0,1\n\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )
    for segment in segments:
        words = [w for w in segment.get('words', []) if clean_word(w['word'])]
        for chunk_start in range(0, len(words), words_per_line):
            chunk = words[chunk_start:chunk_start + words_per_line]
            for i, word in enumerate(chunk):
                end = chunk[i + 1]['start'] if i + 1 < len(chunk) else word['end']
                text = " ".join(
                    f"{{\\c{highlight_color}&\\fscx115\\fscy115}}{clean_word(w['word'])}{{\\r}}" if j == i else clean_word(w['word'])
                    for j, w in enumerate(chunk)
                )
                ass_output += f"Dialogue: 0,{format_time(word['start'] + offset)},{format_time(end + offset)},Default,,0,0,0,,{text}\n"
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
