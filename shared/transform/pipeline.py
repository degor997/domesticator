from __future__ import annotations

import logging
from typing import Any

from shared.transform.transformers import TRANSFORM_REGISTRY

logger = logging.getLogger(__name__)


def _parse_transform(step: str | dict[str, Any]) -> tuple[str, dict[str, Any]]:
    if isinstance(step, str):
        return step, {}
    name = step["name"]
    kwargs = {k: v for k, v in step.items() if k != "name"}
    return name, kwargs


def apply_transforms(value: Any, transforms: list[str | dict[str, Any]]) -> Any:
    for step in transforms:
        name, kwargs = _parse_transform(step)
        func = TRANSFORM_REGISTRY.get(name)
        if func is None:
            logger.warning("Unknown transform: %s", name)
            continue
        try:
            if kwargs:
                value = func(value, **kwargs)
            else:
                value = func(value)
        except Exception:
            logger.exception("Transform %s failed on value %r", name, value)
            return None
    return value
