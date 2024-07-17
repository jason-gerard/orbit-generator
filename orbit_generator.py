import sys
import copy
import pprint
from enum import Enum
from dataclasses import dataclass


class ConstellationType(Enum):
    WALKER_STAR = 1
    WALKER_DELTA = 2
    FILL = 3


@dataclass
class Orbit:
    semi_major_axis: float  # a, km
    eccentricity: float  # e
    inclination: float  # i, degrees
    right_ascension_of_the_ascending_node: float  # upper omega, degrees
    argument_of_perigee: float  # lower omega, degrees
    mean_anomaly: float  # v, degrees


