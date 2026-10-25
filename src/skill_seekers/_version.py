"""
Single source of truth for skill-seekers version.

This module dynamically reads the version from pyproject.toml to avoid
version mismatches across multiple files.
"""

from pathlib import Path

import tomllib


def get_version() -> str:
    """
    Read version from pyproject.toml.

    Returns:
        Version string (e.g., "3.0.0")
    """
    try:
        # Get path to pyproject.toml (3 levels up from this file)
        repo_root = Path(__file__).parent.parent.parent
        pyproject_path = repo_root / "pyproject.toml"

        if not pyproject_path.exists():
            # Fallback for installed package
            return "3.10.0"  # Hardcoded fallback

        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)

        return pyproject_data["project"]["version"]

    except Exception:
        # Fallback if anything goes wrong
        return "3.10.0"  # Hardcoded fallback


__version__ = get_version()
