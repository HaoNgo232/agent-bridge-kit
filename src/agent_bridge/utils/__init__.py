"""
agent_bridge.utils — backward-compatible re-export package.

All public names from the original utils.py are re-exported here so that
existing ``from agent_bridge.utils import X`` imports continue to work.
"""

# Sub-modules (importable as agent_bridge.utils.colors, etc.)
from agent_bridge.utils import colors, display, filesystem, mcp  # noqa: F401

# Flat re-exports — keep every name that was public in the original utils.py
from agent_bridge.utils.colors import Colors
from agent_bridge.utils.display import print_error, print_header, print_info, print_success
from agent_bridge.utils.filesystem import ensure_dir, safe_copy, safe_remove
from agent_bridge.utils.mcp import (
    _transform_mcp_config,
    install_mcp_for_ide,
    load_mcp_config,
    write_mcp_config,
)

# Everything else that lived in utils.py but doesn't belong to a focused module
# is kept here directly.

import json
import logging
import re
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

logger = logging.getLogger("agent_bridge")


def ask_user(question: str, default: bool = True) -> bool:
    choices = " [Y/n]: " if default else " [y/N]: "
    while True:
        print(f"{Colors.YELLOW}❓ {question}{choices}{Colors.ENDC}", end="", flush=True)
        choice = input().strip().lower()
        if not choice:
            return default
        if choice in ["y", "yes"]:
            return True
        if choice in ["n", "no"]:
            return False


def get_master_agent_dir() -> Path:
    xdg_path = Path.home() / ".config" / "agent-bridge" / "cache" / "antigravity-kit" / ".agent"
    if xdg_path.exists():
        return xdg_path
    return Path(__file__).resolve().parent.parent.parent / ".agent"


def confirm_overwrite(path: Path, default: bool = False) -> bool:
    if not path.exists():
        return True
    default_str = "Y/n" if default else "y/N"
    try:
        response = input(f"  File {path} exists. Overwrite? [{default_str}]: ").strip().lower()
        if not response:
            return default
        return response in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        return False


def validate_path_within_project(path: Path, project_root: Path = None) -> bool:
    project_root = project_root or Path.cwd()
    try:
        resolved = path.resolve()
        project_resolved = project_root.resolve()
        return str(resolved).startswith(str(project_resolved))
    except (OSError, ValueError):
        return False


def safe_read_text(path: Path, encoding: str = "utf-8") -> Optional[str]:
    for enc in [encoding, "utf-8-sig", "latin-1"]:
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
        except OSError as e:
            print(f"  Error reading {path}: {e}")
            return None
    print(f"  Error: Could not decode {path} with any known encoding")
    return None


_RE_FRONTMATTER_STRIP = re.compile(r"^---\n.*?\n---\n*", re.DOTALL)
_RE_H1 = re.compile(r"^#\s+(.+)$", re.MULTILINE)


def strip_frontmatter(content: str) -> str:
    return _RE_FRONTMATTER_STRIP.sub("", content)


def resolve_source_root(source_dir: str) -> Optional[Path]:
    root_path = Path(source_dir).resolve()
    if root_path.name == ".agent":
        return root_path.parent
    elif (root_path / ".agent").exists():
        return root_path
    else:
        master_path = get_master_agent_dir()
        if master_path.exists():
            print(f"{Colors.YELLOW}🔔 Local .agent not found, using Master Vault: {master_path}{Colors.ENDC}")
            return master_path.parent
    print(f"{Colors.RED}❌ Error: No agent knowledge source found.{Colors.ENDC}")
    return None


def extract_yaml_frontmatter(content: str) -> tuple[Optional[Dict], str]:
    match = re.match(r"^---\n(.*?)\n---\n*", content, re.DOTALL)
    if match:
        try:
            frontmatter = yaml.safe_load(match.group(1))
            body = content[match.end():]
            return frontmatter, body
        except yaml.YAMLError:
            pass
    return None, content


def add_yaml_frontmatter(content: str, frontmatter: Dict) -> str:
    content_clean = re.sub(r"^---\n.*?\n---\n*", "", content, flags=re.DOTALL)
    fm_str = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False)
    return f"---\n{fm_str}---\n\n{content_clean.strip()}\n"


def truncate_content(content: str, max_length: int, suffix: str = "\n\n... (truncated)\n") -> str:
    if len(content) <= max_length:
        return content
    return content[: max_length - len(suffix)] + suffix


__all__ = [
    # sub-modules
    "colors", "display", "filesystem", "mcp",
    # colors
    "Colors",
    # display
    "print_header", "print_success", "print_error", "print_info",
    # filesystem
    "safe_copy", "safe_remove", "ensure_dir",
    # mcp
    "load_mcp_config", "write_mcp_config", "install_mcp_for_ide", "_transform_mcp_config",
    # misc (kept here)
    "ask_user", "get_master_agent_dir", "confirm_overwrite",
    "validate_path_within_project", "safe_read_text",
    "strip_frontmatter", "resolve_source_root",
    "extract_yaml_frontmatter", "add_yaml_frontmatter", "truncate_content",
    "logger",
]
