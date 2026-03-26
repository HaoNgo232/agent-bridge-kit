"""
Display formatting for 'agent-bridge status' output.
Separated from collection logic for testability.
"""

from agent_bridge.services.status_service import ProjectStatus
from agent_bridge.utils import Colors


def display_status(status: ProjectStatus) -> None:
    """Print formatted status dashboard with grouped display."""
    
    print(f"\n{Colors.BOLD}📊 Agent Bridge Dashboard{Colors.ENDC}")
    print(f"{Colors.BOLD}📍 Project:{Colors.ENDC} {status.project_path}")
    
    # Quick summary bar
    total_agents = status.agent_counts.get('agents', 0)
    total_skills = status.agent_counts.get('skills', 0)
    active_vaults = len([v for v in status.vault_statuses if v.enabled])
    init_ides = len([i for i in status.ide_statuses if i.initialized])
    
    print(f"\n{Colors.CYAN}📈 Summary:{Colors.ENDC} {total_agents} agents • {total_skills} skills • {active_vaults} vaults • {init_ides} IDEs")

    # Source with summary line
    print()
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
    active_vaults_list = [v for v in status.vault_statuses if v.enabled]
    print(f"{Colors.BOLD}🔗 Vaults ({len(active_vaults_list)} active):{Colors.ENDC}")

    if not active_vaults_list:
        print(f"   {Colors.YELLOW}⚠ No vaults registered — run 'agent-bridge vault add'{Colors.ENDC}")
    else:
        synced = [v for v in active_vaults_list if v.is_cached and not v.stale]
        stale = [v for v in active_vaults_list if v.is_cached and v.stale]
        never = [v for v in active_vaults_list if not v.is_cached]

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
            note = f" (stale — run '{Colors.CYAN}agent-bridge update{Colors.ENDC}')"
        else:
            symbol = f"{Colors.GREEN}✓{Colors.ENDC}"
            note = ""
        print(f"   {symbol} {ide.name:<10} {ide.output_dir:<15} ({ide.file_count} files){note}")

    if not_init:
        names = ", ".join(i.name for i in not_init)
        print(f"   {Colors.RED}✗ Not initialized:{Colors.ENDC} {names}")

    # MCP
    print(f"{Colors.BOLD}🔌 MCP:{Colors.ENDC}", end=" ")
    if status.mcp_info and status.mcp_info.config_exists:
        servers = ", ".join(status.mcp_info.server_names)
        print(f".agent/mcp_config.json ({status.mcp_info.server_count} servers: {servers})")
    else:
        print(f"{Colors.YELLOW}⚠ No MCP configuration{Colors.ENDC}")

    # Recommended actions
    _show_recommended_actions(status)
    print()


def _show_recommended_actions(status: ProjectStatus) -> None:
    """Suggested next actions based on current project state."""
    print(f"\n{Colors.BOLD}🧭 Recommended next steps:{Colors.ENDC}")
    
    if not status.agent_dir_exists:
        print(f"  {Colors.CYAN}• Run 'agent-bridge init' to set up AI agents{Colors.ENDC}")
    else:
        stale_vaults = [v for v in status.vault_statuses if v.enabled and v.stale]
        stale_ides = [i for i in status.ide_statuses if i.initialized and i.is_stale]
        
        if stale_vaults:
            print(f"  {Colors.CYAN}• Run 'agent-bridge vault sync' to download latest vault changes{Colors.ENDC}")
        elif stale_ides:
            print(f"  {Colors.CYAN}• Run 'agent-bridge update' to refresh IDE configs{Colors.ENDC}")
        else:
            print(f"  {Colors.GREEN}• Everything is up to date! Try 'agent-bridge capture' after making IDE changes{Colors.ENDC}")
