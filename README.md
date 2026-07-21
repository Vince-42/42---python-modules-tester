_This project was made by vleroy to help test python module project for the 42 core curriculum._

# Python Module Checker

A command-line tool for validating student Python exercises across 9 modules covering basic Python, object-oriented programming, exception handling, collections, file I/O, abstract classes, import systems, design patterns, and environment management.

## Overview

The checker validates exercises by:
- Verifying required files and directory structures
- Checking class/function/method existence via AST parsing
- Running code in isolated subprocesses with controlled inputs
- Validating output against expected patterns
- Running `flake8` and `mypy` static analysis
- Generating per-exercise trace files for debugging

## Installation

### Prerequisites

- Python 3.10 or later
- `flake8` (optional, for style checking)
- `mypy` (optional, for type checking)

### Install Dependencies

```bash
# Install flake8 and mypy (recommended)
pip install flake8 mypy

# Or with Poetry
poetry add --dev flake8 mypy
```

### Setup

1. Clone or download the checker repository
2. Ensure the `checker.py` file and `modules/` directory are in the same folder
3. The checker is ready to use — no additional installation required

## Directory Structure

The checker expects student submissions to follow the structure defined in the subject PDFs:

```
student_directory/
├── ex0/
│   └── ft_garden_intro.py          # Module 1, Exercise 0
├── ex1/
│   └── ft_garden_data.py           # Module 1, Exercise 1
├── ex2/
│   └── ft_plant_growth.py          # Module 1, Exercise 2
...
```

For multi-file exercises (Modules 6, 7, 8), the structure follows the subject requirements:
- **Module 6**: `elements.py`, `alchemy/` package, `ft_alembic_*.py`, etc.
- **Module 7**: `ex0/`, `ex1/`, `ex2/` packages with `__init__.py`, plus `battle.py`, `capacitor.py`, `tournament.py`
- **Module 8**: `ex0/construct.py`, `ex1/loading.py` with `requirements.txt` and `pyproject.toml`, `ex2/oracle.py` with `.env.example` and `.gitignore`

## Usage

### Check a Single Module

```bash
python3 checker.py --module 1
```

### Check All Modules

```bash
python3 checker.py --all
```

### Check a Specific Exercise

```bash
python3 checker.py --module 3 --ex 2
```

### Specify Student Directory

```bash
python3 checker.py --module 1 --student-dir /path/to/student/work
```

### Enable Verbose Output

```bash
python3 checker.py --all --verbose
```

### Custom Trace Directory

```bash
python3 checker.py --all --trace-dir /path/to/traces
```

## Command-Line Options

| Option | Description |
|--------|-------------|
| `--module MODULE` | Check specific module only (0-8) |
| `--ex EX` | Check specific exercise only (requires `--module`) |
| `--all` | Check all modules |
| `--student-dir PATH` | Directory containing student submissions (default: current directory) |
| `--trace-dir PATH` | Directory for trace files (default: `traces/`) |
| `--verbose` | Show detailed output including warnings |
| `-h`, `--help` | Show help message |

## Understanding Results

### Console Output

```
📚 Module 1: Code Cultivation - OOP
--------------------------------------------------
  ✅ PASS | Ex 0: Planting Your First Seed
  ✅ PASS | Ex 1: Garden Data Organizer
  ❌ FAIL | Ex 2: Plant Growth Simulator
       → Expected exit code 0, got 1
       → Missing pattern in output: Growth this week:\s*\d+\.?\d*cm
       📄 Trace: traces/module01_ex2_Plant_Growth_Simulator.trace.txt
```

- **✅ PASS**: Exercise meets all requirements
- **❌ FAIL**: Exercise has errors (check the trace file for details)
- **⚠**: Warnings (e.g., flake8/mypy issues) shown in verbose mode

### Trace Files

For each exercise, a trace file is generated in `traces/` containing:
- Full stdout and stderr from execution
- flake8 and mypy errors
- Validation errors with context
- List of files checked

## Module Coverage

| Module | Topic | Exercises | Notes |
|--------|-------|-----------|-------|
| 0 | Basic Python | 8 | Functions, input, conditionals, loops, type annotations |
| 1 | OOP Basics | 7 | Classes, inheritance, encapsulation |
| 2 | Exception Handling | 5 | try/except, custom exceptions, finally |
| 3 | Collections | 7 | Lists, tuples, sets, dicts, generators |
| 4 | File I/O | 4 | Reading, writing, streams, context managers |
| 5 | Abstract Classes | 3 | ABC, polymorphism, data pipelines |
| 6 | Import Systems | 4 parts | Packages, absolute/relative imports |
| 7 | Design Patterns | 3 | Abstract factory, capabilities, strategy |
| 8 | Environment & Dependencies | 3 | venv, requirements, dotenv |

## How Validation Works

### File Structure Validation
The checker verifies that required files and directories exist according to each subject's specifications.

### Static Analysis (AST Parsing)
The checker parses Python files to verify:
- Class definitions exist
- Methods are implemented
- Inheritance relationships are correct
- Functions have required signatures

### Runtime Validation
The checker runs student code via subprocess to verify:
- Program executes without crashing
- Output matches expected patterns
- Input handling works correctly
- Error handling behaves as expected

### Static Analysis Tools
When available, `flake8` and `mypy` are run on every Python file:
- **flake8**: Style and syntax issues
- **mypy**: Type annotation errors

These are reported as warnings and do not automatically fail exercises unless explicitly configured.

## Trace File Format

```
=== Module 1, Exercise 2: Plant Growth Simulator ===
Status: FAILED

Exit code: 1
Files checked: ex2/ft_plant_growth.py

--- STDOUT ---
=== Garden Plant Growth ===
Rose: 25.0cm, 30 days old

--- STDERR ---
Traceback (most recent call last):
  File "ft_plant_growth.py", line 14, in <module>
    plant.age()
TypeError: 'int' object is not callable

--- FLAKE8 ERRORS ---
...

--- MYPY ERRORS ---
...

--- VALIDATION ERRORS ---
Expected exit code 0, got 1
Missing pattern in output: Growth this week:\s*\d+\.?\d*cm
```

## Limitations

1. **Random Output**: Exercises using `random` (Module 3 Achievement Hunter, Stream Wizard) are validated by output structure rather than exact values
2. **Virtual Environments**: Module 8 exercises are validated statically (file contents, code inspection) without creating actual virtual environments
3. **Network Access**: Exercises requiring API calls are validated for structure but may not fully test network behavior
4. **Input Timing**: The checker provides all stdin input at once; interactive programs with complex input timing may need adjustment

## Troubleshooting

### "Module X test definitions not found"
Ensure the `modules/` directory is present alongside `checker.py` and contains `moduleXX.py` files.

### "flake8/mypy not found"
Install the optional dependencies: `pip install flake8 mypy`. The checker will still work without them but won't report style/type issues.

### Exercise fails but code looks correct
Check the trace file for the exact error. Common issues:
- Output formatting doesn't match expected patterns
- Missing required methods or classes
- File naming or directory structure doesn't match subject requirements

## Contributing

The checker is designed to be extensible. To add or modify exercise validations:

1. Edit the corresponding `modules/moduleXX.py` file
2. Each exercise has a check function that receives `checker` and `result` objects
3. Use helper functions from `modules/__init__.py` for common validations
4. Run the checker against sample solutions to verify your changes

## Requirements

- Python 3.10+
- flake8 (optional)
- mypy (optional)

## License

MIT - Vincent Leroy
