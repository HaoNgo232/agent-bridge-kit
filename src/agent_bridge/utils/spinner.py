"""Loading spinner for long-running operations."""

import sys
import time
import threading
from .colors import Colors


import os

class SimpleSpinner:
    """Context manager for displaying a loading spinner with optional progress %."""

    def __init__(self, message="Loading...", show_progress=False, estimated_seconds=None):
        self.chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        self.message = message
        self.show_progress = show_progress
        self.estimated_seconds = estimated_seconds
        self.progress = 0
        self.running = False
        self.thread = None
        self._lock = threading.Lock()
        self.start_time = None
        # Screen reader mode if env var is set or if NO_COLOR is set (sometimes indicative of simple terminal)
        self.screen_reader_mode = os.environ.get("SCREEN_READER") == "1"

    def update_progress(self, percent: int) -> None:
        """Update progress percentage (0-100)."""
        with self._lock:
            self.progress = max(0, min(100, percent))

    def spin(self):
        i = 0
        self.start_time = time.time()
        
        if self.screen_reader_mode:
            # Simple periodic updates for screen readers
            while self.running:
                elapsed = int(time.time() - self.start_time)
                print(f"\r{self.message} ({elapsed} seconds elapsed)...", end="")
                sys.stdout.flush()
                time.sleep(3)
            return

        while self.running:
            with self._lock:
                progress = self.progress
            
            elapsed = int(time.time() - self.start_time)
            if self.estimated_seconds and elapsed < self.estimated_seconds:
                remaining = self.estimated_seconds - elapsed
                progress_msg = f"{self.message} (~{remaining}s remaining)"
            elif self.show_progress and progress > 0:
                progress_msg = f"{self.message} ({progress}%)"
            else:
                progress_msg = f"{self.message} ({elapsed}s)"
                
            char = self.chars[i % len(self.chars)]
            sys.stdout.write(f"\r  {Colors.CYAN}{char}{Colors.ENDC} {progress_msg}")
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
        # Clean up line
        sys.stdout.write(f"\r{' ' * 80}\r")
        sys.stdout.flush()
