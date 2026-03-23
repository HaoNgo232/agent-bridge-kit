"""Tests for _write_bridge_meta delegation to converters."""

import json
import pytest
from pathlib import Path

from agent_bridge.services.init_service import _write_bridge_meta


def test_write_bridge_meta_cursor(tmp_path):
    """_write_bridge_meta delegates to CursorConverter.build_bridge_meta_map."""
    agent_dir = tmp_path / ".agent"
    agent_dir.mkdir()
    cursor_agents = tmp_path / ".cursor" / "agents"
    cursor_agents.mkdir(parents=True)
    (cursor_agents / "orchestrator.md").write_text("# Orchestrator\n")

    _write_bridge_meta(tmp_path, ["cursor"])

    meta = json.loads((agent_dir / ".bridge-meta.json").read_text())
    assert ".cursor/agents/orchestrator.md" in meta["file_map"]
    assert meta["file_map"][".cursor/agents/orchestrator.md"] == ".agent/agents/orchestrator.md"
    assert "generated_at" in meta
    assert meta["generated_for"] == ["cursor"]


def test_write_bridge_meta_kiro(tmp_path):
    """_write_bridge_meta delegates to KiroConverter.build_bridge_meta_map."""
    agent_dir = tmp_path / ".agent"
    agent_dir.mkdir()
    kiro_agents = tmp_path / ".kiro" / "agents"
    kiro_agents.mkdir(parents=True)
    (kiro_agents / "orchestrator.json").write_text("{}")

    _write_bridge_meta(tmp_path, ["kiro"])

    meta = json.loads((agent_dir / ".bridge-meta.json").read_text())
    assert ".kiro/agents/orchestrator.json" in meta["file_map"]


def test_write_bridge_meta_multiple_ides(tmp_path):
    """Multiple IDEs combine their file_maps."""
    agent_dir = tmp_path / ".agent"
    agent_dir.mkdir()
    (tmp_path / ".cursor" / "agents").mkdir(parents=True)
    (tmp_path / ".cursor" / "agents" / "test.md").write_text("# Test\n")
    (tmp_path / ".kiro" / "agents").mkdir(parents=True)
    (tmp_path / ".kiro" / "agents" / "test.json").write_text("{}")

    _write_bridge_meta(tmp_path, ["cursor", "kiro"])

    meta = json.loads((agent_dir / ".bridge-meta.json").read_text())
    assert ".cursor/agents/test.md" in meta["file_map"]
    assert ".kiro/agents/test.json" in meta["file_map"]


def test_write_bridge_meta_no_agent_dir(tmp_path):
    """Silently skips if .agent/ does not exist."""
    _write_bridge_meta(tmp_path, ["cursor"])  # Should not raise
    assert not (tmp_path / ".agent" / ".bridge-meta.json").exists()


def test_write_bridge_meta_unknown_ide(tmp_path):
    """Unknown IDE is silently skipped."""
    agent_dir = tmp_path / ".agent"
    agent_dir.mkdir()

    _write_bridge_meta(tmp_path, ["nonexistent-ide"])

    meta = json.loads((agent_dir / ".bridge-meta.json").read_text())
    assert meta["file_map"] == {}
