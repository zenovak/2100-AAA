from pydantic import BaseModel


class ReturnNode(BaseModel):
    type: str

    output: list[str]
