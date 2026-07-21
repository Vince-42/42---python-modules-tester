"""Module 4: File I/O exercises"""

import ast
import re
import tempfile
from pathlib import Path

from checker import Checker, ExerciseResult
from modules import (
    check_directory_exists,
    check_file_exists,
    check_function_exists,
    run_and_validate,
)

MODULE_NAME = "Module 4: File I/O"


def check_ex0(checker: Checker, result: ExerciseResult):
    """Exercise 0: Ancient Text Recovery"""
    file_path = "ex0/ft_ancient_text.py"
    
    if not check_file_exists(checker, result, file_path):
        return
    
    # Verify explicit .close() is called in source
    full_path = checker.student_dir / file_path
    content = full_path.read_text()
    if ".close()" not in content:
        result.passed = False
        result.errors.append("Must explicitly close the file with .close()")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("[FRAGMENT 001] Digital preservation protocols established 2087\n")
        f.write("[FRAGMENT 002] Knowledge must survive the entropy wars\n")
        test_file = f.name
    
    try:
        code, stdout, stderr = checker.runner.run_file(
            checker.student_dir / file_path,
            args=[test_file],
        )
        
        # Check exact output format
        if "=== Cyber Archives Recovery ===" not in stdout:
            result.passed = False
            result.errors.append("Missing header: '=== Cyber Archives Recovery ==='")
        
        if f"Accessing file '{test_file}'" not in stdout and f'Accessing file \'{test_file}\'' not in stdout:
            result.passed = False
            result.errors.append("Missing access message with filename")
        
        if "---" not in stdout:
            result.passed = False
            result.errors.append("Missing separator '---'")
        
        if "Digital preservation protocols" not in stdout:
            result.passed = False
            result.errors.append("Missing file content in output")
        
        if f"File '{test_file}' closed." not in stdout and f'File \'{test_file}\' closed.' not in stdout:
            result.passed = False
            result.errors.append("Missing close message: 'File <name> closed.'")
        
        # Test nonexistent file
        code, stdout, stderr = checker.runner.run_file(
            checker.student_dir / file_path,
            args=["nonexistent_file.txt"],
        )
        
        if "Error opening file 'nonexistent_file.txt'" not in stdout and 'Error opening file \'nonexistent_file.txt\'' not in stdout:
            result.passed = False
            result.errors.append("Missing error message for nonexistent file")
        
        if "[Errno 2] No such file or directory" not in stdout + stderr:
            result.passed = False
            result.errors.append("Missing FileNotFoundError details")
    finally:
        Path(test_file).unlink(missing_ok=True)


def check_ex1(checker: Checker, result: ExerciseResult):
    """Exercise 1: Archive Creation"""
    file_path = "ex1/ft_archive_creation.py"
    
    if not check_file_exists(checker, result, file_path):
        return
    
    # Verify input() is used
    full_path = checker.student_dir / file_path
    content = full_path.read_text()
    if "input(" not in content:
        result.passed = False
        result.errors.append("Must use input() to get save filename")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("[FRAGMENT 001] Digital preservation protocols established 2087\n")
        test_file = f.name
    
    try:
        # Test with empty filename (should not save)
        code, stdout, stderr = checker.runner.run_file(
            checker.student_dir / file_path,
            args=[test_file],
            stdin="\n",
        )
        
        if "Not saving data." not in stdout:
            result.passed = False
            result.errors.append("Empty filename should show 'Not saving data.'")
        
        # Test with valid filename (should save)
        output_file = tempfile.mktemp(suffix='.txt')
        code, stdout, stderr = checker.runner.run_file(
            checker.student_dir / file_path,
            args=[test_file],
            stdin=f"{output_file}\n",
        )
        
        if "Saving data to" not in stdout:
            result.passed = False
            result.errors.append("Missing 'Saving data to' message")
        
        if "Data saved in file" not in stdout:
            result.passed = False
            result.errors.append("Missing 'Data saved in file' confirmation")
        
        if Path(output_file).exists():
            saved_content = Path(output_file).read_text()
            if "#" not in saved_content:
                result.passed = False
                result.errors.append("Saved file missing archive character (#)")
            # Verify each line ends with #
            lines = saved_content.strip().split('\n')
            for line in lines:
                if line and not line.endswith('#'):
                    result.passed = False
                    result.errors.append(f"Line does not end with #: {line[:50]}")
                    break
            Path(output_file).unlink(missing_ok=True)
        else:
            result.passed = False
            result.errors.append("Output file was not created")
    finally:
        Path(test_file).unlink(missing_ok=True)


def check_ex2(checker: Checker, result: ExerciseResult):
    """Exercise 2: Stream Management"""
    file_path = "ex2/ft_stream_management.py"
    
    if not check_file_exists(checker, result, file_path):
        return
    
    # Verify input() is NOT used - must use sys.stdin.readline()
    full_path = checker.student_dir / file_path
    content = full_path.read_text()
    if "input(" in content:
        result.passed = False
        result.errors.append("Must NOT use input() - use sys.stdin.readline() instead")
    
    if "sys.stdin" not in content and "stdin" not in content:
        result.passed = False
        result.errors.append("Must use sys.stdin.readline() for input")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("[FRAGMENT 001] Digital preservation protocols established 2087\n")
        test_file = f.name
    
    try:
        # Test nonexistent file - errors must go to stderr with [STDERR] prefix
        code, stdout, stderr = checker.runner.run_file(
            checker.student_dir / file_path,
            args=["nonexistent"],
        )
        
        if "[STDERR]" not in stderr:
            result.passed = False
            result.errors.append("Error messages must have [STDERR] prefix")
        
        if re.search(r"error|exception|failed", stdout, re.IGNORECASE):
            result.passed = False
            result.errors.append("Errors must be printed to stderr, not stdout")
        
        # Test valid file with save to invalid path
        output_file = "/etc/passwd"  # Should fail with permission denied
        code, stdout, stderr = checker.runner.run_file(
            checker.student_dir / file_path,
            args=[test_file],
            stdin=f"{output_file}\n",
        )
        
        if "[STDERR]" not in stderr and code != 0:
            result.passed = False
            result.errors.append("Save errors must have [STDERR] prefix")
        
        if "Data not saved." not in stdout:
            result.passed = False
            result.errors.append("Missing 'Data not saved.' message when save fails")
    finally:
        Path(test_file).unlink(missing_ok=True)


def check_ex3(checker: Checker, result: ExerciseResult):
    """Exercise 3: Vault Security"""
    file_path = "ex3/ft_vault_security.py"
    
    check_function_exists(checker, result, file_path, "secure_archive")
    
    if not result.passed:
        return
    
    # Verify function signature and return type
    full_path = checker.student_dir / file_path
    try:
        content = full_path.read_text()
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "secure_archive":
                # Check parameters
                arg_names = [arg.arg for arg in node.args.args]
                if len(arg_names) < 3:  # self + filename + action
                    result.passed = False
                    result.errors.append("secure_archive must accept at least (filename, action)")
                
                # Check return annotation
                if node.returns is None:
                    result.passed = False
                    result.errors.append("secure_archive must have return type annotation")
                elif "tuple" not in ast.unparse(node.returns).lower():
                    result.passed = False
                    result.errors.append("secure_archive must return tuple[bool, str]")
                
                # Check for with statement
                has_with = any(isinstance(n, ast.With) for n in ast.walk(node))
                if not has_with:
                    result.passed = False
                    result.errors.append("secure_archive must use with statement")
                break
    except SyntaxError:
        pass
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("[FRAGMENT 001] Digital preservation protocols established 2087\n")
        f.write("[FRAGMENT 002] Knowledge must survive the entropy wars\n")
        test_file = f.name
    
    try:
        # Test by importing and calling the function
        student_dir = str(full_path.parent)
        wrapper = f"""
import sys
sys.path.insert(0, {repr(student_dir)})
from ft_vault_security import secure_archive

# Test read success
result = secure_archive({repr(test_file)}, 'read')
print(f"READ_RESULT: {{result}}")

# Test read nonexistent
result = secure_archive('/not/existing/file', 'read')
print(f"READ_FAIL: {{result}}")

# Test write
result = secure_archive('/tmp/test_vault_write.txt', 'write', 'test content')
print(f"WRITE_RESULT: {{result}}")
"""
        code, stdout, stderr = checker.runner.run_code(wrapper)
        
        # Verify results
        read_success = re.search(r"READ_RESULT:\s*\((True|False),\s*(.+?)\)", stdout)
        read_fail = re.search(r"READ_FAIL:\s*\((True|False),\s*(.+?)\)", stdout)
        write_result = re.search(r"WRITE_RESULT:\s*\((True|False),\s*(.+?)\)", stdout)
        
        if not read_success or read_success.group(1) != "True":
            result.passed = False
            result.errors.append("secure_archive should return (True, content) for successful read")
        
        if not read_fail or read_fail.group(1) != "False":
            result.passed = False
            result.errors.append("secure_archive should return (False, error) for failed read")
        
        if not write_result:
            result.passed = False
            result.errors.append("secure_archive should return tuple for write operations")
    finally:
        Path(test_file).unlink(missing_ok=True)


EXERCISES = {
    0: {"name": "Ancient Text Recovery", "check": check_ex0},
    1: {"name": "Archive Creation", "check": check_ex1},
    2: {"name": "Stream Management", "check": check_ex2},
    3: {"name": "Vault Security", "check": check_ex3},
}
