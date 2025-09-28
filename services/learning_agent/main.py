from fastapi import FastAPI
from archi_core import Settings, Health, MessageBus
import json

settings = Settings()
app = FastAPI(title="Learning Agent")
bus = MessageBus(url=settings.rabbitmq_url)

@app.get("/health", response_model=Health)
def health():
    return Health(service=settings.service_name or "learning-agent", status="ok")


def _handle_learning_task(body: bytes):
    data = json.loads(body)
    # Placeholder: process learning task
    _ = data


@app.on_event("startup")
def _startup():
    bus.consume_in_background("learning.task", _handle_learning_task)
