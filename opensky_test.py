import os
import requests

WEBHOOK = os.environ["DISCORD_WEBHOOK"]

username = os.environ["OPENSKY_USERNAME"]
password = os.environ["OPENSKY_PASSWORD"]

try:
    response = requests.get(
        "https://opensky-network.org/api/states/all",
        auth=(username, password),
        timeout=120
    )

    payload = {
        "content": f"Status: {response.status_code}"
    }

except Exception as e:
    payload = {
        "content": f"ERROR: {type(e).__name__}: {str(e)}"
    }

requests.post(WEBHOOK, json=payload)
