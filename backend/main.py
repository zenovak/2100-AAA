import asyncio
import os
import uuid

from fastapi import FastAPI, BackgroundTasks, HTTPException
import httpx

from models.agent import Agent
from models.task import Task
from services.node_handler import handle_prompt_node, handle_return_node

from dotenv import load_dotenv


load_dotenv()
app = FastAPI(debug=True)

tasks = {}

FRONT_CALLBACK_URL = os.getenv("FRONT_CALLBACK_URL")


async def fire_webhook(task: Task):
    """
    Fires the webhook for alerting the frontend for updates
    :param task:
    :return:
    """

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                FRONT_CALLBACK_URL, 
                headers={
                    "Content-Type": "application/json"
                },
                params={
                    "taskId": task.id
                },
                json=task.model_dump_json()
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


async def run_workflow(agent: Agent, task: Task):
    context = agent.variables

    for node in agent.promptChain:
        task.logs.append(f"{node.name}: Running")
        task.logs.append("Data: " + str(context))

        if node.type == "prompt":
            await handle_prompt_node(node, context)

        if node.type == "return":
            data = handle_return_node(node, context)
            task.output = data
            return

        # Fire Notification asynchronously. without await to avoid stalling
        asyncio.create_task(fire_webhook(task))


@app.get('/')
async def root():
    return {"message": "Agent Engine Running"}


@app.post('/api/task')
async def execute(agent: Agent, background_task: BackgroundTasks) -> Task:
    task = Task(id=str(uuid.uuid4()))
    background_task.add_task(run_workflow, agent, task)
    tasks[task.id] = task

    return task


@app.get('/api/task/{taskId}')
async def get_results(taskId) -> Task:
    if taskId not in tasks:
        raise HTTPException(404, "Task Not found!")

    return tasks[taskId]


print(f"""
Confirming credentials:
 - FRONTEND_CALLBACK_URL={FRONT_CALLBACK_URL}
""")

# Run with
# uvicorn main:app --reload
