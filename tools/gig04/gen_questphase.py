r"""Return Ticket: the quest phase.

    python tools\gig04\gen_questphase.py

THE WHOLE GIG. It waits for her introduction, puts the gig's icon on the
map at Ligaya's stall, and when V comes near the stall she rings with the
job; the quest, its briefing, her text with the gig card and the
first objective follow. Then the stall, Stamps's couch and his shard, the
bar, the Claws' van and its clues, the room, Orbital Air, and her last
call, the fee, her counter, and the quest closes.

  the start     the cast switched off, Ligaya on. Wait for
                `cc_f01_intro_done`, hers: V has taken her introduction
                call (node 22, fixed: see INTRO_WAIT_ID). Then the icon,
                then `cc_g04_near_offer`, then wait until V is not already
                talking to her.
  her call      she rings once, video, for up to 30 seconds; missed, the job
                comes as her text (`her_call`, below). `gig04_brief`.
  the job       the quest goes Active and tracked, with its briefing, her
                text and its first objective.
  the stall     Ligaya and Stamps are switched on. V within TALK_RADIUS of
                her plays `gig04_stall` where V stands; the scene ends on
                her last line or when V walks off, and a walk-off re-arms
                the wait a second later (the fixer's loop). The first
                shard is armed as the scene ends.
  the couch     Stamps is not on it. His shard is on its seat:
                Gig04_Shard.reds sets `cc_g04_shard_got` when it is in V's
                hands and `cc_g04_shard_read` when read; each closes an
                objective.
  the bar       the same loop on Stamps at the bar, `gig04_booth`: four
                ways to make him talk, Body, Intelligence, 1,000 eddies or
                a fight that ends in `gig04_beaten`. He cannot die before
                he talks: raced against `cc_g04_stamps_hit`, so a V who
                hurts him before or during his conversation is in the
                fight.
  the van       the false lead, in a yard in south-west Little China. The Claws' van is switched on; V within 20 m opens
                the clue hunt, three scans counted on the objective; then
                the Claws' shard behind it (`cc_g04_shard2_*`) says they
                moved Bayani to the shop in Little China.
  the room      Bayani and the three Claws are switched on and armed. V
                inside the room's area closes "go to"; V within
                TALK_RADIUS of Bayani plays `gig04_room`.
  Orbital Air   one car and three guards on the street, one of two sets
                by `cc_g04_ep1`; `cc_g04_oa_clear` when they are down.
                Then Bayani runs, "leave the area" until V is out of the
                drawn circle, then "Wait for Hodan's call": two hours of
                the world clock, or the railing, which moves the clock on.
                The cast is switched off out of sight.
  her last call `gig04_close`, or `gig04_close_dead` when `cc_g04_stamps_dead`
                is set.
  the end       the fee, +1 on her counter, the quest Succeeded.

WHO SETS WHICH FACT:

  cc_f01_intro_done   HER graph, once her introduction call was taken
  cc_f01_talk_mode    HER graph: 0 while V is not in her conversation
  cc_f01_intro_time   HER script (Fixer01_Stamp.reds): the world clock, in
                      seconds, as her introduction call ended
  cc_g04_near_offer   Gig04_Places.reds, V near the stall, calm, once armed
  cc_g04_brief_*      THIS GRAPH's latches for her first call (claim, video,
  cc_g04_close_*      rings, step) and for her last, cleared before use
  cc_g04_started      THIS GRAPH, once the quest is in the journal
  cc_g04_stall_done   THIS GRAPH, once Ligaya's scene has played to its end
  cc_g04_shard_armed  THIS GRAPH: Gig04_Shard.reds may read the shard now
  cc_g04_shard_got    Gig04_Shard.reds: the shard is in V's hands
  cc_g04_shard_read   Gig04_Shard.reds: the shard has been read
  cc_g04_booth_claim  THIS GRAPH, the booth race's scratch
  cc_g04_stamps_paid  THIS GRAPH, V paid him; the game took the 1,000
  cc_g04_stamps_talked THIS GRAPH, he said where Bayani is, any way
  cc_g04_booth_on     THIS GRAPH, 1 while his conversation is up (a readout)
  cc_g04_booth_picked his scene: 1 Body, 2 Intelligence, 3 paid, 4 fight
  cc_g04_booth_once   THIS GRAPH: only one way past the booth goes on
  cc_g04_booth_done   THIS GRAPH, once the booth is behind V
  cc_g04_stamps_fight THIS GRAPH, the fight is on (the claim on it too)
  cc_g04_stamps_down  Gig04_Places.reds, at a third of his health in it
  cc_g04_flop_armed   THIS GRAPH: the van is out; Gig04_Places.reds locks it
  cc_g04_clue_blood   the clue object (gen_clues), once V has scanned it;
  cc_g04_clue_cuffs   one each. The quest counts the three
  cc_g04_clue_bag
  cc_g04_clues_all    THIS GRAPH: all three clues scanned
  cc_g04_bye_here     Gig04_Places.reds: Bayani is on his spot in the hall
                      (1); or THIS GRAPH, BYE_WAIT has passed (2). His
                      goodbye is offered
  cc_g04_shard2_armed THIS GRAPH: Gig04_Shard.reds reads the Claws' shard
  cc_g04_shard2_got   Gig04_Shard.reds: the Claws' shard is in V's hands
  cc_g04_shard2_read  Gig04_Shard.reds: the Claws' shard has been read
  cc_g04_ep1          Gig04_Places.reds, from IsEP1(): which guards come
  cc_g04_oa_armed     the room scene, as V's company line starts: Orbital
                      Air come in along their paths and are turned on V
  cc_g04_bye_go       Gig04_Places.reds, Orbital Air down and both doors
                      open: THIS GRAPH walks Bayani to the hall
  cc_g04_run_go       Gig04_Places.reds, his goodbye over and his hall hold
                      cancelled: THIS GRAPH sends him on his run
  cc_g04_oa_set       THIS GRAPH: which three came, 1 Orbital Air, 2 security
  cc_g04_oa_on        THIS GRAPH, once they and the car are switched on
  cc_g04_oa_clear     Gig04_Places.reds, once the three guards are down
  cc_g04_claws_clear  Gig04_Places.reds, once the room's Claws are down
  cc_g04_room_far     Gig04_Places.reds, V 150 m from the building's door
  cc_g04_room_off     THIS GRAPH, the room's Claws, Orbital Air, car off
  cc_g04_rail_taken   the railing's scene, once V leans on it
  cc_g04_rail_shift   THIS GRAPH: Gig04_Places.reds moves the clock on
  cc_g04_rail_release THIS GRAPH or Gig04_Places.reds: V leaves the lean
  cc_g04_wait_from    Gig04_Places.reds, the clock as the wait began
  cc_g04_rail_skipped Gig04_Places.reds, once the clock has been moved on
  cc_g04_bayani_ran   THIS GRAPH, once his run order has gone out
  cc_g04_bayani_rerun Gig04_Places.reds: a body back in the cell, send again
  cc_g04_watch_gone   THIS GRAPH, once V is out of the circle: watch him now
  cc_g04_market_far   Gig04_Places.reds, V far from the stall and the bar
  cc_g04_market_off   THIS GRAPH, Ligaya and Stamps switched off
  cc_g04_flop_far     Gig04_Places.reds, V 150 m from the van
  cc_g04_van_near     Gig04_Places.reds, V within 20 m of the van
  cc_g04_bar_far      Gig04_Places.reds, V 150 m from the bar
  cc_g04_stamps_hit   Gig04_Places.reds, hurt or knocked out before the
                      fight: the fight starts
  cc_g04_stamps_dead  Gig04_Places.reds, once his body is found dead after
                      he talked. Picks her last call
  cc_g04_room_armed   THIS GRAPH: Gig04_Places.reds may turn the Claws now
  cc_g04_room_done    THIS GRAPH, once Bayani's scene has played to its end
  cc_g04_mid_done     THIS GRAPH, once V is away from the room
  cc_g04_close_said   THIS GRAPH, once her last call's scene has played
  cc_g04_pay          THIS GRAPH, telling the script the fee is due
  cc_g04_paid         Gig04_Pay.reds, once the fee has been handed over. Its
                      latch; nothing here reads it
  cc_f01_fixer_count  THIS GRAPH, +1 as the gig closes. Hers, shared by every
                      gig of hers (`mods/fixer-01/docs/design.md`)
  cc_g04_done         THIS GRAPH, at the very end

HER CALL IS HER OWN INTRODUCTION CALL, node for node
(`tools/fixer01/gen_questphase.py`, "the call"): the mod-owned video recipe
(`docs/scene-playbook.md`), her contact as the caller by journal path, the
studio set her introduction borrows, the pick-up read off the fact
PhoneSystem writes (gotcha 58), and the ring-again loop. Her contact is
already active: her own graph switched it on before her first call.

THE PAYMENT IS GIG 03'S ROUTE, the one that has been played: a script hands
a `QuestRewards` record to `RPGManager.GiveReward` (`Gig04_Pay.reds`,
`docs/architecture.md` "Paying the player"). The graph only says when, by
setting `cc_g04_pay`, and does not wait for it, as gig 03's does not: a
wait on a script is a gig that never closes if the script is missing
(gotcha 22).

THE COUNT IS +1, NOT =1: the base game's fixer loop adds to
`<district>_sts_counter` with the same node, and her second gig will add
another.

NODE NUMBERS FREEZE AT THE FIRST RELEASE (gotcha 123). Until then the graph
is free to change, and every test starts from a save taken before the gig.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from questkit.questgraph import (  # noqa: E402
    b, configure, add_input, add_output, add_pause_fact, add_setvar,
    add_addvar, add_journal, add_journal_quest, add_game_delay, add_race2,
    add_scene, add_call_contact, add_prefab_variant, add_pause_node_loaded,
    add_delay, add_toggle_component, add_condition_fact, add_community,
    add_pause_distance, add_pause_triggers, add_ai_patrol, add_cut_control,
    add_pause_facts, add_condition_phone_muted, add_fade, add_player_fx,
    add_objective_counter, skip_ids_to, add_crowd_null_area,
    ANCHOR_PLAYER,
)

from questkit import questgraph  # noqa: E402
import gig04_config as cfg  # noqa: E402

# IDS FOR NODES ADDED AFTER A PLAYTEST SAVE EXISTS, past every other node
# (367 the highest on 2026-11-01), so adding one does not renumber the rest
# (gotcha 123). Taken in build order; `late()` below hands them out.
LATE_IDS = iter(range(900, 950))
# The room's second group of Claws (below, "THE ROOM'S CLAWS IN TWO GROUPS"),
# a range of its own so the railing's 900-903 keep their numbers.
ROOM_LATE_IDS = iter(range(950, 1000))


def late(make, *args, ids=None):
    saved = questgraph.NID
    questgraph.NID = LATE_IDS if ids is None else ids
    try:
        return make(*args)
    finally:
        questgraph.NID = saved
import gen_journal  # noqa: E402
import gen_community  # noqa: E402
import gen_room  # noqa: E402

OUT = os.path.join(cfg.RAW_MOD, 'quest', 'gig04.questphase.json')

configure(phase_name='gig04')

# The same string gen_scenes.SCENE_DEPOT builds, and it has to stay so: the
# lipmap is keyed by FNV1a64 of exactly this path plus the scene name.
SCENES = cfg.DEPOT + chr(92) + 'scenes' + chr(92)

QUEST = gen_journal.QUEST_PATH
PHASE = QUEST + '/phase_main'
BRIEF = QUEST + '/' + gen_journal.BRIEF_ID
FIRST = PHASE + '/' + gen_journal.OBJECTIVES[0][0]
MSG_BRIEF = gen_journal.MSG_BRIEF_PATH
MSG_CLOSE = gen_journal.MSG_CLOSE_PATH
MSG_CLOSE_DEAD = gen_journal.MSG_CLOSE_DEAD_PATH
POI = 'points_of_interest/street_stories/' + gen_journal.QUEST_ID

# THE CAST, one community (gen_community): the NodeRef the graph switches
# entries of, and the area round the room.
CAST_REF = gen_community.build().community_ref
CAST_ENTRIES = [e.name for e in gen_community.entries()]
ROOM_ENTRIES = [gen_community.BAYANI] + [c[0] for c in cfg.ROOM_CLAWS]
AREA_REF = gen_community.AREA_REF

# A PIN MUST BE ACTIVATED ALONGSIDE ITS OBJECTIVE OR IT NEVER APPEARS
# (docs/map-pins-playbook.md; gig 03's table).
# DERIVED FROM THE JOURNAL'S OWN LIST (audit 2026-10-01; gotcha 76): an
# objective with an anchor has a pin, named `pin_` + its name after `obj_`,
# which is how questkit.journal.objective names it.
PINS = {o: 'pin_' + o[len('obj_'):] for o, _s, a in gen_journal.OBJECTIVES if a}

FIXER_CONTACT = cfg.FIXER_CONTACT
PLAYER_CONTACT = 'contacts/player'

F = cfg.FACT_PREFIX

# ------------------------------------------------------------- the studio
#
# THE SET HER INTRODUCTION BORROWS, the five names that are only correct
# together (`tools/fixer01/gen_questphase.py`, "THE BORROWED SET"). The pose
# half is in gen_scenes.STUDIO_POSE.
STUDIO_PREFAB = '#holocalls_studio'
LIGHTS_REF = '#holocalls_studio_lighting'
LIGHTS_VARIANT = 'jefferson_holocall_lights'
SETUP_REF = '#jefferson_holocall_setup'
SETUP_VARIANT = 'jefferson_holocall_setup'
CAMERA_REF = '#jefferson_holocall_camera'

STUDIO_SECONDS = 20     # a cold studio that has not arrived by then is not coming
RING_SECONDS = 30       # one ring: Wakako's call gives up after 30 s
DIAL_SECONDS = 2

# The fact PhoneSystem writes as the call changes state, built from the two
# contact ids exactly as `PhoneSystem.GetPhoneCallFactName` builds it:
#   Ended 0    Initializing 1    Talking 2    Rejected 3
PHONE_FACT = ('phonecall_' + cfg.FIXER_ID + '_with_player').lower()

# ---- graph ----------------------------------------------------------------
chain = []
PHASE_IN = add_input()
chain.append((PHASE_IN, 'Out'))


def step(nid, in_sock='In', out_sock='Out'):
    prev_nid, prev_sock = chain[-1]
    b.connect((prev_nid, prev_sock), (nid, in_sock))
    chain.append((nid, out_sock))


def open_journal(class_name, path, notify=1):
    step(add_journal(class_name, path, notify=notify), in_sock='Active')


def close_journal(class_name, path):
    step(add_journal(class_name, path, notify=0), in_sock='Succeeded')


def johnny_beat(scene, entry, exit_):
    """One of Johnny's lines, with V held still around it (gig 03's door
    beat): the hold, a second for V to stop, the scene, the hold lifted."""
    step(add_setvar(F + 'hold', 1))
    step(add_delay(1.0))
    step(add_scene(SCENES + scene + '.scene', ANCHOR_PLAYER, [entry], [exit_]),
         in_sock=entry, out_sock=exit_)
    step(add_setvar(F + 'hold', 0))


def open_objective(oid):
    open_journal('gameJournalQuestObjective', PHASE + '/' + oid)
    if PINS.get(oid):
        open_journal('gameJournalQuestMapPin',
                     PHASE + '/' + oid + '/' + PINS[oid], notify=0)
    # BAYANI'S OWN DOT, on the objectives he is about: an NPC pin on his
    # body (gen_journal.NPC_PINS), so the map and the minimap mark him as
    # the game marks a friend, not only while he is the objective.
    if gen_journal.NPC_PINS.get(oid):
        open_journal('gameJournalQuestMapPin',
                     PHASE + '/' + oid + '/' + gen_journal.NPC_PINS[oid], notify=0)


def close_objective(oid):
    close_journal('gameJournalQuestObjective', PHASE + '/' + oid)


def talk_to(entry, name, entry_sock, exits, done_fact, radius=None):
    """An in-person conversation with a placed body, the fixer's loop
    (`tools/fixer01/gen_questphase.py`, "IN PERSON"): wait for V within
    TALK_RADIUS of the entry, play the scene where V stands, and if V walked
    off before the end (`exits[-1]`, the scene's walk-away exit) re-arm a
    second later. Every other exit meets on `done_fact`, so the caller's
    chain continues from there. Returns the scene node for a caller that
    wants to read an exit on its own."""
    top = add_pause_distance(CAST_REF, radius or cfg.TALK_RADIUS, entry=entry,
                             cmp='Less')
    step(top)
    node = add_scene(SCENES + name + '.scene', ANCHOR_PLAYER,
                     [entry_sock], exits)
    b.connect(chain[-1], (node, entry_sock))
    rearm = add_delay(1)
    b.connect((node, exits[-1]), (rearm, 'In'))
    b.connect((rearm, 'Out'), (top, 'In'))
    done = add_setvar(done_fact, 1)
    for x in exits[:-1]:
        b.connect((node, x), (done, 'In'))
    chain.append((done, 'Out'))
    return node


def call(phase, rejectable=False):
    """Her calling V. Caller and addressee are journal paths. No phone
    restriction: a restriction applied and never released is a phone broken
    for the rest of the save (gig 01's note)."""
    return add_call_contact(FIXER_CONTACT, PLAYER_CONTACT, phase, video=True,
                            prefab=STUDIO_PREFAB, rejectable=rejectable,
                            restrict=False)


def her_call(prefix, play, on_miss=None):
    """She rings V on video once; `play()` adds the scene if V answers, and
    `on_miss()` what replaces it if V does not.

    Her introduction call, node for node, with the game's own fixer rule
    for an answer that does not come (the design call, 2026-10-13: "copy
    vanilla"). Wakako's brief and debrief scenes
    (`sts_wbr_hil_01_holocall_prebrief.scene`) set the call rejectable, and
    a call rejected or not answered within 30 seconds leaves by the scene's
    `rejected_out`, after which the gig sends the text and goes on. A V who
    has muted fixer calls gets the text with no ring at all
    (`add_condition_phone_muted`). Until 2026-10-13 she rang again every
    minute until V answered.

    `play` is called with the chain at the connected call and must leave
    the chain at the scene's exit; `on_miss` is called with the chain at the
    end of a call that did not happen and must leave it at its own end.
    Both ways join, so the gig goes on either way.
    """
    P = F + prefix
    for latch in ('_claim', '_video', '_rings', '_step'):
        step(add_setvar(P + latch, 0))

    # NOT WHILE V IS TALKING TO HER: V may be in her own conversation, which
    # plays in the same studio (audit 2026-10-01).
    step(add_pause_fact(F + 'fixer_free'))
    # MUTED: no ring, straight to what replaces the call.
    muted = add_condition_phone_muted()
    b.connect(chain[-1], (muted, 'In'))
    miss_join = add_setvar(P + '_step', 4)
    b.connect((muted, 'True'), (miss_join, 'In'))
    chain.append((muted, 'False'))
    step(add_setvar(P + '_claim', 0))
    # Ask for the studio pieces: her own call hides both as it ends
    # (tools/fixer01/gen_questphase.py; audit 2026-10-01, second pass). This
    # says which pieces should exist; the call node below is what loads the
    # sector (gotcha 105).
    step(add_prefab_variant(LIGHTS_REF, LIGHTS_VARIANT, True))
    step(add_prefab_variant(SETUP_REF, SETUP_VARIANT, True))
    # PhoneSystem's own call fact persists at Talking once a call has been
    # answered, so it is cleared before the ring.
    step(add_setvar(PHONE_FACT, 0))
    # THE PHONE STARTS RINGING, and the studio sector starts arriving with it.
    step(call('IncomingCall', rejectable=True))

    # Wait for the camera node, raced against a clock, then switch it on. On
    # the timeout the call still goes out, into an empty frame, which is the
    # known cold-studio failure and better than a gig that stops here.
    studio = add_race2(chain[-1],
                       (add_pause_node_loaded(CAMERA_REF), 'In', 'Out'),
                       (add_delay(STUDIO_SECONDS), 'In', 'Out'),
                       P + '_claim')
    got = add_toggle_component(CAMERA_REF, 'RenderToTextureCamera', True)
    b.connect((studio, 'True'), (got, 'In'))
    lit = add_setvar(P + '_video', 1)
    b.connect((got, 'Out'), (lit, 'In'))
    join = add_setvar(P + '_step', 1)
    b.connect((lit, 'Out'), (join, 'In'))
    b.connect((studio, 'False'), (join, 'In'))
    chain.append((join, 'Out'))

    # Did V answer? Greater than 1 is Talking or Rejected: the player did
    # something. Then RE-READ in the same tick, because a declined call
    # reports Rejected and then Talking a second and a half later (gotcha
    # 10j).
    step(add_setvar(P + '_claim', 0))
    answer = add_race2(chain[-1],
                       (add_pause_fact(PHONE_FACT, 1, 'Greater'), 'In', 'Out'),
                       (add_delay(RING_SECONDS), 'In', 'Out'),
                       P + '_claim')
    picked = add_condition_fact(PHONE_FACT, 2, 'Equal')
    b.connect((answer, 'True'), (picked, 'In'))
    b.connect((answer, 'False'), (picked, 'In'))

    # NOT ANSWERED OR REJECTED: take the chrome and the studio down, once.
    missed = call('EndCall')
    b.connect((picked, 'False'), (missed, 'In'))
    m_cam = add_toggle_component(CAMERA_REF, 'RenderToTextureCamera', False)
    b.connect((missed, 'Out'), (m_cam, 'In'))
    m_setup = add_prefab_variant(SETUP_REF, SETUP_VARIANT, False)
    b.connect((m_cam, 'Out'), (m_setup, 'In'))
    m_lights = add_prefab_variant(LIGHTS_REF, LIGHTS_VARIANT, False)
    b.connect((m_setup, 'Out'), (m_lights, 'In'))
    m_count = add_addvar(P + '_rings', 1)
    b.connect((m_lights, 'Out'), (m_count, 'In'))
    b.connect((m_count, 'Out'), (miss_join, 'In'))

    # ANSWERED: connect, speak, hang up.
    chain.append((picked, 'True'))
    step(add_delay(DIAL_SECONDS))
    step(call('StartCall'))
    step(add_setvar(P + '_step', 2))
    play()
    step(call('EndCall'))
    step(add_toggle_component(CAMERA_REF, 'RenderToTextureCamera', False))
    step(add_prefab_variant(SETUP_REF, SETUP_VARIANT, False))
    step(add_prefab_variant(LIGHTS_REF, LIGHTS_VARIANT, False))
    step(add_setvar(P + '_step', 3))
    answered = chain[-1]

    # BOTH WAYS JOIN.
    done = add_setvar(P + '_done', 1)
    b.connect(answered, (done, 'In'))
    chain.append((miss_join, 'Out'))
    if on_miss is not None:
        on_miss()
    b.connect(chain[-1], (done, 'In'))
    chain.append((done, 'Out'))


def scene_node(name, entry, exit_):
    return add_scene(SCENES + name + '.scene', cfg.ANCHOR_STUDIO,
                     [entry], [exit_])


# ---- the start ------------------------------------------------------------
# The id of the wait for her introduction, fixed (below).
INTRO_WAIT_ID = 22
# Seconds after the fight before Bayani's goodbye is offered wherever he
# is, should he never reach his spot in the hall: his walk there takes
# about ten.
BYE_WAIT = 60.0
#
# NOBODY IS THERE YET. A mod community spawns its entries on save load
# whatever `entryActiveOnStart` says (backlog run 14), so without this
# Ligaya, Stamps, Bayani, three Claws, six guards, a car and a van would be
# standing there from the moment the save loads, in every save. Each entry
# off by name, FIRST, before anything waits: gig 03 does it before its own
# gate (tools/gig03/gen_questphase.py), and until the audit of 2026-10-01
# this came after the wait for her introduction, so every save before her
# call kept the whole cast standing.
for _e in CAST_ENTRIES:
    if _e == gen_community.LIGAYA:
        continue
    step(add_community('Deactivate', CAST_REF, entry=_e))
# EXCEPT LIGAYA, WHO KEEPS THE STALL. The game's own vendor there is
# deleted by the manifest for good, so without her the stall stood empty
# before the gig and after it (audit 2026-10-13; the design call: "keep
# her"). She says nothing until the job, and stays when it is over.
step(add_community('Activate', CAST_REF, entry=gen_community.LIGAYA))

# HER FIRST, THEN THE GIG. The phase waits for her introduction call to have
# been taken (her own fact, set by her graph) before anything else, so the
# gig cannot begin for a V who has never heard of her: no contact, no codex
# entry and no icon to count on would exist yet.
# THE WAIT IS NODE 22, AND STAYS 22 however many people the cast has: a
# save made before her call resumes here by that number (gotcha 123).
# Playtest 2026-10-13: the cast lost two entries, this wait moved to node
# 20, and a save parked at 22 resumed past Ligaya's switch-on, with the icon
# on the map, an empty stall and no call.
skip_ids_to(INTRO_WAIT_ID)
step(add_pause_fact(cfg.FIXER_INTRO_DONE))

# THE OFFER, the game's own shape: a gig is tied to a place, not a clock. Once her
# introduction is done the gig's icon is on the map at Ligaya's stall, and
# V coming within OFFER_RADIUS of the stall is what starts her call (the
# design call, 2026-10-13: "If the player already took the intro call,
# then the pin of the quest appears, when we get near that, it triggers the
# call"). The day's wait after her introduction that stood here is gone.
# Gig04_Places.reds sets `cc_g04_near_offer`; it is written only before
# the job has started, and only once V has been OFFER_ARM_RADIUS from the
# stall since her introduction (`cc_g04_offer_armed`), so Ligaya, switched
# on below, has had the chance to appear (gotcha 132).
# LIGAYA IS AT HER STALL FROM HERE ON, before V can be near it. The game's
# own gig switches its people on first, then its icon, then waits for V
# (sts_wbr_hil_01_open_world, the spawn node before the icon). Playtest
# 2026-10-13: switched on as the job arrived, with the call now made at the
# stall, she never appeared ("since I was already at Kabuki when I got the
# call, the sister's not there").
step(add_community('Activate', CAST_REF, entry=gen_community.LIGAYA))
_ligaya_on = chain[-1]
step(add_journal('gameJournalPointOfInterestMappin', POI, notify=0),
     in_sock='Active')
# STAMPS IS SWITCHED ON HERE, once V has been 250 m from both the stall and
# his bar (`cc_g04_offer_armed`, Gig04_Places.reds): a person switched on
# with V nearby does not appear (gotcha 132), and the call rings within
# OFFER_RADIUS of the stall (audit 2026-10-13). Until then he was switched
# on as the job arrived.
step(add_pause_fact(F + 'offer_armed'))
# NO PASSER-BY ON HIS STOOL (gen_community.BAR_NULL), from now until he goes.
step(add_crowd_null_area(gen_community.BAR_NULL_REF, True))
step(add_community('Activate', CAST_REF, entry=gen_community.STAMPS))
step(add_pause_fact(F + 'near_offer'))

# NOT WHILE V IS ALREADY TALKING TO HER. Her own graph keeps
# `cc_f01_talk_mode` at 1 or 2 for the length of her conversation, in person
# or on the phone, and both use her or her studio. 0 is idle.
# `cc_g04_fixer_free` is Gig04_Places.reds's reading of it, which also lets
# an in-person talk end once V is 100 m from her: one left by fast travel
# may never set it back to 0. Same node, same id (gotcha 123).
step(add_pause_fact(F + 'fixer_free'))


# ---- her call -------------------------------------------------------------
def play_brief():
    step(scene_node('gig04_brief', 'brief_in', 'brief_out'),
         in_sock='brief_in', out_sock='brief_out')


her_call('brief', play_brief)

# ---- the job --------------------------------------------------------------
step(add_journal_quest(QUEST), in_sock='Active')
open_journal('gameJournalQuestDescription', BRIEF, notify=0)
# WITH ITS PIN: `open_objective` activates the map pin with the objective,
# which `open_journal` alone does not (docs/map-pins-playbook.md; audit
# 2026-10-01).
open_objective(gen_journal.OBJECTIVES[0][0])
# HER TEXT, with the gig card. It carries its own arrival delay (gen_journal),
# which also keeps its notice off the frame the quest's notice is on.
open_journal('gameJournalPhoneMessage', MSG_BRIEF)
step(add_setvar(F + 'started', 1))

# ---- the stall ------------------------------------------------------------
#
# Ligaya and Stamps have been in place since before her call (above).
talk_to(gen_community.LIGAYA, 'gig04_stall', 'stall_in',
        ['stall_out', 'stall_left'], F + 'stall_done')
close_objective('obj_stall')

# ---- Stamps's couch, and his shard ---------------------------------------
#
# HE IS NOT THERE (the design call, 2026-10-01). Ligaya sends V to his couch
# in the alley; his shard is on its seat: Orbital Air's payment,
# the Claws, and his barkeep. TWO OBJECTIVES, the shard playbook's rule.
# Gig04_Shard.reds reads the journal entry's state from here on: `_got`
# when the shard is in V's hands by either route, `_read` when the reader
# has been raised and shut.
open_objective('obj_couch')
step(add_setvar(F + 'shard_armed', 1))
step(add_pause_fact(F + 'shard_got'))
close_objective('obj_couch')
open_objective('obj_read')
step(add_pause_fact(F + 'shard_read'))
close_objective('obj_read')

# ---- the booth ------------------------------------------------------------
#
# STAMPS, TALKING OR BEATEN. He cannot die before he talks (the design
# call, 2026-10-02: "he needs to stay alive, wounded so he talks, exactly
# like gig02"). The conversation wait is raced against an attack:
# Gig04_Places.reds sets `cc_g04_stamps_hit` at his first wound or
# knockout, and the fight starts. Killed after he talked, only her last
# call changes.
# STAMPS IS AT THE BAR on the walkway west of the market, on a stool. His
# conversation is the same one; only the place moved.
open_objective('obj_bar')
# THE LOOP TARGET is the claim's reset, which a race needs every time round.
booth_reset = add_setvar(F + 'booth_claim', 0)
step(booth_reset)
# WHICH BUTTON V PICKED, written by the scene as the button is taken
# (gen_scenes, BOOTH_PICKED): 1 Body, 2 Intelligence, 3 paid, 4 the fight.
# A walk-off after a pick is read by it below.
step(add_setvar(F + 'booth_picked', 0))
alive = add_race2(chain[-1],
                  (add_pause_distance(CAST_REF, cfg.TALK_RADIUS,
                                      entry=gen_community.STAMPS, cmp='Less'),
                   'In', 'Out'),
                  (add_pause_fact(F + 'stamps_hit'), 'In', 'Out'),
                  F + 'booth_claim')
booth = add_scene(SCENES + 'gig04_booth.scene', ANCHOR_PLAYER, ['booth_in', 'booth_again'],
                  ['booth_paid', 'booth_threat', 'booth_deal', 'booth_fight',
                   'booth_left'])
# `cc_g04_booth_on` is 1 while his conversation is up, for the dev window.
# HE CAN BE HURT WHILE IT IS UP. A shield over the conversation stood here
# for two builds and is gone (playtest 2026-10-01: "cannot wound Stamps,
# he's invincible, remove it"). What it guarded against is answered in the
# graph instead: a wound while the scene is up cuts the scene and starts
# the fight, below.
booth_on = add_setvar(F + 'booth_on', 1)
b.connect((alive, 'True'), (booth_on, 'In'))
# BACK AFTER HIS THREE LINES: straight to the buttons (`booth_again`). The
# scene writes `cc_g04_booth_heard` as his third line starts (audit
# 2026-10-02: a walk-off replayed his speech on every approach).
booth_heard = add_condition_fact(F + 'booth_heard', 1, 'Equal')
b.connect((booth_on, 'Out'), (booth_heard, 'In'))
b.connect((booth_heard, 'True'), (booth, 'booth_again'))
b.connect((booth_heard, 'False'), (booth, 'booth_in'))
# WALKED OFF, from either set of buttons. Before a pick: re-arm a second
# later, back through the race so a wound in the meantime is still read.
# AFTER A PICK the walk-off is read as the pick (audit 2026-10-01): a V who
# paid and walked off during his answer has paid, the game took the money
# as the button was picked, and must not be asked again; a V who picked
# the fight and walked off is in the fight.
booth_off = add_setvar(F + 'booth_on', 0)
b.connect((booth, 'booth_left'), (booth_off, 'In'))
left_none = add_condition_fact(F + 'booth_picked', 0, 'Equal')
b.connect((booth_off, 'Out'), (left_none, 'In'))
booth_rearm = add_delay(1)
# NOT AFTER ANOTHER WAY ON HAS BEEN TAKEN (audit 2026-10-01, second
# pass).
# Read AFTER the second's delay, so a claim written on the same frame as
# the walk-off has landed (verification pass, 2026-10-01).
left_open = add_condition_fact(F + 'booth_once', 0, 'Equal')
b.connect((left_none, 'True'), (booth_rearm, 'In'))
b.connect((booth_rearm, 'Out'), (left_open, 'In'))
b.connect((left_open, 'True'), (booth_reset, 'In'))
left_fight = add_condition_fact(F + 'booth_picked', 4, 'Equal')
b.connect((left_none, 'False'), (left_fight, 'In'))
left_paid = add_condition_fact(F + 'booth_picked', 3, 'Equal')
b.connect((left_fight, 'False'), (left_paid, 'In'))
# PAID: the game took the thousand itself as V picked the option (the
# payment check, questkit.scene.payment_check); the fact only records it.
# SCARED HIM OR SOLD HIM ON HODAN: nothing to take.
paid = add_setvar(F + 'stamps_paid', 1)
b.connect((booth, 'booth_paid'), (paid, 'In'))
b.connect((left_paid, 'True'), (paid, 'In'))
talked = add_setvar(F + 'stamps_talked', 1)
b.connect((paid, 'Out'), (talked, 'In'))
b.connect((booth, 'booth_threat'), (talked, 'In'))
b.connect((booth, 'booth_deal'), (talked, 'In'))
b.connect((left_paid, 'False'), (talked, 'In'))
# HURT WHILE THE CONVERSATION IS UP: a wait on the wound runs beside the
# scene from its start. If it completes first it cuts the scene, the way a
# race disarms its loser (questgraph.add_cut_control), and the fight
# starts. Every exit of the scene cuts the wait, so it can never fire later.
booth_hit = add_pause_fact(F + 'stamps_hit')
b.connect((booth_on, 'Out'), (booth_hit, 'In'))
booth_cut_scene = add_cut_control()
b.connect((booth_hit, 'Out'), (booth_cut_scene, 'In'))
b.connect((booth_cut_scene, 'CutSource'), (booth, 'CutDestination'))
booth_cut_wait = add_cut_control()
for _x in ('booth_paid', 'booth_threat', 'booth_deal', 'booth_fight', 'booth_left'):
    b.connect((booth, _x), (booth_cut_wait, 'In'))
b.connect((booth_cut_wait, 'CutSource'), (booth_hit, 'CutDestination'))
# ONE TOKEN ON, HOWEVER MANY ARRIVE (audit 2026-10-01): a wound on the
# same frame as a scene exit sends two, and two would run the van and the
# room twice, a scene entered twice among it (gotcha 51). Each way on reads
# `cc_g04_booth_once` and writes it before it goes on, the claim add_race2
# uses for the same frame.
booth_done = add_setvar(F + 'booth_done', 1)
once_a = add_condition_fact(F + 'booth_once', 0, 'Equal')
b.connect((talked, 'Out'), (once_a, 'In'))
claim_a = add_setvar(F + 'booth_once', 1)
b.connect((once_a, 'True'), (claim_a, 'In'))
booth_closed = add_journal('gameJournalQuestObjective', PHASE + '/obj_bar',
                           notify=0)
b.connect((claim_a, 'Out'), (booth_closed, 'Succeeded'))
b.connect((booth_closed, 'Out'), (booth_done, 'In'))
once_b = add_condition_fact(F + 'booth_once', 0, 'Equal')
claim_b = add_setvar(F + 'booth_once', 1)
b.connect((once_b, 'True'), (claim_b, 'In'))
b.connect((claim_b, 'Out'), (booth_done, 'In'))

# THE FIGHT, gig 02's merc: Gig04_Places.reds makes him hittable and
# Immortal on `cc_g04_stamps_fight`, and sets `cc_g04_stamps_down` at a
# third of his health, knocking him down with the game's own Defeated
# fall. Three seconds for the fall and the settle (gig 02's pose lab),
# then the beaten scene: the address, from the floor. The objective says
# what to do while it lasts; "Find Stamps" closes as the fight starts.
# THREE WAYS IN: the fight button, a walk-off after it, and a wound
# before or during the conversation (the race's False arm and the cut
# beside the scene). He is Immortal from the moment his body is found, so
# the fight has no death to race against. THE BEATEN SCENE WAITS FOR V NEAR
# HIM: a civilian runs when shot, and his lines would play at V from
# wherever he fell.
_main = chain
fight_start = add_setvar(F + 'stamps_fight', 1)
# ONE FIGHT: the button and a wound on the same frame send two tokens.
# `cc_g04_stamps_fight` is the claim, read here and written by the next
# node (add_race2's shape). `cc_g04_booth_once` is read first, so no way
# in opens after V has talked.
fight_open = add_condition_fact(F + 'booth_once', 0, 'Equal')
fight_claim = add_condition_fact(F + 'stamps_fight', 0, 'Equal')
b.connect((booth, 'booth_fight'), (fight_open, 'In'))
b.connect((left_fight, 'True'), (fight_open, 'In'))
b.connect((alive, 'False'), (fight_open, 'In'))
b.connect((booth_cut_scene, 'Out'), (fight_open, 'In'))
b.connect((fight_open, 'True'), (fight_claim, 'In'))
b.connect((fight_claim, 'True'), (fight_start, 'In'))
chain = [(fight_start, 'Out')]
close_objective('obj_bar')
open_objective('obj_beat')
step(add_pause_fact(F + 'stamps_down'))
step(add_delay(3.0))
step(add_pause_distance(CAST_REF, cfg.LEAVE_RADIUS,
                        entry=gen_community.STAMPS, cmp='Less'))
step(add_scene(SCENES + 'gig04_beaten.scene', ANCHOR_PLAYER, ['beaten_in'],
               ['beaten_out']), in_sock='beaten_in', out_sock='beaten_out')
close_objective('obj_beat')
step(add_setvar(F + 'stamps_talked', 1))
b.connect(chain[-1], (once_b, 'In'))
chain = _main
chain.append((booth_done, 'Out'))
# STAMPS KILLED, switched off once V is 150 m from the bar
# (`cc_g04_bar_far`): after a reload he stood alive at the bar while her last
# call said he was dead (audit 2026-10-01, second pass). On a branch of its
# own; alive, he goes with Ligaya at the end.
_stamps_gone = add_pause_facts([(F + 'stamps_dead', 1, 'Equal'),
                                (F + 'bar_far', 1, 'Equal')])
b.connect(chain[-1], (_stamps_gone, 'In'))
_stamps_off = add_community('Deactivate', CAST_REF, entry=gen_community.STAMPS)
b.connect((_stamps_gone, 'Out'), (_stamps_off, 'In'))
_bar_open = add_crowd_null_area(gen_community.BAR_NULL_REF, False)
b.connect((_stamps_off, 'Out'), (_bar_open, 'In'))

# ---- the van: the false lead ---------------------------------------------
#
# WHERE STAMPS SENDS V: the Tyger Claws' van in a yard in south-west
# Little China, where they kept Bayani before moving him (gig04_config,
# "THE CLAWS' VAN"). No fight: V scans three clues round it, the game's own
# clue hunt (the NCPD activity ma_bls_ina_se1_07: each clue sets a fact
# when its scan completes, and a fact pause hears it), counted on the
# objective as "[n/3]" (q000's counter). Then the Claws' shard, on the
# ground behind the van, names the shop.
open_objective('obj_flop')
step(add_community('Activate', CAST_REF, entry=gen_community.VAN_ENTRY))
step(add_setvar(F + 'flop_armed', 1))
# V AT THE VAN: Gig04_Places.reds raises `cc_g04_van_near` within 20 m.
step(add_pause_fact(F + 'van_near'))
close_objective('obj_flop')
# JOHNNY AT THE VAN, before the hunt (the design call, 2026-10-14; gen_scenes,
# build_johnny_van). GIG 03'S SHAPE: V held still first (`cc_g04_hold`,
# Gig04_Places.reds), a second for V to come to a stop, then Johnny, then
# the hold lifted. Playtest 2026-10-14: played at a walking V, he spoke
# while still appearing and V had walked past him.
johnny_beat('gig04_johnny_van', 'johnny_van_in', 'johnny_van_out')
open_objective('obj_clues')
# THE SHARD COUNTS FROM HERE, so a V who finds it before the clues moves on
# (the design call, 2026-10-14: "If the player immediately finds the shard
# without the clues, you should still advance"). Gig04_Shard.reds reads the
# journal, so a shard taken before this is heard as soon as it is armed.
step(add_setvar(F + 'shard2_armed', 1))
# ONE BRANCH PER CLUE, each adding one to the counter once its fact is up.
# A clue scanned before this point counts at once.
_clues_open = chain[-1]
for _n, _p, _y in cfg.CLUES:
    _found = add_pause_fact('cc_g04_clue_' + _n)
    b.connect(_clues_open, (_found, 'In'))
    _count = add_objective_counter(PHASE + '/obj_clues')
    b.connect((_found, 'Out'), (_count, 'Increment'))
# ALL THREE FOUND raises `cc_g04_clues_all`, on a branch of its own, so the
# hunt can wait on one fact OR the shard with a single pause.
_all = add_pause_facts([('cc_g04_clue_' + _n, 0, 'Greater') for _n, _p, _y in cfg.CLUES])
b.connect(_clues_open, (_all, 'In'))
_all_set = add_setvar(F + 'clues_all', 1)
b.connect((_all, 'Out'), (_all_set, 'In'))
step(add_pause_facts([(F + 'clues_all', 0, 'Greater'),
                      (F + 'shard2_got', 0, 'Greater')], operation='OR'))
# A second, so the third count is on screen before the objective closes.
step(add_delay(1.0))
close_objective('obj_clues')
open_objective('obj_flop_take')
step(add_pause_fact(F + 'shard2_got'))
close_objective('obj_flop_take')
open_objective('obj_flop_read')
step(add_pause_fact(F + 'shard2_read'))
close_objective('obj_flop_read')
# THE VAN, switched off once V is 150 m from it (`cc_g04_flop_far`,
# Gig04_Places.reds), on a branch of its own so it never goes in view. The
# end kills the branch if V never leaves.
_flop_far = add_pause_fact(F + 'flop_far', 1, 'Equal')
b.connect(chain[-1], (_flop_far, 'In'))
_flop_main = chain
chain = [(_flop_far, 'Out')]
step(add_community('Deactivate', CAST_REF, entry=gen_community.VAN_ENTRY))
chain = _flop_main

# ---- the room -------------------------------------------------------------
#
# BAYANI AND THE CLAWS ARE SWITCHED ON HERE, half a kilometre from the room,
# and Gig04_Places.reds is armed: it turns each Claw on V (attitude AND
# senses, gotcha 77) as the bodies stream in while V is within reach of the
# door, so the two on the street are looking before V is in their view.
open_objective('obj_room')
# THE ROOM'S CLAWS IN TWO GROUPS (a test, playtest 2026-11-01: the game
# froze for a second or two on a bike about 175 m out, and the room's own
# pieces were ruled out). Bayani and the Claw deep in the hall are switched
# on here as before; the two by the door only once V is within
# ROOM_SECOND_GROUP m of Bayani, so the game places two people at a time,
# not four. Their old slots in this chain keep their node ids (gotcha 123)
# and write a readout instead; the new nodes take ids from ROOM_LATE_IDS.
ROOM_DOOR_CLAWS = ('claw1', 'claw2')
for _e in ROOM_ENTRIES:
    if _e in ROOM_DOOR_CLAWS:
        step(add_setvar(F + 'dbg_room_split', 1))
    else:
        step(add_community('Activate', CAST_REF, entry=_e))
step(add_setvar(F + 'room_armed', 1))
_split = chain[-1]
_second = late(add_pause_distance, CAST_REF, cfg.ROOM_SECOND_GROUP,
               gen_community.BAYANI, ids=ROOM_LATE_IDS)
b.connect(_split, (_second, 'In'))
_prev = (_second, 'Out')
for _e in ROOM_DOOR_CLAWS:
    _on = late(add_community, 'Activate', CAST_REF, _e, ids=ROOM_LATE_IDS)
    b.connect(_prev, (_on, 'In'))
    _prev = (_on, 'Out')
# "GO TO" CLOSES AT THE AREA, a circle of ROOM_LEAVE_RADIUS round Bayani's
# spot, which reaches about 13 m out from the door onto the street
# (gen_community.ROOM_AREA).
step(add_pause_triggers([AREA_REF], inside=True))
close_objective('obj_room')
open_objective('obj_bayani')
# THE CLAWS FIRST (the design call, 2026-10-13: "first take out the claws,
# then talk with the brother, then Orbital shows up, only after fighting is
# done, then he moves"). Gig04_Places.reds sets `cc_g04_claws_clear` once
# all three are down; his talk, and Orbital Air's arrival with it, wait on
# it.
step(add_pause_fact(F + 'claws_clear'))

# ---- Orbital Air -----------------------------------------------------------
#
# THEY PULL UP WHILE V TALKS TO HIM, with V inside: one car and three guards
# on the street outside the door (the design calls, 2026-10-01: "no choices
# this time, just fight", and 2026-10-02: "3 goons, 1 car"). Switched on as
# V reaches him, which is the moment the talk starts, on a side branch, so
# they are outside by V's "Looks like we got company..." at its end (the
# design call, 2026-10-13, on a warning line from Bayani: "how would he
# know?"; V hears them). THEY WAIT WHERE NOBODY INSIDE CAN SEE THEM, on the
# pavement against the front wall either side of the door (gig04_config
# OA_GUARDS), and come in on her line: its start raises `cc_g04_oa_armed`,
# and each guard is sent along his own path through the door into the
# lobby at a sprint (gen_room OA_PATH_REFS), the patrol order Bayani's run
# uses. Gig04_Places.reds pulls each out of his standing pose so the order
# does not wait behind it (gotcha 135), and turns each on V once he is
# inside (the design call, 2026-10-25: "they appear where the player cannot
# see them, then become hostile and ... run inside"). Started on the street
# and turned on V there, they stayed outside (playtest 2026-10-14), which is
# what the paths are for. Until 2026-10-25 they stood in the lobby, seen
# appearing from the cell, and V was held facing Bayani to hide it.
# One of two sets of three, by `cc_g04_ep1`: Orbital Air's own guards need
# Phantom Liberty, and a V without it gets the game's corporate security
# (gen_community, OA_PL and OA_BASE). Gig04_Places.reds turns them on V,
# counts them down, and sets `cc_g04_oa_clear` when the three are down;
# only then does Bayani run.
_main = chain
_near_him = add_pause_distance(CAST_REF, cfg.BAYANI_TALK_RADIUS, entry=gen_community.BAYANI,
                               cmp='Less')
b.connect(chain[-1], (_near_him, 'In'))
_has_ep1 = add_condition_fact(F + 'ep1')
b.connect((_near_him, 'Out'), (_has_ep1, 'In'))
# WHICH SET CAME is written in each branch (`cc_g04_oa_set`, 1 Orbital Air,
# 2 security), and the script watches that set: re-deriving it from
# `cc_g04_ep1` every tick could, if the two ever disagreed, count down a set
# that never spawned and clear the fight with the real guards standing
# (audit 2026-10-01).
chain = [(_has_ep1, 'True')]
step(add_setvar(F + 'oa_set', 1))
for _e in gen_community.OA_PL_ENTRIES:
    step(add_community('Activate', CAST_REF, entry=_e))
_pl_end = chain[-1]
chain = [(_has_ep1, 'False')]
step(add_setvar(F + 'oa_set', 2))
for _e in gen_community.OA_BASE_ENTRIES:
    step(add_community('Activate', CAST_REF, entry=_e))
_base_end = chain[-1]
_oa_cars = add_setvar(F + 'oa_cars', 1)
b.connect(_pl_end, (_oa_cars, 'In'))
b.connect(_base_end, (_oa_cars, 'In'))
chain = [(_oa_cars, 'Out')]
for _e in gen_community.OA_CAR_ENTRIES:
    step(add_community('Activate', CAST_REF, entry=_e))
step(add_setvar(F + 'oa_on', 1))
# IN THEY COME, on her line: both sets' patrol orders, side by side; only
# the set that was switched on has bodies to take them. Nothing waits on a
# patrol's end (gotcha 136).
step(add_pause_fact(F + 'oa_armed'))
_go = chain[-1]
for _i, _path in enumerate(gen_room.OA_PATH_REFS):
    for _e in (gen_community.OA_PL_ENTRIES[_i], gen_community.OA_BASE_ENTRIES[_i]):
        b.connect(_go, (add_ai_patrol(CAST_REF, _e, _path, movement='Sprint'), 'In'))
chain = _main

talk_to(gen_community.BAYANI, 'gig04_room', 'room_in',
        ['room_out', 'room_left'], F + 'room_done', radius=cfg.BAYANI_TALK_RADIUS)
close_objective('obj_bayani')
# HE STANDS UP on "Yes. I can walk." (gen_scenes, build_room) and, as the
# talk ends, Gig04_Places.reds puts him on his standing spot in the cell by
# its door (gen_community.BAYANI_STAND), where he waits out the fight (the
# design call, 2026-10-14: "he should already get up when he says that he
# can get up, but stay inside the room until orbital air has been
# defeated").
# They are there by now (the side branch above ran as V reached him).
step(add_pause_fact(F + 'oa_on'))
step(add_setvar(F + 'oa_armed', 1))
open_objective('obj_oa')
step(add_pause_fact(F + 'oa_clear'))
close_objective('obj_oa')

# HIS GOODBYE (the design call, 2026-10-14: "a final scene with the brother
# approaching V ... he says goodbye and thanks, and then runs/leaves"). HE
# WALKS TO THE HALL ON A PATH, since 2026-10-25: once Orbital Air is down
# and both doors are open, Gig04_Places.reds cancels his order to the cell
# spot, sends his pose its fast exit and raises `cc_g04_bye_go`, and this
# sends him along `gen_room.BYE_PATH_REF` (the first leg of his run, from
# the cell spot to the hall spot) with the patrol order his run uses. The
# script sets `cc_g04_bye_here` to 1 once his body is within BYE_ARRIVED of
# the hall spot, then holds him there with the use-workspot order. The talk
# is offered only then; nothing waits on the patrol's end (gotcha 136). The
# use-workspot order alone did the walk until now, and the log of
# 2026-10-25 had it take one step and stop in a pose 9 m short, every time.
# The talk also opens after BYE_WAIT seconds wherever he is, should he
# never get there.
_bye_go = add_pause_fact(F + 'bye_go')
b.connect(chain[-1], (_bye_go, 'In'))
_bye_walk = add_ai_patrol(CAST_REF, gen_community.BAYANI, gen_room.BYE_PATH_REF,
                          movement='Walk')
b.connect((_bye_go, 'Out'), (_bye_walk, 'In'))
# THE WALK CUT ONCE HE IS THERE (`cc_g04_bye_here`, 1 on the spot, 2 from
# the fallback): a patrol's order is never heard to end (gotcha 136), and
# one still on him held his run back behind it (playtest 2026-10-25, the
# run ordered and released at 12:09:48 and he stood in the hall). The cut
# is how this graph ends a node's work, as it ends the railing's scene.
_bye_there = add_pause_fact(F + 'bye_here')
b.connect((_bye_go, 'Out'), (_bye_there, 'In'))
_bye_cut = add_cut_control()
b.connect((_bye_there, 'Out'), (_bye_cut, 'In'))
b.connect((_bye_cut, 'CutSource'), (_bye_walk, 'CutDestination'))
open_objective('obj_bye')
_bye_from = chain[-1]
_bye_late = add_delay(BYE_WAIT)
b.connect(_bye_from, (_bye_late, 'In'))
_bye_late_set = add_setvar(F + 'bye_here', 2)
b.connect((_bye_late, 'Out'), (_bye_late_set, 'In'))
step(add_pause_fact(F + 'bye_here'))
talk_to(gen_community.BAYANI, 'gig04_bye', 'bye_in', ['bye_out', 'bye_left'],
        F + 'bye_done', radius=cfg.BYE_TALK_RADIUS)
close_objective('obj_bye')

# HE RUNS OUT, the way the game's own gigs walk a body somewhere: the
# patrol order along the spline the room ships (gen_room.LEAVE_PATH_REF),
# cell, hall, lobby, street, to his sister's stall, once. Gig04_Places.reds
# has opened the two doors by then (it watches `cc_g04_oa_clear`). A
# switch of his entry to a second community phase respawned him a few
# steps into his walk, and a scripted move order turned him on the spot
# and he vanished (playtests 2026-10-01).
# AT A SPRINT: the patrol task reads only Sprint out of the movement type
# (PatrolControllerTask: `sprint` is set when the type is Sprint, and Run
# walks; playtest 2026-10-01, "he should be in a hurry").
# ON A SIDE BRANCH: the node's `Success` fires when the patrol is over, and
# the chain hung on it (playtest 2026-10-01: no objective after the talk).
# AFTER THE SCRIPT HAS LET GO OF HIM (`cc_g04_run_go`, Gig04_Places.reds):
# his hold on the hall spot cancelled and its pose's fast exit sent. A
# second's delay stood here until 2026-10-25; once the hall hold worked,
# the run arrived before the cancel in the same second, waited behind the
# hold and was lost (playtest: "after we say 'get out of here' he doesn't
# move"; gotcha 134).
_fork = chain[-1]
_wait = add_pause_fact(F + 'run_go')
b.connect(_fork, (_wait, 'In'))
_ran = add_setvar(F + 'bayani_ran', 1)
b.connect((_wait, 'Out'), (_ran, 'In'))
_run = add_ai_patrol(CAST_REF, gen_community.BAYANI, gen_room.LEAVE_PATH_REF,
                     movement='Sprint')
b.connect((_ran, 'Out'), (_run, 'In'))
# AGAIN AFTER A RELOAD (audit 2026-10-01): a reload between here and the
# switch-off puts him back in the cell, and the order above is spent.
# Gig04_Places.reds raises `cc_g04_bayani_rerun` when it finds a body it
# has not sent out after `cc_g04_bayani_ran`; this sends that body the same
# order, and waits again. Cut at the switch-off.
# TWO PATROL NODES IN TURN: a node still running its order may ignore a
# second entry, so a second reload during his run goes to the other one
# (audit 2026-10-01, second pass).
_rerun_wait = add_pause_fact(F + 'bayani_rerun', 1, 'Equal')
b.connect((_ran, 'Out'), (_rerun_wait, 'In'))
_rerun_clear = add_setvar(F + 'bayani_rerun', 0)
b.connect((_rerun_wait, 'Out'), (_rerun_clear, 'In'))
_run_again = add_ai_patrol(CAST_REF, gen_community.BAYANI, gen_room.LEAVE_PATH_REF,
                           movement='Sprint')
b.connect((_rerun_clear, 'Out'), (_run_again, 'In'))
_rerun_wait2 = add_pause_fact(F + 'bayani_rerun', 1, 'Equal')
b.connect((_rerun_clear, 'Out'), (_rerun_wait2, 'In'))
_rerun_clear2 = add_setvar(F + 'bayani_rerun', 0)
b.connect((_rerun_wait2, 'Out'), (_rerun_clear2, 'In'))
_run_again2 = add_ai_patrol(CAST_REF, gen_community.BAYANI, gen_room.LEAVE_PATH_REF,
                            movement='Sprint')
b.connect((_rerun_clear2, 'Out'), (_run_again2, 'In'))
b.connect((_rerun_clear2, 'Out'), (_rerun_wait, 'In'))
# THEN HE WALKS (the design call, 2026-10-13: "slow down after 200m"): each
# sprint, the first and the two after a reload, is followed by a walk along
# the route's second half (gen_room.route_halves). The patrol order starts
# from the path's closest point, which is where the sprint ended.
for _sprint in (_run, _run_again, _run_again2):
    _walk = add_ai_patrol(CAST_REF, gen_community.BAYANI, gen_room.LEAVE_PATH2_REF,
                          movement='Walk')
    b.connect((_sprint, 'Success'), (_walk, 'In'))

# AND OUT. Everything below waits on V being away from the room, so V is
# told to go, and the outline is drawn round the building meanwhile. Nobody
# vanishes in view: the cast is switched off once V is ROOM_LEAVE_RADIUS from
# Bayani, the same number the area is drawn with.
open_objective('obj_leave')
# OUT OF THE DRAWN AREA, not a distance from Bayani: he is running down the
# street by now, so a distance from him would close the objective with V
# still in the room (the trigger area is the circle on the minimap).
step(add_pause_triggers([AREA_REF], inside=False))
close_objective('obj_leave')
# THE ROOM'S CLAWS, ORBITAL AIR AND THE CAR go once V is 150 m from the
# door (`cc_g04_room_far`, Gig04_Places.reds), on a branch of their own:
# switched off with Bayani's going, they vanished, bodies and car, in front
# of a V on the street (audit 2026-10-13).
_room_from = chain[-1]
_room_main = chain
chain = [_room_from]
step(add_pause_fact(F + 'room_far', 1, 'Equal'))
for _e in CAST_ENTRIES:
    if _e in (gen_community.LIGAYA, gen_community.STAMPS, gen_community.BAYANI,
              gen_community.VAN_ENTRY):
        continue
    step(add_community('Deactivate', CAST_REF, entry=_e))
step(add_setvar(F + 'room_off', 1))
chain = _room_main
# THEN HER CALL, under "Wait for Hodan's call": TWO HOURS ON THE WORLD
# CLOCK, so her "He's out of Night City" is true when she says it (the
# design call, 2026-10-13). A wait of 45 seconds stood here from 2026-10-02,
# with Bayani still in view on his run. The waiting spot below makes the
# wait gig 02's: lean on the railing and the clock moves on.
open_objective('obj_wait')
# NOW THE SCRIPT WATCHES HIM (`cc_g04_watch_gone`) for the switch-off below.
step(add_setvar(F + 'watch_gone', 1))
# THE CAST GOES ON A BRANCH OF ITS OWN, so her call does not wait on it
# (audit 2026-10-02: a V waiting by Bayani at the stall held her call for
# good). Gig04_Places.reds raises `cc_g04_bayani_gone` once he is behind V
# and 30 m off, or 70 m off however V faces, or at the end of his route
# with V 12 m off; the cast is switched off only then (the design call:
# "he shouldn't disappear until he's out of our eye line").
_cast = chain[-1]
_cast_main = chain
chain = [_cast]
step(add_pause_fact(F + 'bayani_gone', 1, 'Equal'))
_rerun_cut = add_cut_control()
step(_rerun_cut)
b.connect((_rerun_cut, 'CutSource'), (_rerun_wait, 'CutDestination'))
b.connect((_rerun_cut, 'CutSource'), (_rerun_wait2, 'CutDestination'))
# BAYANI, AND THE VAN, which is 450 m away. Ligaya stands where
# Bayani's run ends and Stamps where V left him; the two go only once V is
# far from both (`cc_g04_market_far`, below), so neither vanishes in view
# (audit 2026-10-01). The room's Claws, Orbital Air and the car go on a
# branch of their own, below.
step(add_community('Deactivate', CAST_REF, entry=gen_community.BAYANI))
step(add_community('Deactivate', CAST_REF, entry=gen_community.VAN_ENTRY))
step(add_setvar(F + 'mid_done', 1))
# THE MARKET'S PAIR: Gig04_Places.reds raises `cc_g04_market_far` once V is
# 150 m from both the stall and the bar, from here on and past the end of
# the gig, and stops ticking once this has run.
step(add_pause_fact(F + 'market_far', 1, 'Equal'))
# STAMPS ONLY: Ligaya keeps her stall.
step(add_community('Deactivate', CAST_REF, entry=gen_community.STAMPS))
step(add_crowd_null_area(gen_community.BAR_NULL_REF, False))
step(add_setvar(F + 'market_off', 1))
chain = _cast_main
# THE WAITING SPOT, gig 02's `waiting_spot` (tools/gig02/gen_questphase.py):
# the railing west of the building is offered under "Wait for Hodan's call"
# and pinned "Waiting Spot" (the design call, 2026-10-13: "add the wait
# spot like gig02"). The scene that offers it hangs off a side branch and
# gates nothing. Taken, V leans for three seconds, the screen fades, the
# wait is over behind the black, and V stands as it fades back; her call
# follows. Not taken, the two hours run out on the world clock, which the
# game's own Skip Time also moves. Whichever comes first cuts the scene, so
# the prompt is not left up after the wait.
#
# THE GLITCH IS THE CLAIRE RACES' (playtest 2026-11-01: the vanilla wait
# plays a horizontal glitch going in and coming out, ours did not).
# `sq024_02_santo_domingo_race.scene` plays `fast_travel_glitch` on V as the
# screen goes black, and again before it comes back; the big race and the
# city race hold 0.6 s between the glitch and each cut, and so does ours
# coming back (0.4 s after the release, the fade 1 s after). Its fades are
# instant cuts; ours keep their one-second fades under the glitch, because
# an instant cut with no glitch was refused as abrupt (questgraph.add_fade).
# V STANDS BEFORE HER CALL: six seconds from the release, three and a half
# after the screen is back, so V is out of the lean before the phone rings
# (the same playtest:
# the call came while V was still standing up, with little time to answer).
#
# THESE NODES TAKE IDS FROM LATE_IDS, past every other node, so the nodes
# built after them keep the ids a save made before the room resumes by
# (gotcha 123). `late()` is defined at the top.

_fork = chain[-1]
_rail = add_scene(SCENES + 'gig04_rail.scene', gen_community.RAIL_MARKER_REF,
                  ['rail_in'], ['rail_out'])
b.connect(_fork, (_rail, 'rail_in'))
_posed = add_pause_fact(F + 'rail_taken')
b.connect(_fork, (_posed, 'In'))
_hold = add_delay(3.0)
b.connect((_posed, 'Out'), (_hold, 'In'))
# THE FADE IS A PAIR WITH NOTHING BLOCKING BETWEEN THE HALVES, and its
# times are the prologue's (gig 02's note on the same pair).
_dark = add_fade(False, 1.0)
b.connect((_hold, 'Out'), (_dark, 'In'))
_glitch_in = late(add_player_fx, 'fast_travel_glitch')
b.connect((_hold, 'Out'), (_glitch_in, 'In'))
# BEHIND THE BLACK, THE CLOCK MOVES ON by what is left of the two hours
# (`cc_g04_rail_shift`, Gig04_Places.reds, gig 02's SkipAhead), so her "He's
# out of Night City" is true when V stands up.
_shift = add_setvar(F + 'rail_shift', 1)
b.connect((_dark, 'Out'), (_shift, 'In'))
_behind = add_delay(2.0)
b.connect((_shift, 'Out'), (_behind, 'In'))
_let_go = add_setvar(F + 'rail_release', 1)
b.connect((_behind, 'Out'), (_let_go, 'In'))
_stand = add_delay(1.0)
b.connect((_let_go, 'Out'), (_stand, 'In'))
_light = add_fade(True, 1.5)
b.connect((_stand, 'Out'), (_light, 'In'))
_glitch_wait = late(add_delay, 0.4)
b.connect((_let_go, 'Out'), (_glitch_wait, 'In'))
_glitch_out = late(add_player_fx, 'fast_travel_glitch')
b.connect((_glitch_wait, 'Out'), (_glitch_out, 'In'))
step(add_setvar(F + 'rail_claim', 0))
_who = add_race2(chain[-1],
                 (add_game_delay(hours=2), 'In', 'Out'),
                 (add_pause_fact(F + 'rail_release'), 'In', 'Out'),
                 F + 'rail_claim')
_cut = add_cut_control()
b.connect((_who, 'True'), (_cut, 'In'))
b.connect((_who, 'False'), (_cut, 'In'))
b.connect((_cut, 'CutSource'), (_rail, 'CutDestination'))
chain.append((_cut, 'Out'))
step(late(add_delay, 6.0))
step(add_pause_fact(F + 'fixer_free'))


# ---- her last call --------------------------------------------------------
def play_close():
    """One of two scenes, chosen now: the second has her line about Stamps.
    Two scene nodes on two scene files; both exits meet on a setvar."""
    fork = add_condition_fact(F + 'stamps_dead')
    b.connect(chain[-1], (fork, 'In'))
    plain = scene_node('gig04_close', 'close_in', 'close_out')
    dead = scene_node('gig04_close_dead', 'close_dead_in', 'close_dead_out')
    b.connect((fork, 'False'), (plain, 'close_in'))
    b.connect((fork, 'True'), (dead, 'close_dead_in'))
    said = add_setvar(F + 'close_said', 1)
    b.connect((plain, 'close_out'), (said, 'In'))
    b.connect((dead, 'close_dead_out'), (said, 'In'))
    chain.append((said, 'Out'))


def miss_close():
    """Her closing call not taken: the same words as a text, the version
    with Stamps if he is dead (gen_journal, MSG_CLOSE and MSG_CLOSE_DEAD).
    Wakako's debrief does the same (`contacts/.../debrief_*`)."""
    fork = add_condition_fact(F + 'stamps_dead')
    b.connect(chain[-1], (fork, 'In'))
    plain = add_journal('gameJournalPhoneMessage', MSG_CLOSE, notify=1)
    dead = add_journal('gameJournalPhoneMessage', MSG_CLOSE_DEAD, notify=1)
    b.connect((fork, 'False'), (plain, 'Active'))
    b.connect((fork, 'True'), (dead, 'Active'))
    sent = add_setvar(F + 'close_texted', 1)
    b.connect((plain, 'Out'), (sent, 'In'))
    b.connect((dead, 'Out'), (sent, 'In'))
    chain.append((sent, 'Out'))
    # HER TEXT BEFORE THE FEE: it arrives 2 s after it is sent (gen_journal),
    # and the fee and the completion follow at once (audit 2026-10-13).
    step(add_delay(3.0))


her_call('close', play_close, miss_close)
# "Wait for Hodan's call" stays up while she rings (audit 2026-10-13).
close_objective('obj_wait')
# JOHNNY ON ORBITAL AIR, once she has hung up (the design call, 2026-10-14;
# gen_scenes, build_johnny_end).
johnny_beat('gig04_johnny_end', 'johnny_end_in', 'johnny_end_out')

# ---- the end --------------------------------------------------------------
step(add_setvar(F + 'pay', 1))
# A SECOND FOR THE FEE: Gig04_Pay.reds polls every half second during her
# call, so the fee's notice comes before the completion notice (audit
# 2026-10-02: it came up to three seconds after).
step(add_delay(1.0))
step(add_addvar(cfg.FIXER_COUNTER, 1))
step(add_journal_quest(QUEST, track=0), in_sock='Succeeded')
step(add_setvar(F + 'done', 1))
# NOT ENDED UNTIL THE MARKET'S PAIR IS SWITCHED OFF. The output node is
# Terminating and kills every wait the phase still has armed (gotcha 68),
# the market's among them; reached first, it left Ligaya and Stamps standing
# for the rest of the save (audit 2026-10-01, second pass). The gig is done
# for the player at `cc_g04_done`; the phase lives on until V is far away
# and the cast is gone (`cc_g04_market_off` comes last on that branch).
step(add_pause_facts([(F + 'market_off', 1, 'Equal'),
                      (F + 'room_off', 1, 'Equal')]))
step(add_output(), in_sock='In', out_sock=None)

# ---- Ligaya missing: switched off and on again -----------------------------
#
# BESIDE THE REST, from her switch-on after the introduction: whenever
# Gig04_Places.reds finds her missing from her stall with V near it
# (`cc_g04_ligaya_missing`, at most five times), her entry is switched off,
# and on again three seconds later. Playtest 2026-10-14: switched on with V
# 2 km away, in Charter Hill, she was still not at the stall. The script
# writes each try and what it finds to the game log (`[CC.Gig04]`).
# BUILT LAST ON PURPOSE: these nodes take the highest ids, so no existing
# node's id moves (gotcha 123).
_fix_wait = add_pause_fact(F + 'ligaya_missing')
b.connect(_ligaya_on, (_fix_wait, 'In'))
_fix_off = add_community('Deactivate', CAST_REF, entry=gen_community.LIGAYA)
b.connect((_fix_wait, 'Out'), (_fix_off, 'In'))
_fix_gap = add_delay(3.0)
b.connect((_fix_off, 'Out'), (_fix_gap, 'In'))
_fix_on = add_community('Activate', CAST_REF, entry=gen_community.LIGAYA)
b.connect((_fix_gap, 'Out'), (_fix_on, 'In'))
_fix_count = add_addvar(F + 'ligaya_retries', 1)
b.connect((_fix_on, 'Out'), (_fix_count, 'In'))
_fix_clear = add_setvar(F + 'ligaya_missing', 0)
b.connect((_fix_count, 'Out'), (_fix_clear, 'In'))
b.connect((_fix_clear, 'Out'), (_fix_wait, 'In'))


if __name__ == '__main__':
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    result = b.build()
    with open(OUT, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(result, fh, indent=2)
    print('wrote %s' % OUT)
    print('nodes: %d, connections: %d, handles used: %d'
          % (len(b.nodes), len(b.conns), b.next_handle))
