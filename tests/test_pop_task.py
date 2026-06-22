import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "pop_task"


class PopTaskTests(unittest.TestCase):
    def assert_case(self, name: str) -> None:
        fixture = FIXTURE_ROOT / name
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task_root = root / "tasks"
            shutil.copytree(fixture / "before", task_root)
            shutil.copy2(REPO_ROOT / "pop_task", task_root / "pop_task")

            project_root = root / "sample"
            work_dir = project_root / "nested"
            work_dir.mkdir(parents=True)
            (project_root / ".git").mkdir()

            result = subprocess.run(
                [sys.executable, str(task_root / "pop_task")],
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
                (task_root / "sample.md").read_text(),
                (expected / "sample.md").read_text(),
            )

            expected_done = expected / "done" / "sample.md"
            actual_done = task_root / "done" / "sample.md"
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


if __name__ == "__main__":
    unittest.main()
