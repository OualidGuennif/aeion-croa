#!/usr/bin/env python3
# Spec: knowledge/policies/security.md
"""PreToolUse hook on Read, Edit, Write and Grep: refuses to open a secret file (exit 2)."""
import json
import re
import sys
from pathlib import PurePosixPath

TEMPLATES = {".env.example", ".env.sample", ".env.template", ".env.dist", "env.example.local"}
SECRET_NAMES = {"auth.json", "credentials", "credentials.json", "id_rsa", "id_ed25519", "env.local"}

tool_input = json.load(sys.stdin).get("tool_input", {})
name = PurePosixPath(tool_input.get("file_path") or tool_input.get("path") or "").name
if name not in TEMPLATES and (bool(re.fullmatch(r"\.env(\..+)?", name)) or name in SECRET_NAMES
                              or name.endswith((".pem", ".key"))):
    print(f"Blocked by .claude/hooks/guard-path.py: {name} holds secrets and is never opened "
          f"(knowledge/policies/security.md).", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
