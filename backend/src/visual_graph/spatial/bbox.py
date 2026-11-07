"""Bounding-box representation used by the spatial relationship engine.

Coordinates follow the image convention: the origin is the top-left corner,
``x`` grows to the right and ``y`` grows downward.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


class InvalidBoundingBoxError(ValueError):
    """Raised when bounding-box coordinates do not describe a valid box."""


@dataclass(frozen=True, slots=True)
class BoundingBox:
    """Axis-aligned bounding box with strictly positive width and height."""

    x_min: float
    y_min: float
    x_max: float
    y_max: float

    def __post_init__(self) -> None:
        coords = (self.x_min, self.y_min, self.x_max, self.y_max)
        for value in coords:
            if isinstance(value, bool) or not isinstance(value, int | float):
                raise InvalidBoundingBoxError(f"coordinates must be numbers, got {value!r}")
            if not math.isfinite(value):
                raise InvalidBoundingBoxError(f"coordinates must be finite, got {value!r}")
        if self.x_max <= self.x_min:
            raise InvalidBoundingBoxError(
                f"x_max ({self.x_max}) must be greater than x_min ({self.x_min})"
            )
        if self.y_max <= self.y_min:
            raise InvalidBoundingBoxError(
                f"y_max ({self.y_max}) must be greater than y_min ({self.y_min})"
            )

    @property
    def width(self) -> float:
        return self.x_max - self.x_min

    @property
    def height(self) -> float:
        return self.y_max - self.y_min

    @property
    def area(self) -> float:
        return self.width * self.height

    @property
    def center_x(self) -> float:
        return (self.x_min + self.x_max) / 2

    @property
    def center_y(self) -> float:
        return (self.y_min + self.y_max) / 2
