from fastapi import FastAPI
from archi_core import Settings, Health, MessageBus
import json

settings = Settings()
app = FastAPI(title="Security Agent")
bus = MessageBus(url=settings.rabbitmq_url)

@app.get("/health", response_model=Health)
def health():
    return Health(service=settings.service_name or "security-agent", status="ok")


def _handle_security_event(body: bytes):
    data = json.loads(body)
    # Placeholder: process security events such as permission checks or threat detection
    _ = data


@app.on_event("startup")
def _startup():
    bus.consume_in_background("security.event", _handle_security_event)
