r"""Fixer 01's community: the fixer, standing where his office will be.

    python tools\fixer01\gen_community.py

Writes, under source\wkit\raw:

  mod\worlds\03_night_city\_compiled\default\cc_f01_cast.streamingsector
  mod\worlds\03_night_city\_compiled\default\cc_f01_cast_reg.streamingsector
  mod\worlds\03_night_city\_compiled\default\cc_f01_cast.streamingblock

ONE ENTRY AND ONE MARKER. The entry is the fixer herself, sitting on the
lobby sofa in Charter Hill (fixer01_config.FIXER_POS, the couch workspot
FIXER_WORKSPOT; she stood on a stand-around idle at a Kabuki spot until
2026-09-18). The marker is the fixed point her map icon hangs off: a
`worldStaticMarkerNode` in the same always-loaded sector, so the icon
resolves from anywhere on the map (docs/map-pins-playbook.md, "Your own
anchors"). The base game does the same with an empty entity
(`#cct_fixer_mp`).

HE IS NEVER SWITCHED OFF. A vanilla fixer's community is kept on by his own
phase for the whole game, and this one is the same: no Deactivate at the top
of the graph, unlike every earlier gig's cast. A mod community spawns on save
load whatever `entryActiveOnStart` says (gotcha 69), and for once that is the
behaviour wanted.

THE RECIPE IS GOTCHA 66, through `questkit.community`, and gig 03's
gen_community.py carries the account of why a community rather than a
scene-spawned body. Nothing is different here.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from questkit import community                                       # noqa: E402

from fixer01_config import (                                         # noqa: E402
    RAW, FIXER_POS, FIXER_RECORD, FIXER_WORKSPOT,
)

B = chr(92)


def depot(*parts):
    return B.join(parts)


OUT = os.path.join(RAW, 'mod', 'worlds', '03_night_city', '_compiled', 'default')

SECTOR = 'cc_f01_cast'

# The string a SCENE asks for, when he gets one (gotcha 69). No scene yet.
SPAWNSET_NAME = '#cc_f01_cast_com'

PHASE = 'default'
PERIOD = 'Day'

# THE ENTRY NAME. It is written into the map icon's `dynamicEntityRef.names`
# by gen_journal.py, which is how the base game's icon names its fixer's body
# (`#reggie`, entry `reggie`), and it is the name a quest node addresses him
# by. One string, imported from here.
ENTRY = 'fixer'


def stand_around(n):
    return depot('base', 'workspots', 'common', 'ground',
                 'generic__stand_ground__stand_around__%02d.workspot' % n)


# HER LOOK: the one appearance of the entity gen_npv.py builds, named here as
# well as on the record (source/tweaks/fixer.yaml) so the community cannot
# roll another.
import gen_npv                                                       # noqa: E402
APPEARANCE = gen_npv.APPEARANCE

# THE SOFA. Her AI spot carries the couch workspot and nothing else: no
# markings, so the crowd cannot take the seat (gotcha 96).
CAST = [
    (ENTRY, FIXER_RECORD, APPEARANCE, FIXER_POS[:3], FIXER_POS[3],
     FIXER_WORKSPOT),
]


def entries():
    return [community.Entry(name, record, app, pos, yaw, pose)
            for name, record, app, pos, yaw, pose in CAST]


# THE ICON'S FIXED POINT. Half a metre above his feet, where the base game's
# icons sit (`slotOffset.Z = 0.5` on every fixer entry); the POI's own offset
# is zero, so the marker IS the position.
MARKER_REF = community.Community.ref(SECTOR, 'cc_f01_fixer_marker')
MARKER_POS = (FIXER_POS[0], FIXER_POS[1], FIXER_POS[2] + 0.5)
MARKER = (community.Community.marker_node(None, 'cc_f01_fixer_marker'),
          MARKER_POS, MARKER_REF,
          (community.WB['maxdist'], community.WB['ukfloat'],
           community.WB['uk10'], community.WB['uk11']))


def build():
    # ALWAYS SPAWNED, as the game's own quest characters are
    # (questkit.community, `always_spawned`; gotcha 132). Playtest
    # 2026-10-16: her couch empty after her introduction, the same fault
    # gig 04's Ligaya had until her cast was marked on 2026-10-15.
    return community.Community(SECTOR, entries(), spawnset=SPAWNSET_NAME,
                               phase=PHASE, period=PERIOD, extra=[MARKER],
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
        print('   %-8s %-32s at (%.1f, %.1f, %.1f) yaw %.0f'
              % (e.name, e.record, e.pos[0], e.pos[1], e.pos[2], e.yaw))
    print('   marker %s' % MARKER_REF)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    write(build())
