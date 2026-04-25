"""File removal tool for the chat program.

This module deletes files matching a glob pattern and commits the removal to git.
"""

import glob
import os
from pathlib import PurePath

import git


def rm(path):
    """Delete files matching a glob pattern and commit the removal to git.

    >>> from pathlib import Path
    >>> Path('_rm_test_a.txt').write_text('a', encoding='utf-8')
    1
    >>> Path('_rm_test_b.txt').write_text('b', encoding='utf-8')
    1
    >>> rm('/etc/passwd')
    'Error: Absolute paths and directory traversal are not allowed.'
    >>> rm('../something.txt')
    'Error: Absolute paths and directory traversal are not allowed.'
    >>> result = rm('_rm_test_a.txt')
    >>> 'removed' in result
    True
    >>> os.path.exists('_rm_test_a.txt')
    False
    >>> result = rm('_rm_test_*.txt')
    >>> 'removed' in result
    True
    >>> os.path.exists('_rm_test_b.txt')
    False
    >>> rm('_rm_nonexistent_*.txt')
    'Error: No files matched the pattern: _rm_nonexistent_*.txt'
    """
    if PurePath(path).is_absolute() or any(part == ".." for part in PurePath(path).parts):
        return "Error: Absolute paths and directory traversal are not allowed."

    matched = glob.glob(path)
    if not matched:
        return f"Error: No files matched the pattern: {path}"

    repo = git.Repo(".")
    removed = []
    for f in matched:
        os.remove(f)
        try:
            repo.index.remove([f])
        except git.exc.GitCommandError:
            pass  # file was untracked; no index entry to remove
        removed.append(f)

    repo.index.commit(f"[docchat] rm {path}")
    return f"Files removed and committed: {', '.join(removed)}"


rm_schema = {
    "type": "function",
    "function": {
        "name": "rm",
        "description": "Use this to delete files matching a glob pattern and commit the removal to git.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The file path or glob pattern of files to delete",
                }
            },
            "required": ["path"],
        },
    },
}
