"""Tests for sync service."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from agent_bridge.services.sync_service import run_update, _refresh_detected_ides


@patch('agent_bridge.services.sync_service._refresh_detected_ides')
@patch('agent_bridge.services.sync_service.VaultManager')
def test_run_update_syncs_vaults(mock_vm_class, mock_refresh, tmp_path):
    """Verify run_update() calls VaultManager.sync()."""
    mock_vm = Mock()
    mock_vm.sync.return_value = {"test-vault": {"status": "ok", "agents": 1}}
    mock_vm.enabled_vaults = []
    mock_vm_class.return_value = mock_vm

    target_dir = tmp_path / ".agent"
    target_dir.mkdir()

    run_update(target_dir, verbose=False)

    assert mock_vm.sync.called


@patch('agent_bridge.services.sync_service._refresh_detected_ides')
@patch('agent_bridge.services.sync_service.VaultManager')
def test_run_update_merges_to_project(mock_vm_class, mock_refresh, tmp_path):
    """Verify run_update() calls merge_to_project()."""
    mock_vm = Mock()
    mock_vm.sync.return_value = {"test-vault": {"status": "ok"}}
    mock_vm.enabled_vaults = []
    mock_vm.merge_to_project = Mock()
    mock_vm_class.return_value = mock_vm

    target_dir = tmp_path / ".agent"
    target_dir.mkdir()

    run_update(target_dir, verbose=False)

    assert mock_vm.merge_to_project.called


@patch('agent_bridge.services.sync_service.VaultManager')
def test_run_update_handles_all_failed_syncs(mock_vm_class, tmp_path, capsys):
    """Verify run_update() handles case when all syncs fail."""
    mock_vm = Mock()
    mock_vm.sync.return_value = {
        "vault1": {"status": "error: connection failed"},
        "vault2": {"status": "error: not found"}
    }
    mock_vm_class.return_value = mock_vm
    
    target_dir = tmp_path / ".agent"
    
    run_update(target_dir, verbose=True)
    
    captured = capsys.readouterr()
    assert "All vault syncs failed" in captured.out


@patch('agent_bridge.services.sync_service.VaultManager')
@patch('agent_bridge.services.sync_service._refresh_detected_ides')
def test_run_update_refreshes_ides(mock_refresh, mock_vm_class, tmp_path):
    """Verify run_update() calls _refresh_detected_ides()."""
    mock_vm = Mock()
    mock_vm.sync.return_value = {"test-vault": {"status": "ok"}}
    mock_vm.enabled_vaults = []
    mock_vm_class.return_value = mock_vm
    
    target_dir = tmp_path / ".agent"
    target_dir.mkdir()
    
    with patch('agent_bridge.services.sync_service.Path.cwd', return_value=tmp_path):
        run_update(target_dir, verbose=False)
    
    assert mock_refresh.called


@patch('agent_bridge.services.sync_service.converter_registry')
def test_refresh_detected_ides_finds_cursor(mock_registry, tmp_path):
    """Verify _refresh_detected_ides() detects .cursor/ directory."""
    # Create .cursor directory
    (tmp_path / ".cursor").mkdir()
    (tmp_path / ".agent").mkdir()

    mock_converter = Mock()
    mock_converter.format_info.output_dir = ".cursor"
    mock_converter.display_name = "Cursor"
    mock_registry.all.return_value = [mock_converter]

    _refresh_detected_ides(tmp_path, verbose=False)

    # Should call converter.convert()
    assert mock_converter.convert.called


@patch('agent_bridge.services.sync_service.converter_registry')
def test_refresh_detected_ides_skips_missing_ides(mock_registry, tmp_path):
    """Verify _refresh_detected_ides() skips IDEs without directories."""
    # No IDE directories
    (tmp_path / ".agent").mkdir()
    
    mock_converter = Mock()
    mock_converter.format_info.output_dir = ".cursor"
    mock_registry.get_all.return_value = [mock_converter]
    
    _refresh_detected_ides(tmp_path, verbose=False)
    
    # Should NOT call converter.convert()
    assert not mock_converter.convert.called
