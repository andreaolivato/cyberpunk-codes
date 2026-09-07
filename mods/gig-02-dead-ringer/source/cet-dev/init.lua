-- Dead Ringer, DEV debug menu. Never shipped in a release.
--
-- CET overlay window: where the gig has got to, distances to every trigger,
-- position capture, teleports, facts and journal probes.
--
-- ===========================================================================
-- WHAT THIS ONE IS FOR, AND WHY IT IS NOT A COPY OF THE FIRST GIG'S
-- ===========================================================================
--
-- Gig 01's menu grew around questions that gig had: a holocall that crashed, a
-- camera nobody could identify, doors the base game ships disabled. This gig
-- has a different problem and only one that matters.
--
-- **NOT ONE POSITION IN THIS GIG HAS BEEN STOOD ON.** Every trigger spot, every
-- map pin and the relay object are base-game marker coordinates read out of the
-- streaming sectors, chosen because they are certainly real rather than because
-- anybody looked at them. So the two things this menu has to do well are:
--
--   1. SAY WHY A TRIGGER DID NOT FIRE. The DISTANCES panel is live: every spot
--      the gig measures against, how far the player is from it right now, and
--      the radius it needs. "Afterlife 62 m (needs 40)" is a whole diagnosis in
--      one line, and it is the failure this build is most likely to have.
--   2. CAPTURE THE RIGHT POSITIONS so the guesses can be replaced. Stand on the
--      QUADRACER cabinet, type a name, press the button. That is the fix for
--      the largest compromise in the gig.
--
-- Everything else here is ordinary: facts, teleports, journal state.
--
-- ===========================================================================
-- NOTHING THE MOD SHIPS DEPENDS ON THIS
-- ===========================================================================
--
-- By construction rather than by care: CET is a separate Lua VM that redscript
-- cannot call into at all. The only coupling runs the other way, this menu
-- writes quest facts that the mod reads, and an unset fact reads as 0, which is
-- every gate's "no". Removing CET cannot break the gig; it costs diagnosis.

local visible = false
local PRESET_FILE = "presets.lua"

local function log(msg)
    print("[DR] " .. msg)
    spdlog.info(msg)
end

-- ===========================================================================
-- THE FLOW, AS THE QUEST PHASE ACTUALLY WAITS ON IT
-- ===========================================================================
--
-- In the order `tools/gig02/gen_questphase.py` parks on them. The first row
-- whose fact is still 0 is where the graph is sitting, which is the question
-- every playtest of a quest phase starts with and which nothing in game
-- answers: a stopped phase looks exactly like a beat that never started.
--
-- `who` is who is supposed to set it, and it is the other half of the same
-- question. A row that says SCRIPT and is not going up means a proximity check
-- is not firing, so read the DISTANCES panel. A row that says GRAPH and is not
-- going up means the phase never got there, so look at the row above it.
local STEPS = {
    { fact = "cc_g02_start",            who = "SCRIPT", what = "waiting for the start trigger (Gig02_Start)" },
    { fact = "cc_g02_started",          who = "GRAPH",  what = "the message and the quest are going up" },
    { fact = "cc_g02_called",           who = "GRAPH",  what = "the message is on the phone: waiting for the player to answer it" },
    { fact = "cc_g02_accepted",         who = "GRAPH",  what = "the call is over and the gig goes into the journal" },
    { fact = "cc_g02_afterlife_reached", who = "SCRIPT", what = "travelling to Afterlife" },
    { fact = "cc_g02_merc_placed",      who = "SCRIPT", what = "placing the merc with group 3: if this stays 0 he is NOT IN THE WORLD" },
    { fact = "cc_g02_group_first",      who = "SCRIPT", what = "walk to either of the two marked groups. 1 or 2 says which" },
    { fact = "cc_g02_talk_a_done",      who = "GRAPH",  what = "the first overheard conversation is playing" },
    { fact = "cc_g02_group_second",     who = "SCRIPT", what = "walk to the OTHER marked group" },
    { fact = "cc_g02_groups_done",      who = "GRAPH",  what = "the second conversation is playing; the last group is about to be marked" },
    { fact = "cc_g02_group3_near",      who = "SCRIPT", what = "walk to the last group. The merc is the one talking in it" },
    { fact = "cc_g02_lead_heard",       who = "GRAPH",  what = "the last group's conversation, then straight into the confrontation" },
    { fact = "cc_g02_brief_read",       who = "SCRIPT", what = "the brief has been read and the phone closed; the gig and Johnny follow" },
    { fact = "cc_g02_dev_crowd",        who = "DEV",    what = "door-crowd test harness: 1-8 picks a switch shape, see the DOOR CROWD panel" },
    { fact = "cc_g02_merc_armed",       who = "GRAPH",  what = "the objective is to take him out: he is hittable and fights back when hit" },
    { fact = "cc_g02_merc_down",        who = "SCRIPT", what = "the fight stops at a THIRD of his health and the begging scene takes him" },
    { fact = "cc_g02_merc_talked",      who = "SCENE",  what = "he has said the shard is on him (end of the begging scene)" },
    { fact = "cc_g02_shard_planted",    who = "SCRIPT", what = "the shard is in his pocket, three ticks after the fall" },
    { fact = "cc_g02_shard_taken",      who = "SCRIPT", what = "the shard is in the player's inventory" },
    { fact = "cc_g02_shard_open",       who = "SCRIPT", what = "a shard popup with OUR title has opened (the reader wrap)" },
    { fact = "cc_g02_shard_leg",        who = "GRAPH",  what = "1 = take done or skipped, 2 = read done or skipped" },
    { fact = "cc_g02_merc_fate",        who = "SCENE",  what = "the choice at the end of the begging: 1 = finish it, 2 = let him go" },
    { fact = "cc_g02_merc_kill_armed",  who = "GRAPH",  what = "fate 1: he is killable now, objective says kill him" },
    { fact = "cc_g02_merc_hit",         who = "SCRIPT", what = "fate 1: his body reported a hit after the kill was armed" },
    { fact = "cc_g02_merc_kill_stage",  who = "SCRIPT", what = "fate 1: 1 shield off, 2 Kill called, 3 ForceKill applied" },
    { fact = "cc_g02_merc_dead",        who = "SCRIPT", what = "fate 1: he is dead" },
    { fact = "cc_g02_merc_flee",        who = "GRAPH",  what = "fate 2: he lives, stays down, V told him to keep quiet; the fee stays single" },
    { fact = "cc_g02_merc_done",        who = "GRAPH",  what = "either way, the merc leg is over" },
    { fact = "cc_g02_proof_read",       who = "SCRIPT", what = "waiting for the shard reader to be CLOSED" },
    { fact = "cc_g02_reported",         who = "GRAPH",  what = "V picked the reply in Wakako's thread: the report is a TEXT now" },
    { fact = "cc_g02_wakako_2",         who = "GRAPH",  what = "her answer landed as a message, with the netrunner's location" },
    { fact = "cc_g02_inn_reached",      who = "SCRIPT", what = "travelling to the netrunner (KABUKI, upper walkway)" },
    { fact = "cc_g02_to_char",          who = "GRAPH",  what = "Yoko has sent V to Char: her chair is pinned, 9 m in" },
    { fact = "cc_g02_char_near",        who = "SCRIPT", what = "walk to Char and hand her the shard" },
    { fact = "cc_g02_trace_done",       who = "GRAPH",  what = "Char's verdict landed as a message, HALF AN IN-GAME HOUR after the handover" },
    { fact = "cc_g02_parlor_reached",   who = "SCRIPT", what = "travelling to the pachinko parlor" },
    { fact = "cc_g02_left_parlor",      who = "SCRIPT", what = "V is 20 m from the parlor marker after Wakako's order; the game's own Wakako comes back then, out of sight" },
    { fact = "cc_g02_ap_breached",      who = "SCRIPT", what = "the access point on the parlor wall reports breached (the game's own IsBreached, polled, plus the minigame's success frame). Marker on the box until then. Char texts 'Got the dump'" },
    { fact = "cc_g02_char_named",       who = "GRAPH",  what = "Char's second text, 12 s later, names the man; Wakako's office opens" },
    { fact = "cc_g02_office_reached",   who = "SCRIPT", what = "walking to Wakako's office" },
    { fact = "cc_g02_wakako_met",       who = "GRAPH",  what = "the office scene is playing" },
    { fact = "cc_g02_hit_reached",      who = "SCRIPT", what = "travelling to the Japantown side street" },
    { fact = "cc_g02_hit_armed",        who = "GRAPH",  what = "V has reached the stairs; the objective is up and being seen counts from here" },
    { fact = "cc_g02_toji_placed",      who = "SCRIPT", what = "placing Toji: if this stays 0 he is NOT IN THE WORLD" },
    { fact = "cc_g02_dropped",         who = "SCRIPT", what = "V is at the trash pile or at the bottom; nothing waits on it since 2026-09-05" },
    { fact = "cc_g02_toji_met",         who = "SCRIPT", what = "getting close to Toji, OR killing him from range" },
    { fact = "cc_g02_toji_dead",        who = "SCRIPT", what = "waiting for Toji to die" },
    { fact = "cc_g02_exfil_armed",      who = "GRAPH",  what = "he is down: the objective now asks V to leave without being seen" },
    { fact = "cc_g02_exfil_done",       who = "SCRIPT", what = "get 70 m from the bottom step. BEING SEEN also sets it, so a firefight cannot strand the objective" },
    { fact = "cc_g02_closed",           who = "GRAPH",  what = "one of the two closing calls is playing. Which one is decided by cc_g02_spotted" },
    { fact = "cc_g02_afterlife_clear",  who = "SCRIPT", what = "V is 100 m from the Afterlife door, so our seven bodies may be swapped back for the game's own unseen. Held during a fast travel; also set by a ten-minute cap so the phase cannot stall" },
    { fact = "cc_g02_site_clear",       who = "SCRIPT", what = "V is 80 m clear of the staircase, so the Claws and Toji may be removed unseen. Also set by a five-minute cap, so the phase cannot wait for ever" },
    { fact = "cc_g02_done",             who = "GRAPH",  what = "the gig is over and paid" },
}

-- Everything with a 0/1 button. The base-game ones are FIRST because they are
-- the ones a tester is most likely to need on an old save, and the ones it is
-- most important to know are not ours.
local FACTS = {
    -- BASE GAME. Read these, and set them only knowing what they are.
    --   q101_enable_side_content   the prologue is over. CDPR's own gate for
    --      all side content. Forcing it to 1 is the quickest way to test the
    --      trigger on an early save.
    --   q115_point_of_no_return    Nocturne Op55N1 has begun; the gig stops
    --      offering itself.
    "q101_enable_side_content",
    "q115_point_of_no_return",
    -- WRITTEN BY THE GAME, not by us: 0 Ended, 1 Initializing, 2 Talking,
    -- 3 Rejected. Both of Wakako's calls and Yoko's are OUTGOING, so these
    -- should walk to 2 on their own with no ring to answer. A call that sits
    -- at 0 or 1 is a call that never connected.
    "phonecall_player_with_cc_g02_wakako",
    "phonecall_player_with_cc_g02_yoko",
    -- The flow, in order. Same list as STEPS above plus the ones nothing waits
    -- on.
    "cc_g02_start",
    "cc_g02_started",
    "cc_g02_accepted",
    "cc_g02_called",
    "cc_g02_afterlife_reached",
    "cc_g02_group_first",
    "cc_g02_talk_a_done",
    "cc_g02_group_second",
    "cc_g02_groups_done",
    "cc_g02_group3_near",
    "cc_g02_lead_heard",
    -- IS EACH GROUP SOMEWHERE A FIGHT CAN HAPPEN. Written once, the first time
    -- the player reaches Afterlife, by asking the game's own SafeAreaManager.
    -- 1 means that spot is inside the club's no-weapons zone: the player cannot
    -- draw there, so the merc cannot be beaten and the leg cannot finish. Move
    -- the spot rather than debugging the fight.
    "cc_g02_safe_checked",
    "cc_g02_safe_g1",
    "cc_g02_safe_g2",
    "cc_g02_safe_g3",
    -- DID THE BODY ACTUALLY GET PLACED. Set by Gig02_Encounter the moment the
    -- navigation system accepts a spot for him. 0 with the gig past
    -- `afterlife_reached` means he is not in the world at all, which looks
    -- exactly like a broken trigger and is a completely different problem.
    "cc_g02_merc_placed",
    "cc_g02_merc_armed",
    "cc_g02_merc_down",
    "cc_g02_merc_talked",
    "cc_g02_shard_planted",
    "cc_g02_shard_taken",
    "cc_g02_shard_leg",
    "cc_g02_merc_fate",
    "cc_g02_merc_kill_armed",
    "cc_g02_merc_hit",
    "cc_g02_merc_kill_stage",
    "cc_g02_merc_dead",
    "cc_g02_merc_done",
    "cc_g02_merc_flee",
    "cc_g02_proof_read",
    "cc_g02_reported",
    "cc_g02_wakako_2",
    "cc_g02_inn_reached",
    -- Is Char's own body in the world. 0 with the leg running means the spawn
    -- was refused and the player is looking at the base game's crowd again.
    "cc_g02_char_placed",
    "cc_g02_to_char",
    "cc_g02_char_near",
    "cc_g02_trace_done",
    "cc_g02_parlor_reached",
    "cc_g02_ap_breached",
    "cc_g02_left_parlor",
    "cc_g02_char_named",
    "cc_g02_office_reached",
    "cc_g02_wakako_met",
    "cc_g02_hit_reached",
    "cc_g02_hit_armed",
    "cc_g02_toji_placed",
    "cc_g02_spotted",
    "cc_g02_dropped",
    "cc_g02_toji_met",
    "cc_g02_kill_seen",
    "cc_g02_toji_dead",
    "cc_g02_exfil_armed",
    "cc_g02_exfil_done",
    "cc_g02_afterlife_clear",
    "cc_g02_closed",
    "cc_g02_site_clear",
    "cc_g02_done",
    "cc_g02_paid",
    -- The two holocall blocks' own bookkeeping. READ THESE, do not set them.
    --   _step   how far into the block the graph got: 1 the studio was asked
    --           for, and that is the only mark this gig's calls carry, because
    --           an outgoing call has nothing else that can go wrong.
    --   _video  1 the camera node arrived and the feed is live, 0 the studio
    --           lost its 20 s race and the call is running behind an empty
    --           frame. A call that works with a blank picture is this, and it
    --           is cosmetic.
    --   _claim  the race's own scratch: 1 the camera arrived first, 2 the 20 s
    --           clock did. It is cleared on the way in, so a call that has
    --           stalled with this still at 0 stalled BEFORE the race, which
    --           means the two prefab variants never went up.
    "cc_g02_call1_step",
    "cc_g02_call1_claim",
    "cc_g02_call1_video",
    "cc_g02_call1_talking",
    "cc_g02_call1_done",
    "cc_g02_call2_step",
    "cc_g02_call2_claim",
    "cc_g02_call2_video",
    "cc_g02_call2_talking",
    "cc_g02_call2_done",
    -- THE TWO ENDINGS, and only one of them ever runs in a playthrough: call 3
    -- is the quiet close, call 4 is the one where V was seen.
    -- Char's call on the parlor floor is video too (2026-09-05): same studio, same facts.
    "cc_g02_callc_step",
    "cc_g02_callc_claim",
    "cc_g02_callc_video",
    "cc_g02_callc_talking",
    "cc_g02_callc_done",
    "cc_g02_call3_step",
    "cc_g02_call3_claim",
    "cc_g02_call3_video",
    "cc_g02_call3_talking",
    "cc_g02_call3_done",
    "cc_g02_call4_step",
    "cc_g02_call4_claim",
    "cc_g02_call4_video",
    "cc_g02_call4_talking",
    "cc_g02_call4_done",
    -- HOLD THE GIG. Set to 1 and Gig02_Start stops offering it, so the message
    -- never arrives; clear it and the next check picks up where it left off.
    -- For testing anything that is not this gig. It does not settle the
    -- trigger, so it is releasable without a reload.
    "cc_g02_dev_hold",
    -- The "finish the prologue first" message, already shown. Clear it to see
    -- the message again without a new save. Clearing it does NOT unblock the
    -- gig.
    "cc_g02_prologue_notified",
    -- THE BASE GAME'S OWN, not ours. 1 switches Wakako's default small talk off
    -- and the gig holds it up only while V is in her office. If this is stuck
    -- at 1 with the gig finished, she is mute for the rest of the save: set it
    -- back to 0 here.
    "wakako_default_temp_off",
}

-- ===========================================================================
-- EVERY SPOT THE GIG MEASURES AGAINST
-- ===========================================================================
--
-- KEEP IN STEP WITH `CCGig02Places` in Gig02_DeadRinger.reds AND WITH
-- `ANCHOR_POS` in tools/gig02/gig02_config.py. Three copies of the same
-- numbers is two too many, and this one is the copy that exists so a human can
-- see them: the redscript measures and this reports what the redscript would
-- have measured. A disagreement here would report a trigger as ready when it
-- is not, which is worse than having no panel.
--
-- `radius` is the redscript's own, so the panel says READY exactly when the
-- script's own test would pass. The Z band is asymmetric in the script (tight
-- below, generous above, so a road tunnelling underneath cannot fire it) and
-- this panel reports plain 3D distance, so a spot directly below the player
-- can read as in range here and not fire. That is worth knowing rather than
-- worth fixing: if a trigger says READY here and does not fire, the height is
-- the first thing to suspect.
local SPOTS = {
    { name = "Afterlife (arrive)",   x = -1465.155, y = 1046.971, z = 22.759, radius = 40.0,
      gate = "cc_g02_called",           sets = "cc_g02_afterlife_reached" },
    -- THE THREE GROUPS, captured in game 2026-08-26. Groups 1 and 2 are 3.6 m
    -- apart, so a row here can read >> for both at once: the redscript breaks
    -- the tie by taking the NEARER group, which this panel does not model.
    { name = "Group 1",              x = -1467.443, y = 1052.568, z = 22.709, radius = 3.0,
      gate = "cc_g02_afterlife_reached", sets = "cc_g02_group_first" },
    { name = "Group 2",              x = -1470.628, y = 1050.988, z = 22.722, radius = 3.0,
      gate = "cc_g02_talk_a_done",       sets = "cc_g02_group_second" },
    { name = "Group 3 (the merc)",   x = -1470.163, y = 1044.159, z = 22.722, radius = 3.0,
      gate = "cc_g02_groups_done",       sets = "cc_g02_group3_near" },
    -- THE ONLY CAPTURED SPOT IN THIS LIST, so its radius can be tight where
    -- every other one has to be generous.
    -- 3 m, not 12. Playtest, 2026-08-26: the Yoko conversation started from
    -- outside the shop. This spot was walked to, so it IS where the player
    -- stands and does not need a marker's slack.
    { name = "Netrunner, KABUKI",    x = -1179.864, y = 2037.655, z = 20.087, radius = 3.0,
      gate = "cc_g02_wakako_2",         sets = "cc_g02_inn_reached" },
    -- Char's chair, 9 m further in. Captured in game 2026-08-26. One visit:
    -- her verdict is a message now.
    { name = "Char's chair (shard)", x = -1183.542, y = 2045.510, z = 20.487, radius = 3.0,
      gate = "cc_g02_to_char",          sets = "cc_g02_char_near" },
    { name = "Pachinko parlor",      x = -657.332, y = 826.691, z = 19.522, radius = 20.0,
      gate = "cc_g02_trace_done",       sets = "cc_g02_parlor_reached" },
    { name = "The access point",     x = -663.250, y = 822.330, z = 20.900, radius = 3.0,
      gate = "cc_g02_parlor_reached",   sets = "cc_g02_ap_breached" },
    -- EITHER of two spots closes this one: the trash, or the bottom on foot.
    -- The panel can only show one, so it shows the trash, which is the route
    -- the pin points at.
    { name = "The trash (the drop)",  x = -391.116, y = 1284.479, z = 25.910, radius = 6.0,
      gate = "cc_g02_hit_reached",      sets = "cc_g02_dropped" },
    { name = "Toji, bottom of stairs", x = -381.087, y = 1233.990, z = 23.428, radius = 25.0,
      gate = "cc_g02_hit_reached",      sets = "cc_g02_dropped" },
}

-- Teleports. The gig's own spots plus two the gig does not measure against but
-- a tester needs: the holocall studio, which is where Wakako's body stands
-- while she is on the phone, and Jig-Jig Street, which is the job the merc
-- took and is thirty metres from the parlor.
local presets = {
    { name = "Afterlife entrance (LOCATION 1)", pos = { x = -1465.155, y = 1046.971, z = 22.759, w = 1.0 } },
    { name = "Group 1, outside Afterlife", pos = { x = -1467.443, y = 1052.568, z = 22.709, w = 1.0 } },
    { name = "Group 2, outside Afterlife", pos = { x = -1470.628, y = 1050.988, z = 22.722, w = 1.0 } },
    { name = "Group 3, the merc", pos = { x = -1470.163, y = 1044.159, z = 22.722, w = 1.0 } },
    { name = "Pose lab (spawnhere)", pos = { x = -1472.817, y = 1028.142, z = 22.690, w = 1.0 } },
    { name = "Char's chair, Dewdrop Inn", pos = { x = -1183.542, y = 2045.510, z = 20.487, w = 1.0 } },
    { name = "Netrunner, Kabuki (LOCATION 2)", pos = { x = -1179.864, y = 2037.655, z = 20.087, w = 1.0 } },
    { name = "Pachinko parlor (LOCATION 3)", pos = { x = -657.332, y = 826.691, z = 19.522, w = 1.0 } },
    { name = "Parlor counter (Ideka)", pos = { x = -662.989, y = 827.050, z = 19.522, w = 1.0 } },
    { name = "Wakako's office (LOCATION 4)", pos = { x = -671.492, y = 822.324, z = 19.598, w = 1.0 } },
    { name = "Stairs, top (LOCATION 5)", pos = { x = -399.587, y = 1318.163, z = 42.167, w = 1.0 } },
    { name = "Stairs, the trash pile", pos = { x = -391.116, y = 1284.479, z = 25.910, w = 1.0 } },
    { name = "Stairs, bottom (Toji)", pos = { x = -381.087, y = 1233.990, z = 23.428, w = 1.0 } },
    -- Traced from the comic: the Aoba banner on page 74 is the only one of its
    -- 28 instances in the game anywhere near here. Stand under it and look around.
    { name = "Aoba banner (comic p74)", pos = { x = -672.300, y = 395.400, z = 19.500, w = 1.0 } },
    { name = "Jig-Jig Street (the merc's job)", pos = { x = -628.711, y = 814.856, z = 18.435, w = 1.0 } },
    -- 8.5 km from anywhere the player belongs. Going there is how you find out
    -- whether the studio staged and whether Wakako's body is standing in it.
    { name = "Holocall studio floor spot", pos = { x = 5894.173, y = 6135.749, z = 0.035, w = 1.0 } },
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

-- ===========================================================================
-- POSITION CAPTURE: the reason this menu exists
-- ===========================================================================
--
-- APPENDED TO A FILE ON EVERY PRESS, and closed each time, so nothing is lost
-- to a crash and the file is readable off disk while the game is still
-- running. CET buffers its own log, so reading that back costs a quit.
--
-- The output is pasteable straight into a generator.
local captureName = "quadracer"
local captureCount = 0

-- IS THIS POINT INSIDE A SAFE AREA. Outside a club door, in a market, in a
-- ripperdoc's shop, the game holsters the player's weapon and will not let it
-- come out, so nobody standing there can be fought. That is what made the
-- Afterlife leg unplayable on its first test: the merc was spawned on the
-- entrance marker, which is the door.
--
-- Wrapped in a pcall because it is the one call in this file whose name was
-- read out of the game's scripts rather than used before. If it is not reachable
-- from Lua the panel says "?" and the redscript's own three facts still answer
-- the question; nothing else in the menu is affected.
local function inSafeArea(pos)
    local ok, res = pcall(function()
        return Game.GetSafeAreaManager():IsPointInSafeArea(
            Vector4.new(pos.x, pos.y, pos.z, 1.0))
    end)
    if not ok then return nil end
    return res
end

-- NPCS AROUND THE PLAYER, the way AMM asks for them: a targeting query with a
-- radius, the parts it returns, and the entity behind each part.
local OURS = { ["Character.cc_g02_merc"] = true, ["Character.cc_g02_queue_a"] = true,
    ["Character.cc_g02_queue_f"] = true, ["Character.cc_g02_queue_g"] = true,
    ["Character.cc_g02_queue_b"] = true, ["Character.cc_g02_queue_c"] = true,
    ["Character.cc_g02_queue_d"] = true, ["Character.cc_g02_queue_e"] = true }

local function recordName(npc)
    local ok, id = pcall(function() return npc:GetRecordID() end)
    if not ok or id == nil then return "?" end
    local s = tostring(id)
    local inner = s:match("%-%-%[%[%s*(.-)%s*%]%]")
    return inner or s
end

local function nearbyNPCs(radius)
    local out = {}
    local player = Game.GetPlayer()
    if not player then return out end
    local q = TSQ_NPC()
    q.maxDistance = radius
    q.testedSet = TargetingSet.Complete
    q.includeSecondaryTargets = false
    q.ignoreInstigator = true
    q.filterObjectByDistance = true
    local ok, parts = pcall(function()
        local _, p = Game.GetTargetingSystem():GetTargetParts(player, q)
        return p
    end)
    if not ok or parts == nil then log("nearby: targeting query failed") return out end
    local seen = {}
    for _, part in ipairs(parts) do
        local ent = nil
        pcall(function() ent = part:GetComponent():GetEntity() end)
        if ent ~= nil then
            local key = tostring(ent:GetEntityID().hash)
            if not seen[key] and not ent:IsPlayer() then
                seen[key] = true
                table.insert(out, ent)
            end
        end
    end
    return out
end

local function listNearby(radius)
    local player = Game.GetPlayer()
    local pp = player:GetWorldPosition()
    local npcs = nearbyNPCs(radius)
    log(string.format("==== %d NPC(s) within %.0f m ====", #npcs, radius))
    for _, npc in ipairs(npcs) do
        local p = npc:GetWorldPosition()
        local d = math.sqrt((p.x - pp.x)^2 + (p.y - pp.y)^2 + (p.z - pp.z)^2)
        local crowd, civ, att = "?", "?", "?"
        pcall(function() crowd = tostring(npc:IsCrowd()) end)
        pcall(function() civ = tostring(npc:IsCharacterCivilian()) end)
        pcall(function() att = tostring(npc:GetAttitudeAgent():GetAttitudeTowards(player:GetAttitudeAgent())) end)
        log(string.format("  %5.1f m  %-40s id %-14s crowd=%s civilian=%s attitude=%s", d, recordName(npc),
            tostring(npc:GetEntityID().hash), crowd, civ, att))
    end
end

local function disposeNearby(radius)
    local n = 0
    for _, npc in ipairs(nearbyNPCs(radius)) do
        if not OURS[recordName(npc)] then
            local ok = pcall(function() npc:Dispose() end)
            if ok then n = n + 1 else log("dispose failed on " .. recordName(npc)) end
        end
    end
    log(string.format("disposed %d NPC(s) within %.0f m (ours kept)", n, radius))
end

local function calmNearby(radius)
    local player = Game.GetPlayer()
    local n = 0
    for _, npc in ipairs(nearbyNPCs(radius)) do
        if not OURS[recordName(npc)] then
            pcall(function()
                npc:GetAttitudeAgent():SetAttitudeTowards(player:GetAttitudeAgent(), EAIAttitude.AIA_Friendly)
                player:GetAttitudeAgent():SetAttitudeTowards(npc:GetAttitudeAgent(), EAIAttitude.AIA_Friendly)
                npc:SetReactionPresetID(TweakDBID.new("ReactionPresets.Civilian_Neutral"))
            end)
            n = n + 1
        end
    end
    log(string.format("calmed %d NPC(s) within %.0f m", n, radius))
end

-- THE POSE LAB. Bodies are found by tag, so they survive a menu reload.
local LAB_POSES = { "sit_wounded", "kneel_afraid", "kneel_cover", "kneel_cry", "sit_scared",
                    "sit_wall_hurt", "hands_up", "kneel_inspect", "stand",
                    "lie_knockdown", "lie_knock_r", "lie_uncons", "lie_cover", "lie_wounded" }
-- "spawnhere", captured 2026-09-05 00:07. The pose spots are HERE too after
-- the next restart (built 2026-09-05); until then WALK goes to the post.
local LAB_POS = { x = -1472.817, y = 1028.142, z = 22.690, yaw = -7.9 }
-- ONE BODY, MANY TRIES. A body in a workspot or a knock-down ignores the next
-- command, so every action can first put it back to a plain standing state
-- (workspot stopped, every lab status effect removed, Relaxed) and run the
-- action a moment later. The queue below is what "a moment later" is.
local labAutoReset = true
-- What the appearance A/B last copied off a live body (backlog 42).
local abRecord, abAppearance = nil, nil
-- Quest-facts panel: a name filter and an A-Z toggle.
local factFilter, factsAZ = "", false
local labPending = nil  -- { t = seconds left, fn = function }

-- LAB LINES ALSO GO TO lab.txt, opened and closed per line so they are on
-- disk at once. The main log is buffered until the game quits, and
-- the lab is read from another machine while the game runs.
local function labLog(msg)
    log(msg)
    local f = io.open("lab.txt", "a")
    if f then f:write(os.date("%H:%M:%S ") .. tostring(msg) .. "\n"); f:close() end
end

local function labBodies()
    local out = {}
    -- CET supplies the GameInstance a script global takes; passing one is
    -- "requires 0 parameter(s)" (2026-09-05).
    local ok, ids = pcall(function() return CCLab_Find() end)
    if not ok or ids == nil then labLog("lab: CCLab_Find failed: " .. tostring(ids)) return out end
    for _, id in ipairs(ids) do
        local ent = Game.FindEntityByID(id)
        if ent ~= nil then table.insert(out, ent) end
    end
    return out
end

local labSpawned = 0
local function labSpawn(record)
    -- Each body a step further along -Y, so two spawns do not share a spot.
    local y = LAB_POS.y - 1.2 * labSpawned
    labSpawned = labSpawned + 1
    local ok, err = pcall(function() CCLab_Spawn(record, LAB_POS.x, y, LAB_POS.z, LAB_POS.yaw) end)
    labLog(ok and ("lab: spawned " .. record .. " on the post") or ("lab: spawn failed: " .. tostring(err)))
end

local function labDespawn()
    local n = 0
    for _, npc in ipairs(labBodies()) do
        pcall(function() CCLab_Despawn(npc:GetEntityID()) end)
        n = n + 1
    end
    labLog(string.format("lab: despawned %d", n))
end

local function labEach(fn, what)
    local bodies = labBodies()
    if #bodies == 0 then labLog("lab: no lab body. SPAWN one first.") return end
    for _, npc in ipairs(bodies) do
        local ok, err = pcall(fn, npc)
        labLog(ok and ("lab: " .. what) or ("lab: " .. what .. " FAILED: " .. tostring(err)))
    end
end

local LAB_STATUSES = { "Defeated", "DefeatedWithRecover", "Knockdown", "KnockdownInfinite", "Sleep",
    "Wounded", "Unconscious", "Bleeding", "BleedingInfinite", "Crippled", "CrippledLeg", "CrippledLegLeft", "CrippledLegRight" }

local function labResetOne(npc)
    pcall(function() CCLab_StopWorkspot(npc) end)
    for _, se in ipairs(LAB_STATUSES) do
        pcall(function() CCLab_Status(npc, "BaseStatusEffect." .. se, false) end)
    end
    pcall(function() CCLab_Relax(npc, true) end)
end

-- Run an action on every lab body, after a reset if that is switched on.
local function labDo(fn, what)
    if not labAutoReset then labEach(fn, what) return end
    local bodies = labBodies()
    if #bodies == 0 then labLog("lab: no lab body. SPAWN one first.") return end
    for _, npc in ipairs(bodies) do labResetOne(npc) end
    labLog("lab: reset, then in 0.8 s: " .. what)
    labPending = { t = 0.8, fn = function() labEach(fn, what) end }
end

local function labPose(pose, move, jump, idleOnly)
    local ref = "$/mod/cc_g02_cast/#cc_g02_lab_" .. pose .. "_spot"
    labDo(function(npc)
        local sent = CCLab_UseWorkspot(npc, ref, move, jump, idleOnly)
        if not sent then error("command not sent (no AI component?)") end
    end, string.format("%s move=%s jump=%s idleOnly=%s", pose, tostring(move), tostring(jump), tostring(idleOnly)))
end

local function captureCurrent(name)
    local player = Game.GetPlayer()
    if not player then return end
    local p = player:GetWorldPosition()
    local yaw = 0.0
    local ok, angles = pcall(function() return player:GetWorldOrientation():ToEulerAngles() end)
    if ok and angles then yaw = angles.yaw end
    local f = io.open("captured_positions.txt", "a")
    if f then
        f:write(string.format("%s = { x = %.3f, y = %.3f, z = %.3f, yaw = %.1f }\n",
            name, p.x, p.y, p.z, yaw))
        f:close()
    end
    captureCount = captureCount + 1
    log(string.format("CAPTURED %s = %.3f, %.3f, %.3f (yaw %.1f)", name, p.x, p.y, p.z, yaw))
end

-- WHERE IS THE THING I AM LOOKING AT. Same idea, but it takes the target's
-- position rather than the player's, which is what you want for an object you
-- cannot stand inside: the arcade cabinet, a machine on the floor, a chair.
-- WHAT IS THE CROSSHAIR ON. Three routes, tried in order, because the obvious
-- one is unreliable in exactly the case this menu exists for.
--
-- `GetLookAtObject` WAS THE ONLY ROUTE AND IT LIES. Asked for a target it
-- cannot resolve, it hands back the LAST one it did resolve, still reporting
-- the position that one had. Six captures in one session came back with
-- byte-identical coordinates, an empty name and no record, taken in two
-- different rooms several minutes apart, and every one of them looked like a
-- successful capture in the file. Confirmed at the keyboard: "I did move
-- between the takes."
--
-- So an NPC search comes first. `GetObjectClosestToCrosshair` with `TSQ_NPC()`
-- asks the targeting system for the nearest NPC to where the player is aiming,
-- which is the actual question whenever the thing being captured is a person,
-- and it cannot answer with a pachinko cabinet.
local function lookedAtObject()
    local player = Game.GetPlayer()
    local ts = Game.GetTargetingSystem()
    local obj = nil

    -- 1. the nearest NPC to the crosshair.
    pcall(function()
        obj = ts:GetObjectClosestToCrosshair(player, EulerAngles.new(0, 0, 0),
                                             TSQ_NPC())
    end)
    if obj ~= nil then return obj, "nearest NPC to crosshair" end

    -- 2. anything in plain sight. For objects rather than people.
    pcall(function() obj = ts:GetLookAtObject(player, true, true) end)
    if obj ~= nil then return obj, "look-at, line of sight" end

    -- 3. the permissive form, which is the one that lies. Last.
    pcall(function() obj = ts:GetLookAtObject(player, false, false) end)
    if obj ~= nil then return obj, "look-at, no line of sight" end
    return nil, nil
end

local function captureLookedAt(name)
    local target, how = lookedAtObject()
    if target == nil then
        log("capture: nothing targeted. Stand closer and put the crosshair on it.")
        return
    end

    local p = target:GetWorldPosition()
    local yaw = 0.0
    pcall(function() yaw = target:GetWorldOrientation():ToEulerAngles().yaw end)
    local what = ""
    pcall(function() what = tostring(target:GetDisplayName()) end)
    -- THE RECORD, NOT ONLY THE NAME. A display name says "Street Vendor", which
    -- is a hundred different NPCs; the record id is the one thing a Character
    -- record of ours can be based on, so it is what a borrowed body needs.
    local rec = nil
    pcall(function() rec = tostring(target:GetRecord():GetID()) end)
    local app = "?"
    pcall(function() app = tostring(target:GetCurrentAppearanceName()) end)

    -- REFUSE A TARGET THAT CANNOT SAY WHAT IT IS. An object with neither a name
    -- nor a record is the dead handle described above. Writing the line is
    -- worse than writing nothing, because nothing announces it.
    if rec == nil and what == "" then
        log("capture REFUSED: the crosshair is not on anything the game can")
        log("  identify, which usually means the NPC is not actually there.")
        log("  Face them, check you can SEE them, then open the overlay.")
        return
    end

    -- HOW FAR AWAY IT IS, because a target forty metres off is not the one in
    -- front of you, and the entity id, because two captures of the same id are
    -- the same body however different the two names look.
    local away = 0.0
    pcall(function()
        local me = Game.GetPlayer():GetWorldPosition()
        away = math.sqrt((p.x - me.x) ^ 2 + (p.y - me.y) ^ 2 + (p.z - me.z) ^ 2)
    end)
    local eid = "?"
    pcall(function()
        local id = target:GetEntityID()
        local ok, h = pcall(function() return id.hash end)
        eid = tostring(ok and h or id)
    end)

    local f = io.open("captured_positions.txt", "a")
    if f then
        f:write(string.format(
            "%s = { x = %.3f, y = %.3f, z = %.3f, yaw = %.1f }  -- %s  record: %s  %.1f m  id: %s  via: %s\n",
            name, p.x, p.y, p.z, yaw,
            what ~= "" and what or "(no name)", rec or "?", away, eid, how))
        f:close()
    end
    captureCount = captureCount + 1
    log(string.format("CAPTURED (looked at) %s = %.3f, %.3f, %.3f  [%s / %s] appearance=%s %.1f m via %s",
        name, p.x, p.y, p.z, what, rec or "?", app, away, how))
end

-- ===========================================================================
-- WHAT AM I LOOKING AT
-- ===========================================================================
--
-- Aimed at PUPPETS rather than at devices, which is the opposite of gig 01's
-- version, because the things this gig needs to interrogate are the merc, Toji
-- and the Claws. It answers the three questions the build cannot answer from
-- here: is he alive, can he be hurt, and has he seen the player.
--
-- EVERY PROBE IS WRAPPED AND TRIED ALONE. CET cannot be asked whether a method
-- exists and a missing one throws, so a row that says "<no such method>" is not
-- a failure: it is that this kind of object does not have that idea.
local function dumpLookedAt(name)
    local target = Game.GetTargetingSystem():GetLookAtObject(Game.GetPlayer(), false, false)
    if target == nil then
        log("look: nothing targeted.")
        return
    end

    local lines = {}
    local function say(fmt, ...)
        local text = select("#", ...) > 0 and string.format(fmt, ...) or fmt
        table.insert(lines, text)
        log("look: " .. text)
    end
    local function head(t) say(""); say("-- %s", t) end
    local function m(label, fn)
        local ok, v = pcall(fn)
        say("  %-26s %s", label, ok and tostring(v) or "<no such method>")
    end

    say("==== %s ====", name ~= "" and name or "looked-at")

    head("identity")
    local p = target:GetWorldPosition()
    say("  %-26s %.3f, %.3f, %.3f", "position", p.x, p.y, p.z)
    m("yaw", function() return target:GetWorldOrientation():ToEulerAngles().yaw end)
    m("class", function() return target:GetClassName() end)
    m("display name", function() return target:GetDisplayName() end)
    m("record", function() return target:GetRecord():GetID() end)
    m("entity id", function()
        local id = target:GetEntityID()
        local ok, h = pcall(function() return id.hash end)
        if ok and h ~= nil then return h end
        return id
    end)
    m("is puppet", function() return target:IsPuppet() end)
    m("is device", function() return target:IsDevice() end)

    -- CAN HE BE HURT, AND IS HE DOWN. The merc is held at Immortal through the
    -- fight, so his health falls and stops short of zero; the threshold that
    -- declares him beaten is 25. If health will not move at all he is on
    -- Invulnerable, which is the state he is supposed to be in BEFORE V speaks
    -- to him and AFTER he is down, and never during.
    head("damage")
    m("health %", function()
        return Game.GetStatPoolsSystem():GetStatPoolValue(
            target:GetEntityID(), gamedataStatPoolType.Health, false)
    end)
    m("IsDead", function() return target:IsDead() end)
    m("IsDefeated", function() return target:IsDefeated() end)

    -- HAS HE SEEN THE PLAYER. `highLevelState` is what the gig's own stealth
    -- check reads: Combat means spotted. Relaxed or Alerted does not.
    -- The attitude GROUP is what decides the reticle, which is why a friendly
    -- NPC cannot be locked onto however much god mode he has.
    head("attitude and awareness")
    m("highLevelState", function() return target:GetHighLevelStateFromBlackboard() end)
    m("IsAggressive", function() return target:IsAggressive() end)
    m("attitude group", function() return target:GetAttitudeAgent():GetAttitudeGroup() end)
    m("attitude to player", function()
        return target:GetAttitudeAgent():GetAttitudeTowards(
            Game.GetPlayer():GetAttitudeAgent())
    end)
    m("affiliation", function() return target:GetRecord():Affiliation():Type() end)

    local fh = io.open("looked_at.txt", "a")
    if fh then
        for _, line in ipairs(lines) do fh:write(line .. "\n") end
        fh:write("\n")
        fh:close()
    end
end

-- ===========================================================================
-- THE JOURNAL, WHICH IS WHERE THE OPENING LIVES
-- ===========================================================================
--
-- The gig opens on an SMS thread, and four separate entries have to be Active
-- before the player can answer it: the contact, its conversation, the message
-- and the choice group. A missing one is silent and looks like "the message
-- never arrived".
local JOURNAL = {
    { "contacts/cc_g02_wakako", "gameJournalContact" },
    { "contacts/cc_g02_wakako/cc_g02_wakako_conv", "gameJournalPhoneConversation" },
    { "contacts/cc_g02_wakako/cc_g02_wakako_conv/cc_g02_msg_01", "gameJournalPhoneMessage" },
    { "contacts/cc_g02_wakako/cc_g02_wakako_conv/cc_g02_ch_01", "gameJournalPhoneChoiceGroup" },
    { "contacts/cc_g02_wakako/cc_g02_wakako_conv/cc_g02_ch_01/cc_g02_ch_01a", "gameJournalPhoneChoiceEntry" },
    { "contacts/cc_g02_yoko", "gameJournalContact" },
    { "quests/street_stories/cc_g02_dead_ringer", "gameJournalQuest" },
    { "points_of_interest/street_stories/cc_g02_dead_ringer", "gameJournalPointOfInterestMappin" },
}

local OBJECTIVES = {
    "obj_afterlife", "obj_lead", "obj_merc", "obj_beat", "obj_proof",
    "obj_wakako2", "obj_inn", "obj_trace", "obj_parlor", "obj_relay",
    "obj_face", "obj_wakako_met", "obj_hit", "obj_toji", "obj_toji_loud",
    "obj_exfil", "obj_exfil_loud", "obj_call_wakako", "obj_johnny_3",
}

-- objective -> its pin, for the five that have one. A PIN IS A JOURNAL ENTRY IN
-- ITS OWN RIGHT and the engine never queries an inactive one, so an objective
-- that is Active with a pin that is not is the single commonest way a map pin
-- goes missing. This prints both.
local PINS = {
    obj_afterlife = "pin_afterlife",
    obj_inn = "pin_inn",
    obj_parlor = "pin_parlor",
    obj_wakako_met = "pin_wakako_met",
    obj_hit = "pin_hit",
}

local PHASE = "quests/street_stories/cc_g02_dead_ringer/phase_main"

local function entryState(path, class)
    local jm = Game.GetJournalManager()
    if jm == nil then return "no journal manager" end
    local ok, res = pcall(function()
        local e = jm:GetEntryByString(path, class)
        if e == nil then return "NOT FOUND" end
        local ok2, state = pcall(function() return jm:GetEntryState(e) end)
        return ok2 and tostring(state) or ("exists, state unreadable")
    end)
    return ok and res or ("ERROR: " .. tostring(res))
end

-- FORCE THE REPLY. The quest phase pauses on the choice ENTRY going Succeeded,
-- which is the one gate in the gig that is not a fact and so cannot be set from
-- the facts panel. Without this there is no way past the opening except by
-- opening the phone and pressing the reply, which is exactly what a tester
-- wants to skip on the fifth run.
local function forceReply()
    local jm = Game.GetJournalManager()
    if jm == nil then return end
    local path = "contacts/cc_g02_wakako/cc_g02_wakako_conv/cc_g02_ch_01/cc_g02_ch_01a"
    local ok, err = pcall(function()
        jm:ChangeEntryState(path, "gameJournalPhoneChoiceEntry",
            gameJournalEntryState.Succeeded, JournalNotifyOption.Notify)
    end)
    log(ok and "forced the reply Succeeded; the call should place itself"
           or ("could not force the reply: " .. tostring(err)))
end

-- ===========================================================================
-- JUMPING FORWARD, AND WHAT IT DOES NOT DO
-- ===========================================================================
--
-- Setting a fact does NOT skip the scene attached to it. Gig 01 established
-- that the hard way: a quest phase parked on a pause node advances when that
-- pause completes and then runs its chain, and a scene node in that chain
-- PLAYS. Both of its attempts at a dev branch that entered a scene directly
-- failed, one of them by crashing the game on load, because a scene node cannot
-- be entered from two places.
--
-- So a jump sets every gate up to the chosen beat and the graph then runs
-- forward through everything in between, playing each scene as it goes. With
-- placeholder tones that is a couple of minutes of beeping rather than a couple
-- of hours of driving, which is the whole benefit and is worth being honest
-- about.
--
-- IT ONLY WORKS FORWARDS. Facts persist, so a jump cannot be undone by clearing
-- them: the graph has already moved. Reload the save.
local JUMPS = {
    { label = "1. the message has arrived", upto = "cc_g02_start" },
    { label = "2. the call is placed", upto = "cc_g02_called" },
    { label = "3. outside Afterlife", upto = "cc_g02_afterlife_reached" },
    { label = "4. both groups heard, the merc's group is marked", upto = "cc_g02_groups_done" },
    { label = "5. the merc is beaten", upto = "cc_g02_merc_down" },
    { label = "6. the proof is read", upto = "cc_g02_proof_read" },
    { label = "7. at the Dewdrop Inn", upto = "cc_g02_inn_reached" },
    { label = "8. at the parlor", upto = "cc_g02_parlor_reached" },
    { label = "9. the access point is breached", upto = "cc_g02_ap_breached" },
    { label = "9b. the relay is with Char", upto = "cc_g02_char_named" },
    { label = "11. in Wakako's office", upto = "cc_g02_office_reached" },
    { label = "12. at the side street", upto = "cc_g02_hit_reached" },
}

-- ONLY THE FACTS THE PLAYER WOULD HAVE PRODUCED. The graph sets its own as it
-- passes them, and setting one early tells the script a beat has happened when
-- the graph has not reached it, which is how a jump turns into a gig that skips
-- a scene and then waits forever on the fact that scene was supposed to set.
local function jumpTo(upto)
    local qs = Game.GetQuestsSystem()
    if qs == nil then return end
    local set = 0
    for _, step in ipairs(STEPS) do
        if step.who == "SCRIPT" and qs:GetFactStr(step.fact) == 0 then
            qs:SetFactStr(step.fact, 1)
            set = set + 1
        end
        if step.fact == upto then break end
    end
    -- The reply is a journal entry rather than a fact, so it needs its own
    -- push, and only if the jump is meant to go past it.
    if upto ~= "cc_g02_start" then forceReply() end
    log(string.format("jumped to %s: set %d player-side fact(s). The scenes in "
        .. "between will now play through.", upto, set))
end

registerForEvent("onInit", function()
    loadPresets()
end)

registerForEvent("onUpdate", function(dt)
    if labPending ~= nil then
        labPending.t = labPending.t - dt
        if labPending.t <= 0 then
            local fn = labPending.fn
            labPending = nil
            fn()
        end
    end
end)
registerForEvent("onOverlayOpen", function() visible = true end)
registerForEvent("onOverlayClose", function() visible = false end)

registerForEvent("onDraw", function()
    if not visible then return end
    if not ImGui.Begin("Dead Ringer [DEV]") then
        ImGui.End()
        return
    end

    local qs = Game.GetQuestsSystem()
    local player = Game.GetPlayer()

    -- ALWAYS OPEN: the two things used in every session. Everything else is
    -- a collapsed section named for what it does (2026-09-05).
    ImGui.Text("CAPTURE A POSITION, OR DUMP WHAT I AM LOOKING AT")
    ImGui.Separator()
    --
    -- HIGH UP ON PURPOSE. Not one position in this gig has been stood on, and
    -- replacing them is the largest single improvement available to it.
    ImGui.Spacing()
    ImGui.TextDisabled("Appends to captured_positions.txt, readable while the game runs.")
    captureName = ImGui.InputText("name", captureName, 64)
    if ImGui.Button("CAPTURE WHERE I STAND") then
        captureCurrent(captureName)
    end
    ImGui.SameLine()
    if ImGui.Button("CAPTURE WHAT I'M LOOKING AT") then
        captureLookedAt(captureName)
    end
    ImGui.SameLine()
    -- A STATIC MESH HAS NO ENTITY TO CAPTURE (the arcade cabinets, 2026-09-05):
    -- this writes where the crosshair's ray lands on static geometry instead.
    if ImGui.Button("CAPTURE THE SURFACE I'M LOOKING AT") then
        local ok, hit = pcall(function() return CCLab_RayHit(Game.GetPlayer()) end)
        if ok and hit ~= nil and hit.w > 0.5 then
            local f = io.open("captured_positions.txt", "a")
            if f then
                f:write(string.format("%s = { x = %.3f, y = %.3f, z = %.3f }  -- surface under the crosshair (static ray)\n",
                    captureName, hit.x, hit.y, hit.z))
                f:close()
            end
            captureCount = captureCount + 1
            log(string.format("surface: %.3f, %.3f, %.3f", hit.x, hit.y, hit.z))
        else
            log("surface: no static hit within 40 m")
        end
    end
    if captureCount > 0 then
        ImGui.Text(string.format("%d capture(s) this session", captureCount))
    end
    ImGui.TextDisabled("Look-at prefers the nearest NPC to the crosshair, and refuses")
    ImGui.TextDisabled("a target it cannot name. It reports metres away and an id:")
    ImGui.TextDisabled("the same id twice is the same body, whatever the name says.")
    ImGui.TextDisabled("SURFACE is for things that are not NPCs: put the crosshair on the")
    ImGui.TextDisabled("parlor wall where the box should hang and press it; that is the number")
    ImGui.TextDisabled("the access point on the parlor wall is placed at.")

    ImGui.Spacing()
    -- IS THE BOX THERE AT ALL (2026-09-05): every entity the targeting system
    -- knows within 15 m, class and position, to the console and the log. A
    -- device the game placed shows up here; so does ours, if it spawned.
    if ImGui.Button("LIST EVERYTHING NEAR ME (15 m) -> log") then
        local player = Game.GetPlayer()
        local q = TSQ_ALL()
        q.maxDistance = 15.0
        q.testedSet = TargetingSet.Complete
        q.includeSecondaryTargets = false
        q.ignoreInstigator = true
        q.filterObjectByDistance = true
        local ok, parts = pcall(function()
            local _, p = Game.GetTargetingSystem():GetTargetParts(player, q)
            return p
        end)
        if not ok or parts == nil then
            log("near: targeting query failed")
        else
            local me = player:GetWorldPosition()
            local seen, n = {}, 0
            for _, part in ipairs(parts) do
                local ent = nil
                pcall(function() ent = part:GetComponent():GetEntity() end)
                if ent ~= nil then
                    local key = tostring(ent:GetEntityID().hash)
                    if not seen[key] and not ent:IsPlayer() then
                        seen[key] = true
                        n = n + 1
                        local p = ent:GetWorldPosition()
                        local cls, nm = "?", ""
                        pcall(function() cls = tostring(ent:GetClassName().value) end)
                        pcall(function() nm = tostring(ent:GetDisplayName()) end)
                        local d = math.sqrt((p.x - me.x) ^ 2 + (p.y - me.y) ^ 2 + (p.z - me.z) ^ 2)
                        log(string.format("near %5.1f m  %-28s %-22s at %.2f, %.2f, %.2f", d, cls, nm, p.x, p.y, p.z))
                    end
                end
            end
            log(string.format("near: %d entities within 15 m; our box should be at -663.25, 822.33, 20.90 (class AccessPoint)", n))
        end
    end
    ImGui.TextDisabled("Stand by the parlor's south wall and press this: an 'AccessPoint' line at")
    ImGui.TextDisabled("-663.7, 822.3 means the box exists; no such line means it never spawned.")
    -- THE BOX, SPAWNED WHERE I STAND (2026-09-05): the game's own access point
    -- entity through the dynamic entity system, no sector, no restart, one
    -- appearance per button. It answers "does this box render at all, and
    -- what does each look wear" without a build. A dynamic device may or may
    -- not offer "Jack in"; the sector node is what ships.
    ImGui.TextDisabled("Spawn the access point where I stand, 1.3 m up, facing the way I face:")
    -- THE FOUR LOOKS THAT CARRY THE JACK (gotcha 98); the sockets and router_b
    -- draw a box with no "Jack in".
    local apLooks = { "access_point_router_entropy", "access_point_antenna_small_access_point_entropy_a", "access_point_antenna_small_access_point_neomilitary_b", "access_point_arasaka_access_point_b" }
    for _, look in ipairs(apLooks) do
        if ImGui.Button("SPAWN A BOX HERE: " .. look) then
            local ok, err = pcall(function()
                local player = Game.GetPlayer()
                local p = player:GetWorldPosition()
                local yaw = player:GetWorldYaw()
                local spec = DynamicEntitySpec.new()
                -- gotcha 28: a backslash typed into this string gets eaten; the path is joined at run time.
                local bs = string.char(92)
                local entPath = table.concat({ "base", "gameplay", "devices", "masters", "access_points", "accesspoint.ent" }, bs)
                spec.templatePath = ResRef.FromName(entPath)
                spec.appearanceName = look
                spec.position = Vector4.new(p.x, p.y, p.z + 1.3, 1.0)
                spec.orientation = EulerAngles.ToQuat(EulerAngles.new(0, 0, yaw))
                spec.persistState = false
                spec.persistSpawn = false
                spec.alwaysSpawned = true
                spec.spawnInView = true
                spec.active = true
                spec.tags = { "cc_g02_lab" }
                local id = Game.GetDynamicEntitySystem():CreateEntity(spec)
                log(string.format("box spawned (%s) at %.2f, %.2f, %.2f yaw %.1f  id %s", look, p.x, p.y, p.z + 1.3, yaw, tostring(id)))
            end)
            if not ok then log("box spawn failed: " .. tostring(err)) end
        end
    end
    -- ...AND ON THE SURFACE UNDER THE CROSSHAIR (2026-09-05): the static ray
    -- the capture button uses gives the wall point, the box faces the player,
    -- and the numbers logged are the ones the shipped node takes.
    ImGui.TextDisabled("Or on the wall under the crosshair, facing you (logs position and yaw):")
    for _, look in ipairs(apLooks) do
        if ImGui.Button("SPAWN WHERE I LOOK: " .. look) then
            local ok, err = pcall(function()
                local player = Game.GetPlayer()
                local hit = CCLab_RayHit(player)
                if hit == nil or hit.w < 0.5 then log("spawn: no static surface under the crosshair within 40 m") return end
                local me = player:GetWorldPosition()
                -- a hand's breadth off the wall, toward the player, so the mesh is not inside it
                local dx, dy = me.x - hit.x, me.y - hit.y
                local len = math.sqrt(dx * dx + dy * dy)
                if len < 0.01 then len = 0.01 end
                local px, py = hit.x + dx / len * 0.03, hit.y + dy / len * 0.03
                local yaw = player:GetWorldYaw() + 180.0
                if yaw > 180.0 then yaw = yaw - 360.0 end
                local spec = DynamicEntitySpec.new()
                local bs = string.char(92)
                spec.templatePath = ResRef.FromName(table.concat({ "base", "gameplay", "devices", "masters", "access_points", "accesspoint.ent" }, bs))
                spec.appearanceName = look
                spec.position = Vector4.new(px, py, hit.z, 1.0)
                spec.orientation = EulerAngles.ToQuat(EulerAngles.new(0, 0, yaw))
                spec.persistState = false
                spec.persistSpawn = false
                spec.alwaysSpawned = true
                spec.spawnInView = true
                spec.active = true
                spec.tags = { "cc_g02_lab" }
                Game.GetDynamicEntitySystem():CreateEntity(spec)
                local line = string.format("box (%s) on the wall at %.3f, %.3f, %.3f yaw %.1f", look, px, py, hit.z, yaw)
                log(line)
                local f = io.open("captured_positions.txt", "a")
                if f then f:write(line .. string.char(10)) f:close() end
            end)
            if not ok then log("spawn failed: " .. tostring(err)) end
        end
    end
    -- THE SHIPPED BOX'S OWN STATE (2026-09-05: the router drew at its spot with
    -- no "Jack in"). The device nearest the box, its persistent state read
    -- back, and the switches the game's own devices use, each on its own
    -- button so the one that opens the prompt is known.
    local function findAP()
        local player = Game.GetPlayer()
        local q = TSQ_ALL()
        q.maxDistance = 20.0
        q.testedSet = TargetingSet.Complete
        q.includeSecondaryTargets = false
        q.ignoreInstigator = true
        q.filterObjectByDistance = true
        local ok, parts = pcall(function() local _, p = Game.GetTargetingSystem():GetTargetParts(player, q) return p end)
        if not ok or parts == nil then return nil end
        local best, bestD = nil, 3.0
        for _, part in ipairs(parts) do
            local ent = nil
            pcall(function() ent = part:GetComponent():GetEntity() end)
            if ent ~= nil then
                local cls = ""
                pcall(function() cls = tostring(ent:GetClassName().value) end)
                if cls == "AccessPoint" then
                    local p = ent:GetWorldPosition()
                    local d = math.sqrt((p.x + 663.25) ^ 2 + (p.y - 822.33) ^ 2 + (p.z - 20.9) ^ 2)
                    if d < bestD then best, bestD = ent, d end
                end
            end
        end
        return best
    end
    local function apTry(label, fn)
        local ok, res = pcall(fn)
        log(string.format("  %-28s %s", label, ok and tostring(res) or ("FAILED: " .. tostring(res))))
    end
    -- =======================================================================
    -- THE HOLOCALL PROBE
    -- =======================================================================
    --
    -- WHY IT EXISTS. Nothing the game writes says whether a piece of the
    -- holocall studio is loaded: RED4ext logs plugins, redscript logs
    -- compiling, TweakXL logs records, ArchiveXL logs appearances. So three
    -- explanations of one bug were wrong in a row on 2026-09-07 before this
    -- was built.
    --
    -- WHAT IT ALREADY PROVED, first run, and it is why the breadcrumbs print
    -- FIRST: `cc_g02_call1_claim` is which arm of the studio race won, 1 for
    -- "the camera loaded" and 2 for "the 20-second giveup". A late save read
    -- claim 1 and video 1, and Wakako was on the phone. An early save read
    -- claim 2 and video 0, and the frame was empty. So the call is not
    -- failing: the camera never arrives in time and the call goes ahead
    -- without a feed.
    --
    -- WHAT IS STILL UNKNOWN is WHICH pieces are missing on that save, which
    -- is what the node rows below are for. The first version of them asked
    -- the wrong question and answered false to everything, including nodes
    -- that were demonstrably present, so the rows are worth nothing unless
    -- `#holocalls_studio` reads true during a call that WORKS. Check that
    -- control row first; if it is false the probe is still lying.
    local HOLO_REFS = {
        { "#holocalls_studio",          "the studio (control: true when a call works)" },
        { "#wakako_holocall_setup",     "WAKAKO bundle" },
        { "#wakako_holocall_camera",    "WAKAKO camera  <- the race waits on this" },
        { "#wakako_holocall_workspot",  "WAKAKO chair" },
        { "#regina_holocall_camera",    "control: Regina" },
        { "#vik_holocall_camera",       "control: Vik" },
        { "#blue_moon_holocall_camera", "CHAR rides this one" },
    }

    -- THREE SIGNALS PER REF, because which one the game answers is itself
    -- unknown. `GlobalNodeRef.IsDefined` is the only documented one; the two
    -- entity lookups are the ones that say whether it is actually streamed.
    -- Errors are printed, never swallowed.
    local function holoRow(refStr)
        local ok, nodeRef = pcall(function() return CreateNodeRef(refStr) end)
        if not ok then return "CreateNodeRef failed" end
        local okG, g = pcall(function()
            return ResolveNodeRef(nodeRef, GlobalNodeID.GetRoot())
        end)
        if not okG then return "resolve failed: " .. tostring(g):sub(1, 40) end
        local defined, ent, byHash = "?", "?", "?"
        local a, b = pcall(function() return GlobalNodeRef.IsDefined(g) end)
        defined = a and tostring(b) or "err"
        a, b = pcall(function() return Game.FindEntityByID(g) ~= nil end)
        ent = a and tostring(b) or "err"
        a, b = pcall(function() return Game.FindEntityByID(entEntityID.new({ hash = g.hash })) ~= nil end)
        byHash = a and tostring(b) or "err"
        return string.format("defined=%-5s entity=%-5s byHash=%-5s", defined, ent, byHash)
    end

    if ImGui.Button("HOLO PROBE: what of the studio is loaded -> log") then
        -- BREADCRUMBS FIRST. Both logs are capped at 8 KB and the third run of
        -- the first version was lost to that, so the part that has already
        -- answered a question is written before the part that has not.
        log("=== holocall probe ===")
        local qs = Game.GetQuestsSystem()
        local crumbs = {}
        for _, f in ipairs({ "cc_g02_called", "cc_g02_call1_claim", "cc_g02_call1_step",
                             "cc_g02_call1_video", "cc_g02_call1_talking",
                             "cc_g02_call1_done" }) do
            crumbs[#crumbs + 1] = f:gsub("cc_g02_call1_", ""):gsub("cc_g02_", "")
                                  .. "=" .. tostring(qs:GetFactStr(f))
        end
        log("  " .. table.concat(crumbs, "  "))
        log("  claim 1 = the camera loaded, 2 = the 20 s giveup won")
        for _, row in ipairs(HOLO_REFS) do
            log(string.format("  %-28s %-46s %s", row[1], holoRow(row[1]), row[2]))
        end
        log("=== end of probe ===")
    end
    ImGui.Text("Press DURING a call. Compare a save where it works with one where it does not.")
    ImGui.Separator()

    if ImGui.Button("AP PROBE: the shipped box's state -> log") then
        local dev = findAP()
        if dev == nil then log("ap: no AccessPoint entity within 3 m of the box's spot (stand next to it)") else
            log("ap: entity found")
            apTry("GetDevicePS", function() return dev:GetDevicePS() ~= nil end)
            local ps = dev:GetDevicePS()
            if ps ~= nil then
                apTry("GetDeviceState", function() return ps:GetDeviceState() end)
                apTry("IsON", function() return ps:IsON() end)
                apTry("IsDisabled", function() return ps:IsDisabled() end)
                apTry("IsUnpowered", function() return ps:IsUnpowered() end)
                apTry("IsInitialized", function() return ps:IsInitialized() end)
                apTry("IsAttachedToGame", function() return ps:IsAttachedToGame() end)
                apTry("IsBreached", function() return ps:IsBreached() end)
                apTry("HasNetworkBackdoor", function() return ps:HasNetworkBackdoor() end)
                apTry("HasPersonalLinkSlot", function() return ps:HasPersonalLinkSlot() end)
                apTry("GetDeviceName", function() return ps:GetDeviceName() end)
                apTry("GetClearance", function() return ps:GetClearance() end)
                apTry("IsLogicReady (entity)", function() return dev:IsLogicReady() end)
                apTry("GetInteractionState", function() return ps:IsInteractive() end)
            end
        end
    end
    if ImGui.Button("AP: ForceEnableDevice") then local d = findAP(); if d then apTry("ForceEnableDevice", function() d:GetDevicePS():ForceEnableDevice() return "called" end) else log("ap: not found") end end
    ImGui.SameLine()
    if ImGui.Button("AP: SetDeviceState ON") then local d = findAP(); if d then apTry("SetDeviceState(ON)", function() d:GetDevicePS():SetDeviceState(EDeviceStatus.ON) return "called" end) else log("ap: not found") end end
    ImGui.SameLine()
    if ImGui.Button("AP: TurnOnDevice") then local d = findAP(); if d then apTry("TurnOnDevice", function() d:GetDevicePS():TurnOnDevice() return "called" end) else log("ap: not found") end end
    ImGui.SameLine()
    if ImGui.Button("AP: RefreshInteractions") then local d = findAP(); if d then apTry("RefreshInteraction", function() d:RefreshInteraction(gamedeviceRequestType.Direct, Game.GetPlayer()) return "called" end) else log("ap: not found") end end
    -- TURN AND NUDGE THE SHIPPED BOX IN PLACE (2026-09-05): the interaction
    -- volume of a wall box sits in front of its face, so a node facing into
    -- the wall keeps its prompt inside the wall. The teleport facility moves
    -- any entity, sector node included, until the next load.
    local function apMove(dyaw, out)
        local dev = findAP()
        if dev == nil then log("ap: not found") return end
        local ok, err = pcall(function()
            local p = dev:GetWorldPosition()
            local yaw = dev:GetWorldYaw() + dyaw
            local rad = math.rad(yaw)
            -- forward for this game's yaw: (-sin, cos)
            local nx, ny = p.x - math.sin(rad) * out, p.y + math.cos(rad) * out
            Game.GetTeleportationFacility():Teleport(dev, Vector4.new(nx, ny, p.z, 1.0), EulerAngles.new(0, 0, yaw))
            log(string.format("ap moved: %.3f, %.3f, %.3f yaw %.1f", nx, ny, p.z, yaw))
        end)
        if not ok then log("ap move failed: " .. tostring(err)) end
    end
    if ImGui.Button("AP: turn 180") then apMove(180.0, 0.0) end
    ImGui.SameLine()
    if ImGui.Button("AP: turn +90") then apMove(90.0, 0.0) end
    ImGui.SameLine()
    if ImGui.Button("AP: turn -90") then apMove(-90.0, 0.0) end
    ImGui.SameLine()
    if ImGui.Button("AP: out of the wall 0.15 m") then apMove(0.0, 0.15) end
    ImGui.SameLine()
    if ImGui.Button("AP: SetHasPersonalLinkSlot") then local d = findAP(); if d then apTry("SetHasPersonalLinkSlot(true)", function() d:GetDevicePS():SetHasPersonalLinkSlot(true) return "called" end) else log("ap: not found") end end
    -- HEIGHT (2026-09-05): the small router's prompt volume is a sphere 1.4 m
    -- ABOVE its own origin (access_point.app), so a router hung at chest
    -- height offers nothing; the game's own router_b node sits near the
    -- floor. Lower it until "Jack in" shows, then read the height off the log.
    local function apLift(dz)
        local dev = findAP()
        if dev == nil then log("ap: not found") return end
        local ok, err = pcall(function()
            local p = dev:GetWorldPosition()
            local yaw = dev:GetWorldYaw()
            Game.GetTeleportationFacility():Teleport(dev, Vector4.new(p.x, p.y, p.z + dz, 1.0), EulerAngles.new(0, 0, yaw))
            log(string.format("ap moved: %.3f, %.3f, %.3f yaw %.1f", p.x, p.y, p.z + dz, yaw))
        end)
        if not ok then log("ap move failed: " .. tostring(err)) end
    end
    local function apSlide(dx, dy)
        local dev = findAP()
        if dev == nil then log("ap: not found") return end
        local ok, err = pcall(function()
            local p = dev:GetWorldPosition(); local yaw = dev:GetWorldYaw()
            Game.GetTeleportationFacility():Teleport(dev, Vector4.new(p.x + dx, p.y + dy, p.z, 1.0), EulerAngles.new(0, 0, yaw))
            log(string.format("ap moved: %.3f, %.3f, %.3f yaw %.1f", p.x + dx, p.y + dy, p.z, yaw))
        end)
        if not ok then log("ap move failed: " .. tostring(err)) end
    end
    -- On the parlor's south wall, facing it, V's right is west (x down).
    if ImGui.Button("AP: west 0.1 (my right)") then apSlide(-0.1, 0) end
    ImGui.SameLine()
    if ImGui.Button("AP: east 0.1 (my left)") then apSlide(0.1, 0) end
    ImGui.SameLine()
    if ImGui.Button("AP: down 0.3 m") then apLift(-0.3) end
    ImGui.SameLine()
    if ImGui.Button("AP: down 0.1 m") then apLift(-0.1) end
    ImGui.SameLine()
    if ImGui.Button("AP: up 0.1 m") then apLift(0.1) end
    ImGui.SameLine()
    if ImGui.Button("AP: up 0.3 m") then apLift(0.3) end
    -- THE MINIGAME RECORDS (2026-09-05): our daemon records and the game's, as
    -- TweakDB sees them at run time, to see whether the tweak file applied and
    -- what the device currently names as its minigame.
    if ImGui.Button("TWEAK FLATS: minigame records -> log") then
        local paths = {
            "minigame_v2.cc_g02_parlor.bufferSize", "minigame_v2.cc_g02_parlor.overrideProgramsList",
            "minigame_v2.cc_g02_parlor_inline0.program", "MinigameAction.cc_g02_access_data.objectActionUI",
            "Interactions.cc_g02_access_data.caption", "minigame_v2.Kab08Minigame.overrideProgramsList",
            "minigame_v2.Kab08Minigame_inline0.program", "minigame_v2.FindAnna.objectActionUI",
            "MinigameAction.NetworkDataMineLootAll.objectActionUI",
        }
        for _, pth in ipairs(paths) do
            local ok, v = pcall(function() return TweakDB:GetFlat(pth) end)
            log(string.format("  %-60s %s", pth, ok and tostring(v) or ("FAILED " .. tostring(v))))
        end
        local d = findAP()
        if d then apTry("GetMinigameDefinition (device)", function() return d:GetDevicePS():GetMinigameDefinition() end) end
    end
    -- CHAR'S TWO FACES (playtest 2026-09-05, several reports): the chair body
    -- and the phone body both ask for slacker_wa_slacker_wa_03 and do not
    -- match. This prints what the record resolves to, so the entity behind
    -- the look can be read off disk.
    if ImGui.Button("TWEAK FLATS: Char's record -> log") then
        local paths = {
            "Character.cc_g02_char.entityTemplatePath", "Character.cc_g02_char.appearanceName",
            "Character.cc_g02_char.crowdAppearanceNames",
            "Character.SlackerFemale.entityTemplatePath", "Character.SlackerFemale.appearanceName",
            "Character.SlackerFemale.crowdAppearanceNames",
        }
        for _, pth in ipairs(paths) do
            local ok, v = pcall(function() return TweakDB:GetFlat(pth) end)
            local shown = ok and v or ("FAILED " .. tostring(v))
            if ok and type(v) == "table" then shown = table.concat((function() local t = {} for _, x in ipairs(v) do t[#t + 1] = tostring(x) end return t end)(), ", ") end
            log(string.format("  %-52s %s", pth, tostring(shown)))
        end
    end
    -- WHAT THE GAME PAYS FOR WAKAKO'S OWN GIGS (design question 2026-09-06):
    -- the completion reward records of her nine Westbrook gigs. inline4 is the
    -- currency entry and inline5 its quantity modifier; inline1 and inline3
    -- are the XP and Street Cred ones. Values are flats, so they can only be
    -- read here, in game.
    -- THE HIT AREA TEST (backlog 39): does the area node stand as an entity,
    -- and does the game hold an AREA pin for the way out. The access point is
    -- the control: a node in the same sector that is known to work.
    if ImGui.Button("HIT AREA: node + map pins -> log") then
        local refs = {
            { name = "hit area node",   path = "$/03_night_city/#c_westbrook/japantown/#cc_g02_hit_area" },
            { name = "access point (control)", path = "$/03_night_city/#c_westbrook/japantown/#cc_g02_access_point" },
        }
        for _, r in ipairs(refs) do
            local ok, v = pcall(function() return CCLab_NodeEntity(Game.GetPlayer(), r.path) end)
            if not ok or v == nil then
                log("  " .. r.name .. ": probe failed: " .. tostring(v))
            elseif v.w > 0.75 then
                log(string.format("  %s: LIVE ENTITY at %.2f, %.2f, %.2f", r.name, v.x, v.y, v.z))
            elseif v.w > 0.25 then
                log("  " .. r.name .. ": name resolves, NO entity behind it (not streamed, or never instantiated)")
            else
                log("  " .. r.name .. ": name does not resolve")
            end
        end
        local ok, lines = pcall(function() return CCLab_MappinReport(Game.GetPlayer()) end)
        if ok and lines ~= nil then
            for _, l in ipairs(lines) do log("  " .. tostring(l)) end
        else
            log("  mappin report failed: " .. tostring(lines))
        end
    end
    if ImGui.Button("TWEAK FLATS: Wakako's gig rewards -> log") then
        for _, g in ipairs({ "sts_wbr_jpn_01", "sts_wbr_jpn_02", "sts_wbr_jpn_03", "sts_wbr_jpn_05", "sts_wbr_jpn_09", "sts_wbr_jpn_12", "sts_wbr_hil_01", "sts_wbr_hil_06", "sts_wbr_hil_07" }) do
            for _, suffix in ipairs({ "_completion", "_completion_pacifist" }) do
                local base = "QuestRewards." .. g .. suffix
                local parts = {}
                for _, f in ipairs({ "_inline1.value", "_inline3.value", "_inline5.value", "_inline5.modifierType", "_inline4.currency" }) do
                    local ok, v = pcall(function() return TweakDB:GetFlat(base .. f) end)
                    parts[#parts + 1] = f .. "=" .. (ok and tostring(v) or "?")
                end
                log(string.format("  %-46s %s", base, table.concat(parts, "  ")))
            end
        end
    end
    if ImGui.Button("AP: where is it now -> log") then local d = findAP(); if d then local p = d:GetWorldPosition(); log(string.format("ap at %.3f, %.3f, %.3f yaw %.1f", p.x, p.y, p.z, d:GetWorldYaw())) else log("ap: not found") end end
    ImGui.TextDisabled("Stand next to the router, PROBE first, then try one switch at a time and look for 'Jack in'.")
    -- TOJI'S FACE (design review 2026-09-05): the four top-tier Tyger Claw
    -- looks, one body each where the crosshair lands, so the one that fits
    -- Char's description (or that the description is rewritten to) is chosen
    -- by eye. Same lab tag as the boxes, so DESPAWN clears them.
    -- CHAR'S LOOK IN DAYLIGHT (playtest 2026-09-05, several reports that she
    -- changes between the chair and the phone). The chair body and the phone
    -- body both resolve to slacker_wa_slacker_wa_03, which the game's own
    -- appearance file defines as one fixed set of meshes (dark skin, dishwater
    -- blonde bun, aquamarine knit, neck strap, high-boot pants): the teal chair
    -- room and the warm studio light the same woman differently. This stands
    -- her under the crosshair, so she can be seen in neutral light.
    ImGui.TextDisabled("Toji's look and Char's, one body per button, on the surface under the crosshair:")
    for _, spec in ipairs({
        { rec = "Character.cc_g02_toji", look = "gang__tyger_ma_gangster__lvl3_01" },
        { rec = "Character.cc_g02_toji", look = "gang__tyger_ma_gangster__lvl3_02" },
        { rec = "Character.cc_g02_toji", look = "gang__tyger_ma_gangster__lvl3_03" },
        { rec = "Character.cc_g02_toji", look = "gang__tyger_ma_gangster__lvl3_04" },
        { rec = "Character.cc_g02_char", look = "slacker_wa_slacker_wa_03" },
    }) do
        local look, rec = spec.look, spec.rec
        if ImGui.Button("SPAWN LOOK: " .. look) then
            local ok, err = pcall(function()
                local player = Game.GetPlayer()
                local hit = CCLab_RayHit(player)
                if hit == nil or hit.w < 0.5 then log("toji: no surface under the crosshair") return end
                local yaw = player:GetWorldYaw() + 180.0
                local spec = DynamicEntitySpec.new()
                spec.recordID = TweakDBID.new(rec)
                spec.appearanceName = look
                spec.position = Vector4.new(hit.x, hit.y, hit.z, 1.0)
                spec.orientation = EulerAngles.ToQuat(EulerAngles.new(0, 0, yaw))
                spec.persistState = false
                spec.persistSpawn = false
                spec.alwaysSpawned = true
                spec.spawnInView = true
                spec.active = true
                spec.tags = { "cc_g02_lab" }
                Game.GetDynamicEntitySystem():CreateEntity(spec)
                log("toji look spawned: " .. look)
            end)
            if not ok then log("toji spawn failed: " .. tostring(err)) end
        end
    end
    if ImGui.Button("DESPAWN THE LAB'S BOXES (and any lab body)") then
        local ok, err = pcall(function()
            local ids = Game.GetDynamicEntitySystem():GetTaggedIDs("cc_g02_lab")
            for _, id in ipairs(ids) do Game.GetDynamicEntitySystem():DeleteEntity(id) end
            log(string.format("despawned %d lab entities", #ids))
        end)
        if not ok then log("despawn failed: " .. tostring(err)) end
    end
    ImGui.TextDisabled("Stand with your back to the wall, facing into the room, and press one. If a")
    ImGui.TextDisabled("box appears and one look is right, CAPTURE WHERE I STAND and say which look.")
    ImGui.Spacing()
    if ImGui.Button("DUMP (health, attitude, awareness) -> looked_at.txt") then
        dumpLookedAt(captureName)
    end
    ImGui.TextDisabled("A SEPARATE BUTTON from the two above, and it writes its own")
    ImGui.TextDisabled("file: looked_at.txt, next to captured_positions.txt.")
    ImGui.TextDisabled("Point at the merc: health should fall when shot and stop")
    ImGui.TextDisabled("short of zero. Point at a Claw: highLevelState Combat is")
    ImGui.TextDisabled("what the gig reads as 'spotted'.")

    ImGui.Spacing()
    if ImGui.CollapsingHeader("Gig status: which beat it is on, what it waits for, and which bodies are in the world") then
    -- ------------------------------------------------------------- WHERE
    if qs == nil then
        ImGui.Text("no quest system yet")
    else
        local parkedAt = nil
        local reached = 0
        for _, step in ipairs(STEPS) do
            if qs:GetFactStr(step.fact) > 0 then
                reached = reached + 1
            elseif parkedAt == nil then
                parkedAt = step
            end
        end
        ImGui.Text(string.format("%d of %d beats done", reached, #STEPS))
        if parkedAt == nil then
            ImGui.Text("the gig is finished")
        else
            ImGui.Text(string.format("waiting on: %s", parkedAt.fact))
            ImGui.Text(string.format("set by:     %s", parkedAt.who))
            ImGui.TextDisabled(parkedAt.what)
        end
    end

    -- ------------------------------------------------------- SPAWNED BODIES
    --
    -- IS HE THERE, AND WHERE. The merc and Toji are placed by a navmesh query
    -- at runtime, so neither has a fixed position the DISTANCES panel could
    -- list. "I cannot find him" and "he was never placed" look identical from
    -- inside the game and want completely different fixes.
    --
    -- The tag is what finds them: both are spawned through
    -- `CCSharedWorld.Spawn`, which tags every body it creates.
    ImGui.Spacing()
    if player == nil or qs == nil then
        ImGui.Text("no player yet")
    else
        local p = player:GetWorldPosition()
        for _, row in ipairs({
            { tag = "cc_g02_merc", label = "merc",  placed = "cc_g02_merc_placed" },
            { tag = "cc_g02_char", label = "Char",  placed = "cc_g02_char_placed" },
            { tag = "cc_g02_toji", label = "Toji",  placed = "cc_g02_toji_placed" },
            { tag = "cc_g02_claw", label = "Claws", placed = "cc_g02_hit_armed" },
        }) do
            local shown = false
            local ok = pcall(function()
                local des = Game.GetDynamicEntitySystem()
                local ids = des:GetTaggedIDs(row.tag)
                local n = 0
                local nearest = -1.0
                for _, id in ipairs(ids) do
                    local e = des:GetEntity(id)
                    if e ~= nil then
                        n = n + 1
                        local q = e:GetWorldPosition()
                        local d = math.sqrt((p.x - q.x) ^ 2 + (p.y - q.y) ^ 2
                                            + (p.z - q.z) ^ 2)
                        if nearest < 0 or d < nearest then nearest = d end
                    end
                end
                if n > 0 then
                    ImGui.Text(string.format("  %-6s %d in world, nearest %.0f m",
                        row.label, n, nearest))
                else
                    ImGui.Text(string.format("  %-6s none in world  (placed fact = %d)",
                        row.label, qs:GetFactStr(row.placed)))
                end
                shown = true
            end)
            if not (ok and shown) then
                -- The lookup is the one API here nobody has confirmed from
                -- Lua. A row that says this is the probe failing, not the body
                -- being absent: fall back to the placed fact, which the script
                -- writes and which is always readable.
                ImGui.Text(string.format("  %-6s <cannot query>  placed fact = %d",
                    row.label, qs:GetFactStr(row.placed)))
            end
        end
        ImGui.TextDisabled("A marker sits over the merc's head from the moment the")
        ImGui.TextDisabled("gig asks for him, and over Toji's once the approach ends.")
        ImGui.TextDisabled("Walk up to the merc: shooting him does nothing until he")
        ImGui.TextDisabled("has spoken, because he is friendly and invulnerable.")
    end
    end

    -- --------------------------------------------------------- DISTANCES
    --
    -- THE PANEL THIS MENU EXISTS FOR. Every spot the gig measures against, and
    -- whether the script's own test would pass right now. A trigger that will
    -- not fire is either out of range, which this says, or gated on a fact that
    -- has not been set, which this also says.
    ImGui.Spacing()
    if ImGui.CollapsingHeader("Distances: every trigger the gig measures, and whether it would fire now") then
        if player == nil or qs == nil then
            ImGui.Text("no player yet")
        else
            local p = player:GetWorldPosition()
            -- WHERE I AM STANDING, AND WHETHER A FIGHT COULD HAPPEN HERE.
            -- Walk the three groups with this open: any spot that says IN A
            -- SAFE AREA is a spot the merc cannot be beaten in.
            local here = inSafeArea(p)
            if here == nil then
                ImGui.TextDisabled("safe area: cannot ask from Lua here")
            elseif here then
                ImGui.Text("STANDING IN A SAFE AREA: no weapons, no fight")
            else
                ImGui.TextDisabled("not in a safe area: a fight can happen here")
            end
            ImGui.Spacing()
            ImGui.TextDisabled("spot                       dist  needs  safe  gate")
            for _, s in ipairs(SPOTS) do
                local dx, dy, dz = p.x - s.x, p.y - s.y, p.z - s.z
                local d = math.sqrt(dx * dx + dy * dy + dz * dz)
                local gateOpen = qs:GetFactStr(s.gate) > 0
                local alreadySet = qs:GetFactStr(s.sets) > 0
                local mark = "  "
                if alreadySet then
                    mark = "ok"
                elseif not gateOpen then
                    mark = ".."      -- not this beat's turn yet
                elseif d <= s.radius then
                    mark = ">>"      -- in range and armed: it should fire
                end
                local safe = inSafeArea({ x = s.x, y = s.y, z = s.z })
                local safeMark = "?"
                if safe == true then
                    safeMark = "SAFE"
                elseif safe == false then
                    safeMark = "-"
                end
                ImGui.Text(string.format("%s %-24s %5.0f  %4.0f  %-4s  %s",
                    mark, s.name, d, s.radius, safeMark,
                    alreadySet and "done" or (gateOpen and "ARMED" or s.gate)))
            end
            ImGui.TextDisabled("SAFE in that column means no weapon can be drawn there")
            ImGui.TextDisabled(">> in range and armed, so it should fire within a second")
            ImGui.TextDisabled(".. waiting on the gate fact named in the last column")
            ImGui.TextDisabled("Distance here is plain 3D; the script's own test is")
            ImGui.TextDisabled("tighter below than above, so suspect height first if")
            ImGui.TextDisabled("a row says >> and nothing happens.")
        end
    end

    ImGui.Spacing()
    if ImGui.CollapsingHeader("Gig controls: start it, answer the message") then
    -- ------------------------------------------------------------ ACTIONS
    ImGui.Spacing()
    if ImGui.Button("START THE GIG (bypasses the in-game gate)") then
        if qs then
            qs:SetFactStr("cc_g02_start", 1)
            log("cc_g02_start=1: the message should arrive with its own 3 s delay")
        end
    end
    if ImGui.Button("ANSWER THE MESSAGE (force the reply, places the call)") then
        forceReply()
    end

    ImGui.TextDisabled("The reply is a journal entry rather than a fact, so it is the")
    ImGui.TextDisabled("one gate the facts panel cannot reach.")
    end

    -- ------------------------------------------------------------- JUMPS
    ImGui.Spacing()
    if ImGui.CollapsingHeader("Jump forward to a beat (the scenes in between still play)") then
        ImGui.TextDisabled("Sets the player-side gates up to a beat. It cannot skip a")
        ImGui.TextDisabled("scene and it cannot be undone: reload to go back.")
        for _, j in ipairs(JUMPS) do
            if ImGui.Button(j.label .. "##jump") then
                jumpTo(j.upto)
            end
        end
    end

    -- --------------------------------------------------------- TELEPORTS
    ImGui.Spacing()
    if ImGui.CollapsingHeader("Teleports: every place the gig uses, plus the lab") then
        for i, p in ipairs(presets) do
            if p.pos then
                if ImGui.Button("GO##" .. i) then teleportTo(p.pos) end
                ImGui.SameLine()
            end
            ImGui.Text(p.name)
            ImGui.SameLine(340)
            if ImGui.SmallButton("set here##" .. i) then
                local pl = Game.GetPlayer()
                if pl then
                    local w = pl:GetWorldPosition()
                    p.pos = { x = w.x, y = w.y, z = w.z, w = 1.0 }
                    savePresets()
                    log("preset '" .. p.name .. "' moved to where you are standing")
                end
            end
        end
    end

    -- ----------------------------------------------------------- JOURNAL
    ImGui.Spacing()
    if ImGui.CollapsingHeader("Journal: message thread, quest, objectives, map pins, and the brief probe") then
        if ImGui.Button("Dump everything to the log") then
            for _, item in ipairs(JOURNAL) do
                log(item[1] .. " -> " .. entryState(item[1], item[2]))
            end
            for _, o in ipairs(OBJECTIVES) do
                log(PHASE .. "/" .. o .. " -> "
                    .. entryState(PHASE .. "/" .. o, "gameJournalQuestObjective"))
                if PINS[o] then
                    log(PHASE .. "/" .. o .. "/" .. PINS[o] .. " -> "
                        .. entryState(PHASE .. "/" .. o .. "/" .. PINS[o],
                                      "gameJournalQuestMapPin"))
                end
            end
        end
        ImGui.Spacing()
        for _, item in ipairs(JOURNAL) do
            ImGui.Text(string.format("%-52s %s",
                item[1]:gsub("^contacts/", ""):gsub("^quests/street_stories/", ""),
                entryState(item[1], item[2])))
        end
        ImGui.Spacing()
        ImGui.TextDisabled("A pin is a journal entry in its own right and an inactive")
        ImGui.TextDisabled("one is invisible, so an Active objective with an Inactive")
        ImGui.TextDisabled("pin is a missing map marker.")
        for _, o in ipairs(OBJECTIVES) do
            local line = string.format("%-16s %s", o,
                entryState(PHASE .. "/" .. o, "gameJournalQuestObjective"))
            if PINS[o] then
                line = line .. string.format("   pin: %s",
                    entryState(PHASE .. "/" .. o .. "/" .. PINS[o],
                               "gameJournalQuestMapPin"))
            end
            ImGui.Text(line)
        end
        ImGui.Spacing()
        ImGui.TextDisabled("The brief: does the journal say it was read, is the phone open?")
    if ImGui.Button("PROBE THE BRIEF (visited? phone open?) -> log") then
            local jm = Game.GetJournalManager()
            local entry = nil
            pcall(function() entry = jm:GetEntryByString("contacts/cc_g02_wakako/cc_g02_wakako_conv/cc_g02_msg_04", "gameJournalPhoneMessage") end)
            pcall(function() entry = jm:GetEntryByString("contacts/cc_g02_wakako/cc_g02_wakako_conv/cc_g02_msg_09", "gameJournalPhoneMessage") end)
            local visited, contacts, phone = "?", "?", "?"
            pcall(function() visited = tostring(jm:IsEntryVisited(entry)) end)
            pcall(function()
                local defs = GetAllBlackboardDefs().UI_ComDevice
                local bb = Game.GetBlackboardSystem():Get(defs)
                contacts = tostring(bb:GetBool(defs.ContactsActive))
                phone = tostring(bb:GetBool(defs.PhoneEnabled))
            end)
            log(string.format("brief probe: entry=%s visited=%s ContactsActive=%s PhoneEnabled=%s brief_read=%s",
                tostring(entry ~= nil), visited, contacts, phone, qs and tostring(qs:GetFactStr("cc_g02_brief_read")) or "?"))
        end
    end

    -- -------------------------------------------------------------- FACTS
    ImGui.Spacing()
    if ImGui.CollapsingHeader("Quest facts: read every flag, force it to 0 or 1") then
        if qs then
            -- FIND A FACT WITHOUT SCROLLING SEVENTY ROWS. The list is written
            -- in the order the gig sets them, which is the useful order when
            -- reading a playthrough and the wrong one when hunting a single
            -- name, so both are available and the gig order is still default.
            factFilter = ImGui.InputText("filter##facts", factFilter or "", 64)
            ImGui.SameLine()
            factsAZ = ImGui.Checkbox("A-Z", factsAZ or false)
            ImGui.SameLine()
            if ImGui.SmallButton("clear##factfilter") then factFilter = "" end

            local rows = {}
            local needle = (factFilter or ""):lower()
            for _, fact in ipairs(FACTS) do
                if needle == "" or fact:lower():find(needle, 1, true) then
                    rows[#rows + 1] = fact
                end
            end
            if factsAZ then table.sort(rows) end
            if #rows == 0 then
                ImGui.TextDisabled("no fact matches '" .. tostring(factFilter) .. "'")
            end

            for _, fact in ipairs(rows) do
                local value = qs:GetFactStr(fact)
                ImGui.Text(string.format("%-38s = %d", fact, value))
                ImGui.SameLine(360)
                if ImGui.SmallButton("0##" .. fact) then qs:SetFactStr(fact, 0) end
                ImGui.SameLine()
                if ImGui.SmallButton("1##" .. fact) then qs:SetFactStr(fact, 1) end
            end
        end
    end

    ImGui.Spacing()
    -- =====================================================================
    -- THE APPEARANCE A/B (backlog 42)
    -- =====================================================================
    --
    -- THE QUESTION: Char in the netrunner chair and Char on the holocall are
    -- reported as dressed differently. Every field that could name her look
    -- says `slacker_wa_slacker_wa_03`, the entity resolves that name, and it
    -- maps to a leaf with 18 fixed parts. So either the two spawn routes do
    -- not both get it, or the difference was only ever the light.
    --
    -- PURE LUA ON PURPOSE. Everything in this panel works after CET's "Reload
    -- all mods" and needs no game restart: it reads a live body and spawns
    -- bodies through DynamicEntitySpec, and it touches no redscript, no quest
    -- phase and no archive. Iterate here first.
    --
    -- THE ONE THING THAT IS NOT HERE is putting a chosen look on the holocall
    -- body. The picture only renders when the call is issued from the quest
    -- graph (the graph's node carries the field that aims the phone at the
    -- studio), and a graph change costs a rebuild and a restart. Arm 15 does
    -- that half; this panel does the half that answers the same question
    -- without one.
    if ImGui.CollapsingHeader("Appearance A/B: is the chair body's look reproducible? (backlog 42)") then
    ImGui.TextDisabled("1. Stand in the netrunner room, put the crosshair on Char in the chair,")
    ImGui.TextDisabled("   and press COPY. A body with HER EXACT record and HER LIVE appearance")
    ImGui.TextDisabled("   appears where you stand, so both are in one light.")
    if ImGui.Button("COPY THE BODY I'M LOOKING AT -> where I stand") then
        local target, how = lookedAtObject()
        if target == nil then
            labLog("A/B copy: the crosshair is not on anything the game can identify.")
        else
            local rec, app = nil, nil
            pcall(function() rec = tostring(target:GetRecord():GetID()) end)
            pcall(function() app = tostring(target:GetCurrentAppearanceName()) end)
            if rec == nil or app == nil then
                labLog("A/B copy: target has no record or no appearance; refusing.")
            else
                abRecord, abAppearance = rec, app
                local ok, err = pcall(function()
                    local player = Game.GetPlayer()
                    local p = player:GetWorldPosition()
                    local spec = DynamicEntitySpec.new()
                    spec.recordID = TweakDBID.new(rec)
                    -- THE LIVE APPEARANCE, not the record's. This is the whole
                    -- point: whatever the body in the chair actually resolved
                    -- to is what gets asked for here.
                    spec.appearanceName = app
                    spec.position = Vector4.new(p.x, p.y, p.z, 1.0)
                    spec.orientation = EulerAngles.ToQuat(
                        EulerAngles.new(0, 0, player:GetWorldYaw() + 180.0))
                    spec.persistState = false
                    spec.persistSpawn = false
                    spec.alwaysSpawned = false
                    spec.spawnInView = true
                    spec.active = true
                    spec.tags = { CName.new("cc_g02_lab") }
                    return Game.GetDynamicEntitySystem():CreateEntity(spec)
                end)
                labLog(string.format(
                    "A/B copy (%s): record=%s appearance=%s spawned=%s",
                    how, rec, app, tostring(ok)))
                if not ok then labLog("  " .. tostring(err)) end
            end
        end
    end
    ImGui.TextDisabled("2. Press FALLBACK a few times. It spawns the SAME record with NO")
    ImGui.TextDisabled("   appearance asked for, which is what a body gets when nothing names")
    ImGui.TextDisabled("   one. This entity's default is the literal word `random`, so if the")
    ImGui.TextDisabled("   outfit changes press to press, that is the suspected holocall bug")
    ImGui.TextDisabled("   standing in front of you, no phone needed.")
    if ImGui.Button("FALLBACK: same record, NO appearance asked for") then
        local rec = abRecord or "Character.cc_g02_char"
        local ok, got = pcall(function()
            local player = Game.GetPlayer()
            local p = player:GetWorldPosition()
            local spec = DynamicEntitySpec.new()
            spec.recordID = TweakDBID.new(rec)
            -- appearanceName deliberately LEFT UNSET.
            spec.position = Vector4.new(p.x, p.y, p.z, 1.0)
            spec.orientation = EulerAngles.ToQuat(
                EulerAngles.new(0, 0, player:GetWorldYaw() + 180.0))
            spec.persistState = false
            spec.persistSpawn = false
            spec.alwaysSpawned = false
            spec.spawnInView = true
            spec.active = true
            spec.tags = { CName.new("cc_g02_lab") }
            return Game.GetDynamicEntitySystem():CreateEntity(spec)
        end)
        labLog("A/B fallback: record=" .. rec .. " no appearance; spawned=" .. tostring(ok))
    end
    ImGui.TextDisabled("3. READ tells you what each body in front of you actually resolved to.")
    if ImGui.Button("READ the appearance of the body I'm looking at") then
        local target, how = lookedAtObject()
        if target == nil then
            labLog("A/B read: nothing under the crosshair.")
        else
            local rec, app = "?", "?"
            pcall(function() rec = tostring(target:GetRecord():GetID()) end)
            pcall(function() app = tostring(target:GetCurrentAppearanceName()) end)
            labLog(string.format("A/B read (%s): record=%s appearance=%s", how, rec, app))
        end
    end
    ImGui.SameLine()
    if ImGui.Button("CLEAR the bodies this panel spawned") then
        local n = 0
        local ok, ids = pcall(function() return CCLab_Find(Game.GetGameInstance()) end)
        if ok and ids then
            for _, id in ipairs(ids) do
                pcall(function() CCLab_Despawn(id) end)
                n = n + 1
            end
        end
        labLog("A/B: despawned " .. n .. " lab body(ies)")
    end
    ImGui.TextDisabled("What was copied last:")
    ImGui.SameLine()
    ImGui.Text(tostring(abRecord or "-") .. "  /  " .. tostring(abAppearance or "-"))
    end

    ImGui.Spacing()
    if ImGui.CollapsingHeader("Pose lab: spawn a body outside the gig and try poses, knock-downs and effects") then
    -- --------------------------------------------------------- POSE LAB
    -- Spawn a body on the merc's post and try every way the engine has of
    -- putting it into a pose. Works on any save, gig or no gig. Every call
    -- goes through Gig02_Lab.reds, so the compiler has checked it; a button
    -- that does nothing is the engine refusing, and the log says so.
    ImGui.Spacing()
    if ImGui.Button("GO TO THE LAB") then teleportTo({ x = -1472.817, y = 1028.142, z = 22.690, w = 1.0 }) end
    ImGui.SameLine()
    if ImGui.Button("SPAWN merc body") then labSpawn("Character.cc_g02_merc") end
    ImGui.SameLine()
    if ImGui.Button("SPAWN civilian") then labSpawn("Character.cc_g02_queue_a") end
    ImGui.SameLine()
    if ImGui.Button("DESPAWN lab bodies") then labDespawn() end
    ImGui.TextDisabled("The body stands on the post facing the queue. Each row is one pose;")
    ImGui.TextDisabled("WALK = the AI walks in and plays the enter animation, PLACE = enter")
    ImGui.TextDisabled("animation where it stands, JUMP = straight to the idle (the snap).")
    for _, pose in ipairs(LAB_POSES) do
        ImGui.Text(string.format("%-14s", pose))
        ImGui.SameLine()
        if ImGui.Button("WALK##" .. pose) then labPose(pose, true, false, false) end
        ImGui.SameLine()
        if ImGui.Button("PLACE##" .. pose) then labPose(pose, false, false, false) end
        ImGui.SameLine()
        if ImGui.Button("JUMP##" .. pose) then labPose(pose, false, true, false) end
        ImGui.SameLine()
        if ImGui.Button("IDLE ONLY##" .. pose) then labPose(pose, false, false, true) end
    end
    if ImGui.Button("EXIT the workspot (exit animation)") then labEach(function(npc) CCLab_StopWorkspot(npc) end, "stop workspot") end
    ImGui.SameLine()
    if ImGui.Button("RESET body (stop, clear effects, relaxed)") then labEach(labResetOne, "reset") end
    ImGui.SameLine()
    labAutoReset = ImGui.Checkbox("auto-reset before each action", labAutoReset)
    ImGui.TextDisabled("Knock-downs, the game's own falls. Apply, watch, remove.")
    ImGui.TextDisabled("Second block: the ALIVE-AND-HURT effects. Wounded and the crippled legs are")
    ImGui.TextDisabled("what makes an enemy drop and crawl; try them alone and after Defeated.")
    for _, se in ipairs(LAB_STATUSES) do
        ImGui.Text(string.format("%-20s", se))
        ImGui.SameLine()
        if ImGui.Button("APPLY##" .. se) then labDo(function(npc) CCLab_Status(npc, "BaseStatusEffect." .. se, true) end, "apply " .. se) end
        ImGui.SameLine()
        if ImGui.Button("REMOVE##" .. se) then labEach(function(npc) CCLab_Status(npc, "BaseStatusEffect." .. se, false) end, "remove " .. se) end
    end
    ImGui.TextDisabled("Loot list of a downed body: put the shard in his pocket, take his gun out.")
    if ImGui.Button("GIVE the shard to the body") then labEach(function(npc)
        if not CCLab_GiveItem(npc, "Items.cc_g02_shard", 1) then error("GiveItem returned false") end
    end, "gave Items.cc_g02_shard") end
    ImGui.SameLine()
    if ImGui.Button("STRIP everything but our shard") then labEach(function(npc)
        labLog("lab: removed " .. tostring(CCLab_StripAll(npc, "Items.cc_g02_shard")) .. " item(s)")
    end, "strip all but ours") end
    ImGui.SameLine()
    if ImGui.Button("INSPECT item records -> log") then
        for _, rec in ipairs({ "Items.cc_g02_shard", "Items.Shard1", "Items.generic_hanako_flowers_shard",
                               "Items.q003_chip" }) do
            local ok, err = pcall(function()
                local r = TweakDB:GetRecord(rec)
                if r == nil then labLog("  " .. rec .. ": NO RECORD") return end
                local name, typ, qual, act = "?", "?", "?", "?"
                pcall(function() name = tostring(r:DisplayName()) .. " -> " .. tostring(Game.GetLocalizedTextByKey(r:DisplayName())) end)
                pcall(function() typ = tostring(r:ItemType():Type()) end)
                pcall(function() qual = tostring(r:Quality():Type()) end)
                pcall(function() act = tostring(r:ItemSecondaryAction():GetID()) end)
                labLog(string.format("  %-40s name=%s type=%s quality=%s secondary=%s", rec, name, typ, qual, act))
            end)
            if not ok then labLog("  " .. rec .. ": " .. tostring(err)) end
        end
    end
    ImGui.SameLine()
    if ImGui.Button("DO I HAVE the shard?") then
        local ok, has = pcall(function() return CCLab_HasItem(Game.GetPlayer(), "Items.cc_g02_shard") end)
        labLog("lab: player has shard = " .. tostring(ok and has))
    end
    ImGui.TextDisabled("The Inn on a save already past its switch (one shot each per save):")
    if ImGui.Button("INN BODIES ON: vendor off, our Yoko and Char on (arm 11)") then if qs then qs:SetFactStr("cc_g02_dev_crowd", 11); labLog("cc_g02_dev_crowd=11") end end
    ImGui.SameLine()
    if ImGui.Button("INN BODIES OFF (arm 12)") then if qs then qs:SetFactStr("cc_g02_dev_crowd", 12); labLog("cc_g02_dev_crowd=12") end end
    ImGui.TextDisabled("The parlor on a save already past its switch (one shot each per save):")
    if ImGui.Button("PARLOR BODIES ON: game's Wakako off, ours on (arm 13)") then if qs then qs:SetFactStr("cc_g02_dev_crowd", 13); labLog("cc_g02_dev_crowd=13") end end
    ImGui.SameLine()
    if ImGui.Button("PARLOR BODIES OFF (arm 14)") then if qs then qs:SetFactStr("cc_g02_dev_crowd", 14); labLog("cc_g02_dev_crowd=14") end end
    ImGui.TextDisabled("Quest-side switch on the lab body (one shot each per save): loot access.")
    if ImGui.Button("LOOT ACCESS OFF (arm 9)") then if qs then qs:SetFactStr("cc_g02_dev_crowd", 9); labLog("cc_g02_dev_crowd=9 loot access off") end end
    ImGui.SameLine()
    if ImGui.Button("LOOT ACCESS ON (arm 10)") then if qs then qs:SetFactStr("cc_g02_dev_crowd", 10); labLog("cc_g02_dev_crowd=10 loot access on") end end
    ImGui.SameLine()
    if ImGui.Button("READ PROBE -> log") then
        local jm = Game.GetJournalManager()
        local visited = "?"
        pcall(function()
            local e = jm:GetEntryByString("onscreens/emails/quests/street_stories/cc_g02_dead_ringer/onscreens/cc_g02_shard_note", "gameJournalOnscreen")
            visited = tostring(e ~= nil and jm:IsEntryVisited(e))
        end)
        labLog(string.format("read probe: our entry visited=%s shard_open=%s proof_read=%s", visited,
            qs and tostring(qs:GetFactStr("cc_g02_shard_open")) or "?", qs and tostring(qs:GetFactStr("cc_g02_proof_read")) or "?"))
    end
    if ImGui.Button("RELAXED state") then labEach(function(npc) CCLab_Relax(npc, true) end, "relaxed") end
    ImGui.SameLine()
    if ImGui.Button("COMBAT state") then labEach(function(npc) CCLab_Relax(npc, false) end, "combat") end
    ImGui.SameLine()
    -- Two-step combos: the fall from one effect, the floor state from another.
    -- These do NOT reset in between, so the second lands on the fallen body.
    local combos = {
        { "Defeated -> Wounded (2 s)",        "Defeated", "Wounded" },
        { "Defeated -> CrippledLeg (2 s)",    "Defeated", "CrippledLeg" },
        { "Defeated -> Bleeding (2 s)",       "Defeated", "BleedingInfinite" },
        { "Defeated -> KnockdownInf (2 s)",   "Defeated", "KnockdownInfinite" },
        { "CrippledLeg -> Wounded (2 s)",     "CrippledLeg", "Wounded" },
        { "Knockdown -> Wounded (1 s)",       "Knockdown", "Wounded" },
    }
    for _, c in ipairs(combos) do
        if ImGui.Button(c[1] .. "##combo") then
            labDo(function(npc) CCLab_Status(npc, "BaseStatusEffect." .. c[2], true) end, "apply " .. c[2])
            local second = c[3]
            local wait = (c[2] == "Knockdown") and 1.0 or 2.0
            local first = labPending
            labPending = { t = 0.8, fn = function()
                if first then first.fn() end
                labPending = { t = wait, fn = function()
                    labEach(function(npc) CCLab_Status(npc, "BaseStatusEffect." .. second, true) end, "then apply " .. second)
                end }
            end }
        end
        if _ % 2 == 1 then ImGui.SameLine() end
    end
    ImGui.NewLine()
    if ImGui.Button("COMBAT then Defeated in 2 s (the gig's own order)") then
        labEach(function(npc) CCLab_Relax(npc, false) end, "combat")
        labPending = { t = 2.0, fn = function() labEach(function(npc) CCLab_Status(npc, "BaseStatusEffect.Defeated", true) end, "apply Defeated") end }
    end
    ImGui.TextDisabled("Note which button gives a fluid move and which pose reads as wounded;")
    ImGui.TextDisabled("that pair is what the gig will use.")
    end

    ImGui.Spacing()
    if ImGui.CollapsingHeader("Door crowd: list, dispose or calm the bodies at Afterlife, and the community-switch harness") then
    -- ------------------------------------------------------- DOOR CROWD
    -- The game's own queue outside Afterlife, and every way of removing it,
    -- testable on a PRE-GIG save standing at the door. The quest-side arms
    -- (1-8) are one-shot per save; the Lua ones act at once and repeat.
    ImGui.Spacing()
    if ImGui.Button("LIST NPCS WITHIN 25 M -> log") then listNearby(25.0) end
    ImGui.SameLine()
    if ImGui.Button("DISPOSE non-ours 25 m") then disposeNearby(25.0) end
    ImGui.SameLine()
    if ImGui.Button("CALM non-ours 25 m") then calmNearby(25.0) end
    ImGui.TextDisabled("Quest-side switches, one shot each per save. Watch the door")
    ImGui.TextDisabled("for ~10 s after each; walk 60 m away and back if nothing moves.")
    local arms = {
        {1, "Deactivate 3 entries, LONG ref"}, {2, "Deactivate 3 entries, SHORT ref"},
        {3, "Deactivate whole, LONG"},          {4, "Deactivate whole, SHORT"},
        {5, "Null area ON"},                    {6, "Null area OFF"},
        {7, "Reactivate 3 entries, LONG"},      {8, "Reactivate 3 entries, SHORT"},
    }
    for _, a in ipairs(arms) do
        if ImGui.Button(string.format("%d: %s##dev", a[1], a[2])) then
            if qs then qs:SetFactStr("cc_g02_dev_crowd", a[1]); log("cc_g02_dev_crowd=" .. a[1] .. " (" .. a[2] .. ")") end
        end
        if a[1] % 2 == 1 then ImGui.SameLine() end
    end
    end

    ImGui.End()
end)
