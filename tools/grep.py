"""Search tool for the chat program.

This module searches text files for lines matching a regular expression.
"""

import glob
import re


def grep(regex, filepath):
    """Search for lines matching a regex pattern in files matching a glob pattern.

    >>> grep('apple', 'test_files/grep_*.txt')
    'apple\\napple pie'

    >>> grep('orange', 'test_files/grep_*.txt')
    ''

    >>> grep('^a', 'test_files/grep_*.txt')
    'apple\\napple pie'

    >>> grep('apple', 'nonexistent_*.txt')
    ''

    >>> grep('apple', '/nonexistent/path/file.txt')
    ''
    """
    files = sorted(glob.glob(filepath))
    output = []

    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if re.search(regex, line):
                    output.append(line.rstrip('\n'))


    return '\n'.join(output)


grep_schema = {
    "type": "function",
    "function": {
        "name": "grep",
        "description": "Use this to search for patterns within files. Searches for lines matching a regex pattern in files matching a glob pattern.",
        "parameters": {
            "type": "object",
            "properties": {
                "regex": {
                    "type": "string",
                    "description": "The regex pattern to search for",
                },
                "filepath": {
                    "type": "string",
                    "description": "The file path or glob pattern to search in",
                },
            },
            "required": ["regex", "filepath"],
        },
    },
}