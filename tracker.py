import os
import yaml
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

from datasource import get_aircraft_positions

load_dotenv()

WEBHOOK = os.getenv("DISCORD_WEBHOOK")

with open("fleet.yaml", "r") as file:
fleet = yaml.safe_load(file)["aircraft"]

positions = get_aircraft_positions()

def get_status(data):

```
altitude_ft = (
    round(data["altitude"] * 3.28084)
    if isinstance(data["altitude"], (int, float))
    else 0
)

speed_kts = (
    round(data["velocity"] * 1.94384)
    if isinstance(data["velocity"], (int, float))
    else 0
)

if altitude_ft > 1000:
    return "🟢 Airborne", altitude_ft, speed_kts

if speed_kts > 5:
    return "🟡 Ground Movement", altitude_ft, speed_kts

return "🔵 On Ground", altitude_ft, speed_kts
```

lines = []

for aircraft in fleet:

```
registration = aircraft["registration"]
aircraft_type = aircraft["type"]
icao = aircraft["icao24"].lower()

if icao not in positions:

    lines.append(
        f"⚪ {registration} | {aircraft_type}\n"
        f"Status: No live position"
    )

    continue

data = positions[icao]

status, altitude_ft, speed_kts = get_status(data)

callsign = data["callsign"] or "Unknown"

latitude = data["latitude"]
longitude = data["longitude"]

if latitude and longitude:
    position = f"{latitude:.3f}, {longitude:.3f}"
else:
    position = "Unknown"

if data["last_contact"]:
    age = round(
        datetime.now(timezone.utc).timestamp()
        - data["last_contact"]
    )
else:
    age = -1

lines.append(
    f"{status} {registration}\n"
    f"{aircraft_type}\n"
    f"Flight: {callsign}\n"
    f"Alt: {altitude_ft:,} ft | "
    f"Speed: {speed_kts} kts\n"
    f"Pos: {position}\n"
    f"Seen: {age}s ago"
)
```

message = "✈ FlightWatch\n\n" + "\n\n".join(lines)

print(f"Message length: {len(message)}")

response = requests.post(
WEBHOOK,
json={"content": message}
)

print(f"Discord response: {response.status_code}")
print(response.text)
