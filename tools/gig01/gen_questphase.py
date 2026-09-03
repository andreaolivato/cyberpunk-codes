"""Generates gig01.questphase.json, the quest graph driving Negative Balance.

The questphase chunk format cross-links sockets and connections via HandleId /
HandleRefId. This builder emits each object once (full definition at first
occurrence, HandleRefId afterwards), matching the layout of shipped questphases.
"""
import json
import os

import sys

# This gig's generators sit in tools/gig01/, and questkit is in tools/, one
# level up. Nothing else puts it on the path. See backlog.md 21.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# The graph builder lives in tools/questkit/questgraph.py. This file is the GIG:
# its journal paths, its scene anchors and its flow. ANCHOR_PLAYER comes from
# the scene builder, which is where the evidence for it is written up.
from questkit.questgraph import (                                   # noqa: F401
    b, configure, cname, jpath, Builder, STD, JRN,
    add_input, add_output, add_pause_fact, add_delay, add_game_delay,
    add_pause_journal, add_setvar, add_journal, add_scene, add_journal_quest,
    add_community,
    add_addvar, add_pause_facts, add_condition_fact, add_race2,
    add_pause_node_loaded, add_pause_phone_pickup, add_condition_phone_pickup,
    add_prefab_variant, add_toggle_component, add_call_contact,
    ANCHOR_PLAYER,
)

configure(phase_name='gig01.questphase')

# Paths and scene anchors are gig01_config.py, the file a second gig re-points.
from gig01_config import (                                          # noqa: E402
    RAW_MOD, DEPOT, QUEST_ID,
    ANCHOR_OFFICE, ANCHOR_ESTATE, ANCHOR_COYOTE, ANCHOR_BAR, ANCHOR_MAMA,
)

OUT = os.path.join(RAW_MOD, 'quest', 'gig01.questphase.json')

# The SMS thread's ids live with the journal that builds it, so the two
# cannot drift: a path typed twice is a path that gets fixed once.
from gen_journal import (                                       # noqa: E402
    NIX_CONV_PATH, NIX_MSG_PATHS, NIX_MSG_LAST_PATH,
    NIX_REPLY_GROUP, NIX_REPLY_PATH,
    BRIEF_PATH,
)

CONTACT = 'contacts/elena_ortega'
QUEST = 'quests/street_stories/' + QUEST_ID
POI = 'points_of_interest/street_stories/' + QUEST_ID

# The same string gen_scenes.SCENE_DEPOT builds, and it has to stay so: the
# lipmap is keyed by FNV1a64 of exactly this path plus the scene name.
SCENES = DEPOT + chr(92) + 'scenes' + chr(92)

# Hoshino's community, imported rather than restated: the spawner reference has
# to be the same string the area node carries and the same one the registry item
# hashes into its id, or the node addresses nothing and says so to nobody.
from gen_community import (                                         # noqa: E402
    COMMUNITY_REF, ENTRY as HOSHINO_ENTRY, PHASE as HOSHINO_PHASE,
)
# The estate detail, its own community and switched as a whole. Imported for the
# same reason as Hoshino's above: the reference here has to be the string its
# area node carries, and a phase addressing a name that does not exist is a
# quest node reaching for nothing, silently, on every load (gotcha 73).
import gen_estate_guards                                            # noqa: E402
import gen_compound_guards                                          # noqa: E402

ESTATE_REF = gen_estate_guards.build().community_ref
COMPOUND_REF = gen_compound_guards.build().community_ref


def estate_guards(action):
    """Switch the WHOLE estate detail, every post, in one node.

    No `entry`, which addresses the community rather than one of its entries and
    is what 112 of 133 sampled vanilla uses do. That is the reason the guards are
    a separate community from Hoshino: naming entries one at a time would be
    one node per entry at each of three beats, and one node carrying them all is
    a shape this project has not read off a working example.

    The three beats are the same three Hoshino needs, and for the same reasons:
    off before anything can be seen, on at the beat that wants them, off at the
    end because community state persists in saves and an active entry holding a
    dead man returns him alive on load.
    """
    # NEITHER an entry NOR a phase name, and both omissions are the same
    # decision: address the community itself and set nothing that scopes the
    # action further. That is the plain whole-community form, which is what 112
    # of 133 sampled vanilla uses write. A phase name with no entry beside it is
    # a combination this project has not read off a working example, and this is
    # not the place to find out what it means.
    step(add_community(action, ESTATE_REF))


def compound_guards(action):
    """Switch the WHOLE industrial park detail, every post, in one node.

    Same shape and the same reasoning as `estate_guards` above, and the same
    three beats. The site differs only in when they are wanted: the estate's
    window opens when Nix gives the address, this one opens when the gig starts
    and closes when V is clear of the compound.
    """
    step(add_community(action, COMPOUND_REF))


def hoshino_community(action):
    """Switch Hoshino's entry, and ONLY his.

    THE GIG PHASE TOUCHES NOTHING IT DOES NOT OWN. It named the guard test's
    entry here for one build, and when that entry was renamed the phase went on
    addressing a community entry that no longer existed, which is a quest node
    reaching for nothing, on every load, for every player. The dev entries are
    the LAB phase's business and it switches them off itself.

    A per-entry action leaves the other entries alone (bench run 14), so naming
    one entry is both correct and sufficient."""
    step(add_community(action, COMMUNITY_REF, entry=HOSHINO_ENTRY,
                       phase=HOSHINO_PHASE))

# The scene anchors are gig01_config.py, imported above, along with the
# evidence for each one. They were stated here and in gen_scenes.py, and three
# comments used to warn that the copies had to be kept in step.

# Both opening conversations (Elena's and Nix's) are holocalls, built as real
# .scene files. They replaced an SMS thread of journal messages and reply
# choices paced by this graph, which shipped in gig-01/v0.2.0 and was removed
# on 2026-08-15 once the calls were proven in game. It was carrying 26 dead
# journal entries into the archive for a path nothing activated.
#
# The technique is not lost: it is written up in docs/journal-research.md under
# "Phone messages and reply choices", and git history has the working code.


# ---- graph ----------------------------------------------------------------
chain = []
PHASE_IN = add_input()
chain.append((PHASE_IN, 'Out'))

def step(nid, in_sock='In', out_sock='Out'):
    prev_nid, prev_sock = chain[-1]
    b.connect((prev_nid, prev_sock), (nid, in_sock))
    chain.append((nid, out_sock))

# HOSHINO IS SWITCHED OFF BEFORE ANYTHING ELSE HAPPENS, and this is the first
# node in the graph for a reason.
#
# He is placed by a community this mod ships (`gen_community.py`), which replaced
# the old arrangement of a script-spawned body plus an invisible scene actor. A
# community spawns its entries ON SAVE LOAD with no quest node involved, and
# `entryActiveOnStart: 0` does not stop it: measured, gotcha 69's bench, run 14.
# So without this node he would be standing at the North Oak estate from the
# moment the mod is installed.
#
# BEFORE the wait on `cc_g01_start`, not after: the phase is entered at game
# start for everyone who has the mod, and the gig may never be started at all.
# A player who never takes this job must never meet him.
#
# The window between the save loading and this node running is not zero, and it
# has not been measured. It only matters to a player who loads a save while
# standing at the estate, which for a pre-gig save is nobody.
hoshino_community('Deactivate')
# AND THE ESTATE DETAIL, for exactly the same reason and on the same terms. It
# is a detail of armed Arasaka guards at a North Oak residence: a player who never
# takes this job must never drive past them.
estate_guards('Deactivate')
# AND THE INDUSTRIAL PARK, on the same terms. Forty-six armed guards at a
# working Arasaka site is not something a player who never took this job should
# drive past.
compound_guards('Deactivate')
step(add_pause_fact('cc_g01_start'))
step(add_setvar('cc_g01_started', 1))
# The contact is activated either way: Elena has to exist in V's phone before
# she can be the addressee of a call (HudPhoneGameController resolves the
# caller by walking JournalManager.GetContacts).
step(add_journal('gameJournalContact', CONTACT, notify=0), in_sock='Active')

# Holocall. This graph owns the handshake's two waits; the ringing itself is
# Gig01_Holocall.reds, because a mod contact has no base-game holocall phase
# to talk to. cc_g01_call_talking means "V picked up", so the scene is only
# entered once there is actually a call to put words into.
step(add_setvar('cc_g01_call_request', 1))
step(add_pause_fact('cc_g01_call_talking'))
# KEEP V ON FOOT FOR THE BEAT THAT FOLLOWS THIS CALL (backlog.md 16).
# cc_g01_vlock is the whole contract with Gig01_VehicleLock.reds: 1 means "a
# Johnny beat is coming, do not let V get into a vehicle", 0 means done. The
# script derives everything from it and decides nothing about when a window
# opens, which is why the pair below always has to be balanced.
# Opened on PICKUP rather than on the ring: a ring V never answers would
# otherwise hold the lock through the whole retry back-off, which runs to five
# minutes. Gig01_Holocall already refuses to ring at all while V is riding, so
# by the time this lands V is on foot.
step(add_setvar('cc_g01_vlock', 1))
step(add_scene(SCENES + 'gig01_elena_call.scene', ANCHOR_OFFICE,
               ['elena_call_in'], ['elena_call_out']),
     in_sock='elena_call_in', out_sock='elena_call_out')
step(add_setvar('cc_g01_call_end', 1))
step(add_pause_fact('cc_g01_call_done'))
# Comic p11: the location lands and Johnny puts a name to it. A scene since
# 2026-08-13 - it was a caption, so it could never carry audio.
#
# ANCHOR_PLAYER because the gig can be started anywhere in Night City: there
# is no fixed marker within earshot of V, and a world line plays from the
# speaker's position. The `cc_g01_johnny_cue` fact that used to stage him
# from inside Elena's call is gone with the script spawn; a scene stages its
# own actor when it starts.
step(add_setvar('cc_g01_johnny_done', 0))
step(add_scene(SCENES + 'gig01_arasaka.scene', ANCHOR_PLAYER,
               ['arasaka_in'], ['arasaka_out']),
     in_sock='arasaka_in', out_sock='arasaka_out')
step(add_setvar('cc_g01_johnny_done', 1))
# Johnny has finished, so V can ride again.
step(add_setvar('cc_g01_vlock', 0))

step(add_setvar('cc_g01_accepted', 1))
step(add_journal_quest(QUEST), in_sock='Active')
step(add_journal('gameJournalQuestPhase', QUEST + '/phase_main', notify=0), in_sock='Active')
# THE BRIEFING PARAGRAPH, new 2026-09-03. Vanilla street stories all carry
# one and this gig shipped without through six releases. It states the
# scheme in plain text, which matters more now that no spoken line can.
step(add_journal('gameJournalQuestDescription', BRIEF_PATH, notify=0),
     in_sock='Active')
step(add_journal('gameJournalQuestObjective', QUEST + '/phase_main/obj_office'), in_sock='Active')
# Map pins are journal entries in their own right: the engine only creates a
# mappin once the pin entry itself is Active. Activating just the objective
# leaves the pin dormant (this cost a full day of investigation).
step(add_journal('gameJournalQuestMapPin', QUEST + '/phase_main/obj_office/pin_office', notify=0),
     in_sock='Active')
step(add_journal('gameJournalPointOfInterestMappin', POI, notify=0), in_sock='Active')
# AND THE DETAIL GOES ON, as the objective that sends V there goes up.
#
# Earlier than the estate's equivalent relative to arrival, and deliberately so:
# the compound is in Arroyo and the player may already be near it when he takes
# the job, where the estate is a drive across the city. The community needs the
# walk or the drive to place forty-six bodies, and this is the first moment the
# gig knows he is going.
compound_guards('Activate')
step(add_setvar('cc_g01_nix_done', 0))

# --- objective progression, gated by facts (set by the encounter script)
#
# Pin entries must be activated alongside their objective: an inactive pin is
# invisible to the engine (docs/map-pins-playbook.md).
def objective_step(gate_fact, done_obj, next_obj=None, next_pin=None):
    step(add_pause_fact(gate_fact))
    step(add_journal('gameJournalQuestObjective', QUEST + '/phase_main/' + done_obj, notify=0),
         in_sock='Succeeded')
    if next_obj:
        step(add_journal('gameJournalQuestObjective', QUEST + '/phase_main/' + next_obj),
             in_sock='Active')
        if next_pin:
            step(add_journal('gameJournalQuestMapPin',
                             QUEST + '/phase_main/' + next_obj + '/' + next_pin, notify=0),
                 in_sock='Active')

# Office: arrive, then read the ledger from the terminal.
objective_step('cc_g01_office_reached', 'obj_office', 'obj_terminal', 'pin_terminal')
# Reading the ledger and unplugging from it are two separate player actions, and
# the gig used to collapse them. "Disconnect from the terminal" is what the game
# is waiting on: Johnny will not appear until IsUsingDevice goes false
# (Gig01_Encounter, after the 2026-08-12 input lock), so the journal now says so.
objective_step('cc_g01_ledger_copied', 'obj_terminal', 'obj_disconnect')

# THE OFFICE TERMINAL EXCHANGE - comic pp. 22 and 25, nine lines, and the
# longest of the beats converted from captions on 2026-08-13.
#
# objective_step is unrolled here rather than called, because the scene has to
# sit BETWEEN completing "disconnect" and offering "get clear of the compound".
# That ordering is the original intent: the conversation is what produces the
# decision to find a netrunner, so the next objective must not appear until it
# has happened. It used to be enforced by Line(38)'s CloseAfter.
step(add_pause_fact('cc_g01_terminal_left'))
step(add_journal('gameJournalQuestObjective', QUEST + '/phase_main/obj_disconnect',
                 notify=0), in_sock='Succeeded')
step(add_setvar('cc_g01_johnny_done', 0))
step(add_scene(SCENES + 'gig01_terminal.scene', ANCHOR_PLAYER,
               ['terminal_in'], ['terminal_out']),
     in_sock='terminal_in', out_sock='terminal_out')
step(add_setvar('cc_g01_terminal_done', 1))

# COMIC p25 IS BACK INSIDE gig01_terminal, so there is no scene node here.
#
# It ran BEFORE the shard and always did; what was wrong was that it ran as its
# OWN SCENE with nothing between the two - no fact gate, no player action, the
# graph stepping straight from `gig01_terminal` to `gig01_netrunner`. That was a
# leftover from 2026-08-13, when the beat was briefly moved to sit after the
# shard and the ORDER was reverted without the split being undone with it.
#
# It cost nothing while the script owned Johnny's body across both scenes. Now
# the scene owns him, so a seam is a glitch-out and a glitch-in in the middle of
# one conversation - playtest, 2026-08-14: *"There's no choice or action in the
# middle."* Merged back into build_terminal.
#
# THE STRUCTURE HE CODIFIED, and it is the shape to keep:
#
#   1. one long scene, the whole desk conversation (gig01_terminal)
#   2. look for the shard - Johnny is gone
#   3. find and read it (gig01_shard_find, then the reader)
#   4. Johnny REAPPEARS for the last lines (gig01_shard_read)
#
# Step 2 is a real gap with player action in it, so the break there is genuine
# and stays. The one between p22 and p25 never was.

# THE SHARD, comic pp. 23-24 - restored 2026-08-13.
#
# It sits AFTER the whole terminal conversation rather than inside it, which is
# the design call: "a new mission after talking with Johnny: read the shard". The
# comic puts pp. 23-24 between p22 and p25, so this moves the beat one
# conversation later - and it pays for itself, because V now goes into the Nix
# call having just learned what the ledger is FOR, which is what V's
# reworked ask on that call claims.
#
# Johnny has NO LINE here - pp. 23-24 are V alone - but he is still STANDING
# there, because cc_g01_johnny_done is not set until after p25. the playtest, having
# played the version that despawned him between beats: "Johnny must stay present
# until the last dialogue, not disappear after the first one." A hallucination
# that blinks out between two sentences of the same conversation reads as a bug,
# and silence is a normal thing for him to be doing.
#
# Three facts, three owners, no guessing about who sets what:
#   cc_g01_shard_found  script  - V is at the desk (Gig01_Encounter tick)
#   cc_g01_shard_open   HERE    - the find line is over, open the reader
#   cc_g01_shard_read   script  - the reader has been CLOSED (Gig01_Shard's wrap
#                                 on PopupsManager.OnShardReadClosed)
#
# The last one is why this waits on a fact and not on the journal entry's state.
# Reading a shard sets the entry Active the moment the popup OPENS
# (readAction.swift), so add_pause_journal(..., 'Active') would let V's p24 lines
# start while the player is still reading - under a modal popup that hides
# subtitles. The close callback is the only signal that means "he has read it".
# THE SHARD BEAT IS OUT OF THE FLOW (2026-09-02, the spliced-voices
# restructure): the terminal gives partial data only, and the mercs-do-the-
# killing reveal now lives in Nix's message. The shard scenes, the reader
# script and the sector node still ship; nothing here enters them. The chain
# that lived here (the two shard objectives, their pin, gig01_shard_find,
# gig01_shard_read) is in git history if the beat ever comes back.
step(add_delay(2))

# JOHNNY LEAVES HERE, AND NOT BEFORE. He was staged once for the terminal
# exchange and has been standing there through p25 and the whole shard beat -
# "Johnny must stay present until the last dialogue, not disappear after the
# first one" (playtest, 2026-08-13). This is that last dialogue.
step(add_setvar('cc_g01_johnny_done', 1))

step(add_journal('gameJournalQuestObjective', QUEST + '/phase_main/obj_nix'),
     in_sock='Active')
# Our own Nix contact - see gen_journal.py. The base game's `nix` is left
# alone; activating ours is what makes the calls addressable.
step(add_journal('gameJournalContact', 'contacts/cc_g01_nix', notify=0), in_sock='Active')
# Nix only calls once V is clear of the compound - reading a ledger in a guarded
# building is no time for a conversation.
#
# THIS USED TO BE A BARE add_pause_fact, and that was the bug the playtest hit
# 2026-08-12: "Get clear of the compound" stayed on screen after he was clear,
# because obj_nix was not completed until the whole Nix call had finished. He
# walked, nothing changed, and he stopped. The trace showed the fact firing on
# time and Nix's call ringing three times unanswered - the objective was telling
# him to keep walking while the game was waiting for him to pick up the phone.
#
# Completing obj_nix here and handing over to obj_nixcall makes the journal say
# what is actually being waited on. General rule: an objective must not outlive
# the thing it describes.
# Johnny's terminal exchange has to FINISH before the call, or two subtitle
# sources fight over one widget. It usually will have - the walk out is long -
# but a player who sprints could otherwise outrun it.
step(add_pause_fact('cc_g01_terminal_done'))
objective_step('cc_g01_left_compound', 'obj_nix', 'obj_nixcall')
# AND OFF AGAIN, once V IS OUT. Same argument as the estate's, and the same
# fact-shaped answer: `cc_g01_left_compound` already means he has gone.
#
# The bodies stay for the whole time he can see them, which is what the estate's
# first attempt got wrong by switching them off while he was still standing
# among them. The entries cannot simply be left on, because community state
# persists in saves and an active entry holding a dead man stands him back up
# alive on the next load.
compound_guards('Deactivate')

# ============================================================================
# NIX ON SCREEN: the mod-owned video holocall
# ============================================================================
#
# Both of Nix's conversations put him on the phone as a live picture, in a
# studio this mod opens itself, on a contact this mod invented. The base game's
# per-contact holocall phase is not involved in either direction, which is what
# keeps his ordinary small talk out of them. docs/backlog.md 3d is the whole
# account and docs/scene-playbook.md is the recipe.
#
# Every name below is read out of the contact's own holocall scene. None of
# them is guessable and a wrong one is a silent no-op.
STUDIO_MARKER = '#holocall_marker'
LIGHTS_REF = '#holocalls_studio_lighting'
CAMERA_REF = '#mama_welles_holocall_camera'
SETUP_REF = '#mama_welles_holocall_setup'
# CAMERA HEIGHT IS POSE, NOT CONTACT, which is why the setup borrowed here is
# not Nix's. The 59 studio setups share one floor spot and differ in where the
# camera sits, because each is framed on the pose its contact uses:
# #nix_holocall_camera is at z 0.75 because Nix SITS cross-legged, and
# #mama_welles_holocall_camera is at 1.52 because she STANDS. Our Nix is a
# plain spawned NPC and stands, so his own camera frames the air above his
# head. Nothing about this setup is hers except the name: the variant is
# scenery and lighting, and our own actor is what stands in it.
LIGHTS_VARIANT = 'mama_welles_holocall_lights'
SETUP_VARIANT = 'mama_welles_holocall_setup'

# OUR OWN CONTACT, which is the point. The call node takes JOURNAL PATHS, not
# CNames, so a contact this mod merged in is as valid as a base-game one, and
# a mod contact has no conversation behind it to interrupt ours.
NIX_CONTACT = 'contacts/cc_g01_nix'
PLAYER_CONTACT = 'contacts/player'

# Seconds. Every one of these is a cap on something that would otherwise be
# able to wait for ever (docs/gotchas.md 22).
STUDIO_SECONDS = 20      # for the studio sector to stream in after we ask for it
GATE_SECONDS = 90        # for a good moment to ring; after this, ring anyway
RING_SECONDS = 10        # the phone itself gives up at 8, so this outlasts it
RETRY_SECONDS = 30       # between one missed ring and the next
RING_TRIES = 5           # missed rings before the video route is abandoned


def nix_call(p, holo_scene, plain_scene, entries, exits, incoming):
    r"""One Nix call: on screen if the studio cooperates, on the phone if not.

    ------------------------------------------------------------------------
    WHAT THE PLAYER SEES
    ------------------------------------------------------------------------
    His phone rings, he answers, and Nix is there as a live picture speaking
    this gig's lines. If he declines, or lets it ring out, Nix calls back
    half a minute later, and again, and the call is the same one when he does
    take it. Nothing about missing it can cost him the gig.

    ------------------------------------------------------------------------
    THE FOUR THINGS THAT CANNOT BE ALLOWED TO HAPPEN, and where each is handled
    ------------------------------------------------------------------------
    A quest phase has no error path. A node that waits on something that never
    arrives is a gig that stops there, silently, half an hour in, with no log
    line and nothing on screen to say why (docs/gotchas.md 22 and 54). Every
    wait below is therefore raced against a clock.

    1. THE CALL IS NEVER ANSWERED. The waits that report a pick-up do not
       report a ring-out, so on their own they would wait for ever. They are
       raced against RING_SECONDS, and a missed ring goes round the loop.
    2. THE CALL IS DECLINED. Same loop, and it is the same code path, because
       the branch is not decided by which wait woke up. Declining reports
       Rejected and then reports Talking about a second and a half later
       (docs/gotchas.md 10j), so the graph re-reads the phone at the moment it
       needs the answer instead of trusting the event.
    3. THE STUDIO NEVER ARRIVES. It is a Quest sector and showing its prefab
       variant only ASKS for it. Raced against STUDIO_SECONDS, and if it loses,
       the whole beat falls back to the audio call that has shipped since 1.2.0
       - the same words, the same voice, a contact portrait instead of a face.
    4. THE PHONE IS NEVER IN A STATE TO RING. Raced against GATE_SECONDS, after
       which it rings regardless. A call refused for ever is worse than a call
       placed at an awkward moment.

    The audio fallback is the floor under all of it, and it is deliberately the
    OLD route, unchanged: `Gig01_Holocall.reds` rings it, with the back-off
    ladder and the guards that three playtests bought. It never gives up.

    ------------------------------------------------------------------------
    THE SHAPE
    ------------------------------------------------------------------------
    ::

        show the two prefab variants          the studio is asked for
        wait for the camera node to load  ----timeout----> AUDIO FALLBACK
        switch the camera on
      ,-wait for a moment when it may ring    (capped, then ring anyway)
      | ring
      | wait for a pick-up  or  a decline  or  RING_SECONDS
      | re-read the phone: is it actually answered?
      |     no  --> hang up, count it, and either loop or give up
      `-----'         after RING_TRIES ------> AUDIO FALLBACK
            yes --> connect, speak, hang up, put the studio away

    An outgoing call (V ringing Nix) has no pick-up to wait for: vanilla's own
    player-calling path plays a dial tone for two to four seconds and connects
    itself, so `incoming=False` replaces the whole ring loop with a delay. That
    also means the outgoing call has no way to strand at all.
    """
    global chain
    cur = chain[-1]

    def go(nid, in_sock='In', out_sock='Out'):
        """Append a node to this block's chain."""
        nonlocal cur
        b.connect(cur, (nid, in_sock))
        cur = (nid, out_sock)
        return nid

    def mark(n):
        """Leave a number behind, because a stopped phase says nothing.

        A quest phase has a POSITION and nothing reports it. A block parked
        mid-chain looks exactly like a beat that never started: no error, no log
        line, and the fact that was supposed to trigger it sitting at 1. This is
        the only way to find out WHERE it stopped, and it cost an afternoon to
        learn (docs/gotchas.md 54).
        """
        go(add_setvar(p + '_step', n))

    caller = NIX_CONTACT if incoming else PLAYER_CONTACT
    addressee = PLAYER_CONTACT if incoming else NIX_CONTACT

    # THE FACT THE GAME WRITES WHEN THE PHONE CHANGES STATE, and it is how this
    # block knows the player answered. PhoneSystem.GetPhoneCallFactName builds
    # "phonecall_" + caller + "_with_" + addressee from the CONTACT IDS, both
    # lowercased, so it is derived here rather than typed out: the two would
    # drift the first time a contact was renamed.
    #
    #   Ended 0    Initializing 1    Talking 2    Rejected 3
    phone_fact = ('phonecall_' + caller.split('/')[-1] + '_with_'
                  + addressee.split('/')[-1]).lower()

    def call_node(phase, rejectable=False):
        # applyPhoneRestriction OFF, unlike vanilla, which sets it on every one
        # of its own call nodes. This mod's calls have never carried a phone
        # restriction (Gig01_Holocall sets isPlayerTriggered false on purpose)
        # and none has ever needed one. It buys nothing here: it is not what
        # blocks the skip on a video call, measured 2026-08-23, docs/gotchas.md
        # 52. And a restriction that is applied and then not released because
        # the call was abandoned is a phone that stays broken for the rest of
        # the save.
        return add_call_contact(caller, addressee, phase, rejectable=rejectable,
                                restrict=False)

    # -- every latch this block sets, cleared before it is read ---------------
    # A fact outlives the node that wrote it and a quest phase's progress is
    # saved, so a value left behind by an earlier call is a wait that returns on
    # its first tick.
    go(add_setvar(p + '_step', 0))
    go(add_setvar(p + '_rings', 0))
    go(add_setvar(p + '_video', 0))
    go(add_setvar(p + '_claim', 0))
    go(add_setvar('cc_g01_ringing', 0))
    mark(1)

    # -- 1. ask for the studio, and wait for it to actually be there ----------
    #
    # Showing a prefab variant is a request, not an arrival: the holocall studio
    # is a `category: Quest` sector with no streaming box, and standing 2.8 m
    # from the spot is not enough to bring it in. Switching the camera on before
    # it lands is a silent no-op against an entity that does not exist yet, and
    # the result is a call with a black picture.
    #
    # Vanilla waits on the camera node itself rather than guessing a delay
    # (`nix_holocall.scene` node 331) and then waits for ever. We race it.
    go(add_prefab_variant(LIGHTS_REF, LIGHTS_VARIANT, True))
    go(add_prefab_variant(SETUP_REF, SETUP_VARIANT, True))
    mark(2)
    studio = add_race2(cur,
                       (add_pause_node_loaded(CAMERA_REF), 'In', 'Out'),
                       (add_delay(STUDIO_SECONDS), 'In', 'Out'),
                       p + '_claim')

    # -- THE AUDIO FALLBACK, reachable from here and from a call nobody answers
    #
    # Everything below this point is the route that has shipped since 1.2.0,
    # untouched. The graph sets <prefix>_request, Gig01_Holocall.reds rings the
    # phone with its own guards and its own back-off ladder, and the plain scene
    # plays behind a contact portrait. It cannot strand: that ladder never gives
    # up, and Elena's call, the only way into the gig, has used it since 1.0.
    fallback = add_setvar(p + '_video', 0)
    b.connect((studio, 'False'), (fallback, 'In'))
    cur = (fallback, 'Out')
    go(add_setvar(p + '_videofail', 1))
    go(add_toggle_component(CAMERA_REF, 'RenderToTextureCamera', False))
    go(add_prefab_variant(SETUP_REF, SETUP_VARIANT, False))
    go(add_prefab_variant(LIGHTS_REF, LIGHTS_VARIANT, False))
    go(add_setvar('cc_g01_ring_want', 0))
    go(add_setvar('cc_g01_ringing', 0))
    mark(20)
    go(add_setvar(p + '_request', 1))
    go(add_pause_fact(p + '_talking'))
    # V stays on foot from here: Johnny has a beat after this call and he is
    # staged where V is standing. See the note by Elena's call.
    go(add_setvar('cc_g01_vlock', 1))
    go(add_scene(SCENES + plain_scene, ANCHOR_OFFICE, entries, exits),
       in_sock=entries[0], out_sock=exits[0])
    go(add_setvar(p + '_end', 1))
    go(add_pause_fact(p + '_done'))
    mark(21)
    audio_tail = cur

    # -- 2. the studio is there: light it and point the camera at the spot ----
    cur = (studio, 'True')
    mark(3)
    go(add_toggle_component(CAMERA_REF, 'RenderToTextureCamera', True))
    go(add_setvar(p + '_video', 1))
    go(add_setvar('cc_g01_ring_want', 1))

    # -- 3. wait for a moment when the phone may ring -------------------------
    #
    # cc_g01_ring_ok is Gig01_Holocall.reds answering three questions this graph
    # cannot ask: is the phone usable at all, is a fast travel in progress, and
    # is V on a bike. All three are playtest fixes and all three would be lost
    # by moving the ring into the graph, so the script keeps answering and the
    # graph waits for the answer. holo_setup_active is the base game's own
    # mutex on the studio: it is read and never written, so nothing this mod
    # does can leave a vanilla holocall unable to stage.
    #
    # This node is also the LOOP TARGET. Vanilla's holocall phases are loops
    # whose first pause node is fed from more than one place, and fan-in on a
    # pause node is ordinary (docs/gotchas.md 51).
    ring_top = add_setvar(p + '_claim', 0)
    go(ring_top)
    gate = add_race2(cur,
                     (add_pause_facts([('cc_g01_ring_ok', 0, 'Greater'),
                                       ('holo_setup_active', 1, 'Less')]), 'In', 'Out'),
                     (add_delay(GATE_SECONDS), 'In', 'Out'),
                     p + '_claim')
    # Both ways out do the same thing. The cap is not a different outcome, it is
    # the promise that waiting for a good moment cannot become waiting for ever.
    armed = add_setvar(p + '_claim', 0)
    b.connect((gate, 'True'), (armed, 'In'))
    b.connect((gate, 'False'), (armed, 'In'))
    cur = (armed, 'Out')
    mark(4)

    if incoming:
        # -- 4. ring, and find out what the player did ------------------------
        # WHILE THIS IS 1 THE PHONE IS ACTUALLY RINGING, and Gig01_Holocall
        # blocks fast travel for exactly that long. The script used to work it
        # out from its own state machine and got it wrong in a way that broke
        # fast travel for the rest of the save: "ringing" was read as the whole
        # state, which is the ring PLUS the entire back-off, so five-minute
        # stretches were locked for eight seconds of ringing. The graph knows
        # precisely, so it says so (docs/gotchas.md 24).
        # CLEAR THE GAME'S OWN CALL FACT FIRST. It persists, and it persists
        # at Talking once a call has been answered, so a ring placed without
        # clearing it finds the answer already reported and connects itself
        # before the phone has rung. Gig01_Holocall does the same thing in the
        # same place and for the same reason.
        go(add_setvar(phone_fact, 0))
        go(add_setvar('cc_g01_ringing', 1))
        go(call_node('IncomingCall', rejectable=True))
        # WAIT ON THE FACT, NOT ON questPhonePickUp_ConditionType.
        #
        # Measured in play 2026-08-23, and it is the one thing that did not
        # work: the player tapped T, the game wrote
        # `phonecall_cc_g01_nix_with_player = 2` on time, and the pick-up
        # condition never completed. The call sat connected and silent for six
        # seconds and the game dropped it. That is vanilla's own node, read out
        # of its own scene with the fields checked against the SDK, and for a
        # call a mod issues from a quest phase it reports nothing. See
        # docs/gotchas.md 58.
        #
        # The fact is written by PhoneSystem itself, it is what this mod's
        # script has watched since 1.0, and it is visible in the dev menu's
        # trace, which is how this was found. Greater than 1 means Talking or
        # Rejected: the player did something.
        answer = add_race2(cur,
                           (add_pause_fact(phone_fact, 1, 'Greater'), 'In', 'Out'),
                           (add_delay(RING_SECONDS), 'In', 'Out'),
                           p + '_claim')
        # RE-READ. Which wait woke up is not the question; what the phone says
        # right now is. A declined call reports Rejected and then reports
        # Talking about a second and a half later, so a branch that trusted the
        # event would take the wrong one about half the time
        # (docs/gotchas.md 10j). Reading it HERE, in the same tick the race
        # resolved, is what makes that safe: the value is still Rejected.
        # Vanilla asks the same question in the same place with its own node,
        # `nix_holocall.scene` node 444.
        picked = add_condition_fact(phone_fact, 2, 'Equal')
        ring_off = add_setvar('cc_g01_ringing', 0)
        b.connect((answer, 'True'), (ring_off, 'In'))
        b.connect((answer, 'False'), (ring_off, 'In'))
        b.connect((ring_off, 'Out'), (picked, 'In'))

        # NOT ANSWERED: take the chrome down ourselves and go round again.
        #
        # Ending it here rather than leaving it to the phone's own 8 s timeout
        # is what makes a decline behave. Vanilla's per-contact phase reacts to
        # Rejected by ending the call, and because this mod never did, the
        # banner stayed up, still answerable, and the key coming back up
        # answered it.
        cur = (picked, 'False')
        go(call_node('EndCall'))
        mark(5)
        go(add_addvar(p + '_rings', 1))
        enough = add_condition_fact(p + '_rings', RING_TRIES, 'GreaterOrEqual')
        b.connect(cur, (enough, 'In'))
        # Rung out or waved away enough times that something is probably wrong
        # with the video route rather than with the player's timing. Fall back
        # to the phone call, which rings by a completely different mechanism.
        b.connect((enough, 'True'), (fallback, 'In'))
        backoff = add_delay(RETRY_SECONDS)
        b.connect((enough, 'False'), (backoff, 'In'))
        b.connect((backoff, 'Out'), (ring_top, 'In'))

        cur = (picked, 'True')
    else:
        # V IS DIALLING, so there is nothing to answer and nothing to miss.
        # Vanilla's player-calling path rings the initiation tone and connects
        # itself two to four seconds later; this is that, at a fixed length.
        go(add_setvar('cc_g01_ringing', 1))
        go(call_node('IncomingCall'))
        go(add_delay(2))
        go(add_setvar('cc_g01_ringing', 0))

    # -- 5. connect, speak, hang up -------------------------------------------
    mark(6)
    go(call_node('StartCall'))
    # Written for the dev menu's trace rather than for anything that reads them.
    # The audio route sets the same pair from the script, so a trace of a video
    # call and a trace of an audio one line up beat for beat.
    go(add_setvar(p + '_answered', 1))
    go(add_setvar(p + '_talking', 1))
    go(add_setvar('cc_g01_ring_want', 0))
    # Same window as the audio branch: V stays on foot for Johnny's beat.
    go(add_setvar('cc_g01_vlock', 1))
    # THE SCENE IS ANCHORED ON THE STUDIO SPOT, not on the office. Its actor
    # spawns at offset (0, 0, 0) from this marker, so the marker IS where Nix
    # stands. #holocall_marker lives in always_loaded_2, so it resolves from
    # anywhere in the city.
    go(add_scene(SCENES + holo_scene, STUDIO_MARKER, entries, exits),
       in_sock=entries[0], out_sock=exits[0])
    mark(7)
    go(add_setvar(p + '_end', 1))
    go(call_node('EndCall'))
    go(add_toggle_component(CAMERA_REF, 'RenderToTextureCamera', False))
    go(add_prefab_variant(SETUP_REF, SETUP_VARIANT, False))
    go(add_prefab_variant(LIGHTS_REF, LIGHTS_VARIANT, False))
    # <prefix>_done is read by Gig01_Encounter (the ledger goes to Nix on
    # nixbrief_done) and by the rest of this graph, so the video branch has to
    # write it. On the audio branch the script does.
    go(add_setvar(p + '_done', 1))

    # -- both ways out of the beat meet here ----------------------------------
    #
    # cc_g01_ringing is cleared on every path above already. Clearing it once
    # more here is the belt on the braces, because it is the only fact this
    # block writes that another system READS as a reason to take something away
    # from the player: a stale 1 is fast travel unavailable for the rest of the
    # save, which is the hardest kind of report to act on (docs/gotchas.md 24).
    go(add_setvar('cc_g01_ringing', 0))
    join = add_setvar(p + '_step', 9)
    b.connect(cur, (join, 'In'))
    b.connect(audio_tail, (join, 'In'))
    chain.append((join, 'Out'))


# CALL 1 - comic pp. 26-27. V CALLS NIX and hands over the ledger.
# Player-initiated: Gig01_Holocall swaps caller/addressee for this one, so the
# phone dials instead of ringing. Nix has no reason to call about a ledger he
# does not know exists (playtest, 2026-08-12). This is the
# handover the gig used to do off-screen: it read a kill ledger and then took a
# callback from a netrunner V had never spoken to.
# THIS CALL LEADS TO A BEAT TOO, which is easy to miss because the beat is not
# the next node: the send sets cc_g01_ledger_sent from Gig01_Encounter first.
# That is three scripted beats 1.6 s apart, so the gap is seconds rather than
# anything a player waits through, and gig01_legend follows it.
#
# Playtest 2026-08-21: *"after the call start, I can mount the bike, so the
# second block is not on."* Correct, because this pair was missing. The lock is
# opened inside nix_call, at the moment the call connects, not here, because
# from here to a call the player may not answer for minutes is a long time to
# be told he cannot get on his bike.
nix_call('cc_g01_nixbrief', 'gig01_nix_brief_holo.scene', 'gig01_nix_brief.scene',
         ['nix_brief_in'], ['nix_brief_out'], incoming=False)

# The send + the payment, then Johnny's p28 beat while Nix works. Both are
# script-driven (Gig01_Encounter): the transfer is an on-screen toast in the
# comic, not a spoken line, and Johnny needs staging.
objective_step('cc_g01_ledger_sent', 'obj_nixcall', 'obj_nixwait')
# THE CROSSWALK BEAT IS OUT OF THE FLOW (2026-09-03). gig01_legend was V
# asking Johnny what being a legend costs while Nix worked, and playtest
# rejected it in this position: with the callback gone the beat lands in a
# gap where the player is simply waiting for a text, and neither line has
# anything to do with the gig. The scene still builds and nothing enters it,
# the same standing gig01_graves and gig01_malware now have.
step(add_setvar('cc_g01_vlock', 0))

# NIX NEEDS TIME TO ACTUALLY DIG. Nexus 1.0.0, 2026-08-15: *"I know Nix is a
# slick operator but he'd replied almost before I'd pressed 'send'."*
#
# He was right, and it was not the message delays - USE_SMS_THREAD is False, so
# the thread and its per-message `delay` fields are not in the shipped build at
# all. It was this graph: ledger sent -> gig01_legend.scene -> ring, with
# nothing in between. "Wait for Nix to call back" lasted exactly as long as one
# short crosswalk conversation, and a man who cracks a corpo ledger and names
# the fixer inside thirty seconds is not a fixer, he is a search box.
#
# FOUR IN-GAME HOURS, on the world clock (see add_game_delay for why not
# realtime). Night City's clock runs far faster than real time, so this is a
# handful of real minutes - long enough to read as work, short enough that
# nobody puts the controller down waiting for it. It is also still night when it
# lands, which the comic wants.
#
# Johnny does NOT stand around through this: he is the legend scene's own actor
# and leaves with it. cc_g01_johnny_legend is set above and READ BY NOTHING -
# the fact is a leftover from when the script owned his body, and the intent it
# recorded ("keep him there through Nix's call") stopped being implemented when
# the beat became a scene. Do not resurrect it here; a Johnny trailing V for two
# in-game hours is a different feature and a worse one.
# FOUR HOURS, not two, since 2026-09-03: on the call Nix says "should take
# me, I dunno... four, five hours?" in his own recorded voice, so the wait
# has to match the words the player just heard. Night City's clock runs
# far faster than real time, so this is still a handful of real minutes.
step(add_game_delay(hours=4))

# ===================== NIX'S FINDINGS ARRIVE AS A TEXT MESSAGE ==============
#
# REPLACED THE SECOND HOLOCALL, 2026-09-03, and the reason is the voice route
# rather than the phone. V, Johnny and Nix speak only in recordings the game
# already shipped, and no recording of Nix explains an insurance-kill scheme,
# so the one beat that MUST state the plot cannot be a conversation. In the
# base game a fixer's findings arrive as text and V's replies are unvoiced;
# this is that shape. What used to be `nix_call('cc_g01_nixcall', ...)` - the
# video studio, the ring loop, the five retries, the audio fallback - is gone
# with it, and so is the beat that hung off its end.
#
# The thread is four messages and one reply, built in gen_journal.py, paced by
# each message's own `delay` (a graph timer stalls while the phone menu is
# open, gotchas 3).
#
# THE REPLY IS THE READ RECEIPT. A message going Active means it was
# DELIVERED, which happens while V is driving; the gig must not move on until
# the player has actually opened the thread. Pausing on the choice ENTRY is
# the only signal that means "read", and it is why the thread ends with a
# button instead of trailing off.
step(add_journal('gameJournalPhoneConversation', NIX_CONV_PATH, notify=0),
     in_sock='Active')
# The fact the objective flip waits on: set once the whole thread has been
# pushed, so 'wait for the message' cannot complete before it exists.
for _path in NIX_MSG_PATHS:
    step(add_journal('gameJournalPhoneMessage', _path), in_sock='Active')
# "Wait for Nix's message" is done the moment the thread is on the phone;
# what the player owes now is a read, so the objective says that.
step(add_setvar('cc_g01_nixmsg_sent', 1))
objective_step('cc_g01_nixmsg_sent', 'obj_nixwait', 'obj_nixread')
step(add_journal('gameJournalPhoneChoiceGroup',
                 NIX_CONV_PATH + '/' + NIX_REPLY_GROUP, notify=0),
     in_sock='Active')
step(add_pause_journal('gameJournalPhoneChoiceEntry', NIX_REPLY_PATH))
# THE FEE GOES OUT HERE, and the order is the design call: the location
# lands, V thanks him, THEN the money moves. It used to leave V's account
# during the send, before Nix had read a line. Gig01_Encounter does the
# transaction on this fact and answers with cc_g01_nix_paid; nothing of ours
# is drawn over it, because changing the player's money is what makes the
# game's own eddies counter move.
step(add_setvar('cc_g01_pay_nix', 1))
step(add_pause_fact('cc_g01_nix_paid'))
# ...and Nix throws in the malware, which is where the estate objective's
# upload and the gig's payout finally come from.
step(add_journal('gameJournalPhoneMessage', NIX_MSG_LAST_PATH), in_sock='Active')
step(add_journal('gameJournalQuestObjective', QUEST + '/phase_main/obj_nixread',
                 notify=0), in_sock='Succeeded')
step(add_setvar('cc_g01_nix_done', 1))
# The vehicle lock is released here for the same reason it always was: the
# beat that needed V on foot is over. Nothing after this stages Johnny until
# the estate.
step(add_setvar('cc_g01_vlock', 0))

# Estate: travel, kill Hoshino, upload the malware from his own terminal.
objective_step('cc_g01_nix_done', 'obj_nixread', 'obj_estate', 'pin_estate')
# AND NOW HE EXISTS. Switched on as the objective goes up rather than on arrival,
# so the community has the whole drive across the city to place him: a man who
# streams in while V is already in the room is a man who appears out of nothing.
hoshino_community('Activate')
# THE DETAIL COMES ON WITH HIM, and on the same argument: the drive across the
# city is the community's time to place the bodies. This replaced a script
# spawn that asked for twenty-five entities as V arrived and delivered them in a
# callback chain behind him, which is the "they simply weren't there, then they
# appeared" report the chain was built to answer.
estate_guards('Activate')
# NO PIN ON obj_wayin, and it is the only objective in the gig with a marker but
# no pin entry. Gig01_Encounter registers a runtime mappin instead and walks it
# up the hill; a journal pin cannot be hidden once its objective is active, which
# is what put six markers on screen at once. It also takes the marker down.
objective_step('cc_g01_estate_reached', 'obj_estate', 'obj_wayin')
objective_step('cc_g01_wayin_reached', 'obj_wayin', 'obj_hoshino', 'pin_hoshino')
# Hoshino's exchange, as a real scene with a choice of opening line. The
# encounter script sets cc_g01_hoshino_met when V gets close to him AND when he
# dies, so a kill from across the garden cannot leave this graph waiting on a
# conversation that will never happen.
step(add_pause_fact('cc_g01_hoshino_met'))

# ...AND SKIP HIS CONVERSATION IF HE IS ALREADY DEAD.
#
# playtest, 2026-08-15: *"If I kill hoshino BEFORE he speaks, I still get the
# speaking."* Exactly so - the encounter script sets cc_g01_hoshino_met on a
# ranged kill as an anti-stall (otherwise this pause waits forever for a
# conversation that can no longer happen), and the graph then walked straight
# into the scene and had a corpse deliver "Mmm? You lost, merc?"
#
# The anti-stall is right and stays. What was missing is that reaching this
# point says nothing about WHY: "V is in front of him" and "he is dead" both
# arrive here. So ask.
#
# He offered two fixes and this is the first: skip the beat. The other - make
# Hoshino untargetable until the conversation ends - takes a shot the player
# lined up and refuses it, which is worse than losing two lines of dialogue the
# kill has already made irrelevant.
#
# THE FORK IS ON cc_g01_hoshino_dead, and the two branches rejoin at the
# objective node below, NOT at the scene: `gig01_hoshino.scene` keeps exactly
# one node. Two nodes for one scene is what crashed the game on load in August,
# and a scene node cannot be entered from two places either.
HOSHINO_FORK = chain[-1]
HOSHINO_ALIVE = add_pause_fact('cc_g01_hoshino_dead', 0, 'Equal')
HOSHINO_DEAD = add_pause_fact('cc_g01_hoshino_dead', 1, 'Equal')
b.connect(HOSHINO_FORK, (HOSHINO_ALIVE, 'In'))
b.connect(HOSHINO_FORK, (HOSHINO_DEAD, 'In'))

HOSHINO_TALK = add_scene(SCENES + 'gig01_hoshino.scene', ANCHOR_ESTATE,
                         ['hoshino_in'], ['hoshino_out'])
b.connect((HOSHINO_ALIVE, 'Out'), (HOSHINO_TALK, 'hoshino_in'))

# Rejoin. Everything from here is identical either way - and on the dead branch
# obj_kill is activated and its pause passes at once, so the player is credited
# with the kill instead of the objective being silently skipped.
HOSHINO_JOIN = add_journal('gameJournalQuestObjective',
                           QUEST + '/phase_main/obj_hoshino', notify=0)
# HE TURNS ON V WHEN THE CONVERSATION ENDS, and this fact is how.
#
# ON THE TALKED BRANCH ONLY. The dead branch rejoins below without passing
# through here, which is correct: a corpse does not need an attitude, and the
# kill scene reads cc_g01_hoshino_dead rather than this.
#
# THIS WAS TRIED ONCE AND WITHDRAWN, and the reason it failed then is the
# reason it works now. The design called for it on 2026-08-14, it was built as
# an attitude flip on this fact, and it did nothing observable, because
# `enableSensesOnStart: false` on his record leaves him hostile and never
# looking. The playtest verdict: *"Still doesn't attack but it's ok let's not
# complicate things."* The comment that replaced it said the only way to make
# him fight would be turning senses on, which is what kept him peaceful through
# his own conversation, and to leave it alone.
#
# That was right while the encounter script forced him hostile on every tick,
# because senses on at any point meant senses on during the conversation.
# That force is gone (docs/backlog.md 22), so the flip is now a single event at
# a moment the graph chooses, and turning his senses on AFTER his last line
# cannot reach back into a scene that has finished.
#
# The flip itself is in Gig01_Encounter.reds, which reads this fact alongside
# his health. Both do the same two things: attitude to V hostile, senses on.
HOSHINO_TALKED = add_setvar('cc_g01_hoshino_talked', 1)
b.connect((HOSHINO_TALK, 'hoshino_out'), (HOSHINO_TALKED, 'In'))
b.connect((HOSHINO_TALKED, 'Out'), (HOSHINO_JOIN, 'Succeeded'))
b.connect((HOSHINO_DEAD, 'Out'), (HOSHINO_JOIN, 'Succeeded'))
chain.append((HOSHINO_JOIN, 'Out'))

# "Find Hoshino" is done - succeeded by HOSHINO_JOIN above, which is where the
# two branches meet. Say what the gig wants next instead of leaving a completed
# objective on screen until he dies.
step(add_journal('gameJournalQuestObjective', QUEST + '/phase_main/obj_kill'),
     in_sock='Active')
# Over the body, comic p45: V's "Ledger's closed." and Johnny's "They always
# think names beat bullets." Both were captions; both are this scene now.
# Unrolled so the scene plays before the next objective is offered.
step(add_pause_fact('cc_g01_hoshino_dead'))
step(add_setvar('cc_g01_johnny_done', 0))
step(add_scene(SCENES + 'gig01_kill.scene', ANCHOR_PLAYER,
               ['kill_in'], ['kill_out']),
     in_sock='kill_in', out_sock='kill_out')
step(add_setvar('cc_g01_johnny_done', 1))
step(add_journal('gameJournalQuestObjective', QUEST + '/phase_main/obj_kill',
                 notify=0), in_sock='Succeeded')
step(add_journal('gameJournalQuestObjective', QUEST + '/phase_main/obj_malware'),
     in_sock='Active')
step(add_journal('gameJournalQuestMapPin',
                 QUEST + '/phase_main/obj_malware/pin_malware', notify=0),
     in_sock='Active')

objective_step('cc_g01_malware_done', 'obj_malware', 'obj_escape')
# AND NOW HIS ENTRY GOES OFF. NOT EARLIER, AND THE REASON IS THE BODY.
#
# `Deactivate` removes the community's body, corpse included. It sat right after
# the pause on his death for one build, and playtest, 2026-08-24 reported
# exactly what that does: *"it's a bit weird that the body disappeared"*. He was
# shot and then deleted in front of the player, before the scene over his body
# had finished.
#
# It cannot be dropped altogether either, because community state persists in
# saves: an entry left active with a dead man in it puts him back at his spot,
# alive, for anyone who quits after the kill and loads that save again.
#
# So it happens here, after the malware is uploaded. By then V has walked away
# from the body to the terminal and the kill scene is long finished, and the
# gig has nothing further to do with him. Anyone reloading from here on gets an
# entry that is already off.
hoshino_community('Deactivate')
# ...AND THE TERMINAL EXCHANGE, restored the same day it was cut and recast
# with it. What was rejected was the LINE (V grieving, Johnny silent), not
# the beat: the design call is that the upload wants two voices on it, the
# job closed and the machine outliving the man.
#
# cc_g01_malware_talk is not cc_g01_malware_done: the upload finishes while V
# is still in the device zoom, and staging an actor on a player locked in a
# UI is what soft-locked the office beat once. Gig01_Encounter sets this one
# only when IsUsingDevice goes false, so the eddies (which land on
# malware_done) arrive while he is still at the screen and the conversation
# happens as he steps away.
step(add_pause_fact('cc_g01_malware_talk'))
step(add_setvar('cc_g01_johnny_done', 0))
step(add_scene(SCENES + 'gig01_malware.scene', ANCHOR_PLAYER,
               ['malware_in'], ['malware_out']),
     in_sock='malware_in', out_sock='malware_out')
step(add_setvar('cc_g01_johnny_done', 1))
objective_step('cc_g01_escaped', 'obj_escape', 'obj_epilogue', 'pin_epilogue')
# AND NOW THE DETAIL GOES OFF, once V IS GONE. Not with Hoshino's entry.
#
# Playtest 2026-08-25 asked the obvious question: why would the guards vanish,
# the bodies should stay. That is right, and the earlier placement was wrong. V
# fights his way through the whole detail and the corpses are the evidence of it;
# deleting them while he is still standing among them is the same fault that put
# Hoshino's body out from under the player in August, once per guard.
#
# But the entries cannot simply be left on. Community state persists in saves, so
# an active entry holding a dead man stands him back up alive on the next load,
# and a hostile Arasaka detail would garrison a North Oak residence for the
# rest of the save.
#
# `cc_g01_escaped` is what resolves it, and it already means exactly the right
# thing: the upload is done and V is 160 m clear. He has left, the corpses stayed
# for the whole time he could see them, and the entries go off behind him. Anyone
# reloading from here gets a clean estate.
estate_guards('Deactivate')
# Arriving inside the bar only opens the conversation; the gig closes when Mama
# Welles has actually been spoken to (last epilogue line sets cc_g01_mama_talked).
# Arriving and reaching her are two things. cc_g01_at_coyote used to be set
# only when V was already in front of Mama, so "Talk to Mama Welles" appeared
# and the conversation started in the same breath - the objective was never
# readable. Arrival now fires on walking into the pub; the scene waits for her.
objective_step('cc_g01_at_coyote', 'obj_epilogue', 'obj_mama')
# A questVoicesetManagerNodeDefinition SAT HERE AND IT STALLED THE GIG.
# Removed 2026-08-15, same evening it was added. See docs/backlog.md 7d - the
# node never handed control on, so the graph never reached the pause below and
# the epilogue simply never played. Do not re-add it in this chain.
step(add_pause_fact('cc_g01_mama_reached'))
# The epilogue conversation with Mama Welles. It ends on V saying he is getting
# a drink; the encounter script sets cc_g01_mama_talked when the scene exits.
#
# PLAY IT, OR SKIP IT. See docs/backlog.md 7d and 19.
#
# `gig01_epilogue` TAKES the real Mama Welles as its actor, which is what stops
# her ordinary bar conversation - a quest scene owns the actor it acquires. Yet
# nothing in it spawns anybody, so entering it when she is not in the bar would
# leave the scene holding an actor that never acquired, which is what crashed
# the game at scene teardown in August. That is the whole reason this fork
# exists, and it is why the fork stays even though the branch it protects
# should now be unreachable.
#
# THE SECOND BRANCH USED TO PLAY A STAND-IN and now plays nothing: it goes
# straight to the fan-in, so the gig moves on to the bar without the epilogue.
# The stand-in, and the script that spawned our own Mama Welles for it, were
# deleted on 2026-08-18. Gig01_Start now waits for sq018 (Heroes) before the gig
# begins, and that is the quest that puts Mama in the bar as well as unlocking
# its door, so the absent case should not arise. An ending missing one
# conversation beats a crash, and it beats carrying a whole second scene, a
# spawner and a duplicate NPC for a case nobody should reach.
#
# THE FACT IS TRI-STATE, and deliberately: 0 unknown, 1 she is here, 2 she is
# not. Two pause nodes hang off the same socket, one per answer, and neither can
# fire until Gig01_Encounter has actually looked. A plain 0/1 fact would have the
# "absent" branch waiting on `== 0`, which is true for every player from the
# moment the save loads, so the skip would fire before the probe ever ran.
#
# Fan-out here, fan-in below. Both are shapes vanilla uses.
MAMA_FORK = chain[-1]
MAMA_HERE = add_pause_fact('cc_g01_mama_present', 1, 'Equal')
MAMA_GONE = add_pause_fact('cc_g01_mama_present', 2, 'Equal')
b.connect(MAMA_FORK, (MAMA_HERE, 'In'))
b.connect(MAMA_FORK, (MAMA_GONE, 'In'))

EPILOGUE_NID = add_scene(SCENES + 'gig01_epilogue.scene', ANCHOR_MAMA,
                         ['epilogue_in'], ['epilogue_out'])
b.connect((MAMA_HERE, 'Out'), (EPILOGUE_NID, 'epilogue_in'))

# ...and back to one chain. Everything after this is identical either way.
#
# THE SKIP BRANCH LANDS HERE, on the same node the scene's exit lands on, so it
# is not a dead end: `cc_g01_epilogue_scene_done` is what Gig01_Encounter reads
# before it sets `cc_g01_mama_talked`, and that is the fact the next objective
# waits on. Route the skip anywhere else and the gig strands on obj_mama.
EPILOGUE_DONE = add_setvar('cc_g01_epilogue_scene_done', 1)
b.connect((EPILOGUE_NID, 'epilogue_out'), (EPILOGUE_DONE, 'In'))
b.connect((MAMA_GONE, 'Out'), (EPILOGUE_DONE, 'In'))
chain.append((EPILOGUE_DONE, 'Out'))
# ...and then he actually goes and gets it. Johnny is waiting at the counter for
# the last two lines of the comic, which is where the gig ends.
objective_step('cc_g01_mama_talked', 'obj_mama', 'obj_bar', 'pin_bar')

# THE ENDING, as a scene since 2026-08-13.
#
# It used to be two SCRIPTED CAPTIONS driven entirely from
# Gig01_Encounter.Line(15) and Line(16) - which is why Johnny and V had
# generated audio that nothing could play: a caption has no locstring RUID, so
# the voiceover map has nothing to key on. Rebuilding the beat as a real scene is
# the whole point of the exercise (BUILDING.md, "Audio toolchain").
#
# The script still owns the TRIGGER and only the trigger: it sets
# cc_g01_bar_reached on proximity to the stools, with an "anywhere in the bar
# after ~45 s" fallback that must not be removed - the previous shape of that
# trigger stranded the gig with no way to finish it.
step(add_pause_fact('cc_g01_bar_reached'))
step(add_scene(SCENES + 'gig01_bar.scene', ANCHOR_BAR, ['bar_in'], ['bar_out']),
     in_sock='bar_in', out_sock='bar_out')
# Let the last line of the comic land before the gig announces itself.
#
# This replaces Line(16)'s CloseAfter("cc_g01_bar_done", 4.2). The rule it
# enforces has been paid for once already: quest completion and the reward
# banner both draw OVER the subtitle, and firing them on the same frame as the
# closing line ate it completely while the trace showed it playing perfectly.
# The scene carries a 1.2 s tail of its own; this is the rest of it.
#
# A realtime delay stalls while a menu is open (docs/gotchas.md #3). Here that is
# the desired behaviour, not a hazard: it only postpones the banner.
step(add_delay(3))
step(add_setvar('cc_g01_bar_done', 1))
objective_step('cc_g01_bar_done', 'obj_bar', None)
step(add_journal_quest(QUEST, track=0), in_sock='Succeeded')
step(add_setvar('cc_g01_done', 1))
step(add_output(), in_sock='In', out_sock=None)

# ---- DEV ONLY: jump straight to the epilogue ------------------------------
#
# the design called for "a simple way to skip all the mission and just go there",
# and there wasn't one: the graph has nine scene nodes ahead of the epilogue and
# setting facts does not skip a scene - it plays. Reaching the bar meant sitting
# through every conversation and answering three phone calls.
#
# So this forks off the PHASE INPUT, which is live from the moment the phase
# starts, and waits on a fact nothing but the dev menu ever sets. When it fires,
# it enters the epilogue scene directly. A quest socket takes more than one
# connection, so the normal route into that scene is untouched.
#
# Deliberately a dead end: it does NOT rejoin the main chain, so it cannot
# advance or corrupt a real playthrough - it plays the conversation and stops.
# Same shape as the cc_g01_call_video experiment: gated behind a fact, harmless
# at 0, and worth its keep because the alternative is a four-minute replay every
# time the epilogue needs one listen.
# ============================================================================
# BOTH DEV SHORTCUT BRANCHES ARE REMOVED. THEY NEVER WORKED. 2026-08-14.
# ============================================================================
#
# Playtest: *"Button doesn't work at all, doesn't do anything. Do note the coyote
# button never worked either."* The epilogue one had been in since 2026-08-12
# and was assumed good because nothing ever contradicted it - nobody had needed
# it badly enough to notice it did nothing.
#
# THE REASON, measured across all 358 shipped street-story questphases:
#
#   input-socket fan-in, ALL node types   2 sources: 29 sockets, 3 sources: 2
#   input-socket fan-in, SCENE nodes      **never more than 1 source. Zero.**
#
# Both branches did the same thing: entered a `questSceneNodeDefinition` that
# the main chain already enters. Fan-in in general is fine and vanilla does it;
# fan-in on a SCENE node is something vanilla never does, and it does not work.
#
# The obvious way around it - give the dev branch its own scene node - is what
# was tried on 2026-08-14 and it **crashed the game on load** (see the entry in
# the architecture notes). So neither shape is usable, and the design call was *"if you can't
# make them work it's ok it's just debug, remove them."*
#
# IF A DEV SHORTCUT IS EVER WANTED AGAIN, the untried idea is a phase whose
# scene node is entered from ONE place only, with the dev fact ORed into that
# single entry condition upstream - not a second edge into the node itself.
# Do not re-add a second edge, and do not re-add a second scene node.

# ...and the same trick for the LIPSYNC DIAGNOSTIC, added 2026-08-14.
#
# gig01_arasaka is two minutes into the gig, which sounded cheap enough to
# re-run - until it had to be re-run three times because the thing being
# measured is four seconds long and lands wherever the around_player marker
# feels like putting it. nobody should be replaying an intro to look at a
# mouth.
#
# ============================================================================
# THE FIRST VERSION OF THIS CRASHED THE GAME ON LOAD. Read before editing.
# ============================================================================
#
# It was written as an "improvement" on the epilogue branch above: a SEPARATE
# scene node pointing at the same file, with its exit socket left unconnected,
# so that firing the fact could not advance the real chain. A genuine dead end,
# and tidier. It also killed the game 67 s into a session in which the gig had
# not even been started - `cc_g01_start` was never set, the trace stops at a
# save load, and the only thing that had changed since the previous (clean) run
# was this graph.
#
# Which of the two differences did it - the duplicate scene node, or the
# dangling output socket - was not separated, because the fix removes both:
# **enter the node that already exists, exactly like the epilogue branch does.**
#
# This is the third hand-reasoned improvement on a shipped pattern to cost
# real debugging time (the shard container, the body double's spawn params,
# this). The rule has to be applied even when the deviation looks
# obviously safer: COPY THE THING THAT WORKS, THEN CHANGE ONE THING AT A TIME.
#
# The cost of doing it the proven way is real and accepted: this branch feeds
# into the live chain, so firing it DOES advance the gig past the arasaka beat -
# same as the epilogue button. It is a dev fact that defaults to 0 and is only
# ever set from the CET menu, which is the risk profile the epilogue
# branch has carried since 2026-08-12.
# (nothing here - see the block above)

result = b.build()
with open(OUT, 'w', encoding='utf-8', newline='\n') as fh:
    json.dump(result, fh, indent=2)
print(f'wrote {OUT}')
print(f'nodes: {len(b.nodes)}, connections: {len(b.conns)}, handles used: {b.next_handle}')
