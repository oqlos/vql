# ShapeRegistry - extracted from shapes.py
"""
Shape generators — geometry for all supported shapes.

Each shape is a registered ShapeGenerator that produces point groups.
New shapes can be added via ShapeRegistry.register() (Open/Closed Principle).
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import Any


PointGroup = list[tuple[float, float]]
from vql.drawing.arrow_generator import ArrowGenerator
from vql.drawing.bird_generator import BirdGenerator
from vql.drawing.boat_generator import BoatGenerator
from vql.drawing.butterfly_generator import ButterflyGenerator
from vql.drawing.car_generator import CarGenerator
from vql.drawing.castle_generator import CastleGenerator
from vql.drawing.cat_generator import CatGenerator
from vql.drawing.circle_generator import CircleGenerator
from vql.drawing.cloud_detailed_generator import CloudDetailedGenerator
from vql.drawing.crescent_generator import CrescentGenerator
from vql.drawing.cross_generator import CrossGenerator
from vql.drawing.diamond_generator import DiamondGenerator
from vql.drawing.dot_generator import DotGenerator
from vql.drawing.ellipse_generator import EllipseGenerator
from vql.drawing.fish_generator import FishGenerator
from vql.drawing.flower_generator import FlowerGenerator
from vql.drawing.grid_generator import GridGenerator
from vql.drawing.heart_generator import HeartGenerator
from vql.drawing.hexagon_generator import HexagonGenerator
from vql.drawing.house_generator import HouseGenerator
from vql.drawing.line_generator import LineGenerator
from vql.drawing.mountain_generator import MountainGenerator
from vql.drawing.octagon_generator import OctagonGenerator
from vql.drawing.pentagon_generator import PentagonGenerator
from vql.drawing.rectangle_generator import RectangleGenerator
from vql.drawing.rocket_generator import RocketGenerator
from vql.drawing.shape_generator import ShapeGenerator
from vql.drawing.spiral_generator import SpiralGenerator
from vql.drawing.square_generator import SquareGenerator
from vql.drawing.star_generator import StarGenerator
from vql.drawing.sun_generator import SunGenerator
from vql.drawing.tree_generator import TreeGenerator
from vql.drawing.triangle_generator import TriangleGenerator
from vql.drawing.wave_generator import WaveGenerator

class ShapeRegistry:
    """
    Registry of all available shape generators.

    New shapes can be added at runtime via register().
    This follows the Open/Closed Principle — the registry is open for
    extension but closed for modification.
    """

    _generators: dict[str, ShapeGenerator] = {}

    @classmethod
    def register(cls, generator: ShapeGenerator) -> None:
        """Register a shape generator."""
        cls._generators[generator.name] = generator

    @classmethod
    def get(cls, name: str) -> ShapeGenerator:
        """Get a shape generator by name. Falls back to circle."""
        if not cls._generators:
            cls._init_defaults()
        gen = cls._generators.get(name)
        if gen is None:
            gen = cls._generators.get("circle", CircleGenerator())
        return gen

    @classmethod
    def available(cls) -> list[str]:
        """List all registered shape names."""
        if not cls._generators:
            cls._init_defaults()
        return sorted(cls._generators.keys())

    @classmethod
    def _init_defaults(cls) -> None:
        """Register all built-in shape generators."""
        for gen_class in [
            # Basic shapes
            CircleGenerator, EllipseGenerator, RectangleGenerator, SquareGenerator,
            TriangleGenerator, StarGenerator, HeartGenerator, SpiralGenerator,
            HouseGenerator, FlowerGenerator, SunGenerator, TreeGenerator,
            LineGenerator, DotGenerator, GridGenerator, WaveGenerator,
            # Complex shapes
            CarGenerator, BirdGenerator, ButterflyGenerator, BoatGenerator,
            MountainGenerator, CatGenerator, FishGenerator, RocketGenerator,
            CastleGenerator, DiamondGenerator, ArrowGenerator,
            # Geometric shapes
            PentagonGenerator, HexagonGenerator, OctagonGenerator,
            CrossGenerator, CrescentGenerator, CloudDetailedGenerator,
        ]:
            cls.register(gen_class())
