r"""The North Oak estate detail: one guard at each authored post.

===========================================================================
WHAT THIS REPLACES

`Gig01_Encounter.reds` used to spawn the estate guards through
`DynamicEntitySystem`: six anchor points, twenty-five men, each one scattered
onto whatever walkable ground the navmesh offered within a couple of metres of
his anchor. That is where the huddle came from. Three of the office squads at
the industrial park land within fifteen metres of each other for exactly the
same reason, and it is not a bug in the query: it is what happens when a
navmesh query stands in for a level designer. Nobody had ever said where a
guard should stand.

Nobody could, either, because the game has no authored guard posts here. A
search of the cached sectors for `worldAISpotNode` within 120 m of the estate
found five, all 50 to 90 m away, all belonging to another quest's infiltration
setup (`backlog.md` 31).

THE POSTS BELOW WERE WALKED AND CAPTURED IN GAME, playtest 2026-08-25. Somebody
stood on each spot, faced the way the guard should face, and pressed CAPTURE
HERE in the dev menu. Thirty of them, from the front gate to the roof, of which
twenty-nine ship: `roof01` landed 1.0 m from a sniper the base game already
stands there, and the roof is covered by `roof02` at the other end. That is the
input a survey cannot produce: sightlines, cover, who watches the gate and who
watches the yard are decisions, not measurements (gotcha 67 is what happens when
ground is inferred instead).

===========================================================================
WHY A COMMUNITY RATHER THAN A BETTER SPAWN

A hostile attitude is what makes a guard perceive and fight, and a
script-spawned guard already gets one, so behaviour alone would not have
justified this (gotcha 74, `backlog.md` 31). Three things do:

  - A community entry has a POST and a FACING. A spawn has an anchor and a
    navmesh query.
  - A community can be alerted. The trespass warning - "you shouldn't be here",
    the call-out, the walk over, and only then a fight, comes from a SECURITY
    AREA linked to a community by a `CommunityProxyPS` device connection. There
    is no way to link one to a set of script-spawned bodies.
  - The bodies persist properly. A script spawn is re-run per session and its
    dead do not stay dead across a reload.

===========================================================================
WHAT A SECOND COMMUNITY COSTS, STATED PLAINLY

Community state PERSISTS IN SAVES, so this puts twenty-nine entries into the save
of every player who installs the mod. That is the price of the three things above
and it is why the quest phase has to switch the whole community off as its first
act and off again at the end: an active entry holding a dead man returns him
alive on load (bench run 14, and it is the same reason Hoshino's entry is
switched off after the malware upload rather than left on).

THE GUARDS ARE THEIR OWN COMMUNITY, not more entries in Hoshino's. Two
reasons, and the second is the one that matters:

  - A whole-community action switches them all in one quest node. Naming
    entries one at a time would be one node each per beat, and `actions` holding
    more than one entry is a shape this project has not read off a working
    example.
  - The security area's `CommunityProxyPS` points at ONE community. Pointing it
    at Hoshino's would rope the man V is there to talk to into the alert system
    he is supposed to be standing calmly inside.

===========================================================================
THE RECIPE IS `questkit/community.py`, which is gotcha 66, and it is shared with
Hoshino's community unchanged. Everything specific to the estate is in this
file: who stands where, facing which way, carrying what.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import guard_site                                                   # noqa: E402
from gig01_config import RAW, REPO                                  # noqa: E402

OUT = os.path.join(RAW, 'mod', 'worlds', '03_night_city', '_compiled', 'default')

# ONE name, and it is parts 1 and 4 of the recipe.
SECTOR = 'cc_g01_estate'

ENCOUNTER = os.path.join(REPO, 'mods', 'gig-01-negative-balance', 'source',
                         'scripts', 'Gig01_Encounter.reds')
CACHE = os.path.join(REPO, 'tools', '_anchor_cache', 'base', 'worlds',
                     '03_night_city', '_compiled', 'default')

# ---------------------------------------------------------------- the records
#
# THE SAME FIVE the encounter has always used for this site, deliberately. The
# estate detail is meant to read as an elite Arasaka detail and the industrial
# park as ordinary security, and that difference is carried entirely by which
# records each site uses. Changing the roster here while changing the placement
# would have made a playtest unable to say which of the two it was reacting to.
SEC = 'Character.nok_security_security2_ranged2_ajax_wa'
SHOTGUN = 'Character.arasaka_agent_fshotgun2_tactician_wa_rare'
RANGER = 'Character.arasaka_ranger1_ranged2_shingen_ma'
SNIPER = 'Character.nok_arasaka_fast_sniper_long_range_m_medium'
NETRUNNER = 'Character.arasaka_netrunner_netrunner2_yukimura_ma_rare'

# ------------------------------------------------------------------ the posts
#
# CAPTURED IN GAME, playtest 2026-08-25, `captured_positions.txt`. The position
# is where the player stood and the yaw is the way he was facing, both written
# by the dev menu's CAPTURE HERE.
#
# THE YAW IS THE RAW CAPTURE and is not corrected. That is measured rather than
# assumed: Hoshino's seat was captured the same way at yaw 151.1, shipped
# uncorrected, and he faces the right way in game. The 90-degree correction this
# project once needed belonged to the SCRIPT spawn path, which is a different
# consumer of the same number (gotcha 70).
#
# Five of the captures are dropped on the tester's own instruction: `inner18`,
# `inner19` and `inner20` were superseded by the `1stfloor` walk that followed
# them, and `1stfloor01` sits 2.7 m from the couch Hoshino waits on. They are
# not listed here at all rather than commented out, because a commented-out post
# is one somebody switches back on without knowing why it went.
#
# The names are the tester's, so a post in game can be found in the capture file
# by name. The four `1stfloor0N` are `floorN` here: a CName may begin with a
# digit but a redscript identifier may not, and these names are read back in the
# dev panel.
#
# (name, record, x, y, z, yaw)
POSTS = [
    # --- the front gate, outside. The first thing V meets on the signposted
    # route in, and the three of them cover the gate itself.
    ('gate01', SEC, 387.567, 1163.006, 220.644, -49.8),
    ('gate02', SEC, 382.532, 1163.307, 220.735, -36.5),
    ('gate03', SHOTGUN, 377.486, 1164.584, 220.800, -36.5),

    # --- just inside the gate, facing back at it. `inner02` and `inner03` look
    # the other way, which is what makes this a post rather than a firing line.
    ('inner01', SEC, 375.179, 1160.274, 220.932, -119.0),
    ('inner02', RANGER, 383.786, 1157.866, 220.932, 61.1),
    ('inner03', SEC, 380.556, 1161.031, 220.930, 151.2),

    # --- the grounds and the drive down to the house. This is the stretch the
    # gig's six waypoints cross, and it used to be two anchors' worth of
    # scatter.
    ('inner04', RANGER, 378.296, 1123.063, 220.907, -19.0),
    ('inner05', SEC, 353.762, 1140.353, 220.953, -54.8),
    ('inner06', SEC, 344.721, 1155.510, 220.907, -85.7),
    ('inner07', SHOTGUN, 331.399, 1119.022, 220.663, -37.5),
    ('inner08', RANGER, 328.548, 1118.027, 221.082, 166.5),
    ('inner09', SEC, 311.923, 1114.444, 221.942, -43.6),
    ('inner10', RANGER, 361.589, 1092.489, 221.142, -43.1),
    ('inner11', SHOTGUN, 366.505, 1070.249, 221.956, -9.1),

    # --- the terrace level, 225 m, which is where the house starts.
    ('inner12', RANGER, 352.150, 1052.185, 225.956, -19.0),
    ('inner13', SHOTGUN, 333.290, 1022.528, 225.918, 1.1),
    ('inner14', SEC, 323.799, 1069.865, 225.933, -32.4),
    ('inner15', RANGER, 328.117, 1067.117, 225.878, -47.0),
    ('inner16', SEC, 298.410, 1081.607, 225.933, -32.2),
    ('inner17', SHOTGUN, 310.949, 1050.816, 225.942, -33.9),

    # --- the first floor, 229.9 m, the same level Hoshino waits on. The
    # netrunner is here rather than outside: he is the one who should be near
    # the terminals.
    ('floor02', SHOTGUN, 313.777, 1047.313, 229.928, -16.6),
    ('floor03', RANGER, 297.436, 1035.435, 229.928, -31.0),
    ('floor04', NETRUNNER, 312.758, 1044.063, 229.918, 8.5),
    ('floor05', SHOTGUN, 311.356, 1027.472, 229.994, 60.9),

    # --- the roof, 233.9 m. A post the old spawn could not have produced at
    # all: a navmesh query around a ground anchor never puts anybody up there.
    #
    # ONE SNIPER, NOT TWO. `roof01` was captured at (323.149, 1040.853, 233.916)
    # and is gone, because the base game already stands a sniper 1.0 m from it:
    # captured in game 2026-08-25 at (322.223, 1041.312, 233.868), record
    # `nok_arasaka_fast_sniper_long_range_m_hard` against our `_medium`. Two sets
    # of people picked the same good spot twenty-six years apart, and ours would
    # have stood inside theirs.
    #
    # Dropped rather than moved, because moving it means guessing at ground
    # nobody has stood on (gotcha 67), and the roof does not need a third body:
    # theirs covers that end and `roof02` covers the other, 24 m away.
    ('roof02', SNIPER, 298.541, 1049.397, 233.868, 1.5),

    # --- the office end, 224.9 m, where the malware goes in.
    ('office01', RANGER, 296.481, 1032.695, 225.968, -30.8),
    ('office02', NETRUNNER, 288.087, 1019.276, 224.918, -31.8),
    ('office03', SHOTGUN, 285.228, 1027.040, 224.928, -88.5),
    ('office04', RANGER, 298.884, 1018.012, 224.918, 29.0),
]


# ------------------------------------------------ WHO STANDS DOWN WHEN EASED
#
# THE ROSTER ABOVE IS THE GIG AS SHIPPED. These eleven are switched off again,
# one quest node each, when the player runs a mod that makes every fight in
# the game harder (`Gig01_Companions.reds` says which mods, and
# `gen_questphase.thin_detail` is the node shape). Eighteen stand then.
#
# The count per area is the design call of 2026-09-20, after two playtests
# (five per site, then three here) were judged too light a cut; the roster in
# `gen_compound_guards.py` has the player feedback both lists answer. Which
# man goes within an area follows two rules: the one standing on the
# objective goes first, then one of any pair standing within a few metres.
# The estate has two objectives, the couch Hoshino waits on and the terminal
# the malware goes into, and distances below are to `CCGig01Places.Hoshino()`
# and `EstateTerminal()`.
#
#   area                          shipped  eased   who goes
#   front gate and just inside       6       4     inner03 (3.0 m from gate02,
#                                                  4.5 from inner02, 4.7 from
#                                                  gate03), gate02 (5.0 m from
#                                                  gate01)
#   grounds and the drive            8       6     inner09 and inner11, the two
#                                                  of the eight nearest the
#                                                  house (62 and 69 m from the
#                                                  couch)
#   terrace level                    6       5     inner17, 12 m below the couch
#                                                  and the last post on the way
#                                                  up
#   first floor, Hoshino's           4       1     floor02, floor03, floor04;
#                                                  floor05 stays, the furthest
#                                                  from the couch at 29 m
#   roof                             1       1     nobody; a sniper is a threat
#                                                  the player can see coming
#   office end                       4       1     office03 (3.4 m from the
#                                                  terminal, shotgun), office02
#                                                  (5.5 m, netrunner), office01;
#                                                  office04 stays at 15 m
#
# Every name here has to be a post in POSTS. `guard_site.check_stand_down`
# refuses to write otherwise, because a quest node naming an entry that does
# not exist crashes the game without a message (gotcha 73).
STAND_DOWN = [
    'inner03', 'gate02',
    'inner09', 'inner11',
    'inner17',
    'floor02', 'floor03', 'floor04',
    'office01', 'office02', 'office03',
]


# ------------------------------------------------------- WHO IS DOING WHAT
#
# A handful, and DISCIPLINED ONES ONLY. This is an elite Arasaka detail at a
# private residence, so nobody here is smoking or on the phone: the difference
# between this site and the industrial park is the whole reason the two feel
# different, and it used to be carried by the character records alone.
#
# A workspot is what a man is DOING and nothing else. It is not the attitude and
# not the senses, so none of this changes how any of them fight.
IDLES = {
    'inner04': 'wait',
    'inner09': 'think',
    'inner14': 'stand_around',
    'inner16': 'wait',
    'floor03': 'think',
    'office01': 'stand_around',
    'gate02': 'wait',
}

# NOBODY WALKS HERE, and nobody walks at the industrial park either. Four beats
# were tried there on 2026-08-25 and they did not walk; see the note in
# `gen_compound_guards.py` for what was tried and why it is not chased.


def build():
    return guard_site.build(SECTOR, POSTS, IDLES)


if __name__ == '__main__':
    guard_site.write(OUT, SECTOR, POSTS, ENCOUNTER, 'EstateEntries',
                     cache_dir=CACHE, idles=IDLES,
                     keep_clear=((299.021, 1055.990, 229.928), 3.0,
                                 'the couch Hoshino waits on'),
                     stand_down=STAND_DOWN)
