"""Display / print helpers."""

from .colors import Colors


def print_header(text: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")


def print_success(text: str) -> None:
    print(f"  {Colors.GREEN}✓{Colors.ENDC} {text}")


def print_error(text: str) -> None:
    print(f"  {Colors.RED}✗{Colors.ENDC} {text}")


def print_info(text: str) -> None:
    print(f"  {Colors.BLUE}ℹ{Colors.ENDC} {text}")


def print_step(text: str, step_num: int = None, total: int = None) -> None:
    """Print step with optional numbering."""
    if step_num and total:
        prefix = f"[{step_num}/{total}]"
    else:
        prefix = "→"
    print(f"{Colors.CYAN}{prefix}{Colors.ENDC} {text}")


def print_success_with_details(text: str, details: str = None) -> None:
    """Success message with optional details."""
    print(f"  {Colors.GREEN}✓{Colors.ENDC} {text}")
    if details:
        print(f"    {Colors.BLUE}ℹ{Colors.ENDC} {details}")


def print_error_with_suggestion(error: str, suggestion: str) -> None:
    """Error with actionable suggestion."""
    print(f"  {Colors.RED}✗{Colors.ENDC} {error}")
    print(f"    {Colors.YELLOW}💡{Colors.ENDC} {suggestion}")
