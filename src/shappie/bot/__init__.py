import json
import os
import typing

import discord
import openai

from . import persona
from .. import datastore, llm, tool

MONGO_URI = os.environ.get("MONGO_URI")
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PERSIST = bool(os.environ.get("PERSIST", False))

openai.api_key = OPENAI_API_KEY


def select_tool(
        message: discord.Message,
        tools: tool.ToolCollection,
) -> tuple[typing.Callable, dict]:
    # TODO: Use a language model based on the message content
    selected_tool_name, kwargs_string = "doot", "{}"

    selected_tool = tools.get_tool(selected_tool_name)
    kwargs = json.loads(kwargs_string)
    return selected_tool, kwargs


class Shappie(discord.Client):
    keywords = {"doot"}

    def __init__(self, *, intents: discord.Intents, **options: typing.Any):
        super().__init__(intents=intents, **options)
        self.tree = discord.app_commands.CommandTree(self)
        self._store = None
        if PERSIST:
            self._store = datastore.DataStore(MONGO_URI, MONGO_DB_NAME)

    async def setup_hook(self):
        await self.tree.sync()

    def _get_relevant_tools(self, message: discord.Message):
        tools = tool.ToolCollection()
        relevant_keywords = filter(lambda k: k in message.content, self.keywords)
        for keyword in relevant_keywords:
            tools.add_tool(keyword)

        return tools

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if self._store:
            await self._store.save_message(message)

            if "http" in message.content:
                await self._store.save_link(message)

        if message.content == "!killit":
            await message.channel.purge()

        guild = message.guild
        shappie_member = guild.get_member(self.user.id)
        did_mention_role = set(shappie_member.roles).intersection(message.role_mentions)
        did_mention_bot = self.user in message.mentions or did_mention_role
        if did_mention_bot:
            if self._store:
                bot_persona = self._store.get_persona("")
            else:
                bot_persona = persona.DEFAULT

            async with message.channel.typing():
                response = await llm.generate_response_message(
                    message=message,
                    persona=bot_persona,
                )
            await message.reply(response)

        tools = self._get_relevant_tools(message)
        if len(tools):
            selected_tool, kwargs = select_tool(message, tools)
            result = selected_tool(**kwargs)
            await message.channel.send(result)
