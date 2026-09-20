-- Acceptable Loss [DEV]: the gig's own CET menu.
--
-- Small on purpose. Gig 01's and gig 02's menus grew to two thousand lines each
-- because they accumulated a probe per investigation; this one starts as the
-- three things a gig needs on day one and grows only when a question actually
-- costs a session.
--
--   * every fact, readable and settable
--   * the objective chain walked one step at a time
--   * teleports to both places, and to each side of the compound wall
--
-- CET Lua reloads in place, so "Reload all mods" is enough for a change to this
-- file. Everything else in this gig, redscript and archive both, is read at
-- launch and needs a full restart.

local visible = false
local status = "ready"

local function qs()
    return Game.GetQuestsSystem()
end

local function get(f)
    local v = 0
    pcall(function() v = qs():GetFactStr(f) end)
    return v
end

local function set(f, v)
    pcall(function() qs():SetFactStr(f, v) end)
    status = string.format("%s = %d", f, v)
    print("[G03] " .. status)
end

-- THE FACTS, in the order the gig sets them. The comment on each says WHO sets
-- it in a real playthrough, because a fact with two writers is a fact nobody
-- owns. The same table is in tools/gig03/gen_questphase.py and the two must
-- agree.
local FACTS = {
    { "cc_g03_start",          "the start trigger, once Dino is a contact" },
    { "cc_g03_called",         "the phone, when V taps the reply that calls him" },
    { "cc_g03_arrived",        "at the Badlands site" },
    { "cc_g03_inside",         "across the perimeter" },
    { "cc_g03_terminal",       "at the terminal. Set by walking up to it" },
    { "cc_g03_data",           "the third file has been opened. Set by reading it" },
    { "cc_g03_alarm",          "the security-room door opened. Starts the trace bar, nothing else" },
    { "cc_g03_shard_got",      "the shard taken OR read. Opens 'get out'" },
    { "cc_g03_shard_read",     "the reader was opened and shut" },
    { "cc_g03_traced",         "the bar finished: V is found. Stars, guards and reinforcements follow this" },
    { "cc_g03_escaped",        "clear of the compound. Opens 'leave the Badlands'" },
    { "cc_g03_badlands_left",  "the game says V is out of the Badlands. Drops the stars" },
    { "cc_g03_mounted",        "with badlands_left: 1 = V was driving (objective shown), 2 = on foot" },
    { "cc_g03_on_foot",        "out of a vehicle with no stars. Johnny waits on this" },
    { "cc_g03_loyal",          "SET BY THE GRAPH: V chose to wipe the shard (ending B)" },
    { "cc_g03_unlock_dino",    "SET BY THE GRAPH, with the trip to him" },
    { "cc_g03_at_bar",         "within 35 m of his stool. This is what swaps the bodies" },
    { "cc_g03_swapped",        "SET BY THE GRAPH once the game's Dino is off and ours on. The keeper waits on it" },
    { "cc_g03_delivered",      "at Dino. Starts his scene" },
    { "cc_g03_pay_due",        "SET BY THE GRAPH as his calm scene ends. Pays the fee" },
    { "cc_g03_docked",         "SET BY THE GRAPH as his loud scene ends. Takes the advance" },
    { "cc_g03_left_dino",      "35 m from the bar again, on foot. Holds V still; Johnny and the ending wait on this" },
    { "cc_g03_johnny_done",    "SET BY THE GRAPH as Johnny's door scene ends. Releases the hold" },
    { "cc_g03_done",           "SET BY THE GRAPH, at the end" },
}

-- READ THESE, do not set them.
local PROBES = {
    { "cc_g03_dino_notified",  "1 = the blocked message has been shown once" },
    { "cc_g03_paid",           "1 = the fee has been transferred, once per save" },
    { "cc_g03_files_installed","1 = the terminal's folder has been written once" },
    { "cc_g03_heat_raised",    "1 = the trace has already raised the stars, once per save" },
    { "cc_g03_dbg_located",    "how many times V's position was handed to the responders (every 3 s of the chase)" },
    { "cc_g03_dbg_cars",       "how many Militech chase cars the gig asked the game to send (keeps 3 in play)" },
    { "cc_g03_dbg_followed",   "how many response cars were told to drive at V off-road on the last pass" },
    { "cc_g03_dbg_dino_seen",  "how many bodies the game's own Dino community reported on the last look" },
    { "cc_g03_dbg_dino_disposed", "how many game-Dino bodies were removed at the bar (0 = none found)" },
    { "cc_g03_dbg_dino_route", "which route last found him: 1 the community's bodies, 2 its fixed ids, 3 the census" },
    { "dyno_default_on",       "THE GAME'S OWN switch for Dino's bar: 1 normally, held at 0 by the graph while ours sits there" },
    { "cc_g03_dbg_hold",       "1 = V is being held still for Johnny, 2 = the hold was lifted" },
    { "cc_g03_dbg_heat",       "1 = the raise was asked for, 2 = it was refused or already high" },
    { "cc_g03_dbg_alarm_src",  "what raised the alarm: 1 the door, 2 the cabinet, 3 the shard itself" },
    { "cc_g03_dbg_guards_seen","Militech standing inside the wire on the last alarm pass" },
    { "cc_g03_dbg_guards_turned", "how many of them have been turned on V at least once" },
    { "cc_g03_dbg_reraised",   "how many times the stars were brought back in the Badlands" },
    { "cc_g03_heat_cleared",   "1 = the stars were dropped at the Badlands line, once per save" },
    { "cc_g03_dbg_heat_drop",  "1 = the drop was asked for, 2 = nothing to drop" },
    { "cc_g03_choice_claim",   "the decision race: 1 bring it, 2 wipe it" },
    { "cc_g03_shard_destroyed","1 = the shard was removed, once per save" },
    { "cc_g03_dbg_destroyed",  "1 = it was in the backpack, 2 = it was not (left on the cabinet)" },
    { "cc_g03_dock_paid",      "1 = the advance has been taken, once per save" },
    { "cc_g03_dbg_docked",     "how many eddies the advance took" },
    { "cc_g03_ended",          "1 = an ending has played" },
}

-- HOLD THE TRIGGER while testing anything that is not the start itself.
local HOLD = "cc_g03_dev_hold"

-- INSIDE THE WIRE, and both of these are positions somebody stood on.
local TELEPORTS = {
    -- THE TERMINAL THE GIG USES, in the north-west corner. NOT the one in the
    -- office, which belongs to the base game's own street story here.
    { "The compound, at the terminal", -132.000, -5194.600, 88.500 },
    { "The office (the quest computer, off limits)", -101.800, -5215.284, 87.151 },
    { "The compound, north wall",       -94.603, -5182.958, 87.070 },
    -- THE GATE, where the three reinforcements arrive. Captured 2026-09-15.
    { "The compound, the gate",        -133.181, -5200.584, 87.139 },
    -- DINO'S BAR, in Downtown. The spot the base game itself teleports V to
    -- beside him (`#mq033_dino_teleport`, always_loaded_1), 5 m south of his
    -- stool; nobody has stood on it in play yet. His stool is at
    -- -1969.884, 377.748, 8.046 (gig03_config.DINO_POS).
    { "Dino's bar, beside him",       -1969.496,   372.634,  8.041 },
    -- THE SHARD, on the cabinet in the security room. Its height is the one
    -- thing about it that was computed rather than walked, and it has been
    -- lowered once already. tools/gig03/gen_sector.py holds the number.
    { "The shard on the cabinet",      -95.621, -5211.431, 87.135 },
    -- THE SECURITY-ROOM DOOR, captured 2026-09-11. Opening it is the alarm.
    { "The security-room door",        -92.705, -5212.610, 87.155 },
}

-- JUST OUTSIDE THE WIRE, one per side, 15 m beyond the middle of the longest
-- edge on that side. Every one is confirmed outside the walked perimeter by a
-- point-in-polygon test rather than by eye.
--
-- THE HEIGHT IS A GUESS AND THESE FOUR ARE THE ONLY POSITIONS IN THIS MENU THAT
-- ARE. The x and y are computed from corners that were walked, so they are as
-- good as the walk. The z is the compound's own ground, 87, plus 3 m, because
-- nothing here knows what the terrain does outside the wall and the Badlands
-- around this site is rock. Landing 3 m up and dropping is harmless; landing
-- inside a hillside is not, so the error is deliberately on the high side.
--
-- If one of them lands badly, stand where you want it and capture the spot with
-- cc_capture, which beats computing a better guess.
local OUTSIDE = {
    { "Outside, east",   -45.967, -5214.787, 90.0 },
    { "Outside, south",  -92.561, -5262.824, 90.0 },
    { "Outside, west",  -141.835, -5234.228, 90.0 },
    { "Outside, north", -126.661, -5172.230, 90.0 },
}

-- THE THREE OTHER COMPUTERS IN THE COMPOUND, read out of the sector index on
-- 2026-09-09, all named `ina_05_booth_computer`. None of them is the street
-- story's quest device, which is the one V captured.
--
-- THEY HAVE NOT BEEN SEEN IN GAME. A node named "booth computer" may be a
-- working terminal or it may be a screen prop with no interaction on it, and the
-- sector data does not say which. Stand on one and use cc_doors' LOOK button:
-- a real one answers with a ComputerControllerPS the way the captured terminal
-- did, a prop answers with nothing.
local COMPUTERS = {
    { "Booth computer 1 (16 m S)",  -102.2, -5232.3, 88.0 },
    { "Booth computer 2 (30 m SW)", -121.8, -5238.1, 92.3 },
    { "Booth computer 3 (39 m NW)", -133.2, -5193.8, 89.5 },
}

-- THE WALKED PERIMETER, in order, so the census below can say whether a body is
-- inside the wire or merely nearby. Same ten corners as tools/gig03/gig03_config.py.
local POLY = {
    { -94.603, -5182.958 }, { -93.260, -5191.834 }, { -63.751, -5188.975 },
    { -58.180, -5240.128 }, { -62.299, -5241.255 }, { -62.074, -5245.433 },
    { -125.795, -5250.342 }, { -130.538, -5205.756 }, { -138.655, -5207.188 },
    { -141.365, -5185.973 },
}

local function insidePoly(px, py)
    local n = #POLY
    local c = false
    local j = n
    for i = 1, n do
        local xi, yi = POLY[i][1], POLY[i][2]
        local xj, yj = POLY[j][1], POLY[j][2]
        if ((yi > py) ~= (yj > py))
           and (px < (xj - xi) * (py - yi) / (yj - yi) + xi) then
            c = not c
        end
        j = i
    end
    return c
end

-- COUNT WHO IS ACTUALLY STANDING HERE.
--
-- The base game populates this compound itself: the sector index lists guard
-- workspots, guard patrol splines, workers and refugees, all belonging to the
-- street story set at this site. So the question "do we need to spawn anyone"
-- is a measurement, not a design decision, and it has to be taken on a real
-- save because whether those bodies are present may depend on that street
-- story's own state.
--
-- Run it standing inside the compound. It reports every NPC the targeting
-- system can see, splits them by whether they are inside the walked perimeter,
-- and says which are alive and which are hostile to V.
local function census()
    local out = {}
    local function line(s)
        out[#out + 1] = s
        print("[G03] " .. s)
    end

    local player = Game.GetPlayer()
    if not player then
        status = "no player"
        return
    end

    -- WHY THE FIRST VERSION OF THIS COUNTED NOTHING.
    --
    -- `TSQ_NPC()` on its own is a CROSSHAIR query. Its default tested set is
    -- what the targeting system currently considers targetable from where the
    -- player is aiming, so it answers "who am I looking at", not "who is here".
    -- Standing in a doorway with the crosshair on a wall it returns zero while
    -- the room is full of guards, which is exactly what happened: one run on
    -- the road returned the one sniper in view, and every run indoors returned
    -- nothing.
    --
    -- `testedSet = TargetingSet.Complete` is what turns it into a real sphere
    -- search. Both queries are run below and both counts are reported, because
    -- the difference between them is the measurement.
    local function runQuery(complete)
        local parts = nil
        pcall(function()
            local q = Game["TSQ_ALL;"]()
            if complete then
                q.testedSet = TargetingSet.Complete
            end
            q.maxDistance = 250.0
            q.includeSecondaryTargets = false
            q.ignoreInstigator = true
            local found
            found, parts = Game.GetTargetingSystem():GetTargetParts(player, q)
        end)
        return parts
    end

    local parts = runQuery(true)
    local how = "TSQ_ALL, complete set"
    if parts == nil or #parts == 0 then
        local fallback = runQuery(false)
        if fallback ~= nil and #fallback > 0 then
            parts = fallback
            how = "TSQ_ALL, default set (the complete set returned nothing)"
        end
    end
    if parts == nil then
        pcall(function()
            local q = TSQ_NPC()
            q.maxDistance = 250.0
            local found
            found, parts = Game.GetTargetingSystem():GetTargetParts(player, q)
        end)
        how = "TSQ_NPC, crosshair only"
    end

    if parts == nil then
        status = "every targeting query failed"
        line("no query answered. Nothing counted.")
        return
    end
    line("query: " .. how)

    local inside, outside, alive, hostile, people = 0, 0, 0, 0, 0
    local names = {}
    local seen = {}

    for _, part in ipairs(parts) do
        local ent = nil
        pcall(function() ent = part:GetComponent():GetEntity() end)
        if ent ~= nil then
            local id = nil
            pcall(function() id = tostring(ent:GetEntityID().hash) end)
            if id ~= nil and not seen[id] then
                seen[id] = true
                local p = ent:GetWorldPosition()
                local isIn = insidePoly(p.x, p.y)
                if isIn then inside = inside + 1 else outside = outside + 1 end

                local isAlive = false
                pcall(function() isAlive = ent:IsAlive() end)
                if isAlive then alive = alive + 1 end

                -- TSQ_ALL RETURNS VEHICLES TOO, and the first run counted
                -- five of them among "17 inside the wire", which makes the
                -- number useless for deciding whether to spawn anybody. A
                -- puppet answers IsNPC; a parked Chevalier does not.
                local isPuppet = false
                pcall(function() isPuppet = ent:IsNPC() end)
                if isPuppet and isIn then people = people + 1 end

                local isHostile = false
                pcall(function()
                    isHostile = ent:IsHostile() or ent:IsHostileToPlayer()
                end)
                if isHostile then hostile = hostile + 1 end

                if isIn then
                    local nm = "?"
                    pcall(function() nm = tostring(ent:GetRecordID()) end)
                    names[nm] = (names[nm] or 0) + 1
                end
            end
        end
    end

    line("---------------- guard census ----------------")
    line(string.format("NPCs seen        %d", inside + outside))
    line(string.format("inside the wire  %d  (of which people: %d)", inside, people))
    line(string.format("outside          %d", outside))
    line(string.format("alive            %d", alive))
    line(string.format("hostile to V     %d", hostile))
    line("records inside the wire:")
    for nm, n in pairs(names) do
        line(string.format("   %3d  %s", n, nm))
    end
    line("NOTE: this counts what is STREAMED IN right now. Stand in the middle")
    line("of the compound and run it again if the numbers look low.")

    local f = io.open("census.txt", "a")
    if f then
        for _, l in ipairs(out) do f:write(l .. "\n") end
        f:close()
    end
    status = string.format("census: %d inside the wire, %d hostile", inside, hostile)
end

-- HOW DO YOU RAISE THE PLAYER'S WANTED LEVEL?
--
-- The design wants three stars the moment the trace lands, because in the
-- Badlands a wanted player brings Militech, which is exactly who V has just
-- stolen from. The beat is right; the call is not written down anywhere this
-- project has read, and a guessed one fails silently.
--
-- So this asks the game. It finds the prevention system, then tries each
-- candidate route under pcall and reports which of them the game accepted.
-- Nothing here is shipped: once one route answers, that one goes into redscript
-- and this stays as the record of how it was found.
--
-- Watch the star meter, not this readout. "Accepted" only means the call did
-- not throw.
local function preventionSystem()
    local sys = nil
    pcall(function()
        sys = Game.GetScriptableSystemsContainer():Get(CName.new("PreventionSystem"))
    end)
    if sys == nil then
        pcall(function() sys = Game.GetPreventionSystem() end)
    end
    return sys
end

-- WHAT THE PREVENTION SYSTEM ITSELF SAYS THE HEAT IS.
--
-- `GetHeatStage` and `GetHeatStageAsInt` are public, so the system can be asked
-- directly instead of guessing from the star meter. That splits the failure in
-- two, which the star meter alone cannot:
--
--   the system says Heat_3 and no stars show  -> the request worked and
--       something downstream is suppressing it, most likely a prevention free
--       area. The compound is a Militech security zone and the system has a
--       `m_playerIsInPreventionFreeArea` flag for exactly that.
--   the system still says Heat_0             -> the request never landed, and
--       queueing it from Lua is not the same as queueing it from redscript.
--
-- It is drawn every frame rather than logged, so the number can be watched
-- while the button is pressed.
local function heatNow()
    local sys = preventionSystem()
    if sys == nil then return "no PreventionSystem" end
    local stage, n = "?", "?"
    pcall(function() stage = tostring(sys:GetHeatStage()) end)
    pcall(function() n = tostring(sys:GetHeatStageAsInt()) end)
    return string.format("%s  (as int: %s)", stage, n)
end

-- WHICH DISTRICT THE GAME THINKS V IS IN, and whether it counts as the
-- Badlands. The same call the gig makes: the prevention system's district
-- stack, read through `GetCurrentDistrict`, and `IsBadlands()` on the top of
-- it, which looks through a named sub-district to its parent. "nil" means the
-- stack is empty, which it is for a frame or two after a load; the gig treats
-- that as still inside.
local function districtNow()
    local sys = preventionSystem()
    if sys == nil then return "no PreventionSystem" end
    local d = nil
    pcall(function() d = sys:GetCurrentDistrict() end)
    if d == nil then return "nil (unknown; treated as inside)" end
    local id, bad = "?", "?"
    pcall(function() id = tostring(TDBID.ToStringDEBUG(d:GetDistrictID())) end)
    pcall(function() bad = tostring(d:IsBadlands()) end)
    return string.format("%s   badlands: %s", id, bad)
end

-- THREE STARS, THE ROUTE THAT IS NOW KNOWN TO BE THE REAL ONE.
--
-- Read out of the decompiled scripts: PreventionSystem has no public setter,
-- only a handler for a queued request.
--
--     private final func OnSetWantedLevel(evt: ref<SetWantedLevel>)
--     public class SetWantedLevel extends ScriptableSystemRequest
--
-- The handler switches prevention on, takes V's position as the crime point,
-- and changes the heat stage with reason "QuestEvent". That is what the gig
-- wants when the trace lands, so this is the shape the redscript will use.
-- KEPT, BUT IT DOES NOT WORK, AND THE READOUT ABOVE IS WHY IT IS KEPT.
--
-- Measured 2026-09-09: this builds the request, m_wantedLevel reads back as
-- Heat_3, QueueRequest is accepted, and GetHeatStage() still answers Heat_0.
-- Eight spellings of the construction behaved identically. Lua cannot hand the
-- native a request object it will accept, and the native drops it silently.
--
-- The working version is redscript, in CCShared_Prevention.reds. This stays as
-- the record of what was tried, so nobody spends another session on it, and the
-- button is gone from the window so nobody presses it expecting stars.
local function giveThreeStars()
    local sys = preventionSystem()
    if sys == nil then
        status = "no PreventionSystem"
        print("[G03] no PreventionSystem")
        return
    end
    local ok, err = pcall(function()
        local evt = SetWantedLevel.new()
        evt.m_wantedLevel = EPreventionHeatStage.Heat_3
        evt.m_forcePlayerPositionAsLastCrimePoint = true
        sys:QueueRequest(evt)
    end)
    status = ok and "three stars requested, watch the meter"
                or ("refused: " .. tostring(err))
    print("[G03] " .. status)
end

-- WHAT DID THE REQUEST ACTUALLY CARRY?
--
-- The direct button above reported success and moved no stars, which narrows
-- it to one thing: the call was fine and the VALUE was not. `OnSetWantedLevel`
-- returns immediately when `m_wantedLevel` is Heat_0, and Heat_0 is the field's
-- default, so an enum that did not resolve in Lua produces exactly this: a
-- request that is accepted, handled, and does nothing.
--
-- So this stops guessing at call syntax and starts reading back what was set.
-- Every route builds the event, assigns the heat stage a different way, PRINTS
-- WHAT THE FIELD THEN HOLDS, and queues it. The route whose readback is not
-- Heat_0 is the answer.
local function wantedProbe()
    local out = {}
    local function line(t)
        out[#out + 1] = t
        print("[G03] " .. t)
    end

    line("------------- wanted level, what the field holds -------------")

    local sys = preventionSystem()
    line("PreventionSystem  " .. (sys ~= nil and "found" or "NOT FOUND"))
    if sys == nil then
        status = "no PreventionSystem"
        return
    end

    -- Is the enum visible to Lua at all? If this prints nil, every assignment
    -- below that uses it is writing nil and the default survives.
    local enumOk, enumVal = pcall(function() return EPreventionHeatStage.Heat_3 end)
    line("EPreventionHeatStage.Heat_3 -> " ..
         (enumOk and tostring(enumVal) or "NOT VISIBLE TO LUA"))

    local function newEvent(how)
        local evt = nil
        if how == "SetWantedLevel.new()" then
            pcall(function() evt = SetWantedLevel.new() end)
        else
            pcall(function() evt = NewObject("SetWantedLevel") end)
        end
        return evt
    end

    local assigns = {
        { "enum EPreventionHeatStage.Heat_3",
          function(evt) evt.m_wantedLevel = EPreventionHeatStage.Heat_3 end },
        { "Enum.new(EPreventionHeatStage, Heat_3)",
          function(evt) evt.m_wantedLevel = Enum.new("EPreventionHeatStage", "Heat_3") end },
        { "the string Heat_3",
          function(evt) evt.m_wantedLevel = "Heat_3" end },
        { "the number 3",
          function(evt) evt.m_wantedLevel = 3 end },
    }

    for _, ctor in ipairs({ "SetWantedLevel.new()", "NewObject" }) do
        for _, a in ipairs(assigns) do
            local label, setter = a[1], a[2]
            local evt = newEvent(ctor)
            if evt == nil then
                line(string.format("  %-22s %-38s event NOT CREATED", ctor, label))
            else
                local sok = pcall(function() setter(evt) end)
                local readback = "?"
                pcall(function() readback = tostring(evt.m_wantedLevel) end)
                local qok = false
                if sok then
                    qok = pcall(function()
                        evt.m_forcePlayerPositionAsLastCrimePoint = true
                        sys:QueueRequest(evt)
                    end)
                end
                line(string.format("  %-22s %-38s -> %s %s",
                    ctor, label, readback,
                    (sok and (qok and "(queued)" or "(queue refused)") or "(assign refused)")))
            end
        end
    end

    line("The route whose readback is NOT Heat_0 is the one to ship.")
    line("If every readback says Heat_0, the enum is not reachable from Lua and")
    line("the answer is to do this from redscript, where it certainly is.")

    local f = io.open("wanted_probe.txt", "a")
    if f then
        for _, l in ipairs(out) do f:write(l .. "\n") end
        f:close()
    end
    status = "wanted probe run, read the Console tab"
end

-- WHY IS THE GIG NOT STARTING?
--
-- Gig03_Start.reds holds five conditions and sets `cc_g03_start` only when all
-- five pass. When it holds, nothing says so: the player gets silence, which
-- looks exactly like a broken install. This reads the same five, live, so the
-- one that is false is visible.
--
-- It reads the game; it changes nothing. The redscript is what actually
-- decides, and this is a copy of its conditions, so if the two ever disagree
-- the redscript is right and this is stale.
local function gateRows()
    local rows = {}
    local function row(ok, label, detail)
        rows[#rows + 1] = { ok = ok, label = label, detail = detail or "" }
    end

    local prologue = get("q101_enable_side_content")
    row(prologue > 0, "the prologue is over",
        "q101_enable_side_content = " .. tostring(prologue))

    local pnr = get("q115_point_of_no_return")
    row(pnr <= 0, "the endgame has not started",
        "q115_point_of_no_return = " .. tostring(pnr))

    -- DINO HAS BEEN IN TOUCH. The gig's own condition, read off his journal
    -- contact. It fails OPEN in the redscript: if the journal cannot answer,
    -- the gig starts anyway.
    local dinoState, dinoOk = "(journal did not answer)", true
    pcall(function()
        local jm = Game.GetJournalManager()
        local e = jm:GetEntryByString("contacts/dino_dinovic", "gameJournalContact")
        if e ~= nil then
            dinoState = tostring(jm:GetEntryState(e))
            dinoOk = not string.find(dinoState, "Inactive")
        end
    end)
    row(dinoOk, "Dino has been in touch", "contacts/dino_dinovic = " .. dinoState)

    local phoneOk = false
    pcall(function()
        local phone = Game.GetScriptableSystemsContainer():Get(CName.new("PhoneSystem"))
        phoneOk = phone:IsCallingEnabled()
    end)
    row(phoneOk, "the phone can ring now",
        phoneOk and "" or "in a menu, on a device, or mid-load")

    local held = get(HOLD) > 0
    row(not held, "the trigger is not held", held and "cc_g03_dev_hold = 1" or "")

    -- NAME THE FACT. "Already run" is true of three different facts and the
    -- fix is the same for all three, but knowing which one is set says how far
    -- the last run got, which is the difference between "it started" and "it
    -- finished".
    local ran = {}
    for _, f in ipairs({ "cc_g03_start", "cc_g03_called", "cc_g03_done" }) do
        if get(f) > 0 then ran[#ran + 1] = f end
    end
    row(#ran == 0, "the gig has not already run",
        #ran > 0 and ("set on this save: " .. table.concat(ran, ", ")
                      .. "  -> CLEAR EVERYTHING, then reload a save") or "")

    return rows
end

local function teleport(x, y, z)
    local p = Game.GetPlayer()
    if not p then return end
    Game.GetTeleportationFacility():Teleport(
        p, Vector4.new(x, y, z, 1.0), EulerAngles.new(0, 0, 0))
    status = string.format("teleported to %.1f, %.1f, %.1f", x, y, z)
end

-- WALK THE CHAIN. Each press satisfies the next objective's gate, so the gig can
-- be driven from the log without playing it. It stops at the first fact that is
-- not yet set rather than setting them all, because setting them all at once
-- races the graph.
local CHAIN = { "cc_g03_start", "cc_g03_called", "cc_g03_arrived",
                "cc_g03_inside", "cc_g03_terminal", "cc_g03_data",
                "cc_g03_alarm", "cc_g03_shard_got", "cc_g03_escaped",
                "cc_g03_shard_read", "cc_g03_badlands_left", "cc_g03_on_foot",
                "cc_g03_at_bar", "cc_g03_delivered", "cc_g03_left_dino" }

local function advance()
    for _, f in ipairs(CHAIN) do
        if get(f) <= 0 then
            set(f, 1)
            return
        end
    end
    status = "the whole chain is already set"
end

local function resetAll()
    for _, row in ipairs(FACTS) do set(row[1], 0) end
    for _, row in ipairs(PROBES) do set(row[1], 0) end
    status = "every fact cleared"
end

registerForEvent("onOverlayOpen", function() visible = true end)
registerForEvent("onOverlayClose", function() visible = false end)

registerForEvent("onDraw", function()
    if not visible then return end
    ImGui.SetNextWindowSize(560, 620, ImGuiCond.FirstUseEver)
    if not ImGui.Begin("Acceptable Loss [DEV]") then ImGui.End() return end

    ImGui.Text(status)
    ImGui.Text("heat right now: " .. heatNow())
    ImGui.Text("district: " .. districtNow())
    ImGui.TextDisabled("raised by the gig at the security-room door, kept up until the district stops being Badlands")
    ImGui.Separator()

    if ImGui.Button("COUNT THE GUARDS") then census() end
    ImGui.SameLine()
    if ImGui.Button("WANTED LEVEL PROBE") then wantedProbe() end
    ImGui.SameLine()
    ImGui.TextDisabled("stand inside the compound first")

    if ImGui.Button("NEXT STEP") then advance() end
    ImGui.SameLine()
    if ImGui.Button("START THE GIG") then set("cc_g03_start", 1) end
    ImGui.SameLine()
    if ImGui.Button("CLEAR EVERYTHING") then resetAll() end

    local held = get(HOLD) > 0
    if ImGui.Button(held and "RELEASE THE TRIGGER" or "HOLD THE TRIGGER") then
        set(HOLD, held and 0 or 1)
    end
    ImGui.SameLine()
    ImGui.Text(held and "held: the gig will not offer itself" or "the trigger is live")

    if ImGui.CollapsingHeader("Why is the gig not starting?") then
        local all = true
        for _, r in ipairs(gateRows()) do
            if not r.ok then all = false end
            ImGui.Text((r.ok and "  OK   " or " NO    ") .. r.label)
            if r.detail ~= "" then
                ImGui.TextDisabled("         " .. r.detail)
            end
        end
        if all then
            ImGui.TextWrapped("All five pass. The trigger checks at 24 seconds "
                .. "after a load, then 30, 30, 60, then every 5 minutes. Give "
                .. "it half a minute, or press START THE GIG.")
        end
    end

    if ImGui.CollapsingHeader("Facts") then
        for _, row in ipairs(FACTS) do
            local name, why = row[1], row[2]
            local v = get(name)
            ImGui.Text(string.format("%d  %s", v, name))
            ImGui.SameLine()
            if ImGui.SmallButton("1##" .. name) then set(name, 1) end
            ImGui.SameLine()
            if ImGui.SmallButton("0##" .. name) then set(name, 0) end
            ImGui.TextDisabled("     " .. why)
        end
    end

    if ImGui.CollapsingHeader("Probes, read only") then
        for _, row in ipairs(PROBES) do
            ImGui.Text(string.format("%d  %s", get(row[1]), row[1]))
            ImGui.TextDisabled("     " .. row[2])
        end
    end

    if ImGui.CollapsingHeader("Teleports") then
        for _, t in ipairs(TELEPORTS) do
            if ImGui.Button(t[1]) then teleport(t[2], t[3], t[4]) end
        end
        ImGui.Separator()
        ImGui.TextDisabled("Just outside the wire. Heights are computed, not walked.")
        for _, t in ipairs(OUTSIDE) do
            if ImGui.Button(t[1]) then teleport(t[2], t[3], t[4]) end
        end
        ImGui.Separator()
        ImGui.TextDisabled("The other computers. Never seen in game, may be props.")
        for _, t in ipairs(COMPUTERS) do
            if ImGui.Button(t[1]) then teleport(t[2], t[3], t[4]) end
        end
    end

    ImGui.Separator()
    ImGui.TextWrapped("Redscript and the archive are read at launch. A change to "
        .. "either needs a full quit to desktop, not a mod reload.")
    ImGui.End()
end)
