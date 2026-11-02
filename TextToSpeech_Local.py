import torch
import scipy
import os
from transformers import AutoProcessor, BarkModel
from TTS.api import TTS

barkSpeaker1 = "v2/en_speaker_1"
barkSpeaker6 = "v2/en_speaker_6"
barkSpeaker9 = "v2/en_speaker_9"

preferred_bark_speaker = barkSpeaker6

coqui_models = {
    "en": "tts_models/en/jenny/jenny",
    "de": "tts_models/de/thorsten/vits",
}

# Built-in XTTS v2 speaker, works for every language
preferred_xtts_speaker = "Ana Florence"

class TextToSpeech_Local:
    def __init__(self, engine='coqui', language='en'):
        self.engine = engine.lower()
        self.language = language

        if self.engine == 'xtts':
            print("Initializing XTTS v2")
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False).to(self.device)
        elif self.engine == 'coqui':
            print("Initializing Coqui TTS")
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.tts = TTS(model_name=coqui_models[language], progress_bar=False).to(self.device)
        elif self.engine == 'bark':
            print("Initializing Bark TTS")
            os.environ["SUNO_OFFLOAD_CPU"] = "True"
            os.environ["SUNO_USE_SMALL_MODELS"] = "True"
            self.processor = AutoProcessor.from_pretrained("suno/bark")
            self.model = BarkModel.from_pretrained("suno/bark")
            self.voice_preset = preferred_bark_speaker if language == 'en' else f"v2/{language}_speaker_6"
        else:
            raise ValueError("Unsupported engine. Choose 'xtts', 'coqui' or 'bark'.")

    def create_text_to_speech_file(self, text, path):
        if self.engine == 'xtts':
            print("Generating audio with XTTS v2")
            self.tts.tts_to_file(text, speaker=preferred_xtts_speaker, language=self.language, file_path=path)
        elif self.engine == 'coqui':
            print("Generating audio with Coqui TTS")
            self.tts.tts_to_file(text, speaker_wav="my/cloning/audio.wav", file_path=path)
        elif self.engine == 'bark':
            print("Generating audio with Bark TTS")
            # Add [fast-paced] and [narration] conditioning tokens
            narration_text = "[narration][fast-paced] " + text
            inputs = self.processor(narration_text, voice_preset=self.voice_preset)
            audio_array = self.model.generate(**inputs)
            audio_array = audio_array.cpu().numpy().squeeze()
            sample_rate = self.model.generation_config.sample_rate
            scipy.io.wavfile.write(path, rate=sample_rate, data=audio_array)
