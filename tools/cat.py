"""File reading tool for the chat program.

This module reads UTF-8 text from a file and returns its contents.
"""


def cat(filename):
    """Read the contents of a UTF-8 text file.

    >>> from pathlib import Path
    >>> test_path = Path('tools_cat_test.txt')
    >>> _ = test_path.write_text('hello', encoding='utf-8')
    >>> cat('tools_cat_test.txt')
    'hello'
    >>> _ = test_path.unlink()
    >>> cat('tools_cat_test.txt')
    "Error: [Errno 2] No such file or directory: 'tools_cat_test.txt'"
    >>> _ = open('binary_file.txt', 'wb').write(b'\\xff\\xfe')
    >>> cat('binary_file.txt')
    "Error: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte"
    >>> import os; os.remove('binary_file.txt')
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    except (FileNotFoundError, UnicodeDecodeError) as e:
        return f"Error: {e}"
