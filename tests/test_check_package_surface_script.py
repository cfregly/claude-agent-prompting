from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest

from scripts.check_package_surface import check_package_surface


ROOT = Path(__file__).resolve().parents[1]


class CheckPackageSurfaceScriptTests(unittest.TestCase):
    def test_script_passes_current_repo(self):
        result = subprocess.run(
            [sys.executable, "scripts/check_package_surface.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("package surface check passed", result.stdout)

    def test_accepts_minimal_valid_package_surface(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            package = root / "claude_agent_harness_opt"
            package.mkdir()
            (root / ".gitignore").write_text(
                "\n".join(
                    [
                        ".env",
                        ".venv/",
                        "__pycache__/",
                        "*.pyc",
                        "*.egg-info/",
                        ".pytest_cache/",
                        "dist/",
                        "build/",
                    ]
                ),
                encoding="utf-8",
            )
            (root / "pyproject.toml").write_text(_valid_pyproject(), encoding="utf-8")
            (root / "LICENSE").write_text(_valid_license(), encoding="utf-8")
            (package / "__init__.py").write_text("", encoding="utf-8")
            (package / "__main__.py").write_text(
                "from .cli import main\n\nif __name__ == '__main__':\n    raise SystemExit(main())\n",
                encoding="utf-8",
            )
            (package / "cli.py").write_text("def main(argv=None):\n    return 0\n", encoding="utf-8")

            failures = check_package_surface(root, tracked_paths=[], run_smoke=False)

        self.assertEqual([], failures)

    def test_rejects_package_metadata_and_artifact_drift(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            package = root / "claude_agent_harness_opt"
            stale = root / "claude_agent_harness_optimization"
            package.mkdir()
            stale.mkdir()
            (root / ".gitignore").write_text(".env\n", encoding="utf-8")
            (root / "pyproject.toml").write_text(
                textwrap.dedent(
                    """
                    [build-system]
                    requires = []
                    build-backend = "other.backend"

                    [project]
                    name = "claude-agent-harness-optimization"
                    readme = "docs/readme.md"
                    requires-python = ">=3.10"
                    license = { text = "Apache-2.0" }

                    [project.scripts]
                    claude-agent-harness-opt = "missing:main"
                    """
                ),
                encoding="utf-8",
            )
            (package / "__init__.py").write_text("", encoding="utf-8")
            (package / "__main__.py").write_text("print('wrong')\n", encoding="utf-8")
            (package / "cli.py").write_text("print('no main')\n", encoding="utf-8")
            (stale / "__init__.py").write_text("", encoding="utf-8")

            failures = check_package_surface(
                root,
                tracked_paths=[
                    "claude_agent_harness_opt/__pycache__/cli.pyc",
                    "dist/package.tar.gz",
                    "build/lib/file.py",
                    "claude_agent_harness_opt.egg-info/PKG-INFO",
                ],
                run_smoke=False,
            )

        joined = "\n".join(failures)
        self.assertIn("pyproject.toml: project.name must be claude-agent-harness-opt", joined)
        self.assertIn("pyproject.toml: project.license.text must be MIT", joined)
        self.assertIn("LICENSE: missing", joined)
        self.assertIn("pyproject.toml: console script claude-agent-harness-opt must target", joined)
        self.assertIn("claude_agent_harness_opt/__main__.py: must delegate to cli.main", joined)
        self.assertIn("claude_agent_harness_optimization: stale package source must not be present", joined)
        self.assertIn("tracked Python bytecode is not allowed", joined)
        self.assertIn("tracked build artifact is not allowed", joined)
        self.assertIn("tracked egg-info artifact is not allowed", joined)
        self.assertIn(".gitignore: missing generated artifact pattern __pycache__/", joined)


def _valid_pyproject() -> str:
    return textwrap.dedent(
        """
        [build-system]
        requires = ["setuptools>=68"]
        build-backend = "setuptools.build_meta"

        [project]
        name = "claude-agent-harness-opt"
        version = "0.1.0"
        readme = "README.md"
        requires-python = ">=3.11"
        license = { text = "MIT" }

        [project.scripts]
        claude-agent-harness-opt = "claude_agent_harness_opt.cli:main"
        """
    )


def _valid_license() -> str:
    return textwrap.dedent(
        """
        MIT License

        Copyright (c) 2026 Contributors

        Permission is hereby granted, free of charge, to any person obtaining a copy
        of this software and associated documentation files (the "Software"), to deal
        in the Software without restriction.
        """
    ).lstrip()


if __name__ == "__main__":
    unittest.main()
