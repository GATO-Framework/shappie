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


def _did_mention_bot(message: discord.Message, bot_user: discord.ClientUser) -> bool:
    guild = message.guild
    if guild:
        bot_roles = set(guild.get_member(bot_user.id).roles)
        did_mention_role = bot_roles.intersection(message.role_mentions)
        did_mention_bot = bot_user in message.mentions
        return did_mention_bot or did_mention_role
    return False


async def _get_channel_history(
        channel: discord.TextChannel,
        limit=10,
) -> typing.Iterable[discord.Message]:
    return reversed([message async for message in channel.history(limit=limit)])


async def _respond_to_message_without_tools(
        message: discord.Message,
        bot_persona: persona.Persona
) -> str:
    history = await _get_channel_history(message.channel)
    response = await llm.generate_response_message(
        messages=history,
        persona=bot_persona,
    )

    return response["content"]


async def _respond_to_message_with_tools(
        message: discord.Message,
        bot_persona: persona.Persona,
        tools: tool.ToolCollection,
) -> str:
    did_select_tool, *values = await _select_tool(
        message, bot_persona, tools
    )
    if did_select_tool:
        selected_tool, kwargs = values
        result = selected_tool(**kwargs)
        return result
    else:
        content, _ = values
        return content


async def _respond_to_message(
        message: discord.Message,
        bot_persona: persona.Persona,
        tools: tool.ToolCollection,
) -> str:
    if len(tools) > 0:
        return await _respond_to_message_with_tools(message, bot_persona, tools)
    else:
        return await _respond_to_message_without_tools(message, bot_persona)


async def _select_tool(
        message: discord.Message,
        bot_persona: persona.Persona,
        tools: tool.ToolCollection,
) -> tuple[bool, typing.Callable, dict]:
    history = await _get_channel_history(message.channel)
    response = await llm.generate_response_message(
        messages=history,
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


class ShappieClient(discord.Client):
    def __init__(self, *, intents: discord.Intents, **options: typing.Any):
        super().__init__(intents=intents, **options)
        self.tree = discord.app_commands.CommandTree(self)
        self._store = None
        if PERSIST:
            self._store = datastore.DataStore(MONGO_URI, MONGO_DB_NAME)

    async def setup_hook(self):
        await self.tree.sync()

    async def _save_data(self, message: discord.Message):
        if not self._store:
            return

        await self._store.save_message(message)

        if "http" in message.content:
            await self._store.save_link(message)

    async def _get_persona(self):
        if self._store:
            return await self._store.get_persona("default")
        else:
            return persona.DEFAULT

    async def on_message(self, message: discord.Message):
        await self._save_data(message)

        if message.author.bot:
            return

        tools = tool.ToolCollection()
        tools.add_relevant_tools(message)

        async with message.channel.typing():
            bot_persona = await self._get_persona()
            content = await _respond_to_message(message, bot_persona, tools)

        if _did_mention_bot(message, self.user):
            await message.reply(content)
        else:
            await message.channel.send(content)
