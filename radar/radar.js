// Visual style of the plane
let dot_size = 5;   // size of dot showing the location of the plane
let trail_width = 2; // width of the trail
let max_trail = 100; // length of trail behing plane
let plane_palette = ['#e6194b', '#f58231', '#911eb4', '#42d4f4', '#f032e6', '#fabed4', '#469990'];
let font_size = 10;
let cycle_length = 5;

// Visual style of the path showing the challenge
let path_fill_color = '#00ff0040';
let path_contour_color = '#ffff00';
let path_contour_width = 1;

// The background map and reference points

let map_img_url = 'LOWI.png';

let pointsXY = [[47.258888, 11.331700], // lat/lon of 3 reference points
[47.261625, 11.357035],
[47.250274, 11.353668]];

let pointsUV = [[2348, 1310], // pixel coordinates of above lat/lon
[2937, 1215],
[2861, 1607]];

//------------------------------------------------------------------------------

let planes = {}; // planes being tracked
let cycle = 0;
let plane_style_counter = 0;

function Timer() {
    this.start = new Date();
    this.stop = false;
    this.stop_time = 0;

    this.elapsed = function () {
        if (!this.stop) {
            this.stop_time = (new Date() - this.start) / 1000;
        }
        return this.stop_time;
    };

    this.stopTimer = function () {
        this.stop = true;
    };
}

//------------------------------------------------------------------------------

// Linear algebra.
function solveLinearSystem(A, B) {
    // Augment A with B to create an augmented matrix
    let n = A.length;
    let augmented = A.map((row, i) => [...row, B[i]]);

    // Perform Gaussian elimination
    for (let i = 0; i < n; i++) {
        // Find max pivot
        let maxRow = i;
        for (let k = i + 1; k < n; k++) {
            if (Math.abs(augmented[k][i]) > Math.abs(augmented[maxRow][i])) {
                maxRow = k;
            }
        }
        // Swap rows
        [augmented[i], augmented[maxRow]] = [augmented[maxRow], augmented[i]];

        // Make leading coefficient 1
        let lead = augmented[i][i];
        for (let j = i; j <= n; j++) {
            augmented[i][j] /= lead;
        }

        // Make other rows 0 in this column
        for (let k = 0; k < n; k++) {
            if (k !== i) {
                let factor = augmented[k][i];
                for (let j = i; j <= n; j++) {
                    augmented[k][j] -= factor * augmented[i][j];
                }
            }
        }
    }

    // Extract solution
    return augmented.map(row => row[n]);
}

function findLinearTransformation(pointsXY, pointsUV) {
    // Extract coordinates
    let [[X1, Y1], [X2, Y2], [X3, Y3]] = pointsXY;
    let [[u1, v1], [u2, v2], [u3, v3]] = pointsUV;

    // Construct the system of equations: Ax = B
    let A = [
        [X1, Y1, 1, 0, 0, 0],
        [0, 0, 0, X1, Y1, 1],
        [X2, Y2, 1, 0, 0, 0],
        [0, 0, 0, X2, Y2, 1],
        [X3, Y3, 1, 0, 0, 0],
        [0, 0, 0, X3, Y3, 1]
    ];

    let B = [u1, v1, u2, v2, u3, v3]; // Target pixel positions

    // Solve for transformation parameters
    let solution = solveLinearSystem(A, B);

    let [a, b, e, c, d, f] = solution; // Extract transformation parameters

    // Return transformation matrix and translation vector
    return {
        matrix: [[a, b], [c, d]],
        translation: [e, f]
    };
}

function applyTransformation(matrix, translation, X, Y) {
    let [[a, b], [c, d]] = matrix;
    let [e, f] = translation;

    // Compute transformed coordinates
    let u = a * X + b * Y + e;
    let v = c * X + d * Y + f;

    return [u, v];
}

let transform = findLinearTransformation(pointsXY, pointsUV);

function LocationToXY(loc) {

    let { matrix, translation } = transform;
    let [x, y] = applyTransformation(matrix, translation, loc.lat, loc.lon);

    return { x: x, y: y };
}

//------------------------------------------------------------------------------

// Mapping of lat/lon to pixel coordinates on LOWI map.

let flight_path = null;
let flight_path_polygon = null;

//------------------------------------------------------------------------------


function draw_path(ctx, path) {

    ctx.fillStyle = path_fill_color;
    ctx.strokeStyle = path_contour_color;
    ctx.lineWidth = path_contour_width;

    ctx.beginPath();

    for (let i = 0; i <= path.length(); i++) {
        let loc = path.locations[i];
        let p = LocationToXY(loc);
        if (i === 0) {
            ctx.moveTo(p.x, p.y);
        } else {
            ctx.lineTo(p.x, p.y);
        }
    }

    ctx.closePath();
    ctx.stroke();
    ctx.fill();
}


function start() {

    let canvas = document.getElementById('mapCanvas');
    let ctx = canvas.getContext('2d');

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    ctx.font = font_size + 'px Courier';

    let map_img = new Image();
    map_img.src = map_img_url;

    // Initial transformation settings
    let scale = 1;
    let originX = 0;
    let originY = 0;

    // Panning state
    let isDragging = false;
    let startX, startY;

    async function image_loaded() {

        let r = await fetch('/flight-path');
        let t = await r.text();
        let fp = JSON.parse(t);

        if (fp.length > 0) {
            let locations = [];
            let tolerances = [];

            for (let i = 0; i < fp.length; i++) {
                let loc = fp[i];
                locations.push(new Location(loc[0], loc[1], loc[2]));
                tolerances.push(loc[3]);
            }

            flight_path = new Path(locations, tolerances);

            flight_path_polygon = flight_path.polygon();
        }

        scale = Math.max(canvas.width / map_img.width,
            canvas.height / map_img.height);

        redraw();

        async function poll() {
            let r = await fetch('/state');
            let t = await r.text();
            let state = JSON.parse(t);
            for (let a in state) {
                let loc = state[a];
                loc = new Location(loc.lat, loc.lon, loc.alt);
                let curr = planes[a];

                function new_plane() {
                    let color = plane_style_counter % 11;
                    let style = plane_style_counter % 4;
                    plane_style_counter++;
                    if (plane_style_counter >= plane_palette.length * 4) plane_style_counter = 0;
                    curr = {
                        last_comm: 0,
                        trail: [loc],
                        follower: (flight_path===null) ? null : new PathFollower(flight_path),
                        color: color,
                        style: style,
                        timer: new Timer(),
                        status: '',
                    };
                }


                if (curr === undefined || loc.distance(curr.trail[curr.trail.length - 1]) > 500) {
                    new_plane();
                } else {
                    curr.last_comm = 0;
                    curr.trail[curr.trail.length - 1] = loc;
                    if (cycle === 0) {
                        curr.trail.push(loc);
                        while (curr.trail.length > max_trail) curr.trail.shift();
                    }
                }
                planes[a] = curr;
                if (curr.follower !== null) {
                    curr.follower.update(loc);
                }
            }

            let prev_planes = planes;
            planes = {};
            for (let a in prev_planes) {
                let curr = prev_planes[a];
                curr.last_comm++;
                if (curr.last_comm < 10) {
                    planes[a] = curr;
                }
            }

            cycle = (cycle + 1) % cycle_length;

            redraw();
            setTimeout(poll, 200);
        }

        setTimeout(poll, 0);
    }

    map_img.onload = image_loaded;

    // Draw the image with current transformations
    function redraw() {

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.save();

        // setup transformation to place the map at the right place on the screen
        ctx.translate(originX, originY);
        ctx.scale(scale, scale);

        // draw the map
        ctx.drawImage(map_img, 0, 0);

        if (flight_path_polygon !== null) {
            draw_path(ctx, flight_path_polygon);
        }

        let loc;

        function hex(x) { return '0123456789abcdef'[x >> 4] + '0123456789abcdef'[x & 15]; }

        for (let a in planes) {
            let curr = planes[a];
            let n = curr.trail.length;
            let color = plane_palette[curr.color];
            let style = curr.style;
            for (let i = 0; i < n; i++) {
                let loc = curr.trail[i];
                let { x, y } = LocationToXY(loc);
                if (i > 0 && (curr.trail.length - i) % cycle_length != 0) {
                    let loc0 = curr.trail[i - 1];
                    let { x: x0, y: y0 } = LocationToXY(loc0);
                    ctx.beginPath();
                    ctx.lineWidth = trail_width;
                    ctx.strokeStyle = color; // + hex(Math.floor(127 + 128*(i+1)/n));
                    ctx.moveTo(x0, y0);
                    ctx.lineTo(x, y);
                    ctx.stroke();
                    ctx.closePath();
                }
                if (i == n - 1) {
                    if (cycle === 0) {
                        ctx.fillStyle = '#ffffff'; // blink white
                    } else {
                        ctx.fillStyle = color;
                    }
                    ctx.beginPath();
                    ctx.ellipse(x, y, dot_size, dot_size, 0, 0, 2 * Math.PI);
                    ctx.fill();
                    ctx.closePath();

                    let dx = (style & 1) * 2 - 1;
                    let dy = (style & 2) - 1;

                    ctx.beginPath();
                    ctx.lineWidth = 1;
                    ctx.strokeStyle = color;
                    ctx.moveTo(x + 5 * dx, y + 5 * dy);
                    ctx.lineTo(x + 30 * dx, y + 30 * dy);
                    ctx.stroke();
                    ctx.closePath();

                    let len = a.length;
                    ctx.fillStyle = color;
                    ctx.fillText(a, x + 30 * dx + ((dx > 0) ? 0 : -0.6 * len * font_size), y + 30 * dy - font_size * 0.2);
                    let t = Math.floor(loc.alt) + ' ft';

                    let time_info = curr.timer.elapsed().toFixed(0) + 's';

                    if (dx > 0) {
                        t = t + ' / ' + time_info;
                    } else {
                        t = time_info + ' / ' + t;
                    }

                    if (curr.follower && !curr.follower.has_stayed_on_path()) {
                        if (curr.status === '') {
                            curr.status = '[OFF-COURSE]';
                        }
                    }

                    if (curr.follower && curr.follower.has_reached_destination()) {
                        if (curr.status === '') {
                            curr.status = '[COMPLETED]';
                            console.log(a + ' completed in: ' + curr.timer.elapsed().toFixed(0) + 's');
                        }
                    }

                    if (curr.status !== '') {
                        curr.timer.stopTimer();
                        if (dx > 0) {
                            t = t + ' ' + curr.status;
                        } else {
                            t = curr.status + ' ' + t;
                        }
                    }

                    len = t.length;
                    ctx.fillText(t, x + 30 * dx + ((dx > 0) ? 0 : -0.6 * len * font_size), y + 30 * dy + font_size * 0.7);
                }
            }
        }


        ctx.restore();
    }

    // Zoom with mouse wheel
    canvas.addEventListener('wheel', function (event) {
        event.preventDefault();
        let mouseX = event.clientX - originX;
        let mouseY = event.clientY - originY;
        let zoomFactor = 1.05;
        let delta = event.deltaY > 0 ? 1 / zoomFactor : zoomFactor;

        // Zoom towards mouse position
        originX -= mouseX * (delta - 1);
        originY -= mouseY * (delta - 1);
        scale *= delta;

        redraw();
    });

    // Mouse down for panning
    canvas.addEventListener('mousedown', function (event) {
        isDragging = true;
        startX = event.clientX - originX;
        startY = event.clientY - originY;
    });

    // Mouse move for panning
    canvas.addEventListener('mousemove', function (event) {
        if (isDragging) {
            originX = event.clientX - startX;
            originY = event.clientY - startY;
            redraw();
        }
    });

    // Mouse up to stop panning
    canvas.addEventListener('mouseup', function () {
        isDragging = false;
    });

    // Mouse out to stop panning
    canvas.addEventListener('mouseout', function () {
        isDragging = false;
    });

    // Adjust canvas size on window resize
    window.addEventListener('resize', function () {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        redraw();
    });

}

document.addEventListener('DOMContentLoaded', start);
