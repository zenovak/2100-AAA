from typing import Literal, Union

from pydantic import BaseModel, Field


class Node(BaseModel):
    type: str
    name: str

    output: str
