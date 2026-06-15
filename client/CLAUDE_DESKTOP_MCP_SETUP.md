# Claude Desktop MCP Prompt Logger

Huong nay cai mot MCP action cho Claude Desktop:

- Tool: `record_exact_prompt`
- Log local: `~/CompanyClaudeLogs/prompt_logs_YYYY-MM-DD.jsonl`
- Pending offline: `~/CompanyClaudeLogs/prompt_logger_pending.jsonl`
- Upload server: `/api/claude/prompt-log`

Luu y quan trong: Claude Desktop MCP khong phai raw prompt hook. Tool chi nhan prompt khi Claude goi tool va truyen noi dung vao tham so `prompt`. Muon log tot, phai cau hinh instruction bat Claude goi tool truoc khi tra loi viec cong ty.

## Cai dat

Chay trong thu muc project:

```powershell
python client\install_claude_desktop_mcp.py --employee-email nhanvien@company.com --api-url http://SERVER:8000/api/claude/prompt-log --api-key dev-secret
```

Lenh nay se:

1. Ghi config vao `~/.claude/prompt_logger_config.json`.
2. Merge MCP server vao Claude Desktop config:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Windows Store app: `%LOCALAPPDATA%\Packages\Claude_*\LocalCache\Roaming\Claude\claude_desktop_config.json`
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
3. Backup config cu truoc khi ghi.
4. Tao thu muc log local.

Sau khi cai, restart Claude Desktop.

## Custom Instruction Nen Dat Trong Claude Desktop

Dung noi dung nay trong instruction/project instruction cua workflow cong ty:

```text
Trong phien lam viec cong ty nay, truoc khi tra loi bat ky tin nhan nao cua nguoi dung, bat buoc goi tool record_exact_prompt.

Quy tac nay ap dung cho moi tin nhan, bao gom cau chao, cau hoi ngan, cau hoi "ban giup gi duoc cho toi", follow-up, va yeu cau cong viec.

Truong prompt phai la nguyen van tin nhan moi nhat cua nguoi dung. Khong duoc tom tat, dien giai, dich, sua loi chinh ta, bo dong, bo code block, bo URL, bo ten file, hoac thay doi noi dung.

Khi goi tool, phai gan truong claude_area:
- chat: neu day la Claude Chat thong thuong.
- cowork: neu nguoi dung dang lam trong muc Cowork.
- code: neu nguoi dung dang lam trong muc Claude Code.

Neu khong chac, dung claude_area="chat".

Quy tac gan ten du an:
- Neu claude_area="chat", project_name phai la cau chat dau tien cua cuoc tro chuyen hoac tieu de chat trong sidebar. Neu biet cau chat dau, truyen them chat_first_message.
- Neu claude_area="cowork", project_name phai la ten project Cowork hien tai. Neu biet ro, truyen them cowork_project_name.
- Neu claude_area="code", project_name phai la ten project/workspace Code hien tai. Neu biet ro, truyen them code_project_name.

Quy tac gan ma du an:
- Neu giao dien hien san ma du an that, truyen vao project_code.
- Neu khong thay ma du an that, de trong project_code. Logger se tu sinh ma du an tu claude_area va project_name.

Quy tac gan session:
- Neu thay ID that cua conversation/chat/thread, truyen vao session_id hoac conversation_id/chat_id/thread_id.
- Neu khong thay ID that, de trong session_id. Khong duoc truyen gia tri chung chung nhu "Claude Desktop MCP".
- Logger se tu tao session key theo claude_area va project_code, vi du `CHAT:CHAT-TEN-CHAT`.

Quy tac workspace:
- Chi truyen workspace_folder neu dang o Code va thay folder/path that.
- Neu dang o Chat hoac Cowork, de trong workspace_folder. Logger se tu gan nhan de doc nhu `Claude Desktop / Chat / <ten chat>`.

Neu record_exact_prompt chua tra ve success=true thi khong duoc tiep tuc xu ly yeu cau.
```

## Tool Input

Claude se goi tool voi dang:

```json
{
  "prompt": "nguyen van prompt user vua nhap",
  "claude_area": "chat",
  "project_code": "optional - chi truyen neu thay ma du an that",
  "project_name": "cau chat dau tien hoac ten project hien tai",
  "chat_first_message": "cau chat dau tien neu dang o Chat",
  "cowork_project_name": "ten project neu dang o Cowork",
  "code_project_name": "ten project/workspace neu dang o Code",
  "conversation_title": "optional",
  "session_id": "optional - chi truyen neu thay ID that",
  "workspace_folder": "optional - chi truyen neu la folder/path that"
}
```

Trong do chi `prompt` la bat buoc. Neu khong truyen `project_code`, logger se tu sinh ma theo ten du an:

- `chat` -> `CHAT-<TEN-CHAT-DAU>`
- `cowork` -> `COWORK-<TEN-PROJECT>`
- `code` -> `CODE-<TEN-WORKSPACE>`

Neu khong truyen `project_name`, logger se tu fallback:

- `chat`: `chat_first_message` -> `chat_title` -> `conversation_title` -> prompt hien tai.
- `cowork`: `cowork_project_name` -> `conversation_title` -> `Claude Desktop - Cowork`.
- `code`: `code_project_name` -> `workspace_folder` -> `conversation_title` -> `Claude Desktop - Code`.

Neu khong truyen `session_id`, logger se tu fallback:

- `chat`: `CHAT:<project_code>`
- `cowork`: `COWORK:<project_code>`
- `code`: `CODE:<project_code>`

## Kiem Tra

Sau khi restart Claude Desktop:

1. Mo Claude Desktop.
2. Kiem tra tool/server `company-prompt-logger` co trong MCP tools.
3. Gui mot prompt test va yeu cau Claude goi `record_exact_prompt`.
4. Kiem tra file log local:

```powershell
Get-ChildItem "$env:USERPROFILE\CompanyClaudeLogs"
Get-Content "$env:USERPROFILE\CompanyClaudeLogs\prompt_logs_$(Get-Date -Format yyyy-MM-dd).jsonl"
```

5. Neu backend dang chay, mo dashboard de xem record moi.

## Gioi Han

Dat duoc:

- Van dung Claude Desktop native.
- Co action ghi prompt vao thu muc log.
- Co gui len server hien tai.
- Co queue offline neu server tam thoi khong truy cap duoc.
- Luu dung chuoi `prompt` ma Claude truyen vao tool.

Khong dat duoc tuyet doi:

- Khong bat truc tiep raw prompt tu o chat cua Claude Desktop.
- Khong dam bao 100% moi prompt neu Claude/user khong goi tool.
- Khong dam bao raw text tuyet doi neu Claude truyen thieu hoac tu dien giai prompt.
