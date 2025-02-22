# File: airports.py

from geodetic import Location


# Creates a Runway

class Runway:

    def __init__(self, name, reverse, location):

        # name: name of runway
        # reverse: name of reverse runway
        # location: Location giving latitude, longitude, and altitude

        self.name = name
        self.reverse = reverse
        self.location = location


# Creates an Airport

class Airport:

    def __init__(self, name, runways):

        # name: name of airport
        # runways: dictionnary of runways

        self.name = name
        self.runways = runways

    def runway_heading(self, name):

        # name: name of runway

        return self.runways[name].location.bearing(self.runways[self.runways[name].reverse].location)

    def runway_length(self, name):

        # name: name of runway

        return self.runways[name].location.distance(self.runways[self.runways[name].reverse].location)


airports = {

  # KSEA Seattle Tacoma International
  'KSEA': Airport('KSEA', {
                  '16L':
                     Runway('16L',
                            '34R',
                            Location(47.46379733, -122.30775222, 433)),
                  '34R':
                     Runway('34R',
                            '16L',
                            Location(47.43117533, -122.30804122, 347)),
                  '16C':
                     Runway('16C',
                            '34C',
                            Location(47.46381133, -122.31098822, 430)),
                  '34C':
                     Runway('34C',
                            '16C',
                            Location(47.43797233, -122.31121322, 363)),
                  '16R':
                     Runway('16R',
                            '34L',
                            Location(47.46383763, -122.31786263, 415)),
                  '34L':
                     Runway('34L',
                            '16R',
                            Location(47.44053695, -122.31806463, 356))
                  }),

  # KBFI Boeing Field King Co Intl
  'KBFI': Airport('KBFI', {
                  '13L':
                     Runway('13L',
                            '31R',
                            Location(47.53799292, -122.30746100, 18)),
                  '31R':
                     Runway('31R',
                            '13L',
                            Location(47.52916792, -122.30000000, 17)),
                  '13R':
                     Runway('13R',
                            '31L',
                            Location(47.54051792, -122.31135600, 17)),
                  '31L':
                     Runway('31L',
                            '13R',
                            Location(47.51672592, -122.29124200, 21))
                  }),

  # KRNT Renton Muni
  'KRNT': Airport('KRNT', {
                  '16':
                     Runway('16',
                            '34',
                            Location(47.50047200, -122.21685300, 24)),
                  '34':
                     Runway('34',
                            '16',
                            Location(47.48579400, -122.21463300, 32))
                  }),

  # KTCM McChord Air Force Base
  'KTCM': Airport('KTCM', {
                  '16':
                     Runway('16',
                            '34',
                            Location(47.15150600, -122.47655000, 286)),
                  '34':
                     Runway('34',
                            '16',
                            Location(47.12381400, -122.47638100, 322))
                  }),

  # S36 Crest Airpark
  'S36':  Airport('S36', {
                  '15':
                     Runway('15',
                            '33',
                            Location(47.34154700, -122.10457500, 472)),
                  '33':
                     Runway('33',
                            '15',
                            Location(47.33264400, -122.10249700, 472))
                  }),

  # S50 Auburn Muni
  'S50':  Airport('S50', {
                  '16':
                     Runway('16',
                            '34',
                            Location(47.33234200, -122.22670300, 63)),
                  '34':
                     Runway('34',
                            '16',
                            Location(47.32302800, -122.22660600, 63))
                  }),

  # LOWI Innsbruck (Austria)
  'LOWI':  Airport('LOWI', {
                   '08':
                      Runway('08',
                             '26',
                             Location(47.258888, 11.331700, 1915)),
                   '26':
                      Runway('26',
                             '08',
                             Location(47.261625, 11.357035, 1915))
                   }),

  # LOIJ Sankt Johann Airfield (Austria)
  'LOIJ':  Airport('LOIJ', {
                   '13':
                      Runway('13',
                             '31',
                             Location(47.522435, 12.445863, 2210)),
                   '31':
                      Runway('31',
                             '13',
                             Location(47.518256, 12.452785, 2210))
                   }),

}


def runway_heading(airport_and_runway):
    airport = airport_and_runway[0]
    runway = airport_and_runway[1]
    return airports[airport].runway_heading(runway)

def runway_length(airport_and_runway):
    airport = airport_and_runway[0]
    runway = airport_and_runway[1]
    return airports[airport].runway_length(runway)

def runway_location(airport_and_runway):
    airport = airport_and_runway[0]
    runway = airport_and_runway[1]
    return airports[airport].runways[runway].location

def closest_runway(loc):
    min_dist = float("+inf")
    min_rw = None
    for airport in airports:
        for runway in airports[airport].runways:
            rw = (airport, runway)
            d = runway_location(rw).distance(loc)
            if (d < min_dist):
                min_dist = d
                min_rw = rw
    return min_rw
