use python 3.14
pip install -r requirements.txt --build-constraint build-constraints.txt
playwright install

FFmpeg 4–9 must be installed (e.g. `brew install ffmpeg`), it is used for the video and by torchcodec.

Direct dependencies are in `requirements.in`. To update the pinned versions:
`uv pip compile requirements.in --universal --python-version 3.14 --no-annotate -o requirements.txt`

`main.py`: `source = "20min"` or `"reddit"`, `tts_engine = "edge"`, `"xtts"`, `"coqui"` or `"bark"`.
`edge` uses the free Microsoft Edge voices (no API key, unofficial, non-commercial use). Voices for title and comments are set in `TextToSpeech_External.edge_voices`.
XTTS v2 asks on first run to accept the Coqui CPML licence (non-commercial use only).
