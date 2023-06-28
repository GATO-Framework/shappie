import os

import discord

from shappie.bot import ShappieClient

TOKEN = os.environ.get("DISCORD_TOKEN")
shappie = ShappieClient(intents=discord.Intents.all())


def main():
    shappie.run(token=TOKEN)


if __name__ == '__main__':
    main()
