import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class PopTaskTests(unittest.TestCase):
    def run_pop_task(
        self,
        task_text: str,
        project_name: str = "sample",
    ) -> tuple[subprocess.CompletedProcess[str], str, str | None]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task_root = root / "tasks"
            task_root.mkdir()
            script = task_root / "pop_task"
            shutil.copy2(REPO_ROOT / "pop_task", script)

            task_file = task_root / f"{project_name}.md"
            done_file = task_root / "done" / f"{project_name}.md"
            task_file.write_text(task_text)

            project_root = root / project_name
            project_root.mkdir()
            (project_root / ".git").mkdir()
            work_dir = project_root / "nested"
            work_dir.mkdir()

            result = subprocess.run(
                [sys.executable, str(script)],
                cwd=work_dir,
                capture_output=True,
                text=True,
                check=False,
            )

            done_text = done_file.read_text() if done_file.exists() else None
            return result, task_file.read_text(), done_text

    def test_pops_first_task_and_saves_remainder(self) -> None:
        result, task_text, done_text = self.run_pop_task(
            "first task\n---\nsecond task\n---\n",
        )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "first task\n")
        self.assertEqual(result.stderr, "")
        self.assertEqual(task_text, "second task\n---\n")
        self.assertEqual(done_text, "first task\n---\n")

    def test_empty_task_file_exits_without_changes(self) -> None:
        result, task_text, done_text = self.run_pop_task("")

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "No tasks found\n")
        self.assertEqual(task_text, "")
        self.assertIsNone(done_text)

    def test_separators_without_non_blank_lines_exit_without_changes(self) -> None:
        content = "---\n\n---\n   \n---\n"
        result, task_text, done_text = self.run_pop_task(content)

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "No tasks found\n")
        self.assertEqual(task_text, content)
        self.assertIsNone(done_text)

    def test_leading_and_trailing_whitespace_lines_do_not_create_tasks(self) -> None:
        result, task_text, done_text = self.run_pop_task(
            "\n  \nfirst task\n---\n\nsecond task\n---\n\n",
        )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "first task\n")
        self.assertEqual(result.stderr, "")
        self.assertEqual(task_text, "second task\n---\n")
        self.assertEqual(done_text, "first task\n---\n")

    def test_successful_pop_can_leave_empty_task_file(self) -> None:
        result, task_text, done_text = self.run_pop_task("only task\n---\n")

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "only task\n")
        self.assertEqual(result.stderr, "")
        self.assertEqual(task_text, "")
        self.assertEqual(done_text, "only task\n---\n")


if __name__ == "__main__":
    unittest.main()
