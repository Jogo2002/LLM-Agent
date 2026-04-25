"""Doctest tool for the chat program.

This module runs doctests on a Python file and returns the output.
"""

import subprocess
import sys
from pathlib import PurePath


def doctests(path):
    """Run doctests on a Python file with verbose output and return the result.

    >>> result = doctests('test_files/sample_add.py')
    >>> 'ok' in result or 'passed' in result
    True
    >>> doctests('/etc/passwd')
    'Error: Absolute paths and directory traversal are not allowed.'
    >>> doctests('../chat.py')
    'Error: Absolute paths and directory traversal are not allowed.'
    """
    if PurePath(path).is_absolute() or any(part == ".." for part in PurePath(path).parts):
        return "Error: Absolute paths and directory traversal are not allowed."

    result = subprocess.run(
        [sys.executable, "-m", "doctest", path, "-v"],
        capture_output=True,
        text=True,
    )
    return result.stdout + result.stderr


doctests_schema = {
    "type": "function",
    "function": {
        "name": "doctests",
        "description": "Use this to run doctests on a Python file. Returns verbose doctest output showing which tests passed or failed.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The relative path to the Python file to test",
                }
            },
            "required": ["path"],
        },
    },
}
