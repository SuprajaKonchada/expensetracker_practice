"""Environment-driven configuration. Keeps environment-specific values out of business logic."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.environ.get("EXPENSE_TRACKER_DB_PATH", os.path.join(BASE_DIR, "expense_tracker.db"))
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "5000"))
DEBUG = os.environ.get("FLASK_DEBUG", "false").strip().lower() in ("1", "true", "yes")
