from pathlib import Path

import yaml

from agent_bridge.copilot_conv import (
    AGENT_SUBAGENTS_MAP,
    AGENT_TOOLS_MAP,
    convert_skill_to_copilot,
    convert_to_copilot,
    generate_copilot_frontmatter,
)


def _write_agent_source(source_root: Path, file_name: str, content: str) -> None:
    agents_dir = source_root / ".agent" / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    (agents_dir / file_name).write_text(content, encoding="utf-8")


def _write_skill_source(source_root: Path, skill_dir_name: str, content: str) -> None:
    skill_dir = source_root / ".agent" / "skills" / skill_dir_name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")


def _split_frontmatter(markdown: str) -> tuple[dict, str]:
    if not markdown.startswith("---\n"):
        raise AssertionError("frontmatter start marker is missing")

    parts = markdown.split("---\n", 2)
    if len(parts) < 3:
        raise AssertionError("invalid frontmatter layout")

    frontmatter = yaml.safe_load(parts[1])
    body = parts[2].lstrip("\n")

    if not isinstance(frontmatter, dict):
        raise AssertionError("frontmatter must be a YAML object")

    return frontmatter, body


def _assert_valid_agent_frontmatter(frontmatter: dict) -> None:
    assert isinstance(frontmatter.get("name"), str) and frontmatter["name"].strip()
    assert isinstance(frontmatter.get("description"), str) and frontmatter["description"].strip()
    assert len(frontmatter["description"]) <= 500

    tools = frontmatter.get("tools")
    assert isinstance(tools, list)
    assert all(isinstance(tool, str) and tool.strip() for tool in tools)

    agents = frontmatter.get("agents")
    if agents is not None:
        assert "agent" in tools, "agents field requires 'agent' tool"
        assert isinstance(agents, list)
        assert all(isinstance(agent_name, str) and agent_name.strip() for agent_name in agents)

    handoffs = frontmatter.get("handoffs")
    if handoffs is not None:
        assert isinstance(handoffs, list)
        for handoff in handoffs:
            assert isinstance(handoff, dict)
            assert isinstance(handoff.get("label"), str) and handoff["label"].strip()
            assert isinstance(handoff.get("agent"), str) and handoff["agent"].strip()
            if "prompt" in handoff:
                assert isinstance(handoff["prompt"], str)
            if "send" in handoff:
                assert isinstance(handoff["send"], bool)


def _assert_valid_skill_frontmatter(frontmatter: dict) -> None:
    name = frontmatter.get("name")
    description = frontmatter.get("description")

    assert isinstance(name, str) and name
    assert isinstance(description, str) and description
    assert len(name) <= 64
    assert len(description) <= 1024

    assert name == name.lower()
    assert all(ch.isalnum() or ch == "-" for ch in name)


def test_generate_frontmatter_adds_agent_tool_when_subagents_enabled() -> None:
    metadata = {
        "name": "Orchestrator",
        "description": "Coordinates execution",
    }

    parsed = yaml.safe_load(generate_copilot_frontmatter("orchestrator", metadata))

    assert isinstance(parsed, dict)
    assert parsed.get("agents") == AGENT_SUBAGENTS_MAP["orchestrator"]
    assert "agent" in parsed.get("tools", [])


def test_generate_frontmatter_keeps_model_unspecified_for_handoff_flexibility() -> None:
    metadata = {
        "name": "Planner",
        "description": "Planning agent",
    }

    parsed = yaml.safe_load(generate_copilot_frontmatter("project-planner", metadata))

    assert isinstance(parsed, dict)
    for handoff in parsed.get("handoffs", []):
        assert "model" not in handoff


def test_convert_to_copilot_generates_valid_agent_and_skill_format(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    output_root = tmp_path / "output"

    _write_agent_source(
        source_root,
        "orchestrator.md",
        """
# Orchestrator

You are the coordinator agent.
""".strip(),
    )
    _write_skill_source(
        source_root,
        "Web App Testing",
        """
Description: Guide for browser test workflows.

# Web App Testing
Run tests with Playwright.
""".strip(),
    )

    stats = convert_to_copilot(source_root, output_root, verbose=False)
    assert stats["errors"] == []
    assert stats["agents"] == 1
    assert stats["skills"] == 1

    agent_output = output_root / ".github" / "agents" / "orchestrator.md"
    skill_output = output_root / ".github" / "skills" / "Web App Testing" / "SKILL.md"
    assert agent_output.exists()
    assert skill_output.exists()

    agent_frontmatter, agent_body = _split_frontmatter(agent_output.read_text(encoding="utf-8"))
    _assert_valid_agent_frontmatter(agent_frontmatter)
    assert "coordinator agent" in agent_body
    assert "applyTo" not in agent_output.read_text(encoding="utf-8")

    skill_frontmatter, _ = _split_frontmatter(skill_output.read_text(encoding="utf-8"))
    _assert_valid_skill_frontmatter(skill_frontmatter)


def test_convert_skill_to_copilot_normalizes_name_and_truncates_description(tmp_path: Path) -> None:
    source_skill_dir = tmp_path / "source-skill" / "My Skill !!! With___Invalid***Chars And A Very Very Very Long Name"
    source_skill_dir.mkdir(parents=True)

    long_description = "Description: " + ("x" * 1200)
    (source_skill_dir / "SKILL.md").write_text(long_description, encoding="utf-8")

    dest_root = tmp_path / "dest-skills"
    ok = convert_skill_to_copilot(source_skill_dir, dest_root)
    assert ok is True

    generated_file = dest_root / source_skill_dir.name / "SKILL.md"
    assert generated_file.exists()

    frontmatter, _ = _split_frontmatter(generated_file.read_text(encoding="utf-8"))
    _assert_valid_skill_frontmatter(frontmatter)


def test_default_tools_for_unknown_agent_are_stable() -> None:
    parsed = yaml.safe_load(
        generate_copilot_frontmatter(
            "unknown-role",
            {"name": "Unknown", "description": "Unknown role"},
        )
    )

    assert isinstance(parsed, dict)
    assert parsed.get("tools") == ["search/codebase", "edit/editFiles", "web/fetch"]


def test_agent_tools_map_contains_only_string_lists() -> None:
    for agent_slug, tools in AGENT_TOOLS_MAP.items():
        assert isinstance(agent_slug, str) and agent_slug
        assert isinstance(tools, list)
        assert all(isinstance(tool, str) and tool for tool in tools)
