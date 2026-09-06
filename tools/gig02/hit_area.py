"""The hit area: the corners walked in play on 2026-09-06, widened into the
shape the game draws and the script tests.

Twenty-three corners were captured with the dev menu's polygon capture, from
the landing west of the top of the stairs down the west side to the den. The
staircase itself sits 1 to 4 m OUTSIDE that walked line, along the edge that
closes it, so the walked polygon is not the area: it is one side of it. The
area is the convex hull of the walked corners, the eight stair positions and
the trash pile, pushed outward by MARGIN metres, so that every step and the
whole den are inside it with room to spare, and the top of the stairs is out.

Two consumers, and they cannot disagree any more. `gen_community.hit_area_node`
writes the hull as the outline of a `worldTriggerAreaNode` in the cast sector
(the shape the minimap draws for a quest map pin that points at a trigger area,
which is how vanilla's 638 `_tr_` pins do it and what ArchiveXL's journal
extension builds the outline from), and `write_reds` below generates
`Gig02_Area.reds`, which is the same corners for the script's leaving test.

THE SCRIPT USED TO CARRY A HAND-COPIED COPY of these numbers, which was right
only while nobody edited one side. It is generated now (2026-09-06): run_all
writes the file, so a change here reaches the game and the script together.
`python tools\\gig02\\hit_area.py` prints the corners and rewrites the file.
"""
import math
import os

WALKED = [
    (-391.466, 1302.449, 41.482), (-402.962, 1300.099, 41.419),
    (-408.280, 1284.643, 37.411), (-395.281, 1284.628, 32.874),
    (-391.045, 1282.364, 24.851), (-390.898, 1260.729, 23.428),
    (-394.778, 1261.337, 23.428), (-394.937, 1259.376, 23.428),
    (-393.182, 1259.020, 23.428), (-393.364, 1256.344, 23.567),
    (-391.033, 1256.341, 23.428), (-391.264, 1248.420, 23.647),
    (-392.736, 1247.754, 24.116), (-390.193, 1239.993, 23.428),
    (-387.745, 1241.211, 23.428), (-377.738, 1225.001, 23.428),
    (-380.939, 1223.342, 23.475), (-379.955, 1218.425, 23.428),
    (-375.483, 1220.829, 23.428), (-371.431, 1215.537, 24.922),
    (-367.728, 1216.430, 23.435), (-370.881, 1209.034, 14.139),
    (-378.467, 1204.888, 14.616),
]
STAIR = [
    (-399.587, 1318.163, 42.167), (-395.667, 1302.594, 41.464),
    (-393.149, 1290.089, 37.449), (-386.443, 1276.179, 33.469),
    (-381.961, 1262.021, 29.458), (-382.124, 1254.921, 27.458),
    (-385.082, 1242.323, 23.428), (-381.087, 1233.990, 23.428),
]
TRASH = (-391.116, 1284.479, 25.910)
# THE SNIPER'S WALKWAY (playtest 2026-09-06): Toji shot from the elevated
# walkway east of the den, 61 m up, half a metre outside the hull's east edge
# and above its old 45 m top, so the game counted V outside and drew nothing.
# The perch joins the hull's base points, and the height reaches it.
PERCH = (-368.272, 1242.907, 60.901)

# THE TOP STEP IS NOT IN THE AREA. Stair 0 is where V arrives and where the
# way-out marker sits; the area is what V has to get out of, so the hull is
# built without it and the margin stops short of it.
# 12 m all round (design call 2026-09-06: the walkway showed the edge was
# tight, so every edge got the same room). The top step is still outside.
MARGIN = 12.0

# AN EXTRA NODE OF THE CAST COMMUNITY'S SECTOR, so it is named the way
# questkit names them (`community.Community.ref('cc_g02_cast', ...)`) and is
# resident everywhere, the sector being always loaded. The first test put a
# bare trigger node in the gig's Exterior sector under a `$/03_night_city/...`
# name with a shard case's instance flags, and the pin found no position; the
# second made it a security-area device here, and the pin found its position
# but no area, because ArchiveXL builds the area only from a
# `worldAreaShapeNode`. Backlog 39 has all three.
AREA_REF = '$/mod/cc_g02_cast/#cc_g02_hit_area'
# TALL ENOUGH FOR A SNIPER (playtest 2026-09-06: shooting Toji from the
# walkway above the den, inside the footprint, V was above the prism, so the
# game counted V outside, hid the outline and showed the marker). The node
# sits 2 m under the lowest ground; 90 m reaches the rooftops and bridges.
AREA_HEIGHT = 90.0


def _hull(points):
    """Andrew's monotone chain, counter-clockwise."""
    pts = sorted(set((round(x, 3), round(y, 3)) for x, y in points))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def _offset(hull, d):
    """Push a convex, counter-clockwise polygon outward by d metres: each
    corner moves along the bisector of its two edge normals."""
    n = len(hull)
    out = []
    for i in range(n):
        px, py = hull[i - 1]
        cx, cy = hull[i]
        nx, ny = hull[(i + 1) % n]
        # outward normals of the two edges meeting at this corner (CCW: right)
        e1 = (cx - px, cy - py)
        e2 = (nx - cx, ny - cy)
        n1 = (e1[1], -e1[0])
        n2 = (e2[1], -e2[0])
        l1 = math.hypot(*n1) or 1.0
        l2 = math.hypot(*n2) or 1.0
        n1 = (n1[0] / l1, n1[1] / l1)
        n2 = (n2[0] / l2, n2[1] / l2)
        bx, by = n1[0] + n2[0], n1[1] + n2[1]
        bl = math.hypot(bx, by) or 1.0
        bx, by = bx / bl, by / bl
        cos_half = bx * n1[0] + by * n1[1]
        scale = d / max(cos_half, 0.3)
        out.append((round(cx + bx * scale, 3), round(cy + by * scale, 3)))
    return out


def corners():
    """The area's corners in world X and Y, counter-clockwise."""
    base = [(x, y) for x, y, _z in WALKED] + [(x, y) for x, y, _z in STAIR[1:]] \
        + [TRASH[:2], PERCH[:2]]
    return _offset(_hull(base), MARGIN)


def position():
    """Where the node sits: the centroid, at the lowest ground the area
    reaches minus a little, so the outline's height covers the whole drop."""
    cs = corners()
    cx = sum(x for x, _y in cs) / len(cs)
    cy = sum(y for _x, y in cs) / len(cs)
    zmin = min(z for _x, _y, z in WALKED + STAIR)
    return (round(cx, 3), round(cy, 3), round(zmin - 2.0, 3))


def inside(x, y, cs=None):
    cs = cs or corners()
    c = False
    n = len(cs)
    for i in range(n):
        x1, y1 = cs[i]
        x2, y2 = cs[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xi = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if xi > x:
                c = not c
    return c


REDS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'mods', 'gig-02-dead-ringer', 'source', 'scripts', 'Gig02_Area.reds')


def write_reds():
    """Generate the area's corners as redscript. Called by run_all."""
    cs = corners()

    def arr(name, vals):
        out = ['    public static func %s() -> array<Float> {' % name,
               '        let a: array<Float>;']
        out += ['        ArrayPush(a, %.3f);' % v for v in vals]
        out += ['        return a;', '    }']
        return out

    lines = [
        '// GENERATED BY tools/gig02/hit_area.py. DO NOT EDIT.',
        '//',
        "// The hit area's corners: the convex hull of the 23 corners walked in",
        "// play on 2026-09-06, the stairs, the trash pile and the sniper's",
        '// walkway, pushed out by %g m. The top step is outside on purpose,' % MARGIN,
        '// because it is where V arrives and where the way-out marker sits.',
        '//',
        '// THE SAME CORNERS are the outline of the trigger area node the way-out',
        '// pins point at (gen_community.hit_area_node), so the shape the minimap',
        '// draws is the shape that ends the leg. They were a hand-copied copy',
        '// until 2026-09-06; regenerate rather than edit.',
        'module CyberpunkCodes.Gig02',
        '',
        'public class CCGig02Area {',
    ]
    lines += arr('X', [c[0] for c in cs])
    lines.append('')
    lines += arr('Y', [c[1] for c in cs])
    lines.append('}')
    text = chr(10).join(lines) + chr(10)
    tmp = REDS + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline=chr(10)) as fh:
        fh.write(text)
    os.replace(tmp, REDS)
    return REDS


if __name__ == '__main__':
    cs = corners()
    print('%d corners, node at %s' % (len(cs), position()))
    for c in cs:
        print('  %.3f, %.3f' % c)
    for i, (x, y, _z) in enumerate(STAIR):
        print('stair %d %s' % (i, 'inside' if inside(x, y, cs) else 'OUTSIDE'))
    print('wrote', write_reds())
