"""Display / print helpers."""


def print_header(text: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")


def print_success(text: str) -> None:
    print(f"  ✓ {text}")


def print_error(text: str) -> None:
    print(f"  ✗ {text}")


def print_info(text: str) -> None:
    print(f"  ℹ {text}")
