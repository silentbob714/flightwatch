import os
import yaml
import requests

from datasource import get_aircraft_positions


WEBHOOK = os.environ["DISCORD_WEBHOOK"]


with open("fleet.yaml", "r") as file:
    fleet_data = yaml.safe_load(file)


fleet = fleet_data["aircraft"]


positions = get_aircraft_positions()


status = []


for aircraft in fleet:

    icao = aircraft["icao24"].lower()

    registration = aircraft["registration"]
    aircraft_type = aircraft["type"]


    if icao not in positions:

        status.append(
            f"⚪ **{registration}**\n"
            f"{aircraft_type}\n"
            f"Status: No live position available"
        )

        continue


    data = positions[icao]


    altitude_ft = (
        round(data["altitude"] * 3.28084)
        if isinstance(data["altitude"], (int,float))
        else "Unknown"
    )


    speed_kts = (
        round(data["velocity"] * 1.94384)
        if isinstance(data["velocity"], (int,float))
        else "Unknown"
    )


    position = (
        f"{data['latitude']:.3f}, "
        f"{data['longitude']:.3f}"
        if data["latitude"] and data["longitude"]
        else "Unknown"
    )


    status.append(
        f"🟢 **{registration}**\n"
        f"{aircraft_type}\n"
        f"Flight: `{data['callsign']}`\n"
        f"Altitude: `{altitude_ft} ft`\n"
        f"Speed: `{speed_kts} kts`\n"
        f"Position: `{position}`"
    )


message = (
    "✈ **Lufthansa 100th Anniversary Fleet Status**\n\n"
    +
    "\n\n".join(status)
)


requests.post(
    WEBHOOK,
    json={
        "content": message
    }
)
