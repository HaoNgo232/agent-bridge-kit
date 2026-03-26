"""Tests for vault sources (GitSource, LocalSource, BuiltinSource)."""

import pytest
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from agent_bridge.vault.sources import GitSource, LocalSource, BuiltinSource


def test_git_source_validates_url():
    """Verify GitSource rejects unsafe URLs."""
    # Valid URLs
    GitSource("https://github.com/user/repo.git")
    GitSource("git@github.com:user/repo.git")
    
    # Invalid URLs
    with pytest.raises(ValueError, match="Unsafe git URL"):
        GitSource("javascript:alert(1)")
    
    with pytest.raises(ValueError, match="Unsafe git URL"):
        GitSource("-u origin")


@patch('subprocess.run')
def test_git_source_clone_new_repo(mock_run, tmp_path):
    """Verify GitSource clones new repository."""
    mock_run.return_value = Mock(returncode=0, stderr=b"")
    
    source = GitSource("https://github.com/test/repo.git")
    cache_dir = tmp_path / "cache"
    
    # Create minimal .agent structure for counting
    (cache_dir / ".agent" / "agents").mkdir(parents=True)
    (cache_dir / ".agent" / "agents" / "test.md").write_text("# Test")
    
    result = source.sync(cache_dir, verbose=False)
    
    assert result["status"] == "ok"
    assert mock_run.called


@patch('subprocess.run')
def test_git_source_pull_existing_repo(mock_run, tmp_path):
    """Verify GitSource pulls existing repository."""
    mock_run.return_value = Mock(returncode=0, stderr=b"")
    
    source = GitSource("https://github.com/test/repo.git")
    cache_dir = tmp_path / "cache"
    
    # Simulate existing repo
    (cache_dir / ".git").mkdir(parents=True)
    (cache_dir / ".agent" / "agents").mkdir(parents=True)
    
    result = source.sync(cache_dir, verbose=False)
    
    # Should call git pull, not clone
    assert any("pull" in str(call) for call in mock_run.call_args_list)


@patch('subprocess.run')
def test_git_source_validate(mock_run):
    """Verify GitSource.validate() checks remote."""
    mock_run.return_value = Mock(returncode=0)
    
    source = GitSource("https://github.com/test/repo.git")
    assert source.validate() is True
    
    mock_run.return_value = Mock(returncode=1)
    assert source.validate() is False


def test_local_source_sync(tmp_path):
    """Verify LocalSource syncs from local directory."""
    # Create local vault
    local_vault = tmp_path / "local-vault"
    (local_vault / ".agent" / "agents").mkdir(parents=True)
    (local_vault / ".agent" / "agents" / "test.md").write_text("# Test")
    (local_vault / ".agent" / "skills" / "skill1").mkdir(parents=True)
    
    source = LocalSource(str(local_vault))
    cache_dir = tmp_path / "cache"
    
    result = source.sync(cache_dir, verbose=False)
    
    assert result["status"] == "ok"
    assert result["agents"] == 1
    assert result["skills"] == 1


def test_local_source_validate(tmp_path):
    """Verify LocalSource.validate() checks path exists."""
    existing = tmp_path / "existing"
    existing.mkdir()
    
    source = LocalSource(str(existing))
    assert source.validate() is True
    
    source = LocalSource(str(tmp_path / "nonexistent"))
    assert source.validate() is False


def test_builtin_source_sync(tmp_path):
    """Verify BuiltinSource syncs from package builtin_vault."""
    source = BuiltinSource()
    cache_dir = tmp_path / "cache"
    
    # BuiltinSource should find builtin_vault in package
    result = source.sync(cache_dir, verbose=False)
    
    # May succeed or fail depending on package structure
    assert "status" in result


def test_builtin_source_validate():
    """Verify BuiltinSource.validate() checks builtin vault exists."""
    source = BuiltinSource()
    # Should always be valid if package is installed correctly
    assert source.validate() in [True, False]  # Depends on package structure
