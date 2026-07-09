import os

import discord

from discord.ext import commands

from dotenv import load_dotenv

from database import initialize_database


load_dotenv()


TOKEN = os.getenv("DISCORD_TOKEN")

GUILD_ID = 408190501045534720


initialize_database()



class FlightWatchBot(commands.Bot):

    def __init__(self):

        intents = discord.Intents.default()

        super().__init__(
            command_prefix="!",
            intents=intents
        )


async def setup_hook(self):

    print("===== SETUP HOOK START =====", flush=True)

    print("Loading cogs...", flush=True)

    await self.load_extension(
        "cogs.aircraft"
    )

    print("Loaded aircraft cog", flush=True)


    await self.load_extension(
        "cogs.fleet"
    )

    print("Loaded fleet cog", flush=True)


    await self.load_extension(
        "cogs.system"
    )

    print("Loaded system cog", flush=True)


    guild = discord.Object(
        id=GUILD_ID
    )


    print(
        "Removing old global commands...",
        flush=True
    )

    self.tree.clear_commands(
        guild=None
    )


    print(
        "Syncing guild commands...",
        flush=True
    )


    synced = await self.tree.sync(
        guild=guild
    )


    print(
        f"Synced {len(synced)} commands:",
        flush=True
    )


    for command in synced:

        print(
            f"- /{command.name}",
            flush=True
        )


    print(
        "===== SETUP HOOK COMPLETE =====",
        flush=True
    )





bot = FlightWatchBot()



@bot.event
async def on_ready():

    print(
        f"Logged in as {bot.user}",
        flush=True
    )



bot.run(TOKEN)
