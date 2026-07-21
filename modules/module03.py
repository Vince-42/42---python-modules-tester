"""Module 3: Data Quest - Mastering Python Collections"""

import ast
import re

from checker import Checker, ExerciseResult
from modules import (
    check_directory_exists,
    check_file_exists,
    check_function_exists,
    check_try_except_block,
    run_and_validate,
)

MODULE_NAME = "Module 3: Python Collections"


def check_ex0(checker: Checker, result: ExerciseResult):
    """Exercise 0: Command Quest"""
    file_path = "ex0/ft_command_quest.py"
    
    if not check_file_exists(checker, result, file_path):
        return
    
    # Test with no arguments
    code, stdout, stderr = run_and_validate(
        checker, result, file_path,
        expected_patterns=[
            r"=== Command Quest ===",
            r"No arguments provided!",
            r"Total arguments:\s*1",
        ]
    )
    
    if not result.passed:
        return
    
    # Test with arguments
    code, stdout, stderr = checker.runner.run_file(
        checker.student_dir / file_path,
        args=["hello", "world", "42"],
    )
    
    if not re.search(r"Arguments received:\s*3", stdout):
        result.passed = False
        result.errors.append("Missing 'Arguments received: 3' output")
    
    if not re.search(r"Argument 1:\s*hello", stdout):
        result.passed = False
        result.errors.append("Missing numbered argument output")
    
    if not re.search(r"Total arguments:\s*4", stdout):
        result.passed = False
        result.errors.append("Missing 'Total arguments: 4' output")


def check_ex1(checker: Checker, result: ExerciseResult):
    """Exercise 1: Score Cruncher"""
    file_path = "ex1/ft_score_analytics.py"
    
    if not check_file_exists(checker, result, file_path):
        return
    
    # Test with valid scores
    code, stdout, stderr = checker.runner.run_file(
        checker.student_dir / file_path,
        args=["1500", "2300", "1800", "2100", "1950"],
    )
    
    expected_patterns = [
        r"Scores processed:\s*\[",
        r"Total players:\s*5",
        r"Total score:\s*9650",
        r"Average score:\s*1930\.0",
        r"High score:\s*2300",
        r"Low score:\s*1500",
        r"Score range:\s*800",
    ]
    
    for pattern in expected_patterns:
        if not re.search(pattern, stdout):
            result.passed = False
            result.errors.append(f"Missing output pattern: {pattern}")
    
    # Test with invalid args
    code, stdout, stderr = checker.runner.run_file(
        checker.student_dir / file_path,
        args=["ab", "ac"],
    )
    
    if not re.search(r"Invalid parameter:\s*'ab'", stdout):
        result.passed = False
        result.errors.append("Missing invalid parameter message for 'ab'")
    
    if not re.search(r"No scores provided\. Usage:", stdout):
        result.passed = False
        result.errors.append("Missing usage message when all params invalid")
    
    # Test mixed valid/invalid
    code, stdout, stderr = checker.runner.run_file(
        checker.student_dir / file_path,
        args=["1500", "ab", "2300"],
    )
    
    if not re.search(r"Invalid parameter:\s*'ab'", stdout):
        result.passed = False
        result.errors.append("Missing invalid parameter message in mixed case")
    
    if not re.search(r"Total players:\s*2", stdout):
        result.passed = False
        result.errors.append("Should process 2 valid scores when 1 invalid mixed in")


def check_ex2(checker: Checker, result: ExerciseResult):
    """Exercise 2: Position Tracker"""
    file_path = "ex2/ft_coordinate_system.py"
    
    check_function_exists(checker, result, file_path, "get_player_pos")
    
    if not result.passed:
        return
    
    # Verify function has correct return type annotation
    full_path = checker.student_dir / file_path
    try:
        content = full_path.read_text()
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "get_player_pos":
                if node.returns is None:
                    result.passed = False
                    result.errors.append("get_player_pos must have return type annotation")
                break
    except SyntaxError:
        pass
    
    # Test with valid coordinates
    stdin = "1.0,2.5,3.0\n4,5,6\n"
    code, stdout, stderr = checker.runner.run_file(
        checker.student_dir / file_path,
        stdin=stdin,
    )
    
    expected_patterns = [
        r"Got a first tuple:\s*\(1\.0,\s*2\.5,\s*3\.0\)",
        r"Distance to center:\s*4\.0311",
        r"Distance between the 2 sets of coordinates:\s*4\.9244",
    ]
    
    for pattern in expected_patterns:
        if not re.search(pattern, stdout):
            result.passed = False
            result.errors.append(f"Missing output pattern: {pattern}")


def check_ex3(checker: Checker, result: ExerciseResult):
    """Exercise 3: Achievement Hunter"""
    file_path = "ex3/ft_achievement_tracker.py"
    
    check_function_exists(checker, result, file_path, "gen_player_achievements")
    
    if not result.passed:
        return
    
    # Verify return type annotation is set[str]
    full_path = checker.student_dir / file_path
    try:
        content = full_path.read_text()
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "gen_player_achievements":
                if node.returns is None:
                    result.passed = False
                    result.errors.append("gen_player_achievements must have return type annotation")
                break
    except SyntaxError:
        pass
    
    code, stdout, stderr = run_and_validate(
        checker, result, file_path,
        expected_patterns=[
            r"Player\s+\w+:\s*\{",
            r"All distinct achievements:",
            r"Common achievements:",
            r"Only\s+\w+\s+has:",
            r"\w+\s+is missing:",
        ]
    )
    
    # Verify at least 4 players
    player_lines = [line for line in stdout.split('\n') if re.search(r'Player\s+\w+:', line)]
    if len(player_lines) < 4:
        result.passed = False
        result.errors.append(f"Expected at least 4 players, found {len(player_lines)}")


def check_ex4(checker: Checker, result: ExerciseResult):
    """Exercise 4: Inventory Master"""
    file_path = "ex4/ft_inventory_system.py"
    
    if not check_file_exists(checker, result, file_path):
        return
    
    code, stdout, stderr = checker.runner.run_file(
        checker.student_dir / file_path,
        args=["sword:1", "potion:5", "shield:2", "armor:3", "helmet:1", "sword:2", "hello", "key:value"],
    )
    
    expected_patterns = [
        r"Redundant item\s*'sword'\s*- discarding",
        r"Error - invalid parameter\s*'hello'",
        r"Quantity error for\s*'key'",
        r"Got inventory:\s*\{.*'sword':\s*1",
        r"Item list:\s*\[",
        r"Total quantity of the \d+ items:\s*\d+",
        r"Item most abundant:\s*\w+\s+with quantity\s*\d+",
        r"Item least abundant:\s*\w+\s+with quantity\s*\d+",
        r"Updated inventory:",
    ]
    
    for pattern in expected_patterns:
        if not re.search(pattern, stdout):
            result.passed = False
            result.errors.append(f"Missing output pattern: {pattern}")
    
    # Verify percentages are shown with 1 decimal place
    percent_lines = [line for line in stdout.split('\n') if 'represents' in line and '%' in line]
    if len(percent_lines) < 5:
        result.passed = False
        result.errors.append("Missing percentage output for inventory items")


def check_ex5(checker: Checker, result: ExerciseResult):
    """Exercise 5: Stream Wizard"""
    file_path = "ex5/ft_data_stream.py"
    
    check_function_exists(checker, result, file_path, "gen_event")
    check_function_exists(checker, result, file_path, "consume_event")
    
    if not result.passed:
        return
    
    # Verify gen_event is a generator (contains yield)
    full_path = checker.student_dir / file_path
    try:
        content = full_path.read_text()
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "gen_event":
                has_yield = any(isinstance(n, ast.Yield) for n in ast.walk(node))
                if not has_yield:
                    result.passed = False
                    result.errors.append("gen_event must be a generator (use yield)")
                break
    except SyntaxError:
        pass
    
    code, stdout, stderr = run_and_validate(
        checker, result, file_path,
        expected_patterns=[
            r"Event\s+\d+:",
            r"Built list of 10 events:",
            r"Got event from list:",
            r"Remains in list:\s*\[\]",
        ]
    )
    
    # Verify 1000 events are generated
    event_lines = [line for line in stdout.split('\n') if re.search(r'Event\s+\d+:', line)]
    if len(event_lines) < 1000:
        result.passed = False
        result.errors.append(f"Expected at least 1000 events, found {len(event_lines)}")
    
    # Verify list is fully consumed (empty at end)
    if "Remains in list: []" not in stdout:
        result.passed = False
        result.errors.append("List should be fully consumed (empty at end)")


def check_ex6(checker: Checker, result: ExerciseResult):
    """Exercise 6: Data Alchemist"""
    file_path = "ex6/ft_data_alchemist.py"
    
    if not check_file_exists(checker, result, file_path):
        return
    
    # Verify list comprehension and dict comprehension usage
    full_path = checker.student_dir / file_path
    try:
        content = full_path.read_text()
        tree = ast.parse(content)
        
        has_list_comp = any(isinstance(n, ast.ListComp) for n in ast.walk(tree))
        has_dict_comp = any(isinstance(n, ast.DictComp) for n in ast.walk(tree))
        
        if not has_list_comp:
            result.passed = False
            result.errors.append("Must use list comprehensions")
        if not has_dict_comp:
            result.passed = False
            result.errors.append("Must use dictionary comprehensions")
    except SyntaxError:
        pass
    
    code, stdout, stderr = run_and_validate(
        checker, result, file_path,
        expected_patterns=[
            r"Initial list of players:",
            r"New list with all names capitalized:",
            r"New list of capitalized names only:",
            r"Score dict:",
            r"Score average is\s+\d+\.\d+",
            r"High scores:",
        ]
    )
    
    # Verify high scores dictionary is present
    if "High scores:" not in stdout:
        result.passed = False
        result.errors.append("Missing high scores output")


EXERCISES = {
    0: {"name": "Command Quest", "check": check_ex0},
    1: {"name": "Score Cruncher", "check": check_ex1},
    2: {"name": "Position Tracker", "check": check_ex2},
    3: {"name": "Achievement Hunter", "check": check_ex3},
    4: {"name": "Inventory Master", "check": check_ex4},
    5: {"name": "Stream Wizard", "check": check_ex5},
    6: {"name": "Data Alchemist", "check": check_ex6},
}
