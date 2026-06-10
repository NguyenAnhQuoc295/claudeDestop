import os
import sys
import json
import socket
import shutil
import argparse
import urllib.request
import uuid
from datetime import datetime

HOME_DIR = os.path.expanduser("~")
CLAUDE_DIR = os.path.join(HOME_DIR, ".claude")
CONFIG_PATH = os.path.join(CLAUDE_DIR, "prompt_logger_config.json")
SETTINGS_PATH = os.path.join(CLAUDE_DIR, "settings.json")
HOOKS_DIR = os.path.join(CLAUDE_DIR, "hooks")
HOOKS_SCRIPT_DEST = os.path.join(HOOKS_DIR, "push_prompt_log.py")
INSTALL_DEFAULTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "install_defaults.json")
DEFAULT_API_URL = "http://localhost:8000/api/claude/prompt-log"
DEFAULT_API_KEY = "dev-secret"
ENV_API_URL = "CLAUDE_LOGGER_API_URL"
ENV_API_KEY = "CLAUDE_LOGGER_API_KEY"

def load_install_defaults():
    """Load installer defaults from local JSON and environment variables.
    Returns a dict with keys: api_url, api_key, employee_email, machine_id,
    source_app, employee_training_folder_url.
    """
    defaults = {
        "api_url": DEFAULT_API_URL,
        "api_key": DEFAULT_API_KEY,
        "employee_email": None,
        "machine_id": None,
        "source_app": "Claude Code",
        "employee_training_folder_url": "https://drive.google.com/drive/folders/default-employee-training-folder"
    }

    if os.path.exists(INSTALL_DEFAULTS_PATH):
        try:
            with open(INSTALL_DEFAULTS_PATH, "r", encoding="utf-8") as df:
                file_defaults = json.load(df)
            for key in ("api_url", "api_key", "employee_email", "machine_id", "source_app", "employee_training_folder_url"):
                if file_defaults.get(key) is not None:
                    defaults[key] = file_defaults.get(key)
        except Exception as e:
            print(f"Warning: Could not read installer defaults at {INSTALL_DEFAULTS_PATH}: {e}")

    # Environment overrides (optional)
    if os.getenv(ENV_API_URL):
        defaults["api_url"] = os.getenv(ENV_API_URL)
    if os.getenv(ENV_API_KEY):
        defaults["api_key"] = os.getenv(ENV_API_KEY)
    if os.getenv("CLAUDE_EMPLOYEE_EMAIL"):
        defaults["employee_email"] = os.getenv("CLAUDE_EMPLOYEE_EMAIL")

    return defaults

def detect_os_command():
    """Detect operating system and return the appropriate python command string."""
    if os.name == 'nt':  # Windows
        return 'python "%USERPROFILE%\\.claude\\hooks\\push_prompt_log.py"'
    else:  # macOS / Linux
        return 'python3 ~/.claude/hooks/push_prompt_log.py'

def run_api_test():
    """Reads installed config and sends a test payload to backend to verify connection."""
    print("Running integration test connection to backend API...")
    if not os.path.exists(CONFIG_PATH):
        print(f"Error: Config file not found at {CONFIG_PATH}. Please run installation first.")
        sys.exit(1)
        
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error reading config: {e}")
        sys.exit(1)
        
    api_url = config.get("api_url")
    api_key = config.get("api_key")
    employee_email = config.get("employee_email", "test@company.com")
    machine_id = config.get("machine_id", "TEST-MACHINE")
    
    if not api_url:
        print("Error: api_url is not configured in prompt_logger_config.json")
        sys.exit(1)
        
    # Generate test payload
    payload = {
        "event_id": f"test-install-{uuid.uuid4()}",
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "employee_email": employee_email,
        "machine_id": machine_id,
        "project_name": "Claude Prompt Logger Integration Test",
        "project_code": "LOG-TEST-001",
        "workspace_folder": os.getcwd(),
        "session_id": "test-session-id",
        "prompt": "Hello! Truc quan hoa ket noi test tu script cai dat install_hook.py.",
        "prompt_hash": "test-install-hash",
        "related_files": ["install_hook.py", "prompt_logger_config.json"],
        "source_app": config.get("source_app", "Claude Code"),
        "hook_event": "UserPromptSubmit",
        "training_resources": {
            "employee_training_folder_url": config.get("employee_training_folder_url", ""),
            "project_training_folder_url": "https://drive.google.com/drive/folders/test-project",
            "skill_file_url": "https://drive.google.com/file/d/test-skill/view",
            "instruction_file_url": "https://drive.google.com/file/d/test-instruction/view",
            "kb_folder_url": "https://drive.google.com/drive/folders/test-kb"
        }
    }
    
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(api_url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    if api_key:
        req.add_header("X-API-Key", api_key)
        
    try:
        print(f"Sending request to {api_url}...")
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
            if res_json.get("success"):
                print("Success! API responded successfully:")
                print(f"   Record ID: {res_json.get('id')}")
                print(f"   Event ID: {res_json.get('event_id')}")
                print("\nHook is fully ready and tested. Run Claude Code to start logging.")
            else:
                print("Failure: Server returned success=False")
                sys.exit(1)
    except Exception as e:
        print(f"Connection Failure: {e}")
        sys.exit(1)

def merge_settings(hook_command):
    """Merge hook registration into Claude Code ~/.claude/settings.json."""
    settings = {}
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as sf:
                settings = json.load(sf)
        except Exception as e:
            # Create a backup since parsing failed
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            backup_path = f"{SETTINGS_PATH}.bak.{timestamp}"
            print(f"Warning: {SETTINGS_PATH} contains invalid JSON ({e}). Backing up to {backup_path}")
            try:
                shutil.copy2(SETTINGS_PATH, backup_path)
            except Exception as copy_err:
                print(f"Failed to backup file: {copy_err}")
            settings = {}

    # Standard settings structure
    if "hooks" not in settings:
        settings["hooks"] = {}
    
    if "UserPromptSubmit" not in settings["hooks"]:
        settings["hooks"]["UserPromptSubmit"] = []

    # New hook command layout
    new_hook = {
        "type": "command",
        "command": hook_command,
        "async": True,
        "timeout": 10
    }

    # Find or create a matcher with ""
    matched_group = None
    for group in settings["hooks"]["UserPromptSubmit"]:
        if group.get("matcher") == "":
            matched_group = group
            break
            
    if matched_group is None:
        matched_group = {
            "matcher": "",
            "hooks": []
        }
        settings["hooks"]["UserPromptSubmit"].append(matched_group)

    # Check if this command already exists inside the matcher
    hook_exists = False
    for existing_hook in matched_group["hooks"]:
        if existing_hook.get("command") == hook_command:
            hook_exists = True
            break
            
    if not hook_exists:
        matched_group["hooks"].append(new_hook)
        print(f"Added hook command to UserPromptSubmit: {hook_command}")
    else:
        print(f"Hook command already registered in {SETTINGS_PATH}. Skipping registration.")

    # Write merged settings
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as sf:
            json.dump(settings, sf, indent=2, ensure_ascii=False)
        print(f"Updated Claude settings file: {SETTINGS_PATH}")
    except Exception as e:
        print(f"Error writing Claude settings: {e}")
        sys.exit(1)

def main():
    install_defaults = load_install_defaults()
    parser = argparse.ArgumentParser(description="Install Claude Prompt Logger Client Hook")
    parser.add_argument("--config-file", type=str, help="Path to JSON file containing full installation configuration")
    parser.add_argument("--employee-email", type=str, default=install_defaults.get("employee_email"), help="Email address of the employee")
    parser.add_argument("--machine-id", type=str, default=install_defaults.get("machine_id"), help="Machine identifier (default: computer hostname)")
    parser.add_argument("--api-url", type=str, default=install_defaults.get("api_url"), help="Backend log ingestion URL")
    parser.add_argument("--api-key", type=str, default=install_defaults.get("api_key"), help="Authorization key for the API (X-API-Key)")
    parser.add_argument("--test", action="store_true", help="Run integration test to API and exit")

    args = parser.parse_args()

    # If --test is provided, ignore other configurations and run the connection test
    if args.test:
        run_api_test()
        return

    # Merge configuration: CLI args (or defaults) -> optional config file -> install defaults
    combined_config = {
        "employee_email": args.employee_email,
        "machine_id": args.machine_id,
        "api_url": args.api_url,
        "api_key": args.api_key,
        "source_app": install_defaults.get("source_app", "Claude Code"),
        "employee_training_folder_url": install_defaults.get("employee_training_folder_url")
    }

    # If provided, a JSON config file overrides any CLI/default values
    if args.config_file:
        try:
            with open(args.config_file, "r", encoding="utf-8") as cf:
                file_conf = json.load(cf)
            for k, v in file_conf.items():
                combined_config[k] = v
        except Exception as e:
            print(f"Error reading config file {args.config_file}: {e}")
            sys.exit(1)

    # employee_email must be present in the merged config
    if not combined_config.get("employee_email"):
        print("Error: employee_email must be provided via config JSON or --employee-email.")
        sys.exit(1)

    # Fallback for machine id
    if not combined_config.get("machine_id"):
        combined_config["machine_id"] = socket.gethostname()

    print("Starting installation of Claude Prompt Logger Hook...")

    # 1. Create directory structure
    os.makedirs(HOOKS_DIR, exist_ok=True)

    # 2. Locate source hook file and copy it
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src_hook_script = os.path.join(script_dir, "push_prompt_log.py")
    
    if not os.path.exists(src_hook_script):
        # Backup lookup if run from other cwd
        src_hook_script = os.path.join(os.getcwd(), "client", "push_prompt_log.py")

    if not os.path.exists(src_hook_script):
        print(f"Error: Cannot find push_prompt_log.py at {src_hook_script}. Please run inside client folder or project root.")
        sys.exit(1)

    try:
        shutil.copy2(src_hook_script, HOOKS_SCRIPT_DEST)
        print(f"Copied hook script to {HOOKS_SCRIPT_DEST}")
    except Exception as e:
        print(f"Error copying hook script: {e}")
        sys.exit(1)

    # 3. Create or merge prompt_logger_config.json
    config_data = {}
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as cf:
                config_data = json.load(cf)
        except Exception:
            pass

    # Update config_data from combined_config (only non-None values)
    for k, v in combined_config.items():
        if v is not None:
            config_data[k] = v

    # Ensure sensible defaults
    if "source_app" not in config_data or not config_data.get("source_app"):
        config_data["source_app"] = install_defaults.get("source_app", "Claude Code")
    if "employee_training_folder_url" not in config_data or not config_data.get("employee_training_folder_url"):
        config_data["employee_training_folder_url"] = install_defaults.get("employee_training_folder_url", "https://drive.google.com/drive/folders/default-employee-training-folder")

    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as cf:
            json.dump(config_data, cf, indent=2, ensure_ascii=False)
        print(f"Updated configuration details in {CONFIG_PATH}")
    except Exception as e:
        print(f"Error writing configuration file: {e}")
        sys.exit(1)

    # 4. Detect command format and merge settings.json
    hook_command = detect_os_command()
    merge_settings(hook_command)

    # 5. Success Message
    print("\nInstalled Claude prompt logger hook successfully.")
    print(f"   Config:   {CONFIG_PATH}")
    print(f"   Hook:     {HOOKS_SCRIPT_DEST}")
    print(f"   Settings: {SETTINGS_PATH}")
    print("\nTip: Run 'python client/install_hook.py --test' to verify connectivity to your backend.")

if __name__ == "__main__":
    main()
