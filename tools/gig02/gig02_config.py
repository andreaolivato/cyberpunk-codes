"""Gig 02's own constants: where its files live, what its keys are prefixed
with, and which base-game nodes its scenes are anchored to.

A copy of `tools/gig01/gig01_config.py`, re-pointed. Read that file's header for
why the pattern exists; this one only records what is different.

EVERY ANCHOR BELOW IS A NODE IN ONE OF THE THREE ALWAYS-LOADED SECTORS, and
each is also the pin target for its leg. That is a deliberate simplification of
gig 01's arrangement, where an anchor was a nearby origin and the pin sat at
`anchor + offset`. Nobody could walk this gig's five sites and capture a
doorstep, so a made-up target would be a pin at coordinates nobody has looked
at. A base-game node whose own name says what it is cannot be in a wall, and
the offset is then zero.

The cost is that a pin lands on the game's own marker rather than on the exact
step the comic draws. Where that matters it is written down beside the anchor.
Every position here was read out of `tools/_anchor_cache`, not typed.
"""
import os

_TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(_TOOLS)

# ---------------------------------------------------------------------- names
MOD_DIR = 'gig-02-dead-ringer'           # the folder under mods\
MOD_NAME = 'dead_ringer'                 # the folder under mod\ in the archive
LOCKEY_PREFIX = 'cc-g02-'                # every LocKey this gig ships
QUEST_ID = 'cc_g02_dead_ringer'          # the journal quest, and the POI

# ---------------------------------------------------------------------- paths
MOD = os.path.join(REPO, 'mods', MOD_DIR)
SOURCE = os.path.join(MOD, 'source')
RAW = os.path.join(SOURCE, 'wkit', 'raw')
# Where the generators write. Everything under here is generated; the one
# hand-authored file (the .archive.xl) sits beside it in RAW.
RAW_MOD = os.path.join(RAW, 'mod', MOD_NAME)

# The same folder as the engine sees it. A depot path is backslash-separated and
# is NOT a filesystem path. Built from chr(92) because a backslash typed into a
# quoted string in a generated edit gets eaten (gotcha 28).
DEPOT = 'mod' + chr(92) + MOD_NAME

# ------------------------------------------------------------- the five sites
#
# LOCATION 1, outside Afterlife, Watson. The base game's own Afterlife entrance
# mappin, which is the top of the stairs the queue stands on. Comic pp. 10-35.
ANCHOR_AFTERLIFE = '#q005_mrk_afterlife_entrance_mappin'

# LOCATION 2, the netrunner. KABUKI, WATSON, on the upper walkway.
#
# CAPTURED IN GAME 2026-08-26, and it is the only position in this gig that is
# not a guess. The spot below is where the player stood; `#wat_sm_kab_netrunner_01`
# is 4.6 m from it, is in an always-loaded sector, and is named for exactly what
# it is, so it is the pin's anchor and the scenes' marker.
#
# THE ARROYO ANSWER THIS REPLACES WAS WRONG, and the way it was wrong is worth
# keeping. Searching the voice corpus for "Dewdrop" returns a Santo Domingo
# receptionist saying "Welcome to the Dewdrop Inn", and that was read as
# locating the scene. It does not: the corpus says where a NAME IS SPOKEN, not
# where a comic panel is set, and the sign in the art is a Kabuki sign. A
# confident deduction from real evidence, pointing at the wrong side of the
# city, and only standing in the place settled it.
ANCHOR_INN = '#wat_sm_kab_netrunner_01'

# LOCATION 3, Wakako's pachinko parlor, Japantown. The base game's own marker
# for it. Comic pp. 56-68.
ANCHOR_PARLOR = '#q112_mp_wakakos_pachinko_parlor'

# LOCATION 4, Wakako's office.
#
# `#wakako_sm_okada_default` is the spot the real Wakako Okada stands on when
# nothing else is going on, so it IS her office. It is 14.8 m from the parlor
# marker above and at the same height, which is the game's geometry rather than
# the comic's: the comic calls the office "upstairs" and in game it is the room
# behind. The story language is unchanged and nothing depends on the stair.
ANCHOR_OFFICE = '#wakako_sm_okada_default'

# LOCATION 5, the hit. A JAPANTOWN STAIRCASE, captured in game 2026-08-26.
#
# THE SITE MOVED, AND THIS IS THE ONE PLACE THE GIG GOT COMPLETELY WRONG.
# It was `#wbr_jpn_dataterm_03`, a street data terminal 900 m south of here,
# chosen off the files for having empty space around it because nobody could
# walk the city. Playtest: "the last battle is completely in the wrong place.
# It's set in a staircase and we need to descend and then jump like in the
# comic."
#
# The real site is an outdoor staircase falling 19 m over 85 m, with a trash
# pile 8 m below its middle landing. That is the comic's staging and it is a
# far better encounter than a flat street: the Claws hold the steps, and the
# drop onto the trash is a way past them.
#
# `#wbr_sm_jpn_netrun_01` is the nearest always-loaded node, 91 m off, and its
# name confirms the district the design always claimed: Westbrook, Japantown.
ANCHOR_HIT = '#wbr_sm_jpn_netrun_01'

# The holocall studio's own floor spot, in always_loaded_2, which is where the
# body that appears on V's phone stands. See docs/scene-playbook.md, "The
# MOD-OWNED recipe", and gig 01's nix_call().
ANCHOR_STUDIO = '#holocall_marker'

# World positions, read out of the always-loaded sectors with
# tools/find_pin_anchors.py. LOAD-BEARING: a pin lands at position + offset, and
# the scripts measure proximity against these same numbers.
ANCHOR_POS = {
    ANCHOR_AFTERLIFE: (-1465.155029, 1046.971069, 22.759001),
    ANCHOR_INN: (-1179.403000, 2042.247000, 20.072001),
    ANCHOR_PARLOR: (-657.332031, 826.690979, 19.521999),
    ANCHOR_OFFICE: (-671.492004, 822.323975, 19.598000),
    ANCHOR_HIT: (-354.645905, 1366.601440, 42.162102),
}

# THE THREE GROUPS OUTSIDE AFTERLIFE, and this is the one leg that is built on
# walked positions rather than on the entrance marker.
#
# The first playtest of this leg reported the whole area as unplayable, and the
# report carried the design with it: there are always three knots of people
# standing outside the club, so the beat is three of them to listen to rather
# than one anonymous conversation and then a hunt. Two pins go up together, the
# third after both are done, and the man who talks in the third group is the
# merc.
#
# EVERY ONE OF THESE MUST BE OUTSIDE THE CLUB'S SAFE AREA. Inside it the player
# cannot draw a weapon and the fight cannot happen at all, which is half of what
# made the leg unplayable: the entrance marker the merc used to spawn on is the
# door itself. Gig02_Encounter now asks the game directly, through
# `SafeAreaManager.IsPointInSafeArea`, and refuses a spawn point inside one.
#
# CAPTURED IN GAME 2026-08-26, all three, by standing with each group. They are
# where the PLAYER stands to listen, which is what a pin should point at, and
# they are 6 to 9 m from the entrance marker the leg used to use for everything.
#
# GROUPS 1 AND 2 ARE 3.6 M APART, which is closer than a trigger radius can
# separate on its own. Gig02_Encounter therefore picks the NEARER group rather
# than the first one whose radius the player is inside; see `Groups` there.
# Keep this file and Gig02_DeadRinger.reds in step.
# CHAR'S CHAIR at the Dewdrop Inn, 9 m in from Yoko. Captured in game
# 2026-08-26, standing beside it. See Gig02_DeadRinger.reds.
CHAR_POS = (-1183.542, 2045.510, 20.487)

GROUP_POS = {
    'group1': (-1467.443, 1052.568, 22.709),
    'group2': (-1470.628, 1050.988, 22.722),
    'group3': (-1470.163, 1044.159, 22.722),
}

# THE STAIRCASE, top to bottom, captured in game 2026-08-26 by walking down it.
#
# Nine positions. Eight steps of the descent and the trash pile the comic jumps
# onto, which sits 8 m below the stretch between STAIR[2] and STAIR[3] and about
# 2.5 m above the ground at the bottom.
#
# The Claws hold the steps and Toji waits at the bottom. Every one of these is a
# spot somebody has stood on, which is what gig 01 replaced a scatter with
# thirty walked posts to get: a navmesh query answers "somewhere near here" and
# keeps giving nearly the same answer, so a scattered squad huddles.
#
# KEEP IN STEP WITH `CCGig02Places` in Gig02_DeadRinger.reds.
STAIR = [
    (-399.587, 1318.163, 42.167),   # 0  the top, where V arrives
    (-395.667, 1302.594, 41.464),   # 1
    (-393.149, 1290.089, 37.449),   # 2  the drop is off this stretch
    (-386.443, 1276.179, 33.469),   # 3
    (-381.961, 1262.021, 29.458),   # 4
    (-382.124, 1254.921, 27.458),   # 5
    (-385.082, 1242.323, 23.428),   # 6
    (-381.087, 1233.990, 23.428),   # 7  the bottom, where Toji is
]
TRASH = (-391.116, 1284.479, 25.910)


# ===========================================================================
# THE TWO WAITING SPOTS, captured in game 2026-09-08
# ===========================================================================
#
# Each of the gig's two waits has a place to take instead of walking in
# circles: a railing outside Yoko's stall in Kabuki, and a chair outside the
# pachinko parlor in Japantown. The design call, 2026-09-08.
#
# THE SHAPE IS VANILLA'S, and the Claire races are the worked example. Four
# legs of `sq024` carry an objective the game names `wait_for_claire`, and the
# pin on each is a place to take: `01d_wait_for_claire_sit_mappin` and
# `01d_wait_for_claire_Seat_mappin` label their pin "Waiting Spot",
# `01c_wait_for_claire_Lean_mappin` and `00c_wait_for_claire_Lean_mappin`
# label theirs "Meeting Place". Two sits and two leans, under a wait.
#
# ONE DIFFERENCE, and it decides how ours is built. Claire arrives BECAUSE V
# took the spot: no clock is running there and there is nothing to shorten.
# Both of ours are real `questGameTimeDelay` waits, because Char needs the
# time to run the trace. So taking the spot has to satisfy the wait rather
# than pass it, and it moves the world clock with it so that Char's "give me
# half an hour" is still true when V stands up.
#
# PROMPT and POSE are two different points. The prompt is where the player
# stands to be offered it; the pose is where V's feet end up, which for a lean
# is a step nearer the railing and for a sit is at the chair. The yaw on the
# POSE is the one that matters: it is which way V faces while he is in it.
#
# KEEP IN STEP WITH `CCGig02Places` in Gig02_DeadRinger.reds.
LEAN_PROMPT = (-1178.536, 2034.795, 20.078)
LEAN_POSE = (-1177.941, 2033.495, 20.078)
LEAN_YAW = -142.8

SIT_PROMPT = (-653.176, 827.874, 19.350)
SIT_POSE = (-653.355, 828.668, 19.350)
SIT_YAW = -151.7

# THE TWO POSES, and both are the game's own PLAYER poses rather than an NPC
# pose borrowed onto V. Every `.workspot` path the base game's sectors
# reference was byte-searched out of the extracted set on 2026-09-08: 1,317
# distinct files, 37 of them named `player__`, and two of those are this
# request word for word. They come out of `memoryresident_1_general.archive`,
# which is where workspots live and where the merc's kneel came from.
LEAN_WORKSPOT = ('common', 'rail',
                 'player__stand_rail_lean_front__stand_around__01.workspot')
# THE SEAT IS A CHAIR, NOT A STOOL (screenshots, 2026-09-08). The spot outside
# the parlor door is a red plastic garden chair with a back and armrests,
# against the shutter wall between the doorway and the rubbish bags, and it is
# the only seat there. So the barstool pose is wrong: it rests V's arms on a
# bar that is not there. `player__sit_chair__sit_around__01.workspot` is the
# more upright fallback if leaning back does not sit well in a plastic chair.
SIT_WORKSPOT = ('player', 'chair',
                'player__sit_chair_lean_back__sit_around__01.workspot')
