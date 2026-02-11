"""Shared fixtures for tests."""

import pytest
from pathlib import Path
import json


@pytest.fixture
def tmp_project(tmp_path):
    """Create a minimal project with .agent/ structure."""
    agent_dir = tmp_path / ".agent"
    (agent_dir / "agents").mkdir(parents=True)
    (agent_dir / "skills").mkdir(parents=True)
    (agent_dir / "workflows").mkdir(parents=True)
    (agent_dir / "rules").mkdir(parents=True)
    
    # Create sample agents
    (agent_dir / "agents" / "orchestrator.md").write_text(
        "# Orchestrator\n\nYou are the orchestrator agent.\n"
    )
    (agent_dir / "agents" / "frontend-specialist.md").write_text(
        "# Frontend Specialist\n\nYou are a frontend expert.\n"
    )
    
    # Create sample skill
    skill_dir = agent_dir / "skills" / "clean-code"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "# Clean Code\n\n> Best practices for clean code.\n\n## Rules\n\n1. Keep functions small\n"
    )
    
    # Create sample workflow
    (agent_dir / "workflows" / "plan.md").write_text(
        "# Plan\n\n> Create an implementation plan\n\n## Steps\n\n1. Analyze requirements\n2. Break down tasks\n"
    )
    
    # Create sample rule
    (agent_dir / "rules" / "global.md").write_text(
        "# Global Rules\n\n1. Always test your code\n"
    )
    
    # Create sample MCP config
    mcp_config = {
        "mcpServers": {
            "github": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-github"]},
            "filesystem": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem"]}
        }
    }
    (agent_dir / "mcp_config.json").write_text(json.dumps(mcp_config, indent=2))
    
    return tmp_path
