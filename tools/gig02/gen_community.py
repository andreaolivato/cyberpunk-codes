r"""Gig 02's community: every speaking NPC the player LOOKS at.

===========================================================================
WHY THIS EXISTS

`docs/scene-playbook.md` opens with the rule and this file is what makes it
true for this gig: an NPC with a line is a SCENE ACTOR, and a scene actor that
also has to stand in the world, be walked up to or be fought comes from a
community. The scene then ACQUIRES the body that is already there rather than
spawning a second one.

The gig shipped the other arrangement first: a voice-only actor a kilometre out
carrying the words and the lipsync, and a script spawn standing where the player
looks. Playtesting found the consequences one at a time and they are all the
same consequence - the merc's mouth did not move, Char's did not move, scanning
Char returned a passing stranger's name, the handover could not be animated, and
Char could not be seated. One architectural choice, five reports.

It was the right first pass: when it was made, not one position in this gig had
been walked, and a body at a guessed coordinate is a body in a wall. Nine
captures later that reason has expired. Every position below is one somebody
stood on, or one a body was demonstrably standing on when it was captured.

===========================================================================
THE RECIPE IS GOTCHA 66 AND IT IS NOT NEGOTIABLE

All six parts ship together and `questkit.community` implements them; gig 01's
`gen_community.py` carries the full account and sixteen bench runs are behind
it. What matters here:

  * two sectors, both AlwaysLoaded level 1: one for the registry, one for the
    area node and its AI spots
  * every ref rooted `$/mod/<sector>/#<name>`, never `$/03_night_city/`
  * `appearances` non-empty
  * one time period per phase

AND THE PART THE RECIPE DOES NOT COVER: `entryActiveOnStart: 0` IS IGNORED. A
mod's community spawns its entries on save load whatever that field says, so
THE QUEST PHASE is what keeps these people away until their leg opens, and puts
them away afterwards. See gen_questphase.py.

===========================================================================
WHO IS HERE AND WHO IS NOT

Here: everyone the player walks up to and looks at while they talk.

NOT here, and deliberately:

  * WAKAKO IN HER OFFICE WAS NOT HERE UNTIL 2026-09-05. The gig borrowed the
    game's own body and held her small talk off with `wakako_default_temp_off`;
    two playtests had her own hub over our lines anyway, because the fact only
    gates her scene's START and V is already in her doorway when it is set.
    She is in the list now, the Yoko way.
  * YOKO, for the same reason and it took a playtest to find out.
    `Character.wat_kab_netrunner_01` - captured off her in game - is a FIXED
    base-game NPC standing at that door, not ambient crowd. Putting her in this
    community shipped a second woman on the same spot: for one build that was
    Mama Welles, because her `$base` had been chosen back when she was a voice
    nobody would ever see.
    THAT IS SETTLED NOW. Her own vendor scene names the acquisition, so
    `gen_scenes.build_inn` takes the real body with entry
    `wat_kab_netrunner_01` and reference `#wat_kab_netrunner_01` - gig 01's
    Mama Welles route, with the values copied rather than guessed. Owning the
    actor is also what stops her vendor hub opening over ours.
  * WAKAKO AND YOKO ON THE PHONE. A holocall speaker is 2D and the body is in
    the holocall studio; nothing here applies.
  * THE FIVE STRANGERS OUTSIDE AFTERLIFE. The player overhears them and never
    looks at them, which is the test the rule states. They stay voice-only.
  * THE TYGER CLAWS on the staircase. They have no lines. They are a script
    spawn and staying that way, because what a community buys is a mouth.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from questkit import area, community                                # noqa: E402
from gig02_config import RAW, STAIR, TRASH, GROUP_POS, CHAR_POS     # noqa: E402,F401

# A depot path is BUILT, never typed: `\w`, `\a`, `\0` and `\t` are all eaten
# by something between here and the file. Gotcha 28.
B = chr(92)


def depot(*parts):
    return B.join(parts)


OUT = os.path.join(RAW, 'mod', 'worlds', '03_night_city', '_compiled', 'default')

SECTOR = 'cc_g02_cast'
REG_SECTOR = 'cc_g02_cast_reg'

# The string the SCENES ask for. gen_scenes imports it from here so the two
# cannot drift. Registered in `spawnSetNameToCommunityID`; the engine matches
# the string that was registered rather than resolving a world NodeRef, so the
# short form is right (gotcha 69).
SPAWNSET_NAME = '#cc_g02_cast_com'

PHASE = 'default'
PERIOD = 'Day'

# THE TWO POSES, BOTH GIG 01'S, BOTH SEEN TO WORK IN PLAY.
#
# `common\`, NEVER `master\`. That is the whole finding of gig 01's pose lab
# and it is gotcha 72: four sit variants were tried at one seat and the only one
# that took was the COMMON-shelf chair at floor height. A `master_` workspot is
# not something a community spot hands an NPC directly. Height turned out not to
# matter; the shelf did.
#
# A SIT SPOT GOES AT FLOOR HEIGHT and the animation puts the body on the seat.
# Do not give it the cushion's z - gig 01 carries the standing floor height for
# its couch for exactly this reason.
# STANDING AROUND, NOT SHOPPING. The first pose here was
# `generic__stand_ground__look_at_products__03`, and playtest 2026-09-04 showed
# what that means: a body bent double over a shelf that is not there. Eleven
# numbered stand-around idles ship under common/ground; one each so the queue
# does not move in unison.
def stand_around(n):
    return depot('base', 'workspots', 'common', 'ground',
                 'generic__stand_ground__stand_around__%02d.workspot' % n)


STAND = stand_around(1)

# WAKAKO'S DESK. The game's own `#ws_wakako_okada_default` spot: position,
# yaw and workspot, read off the parlor's sector on 2026-09-05. The anchor
# `#wakako_sm_okada_default` is 0.6 m from it and is the marker, not the seat.
WAKAKO_SPOT = ((-671.670, 822.375, 19.554), -81.2)
# NOT HER OWN q112 POSE (design call 2026-09-05): that one has her on the
# phone while V talks to her. A generic seated lean-back from the common
# shelf, placed 17 times by the game, the same chair spot.
# ...AND NOT THE LEAN-BACK EITHER (playtest 2026-09-05, screenshot: its hands
# fold on the lap and go through her skirt). A chair-and-table pose puts the
# arms on the desk in front of her, which is where a fixer's hands are; the
# game places this one at desks six times. If the desk is farther from her
# chair than the pose expects, the hands hover, and `lean_back__think__01`
# (hand at the chin, arm on the rest) is the next candidate.
WAKAKO_POSE = depot('base', 'workspots', 'common', 'chair_table',
                    'generic__sit_chair_table_lean_front__sit_around__02.workspot')

# THE DOORMAN'S POST: the game's own `#q112_ws_wakako_guard` spot, same source.
HUSCLE_SPOT = ((-665.363, 822.442, 19.534), -59.0)
HUSCLE_POSE = STAND
YOKO_POSE = depot('base', 'workspots', 'common', 'ground',
                  'corpo__stand_tablet__work__01.workspot')


def face(at, to):
    """The yaw at `at` that looks at `to`. Yaw is counter-clockwise from +Y
    seen from above, so a heading of theta faces (-sin, cos): atan2(-dx, dy).
    Same convention as scene.yaw_to_face_player, measured 2026-08-16. The
    first placement guessed +90/-90 and playtest 2026-09-04 showed every pair
    back to back, which is this function's reason to exist."""
    import math
    return math.degrees(math.atan2(-(to[0] - at[0]), to[1] - at[1]))
SIT = depot('base', 'workspots', 'common', 'chair',
            'generic__sit_chair__sit_around__01.workspot')

# CHAR LIES BACK, she does not sit up. A netrunner in that chair is reclined and
# jacked in, which is what the base game's own occupant is doing and what
# playtesting asked for.
#
# THE OBVIOUS RESOURCE IS UNUSABLE. `synced_npc_netrunner_chair_sit_connected`
# is the jacked-in pose, and it lives under `gameplay\workspots\devices\` and
# is SYNCED to the chair device. A community spot cannot drive that: gig 01
# established that even a `master\` workspot is not something a community spot
# hands an NPC, and a device-synced one is further away still.
#
# So this is the `common\` shelf's own reclined-in-a-netrunner-chair pose, which
# is the right shelf and the right silhouette. IT IS NAMED FOR A CORPSE, and
# that is the one thing to judge by eye: if it reads as limp rather than as
# somebody working, the sit above is the fallback.
# THE GAME'S OWN OCCUPANT'S POSE (2026-09-05): the seat spot the game shipped
# in this chair (exterior_-10_15_0_1, instance 151, yaw 185 = Char's own) plays
# this workspot, reclined and jacked in and alive. The `common\chair` dead pose
# it replaces read as asleep in play (screenshot).
RECLINE = depot('base', 'workspots', 'netrunner_den', 'netrunner_chair',
                'generic__lie_netrunner_chair__netrun__01.workspot')

# NO MARKINGS ON OUR SPOTS. `sit_chair` is the marking vanilla's seat spots
# carry, and it was copied onto Char's chair spot "because matching the shipped
# node costs nothing". It cost the chair: a marking is what the CROWD SYSTEM
# searches by, so our spot was a free seat to it, a stranger sat down in it
# before Char's entry was switched on, and Char stood beside her own chair
# (playtest 2026-09-05, after the vanilla seat spot had been deleted and the
# body came back anyway). Our entries name their spots; nothing searches.
SIT_MARKINGS = []

# ---------------------------------------------------------------- the cast
#
# EVERY POSITION IS ONE A BODY HAS BEEN SEEN ON. Three kinds, and the
# difference matters when reading the yaws:
#
#   walked   the player stood there and pressed CAPTURE WHERE I STAND. The yaw
#            is the PLAYER'S facing, so the NPC wants that plus 180 - he is
#            being looked at, not looking the same way.
#   looked   the crosshair was on a body and the capture read that body's own
#            transform. The yaw is already the NPC's, and is used as it is.
#
# A looked-at position is worth as much as a walked one for this purpose:
# something was standing on it, so it is ground an NPC can stand on.
MERC_POS = (-1470.163, 1044.159, 22.722)
# HE FACES HIS LISTENERS, 2026-09-04: two bodies a step in front of him, and
# he faces the middle of the pair. Playtest: 283 degrees had him talking to
# nobody.
#
# THE TWO SIDES ARE SWAPPED, 2026-09-07 (playtest). He used to hold the
# captured post with the pair on the -X side, which is the side the player
# walks in from: the player met the merc's back, and the two listeners had
# their faces to him. Now the LISTENERS hold the post and he stands where they
# were, so the player comes up behind the listeners and the man doing the
# talking is the one facing them. He faces +X, towards the pair and the bins
# they are gathered by.
#
# BOTH SPOTS ARE KNOWN GROUND. The post is a capture, and the -X spot is where
# two bodies have been standing since 2026-09-04, so neither side of the swap
# is a new guess about what an NPC can stand on.
MERC_STAND = (MERC_POS[0] - 1.3, MERC_POS[1], MERC_POS[2])
_G3 = [(MERC_POS[0], MERC_POS[1] - 0.75, MERC_POS[2]),
       (MERC_POS[0], MERC_POS[1] + 0.75, MERC_POS[2])]
_G3C = (MERC_POS[0], MERC_POS[1])
MERC_YAW = face(MERC_STAND, _G3C)

_G1 = [(GROUP_POS['group1'][0] - 0.7, GROUP_POS['group1'][1] + 0.9,
        GROUP_POS['group1'][2]),
       (GROUP_POS['group1'][0] + 0.7, GROUP_POS['group1'][1] + 0.9,
        GROUP_POS['group1'][2])]
_G1C = (GROUP_POS['group1'][0], GROUP_POS['group1'][1] + 0.9)
_G2 = [(GROUP_POS['group2'][0] - 0.8, GROUP_POS['group2'][1] + 0.9,
        GROUP_POS['group2'][2]),
       (GROUP_POS['group2'][0] + 0.8, GROUP_POS['group2'][1] + 0.9,
        GROUP_POS['group2'][2]),
       (GROUP_POS['group2'][0], GROUP_POS['group2'][1] + 1.7,
        GROUP_POS['group2'][2])]
_G2C = (GROUP_POS['group2'][0], GROUP_POS['group2'][1] + 1.2)

CAST = [
    # THE MERC, with the third group outside Afterlife.
    # Plain stand-around idles for the three (playtest 2026-09-05: 06 and 08
    # hold the arms out as if around something that is not there).
    ('merc', 'Character.cc_g02_merc', MERC_STAND, MERC_YAW, stand_around(1)),
    # HIS LISTENERS (2026-09-04): a man and a woman a step in front of him.
    ('queue_f', 'Character.cc_g02_queue_f', _G3[0], face(_G3[0], MERC_STAND[:2]),
     stand_around(2)),
    ('queue_g', 'Character.cc_g02_queue_g', _G3[1], face(_G3[1], MERC_STAND[:2]),
     stand_around(3)),


    # THE FIVE STRANGERS, 2026-09-03: two at group 1's captured spot, three
    # at group 2's, a step either side of the spot. Each faces the middle of
    # its own group (face(), 2026-09-04).
    ('queue_a', 'Character.cc_g02_queue_a', _G1[0], face(_G1[0], _G1C),
     stand_around(1)),
    ('queue_b', 'Character.cc_g02_queue_b', _G1[1], face(_G1[1], _G1C),
     stand_around(2)),
    ('queue_c', 'Character.cc_g02_queue_c', _G2[0], face(_G2[0], _G2C),
     stand_around(3)),
    ('queue_d', 'Character.cc_g02_queue_d', _G2[1], face(_G2[1], _G2C),
     stand_around(4)),
    ('queue_e', 'Character.cc_g02_queue_e', _G2[2], face(_G2[2], _G2C),
     stand_around(5)),

    # CHAR, IN THE NETRUNNER'S CHAIR at the Dewdrop Inn, not beside it.
    #
    # The XY is the chair's own, taken by putting the crosshair on the woman
    # sitting in it; the yaw is hers, so she faces the way the seat does. The Z
    # is FLOOR height, which is what a sit spot wants - and the two captures
    # agree on 20.487, the seated body and the player standing beside it, which
    # is what tells us that number is the floor rather than the cushion.
    ('char', 'Character.cc_g02_char',
     (-1184.427, 2045.153, 20.487), -175.0, RECLINE),

    # IDEKA IS GONE, 2026-09-03. She was an invented attendant with three
    # lines, and the camera-log beat she existed for was folded into the relay's
    # own note. A body with nothing to say is a body that should not be shipped.


    # HUSCLE IS NEVER SWITCHED ON (design call 2026-09-05: "the doorman is a
    # confusion, remove that completely"). The game's own doorman keeps his
    # post. The entry stays in this list only because a save keeps each
    # entry's state by its place in it; the phase deactivates it at start
    # and nothing activates it.
    ('huscle', 'Character.cc_g02_huscle',
     HUSCLE_SPOT[0], HUSCLE_SPOT[1], HUSCLE_POSE),


    # TOJI, at the bottom of the Japantown staircase. Walked.
    ('toji', 'Character.cc_g02_toji',
     (-381.087, 1233.990, 23.428), -158.4 + 180.0, STAND),

    # WAKAKO, OURS FOR THE PARLOR LEG (2026-09-05, playtest screenshot: her
    # own "Tell me about Westbrook." hub over our office lines, again, and
    # holding `wakako_default_temp_off` did not close a hub that was already
    # open). Same shape as Yoko: the game's entry (`#wakako`, entry `wakako`,
    # phase `default`, read off the community registry) is switched off for
    # the leg, this body sits on her own desk spot in her own pose, and the
    # office scene acquires this one. Spot and pose read off the parlor's
    # sector; see WAKAKO_SPOT.
    ('wakako', 'Character.cc_g02_wakako',
     WAKAKO_SPOT[0], WAKAKO_SPOT[1], WAKAKO_POSE),

    # YOKO, OURS AGAIN (2026-09-05). LAST IN THE LIST ON PURPOSE: a save keeps
    # each entry's state by its place in this list, and a new entry inserted
    # before Char left a mid-leg save with nobody at the Inn (playtest). Her vendor scene offers its hub to anyone
    # in reach and the game merges hubs on one actor, so a scene that acquires
    # the vanilla body still gets her three vendor lines over ours (playtest
    # screenshot). The vanilla entry (`#wat_kab_netrunner_01`) is switched off
    # for the leg and disposed if it lingers, and this body stands on her own
    # idle spot, in her own pose, both read off exterior_-10_15_0_1:
    # `wat_kab_netrunner_01_ws_idle` at this position, yaw -241.1,
    # corpo__stand_tablet__work__01.
    ('yoko', 'Character.cc_g02_yoko',
     (-1177.83, 2039.69, 20.15), -241.1, YOKO_POSE),

]


# THE FACE IS THE ENTRY'S, NOT THE RECORD'S. The game's own entry for the
# Kabuki netrunner names `service__vendor_wa_vendor_asian_02` (read off the
# community registry in always_loaded_1, 2026-09-05); a record's `default`
# put a different woman on Yoko's spot in play.
# THE SAME RULE FOR EVERY FACE THE PLAYER SEES TWICE (2026-09-05). Char is in
# the chair and then on V's phone, so both bodies name one appearance out of
# the game's own placements of `SlackerFemale` (`helper_day` in
# always_loaded_1 pins this one). The doorman's is the game's own entry for
# him, and Wakako's is the one her holocall entry names. Each is ALSO on the
# Character record (characters.yaml) and on the studio actor, so nothing can
# roll another.
APPEARANCE = {
    'yoko': 'service__vendor_wa_vendor_asian_02',
    'char': 'slacker_wa_slacker_wa_03',
    'huscle': 'gang__tyger_mb_ozeki__lvl3_02',
    'wakako': 'wakako_okada_default',
    'toji': 'gang__tyger_ma_gangster__lvl3_04',
    # The masked male Wraith (2026-09-06), pinned here and on the record.
    'merc': 'gang__wraith_ma_grunt__lvl2_02',
    # THE QUEUE KEEPS ITS FACES (playtest 2026-09-06: the seven bodies outside
    # Afterlife changed from one session to the next). Five are the faces
    # captured in play with the look-at probe; queue_f and queue_g were not
    # captured and take two more from the same crowd entity's list
    # (crowd__districts_ma.app, read off disk).
    'queue_a': 'crowd__districts_ma_rich_07',
    'queue_b': 'crowd__districts_ma_rich_09',
    'queue_c': 'crowd__districts_ma_rich_04',
    'queue_d': 'crowd__districts_wa_casual_14',
    'queue_e': 'crowd__districts_ma_teen_04',
    'queue_f': 'crowd__districts_ma_casual_02',
    'queue_g': 'crowd__districts_ma_rich_02',
}


def entries():
    return [community.Entry(name, record, APPEARANCE.get(name, 'default'), pos, yaw, pose,
                            SIT_MARKINGS if pose in (SIT, RECLINE) else [],
                            spot_name='cc_g02_' + name + '_spot')
            for name, record, pos, yaw, pose in CAST]


# NO CROWD AT THE DOOR WHILE THE GIG OWNS IT. The people outside Afterlife are
# the crowd SYSTEM (they change on every load, and switching the two vanilla
# communities that own spots there off changed nothing, 2026-09-04), and the
# vanilla way to clear the crowd system from a place is a crowd null area a
# quest enables. A 28 m by 26 m box on the door and the three listening posts,
# 4 m high, at street level. The graph turns it on when the gig is accepted
# and off once the merc leg is over.
CROWD_NULL_REF = community.Community.ref(SECTOR, 'cc_g02_crowd_null')

# THE HIT AREA (backlog 39, third test 2026-09-06): a `worldTriggerAreaNode`
# as an extra node of this always-loaded sector. ArchiveXL's journal
# extension draws a quest pin's area only when the pin's node instance is a
# `worldAreaShapeNode` (ResolveMappinVolume in its Extension.cpp): the second
# test's security-area DEVICE gave the pin a position and no area, and the
# first test's trigger node sat in the gig's Exterior sector with a shard
# case's instance flags and was never found. This one takes the shape of the
# crowd-null area beside it, which instantiates here, and the flags every
# vanilla trigger area instance carries: Uk11 65024 and Uk12 1.
import hit_area                                                     # noqa: E402
HIT_AREA_REF = community.Community.ref(SECTOR, 'cc_g02_hit_area')
assert HIT_AREA_REF == hit_area.AREA_REF, (HIT_AREA_REF, hit_area.AREA_REF)


def hit_area_node():
    pos = hit_area.position()
    local = [(x - pos[0], y - pos[1]) for x, y in hit_area.corners()]
    node = {
        '$type': 'worldTriggerAreaNode',
        'color': {'$type': 'Color', 'Alpha': 0, 'Blue': 0, 'Green': 0, 'Red': 0},
        'debugName': community.cname('{cc_g02_hit_area}'),
        'isHostOnly': 0,
        'isVisibleInGame': 1,
        'notifiers': [{'HandleId': '1', 'Data': {
            '$type': 'questTriggerNotifier_Quest', 'excludeChannels': 0,
            'includeChannels': 'TC_Default', 'isEnabled': 1}}],
        'outline': area.outline(local, hit_area.AREA_HEIGHT, handle_id='2'),
        'proxyScale': None,
        'sourcePrefabHash': '0',
        'tag': 'None',
        'tagExt': 'None',
    }
    return node, pos


_HIT_NODE, _HIT_POS = hit_area_node()
# MaxStreamingDistance, UkFloat1, Uk10, Uk11, Uk12: the Japantown trigger area
# the outline format was read from (`{cs_tr_vo}`, exterior_-10_18_0_0).
HIT_AREA_NODE = (_HIT_NODE, _HIT_POS, HIT_AREA_REF, (2760.11133, 90.03862, 1056, 65024, 1))
CROWD_NULL_POS = (-1470.2, 1046.0, 22.2)
CROWD_NULL = (community.crowd_null_area_node(
                  'cc_g02_crowd_null',
                  [(-15, -13), (13, -13), (13, 13), (-15, 13)], height=4.0),
              CROWD_NULL_POS, CROWD_NULL_REF,
              (community.WB['maxdist'], community.WB['ukfloat'],
               community.WB['uk10'], community.WB['uk11']))


# THE KNEEL IS A SPOT, NOT A SCENE POSE, 2026-09-04. Two playtests of the
# scene-side workspot (played where he stands) read as a glitch going down
# and getting up. This is an AI spot node of our own with the kneeling-afraid
# workspot, on his own post, and the begging scene sends him to it with the
# AI's walk-and-enter (scene.add_world_workspot_node, walk=True), which is how
# every NPC in the city gets into a pose. He faces the way his post faces.
# WOUNDED, NOT SCARED (playtest 2026-09-04, third pass): sitting on the
# ground, one hand on the knee, checking a wound. Both rigs, six entry and six
# exit animations, twelve idle clips; pulled from memoryresident_1_general by
# hash and read. The kneeling-afraid pose it replaces read as fear.
KNEEL = depot('base', 'workspots', 'archetype', 'homeless', 'common', 'ground',
              'homeless__sit__wounded_creepy_leg__01.workspot')
MERC_KNEEL_REF = community.Community.ref(SECTOR, 'cc_g02_merc_kneel_spot')
MERC_KNEEL = (community.Community.ai_spot_node(None, 'cc_g02_merc_kneel_spot',
                                               KNEEL, []),
              MERC_STAND, MERC_KNEEL_REF,
              (community.WB['maxdist'], community.WB['ukfloat'],
               community.WB['uk10'], community.WB['uk11']),
              MERC_YAW)


# THE POSE LAB'S SPOTS, 2026-09-04: one AI spot per candidate pose, all on
# the merc's post, all facing his way. The CET menu spawns a body there and
# sends it into each with the AI's own use-workspot command. Keys are what the
# menu shows; refs are `cc_g02_lab_<key>_spot`.
LAB_POSES = [
    ('sit_wounded',   ('archetype', 'homeless', 'common', 'ground',
                       'homeless__sit__wounded_creepy_leg__01.workspot')),
    ('kneel_afraid',  ('common', 'ground', 'generic__kneel_ground_lean_front__afraid__01.workspot')),
    ('kneel_cover',   ('common', 'ground', 'generic__kneel_ground__cover__01.workspot')),
    ('kneel_cry',     ('common', 'ground', 'generic__kneel_ground__cry__01.workspot')),
    ('sit_scared',    ('common', 'ground', 'generic__sit_ground_lean_front__scared__01.workspot')),
    ('sit_wall_hurt', ('common', 'ground', 'generic__sit_ground_wall_lean_back__wounded__01.workspot')),
    ('hands_up',      ('common', 'ground', 'generic__stand_ground__hands_up__03.workspot')),
    ('kneel_inspect', ('common', 'ground', 'generic__kneel_ground__inspect__01.workspot')),
    ('stand',         ('common', 'ground', 'generic__stand_ground__stand_around__01.workspot')),
    # ON THE FLOOR, ALIVE (2026-09-05): what a body could hold after the
    # Defeated fall, which the lab found reads well but then looks dead.
    ('lie_knockdown', ('common', 'ground', 'generic__lie_ground_lean_back__knockdown__01.workspot')),
    ('lie_knock_r',   ('common', 'ground', 'generic__lie_ground_lean_right__knockdown__01.workspot')),
    ('lie_uncons',    ('common', 'ground', 'generic__lie_ground_lean_back__unconscious__01.workspot')),
    ('lie_cover',     ('common', 'ground', 'generic__lie__cover__01.workspot')),
    ('lie_wounded',   ('quest', 'main_quests', 'part1', 'q108', 'q108_14_rogue',
                       'dirtboy__lie_ground__wounded__01.workspot')),
]
# THE LAB MOVED to the "spawnhere" capture of 2026-09-05, 16 m from the post,
# so the spots are where the body is spawned.
LAB_POS = (-1472.817, 1028.142, 22.690)
LAB_YAW = -7.9
LAB_SPOTS = []
for _key, _parts in LAB_POSES:
    _ref = community.Community.ref(SECTOR, 'cc_g02_lab_%s_spot' % _key)
    LAB_SPOTS.append((community.Community.ai_spot_node(
                          None, 'cc_g02_lab_%s_spot' % _key,
                          depot('base', 'workspots', *_parts), []),
                      LAB_POS, _ref,
                      (community.WB['maxdist'], community.WB['ukfloat'],
                       community.WB['uk10'], community.WB['uk11']),
                      LAB_YAW))


def build():
    return community.Community(SECTOR, entries(), spawnset=SPAWNSET_NAME,
                               phase=PHASE, period=PERIOD,
                               extra=[CROWD_NULL, MERC_KNEEL, HIT_AREA_NODE] + LAB_SPOTS)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    com = build()
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
    print('   scenes ask for %s' % SPAWNSET_NAME)
