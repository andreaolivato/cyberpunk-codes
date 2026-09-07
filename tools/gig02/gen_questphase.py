r"""Generates gig02.questphase.json, the quest graph driving Dead Ringer.

The builder is tools/questkit/questgraph.py, which emits the CR2W chunk format
and cross-links sockets by HandleId. This file is the GIG: its journal paths,
its scene anchors and its flow. Do not hand-edit the JSON it produces.

===========================================================================
WHO SETS WHAT
===========================================================================

A fact with two writers is a fact nobody owns, so the split is written down
here and nowhere else contradicts it.

THE GRAPH SETS the facts that mean "the story has reached this point":
started, called, accepted, talk_a_done, groups_done, lead_heard, merc_armed,
merc_talked, merc_flee, reported, wakako_2, to_char, trace_done, extract_armed,
crack_armed, wakako_met, hit_armed, exfil_armed, closed, done.

THE SCRIPT SETS the facts that mean "the player has done something":
start, afterlife_reached, group_first, group_second, group3_near, merc_down,
proof_read, inn_reached, char_near, parlor_reached, relay_found, relay_taken,
relay_cracked, office_reached, hit_reached, dropped, toji_met, toji_dead,
exfil_done, spotted.

TWO FACTS ARE SET BY THE BEGGING SCENE: `merc_talked` (the shard lands) and
`merc_fate` (1 kill, 2 spare), because an exit point cannot say which branch
of a conversation reached it.

===========================================================================
THE REBUILD OF 2026-09-03
===========================================================================

Every character the base game voices now speaks in its own recordings
(gen_scenes.py, module docstring), and that moved three beats OFF the phone
and INTO text, which is where the base game keeps a gig's plot anyway:

  the report after the merc     a reply the player picks in Wakako's thread,
                                and her answer by message. Was a video call.
  Char's verdict                a message from Char half an hour after the
                                handover. Was a scene at her chair, with a
                                second walk back to it.
  the camera log                folded into the relay's own note. The
                                attendant and her scene are gone.

Every wait is bounded except the ones the player controls. Both of Wakako's
remaining calls are OUTGOING, so there is no ring to miss.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from questkit.questgraph import (                                   # noqa: F401
    b, configure, cname, jpath, Builder, STD, JRN,
    add_input, add_output, add_pause_fact, add_delay, add_game_delay,
    add_pause_journal, add_setvar, add_journal, add_scene, add_journal_quest,
    add_addvar, add_pause_facts, add_condition_fact, add_race2,
    add_pause_node_loaded, add_prefab_variant, add_toggle_component,
    add_call_contact,
    add_community, add_crowd_null_area, add_loot_access,
    ANCHOR_PLAYER,
)

configure(phase_name='gig02.questphase')

from gig02_config import (                                          # noqa: E402
    RAW_MOD, DEPOT, QUEST_ID,
    ANCHOR_AFTERLIFE, ANCHOR_INN, ANCHOR_PARLOR, ANCHOR_OFFICE, ANCHOR_HIT,
    ANCHOR_STUDIO,
)

from gen_community import SPAWNSET_NAME                             # noqa: E402,F401
import gen_community                                                # noqa: E402

CAST_REF = '$/mod/' + gen_community.SECTOR + '/#' + gen_community.SECTOR + '_com'

# THE TWO VANILLA COMMUNITIES AT THE AFTERLIFE DOOR, written the way the game
# writes them. Rogue's date (sq031_date.questphase, nodes 443 and 444) plays at
# this exact door and switches these entries back on afterwards with
# `Reactivate`, the SHORT reference (`#q005_com_afterlife_background`), the
# entry name AND the entry's phase name (`q005`, `q103`). The first attempt
# here (2026-09-04, morning) used the long path from the sector's nodeRef
# table, no phase name and `Activate`, and changed nothing in play; this is
# the vanilla shape, field for field. Entries: every one whose spot is within
# 14 m of the three listening posts, resolved through the nodeRef tables.
# THE VANILLA VENDOR AT THE DEWDROP INN, written the way the game writes a
# community switch (gotcha 94): short reference, entry, phase. Read off
# always_loaded_1: SpawnSet_#wat_kab_netrunner_01, one entry, phase default.
VANILLA_YOKO = ('#wat_kab_netrunner_01', 'wat_kab_netrunner_01', 'default')

# WAKAKO'S OWN SPAWN SET, read off the community registry 2026-09-05:
# `#wakako`, entry `wakako`, phase `default`. Her doorman is the game's and
# is left alone (design call, same day).
VANILLA_WAKAKO = ('#wakako', 'wakako', 'default')

VANILLA_DOOR_CROWD = [
    ('#q005_com_afterlife_background', 'q005',
     ['crowd_female', 'crowd_male', 'male_on_stairs_2']),
    ('#q103_com_afterlife_crowd', 'q103',
     ['showoff', 'groupie_01', 'groupie_02', 'crowd_female', 'crowd_male',
      'claws_out_male_01', 'claws_out_female_01', 'claws_out_female_02',
      'male_on_stairs', 'media_spy']),
]
CAST = [row[0] for row in gen_community.CAST]

OUT = os.path.join(RAW_MOD, 'quest', 'gig02.questphase.json')

QUEST = 'quests/street_stories/' + QUEST_ID
POI = 'points_of_interest/street_stories/' + QUEST_ID
PHASE = QUEST + '/phase_main'

# The same string gen_scenes.SCENE_DEPOT builds, and it has to stay so: the
# lipmap is keyed by FNV1a64 of exactly this path plus the scene name.
SCENES = DEPOT + chr(92) + 'scenes' + chr(92)

# --------------------------------------------------------------- the contacts
#
# Journal paths, not CNames: `questCallContact_NodeType` resolves a caller by
# path, so a mod-owned contact brings none of the real contact's conversation.
WAKAKO_CONTACT = 'contacts/cc_g02_wakako'
WAKAKO_CONV = WAKAKO_CONTACT + '/cc_g02_wakako_conv'
CHAR_CONTACT = 'contacts/cc_g02_char'
CHAR_CONV = CHAR_CONTACT + '/cc_g02_char_conv'
PLAYER_CONTACT = 'contacts/player'

MSG_01 = WAKAKO_CONV + '/cc_g02_msg_01'
CHOICE_GROUP = WAKAKO_CONV + '/cc_g02_ch_01'
CHOICE_CALL = CHOICE_GROUP + '/cc_g02_ch_01a'
CHOICE_GROUP_2 = WAKAKO_CONV + '/cc_g02_ch_02'
CHOICE_REPORT = CHOICE_GROUP_2 + '/cc_g02_ch_02a'
MSG_02 = WAKAKO_CONV + '/cc_g02_msg_02'
CHOICE_GROUP_3 = WAKAKO_CONV + '/cc_g02_ch_03'
CHOICE_REPORT_B = CHOICE_GROUP_3 + '/cc_g02_ch_03a'
MSG_02B = WAKAKO_CONV + '/cc_g02_msg_02b'
MSG_03 = CHAR_CONV + '/cc_g02_msg_03'
# The relay's upload, acknowledged and then answered (2026-09-05).
MSG_05 = CHAR_CONV + '/cc_g02_msg_05'
MSG_06 = CHAR_CONV + '/cc_g02_msg_06'
MSG_07 = CHAR_CONV + '/cc_g02_msg_07'
MSG_08 = CHAR_CONV + '/cc_g02_msg_08'
CHOICE_GROUP_4 = CHAR_CONV + '/cc_g02_ch_04'
CHOICE_REPLY_CHAR = CHOICE_GROUP_4 + '/cc_g02_ch_04a'
CHOICE_GROUP_5 = CHAR_CONV + '/cc_g02_ch_05'
CHOICE_SEND_DUMP = CHOICE_GROUP_5 + '/cc_g02_ch_05a'
MSG_04 = WAKAKO_CONV + '/cc_g02_msg_04'
MSG_09 = WAKAKO_CONV + '/cc_g02_msg_09'
BRIEF_PATH = QUEST + '/cc_g02_briefing'

# ------------------------------------------------------------ the studio
#
# WAKAKO'S OWN SETUP, 2026-09-07, and this reverses a decision from 2026-08-26.
#
# It was hers, then it was swapped to Mama Welles's, on the finding that
# "vanilla does not put its Wakako on the studio's floor spot at all: her own
# holocall scene acquires her from a spawn set, so her camera is aimed at
# wherever that spawn set stands her, and ours is a plain spawned NPC at
# `#holocall_marker`, a different place and a different pose, so her camera
# frames neither." Every word of that is true. What was missing was a way to
# put our body where her camera looks.
#
# THAT IS WHAT THE WORLD WORKSPOT NODE DOES. `{wakako_holocall_workspot}` is a
# `worldAISpotNode` in the studio's quest sector, read off disk 2026-09-07 at
# (5895.207, 6136.237, 0.000) yaw -65, playing
# `generic__sit_chair_table_lean_front__sit_around__01.workspot`. That is the
# spot the spawn set stands her on, and `{wakako_holocall_camera}` sits 0.9 m
# away at height 0.929 aimed at it. `gen_scenes.studio_pose` teleports our
# actor onto that node, so all three now agree.
#
# SHE SITS. The camera height is the giveaway: 0.929 is a seated frame, where
# Mama Welles's is 1.52 for a standing one. A playtest screenshot of the real
# Wakako holocall shows her seated behind a desk, leaning forward, looking
# into the lens; ours was standing, side-on and barely lit, because it was
# framed and lit for somebody else's pose.
#
# CHAR RIDES THE SAME SETUP, and a seated frame suits her: she is a netrunner
# in a chair everywhere else in this gig.
#
# ONE SET PER SPEAKER, 2026-09-07. Char used to ride Wakako's, which put the
# two women in the same chair in the same pose two beats apart and read as one
# recycled shot (playtest: "feels weird"). A contact's four names are a set and
# they are only correct together, so a second speaker takes a second set.
#
# CHAR IS BLUE MOON'S. Every seated setup in the studio was surveyed by camera
# height and workspot resource: El Capitan and Padre are literally Wakako's
# spot and pose with the camera a few centimetres higher, so they would have
# changed nothing. Blue Moon's is `rogue__sit_bench_lean_back__sit_around__01`
# on a different spot at yaw -145, camera 1.037, and it LEANS BACK where
# Wakako leans forward. It is framed for a slim woman, and it matches how the
# player last saw Char, reclining in the netrunner's chair at the Inn.
#
# ALL FIVE NAMES PER SET ARE READ OUT OF THAT CONTACT'S OWN
# `<contact>_holocall.scene`, never extrapolated: a wrong one is a silent
# no-op. The two workspot names live in gen_scenes.
STUDIO_PREFAB = '#holocalls_studio'
LIGHTS_REF = '#holocalls_studio_lighting'

# (lights variant, setup ref, setup variant, camera ref)
WAKAKO_STUDIO = ('wakako_holocall_lights', '#wakako_holocall_setup',
                 'wakako_holocall_setup', '#wakako_holocall_camera')
CHAR_STUDIO = ('blue_moon_holocall_lights', '#blue_moon_holocall_setup',
               'blue_moon_holocall_setup', '#blue_moon_holocall_camera')

STUDIO_SECONDS = 20
DIAL_SECONDS = 3


# ---- graph ----------------------------------------------------------------
chain = []
PHASE_IN = add_input()
chain.append((PHASE_IN, 'Out'))


def step(nid, in_sock='In', out_sock='Out'):
    prev_nid, prev_sock = chain[-1]
    b.connect((prev_nid, prev_sock), (nid, in_sock))
    chain.append((nid, out_sock))


def scene(name, entry, exit_):
    step(add_scene(SCENES + name + '.scene', ANCHOR_PLAYER, [entry], [exit_]),
         in_sock=entry, out_sock=exit_)


def scene_at(name, anchor, entry, exit_):
    step(add_scene(SCENES + name + '.scene', anchor, [entry], [exit_]),
         in_sock=entry, out_sock=exit_)


def objective_step(gate_fact, done_obj, next_obj=None, next_pin=None):
    """Wait for a fact, close one objective, open the next one and its pin.
    A pin entry must be activated ALONGSIDE its objective or it never appears."""
    step(add_pause_fact(gate_fact))
    step(add_journal('gameJournalQuestObjective', PHASE + '/' + done_obj,
                     notify=0), in_sock='Succeeded')
    if next_obj:
        step(add_journal('gameJournalQuestObjective', PHASE + '/' + next_obj),
             in_sock='Active')
        if next_pin:
            step(add_journal('gameJournalQuestMapPin',
                             PHASE + '/' + next_obj + '/' + next_pin, notify=0),
                 in_sock='Active')


def open_objective(oid, pin=None):
    step(add_journal('gameJournalQuestObjective', PHASE + '/' + oid),
         in_sock='Active')
    if pin:
        step(add_journal('gameJournalQuestMapPin', PHASE + '/' + oid + '/' + pin,
                         notify=0), in_sock='Active')


def close_objective(oid):
    step(add_journal('gameJournalQuestObjective', PHASE + '/' + oid, notify=0),
         in_sock='Succeeded')


def wakako_call(prefix, scene_name, entry, exit_, contact=None,
                studio=None):
    """One outgoing video call, to Wakako unless `contact` says otherwise:
    dial, wait for the studio, speak, hang up.

    THE DIAL COMES BEFORE THE WAIT, and that ordering is the whole fix of
    2026-09-07. It looks like a detail and it decides whether the player sees
    a person or an empty frame.

    WHAT LOADS THE STUDIO IS THE CALL NODE, not the prefab variants. The
    studio is a `category: Quest` sector with no streaming box, and
    `questCallContact_NodeType` is the only thing here that carries
    `prefabNodeRef: #holocalls_studio`, which is what asks for it. Showing the
    variants only says which pieces should exist ONCE the sector is there; on
    a sector nobody has asked for, it does nothing at all.

    So the old order could not work on a cold studio:

        variants on   ->  nothing, the sector is not loaded
        wait 20 s for the camera  ->  it cannot arrive, nobody asked
        give up, skip switching the camera on
        place the call  ->  THIS loads the studio, camera appears, too late
        talk to an empty frame

    MEASURED, not reasoned. The dev menu's holocall probe was pressed three
    times during one failed call: `claim` 0 and the camera absent, `claim` 0
    and still absent, then `claim` 2 (the giveup won) and the camera PRESENT.
    It arrives immediately after the giveup because the giveup is immediately
    followed by the call.

    It worked on a late save because a vanilla holocall earlier in that
    session had already pulled the studio in, so the camera was sitting there
    when the wait looked for it. That is also why calling Regina first did not
    help: her studio unloads again when her call ends.

    Vanilla's own `wakako_holocall.scene` has this order: its phone node
    carrying `#holocalls_studio` comes first and its camera waits come after.

    The wait now sits in the gap where the phone is already dialling, which is
    where it belongs. The giveup stays as a safety net rather than as the
    thing that fires every time; a call issued as Video with the camera never
    switched on still connects and draws an empty frame, which is a worse
    picture and not a broken gig."""
    global chain
    contact = contact or WAKAKO_CONTACT
    lights_variant, setup_ref, setup_variant, camera_ref = studio or WAKAKO_STUDIO
    step(add_setvar(prefix + '_claim', 0))
    step(add_setvar(prefix + '_video', 0))
    step(add_prefab_variant(LIGHTS_REF, lights_variant, True))
    step(add_prefab_variant(setup_ref, setup_variant, True))

    # PhoneSystem's own call fact persists at Talking once a call has been
    # answered, so it is cleared before every call.
    phone_fact = ('phonecall_' + PLAYER_CONTACT.split('/')[-1] + '_with_'
                  + contact.split('/')[-1]).lower()
    step(add_setvar(phone_fact, 0))

    def call(phase):
        return add_call_contact(PLAYER_CONTACT, contact, phase,
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
    step(add_setvar(prefix + '_talking', 1))
    scene_at(scene_name, ANCHOR_STUDIO, entry, exit_)
    step(call('EndCall'))
    step(add_toggle_component(camera_ref, 'RenderToTextureCamera', False))
    step(add_prefab_variant(setup_ref, setup_variant, False))
    step(add_prefab_variant(LIGHTS_REF, lights_variant, False))
    step(add_setvar(prefix + '_done', 1))


def char_call(scene_name, entry, exit_):
    """One outgoing VIDEO call to Char (design call 2026-09-05): the same
    studio recipe as Wakako's, with our Char record on the floor spot. She
    was audio, on the argument that one exchange of advice does not earn the
    studio; the same woman on the phone as in the chair is the point now."""
    wakako_call('cc_g02_callc', scene_name, entry, exit_, contact=CHAR_CONTACT,
                studio=CHAR_STUDIO)


# ===========================================================================
# 0. NOBODY IS ON THE STREET YET
# ===========================================================================
#
# A mod's community spawns its entries on save load whatever
# `entryActiveOnStart` says (gotcha 69), so the phase is what keeps these
# people away until their leg opens.
for _who in CAST:
    step(add_community('Deactivate', CAST_REF, entry=_who))

# ===========================================================================
# DEV: THE DOOR-CROWD TEST HARNESS, 2026-09-04
# ===========================================================================
#
# Three playtests could not remove the game's own queue outside Afterlife, and
# each cost a playthrough to the beat. These arms wait from the moment the
# phase starts, BEFORE the gig, on one dev fact the CET menu sets, so every
# shape of the switch can be tried on a pre-gig save in one session, standing
# at the door. Each arm fires once per save and clears the fact after itself.
#
#   1  Deactivate the queue's three entries, LONG reference, phase q005
#   2  the same, SHORT reference (what Rogue's date writes; the main flow's)
#   3  Deactivate the whole community, long reference, no entry
#   4  the same, short reference
#   5  crowd null area ON          6  crowd null area OFF
#   7  Reactivate the three entries, long, phase q005
#   8  the same, short
_Q005_LONG = ('$/03_night_city/c_watson/little_china/#loc_q103_afterlife/'
              '#loc_q103_afterlife_openworld/#q005_com_afterlife_background')
_Q005_SHORT = '#q005_com_afterlife_background'
_Q005_ENTRIES = ['crowd_female', 'crowd_male', 'male_on_stairs_2']
_dev_root = chain[-1]


def _dev_arm(value, actions):
    arm = add_pause_fact('cc_g02_dev_crowd', value, 'Equal')
    b.connect(_dev_root, (arm, 'In'))
    prev = (arm, 'Out')
    for nid in actions + [add_setvar('cc_g02_dev_crowd', 0)]:
        b.connect(prev, (nid, 'In'))
        prev = (nid, 'Out')


_dev_arm(1, [add_community('Deactivate', _Q005_LONG, entry=e, phase='q005') for e in _Q005_ENTRIES])
_dev_arm(2, [add_community('Deactivate', _Q005_SHORT, entry=e, phase='q005') for e in _Q005_ENTRIES])
_dev_arm(3, [add_community('Deactivate', _Q005_LONG)])
_dev_arm(4, [add_community('Deactivate', _Q005_SHORT)])
_dev_arm(5, [add_crowd_null_area(gen_community.CROWD_NULL_REF, True)])
_dev_arm(6, [add_crowd_null_area(gen_community.CROWD_NULL_REF, False)])
_dev_arm(7, [add_community('Reactivate', _Q005_LONG, entry=e, phase='q005') for e in _Q005_ENTRIES])
_dev_arm(8, [add_community('Reactivate', _Q005_SHORT, entry=e, phase='q005') for e in _Q005_ENTRIES])
# THE POSE LAB'S BODY (tag cc_g02_lab): loot access off and on, to see what the
# switch removes on a Defeated body: the list, the pick-up prompt, or both.
_dev_arm(9, [add_loot_access(None, None, False, tag='cc_g02_lab')])
_dev_arm(10, [add_loot_access(None, None, True, tag='cc_g02_lab')])
# THE INN'S BODIES, for a save already past the node that switches them: 11
# turns the vendor off and ours on, 12 the reverse.
_dev_arm(11, [add_community('Deactivate', VANILLA_YOKO[0], entry=VANILLA_YOKO[1], phase=VANILLA_YOKO[2]),
              add_community('Activate', CAST_REF, entry='yoko'),
              add_community('Activate', CAST_REF, entry='char')])
_dev_arm(12, [add_community('Deactivate', CAST_REF, entry='yoko'),
              add_community('Deactivate', CAST_REF, entry='char'),
              add_community('Reactivate', VANILLA_YOKO[0], entry=VANILLA_YOKO[1], phase=VANILLA_YOKO[2])])
# WAKAKO, the same way: 13 the game's off and ours on, 14 the reverse.
_dev_arm(13, [add_community('Deactivate', VANILLA_WAKAKO[0], entry=VANILLA_WAKAKO[1], phase=VANILLA_WAKAKO[2]),
              add_community('Activate', CAST_REF, entry='wakako')])
_dev_arm(14, [add_community('Deactivate', CAST_REF, entry='wakako'),
              add_community('Reactivate', VANILLA_WAKAKO[0], entry=VANILLA_WAKAKO[1], phase=VANILLA_WAKAKO[2])])

# THE APPEARANCE A/B, arm 15 (backlog 42). Char in the holocall studio with
# nothing to say, so she can be looked at on the phone while a body of the same
# record stands in front of the player. The CET button sets this fact AND
# spawns the second body, so the two arrive together.
#
# HER CONTACT IS ADDED FIRST. Outside the gig it has never been added, and the
# phone draws its avatar and its name from the journal contact; without it the
# call is a stranger ringing. Adding a contact twice is what `notify=0` is for.
#
# NOT WIRED THROUGH _dev_arm, because that helper chains single-socket nodes
# and a holocall is a race, a scene and a dozen steps. It borrows `chain` the
# way the main line does and puts it back, so nothing below sees the loan.
step(add_pause_fact('cc_g02_start'))
step(add_setvar('cc_g02_started', 1))

# ===========================================================================
# 1-2. THE MESSAGE, AND THE CALL THE PLAYER PLACES FROM IT
# ===========================================================================
step(add_journal('gameJournalContact', WAKAKO_CONTACT, notify=0),
     in_sock='Active')
step(add_journal('gameJournalPhoneConversation', WAKAKO_CONV, notify=0),
     in_sock='Active')
step(add_journal('gameJournalPhoneMessage', MSG_01), in_sock='Active')

# The message lands alone; the quest goes into the log only after the call,
# with the pin she says she is sending. Two notifications on one frame ate the
# message preview once.
step(add_journal('gameJournalPhoneChoiceGroup', CHOICE_GROUP, notify=0),
     in_sock='Active')

step(add_pause_journal('gameJournalPhoneChoiceEntry', CHOICE_CALL))
step(add_setvar('cc_g02_called', 1))

wakako_call('cc_g02_call1', 'gig02_wakako_call',
            'wakako_call_in', 'wakako_call_out')
# THE ATTACHMENT. "I am attaching more information. Read it. Carefully." is
# the last thing she says on the call, and this is it: her message with the
# premise, then the quest with the same premise as its brief. THE MESSAGE GOES
# FIRST AND ALONE, with a few seconds before anything else, because two
# notifications on one frame ate the message preview once (2026-08-26).
step(add_journal('gameJournalPhoneMessage', MSG_04), in_sock='Active')
# NOTHING HAPPENS UNTIL THE BRIEF HAS BEEN READ AND CLOSED (playtest
# 2026-09-04: Johnny spoke over an unopened message). Gig02_Encounter sets
# `cc_g02_brief_read` when the journal reports the message visited and the
# phone is closed again. No timeout: the brief is the gig.
step(add_pause_fact('cc_g02_brief_read'))
step(add_delay(0.3))

# THE GIG GOES INTO THE JOURNAL THE MOMENT THE BRIEF HAS LANDED, and its first
# objective is Johnny: V's "Shit." and his line are a reaction to what the
# brief says, and Afterlife only opens once he has finished (2026-09-03).
step(add_setvar('cc_g02_accepted', 1))
# THE GAME'S OWN CROWD LEAVES THE DOOR FIRST, 2026-09-04. Playtest: our five
# bodies and the merc spawned in among the game's Afterlife queue, and when V
# shot the merc the queue shot back. Two vanilla communities own spots within
# 14 m of the three listening posts (resolved through the sectors' NodeRef
# tables, tools/sector_scan.py index afterlife, then FNV1a64 of each ref with
# the '#' removed, which is how worldCompiledCommunityAreaNode names a spot):
#
#   q005_com_afterlife_background   the permanent queue: crowd_female,
#                                   crowd_male, male_on_stairs_2. Whole
#                                   community, the vanilla norm.
#   q103_com_afterlife_crowd        Playing for Time's crowd, spots in a
#                                   quest-only sector. Its door entries only,
#                                   so the gang and droid entries elsewhere in
#                                   it are never touched.
#
# Both come back once the merc leg is over, below. An entry whose sector is
# not streamed has nowhere to spawn, so reactivating the quest crowd on a save
# past that quest is a no-op.
for _ref, _phase, _entries in VANILLA_DOOR_CROWD:
    for _who in _entries:
        step(add_community('Deactivate', _ref, entry=_who, phase=_phase))
# ...AND THE CROWD SYSTEM TOO, which is what the people at the door actually
# are (2026-09-04): they change on every load and the community switches
# above did not touch them. The null area is ours, in the cast sector.
step(add_crowd_null_area(gen_community.CROWD_NULL_REF, True))
step(add_community('Activate', CAST_REF, entry='merc'))
for _who in ('queue_a', 'queue_b', 'queue_c', 'queue_d', 'queue_e', 'queue_f', 'queue_g'):
    step(add_community('Activate', CAST_REF, entry=_who))
step(add_journal_quest(QUEST), in_sock='Active')
step(add_journal('gameJournalQuestDescription', BRIEF_PATH, notify=0),
     in_sock='Active')
step(add_journal('gameJournalQuestPhase', PHASE, notify=0), in_sock='Active')
step(add_journal('gameJournalPointOfInterestMappin', POI, notify=0),
     in_sock='Active')
open_objective('obj_johnny')
step(add_delay(0.5))
scene('gig02_johnny_open', 'johnny_open_in', 'johnny_open_out')
close_objective('obj_johnny')

# ===========================================================================
# 3-4. AFTERLIFE, AND THE THING WORTH OVERHEARING
# ===========================================================================
open_objective('obj_afterlife', 'pin_afterlife')
objective_step('cc_g02_afterlife_reached', 'obj_afterlife')

# Two pins up together, the player picks the order, and only the journal
# branches: a scene node cannot be entered from two places.
open_objective('obj_group1', 'pin_group1')
open_objective('obj_group2', 'pin_group2')

step(add_pause_fact('cc_g02_group_first'))
scene_at('gig02_talk_a', ANCHOR_AFTERLIFE, 'talk_a_in', 'talk_a_out')
FIRST_IS_1 = add_condition_fact('cc_g02_group_first', 1, 'Equal')
b.connect(chain[-1], (FIRST_IS_1, 'In'))

chain = [(FIRST_IS_1, 'True')]
close_objective('obj_group1')
A1_END = chain[-1]
chain = [(FIRST_IS_1, 'False')]
close_objective('obj_group2')
A2_END = chain[-1]

TALK_A_DONE = add_setvar('cc_g02_talk_a_done', 1)
b.connect(A1_END, (TALK_A_DONE, 'In'))
b.connect(A2_END, (TALK_A_DONE, 'In'))
chain = [(TALK_A_DONE, 'Out')]

step(add_pause_fact('cc_g02_group_second'))
scene_at('gig02_talk_b', ANCHOR_AFTERLIFE, 'talk_b_in', 'talk_b_out')
SECOND_IS_2 = add_condition_fact('cc_g02_group_first', 1, 'Equal')
b.connect(chain[-1], (SECOND_IS_2, 'In'))

chain = [(SECOND_IS_2, 'True')]
close_objective('obj_group2')
B1_END = chain[-1]
chain = [(SECOND_IS_2, 'False')]
close_objective('obj_group1')
B2_END = chain[-1]

GRP_JOIN = add_setvar('cc_g02_groups_done', 1)
b.connect(B1_END, (GRP_JOIN, 'In'))
b.connect(B2_END, (GRP_JOIN, 'In'))
chain = [(GRP_JOIN, 'Out')]

# ===========================================================================
# 5. THE LAST GROUP, AND THE MERC IS THE ONE TALKING
# ===========================================================================
open_objective('obj_group3', 'pin_group3')
step(add_pause_fact('cc_g02_group3_near'))
scene_at('gig02_group3', ANCHOR_AFTERLIFE, 'group3_in', 'group3_out')
step(add_setvar('cc_g02_lead_heard', 1))
close_objective('obj_group3')

# ===========================================================================
# 5b. TAKE HIM OUT, AND WHAT HE SAYS ON ONE KNEE
# ===========================================================================
#
# THE ORDER IS A KILL, 2026-09-03. His boast named Jig-Jig Street, the brief
# named Jig-Jig Street, and the objective is to take him out. `merc_armed`
# makes him hittable; he is Immortal through the fight so it cannot end
# early, and at a third of his health Gig02_Encounter sets `merc_down`. The
# scene then takes him onto one knee. It hands over the shard from inside
# itself (`merc_talked`) and ends on the choice (`merc_fate`).
open_objective('obj_take_out')
step(add_setvar('cc_g02_merc_armed', 1))
step(add_pause_fact('cc_g02_merc_down'))
# HIS POCKET IS CLOSED UNTIL HE SAYS TO TAKE IT (design call 2026-09-05): the
# shard goes in at the fall, so the loot list is switched off here and back on
# after his last line. The same switch may cover "Pick Up Body"; the lab arms
# 9 and 10 below measure that.
step(add_loot_access(CAST_REF, 'merc', False))
close_objective('obj_take_out')
# THE FALL FIRST. The script knocks him down on the tick that sets merc_down
# (Defeated, then Bleeding, then the shard into his pocket); three seconds is
# the fall and the settle before anyone speaks (pose lab, 2026-09-05).
# NEVER AN EMPTY OBJECTIVE LIST (design call 2026-09-05): while he talks,
# the objective says so.
open_objective('obj_listen_merc')
step(add_delay(3.0))
scene_at('gig02_beaten', ANCHOR_AFTERLIFE, 'beaten_in', 'beaten_out')
close_objective('obj_listen_merc')
step(add_loot_access(CAST_REF, 'merc', True))

# THE SHARD, OFF HIM AND READ. Both objectives are skipped for a player who
# got there first: the loot list is open from the moment he is down, and the
# reader can be opened from it or later from the journal's shards. The script
# sets `shard_taken` when the item is in the player's inventory, and the
# reader wrap sets `proof_read` when OUR shard's popup closes.
SHARD_TAKEN = add_condition_fact('cc_g02_shard_taken', 1, 'Equal')
b.connect(chain[-1], (SHARD_TAKEN, 'In'))
chain = [(SHARD_TAKEN, 'False')]
open_objective('obj_get_shard')
step(add_pause_fact('cc_g02_shard_taken'))
close_objective('obj_get_shard')
TAKE_JOIN = add_setvar('cc_g02_shard_leg', 1)
b.connect(chain[-1], (TAKE_JOIN, 'In'))
b.connect((SHARD_TAKEN, 'True'), (TAKE_JOIN, 'In'))
chain = [(TAKE_JOIN, 'Out')]

SHARD_READ = add_condition_fact('cc_g02_proof_read', 1, 'Equal')
b.connect(chain[-1], (SHARD_READ, 'In'))
chain = [(SHARD_READ, 'False')]
open_objective('obj_proof')
step(add_pause_fact('cc_g02_proof_read'))
close_objective('obj_proof')
READ_JOIN = add_setvar('cc_g02_shard_leg', 2)
b.connect(chain[-1], (READ_JOIN, 'In'))
b.connect((SHARD_READ, 'True'), (READ_JOIN, 'In'))
chain = [(READ_JOIN, 'Out')]

# THE CHOICE, in its own scene now. 1: he is killable and the objective says
# so. 2: he runs.
open_objective('obj_decide')
scene_at('gig02_fate', ANCHOR_AFTERLIFE, 'fate_in', 'fate_out')
close_objective('obj_decide')
MERC_FATE = add_condition_fact('cc_g02_merc_fate', 1, 'Equal')
b.connect(chain[-1], (MERC_FATE, 'In'))

chain = [(MERC_FATE, 'True')]
open_objective('obj_kill_merc')
step(add_setvar('cc_g02_merc_kill_armed', 1))
step(add_pause_fact('cc_g02_merc_dead'))
close_objective('obj_kill_merc')
KILL_END = chain[-1]

chain = [(MERC_FATE, 'False')]
step(add_setvar('cc_g02_merc_flee', 1))
FLEE_END = chain[-1]

MERC_JOIN = add_setvar('cc_g02_merc_done', 1)
b.connect(KILL_END, (MERC_JOIN, 'In'))
b.connect(FLEE_END, (MERC_JOIN, 'In'))
chain = [(MERC_JOIN, 'Out')]

# ===========================================================================
# 7. THE REPORT IS A TEXT
# ===========================================================================
#
# V picks a reply in Wakako's thread and she answers by message with the
# netrunner's location. The pause is on the choice ENTRY. This replaced a
# video call whose nine lines did not exist in her voice, and a message is
# also how she runs her own gigs.
open_objective('obj_report')
# ONE REPLY PER FATE (2026-09-05): the thread offers the "he's dead" reply
# or the "left him breathing" one, and Wakako answers each in kind.
REPORT_FATE = add_condition_fact('cc_g02_merc_fate', 1, 'Equal')
b.connect(chain[-1], (REPORT_FATE, 'In'))
chain = [(REPORT_FATE, 'True')]
step(add_journal('gameJournalPhoneChoiceGroup', CHOICE_GROUP_2, notify=0),
     in_sock='Active')
step(add_pause_journal('gameJournalPhoneChoiceEntry', CHOICE_REPORT))
REPORT_KILL_END = chain[-1]
chain = [(REPORT_FATE, 'False')]
step(add_journal('gameJournalPhoneChoiceGroup', CHOICE_GROUP_3, notify=0),
     in_sock='Active')
step(add_pause_journal('gameJournalPhoneChoiceEntry', CHOICE_REPORT_B))
REPORT_SPARE_END = chain[-1]
REPORT_JOIN = add_setvar('cc_g02_reported', 1)
b.connect(REPORT_KILL_END, (REPORT_JOIN, 'In'))
b.connect(REPORT_SPARE_END, (REPORT_JOIN, 'In'))
chain = [(REPORT_JOIN, 'Out')]
# THE REPLY IS SENT: the objective is Johnny at once (playtest 2026-09-04),
# Wakako's answer lands under it, and he comments on the answer.
close_objective('obj_report')
open_objective('obj_johnny_2')
ANSWER_FATE = add_condition_fact('cc_g02_merc_fate', 1, 'Equal')
b.connect(chain[-1], (ANSWER_FATE, 'In'))
chain = [(ANSWER_FATE, 'True')]
step(add_journal('gameJournalPhoneMessage', MSG_02), in_sock='Active')
ANSWER_KILL_END = chain[-1]
chain = [(ANSWER_FATE, 'False')]
step(add_journal('gameJournalPhoneMessage', MSG_02B), in_sock='Active')
ANSWER_SPARE_END = chain[-1]
ANSWER_JOIN = add_setvar('cc_g02_wakako_2', 1)
b.connect(ANSWER_KILL_END, (ANSWER_JOIN, 'In'))
b.connect(ANSWER_SPARE_END, (ANSWER_JOIN, 'In'))
chain = [(ANSWER_JOIN, 'Out')]

# Char arrives at the Dewdrop Inn, and the Afterlife door goes back to normal
# on its OWN BRANCH.
#
# THE DOOR IS A SIDE BRANCH AND MUST STAY ONE. Waiting for the player to walk
# away is right for the door and wrong for everything else: putting that wait
# on the main line stopped the whole gig at this point, so Johnny never
# commented on the message and the objective never moved (playtest
# 2026-09-07). The rule is the one the seen-while-alive fork below already
# follows: a wait that exists to hide something has no business gating the
# story. Gotcha 104, including how to prove it on the built graph.
#
# WHICH HALF GOES WHERE IS DECIDED BY WHAT THE PLAYER CAN SEE. The Afterlife
# swaps happen where he is standing, so they wait. The Dewdrop Inn swaps are a
# kilometre away in Kabuki and nobody can watch them, so they run at once and
# are certain to be done before he arrives.
AFTERLIFE_FORK = chain[-1]

# --- the branch: the door, once V is 100 m from it -------------------------
# `cc_g02_afterlife_clear` is set by Gig02_Encounter.AfterlifeClear, which
# holds during a fast travel and gives up after ten minutes so this can never
# be left half done. It has no output on purpose: nothing downstream waits.
DOOR_WAIT = add_pause_fact('cc_g02_afterlife_clear')
b.connect(AFTERLIFE_FORK, (DOOR_WAIT, 'In'))
chain = [(DOOR_WAIT, 'Out')]
step(add_community('Deactivate', CAST_REF, entry='merc'))
for _who in ('queue_a', 'queue_b', 'queue_c', 'queue_d', 'queue_e', 'queue_f', 'queue_g'):
    step(add_community('Deactivate', CAST_REF, entry=_who))
# The game's own queue comes back.
for _ref, _phase, _entries in VANILLA_DOOR_CROWD:
    for _who in _entries:
        step(add_community('Reactivate', _ref, entry=_who, phase=_phase))
step(add_crowd_null_area(gen_community.CROWD_NULL_REF, False))

# --- back to the story -----------------------------------------------------
chain = [AFTERLIFE_FORK]
# YOKO: the game's vendor off, ours on, for the leg (2026-09-05). Yoko is the
# base game's own NPC and is acquired by her scene, so nothing of ours is
# switched on for her beyond this body.
step(add_community('Deactivate', VANILLA_YOKO[0], entry=VANILLA_YOKO[1], phase=VANILLA_YOKO[2]))
step(add_community('Activate', CAST_REF, entry='yoko'))
step(add_community('Activate', CAST_REF, entry='char'))

# Let the message land before Johnny comments on it.
step(add_delay(2))
scene('gig02_planned', 'planned_in', 'planned_out')
close_objective('obj_johnny_2')
open_objective('obj_inn', 'pin_inn')

# ===========================================================================
# 8-9. THE DEWDROP INN, AND THE TRACE BY MESSAGE
# ===========================================================================
step(add_pause_fact('cc_g02_inn_reached'))
scene_at('gig02_inn', ANCHOR_INN, 'inn_in', 'inn_out')
objective_step('cc_g02_inn_reached', 'obj_inn', 'obj_shard', 'pin_shard')
step(add_setvar('cc_g02_to_char', 1))
step(add_pause_fact('cc_g02_char_near'))
scene_at('gig02_handover', ANCHOR_INN, 'handover_in', 'handover_out')
close_objective('obj_shard')
open_objective('obj_wait')

# HALF AN IN-GAME HOUR ON THE WORLD CLOCK, then her message. A realtime delay
# stalls while a menu is open (gotcha 3) and the phone is a menu.
step(add_game_delay(minutes=30))
step(add_journal('gameJournalContact', CHAR_CONTACT, notify=0), in_sock='Active')
step(add_journal('gameJournalPhoneConversation', CHAR_CONV, notify=0),
     in_sock='Active')
step(add_journal('gameJournalPhoneMessage', MSG_03), in_sock='Active')
step(add_setvar('cc_g02_trace_done', 1))

# Char goes home; Wakako's doorman takes his post.
step(add_community('Deactivate', CAST_REF, entry='char'))
step(add_community('Deactivate', CAST_REF, entry='yoko'))
step(add_community('Reactivate', VANILLA_YOKO[0], entry=VANILLA_YOKO[1], phase=VANILLA_YOKO[2]))
# WAKAKO IS OURS FROM HERE TO HER ORDER (2026-09-05): the game's own Wakako
# off, ours on, before V is anywhere near the building, so her own greeting
# cannot start on the way in and nothing of hers is open when our scene
# wants her. Gig02_Encounter.ParlorKeeper disposes the game's body if it
# lingers. The doorman is the game's own and is not touched.
step(add_community('Deactivate', VANILLA_WAKAKO[0], entry=VANILLA_WAKAKO[1], phase=VANILLA_WAKAKO[2]))
step(add_community('Activate', CAST_REF, entry='wakako'))
close_objective('obj_wait')
open_objective('obj_parlor', 'pin_parlor')

# ===========================================================================
# 10-11. THE PARLOR: THE BREACH
# ===========================================================================
step(add_pause_fact('cc_g02_parlor_reached'))
# JOHNNY'S "Not a word." IS GONE (design call 2026-09-05: nothing for the
# player to do with it). The phone rings as V walks in.

# CHAR ON THE PHONE SAYS WHAT TO LOOK FOR. This is the parlor's answer to
# "there is nothing to look for", and it is the base game's own device: the
# specialist on comms tells the hero what the room means.
char_call('gig02_char_call', 'char_call_in', 'char_call_out')

# THE BREACH (design call 2026-09-05: "a box where you need to do the number
# hacking, in one of the walls"). The parlor's wall carries an access point of
# the mod's own (gen_sector.py), and the beat is the game's own breach
# protocol on it. The script sets `cc_g02_ap_breached` when the device says
# it is breached (Gig02_Encounter.AccessPoint, two signals). Char texts at
# once, and half an in-game hour later texts the man's name. Then Wakako.
objective_step('cc_g02_parlor_reached', 'obj_parlor', 'obj_relay')
step(add_pause_fact('cc_g02_ap_breached'))
close_objective('obj_relay')
# V SENDS THE DUMP (design call 2026-09-05): the objective says so, and it
# is a pick in Char's thread, the way the report to Wakako is.
open_objective('obj_send_dump')
step(add_journal('gameJournalPhoneChoiceGroup', CHOICE_GROUP_5, notify=0), in_sock='Active')
step(add_pause_journal('gameJournalPhoneChoiceEntry', CHOICE_SEND_DUMP))
close_objective('obj_send_dump')
step(add_journal('gameJournalPhoneMessage', MSG_05), in_sock='Active')
open_objective('obj_wait2')
# ON THE WORLD CLOCK (design call 2026-09-05), for the same reason as her
# verdict at the Inn: a realtime delay does not run while the phone is open
# (gotcha 3).
#
# TWENTY MINUTES, NOT THIRTY (playtest 2026-09-07): a second half-hour so
# soon after the first one reads as the gig stalling rather than as time
# passing. The two waits are deliberately no longer the same length.
step(add_game_delay(minutes=20))
# THREE TEXTS, paced by the journal's own delays (6 s and 5 s), then V's
# reply is a pick in the thread, the way the report to Wakako is.
step(add_journal('gameJournalPhoneMessage', MSG_06), in_sock='Active')
step(add_journal('gameJournalPhoneMessage', MSG_07), in_sock='Active')
step(add_journal('gameJournalPhoneMessage', MSG_08), in_sock='Active')
close_objective('obj_wait2')
open_objective('obj_reply_char')
step(add_journal('gameJournalPhoneChoiceGroup', CHOICE_GROUP_4, notify=0), in_sock='Active')
step(add_pause_journal('gameJournalPhoneChoiceEntry', CHOICE_REPLY_CHAR))
step(add_setvar('cc_g02_char_named', 1))
close_objective('obj_reply_char')

# ===========================================================================
# 12. WAKAKO IN PERSON
# ===========================================================================
open_objective('obj_wakako_met', 'pin_wakako_met')
step(add_pause_fact('cc_g02_office_reached'))
scene_at('gig02_office', ANCHOR_OFFICE, 'office_in', 'office_out')
step(add_setvar('cc_g02_wakako_met', 1))
# THE OBJECTIVE MOVES THE MOMENT SHE IS DONE (playtest 2026-09-05: it sat on
# "Talk to Wakako" until V had left, because it was queued behind the wait
# below). Only the body swap waits for the walk out.
objective_step('cc_g02_wakako_met', 'obj_wakako_met', 'obj_hit', 'pin_hit')
# "I HAVE SHARED THE DETAILS" (design call 2026-09-06): her text with the
# name, the place and the rule, sent as the objective moves to the stairs.
step(add_journal('gameJournalPhoneMessage', MSG_09), in_sock='Active')

step(add_community('Activate', CAST_REF, entry='toji'))
# OURS OFF AND THE GAME'S BACK ONLY ONCE V HAS LEFT THE PARLOR (playtest
# 2026-09-05: the swap happened in front of V as the conversation ended).
# The script sets `cc_g02_left_parlor` at the same 20 m from the parlor
# marker that Char's call fires at on the way in. Toji is on his post from
# the order itself; the staircase is a district away.
step(add_pause_fact('cc_g02_left_parlor'))
step(add_community('Deactivate', CAST_REF, entry='wakako'))
step(add_community('Reactivate', VANILLA_WAKAKO[0], entry=VANILLA_WAKAKO[1], phase=VANILLA_WAKAKO[2]))

# ===========================================================================
# 13-16. THE HIT
# ===========================================================================
# NO CONVERSATION AND NO DROP OBJECTIVE (design review 2026-09-05: Johnny
# on the stairs distracted while moving, and the trash was direction the
# objective has no business giving). Arriving opens the one objective there
# is: kill Toji without being seen.
step(add_pause_fact('cc_g02_hit_reached'))
objective_step('cc_g02_hit_reached', 'obj_hit', 'obj_toji', 'pin_toji')
step(add_setvar('cc_g02_hit_armed', 1))

# SEEN WHILE HE IS STILL ALIVE (playtest 2026-09-05): the objective drops its
# "without being seen". A side branch off the armed step waits for V being
# seen OR Toji dying, whichever is first, and only being seen first changes
# the objective. It has no output: it always resolves before the phase ends,
# because Toji's death is on the main line.
SEEN_FORK = chain[-1]
SEEN_OR = add_pause_facts([('cc_g02_spotted', 0, 'Greater'),
                           ('cc_g02_toji_dead', 0, 'Greater')], 'OR')
b.connect(SEEN_FORK, (SEEN_OR, 'In'))
STILL_ALIVE = add_condition_fact('cc_g02_toji_dead', 0, 'Equal')
b.connect((SEEN_OR, 'Out'), (STILL_ALIVE, 'In'))
chain = [(STILL_ALIVE, 'True')]
close_objective('obj_toji')
open_objective('obj_toji_loud', 'pin_toji_loud')
chain = [SEEN_FORK]

# NOBODY SPEAKS AT THE KILL (design call 2026-09-06). There was a face-to-face
# scene here, a hub where V chose what Toji heard, and a fork deciding whether
# he was still alive to hear it. All three went together: with nothing said,
# the scene had nothing in it and the fork nothing to choose.
#
# THE TRIGGER IS HIS DEATH AND NOTHING ELSE. The wait on `cc_g02_toji_met`
# went with the scene, since being within 6 m of him only ever mattered as the
# cue to start talking.
#
# `cc_g02_kill_seen` is set straight after, so it still marks the same moment.
# `cc_g02_toji_met` is still set by the script and still shown in the dev menu;
# nothing in the flow reads it now.
step(add_pause_fact('cc_g02_toji_dead'))
step(add_setvar('cc_g02_kill_seen', 1))

# OUT AGAIN. Leaving unseen is its own objective, and the script sets
# `exfil_done` when V is clear OR when V has been seen, so a firefight cannot
# strand it. Whichever kill objective is open is the one closed: the plain
# one if V was seen first, the quiet one otherwise.
DEAD_AT = chain[-1]
WAS_SEEN = add_condition_fact('cc_g02_spotted', 0, 'Greater')
b.connect(DEAD_AT, (WAS_SEEN, 'In'))
CLOSE_LOUD = add_journal('gameJournalQuestObjective', PHASE + '/obj_toji_loud',
                         notify=0)
CLOSE_QUIET = add_journal('gameJournalQuestObjective', PHASE + '/obj_toji',
                          notify=0)
b.connect((WAS_SEEN, 'True'), (CLOSE_LOUD, 'Succeeded'))
b.connect((WAS_SEEN, 'False'), (CLOSE_QUIET, 'Succeeded'))
EXFIL_OPEN = add_journal('gameJournalQuestObjective', PHASE + '/obj_exfil')
b.connect((CLOSE_LOUD, 'Out'), (EXFIL_OPEN, 'Active'))
b.connect((CLOSE_QUIET, 'Out'), (EXFIL_OPEN, 'Active'))
chain = [(EXFIL_OPEN, 'Out')]
step(add_journal('gameJournalQuestMapPin', PHASE + '/obj_exfil/pin_exfil',
                 notify=0), in_sock='Active')
step(add_setvar('cc_g02_exfil_armed', 1))

# SEEN ON THE WAY OUT, or seen before it (playtest 2026-09-05): the words
# change to "Leave the area", the same shape as the kill objective's branch.
EXFIL_FORK = chain[-1]
EXFIL_OR = add_pause_facts([('cc_g02_spotted', 0, 'Greater'),
                            ('cc_g02_exfil_done', 0, 'Greater')], 'OR')
b.connect(EXFIL_FORK, (EXFIL_OR, 'In'))
STILL_OUT = add_condition_fact('cc_g02_exfil_done', 0, 'Equal')
b.connect((EXFIL_OR, 'Out'), (STILL_OUT, 'In'))
chain = [(STILL_OUT, 'True')]
close_objective('obj_exfil')
open_objective('obj_exfil_loud', 'pin_exfil_loud')
chain = [EXFIL_FORK]

# THE CALL WAITS FOR V TO BE CLEAR, seen or not; the script sets `exfil_done`
# on distance alone. Whichever leaving objective is open is the one closed.
step(add_pause_fact('cc_g02_exfil_done'))
OUT_AT = chain[-1]
LEFT_SEEN = add_condition_fact('cc_g02_spotted', 0, 'Greater')
b.connect(OUT_AT, (LEFT_SEEN, 'In'))
CLOSE_EXFIL_LOUD = add_journal('gameJournalQuestObjective', PHASE + '/obj_exfil_loud',
                               notify=0)
CLOSE_EXFIL_QUIET = add_journal('gameJournalQuestObjective', PHASE + '/obj_exfil',
                                notify=0)
b.connect((LEFT_SEEN, 'True'), (CLOSE_EXFIL_LOUD, 'Succeeded'))
b.connect((LEFT_SEEN, 'False'), (CLOSE_EXFIL_QUIET, 'Succeeded'))

# THE TWO ENDINGS, both in her own recordings: "You entered and left like a
# ghost, V." against "You were to do this quietly. It was anything but."
# "CALL WAKAKO" is up while the call dials itself (design call 2026-09-06:
# the journal sat empty between leaving and the call).
OPEN_CALL = add_journal('gameJournalQuestObjective', PHASE + '/obj_call_wakako')
b.connect((CLOSE_EXFIL_LOUD, 'Out'), (OPEN_CALL, 'Active'))
b.connect((CLOSE_EXFIL_QUIET, 'Out'), (OPEN_CALL, 'Active'))
UNSEEN = add_condition_fact('cc_g02_spotted', 0, 'Equal')
b.connect((OPEN_CALL, 'Out'), (UNSEEN, 'In'))

chain = [(UNSEEN, 'True')]
wakako_call('cc_g02_call3', 'gig02_close_clean',
            'close_clean_in', 'close_clean_out')
CLEAN_END = chain[-1]

chain = [(UNSEEN, 'False')]
wakako_call('cc_g02_call4', 'gig02_close_loud',
            'close_loud_in', 'close_loud_out')
LOUD_END = chain[-1]

END_JOIN = add_setvar('cc_g02_closed', 1)
b.connect(CLEAN_END, (END_JOIN, 'In'))
b.connect(LOUD_END, (END_JOIN, 'In'))
chain = [(END_JOIN, 'Out')]

# The call is over: "Listen to Johnny" until his last line has played.
close_objective('obj_call_wakako')
open_objective('obj_johnny_3')
step(add_delay(3))
# TWO LAST WORDS (design call 2026-09-06): the quiet ending's line is about
# spending the fee; the loud one gets "What a fuckin' mess."
END_FORK = chain[-1]
END_UNSEEN = add_condition_fact('cc_g02_spotted', 0, 'Equal')
b.connect(END_FORK, (END_UNSEEN, 'In'))
END_QUIET = add_scene(SCENES + 'gig02_end.scene', ANCHOR_PLAYER, ['end_in'], ['end_out'])
END_LOUD = add_scene(SCENES + 'gig02_end_loud.scene', ANCHOR_PLAYER,
                     ['end_loud_in'], ['end_loud_out'])
b.connect((END_UNSEEN, 'True'), (END_QUIET, 'end_in'))
b.connect((END_UNSEEN, 'False'), (END_LOUD, 'end_loud_in'))
END_SAID = add_journal('gameJournalQuestObjective', PHASE + '/obj_johnny_3', notify=0)
b.connect((END_QUIET, 'end_out'), (END_SAID, 'Succeeded'))
b.connect((END_LOUD, 'end_loud_out'), (END_SAID, 'Succeeded'))
chain = [(END_SAID, 'Out')]
# Let the last line land before the completion banner draws over it.
step(add_delay(3))
step(add_journal_quest(QUEST, track=0), in_sock='Succeeded')
# THE CAST GOES ONLY ONCE V IS AWAY FROM THE STAIRCASE (playtest 2026-09-07:
# "once the gig is over, the tyger claws just vanish into thin air"). Toji is
# the community's, so switching the cast off here deleted his body in front of
# a player still standing at the top of the stairs; the six Claws around him
# are the script's and went at the same moment. `cc_g02_site_clear` is set by
# Gig02_Encounter.SiteClear, which is where the distance and the cap that stops
# this waiting for ever are both written down. It is set before this point in
# every run that does not park on the stairs, so nothing normally waits here at
# all.
step(add_pause_fact('cc_g02_site_clear'))
for _who in CAST:
    step(add_community('Deactivate', CAST_REF, entry=_who))

step(add_setvar('cc_g02_done', 1))
step(add_output(), in_sock='In', out_sock=None)


if __name__ == '__main__':
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    result = b.build()
    with open(OUT, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(result, fh, indent=2)
    print('wrote %s' % OUT)
    print('nodes: %d, connections: %d, handles used: %d'
          % (len(b.nodes), len(b.conns), b.next_handle))
