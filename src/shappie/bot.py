import os
import typing

import discord
import openai

import api.storage
from . import interaction

MONGO_URI = os.environ.get("MONGO_URI")
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PERSIST = bool(os.environ.get("PERSIST", False))

openai.api_key = OPENAI_API_KEY


class ShappieClient(discord.Client):
    def __init__(self, *, intents: discord.Intents, **options: typing.Any):
        super().__init__(intents=intents, **options)
        self.tree = discord.app_commands.CommandTree(self)
        self._store = None
        if PERSIST:
            self._store = api.storage.DataStore(MONGO_URI, MONGO_DB_NAME)

    async def setup_hook(self):
        await self.tree.sync()

    async def on_message(self, message: discord.Message):
        bot_interaction = interaction.Interaction(self, message, self._store)
        await bot_interaction.start()
