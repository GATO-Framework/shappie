import openai


async def generate_response_message(message: str, persona: str) -> str:
    # Generate a response with OpenAI
    chat_completion = openai.ChatCompletion(
        model="gpt-3.5-turbo-0613",
        messages=[
            {"role": "system", "content": persona},
            {"role": "user", "content": message}
        ],
        # functions=[],
        temperature=0.25,
        max_tokens=250,
    )

    response = await chat_completion.acreate()
    return response["choices"][0]["message"]["content"]
