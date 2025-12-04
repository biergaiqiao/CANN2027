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


def induce_throttle(duration_seconds: float = 0.5, slowdown_factor: float = 2.0) -> float:
    """Simulate compute throttling and return the expected slowdown factor."""

    time.sleep(duration_seconds)
    return slowdown_factor


def drop_packets(packet_count: int, drop_ratio: float = 0.1) -> int:
    """Emulate partial packet loss at a given ratio and report losses."""

    dropped = int(packet_count * drop_ratio)
    return dropped


from typing import Iterable, List
from random import random


def stuck_at_fault(value: float, stuck_value: float = 0.0) -> float:
    """Force a value to a stuck-at condition for digital-line testing."""
    return stuck_value if value != stuck_value else value + 1e-3


def jitter_series(values: Iterable[float], amplitude: float = 0.02) -> List[float]:
    """Introduce bounded jitter across a sequence for timing noise simulation."""
    return [value + (random() - 0.5) * amplitude for value in values]


