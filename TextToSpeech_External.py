import json
import os
import random
import edge_tts
from pydub import AudioSegment

# edge-tts voices per language, list all with: edge-tts --list-voices
# German voices:
#   de-DE-SeraphinaMultilingualNeural  female
#   de-DE-AmalaNeural                  female
#   de-DE-KatjaNeural                  female
#   de-DE-FlorianMultilingualNeural    male
#   de-DE-ConradNeural                 male
#   de-DE-KillianNeural                male
#   de-AT-IngridNeural                 female, Austrian accent
#   de-AT-JonasNeural                  male, Austrian accent
#   de-CH-LeniNeural                   female, Swiss accent
#   de-CH-JanNeural                    male, Swiss accent
# The title always has the same voice, every comment of a video gets a different one from the list
edge_voices = {
    "de": {
        "title": "de-DE-SeraphinaMultilingualNeural",
        "comment": [
            "de-DE-FlorianMultilingualNeural",
            "de-DE-ConradNeural",
            "de-DE-KillianNeural",
            "de-DE-KatjaNeural",
            "de-DE-AmalaNeural",
        ],
    },
    "en": {"title": "en-US-JennyNeural", "comment": "en-US-GuyNeural"},
}

# Speaking rate per role, e.g. "+10%" for faster speech
edge_rates = {"title": "+15%", "comment": "+15%"}

def add_punctuation(text, words):
    """edge-tts returns the words without the punctuation around them, this takes it from the text."""
    position = 0
    for word in words:
        start = text.find(word['word'], position)
        if start == -1:
            continue
        end = start + len(word['word'])
        while start > position and not text[start - 1].isspace() and not text[start - 1].isalnum():
            start -= 1
        while end < len(text) and not text[end].isspace() and not text[end].isalnum():
            end += 1
        word['word'] = text[start:end]
        position = end
    return words

class TextToSpeech_External:
    def __init__(self, engine='edge', language='en', role='comment'):
        self.engine = engine.lower()

        if self.engine == 'edge':
            print("Initializing edge-tts")
            voices = edge_voices[language][role]
            self.voices = voices if isinstance(voices, list) else [voices]
            self.voice = self.voices[0]
            self.rate = edge_rates[role]
        else:
            raise ValueError("Unsupported engine. Choose 'edge'.")

    def pick_voices(self, count):
        """Random voices for count comments, a voice repeats only when there are more comments than voices."""
        voices = []
        while len(voices) < count:
            voices += random.sample(self.voices, len(self.voices))
        return voices[:count]

    def create_text_to_speech_file(self, text, path, voice=None):
        voice = voice or self.voice
        if self.engine == 'edge':
            print(f"Generating audio with edge-tts ({voice})")
            # edge-tts only returns mp3, the video pipeline expects wav
            mp3_path = path + ".mp3"
            words = []
            with open(mp3_path, "wb") as mp3_file:
                for chunk in edge_tts.Communicate(text, voice, rate=self.rate, boundary="WordBoundary").stream_sync():
                    if chunk["type"] == "audio":
                        mp3_file.write(chunk["data"])
                    elif chunk["type"] == "WordBoundary":
                        # Offset and duration are in units of 100 ns
                        start, end = chunk["offset"] / 1e7, (chunk["offset"] + chunk["duration"]) / 1e7
                        words.append({"word": chunk["text"], "start": start, "end": end})
            AudioSegment.from_mp3(mp3_path).export(path, format="wav")
            os.remove(mp3_path)
            # The time of every word, so the subtitles need no speech recognition
            with open(os.path.splitext(path)[0] + ".json", "w", encoding="utf-8") as words_file:
                json.dump(add_punctuation(text, words), words_file, ensure_ascii=False)
