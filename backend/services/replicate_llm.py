import replicate


def get_model_format(model, system, user, tokens, temperature):
    input_map = {
        "google-deepmind/gemma-3-27b-it": {
            "model": "google-deepmind/gemma-3-27b-it:c0f0aebe8e578c15a7531e08a62cf01206f5870e9d0a67804b8152822db58c54",
            "input": {
                "prompt": user,
                "system_prompt": system,
                "temperature": temperature,
                "max_new_tokens": tokens,
            }
        }
    }

    return input_map[model]


async def replicate_llm_completion(api_key, model, system, user, tokens, temperature):
    client = replicate.Client(api_key=api_key)

    model_format = get_model_format(model, system, user, tokens, temperature)

    response = await client.async_run(
        model_format["model"],
        input=model_format["input"]
    )

    return response
