-- Negative Balance, DEV debug menu (never shipped in releases)
-- CET overlay window: quest facts, teleport presets, smoke checks.

local FACTS = {
    -- THE IN-GAME START GATE (Gig01_Start.reds). These four are BASE-GAME
    -- facts, not ours - read them, and only set them knowing that.
    --   q101_enable_side_content  the prologue is over and side content is
    --      allowed. CDPR's own gate: the root of all 436 minor activities and
    --      every fixer phase waits on it. Set by q101_p2_meet_takemura (and by
    --      ep1.questphase for a Phantom Liberty standalone start). Forcing it
    --      to 1 here is the quickest way to test the trigger on an early save.
    --   q115_point_of_no_return   Nocturne Op55N1 has begun; the gig will not
    --      offer itself any more.
    --   codex_nix / sq018_mama_welles_met   "has V met them". SHOWN ONLY - the
    --      trigger does NOT gate on either, because both belong to optional
    --      content and a gate that can stay false is a deadlock with no error
    --      message. See the header of Gig01_Start.reds.
    "q101_enable_side_content",
    "q115_point_of_no_return",
    "codex_nix",
    "sq018_mama_welles_met",
    "cc_g01_start",
    "cc_g01_started",
    "cc_g01_accepted",
    -- Elena's holocall handshake (Gig01_Holocall.reds <-> the quest phase).
    -- phonecall_elena_ortega_with_player is written by the GAME, not by us:
    -- 0 Ended, 1 Initializing, 2 Talking, 3 Rejected. Watch it to see whether
    -- the ring actually reached the player.
    "cc_g01_call_request",
    "cc_g01_call_answered",
    "cc_g01_call_talking",
    "cc_g01_call_end",
    "cc_g01_call_done",
    "phonecall_elena_ortega_with_player",
    -- Diagnostics, both default off:
    --   cc_g01_no_scene   answer the phone with no scene behind it
    -- (cc_g01_call_video is gone. It gated a Video holocall, which was closed
    --  on reasoning withdrawn 2026-08-22. The HOLOCALL LAB section further
    --  down is where that question is being reopened; see docs/backlog.md 3d.)
    "cc_g01_no_scene",
    -- HOLD THE GIG. Set to 1 and Gig01_Start stops offering the gig, so Elena
    -- never rings; clear it and the next check picks up where it left off. For
    -- testing anything that is not the gig, where an hour parked in the world
    -- otherwise collects her call every few minutes. It does not settle the
    -- trigger, so it is releasable without a reload.
    "cc_g01_dev_hold",
    -- THE "HEROES IS NOT DONE" MESSAGE, already shown. Gig01_Start sets it the
    -- one time it tells a player the gig is waiting on sq018, so the message
    -- cannot repeat every session. Clear it to see the message again without
    -- starting a new save; it has no other effect, and in particular clearing
    -- it does NOT unblock the gig.
    "cc_g01_heroes_notified",
    -- Nix's call, same handshake with a different prefix.
    -- THE VIDEO ROUTE for both Nix calls (docs/backlog.md 3d). Read these, do
    -- not set them: the QUEST PHASE owns both calls now, end to end.
    --   _video     1 = Nix is on screen, rendered live. 0 = the audio call with
    --              a portrait, which is the fallback.
    --   _videofail 1 = the studio never arrived, or the call went unanswered
    --              enough times, so this beat gave up on video and rang the old
    --              way instead.
    --   _rings     how many times the callback has rung unanswered. It falls
    --              back to the audio call at 5.
    --   _step      a breadcrumb the phase drops after every node, so a beat
    --              that stops says WHERE instead of nothing at all. 1 opened
    --              the studio, 2 asked for it, 3 it arrived, 4 ringing, 5 a
    --              ring was missed, 6 connected, 7 the words are done, 9 the
    --              beat is over. 20 and 21 are the audio fallback.
    --   _claim     internal to the phase's races; 0 between them.
    "cc_g01_nixbrief_video",
    "cc_g01_nixbrief_videofail",
    "cc_g01_nixbrief_step",
    "cc_g01_nixcall_video",
    "cc_g01_nixcall_videofail",
    "cc_g01_nixcall_step",
    "cc_g01_nixcall_rings",
    -- MAY THE PHONE RING RIGHT NOW. _want is the quest phase asking,
    -- _ok is Gig01_Holocall answering (combat, fast travel, V on a bike).
    -- A callback that never rings with _want 1 and _ok 0 for minutes is V
    -- riding; the script gives up and rings anyway after ninety seconds.
    "cc_g01_ring_want",
    "cc_g01_ring_ok",
    "cc_g01_nixcall_request",
    "cc_g01_nixcall_answered",
    "cc_g01_nixcall_talking",
    "cc_g01_nixcall_end",
    "cc_g01_nixcall_done",
    "phonecall_cc_g01_nix_with_player",
    "cc_g01_office_reached",
    -- READ THESE, do not set them. Each site's detail is a community, so these
    -- say how many of its posts have been FOUND and turned hostile, and the
    -- bare `cc_g01_dbg_<site>` code says whether the lookup worked at all:
    --   0 nothing has looked yet
    --   1 the community name did not resolve, so its sector is not loading
    --   2 resolved, but no bodies. The quest phase has not switched it on, or
    --     nothing has streamed in yet
    --   3 found and turned. `_guards` is how many, `_total` how many there are
    --
    -- The count is a high-water mark and it climbs as you move, because a post
    -- that has not streamed in yet is asked for again every six seconds while
    -- you are on site. Coming over the estate's back wall gives a low number
    -- that grows as you walk down to the gate. A number that stays at 0 with a
    -- code of 2 is the empty-site bug.
    --
    -- `cc_g01_dbg_office_guards`, the old spawn counter, is gone with the spawn
    -- chain it counted.
    "cc_g01_dbg_estate",
    "cc_g01_dbg_estate_guards",
    -- READ THESE TOO. What actually landed on the guards, as opposed to what
    -- was asked for. See the panel block for how to read them.
    "cc_g01_dbg_estate_hostile",
    "cc_g01_dbg_estate_senses",
    "cc_g01_dbg_estate_workspot",
    "cc_g01_dbg_estate_total",
    -- The same six for the industrial park.
    "cc_g01_dbg_compound",
    "cc_g01_dbg_compound_guards",
    "cc_g01_dbg_compound_total",
    "cc_g01_dbg_compound_hostile",
    "cc_g01_dbg_compound_senses",
    "cc_g01_dbg_compound_workspot",
    -- READ THESE, do not set them. WHERE THE PLAYER IS, and whether the estate
    -- boundary accepts it. Ungated: they update everywhere in the city and with
    -- no gig running, because the fault they exist for is the estate leg doing
    -- NOTHING and saying nothing about why.
    --   _pz         height in whole metres. Estate ground is ~220, the office
    --               level ~226, Hoshino's floor ~230, the roof ~234
    --   _estate_in  1 = the traced wall outline accepts this spot
    --   _at_estate  1 = the arrival test accepts it, by the outline OR the gate
    --               sphere OR the sphere around Hoshino. THIS is what the whole
    --               estate leg waits on. If it reads 0 while you are standing
    --               on the estate, that is the bug, and _pz says at what height
    "cc_g01_dbg_pz",
    "cc_g01_dbg_estate_in",
    "cc_g01_dbg_at_estate",
    -- READ THESE, do not set them. The base game ships the doors onto the
    -- office floor with deviceState DISABLED and switches them on during
    -- "Gimme Danger", so a player who has not done that mission cannot get in
    -- (Nexus, 1.1.x). Gig01_OfficeDoors.reds switches them on while the gig is
    -- live, from two hooks whose timing could not be established offline.
    --   _opened = how many of the five this save has taken to ON, max 5
    --   _state  = what the last of them reported when it streamed in:
    --             1 DISABLED, 2 ON, 3 OFF, 4 UNPOWERED, 9 something else
    --   _giveup = pumps that ran out of passes. MUST STAY 0
    -- On a save where "Gimme Danger" is done, _opened is 0 and _state is 2, and
    -- that is correct: the doors are already ON and there is nothing to do.
    --
    -- The hook runs when a door STREAMS IN. Setting cc_g01_accepted from this
    -- menu while already standing at the door does nothing until the sector
    -- reloads, so set it first, or teleport away and back.
    "cc_g01_doors_opened",
    "cc_g01_dbg_door_state",
    "cc_g01_dbg_door_giveup",
    "cc_g01_ledger_read",
    "cc_g01_terminal_done",
    -- The shard in the office desk, comic pp. 23-24. Set 1 on shard_found to
    -- skip the walk back to the desk; set 1 on shard_read to skip the reader if
    -- it ever fails to close the beat.
    "cc_g01_shard_found",
    "cc_g01_shard_open",
    "cc_g01_shard_read",
    "cc_g01_johnny_done",
    "cc_g01_left_compound",
    "cc_g01_nix_done",
    -- Nix's findings arrive as a TEXT MESSAGE now (2026-09-03), not a second
    -- holocall. cc_g01_nixmsg_sent means the thread has been pushed to the
    -- phone; cc_g01_nix_done means the player has actually opened it and
    -- tapped the reply, which is what the estate objective waits on. Set
    -- nix_done by hand to skip the read.
    "cc_g01_nixmsg_sent",
    -- The fee to Nix: pay_nix is the phase asking, nix_paid is the script
    -- confirming the eddies left. Set nix_paid to 1 by hand to skip the
    -- charge while testing.
    "cc_g01_pay_nix",
    "cc_g01_nix_paid",
    -- The gig pays in two places now: the 2500 eddies as the malware
    -- goes in at the estate (cc_g01_skimmed), the 300 Street Cred when
    -- the gig closes (cc_g01_rewarded). Both guarded by their fact so a
    -- reload cannot pay twice.
    "cc_g01_skimmed",
    "cc_g01_estate_reached",
    "cc_g01_wayin_reached",
    -- Which of the six waypoints into North Oak is pinned, 1..6 (0 reads as 1).
    -- Exactly one marker is ever active. Set it by hand to put a given marker
    -- up without walking to the previous one - the script re-states all six on
    -- the next tick, so a value out of range simply shows nothing.
    "cc_g01_wayin_leg",
    "cc_g01_hoshino_met",
    "cc_g01_hoshino_talked",
    -- Flips Hoshino hostile with no shot fired, for testing the fight
    -- without landing one. One way within a session; reload to undo.
    "cc_g01_dbg_hoshino_fight",
    "cc_g01_hoshino_dead",
    "cc_g01_malware_done",
    "cc_g01_escaped",
    "cc_g01_at_coyote",
    "cc_g01_mama_reached",
    -- 1 = the base-game Mama is in the bar (the epilogue ACQUIRES her),
    -- 2 = she is not and ours stands in. 0 means nobody has looked yet.
    -- Set it by hand to force either epilogue variant.
    "cc_g01_mama_present",
    -- BASE-GAME fact, not ours. Her default dialogue scene will not start while
    -- this is >= 1. Set it by hand before walking into El Coyote to test whether
    -- the gate itself works, separately from whether our script sets it in time.
    "mama_is_talking",
    -- (cc_g01_dev_epilogue / cc_g01_dev_lipsync are GONE, 2026-08-14. Both
    --  entered a scene node the main chain also enters, and no shipped scene
    --  node has two sources - so neither shortcut ever did anything).
    "cc_g01_epilogue_scene_done",
    "cc_g01_mama_reached",
    "cc_g01_mama_talked",
    "cc_g01_done",
    "cc_g01_rewarded",
    -- (cc_g01_dbg_johnny and cc_g01_dbg_johnny_ws are GONE, 2026-08-14, with
    --  the script-owned Johnny they instrumented. Their finding is recorded:
    --  a workspot IS what makes the apparition render - phantomVisibleStates
    --  is ["RootMotion","Workspot"] - and a body with no workspot is invisible
    --  AND untargetable.)
    -- Does the shard entity's CLASS attach at all? Set by the wrap on
    -- HealthConsumable.OnGameAttached in Gig01_Shard.reds.
    --   1  it attaches - the prompt problem is the interaction itself
    --   0  it never attaches (HealthConsumable is a CPO/multiplayer
    --      lineage class), so no component work can help and the vanilla
    --      shard is the answer
    "cc_g01_dbg_shard_class",
    -- What the shard's interaction component reports 2 s after attach:
    --   1  component not resolved (wrong name in the .ent)
    --   2  no hotspot definition loaded (definitionResource wrong/unstreamed)
    --   3  definition loaded, no ACTIVE layer (wrong definition for this shape)
    --   5+ hotspot live (4 + layer count) - problem is the choice or targeting
    "cc_g01_dbg_shard_ui",
    -- The item swap on the office shard case (Gig01_Shard.reds):
    --   1  a shard case took control somewhere
    --   2  ...one within 12 m of the office terminal
    --   3  ...holding the Hanako shard - assignment made
    --   4  ...and it read back as ours
    "cc_g01_dbg_shard_item",
    -- Johnny's four appearances, in story order. Each one stages him and then
    -- plays its lines; the fact is the "already done" guard, so setting one to 1
    -- by hand SKIPS that appearance rather than triggering it.
    --   cue      set by the Elena scene, one line before the last hub
    --   arasaka  his answer as the call drops
    --   hoshino  over the body at the estate
    --   bar      the ending: reached -> he appears, done -> gig over
    "cc_g01_johnny_cue",
    "cc_g01_johnny_hoshino",
    "cc_g01_johnny_legend",
    "cc_g01_bar_reached",
    "cc_g01_bar_done",
    -- Nix's first call and the ledger handover.
    "cc_g01_nixbrief_request",
    "cc_g01_nixbrief_answered",
    "cc_g01_nixbrief_talking",
    "cc_g01_nixbrief_end",
    "cc_g01_nixbrief_done",
    "cc_g01_ledger_sent",
    "cc_g01_ledger_copied",
    "cc_g01_terminal_left",
}

-- Teleport presets. Coords are captured in-game with [Save current position];
-- placeholders (nil) until we stand at the real spots.
local presets = {
    -- The two Personal Mechanics community spots, for the A/B against our
    -- bench (backlog 29-ADDENDUM-4). Positions are the shop sectors' own box
    -- centres, raised half a metre so V does not clip the ground.
    { name = "PM: Miguel's shop (Kabuki)", pos = { x = -1119.9, y = 1201.0, z = 19.2, w = 1.0 } },
    { name = "PM: Viktor garage mechanic", pos = { x = -1572.5, y = 1260.4, z = 12.0, w = 1.0 } },
    { name = "El Coyote Cojo (bar)", pos = { x = -1259.598, y = -989.166, z = 12.037, w = 1.0 } },
    -- Captured off the live NPC; ~10 m from the bar marker above.
    { name = "Mama Welles (her spot)", pos = { x = -1262.178, y = -998.805, z = 12.057, w = 1.0 } },
    { name = "Arasaka compound entry", pos = { x = -189.371, y = -1464.500, z = 7.596, w = 1.0 } },
    -- FOUR POINTS AROUND THE COMPOUND, added 2026-08-25. They were the starts of
    -- four patrol beats that did not work and are gone; the positions are still
    -- the quickest way to reach the second gate and the yard, which are the
    -- parts of the site the old placement never covered, so they stay as plain
    -- teleports under honest names.
    { name = "Compound: second gate", pos = { x = -225.764, y = -1497.931, z = 7.600, w = 1.0 } },
    { name = "Compound: yard by the building", pos = { x = -224.379, y = -1435.308, z = 7.600, w = 1.0 } },
    { name = "Compound: yard by the outer gate", pos = { x = -194.932, y = -1437.813, z = 7.600, w = 1.0 } },
    { name = "Compound: far side of the yard", pos = { x = -243.136, y = -1487.774, z = 7.600, w = 1.0 } },
    { name = "Arasaka office terminal", pos = { x = -251.915, y = -1456.364, z = 14.600, w = 1.0 } },
    -- The two doors the base game ships DISABLED, both on the office floor and
    -- both on the gig's own route. Stand at one and look at it: no interaction
    -- prompt means it is still off. Positions are the door nodes themselves,
    -- read out of the streaming sectors, so V lands in the doorway.
    { name = "Office door (outer, DISABLED)", pos = { x = -241.900, y = -1450.700, z = 14.600, w = 1.0 } },
    { name = "Inner door (DISABLED)", pos = { x = -219.800, y = -1423.200, z = 14.600, w = 1.0 } },
    { name = "Estate gate (North Oak)", pos = { x = 384.181, y = 1164.724, z = 220.643, w = 1.0 } },
    { name = "Estate garden", pos = { x = 340.924, y = 1033.924, z = 225.956, w = 1.0 } },
    { name = "Hoshino", pos = { x = 300.102, y = 1054.556, z = 229.928, w = 1.0 } },
    { name = "Hoshino's terminal", pos = { x = 284.852, y = 1023.697, z = 224.928, w = 1.0 } },
} },
}

local PRESET_FILE = "presets.lua"
local visible = false

local function log(msg)
    print("[NB] " .. msg)
    spdlog.info(msg)
end

-- Crash-safe trace ----------------------------------------------------------
--
-- spdlog and the main dev log are BUFFERED, so a hard crash loses everything
-- that mattered - which is what happened the first time the holocall
-- took the game down (nothing in any log, only a CrashInfo.json). This writes
-- call_trace.log by opening, appending and CLOSING on every single line, so
-- whatever is on disk is what was true the instant before the crash.
--
-- It only records CHANGES, so the file stays short and the last line is always
-- the last thing that happened.
local TRACE_FILE = "call_trace.log"
local TRACE_FACTS = {
    "cc_g01_call_request",
    "phonecall_elena_ortega_with_player",
    "cc_g01_call_answered",
    "cc_g01_call_talking",
    "cc_g01_call_end",
    "cc_g01_call_done",
    "cc_g01_nixcall_request",
    "phonecall_cc_g01_nix_with_player",
    "cc_g01_nixcall_talking",
    "cc_g01_nixcall_done",
    "cc_g01_hoshino_met",
    -- The terminal beat gates "get clear of the compound" now: it is set by the
    -- LAST line of Johnny's exchange at the desk, not by the download finishing.
    -- If the objective ever seems stuck there, this is the fact to look at.
    "cc_g01_ledger_copied",
    "cc_g01_terminal_left",
    "cc_g01_terminal_done",
    -- The shard beat, added 2026-08-13. Three facts with three different owners
    -- (script / quest phase / script), so a stall here is ambiguous without the
    -- trace: found = V is at the desk, open = the find line played and the
    -- reader was asked for, read = the reader was CLOSED.
    "cc_g01_shard_found",
    "cc_g01_shard_open",
    "cc_g01_shard_read",
    "cc_g01_dbg_shard_class",
    "cc_g01_dbg_shard_ui",
    "cc_g01_dbg_shard_item",
    -- Johnny's apparition lives and dies by this one fact. If he vanishes
    -- mid-beat, the trace says whether the quest phase asked for it.
    "cc_g01_johnny_done",
    -- (The five cc_g01_dbg_lip_* facts are GONE, 2026-08-14. They answered
    --  their questions and the answers are recorded: the tags ARE populated,
    --  which is how `type: Tag` was proven dead rather than merely unproven
    --  (docs/backlog.md 2j); and the placement maths was right all along -
    --  `Teleport` ignores the position it is given for a puppet and drops him
    --  on the player, which is why the script route needed a workspot device.
    --  That whole route is gone as of 2026-08-17: every Johnny beat is placed
    --  by its own scene, docs/backlog.md 9.)
    -- Added after 2026-08-12: "get clear of the compound never triggered" was
    -- reported, and the trace could only show it INDIRECTLY (nixcall_request
    -- implies it fired). Trace the fact itself so the next report is one line.
    "cc_g01_left_compound",
    -- Nix is TWO calls now: nixbrief = V hands over the ledger and hires him
    -- (comic pp. 26-27), nixcall = his callback with Hoshino (pp. 29-30).
    "cc_g01_nixbrief_request",
    "cc_g01_nixbrief_talking",
    "cc_g01_nixbrief_done",
    "cc_g01_ledger_sent",
    "cc_g01_johnny_legend",
    "cc_g01_nixcall_answered",
    "cc_g01_nix_done",
    -- The message thread, in firing order: pushed to the phone, then read.
    "cc_g01_nixmsg_sent",
    "cc_g01_at_coyote",
    "cc_g01_mama_reached",
    -- 1 = the base-game Mama is in the bar (the epilogue ACQUIRES her),
    -- 2 = she is not and ours stands in. 0 means nobody has looked yet.
    -- Set it by hand to force either epilogue variant.
    "cc_g01_mama_present",
    -- BASE-GAME fact, not ours. Her default dialogue scene will not start while
    -- this is >= 1. Set it by hand before walking into El Coyote to test whether
    -- the gate itself works, separately from whether our script sets it in time.
    "mama_is_talking",
    -- (cc_g01_dev_epilogue / cc_g01_dev_lipsync are GONE, 2026-08-14. Both
    --  entered a scene node the main chain also enters, and no shipped scene
    --  node has two sources - so neither shortcut ever did anything).
    "cc_g01_epilogue_scene_done",
    -- The tail of the gig. Added 2026-08-12 after a crash ~200 s past the
    -- epilogue scene that could not be attributed, because the trace stopped
    -- exactly where the interesting part started: Johnny's closing line, the
    -- quest closing, the payout, and the stand-in despawn all happen after
    -- cc_g01_epilogue_scene_done and none of them were recorded.
    "cc_g01_mama_talked",
    "cc_g01_johnny_cue",
    "cc_g01_johnny_arasaka",
    "cc_g01_johnny_hoshino",
    "cc_g01_bar_reached",
    "cc_g01_bar_done",
    "cc_g01_done",
    "cc_g01_rewarded",
    -- BASE-GAME facts, traced for the holocall lab (docs/backlog.md 3d). This
    -- is the one area of the game known to hard crash, so the handshake that
    -- leads up to a crash has to be on disk before it happens.
    -- holo_setup_active is a mutex on the studio: one call at a time.
    "holo_setup_started",
    "holo_setup_active",
    "holo_nix_calls_v_start_activate",
    "holo_nix_calls_v_start_done",
    "holo_nix_calls_v_end_activate",
    "holo_nix_calls_v_end_done",
    "holo_nix_calls_v_rejected",
    "phonecall_nix_with_player",
    "phonecall_player_with_nix",
    "holo_v_calls_nix_start_activate",
    "holo_v_calls_nix_start_done",
    "holo_v_calls_nix_end_done",
    "cc_g01_nixbrief_video",
    "cc_g01_nixbrief_videofail",
    "cc_g01_nixbrief_step",
    "cc_g01_nixcall_video",
    "cc_g01_nixcall_videofail",
    "cc_g01_nixcall_step",
    "cc_g01_nixcall_rings",
    "cc_g01_ring_want",
    "cc_g01_ring_ok",
    -- The AUDIO half of the same vanilla holocall phase. Traced so that "the
    -- button did nothing" can be told apart from "the fact was set and the
    -- phase declined to act on it", which need opposite fixes.
    "audio_nix_calls_v_start_activate",
    "audio_nix_calls_v_start_done",
    "audio_nix_calls_v_end_activate",
    "audio_nix_calls_v_end_done",
}
local traceLast = {}
local traceClock = 0
local traceSince = 0

local function trace(msg)
    local f = io.open(TRACE_FILE, "a")
    if f then
        f:write(string.format("%.1f  %s\n", traceClock, msg))
        f:close()
    end
end

registerForEvent("onUpdate", function(delta)
    traceClock = traceClock + delta
    traceSince = traceSince + delta
    -- 4 Hz is enough: the states we care about are seconds apart, and the whole
    -- point is the LAST line before a crash, not a high-resolution history.
    if traceSince < 0.25 then return end
    traceSince = 0

    local qs = Game.GetQuestsSystem()
    if not qs then return end
    for _, fact in ipairs(TRACE_FACTS) do
        local value = qs:GetFactStr(fact)
        if traceLast[fact] ~= value then
            if traceLast[fact] ~= nil or value ~= 0 then
                trace(string.format("%s = %d", fact, value))
            end
            traceLast[fact] = value
        end
    end
end)

-- The holocall lab's helpers lived here: the redscript bridge, the fact latch,
-- the skip probe and the step scheduler. Removed with the bench for 1.2.6. See
-- the note where its buttons were, further down.

-- {journal path, entry class name}
local ELENA_PATHS = {
    { "contacts/elena_ortega", "gameJournalContact" },
    { "contacts/elena_ortega/cc_g01_intro", "gameJournalPhoneConversation" },
    { "contacts/elena_ortega/cc_g01_intro/cc_g01_msg_01", "gameJournalPhoneMessage" },
    { "contacts/elena_ortega/cc_g01_intro/cc_g01_msg_02", "gameJournalPhoneMessage" },
    { "contacts/elena_ortega/cc_g01_intro/cc_g01_msg_03", "gameJournalPhoneMessage" },
    { "contacts/elena_ortega/cc_g01_intro/cc_g01_ch_01", "gameJournalPhoneChoiceGroup" },
    { "contacts/elena_ortega/cc_g01_intro/cc_g01_ch_01/cc_g01_ch_01a", "gameJournalPhoneChoiceEntry" },
    { "contacts/elena_ortega/cc_g01_intro/cc_g01_msg_04", "gameJournalPhoneMessage" },
    { "contacts/elena_ortega/cc_g01_intro/cc_g01_msg_05", "gameJournalPhoneMessage" },
    { "contacts/elena_ortega/cc_g01_intro/cc_g01_msg_06", "gameJournalPhoneMessage" },
    { "contacts/elena_ortega/cc_g01_intro/cc_g01_ch_02", "gameJournalPhoneChoiceGroup" },
    { "contacts/elena_ortega/cc_g01_intro/cc_g01_ch_02/cc_g01_ch_02a", "gameJournalPhoneChoiceEntry" },
    { "contacts/elena_ortega/cc_g01_intro/cc_g01_msg_07", "gameJournalPhoneMessage" },
    { "contacts/elena_ortega/cc_g01_intro/cc_g01_ch_03", "gameJournalPhoneChoiceGroup" },
    { "contacts/elena_ortega/cc_g01_intro/cc_g01_ch_03/cc_g01_ch_03a", "gameJournalPhoneChoiceEntry" },
    { "contacts/elena_ortega/cc_g01_intro/cc_g01_msg_08", "gameJournalPhoneMessage" },
}

-- WHICH BASE-GAME QUESTS HAS THIS SAVE DONE?
--
-- Added 2026-08-18, for a question the world files cannot answer: a player
-- reported El Coyote Cojo's entrance shut, and the device dump says the door
-- is DISABLED on his save while the sector ships it ON. So something in the
-- base game's own progression switched it off, and the next question is
-- which quest turns it back on.
--
-- Journal state is the cheapest way to ask. `GetEntryByString(path, class)`
-- plus `GetEntryState(entry)` is the same pair the Elena dump above uses.
--
-- THE PATHS ARE READ OUT OF THE GAME, NOT GUESSED. They come from the
-- string table of `base\journal\cooked_journal.journal`, which carries 224
-- plain-text quest paths. That is NOT every quest in the game: only 6 side
-- quests and 5 main-quest entries survive as plain strings, so treat a
-- missing entry as "this path is not in the table", never as "not done".
local GATING_QUESTS = {
    -- El Coyote Cojo. sq018 is the Jackie quest line, and the objective ids
    -- around it in the journal are `01_go_to_el_coyote`, `01_visit_el_coyote`
    -- and `03_el_coyote_funeral`, i.e. the ofrenda, which is "Heroes". This
    -- is the prime suspect for what enables the bar's entrance.
    { "quests/side_quest/sq018_jackie", "Heroes / the Jackie line (EL COYOTE)" },
    -- The office doors, already known: they ship DISABLED and "Gimme Danger"
    -- switches them on. See Gig01_OfficeDoors.reds and backlog 8a.
    { "quests/main_quest/act_01/q112_01_old_friend",     "Gimme Danger: old friend" },
    { "quests/main_quest/act_01/q112_02_industrial_park", "Gimme Danger: INDUSTRIAL PARK (office doors)" },
    { "quests/main_quest/act_01/q112_04_hideout",        "Gimme Danger: hideout" },
    { "quests/main_quest/prologue/q003_stout",           "prologue: Stout" },
}

-- Every quest path the base game spells out in plain text, read out of
-- `base\journal\cooked_journal.journal` on 2026-08-18. Extracted
-- rather than typed, and NOT the full quest list: paths that live only as
-- hashes do not appear here. Grouped as the journal groups them.
local ALL_QUEST_PATHS = {
    "quests/gyms/gym_ui/quests",
    "quests/main_quest/act_01/q112_01_old_friend",
    "quests/main_quest/act_01/q112_02_industrial_park",
    "quests/main_quest/act_01/q112_04_hideout",
    "quests/main_quest/prologue/q000_corpo/office/07_go_to_hangar/q000_corpo_mp_hangar",
    "quests/main_quest/prologue/q003_stout",
    "quests/minor_activities/badlands/se1/ma_bls_ina_se1_02",
    "quests/minor_activities/badlands/se1/ma_bls_ina_se1_03",
    "quests/minor_activities/badlands/se1/ma_bls_ina_se1_06",
    "quests/minor_activities/badlands/se1/ma_bls_ina_se1_17",
    "quests/minor_activities/badlands/se1/ma_bls_ina_se1_18",
    "quests/minor_activities/badlands/se1/ma_bls_ina_se1_22",
    "quests/minor_activities/badlands/se5/ma_bls_ina_se5_07",
    "quests/minor_activities/city_center/downtown/ma_cct_dtn_03",
    "quests/minor_activities/city_center/downtown/ma_cct_dtn_12",
    "quests/minor_activities/heywood/glen/ma_hey_gle_02",
    "quests/minor_activities/heywood/glen/ma_hey_gle_07",
    "quests/minor_activities/heywood/wellsprings/ma_hey_spr_04",
    "quests/minor_activities/heywood/wellsprings/ma_hey_spr_11",
    "quests/minor_activities/hidden_stash/ma_wat_lch_03",
    "quests/minor_activities/hidden_stash/ma_wat_lch_05",
    "quests/minor_activities/hidden_stash/ma_wbr_nok_01",
    "quests/minor_activities/pacifica/coastview/ma_pac_cvi_08",
    "quests/minor_activities/pacifica/coastview/ma_pac_cvi_10",
    "quests/minor_activities/pacifica/coastview/ma_pac_cvi_12",
    "quests/minor_activities/pacifica/coastview/ma_pac_cvi_13",
    "quests/minor_activities/pacifica/west_wind_estate/ma_pac_wwd_02",
    "quests/minor_activities/santo_domingo/arroyo/ma_std_arr_03",
    "quests/minor_activities/santo_domingo/arroyo/ma_std_arr_06",
    "quests/minor_activities/santo_domingo/arroyo/ma_std_arr_07",
    "quests/minor_activities/santo_domingo/arroyo/ma_std_arr_10",
    "quests/minor_activities/santo_domingo/arroyo/ma_std_arr_14",
    "quests/minor_activities/santo_domingo/rancho_coronado/ma_std_rcr_10",
    "quests/minor_activities/santo_domingo/rancho_coronado/ma_std_rcr_11",
    "quests/minor_activities/santo_domingo/rancho_coronado/ma_std_rcr_12",
    "quests/minor_activities/santo_domingo/rancho_coronado/ma_std_rcr_13",
    "quests/minor_activities/watson/kabuki/ma_wat_kab_02/ma_wat_kab_02/investigate_bridge",
    "quests/minor_activities/watson/kabuki/ma_wat_kab_05",
    "quests/minor_activities/watson/little_china/ma_wat_lch_01",
    "quests/minor_activities/watson/little_china/ma_wat_lch_08",
    "quests/minor_activities/watson/little_china/ma_wat_lch_15",
    "quests/minor_activities/watson/northside_industrial_district/ma_wat_nid_01",
    "quests/minor_activities/watson/northside_industrial_district/ma_wat_nid_02",
    "quests/minor_activities/watson/northside_industrial_district/ma_wat_nid_03",
    "quests/minor_activities/watson/northside_industrial_district/ma_wat_nid_06",
    "quests/minor_activities/watson/northside_industrial_district/ma_wat_nid_10",
    "quests/minor_activities/watson/northside_industrial_district/ma_wat_nid_12",
    "quests/minor_activities/watson/northside_industrial_district/ma_wat_nid_26",
    "quests/minor_activities/watson/northside_industrial_district/ma_wat_nid_27",
    "quests/minor_activities/westbrook/charter_hill/ma_wbr_hil_05",
    "quests/minor_activities/westbrook/japantown/ma_wbr_jpn_07",
    "quests/minor_activities/westbrook/japantown/ma_wbr_jpn_09",
    "quests/minor_activities/westbrook/japantown/ma_wbr_jpn_20",
    "quests/minor_activities/westbrook/north_oak/ma_wbr_nok_03",
    "quests/minor_activities/westbrook/north_oak/ma_wbr_nok_05",
    "quests/minor_quest/ma_bls_ina_se1_07",
    "quests/minor_quest/ma_bls_ina_se1_08",
    "quests/minor_quest/ma_bls_ina_se1_22",
    "quests/minor_quest/ma_cct_dtn_03",
    "quests/minor_quest/ma_cct_dtn_07",
    "quests/minor_quest/ma_hey_spr_04",
    "quests/minor_quest/ma_hey_spr_06",
    "quests/minor_quest/ma_pac_cvi_08",
    "quests/minor_quest/ma_pac_cvi_15",
    "quests/minor_quest/ma_std_arr_06",
    "quests/minor_quest/ma_std_rcr_11",
    "quests/minor_quest/ma_wat_kab_02",
    "quests/minor_quest/ma_wat_kab_08",
    "quests/minor_quest/ma_wat_lch_06",
    "quests/minor_quest/ma_wat_nid_03",
    "quests/minor_quest/ma_wat_nid_15",
    "quests/minor_quest/ma_wat_nid_22",
    "quests/minor_quest/mq001_scorpion",
    "quests/minor_quest/mq002_veterans",
    "quests/minor_quest/mq003_orbitals",
    "quests/minor_quest/mq005_alley",
    "quests/minor_quest/mq006_rollercoaster",
    "quests/minor_quest/mq007_smartgun",
    "quests/minor_quest/mq008_party",
    "quests/minor_quest/mq010_barry",
    "quests/minor_quest/mq012_stud",
    "quests/minor_quest/mq013_punks",
    "quests/minor_quest/mq014_02_second",
    "quests/minor_quest/mq014_03_third",
    "quests/minor_quest/mq014_04_fourth",
    "quests/minor_quest/mq014_zen",
    "quests/minor_quest/mq015_wizardbook",
    "quests/minor_quest/mq016_bartmoss",
    "quests/minor_quest/mq018_writer",
    "quests/minor_quest/mq019_paparazzi",
    "quests/minor_quest/mq021_guide",
    "quests/minor_quest/mq022_ezekiel",
    "quests/minor_quest/mq023_bootleg",
    "quests/minor_quest/mq024_sandra",
    "quests/minor_quest/mq025_psycho_brawl",
    "quests/minor_quest/mq026_conspiracy",
    "quests/minor_quest/mq027_stunts",
    "quests/minor_quest/mq030_melisa",
    "quests/minor_quest/mq032_sacrum",
    "quests/minor_quest/mq035_ozob",
    "quests/minor_quest/mq036_overload",
    "quests/minor_quest/mq037_brendan",
    "quests/minor_quest/mq038_neweridentity",
    "quests/minor_quest/mq040_biosculpt",
    "quests/minor_quest/mq042_nomad",
    "quests/minor_quest/mq044_jakes_vehicle",
    "quests/minor_quest/mq046_cave_vehicle",
    "quests/minor_quest/mq047_ad_vehicle",
    "quests/minor_quest/mq049_edgerunners",
    "quests/side_quest/sq018_jackie",
    "quests/side_quest/sq021_sick_dreams",
    "quests/side_quest/sq025_0_pickup",
    "quests/side_quest/sq025_compensation",
    "quests/side_quest/sq025_delamain",
    "quests/side_quest/sq_q001_wilson",
    "quests/street_stories/badlands/badlands_reward",
    "quests/street_stories/badlands/inland_avenue/sts_bls_ina_02",
    "quests/street_stories/badlands/inland_avenue/sts_bls_ina_03",
    "quests/street_stories/badlands/inland_avenue/sts_bls_ina_04",
    "quests/street_stories/badlands/inland_avenue/sts_bls_ina_05",
    "quests/street_stories/badlands/inland_avenue/sts_bls_ina_06",
    "quests/street_stories/badlands/inland_avenue/sts_bls_ina_07",
    "quests/street_stories/badlands/inland_avenue/sts_bls_ina_08",
    "quests/street_stories/badlands/inland_avenue/sts_bls_ina_08/ina_08_briefing",
    "quests/street_stories/badlands/inland_avenue/sts_bls_ina_09",
    "quests/street_stories/badlands/inland_avenue/sts_bls_ina_11",
    "quests/street_stories/city_center/corpo_plaza/sts_cct_cpz_01",
    "quests/street_stories/city_center/downtown/sts_cct_dtn_02",
    "quests/street_stories/city_center/downtown/sts_cct_dtn_03",
    "quests/street_stories/city_center/downtown/sts_cct_dtn_04",
    "quests/street_stories/city_center/downtown/sts_cct_dtn_05",
    "quests/street_stories/heywood/glen/sts_hey_gle_01",
    "quests/street_stories/heywood/glen/sts_hey_gle_03",
    "quests/street_stories/heywood/glen/sts_hey_gle_04",
    "quests/street_stories/heywood/glen/sts_hey_gle_05",
    "quests/street_stories/heywood/glen/sts_hey_gle_06",
    "quests/street_stories/heywood/heywood_reward",
    "quests/street_stories/heywood/vista_del_rey/sts_hey_rey_01",
    "quests/street_stories/heywood/vista_del_rey/sts_hey_rey_02",
    "quests/street_stories/heywood/vista_del_rey/sts_hey_rey_06",
    "quests/street_stories/heywood/vista_del_rey/sts_hey_rey_08",
    "quests/street_stories/heywood/vista_del_rey/sts_hey_rey_09",
    "quests/street_stories/heywood/wellsprings/sts_hey_spr_01",
    "quests/street_stories/heywood/wellsprings/sts_hey_spr_03",
    "quests/street_stories/heywood/wellsprings/sts_hey_spr_06",
    "quests/street_stories/pacifica/coastview/sts_pac_cvi_02",
    "quests/street_stories/pacifica/west_wind_estates/sts_pac_wwd_05",
    "quests/street_stories/santo_domingo/arroyo/sts_std_arr_01",
    "quests/street_stories/santo_domingo/arroyo/sts_std_arr_03",
    "quests/street_stories/santo_domingo/arroyo/sts_std_arr_05",
    "quests/street_stories/santo_domingo/arroyo/sts_std_arr_06",
    "quests/street_stories/santo_domingo/arroyo/sts_std_arr_10",
    "quests/street_stories/santo_domingo/arroyo/sts_std_arr_11",
    "quests/street_stories/santo_domingo/arroyo/sts_std_arr_12",
    "quests/street_stories/santo_domingo/rancho_coronado/sts_std_rcr_01",
    "quests/street_stories/santo_domingo/rancho_coronado/sts_std_rcr_02",
    "quests/street_stories/santo_domingo/rancho_coronado/sts_std_rcr_02/brief",
    "quests/street_stories/santo_domingo/rancho_coronado/sts_std_rcr_03",
    "quests/street_stories/santo_domingo/rancho_coronado/sts_std_rcr_04",
    "quests/street_stories/santo_domingo/rancho_coronado/sts_std_rcr_05",
    "quests/street_stories/santo_domingo/santo_domingo_reward",
    "quests/street_stories/watson/kabuki/sts_wat_kab_01",
    "quests/street_stories/watson/kabuki/sts_wat_kab_02",
    "quests/street_stories/watson/kabuki/sts_wat_kab_03",
    "quests/street_stories/watson/kabuki/sts_wat_kab_04",
    "quests/street_stories/watson/kabuki/sts_wat_kab_05",
    "quests/street_stories/watson/kabuki/sts_wat_kab_06",
    "quests/street_stories/watson/kabuki/sts_wat_kab_07",
    "quests/street_stories/watson/kabuki/sts_wat_kab_08",
    "quests/street_stories/watson/kabuki/sts_wat_kab_101",
    "quests/street_stories/watson/kabuki/sts_wat_kab_102",
    "quests/street_stories/watson/kabuki/sts_wat_kab_107",
    "quests/street_stories/watson/little_china/sts_wat_lch_01",
    "quests/street_stories/watson/little_china/sts_wat_lch_03",
    "quests/street_stories/watson/little_china/sts_wat_lch_05",
    "quests/street_stories/watson/little_china/sts_wat_lch_06",
    "quests/street_stories/watson/northside_industrial_district/sts_wat_nid_01",
    "quests/street_stories/watson/northside_industrial_district/sts_wat_nid_02",
    "quests/street_stories/watson/northside_industrial_district/sts_wat_nid_03",
    "quests/street_stories/watson/northside_industrial_district/sts_wat_nid_04",
    "quests/street_stories/watson/northside_industrial_district/sts_wat_nid_05",
    "quests/street_stories/watson/northside_industrial_district/sts_wat_nid_06",
    "quests/street_stories/watson/northside_industrial_district/sts_wat_nid_07",
    "quests/street_stories/watson/northside_industrial_district/sts_wat_nid_12",
    "quests/street_stories/watson/watson_reward",
    "quests/street_stories/wesbrook/charter_hill/sts_wbr_hil_01",
    "quests/street_stories/wesbrook/charter_hill/sts_wbr_hil_06",
    "quests/street_stories/wesbrook/charter_hill/sts_wbr_hil_07",
    "quests/street_stories/wesbrook/japan_town/sts_wbr_jpn_01",
    "quests/street_stories/wesbrook/japan_town/sts_wbr_jpn_02",
    "quests/street_stories/wesbrook/japan_town/sts_wbr_jpn_03",
    "quests/street_stories/wesbrook/japan_town/sts_wbr_jpn_05",
    "quests/street_stories/wesbrook/japan_town/sts_wbr_jpn_09",
    "quests/street_stories/wesbrook/japan_town/sts_wbr_jpn_12",
    "quests/street_stories/wesbrook/westbrook_reward",
    "quests/users/przemek_gladkiewicz/ma_wat_kab_06",
    "quests/vehicle_metaquest/arch",
    "quests/vehicle_metaquest/archer_bandit",
    "quests/vehicle_metaquest/archer_quartz",
    "quests/vehicle_metaquest/brennan_apollo",
    "quests/vehicle_metaquest/chevalier_emperor",
    "quests/vehicle_metaquest/chevalier_thrax",
    "quests/vehicle_metaquest/herrera_outlaw",
    "quests/vehicle_metaquest/mahir_supron",
    "quests/vehicle_metaquest/makigai_maimai",
    "quests/vehicle_metaquest/mizutani_shion",
    "quests/vehicle_metaquest/mizutani_shion_nomad",
    "quests/vehicle_metaquest/quadra_turbo",
    "quests/vehicle_metaquest/quadra_type66",
    "quests/vehicle_metaquest/quadra_type66_avenger",
    "quests/vehicle_metaquest/quadra_type66_nomad",
    "quests/vehicle_metaquest/quadra_type66_nomad_ncu",
    "quests/vehicle_metaquest/rayfield_aerondight",
    "quests/vehicle_metaquest/rayfield_caliburn",
    "quests/vehicle_metaquest/thorton_colby",
    "quests/vehicle_metaquest/thorton_colby_nomad",
    "quests/vehicle_metaquest/thorton_colby_pickup",
    "quests/vehicle_metaquest/thorton_galena",
    "quests/vehicle_metaquest/thorton_galena_nomad",
    "quests/vehicle_metaquest/thorton_mackinaw",
    "quests/vehicle_metaquest/villefort_alvarado",
    "quests/vehicle_metaquest/villefort_columbus",
    "quests/vehicle_metaquest/villefort_cortes",
    "quests/vehicle_metaquest/yaiba_kusanagi",
}

local function loadPresets()
    local chunk = loadfile(PRESET_FILE)
    if chunk then
        local ok, data = pcall(chunk)
        if ok and type(data) == "table" then
            for _, saved in ipairs(data) do
                for _, p in ipairs(presets) do
                    if p.name == saved.name and saved.pos then
                        p.pos = saved.pos
                    end
                end
            end
        end
    end
end

local function savePresets()
    local f = io.open(PRESET_FILE, "w")
    if not f then return end
    f:write("return {\n")
    for _, p in ipairs(presets) do
        if p.pos then
            f:write(string.format(
                '  { name = %q, pos = { x = %.3f, y = %.3f, z = %.3f, w = %.3f } },\n',
                p.name, p.pos.x, p.pos.y, p.pos.z, p.pos.w or 1.0))
        end
    end
    f:write("}\n")
    f:close()
end

local function teleportTo(pos)
    local player = Game.GetPlayer()
    if not player or not pos then return end
    Game.GetTeleportationFacility():Teleport(
        player,
        Vector4.new(pos.x, pos.y, pos.z, pos.w or 1.0),
        EulerAngles.new(0, 0, 0))
end

-- Free-form position capture for building the office encounter.
local captureName = "terminal"
local capturedList = {}

local function captureCurrent(name)
    local player = Game.GetPlayer()
    if not player then return end
    local p = player:GetWorldPosition()
    local yaw = 0.0
    local ok, angles = pcall(function() return player:GetWorldOrientation():ToEulerAngles() end)
    if ok and angles then yaw = angles.yaw end
    local entry = { name = name, x = p.x, y = p.y, z = p.z, yaw = yaw }
    table.insert(capturedList, entry)
    -- append to file so nothing is lost if the game crashes
    local f = io.open("captured_positions.txt", "a")
    if f then
        f:write(string.format("%s = { x = %.3f, y = %.3f, z = %.3f, yaw = %.1f }\n",
            name, p.x, p.y, p.z, yaw))
        f:close()
    end
    log(string.format("CAPTURED %s = %.3f, %.3f, %.3f (yaw %.1f)", name, p.x, p.y, p.z, yaw))
end

-- WHAT AM I LOOKING AT, in as much detail as the game will give, to a file.
--
-- There has been a device dump in this menu since the office doors, and it asks
-- DOOR questions: locked, sealed, open. That is the wrong set for a camera, and
-- it only ever wrote to the log, which means reading it back costs a quit (CET
-- buffers its writes) or somebody typing the answers out.
--
-- This one APPENDS TO A FILE, for the same reason captured_positions.txt does:
-- a file is readable straight off disk while the game is still running and
-- nothing has to be transcribed. That is how the sniper on the residence roof
-- was proved to be the base game's rather than ours, in one press.
--
-- WHAT IT IS FOR. Wiring a camera to our guards needs the camera's IDENTITY,
-- and that is the entity id: a world-placed device's id is the hash of its
-- node, which is the thing a device connection points at. A position cannot be
-- pointed at. Everything else here is about telling the states apart that all
-- look like "the camera is not doing anything": off, disabled, unpowered,
-- hacked, glitching, EMP'd, or physically wrecked.
--
-- EVERY PROBE IS WRAPPED, and the list is deliberately wider than any one
-- object will answer. CET cannot be asked whether a method exists and a missing
-- one throws, so each is tried alone and prints "<no such method>" rather than
-- killing the dump. A row that says that is not a failure, it is that this kind
-- of object does not have that idea.
local function dumpLookedAt(name)
    local target = Game.GetTargetingSystem():GetLookAtObject(Game.GetPlayer(), false, false)
    if target == nil then
        log("look: nothing targeted.")
        log("look: a DISABLED device often cannot be looked at, which is itself")
        log("look: an answer: it is switched off rather than absent.")
        return
    end

    local lines = {}
    local function say(fmt, ...)
        local text = select("#", ...) > 0 and string.format(fmt, ...) or fmt
        table.insert(lines, text)
        log("look: " .. text)
    end
    local function head(t) say(""); say("-- %s", t) end
    -- A METHOD. Tried on its own so a missing one costs a line, not the dump.
    local function m(label, fn)
        local ok, v = pcall(fn)
        say("  %-26s %s", label, ok and tostring(v) or "<no such method>")
    end
    -- A FIELD on the persistent state. Many of the interesting flags are fields
    -- rather than getters, and which is which varies by class.
    local function f(obj, key)
        local ok, v = pcall(function() return obj[key] end)
        if ok and v ~= nil then say("  %-26s %s", key, tostring(v)) end
    end

    say("==== %s ====", name ~= "" and name or "looked-at")

    head("identity")
    local p = target:GetWorldPosition()
    say("  %-26s %.3f, %.3f, %.3f", "position", p.x, p.y, p.z)
    m("yaw", function() return target:GetWorldOrientation():ToEulerAngles().yaw end)
    m("class", function() return target:GetClassName() end)
    m("display name", function() return target:GetDisplayName() end)
    -- THE ONE THAT MATTERS FOR WIRING. For anything the world placed, this hash
    -- IS the node's, and it is what a device connection resolves to.
    m("entity id", function()
        local id = target:GetEntityID()
        local ok, h = pcall(function() return id.hash end)
        if ok and h ~= nil then return h end
        return id
    end)
    m("record", function() return target:GetRecord():GetID() end)
    m("is device", function() return target:IsDevice() end)
    m("is puppet", function() return target:IsPuppet() end)

    head("damage")
    m("health", function()
        return Game.GetStatPoolsSystem():GetStatPoolValue(
            target:GetEntityID(), gamedataStatPoolType.Health, false)
    end)
    m("IsDead", function() return target:IsDead() end)
    m("IsBroken", function() return target:IsBroken() end)
    m("IsDestroyed", function() return target:IsDestroyed() end)

    local ok2, ps = pcall(function() return target:GetDevicePS() end)
    if not ok2 or ps == nil then
        say("")
        say("  (no device state on this entity, so it is not a device)")
    else
        head("device")
        m("PS class", function() return ps:GetClassName() end)
        m("device name", function() return ps:GetDeviceName() end)
        -- THE LADDER. A device walks DISABLED -> OFF -> ON and our script can
        -- push it up: the office doors have done exactly that since 1.1.3. What
        -- no script undoes is a wrecked one, which is why damage is above.
        m("deviceState", function() return ps:GetDeviceState() end)
        m("IsON", function() return ps:IsON() end)
        m("IsOFF", function() return ps:IsOFF() end)
        m("IsDisabled", function() return ps:IsDisabled() end)
        m("IsUnpowered", function() return ps:IsUnpowered() end)
        m("IsBroken", function() return ps:IsBroken() end)
        m("durability", function() return ps:GetDurabilityState() end)
        m("IsAttached", function() return ps:IsAttachedToGame() end)
        m("IsInteractive", function() return ps:IsInteractive() end)

        head("hacking")
        m("wasQuickHacked", function() return ps:WasQuickHacked() end)
        m("IsQuickHacksExposed", function() return ps:IsQuickHacksExposed() end)
        m("HasNetworkBackdoor", function() return ps:HasNetworkBackdoor() end)
        m("IsBreached", function() return ps:IsBreached() end)
        m("IsPlayerAuthorized", function() return ps:IsPlayerAuthorized() end)
        m("IsGlitching", function() return ps:IsGlitching() end)
        m("IsUnderEMP", function() return ps:IsUnderEMPEffect() end)
        m("personalLinkStatus", function() return ps:GetPersonalLinkStatus() end)

        head("security")
        m("securityAccessLevel", function() return ps:GetSecurityAccessLevel() end)
        m("securityAreaType", function() return ps:GetSecurityAreaType() end)
        m("IsPlayerInside", function() return ps:IsPlayerInside() end)
        m("IsControlledByPlayer", function() return ps:IsControlledByThePlayer() end)

        -- Door questions, kept because the doors are still a live part of this
        -- gig and the old probe answered them.
        head("door")
        m("IsLocked", function() return ps:IsLocked() end)
        m("IsSealed", function() return ps:IsSealed() end)
        m("IsOpen", function() return ps:IsOpen() end)

        -- AND THE RAW FIELDS. Most of the flags that separate "hacked" from
        -- "off" from "wrecked" live on the persistent state as fields rather
        -- than getters, and which is which varies by class. Anything nil is
        -- skipped, so this prints only what this object actually carries.
        head("raw state (only what exists is listed)")
        for _, key in ipairs({
            "deviceState", "cachedDeviceState", "durabilityState",
            "isGlitching", "isUnderEMPEffect", "wasQuickHacked",
            "wasRevealedInNetworkPing", "isBeingScanned", "isScanned",
            "hasNetworkBackdoor", "hasPersonalLinkSlot", "isKeyloggerInstalled",
            "personalLinkStatus", "hackingMinigameState", "minigameAttempt",
            "disableQuickHacks", "exposeQuickHacks", "isControlledByThePlayer",
            "isInitialized", "isAttachedToGame", "isLogicReady",
            "securityAccessLevel", "securityAreaType", "isTimedTurnOff",
            "juryrigTrapState", "isLockedViaSequencer", "isRestarting",
            "distractExecuted", "distractionTimeCompleted", "markAsQuest",
            "isInteractive", "hasBeenScavenged", "isPlayerInside",
            "activationState", "backdoorBreachDifficulty", "deviceName",
            "isHighlightedInFocusMode", "blockSecurityWakeUp",
            "hasThisAreaReceivedCombatNotification", "isUnpowered",
        }) do
            f(ps, key)
        end
    end

    local fh = io.open("looked_at.txt", "a")
    if fh then
        for _, line in ipairs(lines) do
            fh:write(line .. "\n")
        end
        fh:write("\n")
        fh:close()
    end
end

-- THE DEVICE-ACTION HELPERS ARE GONE, 2026-08-25, with the camera work they
-- served. What they established is kept in the docs rather than in code:
--
--   gotcha 82  a base-game device's runtime id is the FNV1a64 of its NodeRef,
--              so any of them can be addressed without touching it in game
--   gotcha 83  the full menu of what a camera accepts, the DISABLED -> OFF ->
--              ON ladder, one action per frame, and that there is no repair
--              action at all
--
-- `dumpLookedAt` above stays. It only reads.

registerForEvent("onInit", function()
    loadPresets()
end)

registerForEvent("onOverlayOpen", function() visible = true end)
registerForEvent("onOverlayClose", function() visible = false end)



registerForEvent("onDraw", function()
    if not visible then return end
    if not ImGui.Begin("Negative Balance [DEV]") then
        ImGui.End()
        return
    end

    local qs = Game.GetQuestsSystem()

    -- COLLAPSED BY DEFAULT, 2026-08-25. Sixty-odd rows with two buttons each,
    -- and everything worth reading during a playtest sits below it. A header
    -- costs one click on the rare visit that sets a fact by hand, and gives
    -- back most of a screen on every other one.
    if ImGui.CollapsingHeader("Quest facts (click to open)") then
        for _, fact in ipairs(FACTS) do
            local value = qs:GetFactStr(fact)
            ImGui.Text(string.format("%-24s = %d", fact, value))
            ImGui.SameLine(280)
            if ImGui.SmallButton("0##" .. fact) then qs:SetFactStr(fact, 0) end
            ImGui.SameLine()
            if ImGui.SmallButton("1##" .. fact) then qs:SetFactStr(fact, 1) end
        end
    end

    ImGui.Spacing()
    ImGui.Text("Quest")
    ImGui.Separator()
    if ImGui.Button("START GIG (quest-driven, real pacing)") then
        Game.GetQuestsSystem():SetFactStr("cc_g01_start", 1)
        log("cc_g01_start=1, quest phase should take over: Elena texts with delays")
    end

    -- BOTH DEV SHORTCUT BUTTONS REMOVED 2026-08-14. Neither ever worked:
    -- they entered a questSceneNodeDefinition that the main chain also
    -- enters, and across all 358 shipped street-story questphases a scene
    -- node input socket NEVER has more than one source. The epilogue one
    -- had been in since 2026-08-12 and nobody had needed it badly enough
    -- to notice. Full reasoning in tools/gig01/gen_questphase.py.
    ImGui.TextDisabled("The questphase waits on this fact, then runs the full intro flow")
    ImGui.TextDisabled("This button BYPASSES the in-game gate (Gig01_Start.reds) entirely")

    ImGui.Spacing()
    ImGui.Text("Journal (Elena), manual/debug only")
    ImGui.Separator()
    if ImGui.Button("Dump Elena entry states") then
        local jm = Game.GetJournalManager()
        for _, item in ipairs(ELENA_PATHS) do
            local path, cls = item[1], item[2]
            local ok, err = pcall(function()
                local entry = jm:GetEntryByString(path, cls)
                if entry == nil then
                    log(path .. " -> NOT FOUND")
                else
                    local ok2, state = pcall(function() return jm:GetEntryState(entry) end)
                    log(path .. " -> exists, state=" .. (ok2 and tostring(state) or ("? " .. tostring(state))))
                end
            end)
            if not ok then log(path .. " -> ERROR: " .. tostring(err)) end
        end
    end
    -- WHICH contact the phone actually resolves for Nix, and what avatar it
    -- reports. Everything checkable offline says his portrait should already
    -- show: PhoneAvatars.Avatar_Nix exists (probe, 2026-08-12), gig01.journal
    -- sets it on his contact, showAvatar is true on every call, and
    -- RefreshView shows the portrait in Audiocall mode when it is. So the fault
    -- is somewhere only the running game can see.
    --
    -- The prime suspect is a DUPLICATE: we merge our own contacts/nix over the
    -- base game's, and GetIncomingContact takes the first id match while
    -- walking GetContacts(). If two exist, this prints both.
    if ImGui.Button("*** DUMP: phone contacts (avatar + callable) ***") then
        local jm = Game.GetJournalManager()

        -- Path lookup first, because it is the idiom already proven to work in
        -- this menu (the Elena dump above uses it) and it needs no structs.
        -- The first attempt called GetContacts(list, true), which failed with
        -- "requires 1 parameter(s)": its signature is
        -- GetContacts(context: JournalRequestContext, out entries), and CET
        -- turns the `out` into a return value, so the only real argument is a
        -- context struct.
        for _, id in ipairs({ "contacts/nix", "contacts/elena_ortega" }) do
            local ok, err = pcall(function()
                local e = jm:GetEntryByString(id, "gameJournalContact")
                if e == nil then
                    log(id .. " -> NOT FOUND")
                    return
                end
                local nm, av, callable, state = "?", "?", "?", "?"
                pcall(function() nm = tostring(e:GetLocalizedName(jm)) end)
                pcall(function() av = tostring(e:GetAvatarID(jm)) end)
                pcall(function() callable = tostring(e:IsCallable(jm)) end)
                pcall(function() state = tostring(jm:GetEntryState(e)) end)
                log(string.format("%s -> name=%s | avatar=%s | callable=%s | state=%s",
                                  id, nm, av, callable, state))
            end)
            if not ok then log(id .. " -> ERROR: " .. tostring(err)) end
        end

        -- Then the full walk, which is the only thing that can reveal a
        -- DUPLICATE contact (ours merged alongside the base game's rather than
        -- over it). Best effort: if the context struct cannot be built from
        -- Lua, the lookups above still answer the main question.
        local ok, err = pcall(function()
            local ctx = JournalRequestContext.new()
            ctx.stateFilter = JournalRequestStateFilter.new()
            ctx.stateFilter.active = true
            ctx.stateFilter.inactive = true
            ctx.stateFilter.succeeded = true
            ctx.stateFilter.failed = true
            local list = jm:GetContacts(ctx)
            log("all contacts: " .. tostring(#list))
            for _, e in ipairs(list) do
                local cid = tostring(e:GetId())
                if string.find(string.lower(cid), "nix")
                    or string.find(string.lower(cid), "elena") then
                    local av = "?"
                    pcall(function() av = tostring(e:GetAvatarID(jm)) end)
                    log(string.format("  MATCH %-24s avatar=%s", cid, av))
                end
            end
        end)
        if not ok then log("full contact walk unavailable: " .. tostring(err)) end
        log("contact dump done")
    end

    if ImGui.Button("Activate Elena intro thread (all at once)") then
        local jm = Game.GetJournalManager()
        for _, item in ipairs(ELENA_PATHS) do
            local path, cls = item[1], item[2]
            local ok, err = pcall(function()
                jm:ChangeEntryState(path, cls, "Active", "Notify")
            end)
            if not ok then log("activate " .. path .. " FAILED: " .. tostring(err)) end
        end
        log("Elena intro: activation pass done")
    end
    if ImGui.Button("Step Elena thread (paced preview)") then
        local jm = Game.GetJournalManager()
        elenaStep = elenaStep or 0
        if elenaStep >= #ELENA_PATHS then
            log("thread finished; use Reset to replay")
        else
            while elenaStep < #ELENA_PATHS do
                elenaStep = elenaStep + 1
                local path, cls = ELENA_PATHS[elenaStep][1], ELENA_PATHS[elenaStep][2]
                pcall(function() jm:ChangeEntryState(path, cls, "Active", "Notify") end)
                -- stop after activating a choice group + its reply option(s)
                if cls == "gameJournalPhoneChoiceGroup" then
                    while elenaStep < #ELENA_PATHS
                        and ELENA_PATHS[elenaStep + 1][2] == "gameJournalPhoneChoiceEntry" do
                        elenaStep = elenaStep + 1
                        pcall(function()
                            jm:ChangeEntryState(ELENA_PATHS[elenaStep][1],
                                ELENA_PATHS[elenaStep][2], "Active", "Notify")
                        end)
                    end
                    log("paused at reply choice, answer in phone, then Step again")
                    break
                end
            end
            if elenaStep >= #ELENA_PATHS then log("thread complete") end
        end
    end
    ImGui.SameLine()
    if ImGui.SmallButton("Reset step") then elenaStep = 0 end
    if ImGui.Button("Activate gig + first objective") then
        local ok, err = pcall(function()
            local jm = Game.GetJournalManager()
            jm:ChangeEntryState("quests/street_stories/cc_g01_negative_balance",
                "gameJournalQuest", "Active", "Notify")
            jm:ChangeEntryState("quests/street_stories/cc_g01_negative_balance/phase_main",
                "gameJournalQuestPhase", "Active", "Notify")
            jm:ChangeEntryState("quests/street_stories/cc_g01_negative_balance/phase_main/obj_office",
                "gameJournalQuestObjective", "Active", "Notify")
            log("gig activated")
        end)
        if not ok then log("gig activate failed: " .. tostring(err)) end
    end
    if ImGui.Button("*** FULL PIN DIAGNOSIS (one click, dumps everything) ***") then
        local jm = Game.GetJournalManager()
        local ms = Game.GetMappinSystem()
        local Q = "quests/street_stories/cc_g01_negative_balance"
        local POI = "points_of_interest/street_stories/cc_g01_negative_balance"

        local function try(label, fn)
            local ok, res = pcall(fn)
            if ok then
                log(label .. " = " .. tostring(res))
            else
                log(label .. " ERR: " .. tostring(res))
            end
            return ok and res or nil
        end

        log("================ PIN DIAGNOSIS ================")

        -- 1. our journal tree: existence, state, hash
        local ours = {
            { Q, "gameJournalQuest" },
            { Q .. "/phase_main", "gameJournalQuestPhase" },
            { Q .. "/phase_main/obj_office", "gameJournalQuestObjective" },
            { Q .. "/phase_main/obj_office/pin_office", "gameJournalQuestMapPin" },
            { Q .. "/phase_main/obj_epilogue", "gameJournalQuestObjective" },
            { Q .. "/phase_main/obj_epilogue/pin_coyote", "gameJournalQuestMapPin" },
            { POI, "gameJournalPointOfInterestMappin" },
        }
        for _, p in ipairs(ours) do
            local ok, err = pcall(function()
                local e = jm:GetEntryByString(p[1], p[2])
                if e == nil then
                    log("OURS  MISSING   " .. p[1])
                else
                    local st = jm:GetEntryState(e)
                    local h = jm:GetEntryHash(e)
                    log(string.format("OURS  %-10s h=%-12d %s", tostring(st), h, p[1]))
                end
            end)
            if not ok then log("OURS  ERR " .. p[1] .. ": " .. tostring(err)) end
        end

        -- 2. distance + positions for OUR objective
        pcall(function()
            local obj = jm:GetEntryByString(Q .. "/phase_main/obj_office", "gameJournalQuestObjective")
            if obj then
                try("OURS  distanceToNearestMappin", function() return jm:GetDistanceToNearestMappin(obj) end)
                local h = jm:GetEntryHash(obj)
                local found, positions = ms:GetQuestMappinPositionsByObjective(h)
                local n = (type(positions) == "table") and #positions or -1
                log(string.format("OURS  GetQuestMappinPositionsByObjective(%d) found=%s count=%d", h, tostring(found), n))
                if type(positions) == "table" then
                    for i, p in ipairs(positions) do
                        log(string.format("        our pos %d: %.1f %.1f %.1f", i, p.x, p.y, p.z))
                    end
                end
            end
        end)

        -- 3. same data for the TRACKED base-game quest (the control)
        pcall(function()
            local tracked = jm:GetTrackedEntry()
            if tracked == nil then
                log("BASE  nothing tracked, track a BASE GAME gig and click again for comparison")
                return
            end
            local h = jm:GetEntryHash(tracked)
            log(string.format("BASE  tracked entry hash=%d state=%s", h, tostring(jm:GetEntryState(tracked))))
            try("BASE  distanceToNearestMappin", function() return jm:GetDistanceToNearestMappin(tracked) end)
            local found, positions = ms:GetQuestMappinPositionsByObjective(h)
            local n = (type(positions) == "table") and #positions or -1
            log(string.format("BASE  GetQuestMappinPositionsByObjective found=%s count=%d", tostring(found), n))
            if type(positions) == "table" then
                for i, p in ipairs(positions) do
                    log(string.format("        base pos %d: %.1f %.1f %.1f", i, p.x, p.y, p.z))
                end
            end
            -- what does a working base pin's parent chain look like?
            local parent = jm:GetParentEntry(tracked)
            if parent then
                log("BASE  parent hash=" .. tostring(jm:GetEntryHash(parent)))
            end
        end)

        -- 4. player position for sanity (distance to our office target)
        pcall(function()
            local wp = Game.GetPlayer():GetWorldPosition()
            local dx, dy = wp.x - (-177.761), wp.y - (-1472.829)
            log(string.format("PLAYER at %.1f %.1f %.1f (%.0fm from office target)", wp.x, wp.y, wp.z,
                math.sqrt(dx * dx + dy * dy)))
        end)

        log("================ END DIAGNOSIS ================")
    end

    if ImGui.Button("TEST A: activate the PIN entry itself") then
        -- Hypothesis: mappins only spawn for pin entries whose journal state is
        -- Active. Our quest phase activates quest/phase/objective but never the
        -- gameJournalQuestMapPin child.
        local jm = Game.GetJournalManager()
        local paths = {
            { "quests/street_stories/cc_g01_negative_balance/phase_main/obj_office/pin_office",
              "gameJournalQuestMapPin" },
            { "points_of_interest/street_stories/cc_g01_negative_balance",
              "gameJournalPointOfInterestMappin" },
        }
        for _, p in ipairs(paths) do
            local ok, err = pcall(function()
                jm:ChangeEntryState(p[1], p[2], "Active", "Notify")
                log("TEST A: activated " .. p[1])
            end)
            if not ok then log("TEST A failed for " .. p[1] .. ": " .. tostring(err)) end
        end
        log("TEST A done, open the map and look for the pin")
    end
    if ImGui.Button("CONTROL: positions for the TRACKED objective") then
        -- Track a BASE GAME quest first, then click this. Tells us whether the
        -- out-array marshals at all (control) vs. our objective returning 0.
        local ok, err = pcall(function()
            local jm = Game.GetJournalManager()
            local tracked = jm:GetTrackedEntry()
            if tracked == nil then
                log("CONTROL: nothing tracked, track a base game quest first")
                return
            end
            local h = jm:GetEntryHash(tracked)
            local found, positions = Game.GetMappinSystem():GetQuestMappinPositionsByObjective(h)
            local count = (type(positions) == "table") and #positions or -1
            log(string.format("CONTROL: tracked hash=%d -> found=%s, positions=%d", h, tostring(found), count))
            if type(positions) == "table" then
                for i, p in ipairs(positions) do
                    log(string.format("   base pos %d: %.1f, %.1f, %.1f", i, p.x, p.y, p.z))
                end
            end
        end)
        if not ok then log("CONTROL failed: " .. tostring(err)) end
    end
    if ImGui.Button("PROBE: cooked positions for obj_office") then
        local ok, err = pcall(function()
            local found, positions = Game.GetMappinSystem():GetQuestMappinPositionsByObjective(631112275)
            log("GetQuestMappinPositionsByObjective(obj_office) -> " .. tostring(found))
            if type(positions) == "table" then
                log("positions count: " .. tostring(#positions))
                for i, p in ipairs(positions) do
                    log(string.format("  pos %d: %.1f, %.1f, %.1f", i, p.x, p.y, p.z))
                end
            else
                log("positions (non-table): " .. tostring(positions))
            end
        end)
        if not ok then log("probe failed: " .. tostring(err)) end
    end
    if ImGui.Button("Kill scripted fallback pins (identify visible pin)") then
        local ok, err = pcall(function()
            Game.GetQuestsSystem():SetFactStr("cc_g01_office_reached", 1)
            log("office_reached=1 set -> scripted office pin should unregister within 3s. If a pin REMAINS at the office, it's the cooked one.")
        end)
        if not ok then log("kill failed: " .. tostring(err)) end
    end
    if ImGui.Button("TEST: activate Californication pin (throwaway save!)") then
        local jm = Game.GetJournalManager()
        local ok, err = pcall(function()
            jm:ChangeEntryState("quests/main_quest/prologue/nq_californication",
                "gameJournalQuest", "Active", "Notify")
            jm:ChangeEntryState("quests/main_quest/prologue/nq_californication/californication",
                "gameJournalQuestPhase", "Active", "Notify")
            jm:ChangeEntryState("quests/main_quest/prologue/nq_californication/californication/01_go_to_overlook",
                "gameJournalQuestObjective", "Active", "Notify")
            log("californication test objective activated, check journal for km + map pin near Rancho Coronado dam")
        end)
        if not ok then log("cali test failed: " .. tostring(err)) end
    end
    if ImGui.Button("Dump pin entries + hashes") then
        local jm = Game.GetJournalManager()
        local probes = {
            { "quests/street_stories/cc_g01_negative_balance", "gameJournalQuest" },
            { "quests/street_stories/cc_g01_negative_balance/phase_main", "gameJournalQuestPhase" },
            { "quests/street_stories/cc_g01_negative_balance/phase_main/obj_office", "gameJournalQuestObjective" },
            { "quests/street_stories/cc_g01_negative_balance/phase_main/obj_office/pin_office", "gameJournalQuestMapPin" },
            { "points_of_interest/street_stories/cc_g01_negative_balance", "gameJournalPointOfInterestMappin" },
        }
        for _, p in ipairs(probes) do
            local ok, err = pcall(function()
                local entry = jm:GetEntryByString(p[1], p[2])
                if entry == nil then
                    log("MISS " .. p[1])
                else
                    local ok2, hash = pcall(function() return jm:GetEntryHash(entry) end)
                    log("OK   " .. p[1] .. "  hash=" .. tostring(ok2 and hash or "?"))
                end
            end)
            if not ok then log("ERR  " .. p[1] .. " -> " .. tostring(err)) end
        end
    end
    ImGui.TextDisabled("(watch CET console for [NB] output)")

    if ImGui.Button("DUMP: Arasaka character records (for guard spawning)") then
        local ok, err = pcall(function()
            local records = TweakDB:GetRecords("gamedataCharacter_Record")
            local n = 0
            for _, rec in ipairs(records) do
                local id = tostring(rec:GetID())
                if id:lower():find("arasaka") or id:lower():find("secur") then
                    log("REC " .. id)
                    n = n + 1
                    if n >= 80 then break end
                end
            end
            log("record dump done, matches: " .. tostring(n))
        end)
        if not ok then log("record dump failed: " .. tostring(err)) end
    end

    -- Which Character record is the real Mama Welles? TweakDB stores
    -- "mama_welles" as a bare name with no group, so it cannot be confirmed by
    -- reading the files offline. Enumerate instead of guessing: this lists every
    -- character record whose id mentions her, so the exact one can go into
    -- ResolveMamaRecord in Gig01_Encounter.reds.
    if ImGui.Button("*** DUMP: Mama Welles character records ***") then
        local ok, err = pcall(function()
            local records = TweakDB:GetRecords("gamedataCharacter_Record")
            local n = 0
            for _, rec in ipairs(records) do
                local id = tostring(rec:GetID())
                local low = id:lower()
                if low:find("welles") or low:find("mama") or low:find("coyote") then
                    log("MAMA-CANDIDATE " .. id)
                    n = n + 1
                end
            end
            log("mama dump done, matches: " .. tostring(n))

            -- Also report straight up whether the ids the mod currently tries
            -- actually exist, so a nil result is unambiguous.
            for _, id in ipairs({ "Character.mama_welles", "Character.sq018_mama_welles",
                                  "Character.q003_mama_welles", "Character.mama_welles_coyote" }) do
                log("CANDIDATE " .. id .. " exists=" .. tostring(TweakDB:GetRecord(id) ~= nil))
            end
        end)
        if not ok then log("mama dump failed: " .. tostring(err)) end
    end

    -- Which PhoneAvatars record actually exists for Nix.
    --
    -- gig01.journal already gives his contact avatarID PhoneAvatars.Avatar_Nix,
    -- and RefreshView (hudPhoneAvatarController:176) shows the contact portrait
    -- in Audiocall mode whenever showAvatar is set - which it is. So the wiring
    -- is right and the portrait SHOULD be his. If it comes up as UNKNOWN CALLER
    -- then that record id is wrong, and RequestAvatarOrUnknown falls back
    -- silently, which is indistinguishable from "not implemented".
    --
    -- TweakDBIDs are case-sensitive and not discoverable from the files on disk,
    -- so this probes candidates instead of guessing one. Whichever prints FOUND
    -- goes into gen_journal.py.
    if ImGui.Button("*** PROBE: PhoneAvatars art (atlas + part) ***") then
        -- A phone avatar is a UIIcon_Record: AtlasResourcePath() (the .inkatlas)
        -- plus AtlasPartName() (which sprite inside it). The record EXISTING is
        -- not enough - RequestAvatarOrUnknown only falls back to Avatar_Unknown
        -- when the TweakDBID is INVALID, and ours is valid, so a valid id with
        -- unusable art draws the broken red square seen in game.
        --
        -- So compare Nix against avatars that are known to render. If his atlas
        -- or part is blank, that is the answer. If it looks perfectly normal,
        -- the fault is elsewhere and the offer to trigger a real vanilla
        -- Nix call becomes the next step.
        local ids = {
            "PhoneAvatars.Avatar_Nix",
            "PhoneAvatars.Avatar_Unknown",   -- control: Elena uses it, renders
            "PhoneAvatars.Avatar_Regina",    -- control: a fixer, definitely art
            "PhoneAvatars.Avatar_Johnny",
            "PhoneAvatars.Avatar_Wakako",
        }
        for _, id in ipairs(ids) do
            local ok, err = pcall(function()
                local r = TweakDB:GetRecord(id)
                if r == nil then
                    log(string.format("avatar %-32s MISSING RECORD", id))
                    return
                end
                local atlas, part = "?", "?"
                pcall(function() atlas = tostring(r:AtlasResourcePath()) end)
                pcall(function() part = tostring(r:AtlasPartName()) end)
                log(string.format("avatar %-32s atlas=%s part=%s", id, atlas, part))
            end)
            if not ok then
                -- Record getters can be unavailable from Lua; flats always work.
                local a = TweakDB:GetFlat(id .. ".atlasResourcePath")
                local p = TweakDB:GetFlat(id .. ".atlasPartName")
                log(string.format("avatar %-32s (flat) atlas=%s part=%s",
                                  id, tostring(a), tostring(p)))
            end
        end
        log("avatar art probe done")
    end

    -- Whoever V is aiming at: the definitive answer if the real Mama Welles is
    -- in the bar. Look straight at her and click.
    if ImGui.Button("*** DUMP: record of the NPC I'm looking at ***") then
        local ok, err = pcall(function()
            local target = Game.GetTargetingSystem():GetLookAtObject(Game.GetPlayer(), false, false)
            if target == nil then
                log("look-at: nothing targeted")
                return
            end
            log("look-at display name: " .. tostring(target:GetDisplayName()))
            local rec = target:GetRecord()
            if rec ~= nil then
                log("look-at RECORD ID: " .. tostring(rec:GetID()))
            else
                log("look-at: entity has no character record")
            end
        end)
        if not ok then log("look-at dump failed: " .. tostring(err)) end
    end

    -- THE DOOR PROBE. The Arasaka office doors ship DISABLED (see the doors
    -- facts above) and the redscript that switches them on did nothing on a
    -- pre-"Gimme Danger" save. These two buttons split that into the two
    -- questions it actually is, without a game restart between them:
    --
    --   DUMP  what state is this door really in, and does it even have a
    --         DoorControllerPS we can reach?
    --   FORCE does ActionQuestForceEnabled open it when it is called by hand?
    --
    -- If DUMP says DISABLED and FORCE opens the door, the action is right and
    -- the redscript HOOK is what is not firing. If FORCE does nothing either,
    -- the action is wrong and the hook is innocent. One or the other, and no
    -- guessing between them.
    if ImGui.Button("*** DUMP: the DEVICE I'm looking at ***") then
        local ok, err = pcall(function()
            local target = Game.GetTargetingSystem():GetLookAtObject(Game.GetPlayer(), false, false)
            if target == nil then
                log("device-dump: nothing targeted (a DISABLED device may not be look-at-able)")
                return
            end
            local p = target:GetWorldPosition()
            log(string.format("device-dump: class=%s at %.3f, %.3f, %.3f",
                tostring(target:GetClassName()), p.x, p.y, p.z))

            local ok2, ps = pcall(function() return target:GetDevicePS() end)
            if not ok2 or ps == nil then
                log("device-dump: no device PS on this entity - it is not a device")
                return
            end
            log("device-dump: PS class = " .. tostring(ps:GetClassName()))
            local function probe(name, fn)
                local o, v = pcall(fn)
                log(string.format("device-dump:   %-12s %s", name, o and tostring(v) or "<no such method>"))
            end
            probe("deviceState", function() return ps:GetDeviceState() end)
            probe("IsDisabled", function() return ps:IsDisabled() end)
            probe("IsLocked", function() return ps:IsLocked() end)
            probe("IsSealed", function() return ps:IsSealed() end)
            probe("IsOpen", function() return ps:IsOpen() end)
            probe("IsAttached", function() return ps:IsAttachedToGame() end)
        end)
        if not ok then log("device-dump failed: " .. tostring(err)) end
    end

    -- The compound-door mechanism (Gig01_OfficeDoors.reds, gotcha 83) as a
    -- button: DISABLED -> ForceEnabled -> OFF -> ForceON -> ON. Actions are
    -- DEFERRED, so this sends ONE step per press and prints the state it
    -- read; press again about a second later until it says ON. Works on
    -- whatever door V is looking at. Scouting tool: it changes a base-game
    -- device, so use it to judge rooms, not on doors a quest is mid-using.
    if ImGui.Button("*** DOOR: one step towards ON (look at it) ***") then
        local ok, err = pcall(function()
            local target = Game.GetTargetingSystem():GetLookAtObject(Game.GetPlayer(), false, false)
            if target == nil then
                log("door: nothing targeted (a DISABLED door can be hard to target - stand close, aim at the frame)")
                return
            end
            local ok2, ps = pcall(function() return target:GetDevicePS() end)
            if not ok2 or ps == nil then
                log("door: not a device")
                return
            end
            local state = tostring(ps:GetDeviceState())
            if ps:IsDisabled() then
                ps:ExecutePSAction(ps:ActionQuestForceEnabled(), ps)
                log("door: was " .. state .. ", sent ForceEnabled - press again in a second")
            else
                ps:ExecutePSAction(ps:ActionQuestForceON(), ps)
                log("door: was " .. state .. ", sent ForceON - if still shut, press once more")
            end
        end)
        if not ok then log("door force failed: " .. tostring(err)) end
    end

    -- The door trace lives in facts, and facts are only visible in this window,
    -- which means reading them back costs somebody typing them out. Put them in
    -- the log file instead, where they can be read alongside the device dump
    -- they belong with.
    if ImGui.Button("*** LOG the door trace facts ***") then
        local ok, err = pcall(function()
            local qs = Game.GetQuestsSystem()
            local names = {
                "cc_g01_accepted",
                "cc_g01_doors_opened",
                "cc_g01_dbg_door_state",
                "cc_g01_dbg_door_giveup",
            }
            for _, n in ipairs(names) do
                log(string.format("door-trace: %-26s %d", n, qs:GetFactStr(n)))
            end
        end)
        if not ok then log("door-trace failed: " .. tostring(err)) end
    end

    if ImGui.Button("*** LOG: which gating quests has this save done ***") then
        local ok, err = pcall(function()
            local jm = Game.GetJournalManager()
            log("quest-state: ==== gating quests, this save ====")
            for _, item in ipairs(GATING_QUESTS) do
                local path, label = item[1], item[2]
                local ok2, res = pcall(function()
                    local e = jm:GetEntryByString(path, "gameJournalQuest")
                    if e == nil then return "NOT FOUND (path absent, not proof of anything)" end
                    return tostring(jm:GetEntryState(e))
                end)
                log(string.format("quest-state: %-46s %-44s %s",
                                  label, path, ok2 and res or ("ERROR " .. tostring(res))))
            end
            log("quest-state: ==== end ====")
        end)
        if not ok then log("quest-state failed: " .. tostring(err)) end
    end

    -- ...and the bulk version, for when the curated list above does not contain
    -- the quest that turns out to matter. 224 lines, so it is deliberately a
    -- separate button rather than something that runs every time.
    if ImGui.Button("LOG: every quest path the journal spells out (224)") then
        local ok, err = pcall(function()
            local jm = Game.GetJournalManager()
            local n, seen = 0, 0
            log("quest-dump: ==== every plain-text quest path, and its state ====")
            for _, path in ipairs(ALL_QUEST_PATHS) do
                local ok2, res = pcall(function()
                    local e = jm:GetEntryByString(path, "gameJournalQuest")
                    if e == nil then return nil end
                    return tostring(jm:GetEntryState(e))
                end)
                n = n + 1
                if ok2 and res ~= nil then
                    seen = seen + 1
                    log(string.format("quest-dump: %-64s %s", path, res))
                end
            end
            log(string.format("quest-dump: ==== %d of %d paths resolved to an entry ====", seen, n))
        end)
        if not ok then log("quest-dump failed: " .. tostring(err)) end
    end

    -- ESCALATING FORCE, and the escalation is the point.
    --
    -- ONE ACTION PER BUTTON, and the reason is a trap the escalating version
    -- walked straight into (00:10 on 2026-08-16).
    --
    -- That version sent five actions in one frame and read the state after each.
    -- Every ExecutePSAction read back unchanged and only the direct
    -- SetDeviceState moved it, which looks like proof that the actions do
    -- nothing. It is not. **ExecutePSAction is deferred**: the redscript hook
    -- had already sent ForceEnabled to these doors at attach and read DISABLED
    -- back immediately (`cc_g01_dbg_door_after` = 1), yet by the time anyone
    -- looked at the door it was OFF. So ForceEnabled DID land, one frame or more
    -- later, and took the door from DISABLED to OFF.
    --
    -- A read in the same frame as the action therefore measures nothing, and
    -- five actions in one frame race each other. The door that ladder was run on
    -- ended up reporting EDeviceStatus 4294967294, which is not a state at all.
    --
    -- One action per click, and the DUMP button on the next click is what reads
    -- the result. Slower by two clicks, and it is the difference between an
    -- answer and an artefact.
    local function forceButton(label, name, fn)
        if ImGui.Button(label) then
            local ok, err = pcall(function()
                local target = Game.GetTargetingSystem():GetLookAtObject(Game.GetPlayer(), false, false)
                if target == nil then
                    log("device-force: nothing targeted")
                    return
                end
                local ps = target:GetDevicePS()
                if ps == nil then
                    log("device-force: no device PS")
                    return
                end
                log(string.format("device-force: %s, state before = %s", name, tostring(ps:GetDeviceState())))
                fn(ps)
                log("device-force: " .. name .. " sent. DUMP again to read where it settled.")
            end)
            if not ok then log("device-force failed: " .. tostring(err)) end
        end
    end

    forceButton("*** FORCE 1: ForceEnabled only ***", "ForceEnabled",
        function(ps) ps:ExecutePSAction(ps:ActionQuestForceEnabled(), ps) end)
    forceButton("*** FORCE 2: ForceON only ***", "ForceON",
        function(ps) ps:ExecutePSAction(ps:ActionQuestForceON(), ps) end)
    forceButton("*** FORCE 3: SetDeviceState(ON) only ***", "SetDeviceState(ON)",
        function(ps) ps:SetDeviceState(Enum.new("EDeviceStatus", "ON")) end)

    -- ============ VEHICLE LOCK LAB (docs/backlog.md 16) ============
    --
    -- Johnny's three free-roaming beats stage him at a fixed point in the world,
    -- so a V who is riding leaves him behind and hears the rest of the line from
    -- a spot that is receding. The design under test: refuse to ring while V is
    -- mounted, and block mounting from pickup until the beat ends, so a beat
    -- always plays to a V on foot.
    --
    -- Three things have to be measured in game before any of it is written, and
    -- none of them is answerable from the files on disk.
    --
    -- 1. WHICH QUERY ANSWERS "V IS MOUNTED". 2.31's script bundle holds several
    -- candidate spellings. The readout below evaluates all of them every frame,
    -- so the one that goes into redscript is measured rather than assumed. Open
    -- the overlay and get on a bike while watching it: a row that reads the
    -- same standing and riding is the wrong query, however plausible its name.
    --
    -- 2. WHETHER A GAMEPLAY RESTRICTION BLOCKS GETTING IN. TweakDB ships
    -- GameplayRestriction.NoDriving, VehicleNoSummoning and VehicleNoInteraction
    -- as status effect records. Their names suggest what they do and nothing
    -- more, because the flat values are hashed in tweakdb.bin, so the only way
    -- to learn what one actually stops is to wear it and try to get on a bike.
    -- The game's own gate is DoStatusEffectsAllowMounting, which reads the
    -- player's status effects, which is why a restriction is the thing to try
    -- before anything gets hooked.
    --
    -- 3. WHETHER THE EFFECT IS SAVABLE, and this is the dangerous one. It needs
    -- a save rather than a button: apply one, save, quit to desktop, load, then
    -- dump. If it comes back applied, a lock this mod forgets it is holding
    -- leaves a player unable to drive for the rest of that save. gotchas.md 21
    -- is the same shape, and ApplyLock in Gig01_Holocall.reds is the guard
    -- written for it.

    ImGui.Spacing()
    ImGui.Text("Vehicle lock lab (backlog 16)")
    ImGui.Separator()

    -- THE CANDIDATE SPELLINGS, in one table so the live readout below and the
    -- log button use exactly the same list.
    --
    -- SEVERAL ON PURPOSE, and the reason matters. 2.31 declares
    -- IsMountedToVehicle;GameInstanceGameObject, which takes a GameInstance
    -- first, so a one-argument call can be answering from an argument mismatch
    -- rather than from the game. A row reading false while standing proves
    -- nothing by itself. The row worth putting into redscript is the one that
    -- CHANGES when V gets on a bike.
    --
    -- The last row is the game's own gate on getting in, a static on
    -- gamevehicleVehicleMountableComponent. CET reaches a static through
    -- Game['Class::Method;ArgTypes'], because the bare class name is not a
    -- global.
    local MOUNT_PROBES = {
        { "IsMountedToVehicle(player)", function(player)
            return VehicleComponent.IsMountedToVehicle(player)
        end },
        { "IsMountedToVehicle(game, player)", function(player)
            return Game["VehicleComponent::IsMountedToVehicle;GameInstanceGameObject"](
                Game.GetGameInstance(), player)
        end },
        { "VehicleComponent.GetMountedVehicle", function(player)
            local v = VehicleComponent.GetMountedVehicle(player)
            if v == nil then return "nil" end
            return tostring(v:GetClassName())
        end },
        { "player:GetMountedVehicle()", function(player)
            local v = player:GetMountedVehicle()
            if v == nil then return "nil" end
            return tostring(v:GetClassName())
        end },
        { "PSM Vehicle blackboard int", function(player)
            local defs = Game.GetAllBlackboardDefs().PlayerStateMachine
            local bb = Game.GetBlackboardSystem():GetLocalInstanced(
                player:GetEntityID(), defs)
            return bb:GetInt(defs.Vehicle)
        end },
        { "DoStatusEffectsAllowMounting", function(player)
            return Game[
                "gamevehicleVehicleMountableComponent::DoStatusEffectsAllowMounting;GameObject"](player)
        end },
    }

    -- LIVE READOUT, recomputed every frame the window is open.
    --
    -- The question here is a comparison, standing against riding, and a
    -- comparison read out of a buffered log means quitting the game between its
    -- two halves. These lines move as V moves, so opening the overlay and
    -- getting on a bike is the entire test.
    do
        local player = Game.GetPlayer()
        if player == nil then
            ImGui.TextDisabled("no player")
        else
            for _, row in ipairs(MOUNT_PROBES) do
                local ok, res = pcall(row[2], player)
                if ok then
                    ImGui.Text(string.format("%-34s %s", row[1], tostring(res)))
                else
                    ImGui.TextDisabled(string.format("%-34s MISS", row[1]))
                end
            end
        end
    end
    ImGui.TextDisabled("Watch these while getting on a bike. The row that CHANGES")
    ImGui.TextDisabled("is the one to use. A row stuck on false answers nothing.")

    -- The same list into the log, for when the answer needs to be kept rather
    -- than looked at. MISS is a result: that spelling is not the one.
    if ImGui.Button("*** LOG: the mounted probes, as they read right now ***") then
        local player = Game.GetPlayer()
        log("vehicle-probe: ==== mounted state ====")
        for _, row in ipairs(MOUNT_PROBES) do
            local ok, res = pcall(row[2], player)
            if ok then
                log(string.format("vehicle-probe: %-40s %s", row[1], tostring(res)))
            else
                log(string.format("vehicle-probe: %-40s MISS (%s)", row[1], tostring(res)))
            end
        end
        log("vehicle-probe: ==== end ====")
    end

    -- APPLY AND REMOVE, one pair of buttons per record. Click apply, walk to a
    -- bike, try to get on.
    --
    -- WHAT BEING BLOCKED LOOKS LIKE MATTERS AS MUCH AS WHETHER IT HAPPENS. A
    -- prompt that is simply absent reads to a player as a broken mod, while
    -- vanilla's own refusal message reads as the game saying no. Note which of
    -- the two you get, because it decides whether this design ships at all.
    local VEHICLE_RESTRICTIONS = {
        "GameplayRestriction.NoDriving",
        "GameplayRestriction.VehicleNoSummoning",
        "GameplayRestriction.VehicleNoInteraction",
        -- OURS, a clone of VehicleNoInteraction with savable turned off
        -- (source/tweaks/vehiclelock.yaml). Two questions, both answered by
        -- applying this one instead of the vanilla one above:
        --   does it still block?   walk to a car with it on
        --   is it still savable?   apply, save, quit to DESKTOP, load, and read
        --                          the live status list below
        -- A record that loads is not evidence that every line in it applied;
        -- backlog.md 13 is the case where one line had never run for months.
        "GameplayRestriction.cc_g01_no_vehicle",
    }

    -- Two routes to the same thing, because which one CET exposes here has not
    -- been established. The one that works is named in the log, and that is the
    -- one the redscript should use.
    local function setRestriction(rid, on)
        local player = Game.GetPlayer()
        local verb = on and "applied " or "removed "
        local ok = pcall(function()
            if on then
                StatusEffectHelper.ApplyStatusEffect(player, rid)
            else
                StatusEffectHelper.RemoveStatusEffect(player, rid)
            end
        end)
        if ok then
            log("vehicle-lock: " .. verb .. rid .. " via StatusEffectHelper")
            return
        end
        local ok2, err = pcall(function()
            local ses = Game.GetStatusEffectSystem()
            if on then
                ses:ApplyStatusEffect(player:GetEntityID(), rid)
            else
                ses:RemoveStatusEffect(player:GetEntityID(), rid)
            end
        end)
        if ok2 then
            log("vehicle-lock: " .. verb .. rid .. " via StatusEffectSystem")
        else
            log("vehicle-lock: FAILED on " .. rid .. " -> " .. tostring(err))
        end
    end

    for _, rid in ipairs(VEHICLE_RESTRICTIONS) do
        local short = rid:gsub("^GameplayRestriction%.", "")
        if ImGui.Button("APPLY " .. short) then setRestriction(rid, true) end
        ImGui.SameLine(300)
        if ImGui.SmallButton("REMOVE##" .. short) then setRestriction(rid, false) end
    end

    -- PANIC BUTTON. Anything this lab can put on, this takes off, whatever
    -- state the rest of the menu thinks it is in. It exists so a session that
    -- ends badly does not leave behind a save that cannot drive.
    if ImGui.Button("*** CLEAR every restriction this lab applies ***") then
        for _, rid in ipairs(VEHICLE_RESTRICTIONS) do
            setRestriction(rid, false)
        end
    end

    -- THE HOOK PROBE, the other half of backlog 16 (Gig01_VehicleGate.reds).
    --
    -- The status effect above works and is savable, which is the thing that
    -- makes it wrong to ship: a player who uninstalls while it is applied has a
    -- save that can never drive. A script hook stores nothing, so the question
    -- is whether a hook can do the same job.
    --
    -- TWO READINGS, and the redscript needs a GAME RESTART rather than a mod
    -- reload, because it is redscript and not Lua.
    --
    -- 1. IS IT HEAVY. Switch the hook on and walk down a busy street. The count
    --    is every time the base game asked a vehicle to work out its
    --    interaction. Climbing steadily as cars stream past is expected and
    --    fine. Racing away while standing still in an empty alley is not, and
    --    would mean this method is not the one to hook.
    -- 2. CAN IT SUPPRESS THE PROMPT. Switch BLOCK on, walk to a car. If the
    --    "get in" prompt is gone, the design works with no save footprint at
    --    all. Watch for anything else about vehicles misbehaving, because this
    --    skips the original outright and that method may do more than one job.
    ImGui.Spacing()
    ImGui.Text("Hook probe (Gig01_VehicleGate.reds)")
    do
        local qs = Game.GetQuestsSystem()
        local on = qs:GetFactStr("cc_g01_dbg_vgate_on") > 0
        local blocking = qs:GetFactStr("cc_g01_dbg_vgate_block") > 0
        ImGui.Text(string.format("  calls counted: %d", qs:GetFactStr("cc_g01_dbg_vgate")))
        if ImGui.Button(on and "HOOK: ON (click to stop counting)"
                           or "HOOK: off (click to start counting)") then
            qs:SetFactStr("cc_g01_dbg_vgate_on", on and 0 or 1)
        end
        if ImGui.Button(blocking and "BLOCK: ON (prompt should be gone)"
                                 or "BLOCK: off") then
            qs:SetFactStr("cc_g01_dbg_vgate_block", blocking and 0 or 1)
        end
        if ImGui.Button("reset the count") then
            qs:SetFactStr("cc_g01_dbg_vgate", 0)
        end
        if blocking and not on then
            ImGui.TextDisabled("  BLOCK does nothing while HOOK is off.")
        end
    end
    ImGui.TextDisabled("Redscript, so this needs a game restart, not a reload.")


    -- WHICH COLOUR, and it can only be answered by looking.
    --
    -- Playtest 2026-08-21, on SimpleMessageType.Undefined: *"It's red and at the
    -- top... possible to be grey instead?"* The style is the enum member and
    -- nothing else: position and colour belong to the widget, so there is no
    -- knob for either.
    --
    -- These push through the SAME path the gig ships, CCSharedHud's slot and
    -- field, so whatever a button looks like here is exactly what a player
    -- would get. Lua only, so a mod reload is enough to try them.
    --
    -- A member that does not exist in 2.31 reports itself in the log rather
    -- than taking the overlay down, which also makes this a way to find out
    -- what the enum really holds.


    -- WHAT IS ON V RIGHT NOW, live.
    --
    -- This was a button that only wrote to the log, and twice that read as the
    -- button doing nothing. The reload test is the one place where a reading
    -- has to be taken the moment a save comes up, so it renders here instead.
    --
    -- MEASURED 2026-08-21: GameplayRestriction.VehicleNoInteraction IS SAVABLE.
    -- Applied, saved, quit to desktop, relaunched, loaded, and it came back
    -- still blocking. So this list is the only thing that will tell a session
    -- it inherited a lock, and CLEAR above is the only thing that lifts one.
    ImGui.Spacing()
    ImGui.Text("Status effects on V")
    do
        local ok, err = pcall(function()
            local player = Game.GetPlayer()
            local ses = Game.GetStatusEffectSystem()
            local effects = ses:GetAppliedEffects(player:GetEntityID())
            local n = 0
            for _, e in ipairs(effects or {}) do
                local rid = "?"
                pcall(function() rid = tostring(e:GetRecord():GetID()) end)
                -- The id prints as a TweakDBID struct with the readable name in
                -- a Lua comment inside it. Pull the name out, because the hash
                -- is not what anyone is looking for here.
                local pretty = rid:match("%-%-%[%[%s*(.-)%s*%-%-%]%]") or rid
                if pretty:find("GameplayRestriction") then
                    ImGui.Text("  " .. pretty)
                else
                    ImGui.TextDisabled("  " .. pretty)
                end
                n = n + 1
            end
            ImGui.Text(string.format("  %d effect(s)", n))
        end)
        if not ok then ImGui.TextDisabled("  unreadable: " .. tostring(err)) end
    end
    ImGui.TextDisabled("A GameplayRestriction line here after a fresh load is a")
    ImGui.TextDisabled("lock inherited from the save. Use CLEAR above.")

    if ImGui.Button("*** LOG: the status effects, as they read right now ***") then
        local ok, err = pcall(function()
            local player = Game.GetPlayer()
            local ses = Game.GetStatusEffectSystem()
            local effects = ses:GetAppliedEffects(player:GetEntityID())
            log("status-dump: ==== active on V ====")
            local n = 0
            for _, e in ipairs(effects or {}) do
                local rid = "?"
                pcall(function() rid = tostring(e:GetRecord():GetID()) end)
                log("status-dump: " .. rid)
                n = n + 1
            end
            log(string.format("status-dump: ==== %d effect(s) ====", n))
        end)
        if not ok then log("status-dump failed: " .. tostring(err)) end
    end

    ImGui.Spacing()
    ImGui.Text("Position capture (for the office encounter)")
    ImGui.Separator()
    captureName = ImGui.InputText("name", captureName, 64)
    ImGui.SameLine()
    if ImGui.Button("CAPTURE HERE") then
        captureCurrent(captureName)
    end
    ImGui.TextDisabled("Stand where you want it, type a name, click capture.")

    -- Capture where an NPC actually stands, rather than guessing by standing
    -- next to them. Used to place the Mama Welles stand-in on the exact spot
    -- the real one occupies: look straight at her and click.
    if ImGui.Button("CAPTURE THE NPC I'M LOOKING AT") then
        local ok, err = pcall(function()
            local target = Game.GetTargetingSystem():GetLookAtObject(Game.GetPlayer(), false, false)
            if target == nil then
                log("capture-npc: nothing targeted")
                return
            end
            local p = target:GetWorldPosition()
            local yaw = 0.0
            local ok2, angles = pcall(function() return target:GetWorldOrientation():ToEulerAngles() end)
            if ok2 and angles then yaw = angles.yaw end

            local recId = "?"
            local ok3, rec = pcall(function() return target:GetRecord() end)
            if ok3 and rec ~= nil then recId = tostring(rec:GetID()) end

            local name = (captureName ~= "" and captureName or "npc")
            local entry = { name = name, x = p.x, y = p.y, z = p.z, yaw = yaw }
            table.insert(capturedList, entry)
            local f = io.open("captured_positions.txt", "a")
            if f then
                f:write(string.format("%s = { x = %.3f, y = %.3f, z = %.3f, yaw = %.1f }  -- %s\n",
                    name, p.x, p.y, p.z, yaw, recId))
                f:close()
            end
            log(string.format("CAPTURED-NPC %s = %.3f, %.3f, %.3f (yaw %.1f) record=%s",
                name, p.x, p.y, p.z, yaw, recId))
        end)
        if not ok then log("capture-npc failed: " .. tostring(err)) end
    end
    ImGui.TextDisabled("Look at the NPC (e.g. Mama Welles) and click - captures THEIR spot.")
    ImGui.TextDisabled("Saved to ...\\mods\\negative_balance_dev\\captured_positions.txt")

    -- ANYTHING, not just an NPC and not just a door. It sits beside the two
    -- capture buttons rather than down with the door probes, because this is
    -- the block that gets looked in. The old device dump is still below and is
    -- still door-shaped; this one supersedes it for everything else.
    if ImGui.Button("DUMP WHATEVER I'M LOOKING AT (device, NPC, prop)") then
        local ok, err = pcall(function() dumpLookedAt(captureName) end)
        if not ok then log("look failed: " .. tostring(err)) end
    end
    ImGui.TextDisabled("Type a name first, then look at it and click. Cameras, doors,")
    ImGui.TextDisabled("terminals, anyone. Writes looked_at.txt beside the captures.")
    ImGui.TextDisabled("Reports on/off/disabled/hacked/broken and the entity id a")
    ImGui.TextDisabled("wiring change needs. Rows saying <no such method> are normal.")

    ImGui.Spacing()
    -- THE DEVICE-ACTION BUTTONS ARE GONE, 2026-08-25. They switched a device
    -- on and off, listed what it would accept and tried to repair a broken
    -- one, and all of it existed to serve a camera alarm that has been
    -- removed. What they found is kept where it belongs: gotcha 83 has the
    -- full menu of what a camera accepts and the two-step ladder a device
    -- walks, and gotcha 82 has how to address any base-game device offline.
    --
    -- The DUMP button above stays. It reads, it never writes, and it is the
    -- fastest way to find out what anything in the world actually is.
    for _, c in ipairs(capturedList) do
        ImGui.Text(string.format("  %s: %.1f %.1f %.1f", c.name, c.x, c.y, c.z))
    end

    -- The estate readout lived here: a live panel over Gig01_Bench.reds,
    -- built for backlog 17, 22 and 23 and removed with them once they
    -- closed. A probe that outlives its question ships by accident, and
    -- this one wrote fifteen facts four times a second.
    --
    -- Recover both from the commit before gig-01/v1.2.4 if a future estate
    -- question needs them. Do not rebuild from memory.

    -- The loot bench lived here: twenty one objects in the street, each
    -- varying one field, plus a look-at probe, a direction finder and
    -- seven live TweakDB rewrites. It answered backlog 6 and was removed
    -- with it, 2026-08-22. A probe that outlives its question ships by
    -- accident, and this one wrote a hundred facts four times a second.
    --
    -- The findings are in backlog.md 6 and gotchas.md 47 and 48. The
    -- recipe is in tools/gig01/gen_sector.py and source/tweaks/shard.yaml.
    -- Recover the bench from the commit before gig-01/v1.2.5 if a future
    -- container question needs it; do not rebuild it from memory.

    -- The holocall lab lived here, and it came out with the 1.2.6 release.
    -- It proved the whole video holocall: that a mod can open the studio, take
    -- the camera, ring its own contact in either direction and speak over the
    -- feed. All of it is written up in backlog.md 3d, the recipe is in
    -- scene-playbook.md, and the traps are gotchas 50 to 59. Recover the
    -- buttons from the commit before gig-01/v1.2.6 if a future question needs
    -- them; do not rebuild them from memory.

    -- ============================================ HOSHINO, AS ONE BODY
    --
    -- SHIPPED, not a bench. He is placed by a community this mod ships
    -- (tools/gig01/gen_community.py) and the quest phase switches the entry on
    -- and off; the scene speaks through that body instead of spawning an
    -- invisible second one.
    --
    -- Every way this can fail is silent in game: a man who is not there looks
    -- exactly like a man the game has not placed yet, and a scene with no
    -- speaker plays no subtitle at all rather than erroring. So it is a number.
    ImGui.Spacing()
    ImGui.Text("HOSHINO (one body)")
    ImGui.Separator()
    do
        local qs = Game.GetQuestsSystem()
        local codes = {
            [0] = "nothing has looked yet",
            [1] = "the community name did NOT resolve  <- sector not loading",
            [2] = "resolved, no body yet  <- phase has not activated it, or still placing",
            [3] = "FOUND, and set neutral",
            [4] = "found, and dead",
        }
        local c = qs:GetFactStr("cc_g01_dbg_hoshino")
        ImGui.Text(string.format("  find: %d  %s", c, codes[c] or "?"))
        ImGui.Text(string.format("  estate reached %d   met %d   talked %d   dead %d",
                                 qs:GetFactStr("cc_g01_estate_reached"),
                                 qs:GetFactStr("cc_g01_hoshino_met"),
                                 qs:GetFactStr("cc_g01_hoshino_talked"),
                                 qs:GetFactStr("cc_g01_hoshino_dead")))

        -- THE ESTATE DETAIL, one guard per captured post, placed by
        -- their own community (cc_g01_estate) rather than spawned onto navmesh.
        --
        -- The count RISES as you walk in and that is correct, not a fault: a
        -- post 90 m away has not streamed in yet, exactly as the old spawn's far
        -- anchors had not. It is asked again every six seconds while you are on
        -- site and stops at the full count.
        --
        -- A count that stays at 0 with find 2 is a community that is switched
        -- off, which before the estate objective is the RIGHT answer.
        local ecodes = {
            [0] = "nothing has looked yet",
            [1] = "the community name did NOT resolve  <- sector not loading",
            [2] = "resolved, nobody there  <- phase has not activated it, or not streamed in",
            [3] = "FOUND, and turned hostile",
        }
        local ec = qs:GetFactStr("cc_g01_dbg_estate")
        ImGui.Text(string.format("  detail: %d  %s", ec, ecodes[ec] or "?"))
        -- THE TOTAL COMES FROM THE SCRIPT, not from a number typed here. It
        -- said "of 30" while the list had just become 29.
        ImGui.Text(string.format("  posts standing: %d of %d",
                                 qs:GetFactStr("cc_g01_dbg_estate_guards"),
                                 qs:GetFactStr("cc_g01_dbg_estate_total")))
        -- WHAT ACTUALLY TOOK, read off the guards themselves.
        --
        -- Playtest 2026-08-25: all thirty stood at their posts and none of them
        -- ever noticed V. They fought when shot and joined in when one of the
        -- estate's own NPCs raised the alarm, so they were not inert. They
        -- never STARTED looking. "posts standing" could not tell that apart from
        -- working guards, because it counts who we asked, not what landed.
        --
        -- Whichever of these three is the odd one out is the answer:
        --   hostile   low  -> the attitude is not reaching these bodies
        --   senses    low  -> enemies who cannot see. Expected culprit
        --   workspot  high -> held in an idle, which may suppress perception
        ImGui.Text(string.format("    hostile to V: %d   senses on: %d   in workspot: %d",
                                 qs:GetFactStr("cc_g01_dbg_estate_hostile"),
                                 qs:GetFactStr("cc_g01_dbg_estate_senses"),
                                 qs:GetFactStr("cc_g01_dbg_estate_workspot")))

        -- THE INDUSTRIAL PARK, the same four rows for the same reasons. Its
        -- detail is a community too as of 2026-08-25: forty-six walked posts in
        -- place of five anchors and a navmesh query.
        --
        -- Its window is a different one. The compound detail goes on when the
        -- gig starts and off once V is clear of the site, so `detail: 2` here
        -- while standing in the compound BEFORE taking the job is right.
        ImGui.Text("COMPOUND (Arasaka industrial park)")
        local cc = qs:GetFactStr("cc_g01_dbg_compound")
        ImGui.Text(string.format("  detail: %d  %s", cc, ecodes[cc] or "?"))
        ImGui.Text(string.format("  posts standing: %d of %d",
                                 qs:GetFactStr("cc_g01_dbg_compound_guards"),
                                 qs:GetFactStr("cc_g01_dbg_compound_total")))
        ImGui.Text(string.format("    hostile to V: %d   senses on: %d   in workspot: %d",
                                 qs:GetFactStr("cc_g01_dbg_compound_hostile"),
                                 qs:GetFactStr("cc_g01_dbg_compound_senses"),
                                 qs:GetFactStr("cc_g01_dbg_compound_workspot")))
        -- THE CAMERA AND SECURITY-AREA READOUTS ARE GONE, 2026-08-25.
        --
        -- Neither describes anything that ships any more: the camera pass was
        -- removed at playtest's request, and the security area and its system
        -- are no longer in the archive because they demonstrably did nothing.
        -- A panel row reporting a node that is not there is worse than no row.
        --
        -- The whole investigation is `backlog.md` 31 and gotchas 79 to 83.

        -- THE EXPERIMENT BUTTONS ARE GONE, 2026-08-25, and so is the script
        -- block behind them. They asked three questions and all three are
        -- closed: a hostile attitude is what makes a community guard perceive
        -- and fight (gotchas 74 and 77), and taking them out of their idle
        -- changed nothing, twice. The shipped pass in `FindDetail` now does
        -- what buttons 1 and 3 did, on every guard, every few seconds.

        -- THE GUARD TEST, backlog.md 31. One community-placed guard at a
        -- vanilla workspot on the estate grounds, with the script-spawned ones
        -- a short walk away.
        --
        -- This row only says he EXISTS. The question is whether he BEHAVES:
        -- walk up to him, then to a spawned one, and see whether either
        -- challenges you, looks at you, or reacts at all.
        local gcodes = { [0] = "not there", [1] = "standing", [2] = "dead" }
        local gc = qs:GetFactStr("cc_g01_dbg_guard")
        local gd = qs:GetFactStr("cc_g01_dbg_guard_d") / 10.0
        local gn = qs:GetFactStr("cc_g01_dbg_guard_n")
        ImGui.Text(string.format("  guard test: %d  %s", gc, gcodes[gc] or "?"))
        -- HE LOOKS LIKE THE OTHERS. He wears a record the encounter also
        -- spawns, so the only way to know which man he is, is to be told.
        if gc > 0 then
            local gb = qs:GetFactStr("cc_g01_dbg_guard_b")
            -- Bearing from YOUR facing: 0 dead ahead, rising clockwise.
            local side = "ahead"
            if gb > 15 and gb < 165 then side = "to your RIGHT"
            elseif gb > 195 and gb < 345 then side = "to your LEFT"
            elseif gb >= 165 and gb <= 195 then side = "BEHIND you" end
            ImGui.Text(string.format("    %.1f m away, %d deg %s", gd, gb, side))
            -- THE ROW THAT SETTLES IT. Compared by entity id, so it does not
            -- care how many identical guards are standing together.
            local gl = qs:GetFactStr("cc_g01_dbg_guard_look")
            local looks = { [0] = "looking at nobody",
                            [1] = "YOU ARE LOOKING AT HIM",
                            [2] = "that is somebody else" }
            ImGui.Text(string.format("    %s", looks[gl] or "?"))
            ImGui.Text(string.format("    other NPCs within 5 m of him: %d%s", gn,
                                     gn > 0 and "   (aim to be sure which)" or "   (clean)"))
        end
        if ImGui.Button("TELEPORT: the guard test post") then
            teleportTo({ x = 298.251, y = 1021.907, z = 224.952, w = 1.0 })
        end
        if ImGui.Button("HOSHINO: report to the log") then
            log(string.format("hoshino find %d (%s)", c, codes[c] or "?"))
            log(string.format("guard test %d (%s) %.1f m, bearing %d, look %d, %d others near",
                              gc, gcodes[gc] or "?", gd,
                              qs:GetFactStr("cc_g01_dbg_guard_b"),
                              qs:GetFactStr("cc_g01_dbg_guard_look"), gn))
            log(string.format("hoshino estate %d met %d talked %d dead %d",
                              qs:GetFactStr("cc_g01_estate_reached"),
                              qs:GetFactStr("cc_g01_hoshino_met"),
                              qs:GetFactStr("cc_g01_hoshino_talked"),
                              qs:GetFactStr("cc_g01_hoshino_dead")))
        end
        if ImGui.Button("TELEPORT: where Hoshino waits") then
            teleportTo({ x = 300.102, y = 1054.556, z = 229.928, w = 1.0 })
        end
    end

    ImGui.Spacing()
    ImGui.Text("Zone probe (safe-area restrictions)")
    ImGui.Separator()
    -- The office interior scouting found rooms where the game holsters
    -- weapons and blocks jumping (the club-zone treatment). DUMP says which
    -- restriction effects the zone applied; STRIP removes them so scouting
    -- can continue. The zone REAPPLIES them on re-entry, so strip again
    -- after leaving and coming back. Quest-time removal for the real beat is
    -- the same call from the scene, per docs/gameplay-restrictions.md.
    local ZONE_RESTRICTIONS = {
        "GameplayRestriction.InDaClub",
        "GameplayRestriction.NoCombat",
        "GameplayRestriction.NoWeapons",
        "GameplayRestriction.Firearms",
        "GameplayRestriction.NoJump",
        "GameplayRestriction.NoSprint",
        "GameplayRestriction.FistFight",
        "GameplayRestriction.NoQuickMelee",
        "GameplayRestriction.NoGrenadeOrGadget",
        "GameplayRestriction.Tier2Locomotion",
    }
    if ImGui.Button("DUMP zone restrictions on me") then
        local player = Game.GetPlayer()
        local ses = Game.GetStatusEffectSystem()
        local found = 0
        for _, rid in ipairs(ZONE_RESTRICTIONS) do
            local ok, has = pcall(function()
                return ses:HasStatusEffect(player:GetEntityID(), TweakDBID.new(rid))
            end)
            if ok and has then
                log("zone probe: ACTIVE " .. rid)
                found = found + 1
            end
        end
        if found == 0 then
            log("zone probe: none of the known zone restrictions are active")
        end
    end
    ImGui.SameLine()
    if ImGui.Button("FORCE gameplay tier") then
        -- The zone latches the player into a story tier (the dump showed
        -- Tier2Locomotion), and removing the status effect does not lower
        -- the tier itself. This sets the state machine's scene tier back to
        -- full gameplay and strips the effects again. Test: draw, jump.
        local player = Game.GetPlayer()
        local ok, err = pcall(function()
            local bb = player:GetPlayerStateMachineBlackboard()
            local defs = GetAllBlackboardDefs().PlayerStateMachine
            bb:SetInt(defs.SceneTier, 1, true)
        end)
        log("zone probe: scene tier forced to 1 (" .. tostring(ok) .. ")")
        local ses = Game.GetStatusEffectSystem()
        for _, rid in ipairs(ZONE_RESTRICTIONS) do
            pcall(function() StatusEffectHelper.RemoveStatusEffect(player, TweakDBID.new(rid)) end)
            pcall(function() ses:RemoveStatusEffect(player:GetEntityID(), rid) end)
        end
    end
    ImGui.SameLine()
    if ImGui.Button("STRIP zone restrictions") then
        local player = Game.GetPlayer()
        local ses = Game.GetStatusEffectSystem()
        for _, rid in ipairs(ZONE_RESTRICTIONS) do
            pcall(function() StatusEffectHelper.RemoveStatusEffect(player, TweakDBID.new(rid)) end)
            pcall(function() ses:RemoveStatusEffect(player:GetEntityID(), rid) end)
        end
        log("zone probe: strip attempted for all known zone restrictions")
    end

    ImGui.Spacing()
    ImGui.Text("Teleports")
    ImGui.Separator()
    local player = Game.GetPlayer()
    if player then
        local wp = player:GetWorldPosition()
        ImGui.Text(string.format("Position: %.1f, %.1f, %.1f", wp.x, wp.y, wp.z))
    end
    for i, p in ipairs(presets) do
        if p.pos then
            if ImGui.Button(p.name .. "##tp" .. i) then teleportTo(p.pos) end
        else
            ImGui.TextDisabled(p.name .. " (no coords yet)")
        end
        ImGui.SameLine(300)
        if ImGui.SmallButton("Save current##" .. i) then
            local wp = Game.GetPlayer():GetWorldPosition()
            p.pos = { x = wp.x, y = wp.y, z = wp.z, w = 1.0 }
            savePresets()
        end
    end

    ImGui.End()
end)
