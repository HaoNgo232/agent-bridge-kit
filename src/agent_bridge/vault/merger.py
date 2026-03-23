"""
Vault merge strategies.
Previously scattered across cli.py (_fetch_vault_to_project, _merge_vault_to_project).
"""

import shutil
from enum import Enum
from pathlib import Path
from typing import Dict, List

MERGE_SUBDIRS = ["agents", "skills", "workflows", "rules"]


class MergeStrategy(Enum):
    PROJECT_WINS = "project_wins"
    VAULT_WINS = "vault_wins"
    VAULT_ONLY = "vault_only"


def merge_source_into_project(
    source_dir: Path,
    project_agent_dir: Path,
    strategy: MergeStrategy = MergeStrategy.PROJECT_WINS,
) -> Dict[str, int]:
    counts: Dict[str, int] = {}

    if strategy == MergeStrategy.VAULT_ONLY:
        if project_agent_dir.exists():
            shutil.rmtree(project_agent_dir)
        shutil.copytree(source_dir, project_agent_dir)
        for subdir in MERGE_SUBDIRS:
            sub = project_agent_dir / subdir
            if sub.exists():
                counts[subdir] = sum(1 for _ in sub.iterdir())
        return counts

    project_agent_dir.mkdir(parents=True, exist_ok=True)
    project_agent_dir_resolved = project_agent_dir.resolve()

    for subdir in MERGE_SUBDIRS:
        src = source_dir / subdir
        dst = project_agent_dir / subdir
        if not src.exists():
            continue
        dst.mkdir(parents=True, exist_ok=True)
        merged = 0
        for item in src.iterdir():
            # Block symlinks from vaults
            if item.is_symlink():
                continue
            dest_item = dst / item.name
            # Block path traversal
            try:
                if not str(dest_item.resolve()).startswith(str(project_agent_dir_resolved)):
                    continue
            except (OSError, ValueError):
                continue
            if dest_item.exists() and strategy == MergeStrategy.PROJECT_WINS:
                continue
            if dest_item.exists() and strategy == MergeStrategy.VAULT_WINS:
                if dest_item.is_dir():
                    shutil.rmtree(dest_item)
                else:
                    dest_item.unlink()
            if not dest_item.exists():
                if item.is_dir():
                    shutil.copytree(item, dest_item)
                else:
                    shutil.copy2(item, dest_item)
                merged += 1
        counts[subdir] = merged

    return counts