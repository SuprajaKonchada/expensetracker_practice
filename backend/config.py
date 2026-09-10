"""Environment-driven configuration. Keeps environment-specific values out of business logic."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.environ.get("EXPENSE_TRACKER_DB_PATH", os.path.join(BASE_DIR, "expense_tracker.db"))
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "5000"))
DEBUG = os.environ.get("FLASK_DEBUG", "false").strip().lower() in ("1", "true", "yes")

# AI Expense Assistant model backend: the Claude Agent SDK, which spawns the local `claude`
# CLI as a subprocess and reuses ITS existing login session — no ANTHROPIC_API_KEY is read or
# required here. IMPORTANT: this still costs real money/quota per request, billed against
# whatever Claude plan the `claude` CLI is logged into on the machine running this backend
# (shared with normal Claude Code usage) — this is not free/local in the way Ollama was.
# Overridable via env var (e.g. to a cheaper model like "claude-haiku-4-5").
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-5")
