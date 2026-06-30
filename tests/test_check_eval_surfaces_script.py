from pathlib import Path
import subprocess
import sys
import unittest

from scripts.check_eval_surfaces import (
    ROOT,
    _check_e2e_specs,
    _check_live_harness_specs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class CheckEvalSurfacesScriptTests(unittest.TestCase):
    def test_script_passes_current_repo(self):
        result = subprocess.run(
            [sys.executable, "scripts/check_eval_surfaces.py"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("eval surface check passed", result.stdout)

    def test_e2e_surface_check_rejects_mutating_or_assertionless_specs(self):
        path = ROOT / "evals" / "e2e" / "temporary_bad_e2e.json"
        path.write_text(
            """
{
  "name": "bad e2e",
  "env": {"required": ["TOKEN"]},
  "checks": [
    {
      "method": "POST",
      "name": "mutating call",
      "read_only": false,
      "type": "http_json",
      "url": "https://example.test/mutate"
    }
  ]
}
""",
            encoding="utf-8",
        )
        try:
            failures = _check_e2e_specs()
        finally:
            path.unlink()

        joined = "\n".join(failures)
        self.assertIn("temporary_bad_e2e.json", joined)
        self.assertIn("method must be GET or HEAD", joined)
        self.assertIn("read_only must be true", joined)
        self.assertIn("missing JSON expectation", joined)

    def test_live_harness_surface_check_rejects_missing_prompt_and_adapter(self):
        path = ROOT / "evals" / "live_harnesses" / "temporary_bad_live.json"
        path.write_text(
            """
{
  "name": "bad live harness",
  "value_bar": {"claim": "Bad spec."},
  "cases": [{"name": "case without prompt"}],
  "harnesses": [{"name": "missing adapter", "command": ["echo", "ok"]}]
}
""",
            encoding="utf-8",
        )
        try:
            failures = _check_live_harness_specs()
        finally:
            path.unlink()

        joined = "\n".join(failures)
        self.assertIn("temporary_bad_live.json", joined)
        self.assertIn("value_bar.adversarial_check must be present", joined)
        self.assertIn("cases[0] missing prompt_template", joined)
        self.assertIn("harnesses[0] missing adapter", joined)


if __name__ == "__main__":
    unittest.main()
