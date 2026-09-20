r"""The Arasaka Industrial Park detail: one guard at each authored post.

The compound half of what `gen_estate_guards.py` did for the residence, and the
second half of `backlog.md` 31. The recipe is `questkit/community.py` (gotcha
66) and the checks are `guard_site.py`; this file is a roster and nothing else.

===========================================================================
WHAT THIS REPLACES

Five anchors and twenty men, each scattered onto whatever ground the navmesh
offered within a couple of metres. THREE OF THE FIVE ANCHORS SIT WITHIN FIFTEEN
METRES OF EACH OTHER, which is the huddle in its clearest form: `OfficeEntry`,
`OfficeGuardPost` and `TerminalRoomEntry` are the same corner of the same
building, so a third of the site's guards were asked for in one place and the
rest of it had nobody at all.

The posts below were walked and captured in game, playtest 2026-08-25, one
CAPTURE HERE per post. Forty-seven captures, forty-six kept and thirty shipped.
The first `gate01` was recaptured with a different facing and the second is the
one that ships; the rest of the difference is the stealth thin below.

===========================================================================
WHAT THE WALK FOUND THAT THE OLD PLACEMENT COULD NOT

**Height.** Sixteen of the thirty are off the ground floor: the deck at 14.6 m,
the interior floors at 8.6 and 9.6, and the office level at 14.6. A navmesh
query around a ground anchor never produced one of those, so the whole vertical
half of this site was unguarded.

**The yard.** Twelve `inner` posts cover the ground between the two gates and
the building, which the five anchors skipped entirely.

**A second gate.** `gate2` is a way in the old placement did not know about.

===========================================================================
THIRTY, THINNED FROM FORTY-SIX FOR STEALTH

The site had twenty before the walk and forty-six after it, and playtest found
the obvious consequence: *"too many guards inside the compound, basically
impossible to run stealth"*. Twenty of the forty-six were inside the building.

TWELVE WERE DROPPED, and which twelve was not a taste decision. The captures are
a walk, so posts came in pairs two or three metres apart: `inside09` and
`inside10` stood 2.4 m from each other, `gate01` and `gate03` 1.9 m. One of each
pair adds a body and no coverage. So the thinning removed whichever post stood
closest to another, over and over, with a floor per area so nothing was stripped
bare. The closest two posts are now 3.8 m apart rather than 1.9.

The interior took most of it, 20 down to 12, because that is where stealth was
impossible. The yard, the gates and the office end are barely touched.

The thin ran in two passes. A blanket one took forty-six to thirty-four, and
four further playtests took thirty-four to thirty: four named removals and three
turns, each from a mark taken in game where the problem happened. The notes
against `inside06` and `inside08` below are what those marks found.

It is still more than the twenty the old placement had, and it still covers the
second gate, the deck and three interior levels, which that placement could not
reach at all.

It is also a real change to how hard the gig is, and it puts thirty entries into
every player's save. Both are stated here rather than discovered later.
"""
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import guard_site                                                   # noqa: E402
from questkit import community                                      # noqa: E402
from gig01_config import RAW, REPO                                  # noqa: E402

OUT = os.path.join(RAW, 'mod', 'worlds', '03_night_city', '_compiled', 'default')
SECTOR = 'cc_g01_compound'

ENCOUNTER = os.path.join(REPO, 'mods', 'gig-01-negative-balance', 'source',
                         'scripts', 'Gig01_Encounter.reds')
CACHE = os.path.join(REPO, 'tools', '_anchor_cache', 'base', 'worlds',
                     '03_night_city', '_compiled', 'default')

# ---------------------------------------------------------------- the records
#
# ORDINARY SECURITY, NOT THE ELITE DETAIL. These are the five the encounter has
# always used at this site, and the difference between them and the residence's
# Arasaka combat archetypes is the whole reason the two places feel different.
# Keeping the roster while changing the placement is what lets a playtest say
# which of the two it is reacting to.
GUARD = 'Character.sts_std_arr_12_security_guard1_ranged1_nue_ma'
SHOTGUN = 'Character.sts_std_arr_10_security_shotgun_mb'
BATON = 'Character.arasaka_guard2_melee1_baton_wa'
KNIFE = 'Character.arr_arasaka_ranger1_melee2_knife_ma'
NUE = 'Character.arasaka_2020guard_ranged1_2020nue_ma'

# ------------------------------------------------------------------ the posts
#
# CAPTURED IN GAME, playtest 2026-08-25, `captured_positions.txt`. Position is
# where the player stood, yaw is the way he faced, and the yaw is the RAW
# capture: the residence shipped uncorrected yaws and faces correctly.
#
# The dropped capture is the FIRST `gate01`, on the tester's instruction. He
# captured the spot twice, at yaw -33.5 and then -125.5, and the second is the
# one that ships. It is not listed here at all rather than commented out,
# because a commented-out post is one somebody switches back on without knowing
# why it went.
#
# `gate2-NN` in the capture file is `gate2_NN` here: these names become
# redscript identifiers in `Gig01_Encounter.CompoundEntries()`, and a hyphen is
# not one.
#
# (name, record, x, y, z, yaw)
POSTS = [
    # --- the outer gate off the street, ground level. The way in the gig's own
    # map pin points at, and the first thing V meets.
    ('gate03', SHOTGUN, -193.869, -1460.151, 7.600, -124.0),

    # --- THE SECOND GATE, which the old placement had no anchor for at all.
    ('gate2_01', GUARD, -225.764, -1497.931, 7.600, -129.2),
    ('gate2_02', SHOTGUN, -227.069, -1501.464, 7.600, -120.5),
    ('gate2_03', GUARD, -229.416, -1505.835, 7.611, -119.9),

    # --- the yard between the gates and the building, ground level. Twelve
    # posts over ground the five anchors skipped entirely.
    ('inner02', KNIFE, -245.883, -1491.905, 7.600, -122.5),
    ('inner03', GUARD, -267.818, -1459.454, 7.600, 159.5),
    ('inner04', SHOTGUN, -263.400, -1462.177, 7.655, 135.6),
    ('inner05', NUE, -281.564, -1501.880, 9.607, -36.7),
    ('inner06', GUARD, -240.843, -1468.986, 7.600, -156.8),
    ('inner07', BATON, -245.546, -1466.528, 7.600, -158.4),
    ('inner08', GUARD, -235.577, -1450.776, 7.606, -95.2),
    ('inner09', SHOTGUN, -224.379, -1435.308, 7.600, -132.0),
    ('inner10', GUARD, -212.523, -1440.340, 7.650, -179.4),
    ('inner11', KNIFE, -194.932, -1437.813, 7.600, 155.4),
    ('inner12', GUARD, -199.104, -1450.645, 7.600, -156.7),

    # --- the deck at 14.6 m, overlooking the yard. The old placement could not
    # produce a single one of these.
    ('deck02', GUARD, -219.689, -1426.223, 14.604, -107.1),
    ('deck03', NUE, -207.366, -1433.437, 15.845, -155.0),
    ('deck04', GUARD, -216.947, -1430.111, 14.604, 22.1),

    # --- inside the building, across three levels: 8.6, 12.6 and 14.6 m.
    # THE NORTH-EAST CORRIDOR IS EMPTY ON PURPOSE. Playtest walked it and left
    # two marks eleven metres apart, `noguardshere` and `removeguardsfromhere`.
    # `inside02` had already gone in the stealth trim; `inside03` and `inside04`
    # went with it. That whole approach into the building is unwatched now,
    # which is the point of it.
    # `inside08` IS GONE, marked at 2.4 m on the interior ground floor.
    #
    # He had a run of it. He was first suspected of nothing, then found to be
    # the one who spotted a player up on the deck six metres above him and
    # twenty-three away, so he was turned to -132.0 to close that angle, and
    # then marked for removal outright. Turning a guard closes ONE sightline;
    # a post in a corridor somebody has to walk closes the corridor.
    # `inside06` IS GONE TOO, marked at 3.9 m on the ground floor directly under
    # the side door. He was the last post on the way in from that entrance.
    #
    # WHY IT TOOK THREE PASSES TO FIND HIM. The player was being spotted while
    # coming through the side door, and the guards nearest the spot he was seen
    # from were all cleared or turned first: they were the visible ones. This
    # one stood six metres BELOW the door, out of sight of anybody using it, and
    # was found only when the mark was taken standing on his own floor.
    #
    # THE LESSON IS THE MARK, not the guard. Every one of these was found by
    # somebody standing where the problem happened and pressing a button, and
    # none by reasoning about sightlines from coordinates. Ask for the position,
    # and ask what HEIGHT it was taken at.
    ('inside10', GUARD, -267.007, -1428.349, 8.600, 37.4),
    ('inside11', KNIFE, -259.134, -1432.922, 8.600, -155.9),
    ('inside12', GUARD, -255.260, -1448.073, 8.603, 69.8),
    # TURNED OFF THE SIDE ENTRANCE. Playtest: *"turn them a bit so they don't
    # face the side entrance, otherwise it's impossible to enter from there
    # without being spotted"*, marking the spot facing 139.5. These three are
    # the ones on that floor within ten metres of the mark, and they were facing
    # -34, 55 and -66, which is straight at the way in. They look roughly along
    # the mark now, fanned so they are not a chorus line.
    #
    # `inside08` and `inner08` are as close but a floor or two below, so they
    # never covered that door and are left as they were.
    ('inside14', GUARD, -240.503, -1449.100, 14.600, 139.5),
    ('inside15', SHOTGUN, -239.460, -1442.241, 14.592, 152.0),
    ('inside16', GUARD, -248.284, -1439.285, 14.603, 126.0),
    ('inside17', NUE, -256.987, -1433.086, 14.931, -17.1),
    ('inside18', GUARD, -265.233, -1427.484, 14.601, 32.0),

    # --- the office floor and the terminal room, where the ledger is. The
    # densest part of the site, and the only part the old placement covered.
    ('office01', GUARD, -252.062, -1454.158, 14.600, -74.6),
    ('office02', SHOTGUN, -246.394, -1455.410, 14.600, -34.2),
    ('office03', KNIFE, -256.108, -1445.129, 14.600, -130.7),
    ('office04', GUARD, -263.580, -1438.582, 14.600, 45.2),
]


# ------------------------------------------------ WHO STANDS DOWN WHEN EASED
#
# THE ROSTER ABOVE IS THE GIG AS SHIPPED. These twelve are switched off again,
# one quest node each, when the player runs a mod that makes every fight in
# the game harder (`Gig01_Companions.reds` says which mods, and
# `gen_questphase.thin_detail` is the node shape). Eighteen stand then.
#
# THE COMPLAINT THIS ANSWERS is the workstation. Players on Nexus, three of
# them, with AI and survival mods: "SO many goons around that workstation",
# "remove a goon or two, or put them on patrol so there are gaps", and one
# who wanted stealth to be a real option with a mod that makes guards more
# observant. Patrols were tried and did not walk (see NOBODY WALKS below), so
# the answer is fewer men, and the design call of 2026-09-20 set a count per
# area after two playtests, five per site and then four, both judged too
# light a cut. The count per area is the design; which man goes within an
# area follows two rules: the one standing on the objective goes first, then
# one of any pair standing within a few metres of each other.
#
#   area                          shipped  eased   who goes
#   main gate                        1       1     nobody
#   second gate                      3       1     gate2_01, gate2_03 (the
#                                                  smoker in the middle stays)
#   yard                            11       9     inner04 (5.2 m from inner03)
#                                                  inner07 (5.3 m from inner06),
#                                                  both the pair nearest the
#                                                  building
#   deck                             3       2     deck04 (4.8 m from deck02)
#   lower interior floors            3       2     inside12, the one under the
#                                                  terminal room
#   office floor, outside the room   5       2     inside14 (1.0 m from the
#                                                  door), inside15 (7 m),
#                                                  inside16 (12 m); the two
#                                                  at the far end stay
#   terminal room                    4       1     office01 (2.2 m from the
#                                                  terminal), office02 (5.6 m,
#                                                  shotgun), office04; office03
#                                                  stays, 12 m off, coffee
#
# Distances to the objective were measured from the posts to
# `CCGig01Places.OfficeTerminal()` and `OfficeEntry()`.
#
# Every name here has to be a post in POSTS. `guard_site.check_stand_down`
# refuses to write otherwise, because a quest node naming an entry that does
# not exist crashes the game without a message (gotcha 73).
STAND_DOWN = [
    'gate2_01', 'gate2_03',
    'inner04', 'inner07',
    'deck04',
    'inside12',
    'inside14', 'inside15', 'inside16',
    'office01', 'office02', 'office04',
]


# ------------------------------------------------------- WHO IS DOING WHAT
#
# Playtest 2026-08-25 asked for a few of them to look less alike without
# becoming more dangerous. A workspot is only what a man is DOING: it is not his
# attitude and not his senses, so nothing here changes how any of them fight.
#
# Most stay arms-crossed. These are the ones that do not, and they are the
# ordinary-security half of the two tiers: a long shift at an industrial park
# has somebody smoking by the gate and somebody on the phone indoors, where the
# residence's elite detail does not.
IDLES = {
    'gate2_02': 'smoke2',
    'inner05': 'phone',
    'inner08': 'inspect',
    'deck03': 'smoke',
    'inside16': 'inspect',
    'office03': 'coffee',
    'inner02': 'wait',
    'inside11': 'think',
    'office02': 'stand_around',
}

# ----------------------------------------------------------- NOBODY WALKS
#
# FOUR BEATS WERE TRIED HERE ON 2026-08-25 AND THEY DID NOT WORK. Playtest:
# "the beat doesn't work and I think it's too complex to add".
#
# The mechanism is real in the game's own data and that is not in doubt: of
# 32669 time periods in the cached registries, 1780 carry more than one spot and
# 964 set `isSequence`, and `#q112_ws_oda_patrol_002` upward is nine points on
# one entry. What is not established is how a MOD gets it, and the four routes
# tried here were two-point beats of 9 to 19 m between captured posts, in the
# open, on one level. They did not walk.
#
# NOT CHASED FURTHER, and that is a decision rather than silence. Vanilla's
# patrolling entries sit alongside quest phases, spawn tables and AI setups this
# project has not read, so "give the entry more spots" was the cheap version of
# the question and the cheap version is answered: no. The expensive version is
# a research line of its own and the gig does not need it.
#
# `questkit/community.py` KEEPS its route support. It is inert with one point
# per entry, it was proved not to change a single byte of the three shipped
# communities when it went in, and deleting it would throw away the one thing
# the trial did establish: how to express a route at all.


# ------------------------------------------------ NO SECURITY AREA IS SHIPPED
#
# One was built, measured and taken out again on 2026-08-25. It loaded, resolved,
# reported itself ON, attached, typed RESTRICTED exactly as vanilla's is, linked
# to this community, fed by eighteen cameras, with its security system present,
# and it reported that the player was INSIDE it. The guards did nothing at all.
#
# Every vanilla community a security area alerts, all 21 that resolve in the
# cached sectors, is a `worldCompiledCommunityAreaNode` in the GAME'S OWN
# `always_loaded` sectors. A mod cannot add nodes to those. That is the one
# difference left after eliminating the node class, the area type, the component
# ids, the outline, its winding, the missing system node and containment.
#
# So the nodes are not shipped: a device that does nothing is still a device in
# every player's save. `gen_security.py` and `backlog.md` 31 keep the whole
# thing, so rebuilding it is a one-line change if the picture ever changes.

# ---------------------------------------------- WHICH KIND OF COMMUNITY NODE
#
# THE PLAIN CLASS, and it is here because of an experiment that is now finished.
#
# Of the 32 `CommunityProxyPS` connections vanilla ships, 21 resolve inside the
# cached sectors and ALL TWENTY-ONE point at `worldCompiledCommunityAreaNode`.
# None points at the `_Streamable` class this project had always written, so the
# class looked like the reason a mod's security area could not alert a mod's
# community.
#
# IT WAS NOT. This site shipped the plain class with an area wired to it and the
# guards still did nothing, which eliminates the class along with everything else
# gotcha 80 lists. What separates vanilla's alertable communities is that they
# sit in the game's own `always_loaded` sectors, and a mod cannot add to those.
#
# WHAT THE RUN DID ESTABLISH: a mod's own sector spawns from EITHER class.
# Thirty guards stand here in play, so gotcha 66 part 3 applies to fewer cases
# than its wording suggests.
#
# The residence keeps `_Streamable` and this site keeps the plain class. Neither
# is rewritten to match the other, because both are shipped and playtested and
# regenerating a working sector proves nothing. A new site should take the
# default, which is `_Streamable`.
AREA_CLASS = 'worldCompiledCommunityAreaNode'


def build():
    return guard_site.build(SECTOR, POSTS, IDLES, area_class=AREA_CLASS)


if __name__ == '__main__':
    guard_site.write(OUT, SECTOR, POSTS, ENCOUNTER, 'CompoundEntries',
                     cache_dir=CACHE, idles=IDLES, area_class=AREA_CLASS,
                     stand_down=STAND_DOWN)
