import discord

from discord.ext import commands

from database import get_connection



class System(commands.Cog):

    def __init__(self, bot):

        self.bot = bot



    @discord.app_commands.command(
        name="status",
        description="Show FlightWatch system status"
    )
    async def status(
        self,
        interaction: discord.Interaction
    ):

        try:

            conn = get_connection()

            cursor = conn.cursor()


            cursor.execute(
                "SELECT COUNT(*) FROM tracked_aircraft WHERE active = 1"
            )


            tracked_count = cursor.fetchone()[0]


            conn.close()


            database_status = "🟢 Online"


        except Exception:

            tracked_count = "Unknown"

            database_status = "🔴 Error"



        embed = discord.Embed(

            title="✈ FlightWatch Status",

            description="System health report"

        )


        embed.add_field(

            name="Bot",

            value="🟢 Online",

            inline=True

        )


        embed.add_field(

            name="Database",

            value=database_status,

            inline=True

        )


        embed.add_field(

            name="Tracked Aircraft",

            value=str(tracked_count),

            inline=True

        )


        await interaction.response.send_message(

            embed=embed

        )





async def setup(bot):

    await bot.add_cog(

        System(bot)

    )
