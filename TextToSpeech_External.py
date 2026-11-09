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
            edge_tts.Communicate(text, voice, rate=self.rate).save_sync(mp3_path)
            AudioSegment.from_mp3(mp3_path).export(path, format="wav")
            os.remove(mp3_path)
