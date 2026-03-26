"""Loading spinner for long-running operations."""

import sys
import time
import threading
from .colors import Colors


class SimpleSpinner:
    """Context manager for displaying a loading spinner."""

    def __init__(self, message="Loading..."):
        self.chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        self.message = message
        self.running = False
        self.thread = None

    def spin(self):
        i = 0
        while self.running:
            char = self.chars[i % len(self.chars)]
            sys.stdout.write(f"\r  {Colors.CYAN}{char}{Colors.ENDC} {self.message}")
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
        # Clear spinner line
        sys.stdout.write(f"\r{' ' * (len(self.message) + 4)}\r")
        sys.stdout.flush()
