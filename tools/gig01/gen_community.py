r"""Gig 01's community: the one that stands Hoshino where V meets him.

THIS IS SHIPPED CONTENT, not a bench. `tools/gig01/gen_commlab*.py` are the
bench that proved every part of it, and they live on the `community-lab` branch
only.

===========================================================================
WHAT THIS REPLACES, AND WHY

Hoshino used to be TWO BODIES: one `Gig01_Encounter` spawned for the player to
shoot, and an invisible scene actor a kilometre away carrying the voice and the
lipsync. The reported "half-way in a pillar" was that second actor. Sixteen
bench runs replaced the arrangement; `gotchas.md` 66 and 69 are the recipe and
`backlog.md` 29-ADDENDUM-7 is the evidence.

He is now ONE body: this community stands him where he waits, the quest phase
switches him on when the story wants him, and the scene speaks through the body
that is already there.

===========================================================================
THE RECIPE, WHICH IS GOTCHA 66 AND IS NOT NEGOTIABLE

All six parts ship together. Eleven bench runs failed on the two marked, both of
them the bench's own inventions rather than anything the wiki said.

  1. ONE name for the community. The area node carries it, the sector registers
     it, `sourceObjectId` is its FNV1a64 minus '#', and the registry item
     repeats that hash.
  2. A `worldCommunityRegistryNode` in an AlwaysLoaded level-1 sector with a
     +-99999 box, unnamed uint64 instance, ranges 17.32 / 1e8, uk10 32, uk11 512.
  3. The `_Streamable` area node TOGETHER WITH its AI spots, in their own
     AlwaysLoaded level-1 sector, small local box, grid cell 0.
  4. Every ref rooted `$/mod/<sector>/#<name>`, never `$/03_night_city/`.
  5. **`appearances` NON-EMPTY.** The wiki calls it optional. It is not.
  6. **ONE time period per phase.** Five was a bench invention.

===========================================================================
AND THE ONE THING THE RECIPE DOES NOT COVER

**`entryActiveOnStart: 0` IS IGNORED** (bench run 14). A mod's community spawns
its entries on save load whatever that field says, so the field below states
intent and does nothing, and the QUEST PHASE is what actually keeps him away:
`gen_questphase.py` deactivates the entry as its first act, activates it when the
estate objective goes up, and deactivates it again after the malware is uploaded.

That last one is not tidiness, and its TIMING is not either. Community state
persists in saves, so an entry left active with a dead man in it puts him back at
his spot, alive, for anyone who loads a save taken after the kill. But
`Deactivate` removes the body, corpse included: it sat right after his death for
one build and playtest reported the obvious, *"it's a bit weird that the body
disappeared"*. It happens after the malware now, by which time V has walked away
from the body and the gig is finished with him.

===========================================================================
THE SPAWN SET, which is how the SCENE finds him

`spawnSetNameToCommunityID` maps a `CName` to a community id, and it is the join
a `spawnSet` scene actor walks (gotcha 69). Vanilla ships 329 rows. This ships
one, and `gen_scenes.build_hoshino` names the same string.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from questkit import community                                      # noqa: E402
from gig01_config import REPO, RAW, MOD_NAME                        # noqa: E402

# A DEPOT PATH IS BUILT, NEVER TYPED. `\w`, `\a`, `\0` and `\t` are all eaten by
# something between here and the file. See docs/gotchas.md 28.
B = chr(92)


def depot(*parts):
    return B.join(parts)


OUT = os.path.join(RAW, 'mod', 'worlds', '03_night_city', '_compiled', 'default')

# ------------------------------------------------------------------ the names
#
# Two sectors, because the registry and the area node may not share one: gotcha
# 66 parts 2 and 3. Both AlwaysLoaded, both level 1.
SECTOR = 'cc_g01_hoshino'
REG_SECTOR = 'cc_g01_hoshino_reg'
SECTOR_DEPOT = depot('mod', 'worlds', '03_night_city', '_compiled', 'default',
                     SECTOR + '.streamingsector')
REG_DEPOT = depot('mod', 'worlds', '03_night_city', '_compiled', 'default',
                  REG_SECTOR + '.streamingsector')


def ref(sector, name):
    """`$/mod/<sector>/#<name>`, and part 4 of the recipe. Eleven bench runs
    used `$/03_night_city/...` and none of them spawned anybody."""
    return '$/mod/' + sector + '/#' + name


COMMUNITY_REF = ref(SECTOR, 'cc_g01_hoshino_com')
SPOT_REF = ref(SECTOR, 'cc_g01_hoshino_spot')
REGISTRY_REF = ref(REG_SECTOR, 'cc_g01_hoshino_registry')

# The string the SCENE asks for, and `gen_scenes.py` imports it from here so the
# two cannot drift. Registered in `spawnSetNameToCommunityID` below; the engine
# matches it as the string that was registered rather than resolving it as a
# world NodeRef, so the short form is fine (gotcha 69).
SPAWNSET_NAME = '#cc_g01_hoshino_com'

PHASE = 'default'
PERIOD = 'Day'

ENTRY = 'hoshino'
CHARACTER = 'Character.cc_g01_hoshino'
APPEARANCE = 'default'

# ================================================== THE POSE LAB IS FINISHED
#
# It ran once and answered in one session, playtest 2026-08-25. Four sit
# variants at one seat:
#
#   couch, master\, floor height     no
#   couch, master\, cushion height   no
#   chair, master\, floor height     no
#   chair, COMMON\, floor height     YES, "works great"
#
# **The shelf was the answer and the furniture was not.** Every sit tried before
# came from `master\`; the standing idle that has always worked here comes from
# `common\`. A `master_` workspot is evidently not something a community spot
# hands an NPC directly. Height turned out not to matter either, since the one
# that worked is at floor height.
#
# The three that failed are GONE rather than kept as controls: they are three
# more entries that can be switched on by accident, and a body in the wrong pose
# in the same seat is exactly the confusion this lab existed to remove. The
# finding is in `gotchas.md` 72; the entries do not need to survive it.

# ============================================== THE GUARD LAB, and it is a TEST
#
# `backlog.md` 31. Playtest 2026-08-25, one community-placed guard alone on the
# estate grounds with the gig not running: **he saw V, challenged him out loud,
# and never turned hostile until he was shot first.**
#
# The challenge is the half that matters: it is the warning phase the
# script-spawned guards have never had, and it arrived for free. What is not
# settled is whether never attacking is right, and that is what these three are
# for. Same shape as the pose lab: all at ONE post, switched one at a time, so
# the comparison is between variants rather than between places.
#
#   default   nothing applied. What was tested: challenges, never attacks.
#   hostile   `CCSharedAttitude.Hostile` applied when he is found, which makes
#             him an enemy of THIS player and of nobody else. Does he then
#             challenge first and attack, or skip the warning and open fire?
#   ranged    a different vanilla record, default attitude. Separates "the
#             attitude decides it" from "this particular guard record does".
# OFF. The guard lab answered in one session, 2026-08-25, and its three entries
# are not kept: an entry that can be switched on by accident is a stranger in a
# shipped mod. `gen_poselab.py` rebuilds the whole lab from this one flag.
#
# WHAT IT ANSWERED: a community-placed guard perceives and fights exactly like a
# base-game one, and what he needs is a hostile ATTITUDE, not a particular
# record. Guards 1 and 3 differed only in their vanilla record and both stood
# there; guard 2 was guard 1 with `CCSharedAttitude.Hostile` applied, and he
# detected V on the ordinary ramp, slowly at distance and faster on approach, and
# went to combat. `backlog.md` 31.
GUARD_TEST = False
GUARD_POSITION = (298.250671, 1021.90662, 224.951675)
GUARD_YAW = -120.890587      # the vanilla spot's own yaw, kept with the position

# (entry, character record, what the encounter applies when it finds him)
GUARD_VARIANTS = [
    ('guard_default', 'Character.arasaka_guard2_melee1_baton_wa', 'none'),
    ('guard_hostile', 'Character.arasaka_guard2_melee1_baton_wa', 'hostile'),
    ('guard_ranged',
     'Character.sts_std_arr_12_security_guard1_ranged1_nue_ma', 'none'),
]

# ------------------------------------------------------------------ where
#
# HIS REAL SPOT, captured in game and already in `Gig01_Encounter.reds` as
# `CCGig01Places.Hoshino()`. It is the position the script has been spawning him
# at since 1.0, so the ground under it is proven by every playthrough rather than
# inferred from a survey (gotcha 67, which is what happens when it is inferred).
POSITION = (300.102, 1054.556, 229.928)
YAW = 140.8

# ------------------------------------------------------------------- the pose
#
# TWO POSES, and both paths come from the game's own data rather than from
# memory. A wrong workspot path is SILENT, because the actor simply never
# enters it, and this project has already lost a path that way (see the note in
# `questkit/scene.py`), so anything here has to be found in a shipped sector.
#
#   stand      what he has always done. It is the workspot the vanilla
#              investigation spots at THIS estate use, and the bench stood three
#              NPCs in it for sixteen runs.
#   sit_couch  he waits on the couch beside him. Six vanilla AI spots in the
#              cached sectors use it, and one of them was dumped node by node to
#              build the spot below.
#
# `sit_couch` needs the SEAT's position, which is not his standing position and
# cannot be guessed. Capture it in game (dev menu, CAPTURE HERE, standing where
# he should be sitting) and fill COUCH in. Until then, asking for the pose is
# refused rather than shipped at the wrong coordinates.
# SITTING, and the pose lab is what chose it. Playtest 2026-08-25: of four
# variants at the same seat, `common\chair\generic__sit_chair__sit_around__01`
# was the only one that took, "works great", and the three `master\` ones did
# not, at either height.
#
# **THE SHELF WAS THE ANSWER, NOT THE FURNITURE.** Every sit tried before this
# came from `master\`, and the standing idle that has worked throughout this
# project comes from `common\`. A `master_` workspot is evidently not something
# a community spot can hand an NPC directly. It is a chair pose on a couch and
# it reads correctly, so no couch-specific resource is needed.
POSE = 'sit_chair_common'

WORKSPOTS = {
    'stand': depot('base', 'workspots', 'common', 'ground',
                   'generic__stand_ground__look_at_products__03.workspot'),
    # THE ONE THAT WORKS, and the shelf is why: `common\`, not `master\`.
    # Three master variants were tried at the same seat and none of them took.
    'sit_chair_common': depot('base', 'workspots', 'common', 'chair',
                              'generic__sit_chair__sit_around__01.workspot'),
}
# The marking vanilla's own couch spots carry. Ours names its spot explicitly in
# `spotNodeRefs` so nothing has to search by marking, but it is what the shipped
# node has and matching it costs nothing.
MARKINGS = {'stand': [], 'sit_chair_common': ['sit_chair']}

# ===========================================================================
# THE SIT DOES NOT WORK, AND THE REASON IS WORTH MORE THAN THE POSE
#
# Playtest 2026-08-25, with POSE = 'sit_couch': he stood ON the couch cushion.
# Not sitting, and not at the floor position this file gave him either. The
# community put him at the spot and he was pushed up onto the seat.
#
# **A community places the BODY at its spot. It does not appear to put that body
# into the spot's WORKSPOT.** Sixteen bench runs never caught it because every
# one of them used a STANDING idle, and an NPC standing because his workspot
# never applied looks exactly like an NPC standing because it did.
#
# What DOES work is the quest-node route: `questUseWorkspotParamsV1` with a
# `workspotNode` naming one of our AI spots moved a scene actor into it, proved
# on the bench (`backlog.md` 29-ADDENDUM-7, run 13c) and now
# `Scene.add_world_workspot_node`. A pose therefore has to be driven, not
# declared.
#
# So POSE stays 'stand', which is what tested well: right place, right facing,
# speaks, mouth moves, killable, body stays. The couch would need the scene or
# the quest phase to put him there, and that is a bigger change than a pose.
#
# THE SEAT, captured in game 2026-08-24 (dev menu, CAPTURE HERE):
#
#     COUCH = { x = 299.021, y = 1055.990, z = 230.328, yaw = 151.1 }
#
# THE Z IS NOT THE CAPTURED ONE, and that is deliberate. CAPTURE HERE writes the
# PLAYER's position, and standing on a cushion puts his feet 0.40 m above the
# floor: 230.328 against Hoshino's own 229.928, which is a seat height exactly.
#
# A sit spot goes at FLOOR level and the animation puts the character onto the
# seat. Measured rather than assumed, on the vanilla couch spot this pose was
# taken from: `generic__sit_couch__sit_around__004` sits at the same height as
# the `poor_sofa_b_old` mesh origin beside it (0.006 m apart) and as the buckets,
# cardboard and bottles on the ground around it, all within 0.05 m. None of it is
# at cushion height.
#
# So: the captured x and y, and the floor z he already stands on. If he ends up
# hovering 40 cm over the couch, this note was wrong and the captured z is what
# it wants.
COUCH = (299.021, 1055.990, POSITION[2])
COUCH_YAW = 151.1

WORKSPOT = WORKSPOTS[POSE]


def entries():
    """Every entry this community carries, as questkit `Entry` objects.

    A list rather than one entry, because the pose lab needed a second one
    beside the first. `entryActiveOnStart` is not here: it is ignored (see the
    header) and the quest phase is what switches them.

    `spot_name` is given explicitly so the spot keeps the name it has shipped
    under. The name is hashed into the spot's id, so letting it be derived
    would rewrite a working file to no purpose.
    """
    out = [community.Entry(ENTRY, CHARACTER, APPEARANCE, spot_position(),
                           YAW if POSE == 'stand' else COUCH_YAW,
                           WORKSPOTS[POSE], MARKINGS[POSE],
                           spot_name='cc_g01_hoshino_spot')]
    if GUARD_TEST:
        for name, record, _apply in GUARD_VARIANTS:
            out.append(community.Entry(name, record, 'default', GUARD_POSITION,
                                       GUARD_YAW, WORKSPOTS['stand'],
                                       MARKINGS['stand'],
                                       spot_name='cc_g01_' + name))
    return out


def spot_position():
    """Where the spot node goes: the seat for a sit, his standing spot
    otherwise. A sit spot goes at FLOOR height and the animation puts him on the
    seat, which is why COUCH carries his own floor z rather than the captured
    cushion one."""
    if POSE == 'stand':
        return POSITION
    if COUCH is None:
        raise SystemExit(
            'POSE is %r but COUCH is None. The seat is not his standing '
            'position and cannot be guessed: capture it in game (dev menu, '
            'CAPTURE HERE) and fill COUCH in.' % POSE)
    return COUCH


def build():
    """His community. The recipe and the self-check are questkit.community."""
    return community.Community(SECTOR, entries(), spawnset=SPAWNSET_NAME,
                               phase=PHASE, period=PERIOD)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    com = build()
    for name, doc in com.files():
        path = os.path.join(OUT, name)
        with open(path, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(doc, fh, indent=2)
        print('wrote', path)

    print()
    print('community  %s' % com.community_ref)
    print('   id      %s' % com.community_id)
    for e in com.entries:
        print('   entry %-11s %-45s app %s' % (e.name, e.record, e.appearance))
        print('         at (%.3f, %.3f, %.3f) yaw %.1f'
              % (e.pos[0], e.pos[1], e.pos[2], e.yaw))
        print('         %s' % e.workspot)
    print('   scene   asks for %s' % SPAWNSET_NAME)
    print()
    print('add to the .archive.xl streaming blocks:')
    print('    - %s' % com.block_path())
