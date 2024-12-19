import torch
import scipy
import os
from transformers import AutoProcessor, BarkModel
from TTS.api import TTS

class TextToSpeech_Local:
    def __init__(self, engine='coqui'):
        self.engine = engine.lower()

        if self.engine == 'coqui':
            print("Initializing Coqui TTS")
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.tts = TTS(model_name="tts_models/en/jenny/jenny", progress_bar=False).to(self.device)
        elif self.engine == 'bark':
            print("Initializing Bark TTS")
            os.environ["SUNO_OFFLOAD_CPU"] = "True"
            os.environ["SUNO_USE_SMALL_MODELS"] = "True"
            self.processor = AutoProcessor.from_pretrained("suno/bark")
            self.model = BarkModel.from_pretrained("suno/bark")
            self.voice_preset = "v2/en_speaker_6"
        else:
            raise ValueError("Unsupported engine. Choose 'coqui' or 'bark'.")

    def create_text_to_speech_file(self, text, path):
        if self.engine == 'coqui':
            print("Generating audio with Coqui TTS")
            self.tts.tts_to_file(text, speaker_wav="my/cloning/audio.wav", file_path=path)
        elif self.engine == 'bark':
            print("Generating audio with Bark TTS")
            inputs = self.processor(("[fast-paced]" + text), voice_preset=self.voice_preset)
            audio_array = self.model.generate(**inputs)
            audio_array = audio_array.cpu().numpy().squeeze()
            sample_rate = self.model.generation_config.sample_rate
            scipy.io.wavfile.write(path, rate=sample_rate, data=audio_array)
