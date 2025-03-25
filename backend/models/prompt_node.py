from typing import Literal

from models.base_node import Node


class PromptNode(Node):
    type: Literal["prompt"] = "prompt"

    name: str

    system: str
    user: str

    llm: str
    apikey: str
    temperature: int
    model: str
    maxTokens: int

    output: str
