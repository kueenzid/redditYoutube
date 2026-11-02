use python 3.10
pip install -r requirements.txt
playwright install

`main.py`: `source = "20min"` or `"reddit"`, `tts_engine = "xtts"`, `"coqui"` or `"bark"`.
XTTS v2 asks on first run to accept the Coqui CPML licence (non-commercial use only).
For `tts_engine = "azure"` (free tier F0, 500'000 characters/month) add `azure_speech_key` and `azure_speech_region` to `config.py`.
