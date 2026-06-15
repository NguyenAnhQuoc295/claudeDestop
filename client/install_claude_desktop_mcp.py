import argparse
import json
import os
import shutil
import socket
import sys
from datetime import datetime

from prompt_logger_common import load_install_defaults


HOME_DIR = os.path.expanduser("~")
CLAUDE_DIR = os.path.join(HOME_DIR, ".claude")
LOGGER_CONFIG_PATH = os.path.join(CLAUDE_DIR, "prompt_logger_config.json")
SERVER_NAME = "company-prompt-logger"
DEFAULT_LOG_DIR = os.path.join(HOME_DIR, "CompanyClaudeLogs")


def claude_desktop_config_path():
    store_path = windows_store_claude_config_path()
    if store_path:
        return store_path

    if os.name == "nt":
        appdata = os.getenv("APPDATA")
        if not appdata:
            raise RuntimeError("APPDATA is not set; cannot locate Claude Desktop config.")
        return os.path.join(appdata, "Claude", "claude_desktop_config.json")

    if sys.platform == "darwin":
        return os.path.join(
            HOME_DIR,
            "Library",
            "Application Support",
            "Claude",
            "claude_desktop_config.json",
        )

    return os.path.join(HOME_DIR, ".config", "Claude", "claude_desktop_config.json")


def windows_store_claude_config_path():
    if os.name != "nt":
        return None

    local_appdata = os.getenv("LOCALAPPDATA")
    if not local_appdata:
        return None

    packages_dir = os.path.join(local_appdata, "Packages")
    if not os.path.isdir(packages_dir):
        return None

    try:
        for name in os.listdir(packages_dir):
            if name.lower().startswith("claude_"):
                return os.path.join(
                    packages_dir,
                    name,
                    "LocalCache",
                    "Roaming",
                    "Claude",
                    "claude_desktop_config.json",
                )
    except Exception:
        return None

    return None


def load_json_file(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json_file(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def backup_file(path):
    if not os.path.exists(path):
        return None
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_path = f"{path}.bak.{timestamp}"
    shutil.copy2(path, backup_path)
    return backup_path


def install_logger_config(args, defaults):
    os.makedirs(CLAUDE_DIR, exist_ok=True)
    config = {}
    if os.path.exists(LOGGER_CONFIG_PATH):
        try:
            config = load_json_file(LOGGER_CONFIG_PATH)
        except Exception:
            backup_file(LOGGER_CONFIG_PATH)
            config = {}

    merged = {
        "employee_email": args.employee_email
        or config.get("employee_email")
        or defaults.get("employee_email"),
        "machine_id": args.machine_id
        or config.get("machine_id")
        or defaults.get("machine_id")
        or socket.gethostname(),
        "api_url": args.api_url or config.get("api_url") or defaults.get("api_url"),
        "api_key": args.api_key or config.get("api_key") or defaults.get("api_key"),
        "source_app": "Claude Desktop MCP",
        "employee_training_folder_url": args.employee_training_folder_url
        or config.get("employee_training_folder_url")
        or defaults.get("employee_training_folder_url", ""),
        "log_dir": args.log_dir or config.get("log_dir") or defaults.get("log_dir") or DEFAULT_LOG_DIR,
    }

    if not merged["employee_email"]:
        raise RuntimeError("employee_email is required. Pass --employee-email or set install defaults.")

    for key, value in merged.items():
        if value is not None:
            config[key] = value

    write_json_file(LOGGER_CONFIG_PATH, config)
    return config


def install_claude_desktop_config(args, logger_config):
    desktop_config_path = args.claude_config or claude_desktop_config_path()
    config = {}
    if os.path.exists(desktop_config_path):
        try:
            config = load_json_file(desktop_config_path)
        except Exception as e:
            backup_path = backup_file(desktop_config_path)
            print(f"Warning: invalid Claude Desktop config JSON ({e}). Backup: {backup_path}")
            config = {}

    if not args.no_backup:
        backup_path = backup_file(desktop_config_path)
        if backup_path:
            print(f"Backup Claude Desktop config: {backup_path}")

    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "mcp_prompt_logger.py"))
    python_command = args.python_command or sys.executable or "python"

    config.setdefault("mcpServers", {})
    config["mcpServers"][SERVER_NAME] = {
        "command": python_command,
        "args": [script_path],
        "env": {
            "CLAUDE_LOGGER_API_URL": logger_config.get("api_url", ""),
            "CLAUDE_LOGGER_API_KEY": logger_config.get("api_key", ""),
            "CLAUDE_EMPLOYEE_EMAIL": logger_config.get("employee_email", ""),
            "CLAUDE_MACHINE_ID": logger_config.get("machine_id", ""),
            "CLAUDE_LOG_DIR": logger_config.get("log_dir", DEFAULT_LOG_DIR),
        },
    }

    write_json_file(desktop_config_path, config)
    return desktop_config_path, script_path


def main():
    defaults = load_install_defaults()

    parser = argparse.ArgumentParser(
        description="Install Claude Desktop MCP prompt logger action."
    )
    parser.add_argument("--employee-email")
    parser.add_argument("--machine-id")
    parser.add_argument("--api-url")
    parser.add_argument("--api-key")
    parser.add_argument(
        "--employee-training-folder-url",
    )
    parser.add_argument("--log-dir")
    parser.add_argument("--python-command", help="Python executable command for Claude Desktop to run.")
    parser.add_argument("--claude-config", help="Override Claude Desktop config path.")
    parser.add_argument("--no-backup", action="store_true", help="Do not backup config before writing.")
    args = parser.parse_args()

    logger_config = install_logger_config(args, defaults)
    desktop_config_path, script_path = install_claude_desktop_config(args, logger_config)
    os.makedirs(logger_config.get("log_dir", DEFAULT_LOG_DIR), exist_ok=True)

    print("Installed Claude Desktop MCP prompt logger.")
    print(f"  MCP server: {script_path}")
    print(f"  Logger config: {LOGGER_CONFIG_PATH}")
    print(f"  Claude Desktop config: {desktop_config_path}")
    print(f"  Local log folder: {logger_config.get('log_dir', DEFAULT_LOG_DIR)}")
    print("")
    print("Restart Claude Desktop, then ask it to use the record_exact_prompt tool before company work.")


if __name__ == "__main__":
    main()
