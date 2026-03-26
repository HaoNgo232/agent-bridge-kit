"""
Kiro CLI converter — converts .agent/ sang dang .kiro/agents, skills, prompts, steering.
"""

import shutil
from pathlib import Path
from typing import Dict, List, Optional

from agent_bridge.core.converter import BaseConverter, converter_registry
from agent_bridge.core.types import CapturedFile, ConversionResult, IDEFormat
from agent_bridge.converters._kiro_impl import (
    apply_reverse_capture_kiro,
    convert_to_kiro,
    reverse_convert_kiro,
)


class KiroConverter(BaseConverter):
    """Converter cho Kiro CLI format."""

    @property
    def format_info(self) -> IDEFormat:
        return IDEFormat(
            name="kiro",
            display_name="Kiro CLI",
            output_dir=".kiro",
            checkbox_label="Kiro (.kiro/)",
            status="beta",
        )

    def convert(self, source_root: Path, dest_root: Path, verbose: bool = True, force: bool = False) -> ConversionResult:
        stats = convert_to_kiro(source_root, dest_root, verbose)
        return ConversionResult(
            agents=stats.get("agents", 0),
            skills=stats.get("skills", 0),
            workflows=stats.get("prompts", 0) + stats.get("steering", 0),
            errors=stats.get("errors", []),
            warnings=stats.get("warnings", []),
        )

    def install_mcp(self, source_root: Path, dest_root: Path, force: bool = False) -> bool:
        from agent_bridge.utils import install_mcp_for_ide
        return install_mcp_for_ide(source_root, dest_root, "kiro")

    def clean(self, project_path: Path) -> bool:
        for sub in ["agents", "skills", "steering", "prompts"]:
            p = project_path / ".kiro" / sub
            if p.exists():
                shutil.rmtree(p)
        return True

    def reverse_convert(self, project_path: Path, agent_dir: Path, verbose: bool = True) -> List[CapturedFile]:
        return reverse_convert_kiro(project_path, agent_dir, verbose)

    @property
    def supports_capture(self) -> bool:
        return True

    def apply_reverse_capture(self, captured: CapturedFile, project_path: Path, agent_dir: Path) -> bool:
        return apply_reverse_capture_kiro(captured, project_path, agent_dir)

    def build_bridge_meta_map(self, project_path: Path) -> Dict[str, str]:
        file_map: Dict[str, str] = {}
        kiro_root = project_path / ".kiro"
        if not kiro_root.exists():
            return file_map

        agents_dir = kiro_root / "agents"
        if agents_dir.exists():
            for f in agents_dir.glob("*.json"):
                file_map[f".kiro/agents/{f.name}"] = f".agent/agents/{f.stem}.md"

        skills_dir = kiro_root / "skills"
        if skills_dir.exists():
            for d in skills_dir.iterdir():
                if d.is_dir() and (d / "SKILL.md").exists():
                    file_map[f".kiro/skills/{d.name}/SKILL.md"] = f".agent/skills/{d.name}/SKILL.md"

        prompts_dir = kiro_root / "prompts"
        if prompts_dir.exists():
            for f in prompts_dir.glob("*.md"):
                file_map[f".kiro/prompts/{f.name}"] = f".agent/workflows/{f.name}"

        steering_dir = kiro_root / "steering"
        if steering_dir.exists():
            for f in steering_dir.glob("*.md"):
                file_map[f".kiro/steering/{f.name}"] = f".agent/rules/{f.name}"

        if (kiro_root / "settings" / "mcp.json").exists():
            file_map[".kiro/settings/mcp.json"] = ".agent/mcp_config.json"

        return file_map

    @property
    def mcp_output_path(self) -> Optional[str]:
        return ".kiro/settings/mcp.json"

    def transform_mcp_config(self, config: Dict) -> Dict:
        return {"mcpServers": config.get("mcpServers", {})}


converter_registry.register(KiroConverter)
