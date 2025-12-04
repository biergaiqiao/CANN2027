"""Granularity fault injection to toggle between coarse and fine simulations."""
from enum import Enum
from random import random
from typing import Iterable, List


class Granularity(Enum):
    COARSE = "coarse"
    FINE = "fine"


def apply_noise(value: float, granularity: Granularity) -> float:
    """Apply synthetic noise to a value based on the granularity."""
    factor = 0.1 if granularity is Granularity.COARSE else 0.01
    return value + (random() * factor)


def apply_noise_series(
    values: Iterable[float], granularity: Granularity
) -> List[float]:
    """Vectorized helper to process a batch of values with consistent noise."""
    return [apply_noise(value, granularity) for value in values]


def stuck_at_fault(value: float, stuck_value: float = 0.0) -> float:
    """Force a value to a stuck-at condition for digital-line testing."""
    return stuck_value if value != stuck_value else value + 1e-3


def jitter_series(values: Iterable[float], amplitude: float = 0.02) -> List[float]:
    """Introduce bounded jitter across a sequence for timing noise simulation."""
    return [value + (random() - 0.5) * amplitude for value in values]
