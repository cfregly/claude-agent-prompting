from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.optimize_mcp import Target, optimization_gate


ROOT = Path(__file__).resolve().parents[1]


class OptimizeMcpScriptTests(unittest.TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "scripts/optimize_mcp.py", *args],
            cwd=ROOT,
            check=False,
            text=True,
            capture_output=True,
        )

    def test_screenpipe_dry_run_writes_markdown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            out_path = Path(temp_dir) / "screenpipe.md"
            result = self.run_script(
                "screenpipe",
                "--markdown",
                "--providers",
                "anthropic",
                "--harnesses",
                "prompt_json",
                "--max-cases",
                "1",
                "--out",
                str(out_path),
            )

            self.assertEqual(0, result.returncode, result.stderr)
            report = out_path.read_text(encoding="utf-8")

        self.assertIn("screenpipe mcp tool-selection matrix", report)
        self.assertIn("readme_screenpipe_mcp", report)
        self.assertIn("source_tuned_screenpipe_mcp", report)
        self.assertIn("wrote", result.stdout)

    def test_screenpipe_url_resolves_to_stored_matrix(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            out_path = Path(temp_dir) / "screenpipe.json"
            result = self.run_script(
                "https://github.com/screenpipe/screenpipe",
                "--providers",
                "anthropic",
                "--harnesses",
                "prompt_json",
                "--max-cases",
                "1",
                "--out",
                str(out_path),
            )

            self.assertEqual(0, result.returncode, result.stderr)
            report = out_path.read_text(encoding="utf-8")

        self.assertIn('"matrix": "screenpipe mcp tool-selection matrix"', report)

    def test_optimization_gate_rejects_skipped_optimized_cells(self):
        target = Target(
            inputs=("sample",),
            baseline_variant="baseline",
            default_providers="anthropic",
            default_harnesses="prompt_json",
            instruction_variants="rules",
            matrix="matrix.json",
            optimized_variants=("candidate",),
            variants="baseline,candidate",
        )
        gate = optimization_gate(
            {
                "live": True,
                "cells": [
                    {
                        "errors": 0,
                        "failed": 0,
                        "harness": "prompt_json",
                        "instruction_variant": "rules",
                        "passed": 1,
                        "provider": "anthropic",
                        "score": 1.0,
                        "skipped": 1,
                        "tool_variant": "candidate",
                    }
                ],
            },
            target,
            {"candidate"},
        )

        self.assertIsNotNone(gate)
        self.assertFalse(gate["passed"])
        self.assertEqual(1, gate["optimized_skipped"])

    def test_dry_run_does_not_require_default_env_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            out_path = Path(temp_dir) / "screenpipe.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "optimize_mcp.py"),
                    "screenpipe",
                    "--providers",
                    "anthropic",
                    "--harnesses",
                    "prompt_json",
                    "--max-cases",
                    "1",
                    "--out",
                    str(out_path),
                ],
                cwd=temp_dir,
                check=False,
                text=True,
                capture_output=True,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue(out_path.exists())
            self.assertFalse((Path(temp_dir) / ".env").exists())

    def test_yc_p2026_targets_resolve_to_stored_matrices(self):
        targets = [
            ("humwork", "humwork mcp tool-selection matrix"),
            ("different-ai/openwork", "openwork ui mcp tool-selection matrix"),
            ("https://github.com/InsForge/insforge-mcp", "insforge mcp tool-selection matrix"),
        ]

        for target, matrix_name in targets:
            with self.subTest(target=target):
                with tempfile.TemporaryDirectory() as temp_dir:
                    out_path = Path(temp_dir) / "target.json"
                    result = self.run_script(
                        target,
                        "--providers",
                        "anthropic",
                        "--harnesses",
                        "prompt_json",
                        "--max-cases",
                        "1",
                        "--out",
                        str(out_path),
                    )

                    self.assertEqual(0, result.returncode, result.stderr)
                    report = out_path.read_text(encoding="utf-8")

                self.assertIn(f'"matrix": "{matrix_name}"', report)

    def test_unknown_url_fails_instead_of_falling_back(self):
        result = self.run_script("https://example.com/not-a-known-mcp")

        self.assertNotEqual(0, result.returncode)
        self.assertIn("unknown MCP target", result.stderr)

    def run_make(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["make", *args],
            cwd=ROOT,
            check=False,
            text=True,
            capture_output=True,
        )

    def test_make_optimize_dry_requires_lowercase_selector(self):
        result = self.run_make("optimize-dry")

        self.assertEqual(2, result.returncode)
        self.assertIn("Missing target", result.stdout)

    def test_make_optimize_dry_rejects_uppercase_selector(self):
        result = self.run_make("optimize-dry", "MCP=screenpipe")

        self.assertEqual(2, result.returncode)
        self.assertIn("Use lowercase selectors", result.stdout)

    def test_make_optimize_dry_accepts_lowercase_mcp_selector(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            out_path = Path(temp_dir) / "screenpipe.md"
            result = self.run_make(
                "optimize-dry",
                "mcp=screenpipe",
                "PROVIDERS=anthropic",
                "HARNESSES=prompt_json",
                "MAX_CASES=1",
                f"OUT={out_path}",
            )

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue(out_path.exists())


if __name__ == "__main__":
    unittest.main()
