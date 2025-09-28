import uuid
from datetime import datetime, timezone

from archi_core import Health, MessageBus, PlanMessage, Settings, TaskIn
from fastapi import FastAPI, HTTPException

settings = Settings()
app = FastAPI(
    title="Archi Planning Agent",
    description="AI-powered task planning and workflow orchestration service",
    version="1.0.0",
)
bus = MessageBus(url=settings.rabbitmq_url)


@app.get("/health", response_model=Health)
def health():
    return Health(
        service=settings.service_name or "planning-agent",
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="1.0.0",
    )


@app.post("/plan", response_model=PlanMessage)
def create_plan(task: TaskIn) -> PlanMessage:
    """Create an execution plan for a given task."""
    try:
        # Generate basic task decomposition
        steps = decompose_task(task)
        estimated_duration = estimate_duration(task, steps)

        msg = PlanMessage(
            id=str(uuid.uuid4()),
            title=task.title,
            description=task.description,
            priority=task.priority or task.priority.MEDIUM,
            tags=task.tags,
            source="planning",
            steps=steps,
            estimated_duration=estimated_duration,
            requires_confirmation=requires_user_confirmation(task),
        )

        # Publish the plan to the message bus
        bus.publish(queue="plan.created", body=msg.model_dump_json().encode("utf-8"))
        return msg

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create plan: {e!s}") from e


@app.get("/plans/{plan_id}")
def get_plan(plan_id: str):
    """Retrieve a specific plan by ID."""
    # TODO: Implement plan storage and retrieval
    raise HTTPException(status_code=501, detail="Plan retrieval not yet implemented")


@app.post("/plans/{plan_id}/approve")
def approve_plan(plan_id: str):
    """Approve a plan for execution."""
    # TODO: Implement plan approval workflow
    raise HTTPException(status_code=501, detail="Plan approval not yet implemented")


def decompose_task(task: TaskIn) -> list[str]:
    """Break down a task into executable steps."""
    # Basic task decomposition logic
    # TODO: Integrate with LLM for intelligent task breakdown
    steps = []

    if "email" in task.title.lower():
        steps = [
            "Analyze email content requirements",
            "Identify recipients",
            "Compose email draft",
            "Review and send email",
        ]
    elif "file" in task.title.lower() or "document" in task.title.lower():
        steps = [
            "Locate target file/document",
            "Open appropriate application",
            "Perform requested operations",
            "Save changes",
        ]
    elif "schedule" in task.title.lower() or "calendar" in task.title.lower():
        steps = [
            "Check calendar availability",
            "Find suitable time slots",
            "Create calendar entry",
            "Send invitations if needed",
        ]
    else:
        # Generic task breakdown
        steps = [
            "Analyze task requirements",
            "Prepare necessary resources",
            "Execute primary task",
            "Verify completion",
        ]

    return steps


def estimate_duration(task: TaskIn, steps: list[str]) -> int:
    """Estimate task execution time in seconds."""
    base_duration = len(steps) * 30  # 30 seconds per step baseline

    # Adjust based on priority
    if task.priority == task.priority.CRITICAL:
        return base_duration  # No delay for critical tasks
    if task.priority == task.priority.HIGH:
        return int(base_duration * 1.2)
    if task.priority == task.priority.LOW:
        return int(base_duration * 1.5)

    return base_duration


def requires_user_confirmation(task: TaskIn) -> bool:
    """Determine if a task requires user confirmation before execution."""
    # High-risk operations that require confirmation
    risk_keywords = [
        "delete",
        "remove",
        "send",
        "publish",
        "transfer",
        "payment",
        "install",
        "uninstall",
    ]

    task_text = f"{task.title} {task.description or ''}".lower()
    return any(keyword in task_text for keyword in risk_keywords)
