"""
Centralized skill metadata registry.

Each skill can have IDE-specific activation/classification metadata.
IDEs can query this registry or override with their own maps.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class SkillMetadata:
    """Metadata for a skill that varies by IDE."""
    name: str
    description: str
    # Cursor-specific
    cursor_mode: Optional[str] = None  # "always-on" | "glob" | "slash-command"
    cursor_globs: List[str] = field(default_factory=list)
    # Windsurf-specific
    windsurf_mode: Optional[str] = None  # "always" | "glob" | "model" | "manual"
    windsurf_globs: List[str] = field(default_factory=list)


# Skill metadata registry
SKILL_METADATA: Dict[str, SkillMetadata] = {
    "clean-code": SkillMetadata(
        name="clean-code",
        description="Clean code principles and best practices",
        cursor_mode="always-on",
        windsurf_mode="always",
    ),
    "react-best-practices": SkillMetadata(
        name="react-best-practices",
        description="React and Next.js best practices",
        cursor_mode="glob",
        cursor_globs=["**/*.tsx", "**/*.jsx", "**/next.config.*"],
        windsurf_mode="glob",
        windsurf_globs=["**/*.tsx", "**/*.jsx", "**/next.config.*", "**/app/**/*"],
    ),
    "tailwind-patterns": SkillMetadata(
        name="tailwind-patterns",
        description="Tailwind CSS patterns and utilities",
        cursor_mode="glob",
        cursor_globs=["**/*.tsx", "**/*.jsx", "**/*.css"],
        windsurf_mode="glob",
        windsurf_globs=["**/*.tsx", "**/*.jsx", "**/*.css", "**/tailwind.config.*"],
    ),
    "python-patterns": SkillMetadata(
        name="python-patterns",
        description="Python best practices and patterns",
        cursor_mode="glob",
        cursor_globs=["**/*.py"],
        windsurf_mode="glob",
        windsurf_globs=["**/*.py", "**/pyproject.toml", "**/requirements.txt"],
    ),
    "testing-patterns": SkillMetadata(
        name="testing-patterns",
        description="Testing frameworks and patterns",
        cursor_mode="glob",
        cursor_globs=["**/*.test.*", "**/*.spec.*"],
        windsurf_mode="glob",
        windsurf_globs=["**/*.test.*", "**/*.spec.*", "**/__tests__/**/*"],
    ),
    "database-design": SkillMetadata(
        name="database-design",
        description="Database design and SQL patterns",
        cursor_mode="glob",
        cursor_globs=["**/*.sql", "**/prisma/**/*"],
        windsurf_mode="glob",
        windsurf_globs=["**/*.sql", "**/prisma/**/*", "**/migrations/**/*"],
    ),
}


def get_skill_metadata(skill_name: str) -> Optional[SkillMetadata]:
    """Get skill metadata from registry."""
    return SKILL_METADATA.get(skill_name)


def get_cursor_config(skill_name: str) -> Optional[Dict[str, any]]:
    """Get Cursor-specific config for a skill."""
    metadata = get_skill_metadata(skill_name)
    if not metadata or not metadata.cursor_mode:
        return None

    return {
        "mode": metadata.cursor_mode,
        "globs": metadata.cursor_globs or "",
        "description": metadata.description,
        "alwaysApply": metadata.cursor_mode == "always-on",
    }


def get_windsurf_config(skill_name: str) -> Optional[Dict[str, any]]:
    """Get Windsurf-specific config for a skill."""
    metadata = get_skill_metadata(skill_name)
    if not metadata or not metadata.windsurf_mode:
        return None
    
    return {
        "mode": metadata.windsurf_mode,
        "globs": metadata.windsurf_globs,
        "description": metadata.description,
    }
