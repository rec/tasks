import contextlib
import importlib.machinery
import importlib.util
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "pop"


class PopTests(unittest.TestCase):
    def assert_case(
        self,
        name: str,
        project_name: str = "sample",
        args: list[str] | None = None,
    ) -> None:
        fixture = FIXTURE_ROOT / name
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task_dir = root / "tasks"
            shutil.copytree(fixture / "before", task_dir)
            shutil.copy2(REPO_ROOT / "pop", root / "pop")
            if project_name != "sample":
                (task_dir / f"{project_name}.md").write_text(
                    (task_dir / "sample.md").read_text(),
                )

            project_root = root / "sample"
            work_dir = project_root / "nested"
            work_dir.mkdir(parents=True)
            (project_root / ".git").mkdir()

            result = subprocess.run(
                [sys.executable, str(root / "pop"), *(args or [])],
                cwd=work_dir,
                capture_output=True,
                text=True,
                check=False,
            )

            expected = fixture / "after"
            self.assertEqual(
                result.returncode,
                int((expected / "returncode.txt").read_text()),
            )
            self.assertEqual(result.stdout, (expected / "stdout.txt").read_text())
            self.assertEqual(result.stderr, (expected / "stderr.txt").read_text())
            self.assertEqual(
                (task_dir / f"{project_name}.md").read_text(),
                (expected / "sample.md").read_text(),
            )

            expected_done = expected / "done" / "sample.md"
            actual_done = root / "done" / f"{project_name}.md"
            self.assertEqual(actual_done.exists(), expected_done.exists())
            if expected_done.exists():
                self.assertEqual(actual_done.read_text(), expected_done.read_text())

    def test_normal_operation(self) -> None:
        self.assert_case("normal")

    def test_empty_task_file(self) -> None:
        self.assert_case("empty")

    def test_separators_without_non_blank_lines(self) -> None:
        self.assert_case("separator_only")

    def test_leading_and_trailing_whitespace_lines(self) -> None:
        self.assert_case("whitespace")

    def test_successful_pop_can_leave_empty_task_file(self) -> None:
        self.assert_case("leaves_empty")

    def test_explicit_project_argument_selects_that_project(self) -> None:
        self.assert_case("normal", project_name="other", args=["other"])

    def test_main_accepts_project_parameter(self) -> None:
        fixture = FIXTURE_ROOT / "normal"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task_dir = root / "tasks"
            shutil.copytree(fixture / "before", task_dir)
            shutil.copy2(REPO_ROOT / "pop", root / "pop")
            (task_dir / "other.md").write_text((task_dir / "sample.md").read_text())

            loader = importlib.machinery.SourceFileLoader("pop_test", str(root / "pop"))
            spec = importlib.util.spec_from_loader(loader.name, loader)
            self.assertIsNotNone(spec)
            self.assertIsNotNone(spec.loader)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                module.main("other")

            expected = fixture / "after"
            self.assertEqual(stdout.getvalue(), (expected / "stdout.txt").read_text())
            self.assertEqual(
                (task_dir / "other.md").read_text(),
                (expected / "sample.md").read_text(),
            )
            self.assertEqual(
                (root / "done" / "other.md").read_text(),
                (expected / "done" / "sample.md").read_text(),
            )

    def test_multiple_project_arguments_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "tasks").mkdir()
            shutil.copy2(REPO_ROOT / "pop", root / "pop")

            result = subprocess.run(
                [sys.executable, str(root / "pop"), "one", "two"],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "Usage: pop [project]\n")


if __name__ == "__main__":
    unittest.main()
