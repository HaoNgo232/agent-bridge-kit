"""
Cursor AI converter — chuyen doi .agent/ sang dang .cursor/agents, rules, skills.
"""

import shutil
from pathlib import Path
from typing import Dict, List, Optional

from agent_bridge.core.converter import BaseConverter, converter_registry
from agent_bridge.core.types import CapturedFile, ConversionResult, IDEFormat
from agent_bridge.converters._cursor_impl import (
    apply_reverse_capture_cursor,
    convert_to_cursor,
    reverse_convert_cursor,
)


class CursorConverter(BaseConverter):
    """Converter cho Cursor AI format."""

    @property
    def format_info(self) -> IDEFormat:
        return IDEFormat(
            name="cursor",
            display_name="Cursor AI",
            output_dir=".cursor",
            checkbox_label="Cursor (.cursor/)",
            status="beta",
        )

    def convert(self, source_root: Path, dest_root: Path, verbose: bool = True, force: bool = False) -> ConversionResult:
        stats = convert_to_cursor(source_root, dest_root, verbose)
        return ConversionResult(
            agents=stats.get("agents", 0),
            skills=stats.get("skills", 0),
            workflows=stats.get("workflows", 0),
            rules=stats.get("rules", 0),
            errors=stats.get("errors", []),
            warnings=stats.get("warnings", []),
        )

    def install_mcp(self, source_root: Path, dest_root: Path, force: bool = False) -> bool:
        from agent_bridge.utils import install_mcp_for_ide
        return install_mcp_for_ide(source_root, dest_root, "cursor")

    def clean(self, project_path: Path) -> bool:
        for sub in ["agents", "rules", "skills"]:
            p = project_path / ".cursor" / sub
            if p.exists():
                shutil.rmtree(p)
        return True

    def reverse_convert(self, project_path: Path, agent_dir: Path, verbose: bool = True) -> List[CapturedFile]:
        return reverse_convert_cursor(project_path, agent_dir, verbose)

    @property
    def supports_capture(self) -> bool:
        return True

    def apply_reverse_capture(self, captured: CapturedFile, project_path: Path, agent_dir: Path) -> bool:
        return apply_reverse_capture_cursor(captured, project_path, agent_dir)

    def build_bridge_meta_map(self, project_path: Path) -> Dict[str, str]:
        from agent_bridge.converters._cursor_impl import _parse_mdc_frontmatter

        file_map: Dict[str, str] = {}
        cursor_root = project_path / ".cursor"
        if not cursor_root.exists():
            return file_map

        agents_dir = cursor_root / "agents"
        if agents_dir.exists():
            for f in agents_dir.glob("*.md"):
                file_map[f".cursor/agents/{f.name}"] = f".agent/agents/{f.name}"

        rules_dir = cursor_root / "rules"
        if rules_dir.exists():
            for f in rules_dir.glob("*.mdc"):
                if f.name == "project-instructions.mdc":
                    continue
                try:
                    fm, _ = _parse_mdc_frontmatter(f.read_text(encoding="utf-8"))
                    always_apply = fm.get("alwaysApply", False)
                    globs = fm.get("globs", "").strip()
                    if always_apply and not globs:
                        file_map[f".cursor/rules/{f.name}"] = f".agent/rules/{f.stem}.md"
                    else:
                        file_map[f".cursor/rules/{f.name}"] = f".agent/skills/{f.stem}/SKILL.md"
                except (OSError, TypeError):
                    file_map[f".cursor/rules/{f.name}"] = f".agent/skills/{f.stem}/SKILL.md"

        skills_dir = cursor_root / "skills"
        if skills_dir.exists():
            for d in skills_dir.iterdir():
                if d.is_dir() and (d / "SKILL.md").exists():
                    file_map[f".cursor/skills/{d.name}/SKILL.md"] = f".agent/skills/{d.name}/SKILL.md"

        return file_map

    @property
    def mcp_output_path(self) -> Optional[str]:
        return ".cursor/mcp.json"

    def transform_mcp_config(self, config: Dict) -> Dict:
        return config  # Cursor uses config as-is


converter_registry.register(CursorConverter)
