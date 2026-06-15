# Claude Logger System - Tai Lieu Ban Giao IT

Ngay cap nhat: 2026-06-15

## 1. Muc Tieu

He thong ghi nhan prompt nhan vien gui tu cac kenh Claude noi bo, luu vao database tap trung, va hien thi tren dashboard quan ly.

Kien truc UI da duoc chot lai:

- `dashboard-ui/` la giao dien dashboard chinh.
- `backend/` chi giu API, database, xac thuc API key va phuc vu ban build React.
- UI cu trong `backend/app/templates` va `backend/app/static` da duoc loai bo.

## 2. Thanh Phan He Thong

```text
Nhan vien / Claude client
  -> POST /api/claude/prompt-log
  -> FastAPI backend
  -> SQLite hoac PostgreSQL
  -> React dashboard trong dashboard-ui
```

Thu muc quan trong:

| Duong dan | Vai tro |
| --- | --- |
| `backend/app/main.py` | FastAPI app, API nhan log, API dashboard, serve React build |
| `backend/app/models.py` | SQLAlchemy model bang prompt log |
| `backend/app/auth.py` | Kiem tra header `X-API-Key` |
| `backend/app/config.py` | Doc bien moi truong |
| `dashboard-ui/` | React + Vite dashboard |
| `client/` | Script cai dat logger tren may nhan vien |
| `IT_TEST_DASHBOARD.bat` | File double-click de IT build, chay va mo dashboard test nhanh |
| `docs/IT_HANDOVER.md` | Tai lieu ban giao nay |

## 3. API Chinh

| Endpoint | Muc dich |
| --- | --- |
| `GET /health` | Kiem tra backend song |
| `POST /api/claude/prompt-log` | Client gui prompt log ve server |
| `GET /api/claude/prompt-logs` | Lay danh sach prompt log dang JSON |
| `GET /api/dashboard/summary` | Du lieu tong hop cho React dashboard |
| `GET /api/dashboard/employee/{email}/sessions` | Lay session va prompt cua mot nhan vien |

Neu `PROMPT_LOG_API_KEY` co gia tri, client phai gui header:

```http
X-API-Key: <PROMPT_LOG_API_KEY>
```

## 4. Chay Local De Kiem Thu

Yeu cau:

- Python 3.11+
- Node.js LTS 22+ hoac 20+
- PowerShell tren Windows

Nhanh nhat cho IT:

```text
Double-click IT_TEST_DASHBOARD.bat
```

File nay se cai dependency backend, build `dashboard-ui`, chay backend tai `http://127.0.0.1:8000/`, mo trinh duyet, va in ket qua check `/health` + `/api/dashboard/summary`.

Chay backend API:

```powershell
.\start_local.ps1 -ForceRestart
```

Chay dashboard UI dang dev:

```powershell
cd dashboard-ui
npm install
npm run dev
```

Mo dashboard dev tai:

```text
http://localhost:5173
```

Vite se proxy cac request `/api/...` ve backend `http://localhost:8000`.

## 5. Chay Local Theo Kieu Production

Build dashboard React va de backend phuc vu UI tai `/`:

```powershell
.\start_local.ps1 -BuildDashboard -ForceRestart
```

Sau khi backend chay, mo:

```text
http://127.0.0.1:8000/
```

Kiem tra API:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/api/dashboard/summary
```

## 6. Deploy Bang Docker Compose

Dockerfile da duoc doi sang multi-stage build:

1. Stage Node build `dashboard-ui`.
2. Stage Python cai backend.
3. Copy `dashboard-ui/dist` vao image backend.
4. Backend phuc vu React dashboard tai `/`.

Lenh deploy:

```powershell
docker compose up --build -d
```

Kiem tra:

```powershell
docker compose ps
Invoke-RestMethod http://localhost:8000/health
```

Bien moi truong trong `docker-compose.yml` can IT chot lai truoc khi dua len server:

| Bien | Gia tri hien tai | Ghi chu |
| --- | --- | --- |
| `APP_NAME` | `Claude Prompt Logger` | Ten app |
| `DATABASE_URL` | `sqlite:///./prompt_logger.db` | Co the doi sang PostgreSQL |
| `PROMPT_LOG_API_KEY` | `dev-secret` | Bat buoc doi khi production |
| `TIMEZONE` | `Asia/Ho_Chi_Minh` | Mui gio |

## 7. Cai Dat Tren May Nhan Vien

Mau cau hinh nam tai:

```text
client/install_defaults.example.json
```

Tao file that:

```text
client/install_defaults.json
```

Noi dung can sua:

```json
{
  "employee_email": null,
  "machine_id": null,
  "api_url": "http://SERVER_IP_OR_DOMAIN:8000/api/claude/prompt-log",
  "api_key": "dev-secret",
  "source_app": "Claude Desktop MCP",
  "employee_training_folder_url": "",
  "log_dir": "%USERPROFILE%\\CompanyClaudeLogs"
}
```

Sau do tren may nhan vien chay:

```powershell
client\setup_claude_desktop_employee.bat
```

Script se hoi email nhan vien, cai MCP logger vao Claude Desktop, test ket noi backend, va tao log local tai:

```text
%USERPROFILE%\CompanyClaudeLogs
```

Luu y: Claude Desktop MCP khong phai raw prompt hook tuyet doi. Muon log tot, IT can cau hinh instruction bat Claude goi tool `record_exact_prompt` truoc khi tra loi viec cong ty. Huong dan chi tiet nam tai:

```text
client/CLAUDE_DESKTOP_MCP_SETUP.md
```

## 8. Checklist Truoc Khi Ban Giao Production

- Doi `PROMPT_LOG_API_KEY` khoi gia tri `dev-secret`.
- Mo firewall cho cong backend, mac dinh `8000`, hoac dat reverse proxy HTTPS.
- Neu dung SQLite, dam bao volume database duoc backup.
- Neu nhieu nhan vien / log lon, can chuyen `DATABASE_URL` sang PostgreSQL.
- Kiem tra `POST /api/claude/prompt-log` voi API key that.
- Kiem tra dashboard hien thi tai `/`.
- Chay test cai dat tren it nhat 1 may nhan vien.
- Xac nhan folder log local va offline queue tren may nhan vien.
- Chot quy trinh cap nhat `client/install_defaults.json` khi doi domain/API key.

## 9. Huong Mo Rong

- Them dang nhap admin cho dashboard neu dashboard duoc mo ngoai mang noi bo.
- Them export CSV/Excel tu `/api/claude/prompt-logs`.
- Them bo loc ngay, nhan vien, project tren React dashboard.
- Neu trien khai Claude Web PWA + managed browser extension, extension van gui ve endpoint hien tai `POST /api/claude/prompt-log` voi metadata `source_app` va `hook_event` rieng.
