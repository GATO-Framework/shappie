import os

import discord

from shappie.bot import Shappie
from keep_alive import keep_alive

TOKEN = os.environ.get("DISCORD_TOKEN")
shappie = Shappie(intents=discord.Intents.all())


def main():
    keep_alive()
    shappie.run(token=TOKEN)


@shappie.tree.command(name="doot", description="Do the doot")
async def doot(interaction: discord.Interaction):
    await interaction.response.send_message("doot doot the dootly doot 🔥")


if __name__ == '__main__':
    main()
