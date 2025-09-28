from fastapi import FastAPI
from pydantic import BaseModel
from neo4j import GraphDatabase

app = FastAPI(title="Knowledge Graph Service")

class Query(BaseModel):
    cypher: str

class Node(BaseModel):
    label: str
    properties: dict

class Relationship(BaseModel):
    start_node: str
    end_node: str
    type: str
    properties: dict

class GraphManager:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def run_query(self, cypher):
        with self.driver.session() as session:
            result = session.run(cypher)
            return [record.data() for record in result]

    def create_node(self, label, properties):
        with self.driver.session() as session:
            cypher = f"CREATE (n:{label} {{ {', '.join([f'{k}: ${k}' for k in properties.keys()])} }}) RETURN n"
            session.run(cypher, **properties)

    def create_relationship(self, start_node, end_node, rel_type, properties):
        with self.driver.session() as session:
            cypher = (
                f"MATCH (a), (b) WHERE id(a) = $start_id AND id(b) = $end_id "
                f"CREATE (a)-[r:{rel_type} {{ {', '.join([f'{k}: ${k}' for k in properties.keys()])} }}]->(b) RETURN r"
            )
            session.run(cypher, start_id=start_node, end_id=end_node, **properties)

# Initialize the graph manager
graph_manager = GraphManager(uri="bolt://localhost:7687", user="neo4j", password="neo4j_secret")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/query")
def query_graph(query: Query):
    try:
        result = graph_manager.run_query(query.cypher)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}

@app.post("/node")
def create_node(node: Node):
    try:
        graph_manager.create_node(node.label, node.properties)
        return {"message": "Node created successfully."}
    except Exception as e:
        return {"error": str(e)}

@app.post("/relationship")
def create_relationship(relationship: Relationship):
    try:
        graph_manager.create_relationship(
            relationship.start_node, relationship.end_node, relationship.type, relationship.properties
        )
        return {"message": "Relationship created successfully."}
    except Exception as e:
        return {"error": str(e)}