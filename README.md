# orbit-generator
Utility program that can generate orbits for a constellation given a seen orbit.

## Usage
After installing the dependencies you can run the utility by passing in the type of constellation and the initial orbital parameters. The follow call will produce eight orbits across two planes, with four satellites evenly spaced in each plane.
```
python3 orbit_generator.py -type WALKER_DELTA -sats 4 -planes 2 -a 500 -e 0 -i 45 -raan 0 -w 0 -v 0
```

Examples of some other common orbits
```
python3 orbit_generator.py -type WALKER_DELTA -sats 16 -planes 8 -a 500 -e 0 -i 45 -raan 0 -w 0 -v 0

python3 orbit_generator.py -type WALKER_STAR -sats 4 -planes 8 -a 500 -e 0 -i 90 -raan 0 -w 0 -v 0

python3 orbit_generator.py -type WALKER_STAR -sats 4 -planes 2 -a 1500 -e 0 -i 90 -raan 0 -w 0 -v 0

python3 orbit_generator.py -type EQUATORIAL -sats 12 -planes 1 -a 35786 -e 0 -i 0 -raan 0 -w 0 -v 0
```

You can use a file as input for doing larger scenarios. Look at the `cislunar_scenario.csv` file in the `/inputs` folder for an example of a three constellation communication scenario, with two constellation orbiting the Moon and one orbiting Earth. This is an example deployment of LunaNet.
```
python3 orbit_generator.py -f cislunar_scenario.csv
```

You can see what the different parameters mean with the help command
```
python3 orbit_generator.py --help
```

## References
This is a good website to test out your seed orbit, [https://orbitalmechanics.info/](https://orbitalmechanics.info/). It lets you visualize what it will look like, around Earth at least.