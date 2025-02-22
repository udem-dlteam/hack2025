// File: geodetic.js


function feet_to_meters(x) {
    return x * 0.3048; // meters per foot
}

function deg2rad(deg) {
    return deg*Math.PI/180;
}

function rad2deg(rad) {
    return rad*180/Math.PI;
}

function heading_diff(heading1, heading2) {
    return ((heading1 - heading2 + 180) % 360 + 360) % 360 - 180;
}


// Creates a point on the earth's surface at the supplied latitude,
// longitude and altitude.

function Location(lat, lon, alt=0) {

    let loc = this;

    loc.lat = lat;
    loc.lon = lon;
    loc.alt = alt;
    loc.radius = 20925524.9; // radius of earth in feet
}

Location.prototype.distance = function (other) {

    // Returns the distance in feet from this point to the
    // other point.

    // other: the Location to compute distance with

    let loc = this;

    let lat1 = deg2rad(loc.lat);
    let lon1 = deg2rad(loc.lon);
    let lat2 = deg2rad(other.lat);
    let lon2 = deg2rad(other.lon);

    let v = Math.sin(lat1)*Math.sin(lat2) +
            Math.cos(lat1)*Math.cos(lat2)*Math.cos(lon1-lon2);

    let r = loc.radius + Math.min(loc.alt, other.alt);

    return Math.sqrt((Math.acos(Math.max(-1, Math.min(1, v))) * r)**2 +
                     (loc.alt - other.alt)**2);
};

Location.prototype.distance_haversine = function (other) {

    // Returns the distance in feet from this point to the
    // other point. It is computed using the Haversine formula.

    // other: the Location to compute distance with

    let loc = this;

    let phi1 = deg2rad(loc.lat);
    let lambda1 = deg2rad(loc.lon);
    let phi2 = deg2rad(other.lat);
    let lambda2 = deg2rad(other.lon);
    let deltaphi = phi2 - phi1;
    let deltalambda = lambda2 - lambda1;

    let a = Math.sin(deltaphi/2) * Math.sin(deltaphi/2) +
            Math.cos(phi1) * Math.cos(phi2) *
            Math.sin(deltalambda/2) * Math.sin(deltalambda/2);

    let c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

    return Math.sqrt((loc.radius * c)**2 + (loc.alt - other.alt)**2);
};

Location.prototype.bearing = function (other) {

    // Returns the bearing from this point to the
    // other point. The bearing is an angle from 0 to 360
    // degrees indicating the direction to travel to get to the
    // other point. 0 means "north", 90 is "east", 180 is "south"
    // and 270 is "west".

    // other: the Location to compute bearing to

    let loc = this;

    let phi1 = deg2rad(loc.lat);
    let phi2 = deg2rad(other.lat);
    let deltalambda = deg2rad(other.lon - loc.lon);

    let y = Math.sin(deltalambda) * Math.cos(phi2);
    let x = Math.cos(phi1)*Math.sin(phi2) -
            Math.sin(phi1)*Math.cos(phi2)*Math.cos(deltalambda);
    let theta = Math.atan2(y, x);

    return (rad2deg(theta) % 360 + 360) % 360;
}

Location.prototype.destination = function (bearing, dist) {

    // Returns the point (Location) at a certain bearing
    // and distance from this point.

    // bearing: the bearing in degrees
    // dist: the distance in feet

    let loc = this;

    let theta = deg2rad(bearing);
    let d = dist / loc.radius;  // angular distance in radians

    let phi1 = deg2rad(loc.lat);
    let lambda1 = deg2rad(loc.lon);

    let phi2 = Math.asin(Math.sin(phi1)*Math.cos(d) +
                         Math.cos(phi1)*Math.sin(d)*Math.cos(theta));
    let lambda2 = lambda1 +
        Math.atan2(Math.sin(theta)*Math.sin(d)*Math.cos(phi1),
                   Math.cos(d)-Math.sin(phi1)*Math.sin(phi2));

    lambda2 = ((lambda2+3*Math.PI) % (2*Math.PI) + (2*Math.PI)) % (2*Math.PI) - Math.PI; // normalise to -180..+180

    return new Location(rad2deg(phi2), rad2deg(lambda2), loc.alt);
};

Location.prototype.interpolate = function (other, pos) {

    // Finds the Location between this Location and the
    // other Location that is the interpolation at
    // position pos (between 0 and 1).

    let loc = this;

    function interpolate(start, end, pos) {
        return start + (end-start)*pos;
    }

    return new Location(interpolate(loc.lat, other.lat, pos),
                        interpolate(loc.lon, other.lon, pos),
                        interpolate(loc.alt, other.alt, pos));
};

Location.prototype.toString = function () {

    let loc = this;

    return '<Location lat=' + loc.lat +
           ' lon=' + loc.lon +
           ' alt=' + loc.alt + '>';
};


// Creates a path, which is a sequence of locations.

function Path(locations, tolerances) {

    // locations: the array of Locations defining the path
    // tolerances: the array of tolerances, in feet, at each Location (optional)

    let path = this;

    path.locations = locations
    if (tolerances === undefined) {
        path.tolerances = Array(locations.length).fill(0);
    } else {
        path.tolerances = tolerances;
    }
};

Path.prototype.length = function () {

    // A Path that is composed of N Locations contains N-1 segments.
    // The length of a Path is the number of segments.

    let path = this;

    return path.locations.length-1;
};

Path.prototype.segment = function (i) {

    // Returns the i'th segment of the Path. A segment is
    // a Path that has just two Locations.

    let path = this;

    return new Path(path.locations.slice(i, i+2), path.tolerances.slice(i, i+2));
};

Path.prototype.distance = function () {

    // Returns the distance of the path.

    let path = this;

    let result = 0

    for (let i=0; i<path.length(); i++) {
        result += path.locations[i].distance(path.locations[i+1]);
    }

    return result;
};

Path.prototype.segment_dist = function (loc) {

    // Returns the distance of the path.

    let path = this;

    let levels = Math.ceil(Math.log2(Math.max(4, path.distance())));
    let discretization = (1<<levels) - 2;
    let loc0 = path.locations[0];
    let loc1 = path.locations[1];
    let span = 1<<(levels-2);
    let pos_index = (1<<(levels-1)) - 1;

    function interpolate_dist(pos) {
        console.log(loc, loc1, pos);
        return loc.distance(loc0.interpolate(loc1, pos));
    }

    while (span > 0) {
        let d0 = interpolate_dist(pos_index/discretization);
        let d1 = interpolate_dist((pos_index+1)/discretization);
        if (d0 < d1) {
            pos_index -= span;
        } else {
            pos_index += span;
        }
        span >>= 1;
    }

    let pos = pos_index / discretization;
    return [pos, interpolate_dist(pos)];
};

Path.prototype.interpolate = function (pos) {

    let path = this;

    if (pos <= 0) {
        let loc = path.locations[0];
        return new Location(loc.lat, loc.lon, loc.alt);
    } else if (pos >= path.length()) {
        let loc = path.locations[-1];
        return new Location(loc.lat, loc.lon, loc.alt);
    } else {
        let i = Math.floor(pos);
        return path.locations[i].interpolate(path.locations[i+1], pos-i);
    }
};

Path.prototype.polygon = function () {

    // Returns a list of the Locations that define the contour
    // of the Path, taking into account the tolerance at each
    // Location of the Path.

    let path = this;

    let n = path.length();

    let side1 = [];
    let side2 = [];
    let prev_bearing;

    let i = 0;

    while (i <= n) {
        let start = path.locations[i]
        let tol = path.tolerances[i]
        let j = i+1
        let bearing;
        if (i === n) {
            end = start;
            bearing = prev_bearing;
        } else {
            let end = path.locations[j]
            while (j < n && start.lat === path.locations[j].lat && start.lon === path.locations[j].lon) {
                j += 1;
            }
            bearing = start.bearing(path.locations[j]);
            if (i === 0 || i === n) {
                if (i === 0) {
                    side1.push(start.destination(bearing, -tol));
                }
                side1.push(start.destination(bearing-90, tol));
                side2.push(start.destination(bearing+90, tol));
                if (i === n) {
                    side2.push(start.destination(bearing, tol));
                }
            } else {
                let turn = heading_diff(bearing, prev_bearing);
                if (turn >= -1 && turn <= 1) {
                    side1.push(start.destination(bearing-90, tol));
                    side2.push(start.destination(bearing+90, tol));
                } else {
                    let angle;
                    let s1;
                    let s2;
                    if (turn > 0) {
                        angle = prev_bearing-90;
                        s1 = side1;
                        s2 = side2;
                    } else {
                        angle = prev_bearing+90;
                        s1 = side2;
                        s2 = side1;
                    }
                    s1.push(start.destination(angle, tol));
                    s1.push(start.destination(angle+turn/2, tol));
                    s1.push(start.destination(angle+turn, tol));
                    s2.push(start.destination(angle+turn/2, -tol/Math.cos(deg2rad(Math.max(-60, Math.min(60, turn/2))))));
                }
            }
        }
        prev_bearing = bearing;
        i += 1;
    }

    side2.reverse();

    return new Path(side1.concat(side2, [side1[0]])); // make a closed path
};


// Verification of a path following within the path's tolerance.

function PathFollower(path) {

    // path: the Path to follow

    let pf = this;

    pf.path = path;
    pf.min_segm = 0;
    pf.max_segm = 0;
    pf.progress = 0;
    pf.distance = 0;
};

PathFollower.prototype.has_stayed_on_path = function () {

    let pf = this;

    return pf.min_segm !== null;
};
    
PathFollower.prototype.update = function (loc) {

    let pf = this;

    let path = pf.path;
    let locations = path.locations;
    let progress = pf.progress;
    let dist = 1e400;
    let min_s = null;
    let max_s = null;
    let prev_within_tol = false;
    let i;
    let limit;

    if (pf.min_segm === null) {
        i = 0;
        limit = path.length()-1;
    } else {
        i = pf.min_segm;
        limit = Math.min(path.length()-1, pf.max_segm+1);
    }

    while (i <= limit) {
        let s = path.segment(i);
        console.log(s, loc);
        let [p, d] = s.segment_dist(loc);
        console.log(p, d);
        if (d < dist) dist = d;
        if ((s.tolerances[0] == 0 && s.tolerances[1] == 0) ||
            d <= Math.max(s.tolerances[0], s.tolerances[1])) {
            // within tolerance
            if (i+p > progress)
                progress = i+p;
            if (!prev_within_tol)
                min_s = i;
            max_s = i;
            prev_within_tol = true;
        } else {
            // not within tolerance
            if (pf.max_segm !== null && i > pf.max_segm)
                break;
            prev_within_tol = false;
        }
        i++;
    }

    if (pf.min_segm === null) {
        min_s = null;
        max_s = null;
    }

    pf.min_segm = min_s;
    pf.max_segm = max_s;
    pf.progress = progress;
    pf.distance = dist;

    return min_s !== null;
};
