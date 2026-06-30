from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

from scripts.check_prompt_recipe_surfaces import _check_prompt_templates, _check_recipes


ROOT = Path(__file__).resolve().parents[1]


class CheckPromptRecipeSurfacesScriptTests(unittest.TestCase):
    def test_script_passes_current_repo(self):
        result = subprocess.run(
            [sys.executable, "scripts/check_prompt_recipe_surfaces.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("prompt/recipe surface check passed", result.stdout)

    def test_recipe_check_rejects_uncovered_recipe_drift(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            recipe_dir = root / "recipes"
            recipe_dir.mkdir()
            (recipe_dir / "bad_recipe.json").write_text(
                json.dumps(
                    {
                        "name": "not_matching_file",
                        "role": "You are a test agent.",
                        "task": "Test bad recipe validation.",
                        "use_case": {
                            "complexity": 1,
                            "value": 1,
                            "viability": 1,
                            "cost_of_error": 5,
                            "recoverability": 1,
                        },
                        "success_criteria": ["Check something."],
                        "done_when": ["Done."],
                        "budgets": {"simple": 5, "standard": 2, "complex": 1},
                        "tools": [
                            {
                                "name": "lookup",
                                "purpose": "Lookup",
                                "use_when": "Use when needed",
                            }
                        ],
                        "thinking": {
                            "initial_plan": [],
                            "after_tool_result": ["Check the result."],
                            "self_check": ["Check the answer."],
                        },
                        "guardrails": {"confirm_before": [], "never": ["Skip checks."]},
                        "context": {
                            "strategy": "",
                            "progress_file": "notes.md",
                            "compact_when": "later",
                            "subagent_policy": "none",
                        },
                        "parallel_tool_calls": "yes",
                    }
                ),
                encoding="utf-8",
            )

            failures = _check_recipes(root)

        joined = "\n".join(failures)
        self.assertIn("recipe.name must match file stem", joined)
        self.assertIn("budgets must be monotonic", joined)
        self.assertIn("tools[0] missing quality_checks", joined)
        self.assertIn("thinking.initial_plan must be a nonempty list", joined)
        self.assertIn("guardrails.confirm_before must be a nonempty list", joined)
        self.assertIn("context.strategy must be present", joined)
        self.assertIn("parallel_tool_calls must be boolean", joined)
        self.assertIn("use_case verdict is not agent-ready", joined)
        self.assertIn("tool lint failed", joined)

    def test_prompt_check_requires_explicit_template_contracts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_dir = root / "prompts"
            prompt_dir.mkdir()
            (prompt_dir / "extra.md").write_text("# Extra\n", encoding="utf-8")

            failures = _check_prompt_templates(root)

        joined = "\n".join(failures)
        self.assertIn("prompts/agent_system_template.md: missing contracted prompt template", joined)
        self.assertIn("prompts/llm_judge.md: missing contracted prompt template", joined)
        self.assertIn("prompts/extra.md: prompt template has no surface contract", joined)


if __name__ == "__main__":
    unittest.main()
