r"""Gig 03's communities: Dino at his bar, and the three Militech who arrive
when the security room is opened.

    python tools\gig03\gen_community.py

Writes, under source\wkit\raw:

  mod\worlds\03_night_city\_compiled\default\cc_g03_cast.streamingsector
  mod\worlds\03_night_city\_compiled\default\cc_g03_cast_reg.streamingsector
  mod\worlds\03_night_city\_compiled\default\cc_g03_cast.streamingblock
  mod\worlds\03_night_city\_compiled\default\cc_g03_militech.streamingsector
  mod\worlds\03_night_city\_compiled\default\cc_g03_militech_reg.streamingsector
  mod\worlds\03_night_city\_compiled\default\cc_g03_militech.streamingblock

TWO COMMUNITIES, TWO STACKS. Gotcha 75: a second community is its own pair of
sectors and its own block, not a second item in the first one's registry, so
the one that already works is not rewritten to add the one being built. The
cast community was Regina's until 2026-09-15 and is Dino's now; the militech
one is unchanged by the switch.

===========================================================================
WHY THIS EXISTS, AND WHY IT DID NOT UNTIL 2026-09-10

`docs/scene-playbook.md` opens with the rule: an NPC with a line is a SCENE
ACTOR, and a scene actor that also has to stand in the world and be walked up
to comes from a COMMUNITY. The scene then acquires the body that is already
standing there instead of spawning a second one.

This gig shipped the other arrangement first. Regina in her flat was an actor
the SCENE spawned, and a scene-spawned actor exists for exactly as long as the
scene does: it arrives when the scene starts and it is deleted the moment the
scene exits. Four playtest reports on 2026-09-10 are that one choice:

  * "as I enter the room it goes from her default pose to our body and I can
    see the jump" - the body cannot arrive before the conversation, because the
    conversation is what creates it
  * "as soon as the interaction with Regina is done, our body disappears, stays
    empty a bit, then the old default body appears, all while I'm still there"
  * "she just stares in the void", then "she looks at her feet"
  * gating the swap on an earlier fact changed none of it, because the fact was
    never what created the body

Gig 02 had the same four symptoms from the same cause and its
`gen_community.py` records five. Its Wakako was a borrowed base-game body until
2026-09-05 and is a community entry now.

===========================================================================
THE RECIPE IS GOTCHA 66 AND IT IS NOT NEGOTIABLE

`questkit.community` implements all six parts and gig 01's generator carries the
full account. What matters here:

  * two sectors, both AlwaysLoaded level 1: one for the registry, one for the
    area node and its AI spot
  * every ref rooted `$/mod/<sector>/#<name>`, never `$/03_night_city/`
  * `appearances` non-empty
  * one time period per phase

AND THE PART THE RECIPE DOES NOT COVER: `entryActiveOnStart: 0` IS IGNORED. A
mod's community spawns its entries on save load whatever that field says, so
THE QUEST PHASE is what keeps her away until her leg opens and puts her away
afterwards. See gen_questphase.py, which deactivates this community at the top
of the graph and activates it when the player reaches her street door.

===========================================================================
HE IS THE GAME'S OWN FACE UNDER THIS GIG'S OWN RECORD

`Character.cc_g03_dino`, which is `$base: Character.dyno` plus this gig's
shortened speaker name. So the body is the game's own Dino and the name over
his lines is the same one the holocall uses; a community built on
`Character.dyno` itself would have shown the full name at the bar and the
short one on the phone, for the same voice.

`Character.dyno`, the spot and the facing below were read out of the shipped
world (gig03_config.py has the reading), not captured in play: the switch
from Regina was made at the desk. The graph switches the game's own `#dyno`
off for the leg, so there is never a second one.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from questkit import area, community                                 # noqa: E402

from gig03_config import (                                           # noqa: E402
    RAW, DINO_POS, DINO_WORKSPOT, DINO_LEAVE_RADIUS, DINO_AREA_SIDES,
    DINO_AREA_HEIGHT, GATE_POS, GATE_FACING_YAW, GATE_SPREAD,
)

# A depot path is BUILT, never typed: `\w`, `\a`, `\0` and `\t` are all eaten
# by something between here and the file. Gotcha 28.
B = chr(92)


def depot(*parts):
    return B.join(parts)


OUT = os.path.join(RAW, 'mod', 'worlds', '03_night_city', '_compiled', 'default')

SECTOR = 'cc_g03_cast'
REG_SECTOR = 'cc_g03_cast_reg'

# The string the SCENES ask for. gen_scenes imports it from here so the two
# cannot drift. Registered in `spawnSetNameToCommunityID`; the engine matches
# the string that was registered rather than resolving a world NodeRef, so the
# short form is right (gotcha 69).
SPAWNSET_NAME = '#cc_g03_cast_com'

PHASE = 'default'
PERIOD = 'Day'


def stand_around(n):
    return depot('base', 'workspots', 'common', 'ground',
                 'generic__stand_ground__stand_around__%02d.workspot' % n)


# WHERE THE REAL DINO SITS, read out of `exterior_-16_2_0_1` on 2026-09-15:
# his own AI spot `#ws_dyno_default`, a `worldAISpotNode` at this position
# and facing, on the game's barstool workspot. Gig 02's rule is that every
# position in a community is one somebody stood on or one a body was
# demonstrably standing on when it was captured; this is a third kind, the
# spot the game's own body is placed on, and it has not been stood on in
# play yet.
#
# HIS OWN WORKSPOT IS USED, unlike Regina's. Her AI spot's resource could not
# be decoded and a stand-around idle stood in for it; his decoded to
# `generic__sit_barstool_bar__sit_around__01`, so ours sits on the same stool
# the same way and the swap has nothing to show.
DINO_POS_XYZ = DINO_POS[:3]
DINO_YAW = DINO_POS[3]

# OUR OWN RECORD, not `Character.dyno` directly. `Character.cc_g03_dino` is
# based on it, so he looks exactly like the game's Dino, and it carries this
# gig's shortened speaker name. The holocall body already uses it, and a
# community on the base record would have put the full name over his lines
# at the bar and the short one over the same voice on the phone.
CAST = [
    ('dino', 'Character.cc_g03_dino', DINO_POS_XYZ, DINO_YAW, DINO_WORKSPOT),
]

# ===========================================================================
# THE REINFORCEMENTS
#
# Three Militech soldiers who arrive when the security-room door is opened
# (the design call, 2026-09-11: "two or three more guards spawn"). A community,
# not a script spawn: a script spawn has no facing, huddles around its anchor,
# and its dead do not stay dead across a reload (docs/architecture.md, "Placing
# NPCs").
#
# THE RECORDS ARE THE SITE'S OWN. The census on 2026-09-09 read every soldier
# inside the wire, and these are three of those records, so the reinforcements
# are indistinguishable from the men already there. Vanilla records, so no
# TweakXL is needed for them (gig 01's thirty compound guards are placed the
# same way).
#
# THE SPOT IS THE GATE, captured in playtest 2026-09-15 (gig03_config.GATE_*).
# Every position in a community is one somebody stood on (gig 02's rule;
# gotcha 67 is what happens otherwise), and this one was. The three stand
# in a line across the gate, 1.5 m apart, facing into the compound (the
# opposite of the way the capture faced), so they arrive as one squad from
# the way V came in. They stood at three walked fence corners before the
# capture, which put them against the wall mesh.
#
# THEY ARE OFF UNTIL THE DOOR. A mod community spawns on save load whatever
# `entryActiveOnStart` says (gotcha 69), so gen_questphase.py deactivates this
# community at the top of the graph, activates it on the alarm, and
# deactivates it again once V is out of the Badlands, because community state
# persists in saves and a reload would otherwise bring the dead back.
#
# Gig03_Alarm.reds turns them on V the same way it turns the site's own
# soldiers: their records carry "militech" and they stand inside the wire.
MILITECH_SECTOR = 'cc_g03_militech'

RANGER = 'Character.bls_se_militech_ranger1_ranged1_saratoga_ma'
ENFORCER = 'Character.bls_se_militech_enforcer2_shotgun2_tactician_mah_rare'
TECH = 'Character.bls_se_militech_tech_franged2_omaha_ma_rare'

# The middle of the walked perimeter, the same number Gig03_Places.Middle()
# carries, which the three face.
COMPOUND_MIDDLE = (-97.052, -5213.984, 87.1)


def face(at, to):
    """The yaw at `at` that looks at `to`. Yaw is counter-clockwise from +Y
    seen from above, so a heading of theta faces (-sin, cos): atan2(-dx, dy).
    Same convention as gig 02's gen_community.face and scene.yaw_to_face_player,
    measured 2026-08-16."""
    import math
    return math.degrees(math.atan2(-(to[0] - at[0]), to[1] - at[1]))


# (name, record, offset) with the offset in metres ACROSS the facing line:
# negative to the left of the middle man, positive to the right.
REINFORCEMENTS = [
    ('left', RANGER, -GATE_SPREAD),
    ('middle', ENFORCER, 0.0),
    ('right', TECH, GATE_SPREAD),
]


def gate_spots():
    """The three positions at the gate. A heading of yaw faces
    (-sin, cos), so "across" is (cos, sin), the same convention as face()."""
    import math
    a = math.radians(GATE_FACING_YAW)
    across = (math.cos(a), math.sin(a))
    return [(name, record,
             (GATE_POS[0] + off * across[0], GATE_POS[1] + off * across[1],
              GATE_POS[2]))
            for name, record, off in REINFORCEMENTS]


def militech_entries():
    return [community.Entry(name, record, 'default', pos, GATE_FACING_YAW,
                            stand_around(1))
            for name, record, pos in gate_spots()]


def entries():
    return [community.Entry(name, record, 'default', pos, yaw, pose)
            for name, record, pos, yaw, pose in CAST]


# ===========================================================================
# THE BAR, DRAWN ON THE MINIMAP
#
# "Leave Dino's bar" is a leave-the-area objective, and the game draws those
# as a shaded zone while the player is inside it (docs/map-pins-playbook.md,
# "A quest area drawn on the minimap"; gig 02's way out is the worked
# example). The zone is a `worldTriggerAreaNode` shipped as an extra node of
# this always-loaded sector, and the objective's pin points at it.
#
# THE SHAPE IS THE LEAVING TEST. Gig03_Places.reds calls V out at
# DINO_LEAVE_RADIUS from the stool, so the area is that circle, as a 16-gon
# inscribed in it: the outline disappears as V crosses an edge (0.7 m inside
# the circle at worst) and the objective closes at the circle. One number in
# gig03_config.py feeds both. Nobody has walked the bar's edge, so a circle
# round the stool is what there is; a walked polygon can replace it the way
# gig 02's did (tools/gig02/hit_area.py).
#
# The instance flags are the ones every vanilla trigger area carries (Uk11
# 65024, Uk12 1); with a shard case's flags the loader never found gig 02's.
BAR_AREA_REF = community.Community.ref(SECTOR, 'cc_g03_bar_area')


def bar_area_position():
    """The node sits 2 m under the bar floor, under the stool."""
    return (DINO_POS[0], DINO_POS[1], DINO_POS[2] - 2.0)


def bar_area_corners():
    """The 16-gon's corners in world XY, counter-clockwise."""
    import math
    out = []
    for i in range(DINO_AREA_SIDES):
        a = 2.0 * math.pi * i / DINO_AREA_SIDES
        out.append((DINO_POS[0] + DINO_LEAVE_RADIUS * math.cos(a),
                    DINO_POS[1] + DINO_LEAVE_RADIUS * math.sin(a)))
    return out


def bar_area_node():
    pos = bar_area_position()
    local = [(x - pos[0], y - pos[1]) for x, y in bar_area_corners()]
    node = {
        '$type': 'worldTriggerAreaNode',
        'color': {'$type': 'Color', 'Alpha': 0, 'Blue': 0, 'Green': 0, 'Red': 0},
        'debugName': community.cname('{cc_g03_bar_area}'),
        'isHostOnly': 0,
        'isVisibleInGame': 1,
        'notifiers': [{'HandleId': '1', 'Data': {
            '$type': 'questTriggerNotifier_Quest', 'excludeChannels': 0,
            'includeChannels': 'TC_Default', 'isEnabled': 1}}],
        'outline': area.outline(local, DINO_AREA_HEIGHT, handle_id='2'),
        'proxyScale': None,
        'sourcePrefabHash': '0',
        'tag': 'None',
        'tagExt': 'None',
    }
    return node, pos


_BAR_NODE, _BAR_POS = bar_area_node()
# MaxStreamingDistance, UkFloat1, Uk10, Uk11, Uk12: the Japantown trigger area
# gig 02 read the outline format from (`{cs_tr_vo}`, exterior_-10_18_0_0).
BAR_AREA = (_BAR_NODE, _BAR_POS, BAR_AREA_REF, (2760.11133, 90.03862, 1056, 65024, 1))


def build():
    return community.Community(SECTOR, entries(), spawnset=SPAWNSET_NAME,
                               phase=PHASE, period=PERIOD, extra=[BAR_AREA])


def build_militech():
    # No spawn set: no scene ever acquires one of these bodies.
    return community.Community(MILITECH_SECTOR, militech_entries(),
                               phase=PHASE, period=PERIOD)


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
        print('   %-8s %-32s at (%.1f, %.1f, %.1f) yaw %.0f'
              % (e.name, e.record, e.pos[0], e.pos[1], e.pos[2], e.yaw))


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    write(build())
    print('   scenes ask for %s' % SPAWNSET_NAME)
    print()
    write(build_militech())
