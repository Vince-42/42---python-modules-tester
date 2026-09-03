"""Focused regression tests for Module 3, Exercise 3 (Achievement Hunter).

These tests lock the validation contract of ``modules.module03.check_ex3``
using the repo's stdlib-unittest convention (``test_process_invocations.py``):

* Player names may contain spaces; a report whose *All distinct achievements*
  union is structurally equal to the union of the players' achievements must
  PASS.
* A reported union that is a *superset* of the players' achievements must FAIL
  with a mismatch error that names the achievements reported but earned by no
  player.

They guard against regressions to the loose single-word pattern matching
(``Player\\s+\\w+:`` / ``Only\\s+\\w+\\s+has:``) or to a union line that is
checked for existence only: multi-word names must still match, the reported
union must still be compared structurally against the players, and superset
reports must still fail with a detailed error.

Run:  python3 -m unittest test_module03_ex3_regressions -v
"""

import ast
import re
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

from checker import Checker, ExerciseResult  # noqa: E402


# A correct submission: four multi-word player names, and a reported union
# that is exactly the union of their achievements. The union line is printed in
# reverse-sorted order so that only a structural (set-content) comparison can
# accept it; an order-preserving textual comparison cannot.
MULTI_WORD_EQUAL_UNION = textwrap.dedent(
    """\
    PLAYERS: list[tuple[str, list[str]]] = [
        ("Michael De Santa", ["Bulletproof Vest", "Shark Card"]),
        ("Trevor Philips", ["Shark Card", "Gold Bars"]),
        ("Franklin Clinton", ["Gold Bars", "Bull Shark Testosterone"]),
        ("Lester Crest", ["Bull Shark Testosterone", "Bulletproof Vest"]),
    ]


    def gen_player_achievements(player: str) -> set[str]:
        for name, achievements in PLAYERS:
            if name == player:
                return set(achievements)
        return set()


    def main() -> None:
        sets = {name: set(achievements) for name, achievements in PLAYERS}
        for name, achievements in PLAYERS:
            print(f"Player {name}: {set(achievements)}")
        union = set().union(*sets.values())
        rendered = ", ".join(repr(a) for a in sorted(union, reverse=True))
        print(f"All distinct achievements: {{{rendered}}}")
        print(f"Common achievements: {set.intersection(*sets.values())}")
        for name, own in sets.items():
            others = set().union(*(s for n, s in sets.items() if n != name))
            print(f"Only {name} has: {own - others}")
            print(f"{name} is missing: {union - own}")


    if __name__ == "__main__":
        main()
    """
)


# A plausible but wrong submission: every player earns achievements from
# {Alpha, Beta, Gamma, Delta}, yet the program also reports "Phantom Trophy"
# under *All distinct achievements* although no player ever earned it.
REPORTED_UNION_SUPERSET = textwrap.dedent(
    """\
    PLAYERS: list[tuple[str, set[str]]] = [
        ("Alice", {"Alpha", "Beta"}),
        ("Bob", {"Beta", "Gamma"}),
        ("Charlie", {"Gamma", "Delta"}),
        ("Dylan", {"Delta", "Alpha"}),
    ]


    def gen_player_achievements(player: str) -> set[str]:
        for name, achievements in PLAYERS:
            if name == player:
                return achievements
        return set()


    def main() -> None:
        for name, achievements in PLAYERS:
            print(f"Player {name}: {achievements}")
        union = set().union(*(achievements for _, achievements in PLAYERS))
        reported = union | {"Phantom Trophy"}
        print(f"All distinct achievements: {reported}")
        print(f"Common achievements: {set.intersection(*(s for _, s in PLAYERS))}")
        for name, own in PLAYERS:
            others = set().union(*(s for n, s in PLAYERS if n != name))
            print(f"Only {name} has: {own - others}")
            print(f"{name} is missing: {reported - own}")


    if __name__ == "__main__":
        main()
    """
)


def parse_players(stdout: str) -> dict[str, frozenset[str]]:
    """Parse ``Player <name>: {..}`` lines into {name: achievements}."""
    players: dict[str, frozenset[str]] = {}
    for line in stdout.splitlines():
        match = re.match(r"^Player (.+): (.+)$", line)
        if match:
            players[match.group(1)] = frozenset(ast.literal_eval(match.group(2)))
    return players


def parse_reported_union(stdout: str) -> tuple[list[str], frozenset[str]]:
    """Return (printed element order, parsed set) of the reported union line."""
    for line in stdout.splitlines():
        if line.startswith("All distinct achievements: "):
            literal = line.split(": ", 1)[1]
            order = re.findall(r"'([^']*)'", literal)
            return order, frozenset(ast.literal_eval(literal))
    raise AssertionError("'All distinct achievements:' section missing from stdout")


class AchievementHunterValidationTests(unittest.TestCase):
    """Regression coverage for module 3 exercise 3 validation behaviour."""

    def _make_checker(self) -> tuple[Checker, Path]:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        student = Path(tmp.name) / "student"
        trace_dir = Path(tmp.name) / "traces"
        student.mkdir(parents=True, exist_ok=True)
        return Checker(student, trace_dir), student

    def _check(self, source: str) -> ExerciseResult:
        checker, student = self._make_checker()
        target = student / "ex3" / "ft_achievement_tracker.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source)
        self.assertTrue(checker.load_module(3))
        return checker.check_exercise(3, 3, checker.modules[3])

    def test_multiword_players_with_equal_union_are_accepted(self):
        """Given four multi-word player names whose reported union is
        structurally equal to the union of their achievements, when check_ex3
        runs, then the exercise passes."""
        result = self._check(MULTI_WORD_EQUAL_UNION)

        players = parse_players(result.stdout)
        self.assertEqual(
            set(players),
            {"Michael De Santa", "Trevor Philips", "Franklin Clinton", "Lester Crest"},
        )

        printed_order, reported = parse_reported_union(result.stdout)
        expected_union = frozenset().union(*players.values())
        self.assertEqual(reported, expected_union)
        # The fixture renders the union in reverse-sorted order; accepting this
        # correct report requires comparing sets structurally, not textually.
        self.assertNotEqual(printed_order, sorted(expected_union))

        self.assertTrue(result.passed, msg=result.errors)

    def test_union_superset_is_rejected_with_mismatch_error(self):
        """Given a report whose *All distinct achievements* line lists an
        achievement no player earned, when check_ex3 runs, then the exercise
        fails with a mismatch error naming the unearned achievement."""
        result = self._check(REPORTED_UNION_SUPERSET)

        players = parse_players(result.stdout)
        _printed_order, reported = parse_reported_union(result.stdout)
        actual_union = frozenset().union(*players.values())
        self.assertEqual(reported - actual_union, frozenset({"Phantom Trophy"}))

        self.assertFalse(result.passed)
        self.assertTrue(
            any("Phantom Trophy" in error for error in result.errors),
            msg=result.errors,
        )


if __name__ == "__main__":
    unittest.main()
