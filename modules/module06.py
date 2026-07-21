"""Module 6: Import systems"""

import ast
import re
from pathlib import Path

from checker import Checker, ExerciseResult
from modules import (
    check_directory_exists,
    check_file_exists,
    check_function_exists,
    run_and_validate,
)

MODULE_NAME = "Module 6: Import Systems"


def check_ex0_alembic(checker: Checker, result: ExerciseResult):
    """Part I: The Alembic (exercises 0-5)"""
    files_to_check = [
        "elements.py",
        "alchemy/__init__.py",
        "alchemy/elements.py",
        "ft_alembic_0.py",
        "ft_alembic_1.py",
        "ft_alembic_2.py",
        "ft_alembic_3.py",
        "ft_alembic_4.py",
        "ft_alembic_5.py",
    ]
    
    for f in files_to_check:
        check_file_exists(checker, result, f)
    
    if not result.passed:
        return
    
    check_function_exists(checker, result, "elements.py", "create_fire")
    check_function_exists(checker, result, "elements.py", "create_water")
    check_function_exists(checker, result, "alchemy/elements.py", "create_earth")
    check_function_exists(checker, result, "alchemy/elements.py", "create_air")
    
    # Verify exact function return strings by importing
    student_dir = str(checker.student_dir)
    for func_name, expected in [
        ("create_fire", "Fire element created"),
        ("create_water", "Water element created"),
    ]:
        wrapper = f"""
import sys
sys.path.insert(0, {repr(student_dir)})
from elements import {func_name}
result = {func_name}()
print(f"RESULT: {{result}}")
"""
        code, stdout, stderr = checker.runner.run_code(wrapper)
        if f"RESULT: {expected}" not in stdout:
            result.passed = False
            result.errors.append(f"{func_name}() must return exactly '{expected}'")
    
    # Verify alchemy/__init__.py exposes create_air but NOT create_earth
    init_path = checker.student_dir / "alchemy/__init__.py"
    if init_path.exists():
        init_content = init_path.read_text()
        # Check that create_air is exposed
        if "create_air" not in init_content:
            result.passed = False
            result.errors.append("alchemy/__init__.py must expose create_air")
    
    # Test import behavior
    for i in range(6):
        file_path = f"ft_alembic_{i}.py"
        if not (checker.student_dir / file_path).exists():
            result.passed = False
            result.errors.append(f"Missing {file_path}")
            continue
        
        code, stdout, stderr = checker.runner.run_file(
            checker.student_dir / file_path,
        )
        
        if i == 4:
            # Must fail with AttributeError for create_earth
            if "AttributeError" not in stderr and "AttributeError" not in stdout:
                result.passed = False
                result.errors.append("ft_alembic_4.py must raise AttributeError for create_earth")
            if "has no attribute 'create_earth'" not in stdout + stderr:
                result.passed = False
                result.errors.append("ft_alembic_4.py must show exact AttributeError message")
        elif code != 0:
            result.passed = False
            result.errors.append(f"ft_alembic_{i}.py failed with exit code {code}")
        else:
            # Verify exact output patterns
            expected_outputs = [
                ("0", "Fire element created"),
                ("1", "Water element created"),
                ("2", "Earth element created"),
                ("3", "Air element created"),
                ("5", "Air element created"),
            ]
            for idx, expected in expected_outputs:
                if i == int(idx) and expected not in stdout:
                    result.passed = False
                    result.errors.append(f"ft_alembic_{i}.py missing expected output: {expected}")


def check_ex1_distillation(checker: Checker, result: ExerciseResult):
    """Part II: Distillation (exercises 0-1)"""
    files_to_check = [
        "alchemy/potions.py",
        "ft_distillation_0.py",
        "ft_distillation_1.py",
    ]
    
    for f in files_to_check:
        check_file_exists(checker, result, f)
    
    if not result.passed:
        return
    
    check_function_exists(checker, result, "alchemy/potions.py", "healing_potion")
    check_function_exists(checker, result, "alchemy/potions.py", "strength_potion")
    
    # Verify exact return strings
    student_dir = str(checker.student_dir)
    for func_name, expected in [
        ("healing_potion", "Healing potion brewed with 'Earth element created' and 'Air element created'"),
        ("strength_potion", "Strength potion brewed with 'Fire element created' and 'Water element created'"),
    ]:
        wrapper = f"""
import sys
sys.path.insert(0, {repr(student_dir)})
from alchemy.potions import {func_name}
result = {func_name}()
print(f"RESULT: {{result}}")
"""
        code, stdout, stderr = checker.runner.run_code(wrapper)
        if f"RESULT: {expected}" not in stdout:
            result.passed = False
            result.errors.append(f"{func_name}() must return exactly '{expected}'")
    
    # Verify alchemy/__init__.py has heal alias
    init_path = checker.student_dir / "alchemy/__init__.py"
    if init_path.exists():
        init_content = init_path.read_text()
        if "heal" not in init_content:
            result.passed = False
            result.errors.append("alchemy/__init__.py must expose 'heal' alias for healing_potion")
    
    for i in range(2):
        file_path = f"ft_distillation_{i}.py"
        code, stdout, stderr = checker.runner.run_file(
            checker.student_dir / file_path,
        )
        
        if code != 0:
            result.passed = False
            result.errors.append(f"ft_distillation_{i}.py failed with exit code {code}")
        elif "potion" not in stdout.lower():
            result.passed = False
            result.errors.append(f"ft_distillation_{i}.py missing potion output")


def check_ex2_transmutation(checker: Checker, result: ExerciseResult):
    """Part III: Transmutation (exercises 0-2)"""
    files_to_check = [
        "alchemy/transmutation/recipes.py",
        "alchemy/transmutation/__init__.py",
        "ft_transmutation_0.py",
        "ft_transmutation_1.py",
        "ft_transmutation_2.py",
    ]
    
    for f in files_to_check:
        check_file_exists(checker, result, f)
    
    if not result.passed:
        return
    
    check_function_exists(checker, result, "alchemy/transmutation/recipes.py", "lead_to_gold")
    
    # Verify exact return string
    student_dir = str(checker.student_dir)
    expected = "Recipe transmuting Lead to Gold: brew 'Air element created' and 'Strength potion brewed with 'Fire element created' and 'Water element created'' mixed with 'Fire element created'"
    wrapper = f"""
import sys
sys.path.insert(0, {repr(student_dir)})
from alchemy.transmutation.recipes import lead_to_gold
result = lead_to_gold()
print(f"RESULT: {{result}}")
"""
    code, stdout, stderr = checker.runner.run_code(wrapper)
    if f"RESULT: {expected}" not in stdout:
        result.passed = False
        result.errors.append(f"lead_to_gold() must return exact expected string")
    
    # Verify imports are actual imports (not comments)
    recipes_path = checker.student_dir / "alchemy/transmutation/recipes.py"
    if recipes_path.exists():
        try:
            content = recipes_path.read_text()
            tree = ast.parse(content)
            
            has_relative = False
            has_absolute = False
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.level > 0:  # relative import
                        has_relative = True
                    elif node.module and node.module.startswith("alchemy"):
                        has_absolute = True
            
            if not has_relative:
                result.passed = False
                result.errors.append("recipes.py must use relative imports")
            if not has_absolute:
                result.passed = False
                result.errors.append("recipes.py must use absolute imports")
        except SyntaxError:
            pass
    
    for i in range(3):
        file_path = f"ft_transmutation_{i}.py"
        code, stdout, stderr = checker.runner.run_file(
            checker.student_dir / file_path,
        )
        
        if code != 0:
            result.passed = False
            result.errors.append(f"ft_transmutation_{i}.py failed with exit code {code}")
        elif not re.search(r"lead to gold|transmutation|recipe", stdout, re.IGNORECASE):
            result.passed = False
            result.errors.append(f"ft_transmutation_{i}.py missing expected output")


def check_ex3_kaboom(checker: Checker, result: ExerciseResult):
    """Part IV: Avoid the Explosion (exercises 0-1)"""
    files_to_check = [
        "alchemy/grimoire/__init__.py",
        "alchemy/grimoire/light_spellbook.py",
        "alchemy/grimoire/light_validator.py",
        "alchemy/grimoire/dark_spellbook.py",
        "alchemy/grimoire/dark_validator.py",
        "ft_kaboom_0.py",
        "ft_kaboom_1.py",
    ]
    
    for f in files_to_check:
        check_file_exists(checker, result, f)
    
    if not result.passed:
        return
    
    check_function_exists(checker, result, "alchemy/grimoire/light_spellbook.py", "light_spell_allowed_ingredients")
    check_function_exists(checker, result, "alchemy/grimoire/light_spellbook.py", "light_spell_record")
    check_function_exists(checker, result, "alchemy/grimoire/light_validator.py", "validate_ingredients")
    
    # Verify light_validator is case-insensitive
    student_dir = str(checker.student_dir)
    wrapper = f"""
import sys
sys.path.insert(0, {repr(student_dir)})
from alchemy.grimoire.light_validator import validate_ingredients
result = validate_ingredients("Earth, wind and fire")
print(f"RESULT: {{result}}")
"""
    code, stdout, stderr = checker.runner.run_code(wrapper)
    if "VALID" not in stdout:
        result.passed = False
        result.errors.append("validate_ingredients must be case-insensitive and return VALID for 'Earth, wind and fire'")
    
    # Test ft_kaboom_0.py
    code, stdout, stderr = checker.runner.run_file(
        checker.student_dir / "ft_kaboom_0.py",
    )
    
    if code != 0:
        result.passed = False
        result.errors.append("ft_kaboom_0.py should succeed")
    elif "Spell recorded:" not in stdout:
        result.passed = False
        result.errors.append("ft_kaboom_0.py missing spell record output")
    
    # Test ft_kaboom_1.py - must fail with circular import
    code, stdout, stderr = checker.runner.run_file(
        checker.student_dir / "ft_kaboom_1.py",
    )
    
    if code == 0:
        result.passed = False
        result.errors.append("ft_kaboom_1.py must fail with circular import error")
    elif "circular import" not in stderr.lower() and "cannot import name" not in stderr.lower():
        result.passed = False
        result.errors.append("ft_kaboom_1.py must fail with circular import ImportError")


EXERCISES = {
    "alembic": {"name": "Part I: The Alembic", "check": check_ex0_alembic},
    "distillation": {"name": "Part II: Distillation", "check": check_ex1_distillation},
    "transmutation": {"name": "Part III: Transmutation", "check": check_ex2_transmutation},
    "kaboom": {"name": "Part IV: Avoid the Explosion", "check": check_ex3_kaboom},
}
