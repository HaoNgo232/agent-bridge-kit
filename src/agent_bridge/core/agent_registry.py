"""
Centralized Agent Role Registry — THE single source of truth.

Previously every converter had its own AGENT_CONFIG_MAP / AGENT_TOOLS_MAP.
Now they all query here. Add a new role once, every converter picks it up.
"""

from typing import Dict, Optional
from .types import AgentRole

AGENT_ROLES: Dict[str, AgentRole] = {}


def _r(*roles: AgentRole) -> None:
    for role in roles:
        AGENT_ROLES[role.slug] = role


_r(
    # === Primary agents ===
    AgentRole(
        slug="orchestrator", name="Orchestrator",
        description="High-level coordinator for complex, multi-step tasks",
        can_read=True, can_write=False, can_execute=False, can_search=True,
        can_delegate=True, delegatable_agents=["*"],
        allowed_commands=["git status", "git log *"],
        category="primary",
        subagents=["*"],
        handoff_targets=["frontend-specialist", "backend-specialist", "database-architect", "test-engineer"],
        handoff_prompts={
            "frontend-specialist": {"label": "Frontend Tasks", "prompt": "Implement the frontend components as specified."},
            "backend-specialist": {"label": "Backend Tasks", "prompt": "Implement the backend services as specified."},
            "database-architect": {"label": "Database Setup", "prompt": "Design and implement the database schema."},
            "test-engineer": {"label": "Write Tests", "prompt": "Write tests for the implemented features."},
        },
        opencode_permission={"task": {"*": "allow"}},  # Can invoke any subagent
    ),
    AgentRole(
        slug="frontend-specialist", name="Frontend Specialist",
        description="Frontend development with React, Next.js, UI/UX",
        can_read=True, can_write=True, can_execute=True, can_search=True,
        allowed_commands=[
            "npm *", "npx *", "yarn *", "pnpm *", "node *",
            "tsc *", "eslint *", "prettier *",
            "git status", "git diff *", "git log *",
        ],
        allowed_paths=["src/**", "components/**", "pages/**", "app/**", "public/**", "styles/**"],
        category="primary",
        opencode_permission={"edit": "allow", "bash": "allow"},
    ),
    AgentRole(
        slug="backend-specialist", name="Backend Specialist",
        description="Backend development with APIs, databases, and server logic",
        can_read=True, can_write=True, can_execute=True, can_search=True,
        allowed_commands=[
            "npm *", "node *", "python *", "pip *",
            "docker *", "docker-compose *",
            "git status", "git diff *", "git log *", "curl *", "wget *",
        ],
        allowed_paths=["src/**", "api/**", "server/**", "lib/**", "services/**"],
        category="primary",
        opencode_permission={"edit": "allow", "bash": "allow"},
    ),

    # === Subagents ===
    AgentRole(
        slug="project-planner", name="Project Planner",
        description="Creates implementation plans and task breakdowns",
        can_read=True, can_write=False, can_execute=False, can_search=True,
        can_delegate=True, delegatable_agents=["*"],
        allowed_commands=["git log *", "git status", "find *", "tree *"],
        category="subagent",
        subagents=["*"],
        handoff_targets=["orchestrator", "security-auditor"],
        handoff_prompts={
            "orchestrator": {"label": "Start Implementation", "prompt": "Implement the plan outlined above following the task breakdown."},
            "security-auditor": {"label": "Security Review", "prompt": "Review the security aspects of this implementation plan."},
        },
    ),
    AgentRole(
        slug="explorer-agent", name="Explorer Agent",
        description="Explores and analyzes codebase structure",
        can_read=True, can_write=False, can_execute=False, can_search=True,
        allowed_commands=["git log *", "git status", "find *", "grep *", "tree *", "cat *", "head *", "tail *"],
        category="subagent",
        handoff_targets=["project-planner"],
        handoff_prompts={
            "project-planner": {"label": "Create Plan", "prompt": "Create an implementation plan based on this codebase analysis."},
        },
    ),
    AgentRole(
        slug="security-auditor", name="Security Auditor",
        description="Audits code for security vulnerabilities",
        can_read=True, can_write=False, can_execute=False, can_search=True,
        allowed_commands=["npm audit", "yarn audit", "git log *", "git diff *", "grep *", "find *"],
        category="subagent",
        handoff_targets=["backend-specialist"],
        handoff_prompts={
            "backend-specialist": {"label": "Fix Security Issues", "prompt": "Fix the security vulnerabilities identified in the audit."},
        },
    ),
    AgentRole(
        slug="penetration-tester", name="Penetration Tester",
        description="Security penetration testing",
        can_read=True, can_write=False, can_execute=False, can_search=True,
        allowed_commands=["git log *", "git diff *"],
        category="subagent",
    ),
    AgentRole(
        slug="test-engineer", name="Test Engineer",
        description="Writes and maintains tests",
        can_read=True, can_write=True, can_execute=True, can_search=True,
        allowed_commands=[
            "npm test *", "npm run test *", "npx jest *", "npx vitest *",
            "npx playwright *", "npx cypress *", "python -m pytest *",
            "git status", "git diff *",
        ],
        allowed_paths=["tests/**", "test/**", "__tests__/**", "*.test.*", "*.spec.*"],
        category="subagent",
        handoff_targets=["backend-specialist"],
        handoff_prompts={
            "backend-specialist": {"label": "Fix Failing Tests", "prompt": "Fix the code to make the failing tests pass."},
        },
    ),
    AgentRole(
        slug="debugger", name="Debugger",
        description="Root cause analysis and bug fixing",
        can_read=True, can_write=True, can_execute=True, can_search=True,
        can_delegate=True, delegatable_agents=["backend-specialist", "frontend-specialist", "test-engineer"],
        allowed_commands=[
            "node --inspect *", "python -m pdb *", "npm run *", "node *",
            "git diff *", "git log *", "git blame *",
        ],
        category="subagent",
        subagents=["backend-specialist", "frontend-specialist", "test-engineer"],
        handoff_targets=["backend-specialist"],
        handoff_prompts={
            "backend-specialist": {"label": "Implement Fix", "prompt": "Implement the fix for the identified bug."},
        },
    ),
    AgentRole(
        slug="database-architect", name="Database Architect",
        description="Designs database schemas and migrations",
        can_read=True, can_write=True, can_execute=True, can_search=True,
        allowed_commands=["npx prisma *", "npx drizzle-kit *", "psql *", "mysql *", "sqlite3 *", "git status", "git diff *"],
        allowed_paths=["prisma/**", "drizzle/**", "migrations/**", "db/**", "schema/**"],
        category="subagent",
    ),
    AgentRole(
        slug="devops-engineer", name="DevOps Engineer",
        description="Manages deployment and infrastructure",
        can_read=True, can_write=True, can_execute=True, can_search=True,
        allowed_commands=["docker *", "docker-compose *", "kubectl *", "helm *", "terraform *", "aws *", "gcloud *", "az *", "git *"],
        allowed_paths=[".github/**", "docker/**", "k8s/**", "terraform/**", "infra/**"],
        category="subagent",
    ),
    AgentRole(
        slug="documentation-writer", name="Documentation Writer",
        description="Writes and maintains documentation",
        can_read=True, can_write=True, can_execute=False, can_search=True,
        allowed_commands=["git status", "git log *", "npx typedoc *", "npx jsdoc *"],
        allowed_paths=["docs/**", "*.md", "README*", "CHANGELOG*", "*.mdx"],
        category="subagent",
    ),
    AgentRole(
        slug="performance-optimizer", name="Performance Optimizer",
        description="Optimizes code and application performance",
        can_read=True, can_write=True, can_execute=True, can_search=True,
        allowed_commands=["npx lighthouse *", "npm run build *", "node --prof *", "python -m cProfile *"],
        category="subagent",
    ),
    AgentRole(
        slug="mobile-developer", name="Mobile Developer",
        description="Mobile development for iOS/Android",
        can_read=True, can_write=True, can_execute=True, can_search=True,
        allowed_commands=["npm *", "npx *", "yarn *", "npx react-native *", "npx expo *", "git status", "git diff *"],
        allowed_paths=["src/**", "app/**", "android/**", "ios/**"],
        category="subagent",
    ),
    AgentRole(
        slug="game-developer", name="Game Developer",
        description="Game development specialist",
        can_read=True, can_write=True, can_execute=True, can_search=True,
        category="subagent",
    ),
    AgentRole(
        slug="product-manager", name="Product Manager",
        description="Product management and requirements",
        can_read=True, can_write=False, can_execute=False, can_search=True,
        category="subagent",
    ),
    AgentRole(
        slug="product-owner", name="Product Owner",
        description="Product ownership and backlog management",
        can_read=True, can_write=False, can_execute=False, can_search=True,
        category="subagent",
    ),
    AgentRole(
        slug="seo-specialist", name="SEO Specialist",
        description="Search engine optimization",
        can_read=True, can_write=True, can_execute=False, can_search=True,
        category="subagent",
    ),
    AgentRole(
        slug="qa-automation-engineer", name="QA Automation Engineer",
        description="QA test automation",
        can_read=True, can_write=True, can_execute=True, can_search=True,
        allowed_commands=["npm test *", "npx jest *", "npx playwright *", "git status", "git diff *"],
        category="subagent",
    ),

    # === Internal (hidden) ===
    AgentRole(
        slug="code-archaeologist", name="Code Archaeologist",
        description="Analyzes legacy code and dependencies",
        can_read=True, can_write=False, can_execute=False, can_search=True,
        category="internal", hidden=True,
    ),
)


def get_agent_role(slug: str) -> Optional[AgentRole]:
    return AGENT_ROLES.get(slug)


def get_primary_agents() -> list[AgentRole]:
    return [r for r in AGENT_ROLES.values() if r.category == "primary"]


def get_visible_agents() -> list[AgentRole]:
    return [r for r in AGENT_ROLES.values() if not r.hidden]


def validate_agent_references() -> list[str]:
    """Return list of errors for invalid subagent/handoff references."""
    errors = []
    for slug, role in AGENT_ROLES.items():
        for ref in role.subagents:
            if ref != "*" and ref not in AGENT_ROLES:
                errors.append(f"{slug}.subagents references unknown agent: {ref}")
        for ref in role.handoff_targets:
            if ref not in AGENT_ROLES:
                errors.append(f"{slug}.handoff_targets references unknown agent: {ref}")
    return errors