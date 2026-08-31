"""Subprocess invocation records and their trace rendering."""

import shlex
from dataclasses import dataclass
from typing import List


@dataclass
class ProcessInvocation:
    """One subprocess invocation recorded during an exercise check."""

    command: List[str]
    cwd: str
    exit_code: int
    stdout: str
    stderr: str


def format_invocations(invocations: List[ProcessInvocation]) -> List[str]:
    """Render recorded invocations as ordered, labelled trace lines.

    Returns an empty list when nothing was recorded, so callers can extend a
    trace line list unconditionally.
    """
    if not invocations:
        return []

    lines = ["--- INVOCATIONS ---"]
    for index, invocation in enumerate(invocations, start=1):
        lines.extend(
            [
                "",
                f"--- RUN {index} ---",
                f"Command: {shlex.join(invocation.command)}",
                f"Cwd: {invocation.cwd}",
                f"Exit code: {invocation.exit_code}",
                "--- STDOUT ---",
                invocation.stdout if invocation.stdout else "(empty)",
                "--- STDERR ---",
                invocation.stderr if invocation.stderr else "(empty)",
            ]
        )
    lines.append("")
    return lines
