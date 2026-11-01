r"""Return Ticket: the room's floor sewn into the game's navigation mesh.

    python tools\gig04\gen_navmesh.py
    python tools\gig04\gen_navmesh.py --refresh   # re-pull the source (needs the game)

WHY. An NPC walks the navigation mesh and nothing else: not the collision,
not the walls. The mesh is baked when the game is built, and the building
this room is set into was never meant to be entered, so the baked mesh
reaches 3.2 m in through the doorway (the entrance's own floor) and stops
at a straight edge. Eight Tyger Claws placed behind that edge walked at V
through the walls (playtest 2026-10-01, gotcha 128), and nothing in
ArchiveXL adds a mesh. But the mesh is shipped as ordinary files, and a mod
archive can replace a file.

WHAT THE GAME SHIPS. `navigation_<x>_<y>_<z>_3.streamingsector`, category
Navigation, 3,846 of them, named on a 256 m grid (x -32..31 is the whole
world, Badlands included; the sector at (-6, 6) is x -1536..-1280, y
1536..1792). Each holds `worldNavigationNode`s whose
`worldNavigationTileResource` is embedded: one resource per 162 m square
and per agent (Human, Vehicle), 25 tiles of 32.4 m, plus a second copy of
any tile that has a variant (a door or gate state, keyed by id). A tile's
bytes are a Recast/Detour tile: magic DNAV, version 8, 100-byte header,
Detour's section order, three differences from stock Detour: three
vertices per polygon (20-byte polys), 64-bit polygon references (16-byte
links, zero in the file), and the coordinates are plain metres with the
height on Detour's Y (X = world x, Y = world z, Z = world y). The human
agent is 0.3 m wide, 1.8 m tall and climbs 0.6 m. Flags 3 on every
polygon; area 3 on the street, 4 upstairs, +128 on some. Gotcha 129.

The first build of this generator (2026-10-01) read the tiles in the far
corner of the world, where every tile is a two-triangle slab, took the
slab's 32.4 m tile for 8.1 m and its heights for tenths, and rebuilt nine
tiles 6 km from the room. Every reading in game stayed the same. The
units above were settled by the sector that actually holds the room,
whose street polygons sit at 18.40 m, the height the game's own query
returned at the door.

WHAT THIS WRITES. Phantom Liberty's copy of the one sector that holds the
room's tiles (with Phantom Liberty installed, the game loads its copy),
with the room's floor
added to the human tiles the building touches: the lobby, the hall, the
cell and the two doorways as polygons (gen_room.walkable_polygons), cut to
each tile, as new triangles at the floor's height, plus one threshold
polygon across the street door joined to the street's own floor (gotcha
129). The game's own polygons that cross the room's walls or lie inside it
are switched off first ("THROUGH THE WALLS"). The new polygons are linked
to each other along the edges they share,
portal edges on the tile borders the floor crosses, walls everywhere
else, and each tile's bounding-volume tree rebuilt. Nothing of the game's
own mesh is removed: a polygon switched off stays in the tile, with flags 0
and no links. Written under `base\...` in the raw folder, so the archive
overrides the game's file.

The source is `tools/gig04/nav_source/`, an untracked cache (8 MB of
JSON); it is pulled with the WolvenKit CLI when missing, or on --refresh.
"""
import base64
import json
import math
import os
import re
import struct
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gig04_config as cfg                                           # noqa: E402
import gen_room                                                      # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.join(HERE, 'nav_source')
OUT_DIR = os.path.join(cfg.RAW, 'base', 'worlds', '03_night_city', '_compiled', 'default')

CLI = os.path.expandvars(r'%LOCALAPPDATA%\Programs\WolvenKit.CLI\WolvenKit.CLI.exe')
EP1 = r'C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077\archive\pc\ep1\ep1_1_nightcity.archive'

# ------------------------------------------------------------- the units
TILE = 32.4                      # metres; a resource is 5 by 5 of them
SECTOR_CELL = 256.0              # metres; the sector's name is its cell
EPS = 1e-3

# The walkable floor comes from gen_room.walkable_polygons(): the lobby, the
# hall, the cell and the two doorways between them, inset 0.3 m (the
# agent's width) from every wall, with the big props bitten out. The lobby
# is as wide as the street door's wall, which is where the baked edge is
# looked for.
HW = cfg.LOBBY_U[1] - gen_room.AGENT
# The floor's height on the mesh: 0.15 m over the floor, which is 0.06 m
# under the street polygons' 18.40 at the door.
FLOOR = cfg.ROOM_DOOR[2] + 0.15
# A new polygon takes the flags of every polygon and the area of the
# polygon it is sewn to.
FLAGS = 3
AREA = 3

HDR = '<4s14i3f3f3ff'            # 100 bytes


# --------------------------------------------------------------- the tile
def parse(raw):
    """A tile's bytes as lists. Vertices are kept in Detour order (X, Y
    up, Z); world (x, y, z) is (X, Z, Y)."""
    h = struct.unpack_from(HDR, raw, 0)
    t = {'magic': h[0], 'version': h[1], 'x': h[2], 'y': h[3], 'layer': h[4], 'userId': h[5],
         'nlink': h[8], 'nbv': h[12], 'noc': h[13], 'ombase': h[14],
         'agent': h[15:18], 'bmin': h[18:21], 'bmax': h[21:24], 'quant': h[24]}
    npoly, nvert, nlink, ndm, ndv, ndt, nbv = h[6], h[7], h[8], h[9], h[10], h[11], h[12]
    off = 100
    t['verts'] = [list(struct.unpack_from('<3f', raw, off + 12 * i)) for i in range(nvert)]
    off += 12 * nvert
    t['polys'] = []
    for i in range(npoly):
        p = struct.unpack_from('<I3H3HHBB', raw, off + 20 * i)
        t['polys'].append({'link': p[0], 'v': list(p[1:4]), 'nei': list(p[4:7]),
                           'flags': p[7], 'nv': p[8], 'area': p[9]})
    off += 20 * npoly
    t['links'] = raw[off:off + 16 * nlink]
    off += 16 * nlink
    t['dm'] = [struct.unpack_from('<IIBBxx', raw, off + 12 * i) for i in range(ndm)]
    off += 12 * ndm
    t['dv'] = raw[off:off + 12 * ndv]
    off += 12 * ndv
    t['dt'] = [raw[off + 4 * i:off + 4 * i + 4] for i in range(ndt)]
    off += 4 * ndt
    t['bv'] = [struct.unpack_from('<3H3Hi', raw, off + 16 * i) for i in range(nbv)]
    off += 16 * nbv
    t['om'] = raw[off:]
    return t


def portals(t):
    return sum(1 for p in t['polys'] for n in p['nei'] if n & 0x8000 and (n & 0xf) != 0xf)


def bv_tree(t):
    """Detour's createBVTree: items quantised against the tile's bmin at
    the header's quant (truncated, as Detour does), split on the longest
    axis, leaves carry the polygon index, inner nodes the negative escape;
    two nodes allocated per polygon, the unused ones zero."""
    bmin, q = t['bmin'], t['quant']

    def quantise(v, a):
        # The baked bounds are the vertices' own grid coordinates (0.1 m
        # cells), and a vertex stored as a float is a hair off its cell:
        # 16.9995 for 17. Rounding recovers 43,910 of the 43,910 leaves
        # of the shipped sector; truncation, Detour's own code, misses
        # 35,250 of them.
        return max(0, min(0xffff, int(round((v - bmin[a]) * q))))
    items = []
    # Off-mesh connections are polygons past ombase and have no leaf.
    for i, p in enumerate(t['polys'][:t['ombase']]):
        vs = [t['verts'][k] for k in p['v']]
        lo = [min(v[a] for v in vs) for a in range(3)]
        hi = [max(v[a] for v in vs) for a in range(3)]
        items.append({'i': i,
                      'bmin': [quantise(lo[a], a) for a in range(3)],
                      'bmax': [quantise(hi[a], a) for a in range(3)]})
    nodes = []

    def subdivide(its):
        node = {}
        nodes.append(node)
        if len(its) == 1:
            node['bmin'], node['bmax'], node['i'] = its[0]['bmin'], its[0]['bmax'], its[0]['i']
            return
        lo = [min(it['bmin'][a] for it in its) for a in range(3)]
        hi = [max(it['bmax'][a] for it in its) for a in range(3)]
        node['bmin'], node['bmax'] = lo, hi
        ext = [hi[a] - lo[a] for a in range(3)]
        axis = 0
        if ext[1] > ext[axis]:
            axis = 1
        if ext[2] > ext[axis]:
            axis = 2
        its = sorted(its, key=lambda it: it['bmin'][axis])
        cur = len(nodes)
        half = len(its) // 2
        subdivide(its[:half])
        subdivide(its[half:])
        node['i'] = -(len(nodes) - cur + 1)
    if items:
        subdivide(items)
    while len(nodes) < 2 * t['ombase']:
        nodes.append({'bmin': [0, 0, 0], 'bmax': [0, 0, 0], 'i': 0})
    return nodes


def pack(t):
    """The tile's bytes from its lists, counts recomputed, links zeroed,
    the BV tree rebuilt."""
    npoly, nvert = len(t['polys']), len(t['verts'])
    nlink = 3 * npoly + 2 * portals(t)
    nodes = bv_tree(t)
    out = bytearray()
    out += struct.pack(HDR, t['magic'], t['version'], t['x'], t['y'], t['layer'], t['userId'],
                       npoly, nvert, nlink, len(t['dm']), len(t['dv']) // 12, len(t['dt']),
                       len(nodes), t['noc'], t['ombase'], *t['agent'], *t['bmin'], *t['bmax'], t['quant'])
    for v in t['verts']:
        out += struct.pack('<3f', *v)
    for p in t['polys']:
        out += struct.pack('<I3H3HHBB', p['link'], *p['v'], *p['nei'], p['flags'], p['nv'], p['area'])
    out += bytes(16 * nlink)
    for d in t['dm']:
        out += struct.pack('<IIBBxx', *d)
    out += t['dv']
    for d in t['dt']:
        out += bytes(d)
    for n in nodes:
        out += struct.pack('<3H3Hi', *n['bmin'], *n['bmax'], n['i'])
    out += t['om']
    return bytes(out)


def round_trip_check(raw):
    """An untouched tile packs back to its own bytes up to the BV tree,
    and to the same length; the tree's order can differ."""
    t = parse(raw)
    new = pack(t)
    bv_off = len(raw) - len(t['om']) - 16 * len(t['bv'])
    if new[:bv_off] != raw[:bv_off] or len(new) != len(raw):
        raise SystemExit('tile (%d, %d): the parser does not reproduce the game\'s bytes' % (t['x'], t['y']))


# --------------------------------------------------------------- geometry
def w(u, v):
    x, y, _ = gen_room.room_to_world(u, v)
    return (x, y)


def room_v(p):
    dx, dy = p[0] - gen_room.DX, p[1] - gen_room.DY
    return dx * gen_room.V[0] + dy * gen_room.V[1]


def room_u(p):
    dx, dy = p[0] - gen_room.DX, p[1] - gen_room.DY
    return dx * gen_room.U[0] + dy * gen_room.U[1]


def same(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1]) < EPS


def clip(poly, a, b):
    """Sutherland-Hodgman: keep the left of the directed line a->b. A vertex
    on the line is kept as it is."""
    def inside(p):
        return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) >= -EPS

    def cross(p, q):
        dx1, dy1 = b[0] - a[0], b[1] - a[1]
        dx2, dy2 = q[0] - p[0], q[1] - p[1]
        den = dx1 * dy2 - dy1 * dx2
        s = ((a[0] - p[0]) * dy1 - (a[1] - p[1]) * dx1) / -den
        return (p[0] + dx2 * s, p[1] + dy2 * s)

    out = []
    for i, p in enumerate(poly):
        q = poly[(i + 1) % len(poly)]
        if inside(p):
            out.append(p)
            if not inside(q):
                out.append(cross(p, q))
        elif inside(q):
            out.append(cross(p, q))
    res = []
    for p in out:
        if not res or not same(p, res[-1]):
            res.append(p)
    if len(res) > 1 and same(res[0], res[-1]):
        res.pop()
    return res


def clip_to_square(poly, x0, y0, x1, y1):
    for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        poly = clip(poly, a, b)
        if len(poly) < 3:
            return []
    return poly


def signed_area(poly):
    return sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
               for i in range(len(poly))) / 2


def wind(poly):
    """The game's winding: clockwise in world x, y (read off the shipped
    tiles)."""
    return poly if signed_area(poly) < 0 else list(reversed(poly))


def triangulate(poly):
    """Ear clipping of a simple clockwise polygon. The front edge is a
    polyline of the baked mesh's vertices, so the polygon is not convex
    in general. Index triples into poly."""
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    def in_tri(p, a, b, c):
        d1, d2, d3 = cross(a, b, p), cross(b, c, p), cross(c, a, p)
        return not ((d1 > EPS or d2 > EPS or d3 > EPS) and (d1 < -EPS or d2 < -EPS or d3 < -EPS))

    # A point that repeats adds nothing; drop it. A point on the line
    # between its neighbours STAYS: it is where a doorway polygon meets
    # this one, and the two link only through that shared edge.
    clean = []
    for i, p in enumerate(poly):
        q = poly[(i + 1) % len(poly)]
        if same(p, q):
            continue
        clean.append(p)
    poly = clean
    idx = list(range(len(poly)))
    tris = []
    guard = 0
    while len(idx) > 3:
        guard += 1
        if guard > 10000:
            raise SystemExit('triangulation did not finish')
        found = False
        for k in range(len(idx)):
            i0, i1, i2 = idx[k - 1], idx[k], idx[(k + 1) % len(idx)]
            a, b, c = poly[i0], poly[i1], poly[i2]
            if cross(a, b, c) >= -1e-4:          # a clockwise ear turns right
                continue
            if any(in_tri(poly[j], a, b, c) for j in idx if j not in (i0, i1, i2)):
                continue
            tris.append((i0, i1, i2))
            del idx[k]
            found = True
            break
        if not found:
            raise SystemExit('no ear found: the floor polygon is not simple: %s'
                             % ' '.join('(u%.2f v%.2f)' % (room_u(poly[k]), room_v(poly[k])) for k in idx))
    tris.append(tuple(idx))
    return [t for t in tris if abs(cross(poly[t[0]], poly[t[1]], poly[t[2]])) > 1e-4]


# --------------------------------------------------------------- the seam
def tile_of(p):
    return (math.floor(p[0] / TILE), math.floor(p[1] / TILE))


def room_polygons():
    """The floor as clockwise polygons in world metres, as gen_room lays
    it. Shared points between polygons are the same coordinates, so the
    seam links them."""
    return [(name, wind([w(u, v) for u, v in poly]))
            for name, poly in gen_room.walkable_polygons()]


# ------------------------------------------------------ through the walls
#
# THE GAME'S OWN FLOOR RAN THROUGH THE ROOM'S WALLS. The building was never
# meant to be entered, so its baked floor is a strip of large triangles
# from 1.5 m out on the pavement to 3.2 m inside, right across the line the
# room's front wall stands on, and two more across its right wall
# (measured 2026-10-13: fifteen triangles across a wall, four links joining
# floor on either side of one). An NPC could walk the street to the strip
# and the strip into the lobby, through the wall (playtest 2026-10-13:
# "ensure guards from orbital air cannot pass through walls"). The strip
# also overlapped the hall's own floor.
#
# So every polygon of the game's at the room's floor height that crosses
# one of the room's walls, or lies inside the room, is switched off: flags
# 0, which no walker's filter passes, and every link to it cut on both
# sides, its own portal edges included, so no tile joins to it either. The
# room's floor covers the inside from the wall's inner face, and the
# threshold is the one way through the front wall.
def seg_cross(p, q, a, b):
    def cross(o, s, t):
        return (s[0] - o[0]) * (t[1] - o[1]) - (s[1] - o[1]) * (t[0] - o[0])
    return (cross(a, b, p) * cross(a, b, q) < 0) and (cross(p, q, a) * cross(p, q, b) < 0)


def room_uv(p):
    return (room_u(p), room_v(p))


def switch_off_through_walls(t):
    """Switch off the tile's own polygons that cross a wall of the room or
    lie inside it, at the floor's height. Returns how many."""
    walls = [(a, b) for a, b, _i, _l in gen_room.wall_runs()]
    u0, u1 = cfg.ROOM_U
    v0, v1 = cfg.ROOM_V
    off = set()
    for i, p in enumerate(t['polys'][:t['ombase']]):
        if p['flags'] == 0:
            continue
        vs = [t['verts'][k] for k in p['v']]
        if any(abs(v[1] - FLOOR) > 1.2 for v in vs):
            continue
        uvs = [room_uv((v[0], v[2])) for v in vs]
        cu = sum(q[0] for q in uvs) / 3
        cv = sum(q[1] for q in uvs) / 3
        inside = u0 < cu < u1 and v0 < cv < v1
        crosses = any(seg_cross(uvs[e], uvs[(e + 1) % 3], a, b)
                      for e in range(3) for a, b in walls)
        if inside or crosses:
            off.add(i)
    for i in off:
        p = t['polys'][i]
        p['flags'] = 0
        for e in range(3):
            n = p['nei'][e]
            if n and not n & 0x8000:
                q = t['polys'][n - 1]
                q['nei'] = [0 if m == i + 1 else m for m in q['nei']]
            p['nei'][e] = 0
    return len(off)


def border_side(p, q, tx, ty):
    x0, y0 = tx * TILE, ty * TILE
    x1, y1 = x0 + TILE, y0 + TILE
    if abs(p[0] - x1) < EPS and abs(q[0] - x1) < EPS:
        return 0
    if abs(p[1] - y1) < EPS and abs(q[1] - y1) < EPS:
        return 2
    if abs(p[0] - x0) < EPS and abs(q[0] - x0) < EPS:
        return 4
    if abs(p[1] - y0) < EPS and abs(q[1] - y0) < EPS:
        return 6
    return None


def sew(t, tx, ty, polys, area):
    """Add the parts of the floor polygons inside this tile to the tile,
    sewn to the baked mesh along any edge they share with it and to each
    other along the edges they share. Returns how many polygons were
    added."""
    x0, y0 = tx * TILE, ty * TILE
    parts = []
    for _name, poly in polys:
        part = clip_to_square(poly, x0, y0, x0 + TILE, y0 + TILE)
        if len(part) >= 3:
            parts.append(wind(part))
    if not parts:
        return 0
    # vertices: reuse the tile's own where a point coincides with one near
    # the floor's height, so a shared edge is the same two indices
    index = {}

    def vid(p):
        key = (round(p[0], 3), round(p[1], 3))
        if key in index:
            return index[key]
        for i, v in enumerate(t['verts']):
            if abs(v[1] - FLOOR) < 1.0 and same((v[0], v[2]), p):
                index[key] = i
                return i
        t['verts'].append([p[0], FLOOR, p[1]])
        index[key] = len(t['verts']) - 1
        return index[key]

    # the baked mesh's boundary edges by vertex pair, to sew to
    boundary = {}
    for i, p in enumerate(t['polys']):
        for e in range(3):
            if p['nei'][e] == 0:
                boundary[(p['v'][e], p['v'][(e + 1) % 3])] = (i, e)
    base = len(t['polys'])
    new = []
    for part in parts:
        for tri in triangulate(part):
            pts = [part[k] for k in tri]
            # the game's winding, whatever the clipping left
            if signed_area(pts) > 0:
                pts.reverse()
            vs = [vid(p) for p in pts]
            new.append({'link': 0, 'v': vs, 'nei': [0, 0, 0], 'flags': FLAGS, 'nv': 3, 'area': area})
    for i, p in enumerate(new):
        for e in range(3):
            a, b = p['v'][e], p['v'][(e + 1) % 3]
            nei = 0
            for j, q in enumerate(new):
                if j == i:
                    continue
                for f in range(3):
                    if q['v'][f] == b and q['v'][(f + 1) % 3] == a:
                        nei = base + j + 1
            if not nei and (b, a) in boundary:
                bi, be = boundary[(b, a)]
                nei = bi + 1
                t['polys'][bi]['nei'][be] = base + i + 1
            if not nei:
                pa = (t['verts'][a][0], t['verts'][a][2])
                pb = (t['verts'][b][0], t['verts'][b][2])
                side = border_side(pa, pb, tx, ty)
                if side is not None:
                    nei = 0x8000 | side
            p['nei'][e] = nei
    for p in new:
        t['polys'].append(p)
        t['dm'].append((0, len(t['dt']), 0, 1))
        t['dt'].append(bytes((0, 1, 2, 0x15)))
    t['ombase'] = len(t['polys'])
    return len(new)


# ------------------------------------------------------------ the threshold
#
# THE DOOR LINE HAS NO FLOOR. The street's floor stops 0.6 m outside the
# door, and the game links the two sides of a working door with a second
# copy of the tile for its open state; this tile has none, the door here
# having been fake (gotcha 130). So the room and the street were two
# pieces, and Orbital Air stood outside (playtest 2026-10-01).
#
# One polygon across the door line: the street's open edge at the door, by
# its own three vertices so that seam links (an edge links only whole), and
# the lobby's two door points (gen_room.DOOR_PASS) on the room's side. The
# street's edge runs 0.7 m past the door's opening on each side, so the
# polygon narrows to the lobby's points and crosses the wall line inside
# the door's frame. The quest holds the street door open from the moment
# the room is armed (Gig04_Places.reds, OpenDoor), so the floor is never
# laid through a shut door.
THRESHOLD_TILE = (-45, 47)
THRESHOLD_STREET = [(2.14, -0.62), (0.24, -0.55), (-2.18, -0.64)]


def threshold_polygon(t):
    """The threshold as a world polygon: the lobby's two door points, then
    the street's three vertices read off the tile (each within 3 cm of the
    point above, at the street's height)."""
    a = gen_room.AGENT
    pts = [w(-gen_room.DOOR_PASS, a), w(gen_room.DOOR_PASS, a)]
    for u, v in THRESHOLD_STREET:
        x, y = w(u, v)
        best = None
        for vert in t['verts']:
            if abs(vert[1] - 18.40) > 0.3:
                continue
            d = math.hypot(vert[0] - x, vert[2] - y)
            if d < 0.03 and (best is None or d < best[0]):
                best = (d, (vert[0], vert[2]))
        if best is None:
            raise SystemExit('threshold: no vertex of tile %s at u %.2f v %.2f; '
                             'the baked mesh has changed' % (THRESHOLD_TILE, u, v))
        pts.append(best[1])
    return wind(pts)


# -------------------------------------------------------------- the sector
def sector_name(x, y):
    return 'navigation_%d_%d_' % (math.floor(x / SECTOR_CELL), math.floor(y / SECTOR_CELL))


def refresh():
    """Pull every z-level of the sector cell the door is in; the right one
    is the one whose human resource holds the room's tiles."""
    os.makedirs(SOURCE_DIR, exist_ok=True)
    for f in os.listdir(SOURCE_DIR):
        if f.endswith('.json'):
            os.remove(os.path.join(SOURCE_DIR, f))
    stage = os.path.join(SOURCE_DIR, '_stage')
    os.makedirs(stage, exist_ok=True)
    pat = re.escape(sector_name(cfg.ROOM_DOOR[0], cfg.ROOM_DOOR[1])) + r'-?\d+_3\.streamingsector$'
    subprocess.run([CLI, 'unbundle', EP1, '-o', stage, '-r', pat, '-v', 'Quiet'], check=True)
    files = []
    for dp, _d, fs in os.walk(stage):
        files += [os.path.join(dp, f) for f in fs if f.endswith('.streamingsector')]
    if not files:
        raise SystemExit('no navigation sector matched %s in %s' % (pat, EP1))
    subprocess.run([CLI, 'convert', 'serialize'] + files + ['-o', SOURCE_DIR, '-v', 'Quiet'], check=True)
    print('refreshed %d sector(s) into %s' % (len(files), SOURCE_DIR))


def room_tiles():
    """Every tile some part of the walkable floor lies in (a tile inside
    the floor's bounding box that no polygon reaches is left alone)."""
    polys = [[w(u, v) for u, v in poly] for _name, poly in gen_room.walkable_polygons()]
    pts = [p for poly in polys for p in poly]
    xs = [tile_of(p)[0] for p in pts]
    ys = [tile_of(p)[1] for p in pts]
    out = set()
    for x in range(min(xs), max(xs) + 1):
        for y in range(min(ys), max(ys) + 1):
            x0, y0 = x * TILE, y * TILE
            if any(len(clip_to_square(poly, x0, y0, x0 + TILE, y0 + TILE)) >= 3 for poly in polys):
                out.add((x, y))
    return out


def main():
    if '--refresh' in sys.argv or not os.path.isdir(SOURCE_DIR) or not any(f.endswith('.json') for f in os.listdir(SOURCE_DIR)):
        refresh()
    os.makedirs(OUT_DIR, exist_ok=True)
    wanted = room_tiles()
    # the stale output of the first build, nine tiles in the Badlands
    stale = os.path.join(OUT_DIR, 'navigation_-23_23_0_3.streamingsector.json')
    if os.path.exists(stale):
        os.remove(stale)
        print('removed the stale', stale)
    written = 0
    for name in sorted(os.listdir(SOURCE_DIR)):
        if not name.endswith('.streamingsector.json'):
            continue
        with open(os.path.join(SOURCE_DIR, name), encoding='utf-8') as fh:
            doc = json.load(fh)
        changed = 0
        for emb in doc['Data']['EmbeddedFiles']:
            res = emb['Content']
            if res['agentSize'] != 'Human':
                continue
            have = {(td['tileX'], td['tileY']) for td in res['tilesData']}
            if not wanted <= have:
                continue
            # every buffer of a wanted tile, variants included
            targets = [td for td in res['tilesData'] if (td['tileX'], td['tileY']) in wanted]
            tiles = {}
            for td in targets:
                raw = base64.b64decode(res['tileBuffers'][td['bufferIndex']]['Bytes'])
                round_trip_check(raw)
                tiles[(td['tileX'], td['tileY'], td['bufferIndex'])] = parse(raw)
            polys = room_polygons()
            area = AREA
            for (tx, ty, bi), t in tiles.items():
                if t['noc']:
                    raise SystemExit('tile (%d, %d) has off-mesh connections; the packer does not move those' % (tx, ty))
                off = switch_off_through_walls(t)
                before = len(t['polys'])
                here = list(polys)
                if (tx, ty) == THRESHOLD_TILE:
                    here.append(('threshold', threshold_polygon(t)))
                added = sew(t, tx, ty, here, area)
                print('    tile (%d, %d) buffer %d: %d of the game\'s polygons switched off '
                      'through the walls' % (tx, ty, bi, off))
                if (tx, ty) == THRESHOLD_TILE:
                    # THE STREET'S TWO EDGES must have linked to the
                    # threshold: links from the game's own walkable polygons
                    # to new triangles lying outside the front wall's line.
                    def outside(k):
                        q = t['polys'][k]
                        c = [t['verts'][m] for m in q['v']]
                        return room_v((sum(x[0] for x in c) / 3, sum(x[2] for x in c) / 3)) < 0.0
                    street = sum(1 for q in t['polys'][:before] if q['flags']
                                 for n in q['nei'] if n > before and not n & 0x8000
                                 and outside(n - 1))
                    print('    the threshold: %d edges linked to the street' % street)
                    if street != 2:
                        raise SystemExit('the threshold linked %d edges to the street, 2 wanted'
                                         % street)
                new = pack(t)
                res['tileBuffers'][bi]['Bytes'] = base64.b64encode(new).decode('ascii')
                changed += 1
                sewn = sum(1 for p in t['polys'][:before] for n in p['nei'] if n > before)
                print('    tile (%d, %d) buffer %d: %d polys + %d room, %d sewn edges, %d bytes'
                      % (tx, ty, bi, before, added, sewn, len(new)))
        if not changed:
            continue
        out = os.path.join(OUT_DIR, name)
        with open(out, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(doc, fh, indent=2)
        print('wrote %s (%d tile buffer(s) rebuilt)' % (out, changed))
        written += 1
    if not written:
        raise SystemExit('no sector in %s holds the room\'s tiles %s' % (SOURCE_DIR, sorted(wanted)))


if __name__ == '__main__':
    main()
