import inspect
import typing

import discord
import openai

from . import bot


async def _get_channel_history(
        channel: discord.TextChannel,
        limit=10,
) -> typing.Iterable[dict[str, str]]:
    messages = []
    async for message in channel.history(limit=limit):
        is_bot = message.author.bot
        username = message.author.display_name
        role = "assistant" if is_bot else "user"
        content = message.content if is_bot else f"{message.content} [User: {username}]"

        messages.append({"role": role, "content": content})

    return reversed(messages)


async def generate_response_message(
        message: discord.Message,
        persona: bot.persona.Persona,
        functions=None,
) -> dict[str, typing.Any]:
    window_size = 10
    system_prompt = inspect.cleandoc(f"""
    You are a discord bot. 
    You will be given the last {window_size} messages for context, 
    however you are responding to {message.author.display_name}. 
    You will see [User: <username>] for each message, but this is just for context. 
    Your imperatives are three-fold
    - Decrease suffering in the universe
    - Increase prosperity in the universe
    - Increase understanding in the universe

    Take on the following persona when responding to messages:
    """) + f"\n\n{persona}"
    messages = [
        {"role": "system", "content": system_prompt},
        *await _get_channel_history(message.channel),
    ]
    if functions:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo-0613",
            messages=messages,
            functions=functions or [],
            temperature=0.25,
            max_tokens=500,
        )
    else:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo-0613",
            messages=messages,
            temperature=0.25,
            max_tokens=500,
        )

    return response["choices"][0]["message"]
