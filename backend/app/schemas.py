from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class TrainingResources(BaseModel):
    employee_training_folder_url: Optional[str] = ""
    project_training_folder_url: Optional[str] = ""
    skill_file_url: Optional[str] = ""
    instruction_file_url: Optional[str] = ""
    kb_folder_url: Optional[str] = ""

class PromptLogCreate(BaseModel):
    event_id: Optional[str] = None
    created_at: Optional[str] = None  # Expect ISO datetime string with offset
    employee_email: str
    machine_id: str
    project_name: Optional[str] = "Unknown"
    project_code: Optional[str] = "Unknown"
    workspace_folder: Optional[str] = ""
    session_id: Optional[str] = "Unknown"
    prompt: str
    prompt_hash: Optional[str] = None
    related_files: Optional[List[str]] = Field(default_factory=list)
    source_app: Optional[str] = "Claude Code"
    hook_event: Optional[str] = "UserPromptSubmit"
    training_resources: Optional[TrainingResources] = None

class PromptLogResponse(BaseModel):
    success: bool
    id: int
    event_id: str
