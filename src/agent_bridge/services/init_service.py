"""
Business logic cho lenh 'agent-bridge init'.

Xu ly: 1) Chuan bi .agent/ (tu vault, project, merge, hoac snapshot)
       2) Chay cac converter da chon
       3) Cai dat MCP config
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from agent_bridge.core.converter import converter_registry
from agent_bridge.vault import VaultManager
from agent_bridge.vault.merger import MergeStrategy, merge_source_into_project


def run_init(
    project_path: Path,
    format_names: List[str],
    source_choice: str,
    force: bool = False,
    verbose: bool = True,
    snapshot_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Logic chinh cua init.

    Args:
        project_path: Duong dan project root
        format_names: Danh sach IDE (vd: ["cursor", "kiro"])
        source_choice: "project" | "vault" | "merge"
        force: Ghi de khong hoi
        verbose: In tien trinh

    Returns:
        Dict ket qua: {"error": ...} hoac {format_name: ConversionResult}
    """
    agent_dir = project_path / ".agent"
    source_root = project_path

    # Buoc 1: Xu ly nguon
    if source_choice == "snapshot" and snapshot_name:
        from agent_bridge.services.snapshot_service import get_snapshot_agent_dir

        snapshot_dir = get_snapshot_agent_dir(snapshot_name)
        if not snapshot_dir:
            return {
                "error": f"🔍 We couldn't find the snapshot '{snapshot_name}'",
                "suggestion": "Check available snapshots with 'agent-bridge snapshot list'",
            }
        merge_source_into_project(snapshot_dir, agent_dir, MergeStrategy.VAULT_ONLY)
    elif source_choice == "vault":
        _fetch_vault(agent_dir, overwrite=True)
    elif source_choice == "merge":
        _fetch_vault(agent_dir, overwrite=False)

    if not agent_dir.exists():
        return {
            "error": "🤔 Looks like you haven't set up .agent/ for this project yet",
            "suggestion": "No worries! Let's get you started with 'agent-bridge init' or 'agent-bridge vault sync'",
        }

    # Buoc 2: Chay converter
    results: Dict[str, Any] = {}
    for name in format_names:
        converter = converter_registry.get(name)
        if converter:
            result = converter.convert(
                source_root, project_path, verbose=verbose, force=force
            )
            converter.install_mcp(source_root, project_path, force=force)
            results[name] = result

    # Buoc 3: Ghi .bridge-meta.json de track generated files (cho capture)
    _write_bridge_meta(project_path, format_names)

    return results


def _write_bridge_meta(project_path: Path, format_names: List[str]) -> None:
    """Ghi .agent/.bridge-meta.json de track cac file da generate."""
    import json
    from datetime import datetime, timezone

    agent_dir = project_path / ".agent"
    if not agent_dir.exists():
        return

    file_map: Dict[str, str] = {}
    for name in format_names:
        converter = converter_registry.get(name)
        if converter:
            file_map.update(converter.build_bridge_meta_map(project_path))

    meta = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generated_for": format_names,
        "file_map": file_map,
    }
    (agent_dir / ".bridge-meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")


def _fetch_vault(agent_dir: Path, overwrite: bool) -> None:
    """Lay noi dung vault vao agent_dir."""
    vm = VaultManager()
    vault_source = _ensure_vault_synced(vm)
    if not vault_source:
        return

    if vault_source.resolve() == agent_dir.resolve():
        return

    strategy = MergeStrategy.VAULT_ONLY if overwrite else MergeStrategy.PROJECT_WINS
    merge_source_into_project(vault_source, agent_dir, strategy)


def _ensure_vault_synced(vm: VaultManager) -> Path | None:
    """Dam bao it nhat mot vault da sync, tra ve .agent/ dir."""
    agent_dir = vm.get_first_available_agent_dir()
    if agent_dir:
        return agent_dir

    vm.sync(verbose=True)
    return vm.get_first_available_agent_dir()
