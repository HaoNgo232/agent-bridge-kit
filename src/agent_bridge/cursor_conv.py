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

    cursor_rules_dir = Path(".cursor/rules").resolve()
    cursor_agents_dir = Path(".cursor/agents").resolve()
    cursor_skills_dir = Path(".cursor/skills").resolve()
    
    print(f"{Colors.HEADER}🏗️  Converting to Cursor Format (Agents, Skills, Rules)...{Colors.ENDC}")

    # 1. PROCESS AGENTS -> .cursor/agents/<agent>.md (Subagents)
    agents_src_dir = root_path / "agents"
    if agents_src_dir.exists():
        cursor_agents_dir.mkdir(parents=True, exist_ok=True)
        for agent_file in agents_src_dir.glob("*.md"):
            try:
                meta, body = parse_frontmatter(agent_file.read_text(encoding='utf-8'))
                desc = meta.get("description", "")
                if isinstance(desc, list): desc = " ".join(desc)
                
                lines = [
                    "---",
                    f"name: {agent_file.stem}",
                    f"description: {desc}",
                    "---",
                    f"\n{body}"
                ]

                with open(cursor_agents_dir / f"{agent_file.stem}.md", 'w', encoding='utf-8') as f:
                    f.write("\n".join(lines))
                print(f"{Colors.BLUE}  🔹 Subagent: {agent_file.stem}.md{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.RED}  ❌ Failed cursor subagent {agent_file.name}: {e}{Colors.ENDC}")

    # 2. PROCESS SKILLS -> .cursor/skills/<skill>.md
    skills_src_dir = root_path / "skills"
    if skills_src_dir.exists():
        cursor_skills_dir.mkdir(parents=True, exist_ok=True)
        for skill_dir in skills_src_dir.iterdir():
            if not skill_dir.is_dir(): continue
            src_skill_file = skill_dir / "SKILL.md"
            if src_skill_file.exists():
                try:
                    meta, body = parse_frontmatter(src_skill_file.read_text(encoding='utf-8'))
                    desc = meta.get("description", "")
                    if isinstance(desc, list): desc = " ".join(desc)

                    lines = [
                        "---",
                        f"name: {skill_dir.name}",
                        f"description: {desc or skill_dir.name}",
                        "---",
                        f"\n{body}"
                    ]

                    with open(cursor_skills_dir / f"{skill_dir.name}.md", 'w', encoding='utf-8') as f:
                        f.write("\n".join(lines))
                    print(f"{Colors.BLUE}  🔸 Skill: {skill_dir.name}.md{Colors.ENDC}")
                except Exception as e:
                    print(f"{Colors.RED}  ❌ Failed cursor skill {skill_dir.name}: {e}{Colors.ENDC}")

    # 3. GENERATE GLOBAL INSTRUCTIONS -> .cursor/rules/project-instructions.mdc
    planner_file = agents_src_dir / "project-planner.md"
    if planner_file.exists():
        cursor_rules_dir.mkdir(parents=True, exist_ok=True)
        try:
            _, body = parse_frontmatter(planner_file.read_text(encoding='utf-8'))
            lines = [
                "---",
                "description: Global Project Instructions & Architecture",
                "globs: *",
                "alwaysApply: true",
                "---",
                f"\n# Project Instructions\n\n{body}"
            ]
            with open(cursor_rules_dir / "project-instructions.mdc", 'w', encoding='utf-8') as f:
                f.write("\n".join(lines))
            print(f"{Colors.BLUE}  📜 Generated .cursor/rules/project-instructions.mdc (Global){Colors.ENDC}")
        except: pass

    print(f"{Colors.GREEN}✅ Cursor conversion complete!{Colors.ENDC}")
