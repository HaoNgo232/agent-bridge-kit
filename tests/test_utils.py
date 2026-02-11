"""Tests for utils.py functions."""

import pytest
from pathlib import Path
from agent_bridge.utils import (
    strip_frontmatter,
    extract_yaml_frontmatter,
    add_yaml_frontmatter,
    truncate_content,
    validate_path_within_project,
)


def test_strip_frontmatter():
    """Verify YAML frontmatter removed."""
    content = """---
name: test
description: test desc
---

# Body

Content here"""
    
    result = strip_frontmatter(content)
    
    assert not result.startswith("---")
    assert "# Body" in result
    assert "Content here" in result


def test_strip_frontmatter_no_frontmatter():
    """Verify content unchanged when no frontmatter."""
    content = "# Title\n\nNo frontmatter here"
    
    result = strip_frontmatter(content)
    
    assert result == content


def test_extract_yaml_frontmatter():
    """Verify dict + body returned."""
    content = """---
name: test
description: test desc
---

# Body

Content"""
    
    metadata, body = extract_yaml_frontmatter(content)
    
    assert metadata is not None
    assert metadata["name"] == "test"
    assert metadata["description"] == "test desc"
    assert "# Body" in body


def test_add_yaml_frontmatter():
    """Verify frontmatter added correctly."""
    body = "# Title\n\nContent"
    frontmatter = {"name": "test", "description": "test desc"}
    
    result = add_yaml_frontmatter(body, frontmatter)
    
    assert result.startswith("---\n")
    assert "name: test" in result
    assert "description: test desc" in result
    assert "# Title" in result


def test_truncate_content_short():
    """Verify no truncation when under limit."""
    content = "Short content"
    
    result = truncate_content(content, max_length=100)
    
    assert result == content


def test_truncate_content_long():
    """Verify truncation with suffix."""
    content = "x" * 1000
    
    result = truncate_content(content, max_length=100, suffix="...(truncated)")
    
    assert len(result) <= 100 + len("...(truncated)")
    assert result.endswith("...(truncated)")


def test_validate_path_within_project():
    """Verify True for valid, False for traversal."""
    project = Path("/home/user/project")
    
    # Valid path
    valid = project / "subdir" / "file.txt"
    assert validate_path_within_project(valid, project) is True
    
    # Traversal attempt
    invalid = project / ".." / ".." / "etc" / "passwd"
    assert validate_path_within_project(invalid, project) is False


def test_validate_path_within_project_no_project_root(tmp_path):
    """Verify works without explicit project_root."""
    # Should use cwd if not provided
    test_file = tmp_path / "test.txt"
    test_file.write_text("test")
    
    # This should not raise
    result = validate_path_within_project(test_file)
    assert isinstance(result, bool)
