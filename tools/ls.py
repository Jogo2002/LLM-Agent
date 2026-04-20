"""File listing tool for the chat program.

This module lists files in the current directory or a relative subdirectory.
"""

import glob
import json
import os
from pathlib import PurePath


def ls(path=None):
    """List files in the current directory or in the given relative directory.

    >>> result = ls()
    >>> 'files' in result
    True
    >>> result = ls('nonexistent_dir')
    >>> 'error' in result
    True
    >>> result = ls('.')
    >>> 'files' in result
    True
    >>> ls('/')  # doctest: +ELLIPSIS
    '{"error": "Absolute paths and directory traversal are not allowed."}'
    >>> ls('../')  # doctest: +ELLIPSIS
    '{"error": "Absolute paths and directory traversal are not allowed."}'
    """
    try:
        if path is not None and path != "":
            if os.path.isabs(path) or any(part == ".." for part in PurePath(path).parts):
                raise ValueError("Absolute paths and directory traversal are not allowed.")
            if not os.path.isdir(path):
                raise ValueError("Directory does not exist.")

        if path is None or path == "":
            files = sorted(glob.glob("*"))
        else:
            files = sorted(glob.glob(f"{path}/*"))

        return json.dumps({"files": files})
    except Exception as e:
        return json.dumps({"error": str(e)})
