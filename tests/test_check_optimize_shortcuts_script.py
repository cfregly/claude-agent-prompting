from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

from scripts.check_optimize_shortcuts import (
    _check_matrix_bindings,
    check_optimize_shortcuts,
)
from scripts.optimize_mcp import Target


ROOT = Path(__file__).resolve().parents[1]


class CheckOptimizeShortcutsScriptTests(unittest.TestCase):
    def test_script_passes_current_repo(self):
        result = subprocess.run(
            [sys.executable, "scripts/check_optimize_shortcuts.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("optimize shortcut check passed", result.stdout)

    def test_matrix_binding_check_rejects_stale_names(self):
        target = Target(
            inputs=("sample",),
            baseline_variant="baseline",
            default_providers="anthropic,missing-provider",
            default_harnesses="prompt_json,missing_harness",
            instruction_variants="rules,missing_rules",
            matrix="evals/model_matrix/sample.json",
            optimized_variants=("missing_tuned",),
            variants="baseline,missing_tuned",
        )
        matrix = {
            "profiles": [{"provider": "anthropic", "harnesses": ["prompt_json"]}],
            "instruction_variants": [{"name": "rules"}],
            "tool_variants": [{"name": "baseline"}],
            "cases": [],
        }

        failures = _check_matrix_bindings(target, matrix)

        joined = "\n".join(failures)
        self.assertIn("variant 'missing_tuned' missing", joined)
        self.assertIn("instruction variant 'missing_rules' missing", joined)
        self.assertIn("provider/profile 'missing-provider' missing", joined)
        self.assertIn("harness 'missing_harness' missing", joined)
        self.assertIn("matrix has no cases", joined)

    def test_shortcut_check_rejects_missing_help_docs_and_matrix(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "README.md").write_text("# sample\n", encoding="utf-8")
            (root / "docs").mkdir()
            (root / "Makefile").write_text("help:\n\t@echo missing\n", encoding="utf-8")
            target = Target(
                inputs=("sample",),
                baseline_variant="baseline",
                default_providers="anthropic",
                default_harnesses="prompt_json",
                instruction_variants="rules",
                matrix="evals/model_matrix/missing.json",
                optimized_variants=("tuned",),
                variants="baseline,tuned",
            )

            failures = check_optimize_shortcuts(root, targets=[target])

        joined = "\n".join(failures)
        self.assertIn("Makefile: help output missing optimize shortcut mcp=sample", joined)
        self.assertIn("README/docs: missing public optimize shortcut mcp=sample", joined)
        self.assertIn("sample: matrix file missing", joined)

    def test_shortcut_check_rejects_default_zero_cell_selection(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            matrix_dir = root / "evals" / "model_matrix"
            matrix_dir.mkdir(parents=True)
            (root / "docs").mkdir()
            (root / "README.md").write_text("# sample\nmcp=sample\n", encoding="utf-8")
            (root / "Makefile").write_text(
                'help:\n\t@echo "make optimize mcp=sample"\n',
                encoding="utf-8",
            )
            (matrix_dir / "sample.json").write_text(
                json.dumps(
                    {
                        "name": "sample matrix",
                        "profiles": [{"provider": "anthropic", "harnesses": ["prompt_json"]}],
                        "instruction_variants": [{"name": "rules"}],
                        "tool_variants": [{"name": "baseline"}, {"name": "tuned"}],
                        "cases": [{"name": "case", "task": "Task.", "expected_tools": ["tool"]}],
                    }
                ),
                encoding="utf-8",
            )
            target = Target(
                inputs=("sample",),
                baseline_variant="baseline",
                default_providers="openai",
                default_harnesses="prompt_json",
                instruction_variants="rules",
                matrix="evals/model_matrix/sample.json",
                optimized_variants=("tuned",),
                variants="baseline,tuned",
            )

            failures = check_optimize_shortcuts(root, targets=[target])

        joined = "\n".join(failures)
        self.assertIn("provider/profile 'openai' missing", joined)
        self.assertIn("default dry-run failed", joined)


if __name__ == "__main__":
    unittest.main()
