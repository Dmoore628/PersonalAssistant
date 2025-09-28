from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class Health(BaseModel):
    service: str
    status: str
    timestamp: Optional[str] = None
    version: Optional[str] = None


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(int, Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    MINIMAL = 5


class TaskIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    tags: list[str] = Field(default_factory=list, max_items=10)
    context: Optional[dict[str, Any]] = None
    due_date: Optional[str] = None
    user_role: Optional[str] = None


class TaskOut(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    tags: list[str] = Field(default_factory=list)
    context: Optional[dict[str, Any]] = None
    created_at: str
    updated_at: Optional[str] = None
    due_date: Optional[str] = None
    user_role: Optional[str] = None


class PlanMessage(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    tags: list[str] = Field(default_factory=list)
    source: str = "planning"
    steps: list[str] = Field(default_factory=list)
    estimated_duration: Optional[int] = None  # seconds
    requires_confirmation: bool = False


class ExecutionResult(BaseModel):
    task_id: str
    status: TaskStatus
    result: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None  # seconds
    logs: list[str] = Field(default_factory=list)


class VoiceCommand(BaseModel):
    audio_data: Optional[str] = None  # base64 encoded
    text: Optional[str] = None
    context: dict[str, Any] = Field(default_factory=dict)
    confidence: Optional[float] = None
    language: str = "en-US"


class CUAAction(BaseModel):
    action_type: str  # click, type, scroll, etc.
    target: str  # element identifier or coordinates
    parameters: dict[str, Any] = Field(default_factory=dict)
    confirmation_required: bool = True
    safety_check: bool = True


class MemoryNode(BaseModel):
    id: str
    type: str  # person, task, document, etc.
    properties: dict[str, Any] = Field(default_factory=dict)
    context_roles: list[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    created_at: str
    updated_at: Optional[str] = None


class SecurityAuditLog(BaseModel):
    id: str
    event_type: str
    user_role: Optional[str] = None
    action: str
    resource: Optional[str] = None
    result: str  # success, failure, blocked
    risk_level: str  # low, medium, high, critical
    timestamp: str
    details: Optional[dict[str, Any]] = None


class ToolCreationRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=500)
    parameters: dict[str, Any] = Field(default_factory=dict)
    template_type: str = "script"  # script, automation, integration
    target_application: Optional[str] = None
    safety_level: str = "medium"  # low, medium, high


class LearningFeedback(BaseModel):
    task_id: str
    feedback_type: str  # positive, negative, correction
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None
    context: dict[str, Any] = Field(default_factory=dict)
    user_role: Optional[str] = None
    timestamp: str
