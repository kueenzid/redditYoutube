import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Times of day for a run, set in docker-compose.yml, e.g. RUN_TIMES=07:30,12:30,18:30
RUN_TIMES = os.environ.get("RUN_TIMES", "07:30,12:30,18:30")
SWISS_TIME = ZoneInfo("Europe/Zurich")


def next_run(now):
    runs = []
    for run_time in RUN_TIMES.split(","):
        hour, minute = (int(part) for part in run_time.strip().split(":"))
        run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if run <= now:
            run += timedelta(days=1)
        runs.append(run)
    return min(runs)


# Runs main.py at RUN_TIMES (Swiss time) until the container is stopped.
# main.py runs as its own process, so a failed run does not stop the schedule.
if __name__ == "__main__":
    while True:
        run = next_run(datetime.now(SWISS_TIME))
        print(f"Next run at {run:%Y-%m-%d %H:%M}", flush=True)
        # Timestamps, because subtracting times in the same time zone ignores the switch to summer time
        time.sleep(max(0, run.timestamp() - time.time()))

        print(f"Run started at {datetime.now(SWISS_TIME):%Y-%m-%d %H:%M}", flush=True)
        result = subprocess.run([sys.executable, "main.py"])
        print(f"Run finished with exit code {result.returncode}", flush=True)
