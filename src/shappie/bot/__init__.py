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


def _get_relevant_tools(message: discord.Message):
    tools = tool.ToolCollection()
    relevant_keywords = filter(lambda k: k in message.content, tool.TOOLS)
    for keyword in relevant_keywords:
        tools.add_tool(keyword)

    return tools


async def select_tool(
        message: discord.Message,
        bot_persona: persona.Persona,
        tools: tool.ToolCollection,
) -> tuple[bool, typing.Callable, dict]:
    print(tools.schema())
    response = await llm.generate_response_message(
        message=message,
        persona=bot_persona,
        functions=tools.schema(),
    )
    print(response)
    function_call = response.get("function_call")
    if function_call:
        tool_name = function_call["name"]
        tool_args = json.loads(function_call["arguments"])

        return True, tools.get_tool(tool_name), tool_args

    return False, response["content"], {}


class Shappie(discord.Client):
    def __init__(self, *, intents: discord.Intents, **options: typing.Any):
        super().__init__(intents=intents, **options)
        self.tree = discord.app_commands.CommandTree(self)
        self._store = None
        if PERSIST:
            self._store = datastore.DataStore(MONGO_URI, MONGO_DB_NAME)

    async def setup_hook(self):
        await self.tree.sync()

    async def on_message(self, message: discord.Message):
        if self._store:
            await self._store.save_message(message)

            if "http" in message.content:
                await self._store.save_link(message)

        if message.author.bot:
            return

        if self._store:
            bot_persona = await self._store.get_persona("default")
        else:
            bot_persona = persona.DEFAULT

        did_mention_bot = self.user in message.mentions
        guild = message.guild
        if guild:
            shappie_member = guild.get_member(self.user.id)
            did_mention_role = set(shappie_member.roles).intersection(
                message.role_mentions
            )
            did_mention_bot = did_mention_bot or did_mention_role

        tools = _get_relevant_tools(message)
        if len(tools):
            async with message.channel.typing():
                did_select_tool, *values = await select_tool(
                    message, bot_persona, tools
                )
                if did_select_tool:
                    selected_tool, kwargs = values
                    result = selected_tool(**kwargs)
                    await message.channel.send(result)
                else:
                    content, _ = values
                    await message.channel.send(content)
        elif did_mention_bot:
            async with message.channel.typing():
                content = await llm.generate_response_message(
                    message=message,
                    persona=bot_persona,
                )
            await message.reply(content["content"])
