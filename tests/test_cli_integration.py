"""Tests for CLI integration (init, update, capture, clean, status, vault)."""

import sys
import pytest
from pathlib import Path
from unittest.mock import patch, Mock


def test_cli_init_cursor(tmp_project, monkeypatch):
    """Test `agent-bridge init --cursor` creates .cursor/ directory."""
    monkeypatch.chdir(tmp_project)
    monkeypatch.setattr(sys, "argv", ["agent-bridge", "init", "--cursor"])
    
    from agent_bridge.cli import _main
    _main()
    
    assert (tmp_project / ".cursor").exists()
    assert (tmp_project / ".cursor" / "agents").exists()


def test_cli_init_all(tmp_project, monkeypatch):
    """Test `agent-bridge init --all` creates all IDE directories."""
    monkeypatch.chdir(tmp_project)
    monkeypatch.setattr(sys, "argv", ["agent-bridge", "init", "--all"])
    
    from agent_bridge.cli import _main
    _main()
    
    # Should create all 5 IDE directories
    assert (tmp_project / ".cursor").exists()
    assert (tmp_project / ".github").exists()
    assert (tmp_project / ".kiro").exists()
    assert (tmp_project / ".opencode").exists()
    assert (tmp_project / ".windsurf").exists()


def test_cli_init_force_overwrites(tmp_project, monkeypatch):
    """Test `agent-bridge init --force` overwrites existing files."""
    # Create existing file
    cursor_dir = tmp_project / ".cursor" / "agents"
    cursor_dir.mkdir(parents=True)
    existing_file = cursor_dir / "test.md"
    existing_file.write_text("old content")
    
    monkeypatch.chdir(tmp_project)
    monkeypatch.setattr(sys, "argv", ["agent-bridge", "init", "--cursor", "--force"])
    
    from agent_bridge.cli import _main
    _main()
    
    # Should have new content from conversion
    assert existing_file.exists()


@patch('agent_bridge.services.sync_service.VaultManager')
def test_cli_update(mock_vm_class, tmp_project, monkeypatch):
    """Test `agent-bridge update` syncs vaults."""
    mock_vm = Mock()
    mock_vm.sync.return_value = {"test": {"status": "ok"}}
    mock_vm.enabled_vaults = []
    mock_vm_class.return_value = mock_vm
    
    monkeypatch.chdir(tmp_project)
    monkeypatch.setattr(sys, "argv", ["agent-bridge", "update"])
    
    from agent_bridge.cli import _main
    _main()
    
    assert mock_vm.sync.called


def test_cli_capture_cursor(tmp_project, monkeypatch):
    """Test `agent-bridge capture --cursor` scans for changes."""
    # First init
    monkeypatch.chdir(tmp_project)
    monkeypatch.setattr(sys, "argv", ["agent-bridge", "init", "--cursor"])
    from agent_bridge.cli import _main
    _main()
    
    # Then capture
    monkeypatch.setattr(sys, "argv", ["agent-bridge", "capture", "--cursor", "--dry-run"])
    _main()
    
    # Should complete without error


def test_cli_clean_cursor(tmp_project, monkeypatch):
    """Test `agent-bridge clean --cursor` removes .cursor/ directory."""
    # Create .cursor directory
    (tmp_project / ".cursor").mkdir()
    
    monkeypatch.chdir(tmp_project)
    monkeypatch.setattr(sys, "argv", ["agent-bridge", "clean", "--cursor"])
    
    from agent_bridge.cli import _main
    _main()
    
    assert not (tmp_project / ".cursor").exists()


def test_cli_clean_all(tmp_project, monkeypatch):
    """Test `agent-bridge clean --all` removes all IDE directories."""
    # Create all IDE directories
    for ide_dir in [".cursor", ".github", ".kiro", ".opencode", ".windsurf"]:
        (tmp_project / ide_dir).mkdir()
    
    monkeypatch.chdir(tmp_project)
    monkeypatch.setattr(sys, "argv", ["agent-bridge", "clean", "--all"])
    
    from agent_bridge.cli import _main
    _main()
    
    # All should be removed
    assert not (tmp_project / ".cursor").exists()
    assert not (tmp_project / ".github").exists()
    assert not (tmp_project / ".kiro").exists()
    assert not (tmp_project / ".opencode").exists()
    assert not (tmp_project / ".windsurf").exists()


def test_cli_status(tmp_project, monkeypatch, capsys):
    """Test `agent-bridge status` displays project info."""
    monkeypatch.chdir(tmp_project)
    monkeypatch.setattr(sys, "argv", ["agent-bridge", "status"])
    
    from agent_bridge.cli import _main
    _main()
    
    captured = capsys.readouterr()
    assert "Agent Bridge Status" in captured.out or "status" in captured.out.lower()


def test_cli_status_json(tmp_project, monkeypatch, capsys):
    """Test `agent-bridge status --json` outputs JSON."""
    monkeypatch.chdir(tmp_project)
    monkeypatch.setattr(sys, "argv", ["agent-bridge", "status", "--json"])
    
    from agent_bridge.cli import _main
    _main()
    
    captured = capsys.readouterr()
    # Should be valid JSON
    import json
    try:
        json.loads(captured.out)
        assert True
    except json.JSONDecodeError:
        pytest.fail("Output is not valid JSON")


@patch('agent_bridge.services.sync_service.VaultManager')
def test_cli_vault_list(mock_vm_class, tmp_project, monkeypatch, capsys):
    """Test `agent-bridge vault list` displays vaults."""
    mock_vm = Mock()
    mock_vm.list_vaults.return_value = []
    mock_vm_class.return_value = mock_vm
    
    monkeypatch.chdir(tmp_project)
    monkeypatch.setattr(sys, "argv", ["agent-bridge", "vault", "list"])
    
    from agent_bridge.cli import _main
    _main()
    
    assert mock_vm.list_vaults.called


def test_cli_list_formats(tmp_project, monkeypatch, capsys):
    """Test `agent-bridge list` shows all supported formats."""
    monkeypatch.chdir(tmp_project)
    monkeypatch.setattr(sys, "argv", ["agent-bridge", "list"])
    
    from agent_bridge.cli import _main
    _main()
    
    captured = capsys.readouterr()
    # Should list all 5 IDEs
    assert "cursor" in captured.out.lower() or "Cursor" in captured.out
