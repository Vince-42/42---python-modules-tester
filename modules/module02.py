"""Module 2: Exception handling exercises"""

import ast
import re

from checker import Checker, ExerciseResult
from modules import (
    check_class_exists,
    check_class_method_exists,
    check_directory_exists,
    check_file_exists,
    check_function_exists,
    check_try_except_block,
    run_and_validate,
)

MODULE_NAME = "Module 2: Exception Handling"


def check_ex0(checker: Checker, result: ExerciseResult):
    """Exercise 0: Agricultural Data Validation"""
    file_path = "ex0/ft_first_exception.py"
    
    check_function_exists(checker, result, file_path, "input_temperature")
    check_function_exists(checker, result, file_path, "test_temperature")
    check_try_except_block(checker, result, file_path)
    
    if not result.passed:
        return
    
    code, stdout, stderr = run_and_validate(
        checker, result, file_path,
        expected_patterns=[
            r"Temperature is now\s+\d+",
            r"error|exception|invalid|fail",
            r"didn['']?t crash|did not crash|no crash|completed",
        ]
    )


def check_ex1(checker: Checker, result: ExerciseResult):
    """Exercise 1: Agricultural Data Validation Pipeline"""
    file_path = "ex1/ft_raise_exception.py"
    
    check_function_exists(checker, result, file_path, "input_temperature")
    check_function_exists(checker, result, file_path, "test_temperature")
    
    if not result.passed:
        return
    
    # Verify input_temperature actually raises for out-of-range values
    full_path = checker.student_dir / file_path
    student_dir = str(full_path.parent)
    test_cases = [
        ('"100"', "too hot|exceed|above limit|maximum"),
        ('"-50"', "too cold|below limit|minimum"),
    ]
    for args, expected_pattern in test_cases:
        wrapper = f"""
import sys
sys.path.insert(0, {repr(student_dir)})
from ft_raise_exception import input_temperature
try:
    input_temperature({args})
    print("NO_EXCEPTION_RAISED")
except Exception as e:
    print(f"RAISED: {{e}}")
"""
        code, stdout, stderr = checker.runner.run_code(wrapper)
        if "NO_EXCEPTION_RAISED" in stdout:
            result.passed = False
            result.errors.append(
                f"input_temperature({args}) did not raise an exception for out-of-range value"
            )
        elif not re.search(expected_pattern, stdout, re.IGNORECASE):
            result.passed = False
            result.errors.append(
                f"input_temperature({args}) raised exception but message did not match expected pattern: {expected_pattern}"
            )
    
    code, stdout, stderr = run_and_validate(
        checker, result, file_path,
        expected_patterns=[
            r"Temperature is now\s+\d+",
            r"error|exception|invalid|fail",
            r"too hot|too high|exceed|above limit|maximum",
            r"too cold|too low|below limit|minimum",
            r"didn['']?t crash|did not crash|no crash|completed",
        ]
    )


def check_ex2(checker: Checker, result: ExerciseResult):
    """Exercise 2: Different Types of Problems"""
    file_path = "ex2/ft_different_errors.py"
    
    check_function_exists(checker, result, file_path, "garden_operations")
    check_function_exists(checker, result, file_path, "test_error_types")
    
    if not result.passed:
        return
    
    # Verify test_error_types has no parameters
    full_path = checker.student_dir / file_path
    try:
        content = full_path.read_text()
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "test_error_types":
                if node.args.args or node.args.vararg or node.args.kwarg or node.args.posonlyargs:
                    result.passed = False
                    result.errors.append("test_error_types() must not take any parameters")
                break
    except SyntaxError:
        pass
    
    code, stdout, stderr = run_and_validate(
        checker, result, file_path,
        expected_patterns=[
            r"ValueError",
            r"ZeroDivisionError",
            r"FileNotFoundError",
            r"TypeError",
            r"success|completed|finished|done",
        ]
    )


def check_ex3(checker: Checker, result: ExerciseResult):
    """Exercise 3: Making Your Own Error Types"""
    file_path = "ex3/ft_custom_errors.py"
    
    check_class_exists(checker, result, file_path, "GardenError")
    check_class_exists(checker, result, file_path, "PlantError")
    check_class_exists(checker, result, file_path, "WaterError")
    
    from modules import check_inheritance
    check_inheritance(checker, result, file_path, "PlantError", "GardenError")
    check_inheritance(checker, result, file_path, "WaterError", "GardenError")
    
    if not result.passed:
        return
    
    code, stdout, stderr = run_and_validate(
        checker, result, file_path,
        expected_patterns=[
            r"PlantError",
            r"WaterError",
            r"GardenError",
        ]
    )


def check_ex4(checker: Checker, result: ExerciseResult):
    """Exercise 4: Finally Block - Always Clean Up"""
    file_path = "ex4/ft_finally_block.py"
    
    check_function_exists(checker, result, file_path, "water_plant")
    check_function_exists(checker, result, file_path, "test_watering_system")
    
    # Check for finally block
    full_path = checker.student_dir / file_path
    if full_path.exists():
        content = full_path.read_text()
        if "finally" not in content:
            result.passed = False
            result.errors.append("Missing finally block")
    
    if not result.passed:
        return
    
    # Verify test_watering_system has no parameters
    try:
        content = full_path.read_text()
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "test_watering_system":
                if node.args.args or node.args.vararg or node.args.kwarg or node.args.posonlyargs:
                    result.passed = False
                    result.errors.append("test_watering_system() must not take any parameters")
                break
    except SyntaxError:
        pass
    
    code, stdout, stderr = run_and_validate(
        checker, result, file_path,
        expected_patterns=[
            r"open.*water|water.*open",
            r"clos.*water|water.*clos|shut.*water",
            r"cleanup.*always|always.*cleanup|cleanup.*happen",
        ]
    )


EXERCISES = {
    0: {"name": "Agricultural Data Validation", "check": check_ex0},
    1: {"name": "Data Validation Pipeline", "check": check_ex1},
    2: {"name": "Different Types of Problems", "check": check_ex2, "expected_mypy_errors": ["Unsupported operand types for + (\"str\" and \"int\")"]},
    3: {"name": "Making Your Own Error Types", "check": check_ex3},
    4: {"name": "Finally Block - Always Clean Up", "check": check_ex4},
}
