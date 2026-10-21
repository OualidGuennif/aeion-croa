#!/usr/bin/env python3
"""Tests for the hooks in this folder: each gets a sample event on stdin.

Run with: python3 .claude/hooks/test_hooks.py
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HOOKS = Path(__file__).resolve().parent
ROOT = HOOKS.parents[1]
RUN = str(abs(hash(tempfile.mkdtemp())))
failures, passes = [], 0


def run_hook(name, tool_input, cwd=ROOT, **extra):
    event = json.dumps({"tool_input": tool_input, **extra})
    return subprocess.run([sys.executable, str(cwd / ".claude/hooks" / name)], input=event,
                          capture_output=True, text=True, cwd=cwd)


def expect(label, result, code, stdout_has=None):
    global passes
    if result.returncode == code and (stdout_has is None or stdout_has in result.stdout):
        passes += 1
    else:
        failures.append(f"{label}: exit {result.returncode}, stdout {result.stdout!r}, stderr {result.stderr!r}")


# guard-bash: refused, asked, allowed.
for command in ["cat .env", "cat env.local", "printenv", "cat /proc/1/environ", "python3 -c 'import os; print(os.environ)'", "node -e 'console.log(process.env)'",
                "python3 <<'EOF'\nimport os\nprint(os.environ)\nEOF", "echo 'print(dict(os.environ))' | python3",
                "python3 -c 'from os import environ; print(environ)'", "cd /proc/self && cat environ",
                "npx tsx -e 'console.log(process.env)'", "ruby -e 'p ENV.to_h'", "docker exec cyclone-brain-1 env",
                "sudo env", "env -0", "/usr/bin/env", "export", "declare -x",
                "docker exec -u root cyclone-brain-1 env", "sudo -u root env", "env > /tmp/x", "  env",
                "sh -c env", "(env)", "time env", "ssh vps 'env'", "awk 'BEGIN{for(k in ENVIRON) print k}'",
                "python3 -c 'import os; print(os.environb)'", "jq -n env",
                "env\necho done", "bash <<X\nenv\nX", "cd /tmp\nset\nls", "env 2>&1", "env 1>f",
                "env -u HOME | sort", "env --", "env FOO=1 > out.txt", "xargs env </dev/null", "declare",
                "typeset -x", "ps eww", "ps auxe", "docker exec c sh -c declare", "su -c env",
                "(env)|sort", "echo hi;(env)", "true&&(env)", "ssh vps 'cd /app\ndocker exec cyclone-brain-1 env'",
                "bash -c 'cd /tmp\nenv'", "bash -lc env", "sh -xc env", "bash -c -- env",
                "docker compose exec brain env", "docker container exec c env", "xargs -n 1 env",
                "xargs -I {} env", "ssh vps -- env", "ps -E", "ps -wwE", "docker compose run --rm -v a:b brain env",
                "docker compose -f compose.yml exec brain env", "docker compose --project-directory /x exec brain env",
                "docker --context x exec c env", "for c in a b; do docker exec $c env; done",
                "while read c; do docker exec $c env; done < f", "if true; then env; fi", "{ env; }",
                "docker compose -f x config", "kubectl exec pod -- env",
                "ssh host 'cd /app && docker compose config'", "bash -c 'docker compose config'",
                "ssh -o ConnectTimeout=10 host \\\n'docker exec c env | grep KEY'", "docker compose exec \\\nbrain env",
                "ssh host -t 'docker exec c env'", "docker inspect --format '{{json .}}' c",
                "docker inspect $(docker ps -q -f name=brain)", "cd /app && docker compose -f compose.yml ps && docker inspect c",
                "docker --context x inspect c", "docker inspect -f '{{json .Config}}' c", "docker inspect --format='{{.Config.Env}}' c",
                "cat <<'EOF' | ssh host bash\nenv\nEOF", "ssh h " * 1200 + "env",
                "docker inspect --format json c", "docker inspect -f json c", "docker inspect --format=json c",
                "docker inspect --format '' c", "docker inspect -f '{{. | json}}' c",
                "docker inspect $(docker ps -q\n)", "docker inspect $(docker ps -q;)", "docker inspect -f '{{- json . -}}' c", "docker inspect web",
                "docker compose config", "git push --force origin main", "git commit --no-verify -m x"]:
    expect(f"bash deny: {command}", run_hook("guard-bash.py", {"command": command}), 2)
expect("bash ask: mentions a secret", run_hook("guard-bash.py", {"command": "ls -la .env"}), 0, '"ask"')
for command in ["git status --short", "git commit -m 'the environment check'",
                "grep -rn environment knowledge", "/usr/bin/env python3 tools/x.py", "npm config set registry x", "git commit -m 'block env'", "ps -ef", "ps aux",
                "ps -o etime -p 1", "declare -a arr", "export FOO=bar", "python3 - <<'EOF'\nprint(env)\nEOF",
                "gh pr create --body 'dumps (env)'", "ps -eo pid,etime,args", "ps -C node", "ps axo pid,etime",
                "docker compose logs brain | grep -i config", "docker compose config -q", "ssh host python3 - <<'EOF'\nprint(sorted(set([1])))\nEOF",
                "docker compose config --services", "command -v env", "docker inspect -f '{{.Config.Image}}' c",
                "docker inspect -f '{{.Config.Entrypoint}}' c", "docker inspect -f '{{.State.Health.Status}}' c", "docker inspect $(docker ps -q) --format '{{.Name}} {{.State.Status}}'",
                "echo $(date) && git status", "echo $(date;) && git status", "gh pr create --body \"$(cat <<'EOF'\ndumps (env)\nEOF\n)\"", "cat env.example.local", "npm test", "set -euo pipefail"]:
    result = run_hook("guard-bash.py", {"command": command})
    expect(f"bash allow: {command}", result, 0)
    if '"ask"' in result.stdout:
        failures.append(f"bash allow asked instead: {command}")

# guard-path: secrets refused, templates allowed.
for path in ["/repo/.env", "/repo/env.local", "/x/server.pem", "/h/auth.json"]:
    expect(f"path deny: {path}", run_hook("guard-path.py", {"file_path": path}), 2)
for path in ["/repo/.env.example", "/repo/env.example.local", str(ROOT / "AGENTS.md")]:
    expect(f"path allow: {path}", run_hook("guard-path.py", {"file_path": path}), 0)

# sign-off: in a throwaway repo, a code change without its doc blocks once, then passes.
tmp = Path(tempfile.mkdtemp())
for rel in (".claude/hooks/sign-off.py", "tools/knowledge/doc-links"):
    (tmp / rel).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / rel, tmp / rel)
(tmp / "knowledge/components").mkdir(parents=True)
(tmp / "work").mkdir()
(tmp / "src").mkdir()
(tmp / "knowledge/components/x.md").write_text("---\ntype: Component\nsources:\n  - id: c\n    resource: ../../src/a.ts\n---\n")
(tmp / "src/a.ts").write_text("export const a = 1;\n")
(tmp / "work/current.md").write_text("# Current work\n")
git = ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid"]
for args in (["init", "-q", "-b", "main"], ["add", "."], ["commit", "-qm", "base"], ["switch", "-qc", "task/x"]):
    subprocess.run(git + args, cwd=tmp, capture_output=True)
(tmp / "src/a.ts").write_text("export const a = 2;\n")


def stop(session, active=False):
    return subprocess.run([sys.executable, str(tmp / ".claude/hooks/sign-off.py")], cwd=tmp, capture_output=True,
                          text=True, input=json.dumps({"session_id": f"{session}-{RUN}", "stop_hook_active": active}))


expect("sign-off: a session that edited nothing passes", stop("idle"), 0)
if '"block"' in stop("idle").stdout:
    failures.append("sign-off blocked a session that edited nothing")
with (Path(tempfile.gettempdir()) / f"claude-edited-busy-{RUN}").open("a") as f:
    f.write("src/a.ts\n")
first = stop("busy")
expect("sign-off: code without its doc blocks", first, 0, '"decision": "block"')
expect("sign-off: names the doc", first, 0, "knowledge/components/x.md")
if '"block"' in stop("busy").stdout:
    failures.append("sign-off blocked twice on the same findings")

# session-start: at most 25 lines.
result = subprocess.run([sys.executable, str(HOOKS / "session-start.py")], capture_output=True, text=True, cwd=ROOT)
expect("session-start runs", result, 0, "git status")
if len(result.stdout.strip().split("\n")) > 25:
    failures.append("session-start printed more than 25 lines")

print(f"hook tests: {passes} passed, {len(failures)} failed")
for f in failures:
    print(f"  FAIL {f}")
sys.exit(1 if failures else 0)
