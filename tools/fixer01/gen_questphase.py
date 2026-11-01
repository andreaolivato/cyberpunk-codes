r"""Fixer 01: the quest phase. Her introduction, her conversation, and
Johnny after the call.

    python tools\fixer01\gen_questphase.py

THE SHAPE, and it is the shape of `base\open_world\fixers\dyno\phases\
dyno.questphase` (the introduction call, then the contact) with the mod-owned
video call recipe (docs/scene-playbook.md, "The MOD-OWNED recipe") in place
of the game's own holocall phase, which a contact of ours does not have:

  her body       switch her community on, first thing, every load
  her district   beside everything else, for ever: V inside either of the
                 game's two Charter Hill boxes sets `cc_f01_in_district` to
                 1, V outside both sets it back to 0. The game's own fixers
                 wait on their district's box directly (`#city_center_tr`,
                 `#westbrook_tr`); the fact is so the intro script can add
                 its guards on top.
  the call       wait for `cc_f01_fixer_on` (Fixer01_Intro.reds, the first
                 time V is in Charter Hill after the prologue with the phone
                 free; or the dev menu).
                 Switch on her contact so the phone can name the caller, ask
                 for the studio, ring V, and on an answer connect, play her
                 three lines on the studio floor, hang up. On no answer, hang
                 up and ring again a minute later, for as long as it takes:
                 the game's own callers loop the same way.
  after it       her codex entry and her map icon, once and for good (a pin
                 cannot be un-shown), then her card as a text.
  her talk       FROM THE SAME POINT, A LOOP THAT NEVER ENDS, beside the
                 rest of the graph: wait for V within TALK_RADIUS of her body
                 OR for V to ring her from the contact list, whichever comes
                 first. In person, play `fixer01_face` where V stands (the
                 prompt is pinned to her) and go round again when it ends,
                 by goodbye or by V walking off. On the phone, stage the
                 studio, connect the call V started, play `fixer01_call`,
                 hang up, go round again. This is the game's own "default
                 dialogue" phase for a fixer (`dyno.questphase` node 40:
                 a distance wait and a phone wait racing into one scene's two
                 entries), with the mod-owned call in place of the game's
                 holocall phase.

WHO SETS WHICH FACT:

  cc_f01_in_district    THIS GRAPH, 1 while V is inside Charter Hill
  cc_f01_fixer_on       Fixer01_Intro.reds, or the dev menu
  cc_f01_intro_done     THIS GRAPH, once the call has been taken
  cc_f01_fixer_count    her gigs, +1 each as it closes; the dev menu steps
                        it by hand too
  cc_f01_tooltip_shim   the dev menu. Read by Fixer01_Tooltip.reds only
  cc_f01_call_*         THIS GRAPH's own latches for the call (claim, video,
                        rings, step), cleared before they are read
  cc_f01_talk_*         THIS GRAPH's latches for her conversation: claim (the
                        race), mode (1 in person, 2 on the phone, 0 idle),
                        step (where the phone route is), cleared each round

THE CALL, node for node, is gig 01's incoming Nix call (`nix_call` in
tools/gig01/gen_questphase.py) with the audio fallback and the ring-time
gate left out: no script rings for her, so there is nothing to fall back
to, and a call that connects to an empty frame on a cold studio is the known
failure the race below guards against (STUDIO_SECONDS). The pick-up is read
off the fact PhoneSystem writes, not off `questPhonePickUp_ConditionType`,
which does not fire for a call a mod issues (gotcha 58).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from questkit.questgraph import (  # noqa: E402
    b, configure, add_input, add_output, add_pause_fact, add_setvar,
    add_addvar, add_journal, add_community, skip_ids_to,
    add_scene, add_call_contact, add_prefab_variant, add_race2,
    add_pause_node_loaded, add_delay, add_toggle_component,
    add_condition_fact, add_pause_distance, add_pause_phone_call,
    add_pause_triggers, ANCHOR_PLAYER,
)

from questkit import questgraph  # noqa: E402
import fixer01_config as cfg  # noqa: E402

# IDS FOR NODES ADDED AFTER PLAYTEST SAVES EXIST, past every other node (109
# the highest on 2026-11-01), so adding one does not renumber the rest
# (gotcha 123). `late()` hands them out in build order.
LATE_IDS = iter(range(900, 1000))


def late(make, *args):
    saved = questgraph.NID
    questgraph.NID = LATE_IDS
    try:
        return make(*args)
    finally:
        questgraph.NID = saved
import gen_journal  # noqa: E402
import gen_community  # noqa: E402

OUT = os.path.join(cfg.RAW_MOD, 'quest', 'fixer01.questphase.json')

configure(phase_name='fixer01')

# The same string gen_scenes.SCENE_DEPOT builds, and it has to stay so: the
# lipmap is keyed by FNV1a64 of exactly this path plus the scene name.
SCENES = cfg.DEPOT + chr(92) + 'scenes' + chr(92)

FIXER_CONTACT = 'contacts/' + gen_journal.FIXER_CONTACT
FIXER_CONV = FIXER_CONTACT + '/' + gen_journal.FIXER_CONV
MSG_CARD = FIXER_CONV + '/' + gen_journal.MSG_CARD
PLAYER_CONTACT = 'contacts/player'
POI = gen_journal.POI_PATH
CODEX = gen_journal.CODEX_PATH
# Johnny's beat starts at this node id, where it was first built (see the
# end of this file).
JOHNNY_FIRST_ID = 103

# ------------------------------------------------------------- the studio
#
# THE BORROWED SET. An invented caller has no studio setup of her own, and
# a contact's five names are only correct together, so she takes Jefferson
# Peralez's whole: standing, arms crossed, camera at 1.516 (read off the
# studio's quest sector, 2026-09-18), lighting variant read off
# `base\quest\holocalls\jefferson\jefferson_holocall.scene`. The workspot
# and look-at halves are in gen_scenes.STUDIO_POSE.
STUDIO_PREFAB = '#holocalls_studio'
LIGHTS_REF = '#holocalls_studio_lighting'
LIGHTS_VARIANT = 'jefferson_holocall_lights'
SETUP_REF = '#jefferson_holocall_setup'
SETUP_VARIANT = 'jefferson_holocall_setup'
CAMERA_REF = '#jefferson_holocall_camera'

STUDIO_SECONDS = 20     # a cold studio that has not arrived by then is not coming
RING_SECONDS = 12       # a ring nobody answers
RETRY_SECONDS = 60      # before she rings again
DIAL_SECONDS = 2

# The fact PhoneSystem writes as the call changes state, built from the two
# contact ids exactly as `PhoneSystem.GetPhoneCallFactName` builds it:
#   Ended 0    Initializing 1    Talking 2    Rejected 3
PHONE_FACT = ('phonecall_' + gen_journal.FIXER_CONTACT + '_with_player').lower()

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


def call(phase, rejectable=False, outgoing=False):
    """Her calling V, or V calling her (`outgoing`). Caller and addressee are
    journal paths, so our contact works and brings no base-game small talk
    with it. No phone restriction: a restriction applied and never released
    is a phone broken for the rest of the save (gig 01's note)."""
    caller, addressee = ((PLAYER_CONTACT, FIXER_CONTACT) if outgoing else
                         (FIXER_CONTACT, PLAYER_CONTACT))
    return add_call_contact(caller, addressee, phase, video=True,
                            prefab=STUDIO_PREFAB, rejectable=rejectable,
                            restrict=False)


# ---- her body -------------------------------------------------------------
#
# Whole community, no entry named (112 of 133 sampled vanilla uses), long-form
# reference (the only form a name this mod ships resolves under, gotcha 34).
# First thing and on every load: the first build had no such node and nobody
# stood at the spot.
step(add_community('Activate', gen_community.build().community_ref))
placed = chain[-1]

# ---- her district, watched for ever ---------------------------------------
#
# A loop beside the rest of the graph, off the same socket as the call's
# wait: inside any of the district's boxes, write 1; outside all of them,
# write 0; round again. The game's fixer phases wait on the same box shape
# once; this loop keeps the answer current so the intro script (and the dev
# menu) can read it as a fact.
d_in = add_pause_triggers(cfg.DISTRICT_TRIGGERS, inside=True, operation='OR')
b.connect(placed, (d_in, 'In'))
d_set = add_setvar(cfg.IN_DISTRICT_FACT, 1)
b.connect((d_in, 'Out'), (d_set, 'In'))
d_out = add_pause_triggers(cfg.DISTRICT_TRIGGERS, inside=False, operation='AND')
b.connect((d_set, 'Out'), (d_out, 'In'))
d_clear = add_setvar(cfg.IN_DISTRICT_FACT, 0)
b.connect((d_out, 'Out'), (d_clear, 'In'))
b.connect((d_clear, 'Out'), (d_in, 'In'))

# ---- the call -------------------------------------------------------------
step(add_pause_fact(cfg.FACT_PREFIX + 'fixer_on'))

# The contact and its thread, silently, BEFORE the phone rings: the phone
# resolves a caller by walking the journal's contacts, and a mod contact is
# inert until a quest activates it.
open_journal('gameJournalContact', FIXER_CONTACT, notify=0)
open_journal('gameJournalPhoneConversation', FIXER_CONV, notify=0)

P = cfg.FACT_PREFIX + 'call'
for latch in ('_claim', '_video', '_rings', '_step'):
    step(add_setvar(P + latch, 0))

# Ask for the studio pieces. This says which pieces should exist; the call
# node below is what loads the sector (the order warning in the playbook).
step(add_prefab_variant(LIGHTS_REF, LIGHTS_VARIANT, True))
step(add_prefab_variant(SETUP_REF, SETUP_VARIANT, True))

# THE LOOP TARGET. Vanilla's holocall phases are loops whose first pause node
# is fed from more than one place; fan-in on a setvar is ordinary.
ring_top = add_setvar(P + '_claim', 0)
step(ring_top)
# PhoneSystem's own call fact persists at Talking once a call has been
# answered, so it is cleared before every ring.
step(add_setvar(PHONE_FACT, 0))
# THE PHONE STARTS RINGING, and the studio sector starts arriving with it.
step(call('IncomingCall', rejectable=True))

# Wait for the camera node, raced against a clock, then switch it on. On the
# timeout the call still goes out, into an empty frame, which is the known
# cold-studio failure and better than a gig that stops here.
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
# something. Then RE-READ in the same tick, because a declined call reports
# Rejected and then Talking a second and a half later (gotcha 10j).
step(add_setvar(P + '_claim', 0))
answer = add_race2(chain[-1],
                   (add_pause_fact(PHONE_FACT, 1, 'Greater'), 'In', 'Out'),
                   (add_delay(RING_SECONDS), 'In', 'Out'),
                   P + '_claim')
picked = add_condition_fact(PHONE_FACT, 2, 'Equal')
b.connect((answer, 'True'), (picked, 'In'))
b.connect((answer, 'False'), (picked, 'In'))

# NOT ANSWERED: take the chrome down and ring again in a minute. Ending it
# here is what makes a decline behave; vanilla's per-contact phase does the
# same.
missed = call('EndCall')
b.connect((picked, 'False'), (missed, 'In'))
again = add_addvar(P + '_rings', 1)
b.connect((missed, 'Out'), (again, 'In'))
backoff = add_delay(RETRY_SECONDS)
b.connect((again, 'Out'), (backoff, 'In'))
# AND ONLY WHEN SHE MAY RING: `cc_f01_ring_ok`, kept by Fixer01_Intro.reds
# from the first ring until her introduction is done. The first ring has
# its checks in that script; a retry had none and rang through main
# missions (audit 2026-11-01).
ring_ok = late(add_pause_fact, cfg.FACT_PREFIX + 'ring_ok')
b.connect((backoff, 'Out'), (ring_ok, 'In'))
b.connect((ring_ok, 'Out'), (ring_top, 'In'))

# ANSWERED: connect, speak, hang up.
chain.append((picked, 'True'))
step(add_delay(DIAL_SECONDS))
step(call('StartCall'))
step(add_scene(SCENES + 'fixer01_intro.scene', cfg.ANCHOR_STUDIO,
               ['intro_in'], ['intro_out']),
     in_sock='intro_in', out_sock='intro_out')
step(call('EndCall'))
step(add_toggle_component(CAMERA_REF, 'RenderToTextureCamera', False))
step(add_prefab_variant(SETUP_REF, SETUP_VARIANT, False))
step(add_prefab_variant(LIGHTS_REF, LIGHTS_VARIANT, False))
step(add_setvar(cfg.FACT_PREFIX + 'intro_done', 1))
introduced = chain[-1]

# ---- her conversation, for the rest of the save ---------------------------
#
# A SECOND BRANCH OFF THE SAME SOCKET: the chain below carries on to her
# codex entry, icon and card, and this loop runs beside it for ever. The
# game's own fixer phase does the same (`dyno.questphase`: its input fans
# out to the counter, the crowd and the default dialogue phase at once).
#
# Both waits are armed together and raced, the way the game's node 8 (10 m
# of the body) and node 9 (V dialling the contact) are: vanilla cuts the
# loser with a cut-control node, add_race2 is that with the claim fact that
# closes the same-frame case.
T = cfg.FACT_PREFIX + 'talk'
CAST_REF = gen_community.build().community_ref
talk_top = add_setvar(T + '_claim', 0)
b.connect(introduced, (talk_top, 'In'))
idle = add_setvar(T + '_mode', 0)
b.connect((talk_top, 'Out'), (idle, 'In'))
offered = add_race2((idle, 'Out'),
                    (add_pause_distance(CAST_REF, cfg.TALK_RADIUS,
                                        entry=gen_community.ENTRY, cmp='Less'),
                     'In', 'Out'),
                    (add_pause_phone_call(PLAYER_CONTACT, FIXER_CONTACT,
                                          'IncomingCall'),
                     'In', 'Out'),
                    T + '_claim')

# IN PERSON. The scene is staged where V stands and acquires her community
# body; its hub is pinned to her, so nothing shows until V is at arm's
# length. It ends on her goodbye or when V is LEAVE_RADIUS away, and either
# way the loop re-arms a second later, which is the game's own 1 s
# (`dyno.questphase` node 50). Still within reach, the prompt is back.
in_person = add_setvar(T + '_mode', 1)
b.connect((offered, 'True'), (in_person, 'In'))
face = add_scene(SCENES + 'fixer01_face.scene', ANCHOR_PLAYER,
                 ['face_in'], ['face_out', 'face_left'])
b.connect((in_person, 'Out'), (face, 'face_in'))
rearm = add_delay(1)
b.connect((face, 'face_out'), (rearm, 'In'))
b.connect((face, 'face_left'), (rearm, 'In'))
b.connect((rearm, 'Out'), (talk_top, 'In'))

# ON THE PHONE. V has already dialled: the contact list queued the request
# the wait above reported, and the phone is playing its dial tone. What
# follows is the game's own V-calls-a-fixer route (`dino_holocall.scene`,
# entry `holo_v_calls_dino_start`: an IncomingCall node from the player to
# the contact with the studio prefab, the two variants, a wait on the camera
# node, StartCall, the camera on), with the timeout the intro's studio wait
# has. Nothing to answer and nothing to miss: V is the one calling.
on_phone = add_setvar(T + '_mode', 2)
b.connect((offered, 'False'), (on_phone, 'In'))
cur = (on_phone, 'Out')


def go(nid, in_sock='In', out_sock='Out'):
    global cur
    b.connect(cur, (nid, in_sock))
    cur = (nid, out_sock)
    return nid


go(add_setvar(T + '_step', 1))
go(add_prefab_variant(LIGHTS_REF, LIGHTS_VARIANT, True))
go(add_prefab_variant(SETUP_REF, SETUP_VARIANT, True))
go(call('IncomingCall', outgoing=True))
go(add_setvar(T + '_claim', 0))
ready = add_race2(cur,
                  (add_pause_node_loaded(CAMERA_REF), 'In', 'Out'),
                  (add_delay(STUDIO_SECONDS), 'In', 'Out'),
                  T + '_claim')
cam_on = add_toggle_component(CAMERA_REF, 'RenderToTextureCamera', True)
b.connect((ready, 'True'), (cam_on, 'In'))
dialled = add_setvar(T + '_step', 2)
b.connect((cam_on, 'Out'), (dialled, 'In'))
b.connect((ready, 'False'), (dialled, 'In'))
cur = (dialled, 'Out')
go(add_delay(DIAL_SECONDS))
go(call('StartCall', outgoing=True))
go(add_setvar(T + '_step', 3))
go(add_scene(SCENES + 'fixer01_call.scene', cfg.ANCHOR_STUDIO,
             ['call_in'], ['call_out']),
   in_sock='call_in', out_sock='call_out')
go(call('EndCall', outgoing=True))
go(add_toggle_component(CAMERA_REF, 'RenderToTextureCamera', False))
go(add_prefab_variant(SETUP_REF, SETUP_VARIANT, False))
go(add_prefab_variant(LIGHTS_REF, LIGHTS_VARIANT, False))
go(add_setvar(T + '_step', 0))
go(add_delay(1))
b.connect(cur, (talk_top, 'In'))

# ---- after the call -------------------------------------------------------
#
# Her codex entry and her map icon, once. Dino's own phase activates his icon
# with the same journal node after his call.
open_journal('gameJournalCodexEntry', CODEX, notify=0)
open_journal('gameJournalPointOfInterestMappin', POI, notify=0)
# HER CARD, as a text. It carries its own arrival delay (gen_journal); the
# notification is the message's.
open_journal('gameJournalPhoneMessage', MSG_CARD)

# THE STUB JOB IS GONE (the design call, 2026-10-15), BUT ITS FIRST WAIT
# STAYS, as node 92, on a fact nothing sets now. Every save made after her
# introduction is parked on this node (gotcha 123), and a save resumes by
# node id: a different node at 92 would be where those saves wake up. The
# phase's output, which ends the phase, is the last node of the file.
step(add_pause_fact(cfg.FACT_PREFIX + 'probe'))

# ---- Johnny, once her introduction is over ---------------------------------
#
# HIS ONE LINE ABOUT HER (the design call, 2026-10-15; gen_scenes,
# build_johnny), gig 04's shape: V held still (`cc_f01_hold`,
# Fixer01_Hold.reds), a second and a half for the call screen to clear and V
# to stop, the scene, the hold lifted. On a branch of its own off the end of
# the introduction, so nothing waits on it.
# LAST IN THIS FILE ON PURPOSE: saves resume by node id (gotcha 123), and
# nodes added here take the next free ids without moving any existing one.
# PINNED AT 103, where they were built: the stub job's nodes before them
# are gone, and without the skip these four would move down.
skip_ids_to(JOHNNY_FIRST_ID)
HOLD = cfg.FACT_PREFIX + 'hold'
_j_hold = add_setvar(HOLD, 1)
b.connect(introduced, (_j_hold, 'In'))
_j_wait = add_delay(1.5)
b.connect((_j_hold, 'Out'), (_j_wait, 'In'))
_j_scene = add_scene(SCENES + 'fixer01_johnny.scene', ANCHOR_PLAYER,
                     ['johnny_in'], ['johnny_out'])
b.connect((_j_wait, 'Out'), (_j_scene, 'johnny_in'))
_j_free = add_setvar(HOLD, 0)
b.connect((_j_scene, 'johnny_out'), (_j_free, 'In'))

# THE PHASE'S OUTPUT, ON NOTHING. It is `Terminating`: reached, it would end
# the phase and her conversation loop with it. It stays so the phase keeps
# its output socket, and stays last so it never takes an id a save is
# parked on.
add_output()

# ---- her body, switched on again ------------------------------------------
#
# THE GAME'S OWN SHAPE (gotcha 122): a fixer's phase switches his community
# on every time V enters his area, not once. Hers was switched on once, as
# the phase began, and on 2026-10-16 her couch was empty after her
# introduction with her entry at 0 bodies (the dev menu's readout, her
# community resolving and always spawned). Now also each time V enters
# Charter Hill, and as her introduction call ends. Side branches with
# nothing after them; appended after the output, so no id moves.
_again_district = add_community('Activate', gen_community.build().community_ref)
b.connect((d_set, 'Out'), (_again_district, 'In'))
_again_intro = add_community('Activate', gen_community.build().community_ref)
b.connect(introduced, (_again_intro, 'In'))


if __name__ == '__main__':
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    result = b.build()
    with open(OUT, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(result, fh, indent=2)
    print('wrote %s' % OUT)
    print('nodes: %d, connections: %d, handles used: %d'
          % (len(b.nodes), len(b.conns), b.next_handle))
