"""Helper utilities for module test definitions."""

import ast
import re
from pathlib import Path
from typing import Callable, List, Optional, Tuple

from checker import Checker, ExerciseResult, ExerciseRunner


def check_file_exists(checker: Checker, result: ExerciseResult, file_path: str) -> bool:
    """Check if a file exists in the student directory."""
    full_path = checker.student_dir / file_path
    if not full_path.exists():
        result.passed = False
        result.errors.append(f"Missing file: {file_path}")
        return False
    result.files_checked.append(file_path)
    return True


def check_directory_exists(checker: Checker, result: ExerciseResult, dir_path: str) -> bool:
    """Check if a directory exists."""
    full_path = checker.student_dir / dir_path
    if not full_path.exists() or not full_path.is_dir():
        result.passed = False
        result.errors.append(f"Missing directory: {dir_path}")
        return False
    return True


def run_and_validate(
    checker: Checker,
    result: ExerciseResult,
    file_path: str,
    args: List[str] = None,
    stdin: str = "",
    expected_patterns: List[str] = None,
    expected_output: str = None,
    exit_code: int = 0,
    timeout: int = 10
) -> Tuple[int, str, str]:
    """
    Run a file and validate output.
    
    expected_patterns: List of regex patterns that must all match in stdout
    expected_output: Exact expected output (overrides patterns if set)
    """
    if not check_file_exists(checker, result, file_path):
        return 1, "", ""
    
    full_path = checker.student_dir / file_path
    code, stdout, stderr = checker.runner.run_file(
        full_path,
        args=args or [],
        stdin=stdin,
        timeout=timeout,
        cwd=checker.student_dir
    )
    
    result.exit_code = code
    result.stdout = stdout
    result.stderr = stderr
    
    if code != exit_code:
        result.passed = False
        result.errors.append(f"Expected exit code {exit_code}, got {code}")
    
    if expected_output is not None:
        # Normalize whitespace for comparison
        actual = stdout.strip()
        expected = expected_output.strip()
        if actual != expected:
            result.passed = False
            result.errors.append("Output mismatch")
            if checker.verbose:
                result.errors.append(f"Expected:\n{expected}\nActual:\n{actual}")
    
    if expected_patterns:
        for pattern in expected_patterns:
            if not re.search(pattern, stdout, re.MULTILINE | re.IGNORECASE):
                result.passed = False
                result.errors.append(f"Missing pattern in output: {pattern}")
    
    return code, stdout, stderr


def check_function_exists(
    checker: Checker,
    result: ExerciseResult,
    file_path: str,
    function_name: str
) -> bool:
    """Check if a function exists in a Python file."""
    if not check_file_exists(checker, result, file_path):
        return False
    
    full_path = checker.student_dir / file_path
    try:
        content = full_path.read_text()
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == function_name:
                    return True
        
        result.passed = False
        result.errors.append(f"Missing function: {function_name}")
        return False
    except SyntaxError as e:
        result.passed = False
        result.errors.append(f"Syntax error in {file_path}: {e}")
        return False


def check_class_exists(
    checker: Checker,
    result: ExerciseResult,
    file_path: str,
    class_name: str
) -> bool:
    """Check if a class exists in a Python file."""
    if not check_file_exists(checker, result, file_path):
        return False
    
    full_path = checker.student_dir / file_path
    try:
        content = full_path.read_text()
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name == class_name:
                    return True
        
        result.passed = False
        result.errors.append(f"Missing class: {class_name}")
        return False
    except SyntaxError as e:
        result.passed = False
        result.errors.append(f"Syntax error in {file_path}: {e}")
        return False


def check_class_method_exists(
    checker: Checker,
    result: ExerciseResult,
    file_path: str,
    class_name: str,
    method_name: str
) -> bool:
    """Check if a method exists in a class."""
    if not check_file_exists(checker, result, file_path):
        return False
    
    full_path = checker.student_dir / file_path
    try:
        content = full_path.read_text()
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if item.name == method_name:
                            return True
        
        result.passed = False
        result.errors.append(f"Missing method: {class_name}.{method_name}")
        return False
    except SyntaxError as e:
        result.passed = False
        result.errors.append(f"Syntax error in {file_path}: {e}")
        return False


def check_class_attribute(
    checker: Checker,
    result: ExerciseResult,
    file_path: str,
    class_name: str,
    attribute_name: str
) -> bool:
    """Check if a class has an attribute (in __init__ or class body)."""
    if not check_file_exists(checker, result, file_path):
        return False
    
    full_path = checker.student_dir / file_path
    try:
        content = full_path.read_text()
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                # Check class body for assignments
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name) and target.id == attribute_name:
                                return True
                    elif isinstance(item, ast.AnnAssign):
                        if isinstance(item.target, ast.Name) and item.target.id == attribute_name:
                            return True
                    elif isinstance(item, ast.FunctionDef) and item.name == "__init__":
                        # Check __init__ for self.attribute assignments
                        for init_item in ast.walk(item):
                            if isinstance(init_item, ast.Assign):
                                for target in init_item.targets:
                                    if isinstance(target, ast.Attribute):
                                        if target.value.id == "self" and target.attr == attribute_name:
                                            return True
        
        result.passed = False
        result.errors.append(f"Missing attribute: {class_name}.{attribute_name}")
        return False
    except SyntaxError as e:
        result.passed = False
        result.errors.append(f"Syntax error in {file_path}: {e}")
        return False


def check_inheritance(
    checker: Checker,
    result: ExerciseResult,
    file_path: str,
    child_class: str,
    parent_class: str
) -> bool:
    """Check if a class inherits from another."""
    if not check_file_exists(checker, result, file_path):
        return False
    
    full_path = checker.student_dir / file_path
    try:
        content = full_path.read_text()
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == child_class:
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == parent_class:
                        return True
                    elif isinstance(base, ast.Attribute):
                        if base.attr == parent_class:
                            return True
        
        result.passed = False
        result.errors.append(f"{child_class} must inherit from {parent_class}")
        return False
    except SyntaxError as e:
        result.passed = False
        result.errors.append(f"Syntax error in {file_path}: {e}")
        return False


def check_import_in_file(
    checker: Checker,
    result: ExerciseResult,
    file_path: str,
    import_pattern: str
) -> bool:
    """Check if a file contains a specific import."""
    if not check_file_exists(checker, result, file_path):
        return False
    
    full_path = checker.student_dir / file_path
    content = full_path.read_text()
    
    if re.search(import_pattern, content):
        return True
    
    result.passed = False
    result.errors.append(f"Missing import pattern in {file_path}: {import_pattern}")
    return False


def check_try_except_block(
    checker: Checker,
    result: ExerciseResult,
    file_path: str
) -> bool:
    """Check if a file contains try/except blocks."""
    if not check_file_exists(checker, result, file_path):
        return False
    
    full_path = checker.student_dir / file_path
    try:
        content = full_path.read_text()
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                return True
        
        result.passed = False
        result.errors.append(f"Missing try/except block in {file_path}")
        return False
    except SyntaxError as e:
        result.passed = False
        result.errors.append(f"Syntax error in {file_path}: {e}")
        return False
