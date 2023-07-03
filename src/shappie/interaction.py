import json
import typing

import discord

import api.storage
import model
from .tools import tool
from . import llm


class Interaction:

    def __init__(
            self,
            client: discord.Client,
            message: discord.Message,
            store: api.storage.DataStore | None = None,
    ):
        self._client = client
        self._message = message
        self._channel_history = []
        self._store = store
        self._state: model.State | None = None
        self._modes = {
            "chatbot": self._chatbot_mode,
            "test": lambda: None,
        }

        self._tools = tool.ToolCollection()
        self._keywords = set(
            filter(lambda k: k in self._message.content, tool.TOOLS))
        self._add_relevant_tools()

    def _did_mention_bot(self) -> bool:
        guild = self._message.guild
        if guild:
            bot_roles = set(guild.get_member(self._client.user.id).roles)
            did_mention_role = bot_roles.intersection(self._message.role_mentions)
            did_mention_bot = self._client.user in self._message.mentions
            return did_mention_bot or did_mention_role
        return False

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

        message = model.Message(
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
            state=self._state,
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
            state=self._state,
        )

        return dict(content=response["content"][:2000])

    async def _respond_to_message_with_tools(self) -> dict[str, str]:
        did_select_tool, *values = await self._select_tool()
        if did_select_tool:
            selected_tool, kwargs = values
            results = await selected_tool(**kwargs)
            if results.pop("use_llm", False):
                history = self._channel_history
                response = await llm.generate_response_message(
                    messages=history,
                    state=self._state,
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

        return results

    async def respond_to_message(self) -> dict[str, str]:
        if len(self._tools) > 0:
            return await self._respond_to_message_with_tools()
        else:
            return await self._respond_to_message_without_tools()

    async def _chatbot_mode(self):
        if self._did_mention_bot():
            async with self._message.channel.typing():
                results = await self.respond_to_message()
            await self._message.reply(**results)
        elif self.should_respond():
            async with self._message.channel.typing():
                results = await self.respond_to_message()
            await self._message.channel.send(**results)

    async def start(self):
        if self._store:
            self._state = await self._store.get_state()
            mode = self._state.mode.name

            constitutions = ",".join([c.name for c in self._state.constitutions])
            persona = self._state.persona.name
            activity = discord.Game(
                name=f"{mode.capitalize()} | Const: {constitutions} | "
                     f"Persona: {persona}",
            )
            await self._client.change_presence(activity=activity)
            mode_name = self._state.mode.name
        else:
            mode_name = "chatbot"

        self._channel_history = await self._get_channel_history()

        await self.save_data()

        if self._message.author.bot:
            return

        mode = self._modes[mode_name]
        await mode()
