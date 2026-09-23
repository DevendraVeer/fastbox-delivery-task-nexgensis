"""
This calculates the Euclidean distance between two points.
Uses math.sqrt since the simulation only works with 2D coordinates.
"""


import math
from typing import Tuple


def euclidean_distance(point_a: Tuple[float, float], point_b: Tuple[float, float]) -> float:

    
    #Straight-line distance between two (x, y) points.
    return math.sqrt((point_a[0] - point_b[0]) ** 2 + (point_a[1] - point_b[1]) ** 2)
