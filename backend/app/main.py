import datetime as dt
import hashlib
import json
import os
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app import auth, config, models, schemas
from app.database import Base, engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=config.APP_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIST_DIR = Path(
    os.getenv("DASHBOARD_DIST_DIR")
    or Path(__file__).resolve().parents[2] / "dashboard-ui" / "dist"
)
FRONTEND_INDEX = FRONTEND_DIST_DIR / "index.html"
FRONTEND_ASSETS_DIR = FRONTEND_DIST_DIR / "assets"

if FRONTEND_ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_ASSETS_DIR), name="dashboard-assets")


def normalize_claude_area(value):
    value = (value or "").strip().lower()
    if value in {"chat", "cowork", "code"}:
        return value
    return ""


def apply_prompt_filters(
    query,
    from_date=None,
    to_date=None,
    employee_email=None,
    machine_id=None,
    project_code=None,
    project_name=None,
    keyword=None,
    claude_area=None,
):
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
    if employee_email and employee_email.strip():
        query = query.filter(models.AIPromptLog.employee_email.like(f"%{employee_email.strip()}%"))
    if machine_id and machine_id.strip():
        query = query.filter(models.AIPromptLog.machine_id.like(f"%{machine_id.strip()}%"))
    if project_code and project_code.strip():
        query = query.filter(models.AIPromptLog.project_code.like(f"%{project_code.strip()}%"))
    if project_name and project_name.strip():
        query = query.filter(models.AIPromptLog.project_name.like(f"%{project_name.strip()}%"))
    area = normalize_claude_area(claude_area)
    if area:
        prefix = f"{area.upper()}-"
        source_label = area.capitalize()
        query = query.filter(
            or_(
                models.AIPromptLog.project_code.like(f"{prefix}%"),
                models.AIPromptLog.source_app.like(f"%{source_label}%"),
            )
        )
    if keyword and keyword.strip():
        query = query.filter(models.AIPromptLog.prompt.like(f"%{keyword.strip()}%"))
    return query


def classify_source_app(source_app: str) -> str:
    value = (source_app or "").strip().lower()
    if "cowork" in value:
        return "cowork"
    if "chat" in value:
        return "chat"
    return "code"


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/claude/prompt-log", response_model=schemas.PromptLogResponse)
def create_prompt_log(
    payload: schemas.PromptLogCreate,
    db: Session = Depends(get_db),
    api_key_valid=Depends(auth.verify_api_key),
):
    if payload.event_id:
        existing = db.query(models.AIPromptLog).filter(models.AIPromptLog.event_id == payload.event_id).first()
        if existing:
            return schemas.PromptLogResponse(success=True, id=existing.id, event_id=existing.event_id)
    else:
        payload.event_id = str(uuid.uuid4())

    if payload.created_at:
        try:
            created_at = dt.datetime.fromisoformat(payload.created_at)
        except Exception:
            created_at = dt.datetime.now()
    else:
        created_at = dt.datetime.now()

    prompt_hash = payload.prompt_hash or hashlib.sha256(payload.prompt.encode("utf-8")).hexdigest()
    related_files_json = json.dumps(payload.related_files or [])

    training_resources_json = None
    if payload.training_resources:
        training_resources_json = json.dumps(payload.training_resources.dict())

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
        training_resources_json=training_resources_json,
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
    claude_area: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    limit: int = Query(50),
    offset: int = Query(0),
    db: Session = Depends(get_db),
):
    query = db.query(models.AIPromptLog)
    query = apply_prompt_filters(
        query,
        from_date=from_date,
        to_date=to_date,
        employee_email=employee_email,
        machine_id=machine_id,
        project_code=project_code,
        project_name=project_name,
        keyword=keyword,
        claude_area=claude_area,
    )

    total = query.count()
    items = query.order_by(models.AIPromptLog.created_at.desc()).offset(offset).limit(limit).all()

    out_items = []
    for item in items:
        training_resources = {}
        if item.training_resources_json:
            try:
                training_resources = json.loads(item.training_resources_json)
            except Exception:
                pass

        related_files = []
        if item.related_files_json:
            try:
                related_files = json.loads(item.related_files_json)
            except Exception:
                pass

        out_items.append(
            {
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
                "related_files": related_files,
                "source_app": item.source_app,
                "hook_event": item.hook_event,
                "training_resources": training_resources,
            }
        )

    return {
        "items": out_items,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@app.get("/api/dashboard/summary")
def dashboard_summary(
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(models.AIPromptLog)
    query = apply_prompt_filters(query, from_date=from_date, to_date=to_date, keyword=keyword)

    total_prompts = query.count()
    unique_employees = query.with_entities(func.count(func.distinct(models.AIPromptLog.employee_email))).scalar() or 0
    unique_projects = query.with_entities(func.count(func.distinct(models.AIPromptLog.project_code))).scalar() or 0

    records = query.with_entities(
        models.AIPromptLog.employee_email,
        models.AIPromptLog.source_app,
        models.AIPromptLog.session_id,
        models.AIPromptLog.project_name,
    ).all()

    category_counts = {"chat": 0, "cowork": 0, "code": 0}
    employee_map = {}

    for record in records:
        category = classify_source_app(record.source_app)
        category_counts[category] += 1

        email = record.employee_email or "Unknown"
        if email not in employee_map:
            employee_map[email] = {
                "email": email,
                "total": 0,
                "chat": 0,
                "cowork": 0,
                "code": 0,
                "projects": set(),
                "sessions": set(),
            }

        employee_map[email]["total"] += 1
        employee_map[email][category] += 1
        if record.project_name:
            employee_map[email]["projects"].add(record.project_name)
        if record.session_id:
            employee_map[email]["sessions"].add(record.session_id)

    employees = []
    for employee in employee_map.values():
        employees.append(
            {
                "email": employee["email"],
                "name": employee["email"].split("@")[0].replace(".", " ").title(),
                "total": employee["total"],
                "chat": employee["chat"],
                "cowork": employee["cowork"],
                "code": employee["code"],
                "project_count": len(employee["projects"]),
                "session_count": len(employee["sessions"]),
            }
        )

    employees.sort(key=lambda item: item["total"], reverse=True)

    return {
        "total_prompts": total_prompts,
        "unique_employees": unique_employees,
        "unique_projects": unique_projects,
        "categories": category_counts,
        "employees": employees,
    }


@app.get("/api/dashboard/employee/{employee_email:path}/sessions")
def dashboard_employee_sessions(
    employee_email: str,
    db: Session = Depends(get_db),
):
    records = (
        db.query(models.AIPromptLog)
        .filter(models.AIPromptLog.employee_email == employee_email)
        .order_by(models.AIPromptLog.created_at.desc(), models.AIPromptLog.id.desc())
        .all()
    )

    if not records:
        return {"employee_email": employee_email, "sessions": []}

    session_map = {}
    for record in records:
        session_id = record.session_id or "Unknown"
        category = classify_source_app(record.source_app)
        current_time = record.created_at.isoformat() if record.created_at else ""

        if session_id not in session_map:
            session_map[session_id] = {
                "session_id": session_id,
                "project_name": record.project_name or "Unknown",
                "project_code": record.project_code or "Unknown",
                "source_app": record.source_app or "Unknown",
                "category": category,
                "prompt_count": 0,
                "first_prompt_at": current_time,
                "last_prompt_at": current_time,
                "prompts": [],
            }

        session_map[session_id]["prompt_count"] += 1
        if current_time and current_time < session_map[session_id]["first_prompt_at"]:
            session_map[session_id]["first_prompt_at"] = current_time
        if current_time and current_time > session_map[session_id]["last_prompt_at"]:
            session_map[session_id]["last_prompt_at"] = current_time

        session_map[session_id]["prompts"].append(
            {
                "id": record.id,
                "prompt": record.prompt,
                "created_at": current_time,
                "category": category,
                "hook_event": record.hook_event or "",
            }
        )

    sessions = list(session_map.values())
    for session in sessions:
        session["prompts"].sort(key=lambda item: item["created_at"])

    return {
        "employee_email": employee_email,
        "sessions": sessions,
    }


@app.get("/", include_in_schema=False)
@app.get("/{full_path:path}", include_in_schema=False)
def serve_dashboard(full_path: str = ""):
    if full_path.startswith("api/"):
        return JSONResponse({"detail": "Not Found"}, status_code=404)

    if full_path:
        candidate = (FRONTEND_DIST_DIR / full_path).resolve()
        try:
            candidate.relative_to(FRONTEND_DIST_DIR.resolve())
        except ValueError:
            return JSONResponse({"detail": "Not Found"}, status_code=404)
        if candidate.is_file():
            return FileResponse(candidate)

    if FRONTEND_INDEX.exists():
        return FileResponse(FRONTEND_INDEX)

    return JSONResponse(
        {
            "detail": "Dashboard UI is not built yet.",
            "local_dev": "Run npm install and npm run dev inside dashboard-ui.",
            "production": "Run npm install and npm run build inside dashboard-ui, then start the backend.",
        },
        status_code=404,
    )
