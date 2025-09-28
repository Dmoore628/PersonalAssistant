import json
from datetime import datetime, timezone
from typing import Optional

from archi_core import Health, MemoryNode, MessageBus, Settings, logger
from fastapi import FastAPI, HTTPException
from neo4j import GraphDatabase

settings = Settings()
app = FastAPI(
    title="Archi Memory Agent",
    description="Knowledge graph and contextual memory management service",
    version="1.0.0",
)
bus = MessageBus(url=settings.rabbitmq_url)

# Neo4j connection
try:
    driver = GraphDatabase.driver(
        settings.neo4j_url, auth=(settings.neo4j_user, settings.neo4j_password)
    )
except Exception as e:
    driver = None
    logger.warning(f"Neo4j connection failed: {e}")


@app.get("/health", response_model=Health)
def health():
    status = "healthy" if driver else "degraded"
    return Health(
        service=settings.service_name or "memory-agent",
        status=status,
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="1.0.0",
    )


@app.post("/memory/store", response_model=MemoryNode)
def store_memory(node: MemoryNode):
    """Store a memory node in the knowledge graph."""
    if not driver:
        raise HTTPException(status_code=503, detail="Knowledge graph database unavailable")

    try:
        with driver.session() as session:
            # Create or update the memory node
            query = """
            MERGE (n:Memory {id: $id})
            SET n.type = $type,
                n.properties = $properties,
                n.context_roles = $context_roles,
                n.confidence = $confidence,
                n.created_at = $created_at,
                n.updated_at = $updated_at
            RETURN n
            """

            session.run(
                query,
                {
                    "id": node.id,
                    "type": node.type,
                    "properties": json.dumps(node.properties),
                    "context_roles": node.context_roles,
                    "confidence": node.confidence,
                    "created_at": node.created_at,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
            )

            # Publish memory creation event
            bus.publish(queue="memory.stored", body=node.model_dump_json().encode("utf-8"))

            return node

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store memory: {e!s}") from e


@app.get("/memory/{node_id}", response_model=MemoryNode)
def get_memory(node_id: str):
    """Retrieve a specific memory node."""
    if not driver:
        raise HTTPException(status_code=503, detail="Knowledge graph database unavailable")

    try:
        with driver.session() as session:
            query = "MATCH (n:Memory {id: $id}) RETURN n"
            result = session.run(query, {"id": node_id})
            record = result.single()

            if not record:
                raise HTTPException(status_code=404, detail="Memory node not found")

            node_data = record["n"]
            return MemoryNode(
                id=node_data["id"],
                type=node_data["type"],
                properties=json.loads(node_data.get("properties", "{}")),
                context_roles=node_data.get("context_roles", []),
                confidence=node_data.get("confidence", 1.0),
                created_at=node_data["created_at"],
                updated_at=node_data.get("updated_at"),
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve memory: {e!s}") from e


@app.get("/memory/search")
def search_memories(
    query: str,
    context_role: Optional[str] = None,
    memory_type: Optional[str] = None,
    limit: int = 10,
):
    """Search memories using text and filters."""
    if not driver:
        raise HTTPException(status_code=503, detail="Knowledge graph database unavailable")

    try:
        with driver.session() as session:
            # Build dynamic query based on filters
            cypher_query = "MATCH (n:Memory) WHERE "
            params = {"query": query, "limit": limit}
            conditions = []

            # Text search in properties
            conditions.append(
                "ANY(key IN keys(n.properties) WHERE toString(n.properties[key]) CONTAINS $query)"
            )

            if context_role:
                conditions.append("$context_role IN n.context_roles")
                params["context_role"] = context_role

            if memory_type:
                conditions.append("n.type = $memory_type")
                params["memory_type"] = memory_type

            cypher_query += " AND ".join(conditions)
            cypher_query += " RETURN n ORDER BY n.confidence DESC, n.updated_at DESC LIMIT $limit"

            result = session.run(cypher_query, params)

            memories = []
            for record in result:
                node_data = record["n"]
                memories.append(
                    {
                        "id": node_data["id"],
                        "type": node_data["type"],
                        "properties": json.loads(node_data.get("properties", "{}")),
                        "context_roles": node_data.get("context_roles", []),
                        "confidence": node_data.get("confidence", 1.0),
                        "created_at": node_data["created_at"],
                        "updated_at": node_data.get("updated_at"),
                    }
                )

            return {"memories": memories, "count": len(memories)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {e!s}") from e


@app.post("/memory/relate")
def create_relationship(
    from_id: str, to_id: str, relationship_type: str, properties: Optional[dict] = None
):
    """Create a relationship between two memory nodes."""
    if not driver:
        raise HTTPException(status_code=503, detail="Knowledge graph database unavailable")

    try:
        with driver.session() as session:
            query = f"""
            MATCH (from:Memory {{id: $from_id}}), (to:Memory {{id: $to_id}})
            MERGE (from)-[r:{relationship_type}]->(to)
            SET r.created_at = $created_at
            """

            if properties:
                query += ", r.properties = $properties"

            query += " RETURN r"

            params = {
                "from_id": from_id,
                "to_id": to_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            if properties:
                params["properties"] = json.dumps(properties)

            session.run(query, params)

            return {"message": "Relationship created successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create relationship: {e!s}") from e


@app.get("/memory/context/{role}")
def get_context_memories(role: str, limit: int = 20):
    """Get memories relevant to a specific user role/context."""
    if not driver:
        raise HTTPException(status_code=503, detail="Knowledge graph database unavailable")

    try:
        with driver.session() as session:
            query = """
            MATCH (n:Memory) 
            WHERE $role IN n.context_roles 
            RETURN n 
            ORDER BY n.confidence DESC, n.updated_at DESC 
            LIMIT $limit
            """

            result = session.run(query, {"role": role, "limit": limit})

            memories = []
            for record in result:
                node_data = record["n"]
                memories.append(
                    {
                        "id": node_data["id"],
                        "type": node_data["type"],
                        "properties": json.loads(node_data.get("properties", "{}")),
                        "context_roles": node_data.get("context_roles", []),
                        "confidence": node_data.get("confidence", 1.0),
                        "created_at": node_data["created_at"],
                        "updated_at": node_data.get("updated_at"),
                    }
                )

            return {"role": role, "memories": memories, "count": len(memories)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Context retrieval failed: {e!s}") from e


def _handle_plan_created(body: bytes):
    """Handle plan creation events and store in knowledge graph."""
    try:
        data = json.loads(body)
        if driver:
            with driver.session() as session:
                session.execute_write(
                    lambda tx: tx.run(
                        """
                        MERGE (t:Task {id: $id})
                        SET t.title = $title, 
                            t.description = $description, 
                            t.priority = $priority, 
                            t.tags = $tags,
                            t.source = $source,
                            t.created_at = $created_at
                        """,
                        created_at=datetime.now(timezone.utc).isoformat(),
                        **data,
                    )
                )
    except Exception as e:
        logger.error(f"Failed to handle plan creation: {e}")


@app.on_event("startup")
def _startup():
    """Initialize message bus consumers."""
    bus.consume_in_background("plan.created", _handle_plan_created)


@app.on_event("shutdown")
def shutdown_event():
    """Clean up database connections on shutdown."""
    if driver:
        driver.close()
