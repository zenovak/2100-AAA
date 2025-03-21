from anthropic import AsyncAnthropic


async def claude_llm_completion(api_key, model, system, user, tokens, temperature):
    client = AsyncAnthropic(api_key=api_key)

    response = await client.messages.create(
        model=model,
        max_tokens=tokens,
        temperature=temperature,
        system=system,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user
                    }
                ]
            }
        ]
    )

    return response.content
