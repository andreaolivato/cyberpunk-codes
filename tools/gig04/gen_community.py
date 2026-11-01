r"""Return Ticket's community: Ligaya at her stall, Stamps at the bar, the
Tyger Claws' van, Bayani and eight Claws in the room, Orbital Air's guards
in two sets and their car, and the area round the room.

    python tools\gig04\gen_community.py

Writes, under source\wkit\raw:

  mod\worlds\03_night_city\_compiled\default\cc_g04_cast.streamingsector
  mod\worlds\03_night_city\_compiled\default\cc_g04_cast_reg.streamingsector
  mod\worlds\03_night_city\_compiled\default\cc_g04_cast.streamingblock

ONE COMMUNITY, NINETEEN ENTRIES. The quest phase switches entries on by name
as their beats open (gotcha 69: a mod community spawns everything on save
load whatever `entryActiveOnStart` says, so the graph deactivates the whole
community at its top and activates entries one at a time). The recipe is
gotcha 66 through `questkit.community`; gig 03's generator carries the
account of why a community rather than a scene-spawned body.

WHERE THEY STAND. Ligaya is a capture (`captures/`, 2026-09-30): she
stands behind the counter of a Kabuki Market stall, in the spot of the
game's own vendor, whose community the manifest deletes. Stamps sits on the game's own bar stool on the walkway
west of the market, and the van is parked in a lot in south-west Little
China (gig04_config, BAR_STAMPS and VAN). Bayani and the
Claws are placed in the room's own frame (gig04_config.ROOM_*), because the
room did not exist to be walked (tools/gig04/gen_room.py).

THE CLAWS ARE THE GAME'S OWN RECORDS, Tyger Claws the game places in City
Center (`Character.dtn_tyger_claws_*`, read off the TweakDB name table), so no
TweakXL is needed for them. Gig04_Places.reds turns them on V when V comes
near the room (gotchas 74 and 77: a community NPC arrives with no quarrel and
with its senses off).
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from questkit import area, community                                 # noqa: E402

from gig04_config import (                                           # noqa: E402
    RAW, STALL_LIGAYA, BAR_STAMPS, ROOM_BAYANI, ROOM_CLAWS,
    ROOM_LEAVE_RADIUS, ROOM_HEIGHT, VAN, VAN_PIN, OA_CARS, OA_GUARDS, STREET_Z,
    RAIL_PROMPT, RAIL_POSE, RAIL_YAW, LEAN_WORKSPOT,
)

import gen_room                                                      # noqa: E402
import gig04_config as cfg                                           # noqa: E402

B = chr(92)


def depot(*parts):
    return B.join(parts)


OUT = os.path.join(RAW, 'mod', 'worlds', '03_night_city', '_compiled', 'default')

SECTOR = 'cc_g04_cast'
# The string the SCENES ask for (gotcha 69).
SPAWNSET_NAME = '#cc_g04_cast_com'
PHASE = 'default'
PERIOD = 'Day'

LIGAYA = 'ligaya'
STAMPS = 'stamps'
BAYANI = 'bayani'

# ONE FACE EACH, the same one the record pins (source/tweaks/characters.yaml
# has the account), named on the entry and on the scene actor as well so
# nothing can roll another (gig 02's rule).
APPEARANCE = {
    LIGAYA: 'service__vendor_wa_vendor_asian_03',
    STAMPS: 'service__vendor_ma_vendor_asian_01',
    BAYANI: 'service__vendor_ma_vendor_asian_02',
}


def stand_around(n):
    return depot('base', 'workspots', 'common', 'ground',
                 'generic__stand_ground__stand_around__%02d.workspot' % n)


# STAMPS DRINKS AT THE BAR, leaning on the counter: the game's own barstool
# pose with a glass, read off the stools round Kabuki Market (2026-10-01).
BARSTOOL = depot('base', 'workspots', 'common', 'bar_and_barstool',
                 'generic__sit_barstool_bar_lean_front_vodka__drink__01.workspot')
# THE CLAWS ON THE COUCHES SIT. The plain couch pose the fixer's pose panel lists
# (tools/fixer01/gen_poses.py, `couch_01`); Hodan herself sits on a chair
# pose because the couch one read as a slouch, and a slouch suits a Claw.
COUCH = depot('base', 'workspots', 'common', 'couch',
              'generic__sit_couch__sit_around__01.workspot')
# BAYANI SITS ON THE FLOOR, back to the wall: the game's own ground pose
# (read out of memoryresident_1_general on 2026-10-01 with the other
# ground, lying and sitting poses; this one leans back against a wall).
SIT_FLOOR = depot('base', 'workspots', 'common', 'ground',
                  'generic__sit_ground_lean_back__sit_around__01.workspot')
# THE TWO AT THE DOOR STAND GUARD, hands clasped in front, facing the street
# (the design call, 2026-10-01; the bodyguard pose out of the same list).
GUARD = depot('base', 'workspots', 'common', 'ground',
              'bodyguard__stand_ground__2h_front__01.workspot')

# THE CLAWS' RECORDS, the game's own. Two on the street with pistols, the
# rest inside: rifles, a shotgun, knives and a katana. THE DISTRICT'S OWN
# COPIES: the room is in Little China, so `lch_`
# (audit 2026-10-13: City Center's `dtn_` stood in both). The
# Shingen biker has no `lch_` copy in the TweakDB name table, so the room's
# one is Kabuki's, the next district over.
CLAW_RECORDS = {
    'claw1': 'Character.lch_tyger_claws_gangster1_ranged1_nue_ma',
    'claw2': 'Character.lch_tyger_claws_biker1_ranged1_saratoga_wa',
    'claw3': 'Character.lch_tyger_claws_gangster2_ranged2_copperhead_ma',
}


# THE CLAWS' VAN: the game's Tyger Claws Columbus, in the look its own
# communities give it (`villefort_columbus__basic_tygerclaws_01`, the sector
# cache). Placed like Orbital Air's car, an entry with no pose.
VAN_ENTRY = 'van'
VAN_RECORD = 'Vehicle.v_standard25_villefort_columbus_tyger'
VAN_LOOK = 'villefort_columbus__basic_tygerclaws_01'

# ORBITAL AIR, TWO WAYS. Its own guards exist only with Phantom Liberty
# (quest q306, `Character.q306_orbital_air_*`, read off the TweakDB name
# table), and this gig needs nothing from the expansion. So there are two
# sets of three entries at the same three spots: Orbital Air's own for a
# player who has the expansion, the game's unbranded corporate security
# from Corpo Plaza (`cpz_security_*`) for one who does not. The quest
# switches on one set, by `cc_g04_ep1`, which Gig04_Places.reds writes from
# the game's own `IsEP1()`. The looks are the ones the game's own
# communities give these records (always_loaded, 2026-10-01): `default`
# where the game uses it, the guard look where it does not.
OA_PL = [
    ('oa1', 'Character.q306_orbital_air_generic_guard_ma', 'orbital_air_ma_guard__lvl1_01'),
    ('oa2', 'Character.q306_orbital_air_guard_rifle_ma', 'orbital_air_ma_guard__lvl2_01'),
    ('oa3', 'Character.q306_orbital_air_generic_guard_smg_ma', 'orbital_air_ma_guard__lvl1_02'),
]
OA_BASE = [
    ('sec1', 'Character.cpz_security_guard1_ranged1_nue_ma', 'default'),
    ('sec2', 'Character.cpz_security_security2_ranged2_ajax_ma', 'default'),
    ('sec3', 'Character.cpz_security_enforcer3_shotgun2_tactician_mb_rare', 'default'),
]
# THE CAR, the same for both sets: the game's corporate Columbus,
# which its own communities place (always_loaded_1), in the look they give
# it. A community spawns a car the way it spawns a person, at a spot with
# no pose (questkit.community, `ai_spot_node`).
OA_CAR_RECORD = 'Vehicle.v_standard25_villefort_columbus_corpo'
OA_CAR_LOOK = 'villefort_columbus__basic_corpo_01'
OA_PL_ENTRIES = [n for n, _r, _a in OA_PL]
OA_BASE_ENTRIES = [n for n, _r, _a in OA_BASE]
OA_CAR_ENTRIES = [n for n, _u, _v, _z, _y in OA_CARS]


def street(u, v, z):
    """A point on the street in the room's frame at its own height."""
    x, y, _ = gen_room.room_to_world(u, v)
    return (x, y, z)


def entries():
    out = [
        community.Entry(LIGAYA, 'Character.cc_g04_ligaya', APPEARANCE[LIGAYA],
                        STALL_LIGAYA[:3], STALL_LIGAYA[3], stand_around(2)),
        community.Entry(STAMPS, 'Character.cc_g04_stamps', APPEARANCE[STAMPS],
                        BAR_STAMPS[:3], BAR_STAMPS[3], BARSTOOL),
    ]
    bx, by, byaw = ROOM_BAYANI
    # HE LEAVES BY HIMSELF after his talk, but not through a second
    # community phase: a `leave` phase with one street spot made him vanish
    # a few steps into his walk when the quest switched him to it (playtest
    # 2026-10-01; the switch respawns the entry). One phase, one spot, and
    # Gig04_Places.reds sends him out with the game's own move order.
    out.append(community.Entry(BAYANI, 'Character.cc_g04_bayani',
                               APPEARANCE[BAYANI],
                               gen_room.room_to_world(bx, by),
                               gen_room.room_yaw(byaw), SIT_FLOOR))
    # THREE CLAWS SIT, on the couches gen_room places (the design call,
    # 2026-10-01): the plain couch pose, at a spot 0.2 m in front
    # of the couch's centre, facing the way the couch faces. The rest stand.
    for i, (name, x, y, yaw, pose) in enumerate(ROOM_CLAWS):
        spot = {'sit': COUCH, 'guard': GUARD}.get(pose, stand_around(1 + i % 5))
        # ON THE STREET (y < 0, the two at the door) AT THE PAVEMENT'S OWN
        # HEIGHT: the door's 18.19 is 0.2 m under it (audit 2026-10-01,
        # second pass). Inside, the room's floor is the door's height.
        pos = street(x, y, STREET_Z) if y < 0 else gen_room.room_to_world(x, y)
        out.append(community.Entry(name, CLAW_RECORDS[name], 'default',
                                   pos, gen_room.room_yaw(yaw), spot))
    out.append(community.Entry(VAN_ENTRY, VAN_RECORD, VAN_LOOK, VAN[:3],
                               VAN[3], None))
    # ORBITAL AIR: both sets at the same three spots on the street, out of
    # sight of the door, each facing it (gig04_config OA_GUARDS), at the
    # pavement's height.
    for (u, v, z, ryaw), pl, base in zip(OA_GUARDS, OA_PL, OA_BASE):
        pos = street(u, v, z) if v < 0 else gen_room.room_to_world(u, v)
        yaw = gen_room.room_yaw(ryaw)
        for i, (name, record, look) in enumerate((pl, base)):
            out.append(community.Entry(name, record, look, pos, yaw,
                                       stand_around(1 + (len(out) + i) % 5)))
    for name, u, v, z, yaw in OA_CARS:
        out.append(community.Entry(name, OA_CAR_RECORD, OA_CAR_LOOK,
                                   street(u, v, z),
                                   gen_room.room_yaw(yaw), None))
    return out


def check_script_names():
    """THE ENTRY NAMES THE SCRIPT USES, against these. Gig04_Places.reds
    restates them by hand (ClawEntries, OAEntries,
    StampsEntry, BayaniEntry, and Ligaya's), and a name that drifts is a
    group the script never finds, in silence. Every n"..." name in the
    script that looks like an entry has to be one here."""
    import re
    here = os.path.dirname(os.path.abspath(__file__))
    reds = os.path.join(os.path.dirname(os.path.dirname(here)), 'mods',
                        'gig-04-return-ticket', 'source', 'scripts',
                        'Gig04_Places.reds')
    with open(reds, encoding='utf-8') as fh:
        text = fh.read()
    names = {e.name for e in entries()}
    pattern = r'n"((?:claw|oa|sec)[0-9]|stamps|bayani|ligaya)"'
    used = set(re.findall(pattern, text))
    missing = sorted(used - names)
    if missing:
        raise SystemExit('Gig04_Places.reds names entries this community '
                         'does not have: %s' % ', '.join(missing))
    # AND THE OTHER WAY: every person the script has to turn, hunt, watch or
    # shield is named there (audit 2026-10-01, second pass). The cars are
    # not people.
    people = {n for n in names if not n.startswith('oacar') and n != VAN_ENTRY}
    forgotten = sorted(people - used)
    if forgotten:
        raise SystemExit('Gig04_Places.reds never names these entries: %s'
                         % ', '.join(forgotten))
    # THE PLACES IT RESTATES, against the config, to the centimetre.
    want = {'Door': cfg.ROOM_DOOR[:3], 'Stall': cfg.STALL_LIGAYA[:3],
            'Bar': cfg.BAR_STAMPS[:3], 'Van': cfg.VAN_PIN,
            'LeaveSpot': cfg.LEAVE_END[:3],
            'ByeSpot': gen_room.room_to_world(*cfg.ROOM_BAYANI_BYE[:2])}
    # HODAN'S SOFA, the fixer's own config.
    sys.path.insert(0, os.path.join(os.path.dirname(here), 'fixer01'))
    import fixer01_config
    want['FixerSofa'] = fixer01_config.FIXER_POS[:3]
    for fn, pos in want.items():
        m = re.search(r'static func %s\(\) -> Vector4 \{\s*return new Vector4\('
                      r'([-0-9.]+), ([-0-9.]+), ([-0-9.]+)' % fn, text)
        if not m:
            raise SystemExit('Gig04_Places.reds has no %s()' % fn)
        got = tuple(float(v) for v in m.groups())
        if max(abs(a - b) for a, b in zip(got, pos)) > 0.01:
            raise SystemExit('Gig04_Places.reds %s() is %r, the config says %r'
                             % (fn, got, pos))


# ===========================================================================
# THE ROOM, DRAWN ON THE MINIMAP for "leave the area": a trigger area node
# round Bayani's spot, a 16-gon of ROOM_LEAVE_RADIUS, gig 03's bar shape
# (docs/map-pins-playbook.md, "A quest area drawn on the minimap"). The
# quest phase's leaving wait is a distance from Bayani's entry of the same
# number, so the outline goes as the objective closes.
AREA_REF = community.Community.ref(SECTOR, 'cc_g04_room_area')
AREA_SIDES = 16
AREA_HEIGHT = 30.0


def area_centre():
    bx, by, _ = ROOM_BAYANI
    x, y, z = gen_room.room_to_world(bx, by)
    return (x, y, z - 2.0)


def area_corners():
    cx, cy, _ = area_centre()
    return [(cx + ROOM_LEAVE_RADIUS * math.cos(2 * math.pi * i / AREA_SIDES),
             cy + ROOM_LEAVE_RADIUS * math.sin(2 * math.pi * i / AREA_SIDES))
            for i in range(AREA_SIDES)]


def area_node():
    pos = area_centre()
    local = [(x - pos[0], y - pos[1]) for x, y in area_corners()]
    node = {
        '$type': 'worldTriggerAreaNode',
        'color': {'$type': 'Color', 'Alpha': 0, 'Blue': 0, 'Green': 0, 'Red': 0},
        'debugName': community.cname('{cc_g04_room_area}'),
        'isHostOnly': 0,
        'isVisibleInGame': 1,
        'notifiers': [{'HandleId': '1', 'Data': {
            '$type': 'questTriggerNotifier_Quest', 'excludeChannels': 0,
            'includeChannels': 'TC_Default', 'isEnabled': 1}}],
        'outline': area.outline(local, AREA_HEIGHT, handle_id='2'),
        'proxyScale': None,
        'sourcePrefabHash': '0',
        'tag': 'None',
        'tagExt': 'None',
    }
    return node, pos


_AREA_NODE, _AREA_POS = area_node()


# THE CLUE HUNT, DRAWN ON THE MINIMAP the same way (the design call,
# 2026-10-14: "draw the yellow area so that it encompasses the 3 clues"),
# on the design's own outline (gig04_config.CLUE_AREA_POLY). "Scan the
# area for clues" is anchored on it, at the middle of its points.
CLUE_AREA_REF = community.Community.ref(SECTOR, 'cc_g04_clue_area')


def clue_area_centre():
    pts = cfg.CLUE_AREA_POLY
    x = sum(p[0] for p in pts) / len(pts)
    y = sum(p[1] for p in pts) / len(pts)
    return (x, y, cfg.GROUND_Z - 2.0)


def clue_area_node():
    cx, cy, cz = clue_area_centre()
    local = [(x - cx, y - cy) for x, y in cfg.CLUE_AREA_POLY]
    node = json.loads(json.dumps(_AREA_NODE))
    node['debugName'] = community.cname('{cc_g04_clue_area}')
    node['outline'] = area.outline(local, AREA_HEIGHT, handle_id='2')
    return node, (cx, cy, cz)


_CLUE_NODE, _CLUE_POS = clue_area_node()
CLUE_AREA = (_CLUE_NODE, _CLUE_POS, CLUE_AREA_REF, (2760.11133, 90.03862, 1056, 65024, 1))
# The instance flags every vanilla trigger area carries (gig 02's reading).
ROOM_AREA = (_AREA_NODE, _AREA_POS, AREA_REF, (2760.11133, 90.03862, 1056, 65024, 1))


# THE WAITING SPOT, gig 02's two nodes (tools/gig02/gen_community.py, "THE
# TWO PROMPTS"): a spot with the game's player lean, which a scene hands to
# V at its own place, and a marker at the prompt point, which the scene
# plays at and the objective's map marker sits on with a zero offset. The
# cast sector is AlwaysLoaded, which a marker's anchor needs.
RAIL_SPOT_REF = community.Community.ref(SECTOR, 'cc_g04_rail_spot')
RAIL_SPOT = (community.Community.ai_spot_node(
                 None, 'cc_g04_rail_spot',
                 depot('base', 'workspots', *LEAN_WORKSPOT), []),
             RAIL_POSE, RAIL_SPOT_REF,
             (community.WB['maxdist'], community.WB['ukfloat'],
              community.WB['uk10'], community.WB['uk11']),
             RAIL_YAW)
# BAYANI'S TWO STANDING SPOTS (gig04_config ROOM_BAYANI_STAND and
# ROOM_BAYANI_BYE): the plain standing idle, no markings, so the crowd
# never takes one (gotcha 96). Gig04_Places.reds sends him to them.
def _bayani_spot(name, where):
    u, v, yaw = where
    ref = community.Community.ref(SECTOR, name)
    return ref, (community.Community.ai_spot_node(None, name, stand_around(1), []),
                 gen_room.room_to_world(u, v), ref,
                 (community.WB['maxdist'], community.WB['ukfloat'],
                  community.WB['uk10'], community.WB['uk11']),
                 gen_room.room_yaw(yaw))


BAYANI_STAND_REF, BAYANI_STAND = _bayani_spot('cc_g04_bayani_stand', cfg.ROOM_BAYANI_STAND)
BAYANI_BYE_REF, BAYANI_BYE = _bayani_spot('cc_g04_bayani_bye', cfg.ROOM_BAYANI_BYE)
RAIL_MARKER_REF = community.Community.ref(SECTOR, 'cc_g04_rail_marker')
RAIL_MARKER = (community.Community.marker_node(None, 'cc_g04_rail_marker'),
               RAIL_PROMPT, RAIL_MARKER_REF,
               (community.WB['maxdist'], community.WB['ukfloat'],
                community.WB['uk10'], community.WB['uk11']))


# THE VAN'S MARKER, at its back doors: the two van objectives' map pins
# hang on it with a zero offset, as the waiting spot's does.
VAN_MARKER_REF = community.Community.ref(SECTOR, 'cc_g04_van_marker')
VAN_MARKER = (community.Community.marker_node(None, 'cc_g04_van_marker'),
              VAN_PIN, VAN_MARKER_REF,
              (community.WB['maxdist'], community.WB['ukfloat'],
               community.WB['uk10'], community.WB['uk11']))

# NO PASSER-BY AT STAMPS'S BAR. Playtest 2026-10-14: a woman from the crowd
# sat on his stool with him, after the game's own seat there was deleted
# (the manifest) and with no marking on his spot (gotcha 96). The crowd
# system spawns nobody inside a null area; this one covers both stools and
# the front of the counter, 5.5 m by 5 m round him. The barkeep is a
# community and stays. Switched on with Stamps and off when he goes
# (gen_questphase), the shape gig 02 uses outside the Afterlife.
BAR_NULL_REF = community.Community.ref(SECTOR, 'cc_g04_bar_null')
BAR_NULL = (community.crowd_null_area_node(
                'cc_g04_bar_null',
                [(-3.0, -2.5), (2.5, -2.5), (2.5, 2.5), (-3.0, 2.5)], height=4.0),
            BAR_STAMPS[:3], BAR_NULL_REF,
            (community.WB['maxdist'], community.WB['ukfloat'],
             community.WB['uk10'], community.WB['uk11']))


def build():
    # THE GAME'S OWN AREA DISTANCE (questkit.community, `area_distance`): the
    # cast runs from the market to the van, 1 km, and at 120 m from the
    # middle of that box Ligaya and Stamps took minutes to appear.
    # ALWAYS SPAWNED, as the game's own quest characters are
    # (questkit.community, `always_spawned`): Ligaya at the default was
    # missing at her first talk in one run of three (playtest 2026-10-14).
    return community.Community(SECTOR, entries(), spawnset=SPAWNSET_NAME,
                               phase=PHASE, period=PERIOD,
                               extra=[ROOM_AREA, RAIL_SPOT, RAIL_MARKER, VAN_MARKER,
                                      BAR_NULL, BAYANI_STAND, BAYANI_BYE, CLUE_AREA],
                               area_distance=3.40282347e+38,
                               always_spawned=True)


def write(com):
    for name, doc in com.files():
        path = os.path.join(OUT, name)
        with open(path, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(doc, fh, indent=2)
        print('wrote', path)
    print()
    print('community %s' % com.community_ref)
    print('   id     %s' % com.community_id)
    for e in com.entries:
        print('   %-8s %-52s at (%.1f, %.1f, %.1f) yaw %.0f'
              % (e.name, e.record, e.pos[0], e.pos[1], e.pos[2], e.yaw))
    print('   scenes ask for %s' % SPAWNSET_NAME)
    print('   area   %s, %.0f m round Bayani' % (AREA_REF, ROOM_LEAVE_RADIUS))


if __name__ == '__main__':
    check_script_names()
    os.makedirs(OUT, exist_ok=True)
    write(build())
