from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Service Configuration
    service_name: str = "archi-service"
    log_level: str = "INFO"

    # RabbitMQ Configuration
    rabbitmq_url: str = "amqp://archi:archi_secret@rabbitmq:5672/"
    rabbitmq_user: str = "archi"
    rabbitmq_password: str = "archi_secret"

    # Neo4j Configuration
    neo4j_url: str = "bolt://neo4j:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "neo4j_secret"

    # AI Service Configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_key: Optional[str] = None

    # Voice Processing Configuration
    wake_word_model_path: str = "./models/wake-word.pv"
    speech_recognition_provider: str = "azure"
    voice_synthesis_provider: str = "azure"

    # Computer Use Agent Configuration
    screen_capture_fps: int = Field(default=30, ge=1, le=60)
    cua_safety_mode: bool = True
    cua_confirmation_required: bool = True

    # Security Configuration
    encryption_key_path: str = "./keys/encryption.key"
    credential_store_type: str = "windows"
    audit_log_retention_days: int = Field(default=90, ge=1)

    # Windows Integration
    hud_overlay_enabled: bool = True
    hud_transparency: float = Field(default=0.8, ge=0.0, le=1.0)
    hud_position: str = "top-right"

    # Performance Configuration
    max_concurrent_tasks: int = Field(default=10, ge=1, le=100)
    knowledge_graph_cache_size: int = Field(default=1024, ge=64)
    voice_buffer_seconds: int = Field(default=5, ge=1, le=60)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
