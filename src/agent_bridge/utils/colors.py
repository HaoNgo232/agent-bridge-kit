"""ANSI color constants with NO_COLOR support."""

import os


class Colors:
    _color_enabled = not os.environ.get("NO_COLOR") and os.isatty(1)

    HEADER = "\033[95m" if _color_enabled else ""
    BLUE = "\033[94m" if _color_enabled else ""
    CYAN = "\033[96m" if _color_enabled else ""
    GREEN = "\033[92m" if _color_enabled else ""
    YELLOW = "\033[93m" if _color_enabled else ""
    RED = "\033[91m" if _color_enabled else ""
    BOLD = "\033[1m" if _color_enabled else ""
    ENDC = "\033[0m" if _color_enabled else ""
