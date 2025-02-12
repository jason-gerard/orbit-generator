import copy
import time
import argparse
import csv
import constants
import random
from enum import Enum
from dataclasses import dataclass


class ConstellationType(Enum):
    WALKER_STAR = 1
    WALKER_DELTA = 2
    EQUATORIAL = 3


@dataclass
class Orbit:
    altitude: float  # a, km
    eccentricity: float  # e
    inclination: float  # i, degrees
    right_ascension_of_the_ascending_node: float  # omega, degrees
    argument_of_perigee: float  # w, degrees
    mean_anomaly: float  # v, degrees


@dataclass
class SeedOrbit:
    name: str
    central_object: str
    rules: list[str]
    constellation_type: ConstellationType
    num_planes: int
    num_sats_per_plane: int
    orbit: Orbit


@dataclass
class Constellation:
    name: str
    central_object: str
    rules: list[str]
    orbits: list[Orbit]


@dataclass
class GSPosition:
    latitude: float
    longitude: float
    altitude: float

@dataclass
class GSPositions:
    name: str
    central_object: str
    positions: list[GSPosition]


def generate_orbits(
        initial_orbit: Orbit,
        constellation_type: ConstellationType,
        num_planes: int,
        num_sats_per_plane: int,
) -> list[Orbit]:
    if constellation_type == ConstellationType.EQUATORIAL and num_planes != 1:
        raise Exception("EQUATORIAL type must have a single plane")

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
                right_ascension_of_the_ascending_node_spacing = 360 / num_planes
                orbit.right_ascension_of_the_ascending_node = (plane_idx
                                                               * right_ascension_of_the_ascending_node_spacing
                                                               + right_ascension_of_the_ascending_node_offset)
            elif constellation_type == ConstellationType.EQUATORIAL:
                pass

            orbits.append(orbit)

    return orbits


def seed_orbit_csv_reader(file_name: str) -> list[SeedOrbit]:
    seed_orbits = []

    with open(f"./inputs/{file_name}", "r") as f:
        sections = f.read().split("\n\n")

        # Constellation section goes first
        reader = csv.DictReader(sections[0].split("\n"), delimiter=",")
        for row in reader:
            seed_orbit = SeedOrbit(
                name=row['name'],
                central_object=row['central_object'],
                rules=row['rules'].split(constants.RULE_SEPARATOR),
                constellation_type=ConstellationType[row['constellation_type']],
                num_sats_per_plane=int(row['num_sats_per_plane']),
                num_planes=int(row['num_planes']),
                orbit=Orbit(
                    altitude=float(row['altitude']),
                    eccentricity=float(row['eccentricity']),
                    inclination=float(row['inclination']),
                    right_ascension_of_the_ascending_node=float(row['right_ascension_of_the_ascending_node']),
                    argument_of_perigee=float(row['argument_of_perigee']),
                    mean_anomaly=float(row['mean_anomaly']),
                )
            )

            seed_orbits.append(seed_orbit)

    return seed_orbits


def seed_gs_position_reader(file_name: str) -> GSPositions | None:
    gs_positions = []

    latitude_upper = 90.0
    latitude_lower = -90.0
    longitude_upper = 180.0
    longitude_lower = -180.0

    with open(f"./inputs/{file_name}", "r") as f:
        sections = f.read().split("\n\n")
        if len(sections) == 1:
            return

        reader = csv.DictReader(sections[1].split("\n"), delimiter=",")
        for row in reader:
            gs_altitude = row['altitude']
            num_gs = row['num_gs']

            for _ in range(int(num_gs)):
                gs_positions.append(GSPosition(
                    altitude=gs_altitude,
                    latitude=int(random.uniform(latitude_lower, latitude_upper)),
                    longitude=int(random.uniform(longitude_lower, longitude_upper)),
                ))

            gs = GSPositions(
                name=row['name'],
                central_object=row['central_object'],
                positions=gs_positions
            )

    return gs


def constellation_csv_writer(file_name: str, constellations: list[Constellation]):
    header = ",".join([
        "node_type",
        "node_name",
        "id",
        "central_object",
        "altitude",
        "inclination",
        "eccentricity",
        "right_ascension_of_the_ascending_node",
        "argument_of_perigee",
        "mean_anomaly",
        "rules",
    ])

    with open(f"./outputs/{file_name}", "w") as f:
        f.write(f"#{header}\n")

        for constellation_idx, constellation in enumerate(constellations):
            f.write(f"#{constellation.name}\n")
            for orbit_idx, orbit in enumerate(constellation.orbits):
                node_name = f"c{constellation_idx+1}o{orbit_idx+1}"
                # TODO: This node_id generator only support constellations up to size 1,000 before spilling over into the next
                # constellation, this should be changes such that we can encode the planet, constellation, and a unique
                # node id into the value.
                node_id = str(1000 * (constellation_idx + 1) + orbit_idx + 1)
                line = ",".join([
                    constants.NODE_TYPE,
                    node_name,
                    node_id,
                    constellation.central_object,
                    str(orbit.altitude),
                    str(orbit.inclination),
                    str(orbit.eccentricity),
                    str(orbit.right_ascension_of_the_ascending_node),
                    str(orbit.argument_of_perigee),
                    str(orbit.mean_anomaly),
                    constants.RULE_SEPARATOR.join(constellation.rules)
                ])

                f.write(line + "\n")

def gs_csv_writer(file_name: str, gs_positions: GSPositions):
    header = ",".join([
        "node_type",
        "node_name",
        "id",
        "central_object",
        "latitude",
        "longitude",
        "altitude",
        "rules",
    ])

    with open(f"./outputs/{file_name}", "a") as f:
        f.write(f"#{header}\n")

        f.write(f"#{gs_positions.name}\n")
        for gs_idx, gs in enumerate(gs_positions.positions):
            node_name = f"gs{gs_idx+1}"
            node_id = str(9000 + gs_idx + 1)
            line = ",".join([
                constants.LANDER_TYPE,
                node_name,
                node_id,
                gs_positions.central_object,
                str(gs.latitude),
                str(gs.longitude),
                str(gs.altitude),
                "",
            ])

            f.write(line + "\n")


def incremental_scenarios(file_name):
    # Static Earth assets
    ground_stations = GSPositions(
        name="Earth ground stations",
        central_object="Earth",
        positions=[
            # Goldstone
            GSPosition(
                altitude=100,
                latitude=35.426667,
                longitude=-116.89,
            ),
            # Madrid
            GSPosition(
                altitude=100,
                latitude=40.431389,
                longitude=-4.248056,
            ),
            # Canberra
            GSPosition(
                altitude=100,
                latitude=-35.401389,
                longitude=148.981667,
            ),
        ]
    )

    # Dynamic deep-space assets
    min_source_nodes = 4
    max_source_nodes = 64
    num_planes = 4

    for num_source_nodes in range(min_source_nodes, max_source_nodes+1, 4):
        mars_seed_orbit = SeedOrbit(
            name="Mars constellation",
            central_object="Mars",
            rules=[],
            constellation_type=ConstellationType.WALKER_STAR,
            num_sats_per_plane=int(num_source_nodes/num_planes),
            num_planes=num_planes,
            orbit=Orbit(
                altitude=500,
                eccentricity=0,
                inclination=90,
                right_ascension_of_the_ascending_node=0,
                argument_of_perigee=0,
                mean_anomaly=0,
            )
        )

        mars_constellation = Constellation(
            name=mars_seed_orbit.name,
            central_object=mars_seed_orbit.central_object,
            rules=mars_seed_orbit.rules,
            orbits=generate_orbits(
                mars_seed_orbit.orbit,
                mars_seed_orbit.constellation_type,
                mars_seed_orbit.num_planes,
                mars_seed_orbit.num_sats_per_plane,
            ),
        )

        earth_relay_seed_orbit = SeedOrbit(
            name="Earth constellation",
            central_object="Earth",
            rules=[],
            constellation_type=ConstellationType.EQUATORIAL,
            num_sats_per_plane=1+int((num_source_nodes-1)/16),
            num_planes=1,
            orbit=Orbit(
                altitude=5000.0,
                eccentricity=0,
                inclination=0,
                right_ascension_of_the_ascending_node=0,
                argument_of_perigee=0,
                mean_anomaly=0,
            )
        )

        earth_relay_constellation = Constellation(
            name=earth_relay_seed_orbit.name,
            central_object=earth_relay_seed_orbit.central_object,
            rules=earth_relay_seed_orbit.rules,
            orbits=generate_orbits(
                earth_relay_seed_orbit.orbit,
                earth_relay_seed_orbit.constellation_type,
                earth_relay_seed_orbit.num_planes,
                earth_relay_seed_orbit.num_sats_per_plane,
            ),
        )

        constellations = [earth_relay_constellation, mars_constellation]

        output_filename = f"{file_name.split('.')[0]}_{num_source_nodes}.csv"
        constellation_csv_writer(output_filename, constellations)
        gs_csv_writer(output_filename, ground_stations)


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
                rules=seed_orbit.rules,
                orbits=orbits,
            ))

        gs = seed_gs_position_reader(file_name)
    else:
        constellation_type = ConstellationType[args.constellation_type]
        num_planes = int(args.num_planes)
        num_sats_per_plane = int(args.num_sats_per_plane)

        initial_orbit = Orbit(
            altitude=float(args.altitude),
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
            rules=[],
            orbits=orbits,
        )]

        gs = None

    constellation_csv_writer(file_name, constellations)

    if gs:
        gs_csv_writer(file_name, gs)


if __name__ == "__main__":
    random.seed(42)

    parser = argparse.ArgumentParser()

    parser.add_argument('-type', '--constellation_type', help='WALKER_DELTA, WALKER_STAR, EQUATORIAL')
    parser.add_argument('-sats', '--num_sats_per_plane', help='The number of satellites per orbital plane')
    parser.add_argument('-planes', '--num_planes', help='The number of orbital plans to generate')

    parser.add_argument('-a', '--altitude', help='a, km')
    parser.add_argument('-e', '--eccentricity', help='e')
    parser.add_argument('-i', '--inclination', help='i, degrees')
    parser.add_argument('-raan', '--right_ascension_of_the_ascending_node', help='omega, degrees')
    parser.add_argument('-w', '--argument_of_perigee', help='w, degrees')
    parser.add_argument('-v', '--mean_anomaly', help='v, degrees')

    parser.add_argument('-f', '--file', help='File input name to generate orbit scenario from')

    parser.add_argument('-if', '--ifile', help='File input name to generate incremental orbit scenario from')

    args = parser.parse_args()

    if args.ifile:
        incremental_scenarios(args.ifile)
    else:
        main(args)
