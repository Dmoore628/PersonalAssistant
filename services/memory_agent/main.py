from fastapi import FastAPI
from archi_core import Settings, Health, MessageBus
from neo4j import GraphDatabase
import json

settings = Settings()
app = FastAPI(title="Memory Agent")
bus = MessageBus(url=settings.rabbitmq_url)
driver = GraphDatabase.driver(settings.neo4j_url, auth=(settings.neo4j_user, settings.neo4j_password))

@app.get("/health", response_model=Health)
def health():
    return Health(service=settings.service_name or "memory-agent", status="ok")


def _handle_plan_created(body: bytes):
    data = json.loads(body)
    with driver.session() as session:
        session.execute_write(
            lambda tx: tx.run(
                """
                MERGE (t:Task {id: $id})
                SET t.title = $title, t.description = $description, t.priority = $priority, t.tags = $tags
                """,
                **data,
            )
        )


@app.on_event("startup")
def _startup():
    bus.consume_in_background("plan.created", _handle_plan_created)
