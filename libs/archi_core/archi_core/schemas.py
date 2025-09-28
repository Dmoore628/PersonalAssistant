from typing import Optional

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
