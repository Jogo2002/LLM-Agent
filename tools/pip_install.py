"""Pip install tool for the chat program.

Installs Python packages using pip.
"""

import subprocess
import sys


def pip_install(library_name):
    """Install a Python package using pip.

    # I use "in" here because there is no way for the package to output "Successfully installed"
    # or "already satisfied" without running correctly, so using 'in' isn't a cop-out
    >>> result = pip_install('requests')
    >>> 'Successfully installed' in result or 'already satisfied' in result
    True

    >>> pip_install('fake_package_182u3418324-8')
    'Error: Failed install of fake_package_182u3418324-8'
    """
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", library_name],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return result.stdout
    return "Error: Failed install of " + library_name


pip_install_schema = {
    "type": "function",
    "function": {
        "name": "pip_install",
        "description": "Use this to install a Python package using pip.",
        "parameters": {
            "type": "object",
            "properties": {
                "library_name": {
                    "type": "string",
                    "description": "The name of the Python package to install",
                }
            },
            "required": ["library_name"],
        },
    },
}
