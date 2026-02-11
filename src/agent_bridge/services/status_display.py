"""
Display formatting for 'agent-bridge status' output.
Separated from collection logic for testability.
"""

from agent_bridge.services.status_service import ProjectStatus
from agent_bridge.utils import Colors


def display_status(status: ProjectStatus) -> None:
    """Print formatted status dashboard."""
    
    # Project header
    print(f"\n{Colors.BOLD}📍 Project:{Colors.ENDC} {status.project_path}")
    
    # Source content
    if status.agent_dir_exists:
        counts = status.agent_counts
        print(f"{Colors.BOLD}📦 Source:{Colors.ENDC}  .agent/ "
              f"({counts.get('agents', 0)} agents, "
              f"{counts.get('skills', 0)} skills, "
              f"{counts.get('workflows', 0)} workflows, "
              f"{counts.get('rules', 0)} rules)")
    else:
        print(f"{Colors.BOLD}📦 Source:{Colors.ENDC}  {Colors.RED}✗ .agent/ not found{Colors.ENDC}")
    
    # Vaults
    print(f"{Colors.BOLD}🔗 Vaults:{Colors.ENDC}")
    if not status.vault_statuses:
        print(f"   {Colors.YELLOW}⚠ No vaults registered{Colors.ENDC}")
    else:
        for vault in status.vault_statuses:
            if not vault.enabled:
                continue
            
            if vault.is_cached:
                if vault.stale:
                    symbol = f"{Colors.YELLOW}⚠{Colors.ENDC}"
                    note = f" — consider running 'agent-bridge vault sync'"
                else:
                    symbol = f"{Colors.GREEN}✓{Colors.ENDC}"
                    note = ""
                print(f"   {symbol} {vault.name:<20} (synced {vault.freshness}){note}")
            else:
                symbol = f"{Colors.RED}✗{Colors.ENDC}"
                print(f"   {symbol} {vault.name:<20} (never synced)")
    
    # IDEs
    print(f"{Colors.BOLD}🖥  IDEs:{Colors.ENDC}")
    for ide in status.ide_statuses:
        if ide.initialized:
            if ide.is_stale:
                symbol = f"{Colors.YELLOW}⚠{Colors.ENDC}"
                note = " (stale — run 'agent-bridge update')"
            else:
                symbol = f"{Colors.GREEN}✓{Colors.ENDC}"
                note = ""
            print(f"   {symbol} {ide.name:<10} — {ide.output_dir:<15} ({ide.file_count} files, synced){note}")
        else:
            symbol = f"{Colors.RED}✗{Colors.ENDC}"
            print(f"   {symbol} {ide.name:<10} — not initialized")
    
    # MCP
    if status.mcp_info and status.mcp_info.config_exists:
        servers = ", ".join(status.mcp_info.server_names)
        print(f"{Colors.BOLD}🔌 MCP:{Colors.ENDC} .agent/mcp_config.json found "
              f"({status.mcp_info.server_count} servers: {servers})")
    else:
        print(f"{Colors.BOLD}🔌 MCP:{Colors.ENDC} {Colors.YELLOW}⚠ No MCP configuration{Colors.ENDC}")
    
    print()  # Trailing newline
