"""Model loader utilities for both main and monitoring models."""
from importlib import import_module
from pathlib import Path
from typing import Any, Type, Union


class ModelLoader:
    def __init__(
        self, module_path: str, class_name: str, weights_path: Union[Path, str]
    ):
        self.module_path = module_path
        self.class_name = class_name
        self.weights_path = Path(weights_path)

    def _resolve_class(self) -> Type[Any]:
        module = import_module(self.module_path)
        return getattr(module, self.class_name)

    def load(self) -> Any:
        model_cls = self._resolve_class()
        instance = model_cls(self.weights_path)
        if hasattr(instance, "load_weights"):
            instance.load_weights()
        return instance

    def exists(self) -> bool:
        """Quick check to validate that weights are present on disk."""
        return self.weights_path.exists()
