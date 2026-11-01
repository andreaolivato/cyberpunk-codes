r"""Return Ticket: the building, a whole interior the gig builds behind a fake door.

    python tools\gig04\gen_room.py

Writes, under source\wkit\raw:

  mod\worlds\03_night_city\_compiled\default\cc_g04_room.streamingsector
  mod\worlds\03_night_city\_compiled\default\cc_g04_room.streamingblock

WHY. No free, full, run-down interior exists in Watson: every one belongs to
a gig, a quest or a police event, and every gig shuts its building when it
ends (all 23 Watson gigs' phases, read 2026-09-30). The design call chose to
build one instead. The fake double door captured in Little China stands in a
building shell 48 m wide and 18 m deep that has nothing inside, not even a
floor (the teleport test of 2026-09-30 fell through it). So this file lays
three rooms in that shell out of the game's own pieces: a lobby behind the
street door, a hall with couches for the Claws, and a cell with its own
door where Bayani is kept (gig04_config, "THE BUILDING").

WHAT IT SHIPS, all of it copied from shipped data rather than typed:

  * FLOOR, WALLS, CEILING: `worldStaticMeshNode`s on the game's own interior
    kit (`int_common_a`, the most used pieces across 2,402 interior sectors).
    The node is the shape of a vanilla static mesh node
    (interior_-16_17_1_0, a fuse box); the mesh sizes were read off the
    meshes' own bounding boxes: a floor tile is 3 x 3 m with its origin at
    its +x +y corner and 0.2 m of thickness below the surface, a wall piece
    is 3 (or 1) m long from its origin towards -x, 0.23 m thick towards +y,
    3.8 m tall; a ceiling piece is 3 x 3 m with 0.1 m above. A doorway in
    an inside wall is a gap in the run with a wall piece raised over it as
    the lintel.
  * COLLISION: one `worldCollisionNode` of box shapes, the shape of the
    game's own. Actors are in world coordinates (FixedPoint, bits / 131072,
    checked against the node's own position on a vanilla node); a box's
    `Size` is HALF extents in a frame every shipped box shape rotates with
    the same fixed quaternion (0, 0.7071, 0.7071, 0), which swaps y and z:
    `Size` (x, y, z) is world half (x, z, y). Read off two vanilla boxes and
    their node extents. Without this node the floor is a picture and V falls
    through it, as V did through the empty shell.
  * LIGHT: point lights, the node lifted from a vanilla interior lamp
    (10 m, 500 lumen, no local shadows).
  * THE DOORS: the game's own working double door in the same look as the
    fake one (`double_door.ent`, `doors_double_kitsch_g`), lifted whole from
    exterior_-25_18_0_0 with its DoorController state, placed exactly where
    the fake door stands, named `$/mod/cc_g04_room/#cc_g04_room_door`; and
    a single sliding door (`single_door.ent`, lifted by lift_door.py) in
    the cell's wall, `#cc_g04_cell_door`. The fake door and its two
    distance proxies are deleted through the manifest (gotcha 47).
  * THE ROUTE OUT: a `worldPatrolSplineNode`, `#cc_g04_leave_path`, from the cell
    to the street, which the quest sends Bayani along (gen_questphase).
  * THE WALKABLE FLOOR, as polygons for gen_navmesh.py, which sews them into
    the game's navigation mesh (gotcha 129).

THE ROOM FRAME. u along the front wall to the right when facing in, v from
the door into the building, the door's yaw as the frame's. `room_to_world`
is the one conversion, used here and by gen_community.py for the people.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from questkit import cr2w                                            # noqa: E402
import gig04_config as cfg                                           # noqa: E402
from gig04_config import ROOM_DOOR, ROOM_HEIGHT                      # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
B = chr(92)


def depot(*parts):
    return B.join(parts)


OUT = os.path.join(cfg.RAW, 'mod', 'worlds', '03_night_city', '_compiled', 'default')
SECTOR = 'cc_g04_room'
SECTOR_DEPOT = depot('mod', 'worlds', '03_night_city', '_compiled', 'default',
                     SECTOR + '.streamingsector')
DOOR_REF = '$/mod/' + SECTOR + '/#cc_g04_room_door'
CELL_DOOR_REF = '$/mod/' + SECTOR + '/#cc_g04_cell_door'
LEAVE_PATH_REF = '$/mod/' + SECTOR + '/#cc_g04_leave_path'
LEAVE_PATH2_REF = '$/mod/' + SECTOR + '/#cc_g04_leave_path2'
# BAYANI'S WALK TO THE HALL and ORBITAL AIR'S THREE WAYS IN (gig04_config
# ROOM_BYE_PATH, OA_PATHS), patrol splines like the run's, since 2026-10-25.
BYE_PATH_REF = '$/mod/' + SECTOR + '/#cc_g04_bye_path'
OA_PATH_REFS = ['$/mod/' + SECTOR + '/#cc_g04_oa_path%d' % (i + 1)
                for i in range(len(cfg.OA_PATHS))]

KIT = depot('base', 'environment', 'architecture', 'common', 'int', 'int_common_a')
FLOOR = depot(KIT, 'int_common_a_floor_l300_a.mesh')
CEILING = depot(KIT, 'int_common_a_ceiling_l300_a.mesh')
WALL3 = depot(KIT, 'int_common_a_wall_h400_l300_a.mesh')
WALL1 = depot(KIT, 'int_common_a_wall_h400_l100_a.mesh')

DOOR_SOURCE = os.path.join(HERE, 'door_node.json')
CELL_DOOR_SOURCE = os.path.join(HERE, 'door_single.json')
LIGHT_SOURCE = os.path.join(HERE, 'light_node.json')

# ------------------------------------------------------------- the frame
DX, DY, DZ, DYAW = ROOM_DOOR
_a = math.radians(DYAW)
# A yaw of theta faces (-sin, cos) (gig 02's measured convention). The door
# faces the street; the room is behind it.
FACE = (-math.sin(_a), math.cos(_a))
U = (FACE[1], -FACE[0])          # along the front wall, to the right facing in
V = (-FACE[0], -FACE[1])         # into the room


def room_to_world(x, y, z=0.0):
    return (DX + U[0] * x + V[0] * y, DY + U[1] * x + V[1] * y, DZ + z)


def room_yaw(yaw):
    """A yaw in the room frame (0 faces +v, into the building; 180 faces the
    street door) as a world yaw."""
    return DYAW + 180.0 + yaw


def quat_yaw(deg):
    h = math.radians(deg) / 2.0
    return {'$type': 'Quaternion', 'i': 0, 'j': 0, 'k': math.sin(h), 'r': math.cos(h)}


def qmul(a, b):
    """Hamilton product a * b, on the sector's {i, j, k, r} shape."""
    return {'$type': 'Quaternion',
            'i': a['r'] * b['i'] + a['i'] * b['r'] + a['j'] * b['k'] - a['k'] * b['j'],
            'j': a['r'] * b['j'] - a['i'] * b['k'] + a['j'] * b['r'] + a['k'] * b['i'],
            'k': a['r'] * b['k'] + a['i'] * b['j'] - a['j'] * b['i'] + a['k'] * b['r'],
            'r': a['r'] * b['r'] - a['i'] * b['i'] - a['j'] * b['j'] - a['k'] * b['k']}


def with_tilt(yaw_q, src):
    """The yaw we want, with the tilt the game placed the prop with.

    A prop's source instance orientation is its yaw times a tilt (a roll or
    pitch the mesh needs to stand up, when its author built it on its
    side). The tilt is what is left after the source's own yaw is taken
    off, and it goes under our yaw. A source with no tilt gives our yaw
    back unchanged.
    """
    if not src:
        return yaw_q
    s = {'i': src['i'], 'j': src['j'], 'k': src['k'], 'r': src['r']}
    src_yaw = math.degrees(math.atan2(2 * (s['r'] * s['k'] + s['i'] * s['j']),
                                      1 - 2 * (s['j'] ** 2 + s['k'] ** 2)))
    y = quat_yaw(src_yaw)
    y_inv = {'i': -y['i'], 'j': -y['j'], 'k': -y['k'], 'r': y['r']}
    tilt = qmul(y_inv, s)
    if abs(tilt['i']) < 1e-3 and abs(tilt['j']) < 1e-3:
        return yaw_q
    return qmul(yaw_q, tilt)


def vec3(p):
    return {'$type': 'Vector3', 'X': p[0], 'Y': p[1], 'Z': p[2]}


def vec4(p, w=0):
    return {'$type': 'Vector4', 'W': w, 'X': p[0], 'Y': p[1], 'Z': p[2]}


def cname(v):
    return {'$type': 'CName', '$storage': 'string', '$value': v}


# ------------------------------------------------------------ the layout
#
# Every wall is a run from a room point to a room point with the room on
# one side; every opening is a gap between two runs. Interior walls are
# listed once and built with a face each way.
U0, U1 = cfg.ROOM_U
V0, V1 = cfg.ROOM_V
LU0, LU1 = cfg.LOBBY_U
LV0, LV1 = cfg.LOBBY_V
GAP0, GAP1 = cfg.LOBBY_GAP
CU0, CU1 = cfg.CELL_U
CV0, CV1 = cfg.CELL_V
CD0, CD1 = cfg.CELL_DOOR
# How wide the opening in the front wall is. The kitsch double door is
# 2.6 m across its frame.
DOOR_GAP = 3.0
# Over a doorway in an inside wall: a wall piece raised to this height.
LINTEL_Z = 2.6

WALL_THICK = 0.23


def wall_runs():
    """(a, b, inside, label): each wall as a run from a to b in the room
    frame, `inside` the room-frame direction the wall faces. A run that ends
    at a doorway STARTS at the doorway, so the overshoot goes into a
    corner."""
    g = DOOR_GAP / 2
    return [
        # the outer walls
        ((U0, V1), (U1, V1), (0, -1), 'back'),
        ((U0, V0), (U0, V1), (1, 0), 'left'),
        ((U1, V0), (U1, V1), (-1, 0), 'right'),
        ((-g, V0), (U0, V0), (0, 1), 'front_left'),
        ((g, V0), (U1, V0), (0, 1), 'front_right'),
        # the lobby: its left wall and its back wall either side of the gap
        ((LU0, LV0), (LU0, LV1), (1, 0), 'lobby_left'),
        ((GAP0, LV1), (LU0, LV1), (0, -1), 'lobby_back_left'),
        ((GAP1, LV1), (LU1, LV1), (0, -1), 'lobby_back_right'),
        # the cell: its left wall and its front wall either side of its door
        ((CU0, CV0), (CU0, CV1), (1, 0), 'cell_left'),
        ((CD0, CV0), (CU0, CV0), (0, 1), 'cell_front_left'),
        ((CD1, CV0), (CU1, CV0), (0, 1), 'cell_front_right'),
    ]


def lintels():
    """(a, b, inside): a wall piece raised over each inside doorway."""
    return [
        ((GAP0, LV1), (GAP1, LV1), (0, -1)),
        ((CD0, CV0), (CD1, CV0), (0, 1)),
    ]


# ---------------------------------------------------------- the pieces
#
# Each piece is (mesh, node position in the room frame, world yaw). A mesh's
# +x rotated by yaw t points along (cos t, sin t), its +y along (-sin t,
# cos t).
#
# The room's own yaw R puts a mesh's +x along U and +y along -V (out of the
# room), which is what a floor tile and a ceiling tile want: their 3 x 3 m
# body lies at -x, -y from the origin, so a tile at room (xr, yf) covers
# x in [xr - 3, xr] and y in [yf, yf + 3].
R = DYAW


def floor_tiles():
    """THE LAST COLUMN REACHES PAST THE RIGHT WALL. The room is 19.6 m
    across and the tiles 3 m, so stopping at the wall left a 1.6 m strip
    with no floor and no ceiling the whole depth of the room (playtest
    2026-10-14, "a hole in the floor"). The extra 1.4 m lies behind the
    right wall, inside the shell's own empty space (gig04_config, THE
    BUILDING)."""
    out = []
    xr = U0 + 3.0
    while xr - 3.0 < U1 - 0.01:
        yf = V0
        while yf < V1 - 0.01:
            out.append((FLOOR, (xr, yf, 0.0), R))
            out.append((CEILING, (xr, yf, ROOM_HEIGHT), R))
            yf += 3.0
        xr += 3.0
    return out


# A WALL PIECE'S VISIBLE FACE POINTS ALONG ITS OWN +Y, read off the mesh's
# triangles (2026-10-01: 80 % of the wall's area faces +Y, the floor's
# faces +Z, the ceiling's faces -Z). The first build put +Y outward on every
# wall, so from inside V looked through all four of them at the city
# (playtest 2026-10-01, "I can see cars outside"). The body of a piece runs
# from its origin to -X, 0.23 m thick toward +Y, L metres long.
def world_dir(dx, dy):
    """A direction given in the room frame, as a world unit vector."""
    x = U[0] * dx + V[0] * dy
    y = U[1] * dx + V[1] * dy
    n = math.hypot(x, y)
    return (x / n, y / n)


def wall_run(a, b, inside, pieces, z=0.0, setback=0.0):
    """Tile a wall from room point `a` toward room point `b`, with the
    room on the `inside` side (a room-frame direction). Each piece faces
    the room; the run may overshoot `b` by up to a metre, into the corner,
    where the next wall hides it. `setback` moves the run away from the
    room by that much (a lintel, hidden behind the wall it overlaps).
    Returns (mesh, world pos, world yaw)."""
    ax, ay = room_to_world(a[0] - inside[0] * setback, a[1] - inside[1] * setback)[:2]
    bx, by = room_to_world(b[0] - inside[0] * setback, b[1] - inside[1] * setback)[:2]
    n = world_dir(*inside)
    length = math.hypot(bx - ax, by - ay)
    s = ((bx - ax) / length, (by - ay) / length)
    # Local +y must be n, so local +x is d = n turned a quarter clockwise,
    # and the piece covers from its origin back along -d.
    d = (n[1], -n[0])
    yaw = math.degrees(math.atan2(d[1], d[0]))
    along = s[0] * d[0] + s[1] * d[1]      # +1: d runs a->b, -1: b->a
    out = []
    done = 0.0
    for mesh, L in pieces:
        if done >= length - 0.01:
            break
        if along < 0:
            ox, oy = ax + s[0] * done, ay + s[1] * done
        else:
            ox, oy = ax + s[0] * (done + L), ay + s[1] * (done + L)
        out.append((mesh, (ox, oy, DZ + z), yaw))
        done += L
    return out


def tiles_for(length):
    """3 m pieces, then 1 m pieces, to cover `length`."""
    out = []
    done = 0.0
    while done + 3.0 <= length + 0.01:
        out.append((WALL3, 3.0))
        done += 3.0
    while done < length - 0.01:
        out.append((WALL1, 1.0))
        done += 1.0
    return out


def walls():
    out = []
    for a, b, inside, _label in wall_runs():
        length = math.hypot(b[0] - a[0], b[1] - a[1])
        pieces = tiles_for(length)
        out += wall_run(a, b, inside, pieces)
        # EVERY WALL TWICE, THE SECOND COPY FACING OUT. Two builds have
        # stood with the walls see-through from inside (playtests
        # 2026-10-01, the second after turning every piece round on the
        # strength of the mesh's own normals, whose sign the reader could
        # not pin down). The copy faces the other way and its body lies
        # on the other side of the line; whichever side the engine draws,
        # V sees a wall, and the copy that faces away is hidden behind it.
        # For an inside wall the copy is the other room's face.
        out += wall_run(a, b, (-inside[0], -inside[1]), pieces)
    for a, b, inside in lintels():
        length = math.hypot(b[0] - a[0], b[1] - a[1])
        pieces = tiles_for(math.ceil(length))
        # The lintel overshoots into the wall beside the doorway; set back
        # 2 cm so the overlap hides behind that wall's face.
        out += wall_run(a, b, inside, pieces, z=LINTEL_Z, setback=0.02)
        out += wall_run(a, b, (-inside[0], -inside[1]), pieces, z=LINTEL_Z, setback=0.02)
    return out


def ceiling_flipped():
    """A second ceiling, rolled over, 0.1 m above the first, for the same
    reason the walls are doubled: (mesh, room position, orientation)."""
    h = math.radians(R) / 2.0
    # Yaw R, then a half turn about the piece's own X: (i, j, k, r) =
    # (cos, sin, 0, 0). The roll sends the body's -y to +y and its z under
    # the origin, so the origin moves 3 m further in and 0.1 m up.
    q = {'$type': 'Quaternion', 'i': math.cos(h), 'j': math.sin(h), 'k': 0.0, 'r': 0.0}
    out = []
    xr = U0 + 3.0
    while xr < U1 + 0.01:
        yf = V0
        while yf < V1 - 0.01:
            out.append((CEILING, (xr, yf + 3.0, ROOM_HEIGHT + 0.1), q))
            yf += 3.0
        xr += 3.0
    return out


# ------------------------------------------------------------ the dressing
#
# THE SCAVENGERS' OWN PROPS, lifted whole from the game (lift_props.py,
# props_scav.json): the node as shipped, placed where this room wants it.
# (mesh file, room u, room v, room yaw). A prop's front (+Y of its mesh)
# faces its yaw: a couch with yaw 90 is sat on facing the right. Sizes from
# the meshes' bounding boxes: the long couch is 3.2 by 1.3 m, the short one
# 1.5 by 1.3, the diner sofa 2.0 by 0.8, a shelf 0.6 by 1.9 (a or c) or 0.7
# by 2.1 (f), the rig 2.1 by 2.2 and 0.3 tall.
PROPS_SOURCE = os.path.join(HERE, 'props_scav.json')
PROPS = [
    # the hall: couches along the left wall, facing the room
    ('poor_sofa_a_old.mesh', -12.9, 8.0, 90.0),
    ('poor_sofa_b_old.mesh', -12.9, 11.5, 90.0),
    ('poor_residential_chair_c.mesh', -10.5, 10.0, 270.0),
    ('floor_carpet_c.mesh', -10.0, 9.5, 5.0),
    # the lounge under the front wall, left of the lobby
    ('poor_sofa_a.mesh', -10.0, 0.75, 0.0),
    ('diner_sofa_01_c.mesh', -7.0, 3.5, 270.0),
    ('floor_carpet_b.mesh', -10.0, 3.0, 90.0),
    ('cable_coil_c.mesh', -12.5, 2.5, 40.0),
    # shelves along the back wall
    ('industrial_shelf_a.mesh', -8.0, 17.6, 90.0),
    ('industrial_shelf_f.mesh', -11.5, 17.6, 90.0),
    ('industrial_shelf_c.mesh', -4.0, 17.6, 90.0),
    ('gas_tank_d.mesh', 5.3, 6.2, 0.0),
    ('military_case_i.mesh', -7.5, 16.6, 110.0),
    # the lobby
    ('plastic_floor_mat_a.mesh', 0.0, 2.0, 5.0),
    ('cardboard_trash_a.mesh', 4.5, 1.6, 70.0),
    ('street_trash_d.mesh', -4.5, 3.5, 120.0),
    ('garbage_bag_c.mesh', 5.0, 3.8, 60.0),
    # the cell: the rig and the cart Bayani is kept with
    ('poor_braindance_a_base.mesh', 3.5, 16.7, 180.0),
    ('braindance_cable_set_b.mesh', 2.2, 16.2, 90.0),
    ('medical_cart_c.mesh', 1.8, 16.6, 160.0),
    ('cardboard_box_b_closed.mesh', 5.2, 14.0, 25.0),
    ('cleaning_rag_c_bloody.mesh', 3.0, 15.8, 30.0),
    ('cleaning_rag_c_bloody.mesh', 4.4, 14.6, 300.0),
    # what lies about the hall
    ('cardboard_trash_a.mesh', -3.8, 10.0, 200.0),
    ('cardboard_trash_a.mesh', -12.0, 15.5, 310.0),
    ('street_trash_d.mesh', -1.0, 11.5, 250.0),
    ('postal_box_e.mesh', -6.5, 16.8, 80.0),
    ('barrel_drum_e_destroyed.mesh', -12.9, 16.8, 0.0),
    ('garbage_bag_l_pile.mesh', 0.2, 16.9, 190.0),
    ('cleaning_rag_b.mesh', -10.0, 12.0, 100.0),
    ('newspaper_b_full.mesh', -11.0, 6.0, 170.0),
    ('newspaper_k_pile.mesh', -12.5, 4.5, 50.0),
    ('drink_bottle_b_wine.mesh', -11.3, 8.6, 0.0),
    ('drink_bottle_e_beer.mesh', -11.1, 11.0, 0.0),
    ('drink_bottle_e_beer.mesh', -10.8, 1.8, 0.0),
]
# Ceiling lamps, the bar's long tube, under the ceiling.
LAMPS = [
    ('ceiling_lamp_long_a.mesh', 0.0, 2.5, 90.0),
    ('ceiling_lamp_long_a.mesh', -10.0, 2.5, 90.0),
    ('ceiling_lamp_long_a.mesh', -10.0, 9.5, 90.0),
    ('ceiling_lamp_long_a.mesh', -4.0, 9.5, 90.0),
    ('ceiling_lamp_long_a.mesh', -10.0, 15.0, 90.0),
    ('ceiling_lamp_long_a.mesh', -4.0, 15.0, 90.0),
    ('ceiling_lamp_long_a.mesh', 3.5, 15.5, 0.0),
]
# Floor decals: (material, room u, room v, room yaw).
DECALS = [
    ('blood_g.mi', 3.0, 15.2, 20.0),
    ('blood_b.mi', 2.4, 14.3, 140.0),
    ('blood_f.mi', 4.2, 16.0, 90.0),
    ('blood_decal_06.mi', -9.0, 7.5, 60.0),
    ('blood_g.mi', 0.5, 2.8, 300.0),
    ('decal_trash_06.mi', -3.5, 4.5, 10.0),
    ('decal_trash_06.mi', -11.5, 12.5, 220.0),
    ('dirt_f.mi', 0.0, 1.5, 0.0),
    ('dirt_f.mi', -11.0, 8.0, 120.0),
    ('dirt_f.mi', -1.5, 10.5, 240.0),
    ('dirt_l.mi', -8.0, 14.5, 30.0),
    ('dirt_l.mi', -1.0, 7.0, 200.0),
    ('dirt_l.mi', -12.0, 2.0, 80.0),
]


def lifted():
    with open(PROPS_SOURCE, encoding='utf-8') as fh:
        return json.load(fh)


def dressing():
    """(node, world pos, world orient, flags) for every prop, lamp and
    decal, each node a fresh copy of the lifted one."""
    src = lifted()
    out = []
    for mesh, x, y, yaw in PROPS:
        rec = src['props'][mesh]
        node = json.loads(json.dumps(rec['node']))
        node['debugName'] = cname('cc_g04_' + mesh[:-5])
        out.append((node, room_to_world(x, y, 0.0),
                    with_tilt(quat_yaw(room_yaw(yaw)), rec.get('orientation')),
                    rec['flags']))
    for mesh, x, y, yaw in LAMPS:
        rec = src['props'][mesh]
        node = json.loads(json.dumps(rec['node']))
        node['debugName'] = cname('cc_g04_lamp')
        out.append((node, room_to_world(x, y, ROOM_HEIGHT - 0.05),
                    quat_yaw(room_yaw(yaw)), rec['flags']))
    for mat, x, y, yaw in DECALS:
        rec = src['decals'][mat]
        node = json.loads(json.dumps(rec['node']))
        node['debugName'] = cname('cc_g04_' + mat[:-3])
        # A floor decal's lifted orientation is a yaw; this one's is ours.
        out.append((node, room_to_world(x, y, 0.02), quat_yaw(room_yaw(yaw)),
                    rec['flags']))
    return out


# THE LOOK OF EACH KIT PIECE, by name, and never `default`. Three builds
# rendered the floor and nothing else, and the floor is the one piece
# whose appearance list has no `default`: asked for a name it lacks, the
# engine fell back to its first appearance (terracotta tiles, which is what
# showed) and drew it. The wall and the ceiling do have a `default`
# appearance, and it drew nothing. The names here are the ones the game
# puts on these pieces when it places them as static nodes (read off the
# sector cache 2026-10-01: walls `concrete_bare` 28 times, ceilings
# `concrete` 127, floors `tiles_grey` 16).
APPEARANCE = {
    FLOOR: 'tiles_grey',
    CEILING: 'concrete',
    WALL3: 'concrete_bare',
    WALL1: 'concrete_bare',
}


# HOW FAR AWAY A KIT PIECE STOPS BEING DRAWN, and how far away it streams
# in. The game's own static wall (interior_-12_17_0_1 instance 166) carries
# 98.77 for both; across 15,846 static meshes in 500 interior sectors not
# one has `forceAutoHideDistance` 0, which is what four builds of this room
# wrote (read 2026-10-01). The streaming ref point (`Bounds`, a point, not
# a box, on every one of those 15,846) is the piece's centre, not its
# origin, and `Pivot` is a real point near the piece.
KIT_HIDE_DISTANCE = 98.7732315
# A piece's centre in its own frame, from the mesh bounding boxes.
KIT_CENTRE = {
    FLOOR: (-1.5, -1.5, -0.1),
    CEILING: (-1.5, -1.5, 0.05),
    WALL3: (-1.5, 0.115, 1.9),
    WALL1: (-0.5, 0.115, 1.9),
}


def mesh_node(label, mesh, appearance=None, hide=None):
    """The shape of a vanilla static mesh node (interior_-16_17_1_0 node 84),
    with the mesh and the name ours."""
    if appearance is None:
        appearance = APPEARANCE.get(mesh, 'default')
    if hide is None:
        hide = KIT_HIDE_DISTANCE if mesh in KIT_CENTRE else 0
    return {
        '$type': 'worldStaticMeshNode',
        'castLocalShadows': 'Always',
        'castRayTracedGlobalShadows': 'Always',
        'castRayTracedLocalShadows': 'Always',
        'castShadows': 'Always',
        'debugName': cname(label),
        'forceAutoHideDistance': hide,
        'isHostOnly': 0,
        'isVisibleInGame': 1,
        'lodLevelScales': 4294967295,
        'mesh': {'DepotPath': {'$type': 'ResourcePath', '$storage': 'string',
                               '$value': mesh}, 'Flags': 'Soft'},
        'meshAppearance': cname(appearance),
        'occluderAutohideDistanceScale': 255,
        'occluderType': 'Default',
        'proxyScale': None,
        'removeFromRainMap': 0,
        'renderSceneLayerMask': 'Default',
        'sourcePrefabHash': '0',
        'tag': 'None',
        'tagExt': 'None',
        'version': 2,
        'windImpulseEnabled': 0,
    }


# --------------------------------------------------------- collision
#
# Boxes in the room frame: (name, centre u, centre v, centre z, half u,
# half v, half z). A wall's box sits on its line, 0.3 m thick; the floor
# slab 0.3 m under the surface, the ceiling 0.3 m above it.
#
# THE BIG PROPS get a box each, so V and the Claws walk round them rather
# than through them: a static mesh node brings no collision of its own
# (the game's sectors carry theirs in the collision node). (u, v, half
# along, half across, height, yaw): a prop's bounding box, turned to its
# yaw; gen_navmesh keeps the walkable floor off the same footprints.
BIG_PROPS = [
    ('couch_long', -12.9, 8.0, 1.58, 0.63, 1.05, 90.0),
    ('couch_short', -12.9, 11.5, 0.77, 0.64, 1.04, 90.0),
    ('couch_front', -10.0, 0.75, 1.57, 0.63, 1.03, 0.0),
    ('couch_diner', -7.0, 3.5, 1.0, 0.55, 1.1, 270.0),
    ('chair', -10.5, 10.0, 0.21, 0.28, 0.93, 270.0),
    ('shelf_a', -8.0, 17.6, 0.29, 0.95, 2.06, 90.0),
    ('shelf_f', -11.5, 17.6, 0.34, 1.05, 1.09, 90.0),
    ('shelf_c', -4.0, 17.6, 0.33, 0.63, 2.05, 90.0),
    ('rig', 3.5, 16.7, 1.03, 1.12, 0.26, 180.0),
    ('cart', 1.8, 16.6, 0.52, 0.17, 1.31, 160.0),
]


def prop_footprint(u, v, hx, hy, yaw):
    """The four corners, in the room frame, of a prop's box turned to its
    yaw (its mesh +x along the yaw's right, +y along the yaw)."""
    t = math.radians(yaw)
    # yaw 0 faces +v: mesh +y -> +v, mesh +x -> -u... a yaw of 90 faces +u.
    fy = (math.sin(t), math.cos(t))       # +y of the mesh, in (u, v)
    fx = (math.cos(t), -math.sin(t))      # +x of the mesh, in (u, v)
    out = []
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        out.append((u + fx[0] * hx * sx + fy[0] * hy * sy,
                    v + fx[1] * hx * sx + fy[1] * hy * sy))
    return out


def boxes():
    """(name, cu, cv, cz, hu, hv, hz, yaw) in the room frame."""
    h = ROOM_HEIGHT
    cu, cv = (U0 + U1) / 2, (V0 + V1) / 2
    hu, hv = (U1 - U0) / 2, (V1 - V0) / 2
    out = [
        ('floor', cu, cv, -0.15, hu + 0.3, hv + 0.3, 0.15, 0.0),
        ('ceiling', cu, cv, h + 0.15, hu + 0.3, hv + 0.3, 0.15, 0.0),
    ]
    for a, b, inside, label in wall_runs():
        mu, mv = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        if abs(a[1] - b[1]) < 1e-6:         # runs along u
            out.append((label, mu, mv, h / 2, abs(b[0] - a[0]) / 2 + 0.15, 0.15, h / 2 + 0.3, 0.0))
        else:                               # runs along v
            out.append((label, mu, mv, h / 2, 0.15, abs(b[1] - a[1]) / 2 + 0.15, h / 2 + 0.3, 0.0))
    for a, b, _inside in lintels():
        mu, mv = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        hz = (h - LINTEL_Z) / 2
        out.append(('lintel', mu, mv, LINTEL_Z + hz, abs(b[0] - a[0]) / 2, 0.15, hz, 0.0))
    for name, u, v, hx, hy, hz, yaw in BIG_PROPS:
        out.append((name, u, v, hz / 2, hx, hy, hz / 2, yaw))
    return out


FIXED_BITS = 131072.0
# The one rotation every shipped box shape carries.
SHAPE_ROT = {'$type': 'Quaternion', 'i': 4.32978163e-17, 'j': 0.707106829,
             'k': 0.707106829, 'r': 4.32978096e-17}
# A preset and a material read off vanilla wall collision
# (interior_-10_-1_-1_2, NormalCollisionNode_020).
PRESET = {'$type': 'CName', '$storage': 'uint64', '$value': '11199900243055890879'}
MATERIAL = {'$type': 'CName', '$storage': 'uint64', '$value': '6158994176895877186'}


def fixed(v):
    return {'$type': 'FixedPoint', 'Bits': int(round(v * FIXED_BITS))}


def collision_node():
    actors = []
    lo = [1e9, 1e9, 1e9]
    hi = [-1e9, -1e9, -1e9]
    for _name, cx, cy, cz, hx, hy, hz, yaw in boxes():
        wx, wy, wz = room_to_world(cx, cy, cz)
        # The actor carries the room's yaw plus the prop's own; the box is
        # axis-aligned inside it.
        actors.append({
            'Position': {'$type': 'WorldPosition', 'x': fixed(wx), 'y': fixed(wy),
                         'z': fixed(wz)},
            'Orientation': quat_yaw(room_yaw(yaw) + 180.0) if yaw else quat_yaw(R),
            'Shapes': [{
                'ShapeType': 'Box',
                # Half extents, in the shape's own frame: (x, z, y) of ours.
                'Size': vec3((hx, hz, hy)),
                'Position': vec3((0.0, 0.0, 0.0)),
                'Rotation': SHAPE_ROT,
                'Preset': PRESET,
                'ProxyType': 'CharacterObstacle',
                'Materials': [MATERIAL],
                'Uk1': 0, 'Uk2': 0, 'Uk3': 0,
            }],
            'Scale': vec3((1, 1, 1)),
            'Uk1': 0, 'Uk2': '0',
        })
        r = math.hypot(hx, hy)
        for i, (c, e) in enumerate(((wx, r), (wy, r), (wz, hz))):
            lo[i] = min(lo[i], c - e)
            hi[i] = max(hi[i], c + e)
    centre = tuple((lo[i] + hi[i]) / 2 for i in range(3))
    extents = tuple((hi[i] - lo[i]) / 2 for i in range(3))
    n = len(actors)
    node = {
        '$type': 'worldCollisionNode',
        'compiledData': {
            'BufferId': '1', 'Flags': 4063232,
            'Type': ('WolvenKit.RED4.Archive.Buffer.CollisionBuffer, '
                     'WolvenKit.RED4, Version=8.20.0.0, Culture=neutral, '
                     'PublicKeyToken=null'),
            'Data': {'Actors': actors},
        },
        'debugName': cname('cc_g04_room_collision'),
        'extents': vec4(extents),
        'isHostOnly': 0,
        'isVisibleInGame': 1,
        'lod': 1,
        'numActors': n,
        'numMaterialIndices': n,
        'numMaterials': 1,
        'numPresets': 1,
        'numScales': 0,
        'numShapeIndices': n,
        'numShapeInfos': n,
        'numShapePositions': n,
        'numShapeRotations': 1,
        'proxyScale': None,
        'resourceVersion': 2,
        'sectorHash': '0',
        'sourcePrefabHash': '0',
        # The shape of a vanilla architecture ("Normal") collision node with
        # N box shapes, read off 18 of them: [N, 0..] [0..] [N, 0..] [0..] [0..].
        'staticCollisionShapeCategories': {
            '$type': 'worldStaticCollisionShapeCategories_CollisionNode',
            'arr': {'Elements': [
                {'Elements': [n, 0, 0, 0, 0, 0]},
                {'Elements': [0, 0, 0, 0, 0, 0]},
                {'Elements': [n, 0, 0, 0, 0, 0]},
                {'Elements': [0, 0, 0, 0, 0, 0]},
                {'Elements': [0, 0, 0, 0, 0, 0]},
            ]}},
        'tag': 'None',
        'tagExt': 'None',
    }
    return node, centre


# ----------------------------------------------------------- the lights
def light_node():
    with open(LIGHT_SOURCE, encoding='utf-8') as fh:
        doc = json.load(fh)
    n = json.loads(json.dumps(doc['data']))
    n['debugName'] = cname('cc_g04_room_lamp')
    n['sourcePrefabHash'] = '0'
    return n, doc['instanceRecord']


def lights():
    z = ROOM_HEIGHT - 0.4
    return [(0.0, 2.5, z), (-10.0, 2.5, z), (-10.0, 9.5, z), (-4.0, 9.5, z),
            (-10.0, 15.0, z), (-4.0, 15.0, z), (3.5, 15.5, z)]


# -------------------------------------------------------------- the doors
def door_node():
    """The lifted double door, whole, renamed and re-placed."""
    with open(DOOR_SOURCE, encoding='utf-8') as fh:
        doc = json.load(fh)
    n = json.loads(json.dumps(doc['data']))
    n['debugName'] = cname('cc_g04_room_door')
    # THE LIFTED DOOR IS A QUEST DOOR AND SHIPS SEALED. Its DoorSetup says
    # `initialDoorState: SEALED`, which is what its own quest unseals, and
    # the flags beside it (`isSealed 0`, `isLocked 0`, `deviceState ON`)
    # are not the state: gotcha 37, the setup decides at first attach.
    # Playtest 2026-10-01: the door stood shut with no prompt. The game's own
    # kitsch double doors that open on a prompt carry INTERACTIVE and CLOSED
    # (exterior_-19_24_0_0 node 1170), so that is what this one gets.
    for chunk in n['instanceData']['Data']['buffer']['Data']['Chunks']:
        if chunk.get('$type') == 'DoorController':
            setup = chunk['persistentState']['Data']['doorProperties']
            setup['initialDoorState'] = 'CLOSED'
            setup['doorType'] = 'INTERACTIVE'
    n['instanceData']['Data']['buffer']['Data']['Chunks'] += shrunk_occluders(DOOR_OCCLUDERS)
    return n, doc['instanceRecord']


# A DOOR'S OWN OCCLUSION PLANES, SHRUNK TO NOTHING. Every door look carries
# two occluders: a box the door script switches off while the door is open,
# and a solid plane the size of the opening (`door_sliding_j_frame_occluder`,
# four vertices, read 2026-10-01) that nothing ever switches off. A room
# built of 3 m pieces behind an open door is culled piece by piece from a
# few metres back, because each piece hides whole behind that plane
# (playtest 2026-10-01: the city through the cell's door from the hall, the
# hall gone from inside the cell). An instance may override a component
# of its look through `instanceData`, the way a shipped door overrides its
# lights (exterior_-20_-16_0_0 node 976); the override is the whole
# component as the look defines it, with the scale a thousandth. WolvenKit
# round-trips it; whether the game honours an override of a look's
# component is UNPLAYED.
DOOR_OCCLUDERS = (os.path.join(HERE, 'door_occluders.json'), 'kitsch_g')
CELL_DOOR_OCCLUDERS = (os.path.join(HERE, 'door_occluders.json'), 'entropy_c_baremetal')


def shrunk_occluders(which):
    path, look = which
    with open(path, encoding='utf-8') as fh:
        comps = json.load(fh)[look]
    out = []
    for c in comps:
        c = json.loads(json.dumps(c))
        c['scale'] = vec3((0.001, 0.001, 0.001))
        out.append(c)
    return out


def cell_door_node():
    """The lifted single door (lift_door.py): a sliding door whose frame
    spans 1.66 m to the LEFT of its origin (mesh x -1.58..0.08, read off
    door_frame_single_a and door_sliding_c), so the origin goes at the
    right-hand edge of the gap and the mesh +x along +u."""
    with open(CELL_DOOR_SOURCE, encoding='utf-8') as fh:
        doc = json.load(fh)
    n = json.loads(json.dumps(doc['data']))
    n['debugName'] = cname('cc_g04_cell_door')
    for chunk in n['instanceData']['Data']['buffer']['Data']['Chunks']:
        if chunk.get('$type') == 'DoorController':
            setup = chunk['persistentState']['Data']['doorProperties']
            setup['initialDoorState'] = 'CLOSED'
            setup['doorType'] = 'INTERACTIVE'
    n['instanceData']['Data']['buffer']['Data']['Chunks'] += shrunk_occluders(CELL_DOOR_OCCLUDERS)
    return n, doc['instanceRecord']


def cell_door_place():
    """World position and yaw of the cell door: origin at the gap's right
    edge less the frame's 0.08 m, +x along +u (world yaw of U)."""
    u = CD1 - 0.08
    pos = room_to_world(u, CV0, 0.0)
    yaw = math.degrees(math.atan2(U[1], U[0]))
    return pos, yaw


# -------------------------------------------------------------- the route
# HE SPRINTS THE FIRST 200 M AND WALKS THE REST (the design call,
# 2026-10-13: "slow down after 200m"; the audit: 820 m at a sprint looked
# odd). The patrol order takes one movement type for a whole path, so the
# route is two paths, split where it passes SPRINT_METRES.
SPRINT_METRES = 200.0


def route_points():
    """The whole route in world points: the room's leg, the street's, the
    end."""
    pts = [room_to_world(u, v, 0.0) for u, v in cfg.ROOM_LEAVE_ROUTE]
    pts += [tuple(p) for p in cfg.LEAVE_ROUTE_WORLD]
    pts.append(cfg.LEAVE_END[:3])
    return pts


def route_halves():
    """(the sprint's points, the walk's points), split SPRINT_METRES along
    the route at a point on its line; the split point ends one and starts
    the other."""
    pts = route_points()
    run = 0.0
    for k in range(1, len(pts)):
        a, b = pts[k - 1], pts[k]
        seg = math.dist(a, b)
        if run + seg >= SPRINT_METRES:
            t = (SPRINT_METRES - run) / seg
            mid = tuple(a[i] + (b[i] - a[i]) * t for i in range(3))
            return pts[:k] + [mid], [mid] + pts[k:]
        run += seg
    return pts, pts[-2:]


def room_path(pts):
    """A path given in the room frame as world points: on the floor inside
    (v >= 0), at the pavement's height outside."""
    out = []
    for u, v in pts:
        x, y, z = room_to_world(u, v, 0.0)
        out.append((x, y, cfg.STREET_Z if v < 0 else z))
    return out


def spline_node(name, pts):
    """`worldPatrolSplineNode` through `pts`: a shipped spline's
    shape (exterior_-19_-16_0_0 node 1237, a `worldSplineNode`) plus the
    three lists the patrol kind adds, empty (WolvenKit writes
    `patrolPointDefs`, `patrolPoints` and `spots` for the type; the wiki's
    patrol guide and the shipped gig whose drones patrol both point a
    patrol order at this kind). Points local to the node's position (the
    first point), tangents left to the engine."""
    origin = pts[0]
    points = []
    for i, p in enumerate(pts):
        local = (p[0] - origin[0], p[1] - origin[1], p[2] - origin[2])
        prev = pts[max(i - 1, 0)]
        nxt = pts[min(i + 1, len(pts) - 1)]
        tangent = ((nxt[0] - prev[0]) / 4.0, (nxt[1] - prev[1]) / 4.0, (nxt[2] - prev[2]) / 4.0)
        points.append({
            '$type': 'SplinePoint',
            'automaticTangents': 1,
            'continuousTangents': 1,
            'id': 0,
            'position': vec3(local),
            'rotation': {'$type': 'Quaternion', 'i': 0, 'j': 0, 'k': 0, 'r': 1},
            'tangents': {'Elements': [vec3(tangent), vec3(tangent)]},
        })
    node = {
        '$type': 'worldPatrolSplineNode',
        'debugName': cname(name),
        'destSnapedNode': {'$type': 'NodeRef', '$storage': 'uint64', '$value': '0'},
        'destSnapedSocketName': cname('None'),
        'entrySnapedNode': {'$type': 'NodeRef', '$storage': 'uint64', '$value': '0'},
        'entrySnapedSocketName': cname('None'),
        'isHostOnly': 0,
        'isVisibleInGame': 1,
        'patrolPointDefs': [],
        'patrolPoints': [],
        'proxyScale': None,
        'sourcePrefabHash': '0',
        'splineData': {'HandleId': '0', 'Data': {
            '$type': 'Spline', 'hasDirection': 1, 'looped': 0, 'points': points}},
        'spots': [],
        'tag': 'None',
        'tagExt': 'None',
    }
    return node, origin


# ------------------------------------------------------- the walkable floor
#
# For gen_navmesh.py: the floor an NPC may walk, as simple polygons in the
# room frame, inset AGENT from every wall, each doorway a small polygon of
# its own that shares an edge with the room on either side, and the big
# props bitten out of the room they stand in.
AGENT = 0.3
# The cell's floor stops 0.7 m short of the right wall: past that line, at
# the cell's depth, the floor would fall in a navigation tile that carries
# off-mesh connections (tile -44, 46), which the packer does not move.
CELL_WALK_U1 = 5.3
# THE WAY THROUGH THE STREET DOOR: the lobby's front edge has two points
# this far either side of the door's middle, and gen_navmesh's threshold
# runs from them out to the street's floor. 0.6 m keeps the walker's middle
# inside the door's 2.6 m frame where the threshold crosses the wall line.
DOOR_PASS = 0.6
# No prop stands against the right wall either: a bite there would straddle
# the border between two navigation tiles (x -1425.6, which runs 0.3 to
# 1.3 m inside that wall), and a bitten polygon cut on that line comes
# apart at the bite.


def notch(poly, rect):
    """Bite an axis-aligned rect (u0, v0, u1, v1) out of `poly` where the
    rect crosses one of the polygon's axis-aligned edges; the polygon stays
    simple. A rect that touches no edge leaves the polygon alone (the prop
    stands free, and an NPC may brush it)."""
    u0, v0, u1, v1 = rect
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        if abs(a[1] - b[1]) < 1e-6:                   # edge along u at v = a[1]
            vv = a[1]
            if not (v0 - 1e-6 <= vv <= v1 + 1e-6):
                continue
            lo, hi = min(a[0], b[0]), max(a[0], b[0])
            if u1 <= lo + 1e-6 or u0 >= hi - 1e-6:
                continue
            cu0, cu1 = max(u0, lo), min(u1, hi)
            # which side of the edge is the polygon's inside: the other
            # vertex of the rect in v tells where the bite goes
            inner = v1 if abs(vv - v0) < abs(vv - v1) else v0
            pts = [(cu0, vv), (cu0, inner), (cu1, inner), (cu1, vv)]
            if a[0] > b[0]:
                pts.reverse()
            return poly[:i + 1] + pts + poly[i + 1:]
        if abs(a[0] - b[0]) < 1e-6:                   # edge along v at u = a[0]
            uu = a[0]
            if not (u0 - 1e-6 <= uu <= u1 + 1e-6):
                continue
            lo, hi = min(a[1], b[1]), max(a[1], b[1])
            if v1 <= lo + 1e-6 or v0 >= hi - 1e-6:
                continue
            cv0, cv1 = max(v0, lo), min(v1, hi)
            inner = u1 if abs(uu - u0) < abs(uu - u1) else u0
            pts = [(uu, cv0), (inner, cv0), (inner, cv1), (uu, cv1)]
            if a[1] > b[1]:
                pts.reverse()
            return poly[:i + 1] + pts + poly[i + 1:]
    return poly


def insert_points(poly, pts):
    """Put points that lie on an edge of `poly` into its outline."""
    for p in pts:
        n = len(poly)
        for i in range(n):
            a, b = poly[i], poly[(i + 1) % n]
            if abs(a[0] - b[0]) < 1e-6 and abs(p[0] - a[0]) < 1e-6 and min(a[1], b[1]) + 1e-6 < p[1] < max(a[1], b[1]) - 1e-6:
                poly = poly[:i + 1] + [p] + poly[i + 1:]
                break
            if abs(a[1] - b[1]) < 1e-6 and abs(p[1] - a[1]) < 1e-6 and min(a[0], b[0]) + 1e-6 < p[0] < max(a[0], b[0]) - 1e-6:
                poly = poly[:i + 1] + [p] + poly[i + 1:]
                break
    return poly


def walkable_polygons():
    """[(name, [(u, v), ...])], each simple, in the room frame. The lobby's
    front edge is inset from the front wall like every other edge, with two
    points at the door for gen_navmesh's threshold. The game's own floor
    that reached 3.2 m in through the doorway is switched off there
    (gen_navmesh, "THROUGH THE WALLS")."""
    a = AGENT
    lobby = [(LU0 + a, V0 + a), (LU1 - a, V0 + a), (LU1 - a, LV1 - a), (LU0 + a, LV1 - a)]
    lobby = insert_points(lobby, [(-DOOR_PASS, V0 + a), (DOOR_PASS, V0 + a)])
    gap = [(GAP0 + a, LV1 - a), (GAP1 - a, LV1 - a), (GAP1 - a, LV1 + a), (GAP0 + a, LV1 + a)]
    hall = [(U0 + a, V0 + a), (LU0 - a, V0 + a), (LU0 - a, LV1 + a), (U1 - a, LV1 + a),
            (U1 - a, CV0 - a), (CU0 - a, CV0 - a), (CU0 - a, V1 - a), (U0 + a, V1 - a)]
    cell_gap = [(CD0 + a, CV0 - a), (CD1 - a, CV0 - a), (CD1 - a, CV0 + a), (CD0 + a, CV0 + a)]
    cell = [(CU0 + a, CV0 + a), (CELL_WALK_U1, CV0 + a), (CELL_WALK_U1, V1 - a), (CU0 + a, V1 - a)]
    lobby = insert_points(lobby, [gap[0], gap[1]])
    hall = insert_points(hall, [gap[3], gap[2], cell_gap[0], cell_gap[1]])
    cell = insert_points(cell, [cell_gap[3], cell_gap[2]])
    # the big props, as rects grown by the agent, bitten out of the room
    # they stand in
    rooms = {'lobby': lobby, 'hall': hall, 'cell': cell}
    for name, u, v, hx, hy, hz, yaw in BIG_PROPS:
        if hz < 0.5:                       # a rig is stepped over
            continue
        corners = prop_footprint(u, v, hx + a, hy + a, yaw)
        rect = (min(c[0] for c in corners), min(c[1] for c in corners),
                max(c[0] for c in corners), max(c[1] for c in corners))
        for key in rooms:
            rooms[key] = notch(rooms[key], rect)
    return [('lobby', rooms['lobby']), ('lobby_gap', gap), ('hall', rooms['hall']),
            ('cell_gap', cell_gap), ('cell', rooms['cell'])]


# -------------------------------------------------------------- the file
def renumber(obj, counter):
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k == 'HandleId':
                counter[0] += 1
                out[k] = str(counter[0])
            else:
                out[k] = renumber(v, counter)
        return out
    if isinstance(obj, list):
        return [renumber(v, counter) for v in obj]
    return obj


def rotate(orient, p):
    """A local point through a quaternion, as world offset."""
    i, j, k, r = orient['i'], orient['j'], orient['k'], orient['r']
    x, y, z = p
    # q * v * q^-1
    tx = 2 * (j * z - k * y)
    ty = 2 * (k * x - i * z)
    tz = 2 * (i * y - j * x)
    return (x + r * tx + (j * tz - k * ty),
            y + r * ty + (k * tx - i * tz),
            z + r * tz + (i * ty - j * tx))


def instance(index, pos, orient, ref, max_dist, uk_float, uk10, uk11,
             centre=None, floor_z=None):
    """`centre` is the piece's centre in its own frame; the streaming ref
    point goes there, as the game writes it. None keeps it at the origin,
    which is what an entity or a light carries. `floor_z` is the floor the
    reference point sits under; None is the room's own threshold, and a
    piece placed anywhere else must pass its own (audit 2026-10-01, second
    pass: Bayani's bag in Kabuki got the room's 18.09, 10 m above it)."""
    if centre is not None:
        c = rotate(orient, centre)
        refpt = (pos[0] + c[0], pos[1] + c[1], pos[2] + c[2])
    else:
        refpt = pos
    # THE REFERENCE POINT SITS JUST UNDER THE FLOOR, whatever the piece.
    # Playtest 2026-10-01: with the walls' points at their centres (1.9 m
    # up) the walls drew once V was inside and not from the doorway, while
    # the floor, whose point is 0.1 m under the floor, drew from both. The
    # building's facade carries occlusion that hides points above the
    # threshold from a camera outside it, and a point under the threshold
    # passes. The pieces stream at 98 m, so the two metres do not matter.
    refpt = (refpt[0], refpt[1], (DZ if floor_z is None else floor_z) - 0.1)
    return {
        'Id': '0',
        'NodeIndex': index,
        'Position': vec4(pos),
        'Orientation': orient,
        'Scale': vec3((1, 1, 1)),
        'Pivot': vec3(refpt),
        'Bounds': {'$type': 'Box', 'Max': vec4(refpt), 'Min': vec4(refpt)},
        'QuestPrefabRefHash': ({'$type': 'NodeRef', '$storage': 'string', '$value': ref}
                               if ref else
                               {'$type': 'NodeRef', '$storage': 'uint64', '$value': '0'}),
        'UkHash1': {'$type': 'NodeRef', '$storage': 'uint64', '$value': '0'},
        'CookedPrefabData': {'DepotPath': {'$type': 'ResourcePath',
                                           '$storage': 'uint64', '$value': '0'},
                             'Flags': 'Default'},
        'MaxStreamingDistance': max_dist,
        'UkFloat1': uk_float,
        'Uk10': uk10,
        'Uk11': uk11,
        'Uk12': 0,
        'Uk13': '0',
        'Uk14': '0',
    }


def sector():
    nodes = []
    inst = []

    def add(node, pos, orient, ref=None, flags=(2760.11133, 20.0, 1088, 20610),
            centre=None):
        nodes.append({'HandleId': '0', 'Data': node})
        inst.append(instance(len(nodes) - 1, pos, orient, ref, *flags,
                             centre=centre))

    # The kit pieces, with the game's own wall's numbers: a 1177 m
    # secondary distance, 98.77 m streaming distance, and the flags the
    # game's wall carries (interior_-12_17_0_1 instance 166).
    KIT_FLAGS = (1177.27527, KIT_HIDE_DISTANCE, 1088, 20610)
    for mesh, (x, y, z), yaw in floor_tiles():
        label = os.path.basename(mesh)[:-5]
        add(mesh_node(label, mesh), room_to_world(x, y, z), quat_yaw(yaw),
            None, KIT_FLAGS, KIT_CENTRE[mesh])
    for mesh, pos, yaw in walls():
        label = os.path.basename(mesh)[:-5]
        add(mesh_node(label, mesh), pos, quat_yaw(yaw), None, KIT_FLAGS,
            KIT_CENTRE[mesh])
    for mesh, (x, y, z), q in ceiling_flipped():
        add(mesh_node('ceiling_over', mesh), room_to_world(x, y, z), q, None,
            KIT_FLAGS, KIT_CENTRE[mesh])
    for node, pos, orient, flags in dressing():
        add(node, pos, orient, None,
            (flags['MaxStreamingDistance'], flags['UkFloat1'], flags['Uk10'],
             flags['Uk11']))
    col, centre = collision_node()
    # A vanilla collision instance: float-max streaming distance, Uk10 33792,
    # Uk11 768 (exterior_-23_24_0_0 instance 956).
    add(col, centre, quat_yaw(0.0), None, (3.40282347e+38, 20.0, 33792, 768))
    lamp, lamp_inst = light_node()
    for x, y, z in lights():
        add(json.loads(json.dumps(lamp)), room_to_world(x, y, z), quat_yaw(0.0), None,
            (lamp_inst['MaxStreamingDistance'], lamp_inst['UkFloat1'],
             lamp_inst['Uk10'], lamp_inst['Uk11']))
    door, door_inst = door_node()
    add(door, (DX, DY, DZ), quat_yaw(DYAW), DOOR_REF,
        (door_inst['MaxStreamingDistance'], door_inst['UkFloat1'],
         door_inst['Uk10'], door_inst['Uk11']))
    cdoor, cdoor_inst = cell_door_node()
    cpos, cyaw = cell_door_place()
    add(cdoor, cpos, quat_yaw(cyaw), CELL_DOOR_REF,
        (cdoor_inst['MaxStreamingDistance'], cdoor_inst['UkFloat1'],
         cdoor_inst['Uk10'], cdoor_inst['Uk11']))
    # The route, with the flags of the shipped spline it is shaped on
    # (exterior_-19_-16_0_0 node 1237: 3856 m, 74 m, 2080, 512).
    sprint, walk = route_halves()
    paths = [(LEAVE_PATH_REF, 'cc_g04_leave_path', sprint),
             (LEAVE_PATH2_REF, 'cc_g04_leave_path2', walk),
             (BYE_PATH_REF, 'cc_g04_bye_path', room_path(cfg.ROOM_BYE_PATH))]
    paths += [(ref, ref.rsplit('#', 1)[1], room_path(pts))
              for ref, pts in zip(OA_PATH_REFS, cfg.OA_PATHS)]
    for ref, name, pts in paths:
        spl, origin = spline_node(name, pts)
        add(spl, origin, quat_yaw(0.0), ref, (3856.41016, 74.052475, 2080, 512))

    nodes = renumber(nodes, [0])
    return {
        'Header': cr2w.header(SECTOR + '.streamingsector'),
        'Data': {
            'Version': 195, 'BuildVersion': 0,
            'RootChunk': {
                '$type': 'worldStreamingSector',
                'category': 'Exterior',
                'cookingPlatform': 'PLATFORM_PC',
                'externInplaceResource': {'DepotPath': {'$type': 'ResourcePath',
                                                        '$storage': 'uint64',
                                                        '$value': '0'},
                                          'Flags': 'Soft'},
                'level': 1,
                'localInplaceResource': [],
                'nodeData': {
                    'BufferId': '0',
                    'Flags': 4063232,
                    'Type': ('WolvenKit.RED4.Archive.Buffer.worldNodeDataBuffer, '
                             'WolvenKit.RED4, Version=8.20.0.0, Culture=neutral, '
                             'PublicKeyToken=null'),
                    'Data': inst,
                },
                'nodeRefs': [{'$type': 'NodeRef', '$storage': 'string', '$value': r}
                             for r in [DOOR_REF, CELL_DOOR_REF, LEAVE_PATH_REF,
                                       LEAVE_PATH2_REF, BYE_PATH_REF] + OA_PATH_REFS],
                'nodes': nodes,
                'persistentNodeIndex': 0,
                'persistentNodes': [],
                'variantIndices': [0],
                'variantNodes': [],
                'version': 62,
            },
            'EmbeddedFiles': [],
        },
    }


# The grid, as gig 03's gen_sector.py derives it: a level-1 Exterior cell is
# 128 m, 128 cells per axis.
LEVEL = 1
CELL = 64.0 * (2 ** LEVEL)
AXIS = 2 ** (8 - LEVEL)


def grid_cell(pos):
    half = AXIS // 2
    i, j, k = (int(math.floor(c / CELL)) for c in pos)
    return (i + half) + AXIS * (j + half) + AXIS * AXIS * (k + half)


REACH = 200.0


def block():
    """The sector streams while V is within REACH of the building, and
    along the whole of Bayani's route as well: the route's spline is a
    node of this sector, and a patrol whose path streams out stops."""
    c = room_to_world((U0 + U1) / 2, (V0 + V1) / 2, 1.5)
    pts = [c] + [tuple(p) for p in cfg.LEAVE_ROUTE_WORLD] + [cfg.LEAVE_END[:3]]
    lo = tuple(min(p[i] for p in pts) - REACH for i in range(3))
    hi = tuple(max(p[i] for p in pts) + REACH for i in range(3))
    return {
        'Header': cr2w.header(SECTOR + '.streamingblock'),
        'Data': {
            'Version': 195, 'BuildVersion': 0,
            'RootChunk': {
                '$type': 'worldStreamingBlock',
                'cookingPlatform': 'PLATFORM_PC',
                'descriptors': [{
                    '$type': 'worldStreamingSectorDescriptor',
                    'blockIndex': {'$type': 'worldStreamingBlockIndex',
                                   'oup': 'Base', 'rldGridCell': grid_cell(c)},
                    'category': 'Exterior',
                    'data': {'DepotPath': {'$type': 'ResourcePath',
                                           '$storage': 'string',
                                           '$value': SECTOR_DEPOT},
                             'Flags': 'Soft'},
                    'level': LEVEL,
                    'numNodeRanges': 1,
                    'questPrefabNodeRef': {'$type': 'NodeRef',
                                           '$storage': 'uint64', '$value': '0'},
                    'streamingBox': {'$type': 'Box',
                                     'Max': vec4(hi, w=1),
                                     'Min': vec4(lo, w=1)},
                    'variants': [],
                }],
                'index': {'$type': 'worldStreamingBlockIndex',
                          'oup': 'Base', 'rldGridCell': 0},
            },
            'EmbeddedFiles': [],
        },
    }


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for name, doc in ((SECTOR + '.streamingsector.json', sector()),
                      (SECTOR + '.streamingblock.json', block())):
        path = os.path.join(OUT, name)
        with open(path, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(doc, fh, indent=2)
        print('wrote', path)
    print('%d meshes, 1 collision node of %d boxes, %d lights, doors at %s and %s, the route %s'
          % (len(floor_tiles()) + len(walls()) + len(ceiling_flipped()), len(boxes()),
             len(lights()), DOOR_REF, CELL_DOOR_REF, LEAVE_PATH_REF))
    for name, poly in walkable_polygons():
        print('  walkable %-9s %d points' % (name, len(poly)))
