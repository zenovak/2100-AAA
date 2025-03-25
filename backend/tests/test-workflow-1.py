# An API call test targeted towards this backend service
# Simulates a typical agent workflow
import os

import requests


agent = {
    "name": "Movie agent",

    "variables": {
        "replicateAPI": os.getenv("REPLICATE_API"),
        "prompt": "Write a story about minecraft",
        "context": "",
        "genre": "Science fiction"
    },
    "promptChain": [
        {
            "type": "prompt",
            "name": "Sypnosis",

            "system": "You are a story development expert creating a synopsis for a {genre} film according to the user's request",
            "user": "{prompt}",
            "apikey": "{replicateAPI}",
            "llm": "replicate",
            "model": "google-deepmind/gemma-3-27b-it",
            "temperature": 1,
            "maxTokens": 2000,
            "output": "context",
        },
        {
            "type": "prompt",
            "name": "character dev",

            "system": "You are a character development specialist for {genre} films. Given the film's sypnosis enclosed in ### and the user's main request, \n Write the film's character development plans",
            "user": "### {context} ### {prompt}",
            "apikey": "{replicateAPI}",
            "llm": "replicate",
            "model": "google-deepmind/gemma-3-27b-it",
            "temperature": 1,
            "maxTokens": 2000,
            "output": "context",
        },
        {
            "name": "Return",
            "type": "return",
            "output": "context"
        }
    ]
}


def run():
    response = requests.post(
        "http://localhost:8000/api/task",
        headers={
            "Content-type": "application/json"
        },
        json=agent
    )

    print(response.json())
    return

run()

