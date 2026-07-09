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

        await self.load_extension(
            "cogs.aircraft"
        )

        await self.load_extension(
            "cogs.fleet"
        )

        await self.load_extension(
            "cogs.system"
        )


        guild = discord.Object(
            id=GUILD_ID
        )


        # Remove old global commands
        self.tree.clear_commands(
            guild=None
        )


        print("Copying application commands...")


        self.tree.copy_global_to(
            guild=guild
        )


        print("Syncing guild commands...")


        synced = await self.tree.sync(
            guild=guild
        )


        print(
            f"Synced {len(synced)} guild commands:"
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
