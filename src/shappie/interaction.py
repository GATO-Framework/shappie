import json
import typing

import discord

import api.storage
import model.message
import model.persona
from . import llm, tool


class Interaction:

    def __init__(
            self,
            message: discord.Message,
            store: api.storage.DataStore | None = None,
    ):
        self._message = message
        self._channel_history = []
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

    def _channel_name(self):
        channel = self._message.channel
        is_dm = isinstance(channel, discord.DMChannel)
        return "dm" if is_dm else channel.name

    def _server_name(self):
        if self._message.guild:
            return self._message.guild.name
        return None

    async def save_data(self):
        if not self._store:
            return

        message = model.message.Message(
            server=self._server_name(),
            channel=self._channel_name(),
            sender=self._message.author.name,
            message=self._message.content,
            time=self._message.created_at,
        )
        await self._store.save_message(message)

    async def _get_channel_history(self, limit=10) -> list[discord.Message]:
        history = self._message.channel.history(limit=limit)
        return list(reversed([message async for message in history]))

    async def _select_tool(
            self,
    ) -> tuple[bool, typing.Callable, dict]:
        history = self._channel_history
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

    async def _respond_to_message_without_tools(self) -> dict[str, str]:
        history = self._channel_history
        response = await llm.generate_response_message(
            messages=history,
            persona=self._persona,
        )

        return dict(content=response["content"][:2000])

    async def _respond_to_message_with_tools(self) -> dict[str, str]:
        did_select_tool, *values = await self._select_tool()
        if did_select_tool:
            selected_tool, kwargs = values
            results = selected_tool(**kwargs)
            if results.pop("use_llm", False):
                history = self._channel_history
                response = await llm.generate_response_message(
                    messages=history,
                    persona=self._persona,
                    additional_context=results.pop("context"),
                )
                content = response["content"]
                results["content"] = content[:2000]
        else:
            content, _ = values
            results = dict(content=content)

        if url := results.pop("url", None):
            embed = discord.Embed(title="When to Meet", url=url)
            results["embed"] = embed

        if url := results.pop("image_url", None):
            embed = discord.Embed()
            embed.set_image(url=url)
            results["embed"] = embed

        print(results)
        return results

    async def respond_to_message(self, persona: str = "default") -> dict[str, str]:
        if self._store:
            self._persona = await self._store.get_persona(persona)
        self._channel_history = await self._get_channel_history()
        if len(self._tools) > 0:
            return await self._respond_to_message_with_tools()
        else:
            return await self._respond_to_message_without_tools()
