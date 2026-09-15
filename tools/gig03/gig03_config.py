"""Gig 03's own constants: where its files live, what its keys are prefixed
with, and which base-game nodes its scenes are anchored to.

A copy of `tools/gig02/gig02_config.py`, re-pointed. Read `tools/gig01/
gig01_config.py`'s header for why the pattern exists; this one records only what
is different.

WHAT IS DIFFERENT ABOUT THIS GIG. Both earlier gigs are set in streets and rooms
the player already walks past. This one is a single walled compound in the
Badlands with a computer in it, so it has one site rather than five, and the
perimeter was walked in game rather than read out of a sector file. The numbers
below under THE COMPOUND are the only positions in this repo captured by walking
a boundary.
"""
import os

_TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(_TOOLS)

# ---------------------------------------------------------------------- names
MOD_DIR = 'gig-03-acceptable-loss'       # the folder under mods\
MOD_NAME = 'acceptable_loss'             # the folder under mod\ in the archive
LOCKEY_PREFIX = 'cc-g03-'                # every LocKey this gig ships
FACT_PREFIX = 'cc_g03_'                  # every quest fact this gig sets
QUEST_ID = 'cc_g03_acceptable_loss'      # the journal quest, and the POI
REDS_MODULE = 'CyberpunkCodes.Gig03'     # see docs/conventions.md

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
#
# THIS GIG IS THE WORST CASE FOR THAT AND EVERY GENERATOR HERE MUST USE THIS
# CONSTANT. Its depot folder is `mod` + backslash + `acceptable_loss`, so the
# literal a modder would naturally type contains backslash-a, which is the bell
# character. Written into a normal quoted string it silently becomes one byte of
# 0x07 and the path stops existing, with no error from anything. The four wrong
# depot paths that reached the public docs were all this bug and one of them was
# exactly this escape. Never type the folder; join it.
DEPOT = 'mod' + chr(92) + MOD_NAME

# --------------------------------------------------------------- the compound
#
# The Militech detention centre in the Badlands, near the Tango Tors motel.
#
# THE PERIMETER WAS WALKED, 2026-09-09, one capture per corner in order, so the
# list closes as it stands and vertex 10 joins back to vertex 1. Ground sits at
# about z = 87 throughout.
#
# It is used for two things and neither of them is a map pin: deciding whether
# the player is inside the wire, and placing the guards. The pin needs a
# base-game node in the long NodeRef form and no such node has been found here
# yet, which is the next thing to do.
COMPOUND = [
    (-94.603, -5182.958, 87.070),
    (-93.260, -5191.834, 87.070),
    (-63.751, -5188.975, 87.070),
    (-58.180, -5240.128, 87.198),
    (-62.299, -5241.255, 87.106),
    (-62.074, -5245.433, 87.133),
    (-125.795, -5250.342, 87.042),
    (-130.538, -5205.756, 87.096),
    (-138.655, -5207.188, 87.074),
    (-141.365, -5185.973, 87.026),
]

# THE TERMINAL THE GIG USES, captured 2026-09-09 in the north-west corner of
# the compound. A plain base-game computer, which is the case
# docs/computer-ui-playbook.md is written against.
#
# IT IS DELIBERATELY NOT THE OBVIOUS ONE. The computer in the office, at
# -101.091, -5216.215, is `ina_05_dvc_comp`: the quest device belonging to the
# base game's own street story at this site, with three
# `DeviceContentAssignment.sts_bls_ina_05` nodes within five metres of it.
# Putting mod content on a live quest's device risks both directions. This one
# is 39 m away, is a real working computer (its device probe answers with a
# `ComputerControllerPS`, powered), and belongs to no quest.
TERMINAL_STAND = (-132.000, -5194.600, 88.500, -50.0)
TERMINAL_POS = (-133.173, -5193.786, 88.564, -50.0)
TERMINAL_RECORD = 'Devices.Computer'
TERMINAL_APPEARANCE = 'computer_computer_1'
TERMINAL_ENTITY_ID = 15145940603936824689

# THE STREET STORY'S OWN COMPUTER, recorded so nobody captures it again and
# takes it for a find. Nothing in this gig may write to it.
QUEST_COMPUTER_POS = (-101.091, -5216.215, 88.580)
QUEST_COMPUTER_ENTITY_ID = 2518579185671404974

# ------------------------------------------------------------------- the gate
#
# WHERE THE REINFORCEMENTS ARRIVE, captured in playtest 2026-09-15 ("3guards"
# in captured_positions.txt): a spot at the compound's gate, on the west
# side, 25 m from the terminal. The three stand here facing the OPPOSITE way
# to the capture (the design call: "facing opposite of where I was facing
# during capture"), which is into the compound, and are spread 1.5 m apart
# across that line so they do not stand inside one another. Until this
# capture they stood at three walked fence corners.
GATE_POS = (-133.181, -5200.584, 87.139)
GATE_CAPTURE_YAW = 103.8
GATE_FACING_YAW = GATE_CAPTURE_YAW - 180.0          # -76.2
GATE_SPREAD = 1.5

# ------------------------------------------------------------------- the safe
#
# THE CABINET IN THE SECURITY ROOM, which holds the shard. Captured 2026-09-09.
# A `LootContainerObjectAnimatedByTransform` with appearance
# `safe_medium_entropy_a`, so it is the game's own medium safe, and its state
# object is a `LootContainerObjectAnimatedByTransformPS`.
#
# It reports no TweakDB record and no display name beyond `LocKey#18684`, which
# is what a loot container looks like: a container is not a device carrying a
# record the way the computer is.
SAFE_POS = (-95.621, -5211.431, 87.135, -84.1)
SAFE_STAND = (-94.632, -5211.424, 87.135, 92.9)
SAFE_ENTITY_ID = 1974278932582223405
SAFE_APPEARANCE = 'safe_medium_entropy_a'

# --------------------------------------------------------------------- Dino's
#
# The closing scene is face to face, not a call, at Dino Dinovic's own bar in
# Downtown (the Electric Orgasm, which is what his own welcome text calls it).
#
# THE FIXER WAS REGINA JONES UNTIL 2026-09-15. The design call, after the
# research that day: her whole base-game identity is the ex-media crusader
# whose cyberpsycho programme exists to keep people alive, so a plot where
# the fixer shrugs at mercs being farmed as targets fought her on every line.
# Dino is the City Center fixer whose clientele is corpos, who has V kill a
# merc to placate Zetatech in his own Mausser brief, and whose rebukes
# ("I didn't say 'Don't make a complete fuckin' mess', but I didn't think I
# had to") are the scene this gig needed. Everything Regina-specific was
# rebuilt on him; the Regina positions and door are in git history.
#
# WHERE HE SITS, READ OUT OF THE SHIPPED WORLD rather than captured, because
# the switch was made at the desk: `#ws_dyno_default`, the AI spot his own
# community entry (`#dyno`, entry `dyno`, phase `default`, in always_loaded_1)
# puts him on, is a `worldAISpotNode` in `exterior_-16_2_0_1` at the position
# below, orientation quaternion k=0.6496 r=0.7603, which is a yaw of 81.0
# degrees, on the game's own barstool workspot
# `base\workspots\bar\bar_and_barstool\generic__sit_barstool_bar__sit_around__01`.
# So he sits at the bar facing roughly west, with the counter in front of
# him; V talks to him from beside or behind the stool.
#
# `#mq033_dino_teleport`, 5.1 m south of the stool in always_loaded_1, is a
# spot the base game itself uses to put V next to him, so it is where the
# dev menu's teleport lands. `#dyno_sm_default`, 9.5 m north, is the pin
# anchor, the same role `#reggie_sm_default` played for Regina.
#
# NOTHING HERE HAS BEEN STOOD ON IN PLAY YET. The first playtest of the bar
# leg is what checks that the stool is his, that the bar has no door in the
# way (none is in the sector within 45 m of him; Regina's building had a
# locked one), and that the swap radius below is out of sight. Replace any of
# these with a captured number if it is wrong.
DINO_POS = (-1969.884, 377.748, 8.046, 81.0)
DINO_STAND = (-1969.496, 372.634, 8.041, 4.4)        # #mq033_dino_teleport
DINO_RECORD = 'Character.dyno'             # the base game's own Dino Dinovic
DINO_WORKSPOT = ('base' + chr(92) + 'workspots' + chr(92) + 'bar' + chr(92)
                 + 'bar_and_barstool' + chr(92)
                 + 'generic__sit_barstool_bar__sit_around__01.workspot')
# THE BODY SWAP happens when V is this far from the stool, in plan, so the
# game's own Dino is out and ours is in before the stool is in view. 35 m is
# a desk guess for a bar under a tech shell; Regina's swap was keyed to her
# street door, 48 m below her floor.
DINO_SWAP_RADIUS = 35.0
# LEAVING is being this far from the stool again, in plan, once the scene
# has played. THE SAME NUMBER DRAWS THE AREA ON THE MINIMAP: gen_community.py
# ships a trigger area of this radius round the stool (a 16-gon inscribed in
# the circle, so its edges sit 0.7 m inside it), and the "leave the bar"
# objective's pin points at it, the way gig 02 draws its way out
# (docs/map-pins-playbook.md, "A quest area drawn on the minimap"). The
# outline goes as V crosses the edge and Gig03_Places.reds calls V out at
# the circle, at most 0.7 m later. The swap-in and the leaving radius are the
# same on purpose: our Dino goes back to the game's own at the distance he
# arrived at.
DINO_LEAVE_RADIUS = 35.0
DINO_AREA_SIDES = 16
# The area prism: from 2 m under the bar floor to well over the tech shell.
DINO_AREA_HEIGHT = 30.0

# WHERE A HOLOCALL IS STAGED. The scene's own marker, not a place: a call is
# played at the studio rather than wherever the player is standing, and the
# studio is kilometres away. Gig 01 measured the pairing and gig 02 uses the
# same marker.
ANCHOR_STUDIO = '#holocall_marker'

