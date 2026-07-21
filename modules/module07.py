"""Module 7: Design patterns"""

import ast
import re
from pathlib import Path

from checker import Checker, ExerciseResult
from modules import (
    check_class_exists,
    check_class_method_exists,
    check_directory_exists,
    check_file_exists,
    check_inheritance,
    run_and_validate,
)

MODULE_NAME = "Module 7: Design Patterns"


def _check_abc_class(checker: Checker, result: ExerciseResult, file_path: str, class_name: str):
    """Verify class inherits from ABC."""
    full_path = checker.student_dir / file_path
    if not full_path.exists():
        return False
    try:
        content = full_path.read_text()
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                has_abc = any(
                    (isinstance(base, ast.Name) and base.id == "ABC") or
                    (isinstance(base, ast.Attribute) and base.attr == "ABC")
                    for base in node.bases
                )
                if not has_abc:
                    result.passed = False
                    result.errors.append(f"{class_name} must inherit from ABC")
                    return False
                return True
    except SyntaxError:
        pass
    return False


def _check_abstract_method(checker: Checker, result: ExerciseResult, file_path: str, class_name: str, method_name: str):
    """Verify method is decorated with @abstractmethod."""
    full_path = checker.student_dir / file_path
    if not full_path.exists():
        return False
    try:
        content = full_path.read_text()
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == method_name:
                        has_abstract = any(
                            (isinstance(dec, ast.Name) and dec.id == "abstractmethod") or
                            (isinstance(dec, ast.Attribute) and dec.attr == "abstractmethod")
                            for dec in item.decorator_list
                        )
                        if not has_abstract:
                            result.passed = False
                            result.errors.append(f"{class_name}.{method_name} must be abstract")
                            return False
                        return True
    except SyntaxError:
        pass
    return False


def check_ex0(checker: Checker, result: ExerciseResult):
    """Exercise 0: Creature Factory"""
    check_file_exists(checker, result, "ex0/__init__.py")
    check_file_exists(checker, result, "battle.py")
    
    check_class_exists(checker, result, "ex0/__init__.py", "Creature")
    check_class_exists(checker, result, "ex0/__init__.py", "CreatureFactory")
    check_class_exists(checker, result, "ex0/__init__.py", "FlameFactory")
    check_class_exists(checker, result, "ex0/__init__.py", "AquaFactory")
    
    check_class_method_exists(checker, result, "ex0/__init__.py", "Creature", "attack")
    check_class_method_exists(checker, result, "ex0/__init__.py", "CreatureFactory", "create_base")
    check_class_method_exists(checker, result, "ex0/__init__.py", "CreatureFactory", "create_evolved")
    
    if not result.passed:
        return
    
    # Verify ABC and abstract methods
    _check_abc_class(checker, result, "ex0/__init__.py", "Creature")
    _check_abstract_method(checker, result, "ex0/__init__.py", "Creature", "attack")
    _check_abc_class(checker, result, "ex0/__init__.py", "CreatureFactory")
    _check_abstract_method(checker, result, "ex0/__init__.py", "CreatureFactory", "create_base")
    _check_abstract_method(checker, result, "ex0/__init__.py", "CreatureFactory", "create_evolved")
    
    # Verify concrete creatures exist
    full_path = checker.student_dir / "ex0/__init__.py"
    try:
        content = full_path.read_text()
        tree = ast.parse(content)
        required_creatures = ["Flameling", "Pyrodon", "Aquabub", "Torragon"]
        found_classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        for creature in required_creatures:
            if creature not in found_classes:
                result.passed = False
                result.errors.append(f"Missing concrete creature: {creature}")
    except SyntaxError:
        pass
    
    code, stdout, stderr = checker.runner.run_file(
        checker.student_dir / "battle.py",
    )
    
    # Verify exact output patterns
    expected_patterns = [
        r"Flameling is a Fire type Creature",
        r"Flameling uses Ember!",
        r"Pyrodon is a Fire/Flying type Creature",
        r"Pyrodon uses Flamethrower!",
        r"Aquabub is a Water type Creature",
        r"Aquabub uses Water Gun!",
        r"Torragon is a Water type Creature",
        r"Torragon uses Hydro Pump!",
        r"vs\.",
        r"fight!",
    ]
    
    for pattern in expected_patterns:
        if not re.search(pattern, stdout):
            result.passed = False
            result.errors.append(f"Missing output pattern: {pattern}")


def check_ex1(checker: Checker, result: ExerciseResult):
    """Exercise 1: Capabilities"""
    check_file_exists(checker, result, "ex1/__init__.py")
    check_file_exists(checker, result, "capacitor.py")
    
    check_class_exists(checker, result, "ex1/__init__.py", "HealCapability")
    check_class_exists(checker, result, "ex1/__init__.py", "TransformCapability")
    check_class_exists(checker, result, "ex1/__init__.py", "HealingCreatureFactory")
    check_class_exists(checker, result, "ex1/__init__.py", "TransformCreatureFactory")
    
    check_class_method_exists(checker, result, "ex1/__init__.py", "HealCapability", "heal")
    check_class_method_exists(checker, result, "ex1/__init__.py", "TransformCapability", "transform")
    check_class_method_exists(checker, result, "ex1/__init__.py", "TransformCapability", "revert")
    
    if not result.passed:
        return
    
    # Verify capabilities are ABCs and don't inherit from Creature
    _check_abc_class(checker, result, "ex1/__init__.py", "HealCapability")
    _check_abc_class(checker, result, "ex1/__init__.py", "TransformCapability")
    
    # Verify concrete creatures exist
    full_path = checker.student_dir / "ex1/__init__.py"
    try:
        content = full_path.read_text()
        tree = ast.parse(content)
        required_creatures = ["Sproutling", "Bloomelle", "Shiftling", "Morphagon"]
        found_classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        for creature in required_creatures:
            if creature not in found_classes:
                result.passed = False
                result.errors.append(f"Missing concrete creature: {creature}")
    except SyntaxError:
        pass
    
    code, stdout, stderr = checker.runner.run_file(
        checker.student_dir / "capacitor.py",
    )
    
    # Verify exact output patterns
    expected_patterns = [
        r"Sproutling is a Grass type Creature",
        r"Sproutling uses Vine Whip!",
        r"Sproutling heals itself for a small amount",
        r"Bloomelle is a Grass/Fairy type Creature",
        r"Bloomelle uses Petal Dance!",
        r"Bloomelle heals itself and others for a large amount",
        r"Shiftling is a Normal type Creature",
        r"Shiftling attacks normally\.",
        r"Shiftling shifts into a sharper form!",
        r"Shiftling performs a boosted strike!",
        r"Shiftling returns to normal\.",
        r"Morphagon is a Normal/Dragon type Creature",
        r"Morphagon attacks normally\.",
        r"Morphagon morphs into a dragonic battle form!",
        r"Morphagon unleashes a devastating morph strike!",
        r"Morphagon stabilizes its form\.",
    ]
    
    for pattern in expected_patterns:
        if not re.search(pattern, stdout):
            result.passed = False
            result.errors.append(f"Missing output pattern: {pattern}")


def check_ex2(checker: Checker, result: ExerciseResult):
    """Exercise 2: Abstract Strategy"""
    check_file_exists(checker, result, "ex2/__init__.py")
    check_file_exists(checker, result, "tournament.py")
    
    check_class_exists(checker, result, "ex2/__init__.py", "BattleStrategy")
    check_class_exists(checker, result, "ex2/__init__.py", "NormalStrategy")
    check_class_exists(checker, result, "ex2/__init__.py", "AggressiveStrategy")
    check_class_exists(checker, result, "ex2/__init__.py", "DefensiveStrategy")
    
    check_class_method_exists(checker, result, "ex2/__init__.py", "BattleStrategy", "act")
    check_class_method_exists(checker, result, "ex2/__init__.py", "BattleStrategy", "is_valid")
    
    if not result.passed:
        return
    
    # Verify BattleStrategy is ABC
    _check_abc_class(checker, result, "ex2/__init__.py", "BattleStrategy")
    _check_abstract_method(checker, result, "ex2/__init__.py", "BattleStrategy", "act")
    _check_abstract_method(checker, result, "ex2/__init__.py", "BattleStrategy", "is_valid")
    
    code, stdout, stderr = checker.runner.run_file(
        checker.student_dir / "tournament.py",
    )
    
    # Verify exact tournament output
    expected_patterns = [
        r"Tournament 0 \(basic\)",
        r"Tournament 1 \(error\)",
        r"Tournament 2 \(multiple\)",
        r"\*\*\* Tournament \*\*\*",
        r"\d+ opponents involved",
        r"\* Battle \*",
        r"now fight!",
        r"Invalid Creature .* for this aggressive strategy",
    ]
    
    for pattern in expected_patterns:
        if not re.search(pattern, stdout):
            result.passed = False
            result.errors.append(f"Missing output pattern: {pattern}")


EXERCISES = {
    0: {"name": "Creature Factory", "check": check_ex0},
    1: {"name": "Capabilities", "check": check_ex1},
    2: {"name": "Abstract Strategy", "check": check_ex2},
}
