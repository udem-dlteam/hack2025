# File: geodetic.py

import math


def feet_to_meters(x):
    return x * 0.3048 # meters per foot


def deg2rad(deg):
    # Converts degrees to radians.
    return deg*math.pi/180


def rad2deg(rad):
    # Converts radians to degrees.
    return rad*180/math.pi


def heading_diff(heading1, heading2):
    # Given two headings in degrees, returns the difference
    # in the range -180..+180.
    return (heading1 - heading2 + 180) % 360 - 180


# Creates a point on the earth's surface at the supplied latitude,
# longitude and altitude.

class Location:

    def __init__(self, lat, lon, alt=0):

        # lat: latitude in degrees
        # lon: longitude in degrees
        # alt: altitude in feet

        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.radius = 20925524.9 # radius of earth in feet

    def distance(self, other):

        # Returns the distance in feet from this point to the
        # other point.

        # other: the other Location to compute distance with

        lat1 = deg2rad(self.lat)
        lon1 = deg2rad(self.lon)
        lat2 = deg2rad(other.lat)
        lon2 = deg2rad(other.lon)

        v = (math.sin(lat1)*math.sin(lat2) +
             math.cos(lat1)*math.cos(lat2)*math.cos(lon1-lon2))

        r = self.radius + min(self.alt, other.alt)

        return math.sqrt((math.acos(max(-1, min(1, v))) * r)**2 +
                         (self.alt - other.alt)**2)

    def distance_haversine(self, other):

        # Returns the distance in feet from this point to the
        # other point. It is computed using the Haversine formula.

        # other: the other Location to compute distance with

        phi1 = deg2rad(self.lat)
        lambda1 = deg2rad(self.lon)
        phi2 = deg2rad(other.lat)
        lambda2 = deg2rad(other.lon)
        deltaphi = phi2 - phi1
        deltalambda = lambda2 - lambda1

        a = math.sin(deltaphi/2) * math.sin(deltaphi/2) + \
            math.cos(phi1) * math.cos(phi2) * \
            math.sin(deltalambda/2) * math.sin(deltalambda/2)

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        r = self.radius + min(self.alt, other.alt)

        return math.sqrt((c * r)**2 + (self.alt - other.alt)**2)

    def bearing(self, other):

        # Returns the bearing from this point to the
        # other point. The bearing is an angle from 0 to 360
        # degrees indicating the direction to travel to get to the
        # other point. 0 means "north", 90 is "east", 180 is "south"
        # and 270 is "west".

        # other: the Location to compute bearing to

        phi1 = deg2rad(self.lat)
        phi2 = deg2rad(other.lat)
        deltalambda = deg2rad(other.lon - self.lon)

        y = math.sin(deltalambda) * math.cos(phi2)
        x = (math.cos(phi1)*math.sin(phi2) -
             math.sin(phi1)*math.cos(phi2)*math.cos(deltalambda))
        theta = math.atan2(y, x)

        return rad2deg(theta) % 360

    def destination(self, bearing, dist):

        # Returns the point (Location) at a certain bearing
        # and distance from this point.

        # bearing: the bearing in degrees
        # dist: the distance in feet

        theta = deg2rad(bearing)
        d = dist / self.radius # angular distance in radians

        phi1 = deg2rad(self.lat)
        lambda1 = deg2rad(self.lon)

        phi2 = (math.asin(math.sin(phi1)*math.cos(d) +
                          math.cos(phi1)*math.sin(d)*math.cos(theta)))
        lambda2 = (lambda1 +
                   math.atan2(math.sin(theta)*math.sin(d)*math.cos(phi1),
                              math.cos(d)-math.sin(phi1)*math.sin(phi2)))
        lambda2 = (lambda2+3*math.pi) % (2*math.pi) - math.pi # normalise to -180..+180

        return Location(rad2deg(phi2), rad2deg(lambda2), self.alt)

    def interpolate(self, other, pos):

        # Finds the Location between this Location and the
        # other Location that is the interpolation at
        # position pos (between 0 and 1).

        def interpolate(start, end, pos):
            return start + (end-start)*pos

        return Location(interpolate(self.lat, other.lat, pos),
                        interpolate(self.lon, other.lon, pos),
                        interpolate(self.alt, other.alt, pos))

    def __repr__(self):
        return ('<Location lat=' + repr(self.lat) +
                ' lon=' + repr(self.lon) +
                ' alt=' + repr(self.alt) + '>')


# Creates a path, which is a sequence of locations.

class Path:

    def __init__(self, locations, tolerances=None):

        # locations: the list of Locations defining the path

        self.locations = locations
        if tolerances is None:
            self.tolerances = [0] * len(locations)
        else:
            self.tolerances = tolerances

    def length(self):

        # A Path that is composed of N Locations contains N-1 segments.
        # The length of a Path is the number of segments.

        return len(self.locations)-1

    def segment(self, i):

        # Returns the i'th segment of the Path. A segment is
        # a Path that has just two Locations.

        return Path(self.locations[i:i+2], self.tolerances[i:i+2])

    def distance(self):

        # Returns the distance of the path.

        result = 0

        for i in range(self.length()):
            result += self.locations[i].distance(self.locations[i+1])

        return result

    def segment_dist(self, loc):

        levels = math.ceil(math.log(max(4, self.distance()), 2))
        discretization = (1<<levels) - 2
        loc0 = self.locations[0]
        loc1 = self.locations[1]
        span = 1<<(levels-2)
        pos_index = (1<<(levels-1)) - 1

        def interpolate_dist(pos):
            return loc.distance(loc0.interpolate(loc1, pos))

        while span > 0:
            d0 = interpolate_dist(pos_index/discretization)
            d1 = interpolate_dist((pos_index+1)/discretization)
            if d0 < d1:
                pos_index -= span
            else:
                pos_index += span
            span >>= 1

        pos = pos_index / discretization
        return (pos, interpolate_dist(pos))

    def interpolate(self, pos):
        if pos <= 0:
            loc = self.locations[0]
            return Location(loc.lat, loc.lon, loc.alt)
        elif pos >= self.length():
            loc = self.locations[-1]
            return Location(loc.lat, loc.lon, loc.alt)
        else:
            i = math.floor(pos)
            return self.locations[i].interpolate(self.locations[i+1], pos-i)

    def polygon(self):

        # Returns a list of the Locations that define the contour
        # of the Path, taking into account the tolerance at each
        # Location of the Path.

        n = self.length()

        side1 = []
        side2 = []

        i = 0

        while i <= n:
            start = self.locations[i]
            tol = self.tolerances[i]
            j = i+1
            if i == n:
                end = start
                bearing = prev_bearing
            else:
                end = self.locations[j]
                while j < n and start.lat == self.locations[j].lat and start.lon == self.locations[j].lon:
                    j += 1
                bearing = start.bearing(self.locations[j])
            if i == 0 or i == n:
                if i == 0:
                    side1.append(start.destination(bearing, -tol))
                side1.append(start.destination(bearing-90, tol))
                side2.append(start.destination(bearing+90, tol))
                if i == n:
                    side2.append(start.destination(bearing, tol))
            else:
                turn = heading_diff(bearing, prev_bearing)
                if turn >= -1 and turn <= 1:
                    side1.append(start.destination(bearing-90, tol))
                    side2.append(start.destination(bearing+90, tol))
                else:
                    if turn > 0:
                        angle = prev_bearing-90
                        s1 = side1
                        s2 = side2
                    else:
                        angle = prev_bearing+90
                        s1 = side2
                        s2 = side1
                    s1.append(start.destination(angle, tol))
                    s1.append(start.destination(angle+turn/2, tol))
                    s1.append(start.destination(angle+turn, tol))
                    s2.append(start.destination(angle+turn/2, -tol/math.cos(deg2rad(max(-60, min(60, turn/2))))))
            prev_bearing = bearing
            i += 1

        side2.reverse()

        return Path(side1 + side2 + [side1[0]])  # make a closed path

    def to_kml(self, extrude_from_ground=False):

        # Returns a string that describes the Path in KML format.

        result = ''

        for i in range(self.length()+1):
            loc = self.locations[i]
            result += (str(loc.lon) + ',' +
                       str(loc.lat) + ',' +
                       str(feet_to_meters(loc.alt)) + '\n')

        return ("""\
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>

    <Style id="yellowLineGreenPoly">
      <LineStyle>
        <color>5f00ffff</color>
        <width>4</width>
      </LineStyle>
      <PolyStyle>
        <color>5f00ff00</color>
      </PolyStyle>
    </Style>

    <Placemark>
      <name>Flight path</name>
      <description>Flight path</description>
      <styleUrl>#yellowLineGreenPoly</styleUrl>
      <Polygon>
""" + ("""\
        <extrude>1</extrude>
""" if extrude_from_ground else "") + """\
        <altitudeMode>absolute</altitudeMode>
        <outerBoundaryIs>
        <LinearRing>
        <coordinates>
""" + result + """\
        </coordinates>
        </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>
  </Document>
</kml>""")


def read_path_file(path):

    # Reads a .csv file with a sequence of latitude/longitude
    # locations, with optional altitude and tolerances, and returns a
    # Path.

    import csv

    locations = []
    tolerances = []

    with open(path) as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 2 and not row[0].isalpha():
                tol = 0
                if len(row) == 2:
                    loc = Location(float(row[0]), float(row[1]), 0)
                else:
                    loc = Location(float(row[0]), float(row[1]), float(row[2]))
                    if len(row) >= 4: tol = float(row[3])
                locations.append(loc)
                tolerances.append(tol)

    return Path(locations, tolerances)


# Verification of a path following within the path's tolerance.

class PathFollower:

    def __init__(self, path):

        # path: the Path to follow

        self.path = path
        self.min_segm = 0
        self.max_segm = 0
        self.progress = 0
        self.distance = 0

    def has_stayed_on_path(self):
        return self.min_segm is not None

    def update(self, loc):

        path = self.path
        locations = path.locations
        progress = self.progress
        dist = 1e400
        min_s = None
        max_s = None
        prev_within_tol = False

        if self.min_segm is None:
            i = 0
            limit = path.length()-1
        else:
            i = self.min_segm
            limit = min(path.length()-1, self.max_segm+1)

        while i <= limit:
            s = path.segment(i)
            p, d = s.segment_dist(loc)
            if d < dist: dist = d
            if ((s.tolerances[0] == 0 and s.tolerances[1] == 0) or
                d <= max(s.tolerances[0], s.tolerances[1])):
                # within tolerance
                if i+p > progress:
                    progress = i+p
                if not prev_within_tol:
                    min_s = i
                max_s = i
                prev_within_tol = True
            else:
                # not within tolerance
                if self.max_segm is not None and i > self.max_segm:
                    break
                prev_within_tol = False
            i += 1

        if self.min_segm is None:
            min_s = None
            max_s = None

        self.min_segm = min_s
        self.max_segm = max_s
        self.progress = progress
        self.distance = dist

        return min_s is not None


def to_kml(file, extrude):

    import pathlib

    kml = read_path_file(file).polygon().to_kml(extrude)
    kml_file = pathlib.Path(file).with_suffix('.kml')
    with open(kml_file, 'w') as f:
        f.write(kml)


def cli():

    import argparse

    parser = argparse.ArgumentParser(
                prog = 'geodetic',
                description = 'Geodetic path conversion to KML files for viewing in Google earth.')
    parser.add_argument('--tokml', action='store_true')
    parser.add_argument('--extrude', action='store_true')
    parser.add_argument('files', nargs='*')
    args = parser.parse_args()

    if args.tokml:
        for file in args.files:
            to_kml(file, args.extrude)

if __name__ == '__main__':
    cli()
