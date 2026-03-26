"""Tests for Windsurf converter."""

import pytest
from pathlib import Path
from agent_bridge.converters.windsurf import WindsurfConverter


def test_convert_creates_rules(tmp_project):
    """Verify .windsurf/rules/ files created."""
    converter = WindsurfConverter()
    source_root = tmp_project
    dest_root = tmp_project
    
    result = converter.convert(source_root, dest_root, verbose=False)
    
    assert result.ok is True
    rules_dir = dest_root / ".windsurf" / "rules"
    assert rules_dir.exists()
    assert len(list(rules_dir.glob("*.md"))) > 0


def test_rule_frontmatter_format(tmp_project):
    """Verify Windsurf rule has name, activation mode, description header."""
    converter = WindsurfConverter()
    source_root = tmp_project
    dest_root = tmp_project

    result = converter.convert(source_root, dest_root, verbose=False)

    # Check any rule file
    rule_files = list((dest_root / ".windsurf" / "rules").glob("*.md"))
    assert len(rule_files) > 0

    content = rule_files[0].read_text()
    # Windsurf uses markdown headers, not YAML frontmatter
    assert "**Activation:**" in content or content.startswith("# ")



def test_truncation_for_long_content(tmp_project):
    """Verify Windsurf truncates content exceeding 12000 chars."""
    # Create a very long skill
    long_skill_dir = tmp_project / ".agent" / "skills" / "long-skill"
    long_skill_dir.mkdir()
    long_content = "# Long Skill\n\n" + ("x" * 15000)
    (long_skill_dir / "SKILL.md").write_text(long_content)
    
    converter = WindsurfConverter()
    source_root = tmp_project
    dest_root = tmp_project
    
    result = converter.convert(source_root, dest_root, verbose=False)
    
    rule_file = dest_root / ".windsurf" / "rules" / "long-skill.md"
    assert rule_file.exists()
    
    content = rule_file.read_text()
    # Should be truncated to 12000 chars
    assert len(content) == 12000
    assert "(truncated to fit Windsurf rule limit)" in content


def test_legacy_windsurfrules_created(tmp_project):
    """Verify .windsurfrules root file is created."""
    converter = WindsurfConverter()
    source_root = tmp_project
    dest_root = tmp_project
    
    result = converter.convert(source_root, dest_root, verbose=False)
    
    legacy_file = dest_root / ".windsurfrules"
    assert legacy_file.exists()


def test_convert_to_windsurf_full(tmp_project):
    """End-to-end with tmp_project."""
    converter = WindsurfConverter()
    source_root = tmp_project
    dest_root = tmp_project
    
    result = converter.convert(source_root, dest_root, verbose=False)
    
    assert result.ok is True
    # Windsurf converts agents + skills + workflows to rules
    assert result.rules > 0


def test_clean_removes_windsurf_dir(tmp_project):
    """Verify clean() removes .windsurf/ directory and .windsurfrules."""
    converter = WindsurfConverter()
    source_root = tmp_project
    dest_root = tmp_project
    
    # Convert first
    converter.convert(source_root, dest_root, verbose=False)
    assert (dest_root / ".windsurf").exists()
    assert (dest_root / ".windsurfrules").exists()
    
    # Clean
    result = converter.clean(dest_root)
    assert result is True
    assert not (dest_root / ".windsurf").exists()
    assert not (dest_root / ".windsurfrules").exists()
