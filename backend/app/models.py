from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from app.database import Base

class AIPromptLog(Base):
    __tablename__ = "ai_prompt_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(64), unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False)
    server_received_at = Column(DateTime, nullable=False)
    employee_email = Column(String(255), nullable=False)
    machine_id = Column(String(255), nullable=False)
    project_name = Column(String(255), nullable=True)
    project_code = Column(String(100), nullable=True)
    workspace_folder = Column(Text, nullable=True)
    session_id = Column(String(255), nullable=True)
    prompt = Column(Text, nullable=False)
    prompt_hash = Column(String(128), nullable=False)
    related_files_json = Column(Text, nullable=True)  # Holds JSON list of related files
    source_app = Column(String(100), nullable=True)
    hook_event = Column(String(100), nullable=True)
    training_resources_json = Column(Text, nullable=True)  # Holds JSON training resource URLs

    # Indexes as required by the specification
    __table_args__ = (
        Index("idx_ai_prompt_log_created_at", "created_at"),
        Index("idx_ai_prompt_log_employee_email", "employee_email"),
        Index("idx_ai_prompt_log_project_code", "project_code"),
        Index("idx_ai_prompt_log_machine_id", "machine_id"),
        Index("idx_ai_prompt_log_prompt_hash", "prompt_hash"),
    )
