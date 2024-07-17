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


def main():
    # print(sys.argv)
    constellation_type = ConstellationType.WALKER_DELTA
    num_planes = 2
    num_sats_per_plane = 2

    if constellation_type == ConstellationType.FILL and num_planes != 1:
        raise Exception("Fill type must have a single plane")

    initial_orbit = Orbit(
        semi_major_axis=500,
        eccentricity=0,
        inclination=45,
        right_ascension_of_the_ascending_node=0,
        argument_of_perigee=0,
        mean_anomaly=0,
    )

    # Adjust the mean anomaly to evenly space satellites in the same plane
    mean_anomaly_spacing = 360 / num_sats_per_plane
    mean_anomaly_offset = initial_orbit.mean_anomaly

    right_ascension_of_the_ascending_node_offset = initial_orbit.right_ascension_of_the_ascending_node

    orbits = []
    for plane_idx in range(num_planes):
        for sat_idx in range(num_sats_per_plane):
            orbit = copy.deepcopy(initial_orbit)
            orbit.mean_anomaly = sat_idx * mean_anomaly_spacing + mean_anomaly_offset

            if constellation_type == ConstellationType.WALKER_STAR:
                assert initial_orbit.inclination == 90

                right_ascension_of_the_ascending_node_spacing = (360 / 2) / num_planes
                orbit.right_ascension_of_the_ascending_node = (plane_idx
                                                               * right_ascension_of_the_ascending_node_spacing
                                                               + right_ascension_of_the_ascending_node_offset)
            elif constellation_type == ConstellationType.WALKER_DELTA:
                assert initial_orbit.inclination == 45

                right_ascension_of_the_ascending_node_spacing = 360 / num_planes
                orbit.right_ascension_of_the_ascending_node = (plane_idx
                                                               * right_ascension_of_the_ascending_node_spacing
                                                               + right_ascension_of_the_ascending_node_offset)
            elif constellation_type == ConstellationType.FILL:
                pass

            orbits.append(orbit)

    pprint.pprint(orbits)


if __name__ == "__main__":
    main()
