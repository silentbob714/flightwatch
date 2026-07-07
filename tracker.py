import os
import yaml
import requests


WEBHOOK = os.environ["DISCORD_WEBHOOK"]

username = os.environ["OPENSKY_USERNAME"]
password = os.environ["OPENSKY_PASSWORD"]


with open("fleet.yaml", "r") as file:
    fleet_data = yaml.safe_load(file)


tracked_aircraft = fleet_data["aircraft"]


status = []


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
            status.append(
                f"❌ **{registration}**\n"
                f"OpenSky error: {response.status_code}"
            )
            continue


        data = response.json()

        states = data.get("states")


        if not states:

            status.append(
                f"⚪ **{registration}**\n"
                f"{aircraft_type}\n"
                f"Status: Not currently airborne"
            )

            continue


        state = states[0]


        callsign = (
            state[1].strip()
            if state[1]
            else "Unknown"
        )


        altitude_ft = (
            round(state[7] * 3.28084)
            if isinstance(state[7], (int, float))
            else None
        )


        speed_kts = (
            round(state[9] * 1.94384)
            if isinstance(state[9], (int, float))
            else None
        )


        latitude = state[6]
        longitude = state[5]


        altitude_display = (
            f"{altitude_ft:,} ft"
            if altitude_ft is not None
            else "Unknown"
        )


        speed_display = (
            f"{speed_kts} kts"
            if speed_kts is not None
            else "Unknown"
        )


        position_display = (
            f"{latitude:.3f}, {longitude:.3f}"
            if isinstance(latitude, (int, float))
            and isinstance(longitude, (int, float))
            else "Unknown"
        )


        status.append(
            f"🟢 **{registration}**\n"
            f"{aircraft_type}\n"
            f"Flight: `{callsign}`\n"
            f"Altitude: `{altitude_display}`\n"
            f"Speed: `{speed_display}`\n"
            f"Position: `{position_display}`"
        )


    except Exception as e:

        status.append(
            f"❌ **{registration}**\n"
            f"Error: {e}"
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
