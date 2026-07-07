import os
import requests

WEBHOOK = os.environ["DISCORD_WEBHOOK"]

username = os.environ["OPENSKY_USERNAME"]
password = os.environ["OPENSKY_PASSWORD"]

response = requests.get(
    "https://opensky-network.org/api/states/all",
    auth=(username, password),
    timeout=120
)

data = response.json()

count = len(data.get("states", []))

payload = {
    "content": f"OpenSky returned {count:,} aircraft states."
}

requests.post(WEBHOOK, json=payload)
