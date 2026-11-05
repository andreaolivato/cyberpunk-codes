"""Gig 05's own constants: where its files live, what its keys are prefixed
with, and every place the first shift uses.

A copy of `tools/gig04/gig04_config.py`, re-pointed. Read `tools/gig01/
gig01_config.py`'s header for why the pattern exists; this one records only
what is different.

WHAT IS DIFFERENT ABOUT THIS GIG. It repeats. V signs on with Trauma Team
once, then works shifts: board the AV, fly to an incident, fight beside the
crew while the medic works on the client, fly back. The design is
`mods/gig-05-trauma-team/docs/design.md`; the desk research behind the AV
and the crew is `docs/gig05-av-research.md`.

NO FIXER. Trauma Team hires V directly, so this gig needs no other mod of
ours.

THE NAME IS TRAUMA TEAM (the design call): the folder, the depot names
and the title the player reads.

EVERY PLACE BELOW IS THE GAME'S OWN, read off its sectors on 2026-11-03,
because nothing has been captured in game yet. Where the game lands a Trauma
Team AV, an AV fits and the sky above is clear; where the game stands a
guard, there is floor. Each is to be checked in the first playtest and
replaced by a capture if it is wrong.
"""
import math
import os

_TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(_TOOLS)

# ---------------------------------------------------------------------- names
MOD_DIR = 'gig-05-trauma-team'           # the folder under mods\
MOD_NAME = 'trauma_team'                 # the folder under mod\ in the archive
LOCKEY_PREFIX = 'cc-g05-'                # every LocKey this gig ships
FACT_PREFIX = 'cc_g05_'                  # every quest fact this gig sets
QUEST_ID = 'cc_g05_trauma_team'          # the journal quest
REDS_MODULE = 'CyberpunkCodes.Gig05'     # see docs/conventions.md

# ---------------------------------------------------------------------- paths
MOD = os.path.join(REPO, 'mods', MOD_DIR)
SOURCE = os.path.join(MOD, 'source')
RAW = os.path.join(SOURCE, 'wkit', 'raw')
# Where the generators write. Everything under here is generated; the one
# hand-authored file (the .archive.xl) sits beside it in RAW.
RAW_MOD = os.path.join(RAW, 'mod', MOD_NAME)

# The same folder as the engine sees it. Built from chr(92), never typed
# (gotcha 28).
DEPOT = 'mod' + chr(92) + MOD_NAME


def heading(a, b):
    """The game's yaw for facing from a to b: 0 is +Y, and a heading of yaw
    faces (-sin, cos)."""
    return math.degrees(math.atan2(-(b[0] - a[0]), b[1] - a[1]))


def ahead(p, yaw, forward, left=0.0, up=0.0):
    """A point `forward` metres ahead of p along yaw and `left` metres to its
    left. Forward is (-sin, cos), left is (-cos, -sin)."""
    r = math.radians(yaw)
    return (p[0] - math.sin(r) * forward - math.cos(r) * left,
            p[1] + math.cos(r) * forward - math.sin(r) * left,
            p[2] + up)


# THE GRAB BAR OVER V'S HAND, in the AV's own frame: (x across, y along, z up).
# The game's shuttle handle, 1.08 m long on its own z, the bar 0.17 m out from
# its mounts on its own y. The mounts lean 70 degrees out from straight up, so
# their blocks meet the pipe over the door and the bar is in V's fist, at
# (-1.1, 1.95) across and up. Fitted live from CET in flight, playtest 2026-11-05:
# at (-0.86, 2.22) the fist closed on air, and mounts straight up left the blocks
# hanging under the ceiling.
RAIL_A = (-1.26, -0.79, 2.008)
RAIL_LEAN = 70.0
# Brekke's offset on V's place: 1.35 m across the cabin, clear of V's raised arm.
# The place is turned 45 degrees, so that is (0.95, -0.95) in its own frame.
BOSS_OFFSET = (0.95, -0.95, 0.0)

# ------------------------------------------------------------ the recruiter
#
# CAREER OPPORTUNITIES' SPOT. The game stages its two Trauma Team people for
# the hand scan here, outside the Night City Medical Center in Little China:
# community `#mws_wat_08_com_trauma_team` in always_loaded_2 at (-1333.8,
# 1745.1, 18.2), its two workspots at (-1333.5, 1744.4) and (-1335.3,
# 1743.9), and a trigger that keeps cars out round them
# (`tools/_sector_cache/index_mws_wat_08.json`). The recruiter stands on the
# second workspot. Her facing is a guess, toward the street to the west.
RECRUITER = (-1335.3, 1743.9, 18.2, 90.0)
TALK_RADIUS = 6.0
LEAVE_RADIUS = 12.0

B = chr(92)

# ------------------------------------------------------------------ the pad
#
# THE MEDICAL CENTER'S TOP ROOF, flat at 128.9 from x -1395 to past -1315
# and y 1739.4 to 1825 (traced in game, 2026-11-03). Playtest 2026-11-03: the
# first pad, the AV deck at 118.2, is one floor below the building to its
# east, and the AV came home through that building. The roof has nothing on
# it. The way up and down is the game's own lift on its south edge (below).
# The AV faces west, the way it leaves.
# THE FLOOR OF THE ROOF IS THE GIG'S OWN, an invisible slab at ROOF_Z on the
# surface V sees (gen_community.py, ROOF_FLOOR). The game's collision is
# 128.86 and the roof it draws is above that, so V and the crew stood in it
# (playtest 2026-11-04). On the slab everything stands where it looks.
ROOF_Z = 129.2
ROOF_BOX = (-1395.0, 1739.4, -1309.0, 1825.0)
PAD = (-1362.0, 1785.0, ROOF_Z)
PAD_YAW = 90.0
# THE GAME'S LIFT, a glass car in the tank yard east of the building, open sky
# to well over the roof (rays, 2026-11-04). The yard is the only place near the
# roof that V can walk to: every clear column under the roof's own edge is in the
# unlit hollow inside the building, behind a wall drawn only from the yard side
# and solid from both. Its door is its front, opposite its wall of screens; yaw
# -90 puts that south, on the yard's open floor at the bottom and on the walkway
# at the top. North of the car are stairs and a machine, west of it the tanks.
LIFT_XY = (-1261.5, 1769.0)
LIFT_LOW = 18.2
LIFT_YAW = -90.0
# THE CALL PANELS, right against the door, 1.4 m up, the way the game's own lifts
# have them (flights/lift_vanilla.json: 1.6 m to the side of the car's centre line,
# on the door's wall). The car's door is 2.4 m wide. The street's panel is on a post
# of its own at the door's east edge, since nothing else stands still there. A
# panel's front is its own +x at yaw 0, so yaw -90 faces south.
# THE FLOOR NAMES ARE THE GAME'S OWN, from the keys its lifts use, so they come
# translated. Plain text drew a blank button.
LIFT_PANEL_STREET = ((-1259.9, 1765.66, LIFT_LOW + 1.4), -90.0)
LIFT_PANEL_ROOF = ((-1262.78, 1765.81, ROOF_Z + 1.4), -90.0)
# THE WALKWAY, the roof's edge to the car: gig 04's interior kit, 3 m wide, from
# the east edge of the roof along the car's south side. The north wall stops short
# of the car's door. The kit is drawn from inside only, so a closed skin of plates
# goes round it, and it brings no collision, so gen_community adds boxes.
WALK_Y = (1762.9, 1765.9)
WALK_X = (-1309.0, -1258.6)
WALK_DOOR_X = -1264.6
# THE ROOF DOOR, between the walkway and the shaft, centred on the car: gig 04's
# sliding single door, 1.66 m wide. It stays locked while the car is away. A
# swinging door covered the call panel.
ROOF_DOOR_GAP = (LIFT_XY[0] - 0.83, LIFT_XY[0] + 0.83)
# THE SILL across the gap from the walkway to the car's floor.
ROOF_SILL_Y = 1766.45
# THE LOCKER ROOM, on the roof at the walkway's west end: V passes through it on
# the way to the pad. 12 m square, in gig 04's kit. The door to the roof is in its
# west wall, in line with the walkway. LOCKER is the spot of the Get changed prompt,
# at the shelf of helmets and the team's shirts on the south wall.
ROOM_X = (-1321.2, -1309.2)
ROOM_Y = (1759.4, 1771.4)
ROOM_DOOR_GAP = (1762.9, 1765.9)
ROOM_WAY_IN = (1763.57, 1765.23)
LOCKER = (-1311.5, 1761.0, ROOF_Z)
# THE TOWER the car runs in, street to over the roof: four columns beside the car,
# ring beams, a cap. The car is 5.8 m square.
TOWER_X = ((-1265.2, -1264.5), (-1258.5, -1257.8))
TOWER_Y = ((1766.0, 1766.7), (1772.0, 1772.7))
TOWER_TOP = ROOF_Z + 6.8
TOWER_RINGS = (40.0, 60.0, 80.0, 100.0, 120.0)
# THE KEYS OF THE PANELS' SAVED STATE (`.psrep`), one per stop: what the game
# returns for `PersistentID.ForComponent(entEntityID.new({hash = <node hash>}),
# CName.new('controller')):ToHash()`, asked from CET. They follow from the node
# refs, so renaming a panel changes them. The same call gives the file's own value
# for the vanilla lift_terminal_1.
LIFT_PANEL_PSIDS = ('7765168748376870615', '8088881893561053928')
LIFT_STOPS = [((LIFT_XY[0], LIFT_XY[1], LIFT_LOW), LIFT_PANEL_STREET[0], LIFT_YAW,
               LIFT_PANEL_STREET[1], 'LocKey#49249'),
              ((LIFT_XY[0], LIFT_XY[1], ROOF_Z), LIFT_PANEL_ROOF[0], LIFT_YAW,
               LIFT_PANEL_ROOF[1], 'LocKey#49250')]
# The AV's open side. V's standing slot, `player_standing`, is at (-1.25,
# -1.06) in the AV's own frame (`av_trauma.ent`), so the door is on the
# left. The prompt is 3.5 m out from it.
PAD_BOARD = ahead(PAD, PAD_YAW, -1.0, left=3.5)
# Where V stands at the door to board, and where V steps off after the last
# call: past Brekke, on the side he looks at. Beside the door V got his back.
PAD_DOOR = ahead(PAD, PAD_YAW, -1.0, left=2.6)
PAD_OUT = ahead(PAD, PAD_YAW, -1.0, left=8.4)
# Brekke speaks as V comes this near him on the roof.
GREET_RADIUS = 7.0
# THE CREW WAIT BY THE DOOR before a shift, on the slab (ROOF_Z), each in a
# standing pose, which holds him at the height written.
# Brekke faces the door and V steps off facing him (gen_community, PAD_OUT);
# the other two stand either side, clear of the door.
PAD_SKIN = 0.0
PAD_CREW = {
    # THE STANDING POSE FACES AWAY FROM ITS SPOT'S YAW, so these are the way each
    # man looks plus 180. Brekke looks at the AV's door, at V stepping off.
    'lead': ahead(PAD, PAD_YAW, -1.0, left=5.6, up=PAD_SKIN) + (PAD_YAW + 90.0,),
    'soldier': ahead(PAD, PAD_YAW, -5.0, left=3.4, up=PAD_SKIN) + (PAD_YAW + 90.0,),
    'medic': ahead(PAD, PAD_YAW, 3.0, left=3.4, up=PAD_SKIN) + (PAD_YAW + 90.0,),
}

# ---------------------------------------------------------------- the sites
#
# THREE CALLS A SHIFT (the design call, 2026-11-03): the AV goes from one
# call to the next and home after the third. Each site has the AV's spot and
# facing, the client, the medic kneeling at him, the two posts (the soldier
# at the AV's door, the lead free), and five Scavs.
#
# THE CREW'S ORDERS, the design call of 2026-11-03: Raman kneels at the
# client and does not fight; Wrona holds at the AV and shoots from there;
# Brekke goes after the Scavs with V.


def _site(name, av, yaw, client, scavs, lead, depart=None, soldier_z=None):
    """`yaw` is the way the AV faces when it lands, `depart` the way it
    faces to take off (the same when not given). The AV is turned between
    the two in the fade as V boards."""
    depart = yaw if depart is None else depart
    to_av = heading(client, av)
    medic = ahead(client, to_av, 1.1)
    out = ahead(av, yaw, -1.0, left=2.6)
    mid = (sum(p[0] for p in scavs) / len(scavs), sum(p[1] for p in scavs) / len(scavs))
    # THE SOLDIER'S POSE HOLDS HIM AT THE HEIGHT WRITTEN, so it is the ground's
    # there, not the AV's. Playtest 2026-11-04: at the street call the kerb
    # under him is 17 cm above the AV's spot, and his boots were under it.
    soldier = ahead(av, yaw, 0.0, left=4.2)
    soldier = soldier[:2] + (soldier_z if soldier_z is not None else soldier[2],)
    return {
        'name': name, 'av': av, 'yaw': yaw, 'depart': depart,
        'board': ahead(av, yaw, -1.0, left=3.5),
        # Where V is stood in the boarding fade, at the door of the AV
        # turned for takeoff, facing it.
        'step_in': ahead(av, depart, -1.0, left=2.6) + (depart - 90.0,),
        'out': out,
        # V STEPS OFF FACING THE SCAVS, weapon out (playtest 2026-11-03:
        # stepped off facing away from the door, V was shot turning round).
        'out_yaw': heading(out, mid),
        'client': client + (to_av,),
        'medic': medic + (heading(medic, client),),
        'soldier': soldier + (yaw + 90.0,),
        'lead': lead + (heading(lead, scavs[0]),),
        'scavs': [p + (heading(p, av),) for p in scavs],
    }


# A HOTEL ROOF, where the game's own street story `sts_cct_dtn_04` lands an
# AV: the end of `dtn_04_spl_av_arrive` in `quest_3172ae34a552dccd`. The
# Scavs stand on that story's own security spots on the lower roof.
SITE1 = (-2148.7, 477.7, 95.8)
SITE1_YAW = heading((-2126.6, 492.2), SITE1)
# A STREET BY THE COAST, open-world Trauma Team intervention 17: open sky
# 90 m to the north, open street 140 m to the east, the sea west (traced in
# game, 2026-11-03). The AV comes down from the north, its door east.
SITE2 = (-2370.2, 419.2, 8.7)
# The community of the game's Trauma Team scene on that spot, in its two prefabs.
_CALL2 = '$/03_night_city/#c_city_center/downtown/dtn_cs_prefab73SWZKQ/'
CALL2_VANILLA_CREW = [
    _CALL2 + 'cs_trauma_team_intervention_openworld_001_prefabJ5BXOCY/cs_trauma_team_intervention_com',
    _CALL2 + 'cs_trauma_team_intervention_openworld_prefabJ5BXOCY/cs_trauma_team_intervention_com',
]
# A STREET IN KABUKI, intervention 12: open 50 m to the west, a 43 m
# building past that.
SITE3 = (-1971.5, 1213.5, 8.9)
# WHICH WAY EACH AV COMES IN AND GOES OUT, from the dev menu's glide probe
# (`flights/route_glide.txt`, 2026-11-03): rays from 2.5 m over each spot,
# every 10 degrees round, at climbs of 8 to 50 degrees, out to 260 m.
# The street by the coast is shut in on three sides: open along the street
# to the east-south-east at any angle. So the AV comes in along the street
# over the client, and is turned round in the boarding fade to leave the
# same way. The Kabuki street is open only
# from the north-north-west round by the west to the south-south-west, at
# 22 to 28 degrees: the AV comes in from the south-south-west and leaves
# to the north-north-west. The hotel roof is open over 230 degrees and
# the pad all round.
# THE HOTEL TO THE STREET IS ONE STRAIGHT LINE, the AV turned in the
# boarding fade to face the street: up 6 m off the roof, then down at 25
# degrees, which the street's open side takes (glide probe, open at 17 and
# 28 degrees). Playtest 2026-11-03: a loop south of the hotel to come in
# lower flew through a tower at 126 m (the clearance log).
SITE1_DEP = heading(SITE1, SITE2)
SITE2_IN, SITE2_OUT = SITE1_DEP, SITE1_DEP + 180.0
SITE3_IN, SITE3_OUT = -30.0, 24.0
SITES = [
    _site('site1', SITE1, SITE1_YAW, (-2142.4, 478.6, 95.5),
          [(-2161.5, 460.6, 94.5), (-2160.6, 449.3, 94.5), (-2164.3, 472.0, 94.5),
           (-2172.2, 449.6, 94.5), (-2132.6, 472.9, 94.5)],
          (-2151.9, 482.4, 95.7), depart=SITE1_DEP),
    _site('site2', SITE2, SITE2_IN, (-2361.2, 419.2, 8.5),
          [(-2354.6, 410.2, 8.1), (-2347.7, 406.2, 8.1), (-2344.2, 419.2, 7.3),
           (-2347.7, 432.2, 7.7), (-2354.6, 428.2, 8.0)],
          (-2364.0, 425.0, 8.6), depart=SITE2_OUT, soldier_z=8.9),
    _site('site3', SITE3, SITE3_IN, (-1971.5, 1222.5, 8.9),
          [(-1971.5, 1231.5, 9.7), (-1980.5, 1229.1, 9.0), (-1971.5, 1239.5, 10.0),
           (-1984.5, 1236.0, 9.0), (-1958.5, 1236.0, 10.0)],
          (-1977.0, 1219.5, 8.9), depart=SITE3_OUT, soldier_z=8.95),
]
SCAV_RECORDS = [('scav1', 'Character.cc_g05_scav_pulsar'),
                ('scav2', 'Character.cc_g05_scav_copperhead'),
                ('scav3', 'Character.cc_g05_scav_shotgun'),
                ('scav4', 'Character.cc_g05_scav_slaughtomatic'),
                ('scav5', 'Character.cc_g05_scav_wrench')]
# The first site under its older names, for the dev menu.

# -------------------------------------------------------------- the flights
#
import flight_paths  # noqa: E402

# Four paths a shift: pad to the first call, call to call, and the last call
# home (questkit.avflight). The long legs cruise high (420 m: playtest
# 2026-11-03, lower the AV ran along towers in City Center). Each landing's
# last 14 m are nearly flat, the game's own landing shape
# (`wat_ich_01_spl_av_spawn`): dropping at 45 degrees, the AV stood tipped.
#
# HOME COMES IN OVER THE OPEN ROOF FROM THE EAST, heading west, so it faces
# the way the next shift leaves.
_ARC_OUT = flight_paths._dubins((-1386.0, 1785.4), (-1.0, 0.0), (-1489.0, 1686.0),
                                (-0.637, -0.771), 70.0)
ROUTE_OUT = [
    PAD,
    (-1366.0, 1785.0, 129.2),
    (-1376.0, 1785.3, 132.0),
] + [
    # THE FIRST TURN AS AN ARC, 70 m round. Playtest 2026-11-04 (the flight
    # log): laid as a corner over the roof's west edge, the AV swung 62 degrees
    # a second there.
    (x, y, 138.0 + 69.0 * i / len(_ARC_OUT))
    for i, (x, y) in enumerate(_ARC_OUT) if i % 3 == 0
] + [
    (-1489.0, 1686.0, 207.0),
    (-1560.0, 1600.0, 280.0),
    (-1700.0, 1440.0, 420.0),
    (-2000.0, 1250.0, 420.0),
    (-2250.0, 950.0, 330.0),
    (-2200.0, 700.0, 200.0),
    (-2120.0, 600.0, 130.0),
    (-2110.0, 530.0, 110.0),
    (-2126.6, 492.2, 102.5),
    # FLAT BY THE END: the AV's nose follows the path's last slope all the way
    # along (the flight log: a steady tilt to 19 degrees by touchdown here).
    ahead(SITE1, SITE1_YAW, -14.0, up=1.2),
    SITE1,
]
# THE OTHER THREE FLIGHTS ARE FLOWN BY HAND. Playtest 2026-11-03: laid by
# hand at 100 to 300 m they ran through buildings. The tester flew each leg
# with a flying cheat while the dev menu's flight recorder wrote the line
# (tools/gig05/flights/). flight_paths.py keeps the middle of each
# recording at one cruise height, and puts the first flight's straight
# takeoff and landing on each end, at the slopes the glide probe found
# open, joined to the recording by turns no tighter than 90 m.

# Each leg is the one the dev menu's path probe found clear of the
# buildings (tools/gig05/route_candidates.py, read_hits.py; the hits are
# kept in flights/route_hits_N.txt).
ROUTE_12 = flight_paths.route('flight_rec_1.txt', SITE1, SITE1_DEP, SITE2, SITE2_IN,
                              climb=0.42, out_len=30.0, descent=0.3, in_len=190.0)
# OUT OF THE COAST STREET THE WAY THE AV CAME IN, back along the street
# towards the hotel, at 26 degrees: the street is measured open to 28
# degrees for 260 m (the glide probe), and the AV is over the hotel's roof
# at about 120 m before it turns north onto the recording. Playtest
# 2026-11-03 (the clearance log): out along the street at 7 degrees and
# turning north, the AV went through the hotel's tower at 52 to 66 m; out
# through the gap to the north-north-west it brushed a structure over the
# gap at 20 and at 26 degrees and street furniture under it at 7.
# THE LAST 180 m AT 27 DEGREES, the top of what the street leaves open. Playtest
# 2026-11-04: at 24 degrees the AV brushed something near the end.
ROUTE_23 = flight_paths.route('flight_rec_5.txt', SITE2, SITE2_OUT, SITE3, SITE3_IN,
                              climb=0.5, out_len=250.0, descent=0.52, in_len=180.0,
                              turn=50.0, cap=False)
# LEAVING KABUKI THE TESTER'S WAY: 40 m out to the north-north-west, then a
# 50 m turn onto the recording, which it then follows to within 6 m.
# Playtest 2026-11-03: 150 m out and a 90 m turn swung the AV west of the
# recording, and a 60 m turn 20 to 30 m north of it, both over roofs nobody
# had flown past (the clearance log and the path probe).
# THE LAST TURN, ONTO THE LANDING, IS 110 m ROUND in the open air east of the
# pad. Playtest 2026-11-04 (the flight log): at 50 m the AV swung round 200
# degrees at 21 degrees a second, the turn that felt violent. The climb builds
# up over 12 m: over 30 m the AV was 7 m lower past the building at (-1987,
# 1258) and brushed it (flight_clear_run9.txt).
ROUTE_BACK = flight_paths.route('flight_rec_4.txt', SITE3, SITE3_OUT, PAD, PAD_YAW,
                                climb=0.42, out_len=40.0, descent=0.3, in_len=200.0,
                                turn=50.0, soften=False, turn_in=110.0, ease_out=12.0)
CRUISE_SPEED = 33.3     # the game's own top speed on `dtn_04_spl_av_arrive`
