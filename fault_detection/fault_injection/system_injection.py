"""System-level injection hooks to emulate node failures."""
import time
from typing import Callable, Optional


def simulate_outage(
    recovery_callback: Callable[[], None],
    duration_seconds: float = 1.0,
    on_outage: Optional[Callable[[float], None]] = None,
) -> None:
    """Simulate a temporary outage and trigger recovery.

    The optional ``on_outage`` hook can be used to log or flip feature flags while
    the simulated outage is in effect.
    """
    if on_outage is not None:
        on_outage(duration_seconds)
    time.sleep(duration_seconds)
    recovery_callback()
