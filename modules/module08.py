"""Module 8: Environment & dependencies"""

import ast
import re
import tempfile
from pathlib import Path

from checker import Checker, ExerciseResult
from modules import (
    check_file_exists,
    run_and_validate,
)

MODULE_NAME = "Module 8: Environment & Dependencies"


def check_ex0(checker: Checker, result: ExerciseResult):
    """Exercise 0: Entering the Matrix"""
    file_path = "ex0/construct.py"
    
    if not check_file_exists(checker, result, file_path):
        return
    
    code, stdout, stderr = run_and_validate(
        checker, result, file_path,
        expected_patterns=[
            r"MATRIX STATUS:",
            r"Current Python:",
            r"Virtual Environment:",
        ]
    )
    
    # Verify exact output strings based on environment
    if "VIRTUAL_ENV" in checker.runner.env:
        # Inside venv
        if "Welcome to the construct" not in stdout:
            result.passed = False
            result.errors.append("Inside venv: Missing 'Welcome to the construct'")
        if "SUCCESS: You're in an isolated environment!" not in stdout:
            result.passed = False
            result.errors.append("Inside venv: Missing success message")
    else:
        # Outside venv
        if "You're still plugged in" not in stdout:
            result.passed = False
            result.errors.append("Outside venv: Missing 'You're still plugged in'")
        if "None detected" not in stdout:
            result.passed = False
            result.errors.append("Outside venv: Missing 'None detected'")
        if "WARNING: You're in the global environment!" not in stdout:
            result.passed = False
            result.errors.append("Outside venv: Missing warning message")
        if "python -m venv matrix_env" not in stdout:
            result.passed = False
            result.errors.append("Outside venv: Missing venv creation instructions")
    
    # Verify venv detection logic in source
    full_path = checker.student_dir / file_path
    content = full_path.read_text()
    if "sys.prefix" not in content and "VIRTUAL_ENV" not in content:
        result.passed = False
        result.errors.append("Must detect virtual environment using sys.prefix or VIRTUAL_ENV")


def check_ex1(checker: Checker, result: ExerciseResult):
    """Exercise 1: Loading Programs"""
    file_path = "ex1/loading.py"
    req_file = "ex1/requirements.txt"
    pyproject_file = "ex1/pyproject.toml"
    
    if not check_file_exists(checker, result, file_path):
        return
    if not check_file_exists(checker, result, req_file):
        return
    if not check_file_exists(checker, result, pyproject_file):
        return
    
    req_path = checker.student_dir / req_file
    req_content = req_path.read_text()
    
    required_packages = ["pandas", "numpy", "matplotlib"]
    for pkg in required_packages:
        if pkg not in req_content.lower():
            result.passed = False
            result.errors.append(f"Missing package in requirements.txt: {pkg}")
    
    pyproject_path = checker.student_dir / pyproject_file
    pyproject_content = pyproject_path.read_text()
    
    if "[tool.poetry.dependencies]" not in pyproject_content and "dependencies" not in pyproject_content:
        result.passed = False
        result.errors.append("Missing dependencies section in pyproject.toml")
    
    for pkg in required_packages:
        if pkg not in pyproject_content.lower():
            result.passed = False
            result.errors.append(f"Missing package in pyproject.toml: {pkg}")
    
    # Verify loading.py imports required packages
    full_path = checker.student_dir / file_path
    content = full_path.read_text()
    
    for pkg in required_packages:
        if pkg not in content.lower():
            result.passed = False
            result.errors.append(f"loading.py must import {pkg}")
    
    # Check for numpy data generation (not hardcoded)
    if "np.random" not in content and "numpy.random" not in content and "random" not in content:
        result.warnings.append("Should use numpy.random for data generation")
    
    code, stdout, stderr = checker.runner.run_file(
        checker.student_dir / file_path,
    )
    
    # Verify expected output patterns
    expected_patterns = [
        r"LOADING STATUS:",
        r"Checking dependencies:",
        r"\[OK\] pandas",
        r"\[OK\] numpy",
        r"\[OK\] matplotlib",
        r"Analyzing Matrix data",
        r"Processing \d+ data points",
        r"Generating visualization",
        r"Analysis complete!",
        r"Results saved to:.*matrix_analysis\.png",
    ]
    
    for pattern in expected_patterns:
        if not re.search(pattern, stdout):
            result.passed = False
            result.errors.append(f"Missing output pattern: {pattern}")
    
    # Verify matrix_analysis.png was created
    png_path = checker.student_dir / "ex1/matrix_analysis.png"
    if not png_path.exists():
        result.passed = False
        result.errors.append("Must create matrix_analysis.png")
    elif png_path.stat().st_size == 0:
        result.passed = False
        result.errors.append("matrix_analysis.png is empty")


def check_ex2(checker: Checker, result: ExerciseResult):
    """Exercise 2: Accessing the Mainframe"""
    file_path = "ex2/oracle.py"
    req_file = "ex2/requirements.txt"
    env_example = "ex2/.env.example"
    gitignore = "ex2/.gitignore"
    
    if not check_file_exists(checker, result, file_path):
        return
    if not check_file_exists(checker, result, req_file):
        return
    if not check_file_exists(checker, result, env_example):
        return
    if not check_file_exists(checker, result, gitignore):
        return
    
    env_path = checker.student_dir / env_example
    env_content = env_path.read_text()
    
    required_vars = ["MATRIX_MODE", "DATABASE_URL", "API_KEY", "LOG_LEVEL", "ZION_ENDPOINT"]
    for var in required_vars:
        if var not in env_content:
            result.passed = False
            result.errors.append(f"Missing variable in .env.example: {var}")
    
    gitignore_path = checker.student_dir / gitignore
    gitignore_content = gitignore_path.read_text()
    
    # Verify .env is in .gitignore (as a separate line, not part of another word)
    gitignore_lines = gitignore_content.split('\n')
    has_env = any(line.strip() == '.env' or line.strip() == '*.env' for line in gitignore_lines)
    if not has_env:
        result.passed = False
        result.errors.append(".gitignore must contain '.env' as a separate entry")
    
    # Verify python-dotenv is in requirements.txt
    req_content = (checker.student_dir / req_file).read_text()
    if "python-dotenv" not in req_content and "dotenv" not in req_content:
        result.passed = False
        result.errors.append("requirements.txt must include python-dotenv")
    
    # Verify oracle.py uses load_dotenv
    full_path = checker.student_dir / file_path
    content = full_path.read_text()
    
    if "load_dotenv" not in content:
        result.passed = False
        result.errors.append("oracle.py must call load_dotenv()")
    
    # Test with a temporary .env file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write("MATRIX_MODE=development\n")
        f.write("DATABASE_URL=sqlite:///test.db\n")
        f.write("API_KEY=test-key-12345\n")
        f.write("LOG_LEVEL=DEBUG\n")
        f.write("ZION_ENDPOINT=https://zion.example.com\n")
        env_file = f.name
    
    try:
        # Copy .env to student's ex2 directory
        student_env = checker.student_dir / "ex2/.env"
        student_env.write_text(Path(env_file).read_text())
        
        code, stdout, stderr = checker.runner.run_file(
            checker.student_dir / file_path,
        )
        
        # Verify exact output strings
        expected_patterns = [
            r"ORACLE STATUS:",
            r"Configuration loaded:",
            r"Mode:\s*development",
            r"Database:",
            r"API Access:",
            r"Log Level:\s*DEBUG",
            r"Zion Network:",
            r"Environment security check:",
            r"\[OK\] No hardcoded secrets detected",
            r"\[OK\] \.env file properly configured",
            r"\[OK\] Production overrides available",
            r"The Oracle sees all configurations\.",
        ]
        
        for pattern in expected_patterns:
            if not re.search(pattern, stdout):
                result.passed = False
                result.errors.append(f"Missing output pattern: {pattern}")
    finally:
        Path(env_file).unlink(missing_ok=True)
        if student_env.exists():
            student_env.unlink()


EXERCISES = {
    0: {"name": "Entering the Matrix", "check": check_ex0},
    1: {"name": "Loading Programs", "check": check_ex1},
    2: {"name": "Accessing the Mainframe", "check": check_ex2},
}
