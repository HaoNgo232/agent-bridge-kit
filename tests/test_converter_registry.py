"""Tests for converter registry."""

import pytest
from agent_bridge.core.converter import converter_registry


def test_all_converters_registered():
    """Verify 5 converters exist."""
    names = converter_registry.names()
    
    assert len(names) == 5
    assert "copilot" in names
    assert "cursor" in names
    assert "kiro" in names
    assert "opencode" in names
    assert "windsurf" in names


def test_get_converter_by_name():
    """Verify registry.get('cursor') returns CursorConverter."""
    converter = converter_registry.get("cursor")
    
    assert converter is not None
    assert converter.format_info.name == "cursor"


def test_get_converter_case_insensitive():
    """Verify registry.get('Cursor') works."""
    converter = converter_registry.get("Cursor")
    
    assert converter is not None
    assert converter.format_info.name == "cursor"


def test_converter_has_format_info():
    """Verify each converter has name, display_name, output_dir."""
    for converter in converter_registry.all():
        info = converter.format_info
        
        assert info.name
        assert info.display_name
        assert info.output_dir
        assert info.status in ["Stable", "Beta", "Experimental", "beta", "stable"]


def test_converter_names_list():
    """Verify registry.names() returns all 5."""
    names = converter_registry.names()
    
    assert isinstance(names, list)
    assert len(names) == 5


def test_get_unknown_converter_returns_none():
    """Verify unknown converter returns None."""
    converter = converter_registry.get("nonexistent")
    
    assert converter is None
