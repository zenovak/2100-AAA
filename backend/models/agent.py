from typing import List, Union
from pydantic import BaseModel
from models.base_node import Node
from models.prompt_node import PromptNode
from models.return_node import ReturnNode


class Agent(BaseModel):
    name: str
    variables: dict
    promptChain: List[Union[PromptNode, ReturnNode]]

