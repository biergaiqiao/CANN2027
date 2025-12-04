"""Propagation chain utilities to trace how injected faults manifest in metrics."""
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence


@dataclass
class PropagationLink:
    source: str
    target: str
    signal: str
    intensity: float


@dataclass
class PropagationResult:
    links: List[PropagationLink]
    impacted_metrics: Dict[str, float]

    def as_path(self) -> str:
        """Render a readable path representation of the propagation graph."""
        parts: List[str] = []
        for link in self.links:
            arrow = f"{link.source} -[{link.signal}:{link.intensity:.2f}]-> {link.target}"
            parts.append(arrow)
        if self.impacted_metrics:
            metrics = ", ".join(
                f"{name}={value:.3f}" for name, value in self.impacted_metrics.items()
            )
            parts.append(f"metrics: {metrics}")
        return "\n".join(parts)


def build_propagation(
    injections: Sequence[str],
    monitored_nodes: Sequence[str],
    attenuation: float = 0.8,
) -> List[PropagationLink]:
    """Build a deterministic link chain describing how faults travel downstream."""
    links: List[PropagationLink] = []
    previous = "input"
    for idx, injection in enumerate(injections):
        signal_strength = attenuation ** idx
        links.append(
            PropagationLink(
                source=previous,
                target=injection,
                signal="inject",
                intensity=signal_strength,
            )
        )
        previous = injection
    for monitor in monitored_nodes:
        links.append(
            PropagationLink(
                source=previous,
                target=monitor,
                signal="observe",
                intensity=attenuation ** (len(injections) + 1),
            )
        )
    return links


def summarize_propagation(
    links: Iterable[PropagationLink], metric_samples: Dict[str, float]
) -> PropagationResult:
    """Create a propagation summary with impacted metric values preserved."""
    return PropagationResult(links=list(links), impacted_metrics=dict(metric_samples))


def render_ascii_graph(links: Iterable[PropagationLink]) -> str:
    """Create a compact ASCII graph for quick visualization."""
    lines: List[str] = []
    for link in links:
        lines.append(
            f"{link.source} --{link.signal}({link.intensity:.2f})--> {link.target}"
        )
    return "\n".join(lines)
