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
#   -d, --dir PATH       Student directory (default: asked, Enter = current directory)
#                        With 'all': point at the folder containing the moduleXX dirs
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
DIR_GIVEN=""
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
            STUDENT_DIR="$2"; DIR_GIVEN=1; shift 2 ;;
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

# --- ask for the submission directory unless --dir was given ---
if [[ -z "$DIR_GIVEN" && -n "$MODULE" && "$MODULE" != "all" ]]; then
    read -rp "Directory containing module $MODULE to check [$STUDENT_DIR]: " dir_answer
    if [[ -n "$dir_answer" ]]; then
        STUDENT_DIR="${dir_answer/#\~/$HOME}"
    fi
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

    if [[ "$MODULE" == "all" ]]; then
        if [[ -z "$DIR_GIVEN" ]]; then
            read -rp "Directory containing the moduleXX folders [$STUDENT_DIR]: " dir_answer
            if [[ -n "$dir_answer" ]]; then
                STUDENT_DIR="${dir_answer/#\~/$HOME}"
            fi
        fi
    else
        if [[ -z "$DIR_GIVEN" ]]; then
            read -rp "Directory containing module $MODULE to check [$STUDENT_DIR]: " dir_answer
            if [[ -n "$dir_answer" ]]; then
                STUDENT_DIR="${dir_answer/#\~/$HOME}"
            fi
        fi
        read -rp "Exercise (Enter for all): " ex_answer
        [[ -n "$ex_answer" ]] && EX="$ex_answer"
    fi
    echo
fi

if [[ ! -d "$STUDENT_DIR" ]]; then
    err "student directory '$STUDENT_DIR' does not exist"
    exit 1
fi

# --- all modules: run each moduleXX directory found ---
if [[ "$MODULE" == "all" ]]; then
    shopt -s nullglob
    MODULE_DIRS=("$STUDENT_DIR"/module[0-9] "$STUDENT_DIR"/module[0-9][0-9])
    shopt -u nullglob

    if [[ ${#MODULE_DIRS[@]} -eq 0 ]]; then
        err "no moduleXX directories found in '$STUDENT_DIR'"
        err "checking all modules expects folders like module00/, module01/, ... (run a single module to use a flat exXX/ layout)"
        exit 1
    fi

    OVERALL_STATUS=0
    GRAND_PASSED=0
    GRAND_TOTAL=0
    OUT_FILE="$(mktemp "${TMPDIR:-/tmp}/module-check.XXXXXX")"
    trap 'rm -f "$OUT_FILE"' EXIT
    summary_re='OVERALL: ([0-9]+)/([0-9]+)'
    for dir in "${MODULE_DIRS[@]}"; do
        base="$(basename "$dir")"
        num="${base#module}"
        num=$((10#$num))
        CMD=(python3 "$CHECKER" --student-dir "$dir" --module "$num")
        [[ -n "$TRACE_DIR" ]] && CMD+=(--trace-dir "$TRACE_DIR")
        [[ -n "$VERBOSE" ]] && CMD+=("$VERBOSE")
        CMD+=(${EXTRA_ARGS[@]+"${EXTRA_ARGS[@]}"})

        printf '%srunning:%s %s\n\n' "$DIM" "$RESET" "${CMD[*]}"
        "${CMD[@]}" | tee "$OUT_FILE" || OVERALL_STATUS=$?
        if [[ "$(cat "$OUT_FILE")" =~ $summary_re ]]; then
            GRAND_PASSED=$((GRAND_PASSED + BASH_REMATCH[1]))
            GRAND_TOTAL=$((GRAND_TOTAL + BASH_REMATCH[2]))
        fi
    done
    printf '\n%sGrand total:%s %d/%d exercises passed across %d module(s)\n' \
        "$BOLD" "$RESET" "$GRAND_PASSED" "$GRAND_TOTAL" "${#MODULE_DIRS[@]}"
    exit "$OVERALL_STATUS"
fi

# --- single module: flat exXX/ layout inside STUDENT_DIR ---
CMD=(python3 "$CHECKER" --student-dir "$STUDENT_DIR")
[[ -n "$TRACE_DIR" ]] && CMD+=(--trace-dir "$TRACE_DIR")
[[ -n "$VERBOSE" ]] && CMD+=("$VERBOSE")
CMD+=(--module "$MODULE")
[[ -n "$EX" ]] && CMD+=(--ex "$EX")
CMD+=(${EXTRA_ARGS[@]+"${EXTRA_ARGS[@]}"})

printf '%srunning:%s %s\n\n' "$DIM" "$RESET" "${CMD[*]}"
exec "${CMD[@]}"
