import copy
import time
import argparse
import csv
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


@dataclass
class SeedOrbit:
    name: str
    central_object: str
    constellation_type: ConstellationType
    num_planes: int
    num_sats_per_plane: int
    orbit: Orbit


@dataclass
class Constellation:
    name: str
    central_object: str
    orbits: list[Orbit]


def generate_orbits(
        initial_orbit: Orbit,
        constellation_type: ConstellationType,
        num_planes: int,
        num_sats_per_plane: int,
) -> list[Orbit]:
    if constellation_type == ConstellationType.FILL and num_planes != 1:
        raise Exception("Fill type must have a single plane")

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

    return orbits


def seed_orbit_csv_reader(file_name: str) -> list[SeedOrbit]:
    seed_orbits = []

    with open(f"./inputs/{file_name}", "r") as f:
        reader = csv.DictReader(f, delimiter=",")
        for row in reader:
            seed_orbit = SeedOrbit(
                name=row['name'],
                central_object=row['central_object'],
                constellation_type=ConstellationType[row['constellation_type']],
                num_sats_per_plane=int(row['num_sats_per_plane']),
                num_planes=int(row['num_planes']),
                orbit=Orbit(
                    semi_major_axis=float(row['semi_major_axis']),
                    eccentricity=float(row['eccentricity']),
                    inclination=float(row['inclination']),
                    right_ascension_of_the_ascending_node=float(row['right_ascension_of_the_ascending_node']),
                    argument_of_perigee=float(row['argument_of_perigee']),
                    mean_anomaly=float(row['mean_anomaly']),
                )
            )

            seed_orbits.append(seed_orbit)

    return seed_orbits


def constellation_csv_writer(file_name: str, constellations: list[Constellation]):
    NODE_TYPE = "Orbiter"

    header = ",".join([
        "node_type",
        "node_name",
        "id",
        "central_object",
        "semi_major_axis",
        "inclination",
        "eccentricity",
        "right_ascension_of_the_ascending_node",
        "argument_of_perigee",
        "mean_anomaly"
    ])

    with open(f"./outputs/{file_name}", "w") as f:
        f.write(f"#{header}\n")

        for constellation_idx, constellation in enumerate(constellations):
            f.write(f"#{constellation.name}\n")
            for orbit_idx, orbit in enumerate(constellation.orbits):
                node_name = f"c{constellation_idx+1}o{orbit_idx+1}"
                node_id = str(100 * (constellation_idx + 1) + orbit_idx + 1)
                line = ",".join([
                    NODE_TYPE,
                    node_name,
                    node_id,
                    constellation.central_object,
                    str(orbit.semi_major_axis),
                    str(orbit.inclination),
                    str(orbit.eccentricity),
                    str(orbit.right_ascension_of_the_ascending_node),
                    str(orbit.argument_of_perigee),
                    str(orbit.mean_anomaly),
                ])

                f.write(line + "\n")


def main(args):
    if args.file:
        file_name = args.file
        seed_orbits = seed_orbit_csv_reader(file_name)

        constellations = []
        for seed_orbit in seed_orbits:
            orbits = generate_orbits(
                seed_orbit.orbit,
                seed_orbit.constellation_type,
                seed_orbit.num_planes,
                seed_orbit.num_sats_per_plane
            )

            constellations.append(Constellation(
                name=seed_orbit.name,
                central_object=seed_orbit.central_object,
                orbits=orbits,
            ))
    else:
        constellation_type = ConstellationType[args.constellation_type]
        num_planes = int(args.num_planes)
        num_sats_per_plane = int(args.num_sats_per_plane)

        initial_orbit = Orbit(
            semi_major_axis=float(args.semi_major_axis),
            eccentricity=float(args.eccentricity),
            inclination=float(args.inclination),
            right_ascension_of_the_ascending_node=float(args.right_ascension_of_the_ascending_node),
            argument_of_perigee=float(args.argument_of_perigee),
            mean_anomaly=float(args.mean_anomaly),
        )

        orbits = generate_orbits(initial_orbit, constellation_type, num_planes, num_sats_per_plane)

        file_name = f"{int(time.time())}.csv"
        constellations = [Constellation(
            name="constellation",
            central_object="Earth",
            orbits=orbits,
        )]

    constellation_csv_writer(file_name, constellations)


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

    parser.add_argument('-f', '--file', help='File input name to generate orbit scenario from')

    args = parser.parse_args()

    main(args)
