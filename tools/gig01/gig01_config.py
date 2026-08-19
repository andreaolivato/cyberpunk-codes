"""Gig 01's own constants: where its files live, what its keys are prefixed
with, and which base-game nodes its scenes are anchored to.

WHY THIS FILE EXISTS. Everything here was stated in two or more generators, and
the anchors carried three comments warning that the copies had to be kept in
step. A value stated twice is a value that will disagree with itself eventually,
and the scene anchors are the ones where a disagreement is silent: a scene plays
at the wrong end of the city rather than failing.

A SECOND GIG COPIES THIS FILE and re-points it, and its generators need no other
path edit. Name the copy after the gig (`gig02_config.py`) rather than reusing
one name across gigs, so nothing depends on which directory happens to be on
sys.path first.
"""
import os

_TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(_TOOLS)

# ---------------------------------------------------------------------- names
MOD_DIR = 'gig-01-negative-balance'      # the folder under mods\
MOD_NAME = 'negative_balance'            # the folder under mod\ in the archive
LOCKEY_PREFIX = 'cc-g01-'                # every LocKey this gig ships
QUEST_ID = 'cc_g01_negative_balance'     # the journal quest, and the POI

# ---------------------------------------------------------------------- paths
MOD = os.path.join(REPO, 'mods', MOD_DIR)
SOURCE = os.path.join(MOD, 'source')
RAW = os.path.join(SOURCE, 'wkit', 'raw')
# Where the generators write. Everything under here is generated: nothing in it
# is hand-edited, and the one hand-authored file (the .archive.xl) sits beside
# it in RAW rather than inside it.
RAW_MOD = os.path.join(RAW, 'mod', MOD_NAME)

# The same folder as the engine sees it. A depot path is backslash-separated and
# is NOT a filesystem path: it is what the .archive.xl, the scene resources and
# the journal all refer to each other by.
DEPOT = 'mod' + chr(92) + MOD_NAME

# ------------------------------------------------------------- scene anchors
#
# Base-game NodeRefs, and the same ones the map pins anchor to, which is the
# point: they are known to resolve, and a scene location must resolve for the
# same reason a pin anchor must. A scene location is only a placement origin -
# the player does not have to be anywhere near it, which is what makes one
# usable for a holocall.
ANCHOR_OFFICE = '#std_arr_parking_spwn_179'
ANCHOR_ESTATE = '#q113_dvc_arasaka_estate_camera_010'
ANCHOR_COYOTE = '#loc_sq022_el_coyote_cojo_bar_marker'

# THE BAR BEAT NEEDS ITS OWN ANCHOR, and not ANCHOR_COYOTE.
#
# ANCHOR_COYOTE is at (-1260.280, -983.960, 12.040), the base game's bar marker,
# which sits at the pub's ENTRANCE, 10.4 m from the stools V walks to. That is
# fine for a holocall and fine for the epilogue, whose only actor is a kilometre
# away by design. It is wrong the moment an actor has to stand next to the
# player: a 10 m offset would put Johnny in the doorway.
#
# `#hey_rey_food_01_mp` is (-1256.635, -998.972, 12.158), 1.65 m from
# CCGig01Places.BarStools(), at floor level, in the same streaming sector, with
# an IDENTITY orientation, so a spawn offset is not silently rotated. Found with
# find_pin_anchors.py on the stool coordinates; it was the nearest globally
# named node of 63 candidates within 25 m.
ANCHOR_BAR = '#hey_rey_food_01_mp'

# MAMA WELLES SPEAKS A POSITIONAL LINE, so she gets a real anchor near her.
#
# `around_player` does not put the marker on the player: it lands a few metres
# to one side, which is audible for a Vo_Expression_Spoken line and inaudible
# for an inner-dialogue one. `#sq018_pepevodka` is (-1260.510, -1001.310,
# 13.141), 3.0 m from her own captured mark, and its orientation is IDENTITY.
# Two nearer candidates (`#sq018_03d_infinite_drink` at 2.9 m,
# `#q000_kid_01b_vodka_shot` at 3.9 m) were rejected for having real rotations.
ANCHOR_MAMA = '#sq018_pepevodka'

# MAMA WELLES HERSELF, not the marker beside her. This is the reference her own
# vanilla scene uses to acquire her (`spawnSet` entry `mama_welles`), confirmed
# in game by the epilogue acquiring her through it.
#
# NOTHING USES IT. Kept because the fact is worth having written down, with the
# warning attached: addressing her through it from a QUEST node stalled the
# graph on 2026-08-15. Resolving for a scene actor and resolving for a quest
# node are not the same thing.
ANCHOR_MAMA_NPC = '#mama_welles'
