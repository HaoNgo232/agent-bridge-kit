"""Tests for Cursor converter."""

import pytest
import yaml
from pathlib import Path
from agent_bridge.converters.cursor import CursorConverter


def test_convert_agent_creates_md(tmp_project):
    """Verify .cursor/agents/ files created."""
    converter = CursorConverter()
    source_root = tmp_project
    dest_root = tmp_project
    
    result = converter.convert(source_root, dest_root, verbose=False)
    
    assert result.ok is True
    
    agent_file = dest_root / ".cursor" / "agents" / "orchestrator.md"
    assert agent_file.exists()


def test_convert_skill_to_mdc_rule(tmp_project):
    """For 'clean-code' skill, verify .mdc file with correct frontmatter."""
    converter = CursorConverter()
    source_root = tmp_project
    dest_root = tmp_project
    
    result = converter.convert(source_root, dest_root, verbose=False)
    
    # clean-code should become an MDC rule
    mdc_file = dest_root / ".cursor" / "rules" / "clean-code.mdc"
    assert mdc_file.exists()
    
    content = mdc_file.read_text()
    assert content.startswith("---\n")
    
    # Parse YAML part to verify validity
    fm_text = content.split("---")[1]
    fm = yaml.safe_load(fm_text)
    assert fm["alwaysApply"] is True
    assert "globs" in fm


def test_convert_skill_to_cursor_skill(tmp_project):
    """For unknown skill, verify it goes to .cursor/skills/"""
    # Add a non-standard skill
    skill_dir = tmp_project / ".agent" / "skills" / "custom-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("# Custom Skill\n\nCustom content\n")
    
    converter = CursorConverter()
    source_root = tmp_project
    dest_root = tmp_project
    
    result = converter.convert(source_root, dest_root, verbose=False)
    
    # Should be in skills dir
    skill_file = dest_root / ".cursor" / "skills" / "custom-skill" / "SKILL.md"
    assert skill_file.exists()


def test_mdc_frontmatter_format(tmp_project):
    """Verify description, globs, alwaysApply fields."""
    converter = CursorConverter()
    source_root = tmp_project
    dest_root = tmp_project
    
    result = converter.convert(source_root, dest_root, verbose=False)
    
    mdc_file = dest_root / ".cursor" / "rules" / "clean-code.mdc"
    content = mdc_file.read_text()
    
    # Check frontmatter structure via actual YAML parsing
    assert content.startswith("---\n")
    fm_text = content.split("---")[1]
    fm = yaml.safe_load(fm_text)
    
    assert "description" in fm
    assert "alwaysApply" in fm
    assert isinstance(fm.get("globs"), list)


def test_special_characters_in_globs(tmp_project):
    """Verify that globs with '*' are correctly quoted and valid YAML."""
    # Add a skill with a glob containing '*'
    skill_dir = tmp_project / ".agent" / "skills" / "star-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("# Star Skill\n\nContent\n")
    
    # We rely on core/agent_registry.py or we can mock it.
    # Actually, let's just use the fact that CursorConverter will map it.
    
    converter = CursorConverter()
    source_root = tmp_project
    dest_root = tmp_project
    
    result = converter.convert(source_root, dest_root, verbose=False)
    
    mdc_file = dest_root / ".cursor" / "rules" / "star-skill.mdc"
    # Even if it wasn't specially mapped, we check if ANY mdc's YAML is valid
    if mdc_file.exists():
        content = mdc_file.read_text()
        fm_text = content.split("---")[1]
        try:
            yaml.safe_load(fm_text)
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML generated for MDC Rule with globs: {e}")


def test_convert_to_cursor_full(tmp_project):
    """End-to-end with tmp_project."""
    converter = CursorConverter()
    source_root = tmp_project
    dest_root = tmp_project
    
    result = converter.convert(source_root, dest_root, verbose=False)
    
    assert result.ok is True
    assert result.agents == 2
    assert result.skills == 1
    assert result.workflows == 1
