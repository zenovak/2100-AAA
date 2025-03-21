from pydantic import BaseModel


class PromptNode(BaseModel):
    type: str
    name: str

    system: str
    user: str

    llm: str
    apiKey: str
    temperature: int
    model: str
    maxTokens: str

    output: str
