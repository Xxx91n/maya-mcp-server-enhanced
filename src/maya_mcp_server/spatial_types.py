"""Type definitions for spatial scene data."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DetailLevel(str, Enum):
    """Detail level for scene graph queries."""

    COMPACT = "compact"  # name, type, position, bbox, child_count
    STANDARD = "standard"  # compact + material, vertex/face count
    FULL = "full"  # standard + vertices, normals, UVs (single object)


class MeasureMode(str, Enum):
    """Mode for spatial measurements."""

    CENTER = "center"  # center-to-center distance
    SURFACE = "surface"  # closest surface point distance
    CLEARANCE = "clearance"  # gap/clearance distance
    BBOX = "bbox"  # bounding box overlap detection


class NodeType(str, Enum):
    """Scene node type classification."""

    MESH = "mesh"
    CAMERA = "camera"
    LIGHT = "light"
    GROUP = "group"
    CURVE = "curve"
    LOCATOR = "locator"
    JOINT = "joint"
    UNKNOWN = "unknown"


@dataclass
class SceneObject:
    """Compact representation of a scene object."""

    name: str
    node_type: NodeType
    position: list[float]  # [x, y, z]
    bbox_min: list[float]  # [x, y, z]
    bbox_max: list[float]  # [x, y, z]
    child_count: int = 0
    material: str | None = None
    vertex_count: int | None = None
    face_count: int | None = None
    parent: str | None = None


@dataclass
class ZoneInfo:
    """Information about a spatial zone/region."""

    name: str
    pattern_matched: str
    objects: list[str]  # object names in this zone
    bbox_min: list[float] = field(default_factory=lambda: [0, 0, 0])
    bbox_max: list[float] = field(default_factory=lambda: [0, 0, 0])
    center: list[float] = field(default_factory=lambda: [0, 0, 0])
    object_count: int = 0


@dataclass
class SpatialRelation:
    """Spatial relationship between two objects."""

    obj_a: str
    obj_b: str
    distance: float
    mode: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class SceneGraph:
    """Complete scene graph with metadata."""

    objects: list[SceneObject]
    zones: list[ZoneInfo]
    stats: dict[str, Any]
    unit: str = "cm"
    up_axis: str = "y"


@dataclass
class MeasurementResult:
    """Result of a spatial measurement."""

    obj_a: str
    obj_b: str
    mode: str
    distance: float
    unit: str = "cm"
    bbox_overlap: bool = False
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class AssertionResult:
    """Result of a scene assertion check."""

    passed: bool
    mismatches: list[dict[str, Any]] = field(default_factory=list)
    checked_count: int = 0
    passed_count: int = 0
