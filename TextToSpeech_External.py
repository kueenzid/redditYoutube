import requests
from xml.sax.saxutils import escape
import config

# Azure neural voices, free tier (F0): 500'000 characters per month
azure_voices = {
    "en": ("en-US", "en-US-JennyNeural"),
    "de": ("de-CH", "de-CH-LeniNeural"),  # de-CH-JanNeural for a male voice
}

class TextToSpeech_External:
    def __init__(self, engine='azure', language='en'):
        self.engine = engine.lower()
        self.language = language

        if self.engine == 'azure':
            print("Initializing Azure TTS")
            self.url = f"https://{config.azure_speech_region}.tts.speech.microsoft.com/cognitiveservices/v1"
            self.locale, self.voice = azure_voices[language]
        else:
            raise ValueError("Unsupported engine. Choose 'azure'.")

    def create_text_to_speech_file(self, text, path):
        if self.engine == 'azure':
            print("Generating audio with Azure TTS")
            ssml = (
                f"<speak version='1.0' xml:lang='{self.locale}'>"
                f"<voice name='{self.voice}'>{escape(text)}</voice>"
                "</speak>"
            )
            headers = {
                "Ocp-Apim-Subscription-Key": config.azure_speech_key,
                "Content-Type": "application/ssml+xml",
                "X-Microsoft-OutputFormat": "riff-24khz-16bit-mono-pcm",
                "User-Agent": "redditYoutube",
            }
            resp = requests.post(self.url, data=ssml.encode("utf-8"), headers=headers, timeout=60)
            resp.raise_for_status()
            with open(path, "wb") as f:
                f.write(resp.content)
