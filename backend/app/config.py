import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

APP_NAME = os.getenv("APP_NAME", "Claude Prompt Logger")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./prompt_logger.db")
PROMPT_LOG_API_KEY = os.getenv("PROMPT_LOG_API_KEY", "")
TIMEZONE = os.getenv("TIMEZONE", "Asia/Ho_Chi_Minh")
