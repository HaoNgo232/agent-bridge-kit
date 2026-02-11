"""
Business logic for 'agent-bridge status' command.
Collects project state and returns structured data for display.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from agent_bridge.vault.manager import VaultManager
from agent_bridge.core.converter import converter_registry


@dataclass
class VaultStatus:
    name: str
    enabled: bool
    is_cached: bool
    last_synced: Optional[datetime]
    source_type: str
    freshness: str
    stale: bool


@dataclass
class IDEStatus:
    name: str
    display_name: str
    output_dir: str
    initialized: bool
    file_count: int
    is_stale: bool


@dataclass
class MCPInfo:
    config_exists: bool
    server_names: List[str]
    server_count: int


@dataclass
class ProjectStatus:
    project_path: Path
    agent_dir_exists: bool
    agent_counts: Dict[str, int]
    vault_statuses: List[VaultStatus]
    ide_statuses: List[IDEStatus]
    mcp_info: Optional[MCPInfo]


def collect_status(project_path: Path) -> ProjectStatus:
    """Main entry point. Collects all project status data."""
    agent_dir = project_path / ".agent"
    agent_dir_exists = agent_dir.exists()
    
    agent_counts = _count_agent_content(agent_dir) if agent_dir_exists else {}
    vault_statuses = _get_vault_statuses()
    ide_statuses = _get_ide_statuses(project_path, agent_dir)
    mcp_info = _get_mcp_info(agent_dir) if agent_dir_exists else None
    
    return ProjectStatus(
        project_path=project_path,
        agent_dir_exists=agent_dir_exists,
        agent_counts=agent_counts,
        vault_statuses=vault_statuses,
        ide_statuses=ide_statuses,
        mcp_info=mcp_info,
    )


def _count_agent_content(agent_dir: Path) -> Dict[str, int]:
    """Count agents/*.md, skills/*/ (dirs), workflows/*.md, rules/*.md"""
    counts = {"agents": 0, "skills": 0, "workflows": 0, "rules": 0}
    
    if not agent_dir.exists():
        return counts
    
    agents_dir = agent_dir / "agents"
    if agents_dir.exists():
        counts["agents"] = len([f for f in agents_dir.glob("*.md") if f.is_file()])
    
    skills_dir = agent_dir / "skills"
    if skills_dir.exists():
        counts["skills"] = len([d for d in skills_dir.iterdir() if d.is_dir()])
    
    workflows_dir = agent_dir / "workflows"
    if workflows_dir.exists():
        counts["workflows"] = len([f for f in workflows_dir.glob("*.md") if f.is_file()])
    
    rules_dir = agent_dir / "rules"
    if rules_dir.exists():
        counts["rules"] = len([f for f in rules_dir.glob("*.md") if f.is_file()])
    
    return counts


def _get_vault_statuses() -> List[VaultStatus]:
    """Get status of all registered vaults."""
    vm = VaultManager()
    statuses = []
    
    for vault in vm.vaults:
        is_cached = vault.cache_path.exists() if not vault.is_local else True
        last_synced = None
        
        if vault.is_local:
            local_path = Path(vault.url).resolve()
            if local_path.exists():
                last_synced = datetime.fromtimestamp(local_path.stat().st_mtime)
        elif vault.is_builtin:
            # Builtin is always "synced"
            last_synced = datetime.now()
        elif vault.cache_path.exists():
            last_synced = datetime.fromtimestamp(vault.cache_path.stat().st_mtime)
        
        freshness = _relative_time(last_synced) if last_synced else "never synced"
        stale = False
        if last_synced:
            age_hours = (datetime.now() - last_synced).total_seconds() / 3600
            stale = age_hours > 24
        
        source_type = "builtin" if vault.is_builtin else ("local" if vault.is_local else "git")
        
        statuses.append(VaultStatus(
            name=vault.name,
            enabled=vault.enabled,
            is_cached=is_cached,
            last_synced=last_synced,
            source_type=source_type,
            freshness=freshness,
            stale=stale,
        ))
    
    return statuses


def _get_ide_statuses(project_path: Path, agent_dir: Path) -> List[IDEStatus]:
    """Check initialization status for all registered IDEs."""
    statuses = []
    
    # Get newest mtime in .agent/ tree
    agent_newest = _get_newest_mtime(agent_dir) if agent_dir.exists() else None
    
    for converter in converter_registry.all():
        fmt = converter.format_info  # Property, not method
        output_dir = project_path / fmt.output_dir
        
        initialized = output_dir.exists() and any(output_dir.rglob("*"))
        file_count = len(list(output_dir.rglob("*"))) if initialized else 0
        
        is_stale = False
        if initialized and agent_newest:
            ide_newest = _get_newest_mtime(output_dir)
            if ide_newest and agent_newest > ide_newest:
                is_stale = True
        
        statuses.append(IDEStatus(
            name=fmt.name,
            display_name=fmt.display_name,
            output_dir=fmt.output_dir,
            initialized=initialized,
            file_count=file_count,
            is_stale=is_stale,
        ))
    
    return statuses


def _get_mcp_info(agent_dir: Path) -> Optional[MCPInfo]:
    """Load .agent/mcp_config.json and extract server info."""
    import json
    
    mcp_file = agent_dir / "mcp_config.json"
    if not mcp_file.exists():
        return None
    
    try:
        config = json.loads(mcp_file.read_text(encoding="utf-8"))
        servers = config.get("mcpServers", {})
        server_names = list(servers.keys())
        
        return MCPInfo(
            config_exists=True,
            server_names=server_names,
            server_count=len(server_names),
        )
    except (json.JSONDecodeError, KeyError):
        return None


def _get_newest_mtime(directory: Path) -> Optional[datetime]:
    """Get the newest modification time in a directory tree."""
    if not directory.exists():
        return None
    
    newest = None
    for item in directory.rglob("*"):
        if item.is_file():
            mtime = datetime.fromtimestamp(item.stat().st_mtime)
            if newest is None or mtime > newest:
                newest = mtime
    
    return newest


def _relative_time(dt: Optional[datetime]) -> str:
    """Convert datetime to human-friendly string like '2h ago', '3d ago'."""
    if dt is None:
        return "never"
    
    delta = datetime.now() - dt
    seconds = delta.total_seconds()
    
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes}m ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours}h ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days}d ago"
    else:
        weeks = int(seconds / 604800)
        return f"{weeks}w ago"
