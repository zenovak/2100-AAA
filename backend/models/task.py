from pydantic import BaseModel


class Task(BaseModel):
    id: str
    logs: list[str] = []
    output: dict = {}
