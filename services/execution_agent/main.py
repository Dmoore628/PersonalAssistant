import json
from datetime import datetime, timezone
from typing import Any

from archi_core import CUAAction, ExecutionResult, Health, MessageBus, Settings, TaskStatus
from fastapi import FastAPI, HTTPException

settings = Settings()
app = FastAPI(
    title="Archi Execution Agent",
    description="Computer Use Agent for automated task execution",
    version="1.0.0",
)
bus = MessageBus(url=settings.rabbitmq_url)

# In-memory execution tracking
execution_registry: dict[str, ExecutionResult] = {}


@app.get("/health", response_model=Health)
def health():
    return Health(
        service=settings.service_name or "execution-agent",
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="1.0.0",
    )


@app.post("/execute", response_model=ExecutionResult)
def execute_task(task_id: str, actions: list[CUAAction]):
    """Execute a series of Computer Use Agent actions."""
    try:
        start_time = datetime.now()
        execution_result = ExecutionResult(
            task_id=task_id,
            status=TaskStatus.RUNNING,
            logs=[f"Started execution at {start_time.isoformat()}"],
        )

        execution_registry[task_id] = execution_result

        # Execute each action in sequence
        for i, action in enumerate(actions):
            try:
                step_result = execute_cua_action(action)
                execution_result.logs.append(
                    f"Step {i+1}: {action.action_type} on {action.target} - {step_result}"
                )
            except Exception as e:
                execution_result.status = TaskStatus.FAILED
                execution_result.error_message = f"Failed at step {i+1}: {e!s}"
                execution_result.logs.append(f"Error in step {i+1}: {e!s}")
                break

        # Calculate execution time
        end_time = datetime.now()
        execution_result.execution_time = (end_time - start_time).total_seconds()

        # Update final status
        if execution_result.status != TaskStatus.FAILED:
            execution_result.status = TaskStatus.COMPLETED
            execution_result.logs.append(f"Completed successfully at {end_time.isoformat()}")

        # Publish completion event
        bus.publish(
            queue="execution.completed",
            body=execution_result.model_dump_json().encode("utf-8"),
        )

        return execution_result

    except Exception as e:
        error_result = ExecutionResult(
            task_id=task_id,
            status=TaskStatus.FAILED,
            error_message=str(e),
            logs=[f"Execution failed: {e!s}"],
        )
        execution_registry[task_id] = error_result
        raise HTTPException(status_code=500, detail=f"Execution failed: {e!s}") from e


@app.get("/execution/{task_id}", response_model=ExecutionResult)
def get_execution_status(task_id: str):
    """Get the status of a task execution."""
    if task_id not in execution_registry:
        raise HTTPException(status_code=404, detail="Task execution not found")
    return execution_registry[task_id]


@app.post("/actions/validate")
def validate_action(action: CUAAction) -> dict[str, Any]:
    """Validate a CUA action before execution."""
    validation_result = {
        "valid": True,
        "warnings": [],
        "risks": [],
        "requires_confirmation": action.confirmation_required,
    }

    # Safety checks
    if action.safety_check and not settings.cua_safety_mode:
        validation_result["warnings"].append("Safety mode is disabled")

    if action.action_type in ["delete", "remove", "uninstall"]:
        validation_result["risks"].append("Destructive action detected")
        validation_result["requires_confirmation"] = True

    if "system32" in action.target.lower() or "program files" in action.target.lower():
        validation_result["risks"].append("System-level operation detected")
        validation_result["requires_confirmation"] = True

    return validation_result


def execute_cua_action(action: CUAAction) -> str:
    """Execute a single Computer Use Agent action."""
    # This is a placeholder implementation
    # In a real implementation, this would interface with:
    # - Windows APIs for UI automation
    # - Screen capture and computer vision
    # - Application-specific APIs
    # - Input simulation

    if not settings.cua_safety_mode and action.safety_check:
        raise Exception("Action blocked by safety mode")

    action_type = action.action_type.lower()

    if action_type == "click":
        return f"Clicked on {action.target}"
    if action_type == "type":
        text = action.parameters.get("text", "")
        return f"Typed '{text}' into {action.target}"
    if action_type == "scroll":
        direction = action.parameters.get("direction", "down")
        return f"Scrolled {direction} in {action.target}"
    if action_type == "wait":
        duration = action.parameters.get("duration", 1)
        return f"Waited {duration} seconds"
    if action_type == "screenshot":
        return f"Captured screenshot of {action.target}"
    if action_type == "read_text":
        return f"Read text from {action.target}"
    return f"Executed {action_type} action on {action.target}"


@app.post("/emergency_stop")
def emergency_stop():
    """Emergency stop all running executions."""
    # In a real implementation, this would:
    # - Stop all running automation processes
    # - Cancel pending actions
    # - Return system to safe state

    stopped_tasks = []
    for task_id, result in execution_registry.items():
        if result.status == TaskStatus.RUNNING:
            result.status = TaskStatus.CANCELLED
            result.logs.append("Emergency stop activated")
            stopped_tasks.append(task_id)

    return {"message": f"Stopped {len(stopped_tasks)} running tasks", "tasks": stopped_tasks}


def _handle_plan_created(body: bytes):
    data = json.loads(body)
    # Placeholder: react to new plan by scheduling a step, etc.
    _ = data


@app.on_event("startup")
def _startup():
    bus.consume_in_background("plan.created", _handle_plan_created)
