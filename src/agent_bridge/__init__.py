"""
Agent Bridge - Multi-format Agent/Skill converter for popular IDEs.

Converts agent configurations from multiple vault sources to:
- Kiro CLI (.kiro/)
- GitHub Copilot (.github/)
- Cursor AI (.cursor/)
- OpenCode IDE (.opencode/)
- Windsurf IDE (.windsurf/)
"""

__version__ = "1.0.0"

# Trigger converter auto-registration on import
from agent_bridge import converters  # noqa: F401

__all__ = [
    "cli",
    "converters",
    "core",
    "vault",
    "services",
    "utils",
]