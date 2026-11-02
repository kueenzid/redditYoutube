import os
import edge_tts
from pydub import AudioSegment

# edge-tts voices per language, list all with: edge-tts --list-voices
edge_voices = {
    "de": {"title": "de-DE-SeraphinaMultilingualNeural", "comment": "de-DE-FlorianMultilingualNeural"},
    "en": {"title": "en-US-JennyNeural", "comment": "en-US-GuyNeural"},
}

# Speaking rate per role, e.g. "+10%" for faster speech
edge_rates = {"title": "+10%", "comment": "+0%"}

class TextToSpeech_External:
    def __init__(self, engine='edge', language='en', role='comment'):
        self.engine = engine.lower()

        if self.engine == 'edge':
            print("Initializing edge-tts")
            self.voice = edge_voices[language][role]
            self.rate = edge_rates[role]
        else:
            raise ValueError("Unsupported engine. Choose 'edge'.")

    def create_text_to_speech_file(self, text, path):
        if self.engine == 'edge':
            print(f"Generating audio with edge-tts ({self.voice})")
            # edge-tts only returns mp3, the video pipeline expects wav
            mp3_path = path + ".mp3"
            edge_tts.Communicate(text, self.voice, rate=self.rate).save_sync(mp3_path)
            AudioSegment.from_mp3(mp3_path).export(path, format="wav")
            os.remove(mp3_path)
