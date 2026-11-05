"""The AV's paths between the calls, laid from flights recorded in game.

The tester flew each leg with a flying cheat while the dev menu's flight
recorder wrote V's place every half second (`flights/flight_rec_N.txt`,
"seconds x y z"). A recording proves a line through the city is clear at the
height it was flown, and it is not yet a path an AV would fly: the height
wanders (a double jump here, a dip there), the speed drops on long legs, and
the landing is a fall.

So a recording becomes a path in four steps:

1. The line on the ground: the recording smoothed over a few seconds and
   thinned to a point every SPACING metres, so the AV turns in arcs and not
   in the tester's corrections.
2. The height: one cruise height per leg, CRUISE_MARGIN above the highest
   point flown, so no part of the line is lower than the recording. A
   gradual climb or descent in the recording is kept (never below it); a
   jump or a fall becomes a column over the spot. Nothing is raised
   above the recorded climb: the tester flew under things.
3. The ends: the AV leaves its spot with a short run along its own heading
   and comes down over its landing spot, with the same short run, so it
   faces the way the landing needs (the column above each spot is measured
   open to 360 m, the dev menu's sky probe).
4. The speed is not here: the flight path's speed sections set it, the
   game's own cruise for every leg (gen_community.py, _speeds).
"""

import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SPACING = 20.0          # metres between points along the line
SMOOTH_S = 2.0          # seconds of recording averaged into one point
CRUISE_MARGIN = 5.0     # metres above the highest point flown
RAMP = 150.0            # metres over which the AV eases from the recording to the cruise
TOP_BAND = 25.0         # metres below the top of the recording that count as cruising
STEEP = 120.0           # a climb or descent shorter than this along the ground is a column


def _read(name):
    pts = []
    with open(os.path.join(HERE, 'flights', name), encoding='utf-8') as fh:
        for line in fh:
            parts = line.split()
            if len(parts) == 4:
                pts.append(tuple(float(v) for v in parts[1:]))
    return pts


def _smooth(pts, half):
    out = []
    for i in range(len(pts)):
        lo, hi = max(0, i - half), min(len(pts), i + half + 1)
        n = hi - lo
        out.append(tuple(sum(p[k] for p in pts[lo:hi]) / n for k in range(3)))
    out[0], out[-1] = pts[0], pts[-1]
    return out


def _along(pts):
    """Distance along the ground line at each point."""
    d = [0.0]
    for a, b in zip(pts, pts[1:]):
        d.append(d[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    return d


def _resample(pts, step):
    d = _along(pts)
    total = d[-1]
    n = max(2, int(round(total / step)) + 1)
    out, j = [], 0
    for i in range(n):
        s = total * i / (n - 1)
        while j < len(d) - 2 and d[j + 1] < s:
            j += 1
        span = d[j + 1] - d[j] or 1.0
        t = (s - d[j]) / span
        a, b = pts[j], pts[j + 1]
        out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t,
                    a[2] + (b[2] - a[2]) * t, s))
    return out


def _heights(raw, samples, cruise):
    """Height at each sample. One cruise height for the whole middle of the
    leg (the tester's own varied with each double jump). At each end, the
    climb or the descent the recording made, never below it: followed when
    it was gradual, and turned into a column over the spot when it was a
    jump or a fall (shorter than STEEP along the ground)."""
    d_raw = _along(raw)
    z_raw = [p[2] for p in raw]
    near_top = cruise - CRUISE_MARGIN - TOP_BAND
    first_top = next(d for d, z in zip(d_raw, z_raw) if z >= near_top)
    last_top = next(d for d, z in zip(reversed(d_raw), reversed(z_raw)) if z >= near_top)
    climb_from = first_top if first_top > STEEP else 0.0
    land_from = last_top if d_raw[-1] - last_top > STEEP else d_raw[-1]
    fwd, m = [], -1e9
    for z in z_raw:
        m = max(m, z)
        fwd.append(m)
    bwd, m = [0.0] * len(z_raw), -1e9
    for i in range(len(z_raw) - 1, -1, -1):
        m = max(m, z_raw[i])
        bwd[i] = m

    def interp(arr, s):
        j = 0
        while j < len(d_raw) - 2 and d_raw[j + 1] < s:
            j += 1
        span = d_raw[j + 1] - d_raw[j] or 1.0
        t = max(0.0, min(1.0, (s - d_raw[j]) / span))
        return arr[j] + (arr[j + 1] - arr[j]) * t

    # THE CLIMB IS THE RECORDING'S OWN, to the metre, and the AV eases up to
    # the cruise only once the tester had finished climbing (over RAMP
    # metres after it); the same, mirrored, for the descent. Playtest
    # 2026-11-03: a ramp that lifted the climb early put the AV 12 m above
    # the tester's line leaving Kabuki, into something the tester had flown
    # under at 70 m (the dev menu's clearance log, one hit at -1888 1362).
    end = d_raw[-1]
    top_up = interp(fwd, climb_from) if climb_from > 0.0 else cruise
    top_down = interp(bwd, land_from) if land_from < end else cruise
    zs = []
    for p in samples:
        s = p[3]
        z = cruise
        if climb_from > 0.0:
            if s <= climb_from:
                z = min(z, interp(fwd, s))
            elif s < climb_from + RAMP:
                z = min(z, top_up + (cruise - top_up) * (s - climb_from) / RAMP)
        if land_from < end:
            if s >= land_from:
                z = min(z, interp(bwd, s))
            elif s > land_from - RAMP:
                z = min(z, top_down + (cruise - top_down) * (land_from - s) / RAMP)
        zs.append(z)
    return zs


def _trim(raw, start, end, reach=150.0):
    """The recording from where it passes closest over the start spot to
    where it passes closest over the end spot, each looked for within
    `reach` metres of its end of the recording. Leaving Kabuki the tester
    started 20 m east of the spot and came back over it at 27 m: the path
    starts there, reached by the measured column over the spot, rather than
    flying out east and back."""
    d = _along(raw)
    head = [i for i in range(len(raw)) if d[i] <= reach]
    tail = [i for i in range(len(raw)) if d[-1] - d[i] <= reach]
    i0 = min(head, key=lambda i: math.hypot(raw[i][0] - start[0], raw[i][1] - start[1]))
    i1 = min(tail, key=lambda i: math.hypot(raw[i][0] - end[0], raw[i][1] - end[1]))
    return raw[i0:i1 + 1] if i1 > i0 + 2 else raw


# THE TAKEOFF AND THE LANDING ARE STRAIGHT LINES ALONG THE AV'S NOSE, the
# shape of the first flight, the one the tester called smooth: off the pad
# along its heading, 3 m up in the first 4 m, then a steady climb
# (`wat_ich_01_spl_av_fly_off`), and into the hotel roof along its heading,
# nearly flat for the last 10 m (the end of `dtn_04_spl_av_arrive`).
# Playtest 2026-11-03: legs that went straight up and down over the spot
# turned on the spot in the column, both ways, and a 3 m nudge at each end
# made the path double back on itself.
#
# The slope of each straight line is the spot's own, from the dev menu's
# glide probe (`route_glide.txt`): the shallowest angle along that heading
# with nothing in the way.
STEP = 12.0             # metres between the points written to the path
JOIN = 60.0             # metres of the recording given up to each turn
# THE SLOPE BUILDS UP OVER THE FIRST EASE METRES AND DIES AWAY OVER THE LAST.
# Playtest 2026-11-04: with 3 m of rise in the first 4 m the AV's nose came up
# 25 to 30 degrees in the first second. V stands side-on to the AV, so the
# nose coming up tilts V's whole picture, and the same on the way down.
EASE_OUT = 30.0
EASE_IN = 30.0
TURN_RADIUS = 90.0      # metres, the tightest turn in the air


def _lift(s, slope, ease=EASE_OUT):
    return slope * s * s / (2.0 * ease) if s < ease else slope * (s - ease / 2.0)


def _flare(r, slope):
    return slope * r * r / (2.0 * EASE_IN) if r < EASE_IN else slope * (r - EASE_IN / 2.0)


def _unit(dx, dy):
    n = math.hypot(dx, dy) or 1.0
    return dx / n, dy / n


def _fwd(yaw):
    r = math.radians(yaw)
    return -math.sin(r), math.cos(r)


def _mod(x):
    return x % (2.0 * math.pi)


def _dubins(p0, t0, p1, t1, r=None, step=4.0):
    """The shortest ground curve from p0 leaving along t0 to p1 arriving
    along t1 that never turns tighter than radius r: a turn, a straight
    and a turn (a Dubins path). A curve drawn any other way, a cubic's
    handles, folds into a cusp when the ends face apart, which is the AV
    spinning on the spot."""
    r = r or TURN_RADIUS
    th0, th1 = math.atan2(t0[1], t0[0]), math.atan2(t1[1], t1[0])
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    d = math.hypot(dx, dy) / r
    th = math.atan2(dy, dx)
    al, be = _mod(th0 - th), _mod(th1 - th)
    sa, sb, ca, cb = math.sin(al), math.sin(be), math.cos(al), math.cos(be)
    best = None
    tmp = 2 + d * d - 2 * math.cos(al - be) + 2 * d * (sa - sb)
    if tmp >= 0:
        k = math.atan2(cb - ca, d + sa - sb)
        best = min(best or (1e9,), (_mod(-al + k) + math.sqrt(tmp) + _mod(be - k),
                                    'LSL', _mod(-al + k), math.sqrt(tmp), _mod(be - k)))
    tmp = 2 + d * d - 2 * math.cos(al - be) + 2 * d * (sb - sa)
    if tmp >= 0:
        k = math.atan2(ca - cb, d - sa + sb)
        best = min(best or (1e9,), (_mod(al - k) + math.sqrt(tmp) + _mod(-be + k),
                                    'RSR', _mod(al - k), math.sqrt(tmp), _mod(-be + k)))
    tmp = -2 + d * d + 2 * math.cos(al - be) + 2 * d * (sa + sb)
    if tmp >= 0:
        pp = math.sqrt(tmp)
        k = math.atan2(-ca - cb, d + sa + sb) - math.atan2(-2.0, pp)
        best = min(best or (1e9,), (_mod(-al + k) + pp + _mod(-be + k),
                                    'LSR', _mod(-al + k), pp, _mod(-be + k)))
    tmp = d * d - 2 + 2 * math.cos(al - be) - 2 * d * (sa + sb)
    if tmp >= 0:
        pp = math.sqrt(tmp)
        k = math.atan2(ca + cb, d - sa - sb) - math.atan2(2.0, pp)
        best = min(best or (1e9,), (_mod(al - k) + pp + _mod(be - k),
                                    'RSL', _mod(al - k), pp, _mod(be - k)))
    out = []
    x, y, h = p0[0], p0[1], th0
    for kind, length in zip(best[1], best[2:]):
        dist = length * r
        n = max(1, int(dist / step))
        for _ in range(n):
            ds = dist / n
            if kind == 'S':
                x, y = x + math.cos(h) * ds, y + math.sin(h) * ds
            else:
                turn = ds / r if kind == 'L' else -ds / r
                h2 = h + turn
                if kind == 'L':
                    x += r * (math.sin(h2) - math.sin(h))
                    y += r * (-math.cos(h2) + math.cos(h))
                else:
                    x += r * (-math.sin(h2) + math.sin(h))
                    y += r * (math.cos(h2) - math.cos(h))
                h = h2
            out.append((x, y))
    assert math.hypot(x - p1[0], y - p1[1]) < 0.5, ('dubins missed', x, y, p1)
    return out[:-1]


def _resample2(pts, step):
    d = [0.0]
    for a, b in zip(pts, pts[1:]):
        d.append(d[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    total = d[-1]
    n = max(2, int(round(total / step)) + 1)
    out, j = [], 0
    for i in range(n):
        s = total * i / (n - 1)
        while j < len(d) - 2 and d[j + 1] < s:
            j += 1
        span = d[j + 1] - d[j] or 1.0
        t = (s - d[j]) / span
        a, b = pts[j], pts[j + 1]
        out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, s))
    return out


def route(name, start, start_yaw, end, end_yaw, ahead=None, climb=0.47, descent=0.32,
          out_len=110.0, in_len=160.0, cruise=None, turn=None, cap=True, soften=True,
          turn_in=None, ease_out=EASE_OUT):
    """The path for one leg as world points. The ground line: straight out of
    `start` along `start_yaw` for `out_len` metres, a curve onto the
    tester's recording `name`, the recording, a curve off it, and straight
    into `end` along `end_yaw` for the last `in_len` metres. The height:
    up from the start at `climb` (rise over run), one cruise height, down
    into the end at `descent`; never steeper than needed, never a column.
    A leg too short for both is a single climb and a steady descent.
    `turn` is the tightest turn on this leg, TURN_RADIUS when not given;
    `turn_in` the turn onto the last straight, if that one has room to be wider.
    `ease_out` is how far the climb takes to build up.
    `cap` keeps the first half of the climb under the recording's height."""
    raw = _trim(_read(name), start, end)
    smooth = _smooth(raw, max(1, int(SMOOTH_S / 0.5 / 2)))
    if cruise is None:
        cruise = max(p[2] for p in raw) + CRUISE_MARGIN
    rec = _resample(smooth, SPACING)
    f0, f1 = _fwd(start_yaw), _fwd(end_yaw)
    a = (start[0] + f0[0] * out_len, start[1] + f0[1] * out_len)
    b = (end[0] - f1[0] * in_len, end[1] - f1[1] * in_len)
    # WHERE THE TURNS JOIN THE RECORDING: of the recorded points past the
    # straight line out (and before the straight line in), the one that
    # makes the shortest flight. The first point past the straight line can
    # lie behind the AV, and the turn onto it is then a full loop.
    near_a = [i for i, p in enumerate(rec)
              if math.hypot(p[0] - start[0], p[1] - start[1]) < out_len + JOIN
              or math.hypot(p[0] - a[0], p[1] - a[1]) < JOIN]
    near_b = [i for i, p in enumerate(rec)
              if math.hypot(p[0] - end[0], p[1] - end[1]) < in_len + JOIN
              or math.hypot(p[0] - b[0], p[1] - b[1]) < JOIN]
    lo = (max(near_a) + 1) if near_a else 1
    hi = (min(near_b) - 1) if near_b else len(rec) - 2
    hi = min(hi, len(rec) - 2)

    def heading_at(i):
        j, k = max(0, i - 1), min(len(rec) - 1, i + 1)
        return _unit(rec[k][0] - rec[j][0], rec[k][1] - rec[j][1])

    def plen(pts):
        return sum(math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in zip(pts, pts[1:]))

    ground = [(start[0] + f0[0] * d, start[1] + f0[1] * d)
              for d in range(0, int(out_len), 4)] + [a]
    if hi - lo >= 4:
        span = range(lo, hi + 1)

        def no_loop(p, q, curve):
            return plen(curve) <= 1.5 * math.hypot(q[0] - p[0], q[1] - p[1]) + 10.0

        # The first point the turn reaches without a loop, and the last: a
        # turn that joins further along cuts across the tester's line, and
        # off the line nothing has been flown (playtest 2026-11-03: a join
        # 40 m off the recording leaving Kabuki touched roofs both sides).
        i0 = next((i for i in span if no_loop(a, rec[i], [a] + _dubins(
            a, f0, rec[i][:2], heading_at(i), turn))), None)
        if i0 is None:
            i0 = min(span, key=lambda i: plen([a] + _dubins(a, f0, rec[i][:2], heading_at(i), turn))
                     - rec[i][3])
        later = [i for i in span if i > i0 + 1] or [hi]
        i1 = next((i for i in reversed(later) if no_loop(rec[i], b, _dubins(
            rec[i][:2], heading_at(i), b, f1, turn_in or turn) + [b])), None)
        if i1 is None:
            i1 = min(later, key=lambda i: plen(_dubins(rec[i][:2], heading_at(i), b, f1, turn_in or turn) + [b])
                     + rec[i][3])
        mid = [(p[0], p[1]) for p in rec[i0:i1 + 1]]
        ground += (_dubins(a, f0, mid[0], heading_at(i0), turn) + mid
                   + _dubins(mid[-1], heading_at(i1), b, f1, turn_in or turn))
    else:
        ground += _dubins(a, f0, b, f1, turn)
    ground += [b] + [(end[0] - f1[0] * d, end[1] - f1[1] * d)
                     for d in range(int(in_len) - 4, 0, -4)] + [tuple(end[:2])]
    line = _resample2(ground, STEP)
    # THE TURNS BUILD UP AND DIE AWAY: a straight joined to an arc starts
    # turning all at once (the flight log: no turn, then 25 degrees a second).
    # `soften` False leaves the line alone where it threads past buildings:
    # softened leaving Kabuki, it brushed one at 22 m (flight_clear_run8.txt).
    soft_line = list(line)
    for i in range(2, len(line) - 2):
        if soften and out_len < line[i][2] < line[-1][2] - in_len:
            soft_line[i] = (sum(p[0] for p in line[i - 2:i + 3]) / 5.0,
                            sum(p[1] for p in line[i - 2:i + 3]) / 5.0, line[i][2])
    line = soft_line
    total = line[-1][2]
    # A leg too short to reach the cruise and come down from it at these
    # slopes comes down more steeply, never in a column: the descent is
    # steepened until it starts above where the climb is 20 m out.
    need = (start[2] + _lift(40.0, climb, ease_out) - end[2]) / max(1.0, total - 40.0 - EASE_IN / 2.0)
    descent = max(descent, need)
    zs = [min(cruise, start[2] + _lift(s, climb, ease_out), end[2] + _flare(total - s, descent))
          for _x, _y, s in line]
    # Rounded where the climb meets the cruise and the cruise meets the
    # descent, so the AV eases over the top rather than tipping at a corner.
    soft = list(zs)
    for i in range(3, len(zs) - 3):
        if line[i][2] > 25.0 and total - line[i][2] > 25.0:
            soft[i] = sum(zs[i - 3:i + 4]) / 7.0
    # NO HIGHER THAN THE TESTER HAD FLOWN, on the first half of the leg:
    # over each recorded point, the AV is capped a metre under the highest
    # the recording had been by then. Leaving Kabuki the tester flew under a
    # structure at about 105 m, 300 m out, and a steady climb took the AV
    # into it (the dev menu's path probe, 2026-11-03).
    top, best = [], -1e9
    for p in rec:
        best = max(best, p[2])
        top.append(best)
    caps = [1e9] * len(line)
    for i, (x, y, s) in enumerate(line):
        if s > total / 2.0:
            break
        # Not on the straight takeoff, whose slope is the glide probe's.
        if not cap or s < out_len + 20.0:
            continue
        j = min(range(len(rec)), key=lambda k: (rec[k][0] - x) ** 2 + (rec[k][1] - y) ** 2)
        if (rec[j][0] - x) ** 2 + (rec[j][1] - y) ** 2 < 40.0 ** 2:
            caps[i] = top[j] - 1.0
    # A climb that only climbs: anything capped lower further on, up to the
    # top of the climb, lowers what comes before it, and the corners are
    # rounded again.
    soft = [min(z, c) for z, c in zip(soft, caps)]
    half = next((i for i, p in enumerate(line) if p[2] > total / 2.0), len(line) - 1)
    peak = max(range(half + 1), key=lambda i: soft[i])
    for i in range(peak - 1, -1, -1):
        soft[i] = min(soft[i], soft[i + 1])
    for _ in range(3):
        soft = soft[:3] + [sum(soft[i - 3:i + 4]) / 7.0 if line[i][2] > 25.0
                           and total - line[i][2] > 25.0 else soft[i]
                           for i in range(3, len(soft) - 3)] + soft[-3:]
    # The rounding never lifts a point back over its cap: the AV's centre
    # 3 m over the tester's feet still met the underside of that structure.
    soft = [min(z, c) for z, c in zip(soft, caps)]
    pts = [(x, y, z) for (x, y, _s), z in zip(line, soft)]
    pts[0] = tuple(start[:3])
    pts[-1] = tuple(end[:3])
    return pts


def approach_start(pts, back=320.0):
    """The index of the point `back` metres before the end of `pts`, where a
    skipped flight picks up: the AV is put there and flies the rest."""
    d = 0.0
    for i in range(len(pts) - 1, 0, -1):
        d += math.dist(pts[i], pts[i - 1])
        if d >= back:
            return i - 1
    return 0
