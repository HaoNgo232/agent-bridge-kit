# Refactor Baseline — Agent Bridge v2.0.0

Date: 2026-03-23

## Test Metrics

| Metric | Before | After |
|--------|--------|-------|
| Total tests | 129 | 137 |
| Passing | 129 | 137 |
| Failing | 0 | 0 |

## Changes Completed

### Priority 2 — Shared Frontmatter Module
- `core/frontmatter.py` already existed; migrated remaining converters to use it
- `_cursor_impl.py`: `extract_metadata_from_content()` now uses `FrontmatterParser.extract()`
- `_kiro_impl.py`: `extract_agent_metadata()` now uses `FrontmatterParser.extract()` and `FrontmatterParser.strip()`
- `_copilot_impl.py`: was already using `FrontmatterParser` ✓

### Priority 4 — CaptureStatus Enum
- `core/types.py`: `CapturedFile.status` changed from `str` to `CaptureStatus`
- `_cursor_impl.py`, `_kiro_impl.py`: migrated `status="new"` → `CaptureStatus.NEW`
- `_copilot_impl.py`: was already using `CaptureStatus` ✓
- `capture_service.py`: `_determine_status()` returns `CaptureStatus`, comparison updated
- `tui.py`: uses `cf.status.value` for display
- All test files updated to use `CaptureStatus.NEW` etc.

### Priority 1 — Converter Interface Expansion (OCP Fix)
- `core/converter.py`: Added 5 new methods to `BaseConverter`:
  - `apply_reverse_capture()` — default returns `False`
  - `build_bridge_meta_map()` — default returns `{}`
  - `supports_capture` property — default `False`
  - `mcp_output_path` property — default `None`
  - `transform_mcp_config()` — default no-op
- `cursor.py`: Implements all new methods; `supports_capture=True`
- `kiro.py`: Implements all new methods; `supports_capture=True`
- `copilot.py`: Implements all new methods; `supports_capture=True`
- `opencode.py`: Adds `mcp_output_path`; no capture support
- `windsurf.py`: Adds `mcp_output_path`; no capture support
- `capture_service.py`: `_get_apply_reverse()` now uses `converter_registry` — **no hardcoded dispatch**
- `init_service.py`: `_write_bridge_meta()` reduced from 80+ lines to ~15 lines via delegation
- `utils/mcp.py`: `install_mcp_for_ide()` and `_transform_mcp_config()` use converter registry

### Priority 3 — utils.py Split
- Already completed in prior work: `utils/` package with `colors.py`, `display.py`, `filesystem.py`, `mcp.py`
- `utils/__init__.py` maintains full backward compatibility

### Priority 5 — Consolidate Agent Relationships
- `core/types.py`: `AgentRole` gains `subagents: List[str]` and `handoff_targets: List[str]`
- `core/agent_registry.py`: Populated `subagents`/`handoff_targets` for orchestrator, project-planner, explorer-agent, security-auditor, debugger, test-engineer
- `core/agent_registry.py`: Added `validate_agent_references()` function
- `_copilot_impl.py`: `generate_copilot_frontmatter()` queries registry for subagents/handoffs; falls back to hardcoded maps for prompt text
- `tests/test_agent_registry.py`: Added 3 validation tests

## New Test Files
- `tests/test_init_service.py` — 5 tests for `_write_bridge_meta()` delegation

## Architecture Impact

**Before:** Adding a new IDE required changes to 5-7 files (shotgun surgery):
- `capture_service.py` (hardcoded dispatch)
- `init_service.py` (hardcoded 80-line block)
- `utils/mcp.py` (hardcoded dest_paths dict)
- `cli.py` (hardcoded CAPTURE_IDES list)

**After:** Adding a new IDE requires only:
1. Create `converters/my_ide.py` implementing `BaseConverter`
2. Create `converters/_my_ide_impl.py` with conversion logic
3. Zero changes to services or utils
