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

YouTube upload (`upload_youtube` in `main.py`):
1. In the Google Cloud Console enable the YouTube Data API v3 and create an OAuth client of type "Desktop app". Save it as `Youtube/Config/client_secret.json`.
2. Set the OAuth consent screen to "In production", otherwise the login expires after 7 days.
3. Log in once from the repository root: `python Youtube/auth.py`.
Videos uploaded by API projects that YouTube has not audited stay private, whatever `youtube_privacy` says.

## Docker

The image contains Python, FFmpeg with libass, headless Chromium and all packages (torch as CPU build).
Settings like `source` or `youtube_privacy` are in `main.py`, so rebuild the image after changing them.

1. Put the background video into `assets/backgroundVideos/`.
2. Log in to YouTube once on a computer with a browser (see above), so that `Youtube/Config/` contains `client_secret.json` and `token.json`. On a server without a browser, copy both files there.
3. Build the image: `docker compose build`
4. Test one run: `docker compose run --rm app`

`Output/` (videos and `uploaded.json`), `Youtube/Config/` and `assets/backgroundVideos/` are mounted from the repository folder, the Whisper model is kept in the `model-cache` volume.

Three runs a day with the `scheduler` service, which runs `main.py` at `RUN_TIMES` (Swiss time, set in `docker-compose.yml`) and restarts with Docker, e.g. on a NAS:
```
docker compose up -d scheduler
docker compose logs -f scheduler
```
After changing the code or `RUN_TIMES`: `docker compose build && docker compose up -d scheduler`.

Or with cron on the host (`crontab -e`) instead, `flock` skips a run while the previous one is still running:
```
CRON_TZ=Europe/Zurich
30 7,12,18 * * * cd /path/to/redditYoutube && flock -n /tmp/reddit-youtube.lock docker compose run --rm app >> cron.log 2>&1
```
