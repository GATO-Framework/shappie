from __future__ import annotations
from . import llm, tool
import model.persona
import model.message
import api.storage
import discord
import random
import typing
import json


def _did_mention_bot(message: discord.Message, bot_user: discord.ClientUser) -> bool:
    guild = message.guild
    if guild:
        bot_roles = set(guild.get_member(bot_user.id).roles)
        did_mention_role = bot_roles.intersection(message.role_mentions)
        did_mention_bot = bot_user in message.mentions
        return did_mention_bot or did_mention_role
    return False


async def _talking_to_bot(message: discord.Message) -> bool:
    if any([x in message.content.lower() for x in [
        'shappie',
        'shappy',
        'shapie',
        'shappi',
        'shapi',
        'shapp',
        'shapy',
    ]]):
        prompt = "This is a message sent by a user in a discord server. Shappie is a discord bot. Say 'Yes' if the message is talking *to* Shappie, and respond with 'No' if the message is talking *about* Shappie.\n\n" + message.content
        response = (await llm.get_completion(
            [{'role': 'user', 'content': prompt}],
            temperature=0,
            max_tokens=10,
            logit_bias={5297: 10, 2949: 10},
        ))['content']
        return response.lower().startswith('y')


class Interaction:

    def __init__(
            self,
            client: discord.ClientUser,
            message: discord.Message,
            store: api.storage.DataStore | None = None,
    ):
        self.client = client
        self._message = message
        self._channel_history = []
        self._persona = model.persona.DEFAULT
        self._store = store

        self._tools = tool.ToolCollection()
        self._keywords = set(
            filter(lambda k: k in self._message.content, tool.TOOLS))
        self._add_relevant_tools()

    async def should_respond(self):
        if _did_mention_bot(self._message, self.client.user):
            return True
        if len(self._keywords) > 0:
            return True
        if await _talking_to_bot(self._message):
            return True
        if await self._is_conversational_continuation():
            return True
        return False

    async def _is_conversational_continuation(self) -> bool:
        message = self._message
        history = await self._get_channel_history(limit=4)
        if not any([x.author == message.author for x in history]):
            return False
        # check if the last message was too long ago
        last_message = history[-2]
        if (message.created_at - last_message.created_at).total_seconds() > 150:
            return False

        prompt = "You will be given a conversation history. You will see [User: <username>] for each message, but this is just for context. You must identify if Shappie should respond to the last message in the conversation history.\n\n" + "\n".join(
            [f"{x.content} [User: <{x.author.display_name}>]" for x in history])
        response = (await llm.get_completion(
            [{'role': 'user', 'content': prompt}],
            temperature=0,
            max_tokens=10,
            logit_bias={5297: 10, 2949: 10},
        ))['content']
        print(response)
        return response.lower().startswith('y')

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
            results = await selected_tool(**kwargs)
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
