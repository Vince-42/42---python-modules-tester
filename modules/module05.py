"""Module 5: Abstract classes and polymorphism"""

import ast
import re

from checker import Checker, ExerciseResult
from modules import (
    check_class_exists,
    check_class_method_exists,
    check_directory_exists,
    check_file_exists,
    check_inheritance,
    run_and_validate,
)

MODULE_NAME = "Module 5: Abstract Classes"


def check_ex0(checker: Checker, result: ExerciseResult):
    """Exercise 0: Data Processor"""
    file_path = "ex0/data_processor.py"
    
    check_class_exists(checker, result, file_path, "DataProcessor")
    check_class_exists(checker, result, file_path, "NumericProcessor")
    check_class_exists(checker, result, file_path, "TextProcessor")
    check_class_exists(checker, result, file_path, "LogProcessor")
    
    check_inheritance(checker, result, file_path, "NumericProcessor", "DataProcessor")
    check_inheritance(checker, result, file_path, "TextProcessor", "DataProcessor")
    check_inheritance(checker, result, file_path, "LogProcessor", "DataProcessor")
    
    check_class_method_exists(checker, result, file_path, "DataProcessor", "validate")
    check_class_method_exists(checker, result, file_path, "DataProcessor", "ingest")
    check_class_method_exists(checker, result, file_path, "DataProcessor", "output")
    
    if not result.passed:
        return
    
    # Verify DataProcessor is abstract (ABC)
    full_path = checker.student_dir / file_path
    try:
        content = full_path.read_text()
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "DataProcessor":
                # Check ABC inheritance
                has_abc = any(
                    (isinstance(base, ast.Name) and base.id == "ABC") or
                    (isinstance(base, ast.Attribute) and base.attr == "ABC")
                    for base in node.bases
                )
                if not has_abc:
                    result.passed = False
                    result.errors.append("DataProcessor must inherit from ABC")
                
                # Check abstract methods
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        has_abstract = any(
                            (isinstance(dec, ast.Name) and dec.id == "abstractmethod") or
                            (isinstance(dec, ast.Attribute) and dec.attr == "abstractmethod")
                            for dec in item.decorator_list
                        )
                        if item.name == "validate" and not has_abstract:
                            result.passed = False
                            result.errors.append("validate() must be abstract")
                        if item.name == "ingest" and not has_abstract:
                            result.passed = False
                            result.errors.append("ingest() must be abstract")
                        if item.name == "output" and has_abstract:
                            result.passed = False
                            result.errors.append("output() must be concrete (not abstract)")
                break
    except SyntaxError:
        pass
    
    code, stdout, stderr = run_and_validate(
        checker, result, file_path,
        expected_patterns=[
            r"Testing Numeric Processor",
            r"Trying to validate input",
            r"Extracting \d+ values",
            r"Numeric value \d+:",
            r"Testing Text Processor",
            r"Text value \d+:",
            r"Testing Log Processor",
            r"Log entry \d+:",
        ]
    )


def check_ex1(checker: Checker, result: ExerciseResult):
    """Exercise 1: Data Stream"""
    file_path = "ex1/data_stream.py"
    
    check_class_exists(checker, result, file_path, "DataStream")
    
    check_class_method_exists(checker, result, file_path, "DataStream", "register_processor")
    check_class_method_exists(checker, result, file_path, "DataStream", "process_stream")
    check_class_method_exists(checker, result, file_path, "DataStream", "print_processors_stats")
    
    if not result.passed:
        return
    
    code, stdout, stderr = run_and_validate(
        checker, result, file_path,
        expected_patterns=[
            r"== DataStream statistics ==",
            r"No processor found, no data",
            r"DataStream error - Can't process element in stream:",
            r"\w+ Processor: total \d+ items processed, remaining \d+ on processor",
        ]
    )
    
    # Verify exact stats format
    stats_lines = [line for line in stdout.split('\n') if re.search(r'\w+ Processor: total \d+ items processed, remaining \d+ on processor', line)]
    if not stats_lines:
        result.passed = False
        result.errors.append("Missing processor statistics in exact format")


def check_ex2(checker: Checker, result: ExerciseResult):
    """Exercise 2: Data Pipeline"""
    file_path = "ex2/data_pipeline.py"
    
    check_class_exists(checker, result, file_path, "ExportPlugin")
    check_class_exists(checker, result, file_path, "DataStream")
    
    if not result.passed:
        return
    
    # Verify ExportPlugin is a Protocol
    full_path = checker.student_dir / file_path
    try:
        content = full_path.read_text()
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "ExportPlugin":
                has_protocol = any(
                    (isinstance(base, ast.Name) and base.id == "Protocol") or
                    (isinstance(base, ast.Attribute) and base.attr == "Protocol")
                    for base in node.bases
                )
                if not has_protocol:
                    result.passed = False
                    result.errors.append("ExportPlugin must inherit from Protocol")
                
                # Verify process_output method exists
                has_process_output = any(
                    isinstance(item, ast.FunctionDef) and item.name == "process_output"
                    for item in node.body
                )
                if not has_process_output:
                    result.passed = False
                    result.errors.append("ExportPlugin must define process_output()")
                break
        
        # Check DataStream has output_pipeline method
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "DataStream":
                has_pipeline = any(
                    isinstance(item, ast.FunctionDef) and item.name == "output_pipeline"
                    for item in node.body
                )
                if not has_pipeline:
                    result.passed = False
                    result.errors.append("DataStream must have output_pipeline() method")
                break
        
        # Verify no import csv or import json
        if re.search(r'\bimport\s+csv\b', content) or re.search(r'\bfrom\s+csv\b', content):
            result.passed = False
            result.errors.append("Must not use import csv - format manually")
        if re.search(r'\bimport\s+json\b', content) or re.search(r'\bfrom\s+json\b', content):
            result.passed = False
            result.errors.append("Must not use import json - format manually")
    except SyntaxError:
        pass
    
    code, stdout, stderr = run_and_validate(
        checker, result, file_path,
        expected_patterns=[
            r"CSV Output:",
            r"JSON Output:",
            r"== DataStream statistics ==",
        ]
    )


EXERCISES = {
    0: {"name": "Data Processor", "check": check_ex0},
    1: {"name": "Data Stream", "check": check_ex1},
    2: {"name": "Data Pipeline", "check": check_ex2},
}
