import uuid

from fastapi import FastAPI, BackgroundTasks, HTTPException
import httpx

from models.agent import Agent
from models.task import Task
from services.node_handler import handle_prompt_node, handle_return_node

app = FastAPI()

tasks = {

}


async def run_workflow(agent: Agent, task: Task):
    context = agent.variables

    for node in agent.promptChain:
        task.logs.append(f"{node.name}: Running")

        if node.type == "prompt":
            handle_prompt_node(node, context)

        if node.type == "return":
            data = handle_return_node(node, context)
            task.output = data
            return


@app.get('/')
async def root():
    return {"message": "Agent Engine Running"}


@app.get('/api/task')
async def execute(agent: Agent, background_task: BackgroundTasks):
    task = Task()
    task.id = uuid.uuid4().__str__()
    background_task.add_task(run_workflow, agent, task)
    tasks[task.id] = task

    return 201, task


@app.get('/api/task/{taskId}')
async def get_results(taskId):
    if taskId not in tasks:
        return 404, {"message": "task not found"}

    return tasks[taskId]
