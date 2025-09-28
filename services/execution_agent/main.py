from fastapi import FastAPI
from archi_core import Settings, Health, MessageBus
import json

settings = Settings()
app = FastAPI(title="Execution Agent")
bus = MessageBus(url=settings.rabbitmq_url)

@app.get("/health", response_model=Health)
def health():
    return Health(service=settings.service_name or "execution-agent", status="ok")


def _handle_plan_created(body: bytes):
    data = json.loads(body)
    # Placeholder: react to new plan by scheduling a step, etc.
    _ = data


@app.on_event("startup")
def _startup():
    bus.consume_in_background("plan.created", _handle_plan_created)
