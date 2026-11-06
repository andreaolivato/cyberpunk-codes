r"""Trauma Team: the quest phase. The sign-up and the first shift.

    python tools\gig05\gen_questphase.py

THE SHIFT, top to bottom:

  the start     the cast off (gotcha 69). Wait for `cc_g05_ad_go`
                (Gig05_Shift.reds, after the prologue, or the dev menu). The
                recruiter, the AV and the crew go on then, while V is anywhere in
                the city: a body switched on near V does not appear until V has
                gone away and come back (gotcha 132).
  the ad        the contact and its thread silently, then the ad (notified),
                the quest, its briefing, "Talk to the recruiter".
  the interview the fixer's in-person loop (tools/fixer01/gen_questphase.py,
                "her talk"). It ends on `cc_g05_hired`.
  up            the game's lift in the tank yard, by its keypad: nothing here
                moves V. `cc_g05_on_roof` (Gig05_Shift.reds) says V has come up.
  the lockers   "Get changed" at the shelves (`gig05_locker`), every shift: the
                item card the first time, the uniform and SMG on.
  the pad       Brekke speaks as V comes near, then "Board the AV"
                (`gig05_board_pad`). V goes on `player_standing`, the crew into the
                cabin behind a short fade.
  a call        the briefing in the air, the flight with its skip, the landing,
                V and the crew off in one fade, the roof crew on their posts, the
                fight (`cc_g05_fight_on`), `cc_g05_site_clear`, the stable line,
                "Board the AV". Three calls.
  home          the flight back, the same step-off, Brekke's goodbye.
  the end       "Take the elevator down", and the optional change back at the
                shelves (`gig05_locker_back`). On the street the pay, `shift_done`
                +1, and Dispatch's text.
  again         The wait on `cc_g05_next_shift`, set by Gig05_Shift.reds after V's
                rest. The recruiter comes back with no marker, Dispatch's text
                says so once, and her prompt (`gig05_repeat`) goes back to "Take
                the staff elevator". The same shift, without the welcome and the
                goodbye. A save finished on 1.0.0 is parked on this wait and
                carries on from it. A new shift will come in through the same
                wait: Dispatch's texts are for new work, she is for the repeat.

WHO SETS WHICH FACT (the rest are THIS GRAPH's own):

  cc_g05_ad_go          Gig05_Shift.reds, or the dev menu
  cc_g05_hired          `gig05_interview`'s exit (this graph), or the dev menu
  cc_g05_on_roof        Gig05_Shift.reds, V up on the walkway. Cleared after a shift
  cc_g05_at_street      Gig05_Shift.reds, V back at the bottom
  cc_g05_changed        `gig05_locker`
  cc_g05_changed_back   `gig05_locker_back`
  cc_g05_off_duty       THIS GRAPH, 1 once V has changed back
  cc_g05_suit_up        THIS GRAPH: Gig05_Shift.reds puts the uniform on
  cc_g05_dressed        Gig05_Shift.reds, 1 while V wears the uniform
  cc_g05_on_shift       THIS GRAPH, from boarding until V is on the street
  cc_g05_aboard         THIS GRAPH: Gig05_Shift.reds locks saving while it is 1
  cc_g05_fight_on       THIS GRAPH, the AV is down at a call
  cc_g05_site_clear     Gig05_Shift.reds, every Scav down
  cc_g05_kit            THIS GRAPH or Gig05_Shift.reds, V has the uniform and SMG
  cc_g05_shift_done     THIS GRAPH, +1 per shift
  cc_g05_rest_start     THIS GRAPH: Gig05_Shift.reds starts the rest and clears it
  cc_g05_rest_from      Gig05_Shift.reds, the game hour the rest began
  cc_g05_next_shift     Gig05_Shift.reds, or the dev menu: the rest is over
  cc_g05_posted         THIS GRAPH, +1 per rest ended
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import questkit.questgraph as qg  # noqa: E402
from questkit.questgraph import (  # noqa: E402
    b, configure, add_input, add_output, add_pause_fact, add_setvar,
    add_addvar, add_journal, add_journal_quest, add_race2, add_scene,
    add_delay, add_condition_fact, add_community, add_pause_distance,
    add_device_action,
    add_assign_seat, add_move_on_spline, add_toggle_door,
    add_anim_event, add_restriction, add_pause_mounted,
    add_pause_vehicle_spawned, add_groups_attitude, add_mortality, add_reward,
    add_give_items, add_cut_control,
    add_combat_target, add_teleport_player, add_fade,
    ANCHOR_PLAYER,
)

import gig05_config as cfg  # noqa: E402
import gen_journal  # noqa: E402
import gen_community as gc  # noqa: E402

OUT = os.path.join(cfg.RAW_MOD, 'quest', 'gig05.questphase.json')
configure(phase_name='gig05')

SCENES = cfg.DEPOT + chr(92) + 'scenes' + chr(92)
P = cfg.FACT_PREFIX
COM = gc.build().community_ref
AV = gc.AV
QUEST = gen_journal.QUEST_PATH
OBJ = QUEST + '/phase_main/'
RIDE = 'GameplayRestriction.cc_g05_ride'
NO_TRAVEL = 'GameplayRestriction.cc_g05_no_travel'

# THE SLOTS, off `av_trauma.ent`'s occupant slot component
# (docs/gig05-av-research.md 1): V at the door holding on. The crew's places in
# the cabin are scene poses (gen_scenes.py, CREW_SEATS).
V_SLOT = 'player_standing'
# The door events the game's own scripts send (vehicleComponent.swift); which
# the Atlus answers is unmeasured, so both left doors are asked.
DOOR_EVENTS = ('doorOpenFrontLeft', 'doorOpenBackLeft')

# Who each Scav shoots at first, the Heywood fight's spread: the client, the
# two crew who fight, and V. Not the medic: he kneels out of the fight (the
# design call, 2026-11-03).
SCAV_TARGETS = {
    'scav1': (gc.ROOF_CREW[gc.LEAD], False),
    'scav2': (None, True),
    'scav3': (gc.ROOF_CREW[gc.LEAD], False),
    'scav4': (gc.CLIENT, False),
    'scav5': (None, True),
}

# THE CREW'S OWN TARGETS, the same node the other way round. Playtest
# 2026-11-03: with only the Scavs given targets, none of the crew fired.
# Only the lead has one: the medic works on the client and the soldier
# stands guard at the AV (gen_community.py).
CREW_TARGETS = {gc.ROOF_CREW[gc.LEAD]: 'scav3'}

# NEW NODES SINCE 1.0.0 TAKE IDS ABOVE ITS HIGHEST, 547, and the sequence the
# released nodes number from carries on untouched. Saves resume by id
# (gotcha 123).
LATE_IDS = iter(range(600, 700))
# A RANGE OF ITS OWN for the hotel's cameras, so test saves keep their place.
ALARM_IDS = iter(range(700, 1000))
CAMERA = 'SurveillanceCameraControllerPS'


def late_ids(build, ids=LATE_IDS):
    released = qg.NID
    qg.NID = ids
    made = build()
    qg.NID = released
    return made


chain = []
chain.append((add_input(), 'Out'))


def step(nid, in_sock='In', out_sock='Out'):
    prev = chain[-1]
    b.connect(prev, (nid, in_sock))
    chain.append((nid, out_sock))
    return nid


def side(nid, src=None, in_sock='In'):
    """Hang a node off the current point without moving it."""
    b.connect(src or chain[-1], (nid, in_sock))
    return nid


def objective(name, state):
    sock = {'on': 'Active', 'done': 'Succeeded'}[state]
    return step(add_journal('gameJournalQuestObjective', OBJ + name, notify=0), in_sock=sock)


def switch(entries, action='Activate', phase=None, gap=0.5):
    """Switch entries on two at a time, half a second apart (gotcha 143:
    many at once froze the game)."""
    for i in range(0, len(entries), 2):
        for e in entries[i:i + 2]:
            step(add_community(action, COM, entry=e, phase=phase))
        step(add_delay(gap))


def seat_v():
    """Walk V onto the standing slot; if six seconds pass and V is not
    mounted, seat V at once. The race's loser is cut either way."""
    step(add_setvar(P + 'seat_claim', 0))
    step(add_assign_seat(COM, AV, V_SLOT, player=True, instant=False))
    won = add_race2(chain[-1],
                    (add_pause_mounted(COM, AV, player=True), 'In', 'Out'),
                    (add_delay(6), 'In', 'Out'),
                    P + 'seat_claim')
    snap = add_assign_seat(COM, AV, V_SLOT, player=True, instant=True)
    b.connect((won, 'False'), (snap, 'In'))
    join = add_setvar(P + 'aboard', 1)
    b.connect((won, 'True'), (join, 'In'))
    b.connect((snap, 'Out'), (join, 'In'))
    chain.append((join, 'Out'))


def crew_scene(scene_name):
    nid = add_scene(SCENES + scene_name + '.scene', ANCHOR_PLAYER, ['crew_in'], ['crew_out'])
    side(nid, in_sock='crew_in')


def board_prompt(scene_name, fact='board_taken', entry='board_in', exit_='board_out'):
    """The prompt scene on a side branch (it gates nothing, gotcha 104), and
    the graph waiting on the fact it writes."""
    step(add_setvar(P + fact, 0))
    side(add_scene(SCENES + scene_name + '.scene', _marker_for(scene_name),
                   [entry], [exit_]), in_sock=entry)
    step(add_pause_fact(P + fact))


def _marker_for(scene_name):
    markers = {'gig05_board_pad': gc.PAD_BOARD_REF, 'gig05_locker': gc.LOCKER_REF,
               'gig05_locker_back': gc.LOCKER_REF}
    markers.update({'gig05_board_s%d' % (k + 1): gc.SITE_BOARD[k][0] for k in range(3)})
    return markers[scene_name]


def aboard_scene(name, entry, exit_, delay):
    """A scene staged at V, on a side branch after `delay` seconds."""
    wait = side(add_delay(delay))
    sc = add_scene(SCENES + name + '.scene', ANCHOR_PLAYER, [entry], [exit_])
    b.connect((wait, 'Out'), (sc, entry))
    return sc


# ---- the start ------------------------------------------------------------
#
# The whole cast off first: a mod community spawns everything on load
# whatever its own field says (gotcha 69).
step(add_community('Deactivate', COM))
step(add_pause_fact(P + 'ad_go'))
switch([gc.RECRUITER, AV])
switch(list(gc.CREW))

# ---- the ad ---------------------------------------------------------------
step(add_journal('gameJournalContact', gen_journal.CONTACT_PATH, notify=0), in_sock='Active')
step(add_journal('gameJournalPhoneConversation', gen_journal.CONV_PATH, notify=0),
     in_sock='Active')
step(add_journal('gameJournalPhoneMessage', gen_journal.MSG_AD_PATH), in_sock='Active')
step(add_delay(gen_journal.MSG_AD_DELAY + 2))
step(add_journal_quest(QUEST), in_sock='Active')
step(add_journal('gameJournalQuestDescription', QUEST + '/' + gen_journal.BRIEF_ID,
                 notify=0), in_sock='Active')
objective('obj_recruiter', 'on')
started = chain[-1]

# ---- the AV ready, as soon as it is there ---------------------------------
#
# A branch of its own, so a slow AV holds nothing up. The game's own door
# events and the AV's own Enter prompt taken away (q113 does the same for
# its flight). THE CREW WAIT BY THE DOOR and are seated as V boards
# (`board_crew`). Playtest 2026-11-03: seated here, two seconds after the AV
# appeared, they stayed standing by the door, and the AV left without them.
crew_from = chain[-1]
cur = crew_from
for nid in (add_pause_vehicle_spawned(COM, AV), add_delay(2.0)):
    b.connect(cur, (nid, 'In'))
    cur = (nid, 'Out')
for ev in DOOR_EVENTS:
    nid = add_anim_event(COM, AV, ev)
    b.connect(cur, (nid, 'In'))
    cur = (nid, 'Out')
nid = add_toggle_door(COM, AV, door='invalid', action='DisableAllInteractions')
b.connect(cur, (nid, 'In'))

# ---- the interview, until V is hired --------------------------------------
#
# The fixer's in-person loop, on a branch beside the main line. Its exit
# writes `cc_g05_hired`; the main line waits on that fact, so the dev menu
# can set it and skip the conversation.
T = P + 'talk'
talk_top = add_setvar(T + '_claim', 0)
b.connect(started, (talk_top, 'In'))
near = add_pause_distance(COM, cfg.TALK_RADIUS, entry=gc.RECRUITER, cmp='Less')
b.connect((talk_top, 'Out'), (near, 'In'))
gate = add_condition_fact(P + 'hired', 0, 'Equal')
b.connect((near, 'Out'), (gate, 'In'))
talk = add_scene(SCENES + 'gig05_interview.scene', ANCHOR_PLAYER,
                 ['interview_in'], ['interview_out', 'interview_left'])
b.connect((gate, 'True'), (talk, 'interview_in'))
hired = add_setvar(P + 'hired', 1)
b.connect((talk, 'interview_out'), (hired, 'In'))
rearm = add_delay(1)
b.connect((talk, 'interview_left'), (rearm, 'In'))
b.connect((rearm, 'Out'), (talk_top, 'In'))

step(add_pause_fact(P + 'hired'))
objective('obj_recruiter', 'done')

# ---- up to the roof -------------------------------------------------------
# EVERY LATER SHIFT COMES IN HERE, from the wait at the bottom of the graph.
up_again = objective('obj_up', 'on')
# THE LIFT IS THE GAME'S, and V works it with its own keypad: nothing here moves
# V. Playtest 2026-11-04: "just press on the keypad". Gig05_Shift.reds sets
# `cc_g05_on_roof` as V comes up level with the roof.
step(add_pause_fact(P + 'on_roof'))
# THE RECRUITER LEAVES once V has gone up: her pitch is done, and she had
# nothing more to say (playtest 2026-11-03, the design call: remove her or
# give her something to say).
step(add_community('Deactivate', COM, entry=gc.RECRUITER))
objective('obj_up', 'done')
objective('obj_change', 'on')
# THE KIT, at the locker room, every shift (the design call, 2026-11-04): the
# uniform and the SMG, with the game's own item card and picture (the design
# call, 2026-11-03). Given by a reward record instead, they arrived as plain
# "looted" lines, and during the fade-in; so the game's own item node, with its
# notice asked for, once the screen is back.
board_prompt('gig05_locker', fact='changed', entry='locker_in', exit_='locker_out')
step(add_setvar(P + 'off_duty', 0))
step(add_fade(False, 0.4))
step(add_delay(0.8))
step(add_fade(True, 0.4))
step(add_delay(0.5))
# ONCE: V keeps the uniform and the SMG between shifts, and a second copy of the
# outfit is a second tile in the wardrobe.
kit = step(add_condition_fact(P + 'kit', 0, 'Equal'))
give = add_give_items('Items.Trauma_Team_Outfit', 'Items.Preset_Dian_Trauma')
b.connect((kit, 'True'), (give, 'In'))
kept = add_setvar(P + 'kit', 1)
b.connect((give, 'Out'), (kept, 'In'))
suit = add_setvar(P + 'suit_up', 1)   # Gig05_Shift.reds puts the uniform on
b.connect((kit, 'False'), (suit, 'In'))
b.connect((kept, 'Out'), (suit, 'In'))
chain.append((suit, 'Out'))
objective('obj_change', 'done')
# THE WELCOME IS THE FIRST SHIFT'S: it introduces the crew to a new hire.
first_day = late_ids(lambda: add_condition_fact(P + 'shift_done', 0, 'Equal'))
step(first_day, out_sock='True')
objective('obj_talk', 'on')

# ---- boarding at the pad --------------------------------------------------
# BREKKE MEETS V AT THE AV. Playtest 2026-11-04: walking up to three people
# who said nothing felt wrong. The board prompt waits for the end of it.
step(add_pause_distance(COM, cfg.GREET_RADIUS, entry=gc.LEAD, cmp='Less'))
step(add_scene(SCENES + 'gig05_welcome.scene', ANCHOR_PLAYER, ['welcome_in'], ['welcome_out']),
     in_sock='welcome_in', out_sock='welcome_out')
objective('obj_talk', 'done')
board_on = objective('obj_board', 'on')
b.connect((first_day, 'False'), (board_on, 'Active'))
board_prompt('gig05_board_pad')
step(add_setvar(P + 'on_shift', 1))
step(add_restriction(NO_TRAVEL, add=True))
# THE CREW GET IN UNDER A SHORT FADE, as at a call, and V walks in past them.
# Playtest 2026-11-03: otherwise they vanish from the pad in full view.
step(add_fade(False, 0.3))
step(add_delay(0.35))
crew_scene('gig05_crew_1')
step(add_teleport_player(gc.PAD_STEP_IN_REF))
step(add_delay(0.8))
step(add_fade(True, 0.4))
seat_v()
step(add_delay(2.0))
step(add_restriction(RIDE, add=True))
objective('obj_board', 'done')
objective('obj_ride', 'on')
# The attitude groups, set again with the game's own nodes (characters.yaml
# carries them as records too).
step(add_groups_attitude('cc_g05_gang', 'cc_g05_crew', 'AIA_Hostile'))
step(add_groups_attitude('cc_g05_gang', 'player', 'AIA_Hostile'))
step(add_groups_attitude('cc_g05_gang', 'cc_g05_client', 'AIA_Hostile'))
step(add_groups_attitude('cc_g05_crew', 'player', 'AIA_Friendly'))
# THE GAME'S OWN TRAUMA TEAM ON V'S SIDE FOR THE SHIFT. Playtest 2026-11-03:
# the street call is beside a clinic the game guards with a Trauma Team
# squad, and they went after V in the shootout. Neutral is their normal
# relation to V, put back at the end of the shift.
step(add_groups_attitude('traumateam', 'player', 'AIA_Friendly'))


def site_phase(k):
    """The first call's phase by its name: left unnamed, an entry stays in the
    phase it was last in, which on a later shift is the third call's."""
    return gc.SITE_PHASES[k] or 'default'


def call_people_on(k, after):
    """A call's client and Scavs switched on at its spots, `after` seconds
    into the flight there, on a branch of their own; the client held at 1
    percent until the medic is done. The first call's spots are each
    entry's own, the later ones phases (gen_community.SITE_PHASES)."""
    cur = (side(add_delay(after)), 'Out')
    for e in [gc.CLIENT] + gc.SCAVS:
        for nid in (add_community('Activate', COM, entry=e, phase=site_phase(k)),
                    add_delay(0.5)):
            b.connect(cur, (nid, 'In'))
            cur = (nid, 'Out')
    nid = add_mortality(COM, gc.CLIENT, 'Immortal', source='cc_g05_client')
    b.connect(cur, (nid, 'In'))


def call_people_off(after):
    """The client and the Scavs off once the AV has lifted away."""
    cur = (side(add_delay(after)), 'Out')
    for e in [gc.CLIENT] + gc.SCAVS:
        nid = add_community('Deactivate', COM, entry=e)
        b.connect(cur, (nid, 'In'))
        cur = (nid, 'Out')


def hotel_guards_off():
    """The story's roof guards off for the shift, on a branch of their own.
    Harmless on a save where the story has not switched them on or has
    finished: there is nobody to switch off."""
    cur = chain[-1]
    for e in cfg.HOTEL_ROOF_GUARDS:
        nid = add_community('Deactivate', cfg.HOTEL_GUARDS_COM, entry=e)
        b.connect(cur, (nid, 'In'))
        cur = (nid, 'Out')


def hotel_guards_back(after):
    """The game switches the community on only once, so nothing brings them
    back but this. Only while the story is open: `sts_cct_dtn_tier_3` is what
    lets it run, and `dtn_04_finished` is what ends it."""
    open_ = add_condition_fact('sts_cct_dtn_tier_3', 0, 'Greater')
    b.connect((side(add_delay(after)), 'Out'), (open_, 'In'))
    unfinished = add_condition_fact('dtn_04_finished', 0, 'Equal')
    b.connect((open_, 'True'), (unfinished, 'In'))
    cur = (unfinished, 'True')
    for e in cfg.HOTEL_ROOF_GUARDS:
        for nid in (add_community('Activate', cfg.HOTEL_GUARDS_COM, entry=e, phase='default'),
                    add_delay(0.5)):
            b.connect(cur, (nid, 'In'))
            cur = (nid, 'Out')


def step_off(phase, out_ref, crew_on, ready):
    """V AND THE CREW OFF THE AV IN ONE SHORT FADE. Playtest 2026-11-03: the
    game's own exit stuttered, V was shot before the weapon was out, and the
    riders vanished from the cabin as the ground crew appeared beside it.
    Under the fade V is let go, the AV is put back on its spot (`phase`)
    with its doors open, the riders go and `crew_on` puts the ground crew
    on their posts; V is stood at `out_ref` facing the fight and the
    weapon drawn (`ready`, Gig05_Shift.reds) before the screen comes back.
    The fade node returns at once (gotcha in `elevator`), hence the waits."""
    step(add_fade(False, 0.3))
    step(add_delay(0.35))
    step(add_assign_seat(COM, AV, V_SLOT, player=True, assign=False, instant=True))
    step(add_delay(0.2))
    step(add_setvar(P + 'aboard', 0))
    switch(list(gc.CREW), action='Deactivate', gap=0.1)
    step(add_community('Deactivate', COM, entry=AV))
    step(add_delay(0.2))
    step(add_community('Activate', COM, entry=AV, phase=phase))
    step(add_pause_vehicle_spawned(COM, AV))
    for ev in DOOR_EVENTS:
        step(add_anim_event(COM, AV, ev))
    step(add_toggle_door(COM, AV, door='invalid', action='DisableAllInteractions'))
    crew_on()
    step(add_teleport_player(out_ref))
    step(add_restriction(RIDE, add=False))
    step(add_setvar(P + 'ready', ready))
    step(add_delay(0.4))
    step(add_fade(True, 0.4))


def fly(i, spline):
    """FLIGHT `i` (1 to 4) along `spline`, with the skip choice (gen_scenes.py,
    build_skip) beside it. The race waits on the fact the choice writes, not
    on the scene's exit: a prompt scene's exit drives nothing (gotcha 104).

    THE SKIP IS THE SAME FLIGHT WITH THE CLOCK RUNNING FAST. Under a fade
    `cc_g05_warp` tells Gig05_Shift.reds to speed the world up until the AV is
    near its landing, which sets `cc_g05_warp_done`, and the screen comes back
    on the last stretch. The AV is never touched. Playtest 2026-11-04: put back
    in the air by a phase, an AV stayed there, the second flight order doing
    nothing, V hanging over the city for good."""
    # V CANNOT BE HURT ABOARD: the call's Scavs are out before the AV lands,
    # and V can do nothing about them until the step-off (Gig05_Shift.reds,
    # Ready, keeps the shield a few seconds past it).
    step(add_setvar(P + 'shield', 1))
    step(add_setvar(P + 'skip', 0))
    step(add_setvar(P + 'warp_done', 0))
    choice = side(add_scene(SCENES + 'gig05_skip_%d.scene' % i, ANCHOR_PLAYER,
                            ['skip_in'], ['skip_out']), in_sock='skip_in')
    taken = side(add_pause_fact(P + 'skip'))
    # THE CHOICE GOES before the AV reaches the stretch a skip would show.
    shut = add_cut_control()
    b.connect((shut, 'CutSource'), (choice, 'CutDestination'))
    timer = side(add_delay(gc.skip_window(i)))
    b.connect((timer, 'Out'), (shut, 'In'))
    cur = (taken, 'Out')
    for nid in (add_fade(False, 0.6), add_delay(0.8), add_setvar(P + 'warp', i),
                add_pause_fact(P + 'warp_done'), add_delay(0.6), add_fade(True, 0.8)):
        b.connect(cur, (nid, 'In'))
        cur = (nid, 'Out')
    step(add_move_on_spline(COM, AV, spline))
    gone = add_cut_control()
    b.connect((gone, 'CutSource'), (choice, 'CutDestination'))
    b.connect((gone, 'CutSource'), (taken, 'CutDestination'))
    step(gone)


# ---- the three calls ------------------------------------------------------
#
# THREE CALLS A SHIFT (the design call, 2026-11-03): the AV flies from one
# call to the next and home after the third.
BRIEFS = ['gig05_brief', 'gig05_brief2', 'gig05_brief3']
call_people_on(0, 0)
late_ids(hotel_guards_off)
for k in range(3):
    # THE GAME'S OWN SOLDIERS OFF CALL 2. Its city scene hides for the shift
    # (Gig05_Shift.reds, CityScenes) and three of its soldiers stayed on the spot
    # (playtest 2026-11-05, listed in game at 0 to 5 m). This is the node the scene
    # uses itself, so the scene turns them on again when it next runs.
    if k == 1:
        for ref in cfg.CALL2_VANILLA_CREW:
            step(add_community('Deactivate', ref))
    aboard_scene(BRIEFS[k], 'brief_in', 'brief_out', 4)
    fly(k + 1, gc.FLIGHTS[k][0])
    step(add_setvar(P + 'park', 1))   # Gig05_Shift.reds levels the AV

    # THE HOTEL'S CAMERAS BLIND WHILE V IS ON THEIR ROOF. Playtest 2026-11-06: one
    # saw V in the fight and the alarm moved Dino's gig on. The game's own action
    # for a camera, which leaves one V has shot broken.
    if k == 0:
        late_ids(lambda: side(add_device_action(CAMERA, 'QuestSetDetectionToFalse',
                                                cfg.HOTEL_CAMERAS)), ALARM_IDS)

    # -- down at the call
    side(add_scene(SCENES + 'gig05_land_%d.scene' % (k + 1), ANCHOR_PLAYER,
                   ['land_in'], ['land_out']),
         in_sock='land_in')
    step(add_delay(2.5))
    step_off(gc.AV_PHASES[k], gc.SITE_OUT[k][0],
             lambda k=k: switch([gc.ROOF_CREW[w] for w in gc.CREW], phase=site_phase(k),
                                gap=0.1),
             1)
    objective('obj_ride', 'done')
    objective('obj_hold', 'on')
    step(add_setvar(P + 'site_clear', 0))
    step(add_setvar(P + 'fight_on', 1))
    # EACH ORDER ON A BRANCH OF ITS OWN, fired and left. Playtest 2026-11-03:
    # chained one after another on their `Success` sockets, the graph stopped
    # at the first, because an order with no end (`duration` -1) never
    # succeeds, and the roof could never be called clear.
    for scav, (target, at_player) in SCAV_TARGETS.items():
        side(add_combat_target(COM, scav, COM, target, target_player=at_player))
    for who, scav in CREW_TARGETS.items():
        side(add_combat_target(COM, who, COM, scav))

    # -- clear
    step(add_pause_fact(P + 'site_clear'))
    step(add_setvar(P + 'fight_on', 0))
    step(add_delay(2.0))
    step(add_scene(SCENES + 'gig05_stable_%d.scene' % (k + 1), ANCHOR_PLAYER,
                   ['stable_in'], ['stable_out']),
         in_sock='stable_in', out_sock='stable_out')
    objective('obj_hold', 'done')
    objective('obj_board_site', 'on')
    step(add_setvar(P + 'regroup', 1))   # Gig05_Shift.reds walks the lead back

    # -- aboard again: V and the riders onto the AV's places by the crew
    # scene, the roof crew off as the riders come on.
    # A SHORT FADE HIDES THE SWAP: the men on the ground and the client go,
    # the men who ride stand in the cabin, and V then walks aboard past
    # them. Playtest 2026-11-03: unhidden, the crew vanished from the roof
    # and appeared in the cabin, and the client lay on the ground until V
    # was aboard. The client is carried aboard on screen in a later build.
    board_prompt('gig05_board_s%d' % (k + 1))
    step(add_setvar(P + 'regroup', 0))
    step(add_fade(False, 0.3))
    step(add_delay(0.35))
    switch([gc.ROOF_CREW[w] for w in gc.CREW] + [gc.CLIENT], action='Deactivate', gap=0.1)
    # THE AV TURNED FOR ITS TAKEOFF in the same fade (gig05_config.py,
    # _site), and V stood at its door. The glide probe found most calls
    # open one way in and another way out.
    step(add_community('Deactivate', COM, entry=AV))
    step(add_delay(0.2))
    step(add_community('Activate', COM, entry=AV, phase=gc.AV_DEP_PHASES[k]))
    step(add_pause_vehicle_spawned(COM, AV))
    step(add_toggle_door(COM, AV, door='invalid', action='DisableAllInteractions'))
    step(add_teleport_player(gc.SITE_STEP_IN[k][0]))
    switch(list(gc.CREW), gap=0.1)
    crew_scene('gig05_crew_%d' % (k + 2))
    step(add_delay(0.6))
    step(add_fade(True, 0.4))
    seat_v()
    step(add_delay(2.0))
    step(add_restriction(RIDE, add=True))
    objective('obj_board_site', 'done')
    objective('obj_ride' if k < 2 else 'obj_return', 'on')
    call_people_off(8)
    if k == 0:
        # They see again once the AV has gone.
        late_ids(lambda: b.connect((side(add_delay(25)), 'Out'),
                                   (add_device_action(CAMERA, 'QuestSetDetectionToTrue',
                                                      cfg.HOTEL_CAMERAS), 'In')), ALARM_IDS)
    # THE ROOF GUARDS BACK AFTER THE LAST CALL, about 800 m from that roof. They
    # were back 25 s after the first call, with the AV still close to them.
    if k == 2:
        late_ids(lambda: hotel_guards_back(2))
    if k < 2:
        call_people_on(k + 1, 10)

# ---- home -----------------------------------------------------------------
aboard_scene('gig05_home', 'home_in', 'home_out', 6)
fly(4, gc.FLIGHTS[3][0])
step(add_setvar(P + 'park', 1))   # Gig05_Shift.reds levels the AV
step(add_delay(2.5))
# THE CREW STEP OFF WITH V AND STAY ON THE PAD, on their own spots there
# (gig05_config.py, PAD_CREW). Playtest 2026-11-03: switched off as V
# stepped down, they vanished. The next shift finds them where they stand.
def home_crew():
    switch(list(gc.CREW), gap=0.1)


step_off(gc.AV_PAD_PHASE, gc.PAD_OUT_REF, home_crew, 2)
objective('obj_return', 'done')
# BREKKE'S LAST WORD, on the pad, V beside him. Playtest 2026-11-04: the three
# stood there and said nothing.
step(add_delay(2.0))
# THE FIRST SHIFT'S ONLY: its lines are about the rookie's first day.
first_bye = late_ids(lambda: add_condition_fact(P + 'shift_done', 0, 'Equal'))
step(first_bye, out_sock='True')
step(add_scene(SCENES + 'gig05_bye.scene', ANCHOR_PLAYER, ['bye_in'], ['bye_out']),
     in_sock='bye_in', out_sock='bye_out')

# ---- down to the street, and the end of the shift -------------------------
#
# THE WAY DOWN IS THE ROOF'S LIFT, the keypad again. `cc_g05_at_street` is set by Gig05_Shift.reds with V back at the
# bottom; it is cleared here because a call can be at street level.
down_on = objective('obj_down', 'on')
b.connect((first_bye, 'False'), (down_on, 'Active'))
step(add_setvar(P + 'at_street', 0))
# CHANGING BACK IS OPTIONAL (the design call, 2026-11-04): the Get changed spot,
# on a branch of its own. Taken, the uniform and SMG come off and V's own things go
# back. Left, V goes home in them (`suit_up` stays on).
step(add_setvar(P + 'changed_back', 0))
back_on = add_journal('gameJournalQuestObjective', OBJ + 'obj_back', notify=0)
b.connect(chain[-1], (back_on, 'Active'))
back = add_scene(SCENES + 'gig05_locker_back.scene', gc.LOCKER_REF, ['locker_in'], ['locker_out'])
b.connect((back_on, 'Out'), (back, 'locker_in'))
back_taken = side(add_pause_fact(P + 'changed_back'), src=(back_on, 'Out'))
cur = (back_taken, 'Out')
for nid in (add_fade(False, 0.4), add_delay(0.5), add_setvar(P + 'off_duty', 1), add_setvar(P + 'suit_up', 0),
            add_delay(0.8), add_fade(True, 0.4)):
    b.connect(cur, (nid, 'In'))
    cur = (nid, 'Out')
back_done = add_journal('gameJournalQuestObjective', OBJ + 'obj_back', notify=0)
b.connect(cur, (back_done, 'Succeeded'))
step(add_pause_fact(P + 'at_street'))
# LEFT ON THE ROOF: the prompt goes, and so does the objective.
back_shut = add_cut_control()
b.connect((back_shut, 'CutSource'), (back, 'CutDestination'))
b.connect((back_shut, 'CutSource'), (back_taken, 'CutDestination'))
step(back_shut)
back_kept = side(add_condition_fact(P + 'changed_back', 0, 'Equal'))
back_off = add_journal('gameJournalQuestObjective', OBJ + 'obj_back', notify=0)
b.connect((back_kept, 'True'), (back_off, 'Inactive'))
step(add_setvar(P + 'on_shift', 0))
step(add_restriction(NO_TRAVEL, add=False))
step(add_groups_attitude('traumateam', 'player', 'AIA_Neutral'))

# ---- the pay --------------------------------------------------------------
#
# One payment per call, at the tier its briefing named: Platinum, Gold,
# Silver, with the game's own reward node after the fade has finished: the
# fade node returns at once, so 1.5 s after it the screen is only just back
# and the XP bar played unseen (playtest 2026-11-04), and from the script as
# the screen came back no notice was seen at all (playtest 2026-11-03).
step(add_delay(2.0))
step(add_reward('QuestRewards.sts_cc_g05_platinum', 'QuestRewards.sts_cc_g05_gold',
                'QuestRewards.sts_cc_g05_silver'))
objective('obj_down', 'done')
# THE REST STARTS NOW (Gig05_Shift.reds, NextShift). A save finished on 1.0.0
# never passed this, and that is how the script tells it from a new shift.
late_ids(lambda: step(add_setvar(P + 'rest_start', 1)))
step(add_addvar(P + 'shift_done', 1))
step(add_setvar(P + 'on_roof', 0))
# DISPATCH SAYS WHAT COMES NEXT, and the objective says to wait for it.
step(add_delay(6.0))
step(add_journal('gameJournalPhoneMessage', gen_journal.MSG_DONE_PATH), in_sock='Active')
objective('obj_wait', 'on')

# THE REST ENDS HERE. A finished save is parked on this wait, 1.0.0's too, so
# the wait keeps its id and the way on leaves from it. Gig05_Shift.reds sets
# the fact. The output below is never reached, and keeps its id.
step(add_pause_fact(P + 'next_shift'))


def next_shift():
    step(add_setvar(P + 'next_shift', 0))
    step(add_addvar(P + 'posted', 1))
    # THE TEXT ONCE, after the first rest only (the design call, 2026-11-06:
    # Dispatch's texts mean new work). The objective stays on the wait: she is
    # there for whoever wants her, with no marker and nothing to do otherwise.
    once = add_condition_fact(P + 'posted', 1, 'Equal')
    step(once, out_sock='True')
    step(add_journal('gameJournalPhoneMessage', gen_journal.MSG_REPEAT_PATH), in_sock='Active')
    back = add_community('Activate', COM, entry=gc.RECRUITER)
    b.connect((once, 'False'), (back, 'In'))
    step(back)
    # THE INTERVIEW'S LOOP: the prompt while V is near her, again if V walks off.
    near = step(add_pause_distance(COM, cfg.TALK_RADIUS, entry=gc.RECRUITER, cmp='Less'))
    talk = step(add_scene(SCENES + 'gig05_repeat.scene', ANCHOR_PLAYER,
                          ['repeat_in'], ['repeat_out', 'repeat_left']),
                in_sock='repeat_in', out_sock='repeat_out')
    rearm = add_delay(1)
    b.connect((talk, 'repeat_left'), (rearm, 'In'))
    b.connect((rearm, 'Out'), (near, 'In'))
    objective('obj_wait', 'done')
    b.connect(chain[-1], (up_again, 'Active'))


late_ids(next_shift)
add_output()

if __name__ == '__main__':
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    result = b.build()
    with open(OUT, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(result, fh, indent=2)
    print('wrote %s' % OUT)
    print('nodes: %d, connections: %d, handles used: %d'
          % (len(b.nodes), len(b.conns), b.next_handle))
