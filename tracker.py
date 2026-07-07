import os
import yaml
import requests

from database import setup_database, already_alerted, save_alert


WEBHOOK = os.environ["DISCORD_WEBHOOK"]

username = os.environ["OPENSKY_USERNAME"]
password = os.environ["OPENSKY_PASSWORD"]


setup_database()


# Load tracked aircraft from fleet.yaml
with open("fleet.yaml", "r") as file:
    fleet_data = yaml.safe_load(file)


tracked_aircraft = fleet_data["aircraft"]


found = []


for aircraft_info in tracked_aircraft:

    icao24 = aircraft_info["icao24"].lower()
    registration = aircraft_info["registration"]
    aircraft_type = aircraft_info["type"]


    try:

        response = requests.get(
            "https://opensky-network.org/api/states/all",
            params={
                "icao24": icao24
            },
            auth=(username, password),
            timeout=60
        )


        if response.status_code != 200:
            continue


        data = response.json()

        states = data.get("states")


        if not states:
            continue


        state = states[0]


        callsign = (
            state[1].strip()
            if state[1]
            else "Unknown"
        )


        altitude_m = state[7]

        altitude_ft = (
            round(altitude_m * 3.28084)
            if altitude_m
            else "N/A"
        )


        latitude = state[6]
        longitude = state[5]


        speed_ms = state[9]

        speed_kts = (
            round(speed_ms * 1.94384)
            if speed_ms
            else "N/A"
        )


        heading = (
            round(state[10])
            if state[10]
            else "N/A"
        )


        if already_alerted(
            registration,
            callsign
        ):
            continue


        found.append(
            f"✈ **{registration}**\n"
            f"Type: `{aircraft_type}`\n"
            f"Flight: `{callsign}`\n"
            f"Altitude: `{altitude_ft:,} ft`\n"
            f"Speed: `{speed_kts} kts`\n"
            f"Heading: `{heading}°`\n"
            f"Position: `{latitude:.3f}, {longitude:.3f}`"
        )


        save_alert(
            registration,
            callsign
        )


    except Exception as e:

        print(
            f"Error checking {registration}: {e}"
        )


if found:

    message = (
        "🚨 **Lufthansa 100th Anniversary Aircraft Detected**\n\n"
        +
        "\n\n".join(found)
    )


    requests.post(
        WEBHOOK,
        json={
            "content": message
        }
    )

else:

    print(
        "No new anniversary aircraft detected."
    )
