"""Layer-level fault injection utilities."""
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
