#!/usr/bin/env python3
# Spec: knowledge/policies/security.md
"""PreToolUse hook on Bash: blocks commands that would expose a secret or bypass a guard.

Input: the hook event as JSON on stdin; tool_input.command is the command. Output: exit 2 with the
reason on stderr blocks it; a JSON "ask" decision asks a human; exit 0 lets it run. A seatbelt,
not a guarantee: the rules are in knowledge/policies/security.md.
"""
import json
import re
import shlex
import sys
from pathlib import PurePosixPath

TEMPLATES = {".env.example", ".env.sample", ".env.template", ".env.dist", "env.example.local"}
READERS = {"cat", "less", "more", "head", "tail", "grep", "rg", "awk", "sed", "strings", "base64",
           "xxd", "od", "source", ".", "cp", "scp", "rsync", "jq", "python3", "python", "node", "vim", "nano"}
SECRET_NAMES = {"auth.json", "credentials", "credentials.json", "id_rsa", "id_ed25519", "env.local"}


def deny(reason):
    print(f"Blocked by .claude/hooks/guard-bash.py: {reason}", file=sys.stderr)
    sys.exit(2)


def ask(reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask",
                                             "permissionDecisionReason": reason}}))
    sys.exit(0)


def is_secret(name):
    if name in TEMPLATES:
        return False
    return bool(re.fullmatch(r"\.env(\..+)?", name)) or name in SECRET_NAMES or name.endswith((".pem", ".key"))


# Environment dumps hold keys. The command is split into simple commands (newlines, ; & | && || and
# parentheses outside quotes; redirections dropped; heredoc bodies only when a shell reads them);
# wrappers are unwrapped (sudo, time, xargs, nohup, docker [compose] exec/run, kubectl exec, ssh,
# sh -c/-lc, su -c, shell keywords,
# recursively); then refused: printenv; env with no program to run;
# declare, typeset, export and set that print variables; ps with BSD e or -E (process environments). And
# anywhere in the command: the words environ, environb and ENVIRON; an interpreter together with
# process.env, Deno.env or ENV; jq with env or $ENV. A seatbelt: search for these names with the
# Grep tool, and put prose that names them in a file.
ENV_WORD = re.compile(r"\b(environ|environb|ENVIRON)\b")
INTERPRETER = re.compile(r"\b(python3?|node|deno|bun|tsx|ts-node|npx|ruby|perl)\b")
ENV_IN_CODE = re.compile(r"process\.env\b|Deno\.env\b|%ENV\b|\bENV\b")
JQ_ENV = re.compile(r"\bjq\b.*(\benv\b|\$ENV\b)", re.S)
SEPARATOR_CHARS, REDIRECT_CHARS = set(";&|()\n"), set("<>&")
WRAPPERS = {"sudo", "doas", "time", "nohup", "nice", "xargs", "command", "builtin", "exec", "watch",
            "timeout", "stdbuf", "setsid", "chroot"}
DOCKER_VALUE_FLAGS = {"-u", "--user", "-e", "--env", "-w", "--workdir", "--env-file", "--detach-keys",
                      "-v", "--volume", "--network", "--entrypoint", "-p", "--publish", "--name", "-l",
                      "--label", "--mount", "--platform", "--pull", "--cpus", "-m", "--memory", "--index"}
VALUE_FLAGS = {"sudo": {"-u", "-g", "-h", "-p", "-C", "-D", "-R", "-T", "-U"},
               "docker": DOCKER_VALUE_FLAGS,
               "ssh": {"-i", "-p", "-o", "-l", "-F", "-J", "-L", "-R", "-D", "-E", "-b", "-c", "-m", "-O",
                       "-Q", "-S", "-W", "-w", "-B"},
               "ps": {"-o", "-p", "-u", "-U", "-G", "-g", "-t", "-O", "-q"},
               "env": {"-u", "--unset", "-C", "--chdir", "-S", "--split-string"},
               "xargs": {"-n", "-I", "-i", "-L", "-l", "-P", "-s", "-d", "-E", "-a", "--max-args",
                         "--replace", "--max-lines", "--max-procs", "--delimiter", "--arg-file"},
               "timeout": {"-s", "--signal", "-k", "--kill-after"}, "nice": {"-n"}}
SHELLS = {"sh", "bash", "zsh", "dash", "ksh"}
SHELL_KEYWORDS = {"do", "then", "else", "elif", "if", "while", "until", "{", "}", "!", "time"}
DOCKER_GLOBAL_VALUE_FLAGS = {"-f", "--file", "-p", "--project-name", "--project-directory", "--context",
                             "-c", "-H", "--host", "--env-file", "--profile", "--log-level", "--config",
                             "--ansi", "--progress", "--parallel"}
HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1")
SHELL_CONSUMER = re.compile(r"\b(sh|bash|zsh|dash|ksh|ssh|exec)\b")


def without_inert_heredocs(command):
    """Drops heredoc bodies fed to anything but a shell: a script's text is not a command line."""
    out, end, keep = [], None, True
    for line in command.split("\n"):
        if end is not None:
            if keep:
                out.append(line)
            if line.strip() == end:
                end = None
            continue
        out.append(line)
        m = HEREDOC.search(line)
        if m:
            before, after = line[:m.start()], line[m.end():]
            consumer = before + (after if after.lstrip().startswith("|") else "")
            end = m.group(2)
            keep = bool(SHELL_CONSUMER.search(consumer)) and not INTERPRETER.search(consumer)
    return "\n".join(out)


def tokens_of(text):
    try:
        lexer = shlex.shlex(text, posix=True, punctuation_chars=";&|()<>\n")
        lexer.whitespace, lexer.whitespace_split, lexer.commenters = " \t\r", True, ""
        tokens = list(lexer)
    except ValueError:
        tokens = re.findall(r"[;&|()<>\n]+|[^\s;&|()<>]+", text)
    # A parenthesis glued to other punctuation (";)", "))", ");") stands on its own.
    out = []
    for t in tokens:
        if len(t) > 1 and set(t) <= set(";&|()<>\n") and set(t) & set("()"):
            out += [p for p in re.split(r"([()])", t) if p]
        else:
            out.append(t)
    return out


def simple_commands(command):
    current, skip_next, outer = [], False, []
    for w in tokens_of(without_inert_heredocs(command.replace("\\\n", " "))):
        chars = set(w)
        # $( ... ) is a command of its own; its value stands in the outer command.
        if w == "(" and current and current[-1].endswith("$") and not skip_next:
            current[-1] = current[-1] + "(...)"
            outer.append(current)
            current = []
            continue
        if outer and w[:1] == ")" and chars <= SEPARATOR_CHARS | REDIRECT_CHARS:
            while w[:1] == ")" and outer:
                yield current
                current = outer.pop()
                w = w[1:]
            if not w:
                continue
            chars = set(w)
        if skip_next:
            skip_next = False
        elif w and chars <= SEPARATOR_CHARS | REDIRECT_CHARS and chars & SEPARATOR_CHARS - {"&"}:
            yield current
            current = []
        elif w and chars <= REDIRECT_CHARS and chars & {"<", ">"}:
            skip_next = True
            if current and current[-1].isdigit():
                current.pop()
        elif w and chars <= {"&"}:
            yield current
            current = []
        else:
            current.append(w)
    yield current
    yield from reversed(outer)


def skip_options(words, tool):
    takes_value = VALUE_FLAGS.get(tool, set())
    while words and words[0].startswith("-"):
        flag = words.pop(0)
        if flag == "--":
            break
        if flag in takes_value and words:
            words.pop(0)
    return words


def docker_subcommand(words):
    """(subcommand, the words after it) of a docker or docker compose command line, global options skipped."""
    rest = list(words[1:])
    while rest:
        if rest[0] in ("compose", "container"):
            rest.pop(0)
        elif rest[0] in DOCKER_GLOBAL_VALUE_FLAGS and len(rest) > 1:
            rest = rest[2:]
        elif rest[0].startswith("-"):
            rest.pop(0)
        else:
            return rest[0], rest[1:]
    return None, []


CONFIG_LISTS = {"-q", "--quiet", "--services", "--volumes", "--images", "--profiles", "--networks"}


def compose_config(command):
    """docker compose config prints the configuration with the secrets filled in (-q only validates)."""
    for words in simple_commands(command):
        words = program(words)
        if words and PurePosixPath(words[0]).name in ("docker", "docker-compose", "podman"):
            sub, rest = docker_subcommand(words)
            if sub == "config" and not (CONFIG_LISTS & set(rest)):
                return True
        elif words and words[0] == "<script>" and compose_config(words[1]):
            return True
    return False


def shell_script(args):
    """The -c script of a shell's arguments (-c, -lc, -xc ...), or None."""
    for i, a in enumerate(args):
        if a.startswith("-") and not a.startswith("--") and "c" in a[1:]:
            rest = [x for x in args[i + 1:] if x != "--"]
            return rest[0] if rest else ""
    return None


def program(words):
    """The program a simple command runs, after assignments and wrappers; a nested script is checked whole."""
    words = list(words)
    while words:
        w = PurePosixPath(words[0]).name
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", words[0]) or words[0] in SHELL_KEYWORDS:
            words.pop(0)
        elif w == "command" and len(words) > 1 and words[1] in ("-v", "-V"):
            return []
        elif w in WRAPPERS:
            words = skip_options(words[1:], w)
            if w in ("timeout", "nice") and words and re.fullmatch(r"[\d.]+[smhd]?", words[0]):
                words.pop(0)
        elif w in ("docker", "docker-compose", "podman"):
            sub, rest = docker_subcommand(words)
            if sub not in ("exec", "run"):
                break
            words = skip_options(rest, "docker")[1:]
        elif w == "kubectl" and words[1:2] == ["exec"]:
            words = words[words.index("--") + 1:] if "--" in words else []
        elif w == "ssh":
            words = skip_options(skip_options(words[1:], "ssh")[1:], "ssh")
            if words:
                return ["<script>", " ".join(words)]
        elif w == "su":
            script = shell_script(words[1:])
            return ["<script>", script] if script is not None else []
        elif w in SHELLS:
            script = shell_script(words[1:])
            return ["<script>", script] if script is not None else words
        else:
            break
    return words


def prints_environment(words):
    if not words:
        return False
    name, args = PurePosixPath(words[0]).name, words[1:]
    if name == "<script>":
        return env_dump(args[0])
    if name == "printenv":
        return True
    if name == "env":
        rest = skip_options(list(args), "env")
        while rest and (re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", rest[0]) or rest[0] in ("-", "--")):
            rest.pop(0)
        rest = skip_options(rest, "env")
        return not rest
    if name in ("declare", "typeset"):
        return not args or any(a.startswith("-") and set(a[1:]) & set("xpF") for a in args)
    if name == "export":
        return not args or args == ["-p"]
    if name == "set":
        return not args
    if name == "ps":
        # BSD "e" is a letter cluster in the first argument (ps eww, ps auxe); -E is macOS's flag.
        if args and re.fullmatch(r"[a-zA-Z]+", args[0]) and "e" in args[0]:
            return True
        return any(re.fullmatch(r"-[a-zA-Z]*E[a-zA-Z]*", a) for a in args)
    return False


def env_dump(command):
    if ENV_WORD.search(command) or JQ_ENV.search(command):
        return True
    if INTERPRETER.search(command) and ENV_IN_CODE.search(command):
        return True
    return any(prints_environment(program(words)) for words in simple_commands(command))


INSPECT_DUMP_FORMAT = re.compile(r"\.Env\b|\{\{-?\s*(json\s+)?\.(Config)?\s*(\|\s*json\s*)?-?\}\}|^\s*(json)?\s*$")


def docker_inspect_dump(command):
    """docker inspect shows a container's environment unless a narrow --format leaves it out."""
    for words in simple_commands(command):
        words = program(words)
        if words and words[0] == "<script>":
            if docker_inspect_dump(words[1]):
                return True
            continue
        if not words or PurePosixPath(words[0]).name not in ("docker", "podman"):
            continue
        sub, rest = docker_subcommand(words)
        if sub != "inspect":
            continue
        fmt = None
        for i, a in enumerate(rest):
            if a in ("-f", "--format") and i + 1 < len(rest):
                fmt = rest[i + 1]
            elif a.startswith("--format="):
                fmt = a.split("=", 1)[1]
        if fmt is None or INSPECT_DUMP_FORMAT.search(fmt):
            return True
    return False


def refuses(check, command):
    """Runs one check; a command nested so deep that the check cannot finish is refused."""
    try:
        return check(command)
    except RecursionError:
        return True


try:
    event = json.load(sys.stdin)
    command = event.get("tool_input", {}).get("command", "")
    if not isinstance(command, str):
        raise TypeError("command is not a string")
except Exception:
    deny("the hook input could not be read; refusing rather than guessing.")
tokens = [t for t in re.split(r"[\s'\"=;&|<>()`]+", command) if t]
secrets = sorted({PurePosixPath(t).name for t in tokens if is_secret(PurePosixPath(t).name)})

# Secret files: reading one is refused; any other mention is a human's call.
if secrets:
    if READERS & set(tokens):
        deny(f"it reads a secret file ({', '.join(secrets)}). Secrets are never read or printed.")
    ask(f"The command mentions a secret file ({', '.join(secrets)}).")

# Environment dumps hold keys.
if "printenv" in tokens or refuses(env_dump, command):
    deny("it prints an environment, which holds keys (to search for a name, use the Grep tool; for prose, write it to a file).")
if refuses(docker_inspect_dump, command):
    deny("docker inspect without a narrow --format shows the container's environment.")
if refuses(compose_config, command):
    deny("docker compose config prints the configuration with the secrets filled in.")

# History and checks are not bypassed.
if re.search(r"\bgit\s+push\b", command) and re.search(r"\s(-f|--force|--force-with-lease)(\s|=|$)", command):
    deny("force-pushing rewrites shared history.")
if re.search(r"\bgit\b", command) and "--no-verify" in tokens:
    deny("--no-verify skips the pre-commit checks.")
sys.exit(0)
