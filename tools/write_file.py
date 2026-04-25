"""Single-file writing tool for the chat program.

This module is a thin wrapper around write_files for writing a single file.
"""

try:
    from .write_files import write_files
except ImportError:
    from tools.write_files import write_files


def write_file(path, contents, commit_message):
    """Write a single file to disk and commit it to git.

    Returns doctest output if the file is a Python file, otherwise a success message.

    >>> import os
    >>> from pathlib import Path
    >>> write_file('_wfile_test.txt', 'world', 'test single write')
    'Files written and committed: _wfile_test.txt'
    >>> Path('_wfile_test.txt').read_text(encoding='utf-8')
    'world'
    >>> os.remove('_wfile_test.txt')
    >>> write_file('/etc/hosts', 'x', 'bad')
    'Error: Absolute paths and directory traversal are not allowed.'
    """
    return write_files([{"path": path, "contents": contents}], commit_message)


write_file_schema = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": "Use this to write a single file to disk and commit it to git. Provide the path, contents, and a commit message.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The relative path of the file to write",
                },
                "contents": {
                    "type": "string",
                    "description": "The contents to write to the file",
                },
                "commit_message": {
                    "type": "string",
                    "description": "The commit message describing the change",
                },
            },
            "required": ["path", "contents", "commit_message"],
        },
    },
}
