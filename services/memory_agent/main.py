import json
import time

from archi_core import Health, MessageBus, Settings, ContextData
from fastapi import FastAPI
from neo4j import GraphDatabase

settings = Settings()
app = FastAPI(title="Memory Agent")
bus = MessageBus(url=settings.rabbitmq_url)
driver = GraphDatabase.driver(
    settings.neo4j_url, auth=(settings.neo4j_user, settings.neo4j_password)
)


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
                SET t.title = $title, t.description = $description, t.priority = $priority, 
                    t.tags = $tags, t.created_at = datetime(), t.source = $source
                """,
                **data,
            )
        )


def _handle_memory_store(body: bytes):
    """Handle memory storage requests from other services"""
    data = json.loads(body)
    memory_type = data.get("type", "general")
    
    with driver.session() as session:
        if memory_type == "voice_interaction":
            # Store voice interaction
            session.execute_write(
                lambda tx: tx.run(
                    """
                    CREATE (vi:VoiceInteraction {
                        id: $id,
                        content: $content,
                        timestamp: datetime($timestamp),
                        user_id: $user_id,
                        metadata: $metadata
                    })
                    """,
                    id=str(time.time()),
                    content=data.get("content", ""),
                    timestamp=data.get("timestamp", time.time()),
                    user_id=data.get("user_id", "default"),
                    metadata=json.dumps(data.get("metadata", {}))
                )
            )
        
        elif memory_type == "system_action":
            # Store system action
            session.execute_write(
                lambda tx: tx.run(
                    """
                    CREATE (sa:SystemAction {
                        id: $id,
                        action: $action,
                        success: $success,
                        timestamp: datetime($timestamp),
                        parameters: $parameters
                    })
                    """,
                    id=data.get("execution_id", str(time.time())),
                    action=data.get("action", "unknown"),
                    success=data.get("success", False),
                    timestamp=time.time(),
                    parameters=json.dumps(data.get("parameters", {}))
                )
            )
        
        elif memory_type == "context_update":
            # Store context information
            session.execute_write(
                lambda tx: tx.run(
                    """
                    MERGE (c:Context {user_id: $user_id, session_id: $session_id})
                    SET c.active_application = $active_application,
                        c.current_task = $current_task,
                        c.role_context = $role_context,
                        c.updated_at = datetime(),
                        c.metadata = $metadata
                    """,
                    user_id=data.get("user_id", "default"),
                    session_id=data.get("session_id", "default"),
                    active_application=data.get("active_application"),
                    current_task=data.get("current_task"),
                    role_context=data.get("role_context"),
                    metadata=json.dumps(data.get("metadata", {}))
                )
            )


def _handle_task_progress(body: bytes):
    """Handle task progress updates"""
    data = json.loads(body)
    execution_id = data.get("execution_id")
    
    if execution_id:
        with driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    """
                    MATCH (sa:SystemAction {id: $execution_id})
                    SET sa.progress = $progress, sa.updated_at = datetime()
                    """,
                    execution_id=execution_id,
                    progress=data.get("progress", 0.0)
                )
            )


@app.on_event("startup")
def _startup():
    bus.consume_in_background("plan.created", _handle_plan_created)
    bus.consume_in_background("memory.store", _handle_memory_store)
    bus.consume_in_background("task.progress", _handle_task_progress)
