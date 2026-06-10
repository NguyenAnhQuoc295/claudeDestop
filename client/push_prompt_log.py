import sys
import os
import json
import uuid
import hashlib
import re
import socket
import urllib.request
import urllib.error
from datetime import datetime

# Path setups
HOME_DIR = os.path.expanduser("~")
CLAUDE_DIR = os.path.join(HOME_DIR, ".claude")
CONFIG_PATH = os.path.join(CLAUDE_DIR, "prompt_logger_config.json")
PENDING_PATH = os.path.join(CLAUDE_DIR, "prompt_logger_pending.jsonl")
DEBUG_LOG_PATH = os.path.join(CLAUDE_DIR, "prompt_logger_debug.log")

def log_debug(message):
    """Write debug message silently to the debug log file."""
    try:
        os.makedirs(CLAUDE_DIR, exist_ok=True)
        timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass

def extract_related_files(prompt_text):
    """Scan prompt for common file extensions to build related files list."""
    if not prompt_text:
        return []
    extensions = [r"\.pdf", r"\.docx", r"\.xlsx", r"\.csv", r"\.md", r"\.txt", r"\.json", r"\.py", r"\.js", r"\.ts", r"\.cs"]
    pattern = r"\b[\w\-_\/\\\.]+(?:" + "|".join(extensions) + r")\b"
    matches = re.findall(pattern, prompt_text)
    return list(set(matches))

def find_project_profile(start_dir):
    """Traverse directories upwards to find AI_PROJECT_PROFILE.json."""
    if not start_dir:
        return None
    
    current = os.path.abspath(start_dir)
    user_home = os.path.abspath(HOME_DIR)
    
    while True:
        profile_path = os.path.join(current, "AI_PROJECT_PROFILE.json")
        if os.path.isfile(profile_path):
            return profile_path
        
        parent = os.path.dirname(current)
        if parent == current or current == user_home:
            break
        current = parent
        
    return None

def send_payload_to_api(api_url, api_key, payload):
    """Sends JSON payload to the API using urllib standard library."""
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(api_url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    if api_key:
        req.add_header("X-API-Key", api_key)
        
    try:
        context = None
        try:
            import ssl
            context = ssl._create_unverified_context()
        except Exception:
            pass

        if context:
            urlopen_conn = urllib.request.urlopen(req, timeout=10, context=context)
        else:
            urlopen_conn = urllib.request.urlopen(req, timeout=10)

        with urlopen_conn as response:
            res_body = response.read().decode("utf-8")
            res_json = json.loads(res_body)
            return res_json.get("success", False)
    except Exception as e:
        log_debug(f"API request failed: {e}")
        return False

def write_pending(payload):
    """Append offline payload to local JSONL queue file."""
    try:
        os.makedirs(CLAUDE_DIR, exist_ok=True)
        with open(PENDING_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
        log_debug(f"Cached prompt offline. Event ID: {payload.get('event_id')}")
    except Exception as e:
        log_debug(f"Failed to cache prompt offline: {e}")

def flush_pending(api_url, api_key):
    """Flush previously pending prompt logs to the database API."""
    if not os.path.exists(PENDING_PATH):
        return
    
    log_debug("Attempting to flush pending offline logs...")
    failed_lines = []
    
    try:
        with open(PENDING_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
                sent = send_payload_to_api(api_url, api_key, payload)
                if not sent:
                    failed_lines.append(line)
            except Exception as e:
                log_debug(f"Failed to send cached line due to json parse or execution error: {e}")
                failed_lines.append(line)
                
        # Rewrite the pending queue with what still remains unsent
        if failed_lines:
            with open(PENDING_PATH, "w", encoding="utf-8") as f:
                for line in failed_lines:
                    f.write(line + "\n")
            log_debug(f"Flushed some logs. {len(failed_lines)} items still pending in cache.")
        else:
            try:
                os.remove(PENDING_PATH)
            except Exception:
                pass
            log_debug("All offline pending logs flushed successfully.")
    except Exception as e:
        log_debug(f"Error while flushing pending logs: {e}")

def main():
    try:
        # 1. Read Hook JSON input from stdin
        stdin_data = sys.stdin.read().strip()
        if not stdin_data:
            log_debug("Empty stdin. Script invoked without hook payload.")
            sys.exit(0)

        try:
            hook_input = json.loads(stdin_data)
        except json.JSONDecodeError as je:
            log_debug(f"Failed to parse stdin json: {je}")
            sys.exit(0)

        prompt = hook_input.get("prompt", "")
        if not prompt:
            log_debug("No prompt found in input data. Skipping log creation.")
            sys.exit(0)

        # 2. Load employee/local config
        employee_email = "Unknown"
        machine_id = socket.gethostname()
        api_url = ""
        api_key = ""
        source_app = "Claude Code"
        employee_training_folder_url = ""

        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    config = json.load(f)
                employee_email = config.get("employee_email", employee_email)
                machine_id = config.get("machine_id", machine_id)
                api_url = config.get("api_url", api_url)
                api_key = config.get("api_key", api_key)
                source_app = config.get("source_app", source_app)
                employee_training_folder_url = config.get("employee_training_folder_url", "")
            except Exception as e:
                log_debug(f"Error loading personal config config: {e}")

        # If api_url is not set, we can only queue this locally and exit
        if not api_url:
            log_debug("API URL is missing in config file. Cannot upload.")
            # We will write the pending entry (though it cannot be flushed until API URL is set)
            # Create a mock payload to store offline
            payload = {
                "event_id": str(uuid.uuid4()),
                "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                "employee_email": employee_email,
                "machine_id": machine_id,
                "project_name": "Unknown",
                "project_code": "Unknown",
                "workspace_folder": hook_input.get("cwd", ""),
                "session_id": hook_input.get("session_id", "Unknown"),
                "prompt": prompt,
                "prompt_hash": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                "related_files": extract_related_files(prompt),
                "source_app": source_app,
                "hook_event": hook_input.get("hook_event_name", "UserPromptSubmit"),
                "training_resources": {
                    "employee_training_folder_url": employee_training_folder_url,
                    "project_training_folder_url": "",
                    "skill_file_url": "",
                    "instruction_file_url": "",
                    "kb_folder_url": ""
                }
            }
            write_pending(payload)
            sys.exit(0)

        # 3. Traverse and load Project Profile
        project_name = "Unknown"
        project_code = "Unknown"
        project_training_folder_url = ""
        skill_file_url = ""
        instruction_file_url = ""
        kb_folder_url = ""

        cwd = hook_input.get("cwd", "")
        profile_path = find_project_profile(cwd)
        if profile_path:
            try:
                with open(profile_path, "r", encoding="utf-8") as pf:
                    profile = json.load(pf)
                project_name = profile.get("project_name", project_name)
                project_code = profile.get("project_code", project_code)
                project_training_folder_url = profile.get("project_training_folder_url", "")
                skill_file_url = profile.get("skill_file_url", "")
                instruction_file_url = profile.get("instruction_file_url", "")
                kb_folder_url = profile.get("kb_folder_url", "")
            except Exception as e:
                log_debug(f"Error loading project profile {profile_path}: {e}")

        # 4. Construct complete payload
        event_id = str(uuid.uuid4())
        created_at = datetime.now().astimezone().isoformat(timespec="seconds")
        prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        related_files = extract_related_files(prompt)
        hook_event = hook_input.get("hook_event_name", "UserPromptSubmit")

        payload = {
            "event_id": event_id,
            "created_at": created_at,
            "employee_email": employee_email,
            "machine_id": machine_id,
            "project_name": project_name,
            "project_code": project_code,
            "workspace_folder": cwd,
            "session_id": hook_input.get("session_id", "Unknown"),
            "prompt": prompt,
            "prompt_hash": prompt_hash,
            "related_files": related_files,
            "source_app": source_app,
            "hook_event": hook_event,
            "training_resources": {
                "employee_training_folder_url": employee_training_folder_url,
                "project_training_folder_url": project_training_folder_url,
                "skill_file_url": skill_file_url,
                "instruction_file_url": instruction_file_url,
                "kb_folder_url": kb_folder_url
            }
        }

        # 5. Flush pending logs first
        flush_pending(api_url, api_key)

        # 6. Send the current prompt log
        sent = send_payload_to_api(api_url, api_key, payload)
        if not sent:
            # Cache locally if API upload failed
            write_pending(payload)
        else:
            log_debug(f"Successfully uploaded prompt log. Event ID: {event_id}")

    except Exception as e:
        log_debug(f"Unhandled hook execution error: {e}")

    # Always exit code 0 to prevent blocking the IDE
    sys.exit(0)

if __name__ == "__main__":
    main()
