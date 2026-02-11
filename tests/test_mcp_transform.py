"""Tests for MCP format transformation."""

import pytest
import json
from pathlib import Path
from agent_bridge.utils import _transform_mcp_config, install_mcp_for_ide


def test_copilot_mcp_uses_servers_key():
    """Verify output has 'servers' not 'mcpServers'."""
    config = {
        "mcpServers": {
            "github": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-github"]}
        }
    }
    
    result = _transform_mcp_config(config, "copilot")
    
    assert "servers" in result
    assert "mcpServers" not in result
    assert "github" in result["servers"]


def test_cursor_mcp_uses_mcpservers_key():
    """Verify output keeps 'mcpServers'."""
    config = {
        "mcpServers": {
            "github": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-github"]}
        }
    }
    
    result = _transform_mcp_config(config, "cursor")
    
    assert "mcpServers" in result
    assert "github" in result["mcpServers"]


def test_kiro_mcp_uses_mcpservers_key():
    """Verify Kiro keeps 'mcpServers'."""
    config = {
        "mcpServers": {
            "github": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-github"]}
        }
    }
    
    result = _transform_mcp_config(config, "kiro")
    
    assert "mcpServers" in result
    assert "github" in result["mcpServers"]


def test_windsurf_mcp_uses_mcpservers_key():
    """Verify Windsurf keeps 'mcpServers'."""
    config = {
        "mcpServers": {
            "github": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-github"]}
        }
    }
    
    result = _transform_mcp_config(config, "windsurf")
    
    assert "mcpServers" in result
    assert "github" in result["mcpServers"]


def test_transform_preserves_server_content():
    """Verify server configs are not modified."""
    config = {
        "mcpServers": {
            "github": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-github"],
                "env": {"GITHUB_TOKEN": "xxx"}
            }
        }
    }
    
    result = _transform_mcp_config(config, "copilot")
    
    assert result["servers"]["github"]["command"] == "npx"
    assert result["servers"]["github"]["args"] == ["-y", "@modelcontextprotocol/server-github"]
    assert result["servers"]["github"]["env"]["GITHUB_TOKEN"] == "xxx"


def test_transform_empty_config():
    """Verify handles empty mcpServers gracefully."""
    config = {"mcpServers": {}}
    
    result_copilot = _transform_mcp_config(config, "copilot")
    result_cursor = _transform_mcp_config(config, "cursor")
    
    assert result_copilot == {"servers": {}}
    assert result_cursor == {"mcpServers": {}}


def test_install_mcp_copilot_writes_correct_format(tmp_project):
    """End-to-end test with tmp_project fixture."""
    source_root = tmp_project
    dest_root = tmp_project
    
    success = install_mcp_for_ide(source_root, dest_root, "copilot")
    
    assert success is True
    
    vscode_mcp = dest_root / ".vscode" / "mcp.json"
    assert vscode_mcp.exists()
    
    config = json.loads(vscode_mcp.read_text())
    assert "servers" in config
    assert "mcpServers" not in config
    assert "github" in config["servers"]
    assert "filesystem" in config["servers"]


def test_install_mcp_cursor_writes_correct_format(tmp_project):
    """Verify Cursor uses mcpServers key."""
    source_root = tmp_project
    dest_root = tmp_project
    
    success = install_mcp_for_ide(source_root, dest_root, "cursor")
    
    assert success is True
    
    cursor_mcp = dest_root / ".cursor" / "mcp.json"
    assert cursor_mcp.exists()
    
    config = json.loads(cursor_mcp.read_text())
    assert "mcpServers" in config
    assert "github" in config["mcpServers"]
