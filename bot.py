import os
import typing

import discord


def doot():
    return "Shappie do the doot doot!"


class Shappie(discord.Client):
    channel = int(os.environ.get("DISCORD_TEST_CHANNEL"))
    keyword_commands = {"doot": doot}

    def __init__(self, *, intents: discord.Intents, **options: typing.Any):
        super().__init__(intents=intents, **options)
        self.tree = discord.app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        if message.channel.id != self.channel:
            return

        for keyword, command in self.keyword_commands.items():
            if keyword in message.content:
                await message.channel.send(command())
