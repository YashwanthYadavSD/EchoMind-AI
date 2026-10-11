from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TaskBase(BaseModel):
    task: str
    completed: bool = False
    due_date: Optional[datetime] = None
    priority: str = "normal"

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    task: Optional[str] = None
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = None

class TaskOut(TaskBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ReminderBase(BaseModel):
    message: str
    reminder_time: datetime
    completed: bool = False

class ReminderCreate(ReminderBase):
    pass

class ReminderUpdate(BaseModel):
    message: Optional[str] = None
    reminder_time: Optional[datetime] = None
    completed: Optional[bool] = None

class ReminderOut(ReminderBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    response: str
    intent: str = "UNKNOWN"
