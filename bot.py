import os
import typing

import discord


class Shappie(discord.Client):
    channel = os.environ.get("DISCORD_TEST_CHANNEL")

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

        if message.content.startswith("doot"):
            await message.channel.send("Shappie do the doot doot!")
