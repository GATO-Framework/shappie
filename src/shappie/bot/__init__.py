import os
import typing

import discord
import openai

from . import persona
from .. import datastore, interaction

MONGO_URI = os.environ.get("MONGO_URI")
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PERSIST = bool(os.environ.get("PERSIST", False))

openai.api_key = OPENAI_API_KEY


def _did_mention_bot(message: discord.Message, bot_user: discord.ClientUser) -> bool:
    guild = message.guild
    if guild:
        bot_roles = set(guild.get_member(bot_user.id).roles)
        did_mention_role = bot_roles.intersection(message.role_mentions)
        did_mention_bot = bot_user in message.mentions
        return did_mention_bot or did_mention_role
    return False


class ShappieClient(discord.Client):
    def __init__(self, *, intents: discord.Intents, **options: typing.Any):
        super().__init__(intents=intents, **options)
        self.tree = discord.app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

    async def on_message(self, message: discord.Message):
        store = None
        if PERSIST:
            store = datastore.DataStore(MONGO_URI, MONGO_DB_NAME)
        bot_interaction = interaction.Interaction(store)

        await bot_interaction.save_data(message)

        if message.author.bot:
            return

        async with message.channel.typing():
            content = await bot_interaction.respond_to_message(message)

        if _did_mention_bot(message, self.user):
            await message.reply(content)
        else:
            await message.channel.send(content[:2000])
