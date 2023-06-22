import json
import typing

import discord

import llm
import tool


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

        if self.user in message.mentions:
            response = await llm.generate_response_message(
                message=message.content,
                persona="You are Shappie, you are grumpy and don't like to be bother. "
                        "You should always respond as if you are annoyed and just "
                        "want to be left alone. Look for a reason to use rude "
                        "or other obnoxious emojis if possible.",
            )
            await message.channel.send(response)

        save_message(message)

        tools = self._get_relevant_tools(message)
        if len(tools):
            selected_tool, kwargs = select_tool(message, tools)
            result = selected_tool(**kwargs)
            await message.channel.send(result)
