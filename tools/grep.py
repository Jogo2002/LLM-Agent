"""Search tool for the chat program.

This module searches text files for lines matching a regular expression.
"""

import glob
import re


def grep(regex, filepath):
    """Search for lines matching a regex pattern in files matching a glob pattern.

    >>> import os

    >>> _ = open('tools_grep_1.txt', 'w', encoding='utf-8').write('apple\\nbanana\\nAPPLE\\n')
    >>> _ = open('tools_grep_2.txt', 'w', encoding='utf-8').write('cherry\\napple pie\\n')

    >>> grep('apple', 'tools_grep_*.txt')
    'apple\\napple pie'

    >>> grep('orange', 'tools_grep_*.txt')
    ''

    >>> grep('^a', 'tools_grep_*.txt')
    'apple\\napple pie'

    >>> grep('apple', 'nonexistent_*.txt')
    ''

    >>> _ = open('binary_file.txt', 'wb').write(bytes([0xff, 0xfe, 0xfd]))
    >>> grep('apple', 'binary_file.txt')
    ''

    >>> grep('apple', '/nonexistent/path/file.txt')
    ''

    >>> os.remove('tools_grep_1.txt')
    >>> os.remove('tools_grep_2.txt')
    >>> os.remove('binary_file.txt')
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