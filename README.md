use python 3.10
pip install -r requirements.txt
playwright install

`main.py`: `source = "20min"` or `"reddit"`, `tts_engine = "edge"`, `"xtts"`, `"coqui"` or `"bark"`.
`edge` uses the free Microsoft Edge voices (no API key, unofficial, non-commercial use). Voices for title and comments are set in `TextToSpeech_External.edge_voices`.
XTTS v2 asks on first run to accept the Coqui CPML licence (non-commercial use only).
