"""Tests for status_service.py"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta

# Import converters to trigger registration
from agent_bridge import converters  # noqa: F401

from agent_bridge.services.status_service import (
    collect_status,
    _count_agent_content,
    _get_mcp_info,
    _relative_time,
    _get_newest_mtime,
)


def test_collect_status_with_full_project(tmp_project):
    """Verify counts are correct with full project."""
    status = collect_status(tmp_project)
    
    assert status.project_path == tmp_project
    assert status.agent_dir_exists is True
    assert status.agent_counts["agents"] == 2
    assert status.agent_counts["skills"] == 1
    assert status.agent_counts["workflows"] == 1
    assert status.agent_counts["rules"] == 1
    assert status.mcp_info is not None
    assert status.mcp_info.server_count == 2


def test_collect_status_empty_project(tmp_path):
    """Verify graceful handling when no .agent/"""
    status = collect_status(tmp_path)
    
    assert status.agent_dir_exists is False
    assert status.agent_counts == {}
    assert status.mcp_info is None


def test_count_agent_content(tmp_project):
    """Verify correct counting of agents, skills, workflows, rules."""
    agent_dir = tmp_project / ".agent"
    counts = _count_agent_content(agent_dir)
    
    assert counts["agents"] == 2
    assert counts["skills"] == 1
    assert counts["workflows"] == 1
    assert counts["rules"] == 1


def test_count_agent_content_empty(tmp_path):
    """Verify zeros when dirs are empty."""
    agent_dir = tmp_path / ".agent"
    agent_dir.mkdir()
    (agent_dir / "agents").mkdir()
    (agent_dir / "skills").mkdir()
    (agent_dir / "workflows").mkdir()
    (agent_dir / "rules").mkdir()
    
    counts = _count_agent_content(agent_dir)
    
    assert counts["agents"] == 0
    assert counts["skills"] == 0
    assert counts["workflows"] == 0
    assert counts["rules"] == 0


def test_ide_status_initialized(tmp_project):
    """Verify initialized=True when dir exists with files."""
    # Create a .cursor/ dir with files
    cursor_dir = tmp_project / ".cursor"
    cursor_dir.mkdir()
    (cursor_dir / "test.md").write_text("test")
    
    status = collect_status(tmp_project)
    cursor_status = next((s for s in status.ide_statuses if s.name == "cursor"), None)
    
    assert cursor_status is not None
    assert cursor_status.initialized is True
    assert cursor_status.file_count > 0


def test_ide_status_not_initialized(tmp_project):
    """Verify initialized=False when dir doesn't exist."""
    status = collect_status(tmp_project)
    cursor_status = next((s for s in status.ide_statuses if s.name == "cursor"), None)
    
    assert cursor_status is not None
    assert cursor_status.initialized is False
    assert cursor_status.file_count == 0


def test_ide_staleness(tmp_project):
    """Verify stale=True when .agent/ files are newer than IDE files."""
    import time
    
    # Create old .cursor/ file
    cursor_dir = tmp_project / ".cursor"
    cursor_dir.mkdir()
    old_file = cursor_dir / "old.md"
    old_file.write_text("old")
    
    # Wait a bit
    time.sleep(0.1)
    
    # Touch .agent/ file to make it newer
    agent_file = tmp_project / ".agent" / "agents" / "new.md"
    agent_file.write_text("new")
    
    status = collect_status(tmp_project)
    cursor_status = next((s for s in status.ide_statuses if s.name == "cursor"), None)
    
    assert cursor_status is not None
    assert cursor_status.is_stale is True


def test_mcp_info_exists(tmp_project):
    """Verify server names extracted correctly."""
    agent_dir = tmp_project / ".agent"
    mcp_info = _get_mcp_info(agent_dir)
    
    assert mcp_info is not None
    assert mcp_info.config_exists is True
    assert mcp_info.server_count == 2
    assert "github" in mcp_info.server_names
    assert "filesystem" in mcp_info.server_names


def test_mcp_info_missing(tmp_path):
    """Verify None when no mcp_config.json."""
    agent_dir = tmp_path / ".agent"
    agent_dir.mkdir()
    
    mcp_info = _get_mcp_info(agent_dir)
    
    assert mcp_info is None


def test_relative_time():
    """Test human-readable time function with various deltas."""
    now = datetime.now()
    
    # Just now
    assert _relative_time(now) == "just now"
    
    # Minutes
    assert _relative_time(now - timedelta(minutes=5)) == "5m ago"
    
    # Hours
    assert _relative_time(now - timedelta(hours=2)) == "2h ago"
    
    # Days
    assert _relative_time(now - timedelta(days=3)) == "3d ago"
    
    # Weeks
    assert _relative_time(now - timedelta(weeks=2)) == "2w ago"
    
    # None
    assert _relative_time(None) == "never"


def test_get_newest_mtime(tmp_project):
    """Verify newest mtime is found correctly."""
    import time
    
    agent_dir = tmp_project / ".agent"
    
    # Create old file
    old_file = agent_dir / "old.txt"
    old_file.write_text("old")
    old_mtime = datetime.fromtimestamp(old_file.stat().st_mtime)
    
    time.sleep(0.1)
    
    # Create new file
    new_file = agent_dir / "new.txt"
    new_file.write_text("new")
    new_mtime = datetime.fromtimestamp(new_file.stat().st_mtime)
    
    newest = _get_newest_mtime(agent_dir)
    
    assert newest is not None
    assert newest >= new_mtime
    assert newest >= old_mtime
