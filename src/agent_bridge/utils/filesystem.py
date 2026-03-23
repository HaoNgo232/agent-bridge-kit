"""Filesystem utility helpers."""

import shutil
from pathlib import Path


def safe_copy(src: Path, dest: Path, overwrite: bool = True) -> bool:
    """Safely copy file or directory."""
    try:
        if dest.exists() and not overwrite:
            return False
        dest.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dest)
        return True
    except Exception as e:
        print(f"  Error copying {src} to {dest}: {e}")
        return False


def safe_remove(path: Path) -> bool:
    """Safely remove file or directory."""
    try:
        if not path.exists():
            return True
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
        return True
    except Exception as e:
        print(f"  Error removing {path}: {e}")
        return False


def ensure_dir(path: Path) -> bool:
    """Ensure directory exists."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"  Error creating directory {path}: {e}")
        return False
