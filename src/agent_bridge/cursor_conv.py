import os
from pathlib import Path
from typing import Dict, Tuple, List, Any
from .copilot_conv import parse_frontmatter, get_master_agent_dir, get_glob_for_context

# ANSI colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'

def convert_cursor(source_dir: str, output_unused: str):
    root_path = Path(source_dir).resolve()
    
    if not root_path.exists() or not (root_path / "agents").exists():
        master_path = get_master_agent_dir()
        if master_path.exists():
            root_path = master_path
        else:
            print(f"{Colors.RED}❌ Error: No source tri thức found.{Colors.ENDC}")
            return

    cursor_dir = Path(".cursor/rules").resolve()
    print(f"{Colors.HEADER}🏗️  Converting to Cursor .mdc Format...{Colors.ENDC}")

    # 1. PROCESS AGENTS -> .cursor/rules/<agent>.mdc
    agents_src_dir = root_path / "agents"
    if agents_src_dir.exists():
        cursor_dir.mkdir(parents=True, exist_ok=True)
        for agent_file in agents_src_dir.glob("*.md"):
            try:
                meta, body = parse_frontmatter(agent_file.read_text(encoding='utf-8'))
                desc = meta.get("description", "")
                if isinstance(desc, list): desc = " ".join(desc)
                
                glob = get_glob_for_context(agent_file.stem) or "*"
                
                # Cursor .mdc format
                lines = [
                    "---",
                    f"description: {desc}",
                    f"globs: {glob}",
                    "---",
                    f"\n{body}"
                ]

                with open(cursor_dir / f"{agent_file.stem}.mdc", 'w', encoding='utf-8') as f:
                    f.write("\n".join(lines))
                print(f"{Colors.BLUE}  🔹 Rule: {agent_file.stem}.mdc{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.RED}  ❌ Failed cursor rule {agent_file.name}: {e}{Colors.ENDC}")

    # 2. PROCESS SKILLS -> .cursor/rules/<skill>.mdc
    skills_src_dir = root_path / "skills"
    if skills_src_dir.exists():
        for skill_dir in skills_src_dir.iterdir():
            if not skill_dir.is_dir(): continue
            src_skill_file = skill_dir / "SKILL.md"
            if src_skill_file.exists():
                try:
                    meta, body = parse_frontmatter(src_skill_file.read_text(encoding='utf-8'))
                    desc = meta.get("description", "")
                    if isinstance(desc, list): desc = " ".join(desc)
                    
                    glob = get_glob_for_context(skill_dir.name) or "*"

                    lines = [
                        "---",
                        f"description: Skill - {desc or skill_dir.name}",
                        f"globs: {glob}",
                        "---",
                        f"\n{body}"
                    ]

                    with open(cursor_dir / f"{skill_dir.name}.mdc", 'w', encoding='utf-8') as f:
                        f.write("\n".join(lines))
                    print(f"{Colors.BLUE}  🔸 Skill: {skill_dir.name}.mdc{Colors.ENDC}")
                except Exception as e:
                    print(f"{Colors.RED}  ❌ Failed cursor skill {skill_dir.name}: {e}{Colors.ENDC}")

    print(f"{Colors.GREEN}✅ Cursor conversion complete!{Colors.ENDC}")
