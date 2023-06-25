import json
import typing

import discord

import api.storage
import model.persona
from . import llm, tool


class Interaction:

    def __init__(
            self,
            message: discord.Message,
            store: api.storage.DataStore | None = None,
    ):
        self._message = message
        self._persona = model.persona.DEFAULT
        self._store = store

        self._tools = tool.ToolCollection()
        self._keywords = set(filter(lambda k: k in self._message.content, tool.TOOLS))
        self._add_relevant_tools()

    def should_respond(self):
        return len(self._keywords) > 0

    def _add_relevant_tools(self):
        for keyword in self._keywords:
            self._tools.add_tool(keyword)

    async def save_data(self):
        if not self._store:
            return

        await self._store.save_message(self._message)

        if "http" in self._message.content:
            await self._store.save_link(self._message)

    async def _get_channel_history(self, limit=10) -> list[discord.Message]:
        history = self._message.channel.history(limit=limit)
        return list(reversed([message async for message in history]))

    async def _select_tool(
            self,
    ) -> tuple[bool, typing.Callable, dict]:
        history = await self._get_channel_history()
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

    async def _respond_to_message_without_tools(self) -> str:
        history = await self._get_channel_history()
        response = await llm.generate_response_message(
            messages=history,
            persona=self._persona,
        )

        return response["content"]

    async def _respond_to_message_with_tools(self) -> str:
        did_select_tool, *values = await self._select_tool()
        if did_select_tool:
            selected_tool, kwargs = values
            content = selected_tool(**kwargs)
        else:
            content, _ = values

        response = await llm.generate_response_message(
            messages=[self._message],
            persona=self._persona,
            additional_context=content,
        )
        return response["content"]

    async def respond_to_message(self, persona: str = "default") -> str:
        if self._store:
            self._persona = await self._store.get_persona(persona)
        if len(self._tools) > 0:
            return await self._respond_to_message_with_tools()
        else:
            return await self._respond_to_message_without_tools()
