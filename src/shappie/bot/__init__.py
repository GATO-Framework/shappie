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


def _split_string_into_chunks(input_string, chunk_size=2000):
    return [input_string[i:i + chunk_size]
            for i in range(0, len(input_string), chunk_size)]


class ShappieClient(discord.Client):
    def __init__(self, *, intents: discord.Intents, **options: typing.Any):
        super().__init__(intents=intents, **options)
        self.tree = discord.app_commands.CommandTree(self)
        self._store = None
        if PERSIST:
            self._store = datastore.DataStore(MONGO_URI, MONGO_DB_NAME)

    async def setup_hook(self):
        await self.tree.sync()

    async def on_message(self, message: discord.Message):
        bot_interaction = interaction.Interaction(message, self._store)

        await bot_interaction.save_data()

        if message.author.bot:
            return

        if _did_mention_bot(message, self.user):
            async with message.channel.typing():
                content = await bot_interaction.respond_to_message()
                await message.reply(content)
        elif bot_interaction.should_respond():
            async with message.channel.typing():
                content = await bot_interaction.respond_to_message()
                for chunk in _split_string_into_chunks(content):
                    await message.reply(chunk)
