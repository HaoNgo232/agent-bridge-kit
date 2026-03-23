# Agent Bridge

> Universal converter for AI agent knowledge with bidirectional sync between `.agent/` format and multiple IDE configurations.

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](../LICENSE)
[![Tests: 137 passing](https://img.shields.io/badge/tests-137%20passing-brightgreen.svg)](#testing)

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Key Modules](#key-modules)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Supported IDEs](#supported-ides)
- [Commands Reference](#commands-reference)
- [Bidirectional Sync Workflow](#bidirectional-sync-workflow)
- [Knowledge Vaults](#knowledge-vaults)
- [MCP Integration](#mcp-integration)
- [Plugin System](#plugin-system)
- [Configuration](#configuration)
- [Development Guide](#development-guide)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Credits](#credits)
- [License](#license)

---

## Overview

**Agent Bridge** solves a critical problem in multi-IDE AI development: each IDE (Cursor, Copilot, Kiro, OpenCode, Windsurf) uses its own format for AI agent configurations. Maintaining agent knowledge across multiple IDEs means duplicating and manually syncing configuration files.

Agent Bridge provides a **single source of truth** (`.agent/` directory) and automatically converts it to each IDE's native format. It also supports **reverse conversion** — capturing changes made in IDE configs back to `.agent/`, enabling true bidirectional sync.

### Key Features

- **Forward Conversion**: `.agent/` → IDE-specific formats (5 IDEs supported)
- **Reverse Capture**: IDE configs → `.agent/` (Cursor, Kiro, Copilot)
- **Snapshot Management**: Save, restore, and version `.agent/` states
- **Knowledge Vaults**: Register git repos or local directories as agent knowledge sources
- **MCP Integration**: Model Context Protocol configuration distribution
- **Plugin System**: Declarative external skill installation via `plugins.json`
- **Interactive TUI**: Questionary-based setup wizard
- **Conflict Resolution**: `ide_wins` or `agent_wins` strategies

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                     CLI (cli.py)                     │
│              Thin dispatcher / argparse              │
├──────────┬──────────┬───────────┬───────────────────┤
│ TUI      │ Services │ Vault     │ Utils             │
│ (tui.py) │          │           │                   │
│          │ init     │ manager   │ colors, display   │
│          │ sync     │ merger    │ filesystem, mcp   │
│          │ capture  │ sources   │                   │
│          │ snapshot │           │                   │
│          │ status   │           │                   │
├──────────┴──────────┴───────────┴───────────────────┤
│                   Core Layer                         │
│  types.py │ agent_registry.py │ converter.py        │
│  frontmatter.py │ plugins.py                        │
├─────────────────────────────────────────────────────┤
│                  Converters                           │
│  cursor.py  │ copilot.py │ kiro.py                  │
│  opencode.py │ windsurf.py                          │
│  _cursor_impl.py │ _copilot_impl.py │ _kiro_impl.py│
│  _opencode_impl.py │ _windsurf_impl.py              │
└─────────────────────────────────────────────────────┘
```

### Design Decisions

1. **Self-Registering Converters**: Each converter registers itself with the `ConverterRegistry` on import. Adding a new IDE requires zero changes to services or CLI — just create two files (`converters/my_ide.py` + `converters/_my_ide_impl.py`).

2. **Central Agent Registry**: `core/agent_registry.py` is the single source of truth for agent roles and capabilities. All converters derive IDE-specific configurations from this registry.

3. **Service Layer Separation**: Business logic lives in `services/`, completely decoupled from CLI parsing. This enables testing without simulating CLI invocations.

4. **Strategy Pattern for Vaults**: `vault/sources.py` implements `GitSource`, `LocalSource`, and `BuiltinSource`, each knowing how to sync itself.

5. **Shared Frontmatter Module**: `core/frontmatter.py` provides unified YAML frontmatter parsing across all converters, eliminating duplicate regex patterns.

---

## Tech Stack

| Component      | Technology       | Purpose                      |
| -------------- | ---------------- | ---------------------------- |
| Language       | Python 3.8+      | Cross-platform compatibility |
| CLI Framework  | argparse         | Lightweight argument parsing |
| Interactive UI | questionary 2.0+ | Checkbox/select prompts      |
| Rich Output    | rich 13.0+       | Colored terminal output      |
| Config Parsing | PyYAML           | YAML frontmatter handling    |
| Linting        | Ruff 0.1+        | Fast Python linter/formatter |
| Type Checking  | mypy 1.0+        | Static type analysis         |
| Testing        | pytest 8.3+      | Test framework               |

---

## Key Modules

### Core (`src/agent_bridge/core/`)

| File                | Purpose                                                                                                                           |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `types.py`          | Shared data structures: `AgentRole`, `ConversionResult`, `CapturedFile`, `SnapshotInfo`, `IDEFormat`, `CaptureStatus` enum        |
| `agent_registry.py` | Central agent role definitions with capabilities (read/write/execute/search), allowed commands, paths, subagents, handoff targets |
| `converter.py`      | `BaseConverter` ABC and `ConverterRegistry` — the extension point for new IDEs                                                    |
| `frontmatter.py`    | `FrontmatterParser` for YAML/MDC frontmatter extraction, generation, and stripping                                                |
| `plugins.py`        | Declarative external skill plugin system — reads `.agent/plugins.json`, installs prerequisites, runs IDE-specific commands        |

### Converters (`src/agent_bridge/converters/`)

Each converter consists of a public module (e.g., `cursor.py`) containing the `BaseConverter` subclass, and a private implementation module (e.g., `_cursor_impl.py`) with conversion logic.

| IDE            | Public Module | Impl Module         | Output Directory | Capture Support |
| -------------- | ------------- | ------------------- | ---------------- | --------------- |
| Cursor AI      | `cursor.py`   | `_cursor_impl.py`   | `.cursor/`       | Yes             |
| GitHub Copilot | `copilot.py`  | `_copilot_impl.py`  | `.github/`       | Yes             |
| Kiro CLI       | `kiro.py`     | `_kiro_impl.py`     | `.kiro/`         | Yes             |
| OpenCode       | `opencode.py` | `_opencode_impl.py` | `.opencode/`     | No              |
| Windsurf       | `windsurf.py` | `_windsurf_impl.py` | `.windsurf/`     | No              |

### Services (`src/agent_bridge/services/`)

| File                  | Purpose                                                                                  |
| --------------------- | ---------------------------------------------------------------------------------------- |
| `init_service.py`     | `run_init()` — prepare `.agent/`, run converters, install MCP, write `.bridge-meta.json` |
| `sync_service.py`     | `run_update()` — sync vaults, merge into project, auto-refresh detected IDE configs      |
| `capture_service.py`  | `scan_for_captures()` / `execute_capture()` — reverse-sync IDE changes back to `.agent/` |
| `snapshot_service.py` | CRUD operations for `.agent/` snapshots with manifest tracking                           |
| `status_service.py`   | `collect_status()` — gather project state data                                           |
| `status_display.py`   | `display_status()` — formatted terminal output for status                                |

### Vault (`src/agent_bridge/vault/`)

| File         | Purpose                                                                                  |
| ------------ | ---------------------------------------------------------------------------------------- |
| `manager.py` | `VaultManager` — registry, sync orchestration, merge coordination                        |
| `sources.py` | `GitSource`, `LocalSource`, `BuiltinSource` — strategy pattern                           |
| `merger.py`  | `merge_source_into_project()` with `PROJECT_WINS`, `VAULT_WINS`, `VAULT_ONLY` strategies |

---

## Installation

### From GitHub (recommended)

```bash
pipx install git+https://github.com/HaoNgo232/agent-bridge
```

### From Source (development)

```bash
git clone https://github.com/HaoNgo232/agent-bridge.git
cd agent-bridge
pip install -e ".[dev]"
```

### Quick Setup Script

```bash
make setup  # Checks environment, installs deps, runs lint
```

### Requirements

- Python 3.8 or higher
- Git (for vault sync)
- Node.js/npm (optional, for external skill plugins)

---

## Quick Start

```bash
cd your-project

# Interactive setup (recommended)
agent-bridge init

# Or specify IDE directly
agent-bridge init --cursor
agent-bridge init --kiro
agent-bridge init --all

# Check project status
agent-bridge status

# Pull latest knowledge and refresh configs
agent-bridge update
```

---

## Supported IDEs

| IDE            | Output Directory | Format                           | Status | Capture |
| -------------- | ---------------- | -------------------------------- | ------ | ------- |
| Cursor AI      | `.cursor/`       | Markdown + MDC rules             | Beta   | Yes     |
| GitHub Copilot | `.github/`       | YAML frontmatter markdown        | Beta   | Yes     |
| Kiro CLI       | `.kiro/`         | JSON agents + markdown prompts   | Beta   | Yes     |
| OpenCode       | `.opencode/`     | YAML frontmatter markdown + JSON | Beta   | No      |
| Windsurf       | `.windsurf/`     | Activation-mode markdown         | Beta   | No      |

### Format Details

**Cursor**: Agents go to `.cursor/agents/*.md` with name/description frontmatter. Skills become either MDC rules (`.cursor/rules/*.mdc` with `alwaysApply`/`globs` frontmatter) or slash-command skills (`.cursor/skills/*/SKILL.md`). Workflows become skills.

**Copilot**: Agents get full YAML frontmatter (name, description, tools, agents, handoffs). Skills go to `.github/skills/*/SKILL.md`. Workflows become `.github/prompts/*.prompt.md`. Rules become `.github/instructions/*.instructions.md`.

**Kiro**: Agents become JSON files with tools, allowedTools, toolsSettings, hooks, and resources. Skills are copied directly. Workflows become prompts with Kiro template syntax. Rules go to steering with `inclusion: always` frontmatter.

**OpenCode**: Agents get mode (primary/subagent), tools, and permission frontmatter. Workflows become commands. Skills are copied directly.

**Windsurf**: Everything becomes rules with activation modes (Always On, Glob, Model Decision, Manual). Workflows get step extraction. A legacy `.windsurfrules` root file is also generated.

---

## Commands Reference

### `agent-bridge init`

Set up agent configs for your project.

```bash
agent-bridge init                    # Interactive TUI
agent-bridge init --cursor           # Cursor only
agent-bridge init --kiro --copilot   # Multiple IDEs
agent-bridge init --all              # All IDEs
agent-bridge init --from my-snapshot # From saved snapshot
agent-bridge init --force            # Force overwrite
agent-bridge init --no-interactive   # Skip TUI
```

### `agent-bridge update`

Pull latest knowledge from vaults and refresh existing IDE configs.

```bash
agent-bridge update
agent-bridge update --target .agent
```

### `agent-bridge capture`

Reverse-sync: capture changes from IDE configs back to `.agent/`.

```bash
agent-bridge capture                              # Interactive
agent-bridge capture --cursor                     # Cursor only
agent-bridge capture --all                        # All IDEs
agent-bridge capture --strategy ide_wins          # IDE changes win
agent-bridge capture --strategy agent_wins        # Skip unchanged
agent-bridge capture --dry-run                    # Preview only
```

### `agent-bridge snapshot`

Save and manage `.agent/` snapshots.

```bash
agent-bridge snapshot save my-snapshot -d "Description"
agent-bridge snapshot save tagged -t "framework:flutter" -t "lang:dart"
agent-bridge snapshot list
agent-bridge snapshot info my-snapshot
agent-bridge snapshot restore my-snapshot
agent-bridge snapshot delete my-snapshot
```

### `agent-bridge status`

Show project dashboard.

```bash
agent-bridge status          # Formatted output
agent-bridge status --json   # Machine-readable JSON
```

### `agent-bridge vault`

Manage knowledge vaults.

```bash
agent-bridge vault list
agent-bridge vault add my-team git@github.com:myorg/ai-agents.git
agent-bridge vault add local-agents /path/to/agents -p 50
agent-bridge vault remove my-team
agent-bridge vault sync
agent-bridge vault sync --name my-team
```

### `agent-bridge mcp`

Install MCP configuration.

```bash
agent-bridge mcp --all
agent-bridge mcp --cursor --kiro
agent-bridge mcp --force
```

### `agent-bridge clean`

Remove generated IDE configs.

```bash
agent-bridge clean --all
agent-bridge clean --cursor
```

### `agent-bridge list`

List all supported IDE formats.

### Direct Conversion

```bash
agent-bridge cursor --source .agent
agent-bridge kiro --source .agent
agent-bridge copilot
```

---

## Bidirectional Sync Workflow

```bash
# 1. Initialize IDE configs from .agent/
agent-bridge init --cursor

# 2. Work in Cursor IDE, make changes to agent files
#    ... edit .cursor/agents/orchestrator.md ...

# 3. Capture changes back to .agent/
agent-bridge capture --ide cursor

# 4. Save a snapshot before major changes
agent-bridge snapshot save "before-refactor" -d "Stable state"

# 5. Make experimental changes
#    ... edit .agent/ files ...

# 6. Restore if needed
agent-bridge snapshot restore "before-refactor"

# 7. Push to another IDE
agent-bridge init --kiro
```

### How Bridge Meta Works

When `agent-bridge init` runs, it writes `.agent/.bridge-meta.json` containing:

- `generated_at`: Timestamp of generation
- `generated_for`: List of IDE names
- `file_map`: Mapping of IDE file paths → `.agent/` file paths

The capture service uses this metadata to determine file status:

- **new**: File not in `file_map` (user-created in IDE)
- **modified**: File in `file_map` with mtime > `generated_at`
- **unchanged**: File in `file_map`, not modified since generation

---

## Knowledge Vaults

A vault is any directory (git repo or local path) containing an `.agent/` structure:

```
.agent/
├── agents/          # Agent personality files (*.md)
├── skills/          # Skill directories with SKILL.md
├── workflows/       # Workflow templates (*.md)
├── rules/           # Rule files (*.md)
├── mcp_config.json  # MCP server configuration
└── plugins.json     # External plugin declarations
```

### Built-in Vault

Agent Bridge ships with a minimal built-in starter vault that works offline with zero external dependencies. It has the lowest priority (999) and acts as a fallback.

### Vault Priority

When multiple vaults are registered, files are merged with:

1. **Project-local files** take highest priority
2. **Vaults ordered by priority** (lower number = higher priority)
3. Merge strategy configurable: `PROJECT_WINS`, `VAULT_WINS`, `VAULT_ONLY`

### Vault Storage

Vaults are stored in `~/.config/agent-bridge/`:

- `vaults.json` — vault registry
- `cache/<name>/` — cached vault content
- `snapshots/<name>/` — saved snapshots

---

## MCP Integration

Agent Bridge distributes MCP (Model Context Protocol) configuration from `.agent/mcp_config.json` to each IDE's expected location with format transformation:

| IDE      | MCP Output Path                       | Key Format              |
| -------- | ------------------------------------- | ----------------------- |
| Copilot  | `.vscode/mcp.json`                    | `{"servers": {...}}`    |
| Cursor   | `.cursor/mcp.json`                    | `{"mcpServers": {...}}` |
| Kiro     | `.kiro/settings/mcp.json`             | `{"mcpServers": {...}}` |
| OpenCode | Embedded in `.opencode/opencode.json` | Custom format           |
| Windsurf | `.windsurf/mcp_config.json`           | `{"mcpServers": {...}}` |

Source format (`.agent/mcp_config.json`):

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"]
    }
  }
}
```

---

## Plugin System

External skills can be declared in `.agent/plugins.json`:

```json
{
  "plugins": [
    {
      "name": "ui-ux-pro-max",
      "description": "UI/UX design skill pack",
      "homepage": "https://github.com/nextlevelbuilder/ui-ux-pro-max-skill",
      "install": {
        "requires": "npm",
        "package": "uipro-cli",
        "global": true,
        "commands": {
          "kiro": "uipro init --ai kiro",
          "cursor": "uipro init --ai cursor"
        }
      },
      "condition": {
        "file_exists": ".agent/workflows/ui-ux-pro-max.md"
      },
      "prompt_before_install": true
    }
  ]
}
```

Plugins are:

- **Declarative**: Defined in JSON, not Python code
- **Per-IDE**: Each IDE can have its own install command
- **Conditional**: Only install if trigger condition is met
- **Safe**: Asks user before installing global packages (unless `--force`)

---

## Configuration

### Environment

No environment variables required for basic usage. MCP servers may require their own environment variables (e.g., `GITHUB_TOKEN`).

### Project Structure

```
your-project/
├── .agent/                    # Source of truth
│   ├── agents/*.md            # Agent definitions
│   ├── skills/*/SKILL.md      # Skill packs
│   ├── workflows/*.md         # Workflow templates
│   ├── rules/*.md             # Global rules
│   ├── mcp_config.json        # MCP servers
│   ├── plugins.json           # External plugins
│   └── .bridge-meta.json      # Generated tracking file
├── .cursor/                   # Generated Cursor config
├── .github/                   # Generated Copilot config
├── .kiro/                     # Generated Kiro config
├── .opencode/                 # Generated OpenCode config
└── .windsurf/                 # Generated Windsurf config
```

### Global Config

```
~/.config/agent-bridge/
├── vaults.json                # Vault registry
├── cache/                     # Cached vault content
│   ├── builtin-starter/
│   └── my-team/
└── snapshots/                 # Saved snapshots
    ├── before-refactor/
    └── stable-v1/
```

---

## Development Guide

### Setup

```bash
git clone https://github.com/HaoNgo232/agent-bridge.git
cd agent-bridge
make setup          # Or manually:
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Code Style

- **Linter**: Ruff with pycodestyle, pyflakes, isort, flake8-bugbear, pyupgrade
- **Line length**: 120 characters
- **Target**: Python 3.8
- **Type hints**: Optional but encouraged

```bash
make lint           # Run linter
make format         # Auto-fix and format
make check          # Full check
make clean          # Remove cache files
```

### Adding a New IDE Converter

1. Create `src/agent_bridge/converters/my_ide.py`:

```python
from agent_bridge.core.converter import BaseConverter, converter_registry
from agent_bridge.core.types import ConversionResult, IDEFormat

class MyIDEConverter(BaseConverter):
    @property
    def format_info(self) -> IDEFormat:
        return IDEFormat(name="myide", display_name="My IDE", output_dir=".myide")

    def convert(self, source_root, dest_root, verbose=True, force=False):
        # ... conversion logic ...
        return ConversionResult(agents=N, skills=N)

    def install_mcp(self, source_root, dest_root, force=False):
        from agent_bridge.utils import install_mcp_for_ide
        return install_mcp_for_ide(source_root, dest_root, "myide")

    def clean(self, project_path):
        # ... cleanup logic ...
        return True

converter_registry.register(MyIDEConverter)
```

2. Create `src/agent_bridge/converters/_my_ide_impl.py` with conversion functions.

3. Add import to `src/agent_bridge/converters/__init__.py`.

4. **Zero changes** needed in CLI, services, or utils.

### Pre-commit Hook

```bash
ln -s ../../scripts/pre-commit.sh .git/hooks/pre-commit
```

---

## Testing

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test suites
pytest tests/test_capture_service.py
pytest tests/test_snapshot_service.py
pytest tests/test_roundtrip.py
pytest tests/test_plugins.py
pytest tests/test_status_service.py

# Run tests matching a pattern
pytest tests/ -k "roundtrip"

# Current status: 137/137 tests passing
```

### Test Structure

| Test File                    | Coverage                               |
| ---------------------------- | -------------------------------------- |
| `test_agent_registry.py`     | Central agent role registry validation |
| `test_capture_service.py`    | Reverse-sync scanning and execution    |
| `test_cli_snapshot.py`       | CLI snapshot command integration       |
| `test_converter_registry.py` | Converter registration and lookup      |
| `test_converters.py`         | Copilot converter details              |
| `test_copilot_converter.py`  | Copilot end-to-end conversion          |
| `test_cursor_converter.py`   | Cursor end-to-end conversion           |
| `test_init_service.py`       | Bridge-meta delegation tests           |
| `test_kiro_converter.py`     | Kiro end-to-end conversion             |
| `test_kiro_reverse_edge.py`  | Kiro reverse edge cases                |
| `test_mcp_transform.py`      | MCP format transformation              |
| `test_merger.py`             | Vault merge strategies                 |
| `test_plugins.py`            | Plugin system loading and execution    |
| `test_reverse_copilot.py`    | Copilot reverse conversion             |
| `test_reverse_cursor.py`     | Cursor reverse conversion              |
| `test_reverse_kiro.py`       | Kiro reverse conversion                |
| `test_roundtrip.py`          | Forward → reverse body preservation    |
| `test_snapshot_service.py`   | Snapshot CRUD operations               |
| `test_status_service.py`     | Status collection and display          |
| `test_utils.py`              | Utility function tests                 |

---

## Troubleshooting

### "No .agent/ directory available"

Your project doesn't have a `.agent/` directory. Either:

- Run `agent-bridge init` with the `vault` source option to bootstrap from a vault
- Create `.agent/agents/` and `.agent/skills/` manually
- Use `agent-bridge init --from <snapshot>` if you have a saved snapshot

### "No vaults registered"

Run `agent-bridge vault add` to register a knowledge source:

```bash
agent-bridge vault add my-team https://github.com/myorg/ai-agents.git
agent-bridge vault sync
```

### Capture shows all files as "new"

This happens when `.agent/.bridge-meta.json` is missing or outdated. Re-run `agent-bridge init` to regenerate the tracking file, then capture will correctly detect modifications.

### MCP config not working in VS Code/Copilot

VS Code expects MCP servers under the `"servers"` key, not `"mcpServers"`. Agent Bridge handles this transformation automatically. Verify `.vscode/mcp.json` contains `{"servers": {...}}`.

### Plugin installation fails

1. Ensure the required package manager (npm/pip/cargo) is installed
2. Check network connectivity for global package installs
3. Try manual installation: `npm install -g <package-name>`
4. Use `--force` flag to skip confirmation prompts

### Stale IDE configs

Run `agent-bridge status` to check staleness, then `agent-bridge update` to refresh.

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make changes following the code style guidelines
4. Add tests for new functionality
5. Run `make check` to verify lint passes
6. Run `pytest tests/` to verify all tests pass
7. Submit a pull request

---

## Credits

- [Antigravity Kit](https://github.com/vudovn/antigravity-kit) by Vudovn (MIT License)
- [UI-UX Pro Max](https://github.com/nextlevelbuilder) by NextLevelBuilder (MIT License)

---

## License

MIT © HaoNgo232
