#!/usr/bin/env python3
"""Negative tests for client.sh: the bearer never reaches a command line, plain HTTP is refused,
and a disabled or unconfigured client calls nothing. Each case runs a copy of the script in a
temporary root with a fake settings file; no real secret is read.

Run with: python3 loops/decisions-api/test_client.py
Spec: knowledge/operations/loops.md
"""
import http.server
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

CLIENT = Path(__file__).resolve().parent / "client.sh"
SECRET = "fake-secret-for-tests"
# A fake curl that records its arguments and its stdin, then answers like a server.
FAKE_CURL = '#!/usr/bin/env bash\nprintf "%s\\n" "$@" > "$CURL_ARGS"\ncat > "$CURL_STDIN"\necho "{}"\n'
failures, passes = [], 0


def check(name, ok, detail=""):
    global passes
    if ok:
        passes += 1
    else:
        failures.append(f"{name}: {detail}")


def sandbox(settings):
    root = Path(tempfile.mkdtemp())
    (root / "loops/decisions-api").mkdir(parents=True)
    shutil.copy(CLIENT, root / "loops/decisions-api/client.sh")
    (root / ("env" + ".local")).write_text(settings)
    (root / "bin").mkdir()
    (root / "bin/curl").write_text(FAKE_CURL)
    (root / "bin/curl").chmod(0o755)
    return root


def run(root, *args, fake_curl=True):
    env = dict(os.environ, CURL_ARGS=str(root / "args"), CURL_STDIN=str(root / "stdin"),
               NO_PROXY="127.0.0.1", no_proxy="127.0.0.1")
    if fake_curl:
        env["PATH"] = f"{root / 'bin'}:{env['PATH']}"
    return subprocess.run(["bash", str(root / "loops/decisions-api/client.sh"), *args],
                          capture_output=True, text=True, env=env, timeout=30)


def settings(url="https://decisions.example.invalid/api", secret=SECRET, enabled="true"):
    return f"DECISION_API_ENABLED={enabled}\nDECISION_API_URL={url}\nDECISION_API_SECRET={secret}\n"


# The bearer travels on curl's stdin, never in its arguments, and only over HTTPS.
for args in (["get", "release-freeze"], ["propose", "topic", "a proposal", "a reason"]):
    root = sandbox(settings())
    r = run(root, *args)
    argv = (root / "args").read_text() if (root / "args").exists() else ""
    stdin = (root / "stdin").read_text() if (root / "stdin").exists() else ""
    check(f"{args[0]} succeeds", r.returncode == 0, r.stderr)
    check(f"{args[0]} keeps the secret out of curl's arguments", SECRET not in argv, argv)
    check(f"{args[0]} sends the header on stdin", stdin == f"Authorization: Bearer {SECRET}\n", repr(stdin))
    check(f"{args[0]} restricts curl to HTTPS", "--proto\n=https\n" in argv, argv)
    check(f"{args[0]} prints no secret", SECRET not in r.stdout + r.stderr)

# Disabled, missing or placeholder credentials: refused before curl runs.
for name, text in (("disabled", settings(enabled="false")), ("missing secret", settings(secret="")),
                   ("placeholder secret", settings(secret="???")), ("missing URL", settings(url=""))):
    root = sandbox(text)
    r = run(root, "get", "release-freeze")
    check(f"{name} exits 3", r.returncode == 3, f"exit {r.returncode}")
    check(f"{name} never calls curl", not (root / "args").exists())


# Real curl and a plain HTTP server: the request is refused before anything is sent.
class Recorder(http.server.BaseHTTPRequestHandler):
    seen = []

    def do_GET(self):
        Recorder.seen.append(self.headers.get("Authorization"))
        self.send_response(200)
        self.end_headers()

    def log_message(self, *args):
        pass


server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Recorder)
threading.Thread(target=server.serve_forever, daemon=True).start()
root = sandbox(settings(url=f"http://127.0.0.1:{server.server_address[1]}/api"))
r = run(root, "get", "release-freeze", fake_curl=False)
server.shutdown()
check("plain HTTP is refused", r.returncode != 0, f"exit {r.returncode}")
check("plain HTTP server receives nothing", Recorder.seen == [], repr(Recorder.seen))
check("the refusal prints no secret", SECRET not in r.stdout + r.stderr)

for f in failures:
    print("FAIL:", f)
print(f"{passes} passed, {len(failures)} failed")
sys.exit(1 if failures else 0)
