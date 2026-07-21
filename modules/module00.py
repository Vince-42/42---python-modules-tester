"""Module 0: Garden Foundations - Basic Python"""

import ast
import re

from checker import Checker, ExerciseResult
from modules import (
    check_file_exists,
    check_function_exists,
)

MODULE_NAME = "Module 0: Garden Foundations - Basic Python"


def _run_function(checker: Checker, result: ExerciseResult, file_path: str, function_name: str, stdin: str = "", args: str = "") -> tuple:
    """Run a student function via a wrapper script."""
    if not check_file_exists(checker, result, file_path):
        return 1, "", ""

    full_path = checker.student_dir / file_path
    student_dir = str(full_path.parent)

    wrapper = f"""
import sys
sys.path.insert(0, {repr(student_dir)})
from {function_name} import {function_name}
{function_name}({args})
"""
    code, stdout, stderr = checker.runner.run_code(wrapper, stdin=stdin)
    return code, stdout, stderr


def check_ex0(checker: Checker, result: ExerciseResult):
    """Exercise 0: Hello Garden"""
    file_path = "ex0/ft_hello_garden.py"

    check_function_exists(checker, result, file_path, "ft_hello_garden")

    if not result.passed:
        return

    code, stdout, stderr = _run_function(checker, result, file_path, "ft_hello_garden")

    if not re.search(r"Hello,\s*Garden\s*Community!", stdout):
        result.passed = False
        result.errors.append("Missing expected output: Hello, Garden Community!")


def check_ex1(checker: Checker, result: ExerciseResult):
    """Exercise 1: Garden Name"""
    file_path = "ex1/ft_garden_name.py"

    check_function_exists(checker, result, file_path, "ft_garden_name")

    if not result.passed:
        return

    code, stdout, stderr = _run_function(
        checker, result, file_path, "ft_garden_name", stdin="Community Garden\n"
    )

    if not re.search(r"Garden:\s*Community Garden", stdout):
        result.passed = False
        result.errors.append("Missing expected output: Garden: Community Garden")

    if not re.search(r"Status:\s*Growing well!", stdout):
        result.passed = False
        result.errors.append("Missing expected output: Status: Growing well!")


def check_ex2(checker: Checker, result: ExerciseResult):
    """Exercise 2: Garden Plot Area"""
    file_path = "ex2/ft_plot_area.py"

    check_function_exists(checker, result, file_path, "ft_plot_area")

    if not result.passed:
        return

    code, stdout, stderr = _run_function(
        checker, result, file_path, "ft_plot_area", stdin="5\n3\n"
    )

    if not re.search(r"Plot area:\s*15", stdout):
        result.passed = False
        result.errors.append("Missing expected output: Plot area: 15")


def check_ex3(checker: Checker, result: ExerciseResult):
    """Exercise 3: Harvest Total"""
    file_path = "ex3/ft_harvest_total.py"

    check_function_exists(checker, result, file_path, "ft_harvest_total")

    if not result.passed:
        return

    code, stdout, stderr = _run_function(
        checker, result, file_path, "ft_harvest_total", stdin="5\n8\n3\n"
    )

    if not re.search(r"Total harvest:\s*16", stdout):
        result.passed = False
        result.errors.append("Missing expected output: Total harvest: 16")


def check_ex4(checker: Checker, result: ExerciseResult):
    """Exercise 4: Plant Age Check"""
    file_path = "ex4/ft_plant_age.py"

    check_function_exists(checker, result, file_path, "ft_plant_age")

    if not result.passed:
        return

    test_cases = [
        ("75\n", [r"Plant is ready to harvest!"]),
        ("45\n", [r"Plant needs more time to grow\."]),
        ("0\n", [r"Plant needs more time to grow\."]),
    ]

    for stdin, patterns in test_cases:
        code, stdout, stderr = _run_function(
            checker, result, file_path, "ft_plant_age", stdin=stdin
        )
        for pattern in patterns:
            if not re.search(pattern, stdout):
                result.passed = False
                result.errors.append(
                    f"Input '{stdin.strip()}' - Missing pattern: {pattern}"
                )


def check_ex5(checker: Checker, result: ExerciseResult):
    """Exercise 5: Water Reminder"""
    file_path = "ex5/ft_water_reminder.py"

    check_function_exists(checker, result, file_path, "ft_water_reminder")

    if not result.passed:
        return

    test_cases = [
        ("4\n", [r"Water the plants!"]),
        ("1\n", [r"Plants are fine"]),
        ("2\n", [r"Plants are fine"]),
    ]

    for stdin, patterns in test_cases:
        code, stdout, stderr = _run_function(
            checker, result, file_path, "ft_water_reminder", stdin=stdin
        )
        for pattern in patterns:
            if not re.search(pattern, stdout):
                result.passed = False
                result.errors.append(
                    f"Input '{stdin.strip()}' - Missing pattern: {pattern}"
                )


def check_ex6(checker: Checker, result: ExerciseResult):
    """Exercise 6: Count to Harvest"""
    iterative_file = "ex6/ft_count_harvest_iterative.py"
    recursive_file = "ex6/ft_count_harvest_recursive.py"

    check_function_exists(checker, result, iterative_file, "ft_count_harvest_iterative")
    check_function_exists(checker, result, recursive_file, "ft_count_harvest_recursive")

    if not result.passed:
        return

    test_inputs = ["0\n", "5\n", "100\n"]

    for stdin in test_inputs:
        code_i, stdout_i, stderr_i = _run_function(
            checker, result, iterative_file, "ft_count_harvest_iterative", stdin=stdin
        )
        code_r, stdout_r, stderr_r = _run_function(
            checker, result, recursive_file, "ft_count_harvest_recursive", stdin=stdin
        )

        if stdout_i.strip() != stdout_r.strip():
            result.passed = False
            result.errors.append(
                f"Input '{stdin.strip()}' - Iterative and recursive outputs differ"
            )

        if "Harvest time!" not in stdout_i:
            result.passed = False
            result.errors.append(
                f"Input '{stdin.strip()}' - Missing 'Harvest time!' in iterative version"
            )

    # Check that recursive version actually calls itself
    full_path_r = checker.student_dir / recursive_file
    content = full_path_r.read_text()
    if "ft_count_harvest_recursive" not in content:
        result.passed = False
        result.errors.append("Recursive function must call itself")


def check_ex7(checker: Checker, result: ExerciseResult):
    """Exercise 7: Seed Inventory with Type Annotations"""
    file_path = "ex7/ft_seed_inventory.py"

    if not check_file_exists(checker, result, file_path):
        return

    full_path = checker.student_dir / file_path

    # Verify function exists with type annotations
    try:
        content = full_path.read_text()
        tree = ast.parse(content)

        func_found = False
        has_annotations = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "ft_seed_inventory":
                func_found = True
                for arg in node.args.args:
                    if arg.annotation is not None:
                        has_annotations = True
                if node.returns is not None:
                    has_annotations = True
                break

        if not func_found:
            result.passed = False
            result.errors.append("Missing function: ft_seed_inventory")
            return

        if not has_annotations:
            result.passed = False
            result.errors.append("ft_seed_inventory must have type annotations")
            return
    except SyntaxError as e:
        result.passed = False
        result.errors.append(f"Syntax error in {file_path}: {e}")
        return

    if "Unknown unit type" not in content:
        result.passed = False
        result.errors.append("Missing handling for unsupported unit types")
        return

    # Test all supported units + unsupported unit via wrapper script
    student_dir = str(full_path.parent)
    test_cases = [
        ('"tomato", 15, "packets"', "Tomato seeds: 15 packets available"),
        ('"carrot", 8, "grams"', "Carrot seeds: 8 grams total"),
        ('"lettuce", 12, "area"', "Lettuce seeds: covers 12 square meters"),
        ('"unknown", 5, "bad_unit"', "Unknown unit type"),
    ]

    for args, expected in test_cases:
        wrapper = f"""
import sys
sys.path.insert(0, {repr(student_dir)})
from ft_seed_inventory import ft_seed_inventory
ft_seed_inventory({args})
"""
        code, stdout, stderr = checker.runner.run_code(wrapper)
        actual = stdout.strip()
        if actual != expected:
            result.passed = False
            result.errors.append(
                f"ft_seed_inventory({args}) - Expected: '{expected}', Got: '{actual}'"
            )


EXERCISES = {
    0: {"name": "Hello Garden", "check": check_ex0},
    1: {"name": "Garden Name", "check": check_ex1},
    2: {"name": "Garden Plot Area", "check": check_ex2},
    3: {"name": "Harvest Total", "check": check_ex3},
    4: {"name": "Plant Age Check", "check": check_ex4},
    5: {"name": "Water Reminder", "check": check_ex5},
    6: {"name": "Count to Harvest", "check": check_ex6},
    7: {"name": "Seed Inventory with Type Annotations", "check": check_ex7},
}
