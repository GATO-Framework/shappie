import os

import discord


class Shappie(discord.Client):
    channel = os.environ.get("DISCORD_TEST_CHANNEL")

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        if message.channel.id != self.channel:
            return

        if message.content.startswith("doot"):
            await message.channel.send("Shappie do the doot doot!")
