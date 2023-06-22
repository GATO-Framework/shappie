import openai

import bot.persona


async def generate_response_message(
        messages: list[dict[str, str]],
        persona: bot.persona
) -> str:
    messages.insert(0, {"role": "system", "content": persona})
    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        # functions=[],
        temperature=0.25,
        max_tokens=250,
    )

    return response["choices"][0]["message"]["content"]
