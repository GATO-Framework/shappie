import json
import typing

import discord

from . import bot, datastore, llm, tool


class Interaction:

    def __init__(self, store: datastore.DataStore | None = None):
        self._persona = None
        self._tools = None
        self._store = store

    def _add_relevant_tools(self, message: discord.Message):
        keywords = filter(lambda k: k in message.content, tool.TOOLS)
        for keyword in keywords:
            self._tools.add_tool(keyword)

    async def save_data(self, message: discord.Message):
        if not self._store:
            return

        await self._store.save_message(message)

        if "http" in message.content:
            await self._store.save_link(message)

    async def _get_persona(self, name) -> bot.persona.Persona:
        if self._store:
            return await self._store.get_persona(name)
        else:
            return bot.persona.DEFAULT

    async def _get_channel_history(
            self,
            channel: discord.TextChannel,
            limit=10,
    ) -> list[discord.Message]:
        history = channel.history(limit=limit)
        return list(reversed([message async for message in history]))

    async def _select_tool(
            self,
            message: discord.Message,
    ) -> tuple[bool, typing.Callable, dict]:
        history = await self._get_channel_history(message.channel)
        response = await llm.generate_response_message(
            messages=history,
            persona=self._persona,
            functions=self._tools.schema(),
        )
        function_call = response.get("function_call")
        if function_call:
            tool_name = function_call["name"]
            tool_args = json.loads(function_call["arguments"])

            return True, self._tools.get_tool(tool_name), tool_args

        return False, response["content"], {}

    async def _respond_to_message_without_tools(self, message: discord.Message) -> str:
        history = await self._get_channel_history(message.channel)
        response = await llm.generate_response_message(
            messages=history,
            persona=self._persona,
        )

        return response["content"]

    async def _respond_to_message_with_tools(self, message: discord.Message) -> str:
        did_select_tool, *values = await self._select_tool(message)
        if did_select_tool:
            selected_tool, kwargs = values
            content = selected_tool(**kwargs)
        else:
            content, _ = values

        response = await llm.generate_response_message(
            messages=[message],
            persona=self._persona,
            additional_context=content,
        )
        return response["content"]

    async def respond_to_message(
            self,
            message: discord.Message,
            persona: str = "default",
    ) -> str:
        self._persona = await self._get_persona(persona)
        self._tools = tool.ToolCollection()
        self._add_relevant_tools(message)
        if len(self._tools) > 0:
            return await self._respond_to_message_with_tools(message)
        else:
            return await self._respond_to_message_without_tools(message)
