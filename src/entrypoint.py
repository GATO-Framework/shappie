import os

import discord

from shappie.bot import ShappieClient

TOKEN = os.environ.get("DISCORD_TOKEN")
shappie = ShappieClient(intents=discord.Intents.all())


def main():
    shappie.run(token=TOKEN)


@shappie.tree.command(name="doot", description="Do the doot")
async def doot(interaction: discord.Interaction):
    await interaction.response.send_message("doot doot the dootly doot 🔥")


if __name__ == '__main__':
    main()
