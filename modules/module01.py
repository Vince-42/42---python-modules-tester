"""Module 1: Code Cultivation - Object-Oriented Garden Systems"""

import ast
import re

from checker import Checker, ExerciseResult
from modules import (
    check_class_exists,
    check_class_method_exists,
    check_class_attribute,
    check_directory_exists,
    check_file_exists,
    check_function_exists,
    check_inheritance,
    check_try_except_block,
    run_and_validate,
)

MODULE_NAME = "Module 1: Code Cultivation - OOP"


def check_ex0(checker: Checker, result: ExerciseResult):
    """Exercise 0: Planting Your First Seed"""
    file_path = "ex0/ft_garden_intro.py"
    
    if not check_file_exists(checker, result, file_path):
        return
    
    # Verify if __name__ == "__main__" block exists
    full_path = checker.student_dir / file_path
    content = full_path.read_text()
    if 'if __name__ == "__main__":' not in content and "if __name__ == '__main__':" not in content:
        result.passed = False
        result.errors.append("Missing if __name__ == '__main__' block")
    
    # Verify variables name, height, age exist
    if not all(var in content for var in ['name', 'height', 'age']):
        result.passed = False
        result.errors.append("Missing required variables: name, height, age")
    
    code, stdout, stderr = run_and_validate(
        checker, result, file_path,
        expected_patterns=[
            r"Plant\s*:\s*\w+",
            r"Height\s*:\s*\d+",
            r"Age\s*:\s*\d+",
        ]
    )


def check_ex1(checker: Checker, result: ExerciseResult):
    """Exercise 1: Garden Data Organizer"""
    file_path = "ex1/ft_garden_data.py"
    
    check_class_exists(checker, result, file_path, "Plant")
    check_class_method_exists(checker, result, file_path, "Plant", "show")
    
    if not result.passed:
        return
    
    # Verify at least 3 Plant instances are created
    full_path = checker.student_dir / file_path
    content = full_path.read_text()
    plant_instances = len(re.findall(r'Plant\s*\(', content))
    if plant_instances < 3:
        result.passed = False
        result.errors.append(f"Expected at least 3 Plant instances, found {plant_instances}")
    
    code, stdout, stderr = run_and_validate(
        checker, result, file_path,
        expected_patterns=[
            r"\w+:\s*\d+cm",
        ]
    )
    
    plant_lines = [line for line in stdout.split('\n') if ':' in line and 'cm' in line]
    if len(plant_lines) < 3:
        result.passed = False
        result.errors.append(f"Expected at least 3 plants in output, found {len(plant_lines)}")


def check_ex2(checker: Checker, result: ExerciseResult):
    """Exercise 2: Plant Growth Simulator"""
    file_path = "ex2/ft_plant_growth.py"
    
    check_class_exists(checker, result, file_path, "Plant")
    check_class_method_exists(checker, result, file_path, "Plant", "show")
    check_class_method_exists(checker, result, file_path, "Plant", "grow")
    check_class_method_exists(checker, result, file_path, "Plant", "age")
    
    if not result.passed:
        return
    
    code, stdout, stderr = run_and_validate(
        checker, result, file_path,
        expected_patterns=[
            r"Day\s+\d+",
            r"Growth this week:\s*\d+\.?\d*cm",
        ]
    )
    
    # Verify at least 7 days are shown
    day_lines = [line for line in stdout.split('\n') if re.search(r'Day\s+\d+', line)]
    if len(day_lines) < 7:
        result.passed = False
        result.errors.append(f"Expected at least 7 day entries, found {len(day_lines)}")


def check_ex3(checker: Checker, result: ExerciseResult):
    """Exercise 3: Plant Factory"""
    file_path = "ex3/ft_plant_factory.py"
    
    check_class_exists(checker, result, file_path, "Plant")
    check_class_method_exists(checker, result, file_path, "Plant", "__init__")
    check_class_method_exists(checker, result, file_path, "Plant", "show")
    
    if not result.passed:
        return
    
    # Verify __init__ takes name, height, age parameters
    full_path = checker.student_dir / file_path
    try:
        content = full_path.read_text()
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "Plant":
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                        arg_names = [arg.arg for arg in item.args.args]
                        if len(arg_names) < 4:  # self + 3 params
                            result.passed = False
                            result.errors.append("Plant.__init__ must accept (self, name, height, age)")
                        break
    except SyntaxError:
        pass
    
    code, stdout, stderr = run_and_validate(
        checker, result, file_path,
        expected_patterns=[
            r"Created\s*:\s*\w+",
        ]
    )
    
    created_count = len([line for line in stdout.split('\n') if 'Created' in line and ':' in line])
    if created_count < 5:
        result.passed = False
        result.errors.append(f"Expected at least 5 plants, found {created_count}")


def check_ex4(checker: Checker, result: ExerciseResult):
    """Exercise 4: Garden Security System"""
    file_path = "ex4/ft_garden_security.py"
    
    check_class_exists(checker, result, file_path, "Plant")
    check_class_method_exists(checker, result, file_path, "Plant", "__init__")
    check_class_method_exists(checker, result, file_path, "Plant", "set_height")
    check_class_method_exists(checker, result, file_path, "Plant", "set_age")
    check_class_method_exists(checker, result, file_path, "Plant", "get_height")
    check_class_method_exists(checker, result, file_path, "Plant", "get_age")
    check_class_method_exists(checker, result, file_path, "Plant", "show")
    
    if not result.passed:
        return
    
    code, stdout, stderr = run_and_validate(
        checker, result, file_path,
        expected_patterns=[
            r"height.*negative|negative.*height",
            r"age.*negative|negative.*age",
        ]
    )
    
    # Verify encapsulation (protected attributes)
    full_path = checker.student_dir / file_path
    content = full_path.read_text()
    if "_height" not in content or "_age" not in content:
        result.passed = False
        result.errors.append("Missing protected attributes (_height, _age)")
    
    # Verify exact error messages from PDF
    if "Height update rejected" not in stdout:
        result.passed = False
        result.errors.append("Missing exact error message: 'Height update rejected'")
    if "Age update rejected" not in stdout:
        result.passed = False
        result.errors.append("Missing exact error message: 'Age update rejected'")


def check_ex5(checker: Checker, result: ExerciseResult):
    """Exercise 5: Specialized Plant Types"""
    file_path = "ex5/ft_plant_types.py"
    
    check_class_exists(checker, result, file_path, "Plant")
    check_class_exists(checker, result, file_path, "Flower")
    check_class_exists(checker, result, file_path, "Tree")
    check_class_exists(checker, result, file_path, "Vegetable")
    
    check_inheritance(checker, result, file_path, "Flower", "Plant")
    check_inheritance(checker, result, file_path, "Tree", "Plant")
    check_inheritance(checker, result, file_path, "Vegetable", "Plant")
    
    check_class_method_exists(checker, result, file_path, "Flower", "bloom")
    check_class_method_exists(checker, result, file_path, "Tree", "produce_shade")
    check_class_method_exists(checker, result, file_path, "Vegetable", "grow")
    check_class_method_exists(checker, result, file_path, "Vegetable", "age")
    
    if not result.passed:
        return
    
    # Verify super() is used somewhere in the file
    full_path = checker.student_dir / file_path
    content = full_path.read_text()
    if "super()" not in content:
        result.passed = False
        result.errors.append("Missing super() calls in specialized classes")
    
    # Verify Vegetable.grow and Vegetable.age actually increase nutritional_value
    # by checking the source contains nutritional_value increments
    if "nutritional_value" not in content and "_nut_value" not in content:
        result.passed = False
        result.errors.append("Vegetable must track nutritional_value")
    
    code, stdout, stderr = run_and_validate(
        checker, result, file_path,
        expected_patterns=[
            r"blooming|bloomed",
            r"shade",
            r"Nutritional\s*value\s*:\s*\d+",
        ]
    )
    
    # Check that nutritional value starts at 0 and increases
    nut_lines = [line for line in stdout.split('\n') if 'Nutritional' in line and ':' in line]
    if len(nut_lines) >= 2:
        first_val = re.search(r':\s*(\d+)', nut_lines[0])
        last_val = re.search(r':\s*(\d+)', nut_lines[-1])
        if first_val and last_val:
            if int(first_val.group(1)) != 0:
                result.passed = False
                result.errors.append("Nutritional value must start at 0")
            if int(last_val.group(1)) <= int(first_val.group(1)):
                result.passed = False
                result.errors.append("Nutritional value must increase after grow/age")


def _check_any_static_method(checker, result, file_path, class_name):
    """Check if a class has at least one static method."""
    if not check_file_exists(checker, result, file_path):
        return False
    full_path = checker.student_dir / file_path
    try:
        content = full_path.read_text()
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        for decorator in item.decorator_list:
                            if isinstance(decorator, ast.Name) and decorator.id == "staticmethod":
                                return True
        result.passed = False
        result.errors.append(f"Missing static method in {class_name}")
        return False
    except SyntaxError:
        return False


def _check_any_class_method(checker, result, file_path, class_name):
    """Check if a class has at least one class method."""
    if not check_file_exists(checker, result, file_path):
        return False
    full_path = checker.student_dir / file_path
    try:
        content = full_path.read_text()
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        for decorator in item.decorator_list:
                            if isinstance(decorator, ast.Name) and decorator.id == "classmethod":
                                return True
        result.passed = False
        result.errors.append(f"Missing class method in {class_name}")
        return False
    except SyntaxError:
        return False


def check_ex6(checker: Checker, result: ExerciseResult):
    """Exercise 6: Garden Analytics"""
    file_path = "ex6/ft_garden_analytics.py"
    
    check_class_exists(checker, result, file_path, "Plant")
    check_class_exists(checker, result, file_path, "Flower")
    check_class_exists(checker, result, file_path, "Tree")
    check_class_exists(checker, result, file_path, "Vegetable")
    check_class_exists(checker, result, file_path, "Seed")
    
    check_inheritance(checker, result, file_path, "Seed", "Flower")
    
    _check_any_static_method(checker, result, file_path, "Plant")
    _check_any_class_method(checker, result, file_path, "Plant")
    
    full_path = checker.student_dir / file_path
    if full_path.exists():
        content = full_path.read_text()
        if "class Statistique" not in content and "class Stats" not in content:
            result.passed = False
            result.errors.append("Missing nested statistics class in Plant")
        
        # Verify the static method checks age > 365
        if "365" not in content:
            result.passed = False
            result.errors.append("Static method must check age > 365 days")
        
        # Verify class method creates anonymous plant
        if "Unknown" not in content:
            result.passed = False
            result.errors.append("Class method must create anonymous plant named 'Unknown plant'")
    
    if not result.passed:
        return
    
    code, stdout, stderr = run_and_validate(
        checker, result, file_path,
        expected_patterns=[
            r"True|False",
            r"Stats:",
            r"grow",
            r"age",
            r"show",
        ]
    )
    
    # Verify stats output shows counters
    stats_lines = [line for line in stdout.split('\n') if 'Stats:' in line]
    if not stats_lines:
        result.passed = False
        result.errors.append("Missing statistics output")


EXERCISES = {
    0: {"name": "Planting Your First Seed", "check": check_ex0},
    1: {"name": "Garden Data Organizer", "check": check_ex1},
    2: {"name": "Plant Growth Simulator", "check": check_ex2},
    3: {"name": "Plant Factory", "check": check_ex3},
    4: {"name": "Garden Security System", "check": check_ex4},
    5: {"name": "Specialized Plant Types", "check": check_ex5},
    6: {"name": "Garden Analytics", "check": check_ex6},
}
