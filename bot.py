import os

import discord

from discord.ext import commands

from dotenv import load_dotenv

from database import initialize_database


load_dotenv()


TOKEN = os.getenv("DISCORD_TOKEN")


initialize_database()



class FlightWatchBot(commands.Bot):

    def __init__(self):

        intents = discord.Intents.default()

        super().__init__(
            command_prefix="!",
            intents=intents
        )


    async def setup_hook(self):

        await self.load_extension(
            "cogs.aircraft"
        )

        await self.load_extension(
            "cogs.fleet"
        )

        await self.load_extension(
            "cogs.system"
        )

        synced = await self.tree.sync()

print(
    f"Synced {len(synced)} commands:"
)

for command in synced:
    print(
        f"- /{command.name}"
    )



bot = FlightWatchBot()



@bot.event
async def on_ready():

    print(
        f"Logged in as {bot.user}"
    )



bot.run(TOKEN)
