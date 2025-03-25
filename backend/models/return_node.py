from typing import Literal

from models.base_node import Node


class ReturnNode(Node):
    type: Literal["return"] = "return"

    output: str
