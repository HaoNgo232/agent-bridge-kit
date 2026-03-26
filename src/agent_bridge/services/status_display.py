"""
Display formatting for 'agent-bridge status' output.
Separated from collection logic for testability.
"""

from agent_bridge.services.status_service import ProjectStatus
from agent_bridge.utils import Colors


def display_status(status: ProjectStatus) -> None:
    """Print formatted status dashboard with grouped display."""

    # Project header
    print(f"\n{Colors.BOLD}📍 Project:{Colors.ENDC} {status.project_path}")

    # Source with summary line
    if status.agent_dir_exists:
        counts = status.agent_counts
        total = sum(counts.values())
        print(
            f"{Colors.BOLD}📦 Source:{Colors.ENDC}  .agent/ ({total} items — "
            f"agents: {counts.get('agents', 0)}, "
            f"skills: {counts.get('skills', 0)}, "
            f"workflows: {counts.get('workflows', 0)}, "
            f"rules: {counts.get('rules', 0)})"
        )
    else:
        print(f"{Colors.BOLD}📦 Source:{Colors.ENDC}  {Colors.RED}✗ .agent/ not found{Colors.ENDC}")

    # Vaults — grouped by status
    active_vaults = [v for v in status.vault_statuses if v.enabled]
    print(f"{Colors.BOLD}🔗 Vaults ({len(active_vaults)} active):{Colors.ENDC}")

    if not active_vaults:
        print(f"   {Colors.YELLOW}⚠ No vaults registered — run 'agent-bridge vault add'{Colors.ENDC}")
    else:
        synced = [v for v in active_vaults if v.is_cached and not v.stale]
        stale = [v for v in active_vaults if v.is_cached and v.stale]
        never = [v for v in active_vaults if not v.is_cached]

        if synced:
            names = ", ".join(v.name for v in synced[:3])
            suffix = f" +{len(synced) - 3} more" if len(synced) > 3 else ""
            print(f"   {Colors.GREEN}✓ Synced ({len(synced)}):{Colors.ENDC} {names}{suffix}")
        if stale:
            names = ", ".join(v.name for v in stale[:3])
            suffix = f" +{len(stale) - 3} more" if len(stale) > 3 else ""
            print(f"   {Colors.YELLOW}⚠ Stale ({len(stale)}):{Colors.ENDC} {names}{suffix} — run 'agent-bridge vault sync'")
        if never:
            names = ", ".join(v.name for v in never[:3])
            suffix = f" +{len(never) - 3} more" if len(never) > 3 else ""
            print(f"   {Colors.RED}✗ Not synced ({len(never)}):{Colors.ENDC} {names}{suffix}")

    # IDEs — grouped by status
    initialized = [i for i in status.ide_statuses if i.initialized]
    not_init = [i for i in status.ide_statuses if not i.initialized]
    print(f"{Colors.BOLD}🖥  IDEs ({len(initialized)} initialized):{Colors.ENDC}")

    for ide in initialized:
        if ide.is_stale:
            symbol = f"{Colors.YELLOW}⚠{Colors.ENDC}"
            note = " (stale — run 'agent-bridge update')"
        else:
            symbol = f"{Colors.GREEN}✓{Colors.ENDC}"
            note = ""
        print(f"   {symbol} {ide.name:<10} {ide.output_dir:<15} ({ide.file_count} files){note}")

    if not_init:
        names = ", ".join(i.name for i in not_init)
        print(f"   {Colors.RED}✗ Not initialized:{Colors.ENDC} {names}")

    # MCP
    if status.mcp_info and status.mcp_info.config_exists:
        servers = ", ".join(status.mcp_info.server_names)
        print(
            f"{Colors.BOLD}🔌 MCP:{Colors.ENDC} .agent/mcp_config.json "
            f"({status.mcp_info.server_count} servers: {servers})"
        )
    else:
        print(f"{Colors.BOLD}🔌 MCP:{Colors.ENDC} {Colors.YELLOW}⚠ No MCP configuration{Colors.ENDC}")

    print()
