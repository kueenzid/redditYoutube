import torch
from TTS.api import TTS

class TextToSpeech:
    def __init__(self):
        #Get the device
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # List available 🐸TTS models
        #print(TTS().list_models())

        # Init TTS with the target model name
        self.tts = TTS(model_name="tts_models/en/jenny/jenny", progress_bar=False).to(self.device)

    # Run TTS
    def create_text_to_speech_file(self, text, path):
        self.tts.tts_to_file(text, speaker_wav="my/cloning/audio.wav", file_path=path)
