"""Behavioral tests for bounded evidence handling and honest audit outcomes.

Spec: knowledge/components/croa-audit.md
SPDX-License-Identifier: MIT
"""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

CLI = Path(__file__).resolve().parents[1] / "audit.py"
spec = importlib.util.spec_from_file_location("croa_audit", CLI)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / "evidence").mkdir()
        self.path = self.root / "audit.json"
        self.packet = audit.new_packet("test system")

    def load(self, packet=None):
        self.path.write_text(json.dumps(self.packet if packet is None else packet), encoding="utf-8")
        return audit.load_packet(self.path)

    def evidence(self, kind="assessment", name=None, body=b"Synthetic test fixture; not deployment evidence."):
        name = name or kind + ".txt"
        (self.root / "evidence" / name).write_bytes(body)
        return {"path": "evidence/" + name, "sha256": hashlib.sha256(body).hexdigest(), "kind": kind}

    def complete_packet(self):
        packet = copy.deepcopy(self.packet)
        packet["scope"].update(revision="fixture-revision", boundary="Synthetic fixture only; no deployed system",
                               audit_period="Synthetic test run")
        packet["assessor"].update(name="Fixture", independence_basis="Self-assessment of synthetic bytes")
        evidence = {kind: self.evidence(kind) for kind in audit.KINDS}
        for check, definition in zip(packet["checks"], audit.catalog()["checks"]):
            check.update(status="pass", notes="Recorded fixture finding, not real conformance evidence",
                         evidence=[evidence[k] for k in definition["required_kinds"]])
        return packet

    def test_new_packet_is_incomplete(self):
        report, code = audit.make_report(self.load())
        self.assertEqual((report["outcome"], code), ("incomplete", 2))
        self.assertTrue(all(c["status"] == "unknown" for c in report["checks"]))

    def test_complete_record_still_makes_no_claim(self):
        report, code = audit.make_report(self.load(self.complete_packet()))
        self.assertEqual((report["outcome"], code), ("recorded_for_review", 0))
        self.assertFalse(report["conformance_claim"])
        self.assertIsNone(report["conformance_level"])
        self.assertIn("not verified", report["limitation"])

    def test_missing_scope_stays_incomplete(self):
        packet = self.complete_packet()
        packet["scope"]["boundary"] = None
        self.assertEqual(audit.make_report(self.load(packet))[1], 2)
        packet = self.complete_packet()
        packet["assessor"]["independence_basis"] = None
        self.assertEqual(audit.make_report(self.load(packet))[1], 2)

    def test_failure_outcome(self):
        self.packet["checks"][0].update(status="fail", notes="Boundary not established", evidence=[self.evidence()])
        self.assertEqual(audit.make_report(self.load())[1], 1)

    def test_missing_duplicate_and_extra_checks(self):
        variants = []
        missing = copy.deepcopy(self.packet)
        missing["checks"].pop()
        variants.append(missing)
        duplicate = copy.deepcopy(self.packet)
        duplicate["checks"][1] = duplicate["checks"][0]
        variants.append(duplicate)
        extra = copy.deepcopy(self.packet)
        extra["checks"][0]["id"] = "FORGED"
        variants.append(extra)
        for packet in variants:
            with self.subTest(packet=packet["checks"][0]["id"]), self.assertRaises(audit.AuditError):
                self.load(packet)

    def test_hash_and_missing_evidence(self):
        ref = self.evidence()
        self.packet["checks"][0].update(status="pass", evidence=[ref])
        self.load()
        (self.root / ref["path"]).write_bytes(b"changed")
        with self.assertRaisesRegex(audit.AuditError, "hash mismatch"):
            self.load()
        (self.root / ref["path"]).unlink()
        with self.assertRaises(audit.AuditError):
            self.load()

    def test_pass_requires_evidence_kinds(self):
        self.packet["checks"][-1].update(status="pass", evidence=[self.evidence("code")])
        with self.assertRaisesRegex(audit.AuditError, "required evidence kinds"):
            self.load()
        self.packet["checks"][-1]["evidence"] = []
        with self.assertRaises(audit.AuditError):
            self.load()

    def test_conditional_exclusions(self):
        check = next(c for c in self.packet["checks"] if c["id"] == "NT-005")
        check.update(status="not_applicable", notes="Fixture boundary contains only exact E1 invariants",
                     evidence=[self.evidence()])
        self.load()
        check["notes"] = "No E3"
        with self.assertRaises(audit.AuditError):
            self.load()
        check["notes"] = "Fixture boundary contains only exact E1 invariants"
        self.packet["checks"][-1].update(status="not_applicable", evidence=[self.evidence()])
        with self.assertRaisesRegex(audit.AuditError, "excluded wholesale"):
            self.load()

    def test_forbidden_paths(self):
        paths = ["../outside.txt", "/outside.txt", "evidence/../outside.txt", "evidence//file.txt",
                 "evidence/.env", "evidence/auth.json", "evidence/credentials.json",
                 "evidence/id_rsa", "evidence/file.pem", "evidence\\file.txt", "evidence/C:foo.txt"]
        for path in paths:
            ref = {"path": path, "sha256": "0" * 64, "kind": "code"}
            self.packet["checks"][0]["evidence"] = [ref]
            with self.subTest(path=path), self.assertRaises(audit.AuditError):
                self.load()

    def test_symlinks_and_special_files(self):
        outside = self.root / "outside.txt"
        outside.write_text("Do not read")
        (self.root / "evidence/link.txt").symlink_to(outside)
        (self.root / "evidence/nested").symlink_to(self.root, target_is_directory=True)
        os.link(outside, self.root / "evidence/hardlink.txt")
        os.mkfifo(self.root / "evidence/pipe.txt")
        for path in ("evidence/link.txt", "evidence/nested/outside.txt", "evidence/hardlink.txt", "evidence/pipe.txt"):
            self.packet["checks"][0]["evidence"] = [{"path": path, "sha256": "0" * 64, "kind": "code"}]
            with self.subTest(path=path), self.assertRaises(audit.AuditError):
                self.load()
        self.load(audit.new_packet("fixture"))
        link = self.root / "link.json"
        link.symlink_to(self.path)
        with self.assertRaises(audit.AuditError):
            audit.load_packet(link)

    def test_evidence_limits(self):
        ref = self.evidence(body=b"x" * (audit.MAX_FILE + 1))
        self.packet["checks"][0]["evidence"] = [ref]
        with self.assertRaises(audit.AuditError):
            self.load()
        self.packet["checks"][0]["evidence"] = [self.evidence() for _ in range(21)]
        with self.assertRaises(audit.AuditError):
            self.load()
        self.packet["checks"][0]["evidence"] = [self.evidence()]
        original = audit.MAX_TOTAL
        try:
            audit.MAX_TOTAL = 1
            with self.assertRaisesRegex(audit.AuditError, "aggregate"):
                self.load()
        finally:
            audit.MAX_TOTAL = original
        self.path.write_bytes(b" " * (audit.MAX_FILE + 1))
        with self.assertRaises(audit.AuditError):
            audit.load_packet(self.path)

    def test_invalid_json(self):
        for value in ('{"checks": [], "checks": []}', '{"value": NaN}', '{"value": Infinity}', '[', '[]'):
            self.path.write_text(value)
            with self.subTest(value=value), self.assertRaises(audit.AuditError):
                audit.load_packet(self.path)

    def test_unexpected_fields(self):
        for target in ("packet", "scope", "assessor", "check"):
            packet = copy.deepcopy(self.packet)
            destination = packet if target == "packet" else packet["checks"][0] if target == "check" else packet[target]
            destination["conformance_level"] = "L4"
            with self.subTest(target=target), self.assertRaises(audit.AuditError):
                self.load(packet)

    def test_status_types_and_control_characters(self):
        for status in (True, [], "passed", None):
            packet = copy.deepcopy(self.packet)
            packet["checks"][0]["status"] = status
            with self.subTest(status=status), self.assertRaises(audit.AuditError):
                self.load(packet)
        self.packet["scope"]["system"] = "name\n# injected"
        with self.assertRaises(audit.AuditError):
            self.load()

    def test_markdown_escapes_data(self):
        self.packet["scope"]["system"] = '<script>x</script> | [link](https://example.test) **bold** # heading'
        rendered = audit.markdown(audit.make_report(self.load())[0])
        for unsafe in ("<script>", "[link]", "**bold**", "# heading", "| [link]"):
            self.assertNotIn(unsafe, rendered)
        self.assertIn("&#60;script&#62;", rendered)

    def test_catalog_source_links(self):
        catalog = audit.catalog()
        provenance = json.loads((audit.ROOT / "catalog/upstream.json").read_text())
        paths = {item["path"] for item in provenance["sources"]}
        self.assertEqual(len(catalog["checks"]), 19)
        self.assertEqual(catalog["upstream"]["commit"], provenance["commit"])
        self.assertEqual(catalog["license"], "CC-BY-4.0")
        for check in catalog["checks"]:
            self.assertIn(check["source_path"], paths)
            self.assertTrue(check["section"])

    def test_cli_round_trip_is_read_only(self):
        result = subprocess.run([sys.executable, str(CLI), "init", "--system", "fixture"],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0)
        self.path.write_text(result.stdout)
        original = self.path.read_bytes()
        names = sorted(str(p.relative_to(self.root)) for p in self.root.rglob("*"))
        for command, expected in (("validate", 0), ("report", 2)):
            args = [sys.executable, str(CLI), command, str(self.path)]
            if command == "report":
                args.extend(["--format", "json"])
            result = subprocess.run(args, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, expected, result.stderr)
            self.assertIsInstance(json.loads(result.stdout), dict)
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(sorted(str(p.relative_to(self.root)) for p in self.root.rglob("*")), names)
        self.path.write_text('{"conformance_level": "L4"}')
        result = subprocess.run([sys.executable, str(CLI), "report", str(self.path)],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 3)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
