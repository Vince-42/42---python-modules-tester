#!/usr/bin/env python3
"""
Python Module Checker - Validates student solutions across 9 modules.

Usage:
    python checker.py --module 0          # Check module 0 only
    python checker.py --module 1          # Check module 1 only
    python checker.py --all               # Check all modules
    python checker.py --module 3 --ex 2   # Check module 3, exercise 2 only
"""

import argparse
import importlib.util
import os
import re
import subprocess
import sys
import tempfile
import traceback
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from tracing import ProcessInvocation, format_invocations


@dataclass
class ExerciseResult:
    """Result of checking a single exercise."""
    module: int
    exercise: Union[int, str]
    name: str
    passed: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    trace: str = ""
    files_checked: List[str] = field(default_factory=list)
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    invocations: List[ProcessInvocation] = field(default_factory=list)


@dataclass
class ModuleResult:
    """Result of checking a whole module."""
    module: int
    name: str
    exercises: List[ExerciseResult] = field(default_factory=list)
    
    @property
    def passed_count(self) -> int:
        return sum(1 for e in self.exercises if e.passed)
    
    @property
    def total_count(self) -> int:
        return len(self.exercises)


class ExerciseRunner:
    """Handles subprocess execution of student code with controlled inputs."""
    
    DEFAULT_TIMEOUT = 10
    
    def __init__(self, student_dir: Path, trace_dir: Path):
        self.student_dir = student_dir
        self.trace_dir = trace_dir
        self.env = os.environ.copy()
        # Ensure student packages can be imported
        self.env["PYTHONPATH"] = str(student_dir) + os.pathsep + self.env.get("PYTHONPATH", "")
        self._active_result: Optional[ExerciseResult] = None

    @contextmanager
    def record_into(self, result: Optional[ExerciseResult]):
        """Route subsequent run_file invocations into the given result.

        The previous active result is restored on exit, including when an
        exception propagates, so recording is always scoped to the currently
        checked exercise.
        """
        previous = self._active_result
        self._active_result = result
        try:
            yield
        finally:
            self._active_result = previous

    def _record(
        self,
        command: List[str],
        cwd: str,
        exit_code: int,
        stdout: str,
        stderr: str
    ) -> None:
        """Append a subprocess invocation to the active result, if any."""
        if self._active_result is not None:
            self._active_result.invocations.append(
                ProcessInvocation(
                    command=list(command),
                    cwd=cwd,
                    exit_code=exit_code,
                    stdout=stdout,
                    stderr=stderr,
                )
            )

    def run_file(
        self,
        file_path: Path,
        args: List[str] = None,
        stdin: str = "",
        timeout: int = None,
        cwd: Path = None
    ) -> Tuple[int, str, str]:
        """
        Run a Python file via subprocess.

        Returns: (exit_code, stdout, stderr)
        """
        cmd = [sys.executable, str(file_path)]
        if args:
            cmd.extend(args)
        resolved_cwd = str(cwd) if cwd else str(self.student_dir)

        if not file_path.exists():
            code, stdout, stderr = 1, "", f"File not found: {file_path}"
        else:
            try:
                result = subprocess.run(
                    cmd,
                    input=stdin,
                    capture_output=True,
                    text=True,
                    timeout=timeout or self.DEFAULT_TIMEOUT,
                    env=self.env,
                    cwd=resolved_cwd
                )
                code, stdout, stderr = result.returncode, result.stdout, result.stderr
            except subprocess.TimeoutExpired:
                code, stdout, stderr = 124, "", "Execution timed out"
            except Exception as e:
                code, stdout, stderr = 1, "", f"Execution error: {e}"

        self._record(cmd, resolved_cwd, code, stdout, stderr)
        return code, stdout, stderr
    
    def run_code(
        self,
        code: str,
        stdin: str = "",
        timeout: int = None,
        cwd: Path = None
    ) -> Tuple[int, str, str]:
        """Run Python code string via subprocess."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            tmp_path = f.name
        
        try:
            return self.run_file(Path(tmp_path), stdin=stdin, timeout=timeout, cwd=cwd)
        finally:
            os.unlink(tmp_path)


class StaticAnalyzer:
    """Runs flake8 and mypy on Python files."""
    
    def __init__(self):
        self.flake8_available = self._check_tool("flake8")
        self.mypy_available = self._check_tool("mypy")
    
    def _check_tool(self, tool: str) -> bool:
        try:
            subprocess.run([tool, "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def analyze(self, file_path: Path) -> Tuple[List[str], List[str]]:
        """
        Run flake8 and mypy on a file.
        
        Returns: (flake8_errors, mypy_errors)
        """
        flake8_errors = []
        mypy_errors = []
        
        if self.flake8_available:
            try:
                result = subprocess.run(
                    ["flake8", str(file_path), "--max-line-length=120"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.stdout:
                    flake8_errors = [line for line in result.stdout.strip().split("\n") if line]
            except Exception as e:
                flake8_errors = [f"flake8 execution error: {e}"]
        
        if self.mypy_available:
            try:
                result = subprocess.run(
                    ["mypy", str(file_path), "--ignore-missing-imports"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.stdout and "error:" in result.stdout.lower():
                    mypy_errors = [
                        line for line in result.stdout.strip().split("\n")
                        if "error:" in line.lower()
                    ]
            except Exception as e:
                mypy_errors = [f"mypy execution error: {e}"]
        
        return flake8_errors, mypy_errors


class TraceGenerator:
    """Generates trace files for debugging."""
    
    def __init__(self, trace_dir: Path):
        self.trace_dir = trace_dir
        self.trace_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(
        self,
        result: ExerciseResult,
        flake8_errors: List[str] = None,
        mypy_errors: List[str] = None
    ) -> str:
        """Generate trace content and write to file."""
        trace_lines = [
            f"=== Module {result.module}, Exercise {result.exercise}: {result.name} ===",
            f"Status: {'PASSED' if result.passed else 'FAILED'}",
            "",
            f"Exit code: {result.exit_code}",
            f"Files checked: {', '.join(dict.fromkeys(result.files_checked))}",
            "",
            "--- STDOUT ---",
            result.stdout if result.stdout else "(empty)",
            "",
            "--- STDERR ---",
            result.stderr if result.stderr else "(empty)",
            "",
        ]
        trace_lines.extend(format_invocations(result.invocations))
        
        if flake8_errors:
            trace_lines.extend([
                "--- FLAKE8 ERRORS ---",
                *flake8_errors,
                ""
            ])
        
        if mypy_errors:
            trace_lines.extend([
                "--- MYPY ERRORS ---",
                *mypy_errors,
                ""
            ])
        
        if result.errors:
            trace_lines.extend([
                "--- VALIDATION ERRORS ---",
                *result.errors,
                ""
            ])
        
        if result.warnings:
            trace_lines.extend([
                "--- WARNINGS ---",
                *result.warnings,
                ""
            ])
        
        trace_content = "\n".join(trace_lines)
        
        # Write to file
        trace_file = self.trace_dir / f"module{result.module:02d}_ex{result.exercise}_{result.name.replace(' ', '_')}.trace.txt"
        trace_file.write_text(trace_content)
        
        return str(trace_file)


class Checker:
    """Main checker orchestrator."""
    
    def __init__(self, student_dir: Path, trace_dir: Path, verbose: bool = False):
        self.student_dir = student_dir
        self.trace_dir = trace_dir
        self.verbose = verbose
        self.runner = ExerciseRunner(student_dir, trace_dir)
        self.analyzer = StaticAnalyzer()
        self.tracer = TraceGenerator(trace_dir)
        self.modules: Dict[int, Any] = {}
    
    def load_module(self, module_num: int) -> bool:
        """Load a module's test definitions."""
        module_file = Path(__file__).parent / "modules" / f"module{module_num:02d}.py"
        if not module_file.exists():
            print(f"Warning: Module {module_num} test definitions not found at {module_file}")
            return False
        
        spec = importlib.util.spec_from_file_location(f"module{module_num:02d}", module_file)
        module = importlib.util.module_from_spec(spec)
        sys.modules[f"module{module_num:02d}"] = module
        spec.loader.exec_module(module)
        
        self.modules[module_num] = module
        return True
    
    def check_exercise(
        self,
        module_num: int,
        exercise: Union[int, str],
        module_def: Any
    ) -> ExerciseResult:
        """Check a single exercise."""
        # Get exercise definition
        exercises = getattr(module_def, "EXERCISES", {})
        if exercise not in exercises:
            return ExerciseResult(
                module=module_num,
                exercise=exercise,
                name="Unknown",
                passed=False,
                errors=[f"Exercise {exercise} not defined in module {module_num}"]
            )
        
        ex_def = exercises[exercise]
        result = ExerciseResult(
            module=module_num,
            exercise=exercise,
            name=ex_def.get("name", f"Exercise {exercise}"),
            passed=True
        )
        
        flake8_errors = []
        mypy_errors = []
        
        try:
            check_fn = ex_def.get("check")
            if check_fn:
                with self.runner.record_into(result):
                    check_fn(self, result)
            
            checked_files = list(dict.fromkeys(result.files_checked))
            for file_path_str in checked_files:
                file_path = self.student_dir / file_path_str
                if file_path.exists() and file_path.suffix == ".py":
                    f_errors, m_errors = self.analyzer.analyze(file_path)
                    flake8_errors.extend(f_errors)
                    mypy_errors.extend(m_errors)
            
            expected_mypy = ex_def.get("expected_mypy_errors", [])
            if mypy_errors:
                for expected in expected_mypy:
                    mypy_errors = [e for e in mypy_errors if expected not in e]
                if mypy_errors:
                    result.passed = False
                    result.errors.extend([f"mypy: {e}" for e in mypy_errors])
            if flake8_errors:
                result.passed = False
                result.errors.extend([f"flake8: {e}" for e in flake8_errors])
            
        except Exception as e:
            result.passed = False
            result.errors.append(f"Checker internal error: {e}")
            if self.verbose:
                traceback.print_exc()
        
        trace_file = self.tracer.generate(
            result=result,
            flake8_errors=flake8_errors,
            mypy_errors=mypy_errors
        )
        result.trace = trace_file
        
        return result
    
    def check_module(self, module_num: int) -> ModuleResult:
        """Check all exercises in a module."""
        if not self.load_module(module_num):
            return ModuleResult(
                module=module_num,
                name=f"Module {module_num}",
                exercises=[]
            )
        
        module_def = self.modules[module_num]
        module_name = getattr(module_def, "MODULE_NAME", f"Module {module_num}")
        result = ModuleResult(module=module_num, name=module_name)
        
        exercises = getattr(module_def, "EXERCISES", {})
        for exercise_id in sorted(exercises.keys(), key=lambda x: (isinstance(x, str), x)):
            ex_result = self.check_exercise(module_num, exercise_id, module_def)
            result.exercises.append(ex_result)
        
        return result
    
    def check_all(self) -> List[ModuleResult]:
        """Check all available modules."""
        results = []
        for module_file in sorted(Path(__file__).parent.glob("modules/module*.py")):
            match = re.match(r"module(\d{2})\.py", module_file.name)
            if match:
                module_num = int(match.group(1))
                result = self.check_module(module_num)
                if result.exercises:
                    results.append(result)
        return results
    
    def print_results(self, results: List[ModuleResult]):
        """Print results to console."""
        print("\n" + "=" * 70)
        print("PYTHON MODULE CHECKER RESULTS")
        print("=" * 70)
        
        total_passed = 0
        total_exercises = 0
        
        for module_result in results:
            print(f"\n📚 {module_result.name}")
            print("-" * 50)
            
            for ex in module_result.exercises:
                status = "✅ PASS" if ex.passed else "❌ FAIL"
                print(f"  {status} | Ex {ex.exercise}: {ex.name}")
                
                if not ex.passed and ex.errors:
                    for error in ex.errors[:3]:  # Show first 3 errors
                        print(f"       → {error}")
                
                if ex.warnings and self.verbose:
                    for warning in ex.warnings[:2]:
                        print(f"       ⚠ {warning}")
                
                if not ex.passed:
                    print(f"       📄 Trace: {ex.trace}")
            
            module_total = module_result.total_count
            module_passed = module_result.passed_count
            total_passed += module_passed
            total_exercises += module_total
            
            print(f"  Module summary: {module_passed}/{module_total} passed")
        
        print("\n" + "=" * 70)
        print(f"OVERALL: {total_passed}/{total_exercises} exercises passed")
        print(f"Trace files: {self.trace_dir}")
        print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Python Module Checker - Validate student solutions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python checker.py --module 1           # Check module 1 only
  python checker.py --all                # Check all modules
  python checker.py --module 3 --ex 2   # Check specific exercise
        """
    )
    parser.add_argument(
        "--student-dir",
        default=".",
        help="Directory containing student submissions (default: current directory)"
    )
    parser.add_argument(
        "--trace-dir",
        default="traces",
        help="Directory for trace files (default: traces/)"
    )
    parser.add_argument(
        "--module",
        type=int,
        help="Check specific module only (0-8)"
    )
    parser.add_argument(
        "--ex",
        type=str,
        help="Check specific exercise only (requires --module)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Check all modules"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output including warnings"
    )
    
    args = parser.parse_args()
    
    student_dir = Path(args.student_dir).resolve()
    trace_dir = Path(args.trace_dir).resolve()
    
    if not student_dir.exists():
        print(f"Error: Student directory '{student_dir}' does not exist")
        sys.exit(1)
    
    checker = Checker(student_dir, trace_dir, verbose=args.verbose)
    
    if args.ex and not args.module:
        print("Error: --ex requires --module")
        sys.exit(1)
    
    if args.module is not None:
        result = checker.check_module(args.module)
        if args.ex:
            # Filter to specific exercise
            result.exercises = [
                e for e in result.exercises
                if str(e.exercise) == args.ex
            ]
        checker.print_results([result])
    elif args.all:
        results = checker.check_all()
        checker.print_results(results)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
