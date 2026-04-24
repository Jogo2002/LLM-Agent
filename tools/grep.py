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
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if re.search(regex, line):
                        output.append(line.rstrip('\n'))
        except (FileNotFoundError, UnicodeDecodeError, OSError):
            continue

    return '\n'.join(output)