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



        print(
            "Copying application commands...",
            flush=True
        )


        self.tree.copy_global_to(
            guild=discord.Object(
                id=GUILD_ID
            )
        )


        synced = await self.tree.sync(
            guild=discord.Object(
                id=GUILD_ID
            )
        )


        print(
            f"Synced {len(synced)} guild commands:",
            flush=True
        )


        for command in synced:

            print(
                f"- /{command.name}",
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
