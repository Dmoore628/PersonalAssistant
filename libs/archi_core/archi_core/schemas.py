from pydantic import BaseModel, Field
from typing import Optional, List


class Health(BaseModel):
    service: str
    status: str


class TaskIn(BaseModel):
    title: str = Field(min_length=1)
    description: Optional[str] = None
    priority: Optional[int] = Field(default=3, ge=1, le=5)
    tags: List[str] = []


class PlanMessage(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    priority: int = 3
    tags: List[str] = []
    source: str = "planning"
