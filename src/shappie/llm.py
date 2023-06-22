import openai


async def generate_response_message(message: str, persona: str) -> str:
    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo-0613",
        messages=[
            {"role": "system", "content": persona},
            {"role": "user", "content": message}
        ],
        # functions=[],
        temperature=0.25,
        max_tokens=250,
    )

    return response["choices"][0]["message"]["content"]
