"""Tests for OpenCode converter."""

import json
import pytest
from pathlib import Path
from agent_bridge.converters.opencode import OpenCodeConverter


def test_convert_agent_creates_md(tmp_project):
    """Verify .opencode/agents/ files created."""
    converter = OpenCodeConverter()
    source_root = tmp_project
    dest_root = tmp_project
    
    result = converter.convert(source_root, dest_root, verbose=False)
    
    assert result.ok is True
    
    agent_file = dest_root / ".opencode" / "agents" / "orchestrator.md"
    assert agent_file.exists()


def test_agent_frontmatter_format(tmp_project):
    """Verify OpenCode agent frontmatter has mode, tools, permission."""
    converter = OpenCodeConverter()
    source_root = tmp_project
    dest_root = tmp_project
    
    result = converter.convert(source_root, dest_root, verbose=False)
    
    agent_file = dest_root / ".opencode" / "agents" / "orchestrator.md"
    content = agent_file.read_text()
    
    # Check frontmatter structure
    assert content.startswith("---\n")
    assert "mode:" in content
    assert "tools:" in content
    assert "permission:" in content


def test_convert_skill_to_opencode_skill(tmp_project):
    """Verify skills go to .opencode/skills/"""
    converter = OpenCodeConverter()
    source_root = tmp_project
    dest_root = tmp_project
    
    result = converter.convert(source_root, dest_root, verbose=False)
    
    skill_file = dest_root / ".opencode" / "skills" / "clean-code" / "SKILL.md"
    assert skill_file.exists()


def test_convert_workflow_to_command(tmp_project):
    """Verify workflows become .opencode/commands/"""
    converter = OpenCodeConverter()
    source_root = tmp_project
    dest_root = tmp_project
    
    result = converter.convert(source_root, dest_root, verbose=False)
    
    command_file = dest_root / ".opencode" / "commands" / "brainstorm.md"
    assert command_file.exists()


def test_opencode_json_created(tmp_project):
    """Verify opencode.json is created with correct structure."""
    converter = OpenCodeConverter()
    source_root = tmp_project
    dest_root = tmp_project
    
    result = converter.convert(source_root, dest_root, verbose=False)
    
    config_file = dest_root / ".opencode" / "opencode.json"
    assert config_file.exists()
    
    config = json.loads(config_file.read_text())
    assert "agents" in config
    assert "commands" in config


def test_convert_to_opencode_full(tmp_project):
    """End-to-end with tmp_project."""
    converter = OpenCodeConverter()
    source_root = tmp_project
    dest_root = tmp_project
    
    result = converter.convert(source_root, dest_root, verbose=False)
    
    assert result.ok is True
    assert result.agents == 2
    assert result.skills == 1
    assert result.workflows == 1


def test_mcp_installation(tmp_project):
    """Verify MCP config is embedded in opencode.json."""
    # Create MCP config
    mcp_config = tmp_project / ".agent" / "mcp_config.json"
    mcp_config.write_text(json.dumps({
        "mcpServers": {
            "test-server": {
                "command": "node",
                "args": ["server.js"]
            }
        }
    }))
    
    converter = OpenCodeConverter()
    source_root = tmp_project
    dest_root = tmp_project
    
    # Convert first
    converter.convert(source_root, dest_root, verbose=False)
    
    # Install MCP
    result = converter.install_mcp(source_root, dest_root, force=False)
    assert result is True
    
    # Check opencode.json has MCP embedded
    config_file = dest_root / ".opencode" / "opencode.json"
    config = json.loads(config_file.read_text())
    assert "mcp" in config or "mcpServers" in config


def test_clean_removes_opencode_dir(tmp_project):
    """Verify clean() removes .opencode/ directory."""
    converter = OpenCodeConverter()
    source_root = tmp_project
    dest_root = tmp_project
    
    # Convert first
    converter.convert(source_root, dest_root, verbose=False)
    assert (dest_root / ".opencode").exists()
    
    # Clean
    result = converter.clean(dest_root)
    assert result is True
    assert not (dest_root / ".opencode").exists()
