#!/usr/bin/env bash
#
# check.sh - Friendly wrapper around checker.py
#
# Usage:
#   ./check.sh                     Interactive menu
#   ./check.sh all                 Check all modules
#   ./check.sh 3                   Check module 3
#   ./check.sh 3 2                 Check module 3, exercise 2
#
# Options:
#   -d, --dir PATH       Student directory (default: current directory)
#   -t, --trace-dir PATH Trace output directory (default: traces/)
#   -v, --verbose        Show warnings and detailed output
#   -h, --help           Show this help
#
# Run it from inside the student's submission folder, or point --dir at it.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECKER="$SCRIPT_DIR/checker.py"

MODULE_NAMES=(
    "Garden Foundations - Basic Python"
    "Code Cultivation - OOP"
    "Exception Handling"
    "Python Collections"
    "File I/O"
    "Abstract Classes"
    "Import Systems"
    "Design Patterns"
    "Environment & Dependencies"
)

# --- colors (only on a real terminal) ---
if [[ -t 1 ]]; then
    BOLD=$'\033[1m'; DIM=$'\033[2m'; RED=$'\033[31m'; GREEN=$'\033[32m'
    YELLOW=$'\033[33m'; CYAN=$'\033[36m'; RESET=$'\033[0m'
else
    BOLD=""; DIM=""; RED=""; GREEN=""; YELLOW=""; CYAN=""; RESET=""
fi

usage() {
    sed -n '2,17p' "$0" | sed 's/^# \{0,1\}//'
    exit "${1:-0}"
}

err() { printf '%serror:%s %s\n' "$RED" "$RESET" "$1" >&2; }

# --- preflight ---
if ! command -v python3 >/dev/null 2>&1; then
    err "python3 not found. Install Python 3.10 or later."
    exit 1
fi
if [[ ! -f "$CHECKER" ]]; then
    err "checker.py not found next to this script ($CHECKER)"
    exit 1
fi
for tool in flake8 mypy; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        printf '%snote:%s %s not found - style/type checks will be skipped (pip install %s)\n' \
            "$YELLOW" "$RESET" "$tool" "$tool" >&2
    fi
done

# --- argument parsing ---
STUDENT_DIR="$PWD"
TRACE_DIR=""
VERBOSE=""
MODULE=""
EX=""
EXTRA_ARGS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help) usage 0 ;;
        -v|--verbose) VERBOSE="--verbose"; shift ;;
        -d|--dir)
            [[ $# -lt 2 ]] && { err "--dir requires a path"; exit 1; }
            STUDENT_DIR="$2"; shift 2 ;;
        -t|--trace-dir)
            [[ $# -lt 2 ]] && { err "--trace-dir requires a path"; exit 1; }
            TRACE_DIR="$2"; shift 2 ;;
        all) MODULE="all"; shift ;;
        [0-8])
            if [[ -z "$MODULE" ]]; then MODULE="$1"
            elif [[ -z "$EX" ]]; then EX="$1"
            else err "unexpected argument: $1"; usage 1; fi
            shift ;;
        --) shift; EXTRA_ARGS+=("$@"); break ;;
        *) err "unknown argument: $1"; usage 1 ;;
    esac
done

if [[ ! -d "$STUDENT_DIR" ]]; then
    err "student directory '$STUDENT_DIR' does not exist"
    exit 1
fi

# --- interactive menu when no module was given ---
if [[ -z "$MODULE" ]]; then
    printf '%sPython Module Checker%s\n\n' "$BOLD" "$RESET"
    printf 'Checking submissions in: %s%s%s\n\n' "$CYAN" "$STUDENT_DIR" "$RESET"
    for i in "${!MODULE_NAMES[@]}"; do
        printf '  %s%d%s - %s\n' "$GREEN" "$i" "$RESET" "${MODULE_NAMES[$i]}"
    done
    printf '  %sa%s - all modules\n\n' "$GREEN" "$RESET"

    read -rp "Module to check [a]: " answer
    answer="${answer:-a}"
    case "$answer" in
        a|A|all) MODULE="all" ;;
        [0-8])   MODULE="$answer" ;;
        *) err "invalid module: $answer"; exit 1 ;;
    esac

    if [[ "$MODULE" != "all" ]]; then
        read -rp "Exercise (Enter for all): " ex_answer
        [[ -n "$ex_answer" ]] && EX="$ex_answer"
    fi
    echo
fi

# --- build the checker command ---
CMD=(python3 "$CHECKER" --student-dir "$STUDENT_DIR")
[[ -n "$TRACE_DIR" ]] && CMD+=(--trace-dir "$TRACE_DIR")
[[ -n "$VERBOSE" ]] && CMD+=("$VERBOSE")

if [[ "$MODULE" == "all" ]]; then
    CMD+=(--all)
else
    CMD+=(--module "$MODULE")
    [[ -n "$EX" ]] && CMD+=(--ex "$EX")
fi
# bash 3.2 (macOS default) errors on expanding an empty array under set -u
CMD+=(${EXTRA_ARGS[@]+"${EXTRA_ARGS[@]}"})

printf '%srunning:%s %s\n\n' "$DIM" "$RESET" "${CMD[*]}"
exec "${CMD[@]}"
