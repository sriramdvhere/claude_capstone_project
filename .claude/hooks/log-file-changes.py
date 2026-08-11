"""
PostToolUse hook — logs every Write/Edit tool call to .claude/activity-log.txt

How it works:
  1. Claude Code sends JSON on stdin after every Write or Edit tool call.
  2. This script reads that JSON, extracts the file path, and appends a
     timestamped line to the log.
  3. Always exits 0 so the hook never blocks Claude on failure.

Stdin JSON shape (PostToolUse):
  {
    "hook_event_name": "PostToolUse",
    "tool_name": "Write" or "Edit",
    "tool_input": { "file_path": "...", ... },
    "tool_result": { ... },
    "cwd": "...",
    ...
  }
"""
import sys
import json
import os
from datetime import datetime

try:
    data = json.load(sys.stdin)

    tool = data.get("tool_name", "")
    file_path = data.get("tool_input", {}).get("file_path", "<unknown>")

    # CLAUDE_PROJECT_DIR is injected by Claude Code as an env var;
    # fall back to cwd from the hook payload when running the script manually.
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd", ".")
    log_path = os.path.join(project_dir, ".claude", "activity-log.txt")

    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} | {tool:<5} | {file_path}\n")

except Exception:
    pass  # Never let a logging hook crash Claude's workflow

sys.exit(0)
