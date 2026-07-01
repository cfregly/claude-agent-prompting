from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.check_human_docs import check_human_docs


ROOT = Path(__file__).resolve().parents[1]


class CheckHumanDocsScriptTests(unittest.TestCase):
    def test_script_passes_current_repo(self):
        result = subprocess.run(
            [sys.executable, "scripts/check_human_docs.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("human docs check passed", result.stdout)

    def test_rejects_root_machine_sections_above_llm_details(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_readme(
                root,
                extra_before_details="## Layout\n\n```text\npython scripts/check_example.py\n```\n",
            )

            failures = check_human_docs(root)

        joined = "\n".join(failures)
        self.assertIn("README.md: machine section ## Layout appears before LLM details", joined)
        self.assertIn("README.md: checker inventory appears above LLM details", joined)

    def test_rejects_machine_heavy_doc_without_llm_details(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_readme(root)
            docs = root / "docs"
            docs.mkdir()
            (docs / "machine.md").write_text(
                "# Machine Doc\n\n"
                + "\n".join("python scripts/check_example.py" for _ in range(20))
                + "\n",
                encoding="utf-8",
            )

            failures = check_human_docs(root)

        joined = "\n".join(failures)
        self.assertIn("docs/machine.md: machine-heavy doc must end with LLM / Machine-readable details", joined)

    def test_rejects_sendable_packet_without_human_summary(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_readme(root)
            finding = root / "docs" / "findings" / "sample"
            finding.mkdir(parents=True)
            (finding / "README.md").write_text(
                "# Sample Finding\n\n"
                "Share link: [Sample](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/sample)\n\n"
                "## Full Bundle\n\n"
                "Bundle folder: [Sample](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/sample)\n",
                encoding="utf-8",
            )

            failures = check_human_docs(root)

        joined = "\n".join(failures)
        self.assertIn("docs/findings/sample/README.md: missing ## Human Summary before artifact links", joined)

    def test_allows_findings_index_shareable_bundle_table_before_llm_details(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_readme(root)
            findings = root / "docs" / "findings"
            findings.mkdir(parents=True)
            (findings / "README.md").write_text(
                "# Founder Findings\n\n"
                "These folders are share links.\n\n"
                "## Shareable Bundles\n\n"
                "| Target | Full bundle | Matrix | Result / coverage |\n"
                "|---|---|---|---|\n"
                + "\n".join(
                    "| Sample | "
                    "[Bundle](https://github.com/cfregly/claude-agent-harness-opt/tree/main/evals/pr_packets/sample) | "
                    "[Matrix](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/model_matrix/sample.json) | "
                    "[Receipt](https://github.com/cfregly/claude-agent-harness-opt/blob/main/evals/results/sample.md) |"
                    for _ in range(12)
                )
                + "\n\n"
                "<details>\n"
                "<summary>LLM / Machine-readable details</summary>\n\n"
                "`scripts/check_finding_packets.py` enforces retained PR packets.\n\n"
                "</details>\n",
                encoding="utf-8",
            )

            failures = check_human_docs(root)

        self.assertEqual([], failures)


def _write_readme(root: Path, *, extra_before_details: str = "") -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "README.md").write_text(
        "# claude-agent-harness-opt\n\n"
        "A human-first project page.\n\n"
        "## Demo\n\n"
        "Demo text.\n\n"
        "## Share This\n\n"
        "| Audience | Send this |\n|---|---|\n| maintainer | [bundle](https://github.com/cfregly/claude-agent-harness-opt/tree/main/docs/findings/sample) |\n\n"
        "## Quickstart\n\n"
        "Run it.\n\n"
        "## What it implements\n\n"
        "Tools.\n\n"
        "## How It Works\n\n"
        "Steps.\n\n"
        "## Start Here\n\n"
        "Links.\n\n"
        "## Shareable Bundles\n\n"
        "Bundles.\n\n"
        f"{extra_before_details}"
        "<details>\n"
        "<summary>LLM / Machine-readable details</summary>\n\n"
        "## Verify it\n\n"
        "python scripts/check_human_docs.py\n\n"
        "</details>\n\n"
        "## License\n\n"
        "MIT.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    unittest.main()
