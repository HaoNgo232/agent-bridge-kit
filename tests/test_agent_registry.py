"""Tests for agent registry."""

import pytest
from agent_bridge.core.agent_registry import (
    get_agent_role,
    get_primary_agents,
    get_visible_agents,
)


def test_orchestrator_exists():
    """Verify get_agent_role('orchestrator') returns valid role."""
    role = get_agent_role("orchestrator")
    
    assert role is not None
    assert role.slug == "orchestrator"
    assert role.name == "Orchestrator"


def test_orchestrator_capabilities():
    """Verify can_read=True, can_write=False, can_delegate=True."""
    role = get_agent_role("orchestrator")
    
    assert role.can_read is True
    assert role.can_write is False
    assert role.can_delegate is True


def test_frontend_specialist_is_primary():
    """Verify category == 'primary'."""
    role = get_agent_role("frontend-specialist")
    
    assert role is not None
    assert role.category == "primary"


def test_code_archaeologist_is_hidden():
    """Verify hidden == True."""
    role = get_agent_role("code-archaeologist")
    
    assert role is not None
    assert role.hidden is True


def test_get_primary_agents():
    """Verify returns exactly 3 primary agents."""
    primary = get_primary_agents()
    
    assert len(primary) == 3
    slugs = [a.slug for a in primary]
    # The actual primary agents in the registry
    assert "orchestrator" in slugs or "frontend-specialist" in slugs
    assert "backend-specialist" in slugs


def test_get_visible_agents():
    """Verify code-archaeologist is excluded."""
    visible = get_visible_agents()
    
    slugs = [a.slug for a in visible]
    assert "code-archaeologist" not in slugs
    assert "orchestrator" in slugs


def test_unknown_role_returns_none():
    """Verify get_agent_role('nonexistent') returns None."""
    role = get_agent_role("nonexistent")
    
    assert role is None
