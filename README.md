FlightWatch

Services:
- flightwatch.service
- flightwatch-bot.service

Commands:
- /track
- /untrack
- /lookup
- /fleet
- /status

Structure:
- tracker.py = OpenSky monitoring
- bot.py = Discord startup
- cogs = Discord commands
- database.py = SQLite layer
