from typing import Optional, Dict, Any, List
from enum import Enum

from pydantic import BaseModel, Field


class Health(BaseModel):
    service: str
    status: str


class TaskIn(BaseModel):
    title: str = Field(min_length=1)
    description: Optional[str] = None
    priority: Optional[int] = Field(default=3, ge=1, le=5)
    tags: list[str] = []


class PlanMessage(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    priority: int = 3
    tags: list[str] = []
    source: str = "planning"


class AgentMessageType(str, Enum):
    """Types of messages between agents"""
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    CONTEXT_UPDATE = "context_update"
    ERROR_NOTIFICATION = "error_notification"
    LEARNING_UPDATE = "learning_update"
    SYSTEM_STATUS = "system_status"


class AgentMessage(BaseModel):
    """Standard message format for inter-agent communication"""
    sender_id: str
    receiver_id: str
    message_type: AgentMessageType
    payload: Dict[str, Any]
    priority: int = Field(default=1, ge=1, le=5)
    timestamp: float
    correlation_id: str
    requires_response: bool = False


class ContextData(BaseModel):
    """Context information for agents"""
    user_id: str = "default"
    active_application: Optional[str] = None
    current_task: Optional[str] = None
    role_context: Optional[str] = None
    session_id: str
    metadata: Dict[str, Any] = {}


class SystemStatus(BaseModel):
    """System status information"""
    active_context: str
    system_status: str
    cpu_usage: float
    memory_usage: float
    gpu_usage: float
    active_agents: List[str] = []
    current_task: Optional[str] = None
    task_progress: Optional[float] = None


class WorkflowStep(BaseModel):
    """Individual step in a workflow"""
    id: str
    action: str
    parameters: Dict[str, Any]
    dependencies: List[str] = []
    timeout: int = 30
    retry_policy: Dict[str, Any] = {"max_retries": 3, "retry_delay": 1}


class WorkflowDefinition(BaseModel):
    """Complete workflow definition"""
    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    metadata: Dict[str, Any] = {}
    created_by: str = "system"


class ExecutionResult(BaseModel):
    """Result of workflow or action execution"""
    success: bool
    execution_id: str
    result_data: Dict[str, Any] = {}
    error_message: Optional[str] = None
    execution_time: float
    step_results: List[Dict[str, Any]] = []
