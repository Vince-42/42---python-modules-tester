"""Regression tests for subprocess invocation tracing.

Every ExerciseRunner.run_file invocation made while checking an exercise must be
retained and rendered in that exercise's trace, in order, with command, cwd,
exit code, stdout and stderr. These tests lock that behaviour with the stdlib
unittest runner (the repo declares no test dependency).
"""

import sys
import textwrap
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

from checker import Checker, ExerciseResult  # noqa: E402
from tracing import ProcessInvocation, format_invocations  # noqa: E402


SCORE_ANALYTICS = textwrap.dedent(
    """\
    import sys


    def main():
        scores = []
        for arg in sys.argv[1:]:
            try:
                scores.append(int(arg))
            except ValueError:
                print(f"Invalid parameter: '{arg}'")
        if not scores:
            print("No scores provided. Usage: python ft_score_analytics.py <score1> <score2> ...")
            return
        total = sum(scores)
        print(f"Scores processed: {scores}")
        print(f"Total players: {len(scores)}")
        print(f"Total score: {total}")
        print(f"Average score: {total / len(scores)}")
        print(f"High score: {max(scores)}")
        print(f"Low score: {min(scores)}")
        print(f"Score range: {max(scores) - min(scores)}")


    if __name__ == "__main__":
        main()
    """
)


class ProcessInvocationTraceTests(unittest.TestCase):
    """Regression coverage for ordered subprocess invocation retention."""

    def _make_checker(self):
        import tempfile

        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        student = Path(tmp.name) / "student"
        trace_dir = Path(tmp.name) / "traces"
        student.mkdir(parents=True, exist_ok=True)
        return Checker(student, trace_dir), student

    def _write(self, student: Path, rel: str, content: str) -> Path:
        path = student / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    def test_module03_ex1_records_three_ordered_invocations(self):
        """Given a correct score-analytics submission, when module 3 ex1 is
        checked, then three run_file invocations are retained in order and the
        trace renders each labelled run."""
        checker, student = self._make_checker()
        self._write(student, "ex1/ft_score_analytics.py", SCORE_ANALYTICS)
        self.assertTrue(checker.load_module(3))

        result = checker.check_exercise(3, 1, checker.modules[3])

        self.assertTrue(result.passed, msg=result.errors)
        self.assertEqual(len(result.invocations), 3)

        expected_args = [
            ["1500", "2300", "1800", "2100", "1950"],
            ["ab", "ac"],
            ["1500", "ab", "2300"],
        ]
        expected_markers = ["Scores processed", "No scores provided", "Scores processed"]
        for invocation, args, marker in zip(result.invocations, expected_args, expected_markers):
            self.assertEqual(invocation.exit_code, 0)
            self.assertEqual(invocation.command[2:], args)
            self.assertIn(marker, invocation.stdout)

        trace_content = Path(result.trace).read_text()
        for run_label in ("--- RUN 1 ---", "--- RUN 2 ---", "--- RUN 3 ---"):
            self.assertIn(run_label, trace_content)
        self.assertIn("Exit code: 0", trace_content)
        self.assertIn("Command:", trace_content)
        self.assertIn("Cwd:", trace_content)

    def test_timeout_outcome_is_recorded(self):
        """Given a sleeping script and a 1s timeout, when run_file is called,
        then a timeout invocation (exit 124) is recorded."""
        checker, student = self._make_checker()
        script = self._write(student, "slow.py", "import time\ntime.sleep(30)\n")

        result = ExerciseResult(module=0, exercise=0, name="Slow", passed=True)
        with checker.runner.record_into(result):
            code, _stdout, stderr = checker.runner.run_file(script, timeout=1)

        self.assertEqual(code, 124)
        self.assertEqual(len(result.invocations), 1)
        self.assertEqual(result.invocations[0].exit_code, 124)
        self.assertEqual(result.invocations[0].stderr, "Execution timed out")

    def test_missing_file_outcome_is_recorded(self):
        """Given a non-existent script, when run_file is called, then a
        missing-file invocation (exit 1) is recorded."""
        checker, student = self._make_checker()
        missing = student / "nope.py"

        result = ExerciseResult(module=0, exercise=0, name="Missing", passed=True)
        with checker.runner.record_into(result):
            code, _stdout, stderr = checker.runner.run_file(missing)

        self.assertEqual(code, 1)
        self.assertEqual(len(result.invocations), 1)
        self.assertEqual(result.invocations[0].exit_code, 1)
        self.assertEqual(result.invocations[0].stderr, f"File not found: {missing}")

    def test_execution_error_outcome_is_recorded(self):
        """Given a subprocess that raises unexpectedly, when run_file is called,
        then the execution-error outcome (exit 1) is recorded."""
        checker, student = self._make_checker()
        script = self._write(student, "boom.py", "print('hi')\n")

        result = ExerciseResult(module=0, exercise=0, name="Boom", passed=True)
        with patch("checker.subprocess.run", side_effect=RuntimeError("boom")):
            with checker.runner.record_into(result):
                code, _stdout, stderr = checker.runner.run_file(script)

        self.assertEqual(code, 1)
        self.assertEqual(len(result.invocations), 1)
        self.assertEqual(result.invocations[0].stderr, "Execution error: boom")

    def test_run_code_delegation_is_recorded(self):
        """Given inline code, when run_code is called, then the underlying
        run_file invocation is recorded."""
        checker, _student = self._make_checker()

        result = ExerciseResult(module=0, exercise=0, name="Code", passed=True)
        with checker.runner.record_into(result):
            _code, stdout, _stderr = checker.runner.run_code("print('hello from code')")

        self.assertEqual(stdout.strip(), "hello from code")
        self.assertEqual(len(result.invocations), 1)
        self.assertIn("hello from code", result.invocations[0].stdout)

    def test_run_and_validate_records_invocation(self):
        """Given a script with matching output, when run_and_validate is called
        within a recording context, then the run is recorded and scalar result
        fields are preserved."""
        from modules import run_and_validate

        checker, student = self._make_checker()
        self._write(student, "ex0/ft_hello.py", "print('hello')\n")

        result = ExerciseResult(module=0, exercise=0, name="Hello", passed=True)
        with checker.runner.record_into(result):
            code, stdout, stderr = run_and_validate(
                checker, result, "ex0/ft_hello.py", expected_patterns=[r"hello"]
            )

        self.assertEqual(code, 0)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout.strip(), "hello")
        self.assertEqual(len(result.invocations), 1)
        self.assertIn("hello", result.invocations[0].stdout)

    def test_recording_is_scoped_and_cleared_after_check_raises(self):
        """Given a check function that runs a file then raises, when the
        exercise is checked, then only the runs before the raise are retained
        and the recording context is cleared for subsequent direct calls."""
        checker, student = self._make_checker()
        script = self._write(student, "one.py", "print('one')\n")

        def boom(_checker, result):
            _checker.runner.run_file(script)
            raise RuntimeError("boom")

        module_def = SimpleNamespace()
        module_def.EXERCISES = {1: {"name": "Boom", "check": boom}}

        result = checker.check_exercise(9, 1, module_def)

        self.assertFalse(result.passed)
        self.assertEqual(len(result.invocations), 1)
        self.assertIn("Checker internal error", result.errors[0])

        # Context cleared: a subsequent direct run_file records nothing new.
        checker.runner.run_file(script)
        self.assertEqual(len(result.invocations), 1)

    def test_format_invocations_marks_empty_streams(self):
        """Given an invocation with empty stderr, when formatted, then the empty
        stream is visibly marked and command/cwd/exit code are present."""
        invocation = ProcessInvocation(
            command=["python", "x.py", "1"],
            cwd="/tmp",
            exit_code=0,
            stdout="hello\n",
            stderr="",
        )

        lines = "\n".join(format_invocations([invocation]))

        self.assertIn("Command: python x.py 1", lines)
        self.assertIn("Cwd: /tmp", lines)
        self.assertIn("Exit code: 0", lines)
        self.assertIn("hello", lines)
        self.assertIn("(empty)", lines)


if __name__ == "__main__":
    unittest.main()
