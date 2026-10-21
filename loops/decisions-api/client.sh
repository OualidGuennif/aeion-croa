#!/usr/bin/env bash
# Decisions API client: reads a decision or proposes one. Refuses to run unless enabled; reads its
# secret from env.local itself and never prints it. Spec: knowledge/operations/loops.md
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
setting() { grep -E "^$1=" "$ROOT/env.local" 2>/dev/null | tail -1 | cut -d= -f2- | sed 's/[[:space:]]*#.*$//; s/[[:space:]]*$//'; }

[[ "$(setting DECISION_API_ENABLED)" == true ]] || { echo "Decisions API disabled (DECISION_API_ENABLED)" >&2; exit 3; }
URL="$(setting DECISION_API_URL)"; SECRET="$(setting DECISION_API_SECRET)"
[[ -n "$URL" && -n "$SECRET" && "$SECRET" != "???" ]] || { echo "Decisions API not configured in env.local" >&2; exit 3; }

case "${1:-}" in
    get)     [[ -n "${2:-}" ]] || exit 64
             curl -fsS --max-time 15 -H "Authorization: Bearer $SECRET" --get --data-urlencode "topic=$2" "$URL/decisions" ;;
    propose) [[ $# -eq 4 ]] || { echo "usage: client.sh propose <topic> <proposal> <reason>" >&2; exit 64; }
             body="$(python3 -c 'import json,sys; print(json.dumps({"topic": sys.argv[1], "proposal": sys.argv[2], "reason": sys.argv[3], "proposed_by": "agent"}))' "$2" "$3" "$4")"
             curl -fsS --max-time 15 -H "Authorization: Bearer $SECRET" -H "Content-Type: application/json" -d "$body" "$URL/decisions" ;;
    *)       echo "usage: client.sh get <topic> | propose <topic> <proposal> <reason>" >&2; exit 64 ;;
esac
