# File: geodetic_example.py

from airports import *
from geodetic import *


LOWI_08_loc = runway_location(('LOWI', '08'))

print('LOWI Innsbruck airport runway 08:')

print('lat =', LOWI_08_loc.lat,
      'lon =', LOWI_08_loc.lon,
      'alt =', LOWI_08_loc.alt,
      'heading =', runway_heading(('LOWI', '08')))


print()


LOWI_26_loc = runway_location(('LOWI', '26'))

print('LOWI Innsbruck airport runway 26:')

print('lat =', LOWI_26_loc.lat,
      'lon =', LOWI_26_loc.lon,
      'alt =', LOWI_26_loc.alt,
      'heading =', runway_heading(('LOWI', '26')))


print()


print('runway length in feet:', LOWI_08_loc.distance(LOWI_26_loc))

print('bearing:', LOWI_08_loc.bearing(LOWI_26_loc))
