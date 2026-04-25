"""File writing tool for the chat program.

This module writes files to disk and commits them to git.
"""

import os
from pathlib import PurePath

import git

try:
    from .doctests import doctests
except ImportError:
    from tools.doctests import doctests


def _validate_path(path):
    """Raise ValueError if path is absolute or contains traversal."""
    if PurePath(path).is_absolute() or any(part == ".." for part in PurePath(path).parts):
        raise ValueError("Absolute paths and directory traversal are not allowed.")


def write_files(files, commit_message):
    """Write multiple files to disk and commit them to git.

    Each item in files must be a dict with 'path' and 'contents' keys.
    Returns doctest output for any .py files written, otherwise a success message.

    >>> import os
    >>> from pathlib import Path
    >>> write_files([{'path': '_wf_test.txt', 'contents': 'hello'}], 'test commit')
    'Files written and committed: _wf_test.txt'
    >>> Path('_wf_test.txt').read_text(encoding='utf-8')
    'hello'
    >>> os.remove('_wf_test.txt')
    >>> write_files([{'path': '/etc/passwd', 'contents': 'x'}], 'bad')
    'Error: Absolute paths and directory traversal are not allowed.'
    >>> write_files([{'path': '../evil.txt', 'contents': 'x'}], 'bad')
    'Error: Absolute paths and directory traversal are not allowed.'
    """
    try:
        for f in files:
            _validate_path(f["path"])

        repo = git.Repo(".")
        written_paths = []
        doctest_outputs = []

        for f in files:
            path = f["path"]
            contents = f["contents"]
            os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(contents)
            repo.index.add([path])
            written_paths.append(path)

            if path.endswith(".py"):
                doctest_outputs.append(doctests(path))

        repo.index.commit(f"[docchat] {commit_message}")

        if doctest_outputs:
            return "\n".join(doctest_outputs)
        return f"Files written and committed: {', '.join(written_paths)}"

    except ValueError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error: {e}"


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

write_files_schema = {
    "type": "function",
    "function": {
        "name": "write_files",
        "description": "Use this to write multiple files at once and commit them to git in a single commit. Prefer this over write_file when writing more than one file.",
        "parameters": {
            "type": "object",
            "properties": {
                "files": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "contents": {"type": "string"},
                        },
                        "required": ["path", "contents"],
                    },
                    "description": "List of files with path and contents to write",
                },
                "commit_message": {
                    "type": "string",
                    "description": "The commit message describing the change",
                },
            },
            "required": ["files", "commit_message"],
        },
    },
}
