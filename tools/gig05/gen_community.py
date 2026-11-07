r"""Trauma Team's community, and the buildings the gig adds to the roof.

    python tools\gig05\gen_community.py

Writes, under source\wkit\raw:

  mod\worlds\03_night_city\_compiled\default\cc_g05_cast.streamingsector
  mod\worlds\03_night_city\_compiled\default\cc_g05_cast_reg.streamingsector
  mod\worlds\03_night_city\_compiled\default\cc_g05_cast.streamingblock
  lift.devices.json and lift.psrep.json, the lift's two patches

ONE COMMUNITY, the gig 04 shape (`tools/gig04/gen_community.py`; the recipe
is gotcha 66 through `questkit.community`). The quest phase switches the whole
community off at its top and entries on one at a time (gotcha 69).

THE AV IS A COMMUNITY ENTRY, the way The Rescue places its Trauma Team AV
(`#q001_com_trauma`, entry `av`). A community stands a vehicle on a spot with no
pose, which gig 04's van and Orbital Air's car already do.

THE CREW ARE TWO SETS OF BODIES: the riders, in the cabin and on the pad, and the
roof crew on their posts at a call. A step-off swaps one set for the other in a
fade.

THE FLIGHT PATHS ride in the same sector (`questkit.avflight`), with the game's own
streaming distance for an AV path (`wat_ich_01_spl_av_fly_off`: 4,946 m), so they
are loaded wherever the flight is.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from questkit import community, avflight                             # noqa: E402
import gen_lift                                                       # noqa: E402

import gig05_config as cfg

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'gig04'))
import gen_room                                               # noqa: E402

B = chr(92)


def depot(*parts):
    return B.join(parts)


OUT = os.path.join(cfg.RAW, 'mod', 'worlds', '03_night_city', '_compiled', 'default')

SECTOR = 'cc_g05_cast'
SPAWNSET_NAME = '#cc_g05_cast_com'
PHASE = 'default'
PERIOD = 'Day'

RECRUITER = 'recruiter'
AV = 'av'
LEAD, SOLDIER, MEDIC = 'lead', 'soldier', 'medic'
CREW = (LEAD, SOLDIER, MEDIC)
# THE ROOF CREW: the same three men, a second set of bodies standing on their
# posts at a call, switched on as the AV lands and off as it leaves, while
# the set that rides is switched the other way. Playtest 2026-11-03: the
# crew that had ridden and got out never fired a shot (their targets known,
# their guns in hand, every Scav at full health after two minutes); bodies
# that never sat in the AV carry nothing over from the ride. Their spots at
# the second and third calls are phases of the same entries.
ROOF_CREW = {LEAD: 'lead_r', SOLDIER: 'soldier_r', MEDIC: 'medic_r'}
CLIENT = 'client'
SCAVS = [name for name, _r in cfg.SCAV_RECORDS]
# A CALL'S PHASE: the first call is each entry's own spot, the later ones
# are phases (questkit.community: a phase switch respawns the entry there).
SITE_PHASES = [None, 'site2', 'site3']
AV_PHASES = ['site1', 'site2', 'site3']
# The AV turned for its takeoff at each call (gig05_config.py, _site).
AV_DEP_PHASES = ['site1_dep', 'site2_dep', 'site3_dep']
# THE SKIP SHOWS THE LAST APPROACH_BACK METRES (the design call, 2026-11-03).
APPROACH_BACK = 250.0
AV_PAD_PHASE = 'pad'

# The AV's one appearance: `av_trauma.ent` has only this one, which is
# `zetatech_atlus.app` `trama_team`, the one that keeps the cabin.
AV_LOOK = 'av_zetatech_atlus_basic_01_trama_team'


def ground(name):
    return depot('base', 'workspots', 'common', 'ground', name)


def stand_around(n):
    return ground('generic__stand_ground__stand_around__%02d.workspot' % n)


# THE CLIENT LIES ON HIS BACK, out cold; the medic kneels and looks him over.
# The game's own ground poses (docs/trauma-team-research.md, 5); The Rescue's
# own medic poses are scene animations and need its marker.
LIE = ground('generic__lie_ground_lean_back__unconscious__01.workspot')
KNEEL = ground('generic__kneel_ground__inspect__01.workspot')
# THE SOLDIER ON GUARD AT THE AV: the game's encounter pose of a man standing
# guard, which puts a Copperhead in his hands for as long as he is in it.
RIFLE_GUARD = depot('base', 'workspots', 'encounter', 'generic__stand_rifle_protect__01.workspot')


def _at_sites(key):
    """The first site's spot, and the later sites' as phases."""
    first = cfg.SITES[0][key]
    phases = {SITE_PHASES[i]: [((p[0], p[1], p[2]), p[3])]
              for i, p in ((i, cfg.SITES[i][key]) for i in (1, 2))}
    return first, phases


_LEGS = [cfg.ROUTE_OUT, cfg.ROUTE_12, cfg.ROUTE_23, cfg.ROUTE_BACK]


# ONE LOOK FOR THE RECRUITER (characters.yaml, gen_recruiter.py).
RECRUITER_LOOK = 'cc_g05_recruiter'
# ONE LOOK FOR EACH OF THE CREW, riding or on the ground. Playtest 2026-11-04: on
# `default` each spawn drew a new helmet. Brekke is the game's own team leader.
CREW_LOOK = {LEAD: 'corpo__traumateam_ma__leader__soldier_lvl1',
             SOLDIER: 'corpo__traumateam_ma_soldier__lvl2_01',
             MEDIC: 'corpo__traumateam_ma_paramedic__lvl1_01'}


def entries():
    rx, ry, rz, ryaw = cfg.RECRUITER
    out = [community.Entry(RECRUITER, 'Character.cc_g05_recruiter', RECRUITER_LOOK,
                           (rx, ry, rz), ryaw, stand_around(2))]
    # THE AV HAS A SPOT AT EACH CALL TOO, as phases. Playtest 2026-11-03 (the
    # dev menu's trace): seating V on an AV the spline had flown away from
    # its spot, by the quest's seat node or by the script's mount, first put
    # V at that spot, on the Medical Center, behind two loading screens; and
    # the q115 pose on its slot crashed the game. Re-placed on the spot where
    # it has landed, the AV is where the seat looks for it.
    av_phases = {AV_PHASES[k]: [(s['av'], s['yaw'])] for k, s in enumerate(cfg.SITES)}
    av_phases.update({AV_DEP_PHASES[k]: [(s['av'], s['depart'])] for k, s in enumerate(cfg.SITES)})
    # THE PAD AS A PHASE TOO: switched on with no phase named, the AV came
    # back on the last call it was switched on at (playtest 2026-11-03,
    # the flight home skipped and the pad empty).
    av_phases[AV_PAD_PHASE] = [(cfg.PAD, cfg.PAD_YAW)]
    out.append(community.Entry(AV, 'Vehicle.cc_g05_av', AV_LOOK,
                               cfg.PAD, cfg.PAD_YAW, None, phases=av_phases))
    records = {LEAD: 'Character.cc_g05_lead', SOLDIER: 'Character.cc_g05_soldier',
               MEDIC: 'Character.cc_g05_medic'}
    for i, who in enumerate(CREW):
        px, py, pz, pyaw = cfg.PAD_CREW[who]
        # A STANDING POSE AT THE PAD: it holds the man at the height written
        # (gig05_config.py, PAD_SKIN). The quest's seat node would not take a
        # man in a pose (playtest 2026-11-03), but nothing uses that node for
        # the crew any more: the cabin scene puts them on their places.
        # Brekke on the game's hands-on-hips stand (stand_around__03): arms at his
        # sides read stiff (playtest 2026-11-07). His scenes play that stand's clips.
        out.append(community.Entry(who, records[who], CREW_LOOK[who], (px, py, pz), pyaw,
                                   stand_around(3 if who == LEAD else 1 + i)))
    # THE ROOF MEDIC AND SOLDIER are records of their own: one kneels at the
    # client, the other stands guard at the AV, and both stay out of the
    # fight (characters.yaml, cc_g05_medic_r and cc_g05_soldier_r).
    roof_records = dict(records, **{MEDIC: 'Character.cc_g05_medic_r',
                                    SOLDIER: 'Character.cc_g05_soldier_r'})
    poses = {MEDIC: KNEEL, SOLDIER: RIFLE_GUARD}
    for i, who in enumerate(CREW):
        first, phases = _at_sites(who)
        # NO POSE FOR THE LEAD, WHO FIGHTS: playtest 2026-11-03, he was
        # found parked in a pose 20 m off, not firing.
        spot = poses.get(who)
        out.append(community.Entry(ROOF_CREW[who], roof_records[who], CREW_LOOK[who],
                                   first[:3], first[3], spot, phases=phases))
    first, phases = _at_sites('client')
    out.append(community.Entry(CLIENT, 'Character.cc_g05_client', 'default',
                               first[:3], first[3], LIE, phases=phases))
    for i, (name, record) in enumerate(cfg.SCAV_RECORDS):
        first = cfg.SITES[0]['scavs'][i]
        phases = {SITE_PHASES[k]: [(cfg.SITES[k]['scavs'][i][:3], cfg.SITES[k]['scavs'][i][3])]
                  for k in (1, 2)}
        out.append(community.Entry(name, record, 'default', first[:3], first[3],
                                   stand_around(1 + i % 5), phases=phases))
    return out


def _marker(name, pos, yaw=0.0):
    """A static marker. `yaw` is its facing, which is the way V faces when
    the quest puts V on it (questgraph.add_teleport_player)."""
    ref = community.Community.ref(SECTOR, name)
    return ref, (community.Community.marker_node(None, name), pos, ref,
                 (community.WB['maxdist'], community.WB['ukfloat'],
                  community.WB['uk10'], community.WB['uk11']), yaw)


def _chest(pos):
    """A prompt's marker at chest height. Playtest 2026-11-03: with the
    markers on the floor, V looked at the floor after each prompt taken."""
    return (pos[0], pos[1], pos[2] + 1.3)


# THE ROOF'S FLOOR: one box of collision over the whole top roof, its top on
# the surface the game draws. The shape of gig 04's room (gen_room.py,
# collision_node): a preset and a material off vanilla wall collision.
def _box(name, buffer, x0, y0, x1, y1, z0, z1):
    cx, cy, hx, hy, hz = (x0 + x1) / 2.0, (y0 + y1) / 2.0, (x1 - x0) / 2.0, (y1 - y0) / 2.0, (z1 - z0) / 2.0
    cz = (z0 + z1) / 2.0
    ref = community.Community.ref(SECTOR, name)

    def v3(x, y, z):
        return {'$type': 'Vector3', 'X': x, 'Y': y, 'Z': z}

    node = {
        '$type': 'worldCollisionNode',
        'compiledData': {
            'BufferId': buffer, 'Flags': 4063232,
            'Type': ('WolvenKit.RED4.Archive.Buffer.CollisionBuffer, '
                     'WolvenKit.RED4, Version=8.20.0.0, Culture=neutral, '
                     'PublicKeyToken=null'),
            'Data': {'Actors': [{
                'Position': {'$type': 'WorldPosition', 'x': gen_room.fixed(cx), 'y': gen_room.fixed(cy), 'z': gen_room.fixed(cz)},
                'Orientation': gen_room.quat_yaw(0.0),
                'Shapes': [{
                    'ShapeType': 'Box',
                    'Size': v3(hx, hz, hy),
                    'Position': v3(0.0, 0.0, 0.0),
                    'Rotation': gen_room.SHAPE_ROT,
                    'Preset': gen_room.PRESET,
                    'ProxyType': 'CharacterObstacle',
                    'Materials': [gen_room.MATERIAL],
                    'Uk1': 0, 'Uk2': 0, 'Uk3': 0,
                }],
                'Scale': v3(1, 1, 1),
                'Uk1': 0, 'Uk2': '0',
            }]},
        },
        'debugName': community.cname(name),
        'extents': {'$type': 'Vector4', 'X': hx, 'Y': hy, 'Z': hz, 'W': 0},
        'isHostOnly': 0,
        'isVisibleInGame': 1,
        'lod': 1,
        'numActors': 1,
        'numMaterialIndices': 1,
        'numMaterials': 1,
        'numPresets': 1,
        'numScales': 0,
        'numShapeIndices': 1,
        'numShapeInfos': 1,
        'numShapePositions': 1,
        'numShapeRotations': 1,
        'proxyScale': None,
        'resourceVersion': 2,
        'sectorHash': '0',
        'sourcePrefabHash': '0',
        'staticCollisionShapeCategories': {
            '$type': 'worldStaticCollisionShapeCategories_CollisionNode',
            'arr': {'Elements': [
                {'Elements': [1, 0, 0, 0, 0, 0]},
                {'Elements': [0, 0, 0, 0, 0, 0]},
                {'Elements': [1, 0, 0, 0, 0, 0]},
                {'Elements': [0, 0, 0, 0, 0, 0]},
                {'Elements': [0, 0, 0, 0, 0, 0]},
            ]}},
        'tag': 'None',
        'tagExt': 'None',
    }
    return ref, (node, (cx, cy, cz), ref, (3.40282347e+38, 20.0, 33792, 768), 0.0)


ROOF_FLOOR_REF, ROOF_FLOOR = _box('cc_g05_roof_floor', '1', *cfg.ROOF_BOX, cfg.ROOF_Z - 0.2, cfg.ROOF_Z)
WALK_FLOOR_REF, WALK_FLOOR = _box('cc_g05_walk_floor', '901', cfg.WALK_X[0] - 0.3, cfg.WALK_Y[0], cfg.WALK_X[1],
                                  cfg.WALK_Y[1], cfg.ROOF_Z - 0.2, cfg.ROOF_Z)
WALK_S_REF, WALK_S = _box('cc_g05_walk_south', '902', cfg.WALK_X[0], cfg.WALK_Y[0] - 0.3, cfg.WALK_X[1],
                          cfg.WALK_Y[0], cfg.ROOF_Z, cfg.ROOF_Z + 3.8)
WALK_N_REF, WALK_N = _box('cc_g05_walk_north', '903', cfg.WALK_X[0], cfg.WALK_Y[1], cfg.WALK_DOOR_X,
                          cfg.WALK_Y[1] + 0.3, cfg.ROOF_Z, cfg.ROOF_Z + 3.8)
WALK_E_REF, WALK_E = _box('cc_g05_walk_east', '904', cfg.WALK_X[1], cfg.WALK_Y[0], cfg.WALK_X[1] + 0.3,
                          cfg.WALK_Y[1], cfg.ROOF_Z, cfg.ROOF_Z + 3.8)
WALK_F0_REF, WALK_F0 = _box('cc_g05_walk_door_w', '950', cfg.WALK_DOOR_X, cfg.WALK_Y[1] - 0.1, cfg.ROOF_DOOR_GAP[0],
                            cfg.WALK_Y[1] + 0.1, cfg.ROOF_Z, cfg.ROOF_Z + 3.8)
WALK_F1_REF, WALK_F1 = _box('cc_g05_walk_door_e', '951', cfg.ROOF_DOOR_GAP[1], cfg.WALK_Y[1] - 0.1, cfg.WALK_X[1],
                            cfg.WALK_Y[1] + 0.1, cfg.ROOF_Z, cfg.ROOF_Z + 3.8)
WALK_SILL_REF, WALK_SILL_BOX = _box('cc_g05_walk_sill', '908', cfg.ROOF_DOOR_GAP[0], cfg.WALK_Y[1], cfg.ROOF_DOOR_GAP[1],
                                    cfg.ROOF_SILL_Y, cfg.ROOF_Z - 0.2, cfg.ROOF_Z)
WALK_T_REF, WALK_T = _box('cc_g05_walk_top', '905', cfg.WALK_X[0], cfg.WALK_Y[0], cfg.WALK_X[1], cfg.WALK_Y[1],
                          cfg.ROOF_Z + 3.8, cfg.ROOF_Z + 4.1)
WALK_W0_REF, WALK_W0 = _box('cc_g05_walk_w0', '906', cfg.WALK_X[0] - 0.15, cfg.WALK_Y[0], cfg.WALK_X[0],
                            cfg.ROOM_WAY_IN[0], cfg.ROOF_Z, cfg.ROOF_Z + 3.8)
WALK_W1_REF, WALK_W1 = _box('cc_g05_walk_w1', '907', cfg.WALK_X[0] - 0.15, cfg.ROOM_WAY_IN[1], cfg.WALK_X[0],
                            cfg.WALK_Y[1], cfg.ROOF_Z, cfg.ROOF_Z + 3.8)
TOWER_BOXES = [_box('cc_g05_tower_b%d' % i, str(920 + i), cfg.TOWER_X[i % 2][0], cfg.TOWER_Y[i // 2][0],
                    cfg.TOWER_X[i % 2][1], cfg.TOWER_Y[i // 2][1], cfg.LIFT_LOW, cfg.LIFT_LOW + 6.0)[1]
               for i in range(4)]

# WHERE "BOARD" IS OFFERED, at the AV's open side, and where V is put down
# after getting out. The board prompts are scenes staged at these markers.
PAD_BOARD_REF, PAD_BOARD = _marker('cc_g05_pad_board', _chest(cfg.PAD_BOARD))
LOCKER_REF, LOCKER_MARK = _marker('cc_g05_locker', _chest(cfg.LOCKER))
# The step-off spots face out of the AV's door (its left, yaw + 90): the
# skip stands V there (gen_questphase.py, fly).
PAD_OUT_REF, PAD_OUT = _marker('cc_g05_pad_out', cfg.PAD_OUT,
                               cfg.heading(cfg.PAD_OUT, cfg.PAD_CREW[LEAD]))
# Where V is stood in the boarding fade, facing the door.
PAD_STEP_IN_REF, PAD_STEP_IN = _marker('cc_g05_pad_step_in', cfg.PAD_DOOR, cfg.PAD_YAW - 90.0)
# THE MAP PINS' OWN ANCHORS, zero offset, gig 04's shape (its railing and
# van markers). Career Opportunities' community node was the first anchor
# and ArchiveXL could not resolve it (playtest 2026-11-03: "Can't resolve
# mappin position"): a compiled community area node carries no NodeRef.
RECRUITER_PIN_REF, RECRUITER_PIN = _marker('cc_g05_recruiter_pin', cfg.RECRUITER[:3])
SITE_BOARD = [_marker('cc_g05_%s_board' % s['name'], _chest(s['board'])) for s in cfg.SITES]
SITE_OUT = [_marker('cc_g05_%s_out' % s['name'], s['out'], s['out_yaw']) for s in cfg.SITES]
SITE_STEP_IN = [_marker('cc_g05_%s_step_in' % s['name'], s['step_in'][:3], s['step_in'][3])
                for s in cfg.SITES]
SITE_PIN = [_marker('cc_g05_%s_client_pin' % s['name'], s['client'][:3]) for s in cfg.SITES]
# The first call under its older names.
CLIENT_PIN_REF, CLIENT_PIN = SITE_PIN[0]

# THE GAME'S OWN STREAMING VALUES FOR AN AV PATH, off
# `wat_ich_01_spl_av_fly_off` (MaxStreamingDistance 4946.13672, UkFloat1
# 19266.4688, Uk10 288, Uk11 512).
SPLINE_INST = (4946.13672, 19266.4688, 288, 512)


def _flight(name, pts, speeds):
    ref = community.Community.ref(SECTOR, name)
    node, origin = avflight.speed_spline(name, avflight.fair(pts), speeds, level_pitch=True)
    return ref, (node, origin, ref, SPLINE_INST)


# NO TURN FLOWN HARDER THAN THIS, in m/s2 sideways. Playtest 2026-11-04: the
# flight home, with its 50 m turns at the full 33 m/s (22 m/s2, over 2 g), felt
# much faster and more violent than the others. So every leg's speed comes
# from its own curve.
TURN_ACCEL = 3.0
SPEED_RAMP = 2.0        # m/s2, speeding up or slowing down
TURN_SPAN = 2           # sampled points either side a turn is measured over


def _profile(pts):
    """The AV's speed along a path: [(metres, m/s)] on the sampled curve.
    Off the ground the game's own way, up to the cruise, and slowed for the
    last stretch. Not the vanilla descent's 0.8 m/s over 58 m: playtest
    2026-11-03, that held V aboard, hovering over the deck, for over a
    minute. 2.5 m/s over the last 15 m: at 10 m/s from 220 m out and
    1.5 m/s over the last 25, the columns' descent took 40 s (playtest
    2026-11-03)."""
    curve = avflight.sample(avflight.fair(pts), 8.0)
    at = [0.0]
    for a, b in zip(curve, curve[1:]):
        at.append(at[-1] + math.dist(a, b))
    total = at[-1]
    limits = [(0, 6.0), (15, 16.7), (40, 25.0), (120, cfg.CRUISE_SPEED),
              (total - 160, cfg.CRUISE_SPEED), (total - 100, 12.0),
              (total - 15, 12.0), (total, 2.5)]

    def limit(s):
        for (a, u), (b, v) in zip(limits, limits[1:]):
            if s <= b:
                return u + (v - u) * (s - a) / max(b - a, 1e-6)
        return limits[-1][1]

    v = [limit(s) for s in at]
    n = len(curve)
    for i in range(TURN_SPAN, n - TURN_SPAN):
        a, b, c = curve[i - TURN_SPAN], curve[i], curve[i + TURN_SPAN]
        h1 = math.atan2(b[1] - a[1], b[0] - a[0])
        h2 = math.atan2(c[1] - b[1], c[0] - b[0])
        turn = abs((h2 - h1 + math.pi) % (2 * math.pi) - math.pi)
        run = at[i + TURN_SPAN] - at[i - TURN_SPAN]
        if turn > 1e-3 and run > 1.0:
            v[i] = min(v[i], math.sqrt(TURN_ACCEL * run / turn))
    for i in range(1, n):
        v[i] = min(v[i], math.sqrt(v[i - 1] ** 2 + 2 * SPEED_RAMP * (at[i] - at[i - 1])))
    for i in range(n - 2, -1, -1):
        v[i] = min(v[i], math.sqrt(v[i + 1] ** 2 + 2 * SPEED_RAMP * (at[i + 1] - at[i])))
    return list(zip(at, v))


def _speeds(pts, start=0.0):
    """The profile as the path's speed sections, from `start` metres along
    (the speed changes between each pair of points that differ)."""
    prof = [(s - start, u) for s, u in _profile(pts) if s >= start]
    out, last = [], None
    from_s = prof[0][0]
    for s, u in prof[1:]:
        if last is None or abs(u - last) >= 1.0 or s == prof[-1][0]:
            if s > from_s:
                out.append((from_s, s, u))
            from_s, last = s, u
    return out


FLIGHTS = [_flight('cc_g05_spl_' + n, pts, _speeds(pts)) for n, pts in (
    ('pad_site1', cfg.ROUTE_OUT), ('site1_site2', cfg.ROUTE_12),
    ('site2_site3', cfg.ROUTE_23), ('site3_pad', cfg.ROUTE_BACK))]


def skip_window(i):
    """Seconds into flight `i` (1 to 4) after which the skip is no longer
    offered: when the AV is 80 m short of the stretch a skip flies, at the
    cruise speed plus 3 s for the slower climb."""
    prof = _profile(_LEGS[i - 1])
    stop = prof[-1][0] - APPROACH_BACK - 80.0
    return sum((b[0] - a[0]) / max((a[1] + b[1]) / 2.0, 1.0)
               for a, b in zip(prof, prof[1:]) if b[0] <= stop) + 3.0




# THE LIFT (gen_lift.py). V is put in the car at a stop's marker.
ROOF_DOOR_REF = community.Community.ref(SECTOR, 'cc_g05_lift_door')
# THE SLIDING DOOR'S ORIGIN IS 0.08 m IN FROM THE RIGHT EDGE OF ITS GAP (gen_room.py,
# cell_door_node), its frame spanning 1.58 m along its own -x.
ROOF_DOOR_SPOT = (cfg.ROOF_DOOR_GAP[1] - 0.08, cfg.WALK_Y[1] - 0.1, cfg.ROOF_Z)
WAY_DOOR_REF = community.Community.ref(SECTOR, 'cc_g05_way_door')
WAY_DOOR_SPOT = (cfg.WALK_X[0] - 0.1, cfg.ROOM_WAY_IN[1] - 0.08, cfg.ROOF_Z)
ROOM_DOOR_REF = community.Community.ref(SECTOR, 'cc_g05_room_door')
ROOM_DOOR_SPOT = (cfg.ROOM_X[0] - 0.15, sum(cfg.ROOM_DOOR_GAP) / 2.0, cfg.ROOF_Z)
LIFT_REF, LIFT_NODES, LIFT_STOP_REFS = gen_lift.lift(SECTOR, 'cc_g05_lift', cfg.LIFT_STOPS, _marker, 910,
                                                     doors={1: ROOF_DOOR_REF})


def _door(name, ref, spot, yaw, buffer, locked, single=False):
    """Gig 04's double door, opening as V comes near. The roof door is locked until
    the car arrives: a door is a lift door when a floor terminal is its parent in
    the device graph, and that terminal locks it when the car leaves and unlocks
    it when the car comes back."""
    node, _inst = gen_room.cell_door_node() if single else gen_room.door_node()
    node['debugName'] = community.cname('{%s}' % name)
    node['sourcePrefabHash'] = '0'
    node['instanceData']['Data']['buffer']['BufferId'] = buffer
    for chunk in node['instanceData']['Data']['buffer']['Data']['Chunks']:
        if chunk.get('$type') == 'DoorController':
            state = chunk['persistentState']['Data']
            state['doorProperties']['initialDoorState'] = 'LOCKED' if locked else 'CLOSED'
            state['doorProperties']['doorType'] = 'AUTOMATIC'
            state['isLocked'] = 1 if locked else 0
    return (node, spot, ref, gen_lift.RANGE, yaw)


def _piece(name, mesh, x, y, z, yaw, scale=(1, 1, 1)):
    """A piece of gig 04's interior kit in the open: never hidden by distance,
    since the walkway is seen from the street and from the AV."""
    node = gen_room.mesh_node(name, mesh, hide=0)
    return (node, (x, y, z), community.Community.ref(SECTOR, name),
            (400.0, community.WB['ukfloat'], community.WB['uk10'], community.WB['uk11']), yaw, scale)


# THE PLATES: the game's closed outdoor guardhouse block, stretched. Its top and
# bottom are solid and drawn from outside, where the kit's panels are not. Its long
# sides have window openings, so the walkway's outer walls are the kit's own walls
# turned to face out. Its bounding box at scale 1, read off the mesh.
HUT_MESH = B.join(['base', 'worlds', '03_night_city', 'sectors', '_external', 'proxy',
                   '1659866202', 'arroyo_arasaka_guardhouse_v1.mesh'])
HUT_MIN = (-3.5103, -4.51, -0.21)
HUT_SIZE = (11.0204, 5.4496, 4.5232)


def _wall(name, face, c, a, b, z0, z1):
    """A run of kit wall from `a` to `b` along the wall, its drawn side in the plane
    `c`, facing `face` (n, s, e, w). A wall is drawn on its own +y side, spans 3 m
    along its own -x and is 3.8 m high. Stretched to fit, never overlapped."""
    n = max(1, int(round((b - a) / 3.0)))
    step = (b - a) / n
    scale = (step / 3.0, 1, (z1 - z0) / 3.8)
    out = []
    for i in range(n):
        lo, hi = a + i * step, a + (i + 1) * step
        spot, yaw = {'n': ((hi, c - 0.23), 0.0), 's': ((lo, c + 0.23), 180.0),
                     'w': ((c + 0.23, hi), 90.0), 'e': ((c - 0.23, lo), -90.0)}[face]
        out.append(_piece('%s_%d' % (name, i), gen_room.WALL3, spot[0], spot[1], z0, yaw, scale))
    return out


def _gap_wall(name, face, c, a, b, gap, gap_top, z0, z1):
    """A wall with a doorway in it: either side, and over."""
    return (_wall(name + 'a', face, c, a, gap[0], z0, z1) + _wall(name + 'b', face, c, gap[1], b, z0, z1)
            + _wall(name + 'c', face, c, gap[0], gap[1], gap_top, z1))


with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'room_props.json'), encoding='utf-8') as fh:
    ROOM_PROPS = json.load(fh)


def _prop(name, mesh, x, y, yaw, appearance='default', z=0.0):
    node = gen_room.mesh_node(name, mesh, appearance=appearance, hide=0)
    return (node, (x, y, cfg.ROOF_Z + z), community.Community.ref(SECTOR, name),
            (400.0, community.WB['ukfloat'], community.WB['uk10'], community.WB['uk11']), yaw)


ENV = B.join(['base', 'environment'])
BENCH = B.join([ENV, 'decoration', 'furniture', 'outdoor', 'outdoor_bench', 'outdoor_bench_b.mesh'])
CART = B.join([ENV, 'decoration', 'furniture', 'lab', 'medical_cart', 'medical_cart_c.mesh'])
LAB = B.join([ENV, 'decoration', 'furniture', 'lab', 'lab_locker_set_a'])
RACKS = B.join([ENV, 'architecture', 'megabuilding', 'megabuilding_interior', 'shops', 'wilsons_guns'])
LOCKER_MESH = B.join([ENV, 'decoration', 'furniture', 'industrial', 'industrial_locker_02', 'industrial_locker_02_b_middle.mesh'])


def _room_fill():
    """What a staff room has in it. Every height is above the floor. A rack's three
    shelves are at 0.75, 1.25 and 1.78 m, 0.33 m out from the wall, along 2.2 m of
    its 3 m. The lab counters are 1.1 m high."""
    x0, x1 = cfg.ROOM_X
    y0, y1 = cfg.ROOM_Y
    out = []
    n = [0]

    def put(mesh, x, y, z=0.0, yaw=0.0, look='default'):
        n[0] += 1
        out.append(_prop('cc_g05_fill_%d' % n[0], ROOM_PROPS[mesh], x, y, yaw, look, z))

    # THE RAIL ON THE EAST WALL, south of the door: scrubs and a crew's own clothes.
    rail = x1 - 0.45
    out.append(_plate('cc_g05_room_rail', rail - 0.02, rail + 0.02, y0 + 0.5, cfg.ROOM_WAY_IN[0] - 0.3, 2.04 + cfg.ROOF_Z, 2.08 + cfg.ROOF_Z))
    hang = [('hanging_lab_suit_a', 0.0), ('hanging_lab_suit_b', 0.0), ('hanging_lab_suit_c', 0.0), ('hanging_lab_suit_a', 0.0),
            ('clothes_hanging_male_a', 90.0), ('clothes_hanging_male_b', 90.0), ('clothes_hanging_male_c', 90.0)]
    for i, (mesh, yaw) in enumerate(hang):
        put(mesh, rail, y0 + 0.75 + i * 0.42, 2.03, yaw)
    # THE FIRST RACK: helmets, the team's shirts, trauma packs.
    ox = x1 - 0.8
    sy = y0 + 0.33
    for i in range(4):
        put('militech_helmet_tactical_a', ox - 0.75 - i * 0.48, sy, 1.78 - 1.57, 180.0)
    for i in range(4):
        for j in range(2):
            put('trauma_team_folded_shirt', ox - 0.75 - i * 0.48, sy, 1.29 + j * 0.07)
    for i in range(3):
        put('trauma_pack_deco', ox - 0.85 - i * 0.65, sy, 0.85)
    # THE SECOND RACK: weapon cases and ammunition.
    ox = x1 - 3.9
    put('lootable_weapon_case_medium_neomilitary_a', ox - 1.45, sy, 1.78, 0.0, 'militech')
    put('lootable_weapon_case_medium_neomilitary_a', ox - 1.45, sy, 1.95, 3.0, 'militech')
    for i in range(5):
        put('box_ammo', ox - 0.8 - i * 0.38, sy, 1.25)
        if i % 2 == 0:
            put('box_ammo', ox - 0.8 - i * 0.38, sy, 1.40)
    put('lootable_weapon_case_small_neomilitary_a', ox - 0.9, sy, 0.75, 0.0, 'militech')
    put('lootable_weapon_case_small_neomilitary_a', ox - 1.6, sy, 0.75, 0.0, 'militech')
    put('lootable_ammo_case_small_neomilitary_a', ox - 2.2, sy, 0.75, 90.0, 'neomilitary')
    # THE THIRD RACK, on the west wall: towels and folded clothes.
    ry = 1767.0
    rx = x0 + 0.33
    for i, mesh in enumerate(('towel_b_folded_pile', 'towel_c_folded_pile', 'towel_b_folded_pile', 'towel_c_folded_pile')):
        put(mesh, rx, ry + 0.75 + i * 0.5, 1.78)
    for i, mesh in enumerate(('clothes_folded_jacket_b', 'clothes_folded_tshirt', 'clothes_folded_jacket_b', 'clothes_folded_tshirt')):
        put(mesh, rx, ry + 0.75 + i * 0.5, 1.25)
        put(mesh, rx, ry + 0.75 + i * 0.5, 1.33, 8.0)
    for i in range(3):
        put('duffle_bag_sport_a', rx, ry + 0.85 + i * 0.65, 0.75, 90.0)
    # THE COUNTERS: the open gun case, the trauma kit, the defibrillator.
    for mesh in ('sh_0480__gearup_weapon_case', 'sh_0480__gearup_weapon_case_m_base1', 'sh_0480__gearup_weapon_case_m_capacitor',
                 'sh_0480__gearup_weapon_case_m_decals', 'sh_0480__gearup_weapon_case_m_ironsight',
                 'sh_0480__gearup_weapon_case_m_mag', 'sh_0480__gearup_weapon_case_m_rcv1'):
        put(mesh, x0 + 3.5, y0 + 0.42, 1.1, 90.0)
    put('trauma_pack_deco', x0 + 1.0, y0 + 0.35, 1.2)
    put('sh_0330__traumateam_defibrillator', x0 + 1.7, y0 + 0.35, 1.22, 180.0)
    put('lootable_ammo_case_small_neomilitary_a', x0 + 0.33, 1761.0, 1.1, 0.0, 'neomilitary')
    put('towel_c_folded_pile', x0 + 0.35, 1761.7, 1.1)
    # THE BENCH AND THE FLOOR: bags down, a helmet left out, the laundry.
    put('duffle_bag_sport_a', -1315.8, 1765.9, 0.46, 90.0, 'cyan')
    put('militech_helmet_tactical_a', -1314.8, 1765.9, 0.46 - 1.57, 30.0)
    put('clothes_folded_jacket_b', -1314.5, 1765.75, 0.46, 20.0)
    put('duffle_bag_sport_a', -1316.9, 1764.9, 0.0, 20.0)
    put('laundry_basket_a_full_a', -1313.6, 1767.2, 0.0, 15.0)
    put('entropy_laundry_trolley_b', x0 + 2.6, y1 - 1.6, 0.0, 90.0)
    put('entropy_laundry_trolley_b_laundry_a', x0 + 2.6, y1 - 1.6, 0.45, 90.0, 'white')
    put('clothes_pile_b', -1311.2, 1769.9, 0.0, 40.0)
    put('towel_b_folded_pile', -1316.0, 1770.3, 0.0)
    out.append(_prop('cc_g05_room_cart', CART, x0 + 0.6, 1766.4, 0.0))
    return out


def _room():
    """The locker room: gig 04's kit twice over, one skin facing in and one facing
    out, since a wall is drawn from one side only. The ceiling and floor run under
    and over the walls so no line of sky shows at the joins."""
    x0, x1 = cfg.ROOM_X
    y0, y1 = cfg.ROOM_Y
    z = cfg.ROOF_Z
    top = z + 3.8
    out = []
    # FLOOR AND CEILING, 12 m square stretched a little past the walls.
    spanx, spany = (x1 - x0 + 0.3) / 4.0, (y1 - y0 + 0.3) / 4.0
    for i in range(4):
        for j in range(4):
            px, py = x1 + 0.15 - i * spanx, y1 + 0.15 - j * spany
            scale = (spanx / 3.0, spany / 3.0, 1)
            out.append(_piece('cc_g05_room_f%d%d' % (i, j), gen_room.FLOOR, px, py, z, 0.0, scale))
            out.append(_piece('cc_g05_room_c%d%d' % (i, j), gen_room.CEILING, px, py, top, 0.0, scale))
    # THE WALLS INSIDE, each running 0.1 m past the corners: butted, they left a
    # slit of daylight.
    out += _wall('cc_g05_room_in_n', 's', y1, x0 - 0.1, x1 + 0.1, z, top)
    out += _wall('cc_g05_room_in_s', 'n', y0, x0 - 0.1, x1 + 0.1, z, top)
    out += _gap_wall('cc_g05_room_in_w', 'e', x0, y0 - 0.1, y1 + 0.1, cfg.ROOM_DOOR_GAP, z + 2.3, z, top)
    out += _gap_wall('cc_g05_room_in_e', 'w', x1, y0 - 0.1, y1 + 0.1, cfg.ROOM_WAY_IN, z + 2.3, z, top)
    # THE WALLS OUTSIDE, down past the floor and up past the roof plate.
    lo, hi = z - 0.35, top + 0.35
    ox0, ox1, oy0, oy1 = x0 - 0.3, x1 + 0.3, y0 - 0.3, y1 + 0.3
    out += _wall('cc_g05_room_out_n', 'n', oy1, ox0, ox1, lo, hi)
    out += _wall('cc_g05_room_out_s', 's', oy0, ox0, ox1, lo, hi)
    out += _gap_wall('cc_g05_room_out_w', 'w', ox0, oy0, oy1, cfg.ROOM_DOOR_GAP, z + 2.3, lo, hi)
    out += _wall('cc_g05_room_out_e0', 'e', ox1, oy0, cfg.WALK_Y[0] - 0.46, lo, hi)
    out += _wall('cc_g05_room_out_e1', 'e', ox1, cfg.WALK_Y[1] + 0.46, oy1, lo, hi)
    # THE INSIDES OF THE DOOR TO THE ROOF, closing the hollow between the skins.
    out += _wall('cc_g05_room_rev_s', 'n', cfg.ROOM_DOOR_GAP[0], ox0, x0, z, z + 2.3)
    out += _wall('cc_g05_room_rev_n', 's', cfg.ROOM_DOOR_GAP[1], ox0, x0, z, z + 2.3)
    out.append(_plate('cc_g05_room_top', ox0, ox1, oy0, oy1, top + 0.2, top + 0.35))
    # FLOOR PIECES OVER THE CEILING, hidden under the plate, to throw a shadow.
    for i in range(4):
        for j in range(4):
            out.append(_piece('cc_g05_room_sh%d%d' % (i, j), gen_room.FLOOR, x1 + 0.15 - i * spanx, y1 + 0.15 - j * spany,
                              top + 0.12, 0.0, (spanx / 3.0, spany / 3.0, 1)))
    # THE LAMPS, white: a clinic's.
    lamp, inst = gen_room.light_node()
    for i, (lx, ly) in enumerate(((x0 + 3.0, y0 + 3.0), (x1 - 3.0, y0 + 3.0), (x0 + 3.0, y1 - 3.0), (x1 - 3.0, y1 - 3.0))):
        node = json.loads(json.dumps(lamp))
        node['debugName'] = community.cname('cc_g05_room_lamp_%d' % i)
        node['color'].update({'Red': 255, 'Green': 244, 'Blue': 232})
        node['intensity'] = 1500
        node['radius'] = 14
        out.append((node, (lx, ly, top - 0.4), community.Community.ref(SECTOR, 'cc_g05_room_lamp_%d' % i),
                    (inst['MaxStreamingDistance'], inst['UkFloat1'], inst['Uk10'], inst['Uk11']), 0.0))
    # THE FURNITURE, the game's own.
    out.append(_prop('cc_g05_room_rack0', B.join([RACKS, 'wilsons_shop_weapon_rack_b.mesh']), x1 - 0.8, y0, 0.0))
    out.append(_prop('cc_g05_room_rack1', B.join([RACKS, 'wilsons_shop_weapon_rack_b.mesh']), x1 - 3.9, y0, 0.0))
    out.append(_prop('cc_g05_room_rack2', B.join([RACKS, 'wilsons_shop_weapon_rack_b.mesh']), x0, 1767.0, -90.0))
    out.append(_prop('cc_g05_room_lab0', B.join([LAB, 'lab_set_a_locker_a.mesh']), x0 + 0.4, y0, 0.0, 'military'))
    out.append(_prop('cc_g05_room_lab1', B.join([LAB, 'lab_set_a_locker_b.mesh']), x0 + 2.5, y0, 0.0, 'military'))
    out.append(_prop('cc_g05_room_lab2', B.join([LAB, 'lab_set_a_locker_a.mesh']), x0, 1762.3, -90.0, 'military'))
    out.append(_prop('cc_g05_room_bench', BENCH, -1315.2, 1765.9, 0.0))
    out += _room_fill()
    # THE LOCKER WALL, the length of the north wall.
    for i in range(24):
        out.append(_prop('cc_g05_room_gun%d' % i, LOCKER_MESH, x0 + 0.5 + i * 0.46, y1 - 0.32, 180.0))
    # THE LANDING PAD, a surface of the gig's own under the AV and the crew, just
    # under the roof the game draws. Playtest 2026-11-04: after the flight home that roof
    # was lower than the slab, and the crew stood in the air. Measured
    # afterwards they stood at the same height as before the shift.
    px, py = cfg.PAD[0], cfg.PAD[1]
    out.append(_plate('cc_g05_pad_top', px - 17.0, px + 17.0, py - 15.0, py + 15.0, z - 0.15, z - 0.03))
    # WHAT V CANNOT WALK THROUGH.
    side = 0.3
    boxes = [('n', x0, y1, x1, y1 + side), ('s', x0, y0 - side, x1, y0),
             ('w0', x0 - side, y0, x0, cfg.ROOM_DOOR_GAP[0]), ('w1', x0 - side, cfg.ROOM_DOOR_GAP[1], x0, y1),
             ('e0', x1, y0, x1 + side, cfg.ROOM_WAY_IN[0]), ('e1', x1, cfg.ROOM_WAY_IN[1], x1 + side, y1),
             ('bench', -1316.3, 1765.5, -1314.1, 1766.3),
             ('racks', x1 - 6.9, y0, x1 - 0.8, y0 + 0.75), ('labs', x0 + 0.4, y0, x0 + 4.5, y0 + 0.85),
             ('rack2', x0, 1767.0, x0 + 0.75, 1770.0), ('lab2', x0, 1760.3, x0 + 0.75, 1762.3),
             ('rail', x1 - 0.8, y0, x1, cfg.ROOM_WAY_IN[0] - 0.2),
             ('trolley', x0 + 1.85, y1 - 2.05, x0 + 3.35, y1 - 1.15), ('cart', x0, 1765.95, x0 + 1.1, 1766.9),
             ('guns', x0, y1 - 0.62, x1, y1)]
    for i, (n, a, b, c, d) in enumerate(boxes):
        high = 0.5 if n == 'bench' else 1.2 if n in ('labs', 'lab2') else 3.8
        out.append(_box('cc_g05_room_%s' % n, str(970 + i), a, b, c, d, z, z + high)[1])
    return out


def _plate(name, x0, x1, y0, y1, z0, z1):
    """The block stretched to fill this box."""
    scale = ((x1 - x0) / HUT_SIZE[0], (y1 - y0) / HUT_SIZE[1], (z1 - z0) / HUT_SIZE[2])
    pos = (x0 - HUT_MIN[0] * scale[0], y0 - HUT_MIN[1] * scale[1], z0 - HUT_MIN[2] * scale[2])
    node = gen_room.mesh_node(name, HUT_MESH, appearance='default', hide=0)
    return (node, pos, community.Community.ref(SECTOR, name),
            (600.0, community.WB['ukfloat'], community.WB['uk10'], community.WB['uk11']), 0.0, scale)


def _outer_walls(x0, x1, y0, y1, z, top, door):
    """The kit's walls turned to face out. A wall is drawn on its own +y side, so
    the south row is turned 180 and the north row is not. The lintel over the car's
    door closes the slot between the ceiling and the top of the car, and it is kept
    on the walkway's side of the car's path."""
    out = []
    high = (top + 0.35 - (z - 0.35)) / 3.8
    east, west = x1 + 0.46, x0 - 0.15
    n = int(round((east - west) / 3.0))
    step = (east - west) / n
    for i in range(n):
        out.append(_piece('cc_g05_walk_os%d' % i, gen_room.WALL3, west + i * step, y0 - 0.46 + 0.23, z - 0.35,
                          180.0, (step / 3.0, 1, high)))
    n = int(round((door - west) / 3.0))
    step = (door - west) / n
    for i in range(n):
        out.append(_piece('cc_g05_walk_on%d' % i, gen_room.WALL3, door - i * step, y1 + 0.46 - 0.23, z - 0.35,
                          0.0, (step / 3.0, 1, high)))
    out.append(_piece('cc_g05_walk_oe', gen_room.WALL3, east - 0.23, y0 - 0.46, z - 0.35, -90.0,
                      ((y1 + 0.2 - (y0 - 0.46)) / 3.0, 1, high)))
    for i in (0, 1):
        # DOWN TO THE TOP OF THE ROOF DOOR, which is 2.3 m high.
        out.append(_piece('cc_g05_walk_lintel%d' % i, gen_room.WALL3, door + i * 3.0, y1 + 0.19, z + 2.3, 180.0,
                          (1, 1, 1.5 / 3.8)))
        out.append(_piece('cc_g05_walk_lintel_car%d' % i, gen_room.WALL3, door + (i + 1) * 3.0, y1 - 0.07, z + 2.3,
                          0.0, (1, 1, 1.5 / 3.8)))
    # THE WALL EITHER SIDE OF THE ROOF DOOR, one row facing the walkway and one
    # facing the car, since a wall is drawn from one side only.
    gap0, gap1 = cfg.ROOF_DOOR_GAP
    for i, (a, b) in enumerate(((door, gap0), (gap1, x1 + 0.25))):
        wide = ((b - a) / 3.0, 1, 3.0 / 3.8)
        out.append(_piece('cc_g05_walk_fill%d' % i, gen_room.WALL3, a, y1 + 0.19, z, 180.0, wide))
        out.append(_piece('cc_g05_walk_fill_car%d' % i, gen_room.WALL3, b, y1 - 0.07, z, 0.0, wide))
    return out


def _walkway():
    """A floor or ceiling piece spans 3 m along its own -x and -y from its origin.
    A wall spans 3 m along its own -x, 0.23 m thick along +y. So a floor stands at
    the north-east corner of its square, the south wall at its east end, and the
    north wall, turned, at its west end. Round all of it, the plates."""
    out = []
    x0, x1 = cfg.WALK_X
    y0, y1 = cfg.WALK_Y
    z = cfg.ROOF_Z
    top = z + 3.8
    x, i = x1, 0
    while x > x0:
        out.append(_piece('cc_g05_walk_f%d' % i, gen_room.FLOOR, x, y1, z, 0.0))
        # THE CEILING RUNS OVER THE TOPS OF THE WALLS. Edge to edge, a line of sky
        # showed along the wall's top.
        if i == 0:
            out.append(_piece('cc_g05_walk_c0', gen_room.CEILING, x + 0.25, y1 + 0.15, top, 0.0,
                              (3.25 / 3.0, 3.3 / 3.0, 1)))
        else:
            out.append(_piece('cc_g05_walk_c%d' % i, gen_room.CEILING, x, y1 + 0.15, top, 0.0, (1, 3.3 / 3.0, 1)))
        # THE LAST WALLS OVERLAP AT THE EAST CORNER. Butted end to end they left a
        # slit of daylight.
        if i == 0:
            out.append(_piece('cc_g05_walk_s0', gen_room.WALL3, x + 0.25, y0 - 0.23, z, 0.0, (3.25 / 3.0, 1, 1)))
        else:
            out.append(_piece('cc_g05_walk_s%d' % i, gen_room.WALL3, x, y0 - 0.23, z, 0.0))
        if x <= cfg.WALK_DOOR_X:
            out.append(_piece('cc_g05_walk_n%d' % i, gen_room.WALL3, x - 3.0, y1 + 0.23, z, 180.0))
        x -= 3.0
        i += 1
    out.append(_piece('cc_g05_walk_end', gen_room.WALL3, x1 + 0.23, y1 + 0.1, z, 90.0, (3.3 / 3.0, 1, 1)))
    door = cfg.WALK_DOOR_X
    out += _outer_walls(x0, x1, y0, y1, z, top, door)
    # A SKIRT ROUND THE UNDERSIDE, 1 cm proud of the walls. The side of the plate
    # below, with its window openings, showed under the outer walls from the lift
    # (playtest 2026-11-06).
    west, east = x0 - 0.15, x1 + 0.47
    low, high = z - 0.7, z + 0.3
    out += _wall('cc_g05_skirt_s', 's', y0 - 0.47, west, east, low, high)
    out += _wall('cc_g05_skirt_n', 'n', y1 + 0.47, west, door, low, high)
    out += _wall('cc_g05_skirt_n2', 'n', y1 + 0.21, door, east, low, high)
    out += _wall('cc_g05_skirt_e', 'e', east, y0 - 0.47, y1 + 0.21, low, high)
    # THE UNDERSIDE CLOSED INSIDE THE SKIRT. The plate's bottom stops short of its
    # bounding box, so a gap stayed beside the walls (playtest 2026-11-06). A ceiling
    # panel is drawn from below.
    for name, a, b, north in (('cc_g05_under_w', west, door, y1 + 0.47),
                              ('cc_g05_under_e', door, east, y1 + 0.21)):
        n = max(1, int(round((b - a) / 3.0)))
        step = (b - a) / n
        for i in range(n):
            out.append(_piece('%s%d' % (name, i), gen_room.CEILING, b - i * step, north, z - 0.6, 0.0,
                              (step / 3.0, (north - (y0 - 0.47)) / 3.0, 1)))
    # THE WEST END, a wall with the sliding door to the locker room in it.
    out += _gap_wall('cc_g05_walk_west', 'e', x0, y0 - 0.1, y1 + 0.1, cfg.ROOM_WAY_IN, z + 2.3, z, top)
    gap1 = cfg.ROOF_DOOR_GAP[1] + 0.15
    out.append(_piece('cc_g05_walk_sill', gen_room.FLOOR, gap1, cfg.ROOF_SILL_Y, z, 0.0,
                      ((gap1 - cfg.ROOF_DOOR_GAP[0] + 0.15) / 3.0, (cfg.ROOF_SILL_Y - y1) / 3.0, 1)))
    out += [
        _plate('cc_g05_skin_top', x0 - 0.15, door, y0 - 0.45, y1 + 0.45, top + 0.2, top + 0.35),
        _plate('cc_g05_skin_top2', door, x1 + 0.4, y0 - 0.45, y1 + 0.1, top + 0.2, top + 0.35),
        _plate('cc_g05_skin_under', x0 - 0.15, door, y0 - 0.45, y1 + 0.45, z - 0.35, z - 0.2),
        _plate('cc_g05_skin_under2', door, x1 + 0.4, y0 - 0.45, y1 + 0.2, z - 0.35, z - 0.2),
        # THE SILL IS DRAWN FROM ABOVE ONLY, so this closes it from below.
        _plate('cc_g05_skin_under_sill', cfg.ROOF_DOOR_GAP[0] - 0.15, cfg.ROOF_DOOR_GAP[1] + 0.15, y1 + 0.2,
               cfg.ROOF_SILL_Y, z - 0.14, z - 0.02),
        # THE CAR'S DOOR: the end of the north wall.
        _plate('cc_g05_skin_jamb', door, door + 0.15, y1, y1 + 0.3, z - 0.2, top + 0.2),
    ]
    lamp, lamp_inst = gen_room.light_node()
    for i, lx in enumerate((x1 - 9.0, x1 - 21.0, x1 - 33.0, x1 - 45.0)):
        node = json.loads(json.dumps(lamp))
        node['debugName'] = community.cname('cc_g05_walk_lamp_%d' % i)
        out.append((node, (lx, (y0 + y1) / 2.0, top - 0.4),
                    community.Community.ref(SECTOR, 'cc_g05_walk_lamp_%d' % i),
                    (lamp_inst['MaxStreamingDistance'], lamp_inst['UkFloat1'],
                     lamp_inst['Uk10'], lamp_inst['Uk11']), 0.0))
    return out


def _tower():
    """Four columns, a ring of beams every 20 m, and a cap. The ring's south beam
    stands clear of the car's door side."""
    out = []
    z0, z1 = cfg.LIFT_LOW, cfg.TOWER_TOP
    (w0, w1), (e0, e1) = cfg.TOWER_X
    (s0, s1), (n0, n1) = cfg.TOWER_Y
    for i, (xs, ys) in enumerate((((w0, w1), (s0, s1)), ((e0, e1), (s0, s1)),
                                  ((w0, w1), (n0, n1)), ((e0, e1), (n0, n1)))):
        out.append(_plate('cc_g05_tower_c%d' % i, xs[0], xs[1], ys[0], ys[1], z0, z1))
    for i, z in enumerate(cfg.TOWER_RINGS):
        out.append(_plate('cc_g05_tower_rw%d' % i, w0, w1, s0, n1, z, z + 0.5))
        out.append(_plate('cc_g05_tower_re%d' % i, e0, e1, s0, n1, z, z + 0.5))
        out.append(_plate('cc_g05_tower_rn%d' % i, w0, e1, n0, n1, z, z + 0.5))
        out.append(_plate('cc_g05_tower_rs%d' % i, w0, e1, s0 - 0.7, s0, z, z + 0.5))
    out.append(_plate('cc_g05_tower_cap', w0, e1, s0 - 0.7, n1, z1 - 0.5, z1))
    # THE STREET'S CALL PANEL STANDS ON THIS, up to the first ring of the frame.
    out.append(_plate('cc_g05_tower_post', -1260.2, -1259.6, 1765.7, 1766.0, z0, cfg.TOWER_RINGS[0]))
    out.append(_box('cc_g05_tower_post_b', '952', -1260.2, 1765.7, -1259.6, 1766.0, z0, z0 + 6.0)[1])
    return out


WALKWAY = _walkway()
ROOM = _room()
TOWER = _tower()


def build():
    extra = [ROOF_FLOOR, WALK_FLOOR, WALK_S, WALK_N, WALK_E, WALK_T, WALK_W0, WALK_W1, WALK_F0, WALK_F1, WALK_SILL_BOX, PAD_BOARD, PAD_OUT, PAD_STEP_IN, RECRUITER_PIN, _door('cc_g05_lift_door', ROOF_DOOR_REF, ROOF_DOOR_SPOT, 0.0, '940', True, True), LOCKER_MARK] + WALKWAY + TOWER + TOWER_BOXES + ROOM + [_door('cc_g05_room_door', ROOM_DOOR_REF, ROOM_DOOR_SPOT, 90.0, '941', False),
                                                                _door('cc_g05_way_door', WAY_DOOR_REF, WAY_DOOR_SPOT, 90.0, '942', False, True)]
    extra += [m for _r, m in SITE_BOARD + SITE_OUT + SITE_STEP_IN + SITE_PIN + FLIGHTS]
    extra += LIFT_NODES
    panels = [(community.Community.ref(SECTOR, 'cc_g05_lift_panel_%d' % i), st[1])
              for i, st in enumerate(cfg.LIFT_STOPS)]
    folder = os.path.join(cfg.RAW_MOD, 'lift')
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, 'lift.devices.json'), 'w', encoding='utf-8',
              newline=chr(10)) as fh:
        json.dump(gen_lift.devices('lift.devices', LIFT_REF, cfg.LIFT_STOPS[0][0], panels,
                                  [(ROOF_DOOR_REF, ROOF_DOOR_SPOT, 1), (ROOM_DOOR_REF, ROOM_DOOR_SPOT, None),
                                   (WAY_DOOR_REF, WAY_DOOR_SPOT, None)]), fh,
                  indent=1)
    terminals = [n[0] for n in LIFT_NODES if isinstance(n, tuple)
                 and 'lift_panel' in n[0]['debugName']['$value']]
    with open(os.path.join(folder, 'lift.psrep.json'), 'w', encoding='utf-8',
              newline=chr(10)) as fh:
        json.dump(gen_lift.psrep('lift.psrep', list(zip(cfg.LIFT_PANEL_PSIDS, terminals))), fh,
                  indent=1)
    com = community.Community(SECTOR, entries(), spawnset=SPAWNSET_NAME,
                              phase=PHASE, period=PERIOD, extra=extra,
                              area_distance=3.40282347e+38,
                              always_spawned=True)
    return com


def write(com):
    for name, doc in com.files():
        path = os.path.join(OUT, name)
        with open(path, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(doc, fh, indent=2)
        print('wrote', path)
    print()
    print('community %s' % com.community_ref)
    for e in com.entries:
        print('   %-10s %-40s at (%.1f, %.1f, %.1f) yaw %.0f'
              % (e.name, e.record, e.pos[0], e.pos[1], e.pos[2], e.yaw))
    for label, pts in (('out', cfg.ROUTE_OUT), ('12', cfg.ROUTE_12), ('23', cfg.ROUTE_23),
                       ('back', cfg.ROUTE_BACK)):
        print('   flight %-5s %.0f m' % (label, avflight.length(pts)))


ROUTES = {'out': cfg.ROUTE_OUT, 'r12': cfg.ROUTE_12, 'r23': cfg.ROUTE_23,
          'back': cfg.ROUTE_BACK}


def write_routes():
    """The four flights sampled the way the AV flies them, for the dev
    menu's route check (cet-dev/init.lua): a Catmull-Rom curve through the
    points, which is what the spline's automatic tangents make."""
    path = os.path.join(cfg.MOD, 'source', 'cet-dev', 'routes.lua')
    lines = ['-- Written by tools/gig05/gen_community.py. Do not edit.', 'return {']
    for name, pts in ROUTES.items():
        out = [tuple(round(v, 1) for v in p) for p in avflight.sample(pts, 8.0)]
        lines.append('  %s = {%s},' % (name, ', '.join('{%s, %s, %s}' % p for p in out)))
    spots = [('pad', cfg.PAD)] + [(st['name'], st['av']) for st in cfg.SITES]
    posts = []
    for st in cfg.SITES:
        for key in ('client', 'medic', 'soldier', 'lead', 'board', 'out'):
            q = st[key]
            posts.append((st['name'] + '.' + key, q))
        for j, q in enumerate(st['scavs']):
            posts.append((st['name'] + '.scav%d' % (j + 1), q))
    for who, q in cfg.PAD_CREW.items():
        posts.append(('pad.' + who, q))
    lines.append('  posts = {%s},' % ', '.join(
        '{"%s", %.2f, %.2f, %.2f}' % (n, q[0], q[1], q[2]) for n, q in posts))
    lines.append('  spots = {%s},' % ', '.join(
        '{"%s", %.1f, %.1f, %.1f}' % (n, p[0], p[1], p[2]) for n, p in spots))
    lines.append('}')
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('\n'.join(lines) + '\n')
    print('wrote', path)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    write(build())
    write_routes()
