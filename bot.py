import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from database import initialize_database


load_dotenv()


TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = 408190501045534720


if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing from the environment.")


initialize_database()


class FlightWatchBot(commands.Bot):

    def __init__(self):

        intents = discord.Intents.none()
        intents.guilds = True

        super().__init__(
            command_prefix=None,
            intents=intents,
            help_command=None
        )


    async def setup_hook(self):

        print("===== SETUP HOOK START =====", flush=True)
        print("Loading cogs...", flush=True)

        await self.load_extension("cogs.aircraft")
        print("Loaded aircraft cog", flush=True)

        await self.load_extension("cogs.fleet")
        print("Loaded fleet cog", flush=True)

        await self.load_extension("cogs.system")
        print("Loaded system cog", flush=True)

        guild = discord.Object(id=GUILD_ID)

        print(
            "Removing stale guild-specific commands...",
            flush=True
        )

        self.tree.clear_commands(guild=guild)

        guild_commands = await self.tree.sync(guild=guild)

        print(
            f"Synced {len(guild_commands)} guild-specific commands.",
            flush=True
        )

        print("Syncing global commands...", flush=True)

        global_commands = await self.tree.sync()

        print(
            f"Synced {len(global_commands)} global commands:",
            flush=True
        )

        for command in global_commands:
            print(
                f"- /{command.name}",
                flush=True
            )

        print("===== SETUP HOOK COMPLETE =====", flush=True)


bot = FlightWatchBot()


@bot.event
async def on_ready():

    print(
        f"Logged in as {bot.user}",
        flush=True
    )


bot.run(TOKEN)
