"""Gig 04's own constants: where its files live and what its keys are prefixed
with.

A copy of `tools/gig03/gig03_config.py`, re-pointed. Read `tools/gig01/
gig01_config.py`'s header for why the pattern exists; this one records only
what is different.

WHAT IS DIFFERENT ABOUT THIS GIG. It is the first gig of the mod's own fixer
(`mods/fixer-01`), so it ships no fixer of its own: her contact, her body and
her call record are hers, and this gig names them. It registers itself on her
map icon at launch and adds one to her counter as it closes
(`mods/fixer-01/docs/design.md`, "What a gig of hers does").

The places are below, in the order V meets them: her studio, the stall,
Stamps's couch and his bar, the Claws' van, the room, the street outside it and
the route Bayani runs. Each carries how it was found.

THE NAMES IN THE CODE ARE THE WORKING NAMES. The player meets Maricel and
Reynaldo Manalo; records, facts, files and comments here still say Ligaya
and Bayani. Every name the player reads or hears is in gen_scenes.py and
gen_localization.py.
"""
import os

_TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(_TOOLS)

# ---------------------------------------------------------------------- names
MOD_DIR = 'gig-04-return-ticket'         # the folder under mods\
MOD_NAME = 'return_ticket'               # the folder under mod\ in the archive
LOCKEY_PREFIX = 'cc-g04-'                # every LocKey this gig ships
FACT_PREFIX = 'cc_g04_'                  # every quest fact this gig sets
QUEST_ID = 'cc_g04_return_ticket'        # the journal quest
REDS_MODULE = 'CyberpunkCodes.Gig04'     # see docs/conventions.md

# ---------------------------------------------------------------- her pieces
#
# Read off `tools/fixer01/fixer01_config.py` and `gen_journal.py` rather than
# imported: this gig is a separate mod and must build from its own folder.
# `tools/gig04/gen_journal.py` checks them against hers when her tools are
# present, so a rename on her side stops this gig's run (gotcha 76).
FIXER_ID = 'cc_f01_fixer'
FIXER_CODEX = 'codex/characters/fixers/' + FIXER_ID
FIXER_COUNTER = 'cc_f01_fixer_count'
# SET BY HER GRAPH once V has taken her introduction call. This gig waits on
# it before anything else, so it cannot start for a V she has not met.
FIXER_INTRO_DONE = 'cc_f01_intro_done'
# KEPT BY HER GRAPH: 0 while V is not in her conversation, 1 in person, 2 on
# the phone. This gig's calls wait for 0 before they ring.
FIXER_TALK_MODE = 'cc_f01_talk_mode'
# HER CONTACT'S OWN FIELDS, repeated in this gig's journal so her text can
# hang under her thread whichever of the two journals is merged first
# (gen_journal, "HER TEXT").
FIXER_CONV = FIXER_ID + '_conv'
FIXER_AVATAR = 'PhoneAvatars.Avatar_' + FIXER_ID
FIXER_NAME_KEY = 'cc-f01-fixer-name'
FIXER_CONV_TITLE_KEY = 'cc-f01-fixer-conv-title'
# HER BODY FOR A CALL ON THE STUDIO FLOOR, and her contact for the phone.
FIXER_RECORD = 'Character.cc_f01_fixer'
FIXER_APPEARANCE = 'fixer01'
FIXER_CONTACT = 'contacts/' + FIXER_ID
# THE ID THIS GIG REGISTERS UNDER on her record, in source/scripts.
REGISTER_ID = 'cc_g04'

# THE WAITING SPOT, gig 02's railing (tools/gig02/gig02_config.py, "THE TWO
# WAITING SPOTS"): a place to take under "Wait for Hodan's call", the shape
# of the game's own `wait_for_claire` legs. A railing 48 m west of the
# building's door, outside the drawn circle, captured in game 2026-10-13
# (cc_capture: V stood at the prompt point facing it, the rail 1.56 m
# ahead). PROMPT is where the player stands to be offered it and where the
# map marker sits; POSE is where V's feet end up, 0.2 m from the rail on the
# same line, facing it. It was 0.5 m until playtest 2026-11-01, where V's
# folded arms rested in the air short of the rail; moved 0.3 m along the
# line. Gig04_Places.reds restates it.
RAIL_PROMPT = (-1476.472, 1548.713, 18.180)
RAIL_POSE = (-1477.823, 1548.843, 18.18)
RAIL_YAW = 84.5
# The game's own player pose for leaning forward on a rail, gig 02's.
LEAN_WORKSPOT = ('common', 'rail',
                 'player__stand_rail_lean_front__stand_around__01.workspot')

# HOW NEAR LIGAYA'S STALL V COMES before Hodan rings with the job, once her
# introduction is done, measured flat. And how far V must have been from the
# stall and from Stamps's bar since then first (Stamps is switched on then): Ligaya is switched on as the introduction ends, and
# a person switched on with V nearby does not appear until V has gone about
# 200 m away and come back (gotcha 132). So the call is armed only once V has
# been OFFER_ARM_RADIUS away, and rings as V comes back within OFFER_RADIUS,
# by which time she is there (the design call, 2026-10-13: "If it's
# proximity, trigger the gig from further"). Gig04_Places.reds restates both.
# 50, THE GAME'S OWN DISTANCE, since 2026-10-25 (the design call: "go back
# to the correct vanilla radius around the gig marker"). Wakako's Charter
# Hill gig rings from its start area, a box 96 by 102 m round the building,
# so about 50 m out. It was 150 while Ligaya could be missing at the stall; her
# community is always spawned now and she has been there since.
OFFER_RADIUS = 50.0
OFFER_ARM_RADIUS = 250.0

# THE FEE. source/tweaks/rewards.yaml carries the record.
REWARD = 'QuestRewards.sts_cc_g04_completion'

# ---------------------------------------------------------------------- paths
MOD = os.path.join(REPO, 'mods', MOD_DIR)
SOURCE = os.path.join(MOD, 'source')
RAW = os.path.join(SOURCE, 'wkit', 'raw')
# Where the generators write. Everything under here is generated; the one
# hand-authored file (the .archive.xl) sits beside it in RAW.
RAW_MOD = os.path.join(RAW, 'mod', MOD_NAME)

# The same folder as the engine sees it. A depot path is backslash-separated
# and is NOT a filesystem path. Built from chr(92) because a backslash typed
# into a quoted string in a generated edit gets eaten (gotcha 28). `mod` +
# backslash + `return_ticket` is backslash-r, a carriage return: exactly the
# trap. Never type the folder; join it.
DEPOT = 'mod' + chr(92) + MOD_NAME

# WHERE A HOLOCALL IS STAGED. The scene's own marker, not a place: a call is
# played at the studio rather than wherever the player is standing. Gig 01
# measured the pairing and every gig since uses the same marker.
ANCHOR_STUDIO = '#holocall_marker'

# ----------------------------------------------------- the stall and the booth
#
# CAPTURED IN PLAY, 2026-09-30 (`tools/gig04/captures/`). Ligaya stands
# behind the counter of a Kabuki Market stall, IN THE GAME'S OWN VENDOR'S
# SPOT: the vendor (a `Character.Kiosk_Woman`) is one community of one entry
# with no NodeRef, so the manifest deletes her community node and Ligaya
# takes her place and her facing (playtest 2026-10-01: the vendor stood in
# front of Ligaya).
STALL_LIGAYA = (-1236.688, 1975.171, 7.867, -108.7)
# STAMPS'S SHARD, ON THE SEAT OF HIS COUCH. He is not on the couch any more
# (the design call, 2026-10-01: "Stamps isn't at his couch"); the shard is
# what sends V to the bar. Playtest 2026-10-01: the first build put it at
# the `booth_shard` capture, z 9.416, and it floated in front of the wall
# at eye height. Both captures there (`booth_shard`, `sofa_stamps`) read
# 9.416, which is the standing V's feet plus 1.6 m: the capture tool's ray
# was flat at eye level (fixed in tools/cc_capture/init.lua), so it hit
# the wall behind the couch. The seat is at 8.27: the cushion lying on it
# (`sofa_pillow_a`, exterior_-19_31_0_0 node 2336) stands at 8.27 and its
# mesh's bounds start at its origin. The spot is between the cushion and
# the game's own sitting spot on that seat (-1217.46, 2020.68), on the
# front half; two centimetres up so the case stands on the cushion.
BOOTH_SHARD = (-1217.15, 2020.85, 8.27 + 0.02)

# STAMPS AT THE BAR: a two-stool counter bar with a barkeep on the raised
# walkway west of the market, 200 m from his couch. The stool is the game's
# own crowd seat `master_generic__sit_barstool_bar__sit_around__002`
# (exterior_-11_15_0_1 instance 80), whose position and facing these are;
# the manifest deletes the crowd seat so nobody else sits on him. Picked
# from the bar stools within 400 m of the market (2026-10-01) as the one
# with a barkeep and the fewest people round it: the two nearer ones are
# food courts full of children, and he can be fought here.
BAR_STAMPS = (-1404.26, 1950.77, 23.38, 355.5)


# THE CLAWS' VAN, the false lead: a Tyger Claws van parked in a yard in
# south-west Little China, where they kept Bayani before they moved him to
# the shop. No fight here: V scans three clues round the van and takes the
# Claws' shard off the ground behind it (the design call, 2026-10-13: "how
# about instead of making it a combat vs 3 claws we make it an
# investigation", and "choose a further location, so the gig is a bit
# longer").
# THE PLACE IS A CAPTURE, `putvanhere` in cc_capture, 2026-10-13, at
# (-1739.138, 1214.373, 18.235): the design call, after two searched spots
# failed in play (a lot closed in behind a building, then the middle of a
# road). The van stands 2.6 m east of the captured point, facing east
# (yaw -90, 0 faces +y), so its back doors open onto the point, with
# walkable ground on the meshes under its whole footprint and behind it,
# and nothing overhead.
# 911 m from the market, 809 m from the bar, 446 m from the shop's door.
# THE YARD IS THE GAME'S NCPD ACTIVITY `ma_wat_lch_10` (a homeless man
# runs, a turret fires; homeless people sit here once it is done). Its
# marker is 17 m off and its sitting spots 7 to 23 m; the van and the
# clues keep off them.
VAN = (-1736.5, 1213.0, 18.30, -90.0)
# THE GROUND: the game's own decals in the yard lie at 18.22 to 18.26, and
# the capture stood at 18.235 (the walking mesh is 18.5).
GROUND_Z = 18.22
# The map marker: on the ground at the back doors.
VAN_PIN = (-1740.0, 1213.0, GROUND_Z)
# (name, position, yaw): tools/gig04/gen_clues.py builds each. Each is on
# ground the walking mesh covers; a crate and a pillar stand at
# x -1746..-1742.5, y 1214.5..1217, and are kept clear of.
# THE CUFFS, THE BAG AND THE SHARD ARE CAPTURES (cc_capture, 2026-10-14,
# the design's: `second_clue`, `third_clue`, and `shard` as the spot looked
# at), each at the captured height. The blood stays at the back doors.
# THE CLUE HUNT'S DRAWN AREA, the design's own outline round the three
# clues (`polygongood` in cc_capture, 2026-10-14, in order; the design call:
# "use a polygon instead of a circle"). World (x, y); all three clues and
# the middle of the six points are inside it, checked 2026-10-14.
CLUE_AREA_POLY = [(-1742.348, 1210.871), (-1726.342, 1209.179),
                  (-1725.034, 1223.118), (-1735.164, 1224.936),
                  (-1736.289, 1217.506), (-1741.324, 1218.393)]
CLUES = [
    ('blood', (-1740.6, 1213.0, 18.24), 0.0),
    ('cuffs', (-1727.826, 1216.384, 18.204), 35.0),
    # THE BAG'S ORIGIN IS ITS TOP: the duffel mesh runs from 0.467 m below
    # its origin to 0.015 m above (int_accessories_001__duffel_bag.mesh,
    # read 2026-10-14), so on the captured ground it sat in it (playtest
    # 2026-10-14). Raised by that, plus half a centimetre.
    ('bag', (-1731.573, 1222.038, 18.150 + 0.467 + 0.005), 110.0),
]
# ON TOP OF THE PALLETS beside the van's back doors. The stack there is
# the game's node exterior_-28_19_0_0 #420 (`cargo_pallet_a`, 0.227 m
# tall from its origin, scaled 1.09, so 0.247 m a pallet): two piles of
# four side by side, and a fifth pallet turned 46 degrees on top across
# them, its base at 18.98 and its top at 19.227, centred on
# (-1740.69, 1222.60). Playtest 2026-10-14, first: the captured point was
# in the gap between the stack and the wall. Second, on the west pile's
# top: "a bit towards" the design's `spot1` capture, east of it. Third:
# "almost perfect ... a bit further yet". Fourth, on the turned pallet's
# top at 19.227: floating (playtest 2026-10-14, "down a bit in height and
# more on the same direction ... at the edge of the lumber"), so the
# turned pallet is not where its instance says, or not there. So on the
# east pile's top pallet (instance at (-1740.42, 1222.60, 18.73), top face
# 18.977, east edge at x -1739.75), 0.3 m in from that edge; a centimetre
# up so the case stands on it.
# Fifth, there at 18.987: "too low ... should be a bit higher", seen
# between the decks of the turned pallet, which is there after all; the
# fourth's floating was the case over one of the deck's oval holes. So on
# the turned pallet's top at 19.227, 0.24 m and 0.37 m inside its edges.
VAN_SHARD = (-1740.05, 1222.62, 19.227 + 0.01)

# ORBITAL AIR ARRIVES as V finishes talking to Bayani (the design call,
# 2026-10-01: "no choices, just fight"). ONE CAR AND THREE GUARDS since the
# design call of 2026-10-02 ("let's diminish to 3 goons, 1 car"), the three
# on flat pavement at 18.40: the ramp spot at 19.18 is gone. In the room's
# frame, on the street outside the door: the guards on the walking mesh 5
# to 14 m out and spread at least 4 m apart, the cars on the driving mesh
# with their centres at least 5 m from Bayani's route (picked by script
# from the vanilla navigation tiles, 2026-10-01); a car's body reaches to
# about 3.8 m of it, and the nearest guard stands 3 m off it. The guards
# face the door.
# MOVED OUT, playtest 2026-10-01 ("they are inside walls"): the first
# eight stood 3.5 to 5 m from the front, with 0.8 m of mesh round them,
# and from inside read as standing in the wall. Now 6 to 17 m out, at
# least 6 m from the front line, with 1.5 m of walking mesh all round.
# EACH WITH ITS OWN HEIGHT, read off the walking and driving tiles at that
# point (audit 2026-10-01): until then every street spot took the door's
# 18.19, which put them 0.2 m under the pavement and the third guard, on a
# ramp, a metre under it.
# ON THE STRIP OF PAVEMENT ALONG THE FRONT, v -4.5 to -7.5: past it is a
# kerb and the road, 2.7 m higher at about 21.1. Under that road the
# walking mesh has a second floor at 18.4, and the third guard stood on it
# (playtest 2026-10-02: "guards from orbital are still under the road",
# seen as outlines through the road surface). Every spot below has 1.5 m of
# 18.4 floor round it and no floor between 18.7 and 26 above it, read off
# the shipped navigation file; the car's whole footprint too.
OA_CARS = [('oacar1', -5.5, -6.0, 18.40, 90.0)]
# THE PAVEMENT'S HEIGHT outside the door, off the walking tiles, for the
# room's entries that stand on the street (gen_community).
STREET_Z = 18.40
# THE GUARDS WAIT OUTSIDE, OUT OF SIGHT, and run in on V's line (the design
# call, 2026-10-25: "they appear where the player cannot see them, then
# become hostile and ... run inside"). (u, v, z, room yaw), each facing the
# door. The pavement against the front wall is not on the game's walking
# mesh except a funnel in front of the door; from 3 m out a strip runs the
# whole frontage (read off the built mesh, 2026-10-25, scratch
# street_map.py). The three spots are in that strip, 4 m out: from anywhere
# V can be when they appear (within 2.6 m of Bayani in the cell), the view
# through the 3 m street door at that depth covers about u -3.4 to +2.0, so
# each is a metre or more outside it, and clear of the car (OA_CARS).
# Until 2026-10-25 they appeared in the lobby, seen from the cell; started
# on the street before that and turned on V there, they stayed outside
# (playtest 2026-10-14), which is what OA_PATHS is for.
OA_GUARDS = [(-6.0, -4.0, 18.40, 63.0), (-8.5, -4.0, 18.40, 71.0),
             (4.0, -4.0, 18.40, -53.0)]
# THEIR WAY IN, one path each in the room frame, from the spot along the
# strip, up the funnel, through the door, to the lobby spots they used to
# appear on. The quest sends each along his at a sprint on V's line
# (gen_room OA_PATH_REFS). Every point and the line between each pair is on
# the walking mesh at the pavement's or the floor's height (2026-10-25).
OA_PATHS = [
    [(-6.0, -4.0), (-2.5, -3.0), (-0.5, -1.0), (-0.5, 1.0), (-3.5, 2.5)],
    [(-8.5, -4.0), (-3.0, -3.5), (0.0, -1.5), (0.0, 1.0), (0.0, 3.0)],
    [(4.0, -4.0), (2.5, -3.0), (0.5, -1.0), (0.5, 1.0), (3.5, 2.5)],
]
# How close V has to be for each conversation to be offered, and how far
# before it is withdrawn: the fixer's numbers.
TALK_RADIUS = 6.0
# BAYANI'S TWO, closer: at 6 m his first was offered through the cell's
# wall from the hall (playtest 2026-10-14). The cell door's middle is
# 2.5 m from where he sits, so 2.6 m is V in the doorway. Orbital Air is
# switched on at the same distance, with V inside the cell and the lobby
# out of sight (gen_questphase).
BAYANI_TALK_RADIUS = 2.6
# His goodbye, where his walk ends in the hall.
BYE_TALK_RADIUS = 3.5
LEAVE_RADIUS = 14.0

# ------------------------------------------------------------------ the room
#
# THE ROOM IS OURS. No free, full interior exists in Watson (every one belongs
# to a gig, a quest or a police event, and every gig shuts its building when
# it ends; read out of all 23 Watson gigs' phases on 2026-09-30), so the gig
# builds one: a fake door in Little China, captured in play (`inactive_door`),
# is set into a building shell 19 m deep with nothing modelled inside. The
# fake door goes, a real door of the same look goes in its place, and behind
# it tools/gig04/gen_room.py lays a floor, walls, a ceiling, lights and the
# collision that makes them solid.
#
# The door's own placement, from the capture and confirmed against the
# sector (exterior_-23_24_0_0, instance 451: a `double_door_decorative.ent`
# in appearance `doors_double_kitsch_g`, yaw -5.0). Its z is the threshold.
ROOM_DOOR = (-1429.882, 1536.773, 18.193, -5.0)
# THE ROOM FRAME. u runs along the front wall to the right when facing into
# the building, v runs from the door line into the building.
# gen_room.room_to_world converts. The floor is the door's threshold height.
#
# YAW IN THE ROOM FRAME: 0 faces +v (deeper into the building), 90 faces +u
# (to the right), 180 faces the door, 270 faces the left wall. A prop's own
# front (a sofa's seat side, +Y of its mesh) faces the same way as a person
# standing with that yaw. (Until 2026-10-01 this said 0 faced the door; it
# does not, Bayani stood facing the back wall.)
#
# THE BUILDING. The shell's inside, read off its occlusion box (gotcha 127),
# is u -35..13, v 1.6..19.4, 6 m tall. The gig uses u -18..6 and v 0..18 of
# it, split into three spaces:
#   the LOBBY behind the street door, u -6..6, v 0..5, open to the hall
#     through a 3 m gap in its back wall;
#   the HALL, an L: the lobby's left (u -18..-6, v 0..5) and everything
#     behind the lobby (u -18..6, v 5..18), with couches along the left
#     wall for the Claws;
#   the CELL at the back right, u 1..6, v 13..18, with its own single door
#     in its front wall, where Bayani is kept.
ROOM_HEIGHT = 3.6      # the ceiling; the wall pieces are 3.8 tall
# THE HALL STOPS AT u -13.6: the shell has a wall of its own running the
# whole depth at u -13.9 (`backwall_b_gf_900_door_a` and `_tiles_a`, read
# off exterior_-6_5_0_2 on 2026-10-01 after the playtest saw its barred
# windows from the hall), and anything placed past it is behind it.
ROOM_U = (-13.6, 6.0)
ROOM_V = (0.0, 18.0)
LOBBY_U = (-6.0, 6.0)
LOBBY_V = (0.0, 5.0)
LOBBY_GAP = (-2.5, 0.5)     # the opening in the lobby's back wall, in u
CELL_U = (1.0, 6.0)
CELL_V = (13.0, 18.0)
CELL_DOOR = (2.28, 3.96)    # the gap in the cell's front wall, in u: the
                            # single door's frame is 1.66 m across, 2.30 to
                            # 3.96 (gen_room cell_door_place). The gap began
                            # at 2.2, which left a 10 cm strip of open air
                            # beside the frame (playtest 2026-10-25,
                            # screenshot); 2.28 tucks the wall 2 cm behind it.
# WHERE PEOPLE STAND, (u, v, yaw). Bayani sits on the cell's floor with
# his back to its left wall, facing the room (the design call, 2026-10-01:
# "on the floor when we find him"); he gets up for his talk, which is what
# a scene does with an actor it takes out of a workspot.
# 0.9 m off the wall: the pose's origin is the hips and the back leans
# 0.4 m behind them, and the wall's body is 0.23 m inside its line
# (playtest 2026-10-01, "the brother is inside a wall").
ROOM_BAYANI = (1.9, 15.2, 90.0)
# THREE CLAWS, the whole crew: one outside the street door, one just inside
# it in the lobby, one deep in the hall (the design call, 2026-10-14: "1 tiger guard outside only.
# 2 inside. That's it. That's the total"). Eight until then, five of them on
# the couches and on their feet further in.
# (name, u, v, yaw, pose); room yaw 180 faces the street door.
# THE TWO CLAWS BY THE DOOR ARE SWITCHED ON only within this many metres of
# Bayani, so the game places them apart from him and the hall Claw
# (gen_questphase, "THE ROOM'S CLAWS IN TWO GROUPS"; a test).
ROOM_SECOND_GROUP = 120.0
ROOM_CLAWS = [
    ('claw1', -1.8, -2.5, 180.0, 'guard'),   # street, left of the door, facing out
    ('claw2', 3.0, 3.5, 180.0, 'guard'),     # the lobby, right of the door, facing it
    # deep in the hall by the couches, facing the cell (the design call,
    # 2026-10-14: "the second one add it more inside")
    ('claw3', -8.0, 14.5, 90.0, 'stand'),
]
# HOW FAR FROM BAYANI "leave the area" is drawn, in metres, in plan.
ROOM_LEAVE_RADIUS = 28.0
# WHERE BAYANI RUNS TO after his talk: out of the cell, the hall and the
# street door, then 820 m through Little China to his sister's stall in
# Kabuki market, where he stops 3 m in front of her. The route is a spline
# the room sector ships (gen_room.LEAVE_PATH) and the quest sends him along
# it with the game's own patrol order; Gig04_Places.reds opens the two
# doors first. A second community phase was tried and respawned him a few
# steps in; a scripted move order turned him and he vanished (2026-10-01).
#
# The part inside the building is in the room's frame. The street is world
# metres: 36 points walked and captured in play (2026-10-01, the capture
# tool), three of them dropped (one off the mesh, two of a detour), and 22
# more computed along the game's own navigation mesh where a straight line
# between two captures crossed ground the mesh does not cover (a plaza of
# planters, the ramps down to the market, the alley behind it, the stall's
# front); the whole route was checked against the mesh metre by metre.
# BAYANI'S TWO STANDING SPOTS, (u, v, yaw), each an AI spot of the cast
# community with the plain standing idle (gen_community). Gig04_Places.reds
# sends him to each with the AI's own use-workspot command, which walks him
# there, plays the pose's way in and holds him in it: no patrol order whose
# end has to be heard (playtest 2026-10-14, twice: a patrol's Success never
# came, and a second patrol sent while he sat waited through the fight and
# then overrode the next one).
# IN THE CELL BY ITS DOOR, from the end of his first talk until Orbital Air
# is down (the design call, 2026-10-14: "he should already get up when he
# says that he can get up, but stay inside the room"), facing the door.
ROOM_BAYANI_STAND = (3.1, 14.4, 180.0)
# IN THE HALL, behind the lobby's opening where the fight was, for his
# goodbye ("a final scene with the brother approaching V"), facing the
# lobby. The leave route passes through it, so his run carries on from it.
ROOM_BAYANI_BYE = (-1.0, 6.5, 180.0)
# Within this of the hall spot he is there, and his goodbye is offered
# (Gig04_Places.reds, ByeSpot).
BYE_ARRIVED = 1.5
# HIS WALK TO THE HALL, a path from the cell spot to the hall spot: the
# first leg of ROOM_LEAVE_ROUTE, cut at ROOM_BAYANI_BYE. The quest sends him
# along it with the patrol order his run uses (gen_room BYE_PATH_REF), once
# Orbital Air is down. On the walking mesh point by point (2026-10-25).
ROOM_BYE_PATH = [(3.1, 14.4), (3.1, 12.2), (-1.0, 9.0), (-1.0, 6.5)]
ROOM_LEAVE_ROUTE = [
    (3.1, 14.4), (3.1, 12.2), (-1.0, 9.0), (-1.0, 5.0), (0.0, 2.0),
    (0.0, -3.5),
]
LEAVE_ROUTE_WORLD = [
    (-1415.084, 1538.521, 18.180), (-1403.626, 1539.763, 18.180),
    (-1400.314, 1548.022, 18.180), (-1394.755, 1552.643, 18.200),
    (-1393.756, 1580.412, 18.200), (-1385.828, 1591.603, 18.000),
    (-1375.294, 1605.386, 18.200), (-1371.193, 1632.067, 18.208),
    (-1370.052, 1649.397, 18.205), (-1368.864, 1665.844, 18.197),
    (-1365.093, 1691.045, 18.192), (-1363.924, 1714.464, 18.200),
    (-1363.011, 1736.189, 18.200), (-1343.830, 1739.597, 18.190),
    (-1309.515, 1736.163, 18.190), (-1286.145, 1730.918, 18.208),
    (-1264.820, 1734.037, 20.177), (-1239.253, 1738.358, 23.234),
    (-1224.988, 1744.385, 23.034), (-1211.202, 1744.333, 23.034),
    (-1204.733, 1746.372, 23.234), (-1201.185, 1772.150, 23.421),
    # the plaza of planters, along the mesh
    (-1202.57, 1775.47, 23.50), (-1200.13, 1778.90, 23.50),
    (-1201.13, 1784.83, 23.80), (-1199.57, 1792.83, 23.80),
    (-1197.83, 1794.63, 23.60), (-1193.50, 1794.17, 23.70),
    (-1193.436, 1798.250, 23.374), (-1197.346, 1822.285, 23.511),
    (-1199.862, 1842.649, 22.504),
    (-1199.87, 1849.57, 22.60), (-1202.30, 1853.47, 22.60),
    (-1196.23, 1864.03, 22.60),
    (-1196.474, 1866.702, 22.504), (-1182.239, 1886.039, 18.549),
    (-1165.577, 1906.176, 14.215), (-1161.264, 1933.452, 12.025),
    # the walk north to the market, along the mesh
    (-1164.70, 1934.73, 12.10), (-1165.53, 1937.43, 11.90),
    (-1166.30, 1984.27, 12.10), (-1166.10, 1988.77, 12.20),
    (-1160.678, 1992.730, 12.067), (-1146.461, 1998.196, 12.023),
    (-1137.534, 2009.060, 11.960), (-1148.871, 2028.590, 11.979),
    (-1162.807, 2017.424, 7.763),
    # the alley behind the market, along the mesh
    (-1165.73, 2018.83, 8.00), (-1174.07, 2013.87, 8.00),
    (-1177.93, 2015.80, 8.00), (-1183.73, 2013.00, 8.00),
    (-1193.17, 2020.00, 8.00), (-1205.57, 2022.13, 8.00),
    (-1210.77, 2021.43, 8.00),
    (-1218.967, 2011.264, 7.482), (-1223.948, 1990.995, 7.922),
    (-1225.10, 1988.60, 8.00), (-1229.83, 1986.63, 8.00),
]
# WHERE HE STOPS: 3 m in front of Ligaya at her stall, facing her
# (STALL_LIGAYA, yaw -108.7, faces +x and a little south).
LEAVE_END = (-1233.8, 1974.2, 7.87, 71.3)
