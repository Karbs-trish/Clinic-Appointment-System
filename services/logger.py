from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from utils.clock import Clock


# Invariant:
#   - log_path always points to a writable file
#   - every line is prefixed with [Hour {now}]
class Logger:
    """
    Writes timestamped clinic events to a log file and stdout.
    Owns the Part 4 context manager that guarantees '[log] opened'
    and '[log] closed' are written even when an error occurs.
    """

    def __init__(self, log_path: str, clock: Clock):
        self._log_path = Path(log_path)
        self._clock = clock
        self._log_path.parent.mkdir(parents=True, exist_ok=True)
        self._log_path.touch(exist_ok=True)

    def log(self, message: str) -> None:
        """Write a timestamped line to both the log file and stdout."""
        line = f"[Hour {self._clock.now()}] {message}"
        with open(self._log_path, "a", encoding="utf-8") as file:
            file.write(line + "\n")
        print(line)

    @contextmanager
    def session(self) -> Generator[None, None, None]:
        """
        Context manager for a multi-step clinic operation.

        The 'with' statement + 'finally' guarantees:
          - '[log] opened' is always the first line of the operation.
          - '[log] closed' is always the last, even when an exception occurs.
          - The file is never left half-open (answers D5).

        Usage in Clinic:
            with self._logger.session():
                ...  # do work; raise ValueError on failure
        """
        self.log("[log] opened")
        try:
            yield
        except ValueError as e:
            self.log(f"FAILED: {e}")
            raise
        finally:
            self.log("[log] closed")