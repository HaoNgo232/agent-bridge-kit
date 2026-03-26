"""Loading spinner for long-running operations."""

import sys
import time
import threading
from .colors import Colors


class SimpleSpinner:
    """Context manager for displaying a loading spinner with optional progress %."""

    def __init__(self, message="Loading...", show_progress=False):
        self.chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        self.message = message
        self.show_progress = show_progress
        self.progress = 0
        self.running = False
        self.thread = None
        self._lock = threading.Lock()

    def update_progress(self, percent: int) -> None:
        """Update progress percentage (0-100)."""
        with self._lock:
            self.progress = max(0, min(100, percent))

    def spin(self):
        i = 0
        while self.running:
            with self._lock:
                progress = self.progress
            if self.show_progress and progress > 0:
                display_msg = f"{self.message} ({progress}%)"
            else:
                display_msg = self.message
            char = self.chars[i % len(self.chars)]
            sys.stdout.write(f"\r  {Colors.CYAN}{char}{Colors.ENDC} {display_msg}")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1

    def __enter__(self):
        self.running = True
        self.thread = threading.Thread(target=self.spin, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.running = False
        if self.thread:
            self.thread.join()
        sys.stdout.write(f"\r{' ' * (len(self.message) + 12)}\r")
        sys.stdout.flush()
