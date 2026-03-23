"""MCP configuration helpers."""

import json
from pathlib import Path
from typing import Any, Dict, Optional


def load_mcp_config(source_root: Path) -> Optional[Dict[str, Any]]:
    """Load MCP configuration from .agent/mcp_config.json."""
    mcp_file = source_root / ".agent" / "mcp_config.json"
    if mcp_file.exists():
        try:
            return json.loads(mcp_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None
    return None


def write_mcp_config(dest_path: Path, config: Dict[str, Any]) -> bool:
    """Write MCP configuration to destination."""
    try:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
        return True
    except Exception as e:
        print(f"  Error writing MCP config: {e}")
        return False


def _transform_mcp_config(config: Dict[str, Any], ide: str) -> Dict[str, Any]:
    """Transform .agent/mcp_config.json to IDE-specific MCP format via converter."""
    from agent_bridge.core.converter import converter_registry

    converter = converter_registry.get(ide)
    if converter:
        return converter.transform_mcp_config(config)
    # Fallback for unknown IDEs
    return config


def install_mcp_for_ide(source_root: Path, dest_root: Path, ide: str) -> bool:
    """Install MCP configuration for specific IDE via converter registry."""
    from agent_bridge.core.converter import converter_registry

    mcp_config = load_mcp_config(source_root)
    if not mcp_config:
        print("  No MCP configuration found in .agent/mcp_config.json")
        return False

    converter = converter_registry.get(ide.lower())
    if not converter or not converter.mcp_output_path:
        print(f"  Unknown IDE or no MCP path defined: {ide}")
        return False

    dest_path = dest_root / converter.mcp_output_path
    return write_mcp_config(dest_path, converter.transform_mcp_config(mcp_config))
