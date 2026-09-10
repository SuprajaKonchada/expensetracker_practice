#!/usr/bin/env python3
"""PreToolUse hook for the Bash tool: blocks a fixed set of dangerous commands
before they execute.

Stdlib only, no external dependencies. Reads the hook's JSON payload from
stdin, looks at tool_input.command, and either:
  - blocks (prints "BLOCKED..." to stderr, exit 2), or
  - allows (prints a short confirmation to stdout, exit 0).

Fails open (exit 0) on invalid JSON or a missing command, since this hook's
job is to catch known-dangerous commands, not to gate all Bash usage.
"""
import json
import re
import sys

# Windows consoles often default stdout/stderr to a legacy codepage that
# can't encode the emoji in the blocked-command message; force UTF-8 so it
# renders correctly instead of falling back to an escaped \U... literal.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8")
        except (ValueError, OSError):
            pass

# Each pattern is matched against a normalized (lowercased, whitespace-collapsed)
# copy of the command. Quotes are stripped before matching so `git push` inside
# quotes still matches, and patterns tolerate extra flags/spacing via `.*`.
DANGEROUS_PATTERNS = [
    (r"\bgit\s+push\b.*(--force\b|(?<!\S)-f(\s|$))",
     "git push --force (force push can overwrite remote history)"),
    (r"\bgit\s+reset\b.*--hard\b",
     "git reset --hard (discards uncommitted work)"),
    (r"\bdrop\s+table\b",
     "DROP TABLE (destructive SQL schema change)"),
    (r"\bdelete\s+from\s+\S+(?!.*\bwhere\b).*",
     "DELETE FROM without WHERE (unscoped delete)"),
    (r"\bgit\s+commit\b.*--no-verify\b",
     "git commit --no-verify (bypasses commit hooks)"),
    (r"\bgit\s+push\b.*--no-verify\b",
     "git push --no-verify (bypasses push hooks)"),
]

_COMPILED = [(re.compile(p, re.IGNORECASE | re.DOTALL), reason) for p, reason in DANGEROUS_PATTERNS]

# Shell operators that end a single logical command, so flags don't "leak"
# across chained/piped commands when scanning for rm's flags.
_COMMAND_SEPARATORS = re.compile(r"[;\n]|&&|\|\|?")


def normalize(command: str) -> str:
    """Lowercase, strip quote characters, and collapse whitespace so shell
    quoting/spacing differences don't defeat pattern matching."""
    stripped = command.replace('"', " ").replace("'", " ").replace("`", " ")
    collapsed = re.sub(r"\s+", " ", stripped)
    return collapsed.strip().lower()


def has_rm_rf(normalized: str) -> bool:
    """Detect `rm -rf`-equivalent invocations, including combined flags
    (-rf, -fr), separated flags (-r -f), and long options (--recursive
    --force), regardless of order."""
    for segment in _COMMAND_SEPARATORS.split(normalized):
        tokens = segment.split()
        for i, token in enumerate(tokens):
            if token != "rm":
                continue
            recursive = force = False
            for flag in tokens[i + 1:]:
                if flag == "--recursive":
                    recursive = True
                elif flag == "--force":
                    force = True
                elif flag.startswith("-") and not flag.startswith("--") and len(flag) > 1:
                    if "r" in flag[1:]:
                        recursive = True
                    if "f" in flag[1:]:
                        force = True
            if recursive and force:
                return True
    return False


def find_violation(command: str):
    normalized = normalize(command)

    if has_rm_rf(normalized):
        return "rm -rf (recursive force delete)"

    for pattern, reason in _COMPILED:
        if pattern.search(normalized):
            return reason
    return None


def main() -> int:
    raw = sys.stdin.read()

    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return 0

    if not isinstance(payload, dict):
        return 0

    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return 0

    command = tool_input.get("command")
    if not isinstance(command, str) or not command.strip():
        return 0

    reason = find_violation(command)
    if reason:
        print(f"🚫 BLOCKED by pre-tool-use hook: {reason}", file=sys.stderr)
        return 2

    print("pre-tool-use hook: command looks safe, proceeding.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
