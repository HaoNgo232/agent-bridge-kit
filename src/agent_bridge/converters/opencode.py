"""
OpenCode converter — converts .agent/ sang dang .opencode/agents, commands, skills.
"""

import shutil
from pathlib import Path

from agent_bridge.core.converter import BaseConverter, converter_registry
from agent_bridge.core.types import ConversionResult, IDEFormat
from agent_bridge.converters._opencode_impl import convert_to_opencode, copy_mcp_opencode


class OpenCodeConverter(BaseConverter):
    """Converter cho OpenCode IDE format."""

    @property
    def format_info(self) -> IDEFormat:
        return IDEFormat(
            name="opencode",
            display_name="OpenCode IDE",
            output_dir=".opencode",
            checkbox_label="OpenCode (.opencode/)",
            status="beta",
        )

    def convert(
        self,
        source_root: Path,
        dest_root: Path,
        verbose: bool = True,
        force: bool = False,
    ) -> ConversionResult:
        stats = convert_to_opencode(source_root, dest_root, verbose)
        return ConversionResult(
            agents=stats.get("agents", 0),
            skills=stats.get("skills", 0),
            workflows=stats.get("commands", 0),
            errors=stats.get("errors", []),
        )

    def install_mcp(
        self, source_root: Path, dest_root: Path, force: bool = False
    ) -> bool:
        return copy_mcp_opencode(dest_root, force)

    @property
    def mcp_output_path(self) -> str:
        return ".opencode/mcp.json"

    def clean(self, project_path: Path) -> bool:
        opencode_dir = project_path / ".opencode"
        if opencode_dir.exists():
            shutil.rmtree(opencode_dir)
        config_file = project_path / ".opencode" / "opencode.json"
        if config_file.exists():
            config_file.unlink()
        return True


converter_registry.register(OpenCodeConverter)
