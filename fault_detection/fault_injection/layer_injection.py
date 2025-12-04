
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Tuple


@dataclass
class LayerFault:
    layer_name: str
    perturbation: Callable[[float], float]
    description: str = ""


def inject_fault(weights: Dict[str, float], fault: LayerFault) -> Dict[str, float]:
    """Apply a perturbation to a single layer's weights for testing.

    The function returns a new weight dictionary so that call sites can keep the
    pristine copy for comparison. If the layer is missing, the original weights
    are returned unchanged.
    """
    mutated = weights.copy()
    if fault.layer_name in mutated:
        mutated[fault.layer_name] = fault.perturbation(mutated[fault.layer_name])
    return mutated


def apply_faults(
    weights: Dict[str, float], faults: Iterable[LayerFault]
) -> Tuple[Dict[str, float], List[str]]:
    """Sequentially apply multiple layer faults and report what changed."""
    mutated = weights.copy()
    applied: List[str] = []
    for fault in faults:
        if fault.layer_name not in mutated:
            continue
        mutated[fault.layer_name] = fault.perturbation(mutated[fault.layer_name])
        summary = fault.description or "layer fault"
        applied.append(f"{fault.layer_name}: {summary}")
    return mutated, applied


def bit_flip_fault(bit_position: int) -> LayerFault:
    """Create a deterministic bit-flip perturbation for a layer."""

    def _flip(value: float) -> float:
        as_int = int(value)
        return float(as_int ^ (1 << bit_position))

    return LayerFault(
        layer_name=f"layer_{bit_position}",
        perturbation=_flip,
        description=f"bit flip at position {bit_position}",
    )


def scale_fault(layer_name: str, factor: float) -> LayerFault:
    """Create a multiplicative scaling fault for sensitivity testing."""

    def _scale(value: float) -> float:
        return value * factor

    return LayerFault(
        layer_name=layer_name,
        perturbation=_scale,
        description=f"scaled by {factor}",
    )
