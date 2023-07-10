import json
import logging
import os
import typing

import discord
import openai

import api.storage
from . import interaction, llm

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

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if str(payload.emoji) == "💩":
            logging.warning(payload.emoji)
            channel = self.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)

            with open("data/fallacies.json") as file:
                fallacies = json.load(file)

            state = await self._store.get_state()
            content = message.content
            message.content = f"Determine if any logical fallacies are present " \
                              f"in this message: \"{content}\".\n" \
                              f"If any are present, explain which one(s) and why. " \
                              f"Additionally, ask a socratic question to continue " \
                              f"the dialogue by addressing the fallacious argument."
            async with channel.typing():
                response = await llm.generate_response_message(
                    messages=[message],
                    state=state,
                    additional_context=fallacies,
                )
            await message.reply(response["content"])

    async def on_message(self, message: discord.Message):
        bot_interaction = interaction.Interaction(self, message, self._store)
        await bot_interaction.start()
