"""Fixer 01's own constants: where its files live, what its keys are prefixed
with, and where the fixer stands.

A copy of `tools/gig03/gig03_config.py`, re-pointed. Read `tools/gig01/
gig01_config.py`'s header for why the pattern exists; this one records only
what is different.

THIS IS NOT A GIG. It is a FIXER: a character of the mod's own who hands out
several gigs, shipped as a mod of her own that those gigs require, with the
things the base game gives its seven fixers and nobody else. The hands icon
on the map that never goes away, the "3/10" gig counter on that icon, the
portrait on every gig card, a phone contact V can ring, and a body that is
always where her office is.

HER OWN MOD, NOT PART OF A GIG (the design call, 2026-09-18). Two gigs cannot
both ship her record, her contact and her icon, so she ships once and every
gig of hers requires her. The folder is `mods/fixer-01` beside the `gig-NN`
folders, the tools live in `tools/fixer01/`, and the prefixes follow the
convention with `f` for fixer: facts `cc_f01_*`, LocKeys `cc-f01-*`, records
`Character.cc_f01_*`, module `CyberpunkCodes.Fixer01`. A second fixer would
be `fixer-02`.

SHE IS HODAN WARSAME, with her office on a lobby couch in Charter Hill
(mods/fixer-01/docs/design.md). Her body is built from a character-creator
preset (gen_npv.py, source/tweaks/fixer.yaml).
"""
import os

_TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(_TOOLS)

# ---------------------------------------------------------------------- names
MOD_DIR = 'fixer-01'                 # the folder under mods\
MOD_NAME = 'fixer01'                     # the folder under mod\ in the archive
LOCKEY_PREFIX = 'cc-f01-'                # every LocKey this mod ships
FACT_PREFIX = 'cc_f01_'                  # every quest fact this mod sets
REDS_MODULE = 'CyberpunkCodes.Fixer01'     # see docs/conventions.md

# THE FIXER'S OWN IDS. Everything that is his rather than one gig's carries
# `fixer` in the name, so that when the gigs arrive it is obvious which
# entries belong to him and travel with him.
FIXER_ID = 'cc_f01_fixer'                # the POI, the contact, the codex entry
FIXER_RECORD = 'Character.cc_f01_fixer'  # source/tweaks/fixer.yaml
# THE COUNTER. The fact the map tooltip reads for the "3" in "3/10", named
# on the character record as `factCounterName`. Every gig of hers adds 1 to
# it as it closes, the way the base game's fixer loop adds 1 to
# `cct_sts_counter` when a City Center gig finishes. The dev menu can also
# step it by hand.
COUNTER_FACT = 'cc_f01_fixer_count'
# THE TOTAL, the "10", IS NOT A NUMBER HERE. It is however many of her gigs
# are installed: each gig registers itself at launch and the register
# writes the count onto her record (source/scripts/Fixer01_Gigs.reds).


# ---------------------------------------------------------------------- paths
MOD = os.path.join(REPO, 'mods', MOD_DIR)
SOURCE = os.path.join(MOD, 'source')
RAW = os.path.join(SOURCE, 'wkit', 'raw')
RAW_MOD = os.path.join(RAW, 'mod', MOD_NAME)

# The same folder as the engine sees it. A depot path is backslash-separated
# and is NOT a filesystem path. Built from chr(92) because a backslash typed
# into a quoted string in a generated edit gets eaten (gotcha 28). `mod` +
# backslash + `fixer` is backslash-f, which is a form feed: exactly the trap.
DEPOT = 'mod' + chr(92) + MOD_NAME

# ------------------------------------------------------------ where she sits
#
# THE CHARTER HILL LOBBY (the design call, 2026-09-18). The ground floor of
# the residential tower the gig "Until Death Do Us Part" plays out in, a
# corporate sofa facing a low table with a book and a whiskey glass on it,
# a second sofa opposite, the lifts a few metres away. The gig owns the
# floor above and never the lobby: read off its phases, it switches the
# lift's floor 1 on when it starts and off at its cleanup and touches floor
# 0 not once, and its people are a drone and three guards upstairs plus a
# few lobby civilians while it runs. So she sits there before, during and
# after it, and a player who has never taken that gig walks in off the
# street.
#
# The position is the seat cushion, stood on in play and captured
# (`cc_capture`, spot2: feet at z 15.657, the floor there at 15.294 in the
# sector, so a 36 cm seat). The AI spot goes on the floor under it. The yaw
# is a desk reading: the sofa opposite faces 122, the two are parallel, and
# the arm she sits on runs at right angles to it and faces the table, so
# 32. The first playtest is what checks she faces the table and not the
# wall; it is one number if she does not.
FIXER_FLOOR = 15.294
FIXER_POS = (3.227, 10.466, FIXER_FLOOR, 32.0)

# HER POSE. A community entry sits through its AI spot's workspot, and the
# in-person scene fires the same resource on her at its first beat (gig
# 03's bar lesson: a body the AI holds in a sitting workspot keeps its head
# and mouth for it unless the scene takes the pose over). Entry 2 is the
# main sitting sequence in every generic sitting workspot read (couch and
# chair alike).
#
# WHICH POSE. Chosen in play on 2026-09-21 with the dev menu's pose panel,
# which plays any of the game's 44 sitting workspots on her from a rig at
# her seat (gen_poses.py): upright, legs crossed, hands on the lap, with
# three small shuffles as idles and no prop. The plain couch one
# (`couch\generic__sit_couch__sit_around__01`) read as a slouch on
# 2026-09-18, and the leaning-forward hand-on-chin one
# (`chair\generic__sit_chair_lean_front__think__01`) was the desk pick
# between the two; the panel is what settles this from now on.
#
# A chair pose on a 36 cm sofa: chair animations are authored for a higher
# seat, so if she floats above the cushion the fix is FIXER_FLOOR minus the
# gap, not the pose.
FIXER_WORKSPOT = (chr(92) + 'workspots' + chr(92) + 'common' + chr(92) + 'chair' + chr(92)
                  + 'generic__sit_chair__sit_around__07.workspot')
FIXER_WORKSPOT = 'base' + FIXER_WORKSPOT
FIXER_WORKSPOT_ENTRY = 2

# WHERE A HOLOCALL IS STAGED. The scene's own marker, not a place: a call is
# played at the studio rather than wherever the player is standing, and the
# studio is kilometres away. Gig 01 measured the pairing and every gig since
# uses the same marker.
ANCHOR_STUDIO = '#holocall_marker'

# WHERE SHE FIRST CALLS FROM: her district, the way the game's own fixers
# do it (the design call, 2026-09-21; a 120 m circle round her seat until
# then). Wakako's phase waits for V inside `#westbrook_tr`, Dino's inside
# `#city_center_tr`; hers waits inside Charter Hill, which the game keeps as
# two boxes in `always_loaded_0`. The quest phase watches them and keeps
# the fact below at 1 while V is in the district; the intro script reads
# the fact in place of a distance and keeps its own guards (prologue over,
# story not ended, phone free, V not on a screen or mid fast-travel).
DISTRICT_TRIGGERS = ['#charter_hill_tr', '#charter_hill_tr_001']
IN_DISTRICT_FACT = FACT_PREFIX + 'in_district'

# HOW CLOSE V HAS TO BE FOR HER CONVERSATION TO BE OFFERED, and how far
# before it is withdrawn. The game's own fixers open their in-person talk
# within 10 m of the body (`dyno.questphase`, default dialogue phase, node
# 8) and the prompt itself only shows at arm's length, because the hub is
# pinned to the body. The withdrawal is ours: the game leaves its talk open
# until V says goodbye, and a scene left open across the city is a hub
# nobody can see. Wider than the offer, so the two cannot flap.
TALK_RADIUS = 10.0
LEAVE_RADIUS = 16.0
