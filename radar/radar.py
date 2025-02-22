# File: radar.py

import http.server
import json
import webbrowser
import threading
import time
import argparse
import requests
import os
import socket
from geodetic import *

# ------------------------------------------------------------------------------

update_period = 0.2  # rate of refresh of plane locations

# ignore locations that are far from the point of interest
point_of_interest = Location(47.258888, 11.3317, 1907)  # Innsbruck airport

default_sims = [
    "localhost:5400",
]

# mpservers to use when --mps option is specified
default_mpservers = [
    "fgms.iro.umontreal.ca:5001",
]

flight_path = None


def observe_sim(address):
    if address in observed_sims:
        return
    observed_sims[address] = [0]


def init_observed_sims():
    global observed_sims
    observed_sims = {}
    for address in default_sims:
        observe_sim(address)


def observe_mpserver(address):
    if address in observed_mpservers:
        return
    observed_mpservers[address] = [0]


def init_observed_mpservers():
    global observed_mpservers
    observed_mpservers = {}
    for address in default_mpservers:
        observe_mpserver(address)


def extract(props):

    result = {}

    def walk(props):
        n = props["nChildren"]
        if n > 0:
            if "children" in props:
                for c in props["children"]:
                    walk(c)
        else:
            result[props["name"]] = props["value"]

    walk(props)

    return result


def get_net(address, cmd=None):

    try:
        parts = address.split(":")
        if len(parts) == 2:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((parts[0], int(parts[1])))
                if cmd is not None:
                    s.sendall(cmd.encode("utf-8"))
                data = s.recv(1024 * 1024)
                return data.decode("utf-8")
    except BaseException:
        pass

    return ""


def read_mpserver(address):

    lines = list(filter(lambda line: line[0:1] != "#", get_net(address).split("\n")))

    for line in lines:
        parts = line.split(" ")
        if len(parts) > 6:
            parts[0] = parts[0].replace(":", "").replace("@LOCAL", "")
            parts = [parts[0]] + list(map(float, parts[1:10]))

            name = parts[0]
            lat = parts[4]
            lon = parts[5]
            alt = parts[6]
            loc = Location(lat, lon, alt)

            if point_of_interest.distance(loc) < 1000000:
                pos = (lat, lon, alt)
                planes[name] = pos


def read_mpservers():
    for address in observed_mpservers:
        read_mpserver(address)


# JSON received for get of http://localhost:5400/json/position')
#
# {
#     'longitude-deg': 11.330978,
#     'latitude-deg': 47.258834,
#     'altitude-ft': 1917.499784,
#     'altitude-agl-ft': 4.048276,
#     'ground-elev-m': 583.103422,
#     'latitude-string': '47*15\'31.8"N',
#     'longitude-string': '11*19\'51.5"E',
#     'ground-elev-ft': 1913.06897,
#     'altitude-agl-m': 1.233915,
#     'sea-level-radius-ft': 20887949.744455
# }

planes = {}


def update_plane(address, info):
    pos = (info["latitude-deg"], info["longitude-deg"], info["altitude-ft"])
    planes[address] = pos


#    print('update_plane(address, info)', address, pos)


def delete_plane(address):
    #    print('delete_plane(address)', address)
    try:
        del planes[address]
    except BaseException:
        pass


def read_sims():
    observed_sims_copy = observed_sims.copy()
    for address in observed_sims_copy:
        info = None
        status = observed_sims_copy[address]
        try:
            r = requests.get("http://" + address + "/json/position", timeout=0.2)
            if r.status_code == 200:
                status[0] = 0
                data = r.json()
                info = extract(data)
        except BaseException:
            if debug:
                pass  # print('========== could not get position from ' + address)
            status[0] += 1
            if status[0] >= 100:
                if address not in default_sims:
                    del observed_sims[address]
                delete_plane(address)
        if info is not None:
            update_plane(address, info)


def periodic_update():
    while True:
        read_sims()
        read_mpservers()
        time.sleep(update_period)


def api(request):
    return ("API request = " + repr(request)).encode("utf-8")


def get_state():
    state = {}
    planes_copy = planes.copy()
    for p in planes_copy:
        s = planes_copy[p]
        state[p] = {"lat": s[0], "lon": s[1], "alt": s[2]}
    return state


def get_flight_path():
    fp = []
    if flight_path is not None:
        locations = flight_path.locations
        tolerances = flight_path.tolerances
        for i in range(len(locations)):
            loc = locations[i]
            fp.append([loc.lat, loc.lon, loc.alt, tolerances[i]])
    return fp


# ------------------------------------------------------------------------------


class WebServer(http.server.BaseHTTPRequestHandler):

    def do_GET(self):

        path = self.path

        # print('GET path =', path)

        if path == "/":
            path = "/radar.html"

        response = b""

        if path == "/state":
            response = json.dumps(get_state()).encode("utf-8")
        elif path == "/flight-path":
            response = json.dumps(get_flight_path()).encode("utf-8")
        elif path != "/favicon.ico" and ".." not in path:
            response = open(
                os.path.join(os.path.dirname(__file__), path[1:]), "rb"
            ).read()

        self.send_response(200)
        self.end_headers()
        self.wfile.write(response)

    def do_POST(self):

        path = self.path

        # print('POST path =', path)

        response = b""

        if path == "/api":
            request = None
            try:
                length = int(self.headers.get("content-length"))
                data = self.rfile.read(length)
                request = json.loads(data)
            except BaseException:
                print("POST api exception")
            if request is not None:
                # print('POST api request =', request)
                response = api(request)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, format, *args):
        pass


def main():

    def open_browser():
        time.sleep(0.2)
        url = "http://localhost:" + str(port)
        if debug:
            print("========== opening " + url)
        webbrowser.open_new(url)

    t = threading.Thread(target=open_browser)
    t.start()

    t = threading.Thread(target=periodic_update)
    t.start()

    http.server.ThreadingHTTPServer(("", port), WebServer).serve_forever()


def cli():

    import pathlib

    global port, debug, flight_path, default_mpservers

    parser = argparse.ArgumentParser(
        prog="radar", description="Shows information on a map."
    )
    parser.add_argument("--port", default=8000)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--mps", action="store_true")
    parser.add_argument("--mpserver", action="append")
    parser.add_argument("files", nargs="*")
    args = parser.parse_args()

    port = args.port
    debug = args.debug
    mps = args.mps

    if not mps:
        default_mpservers = []

    init_observed_sims()
    init_observed_mpservers()

    if args.mpserver is not None:
        for address in args.mpserver:
            observe_mpserver(address)

    for file in args.files:
        if pathlib.Path(file).suffix == ".csv":
            flight_path = read_path_file(file)
        else:
            parts = file.split(":")
            if len(parts) == 2:
                observe_sim(file)
            else:
                file = os.path.join(
                    os.path.dirname(__file__), "..", "parcours", file, file + ".csv"
                )
                flight_path = read_path_file(file)

    main()


if __name__ == "__main__":
    cli()
