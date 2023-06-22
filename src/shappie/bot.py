import json
import os
import typing

import discord
import openai

import datastore
import llm
import tool

TOKEN = os.environ.get("DISCORD_TOKEN")
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


def save_message(message: discord.Message):
    pass


class Shappie(discord.Client):
    keywords = {"doot"}

    def __init__(self, *, intents: discord.Intents, **options: typing.Any):
        super().__init__(intents=intents, **options)
        self.tree = discord.app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

    def _get_relevant_tools(self, message: discord.Message):
        tools = tool.ToolCollection()
        relevant_keywords = filter(lambda k: k in message.content, self.keywords)
        for keyword in relevant_keywords:
            tools.add_tool(keyword)

        return tools

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        if PERSIST:
            store = datastore.DataStore(MONGO_URI, MONGO_DB_NAME)
            await store.save_message(message)

            if "http" in message.content:
                await store.save_link(message)

        if message.content == "!killit":
            await message.channel.purge()

        guild = message.guild
        shappie_member = guild.get_member(self.user.id)
        did_mention_role = set(shappie_member.roles).intersection(message.role_mentions)
        if self.user in message.mentions or did_mention_role:
            messages = []
            async for m in message.channel.history(limit=10):
                if m.author == self.user:
                    role = "assistant"
                    content = m.content
                else:
                    role = "user"
                    content = f"{m.content} [User: {m.author.display_name}]"

                messages.append({"role": role, "content": content})

            messages = list(reversed(messages))
            print(messages)

            async with message.channel.typing():
                response = await llm.generate_response_message(
                    messages=messages,
                    persona="You are Shappie, a discord bot with an attitude."
                            "You are grumpy and don't like to be bothered. "
                            "You should always respond as if you are annoyed "
                            "and just want to be left alone. "
                            "Look for any reason to use obnoxious emojis. "
                            "You should still try to help if possible, but you "
                            "will do so begrudgingly. However, don't let anyone know "
                            "that you don't want to help, that's just rude. "
                            "You should avoid revealing anything abut your true nature "
                            "at all costs.",
                )
            await message.channel.send(response)

        tools = self._get_relevant_tools(message)
        if len(tools):
            selected_tool, kwargs = select_tool(message, tools)
            result = selected_tool(**kwargs)
            await message.channel.send(result)
