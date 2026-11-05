from abc import ABC, abstractmethod


# Invariant:
#   - now() always returns a value in the range [0, 168]
class Clock(ABC):
    """
    Abstract clock used by the clinic.
    The clinic must never read the system clock directly — it always
    asks a Clock object for now(). This makes time-dependent logic
    fully testable without waiting for real time to pass.
    """

    @abstractmethod
    def now(self) -> int:
        """
        Return the current hour (0–168).
        """
        pass


# Invariant:
#   - _current_hour is always in the range [0, 168]
#   - advance() clamps at 168 and never wraps
class ManualClock(Clock):
    """
    A manually controlled clock for testing.
    Allows the caller to set, advance, or check the current hour
    without touching the real system clock.
    """

    def __init__(self, current_hour: int = 0):
        if not (0 <= current_hour <= 168):
            raise ValueError("Hour must be between 0 and 168.")
        self._current_hour = current_hour

    def now(self) -> int:
        return self._current_hour

    def set_time(self, hour: int) -> None:
        if not (0 <= hour <= 168):
            raise ValueError("Hour must be between 0 and 168.")
        self._current_hour = hour

    def advance(self, hours: int = 1) -> None:
        if hours < 0:
            raise ValueError("Hours must be non-negative.")
        self._current_hour = min(self._current_hour + hours, 168)