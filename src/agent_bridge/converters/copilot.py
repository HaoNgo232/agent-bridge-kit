"""
GitHub Copilot converter — converts .agent/ to .github/agents and .github/skills format.

Output: .github/agents/*.md, .github/skills/<skill>/SKILL.md,
.github/prompts/*.prompt.md, .github/instructions/*.instructions.md
"""

import shutil
from pathlib import Path
from typing import Dict, List, Optional

from agent_bridge.core.converter import BaseConverter, converter_registry
from agent_bridge.core.types import CapturedFile, ConversionResult, IDEFormat

# Re-export cho tests va backward compatibility
from agent_bridge.converters._copilot_impl import (
    AGENT_SUBAGENTS_MAP,
    _role_to_copilot_tools,
    apply_reverse_capture_copilot,
    convert_rule_to_instruction,
    convert_skill_to_copilot,
    convert_to_copilot,
    convert_workflow_to_prompt,
    generate_copilot_frontmatter,
    reverse_convert_copilot,
)


class CopilotConverter(BaseConverter):
    """Converter cho GitHub Copilot format."""

    @property
    def format_info(self) -> IDEFormat:
        return IDEFormat(
            name="copilot",
            display_name="GitHub Copilot",
            output_dir=".github",
            checkbox_label="Copilot (.github/)",
            status="beta",
        )

    def convert(self, source_root: Path, dest_root: Path, verbose: bool = True, force: bool = False) -> ConversionResult:
        stats = convert_to_copilot(source_root, dest_root, verbose)
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
        return install_mcp_for_ide(source_root, dest_root, "copilot")

    def clean(self, project_path: Path) -> bool:
        for sub in ["agents", "skills", "prompts", "instructions"]:
            p = project_path / ".github" / sub
            if p.exists():
                shutil.rmtree(p)
        return True

    def reverse_convert(self, project_path: Path, agent_dir: Path, verbose: bool = True) -> List[CapturedFile]:
        return reverse_convert_copilot(project_path, agent_dir, verbose)

    @property
    def supports_capture(self) -> bool:
        return True

    def apply_reverse_capture(self, captured: CapturedFile, project_path: Path, agent_dir: Path) -> bool:
        return apply_reverse_capture_copilot(captured, project_path, agent_dir)

    def build_bridge_meta_map(self, project_path: Path) -> Dict[str, str]:
        file_map: Dict[str, str] = {}
        github_root = project_path / ".github"
        if not github_root.exists():
            return file_map

        agents_dir = github_root / "agents"
        if agents_dir.exists():
            for f in agents_dir.glob("*.md"):
                file_map[f".github/agents/{f.name}"] = f".agent/agents/{f.name}"

        skills_dir = github_root / "skills"
        if skills_dir.exists():
            for d in skills_dir.iterdir():
                if d.is_dir() and (d / "SKILL.md").exists():
                    file_map[f".github/skills/{d.name}/SKILL.md"] = f".agent/skills/{d.name}/SKILL.md"

        prompts_dir = github_root / "prompts"
        if prompts_dir.exists():
            for f in prompts_dir.glob("*.prompt.md"):
                file_map[f".github/prompts/{f.name}"] = f".agent/workflows/{f.stem.replace('.prompt', '')}.md"

        instructions_dir = github_root / "instructions"
        if instructions_dir.exists():
            for f in instructions_dir.glob("*.instructions.md"):
                file_map[f".github/instructions/{f.name}"] = f".agent/rules/{f.stem.replace('.instructions', '')}.md"

        return file_map

    @property
    def mcp_output_path(self) -> Optional[str]:
        return ".vscode/mcp.json"

    def transform_mcp_config(self, config: Dict) -> Dict:
        return {"servers": config.get("mcpServers", {})}


converter_registry.register(CopilotConverter)
