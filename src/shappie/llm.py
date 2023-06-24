import inspect
import typing

import discord
import openai

from . import bot


def _format_chat_messages(
        messages: typing.Iterable[discord.Message],
) -> typing.Iterable[dict[str, str]]:
    chat_messages = []
    for message in messages:
        is_bot = message.author.bot
        username = message.author.display_name
        role = "assistant" if is_bot else "user"
        content = message.content if is_bot else f"{message.content} [User: {username}]"

        chat_messages.append({"role": role, "content": content})

    return reversed(chat_messages)


async def get_completion(
        messages: list[dict[str, str]],
        functions=None,
        temperature: float = 0.25,
        max_tokens: float = 500,
) -> dict[str, typing.Any]:
    if functions:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo-0613",
            messages=messages,
            functions=functions or [],
            temperature=temperature,
            max_tokens=max_tokens,
        )
    else:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo-0613",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    return response["choices"][0]["message"]


async def generate_response_message(
        messages: typing.Iterable[discord.Message],
        persona: bot.persona.Persona,
        additional_context: str = "",
        functions=None,
        temperature: float = 0.25,
        max_tokens: float = 500,
        lookback=10,
) -> dict[str, typing.Any]:
    system_prompt = inspect.cleandoc(f"""
    You are a discord bot. 
    You will be given the last {lookback} messages for context, 
    however you are responding to {messages[-1].author.display_name}. 
    You will see [User: <username>] for each message, but this is just for context. 
    Your imperatives are three-fold
    - Decrease suffering in the universe
    - Increase prosperity in the universe
    - Increase understanding in the universe

    Take on the following persona when responding to messages:
    """) + f"\n\n{persona}" + f"\n\nAdditional Context:\n{additional_context}"
    messages = [
        {"role": "system", "content": system_prompt},
        *_format_chat_messages(messages)
    ]
    return await get_completion(messages, functions, temperature, max_tokens)
