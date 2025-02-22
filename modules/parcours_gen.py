# File: parcours_gen

from airports import *
from geodetic import *


path_segment_length = 200
ground_run = 1900
extra_tol = 500
turn = None

mountain_start = Location(47.2870, 11.3050, 5600)
mountain_end   = Location(47.2895, 11.2950, 5600)

river_start = Location(47.26495, 11.3114, 1930)
river_end   = Location(47.26445, 11.3064, 1930)


pos = None
tol = None

output = None


def print_pos():
    global output
    line = (str(pos.lat) + ',' +
            str(pos.lon) + ',' +
            str(pos.alt) + ',' + str(round(tol)))
    output += line + '\n'
    #print(line)


def advance(dist_gain, alt_gain, bearing_gain, tolerance_gain):

    global pos, bearing, tol

    n = round(dist_gain/path_segment_length)
    d = dist_gain/n
    a = alt_gain/n
    b = bearing_gain/n
    t = tolerance_gain/n

    while n > 0:
        bearing += b
        tol += t
        pos = pos.destination(bearing, d)
        pos.alt += a
        print_pos()
        n -= 1


def roll(rw_start, rw_end, ground_run):

    global pos, bearing, tol

    rw_length = rw_start.distance(rw_end)
    rw_bearing = rw_start.bearing(rw_end)

    pos = rw_start.destination(rw_bearing, -120)
    bearing = rw_bearing

    print_pos()

    advance(ground_run, 0, 0, 0)


def takeoff(rw_start, rw_end, ground_run, circuit_alt):

    roll(rw_start, rw_end, ground_run)

    advance(1500, 0.3*circuit_alt, 0, extra_tol)


def partial(rw_start, rw_end, ground_run, circuit_alt, turn):

    takeoff(rw_start, rw_end, ground_run, circuit_alt)

    advance(2000, 0.2*circuit_alt, turn, 0)
    advance(2700, 0.3*circuit_alt, 0, 0)
    advance(2000, 0.2*circuit_alt, turn, 0)

    advance(ground_run+2000, 0, 0, 0)


def circuit(rw_start, rw_end, ground_run, circuit_alt, turn):

    takeoff(rw_start, rw_end, ground_run, circuit_alt)

    advance(2000, 0.2*circuit_alt, turn, 0)
    advance(2700, 0.3*circuit_alt, 0, 0)
    advance(2000, 0.2*circuit_alt, turn, 0)

    advance(ground_run+3900, 0, 0, 0)

    advance(2000, -0.2*circuit_alt, turn, 0)
    advance(2700, -0.3*circuit_alt, 0, 0)
    advance(2000, -0.2*circuit_alt, turn, 0)
    advance(2700, -0.3*circuit_alt, 0, -extra_tol)

    advance(500, 0, 0, 0)


def impossible(rw_start, rw_end, ground_run, circuit_alt, turn):

    takeoff(rw_start, rw_end, ground_run, circuit_alt)

    advance(1000, 0.2*circuit_alt, turn/2, 0)
    advance(925, 0, 0, 0)
    advance(1000, -0.1*circuit_alt, -turn/2, 0)
    advance(900, -0.1*circuit_alt, 0, 0)
    advance(2200, -0.2*circuit_alt, -2*turn, 0)
    advance(900, -0.1*circuit_alt, 0, -extra_tol)

    advance(200, 0, 0, 0)


def flyover(rw_start, rw_end, ground_run, circuit_alt, flyover_start, flyover_end, flyover_tol, turn):

    global pos, bearing, tol

    takeoff(rw_start, rw_end, ground_run, circuit_alt)

    if turn != 0:
        advance(2000, 0.2*circuit_alt, turn, 0)

    tol = 0

    print_pos()

    pos = flyover_start

    print_pos()

    tol = flyover_tol

    print_pos()

    bearing = flyover_start.bearing(flyover_end)

    advance(flyover_start.distance(flyover_end), 0, 0, 0)


def airport_setup(airport, runway):

    global ground_run, circuit_alt, tol, turn, rw_start, rw_end

    if airport == 'LOWI':
        if runway == '08':
            turn = 90
        else:
            turn = -90
        tol = 80
    elif airport == 'LOIJ':
        if runway == '13':
            turn = 90
        else:
            turn = -90
        tol = 50
    else:
        tol = 100

    circuit_alt = 1000

    rw = airports[airport].runways[runway]
    rw_start = rw.location
    rw_end   = airports[airport].runways[rw.reverse].location


def gen(airport, runway, pattern):

    global output, rw_start, rw_end

    output = ''

    airport_setup(airport, runway)

    if pattern == 'roll':
        roll(rw_start, rw_end, ground_run)
    elif pattern == 'takeoff':
        takeoff(rw_start, rw_end, ground_run, circuit_alt)
    elif pattern == 'partial':
        partial(rw_start, rw_end, ground_run, circuit_alt, turn)
    elif pattern == 'circuit':
        circuit(rw_start, rw_end, ground_run, circuit_alt, turn)
    elif pattern == 'impossible':
        impossible(rw_start, rw_end, ground_run, circuit_alt, turn)
    elif pattern == 'mountain':
        flyover(rw_start, rw_end, ground_run, circuit_alt,
                mountain_start, mountain_end, 250, 45)
    elif pattern == 'river':
        flyover(rw_start, rw_end, ground_run, circuit_alt,
                river_start, river_end, 100, 15)
    elif pattern == 'crosscountry':
        dest = 'LOIJ'
        rw = '13'
        rw_reverse = '31'
        dest_start = airports[dest].runways[rw].location
        dest_end   = airports[dest].runways[rw_reverse].location
        dest_start.alt += 200
        dest_end.alt += 200
        flyover(rw_start, rw_end, ground_run, circuit_alt,
                dest_start, dest_end, 250, -5)

    name = airport + '_' + runway + '_' + pattern

    dump_path(name)


def dump_path(name):

    import os

    root_dir = 'parcours'
    if not os.path.exists(root_dir):
        os.makedirs(root_dir)

    specific_dir = root_dir + '/' + name
    if not os.path.exists(specific_dir):
        os.makedirs(specific_dir)

    csv_file = specific_dir + '/' + name + '.csv'
    with open(csv_file, 'w') as f:
        f.write('lat,lon,alt,tol\n' + output)

    to_kml(csv_file, True)


def challenges():

    for pattern in ['roll', 'takeoff', 'partial', 'circuit', 'impossible']:
        for airport in ['LOWI', 'LOIJ']:
            if not (airport == 'LOIJ' and pattern == 'impossible'):
                for runway in airports[airport].runways:
                    gen(airport, runway, pattern)

    gen('LOWI', '26', 'mountain')
    gen('LOWI', '26', 'river')
    gen('LOWI', '08', 'crosscountry')

challenges()
