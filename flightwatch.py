import time
import subprocess
import sys
from datetime import datetime


INTERVAL = 600


def run_tracker():

    print(
        f"[{datetime.now()}] Running FlightWatch check...",
        flush=True
    )

    result = subprocess.run(
        [
            sys.executable,
            "tracker.py"
        ],
        capture_output=True,
        text=True
    )

    if result.stdout:
        print(result.stdout, flush=True)

    if result.stderr:
        print("ERROR:", flush=True)
        print(result.stderr, flush=True)


while True:

    try:

        run_tracker()

    except Exception as e:

        print(
            f"FlightWatch error: {e}",
            flush=True
        )

    print(
        f"Sleeping {INTERVAL} seconds...",
        flush=True
    )

    time.sleep(INTERVAL)
