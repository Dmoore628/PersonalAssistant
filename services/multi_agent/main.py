from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
import asyncio

app = FastAPI(title="Multi-Agent Orchestration")

class TaskRequest(BaseModel):
    task: str
    context: Dict[str, Any]

class Agent:
    def __init__(self, name):
        self.name = name

    async def perform_task(self, task: str, context: Dict[str, Any]):
        await asyncio.sleep(1)  # Simulate task execution
        return {"agent": self.name, "task": task, "status": "completed", "context": context}

# Initialize agents
agents = {
    "planner": Agent("Planner"),
    "executor": Agent("Executor"),
    "memory": Agent("Memory"),
    "security": Agent("Security"),
    "tool_creator": Agent("Tool Creator"),
    "learner": Agent("Learner"),
}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/task")
async def handle_task(request: TaskRequest):
    try:
        # Example: Route task to the appropriate agent
        if "plan" in request.task.lower():
            agent = agents["planner"]
        elif "execute" in request.task.lower():
            agent = agents["executor"]
        elif "memory" in request.task.lower():
            agent = agents["memory"]
        elif "security" in request.task.lower():
            agent = agents["security"]
        elif "tool" in request.task.lower():
            agent = agents["tool_creator"]
        elif "learn" in request.task.lower():
            agent = agents["learner"]
        else:
            return {"error": "No suitable agent found for the task."}

        result = await agent.perform_task(request.task, request.context)
        return result

    except Exception as e:
        return {"error": str(e)}