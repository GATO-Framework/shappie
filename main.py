import os

import discord

import bot

TOKEN = os.environ.get("DISCORD_TOKEN")


def main():
    bot.Shappie(intents=discord.Intents.all()).run(token=TOKEN)


if __name__ == '__main__':
    main()
