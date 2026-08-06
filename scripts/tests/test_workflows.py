import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
SHA_ACTION_RE = re.compile(r"uses:\s+[^\s@]+@[0-9a-f]{40}\s*$", re.MULTILINE)


def load_workflow(name: str) -> tuple[dict, str]:
    path = ROOT / ".github" / "workflows" / name
    text = path.read_text(encoding="utf-8")
    document = yaml.safe_load(text)
    trigger = document.get("on", document.get(True, {}))
    document["on"] = trigger
    return document, text


class WorkflowContractTests(unittest.TestCase):
    def test_ci_is_read_only_and_runs_local_ci(self) -> None:
        document, text = load_workflow("ci.yml")
        self.assertIn("push", document["on"])
        self.assertIn("pull_request", document["on"])
        self.assertIn("workflow_dispatch", document["on"])
        self.assertEqual(document["permissions"]["contents"], "read")
        self.assertIn("./scripts/ci.sh", text)
        self.assertGreaterEqual(len(SHA_ACTION_RE.findall(text)), 2)

    def test_release_is_manual_and_has_exact_candidate_inputs(self) -> None:
        document, text = load_workflow("release.yml")
        self.assertEqual(set(document["on"]), {"workflow_dispatch"})
        inputs = document["on"]["workflow_dispatch"]["inputs"]
        self.assertEqual(set(inputs), {"version", "expected_sha", "dry_run"})
        self.assertTrue(inputs["version"]["required"])
        self.assertTrue(inputs["expected_sha"]["required"])
        self.assertEqual(inputs["dry_run"]["type"], "boolean")
        self.assertIn("inputs.version", document["concurrency"]["group"])
        self.assertIn("expected_sha", text)
        self.assertIn("!inputs.dry_run", text)
        self.assertIn("gh release", text)
        self.assertIn("shasum -a 256 -c SHA256SUMS", text)
        self.assertGreaterEqual(len(SHA_ACTION_RE.findall(text)), 3)

    def test_release_separates_prepare_and_write_publish_jobs(self) -> None:
        document, _ = load_workflow("release.yml")
        prepare = document["jobs"]["prepare"]
        publish = document["jobs"]["publish"]
        self.assertEqual(prepare["permissions"]["contents"], "read")
        self.assertEqual(publish["permissions"]["contents"], "write")
        self.assertEqual(publish["environment"], "release")
        self.assertIn("prepare", publish["needs"])


if __name__ == "__main__":
    unittest.main()
