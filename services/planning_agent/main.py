from fastapi import FastAPI
from archi_core import Settings, Health, MessageBus
from archi_core.schemas import TaskIn, PlanMessage
import uuid

settings = Settings()
app = FastAPI(title="Planning Agent")
bus = MessageBus(url=settings.rabbitmq_url)

@app.get("/health", response_model=Health)
def health():
    return Health(service=settings.service_name or "planning-agent", status="ok")


@app.post("/plan", response_model=PlanMessage)
def create_plan(task: TaskIn) -> PlanMessage:
    msg = PlanMessage(
        id=str(uuid.uuid4()),
        title=task.title,
        description=task.description,
        priority=task.priority or 3,
        tags=task.tags,
        source="planning",
    )
    bus.publish(queue="plan.created", body=msg.model_dump_json().encode("utf-8"))
    return msg
