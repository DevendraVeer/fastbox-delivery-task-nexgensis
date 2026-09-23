"""
These are data models for the three main entities used in the simulation.
Dataclasses make it easier to work with these objects instead of using
raw dictionaries or tuples throughout the code.
"""

from dataclasses import dataclass, field
from typing import Tuple, List


@dataclass
class Warehouse:
    id: str
    location: Tuple[float, float]


@dataclass
class Agent:
    id: str
    location: Tuple[float, float]          # Current position (it updates as the agent moves during simulation)
    start_location: Tuple[float, float]    # Starting position (it is frozen, used for the assignment phase)
    assigned_packages: List[str] = field(default_factory=list)
    total_distance: float = 0.0
    packages_delivered: int = 0
    route_log: List[str] = field(default_factory=list)  # This stores the agent's route (used by --verbose and ASCII map)


@dataclass
class Package:
    id: str
    warehouse_id: str
    destination: Tuple[float, float]
    delivered: bool = False
    delay: float = 0.0   # Delay in minutes
