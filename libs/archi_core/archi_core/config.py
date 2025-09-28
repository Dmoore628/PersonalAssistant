from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    service_name: str = "service"
    rabbitmq_url: str = "amqp://archi:archi_secret@rabbitmq:5672/"
    neo4j_url: str = "bolt://neo4j:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "neo4j_secret"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
