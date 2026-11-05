-- Trauma Team [DEV]: the gig's own CET menu. Not shipped.
--
-- What it is for, in the order it gets pressed:
--
--   1. THE SHIFT. Fact buttons to start the gig without waiting for the ad
--      (cc_g05_ad_go), to skip the interview (cc_g05_hired), and to call the
--      roof clear if the fight stalls (cc_g05_site_clear). Teleports to the
--      recruiter, the pad and the roof.
--   2. THE AV LAB. Look at the AV and press. It reads the vehicle under the
--      crosshair: its record, its look, its seats and who is in them. It can
--      put V on a slot and take V off the script way (Drive an Aerial
--      Vehicle's call, docs/gig05-av-research.md 3), switch the thrusters,
--      open the left doors, and lift the AV 10 m with everyone aboard. Each
--      answers one of the open questions in that file's section 7 without
--      the quest having to reach it.
--
-- CET Lua reloads in place, so "Reload all mods" is enough for a change to
-- this file. Everything else in this mod is read at launch and needs a full
-- restart.

local visible = false
local status = "ready"

local function qs() return Game.GetQuestsSystem() end

local function get(f)
    local v = 0
    pcall(function() v = qs():GetFactStr(f) end)
    return v
end

local function set(f, v)
    pcall(function() qs():SetFactStr(f, v) end)
    status = string.format("%s = %d", f, v)
    print("[G05] " .. status)
end

local function say(s)
    status = s
    print("[G05] " .. s)
end

-- THE FACTS. Who sets each in a real playthrough; the same table is in the
-- header of tools/gig05/gen_questphase.py and the two must agree.
local FACTS = {
    { "cc_g05_ad_go",      "THE START. Gig05_Shift.reds sets it after the prologue, or here" },
    { "cc_g05_hired",      "SKIP THE INTERVIEW. Its scene sets it as it ends" },
    { "cc_g05_board_taken","the board prompt was taken (the scene writes it; the graph clears it)" },
    { "cc_g05_site_clear", "THE ROOF IS CLEAR. Gig05_Shift.reds sets it when no Scav stands" },
    { "cc_g05_dev_down",   "TEST ONLY: 1 kills every Scav still standing (the script clears it)" },
}
local READOUTS = {
    "cc_g05_on_shift", "cc_g05_aboard", "cc_g05_fight_on", "cc_g05_on_roof", "cc_g05_changed",
    "cc_g05_dressed", "cc_g05_off_duty", "cc_g05_kit", "cc_g05_shift_done",
    "q101_enable_side_content",
}

-- gig05_config: the recruiter, a step in front of the pad's board marker,
-- and the roof beside where the AV lands.
local TELEPORTS = {
    { "The recruiter (Medical Center)", -1338.0, 1744.0, 18.4 },
    { "The lift, street", -1261.5, 1758.0, 18.7 },
    { "The locker room", -1313.0, 1764.4, 129.7 },
    { "The pad", -1358.5, 1781.0, 129.7 },
    { "The roof (incident 1)", -2146.0, 474.0, 96.2 },
}

local function teleport(x, y, z)
    local p = Game.GetPlayer()
    if not p then return end
    Game.GetTeleportationFacility():Teleport(p, Vector4.new(x, y, z, 1.0), EulerAngles.new(0, 0, 0))
    say(string.format("teleported to %.1f, %.1f, %.1f", x, y, z))
end

-- ----------------------------------------------- every Trauma Team place
--
-- EVERY PLACE THE GAME STAGES TRAUMA TEAM, read off its own sectors on
-- 2026-11-03 (`python tools\sector_scan.py index trauma`, 1,054 nodes, in
-- tools/_sector_cache/index_trauma.json), to look at each in game as a pad
-- or an incident site. Each row is { label, x, y, z, note }. V lands a few
-- metres from the spot named, at its own height plus half a metre.
--
-- THE INTERVENTIONS are the game's own open-world Trauma Team scenes
-- (`cs_trauma_team_inervention`, the game's spelling): each has a spot the
-- AV lands on and a spot for the patient, in a quest sector of its own.
-- V is put beside the patient spot; the AV spot is a few metres off.
local TT_GROUPS = {
    { "MEDICAL CENTER, Little China (the Trauma Team hub)", {
        { "Career Opportunities hand scan (the recruiter stands here)", -1338.0, 1744.0, 18.7, "street level, covered walkway" },
        { "Staff chatting outside (wat_lch_chat_013)", -1343.0, 1714.0, 18.7, "Trauma Team people chat here" },
    } },
    { "USED BY THE GIG NOW", {
        { "Incident 1: hotel roof (sts_cct_dtn_04)", -2146.0, 474.0, 96.3, "the gig's first landing" },
    } },
    { "QUESTS AND WORLD STORIES", {
        { "The Rescue: Trauma Team landing (q001)", -452.0, 438.0, 132.5, "prologue, may be closed off" },
        { "The Heist: Trauma Team AV at Konpeki (q005)", -2204.0, 1762.0, 321.0, "high up, may be closed off" },
        { "The Beast in Me: Sampson's crash (sq024)", -1384.0, 1420.0, 25.5, "" },
        { "The Hunt: Trauma Team at the farm (sq021)", 2446.3, -1350.0, 64.0, "Badlands" },
        { "Pyramid Song area AVs (q112)", -480.0, 726.0, 59.0, "two AV spawns" },
        { "Phantom Liberty AV (q307)", -1460.0, 1313.0, 88.5, "Phantom Liberty" },
        { "Heywood: Trauma Team vs Tyger Claws (mws_hey_07)", -1172.0, -870.0, 53.3, "world story with its own Trauma Team AV" },
        { "Pacifica: Trauma Team AV (mws_pac_06)", -2103.0, -2033.0, 15.3, "world story" },
        { "Pacifica: Trauma Team interior (traumateam_01)", -1398.0, -2019.0, 75.0, "interior" },
        { "Dead Trauma Team pilot (ma_generic)", -2196.0, -983.4, 36.7, "a crashed crew" },
    } },
    { "OPEN-WORLD INTERVENTIONS (AV spot + patient spot)", {
        { "Intervention 01", -1204.2, 1897.0, 21.2, "Watson" },
        { "Intervention 02", -1560.8, 264.0, 8.7, "" },
        { "Intervention 03", -381.5, 1649.5, 40.3, "" },
        { "Intervention 04", -1013.9, 19.0, 8.0, "" },
        { "Intervention 05", -1664.8, -553.8, 13.5, "" },
        { "Intervention 06", -1835.7, -492.8, 10.7, "" },
        { "Intervention 07", -1764.3, -58.5, 8.1, "two AV spots" },
        { "Intervention 08", -1063.2, -491.5, 8.7, "" },
        { "Intervention 09", 92.9, 803.5, 129.4, "high up" },
        { "Intervention 10", -1837.0, 2063.4, 18.6, "Watson" },
        { "Intervention 11", -2431.4, -633.0, 7.5, "" },
        { "Intervention 12", -1971.5, 1213.5, 9.4, "" },
        { "Intervention 13", -1822.4, 1443.4, 10.6, "" },
        { "Intervention 14", -1165.6, 247.5, 5.8, "" },
        { "Intervention 15", -2269.2, -1035.2, 8.3, "" },
        { "Intervention 16", -1428.9, 996.9, 29.5, "" },
        { "Intervention 17", -2370.2, 419.2, 9.3, "" },
        { "Intervention 18", -1252.9, 73.7, 8.2, "" },
        { "Intervention 19", -829.3, 844.1, 22.9, "" },
        { "Intervention 20", -195.4, 285.9, 36.6, "" },
        { "Intervention 21", -1349.3, -43.6, 30.7, "" },
        { "Intervention 22", -506.4, 922.0, 56.6, "" },
        { "Intervention 23", -790.0, 897.8, 12.5, "" },
        { "Intervention 24", 355.4, -206.2, 12.1, "" },
        { "Intervention 25", -58.9, -35.5, 7.7, "" },
    } },
}

-- WHERE V IS, printed to the console and shown here, so a spot found by
-- walking can be written down exactly.
local hereText = ""
local function whereAmI()
    pcall(function()
        local p = Game.GetPlayer():GetWorldPosition()
        local yaw = Game.GetPlayer():GetWorldYaw()
        hereText = string.format("V at %.2f, %.2f, %.2f  yaw %.1f", p.x, p.y, p.z, yaw)
        print("[G05] " .. hereText)
    end)
end

-- ------------------------------------------------------------- the AV lab
local SLOTS = { "player_standing", "tt_1", "tt_2", "seat_front_left", "seat_front_right",
                "seat_back_left", "seat_back_right" }
local labLines = {}

local function lookedAt()
    local player = Game.GetPlayer()
    local obj = Game.GetTargetingSystem():GetLookAtObject(player, false, false)
    if obj and obj:IsVehicle() then return obj end
    return nil
end

local function readAV()
    labLines = {}
    local ok, err = pcall(function()
        local av = lookedAt()
        if not av then
            table.insert(labLines, "no vehicle under the crosshair")
            return
        end
        local rec = TDBID.ToStringDEBUG(av:GetRecordID())
        table.insert(labLines, "record: " .. tostring(rec))
        table.insert(labLines, "look: " .. Game.NameToString(av:GetCurrentAppearanceName()))
        local p = av:GetWorldPosition()
        table.insert(labLines, string.format("at %.2f, %.2f, %.2f  yaw %.1f", p.x, p.y, p.z, av:GetWorldYaw()))
        table.insert(labLines, "is AV: " .. tostring(av:IsA("vehicleAVBaseObject")))
        local mf = Game.GetMountingFacility()
        for _, s in ipairs(SLOTS) do
            local slot = MountingSlotId.new()
            slot.id = s
            local info = mf:GetMountingInfoSingleWithIds(nil, av:GetEntityID(), slot)
            local who = "empty"
            if info and info.childId and EntityID.IsDefined(info.childId) then
                local child = Game.FindEntityByID(info.childId)
                who = child and Game.NameToString(child:GetClassName()) or "someone"
            end
            table.insert(labLines, string.format("  slot %-18s %s", s, who))
        end
    end)
    if not ok then table.insert(labLines, "read failed: " .. tostring(err)) end
end

-- V ON A SLOT, Drive an Aerial Vehicle's way (its av.lua, 763-810): a
-- MountingRequest naming the AV, V and the slot.
local function mountV(slotName, instant)
    local ok, err = pcall(function()
        local av = lookedAt()
        if not av then say("look at the AV first") return end
        local player = Game.GetPlayer()
        local data = MountEventData.new()
        data.isInstant = instant
        data.slotName = slotName
        data.mountParentEntityId = av:GetEntityID()
        local slot = MountingSlotId.new()
        slot.id = slotName
        local info = MountingInfo.new()
        info.childId = player:GetEntityID()
        info.parentId = av:GetEntityID()
        info.slotId = slot
        local req = MountingRequest.new()
        req.lowLevelMountingInfo = info
        req.mountData = data
        req.preservePositionAfterMounting = true
        Game.GetMountingFacility():Mount(req)
        say("asked to mount V on " .. slotName .. (instant and " (instant)" or ""))
    end)
    if not ok then say("mount failed: " .. tostring(err)) end
end

local function unmountV()
    local ok, err = pcall(function()
        local player = Game.GetPlayer()
        local info = MountingInfo.new()
        info.childId = player:GetEntityID()
        local data = MountEventData.new()
        data.isInstant = true
        local req = UnmountingRequest.new()
        req.lowLevelMountingInfo = info
        req.mountData = data
        Game.GetMountingFacility():Unmount(req)
        say("asked to unmount V")
    end)
    if not ok then say("unmount failed: " .. tostring(err)) end
end

local function thrusters(on)
    pcall(function()
        local av = lookedAt()
        if not av then say("look at the AV first") return end
        if on then av:TurnOnThrusters() else av:TurnOffThrusters() end
        say("thrusters " .. (on and "on" or "off"))
    end)
end

local function animEvent(name)
    pcall(function()
        local av = lookedAt()
        if not av then say("look at the AV first") return end
        AnimationControllerComponent.PushEvent(av, name)
        say("sent " .. name)
    end)
end

-- THE CUT BETWEEN TWO SITES, in small: the AV moved 10 m up with everyone
-- aboard. Pass when V and the crew are still on their slots afterwards.
local function liftAV()
    pcall(function()
        local av = lookedAt()
        if not av then say("look at the AV first") return end
        local p = av:GetWorldPosition()
        Game.GetTeleportationFacility():Teleport(av, Vector4.new(p.x, p.y, p.z + 10.0, 1.0),
            EulerAngles.new(0, 0, av:GetWorldYaw()))
        say("AV lifted 10 m: read it again and check the slots")
    end)
end

-- THE FLIGHT RECORDER. While a shift is on, writes a line to
-- trauma_team_trace.log each time V moves more than 30 m in a quarter of a
-- second, or one of the shift's facts changes. Opened and closed per line,
-- so a running game can be read from disk.
local TRACE_FACTS = {"cc_g05_board_taken", "cc_g05_seat_claim", "cc_g05_aboard",
    "cc_g05_park", "cc_g05_fight_on", "cc_g05_site_clear",
    "cc_g05_on_roof", "cc_g05_at_street", "cc_g05_on_shift"}
local trace = {t = 0, last = nil, facts = {}, clock = 0}
local function traceLine(text)
    local f = io.open("trauma_team_trace.log", "a")
    if f then
        f:write(string.format("%.2f %s\n", trace.clock, text))
        f:close()
    end
end
local function onUpdate1(dt)
    trace.clock = trace.clock + dt
    trace.t = trace.t + dt
    if trace.t < 0.25 then return end
    trace.t = 0
    local player = Game.GetPlayer()
    local qs = Game.GetQuestsSystem()
    if not player or not qs or qs:GetFactStr("cc_g05_ad_go") == 0 then return end
    local p = player:GetWorldPosition()
    if trace.last then
        local dx, dy, dz = p.x - trace.last.x, p.y - trace.last.y, p.z - trace.last.z
        if dx * dx + dy * dy + dz * dz > 900 then
            traceLine(string.format("JUMP (%.1f, %.1f, %.1f) -> (%.1f, %.1f, %.1f)",
                trace.last.x, trace.last.y, trace.last.z, p.x, p.y, p.z))
        end
    end
    trace.last = {x = p.x, y = p.y, z = p.z}
    for _, name in ipairs(TRACE_FACTS) do
        local v = qs:GetFactStr(name)
        if trace.facts[name] ~= v then
            traceLine(string.format("%s %s -> %s at (%.1f, %.1f, %.1f)", name,
                tostring(trace.facts[name]), v, p.x, p.y, p.z))
            trace.facts[name] = v
        end
    end
end

-- THE SKY PROBE. Collision exists only near V, so V is stood on each spot
-- the AV takes off from or lands on (`routes.lua`, written by
-- gen_community.py), and after the city round V has streamed in, rays go
-- out from 4 m above the spot: every 15 degrees round, at 90, 82, 75, 68 and
-- 60 degrees up, each until it is 360 m above the spot. Each ray's first
-- hit, or "clear", goes to `route_sky.txt` as "spot azimuth elevation
-- distance". tools/gig05/gig05_config.py takes its climbs and descents from
-- the clear ones. A first probe flew V over the city at 250 m and found
-- nothing: far from V there is no collision to hit, and V died falling.
local probe = nil
local recStart, recStop, recPinsShow
local recPinOnly
local function probeLog(file, text)
    local f = io.open(file, "a")
    if f then f:write(text .. "\n") f:close() end
end
local function ray(a, b)
    local ok, h = Game.GetSpatialQueriesSystem():SyncRaycastByCollisionGroup(
        Vector4.new(a[1], a[2], a[3], 1), Vector4.new(b[1], b[2], b[3], 1), "Static", false, false)
    if ok then return h.position end
    return nil
end
local function startSky()
    local ok, R = pcall(require, "routes")
    if not ok or not R.spots then say("no routes.lua spots") return end
    Game.GetGodModeSystem():AddGodMode(Game.GetPlayer():GetEntityID(),
        gameGodModeType.Invulnerable, "cc_g05_probe")
    local f = io.open("route_sky.txt", "w") if f then f:close() end
    probe = {stations = R.spots, i = 0, wait = 0}
    say("sky probe: " .. #R.spots .. " spots")
end
-- THE GROUND UNDER EVERY POST, fact 2: V is stood at each call in turn, and
-- for every post there (`routes.lua` posts) a ray finds the ground within
-- 3 m of the height the post is written at. "post x y written ground" to
-- `route_posts.txt`; tools/gig05/gig05_config.py reads them back.
local function startPosts()
    local ok, R = pcall(require, "routes")
    if not ok or not R.posts then say("no routes.lua posts") return end
    Game.GetGodModeSystem():AddGodMode(Game.GetPlayer():GetEntityID(),
        gameGodModeType.Invulnerable, "cc_g05_probe")
    local f = io.open("route_posts.txt", "w") if f then f:close() end
    local st = {}
    for _, s in ipairs(R.spots) do
        local list = {}
        for _, q in ipairs(R.posts) do
            if string.sub(q[1], 1, #s[1] + 1) == s[1] .. "." then table.insert(list, q) end
        end
        table.insert(st, {s[1], s[2], s[3], s[4], posts = list})
    end
    probe = {stations = st, i = 0, wait = 0, posts = true}
    say("post probe: " .. #st .. " places")
end
local function postsAt(s)
    for _, q in ipairs(s.posts) do
        local h = ray({q[2], q[3], q[4] + 3}, {q[2], q[3], q[4] - 3})
        probeLog("route_posts.txt", string.format("%s %.2f %.2f %.2f %s", q[1], q[2], q[3], q[4],
            h and string.format("%.2f", h.z) or "none"))
    end
end
local function skyAt(s)
    local o = {s[2], s[3], s[4] + 4}
    for az = 0, 345, 15 do
        for _, el in ipairs(az == 0 and {90, 82, 75, 68, 60} or {82, 75, 68, 60}) do
            local r, e = math.rad(az), math.rad(el)
            local len = 360 / math.sin(e)
            local tip = {o[1] - math.sin(r) * math.cos(e) * len,
                         o[2] + math.cos(r) * math.cos(e) * len, o[3] + 360}
            local h = ray(o, tip)
            local d = h and math.sqrt((h.x - o[1]) ^ 2 + (h.y - o[2]) ^ 2 + (h.z - o[3]) ^ 2) or -1
            probeLog("route_sky.txt", string.format("%s %d %d %.1f", s[1], az, el, d))
        end
    end
end
-- THE GLIDE PROBE, fact 6: V is stood on each spot in turn, and for every
-- 10 degrees round and each climb angle from 8 to 50 degrees, three rays go
-- out from 2.5 m above the spot to 260 m away along the ground (the AV's
-- middle and 4 m to each side of it). "spot azimuth elevation distance" to
-- `route_glide.txt`, the nearest hit of the three or -1. A straight takeoff
-- or landing along that azimuth at that angle is open when it is -1.
-- tools/gig05/flight_paths.py picks each spot's slopes from it.
local function glideAt(s)
    for az = 0, 350, 10 do
        local r = math.rad(az)
        local fx, fy = -math.sin(r), math.cos(r)
        for _, el in ipairs({8, 12, 17, 22, 28, 35, 42, 50}) do
            local rise = math.tan(math.rad(el)) * 260
            local best = -1
            for _, side in ipairs({0, 4, -4}) do
                local ox, oy = s[2] - fy * side, s[3] + fx * side
                local o = {ox, oy, s[4] + 2.5}
                local tip = {ox + fx * 260, oy + fy * 260, s[4] + 2.5 + rise}
                local h = ray(o, tip)
                if h then
                    local d = math.sqrt((h.x - o[1]) ^ 2 + (h.y - o[2]) ^ 2)
                    if best < 0 or d < best then best = d end
                end
            end
            probeLog("route_glide.txt", string.format("%s %d %d %.1f", s[1], az, el, best))
        end
    end
end
local function startGlide()
    local ok, R = pcall(require, "routes")
    if not ok or not R.spots then say("no routes.lua spots") return end
    Game.GetGodModeSystem():AddGodMode(Game.GetPlayer():GetEntityID(),
        gameGodModeType.Invulnerable, "cc_g05_probe")
    local f = io.open("route_glide.txt", "w") if f then f:close() end
    probe = {stations = R.spots, i = 0, wait = 0, glide = true}
    say("glide probe: " .. #R.spots .. " spots")
end
-- THE PATH PROBE, fact 7: every flight path in `routes.lua` checked against
-- the buildings the way the AV flies it. V is put at a station (each spot
-- on the ground, then a point every 250 m along each path, dropped from
-- the path's height), and every stretch of every path within 300 m of V is swept by five
-- rays: down the middle, 4 m to each side, 2.5 m above and below. Each hit
-- goes to `route_hits.txt` as "path point x y z offset". Collision is
-- only there near V, which is why V goes along too, and why each station
-- waits for the ground under V (below, in onUpdate2).
local function pathAt(st, R)
    local offs = {{"mid", 0, 0}, {"left", 4, 0}, {"right", -4, 0}, {"up", 0, 2.5}, {"down", 0, -2.5}}
    for name, pts in pairs(R) do
        if type(pts) == "table" and type(pts[1]) == "table" and type(pts[1][1]) == "number" then
            for i = 1, #pts - 1 do
                local a, b = pts[i], pts[i + 1]
                local mx, my = (a[1] + b[1]) / 2, (a[2] + b[2]) / 2
                if (mx - st[2]) ^ 2 + (my - st[3]) ^ 2 < 300 ^ 2 then
                    local dx, dy = b[1] - a[1], b[2] - a[2]
                    local n = math.sqrt(dx * dx + dy * dy)
                    if n > 0.01 then
                        local lx, ly = -dy / n, dx / n
                        for _, o in ipairs(offs) do
                            local h = ray({a[1] + lx * o[2], a[2] + ly * o[2], a[3] + o[3]},
                                          {b[1] + lx * o[2], b[2] + ly * o[2], b[3] + o[3]})
                            if h then
                                probeLog("route_hits.txt", string.format("%s %d %.1f %.1f %.1f %s",
                                    name, i, h.x, h.y, h.z, o[1]))
                            end
                        end
                    end
                end
            end
        end
    end
end
local function startPath()

    local ok, R = pcall(require, "routes")
    if not ok or not R.spots then say("no routes.lua") return end
    Game.GetGodModeSystem():AddGodMode(Game.GetPlayer():GetEntityID(),
        gameGodModeType.Invulnerable, "cc_g05_probe")
    local f = io.open("route_hits.txt", "w") if f then f:close() end
    -- THE OTHER WAYS EACH LEG COULD GO (tools/gig05/route_candidates.py),
    -- swept with the paths in use when the file is there.
    local paths = {}
    for _, name in ipairs({"out", "r12", "r23", "back"}) do paths[name] = R[name] end
    -- `candidates.lua`, or `candidates2.lua` to `candidates9.lua` for a
    -- later round in the same session: CET's require keeps the first copy
    -- of a file it has read until the game restarts.
    for k = 1, 9 do
        local okc, C = pcall(require, k == 1 and "candidates" or ("candidates" .. k))
        if okc and type(C) == "table" then
            for name, pts in pairs(C) do paths[name] = pts end
        end
    end
    local st = {}
    for _, s in ipairs(R.spots) do table.insert(st, {s[1], s[2], s[3], s[4]}) end
    -- A stop every 250 m along every path, none within 200 m of another.
    for name, pts in pairs(paths) do
        local d = 0
        for i = 2, #pts do
            d = d + math.sqrt((pts[i][1] - pts[i - 1][1]) ^ 2 + (pts[i][2] - pts[i - 1][2]) ^ 2)
            if d >= 250 then
                d = 0
                local near = false
                for _, o in ipairs(st) do
                    if (o[2] - pts[i][1]) ^ 2 + (o[3] - pts[i][2]) ^ 2 < 200 ^ 2 then near = true end
                end
                if not near then
                    table.insert(st, {name .. i, pts[i][1], pts[i][2], pts[i][3] + 6, air = true})
                end
            end
        end
    end
    probe = {stations = st, i = 0, wait = 0, path = paths}
    say("path probe: " .. #st .. " stations")
end
local function onUpdate2(dt)
    -- From the console: fact cc_g05_dev_probe 1 for the sky probe, 2 for the
    -- posts, 3 to start the flight recorder, 4 to stop it, 5 for the pins.
    local q = Game.GetQuestsSystem()
    local want = q and q:GetFactStr("cc_g05_dev_probe") or 0
    if want >= 3 and want <= 5 then
        q:SetFactStr("cc_g05_dev_probe", 0)
        if want == 3 then recStart() elseif want == 4 then recStop() else recPinsShow() end
    elseif want > 0 and not probe then
        q:SetFactStr("cc_g05_dev_probe", 0)
        if want == 2 then startPosts() elseif want == 6 then startGlide()
        elseif want == 7 then startPath() else startSky() end
    end
    if not probe then return end
    -- With the clock stopped `dt` is stopped too: a frame is counted as a
    -- sixtieth of a second instead.
    probe.wait = probe.wait - ((dt < 0.005) and (1 / 60) or dt)
    -- WAIT FOR THE CITY UNDER V: a teleport across the map is a loading
    -- screen, and the clock runs through it with no collision loaded
    -- (2026-11-03: a first run found nothing at all). The station counts
    -- only once a ray from V finds ground within 3 m below, then 4 s more
    -- for the buildings round it. On the air stations the world's clock is
    -- all but stopped, so V hangs at the path's height while the city loads
    -- under it, and the ground may be anything up to 600 m below: dropped
    -- instead, V fell through a city that was not there yet and died.
    if probe.i > 0 and probe.path and not probe.landed then
        local p = Game.GetPlayer():GetWorldPosition()
        local st = probe.stations[probe.i]
        local there = (p.x - st[2]) ^ 2 + (p.y - st[3]) ^ 2 < 30 ^ 2
        local reach = st.air and 600 or 3
        if there and probe.wait < -1.0 and ray({p.x, p.y, p.z + 0.5}, {p.x, p.y, p.z - reach}) then
            probe.landed = true
            probe.wait = 4.0
        elseif probe.wait < -40 then
            probeLog("route_hits.txt", "skipped " .. probe.stations[probe.i][1])
            probe.landed = true
            probe.wait = 0
        end
        return
    end
    if probe.wait > 0 then return end
    if probe.i > 0 then
        local st = probe.stations[probe.i]
        if probe.posts then postsAt(st) elseif probe.glide then glideAt(st)
        elseif probe.path then pathAt(st, probe.path) else skyAt(st) end
    end
    probe.i = probe.i + 1
    local s = probe.stations[probe.i]
    if probe.path then
        if s and s.air then
            Game.GetTimeSystem():SetTimeDilation("cc_g05_probe", 0.001)
        else
            Game.GetTimeSystem():UnsetTimeDilation("cc_g05_probe")
        end
    end
    if not s then
        say("sky probe done")
        print("PROBE DONE")
        probe = nil
        return
    end
    Game.GetTeleportationFacility():Teleport(Game.GetPlayer(), Vector4.new(s[2], s[3], s[4] + 1, 1),
        EulerAngles.new(0, 0, 0))
    probe.wait = 0
    probe.landed = false
    if not probe.path then probe.wait = 12.0 end
    status = string.format("sky probe %d/%d at %s", probe.i, #probe.stations, s[1])
end

-- THE FLIGHT RECORDER, for laying the AV's paths by hand. Fly V (or V's
-- vehicle) from one spot to the next the way the AV should go; the
-- recorder writes where V is every half second to `flight_rec_N.txt`, one
-- file per recording, "seconds x y z" per line. The four spots the flights
-- join get map pins (`ROUTE PINS`). Start and stop from the dev menu or
-- from CET's Bindings tab.
local rec = {on = false, n = 0, t = 0, clock = 0, file = nil}
local recPins = {}
recStart = function()
    -- The next free number: a reload of the mods must not overwrite a
    -- recording already made.
    repeat
        rec.n = rec.n + 1
        rec.file = string.format("flight_rec_%d.txt", rec.n)
        local old = io.open(rec.file, "r")
        if old then old:close() end
    until not old
    local f = io.open(rec.file, "w") if f then f:close() end
    rec.on, rec.t, rec.clock = true, 0, 0
    say("recording to " .. rec.file)
end
recStop = function()
    if rec.on then say("stopped " .. rec.file) end
    rec.on = false
end
local function recWhere()
    local p = Game.GetPlayer()
    local v = p and GetMountedVehicle(p)
    return (v or p):GetWorldPosition()
end
local function onUpdate3(dt)
    if not rec.on then return end
    rec.t = rec.t + dt
    rec.clock = rec.clock + dt
    if rec.t < 0.5 then return end
    rec.t = 0
    local w = recWhere()
    local f = io.open(rec.file, "a")
    if f then
        f:write(string.format("%.1f %.1f %.1f %.1f\n", rec.clock, w.x, w.y, w.z))
        f:close()
    end
    status = string.format("recording %s, %.0f s", rec.file, rec.clock)
end
recPinsShow = function()
    local ok, R = pcall(require, "routes")
    if not ok or not R.spots then say("no routes.lua spots") return end
    local ms = Game.GetMappinSystem()
    for _, id in ipairs(recPins) do ms:UnregisterMappin(id) end
    recPins = {}
    for _, s in ipairs(R.spots) do
        if not recPinOnly or recPinOnly == s[1] then
            local data = MappinData.new()
            data.mappinType = TweakDBID.new("Mappins.DefaultStaticMappin")
            data.variant = gamedataMappinVariant.CustomPositionVariant
            data.visibleThroughWalls = true
            table.insert(recPins, ms:RegisterMappin(data, Vector4.new(s[2], s[3], s[4], 1)))
        end
    end
    say("pins on the map: " .. #recPins)
end
registerHotkey("cc_g05_rec_start", "Trauma Team: start flight recording", recStart)
registerHotkey("cc_g05_rec_stop", "Trauma Team: stop flight recording", recStop)
registerHotkey("cc_g05_rec_pins", "Trauma Team: route pins on the map", recPinsShow)

-- THE CLEARANCE LOG: while V rides an AV, rays from the AV's middle 4 m to
-- each side, 4 m ahead and behind, 3 m up and down, every quarter second;
-- any that hits a building goes to `flight_clear.txt` with where it was.
-- Collision exists only near V, and V is aboard, so this is the one place
-- a flight path can be checked against the city as it is flown.
-- THE FLIGHT LOG: every tenth of a second aboard, "seconds x y z pitch roll
-- yaw" of the AV to `flight_log.txt`, for how fast and how level it flies.
local clear = {t = 0, log = 0, now = 0}
local function onUpdateClear(dt)
    clear.t = clear.t + dt
    clear.log = clear.log + dt
    clear.now = clear.now + dt
    local p = Game.GetPlayer()
    local av = p and GetMountedVehicle(p)
    if av and clear.log >= 0.1 then
        clear.log = 0
        local c = av:GetWorldPosition()
        local e = GetSingleton("Quaternion"):ToEulerAngles(av:GetWorldOrientation())
        local f = io.open("flight_log.txt", "a")
        if f then
            f:write(string.format("%.2f %.2f %.2f %.2f %.1f %.1f %.1f" .. string.char(10),
                clear.now, c.x, c.y, c.z, e.pitch, e.roll, e.yaw))
            f:close()
        end
    end
    if clear.t < 0.25 then return end
    clear.t = 0
    if not av then return end
    local c = av:GetWorldPosition()
    local yaw = math.rad(av:GetWorldYaw())
    local fx, fy = -math.sin(yaw), math.cos(yaw)
    local sq = Game.GetSpatialQueriesSystem()
    local dirs = {{"left", -fy * 4, fx * 4, 0}, {"right", fy * 4, -fx * 4, 0},
                  {"ahead", fx * 4, fy * 4, 0}, {"behind", -fx * 4, -fy * 4, 0},
                  {"up", 0, 0, 3}, {"down", 0, 0, -3}}
    for _, d in ipairs(dirs) do
        local ok, h = sq:SyncRaycastByCollisionGroup(Vector4.new(c.x, c.y, c.z + 1, 1),
            Vector4.new(c.x + d[2], c.y + d[3], c.z + 1 + d[4], 1), "Static", false, false)
        if ok then
            local f = io.open("flight_clear.txt", "a")
            if f then
                f:write(string.format("%s %.1f %.1f %.1f" .. string.char(10), d[1], c.x, c.y, c.z))
                f:close()
            end
        end
    end
end

-- ONE onUpdate FOR THE WHOLE MOD: CET keeps only the last handler a mod
-- registers for an event, so a second registerForEvent("onUpdate") silently
-- switched the first off (2026-11-03: the probe never started once the
-- recorder was added).
registerForEvent("onUpdate", function(dt)
    onUpdate1(dt)
    onUpdate2(dt)
    onUpdate3(dt)
    onUpdateClear(dt)
end)

registerForEvent("onOverlayOpen", function() visible = true end)
registerForEvent("onOverlayClose", function() visible = false end)

registerForEvent("onDraw", function()
    if not visible then return end
    if not ImGui.Begin("Trauma Team [DEV]") then ImGui.End() return end
    ImGui.Text(status)
    ImGui.Separator()

    if ImGui.CollapsingHeader("The shift") then
        for _, f in ipairs(FACTS) do
            local v = get(f[1])
            if ImGui.Button("0##" .. f[1]) then set(f[1], 0) end
            ImGui.SameLine()
            if ImGui.Button("1##" .. f[1]) then set(f[1], 1) end
            ImGui.SameLine()
            ImGui.Text(string.format("%d  %s", v, f[1]))
            ImGui.TextWrapped("     " .. f[2])
        end
        ImGui.Separator()
        for _, f in ipairs(READOUTS) do
            ImGui.Text(string.format("%d  %s", get(f), f))
        end
        ImGui.Separator()
        for _, t in ipairs(TELEPORTS) do
            if ImGui.Button(t[1]) then teleport(t[2], t[3], t[4]) end
        end
    end

    if ImGui.CollapsingHeader("Trauma Team places (teleport)") then
        if ImGui.Button("WHERE AM I (prints V's position)") then whereAmI() end
        if hereText ~= "" then ImGui.Text(hereText) end
        for _, g in ipairs(TT_GROUPS) do
            ImGui.Separator()
            ImGui.TextColored(0.3, 0.9, 1.0, 1.0, g[1])
            for _, t in ipairs(g[2]) do
                if ImGui.Button(t[1] .. "##tt" .. t[2]) then teleport(t[2], t[3], t[4]) end
                if t[5] ~= "" then
                    ImGui.SameLine()
                    if string.find(t[5], "BLOCKED") or string.find(t[5], "HUSTLE") then
                        ImGui.TextColored(1.0, 0.35, 0.35, 1.0, t[5])
                    else
                        ImGui.TextColored(0.7, 0.7, 0.7, 1.0, t[5])
                    end
                end
            end
        end
    end

    if ImGui.CollapsingHeader("Flight recorder") then
        ImGui.Text("Fly the path; V's place every half second goes to a file.")
        -- ONE PIN AT A TIME: a script's pin can carry no caption a player
        -- sees, and four alike on the map could not be told apart
        -- (playtest 2026-11-03; shop icons in their place did not show).
        ImGui.Text("Show one place's pin at a time; each button hides the others.")
        for _, p in ipairs({{"site1", "PIN: Call 1, hotel roof"},
                            {"site2", "PIN: Call 2, street by the water"},
                            {"site3", "PIN: Call 3, Kabuki"},
                            {"pad", "PIN: the Medical Center roof"}}) do
            if ImGui.Button(p[2]) then recPinOnly = p[1]; recPinsShow() end
        end
        if ImGui.Button("HIDE PINS") then recPinOnly = "none"; recPinsShow() end
        ImGui.Text("Record in this order, one recording per flight:")
        ImGui.Text("  flight_rec_1: Call 1 (hotel roof) to Call 2 (street by the water)")
        ImGui.Text("  flight_rec_2: Call 2 (street by the water) to Call 3 (Kabuki)")
        ImGui.Text("  flight_rec_3: Call 3 (Kabuki) to the Medical Center roof")
        -- 80 M ABOVE each landing spot, in the open air the sky probe
        -- measured there: on the hotel roof itself V landed inside the
        -- building and could not move, and 20 m up was still not clear of
        -- it (playtest 2026-11-03).
        ImGui.Text("Each button puts you 80 m above the spot; fly from there.")
        if ImGui.Button("GO TO Call 1, hotel roof") then teleport(-2148.7, 477.7, 175.8) end
        if ImGui.Button("GO TO Call 2, street by the water") then teleport(-2370.2, 419.2, 88.7) end
        if ImGui.Button("GO TO Call 3, Kabuki") then teleport(-1971.5, 1213.5, 88.9) end
        if ImGui.Button("GO TO the Medical Center roof") then teleport(-1362.0, 1785.0, 208.9) end
        if ImGui.Button("ALL FOUR PINS") then recPinOnly = nil; recPinsShow() end
        if not rec.on then
            if ImGui.Button("START RECORDING") then recStart() end
        else
            if ImGui.Button("STOP RECORDING") then recStop() end
        end
        ImGui.Text(rec.on and ("recording " .. rec.file) or ("files written: " .. rec.n))
    end

    if ImGui.CollapsingHeader("The AV lab (look at the AV)") then
        if ImGui.Button("ROUTE PROBE: open sky over each landing spot") then startSky() end
        if ImGui.Button("READ THE AV UNDER THE CROSSHAIR") then readAV() end
        for _, l in ipairs(labLines) do ImGui.Text(l) end
        ImGui.Separator()
        if ImGui.Button("V on player_standing (walked)") then mountV("player_standing", false) end
        ImGui.SameLine()
        if ImGui.Button("(instant)") then mountV("player_standing", true) end
        if ImGui.Button("V on seat_back_left (instant)") then mountV("seat_back_left", true) end
        if ImGui.Button("V OFF (instant)") then unmountV() end
        ImGui.Separator()
        if ImGui.Button("Thrusters on") then thrusters(true) end
        ImGui.SameLine()
        if ImGui.Button("Thrusters off") then thrusters(false) end
        if ImGui.Button("doorOpenFrontLeft") then animEvent("doorOpenFrontLeft") end
        ImGui.SameLine()
        if ImGui.Button("doorOpenBackLeft") then animEvent("doorOpenBackLeft") end
        if ImGui.Button("LIFT THE AV 10 M WITH EVERYONE ABOARD") then liftAV() end
    end

    ImGui.Separator()
    ImGui.TextWrapped("Redscript, tweaks and the archive are read at launch. A change "
        .. "to any of them needs a full quit to desktop, not a mod reload.")
    ImGui.End()
end)

-- THE SHAFT SCAN: from the console, GetMod("trauma_team_dev").scan(x0,x1,y0,y1,step,ztop,zbot).
-- Every grid cell is a ray straight down, repeated below each hit, so the file
-- has every floor in that column: "x y z z z". Rays only find what is streamed
-- near V. Appends to shaft_scan.txt.
local function shaftScan(x0, x1, y0, y1, step, ztop, zbot)
    local f = io.open("shaft_scan.txt", "a")
    if not f then return 0 end
    local n = 0
    for x = x0, x1, step do
        for y = y0, y1, step do
            local hits, z = {}, ztop
            for _ = 1, 12 do
                local h = ray({x, y, z}, {x, y, zbot})
                if not h then break end
                hits[#hits + 1] = string.format("%.1f", h.z)
                z = h.z - 0.25
                if z <= zbot then break end
            end
            f:write(string.format("%.1f %.1f %s", x, y, table.concat(hits, " ")) .. "\n")
            n = n + 1
        end
    end
    f:close()
    return n
end

-- THE WALK TEST: from the console, GetMod("trauma_team_dev").flood(x,y,z,radius,"name").
-- Spreads over the ground 1.5 m at a time from a start: a step counts if a ray at
-- waist height is clear and there is floor within 0.7 m of the same height. Writes
-- every cell reached to flood_<name>.txt as "x y z". Only sees collision near V.
local function walkFlood(x0, y0, z0, radius, name)
    local step = 1.5
    local seen = { [x0 .. "," .. y0] = true }
    local queue, head = { { x0, y0, z0 } }, 1
    local f = io.open("flood_" .. name .. ".txt", "w")
    if not f then return 0 end
    while head <= #queue and #queue < 60000 do
        local c = queue[head]
        head = head + 1
        f:write(string.format("%.1f %.1f %.2f", c[1], c[2], c[3]) .. "\n")
        for _, d in ipairs({ { step, 0 }, { -step, 0 }, { 0, step }, { 0, -step } }) do
            local nx, ny = c[1] + d[1], c[2] + d[2]
            local key = nx .. "," .. ny
            if not seen[key] and math.abs(nx - x0) < radius and math.abs(ny - y0) < radius then
                seen[key] = true
                if not ray({ c[1], c[2], c[3] + 1.0 }, { nx, ny, c[3] + 1.0 }) then
                    local h = ray({ nx, ny, c[3] + 1.0 }, { nx, ny, c[3] - 1.2 })
                    if h and math.abs(h.z - c[3]) < 0.7 then
                        queue[#queue + 1] = { nx, ny, h.z }
                    end
                end
            end
        end
    end
    f:close()
    return #queue
end

return { scan = shaftScan, flood = walkFlood }
