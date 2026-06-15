import argparse
import json
import os
import socket
import sys
import urllib.request
import uuid
from datetime import datetime


HOME_DIR = os.path.expanduser("~")
CLAUDE_DIR = os.path.join(HOME_DIR, ".claude")
LOGGER_CONFIG_PATH = os.path.join(CLAUDE_DIR, "prompt_logger_config.json")
INSTALL_DEFAULTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "install_defaults.json")

DEFAULT_API_URL = "http://localhost:8000/api/claude/prompt-log"
DEFAULT_API_KEY = "dev-secret"


def _expand_config_value(value):
    if isinstance(value, str):
        return os.path.expandvars(os.path.expanduser(value))
    return value


def load_install_defaults():
    defaults = {
        "api_url": DEFAULT_API_URL,
        "api_key": DEFAULT_API_KEY,
        "employee_email": None,
        "machine_id": None,
        "source_app": "Claude Desktop MCP",
        "employee_training_folder_url": "",
        "log_dir": None,
    }

    if os.path.exists(INSTALL_DEFAULTS_PATH):
        try:
            with open(INSTALL_DEFAULTS_PATH, "r", encoding="utf-8") as df:
                file_defaults = json.load(df)
            for key in defaults:
                if file_defaults.get(key) is not None:
                    defaults[key] = _expand_config_value(file_defaults.get(key))
        except Exception as e:
            print(f"Warning: Could not read installer defaults at {INSTALL_DEFAULTS_PATH}: {e}")

    if os.getenv("CLAUDE_LOGGER_API_URL"):
        defaults["api_url"] = os.getenv("CLAUDE_LOGGER_API_URL")
    if os.getenv("CLAUDE_LOGGER_API_KEY"):
        defaults["api_key"] = os.getenv("CLAUDE_LOGGER_API_KEY")
    if os.getenv("CLAUDE_EMPLOYEE_EMAIL"):
        defaults["employee_email"] = os.getenv("CLAUDE_EMPLOYEE_EMAIL")

    return defaults


def load_installed_logger_config():
    if not os.path.exists(LOGGER_CONFIG_PATH):
        raise RuntimeError(f"Config file not found: {LOGGER_CONFIG_PATH}")

    with open(LOGGER_CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    if not config.get("api_url"):
        raise RuntimeError("api_url is not configured in prompt_logger_config.json")

    return config


def send_backend_test():
    config = load_installed_logger_config()
    api_url = config.get("api_url")
    api_key = config.get("api_key")

    payload = {
        "event_id": f"test-desktop-mcp-{uuid.uuid4()}",
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "employee_email": config.get("employee_email", "test@company.com"),
        "machine_id": config.get("machine_id") or socket.gethostname(),
        "project_name": "Claude Desktop MCP Setup Test",
        "project_code": "CHAT-CLAUDE-DESKTOP-MCP-SETUP-TEST",
        "workspace_folder": "Claude Desktop / Setup Test",
        "session_id": "CHAT:CHAT-CLAUDE-DESKTOP-MCP-SETUP-TEST",
        "prompt": "Test connection from Claude Desktop MCP employee setup.",
        "prompt_hash": "test-desktop-mcp",
        "related_files": ["setup_claude_desktop_employee.bat", "prompt_logger_config.json"],
        "source_app": config.get("source_app", "Claude Desktop MCP"),
        "hook_event": "record_exact_prompt_test",
        "training_resources": {
            "employee_training_folder_url": config.get("employee_training_folder_url", ""),
        },
    }

    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(api_url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    if api_key:
        req.add_header("X-API-Key", api_key)

    with urllib.request.urlopen(req, timeout=10) as response:
        body = response.read().decode("utf-8")
        result = json.loads(body)

    if not result.get("success"):
        raise RuntimeError(f"Server returned success=false: {result}")

    return result


def main():
    parser = argparse.ArgumentParser(description="Claude Desktop prompt logger helper.")
    parser.add_argument("--test", action="store_true", help="Send one test prompt log to backend.")
    args = parser.parse_args()

    if args.test:
        print("Testing backend connection...")
        result = send_backend_test()
        print("Success! Backend accepted test record.")
        print(f"  Record ID: {result.get('id')}")
        print(f"  Event ID: {result.get('event_id')}")
        return

    print(json.dumps(load_install_defaults(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
