use python 3.14
pip install -r requirements.txt --build-constraint build-constraints.txt
playwright install

FFmpeg 4–9 with libass must be installed, it is used for the video (subtitles filter) and by torchcodec.
On macOS the Homebrew `ffmpeg` formula has no libass, use `brew install ffmpeg-full` and `brew unlink ffmpeg && brew link --force ffmpeg-full`.

Direct dependencies are in `requirements.in`. To update the pinned versions:
`uv pip compile requirements.in --universal --python-version 3.14 --no-annotate -o requirements.txt`

`main.py`: `source = "20min"` or `"reddit"`, `tts_engine = "edge"`, `"xtts"`, `"coqui"` or `"bark"`.
`edge` uses the free Microsoft Edge voices (no API key, unofficial, non-commercial use). Voices for title and comments are set in `TextToSpeech_External.edge_voices`.
XTTS v2 asks on first run to accept the Coqui CPML licence (non-commercial use only).
Subtitles are shown word by word, the style (font, size, colours, words per line) is set at the top of `VideoTranscriber.py`.
Cards and subtitles use Archivo Black from `assets/fonts` (SIL Open Font License, see `assets/fonts/OFL.txt`).
