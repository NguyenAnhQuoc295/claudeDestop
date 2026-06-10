import os
import uuid
import hashlib
import json
import datetime as dt
from typing import Optional, List, Dict
from fastapi import FastAPI, Depends, Request, Form, status, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from contextlib import asynccontextmanager

from app import config, models, schemas, auth
from app.database import engine, Base, get_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Automatically create tables on startup
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title=config.APP_NAME, lifespan=lifespan)

# Setup directories for static and templates
base_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(base_dir, "static")
templates_dir = os.path.join(base_dir, "templates")

# Ensure directories exist
os.makedirs(static_dir, exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# Helper to format datetime in templates
def format_datetime(value):
    if not value:
        return ""
    if isinstance(value, str):
        try:
            value = dt.datetime.fromisoformat(value)
        except ValueError:
            return value
    return value.strftime("%Y-%m-%d %H:%M:%S")

templates.env.filters["format_datetime"] = format_datetime

# ==========================================
# REST API Endpoints
# ==========================================

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/claude/prompt-log", response_model=schemas.PromptLogResponse)
def create_prompt_log(
    payload: schemas.PromptLogCreate,
    db: Session = Depends(get_db),
    api_key_valid = Depends(auth.verify_api_key)
):
    # 1. Deduplicate check
    if payload.event_id:
        existing = db.query(models.AIPromptLog).filter(models.AIPromptLog.event_id == payload.event_id).first()
        if existing:
            return schemas.PromptLogResponse(success=True, id=existing.id, event_id=existing.event_id)
    else:
        payload.event_id = str(uuid.uuid4())

    # 2. Parse created_at
    if payload.created_at:
        try:
            created_at = dt.datetime.fromisoformat(payload.created_at)
        except Exception:
            created_at = dt.datetime.now()
    else:
        created_at = dt.datetime.now()

    # 3. Calculate prompt hash
    prompt_hash = payload.prompt_hash
    if not prompt_hash:
        prompt_hash = hashlib.sha256(payload.prompt.encode("utf-8")).hexdigest()

    # 4. Handle related files and training resources
    related_files_json = json.dumps(payload.related_files or [])
    
    training_resources_json = None
    if payload.training_resources:
        tr_dict = payload.training_resources.dict()
        training_resources_json = json.dumps(tr_dict)

    # 5. Save to database
    db_log = models.AIPromptLog(
        event_id=payload.event_id,
        created_at=created_at,
        server_received_at=dt.datetime.now(),
        employee_email=payload.employee_email,
        machine_id=payload.machine_id,
        project_name=payload.project_name or "Unknown",
        project_code=payload.project_code or "Unknown",
        workspace_folder=payload.workspace_folder or "",
        session_id=payload.session_id or "Unknown",
        prompt=payload.prompt,
        prompt_hash=prompt_hash,
        related_files_json=related_files_json,
        source_app=payload.source_app or "Claude Code",
        hook_event=payload.hook_event or "UserPromptSubmit",
        training_resources_json=training_resources_json
    )
    
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    return schemas.PromptLogResponse(success=True, id=db_log.id, event_id=db_log.event_id)

@app.get("/api/claude/prompt-logs")
def list_prompt_logs(
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    employee_email: Optional[str] = Query(None),
    machine_id: Optional[str] = Query(None),
    project_code: Optional[str] = Query(None),
    project_name: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    limit: int = Query(50),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    query = db.query(models.AIPromptLog)

    if from_date:
        try:
            f_dt = dt.datetime.fromisoformat(from_date)
            query = query.filter(models.AIPromptLog.created_at >= f_dt)
        except Exception:
            pass
    if to_date:
        try:
            t_dt = dt.datetime.fromisoformat(to_date)
            query = query.filter(models.AIPromptLog.created_at <= t_dt)
        except Exception:
            pass
    if employee_email:
        query = query.filter(models.AIPromptLog.employee_email == employee_email)
    if machine_id:
        query = query.filter(models.AIPromptLog.machine_id == machine_id)
    if project_code:
        query = query.filter(models.AIPromptLog.project_code == project_code)
    if project_name:
        query = query.filter(models.AIPromptLog.project_name.like(f"%{project_name}%"))
    if keyword:
        query = query.filter(models.AIPromptLog.prompt.like(f"%{keyword}%"))

    total = query.count()
    items = query.order_by(models.AIPromptLog.created_at.desc()).offset(offset).limit(limit).all()

    # Format output items to include parsed json data
    out_items = []
    for item in items:
        tr_data = {}
        if item.training_resources_json:
            try:
                tr_data = json.loads(item.training_resources_json)
            except Exception:
                pass
        
        rel_files = []
        if item.related_files_json:
            try:
                rel_files = json.loads(item.related_files_json)
            except Exception:
                pass

        out_items.append({
            "id": item.id,
            "event_id": item.event_id,
            "created_at": item.created_at.isoformat(),
            "server_received_at": item.server_received_at.isoformat(),
            "employee_email": item.employee_email,
            "machine_id": item.machine_id,
            "project_name": item.project_name,
            "project_code": item.project_code,
            "workspace_folder": item.workspace_folder,
            "session_id": item.session_id,
            "prompt": item.prompt,
            "prompt_hash": item.prompt_hash,
            "related_files": rel_files,
            "source_app": item.source_app,
            "hook_event": item.hook_event,
            "training_resources": tr_data
        })

    return {
        "items": out_items,
        "total": total,
        "limit": limit,
        "offset": offset
    }

# ==========================================
# Dashboard Pages (Jinja2)
# ==========================================

@app.get("/", response_class=HTMLResponse)
def render_dashboard(
    request: Request,
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    employee_email: Optional[str] = Query(None),
    machine_id: Optional[str] = Query(None),
    project_code: Optional[str] = Query(None),
    project_name: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(models.AIPromptLog)

    # Apply filters
    if from_date:
        try:
            # Handle date input from HTML form (YYYY-MM-DD)
            f_dt = dt.datetime.strptime(from_date, "%Y-%m-%d")
            query = query.filter(models.AIPromptLog.created_at >= f_dt)
        except Exception:
            pass
    if to_date:
        try:
            # End of day filter (YYYY-MM-DD 23:59:59)
            t_dt = dt.datetime.strptime(to_date, "%Y-%m-%d") + dt.timedelta(days=1) - dt.timedelta(seconds=1)
            query = query.filter(models.AIPromptLog.created_at <= t_dt)
        except Exception:
            pass
    if employee_email and employee_email.strip():
        query = query.filter(models.AIPromptLog.employee_email.like(f"%{employee_email.strip()}%"))
    if machine_id and machine_id.strip():
        query = query.filter(models.AIPromptLog.machine_id.like(f"%{machine_id.strip()}%"))
    if project_code and project_code.strip():
        query = query.filter(models.AIPromptLog.project_code.like(f"%{project_code.strip()}%"))
    if project_name and project_name.strip():
        query = query.filter(models.AIPromptLog.project_name.like(f"%{project_name.strip()}%"))
    if keyword and keyword.strip():
        query = query.filter(models.AIPromptLog.prompt.like(f"%{keyword.strip()}%"))

    # Stats based on current filter
    total_prompts = query.count()
    
    unique_employees = query.with_entities(func.count(func.distinct(models.AIPromptLog.employee_email))).scalar() or 0
    unique_projects = query.with_entities(func.count(func.distinct(models.AIPromptLog.project_code))).scalar() or 0

    # Get records sorted by creation date descending
    records = query.order_by(models.AIPromptLog.created_at.desc()).all()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "records": records,
            "total_prompts": total_prompts,
            "unique_employees": unique_employees,
            "unique_projects": unique_projects,
            "filters": {
                "from_date": from_date or "",
                "to_date": to_date or "",
                "employee_email": employee_email or "",
                "machine_id": machine_id or "",
                "project_code": project_code or "",
                "project_name": project_name or "",
                "keyword": keyword or ""
            }
        }
    )

@app.get("/logs/{id}", response_class=HTMLResponse)
def render_log_detail(request: Request, id: int, db: Session = Depends(get_db)):
    record = db.query(models.AIPromptLog).filter(models.AIPromptLog.id == id).first()
    if not record:
        return HTMLResponse("<h1>Log not found</h1>", status_code=404)

    # Parse related files
    related_files = []
    if record.related_files_json:
        try:
            related_files = json.loads(record.related_files_json)
        except Exception:
            pass

    # Parse training resources
    training_resources = {}
    if record.training_resources_json:
        try:
            training_resources = json.loads(record.training_resources_json)
        except Exception:
            pass

    return templates.TemplateResponse(
        request=request,
        name="log_detail.html",
        context={
            "record": record,
            "related_files": related_files,
            "training_resources": training_resources
        }
    )
