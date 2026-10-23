#!/usr/bin/env python3
"""Validate an assessment packet and its staged evidence without executing the target.

Spec: knowledge/components/croa-audit.md
SPDX-License-Identifier: MIT
"""
import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import re
import stat
import string
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[2]
MAX_FILE = 1024 * 1024
MAX_TOTAL = 16 * MAX_FILE
KINDS = {"code", "configuration", "executed_test", "c5_log", "system_log", "assessment"}
SUFFIXES = {".json", ".jsonl", ".md", ".txt", ".log", ".csv"}
SENSITIVE = {"auth.json", "credentials.json", "id_rsa", "id_ed25519"}


class AuditError(ValueError):
    pass


def catalog():
    return json.loads((ROOT / "catalog/checks.json").read_text(encoding="utf-8"))


def fields(value, expected, label):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise AuditError("Invalid fields in " + label)


def text(value, label, nullable=False):
    if value is None and nullable:
        return
    if not isinstance(value, str) or not value.strip() or len(value) > 4000:
        raise AuditError("Invalid text in " + label)
    if any(unicodedata.category(c).startswith("C") for c in value):
        raise AuditError("Control characters in " + label)


def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise AuditError("Duplicate JSON key")
        result[key] = value
    return result


def invalid_constant(_value):
    raise AuditError("Non-finite JSON number")


def safe_parts(value):
    text(value, "evidence path")
    parts = value.split("/")
    if len(parts) < 2 or parts[0] != "evidence" or "\\" in value or ":" in value:
        raise AuditError("Evidence must be relative to evidence/")
    if any(not p or p.startswith(".") or p.lower() in SENSITIVE for p in parts):
        raise AuditError("Unsafe evidence path")
    if Path(parts[-1]).suffix.lower() not in SUFFIXES:
        raise AuditError("Unsupported evidence file type")
    return parts


def read_regular(root, parts):
    # Walk descriptors without following links, including intermediate directories.
    directory = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
            os.close(directory)
            directory = child
        descriptor = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                             dir_fd=directory)
        with os.fdopen(descriptor, "rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > MAX_FILE:
                raise AuditError("Input must be a bounded regular file")
            data = stream.read(MAX_FILE + 1)
            if len(data) > MAX_FILE:
                raise AuditError("Input exceeds file limit")
            return data
    finally:
        os.close(directory)


def load_packet(path):
    path = Path(path)
    if path.name.startswith(".") or path.name.lower() in SENSITIVE or path.suffix != ".json":
        raise AuditError("Expected a non-secret .json audit packet")
    try:
        # Only the explicitly selected parent is resolved; the file itself cannot be a link.
        root = path.parent.resolve(strict=True)
        data = read_regular(root, [path.name])
        packet = json.loads(data.decode("utf-8"), object_pairs_hook=pairs,
                            parse_constant=invalid_constant)
        validate(packet, root)
        return packet
    except AuditError:
        raise
    except (OSError, ValueError, RecursionError) as error:
        raise AuditError("Cannot read a valid bounded packet or staged evidence") from error


def validate(packet, root):
    spec = catalog()
    fields(packet, ("schema_version", "upstream", "scope", "assessor", "checks"), "packet")
    if packet["schema_version"] != "aeion.croa.audit/v1" or packet["upstream"] != spec["upstream"]:
        raise AuditError("Unsupported packet schema or upstream revision")
    fields(packet["scope"], ("system", "revision", "boundary", "audit_period", "environment"), "scope")
    for key, value in packet["scope"].items():
        text(value, "scope", nullable=key not in {"system", "environment"})
    if packet["scope"]["environment"] not in {"evaluation", "production"}:
        raise AuditError("Invalid environment")
    fields(packet["assessor"], ("name", "mode", "independence_basis"), "assessor")
    for key, value in packet["assessor"].items():
        text(value, "assessor", nullable=key != "mode")
    if packet["assessor"]["mode"] not in {"self-assessment", "independent-review"}:
        raise AuditError("Invalid assessment mode")
    definitions = {c["id"]: c for c in spec["checks"]}
    checks = packet["checks"]
    if not isinstance(checks, list) or len(checks) != len(definitions):
        raise AuditError("Every catalog check must occur once")
    seen, cache = set(), {}
    for check in checks:
        fields(check, ("id", "status", "notes", "evidence"), "check")
        text(check["id"], "check ID")
        if check["id"] not in definitions or check["id"] in seen:
            raise AuditError("Unknown or duplicate check ID")
        seen.add(check["id"])
        validate_check(check, definitions[check["id"]], root, cache)


def validate_check(check, definition, root, cache):
    text(check["status"], "status")
    text(check["notes"], "notes")
    status = check["status"]
    if status not in {"pass", "fail", "unknown", "not_applicable"}:
        raise AuditError("Unknown finding status")
    if status == "not_applicable" and not definition["allow_not_applicable"]:
        raise AuditError("This check cannot be excluded wholesale")
    refs = check["evidence"]
    if not isinstance(refs, list) or len(refs) > 20 or (status != "unknown" and not refs):
        raise AuditError("Finding requires bounded evidence references")
    kinds = set()
    for ref in refs:
        fields(ref, ("path", "sha256", "kind"), "evidence reference")
        parts = safe_parts(ref["path"])
        text(ref["kind"], "evidence kind")
        text(ref["sha256"], "evidence hash")
        if ref["kind"] not in KINDS or not re.fullmatch("[0-9a-f]{64}", ref["sha256"]):
            raise AuditError("Invalid evidence kind or SHA-256")
        if ref["path"] not in cache:
            data = read_regular(root, parts)
            cache[ref["path"]] = (hashlib.sha256(data).hexdigest(), len(data))
            if sum(size for _, size in cache.values()) > MAX_TOTAL:
                raise AuditError("Evidence exceeds aggregate byte limit")
        if cache[ref["path"]][0] != ref["sha256"]:
            raise AuditError("Staged evidence hash mismatch")
        kinds.add(ref["kind"])
    if status == "pass" and not set(definition["required_kinds"]).issubset(kinds):
        raise AuditError("Passing finding lacks required evidence kinds")
    if status == "not_applicable" and ("assessment" not in kinds or len(check["notes"].strip()) < 20):
        raise AuditError("Non-applicability requires a reason and assessment evidence")


def new_packet(system):
    text(system, "system")
    spec = catalog()
    return {"schema_version": "aeion.croa.audit/v1", "upstream": spec["upstream"],
            "scope": {"system": system, "revision": None, "boundary": None,
                      "audit_period": None, "environment": "evaluation"},
            "assessor": {"name": None, "mode": "self-assessment", "independence_basis": None},
            "checks": [{"id": c["id"], "status": "unknown", "notes": "Not assessed",
                        "evidence": []} for c in spec["checks"]]}


def make_report(packet):
    statuses = {check["status"] for check in packet["checks"]}
    incomplete = any(v is None for v in packet["scope"].values())
    incomplete = incomplete or any(v is None for v in packet["assessor"].values())
    if "fail" in statuses:
        outcome, code = "gaps_found", 1
    elif "unknown" in statuses or incomplete:
        outcome, code = "incomplete", 2
    else:
        outcome, code = "recorded_for_review", 0
    by_id = {c["id"]: c for c in packet["checks"]}
    spec = catalog()
    base = "https://github.com/" + spec["upstream"]["project"] + "/blob/" + spec["upstream"]["commit"]
    checks = [{**by_id[c["id"]], "title": c["title"], "question": c["question"],
               "source": base + "/" + c["source_path"], "section": c["section"]}
              for c in spec["checks"]]
    return {"schema_version": "aeion.croa.report/v1", "upstream": packet["upstream"],
            "scope": packet["scope"], "assessor": packet["assessor"], "outcome": outcome,
            "conformance_claim": False, "conformance_level": None,
            "limitation": "Structure and staged file digests verified; finding truth and deployment conformance are not verified by this tool.",
            "attribution": spec["attribution"], "checks": checks}, code


def markdown(report):
    def cell(value):
        value = "unknown" if value is None else str(value)
        return "".join("&#" + str(ord(c)) + ";" if c in string.punctuation else html.escape(c)
                       for c in value)

    lines = ["# Æion CROA audit", "", "**Outcome:** " + report["outcome"], "",
             "**No conformance level is awarded.** " + report["limitation"], "",
             cell(report["attribution"]), "", "| Scope | Value |", "| --- | --- |"]
    for key, value in report["scope"].items():
        lines.append("| " + cell(key) + " | " + cell(value) + " |")
    lines.extend(["", "Assessor: " + cell(report["assessor"]["name"]) + " (" +
                  cell(report["assessor"]["mode"]) + "); " + cell(report["assessor"]["independence_basis"]),
                  "", "Upstream commit: " + report["upstream"]["commit"], ""])
    for check in report["checks"]:
        lines.extend(["## " + check["id"] + " — " + check["title"], "",
                      "Status: **" + check["status"] + "**", "", cell(check["notes"]), "",
                      "Question: " + cell(check["question"]), "",
                      "Source: [CROA " + cell(check["section"]) + "](" + check["source"] + ")", ""])
        for ref in check["evidence"]:
            lines.append("- " + cell(ref["path"]) + " (" + ref["kind"] + "), SHA-256: " + ref["sha256"])
        lines.append("")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init", help="Emit an unassessed packet").add_argument("--system", required=True)
    commands.add_parser("validate", help="Validate structure and evidence references").add_argument("packet")
    report_parser = commands.add_parser("report", help="Render recorded findings without granting conformance")
    report_parser.add_argument("packet")
    report_parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            print(json.dumps(new_packet(args.system), indent=2, ensure_ascii=False))
            return 0
        packet = load_packet(args.packet)
        if args.command == "validate":
            print(json.dumps({"packet_valid": True, "meaning": "Structure and staged file digests only"}))
            return 0
        report, code = make_report(packet)
        print(json.dumps(report, indent=2, ensure_ascii=False) if args.format == "json" else markdown(report))
        return code
    except (AuditError, OSError) as error:
        message = str(error) if isinstance(error, AuditError) else "Cannot read staged evidence safely"
        print("Invalid audit packet: " + message, file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
