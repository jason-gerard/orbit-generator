import copy
import pprint
import argparse
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
    right_ascension_of_the_ascending_node: float  # omega, degrees
    argument_of_perigee: float  # w, degrees
    mean_anomaly: float  # v, degrees


def generate_orbits(args):
    constellation_type = ConstellationType[args.constellation_type]
    num_planes = int(args.num_planes)
    num_sats_per_plane = int(args.num_sats_per_plane)

    if constellation_type == ConstellationType.FILL and num_planes != 1:
        raise Exception("Fill type must have a single plane")

    initial_orbit = Orbit(
        semi_major_axis=float(args.semi_major_axis),
        eccentricity=float(args.eccentricity),
        inclination=float(args.inclination),
        right_ascension_of_the_ascending_node=float(args.right_ascension_of_the_ascending_node),
        argument_of_perigee=float(args.argument_of_perigee),
        mean_anomaly=float(args.mean_anomaly),
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
    parser = argparse.ArgumentParser()

    parser.add_argument('-type', '--constellation_type', help='WALKER_DELTA, WALKER_STAR, FILL')
    parser.add_argument('-sats', '--num_sats_per_plane', help='The number of satellites per orbital plane')
    parser.add_argument('-planes', '--num_planes', help='The number of orbital plans to generate')

    parser.add_argument('-a', '--semi_major_axis', help='a, km')
    parser.add_argument('-e', '--eccentricity', help='e')
    parser.add_argument('-i', '--inclination', help='i, degrees')
    parser.add_argument('-raan', '--right_ascension_of_the_ascending_node', help='omega, degrees')
    parser.add_argument('-w', '--argument_of_perigee', help='w, degrees')
    parser.add_argument('-v', '--mean_anomaly', help='v, degrees')

    args = parser.parse_args()

    generate_orbits(args)
