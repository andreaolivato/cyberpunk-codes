r"""Flight paths for an AV: the `worldSpeedSplineNode` a quest flies one along.

EVERY AV MOVEMENT IN A VANILLA QUEST PHASE IS `questMoveOnSpline_NodeType`
on one of these (a grep of 3837 questphases, 2026-11-03; the AI vehicle
commands appear only on cars). The node here is the game's own Trauma Team
flight paths in Little China, field for field:
`quest_ed5d1add73ffee63.streamingsector` nodes 5 (`wat_ich_01_spl_av_spawn`,
the descent to the ground) and 51 (`wat_ich_01_spl_av_fly_off`, the climb
away), the minor activity `ma_wat_lch_01`.

WHAT THE TWO VANILLA PATHS SAY ABOUT LANDING. The descent comes down from
121 m to the ground in 258 m of path, at 19.4 m/s, then slows to 0.8 m/s
over the last 58 m (`speedChangeSections` 0-3 m at 19.4, 200-258 m at 0.8).
The climb starts on the same ground point at 6 m/s, 16.7 by 15 m, 25 by
40 m, and keeps its pitch level in world space
(`KeepYawRoll_WorldSpacePitch`). Speed sections are in metres along the
path. The vanilla AV is set down by the path alone: no landing clip.

POINTS ARE LOCAL to the node's position, which is the first point, the
shape gig 04's patrol path (`tools/gig04/gen_room.py`, spline_node) uses.
Tangents are written by hand, as four of the five vanilla climb points have them.

    node, origin = speed_spline('cc_g05_spl_pad_out', points,
                                speeds=[(0, 2, 6.0), (2, 15, 16.7), (30, 40, 25.0)],
                                level_pitch=True)

UNPLAYED: no mod here has shipped a speed spline or flown a vehicle on one.
"""
import math


def _vec3(p):
    return {'$type': 'Vector3', 'X': float(p[0]), 'Y': float(p[1]), 'Z': float(p[2])}


def _cname(v):
    return {'$type': 'CName', '$storage': 'string', '$value': v if v else 'None'}


def length(pts):
    """The path's length in metres along its points, the straight-line sum.
    The engine's curve is a little longer than this; speed sections near the
    end are written against this figure minus a margin."""
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


def speed_spline(name, pts, speeds, level_pitch=False):
    """A `worldSpeedSplineNode` through the world points `pts`.

    `speeds` is [(start_m, end_m, metres_per_second), ...], the vanilla
    `speedChangeSections`. `level_pitch` adds the climb path's one
    orientation section, which keeps the AV level while it climbs.
    """
    origin = pts[0]
    points = []
    for i, p in enumerate(pts):
        local = (p[0] - origin[0], p[1] - origin[1], p[2] - origin[2])
        prev = pts[max(i - 1, 0)]
        nxt = pts[min(i + 1, len(pts) - 1)]
        # A HANDLE A THIRD OF THE WAY TO THE NEXT POINT, the smooth curve through evenly
        # spaced points. The engine's automatic tangents stepped the AV's heading at
        # every point (the flight log, playtest 2026-11-05).
        t = tuple((nxt[k] - prev[k]) / 6.0 for k in range(3))
        points.append({
            '$type': 'SplinePoint',
            'automaticTangents': 0,
            'continuousTangents': 1,
            'id': 0,
            'position': _vec3(local),
            'rotation': {'$type': 'Quaternion', 'i': 0, 'j': 0, 'k': 0, 'r': 1},
            'tangents': {'Elements': [_vec3(tuple(-v for v in t)), _vec3(t)]},
        })
    node = {
        '$type': 'worldSpeedSplineNode',
        'debugName': _cname('{%s}' % name),
        'deprecatedDefaultAdjustTime': 0,
        'deprecatedDefaultSpeed': 0,
        'deprecatedSpeedRestrictions': [{
            '$type': 'worldSpeedSplineNodeSpeedRestriction',
            'adjustTime': 0, 'from': 0, 'speed': 0}],
        'destSnapedNode': {'$type': 'NodeRef', '$storage': 'uint64', '$value': '0'},
        'destSnapedSocketName': _cname(None),
        'entrySnapedNode': {'$type': 'NodeRef', '$storage': 'uint64', '$value': '0'},
        'entrySnapedSocketName': _cname(None),
        # BOTH VANILLA AV PATHS CARRY 1: the path is not pressed onto the
        # ground under it.
        'ignoreTerrain': 1,
        'isHostOnly': 0,
        'isVisibleInGame': 1,
        'orientationChangeSections': ([{
            '$type': 'worldSpeedSplineNodeOrientationChangeSection',
            'pos': 0,
            'targetOrientation': {'$type': 'EulerAngles', 'Pitch': 0, 'Roll': 0, 'Yaw': 0},
            'type': 'KeepYawRoll_WorldSpacePitch'}] if level_pitch else []),
        'proxyScale': None,
        'roadAdjustmentFactorChangeSections': [],
        'sourcePrefabHash': '0',
        'speedChangeSections': [{
            '$type': 'worldSpeedSplineNodeSpeedChangeSection',
            'end': float(e), 'start': float(s), 'targetSpeed_M_P_S': float(v)}
            for s, e, v in speeds],
        'splineData': {'HandleId': '0', 'Data': {
            '$type': 'Spline', 'hasDirection': 1, 'looped': 0,
            'points': points, 'reversed': 0}},
        'tag': 'None',
        'tagExt': 'None',
        'useDeprecated': 0,
    }
    return node, origin


def _even(pts, step):
    """Points every `step` metres along the straight lines between `pts`."""
    at = [0.0]
    for a, b in zip(pts, pts[1:]):
        at.append(at[-1] + math.dist(a, b))
    n = max(2, int(round(at[-1] / step)) + 1)
    out, j = [], 0
    for i in range(n):
        s = at[-1] * i / (n - 1)
        while j < len(at) - 2 and at[j + 1] < s:
            j += 1
        t = (s - at[j]) / ((at[j + 1] - at[j]) or 1.0)
        out.append(tuple(pts[j][k] + (pts[j + 1][k] - pts[j][k]) * t for k in range(3)))
    return out


def fair(pts, spacing=8.0, blur=8, passes=2, hold_start=40.0, hold_end=14.0, ease=40.0, flare=24.0):
    """THE PATH AS THE AV FLIES IT: even points, and every corner rounded.

    The flight log (playtest 2026-11-04) measured what uneven points do. Short
    spans beside long ones gave a 6 degree flick in a tenth of a second where they
    met. A corner on the last approach swung the AV 40 degrees and back in 1.5 s.
    In any turn the heading moved in steps, one at each 12 m point.

    The line is cut every 2 m and blurred over `blur` samples either side, `passes`
    times, then written every `spacing` metres. The first `hold_start` and last
    `hold_end` metres do not move, and the blur comes in over `ease` metres, so the
    AV still climbs off the ground as steeply and arrives on its landing line. The last `flare` metres curve down to
    level: the AV's nose moves steadily along the whole path to the slope at its
    last point, and a landing that ended on a slope was snapped flat at touchdown."""
    line = _even(pts, 2.0)
    n = len(line)
    run = 2.0 * (n - 1)

    def weight(i):
        s = 2.0 * i
        return max(0.0, min(1.0, (s - hold_start) / ease, (run - s - hold_end) / ease))

    for _ in range(passes):
        out = []
        for i, p in enumerate(line):
            w = weight(i)
            lo, hi = max(0, i - blur), min(n - 1, i + blur)
            mean = [sum(q[k] for q in line[lo:hi + 1]) / (hi - lo + 1) for k in range(3)]
            out.append(tuple(p[k] + (mean[k] - p[k]) * w for k in range(3)))
        line = out
    line = _even(line, spacing)
    end, start = pts[-1], pts[0]
    line[0], line[-1] = tuple(start[:3]), tuple(end[:3])
    top = next(p[2] for p in line if math.dist(p[:2], end[:2]) < flare)
    level = [(p[0], p[1], end[2] + (top - end[2]) * (math.dist(p[:2], end[:2]) / flare) ** 2)
             if math.dist(p[:2], end[:2]) < flare else p for p in line]
    level[1] = (level[1][0], level[1][1], start[2])
    last = level[-2]
    run_in = math.dist(last[:2], end[:2]) or 1.0
    near = (end[0] + (last[0] - end[0]) * 2.0 / run_in, end[1] + (last[1] - end[1]) * 2.0 / run_in, end[2])
    return level[:-1] + [near, level[-1]]


def sample(pts, step=8.0):
    """Points every `step` metres or so along the curve the AV flies through
    `pts`: Catmull-Rom, the curve automatic tangents give a spline."""
    out = []
    n = len(pts)
    for i in range(n - 1):
        p0, p1, p2 = pts[max(i - 1, 0)], pts[i], pts[i + 1]
        p3 = pts[min(i + 2, n - 1)]
        m1 = [(p2[k] - p0[k]) / 2.0 for k in range(3)]
        m2 = [(p3[k] - p1[k]) / 2.0 for k in range(3)]
        seg = math.dist(p1, p2)
        steps = max(1, int(seg / step))
        for s in range(steps):
            t = s / steps
            h00, h10 = 2 * t**3 - 3 * t**2 + 1, t**3 - 2 * t**2 + t
            h01, h11 = -2 * t**3 + 3 * t**2, t**3 - t**2
            out.append(tuple(h00 * p1[k] + h10 * m1[k] + h01 * p2[k] + h11 * m2[k]
                             for k in range(3)))
    out.append(tuple(pts[-1][:3]))
    return out


# THE TWO VANILLA SPEED PROFILES, so a path can be written as "a descent" or
# "a climb" and get the game's own numbers.
def descent_speeds(total, cruise=19.4, touchdown=0.8, slow_for=58.0):
    """The Little China descent: cruise speed from the start, slowing to a
    walking pace over the last `slow_for` metres (vanilla: 19.4 m/s, then 0.8
    over the last 58 m of 258)."""
    slow_from = max(total - slow_for, 3.0)
    return [(0, 3, cruise), (slow_from, total, touchdown)]


def climb_speeds():
    """The Little China climb: 6 m/s off the ground, 16.7 by 15 m, 25 by
    40 m."""
    return [(0, 2, 6.0), (2, 15, 16.7), (30, 40, 25.0)]


def arc(start, end, peak, n=6):
    """Points on a smooth climb or descent between two world points, rising
    to `peak` metres above the higher of the two ends at the middle. A
    quadratic Bezier, sampled; the engine's tangents do the rest."""
    top = max(start[2], end[2]) + peak
    mid = ((start[0] + end[0]) / 2.0, (start[1] + end[1]) / 2.0, top)
    out = []
    for i in range(n + 1):
        t = i / float(n)
        out.append(tuple((1 - t) ** 2 * start[k] + 2 * (1 - t) * t * mid[k] + t ** 2 * end[k]
                         for k in range(3)))
    return out


def approach(land, heading_deg, start_dist=420.0, start_alt=110.0, flare=40.0):
    """A descent onto `land` from `start_dist` metres away along
    `heading_deg` (the direction the AV flies, the game's yaw: 0 is +Y),
    `start_alt` metres above it. It comes in high, drops most of the height
    in the first two thirds, and makes its last `flare` metres nearly flat,
    the shape of the vanilla descent's last three points."""
    rad = math.radians(heading_deg)
    dx, dy = -math.sin(rad), math.cos(rad)
    def at(back, up):
        return (land[0] - dx * back, land[1] - dy * back, land[2] + up)
    return [at(start_dist, start_alt),
            at(start_dist * 0.66, start_alt * 0.62),
            at(start_dist * 0.33, start_alt * 0.25),
            at(flare * 1.6, 8.0),
            at(flare * 0.6, 2.0),
            at(0.0, 0.0)]


def departure(lift, heading_deg, dist=900.0, alt=180.0):
    """A climb away from `lift` along `heading_deg`: a few metres straight
    up first, then away and up, the vanilla climb's shape (its first point is
    on the ground, its second 18 m up and 96 m out)."""
    rad = math.radians(heading_deg)
    dx, dy = -math.sin(rad), math.cos(rad)
    def at(out, up):
        return (lift[0] + dx * out, lift[1] + dy * out, lift[2] + up)
    return [at(0.0, 0.0),
            at(4.0, 6.0),
            at(dist * 0.1, alt * 0.12),
            at(dist * 0.45, alt * 0.55),
            at(dist, alt)]
