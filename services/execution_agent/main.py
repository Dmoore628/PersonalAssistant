import json
import time
import uuid

from archi_core import Health, MessageBus, Settings, AgentMessage, AgentMessageType, ExecutionResult
from fastapi import FastAPI

settings = Settings()
app = FastAPI(title="Execution Agent")
bus = MessageBus(url=settings.rabbitmq_url)


@app.get("/health", response_model=Health)
def health():
    return Health(service=settings.service_name or "execution-agent", status="ok")


def _handle_plan_created(body: bytes):
    data = json.loads(body)
    # Enhanced plan handling with execution orchestration
    plan_id = data.get("id")
    title = data.get("title")
    
    # Create execution workflow
    execution_id = str(uuid.uuid4())
    
    # Send to CUA engine for execution if it's a system task
    if "system" in data.get("tags", []) or "automation" in data.get("tags", []):
        cua_message = {
            "action": "execute_workflow",
            "parameters": {
                "plan_id": plan_id,
                "title": title,
                "description": data.get("description"),
                "execution_id": execution_id
            },
            "source": "execution_agent"
        }
        bus.publish(queue="system.execute", body=json.dumps(cua_message).encode("utf-8"))
    
    # Send status update to HUD
    status_message = {
        "type": "task_progress",
        "title": f"Executing: {title}",
        "message": f"Started execution of plan: {plan_id}",
        "priority": data.get("priority", 3),
        "execution_id": execution_id
    }
    bus.publish(queue="system.notification", body=json.dumps(status_message).encode("utf-8"))


def _handle_system_result(body: bytes):
    """Handle results from system execution (CUA engine)"""
    data = json.loads(body)
    
    # Log execution result
    success = data.get("success", False)
    action = data.get("action", "unknown")
    
    # Update task progress
    progress_update = {
        "execution_id": data.get("execution_id"),
        "action": action,
        "success": success,
        "timestamp": time.time(),
        "progress": 1.0 if success else 0.0
    }
    bus.publish(queue="task.progress", body=json.dumps(progress_update).encode("utf-8"))
    
    # Send notification of completion
    notification = {
        "title": "Task Completed" if success else "Task Failed",
        "message": f"Action '{action}' {'completed successfully' if success else 'failed'}",
        "type": "success" if success else "error",
        "priority": 2 if success else 4
    }
    bus.publish(queue="system.notification", body=json.dumps(notification).encode("utf-8"))


@app.on_event("startup")
def _startup():
    bus.consume_in_background("plan.created", _handle_plan_created)
    bus.consume_in_background("system.result", _handle_system_result)
