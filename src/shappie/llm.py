import inspect
import typing

import discord
import openai

import model


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

    return chat_messages


async def get_completion(
        messages: list[dict[str, str]],
        functions=None,
        temperature: float = 0.25,
        max_tokens: float = 500,
        model_id: str = "gpt-3.5-turbo-0613",
) -> dict[str, typing.Any]:
    if functions:
        response = await openai.ChatCompletion.acreate(
            model=model_id,
            messages=messages,
            functions=functions,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    else:
        try:
            response = await openai.ChatCompletion.acreate(
                model=model_id,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except openai.APIError:
            return dict(content="Sorry, my brian broke.")

    return response["choices"][0]["message"]


async def generate_response_message(
        messages: list[discord.Message],
        state: model.State,
        additional_context: str = "",
        functions=None,
        temperature: float = 0.25,
        max_tokens: float = 500,
        lookback=10,
) -> dict[str, typing.Any]:
    constitutions = []
    for constitution in state.constitutions:
        constitutions.extend(constitution.components)
    components = "\n".join(constitutions)
    system_prompt = inspect.cleandoc(f"""
    You are a discord bot. 
    You will be given the last {lookback} messages for context, 
    however you are responding to {messages[-1].author.display_name}. 
    You will see [User: <username>] for each message, but this is just for context. 
    Your imperatives are three-fold
    {components}

    Take on the following persona when responding to messages:
    """) + f"\n{state.persona.description}"
    if additional_context:
        system_prompt += f"\nAdditional Context:\n{additional_context}"
    messages = [
        {"role": "system", "content": system_prompt},
        *_format_chat_messages(messages)
    ]
    return await get_completion(messages, functions, temperature, max_tokens)
