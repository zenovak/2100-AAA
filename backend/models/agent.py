from pydantic import BaseModel
from typing import List

from models.prompt_node import PromptNode


class Agent(BaseModel):
    name: str
    variables: dict
    promptChain: list

