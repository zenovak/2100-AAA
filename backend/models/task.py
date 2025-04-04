from pydantic import BaseModel


class Task(BaseModel):
    id: str
    logs: list[str] = []
    output: dict = {}
    status: str = "running"


    def set_running(self):
        self.status = "running"

    def set_complete(self):
        self.status = "complete"

    def set_error(self):
        self.status = "error"
    # status represents the task prediction status. is a string enum of
    # running, complete, error
