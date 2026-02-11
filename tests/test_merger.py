"""Tests for vault merger."""

import pytest
from pathlib import Path
from agent_bridge.vault.merger import merge_source_into_project, MergeStrategy


def test_vault_only_replaces_all(tmp_path):
    """Verify PROJECT_WINS doesn't apply in VAULT_ONLY mode."""
    source = tmp_path / "source" / ".agent"
    dest = tmp_path / "dest" / ".agent"
    
    # Create source
    (source / "agents").mkdir(parents=True)
    (source / "agents" / "test.md").write_text("source content")
    
    # Create dest with existing file
    (dest / "agents").mkdir(parents=True)
    (dest / "agents" / "test.md").write_text("dest content")
    
    # Merge with VAULT_ONLY
    counts = merge_source_into_project(source, dest, MergeStrategy.VAULT_ONLY)
    
    # Should overwrite
    content = (dest / "agents" / "test.md").read_text()
    assert content == "source content"


def test_project_wins_keeps_existing(tmp_path):
    """Create file in both source and dest, verify dest unchanged."""
    source = tmp_path / "source" / ".agent"
    dest = tmp_path / "dest" / ".agent"
    
    # Create source
    (source / "agents").mkdir(parents=True)
    (source / "agents" / "test.md").write_text("source content")
    
    # Create dest with existing file
    (dest / "agents").mkdir(parents=True)
    (dest / "agents" / "test.md").write_text("dest content")
    
    # Merge with PROJECT_WINS
    counts = merge_source_into_project(source, dest, MergeStrategy.PROJECT_WINS)
    
    # Should keep dest
    content = (dest / "agents" / "test.md").read_text()
    assert content == "dest content"


def test_vault_wins_overwrites(tmp_path):
    """Create file in both, verify source wins."""
    source = tmp_path / "source" / ".agent"
    dest = tmp_path / "dest" / ".agent"
    
    # Create source
    (source / "agents").mkdir(parents=True)
    (source / "agents" / "test.md").write_text("source content")
    
    # Create dest with existing file
    (dest / "agents").mkdir(parents=True)
    (dest / "agents" / "test.md").write_text("dest content")
    
    # Merge with VAULT_WINS
    counts = merge_source_into_project(source, dest, MergeStrategy.VAULT_WINS)
    
    # Should overwrite with source
    content = (dest / "agents" / "test.md").read_text()
    assert content == "source content"


def test_merge_creates_missing_dirs(tmp_path):
    """Verify subdirs created if they don't exist."""
    source = tmp_path / "source" / ".agent"
    dest = tmp_path / "dest" / ".agent"
    
    # Create source with nested structure
    (source / "skills" / "test-skill").mkdir(parents=True)
    (source / "skills" / "test-skill" / "SKILL.md").write_text("skill content")
    
    # Dest doesn't exist
    counts = merge_source_into_project(source, dest, MergeStrategy.PROJECT_WINS)
    
    # Should create dirs
    assert (dest / "skills" / "test-skill" / "SKILL.md").exists()


def test_merge_counts_correct(tmp_path):
    """Verify returned counts dict is accurate."""
    source = tmp_path / "source" / ".agent"
    dest = tmp_path / "dest" / ".agent"
    
    # Create source with multiple items
    (source / "agents").mkdir(parents=True)
    (source / "agents" / "agent1.md").write_text("agent1")
    (source / "agents" / "agent2.md").write_text("agent2")
    
    (source / "skills" / "skill1").mkdir(parents=True)
    (source / "skills" / "skill1" / "SKILL.md").write_text("skill1")
    
    (source / "workflows").mkdir(parents=True)
    (source / "workflows" / "workflow1.md").write_text("workflow1")
    
    counts = merge_source_into_project(source, dest, MergeStrategy.PROJECT_WINS)
    
    assert counts["agents"] == 2
    assert counts["skills"] == 1
    assert counts["workflows"] == 1
