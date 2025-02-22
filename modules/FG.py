# File: FG.py

# This interface to the FlightGear simulator uses the telnet
# protocol. To use it the simulator must be configured with these
# "Additional Settings":
#
#    --httpd=5400 --telnet=x,x,100,x,5454,x --allow-nasal-from-sockets

import socket
import json
import time

from geodetic import *
from airports import airports

_host = '127.0.0.1'
_port = 5454

_retry_timeout = 60
_retry_period = 2


def sim_host_set(h, p=5454):
    global _host
    _host = h
    _port = p


class Instruments:

    def __init__(self):
        self.loc = Location(0, 0, 0)  # latitude/longitude/altitude in feet
        self.alt_agl = 0  # altitude in feet above ground
        self.ias = 0  # indicated airspeed
        self.heading = 0  # heading of plane
        self.pitch = 0  # pitch of plane
        self.roll = 0  # roll of plane

    def __repr__(self):
        return f'Instruments(lat={self.loc.lat:.7f}, lon={self.loc.lon:.7f}), alt={self.loc.alt:.1f}, alt_agl={self.alt_agl:.1f}, ias={self.ias:.1f}, heading={self.heading:.1f}, pitch={self.pitch:.1f}, roll={self.roll:.1f}))'


class Controls:

    def __init__(self):
        self.elevator = 0
        self.aileron = 0
        self.rudder = 0
        self.flaps = 0
        self.throttle = 0
        self.mixture = 0
        self.brake = 0
        self.parking = 0

    def __repr__(self):
        return f'Controls(elevator={self.elevator:.2f}, aileron={self.aileron:.2f}, rudder={self.rudder:.2f}, flaps={self.flaps:.2f}, throttle={self.throttle:.2f}, mixture={self.mixture:.2f}, brake={self.brake:.1f}, parking={self.parking})'


instruments = Instruments()
controls = Controls()


def sim_connect():
    global sock
    print('=== Connecting to FlightGear on ' + _host + ':' + str(_port), end='', flush=True)
    i = 0
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(_retry_period / 2)
            sock.connect((_host, _port))
        except BaseException as exc:
            if not (type(exc) is OSError or type(exc) is TimeoutError or type(exc) is ConnectionRefusedError):
                raise exc
            sock = None
        if sock is not None:
            break
        if i == _retry_timeout:
            print('=== Could not connect to FlightGear on ' + _host + ':' + str(_port))
            raise BaseException('Could not connect to FlightGear')
        i += 1
        print('.', end='', flush=True)
        time.sleep(_retry_period / 2)
    print(': connected!')
    time.sleep(0.25)
    send('data')  # turn on data mode (to avoid prompts)
    time.sleep(0.25)


def send(cmd):
    # print(cmd)
    sock.sendall(cmd.encode() + b'\r\n')


def recv():
    return sock.recv(1024)


def recv_instruments():
    while True:
        try:
            send('nasal\r\nsprintf("[%f,%f,%f,%f,%f,%f,%f,%f]\\r\\n",' +
                 'getprop("instrumentation/airspeed-indicator/indicated-speed-kt"),' +
                 'getprop("position/altitude-ft"),' +
                 'getprop("position/altitude-agl-ft"),' +
                 'getprop("position/latitude-deg"),' +
                 'getprop("position/longitude-deg"),' +
                 'getprop("orientation/model/heading-deg"),' +
                 'getprop("orientation/model/pitch-deg"),' +
                 'getprop("orientation/model/roll-deg"))' +
                 '\r\n##EOF##\r\n')
            response = recv()
            ias, alt, alt_agl, lat, lon, heading, pitch, roll = tuple(json.loads(response.decode()))
            instruments.loc = Location(lat, lon, alt)
            instruments.alt_agl = alt_agl
            instruments.ias = ias
            instruments.heading = heading
            instruments.pitch = pitch
            instruments.roll = roll
            return
        except BaseException:
            time.sleep(0.1)


def send_controls():
    send('nasal\r\n' +
         'setprop("/controls/engines/current-engine/throttle","' + str(controls.throttle) + '");' +
         'setprop("/controls/engines/engine/mixture","' + str(controls.mixture) + '");' +
         'setprop("/controls/flight/elevator","' + str(controls.elevator) + '");' +
         'setprop("/controls/flight/aileron","' + str(controls.aileron) + '");' +
         'setprop("/controls/flight/rudder","' + str(controls.rudder) + '");' +
         'setprop("/controls/flight/flaps","' + str(controls.flaps) + '");' +
         'setprop("/controls/flight/brake","' + str(controls.brake) + '");' +
         'setprop("/sim/model/c172p/brake-parking","' + str(controls.parking) + '")' +
         '\r\n##EOF##\r\n')
    recv()


def autostart_c172p():
    send('nasal\r\nc172p.autostart()\r\n##EOF##\r\n')


def shutdown_engine():
    send('nasal\r\n' +
         'setprop("/engines/active-engine/kill-engine", 1);' +
         'setprop("/controls/engines/active-engine/throttle", 0);' +
         '\r\n##EOF##\r\n')
    recv()

    controls.throttle = 0

    seconds_without_engine = 0
    current_time = time.time()
    while True:
        try:
            send('nasal\r\nsprintf("%d\\r\\n", getprop("/engines/active-engine/running"));\r\n##EOF##\r\n')
            if recv().decode() == '0\r\n':
                seconds_without_engine += time.time() - current_time

            if seconds_without_engine > 2:
                break

            time.sleep(0.1)
        except BaseException:
            return

    send('nasal\r\nsetprop("/engines/active-engine/kill-engine", 0);\r\n##EOF##\r\n')
    recv()


def reset_aircraft(airport: str, runway: str):
    global controls
    airport = airports.get(airport, None)
    if airport is None:
        print(f'Airport {airport} not found')
        return

    runway = airport.runways.get(runway, None)
    if runway is None:
        print(f'Runway {runway} not found at {airport}')
        return

    shutdown_engine()

    send('nasal\r\n' +
         'setprop("/fdm/jsbsim/simulation/pause", 1);' +
         'setprop("/fdm/jsbsim/simulation/reset", 1);'
         '\r\n##EOF##\r\n')
    recv()
    send('nasal\r\nsprintf("%f\\r\\n", getprop("/fdm/jsbsim/position/h-sl-ft"));\r\n##EOF##\r\n')
    current_alt = float(recv().decode())
    send(f'nasal\r\nsetprop("/fdm/jsbsim/position/h-sl-ft", {current_alt + 2 * 3.28084});\r\n##EOF##\r\n')
    recv()
    send('nasal\r\n' +
         'setprop("/fdm/jsbsim/settings/damage", 0);' +
         'setprop("/engines/active-engine/running", 0);' +
         'setprop("/engines/active-engine/kill-engine", 0);' +
         'setprop("/engines/active-engine/killed", 0);' +
         'setprop("/engines/active-engine/crashed", 0);' +
         'setprop("/engines/active-engine/crash-engine"", 0);'
            '\r\n##EOF##\r\n')
    recv()
    controls = Controls()
    send_controls()
    send('nasal\r\nsetprop("/fdm/jsbsim/simulation/pause", 0);\r\n##EOF##\r\n')
    recv()
    time.sleep(3)
    send('nasal\r\nsetprop("/fdm/jsbsim/settings/damage", 0);\r\n##EOF##\r\n')
    recv()
