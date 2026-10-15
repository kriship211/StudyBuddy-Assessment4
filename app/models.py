"""Strict contracts for HTTP requests and every agent handoff."""
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, model_validator

class StrictModel(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)

class AgentRequest(StrictModel):
    message: str = Field(min_length=3, max_length=500)
    mode: Literal['local', 'gemini'] = 'local'
    scenario: Literal['normal', 'timeout', 'invalid_output', 'invalid_receiver', 'loop'] = 'normal'
    max_steps: int = Field(default=4, ge=1, le=8)
    timeout_seconds: float = Field(default=10, ge=0.05, le=30)

class Plan(StrictModel):
    action: Literal['lookup_task', 'summarise_tasks', 'classify_priority', 'general']
    task_id: int | None = Field(default=None, ge=1)
    title: str = Field(default='Requested task', min_length=1, max_length=500)
    due_in_days: int | None = Field(default=None, ge=0, le=36500)
    blocking: bool = False
    clarification: str = Field(default='', max_length=500)

    @model_validator(mode='after')
    def required_arguments(self):
        if self.action == 'lookup_task' and self.task_id is None:
            raise ValueError('lookup_task requires task_id')
        if self.action == 'classify_priority' and self.due_in_days is None:
            raise ValueError('classify_priority requires due_in_days')
        return self

class Result(StrictModel):
    answer: str = Field(min_length=1, max_length=4000)
    action: Literal['lookup_task', 'summarise_tasks', 'classify_priority', 'general', 'fallback']
    used_tool: str | None = None

class Message(StrictModel):
    run_id: UUID
    step: int = Field(ge=1, le=8)
    sender: Literal['orchestrator', 'planner', 'worker']
    receiver: str = Field(min_length=1, max_length=30)
    intent: Literal['plan', 'execute', 'result']
    content: dict
    constraints: dict = Field(default_factory=lambda: {'format': 'json', 'read_only': True})

class AgentResponse(StrictModel):
    run_id: UUID
    status: Literal['completed', 'fallback']
    mode: str
    result: Result
    steps: int
    events: list[dict]
