"""Module 3, Exercise 3: Achievement Hunter — structural output validation.

``check_ex3`` lives here instead of ``modules/module03.py`` so the parsing
logic stays in a focused module. The report is validated structurally rather
than by loose single-word regexes:

* ``Player <name>: <set>`` lines are matched by name (spaces and punctuation
  allowed; a name never crosses a colon or a newline) and parsed with
  ``ast.literal_eval``.
* ``All distinct achievements: <set>`` is parsed the same way and must equal
  the union of every parsed player set.
* Mismatches are appended as sorted, deterministic errors so the existing
  trace mechanism renders them identically on every run.
"""

import ast
import re
from pathlib import Path

from checker import Checker, ExerciseResult
from modules import check_function_exists

FILE_PATH = "ex3/ft_achievement_tracker.py"

_PLAYER_LINE = re.compile(
    r"^Player (?P<name>[^:\n]+):\s*(?P<body>[^\n]+)$", re.MULTILINE
)
_UNION_LINE = re.compile(
    r"^All distinct achievements:\s*(?P<body>[^\n]+)$", re.MULTILINE | re.IGNORECASE
)
_COMMON_LINE = re.compile(r"^Common achievements:", re.MULTILINE | re.IGNORECASE)
_ONLY_LINE = re.compile(r"^Only [^:\n]+ has:", re.MULTILINE | re.IGNORECASE)
_MISSING_LINE = re.compile(r"^[^:\n]+ is missing:", re.MULTILINE | re.IGNORECASE)


def check_ex3(checker: Checker, result: ExerciseResult) -> None:
    """Validate the Achievement Hunter report structurally."""
    check_function_exists(checker, result, FILE_PATH, "gen_player_achievements")
    if not result.passed:
        return

    full_path = checker.student_dir / FILE_PATH
    _check_return_annotation(full_path, result)

    code, stdout, stderr = checker.runner.run_file(full_path, cwd=checker.student_dir)
    result.exit_code = code
    result.stdout = stdout
    result.stderr = stderr

    if code != 0:
        result.passed = False
        result.errors.append(f"Expected exit code 0, got {code}")

    players = _parse_players(stdout, result)
    if len(players) < 4:
        result.passed = False
        result.errors.append(
            f"Expected at least 4 players with parseable achievement sets, "
            f"found {len(players)}"
        )

    _check_summary_labels(stdout, result)

    reported = _parse_union(stdout, result)
    if players and reported is not None:
        _check_union_matches_players(players, reported, result)


def _check_return_annotation(full_path: Path, result: ExerciseResult) -> None:
    """Require gen_player_achievements to carry a return type annotation."""
    try:
        content = full_path.read_text()
        tree = ast.parse(content)
    except SyntaxError:
        return
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "gen_player_achievements":
            if node.returns is None:
                result.passed = False
                result.errors.append(
                    "gen_player_achievements must have return type annotation"
                )
            break


def _parse_players(stdout: str, result: ExerciseResult) -> dict[str, set[str]]:
    """Return {name: achievements} for every Player line that parses to set[str]."""
    players: dict[str, set[str]] = {}
    for match in _PLAYER_LINE.finditer(stdout):
        name = match.group("name").strip()
        achievements = _parse_set(match.group("body"), f"Player {name}", result)
        if achievements is not None:
            players[name] = achievements
    return players


def _parse_union(stdout: str, result: ExerciseResult) -> set[str] | None:
    """Return the reported All-distinct-achievements set, or None if missing."""
    match = _UNION_LINE.search(stdout)
    if match is None:
        result.passed = False
        result.errors.append("Missing 'All distinct achievements' output")
        return None
    return _parse_set(match.group("body"), "All distinct achievements", result)


def _parse_set(
    body: str, owner: str, result: ExerciseResult
) -> set[str] | None:
    """Parse one collection literal and require it to be a set of strings."""
    try:
        value = ast.literal_eval(body)
    except (SyntaxError, ValueError) as exc:
        result.passed = False
        result.errors.append(f"{owner}: could not parse {body!r}: {exc}")
        return None
    if not isinstance(value, set):
        result.passed = False
        result.errors.append(
            f"{owner}: expected a set of string achievements, "
            f"got {type(value).__name__}"
        )
        return None
    if not all(isinstance(item, str) for item in value):
        result.passed = False
        result.errors.append(
            f"{owner}: achievements must be strings, got {body!r}"
        )
        return None
    return value


def _check_union_matches_players(
    players: dict[str, set[str]],
    reported: set[str],
    result: ExerciseResult,
) -> None:
    """Fail when the reported union differs from the parsed players' union."""
    earned = set().union(*players.values())
    if reported == earned:
        return
    result.passed = False
    unearned = sorted(reported - earned)
    omitted = sorted(earned - reported)
    if unearned:
        result.errors.append(
            "All distinct achievements lists achievements earned by no player: "
            f"{unearned}"
        )
    if omitted:
        result.errors.append(
            f"All distinct achievements omits earned achievements: {omitted}"
        )


def _check_summary_labels(stdout: str, result: ExerciseResult) -> None:
    """Keep the summary sections the exercise requires present."""
    if _COMMON_LINE.search(stdout) is None:
        result.passed = False
        result.errors.append("Missing 'Common achievements:' output")
    if _ONLY_LINE.search(stdout) is None:
        result.passed = False
        result.errors.append("Missing 'Only <player> has:' output")
    if _MISSING_LINE.search(stdout) is None:
        result.passed = False
        result.errors.append("Missing '<player> is missing:' output")
