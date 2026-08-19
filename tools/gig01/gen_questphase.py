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
    ANCHOR_PLAYER,
)

configure(phase_name='gig01.questphase')

_TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(_TOOLS)
OUT = os.path.join(REPO, 'mods', 'gig-01-negative-balance', 'source', 'wkit', 'raw',
                   'mod', 'negative_balance', 'quest', 'gig01.questphase.json')

CONTACT = 'contacts/elena_ortega'
QUEST = 'quests/street_stories/cc_g01_negative_balance'
POI = 'points_of_interest/street_stories/cc_g01_negative_balance'

SCENES = 'mod\\negative_balance\\scenes\\'

# Scene markers. Same resolvable base-game NodeRefs the map pins anchor to
# (tools/gig01/gen_journal.py) - a scene location must resolve for the same reason a
# pin anchor must.
ANCHOR_OFFICE = '#std_arr_parking_spwn_179'
ANCHOR_ESTATE = '#q113_dvc_arasaka_estate_camera_010'
ANCHOR_COYOTE = '#loc_sq022_el_coyote_cojo_bar_marker'
# The bar beat needs an anchor next to the STOOLS, not the pub entrance where
# ANCHOR_COYOTE sits - Johnny has to stand beside V for that one. Same node
# gen_scenes.ANCHOR_BAR uses; the two must stay in step.
ANCHOR_BAR = '#hey_rey_food_01_mp'
# Mama Welles speaks a POSITIONAL line (Vo_Expression_Spoken), and an
# around_player marker is not on the player - it lands a few metres to one side,
# which is audible. She gets a fixed anchor 3 m from her mark instead. See
# gen_scenes.ANCHOR_MAMA; the two must stay in step.
ANCHOR_MAMA = '#sq018_pepevodka'
# MAMA WELLES HERSELF, not the marker beside her. ANCHOR_MAMA is a bottle on a
# shelf used to place a scene; this is the NPC, and it is the reference her own
# vanilla scene uses to acquire her (`spawnSet` entry `mama_welles`, reference
# `#mama_welles` - confirmed in game by our epilogue acquiring her through it).
#
# NOTHING USES IT. Kept because the fact is worth having written down, and with
# the warning attached: addressing her through it from a QUEST node stalled the
# graph on 2026-08-15 (see the note where add_voiceset used to be). Resolving for
# a scene actor and resolving for a quest node are not the same thing.
ANCHOR_MAMA_NPC = '#mama_welles'

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

step(add_setvar('cc_g01_accepted', 1))
step(add_journal_quest(QUEST), in_sock='Active')
step(add_journal('gameJournalQuestPhase', QUEST + '/phase_main', notify=0), in_sock='Active')
step(add_journal('gameJournalQuestObjective', QUEST + '/phase_main/obj_office'), in_sock='Active')
# Map pins are journal entries in their own right: the engine only creates a
# mappin once the pin entry itself is Active. Activating just the objective
# leaves the pin dormant (this cost a full day of investigation).
step(add_journal('gameJournalQuestMapPin', QUEST + '/phase_main/obj_office/pin_office', notify=0),
     in_sock='Active')
step(add_journal('gameJournalPointOfInterestMappin', POI, notify=0), in_sock='Active')
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
step(add_journal('gameJournalQuestObjective', QUEST + '/phase_main/obj_shard'),
     in_sock='Active')
# The pin, and it is the objective marker the design called for: a 20 cm chip on a
# desk in a dark office is not findable without one. Pins are journal entries in
# their own right and an inactive one is invisible - activating the objective is
# NOT enough (map-pins-playbook.md, ingredient 2).
step(add_journal('gameJournalQuestMapPin',
                 QUEST + '/phase_main/obj_shard/pin_shard', notify=0),
     in_sock='Active')
step(add_pause_fact('cc_g01_shard_found'))
step(add_scene(SCENES + 'gig01_shard_find.scene', ANCHOR_PLAYER,
               ['shard_find_in'], ['shard_find_out']),
     in_sock='shard_find_in', out_sock='shard_find_out')
step(add_setvar('cc_g01_shard_open', 1))
step(add_pause_fact('cc_g01_shard_read'))
step(add_scene(SCENES + 'gig01_shard_read.scene', ANCHOR_PLAYER,
               ['shard_read_in'], ['shard_read_out']),
     in_sock='shard_read_in', out_sock='shard_read_out')
step(add_journal('gameJournalQuestObjective', QUEST + '/phase_main/obj_shard',
                 notify=0), in_sock='Succeeded')

# ...and a beat AFTER the scene has exited, not on the same frame as its last
# section. playtest, 2026-08-13: "Johnny disappears right before 'Figures', should
# wait more." The scene's own tail went to 2000 ms for the same reason; this is
# the other half, because the dissolve is a quest-phase decision and the scene
# cannot hold it off.
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

# CALL 1 - comic pp. 26-27. V CALLS NIX and hands over the ledger.
# Player-initiated: Gig01_Holocall swaps caller/addressee for this one, so the
# phone dials instead of ringing. Nix has no reason to call about a ledger he
# does not know exists (playtest, 2026-08-12). This is the
# handover the gig used to do off-screen: it read a kill ledger and then took a
# callback from a netrunner V had never spoken to.
step(add_setvar('cc_g01_nixbrief_request', 1))
step(add_pause_fact('cc_g01_nixbrief_talking'))
step(add_scene(SCENES + 'gig01_nix_brief.scene', ANCHOR_OFFICE,
               ['nix_brief_in'], ['nix_brief_out']),
     in_sock='nix_brief_in', out_sock='nix_brief_out')
step(add_setvar('cc_g01_nixbrief_end', 1))
step(add_pause_fact('cc_g01_nixbrief_done'))

# The send + the payment, then Johnny's p28 beat while Nix works. Both are
# script-driven (Gig01_Encounter): the transfer is an on-screen toast in the
# comic, not a spoken line, and Johnny needs staging.
objective_step('cc_g01_ledger_sent', 'obj_nixcall', 'obj_nixwait')
# Johnny on the crosswalk while Nix digs, comic p28 - V asks the question the
# gig is built around. A scene since 2026-08-13; ANCHOR_PLAYER because V has
# just made a phone call and could be anywhere by now.
step(add_setvar('cc_g01_johnny_done', 0))
step(add_scene(SCENES + 'gig01_legend.scene', ANCHOR_PLAYER,
               ['legend_in'], ['legend_out']),
     in_sock='legend_in', out_sock='legend_out')
# NOT set to 1 here. Johnny is staged for the crosswalk (p28) and STAYS
# STANDING THERE through Nix's callback, because he has two lines at the end of
# it (p30) and the design called for the obvious thing: "let's not make Johnny
# disappear when Nix calls. Keep him there until he finishes saying these 2 lines
# too. So the whole call he's there just not saying anything."
#
# That is also what the comic draws - pp. 28-30 are one continuous street scene
# with Johnny in frame throughout, and the phone call happens over the top of it.
step(add_setvar('cc_g01_johnny_legend', 1))

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
# TWO IN-GAME HOURS, on the world clock (see add_game_delay for why not
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
step(add_game_delay(hours=2))

# Same handshake as Elena's call, different fact prefix - one system in
# Gig01_Holocall.reds drives both. Nix's contact is a BASE-GAME one, so the
# addressee is the existing contact id "nix"; nothing new is merged for him.
step(add_setvar('cc_g01_nixcall_request', 1))
step(add_pause_fact('cc_g01_nixcall_talking'))
step(add_scene(SCENES + 'gig01_nix_call.scene', ANCHOR_OFFICE,
               ['nix_call_in'], ['nix_call_out']),
     in_sock='nix_call_in', out_sock='nix_call_out')
step(add_setvar('cc_g01_nixcall_end', 1))
step(add_pause_fact('cc_g01_nixcall_done'))

# COMIC p30 - AFTER THE PHONE IS DOWN, not during the call.
#
# It used to be the tail of gig01_nix_call, and it could not read the way the design wanted from there: the chrome does not hang up until that scene EXITS, because
# cc_g01_nixcall_end is set on its exit socket. So Johnny spoke over a live
# call. His two lines are their own beat now, entered on nixcall_done, which is
# the phone actually being down:
#
#     Nix gives the address -> the call closes -> Johnny appears -> his lines
#     -> he glitches out -> the next objective
step(add_scene(SCENES + 'gig01_graves.scene', ANCHOR_PLAYER,
               ['graves_in'], ['graves_out']),
     in_sock='graves_in', out_sock='graves_out')

# AND NOW Johnny goes - the beat above is the last thing he has to say before
# North Oak.
step(add_setvar('cc_g01_johnny_done', 1))

step(add_setvar('cc_g01_nix_done', 1))
# Estate: travel, kill Hoshino, upload the malware from his own terminal.
objective_step('cc_g01_nix_done', 'obj_nixwait', 'obj_estate', 'pin_estate')
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
b.connect((HOSHINO_TALK, 'hoshino_out'), (HOSHINO_JOIN, 'Succeeded'))
b.connect((HOSHINO_DEAD, 'Out'), (HOSHINO_JOIN, 'Succeeded'))
chain.append((HOSHINO_JOIN, 'Out'))
# HE IS NOT MADE HOSTILE HERE, AND THAT WAS TRIED. the design called for it on
# 2026-08-14, it was built as an attitude flip on this fact, and it did nothing
# observable: `enableSensesOnStart: false` on his record means he is hostile but
# never looking, so he stands there exactly as before. The playtest verdict: *"Still
# doesn't attack but it's ok let's not complicate things. Feel free to remove
# the last change if it can create other issues."* Removed - a code path with no
# effect is a thing someone later debugs for nothing.
#
# The only way to make him fight would be turning senses on, which is what
# kept him peaceful through his own conversation. Do not.

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
# ...and the estate terminal exchange, comic p51, AFTER V has unplugged.
#
# cc_g01_malware_talk is not cc_g01_malware_done: the upload finishes while V is
# still in the device zoom, and staging an actor on a player locked in a UI is
# what soft-locked the office beat once. Gig01_Encounter sets this one only when
# IsUsingDevice goes false. The escape objective is already on screen by then,
# which is what happened before too.
step(add_pause_fact('cc_g01_malware_talk'))
step(add_setvar('cc_g01_johnny_done', 0))
step(add_scene(SCENES + 'gig01_malware.scene', ANCHOR_PLAYER,
               ['malware_in'], ['malware_out']),
     in_sock='malware_in', out_sock='malware_out')
step(add_setvar('cc_g01_johnny_done', 1))
objective_step('cc_g01_escaped', 'obj_escape', 'obj_epilogue', 'pin_epilogue')
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
with open(OUT, 'w', encoding='utf-8') as fh:
    json.dump(result, fh, indent=2)
print(f'wrote {OUT}')
print(f'nodes: {len(b.nodes)}, connections: {len(b.conns)}, handles used: {b.next_handle}')
