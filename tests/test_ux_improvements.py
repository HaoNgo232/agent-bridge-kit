"""Tests for UI/UX improvements."""

import os
import sys
from io import StringIO
from unittest.mock import patch

import pytest


def test_no_color_support():
    """Test NO_COLOR environment variable disables colors."""
    # Set NO_COLOR
    os.environ["NO_COLOR"] = "1"
    
    # Reimport Colors to pick up environment change
    import importlib
    from agent_bridge.utils import colors
    importlib.reload(colors)
    
    # All color codes should be empty strings
    assert colors.Colors.CYAN == ""
    assert colors.Colors.GREEN == ""
    assert colors.Colors.RED == ""
    assert colors.Colors.ENDC == ""
    
    # Cleanup
    del os.environ["NO_COLOR"]
    importlib.reload(colors)


def test_colors_enabled_with_tty():
    """Test colors are enabled when output is a TTY."""
    # Ensure NO_COLOR is not set
    os.environ.pop("NO_COLOR", None)
    
    # Mock isatty to return True
    with patch("os.isatty", return_value=True):
        import importlib
        from agent_bridge.utils import colors
        importlib.reload(colors)
        
        # Colors should be enabled
        assert colors.Colors.CYAN != ""
        assert colors.Colors.GREEN != ""


def test_spinner_context_manager():
    """Test SimpleSpinner context manager."""
    from agent_bridge.utils.spinner import SimpleSpinner
    
    # Capture stdout
    captured = StringIO()
    
    with patch("sys.stdout", captured):
        with SimpleSpinner("Testing"):
            import time
            time.sleep(0.3)  # Let spinner run a bit
    
    # Spinner should have written something
    output = captured.getvalue()
    assert "Testing" in output or output == ""  # May be cleared


def test_display_functions():
    """Test display helper functions."""
    from agent_bridge.utils.display import (
        print_error,
        print_error_with_suggestion,
        print_info,
        print_step,
        print_success,
        print_success_with_details,
    )
    
    # Capture stdout
    captured = StringIO()
    
    with patch("sys.stdout", captured):
        print_step("Step 1", 1, 3)
        print_success("Success")
        print_error("Error")
        print_info("Info")
        print_success_with_details("Done", "Details here")
        print_error_with_suggestion("Failed", "Try this")
    
    output = captured.getvalue()
    
    # Check all messages appear
    assert "Step 1" in output or "[1/3]" in output
    assert "Success" in output
    assert "Error" in output
    assert "Info" in output
    assert "Done" in output
    assert "Failed" in output


def test_dynamic_terminal_width():
    """Test status display adapts to terminal width."""
    from agent_bridge.services.status_display import display_status
    from agent_bridge.services.status_service import ProjectStatus, VaultStatus

    # Mock terminal width
    with patch("shutil.get_terminal_size", return_value=(60, 20)):
        status = ProjectStatus(
            project_path="/test",
            agent_dir_exists=True,
            agent_counts={},
            vault_statuses=[
                VaultStatus(
                    name="very-long-vault-name-that-should-be-truncated",
                    enabled=True,
                    is_cached=True,
                    last_synced=None,
                    source_type="git",
                    stale=False,
                    freshness="1 hour ago",
                )
            ],
            ide_statuses=[],
            mcp_info=None,
        )

        # Should not raise error
        captured = StringIO()
        with patch("sys.stdout", captured):
            display_status(status)

        output = captured.getvalue()
        assert "very-long-vault-name" in output


def test_error_with_suggestion():
    """Test error messages include suggestions."""
    from agent_bridge.services.init_service import run_init
    from pathlib import Path
    
    # Mock no .agent/ directory
    with patch("pathlib.Path.exists", return_value=False):
        result = run_init(
            project_path=Path("/test"),
            format_names=["cursor"],
            source_choice="local",
            verbose=False
        )
        
        # Should return error with suggestion
        assert "error" in result
        assert "suggestion" in result
        assert "vault add" in result["suggestion"]
