r"""Acceptable Loss: the quest phase.

    python tools\gig03\gen_questphase.py

The graph the game runs: it activates the journal quest, paces Dino's SMS
thread, walks the objectives, forks on the decision V makes by text, and closes
on one of two endings. The fixer was Regina Jones until 2026-09-15;
gen_journal.py's header has the design call.

THE SHAPE, since 2026-09-11:

  the hire         message, call, brief
  the site         travel, inside, terminal, files, the shard's room
  THE DOOR         opening the security room is the alarm: the trace runs,
                   the site's guards turn on V, three more arrive (a fork off
                   the main line, so it can never hold the story back)
  the shard        taken or read opens "get out"; read closes "read it"
  THE CHASE        "leave the Badlands", with the stars re-raised until the
                   game says V is out, and dropped the moment it does
  the argument     V texts Dino first, once V is on foot; he answers
  THE DECISION     two replies. Bring it, or wipe it
  ending A         Dino at his bar, half the fee, "dick move, V"
  ending B         the shard wiped beside Johnny, Dino at his bar, no fee,
                   the client's advance out of V's wallet, "you're allowed to
                   be a little proud"

The gig spawns three men and nobody else. The compound populates itself, and
the stars bring Militech.

WHO SETS WHICH FACT. A fact with two writers is a fact nobody owns, so the split
is written down here and nowhere else:

  cc_g03_start          the start trigger, once the gate below passes
  cc_g03_called         THIS GRAPH, once the reply has been tapped. Nothing
                        waits on it; it is there so the dev menu and a save can
                        both say how far the thread has got
  cc_g03_arrived        redscript, when the player reaches the Badlands site
  cc_g03_inside         redscript, when the player crosses the perimeter
  cc_g03_terminal       redscript, at the terminal
  cc_g03_data           redscript, when the terminal's files have been read
  cc_g03_alarm          Gig03_Alarm.reds, the security-room door opening
                        (or the cabinet, or the shard, as fallbacks)
  cc_g03_shard_got      Gig03_Shard.reds, the shard taken OR read
  cc_g03_shard_read     Gig03_Shard.reds, the reader opened and shut
  cc_g03_traced         Gig03_Trace.reds, when the bar finishes: V is FOUND.
                        The reinforcements and the guard pass wait on it
  cc_g03_heat_raised    Gig03_Trace.reds, its own one-per-save latch
  cc_g03_escaped        redscript, when the player leaves the compound
  cc_g03_badlands_left  redscript, when the game says V is out of the Badlands
  cc_g03_heat_cleared   Gig03_Trace.reds, its latch on dropping the stars
  cc_g03_mounted        redscript, with badlands_left: 1 in a vehicle, 2 on foot
  cc_g03_on_foot        redscript, once V is out of a vehicle with no stars
  cc_g03_choice_claim   THIS GRAPH, the decision race's claim (add_race2)
  cc_g03_loyal          THIS GRAPH, 1 on the ending where the shard is wiped
  cc_g03_shard_destroyed  Gig03_Places.reds, the shard removed, once
  cc_g03_pay_due        THIS GRAPH, as Dino's calm scene ends (the fee)
  cc_g03_docked         THIS GRAPH, as Dino's loud scene ends (the advance)
  cc_g03_dock_paid      Gig03_Places.reds, the advance taken, once
  cc_g03_unlock_dino    THIS GRAPH, when the trip to him opens
  cc_g03_at_bar         redscript, within the swap radius of his stool
  cc_g03_swapped        THIS GRAPH, once the game's own Dino is switched off
                        and ours on. Gig03_Places.reds's keeper waits on it
  dyno_default_on       THE GAME'S OWN, the gate of Dino's fixer phase. Held
                        at 0 by this graph from the swap until V has left
                        the bar, then set back to 1 (see VANILLA_DINO)
  cc_g03_delivered      redscript, at Dino
  cc_g03_left_dino      redscript, once the player is away from the bar,
                        on foot. Gig03_Places.reds holds V still on it
  cc_g03_johnny_done    THIS GRAPH, as Johnny's door scene ends. Lifts the
                        hold
  cc_g03_done           THIS GRAPH, at the end

THE TRIP. `cc_g03_unlock_dino` is set when the final objective opens and it
is what lets Gig03_Places.reds watch for V arriving. It is set here rather
than in redscript so that nothing about the bar can happen at any other point
in the gig: the graph reaches this node once, on the way to him, and never
before. (For Regina the same fact also unlocked her street door; no door is
known at Dino's bar, so nothing acts on it beyond the watch.)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from questkit.questgraph import (  # noqa: E402
    b, configure, add_input, add_output, add_pause_fact, add_pause_journal,
    add_setvar, add_journal, add_journal_quest, add_scene,
    add_call_contact, add_prefab_variant, add_race2, add_pause_node_loaded,
    add_delay, add_toggle_component, add_community, add_condition_fact,
    add_spawnset,
)
from questkit.scene import ANCHOR_PLAYER  # noqa: E402

import gig03_config as cfg  # noqa: E402

QUEST_ID = cfg.QUEST_ID
RAW_MOD = cfg.RAW_MOD
ANCHOR_STUDIO = cfg.ANCHOR_STUDIO

OUT = os.path.join(RAW_MOD, 'quest', 'gig03.questphase.json')

QUEST = 'quests/street_stories/' + QUEST_ID
PHASE = QUEST + '/phase_main'
BRIEF = QUEST + '/cc_g03_briefing'

configure(phase_name='gig03')

# The same string gen_scenes.SCENE_DEPOT builds, and it has to stay so: the
# lipmap is keyed by FNV1a64 of exactly this path plus the scene name.
SCENES = cfg.DEPOT + chr(92) + 'scenes' + chr(92)


# ------------------------------------------------------------- the holocall
#
# DINO HAS HIS OWN SPOT IN THE STUDIO. Read out of the shipped sector
# `quest_ec82d0423d8f1435.streamingsector` on 2026-09-15, which carries one
# setup per contact: `#dino_holocall_setup` holding `#dino_holocall_camera`,
# `#dino_holocall_workspot` and `#dino_holocall_lookat`. Spelled `dino_`
# there, while his community and character are `dyno`.
#
# THE SETUP VARIANT NAME IS THE SETUP NODE'S NAME WITHOUT THE HASH, and that is
# evidence rather than a pattern: gig 02's known-good variant string is
# `wakako_holocall_setup` and the node in the sector is `#wakako_holocall_setup`.
# Dino's node is `#dino_holocall_setup`, so his is `dino_holocall_setup`.
#
# THE LIGHTING VARIANT IS READ OFF HIS OWN HOLOCALL SCENE, NOT INFERRED.
# `base\quest\holocalls\dino\dino_holocall.scene` toggles
# `dino_dinovic_holocall_lights`, and the pattern the other fixers follow
# (`regina_holocall_lights`, `wakako_holocall_lights`) does not hold for him.
# The first build inferred `dino_holocall_lights` and played the call as a
# silhouette: playtest 2026-09-15, "he appears but he's like a shadow". A
# wrong lighting name is a silent no-op, so the name comes from the scene
# that uses it, the way gig 02 read Wakako's (backlog 33).
# THE GAME'S OWN DINO, read off the community registry in always_loaded_1 on
# 2026-09-15: spawn set `#dyno`, entry `dyno`, phase `default`, on
# `#ws_dyno_default`. The same shape as gig 02's `('#wakako', 'wakako',
# 'default')` and Regina's `('#reggie', 'reggie', 'default')`.
#
# HE IS SWITCHED OFF ONLY FOR THE HANDOVER, and switched back on when the gig
# ends. A base-game fixer missing from his own bar for the rest of a save is a
# worse bug than anything this gig fixes by removing him.
#
# HIS OWN PHASE SWITCHES HIM TOO, AND IT IS A LOOP. Read off
# `base/open_world/fixers/dyno/phases/dyno.questphase` on 2026-09-20, after
# the Nexus report of two Dinos at the bar: every time V steps inside his
# load trigger (`#dyno_dd_tr_load`) the game ACTIVATES entry `dyno`, and
# every time V steps out it deactivates it. A single Deactivate from this
# graph held only until the next crossing, which is why the double came and
# went with the route taken into the bar. The loop's own gate is the fact
# below: the activate node waits on `dyno_default_on > 0`, and the fact has
# no other writer in the 3,496 quest files of the base game and Phantom
# Liberty (his phase sets it to 1, once, and `character_entries.questphase`
# only reads it). So the graph holds it at 0 for the length of the handover
# and hands it back at 1, which is what lets his phase carry on as before.
#
# AND HE IS SWITCHED BY NAME, NOT BY NODE. His community is a compiled area
# node in `always_loaded_1` with no NodeRef of its own, so the
# community-template node this graph uses for its own cast has nothing to
# resolve for him. His phase uses `questSpawnSet_NodeType` against the
# registered name `#dyno`; `add_spawnset` is that node. Gotcha 122.
import gen_community                                         # noqa: E402

VANILLA_DINO = ('#dyno', 'dyno', 'default')
VANILLA_DINO_GATE = 'dyno_default_on'

# OUR OWN DINO, the community entry gen_community.py places on his stool.
# Long form, because a community reference is resolved as a real world
# NodeRef (gotcha 34).
CAST_REF = ('$/mod/' + gen_community.SECTOR + '/#'
            + gen_community.SECTOR + '_com')
# THE REINFORCEMENTS, the three Militech gen_community.py places at the
# compound's corners. Whole-community switches, no entry named.
MILITECH_REF = ('$/mod/' + gen_community.MILITECH_SECTOR + '/#'
                + gen_community.MILITECH_SECTOR + '_com')

PLAYER_CONTACT = 'contacts/player'
STUDIO_PREFAB = '#holocalls_studio'
LIGHTS_REF = '#holocalls_studio_lighting'
DINO_STUDIO = ('dino_dinovic_holocall_lights', '#dino_holocall_setup',
               'dino_holocall_setup', '#dino_holocall_camera')

STUDIO_SECONDS = 20
DIAL_SECONDS = 3


def dino_call(prefix, scene_name, entry, exit_):
    """One outgoing video call: dial, wait for the studio, speak, hang up.

    THE DIAL COMES BEFORE THE WAIT and that ordering is the whole thing.
    WHAT LOADS THE STUDIO IS THE CALL NODE: the studio is a Quest sector with
    no streaming box, and `questCallContact_NodeType` carrying
    `prefabNodeRef: #holocalls_studio` is the only thing that asks for it.
    Toggling the variants first only says which pieces should exist ONCE the
    sector is there; on a cold studio it does nothing, the wait for the camera
    then cannot succeed, and the call talks to an empty frame.

    Gig 02 measured that in 2026-09-07 and this is its recipe unchanged.
    """
    global chain
    lights_variant, setup_ref, setup_variant, camera_ref = DINO_STUDIO
    step(add_setvar(prefix + '_claim', 0))
    step(add_setvar(prefix + '_video', 0))
    step(add_prefab_variant(LIGHTS_REF, lights_variant, True))
    step(add_prefab_variant(setup_ref, setup_variant, True))

    # PhoneSystem's own call fact persists at Talking once a call has been
    # answered, so it is cleared before the call.
    phone_fact = ('phonecall_' + PLAYER_CONTACT.split('/')[-1] + '_with_'
                  + DINO_CONTACT.split('/')[-1]).lower()
    step(add_setvar(phone_fact, 0))

    def call(phase):
        return add_call_contact(PLAYER_CONTACT, DINO_CONTACT, phase,
                                video=True, prefab=STUDIO_PREFAB,
                                restrict=False)

    # THE PHONE STARTS DIALLING, and the sector starts arriving with it.
    step(call('IncomingCall'))

    studio = add_race2(chain[-1],
                       (add_pause_node_loaded(camera_ref), 'In', 'Out'),
                       (add_delay(STUDIO_SECONDS), 'In', 'Out'),
                       prefix + '_claim')
    got = add_toggle_component(camera_ref, 'RenderToTextureCamera', True)
    b.connect((studio, 'True'), (got, 'In'))
    lit = add_setvar(prefix + '_video', 1)
    b.connect((got, 'Out'), (lit, 'In'))
    join = add_setvar(prefix + '_step', 1)
    b.connect((lit, 'Out'), (join, 'In'))
    b.connect((studio, 'False'), (join, 'In'))
    chain.append((join, 'Out'))

    step(add_delay(DIAL_SECONDS))
    step(call('StartCall'))
    # NO EXTRA BEAT HERE: gig 02's pacing, node for node. A 1.5 s delay stood
    # here for one build, added for a first line with a still face, and the
    # face was a lipsync casing bug (gotcha 114). What the delay did was make
    # the connect, the picture and the first word arrive as three separate
    # events: playtest 2026-09-11, "too much delay ... feels like a glitch".
    scene_at(scene_name, ANCHOR_STUDIO, entry, exit_)
    step(call('EndCall'))
    step(add_toggle_component(camera_ref, 'RenderToTextureCamera', False))
    step(add_prefab_variant(setup_ref, setup_variant, False))
    step(add_prefab_variant(LIGHTS_REF, lights_variant, False))
    step(add_setvar(prefix + '_done', 1))


def scene_at(name, anchor, entry, exit_):
    step(add_scene(SCENES + name + '.scene', anchor, [entry], [exit_]),
         in_sock=entry, out_sock=exit_)


def scene(name, entry, exit_):
    """Play one of our scenes at the player.

    Every scene in this gig is staged AT THE PLAYER rather than at a place: two
    of them are Johnny, who is in V's head, one is a phone call, and the fourth
    is a conversation the player has walked into. None of them needs a marker in
    the world.
    """
    step(add_scene(SCENES + name + '.scene', ANCHOR_PLAYER, [entry], [exit_]),
         in_sock=entry, out_sock=exit_)

# --------------------------------------------------------------- the contact
#
# Journal paths, not CNames: a phone node resolves a contact by path, so a
# mod-owned contact brings none of the real Dino's conversation with it.
DINO_CONTACT = 'contacts/cc_g03_dino'
DINO_CONV = DINO_CONTACT + '/cc_g03_dino_conv'
MSG_01 = DINO_CONV + '/cc_g03_msg_01'
CHOICE_GROUP = DINO_CONV + '/cc_g03_ch_01'
CHOICE_CALL = CHOICE_GROUP + '/cc_g03_ch_01a'
MSG_02 = DINO_CONV + '/cc_g03_msg_02'
CHOICE_GROUP_2 = DINO_CONV + '/cc_g03_ch_02'
CHOICE_RIGGED = CHOICE_GROUP_2 + '/cc_g03_ch_02a'
CHOICE_GROUP_3 = DINO_CONV + '/cc_g03_ch_03'
CHOICE_TARGETS = CHOICE_GROUP_3 + '/cc_g03_ch_03a'
MSG_05 = DINO_CONV + '/cc_g03_msg_05'
CHOICE_GROUP_4 = DINO_CONV + '/cc_g03_ch_04'
CHOICE_COMING = CHOICE_GROUP_4 + '/cc_g03_ch_04a'
CHOICE_WIPE = CHOICE_GROUP_4 + '/cc_g03_ch_04b'
MSG_06 = DINO_CONV + '/cc_g03_msg_06'


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


# A PIN MUST BE ACTIVATED ALONGSIDE ITS OBJECTIVE OR IT NEVER APPEARS. Activating
# the objective is not enough, and an inactive pin is invisible, which then makes
# every layer below it look broken. This is the most commonly missed step in
# docs/map-pins-playbook.md.
PINS = {
    'obj_travel': 'pin_travel',
    'obj_terminal': 'pin_terminal',
    'obj_shard': 'pin_shard',
    'obj_dino': 'pin_dino',
    # AND THE WAY OUT, which draws the bar on the minimap. (Regina's leave
    # pin was added with its objective on 2026-09-10 and missed here on the
    # first pass, which is the exact failure the note above describes: the
    # pin existed in the journal and the phase never switched it on.)
    'obj_leave': 'pin_leave',
    # The loyal ending's trip to him, on its own objective. Same rule.
    'obj_face': 'pin_face',
}


def open_objective(oid):
    open_journal('gameJournalQuestObjective', PHASE + '/' + oid)
    if PINS.get(oid):
        open_journal('gameJournalQuestMapPin',
                     PHASE + '/' + oid + '/' + PINS[oid], notify=0)


def close_objective(oid):
    close_journal('gameJournalQuestObjective', PHASE + '/' + oid)


def objective_step(gate_fact, done_obj, next_obj=None):
    """Wait for a fact, close one objective, open the next."""
    step(add_pause_fact(gate_fact))
    close_objective(done_obj)
    if next_obj:
        open_objective(next_obj)


# THE START. Everything before this node has already happened: the trigger has
# checked that Dino is a contact and has set the fact. See Gig03_Start.reds.
# HE IS NOT AT HIS BAR YET. A mod community spawns its entries on save load
# whatever `entryActiveOnStart` says (gotcha 69), so without this our Dino
# would be sitting on top of the real one from the moment the save loads, in
# every save, whether the gig has started or not.
step(add_community('Deactivate', CAST_REF, entry='dino'))
# AND THE REINFORCEMENTS ARE NOT AT THE COMPOUND YET, for the same reason.
step(add_community('Deactivate', MILITECH_REF))

step(add_pause_fact('cc_g03_start'))

# THE CONTACT AND THE CONVERSATION HAVE TO BE SWITCHED ON FIRST, and this is
# what an earlier build got wrong: it activated the message and nothing else, so
# the thread had no contact to arrive under and the phone showed only the base
# game's fixer. A mod contact is inert until the quest activates it.
#
# Both are SILENT. The notification belongs to the message, not to the contact
# appearing.
open_journal('gameJournalContact', DINO_CONTACT, notify=0)
open_journal('gameJournalPhoneConversation', DINO_CONV, notify=0)

# HIS FIRST MESSAGE. It carries its own arrival delay, set in the journal
# resource, because a graph timer stalls while a menu is open and the phone is a
# menu (gotchas 3).
#
# IT LANDS ALONE. The quest goes into the log after the reply, not here: two
# notifications on one frame ate the message preview in gig 02 once, and this is
# that gig's own ordering.
open_journal('gameJournalPhoneMessage', MSG_01)

# THE GROUP, not the entry. Activating a choice entry without its group leaves
# the reply with nothing to render in.
open_journal('gameJournalPhoneChoiceGroup', CHOICE_GROUP, notify=0)

# WAITING ON THE REPLY ITSELF, not on a fact.
#
# A phone choice entry goes Succeeded when the player taps it, and a journal
# pause node reads that directly. There is no fact behind it and nothing has to
# set one: an earlier draft waited on `cc_g03_called`, which nothing in the game
# ever wrote, so the gig stopped dead at the first message.
step(add_pause_journal('gameJournalPhoneChoiceEntry', CHOICE_CALL))
step(add_setvar('cc_g03_called', 1))

# THE CALL. He says he has a job, that V is to steal a thing, and that the
# details are attached. Every line is his own recording.
#
# A REAL VIDEO CALL, not a scene played at the player. The first build used
# `scene(...)` here: the voice played and there was no call on screen, because
# a scene alone neither opens the phone nor loads the studio the body stands in.
dino_call('cc_g03_call1', 'gig03_dino_call', 'dino_call_in', 'dino_call_out')

# THE GIG GOES INTO THE LOG FIRST, then his message arrives with the gig card
# on it. The card is an attachment naming the quest, and it has something to
# show only once that quest is Active: opened the other way round, the
# message arrived carrying a card for a quest the journal did not have yet.
# Playtest 2026-09-11: "I cannot see the gig card in the SMS". The game's own
# fixers do it in this order, gig active, then the brief with the card.
step(add_journal_quest(QUEST, track=1), in_sock='Active')
open_journal('gameJournalQuestDescription', BRIEF)

# His attachment, off the phone, which is where the job is actually stated.
open_journal('gameJournalPhoneMessage', MSG_02)

# The job proper.
open_objective('obj_travel')

objective_step('cc_g03_arrived', 'obj_travel', 'obj_enter')
objective_step('cc_g03_inside', 'obj_enter', 'obj_terminal')
objective_step('cc_g03_terminal', 'obj_terminal', 'obj_data')

# THE TERMINAL SAYS WHERE THE REAL THING IS. `cc_g03_data` is the player having
# read what is on it: the log Dino wants is not on the network, it is on a
# shard in the security room.
objective_step('cc_g03_data', 'obj_data', 'obj_shard')

# THE DOOR, THE BAR, AND THE TRACE THAT ALWAYS WINS.
#
# `cc_g03_alarm` is set by Gig03_Alarm.reds when the security-room door opens
# (with the cabinet and the shard itself as fallbacks behind it), and it only
# starts the bar. `cc_g03_traced` is set by Gig03_Trace.reds six seconds
# later, when the bar finishes: that is the moment V is found, and the stars,
# the guard pass and the reinforcements below all wait for it. The netrunner
# finds V every time, whatever the player's level, gear or build, because it
# is a story beat and not a skill check.
#
# A FORK, NOT A STEP (gotcha 104). Switching the reinforcements on is
# bookkeeping for the world. The story continues on the shard, below, and
# must not wait here.
AT_SHARD = chain[-1]
FOUND = add_pause_fact('cc_g03_traced')
b.connect(AT_SHARD, (FOUND, 'In'))
REINFORCE = add_community('Activate', MILITECH_REF)
b.connect((FOUND, 'Out'), (REINFORCE, 'In'))
# The branch ends here, with nothing connected to REINFORCE's Out.

# THE SHARD. `cc_g03_shard_got` is set by Gig03_Shard.reds when the shard is
# TAKEN OR READ, whichever happens first, and it is what opens "get out".
step(add_pause_fact('cc_g03_shard_got'))
close_objective('obj_shard')

# BOTH OPEN AT ONCE, and the order they close in is the player's.
#
# Reading it is a separate objective from taking it, because the object offers
# both and a player can walk away holding something unread. It carries no pin:
# the shard may be in the backpack by now and a marker on an empty cabinet
# points at nothing.
#
# The two waits below are sequential in the graph and that is not a constraint
# on the player: a pause node whose fact is ALREADY set completes at once, so
# reading the shard while running still works, and so does reading it after.
open_objective('obj_read')
open_objective('obj_escape')

# READING CLOSES FIRST, AND THE ORDER IS THE WHOLE FIX.
#
# These two waits are sequential in the graph, so whichever is written first is
# the one that can close early. It used to be the escape, which meant a player
# who read the shard standing at the cabinet watched "Read the mission log" stay
# on screen until they were clear of the compound. Playtest, 2026-09-10: "I've
# read the shard but the objective is still up."
#
# Reading first is right round: a pause node whose fact is ALREADY set completes
# at once, so a player who escapes before reading loses nothing, and one who
# reads at the cabinet sees it tick there.
objective_step('cc_g03_shard_read', 'obj_read')

# THE CHASE. Clear of the compound is not clear of Militech: the objective is
# to leave the Badlands, and Gig03_Trace.reds keeps the three stars coming back
# until Gig03_Places.reds reads, off the game's own district tracking, that V
# is out. On that fact the stars drop, and the reinforcements are switched
# off so a reload cannot bring their dead back (community state persists).
objective_step('cc_g03_escaped', 'obj_escape', 'obj_badlands')
objective_step('cc_g03_badlands_left', 'obj_badlands')
step(add_community('Deactivate', MILITECH_REF))

# V TEXTS ONCE OUT OF THE CAR. Gig03_Places.reds sets `cc_g03_on_foot` once
# V is out of a vehicle with the stars gone, and caps the stars half at ten
# minutes so it cannot stall the gig. (Until 2026-09-15 this wait was for a
# Johnny scene staged beside V; the argument is the thread now, and the wait
# stays because V does not text while driving away from Militech.)
#
# AND SAYS SO, IF V IS DRIVING. Playtest 2026-09-11: "after I escape the
# Badlands I have no indication to leave the vehicle". `cc_g03_mounted` is
# written by Gig03_Places.reds on the frame before `badlands_left`, so the
# condition below reads a value that is already there: 1 puts "Get out of the
# vehicle" on screen until V does, 2 waits without an objective. A condition
# node, not a pause: it reads once and moves on (gotcha 55).
MOUNTED = add_condition_fact('cc_g03_mounted', 1, 'Equal')
b.connect(chain[-1], (MOUNTED, 'In'))
chain = [(MOUNTED, 'True')]
open_objective('obj_dismount')
step(add_pause_fact('cc_g03_on_foot'))
close_objective('obj_dismount')
DISMOUNTED = chain[-1]
chain = [(MOUNTED, 'False')]
step(add_pause_fact('cc_g03_on_foot'))
WALKED = chain[-1]
ON_FOOT = add_setvar('cc_g03_ride_ready', 1)
b.connect(DISMOUNTED, (ON_FOOT, 'In'))
b.connect(WALKED, (ON_FOOT, 'In'))
chain = [(ON_FOOT, 'Out')]

# THE ARGUMENT, BY TEXT, AND V STARTS IT BY HAND. The objective says to
# message him; V's two texts are reply buttons the player taps in turn (two
# reply groups back to back, the shape 94 of the game's threads use); then his
# answer, with the notification; then the two replies. Playtest 2026-09-15,
# on a build where V's texts sent themselves: "the gig continues without
# prompt. Not good." This is where the plot no recording can carry gets said.
open_objective('obj_brief')
open_journal('gameJournalPhoneChoiceGroup', CHOICE_GROUP_2, notify=0)
step(add_pause_journal('gameJournalPhoneChoiceEntry', CHOICE_RIGGED))
open_journal('gameJournalPhoneChoiceGroup', CHOICE_GROUP_3, notify=0)
step(add_pause_journal('gameJournalPhoneChoiceEntry', CHOICE_TARGETS))
open_journal('gameJournalPhoneMessage', MSG_05)
open_journal('gameJournalPhoneChoiceGroup', CHOICE_GROUP_4, notify=0)

# THE DECISION: two replies in one group, two waits, one winner. Vanilla waits
# on each entry with no cut between them (mq030's Zane thread, read
# 2026-09-11), because tapping one reply closes the group and the other can
# never go Succeeded. `add_race2` adds the cut and the claim anyway, which
# costs nothing and closes the same-frame window (gotcha 55). True is "bring
# it", False is "wipe it". The messaging objective closes on either.
step(add_setvar('cc_g03_choice_claim', 0))
DECISION = add_race2(chain[-1],
                     (add_pause_journal('gameJournalPhoneChoiceEntry',
                                        CHOICE_COMING), 'In', 'Out'),
                     (add_pause_journal('gameJournalPhoneChoiceEntry',
                                        CHOICE_WIPE), 'In', 'Out'),
                     'cc_g03_choice_claim')


def trip_to_dino(obj, bar_scene, bar_in, bar_out, door_scene, door_in,
                 door_out, before_leave=None):
    """The trip to his bar and away again, shared by both endings: the
    objective, the body swap on the way in, the scene, the walk away, the
    swap back, and Johnny at V's own door.

    `before_leave` is a hook for what happens as his scene ends.
    """
    # THE OBJECTIVE, AND THE WATCH. The unlock fact is set in the same breath
    # as the objective that sends V to him, so Gig03_Places.reds cannot act on
    # the bar at any earlier point in the gig.
    open_objective(obj)
    step(add_setvar('cc_g03_unlock_dino', 1))

    # THE SWAP HAPPENS ON THE WAY IN, AND IT HAS TO COME BEFORE THE ARRIVAL
    # WAIT. `cc_g03_at_bar` is set when the player comes within the swap
    # radius of his stool (gig03_config.DINO_SWAP_RADIUS), so the game's own
    # Dino is out and ours is in before the stool is in view.
    #
    # THE ORDER OF THESE TWO WAITS IS THE WHOLE BUG. Until 2026-09-11 the
    # arrival wait stood first, so the graph sat on it until the player was AT
    # THE FIXER, and only then read the approach fact, which had been set
    # minutes earlier, and only then swapped the bodies: in front of the
    # player, every time. Playtest, on Regina: "for a very quick second I see
    # the old one".
    step(add_pause_fact('cc_g03_at_bar'))
    # HIS OWN PHASE IS HELD FIRST, so that nothing it does can undo the two
    # nodes after it: with the gate at 0, V crossing his load trigger no
    # longer activates him (see VANILLA_DINO above). Then his entry is
    # switched off by name, with the node his own phase uses, and ours on.
    step(add_setvar(VANILLA_DINO_GATE, 0))
    step(add_spawnset('Deactivate', VANILLA_DINO[0], VANILLA_DINO[1],
                      VANILLA_DINO[2]))
    step(add_community('Activate', CAST_REF, entry='dino'))
    # THE KEEPER WAITS ON THIS, NOT ON THE APPROACH FACT. Gig03_Places.reds
    # used to start disposing his body on the tick that set `cc_g03_at_bar`,
    # before this graph had switched anything, and a community whose entry
    # is still on puts a disposed body straight back under the same id.
    step(add_setvar('cc_g03_swapped', 1))

    # NOW WAIT FOR THEM TO REACH HIM.
    step(add_pause_fact('cc_g03_delivered'))

    # DINO, IN PERSON. The reason he is angry arrived in V's message; the
    # scene carries the anger.
    scene(bar_scene, bar_in, bar_out)
    if before_leave:
        before_leave()

    close_objective(obj)

    # AND NOW TELL THEM TO GO. Playtest 2026-09-10, on Regina's flat: "there's
    # no indication that I need to leave the apartment as objective of the
    # gig." Everything below waits on the player being away from the bar, so
    # without this the gig looks finished and stalls.
    open_objective('obj_leave')

    # NOTHING ELSE HAPPENS IN FRONT OF HIM. Our body going, his coming back,
    # and Johnny talking over the top of both all wait until they have left.
    step(add_pause_fact('cc_g03_left_dino'))

    close_objective('obj_leave')

    # HE GOES BACK, now that nobody is watching the swap: ours off, his
    # phase's gate handed back at 1 (from here on it activates him when V
    # is inside his load trigger and deactivates him outside it, as it
    # always did), and his entry switched on by name so the stool is not
    # left empty on the way out when V is already inside that trigger.
    step(add_community('Deactivate', CAST_REF, entry='dino'))
    step(add_setvar(VANILLA_DINO_GATE, 1))
    step(add_spawnset('Activate', VANILLA_DINO[0], VANILLA_DINO[1],
                      VANILLA_DINO[2]))

    # THE LAST LINE, outside V's own door, with "Listen to Johnny" on screen
    # for the length of it (its own journal entry: the one from the decision
    # has succeeded by now and would not reopen).
    #
    # V IS HELD STILL FIRST. Gig03_Places.reds applies the hold on the same
    # tick it sets `cc_g03_left_dino`, and the second here is for V to come
    # to a stop before Johnny is placed beside V (a body placed beside a
    # running V is behind V by the time he speaks). The design call,
    # 2026-09-15: stop, then Johnny, then release, "so we're sure he appears
    # and V sees him". `cc_g03_johnny_done` is what releases the hold.
    step(add_delay(1.0))
    open_objective('obj_johnny_2')
    scene(door_scene, door_in, door_out)
    close_objective('obj_johnny_2')
    step(add_setvar('cc_g03_johnny_done', 1))


# ---------------------------------------------------------------- ENDING A
#
# V brings it. Half the fee, paid by Gig03_Places.reds as his scene ends, and
# Dino furious in his own words.
chain = [(DECISION, 'True')]
close_objective('obj_brief')
# JOHNNY OBJECTS, one line, and V does not listen. "Listen to Johnny" is on
# screen for the length of it, the way the game marks his beats.
open_objective('obj_johnny')
scene('gig03_object', 'object_in', 'object_out')
close_objective('obj_johnny')


def pay():
    # THE FEE, on his last line. Gig03_Places.reds pays it and the game draws
    # the transfer; this only says when. It stood at the stool until
    # 2026-09-15, so the 12,500 landed as he opened his mouth.
    step(add_setvar('cc_g03_pay_due', 1))


trip_to_dino('obj_dino', 'gig03_dino_bar', 'dino_bar_in', 'dino_bar_out',
             'gig03_door', 'door_in', 'door_out', before_leave=pay)
ENDING_A = chain[-1]

# ---------------------------------------------------------------- ENDING B
#
# V wipes it. `cc_g03_loyal` is what everything else keys on: the shard leaves
# the backpack three seconds into Johnny's scene (Gig03_Places.reds), the fee
# is never paid, and the client's advance comes out of V's wallet as his loud
# scene ends. His message lands after Johnny, so the player reads it knowing
# what they did.
chain = [(DECISION, 'False')]
close_objective('obj_brief')
step(add_setvar('cc_g03_loyal', 1))
open_objective('obj_johnny')
scene('gig03_destroy', 'destroy_in', 'destroy_out')
close_objective('obj_johnny')
open_journal('gameJournalPhoneMessage', MSG_06)


def dock():
    # THE ADVANCE, on his last line. Gig03_Places.reds takes it and puts the
    # banner up; this only says when.
    step(add_setvar('cc_g03_docked', 1))


trip_to_dino('obj_face', 'gig03_dino_bar_loud', 'dino_loud_in',
             'dino_loud_out', 'gig03_door_loyal', 'door_loyal_in',
             'door_loyal_out', before_leave=dock)
ENDING_B = chain[-1]

# ------------------------------------------------------------------ THE END
#
# Both endings meet on one node. Fan-in on a setvar is ordinary (gig 02 joins
# its branches the same way); fan-in on a SCENE node is what gotcha 51 warns
# about, and neither ending's scenes are shared.
JOIN = add_setvar('cc_g03_ended', 1)
b.connect(ENDING_A, (JOIN, 'In'))
b.connect(ENDING_B, (JOIN, 'In'))
chain = [(JOIN, 'Out')]

# THE QUEST IS MARKED FINISHED, and this was missing until 2026-09-10.
#
# Closing every objective does NOT close the quest. Playtest: "the gig doesn't
# end after the fixer's dialogue and Johnny's last remark." It did not, because
# nothing had ever put the quest itself into Succeeded, so it sat in the log as
# an active street story with no objectives left in it.
#
# `track=0` stops it tracking at the same time, so the finished gig does not
# stay pinned to the player's HUD.
step(add_journal_quest(QUEST, track=0), in_sock='Succeeded')

step(add_setvar('cc_g03_done', 1))
step(add_output(), in_sock='In', out_sock=None)


if __name__ == '__main__':
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    result = b.build()
    with open(OUT, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(result, fh, indent=2)
    print('wrote %s' % OUT)
    print('nodes: %d, connections: %d, handles used: %d'
          % (len(b.nodes), len(b.conns), b.next_handle))
