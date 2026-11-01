-- Fixer [DEV]: the prototype's own CET menu.
--
-- What it is for, in the order it gets pressed:
--
--   1. MAKE HER CALL, or walk into Charter Hill with the
--      prologue done: the phone rings, she introduces herself, and her
--      contact, codex entry, map icon and card follow. Once per save; the
--      icon cannot be switched off again.
--   2. Read the counter on the map. COUNT +1 / -1 step the fact the tooltip
--      reads, so "0 / 3", "1 / 3" and so on can be looked at without a job.
--   3. THE TOOLTIP SHIM, 0 or 1. At 0 the game answers the hover on its own,
--      which is the measurement. At 1 our redscript answers instead. A fact
--      is read live, so hover, flip it, hover again.
--
-- CET Lua reloads in place, so "Reload all mods" is enough for a change to
-- this file. Everything else in this mod, redscript, tweaks and archive, is
-- read at launch and needs a full restart.

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
    print("[F01] " .. status)
end

-- THE FACTS. The comment on each says WHO sets it in a real playthrough. The
-- same table is in tools/fixer01/gen_questphase.py and the two must agree.
local FACTS = {
    { "cc_f01_in_district",   "SET BY THE GRAPH: 1 while V is inside Charter Hill, 0 outside" },
    { "cc_f01_fixer_on",      "SHE CALLS. Set by Fixer01_Intro.reds the first time V is in Charter Hill, or here. One-way" },
    { "cc_f01_intro_done",    "SET BY THE GRAPH once the call was taken: contact, codex, icon, card follow" },
    { "cc_f01_intro_time",    "SET BY THE SCRIPT (Fixer01_Stamp.reds): the world clock, in seconds, as her call ended. Her gigs count their day from it" },
    { "cc_f01_tooltip_shim",  "0: the game answers the hover itself. 1: our redscript answers" },
}

-- THE CALL'S OWN LATCHES, read only. `phonecall_*` is the game's: 0 ended,
-- 1 initializing, 2 talking, 3 rejected.
local PROBES = {
    { "cc_f01_call_video",    "1 = the studio camera was on when she rang" },
    { "cc_f01_call_rings",    "how many rings went unanswered" },
    { "cc_f01_call_claim",    "the graph's race claim; cleared before every wait" },
    { "cc_f01_call_step",     "1 = past the studio wait, camera on or timed out" },
    { "phonecall_cc_f01_fixer_with_player", "the phone's own state of her call" },
    -- HER CONVERSATION, the loop that runs after the introduction: waiting
    -- for V within 10 m of her or for V to ring her.
    { "cc_f01_talk_mode",     "0 waiting, 1 talking in person, 2 on the phone with her" },
    { "cc_f01_talk_step",     "phone route: 1 studio asked for, 2 connecting, 3 talking, 0 idle" },
    { "cc_f01_talk_claim",    "the conversation race's claim; cleared each round" },
    { "phonecall_player_with_cc_f01_fixer", "the phone's own state of V's call to her" },
    -- THE GIG UPSTAIRS, "Until Death Do Us Part", the game's own facts:
    -- her "What's new around here?" answer forks on the second one.
    { "hil_01_start",         "the game's: 1 once Wakako has given V the gig upstairs" },
    { "hil_01_finished",      "the game's: 1 once that gig is done. Her district answer changes on it" },
}

local COUNTER = "cc_f01_fixer_count"
-- THE TOTAL IS READ OFF HER RECORD, LIVE: it is whatever the installed gigs
-- registered at launch (Fixer01_Gigs.reds), not a number of the menu's.
local function total()
    local ok, v = pcall(function() return TweakDB:GetFlat("Character.cc_f01_fixer.amountOfQuests") end)
    if ok and type(v) == "number" then return v end
    return -1
end

-- WHERE HE STANDS, and a step back from him. fixer01_config.FIXER_POS.
local TELEPORTS = {
    -- HER SOFA, the Charter Hill lobby (fixer01_config.FIXER_POS, captured
    -- as spot2 on 2026-09-18). The first is the seat itself; the second is
    -- 2.5 m in front of it, past the low table, facing her.
    { "Her sofa (the Charter Hill lobby)", 3.227, 10.466, 15.657 },
    { "In front of her sofa",          1.9, 12.6, 15.3 },
    -- THE OLD KABUKI SPOT, 1.1 km away: known ground, outside her district.
    { "Far away (the old Kabuki spot)", -1126.604, 2148.006, 17.331 },
    -- GIG 04's CLAWS' VAN, 6 m behind its back doors on the road
    -- (gig04_config.VAN), to look at the spot before playing to it.
    { "Gig 04: behind the Claws' van", -1745.0, 1212.0, 18.6 },
}

local function teleport(x, y, z)
    local p = Game.GetPlayer()
    if not p then return end
    Game.GetTeleportationFacility():Teleport(
        p, Vector4.new(x, y, z, 1.0), EulerAngles.new(0, 0, 0))
    status = string.format("teleported to %.1f, %.1f, %.1f", x, y, z)
end

-- WHAT THE TOOLTIP WOULD READ, off the record, so the two halves of the
-- question can be told apart: if these three come back right and the hover
-- still shows nothing, the record is fine and the icon is not finding it.
local function recordProbe()
    local rec = "Character.cc_f01_fixer"
    local total = TweakDB:GetFlat(rec .. ".amountOfQuests")
    local fact = TweakDB:GetFlat(rec .. ".factCounterName")
    local avatar = TweakDB:GetFlat(rec .. ".tooltipAvatar")
    local name = TweakDB:GetFlat(rec .. ".fullDisplayName")
    status = string.format("record: total=%s fact=%s avatar=%s name=%s",
        tostring(total), tostring(fact), tostring(avatar), tostring(name))
    print("[F01] " .. status)
end

-- A COPY OF HER, FOR A PHOTO. The Kabuki lockup was dark, so this puts a second body
-- with her record, and so her face and clothes, two metres in front of V
-- facing him, wherever V is standing. Photo mode, then REMOVE. It is a
-- throwaway spawn (persistSpawn false), never saved, tagged so it can be
-- found again; the game's own placement of her on the sofa is untouched.
local PHOTO_TAG = "cc_f01_photo"

local function spawnPhotoCopy()
    local ok, err = pcall(function()
        local player = Game.GetPlayer()
        local p = player:GetWorldPosition()
        local yaw = player:GetWorldYaw()
        -- Two metres ahead of V. A heading of yaw faces (-sin, cos).
        local rad = math.rad(yaw)
        local x = p.x - 2.0 * math.sin(rad)
        local y = p.y + 2.0 * math.cos(rad)
        local spec = DynamicEntitySpec.new()
        spec.recordID = "Character.cc_f01_fixer"
        spec.appearanceName = "fixer01"
        spec.position = Vector4.new(x, y, p.z, 1.0)
        spec.orientation = EulerAngles.ToQuat(EulerAngles.new(0, 0, yaw + 180.0))
        spec.persistState = false
        spec.persistSpawn = false
        spec.alwaysSpawned = true
        spec.spawnInView = true
        spec.active = true
        spec.tags = { PHOTO_TAG }
        local id = Game.GetDynamicEntitySystem():CreateEntity(spec)
        status = string.format("photo copy spawned at %.1f, %.1f, %.1f facing you (id %s)", x, y, p.z, tostring(id))
        print("[F01] " .. status)
    end)
    if not ok then
        status = "photo copy failed: " .. tostring(err)
        print("[F01] " .. status)
    end
end

local function removePhotoCopies()
    local n = 0
    pcall(function()
        local des = Game.GetDynamicEntitySystem()
        local ids = des:GetTaggedIDs(PHOTO_TAG)
        for _, id in ipairs(ids) do des:DeleteEntity(id); n = n + 1 end
    end)
    status = string.format("removed %d photo cop%s", n, n == 1 and "y" or "ies")
end

-- WHY IS SHE NOT CALLING? The same conditions Fixer01_Intro.reds checks,
-- read here so a call that does not come can be explained without a log.
local function gateRows()
    local rows = {}
    local function row(ok, label, detail)
        rows[#rows + 1] = { ok = ok, label = label, detail = detail or "" }
    end
    local p = Game.GetPlayer()
    if not p then row(false, "no player yet") return rows end
    local pos = p:GetWorldPosition()
    local dx, dy = pos.x - 3.227, pos.y - 10.466
    local dist = math.sqrt(dx * dx + dy * dy)
    row(get("cc_f01_in_district") > 0, "inside Charter Hill (cc_f01_in_district, kept by the graph)", string.format("%s, %.0f m from her sofa", tostring(get("cc_f01_in_district")), dist))
    -- THE NEAREST FAST TRAVEL POINTS, read off the always-loaded sector index
    -- (tools/_anchor_cache) on 2026-09-21: the two Charter Hill dataterms
    -- closest to her sofa. Their names are LocKeys on their records, read
    -- live because the flat values are hashed on disk.
    for _, ft in ipairs({ { "wbr_hil_dataterm_03", -57.2, -49.4 }, { "wbr_hil_dataterm_02", -176.4, -82.8 } }) do
        local fdx, fdy = ft[2] - 3.227, ft[3] - 10.466
        local fname = "?"
        pcall(function()
            local key = TweakDB:GetFlat("FastTravelPoints." .. ft[1] .. ".displayName")
            if key ~= nil then fname = tostring(Game.GetLocalizedText(tostring(key))) end
        end)
        row(true, "fast travel " .. ft[1] .. " (" .. fname .. ")", string.format("%.0f m from her sofa", math.sqrt(fdx * fdx + fdy * fdy)))
    end
    row(get("q101_enable_side_content") > 0, "the prologue is over (q101_enable_side_content)", tostring(get("q101_enable_side_content")))
    row(get("q115_point_of_no_return") <= 0, "the story has not ended (q115_point_of_no_return)", tostring(get("q115_point_of_no_return")))
    local calling = false
    pcall(function() calling = Game.GetScriptableSystemsContainer():Get("PhoneSystem"):IsCallingEnabled() end)
    row(calling, "the phone can take a call", tostring(calling))
    row(get("cc_f01_fixer_on") <= 0, "she has not rung yet (cc_f01_fixer_on is 0)", tostring(get("cc_f01_fixer_on")))
    local phone = get("phonecall_cc_f01_fixer_with_player")
    row(true, "the phone's own state of her call", tostring(phone) .. "  (0 ended, 1 initializing, 2 talking, 3 rejected)")
    row(true, "studio camera on when she rang (cc_f01_call_video)", tostring(get("cc_f01_call_video")))
    row(true, "rings unanswered (cc_f01_call_rings)", tostring(get("cc_f01_call_rings")))
    return rows
end

-- DUMP A CHARACTER RECORD. Every value a fixer's record carries, read off
-- the running game (the values are hashed on disk and unreadable there),
-- appended to fixer01_dev.log in this folder. Dino, Regina, the civilian
-- hers is based on, and hers, so the diff says what makes a fixer scan as
-- one and stand unkillable. The 97 names are Character.dyno's, read off the
-- TweakDB string table on 2026-09-18.
local RECORD_FLATS = {
    "EquipmentAreas", "abilities", "actionMap", "additionalDescription", "affiliation", "alertedSensesPreset",
    "alternativeDisplayName", "alternativeFullDisplayName", "amountOfQuests", "appearanceName", "archetypeData", "archetypeName",
    "attachmentSlots", "audioMeleeMaterial", "audioResourceName", "baseAttitudeGroup", "bossHealthBarThresholds", "bountyDrawTable",
    "canHaveGenericTalk", "characterType", "combatSensesPreset", "communitySquad", "contentAssignment", "cpoCharacterBuild",
    "cpoClassName", "crowdAppearanceNames", "crowdMemberSettings", "defaultCrosshair", "defaultEquipment", "despawnChildCommunityWhenPlayerInVehicle",
    "devNotes", "disableDefeatedState", "displayDescription", "displayName", "driving", "dropsAmmoOnDeathChance",
    "dropsControlledLoot", "dropsMoneyOnDeath", "dropsWeaponOnDeath", "effectors", "enableSensesOnStart", "entityTemplatePath",
    "factCounterName", "forceCanHaveGenericTalk", "forcedTBHZOffset", "fullDisplayName", "genders", "globalSquad",
    "hasDirectionalStarts", "hideUIDetection", "hideUIElements", "holocallInitializerPath", "idleActions", "ignoreDetectionForAudioCue",
    "isBumpable", "isChild", "isCrowd", "isLightCrowd", "itemGroups", "items",
    "lootBagEntity", "lootDrop", "lootInjectionParams", "minigameInstance", "multiplayerTemplatePaths", "objectActions",
    "onSpawnGLPs", "persistentName", "primaryEquipment", "priority", "quest", "rarity",
    "reactionPreset", "relaxedSensesPreset", "savable", "scannerModulePreset", "secondaryEquipment", "securitySquad",
    "sensePreset", "skipDisplayArchetype", "squadParamsID", "statModifierGroups", "statModifiers", "statPools",
    "stateMachineName", "staticCommunityAppearancesDistributionEnabled", "tags", "threatTrackingPreset", "thresholds", "tooltipAvatar",
    "uiNameplate", "useForcedTBHZOffset", "vendorID", "visualTags", "voiceTag", "weakspots",
    "weaponSlot"
}

local function flatToString(v)
    if type(v) == "table" then
        local parts = {}
        for _, x in ipairs(v) do parts[#parts + 1] = tostring(x) end
        return "[" .. table.concat(parts, ", ") .. "]"
    end
    return tostring(v)
end

local function dumpRecord(record)
    local f = io.open("fixer01_dev.log", "a")
    if not f then status = "cannot open fixer01_dev.log" return end
    f:write(string.format("== %s  (%s)\n", record, os.date("%Y-%m-%d %H:%M:%S")))
    local n = 0
    for _, name in ipairs(RECORD_FLATS) do
        local ok, v = pcall(function() return TweakDB:GetFlat(record .. "." .. name) end)
        if ok and v ~= nil then
            f:write(string.format("  %-44s %s\n", name, flatToString(v)))
            n = n + 1
        end
    end
    f:write("\n")
    f:close()
    status = string.format("dumped %d values of %s to fixer01_dev.log", n, record)
    print("[F01] " .. status)
end

local function dumpAll()
    for _, r in ipairs({ "Character.dyno", "Character.reggie", "Character.SlackerFemale", "Character.cc_f01_fixer" }) do
        dumpRecord(r)
    end
end

-- THE POSE RIG. An entity of the mod's with no mesh and one workspot component
-- per candidate sitting workspot in the game (tools/fixer01/gen_poses.py
-- writes it; the table below is printed by the same script). Spawned once at
-- her seat with the yaw and nudges set here, and a pose is played on her
-- through the game's own workspot system, which takes a DEVICE entity and the
-- name of a workspot component on it. Look at her, press a pose. Between
-- poses she is released from the rig first. The numbers that look right go
-- into fixer01_config.FIXER_POS and FIXER_WORKSPOT; nothing here is saved.
--
-- The call is the one Appearance Menu Mod's pose tab makes against its own
-- entity (`PlayInDeviceSimple(device, actor, false, component, ...)`,
-- slideBehaviour 1); this file makes it against ours, with nothing of AMM's.
local POSE_RIG_ENT = "mod\\fixer01\\dev\\poses.ent"
local POSES = {
    { "couch_01", "generic__sit_couch__sit_around__01", false },
    { "couch_02", "generic__sit_couch__sit_around__02", false },
    { "couch_03_arms_crossed", "generic__sit_couch__sit_around__03", false },
    { "couch_tv_arms_crossed", "generic__sit_couch_tv__watch__01", false },
    { "couch_tablet", "generic__sit_couch_tablet__read__01", true },
    { "couch_champagne", "generic__sit_couch_lean_back_champagne__drink__01", true },
    { "couch_bottle", "generic__sit_couch_lean_back_bottle__drink__01", true },
    { "couch_gun_relax", "big__sit_couch_lean_back_gun__relax__01", true },
    { "chair_01", "generic__sit_chair__sit_around__01", false },
    { "chair_02", "generic__sit_chair__sit_around__02", false },
    { "chair_03", "generic__sit_chair__sit_around__03", false },
    { "chair_04", "generic__sit_chair__sit_around__04", false },
    { "chair_05", "generic__sit_chair__sit_around__05", false },
    { "chair_06", "generic__sit_chair__sit_around__06", false },
    { "chair_07", "generic__sit_chair__sit_around__07", false },
    { "chair_back_01", "generic__sit_chair_lean_back__sit_around__01", false },
    { "chair_back_02", "generic__sit_chair_lean_back__sit_around__02", false },
    { "chair_back_03", "generic__sit_chair_lean_back__sit_around__03", false },
    { "chair_back_04", "generic__sit_chair_lean_back__sit_around__04", false },
    { "chair_back_think", "generic__sit_chair_lean_back__think__01", false },
    { "chair_back_observe", "generic__sit_chair_lean_back__observe__01", false },
    { "chair_back_nails", "generic__sit_chair_lean_back__look_at_nails__01", false },
    { "chair_back_knife", "generic__sit_chair_lean_back_knife__sit_around__01", true },
    { "chair_back_gun", "generic__sit_chair_lean_back_gun__show_off__01", true },
    { "chair_back_smoke", "generic__sit_chair_lean_back_cigarette__smoke__01", true },
    { "chair_front_01", "generic__sit_chair_lean_front__sit_around__01", false },
    { "chair_front_02", "generic__sit_chair_lean_front__sit_around__02", false },
    { "chair_front_think_01", "generic__sit_chair_lean_front__think__01", false },
    { "chair_front_think_02", "generic__sit_chair_lean_front__think__02", false },
    { "chair_front_nervous", "generic__sit_chair_lean_front__nervous__01", false },
    { "chair_front_smoke", "generic__sit_chair_lean_front__smoke__01", true },
    { "chair_front_glass", "generic__sit_chair_lean_front_glass__drink__01", true },
    { "chair_phone_talk", "generic__sit_chair_cellphone__talk__01", true },
    { "chair_phone_check", "generic__sit_chair_cellphone__check__01", true },
    { "chair_tablet", "generic__sit_chair_tablet__read__01", true },
    { "chair_female_back", "female__sit_chair_lean_back__sit_around__01", false },
    { "chair_female_backrest", "female__sit_chair_backrest__sit_around__01", false },
    { "chair_big_back_01", "big__sit_chair_lean_back__sit_around__01", false },
    { "chair_big_back_02", "big__sit_chair_lean_back__sit_around__02", false },
    { "chair_backwards", "generic__sit_chair_lean0__2h_on_backrest__01", false },
    { "table_feet_up", "generic__sit_chair_table_lean_back__feet_up__01", false },
    { "bench_back_01", "generic__sit_bench_lean_back__sit_around__01", false },
    { "bench_back_02", "generic__sit_bench_lean_back__sit_around__02", false },
    { "bench_back_hand", "generic__sit_bench_lean_back_l_hand_on_back__talk__01", false },
}
local pose = {
    rigId = nil,
    rigYaw = 32.0,        -- fixer01_config.FIXER_POS yaw
    dx = 0.0, dy = 0.0, dz = 0.0,
    spawnedYaw = nil, spawnedDx = nil, spawnedDy = nil, spawnedDz = nil,
    current = "(none)",
    last = "nothing done yet",
}
local SEAT = { x = 3.227, y = 10.466, z = 15.294 }   -- fixer01_config.FIXER_POS

local function poseRig()
    if pose.rigId == nil then return nil end
    local ent = nil
    pcall(function() ent = Game.FindEntityByID(pose.rigId) end)
    return ent
end

local function despawnRig()
    if pose.rigId == nil then return end
    pcall(function() exEntitySpawner.Despawn(Game.FindEntityByID(pose.rigId)) end)
    pose.rigId = nil
end

local function spawnRig()
    despawnRig()
    local ok, err = pcall(function()
        local t = WorldTransform.new()
        t:SetPosition(Vector4.new(SEAT.x + pose.dx, SEAT.y + pose.dy, SEAT.z + pose.dz, 1.0))
        t:SetOrientationEuler(EulerAngles.new(0, 0, pose.rigYaw))
        pose.rigId = exEntitySpawner.Spawn(POSE_RIG_ENT, t, "")
        pose.spawnedYaw, pose.spawnedDx, pose.spawnedDy, pose.spawnedDz = pose.rigYaw, pose.dx, pose.dy, pose.dz
    end)
    if not ok then
        pose.last = "rig spawn failed: " .. tostring(err)
        print("[F01] " .. pose.last)
    end
end

local function rigIsStale()
    return pose.rigId == nil or pose.spawnedYaw ~= pose.rigYaw or pose.spawnedDx ~= pose.dx
        or pose.spawnedDy ~= pose.dy or pose.spawnedDz ~= pose.dz
end

-- Her body: the NPC under the crosshair (cc_capture's route). Look at her.
local function lookedAtNpc()
    local pl = Game.GetPlayer()
    local ts = Game.GetTargetingSystem()
    local obj = nil
    pcall(function() obj = ts:GetObjectClosestToCrosshair(pl, EulerAngles.new(0, 0, 0), TSQ_NPC()) end)
    if obj == nil then pcall(function() obj = ts:GetLookAtObject(pl, true, true) end) end
    return obj
end

local function releasePose()
    local npc = lookedAtNpc()
    if npc == nil then pose.last = "look at her first" return end
    pcall(function() Game.GetWorkspotSystem():StopInDevice(npc) end)
    pose.current = "(released)"
    pose.last = "released her from the rig"
end

local function playPose(comp)
    local npc = lookedAtNpc()
    if npc == nil then pose.last = "look at her first" print("[F01] " .. pose.last) return end
    if rigIsStale() then spawnRig() end
    -- The rig takes a moment to exist after the spawn call; try on the next
    -- frames until it does.
    local tries = 0
    local function attempt()
        local rig = poseRig()
        if rig == nil then
            tries = tries + 1
            if tries < 60 then
                return false
            end
            pose.last = "the rig never appeared (is the archive deployed and the game restarted?)"
            print("[F01] " .. pose.last)
            return true
        end
        local ok, err = pcall(function()
            local ws = Game.GetWorkspotSystem()
            ws:StopInDevice(npc)
            ws:PlayInDeviceSimple(rig, npc, false, CName.new(comp), CName.new("None"), nil, 0, 1, nil)
        end)
        if ok then
            pose.current = comp
            pose.last = string.format("playing %s at yaw %.0f, nudge %.2f %.2f %.2f", comp, pose.rigYaw, pose.dx, pose.dy, pose.dz)
        else
            pose.last = "play failed: " .. tostring(err)
        end
        print("[F01] " .. pose.last)
        return true
    end
    if not attempt() then
        pose.pending = attempt
    end
end

registerForEvent("onUpdate", function()
    if pose.pending ~= nil then
        if pose.pending() then pose.pending = nil end
    end
end)

registerForEvent("onOverlayOpen", function() visible = true end)
registerForEvent("onOverlayClose", function() visible = false end)

registerForEvent("onDraw", function()
    if not visible then return end
    ImGui.SetNextWindowSize(560, 480, ImGuiCond.FirstUseEver)
    if not ImGui.Begin("Fixer 01 [DEV]") then ImGui.End() return end

    ImGui.Text(status)
    ImGui.Separator()

    if ImGui.Button("MAKE HER CALL") then set("cc_f01_fixer_on", 1) end
    ImGui.SameLine()
    ImGui.TextDisabled("the phone rings within seconds; take it. She calls on her own the first time V is in Charter Hill")

    ImGui.Text(string.format("counter: %d / %d   (the total is what the installed gigs registered; -1 = unreadable)", get(COUNTER), total()))
    ImGui.SameLine()
    if ImGui.SmallButton("+1") then set(COUNTER, get(COUNTER) + 1) end
    ImGui.SameLine()
    if ImGui.SmallButton("-1") then set(COUNTER, math.max(0, get(COUNTER) - 1)) end
    ImGui.SameLine()
    if ImGui.SmallButton("0") then set(COUNTER, 0) end
    ImGui.TextDisabled("     the fact the map tooltip reads. Open the map and hover the hands icon")

    local shim = get("cc_f01_tooltip_shim") > 0
    if ImGui.Button(shim and "TOOLTIP SHIM: ON (our script answers)" or "TOOLTIP SHIM: OFF (the game answers)") then
        set("cc_f01_tooltip_shim", shim and 0 or 1)
    end
    ImGui.TextDisabled("     hover with it OFF first. That is the measurement. Then ON, to check the fallback")

    if ImGui.Button("SPAWN A COPY OF HER HERE, FOR A PHOTO") then spawnPhotoCopy() end
    ImGui.SameLine()
    if ImGui.Button("REMOVE THE COPY") then removePhotoCopies() end
    ImGui.TextDisabled("     stand somewhere bright, press, she appears 2 m ahead facing you; photo mode; then remove")

    if ImGui.Button("DUMP THE FIXER RECORDS TO A FILE") then dumpAll() end
    ImGui.SameLine()
    ImGui.TextDisabled("Dino, Regina, her base and her, every value, into fixer01_dev.log")

    if ImGui.Button("READ THE RECORD") then recordProbe() end
    ImGui.SameLine()
    ImGui.TextDisabled("the five fixer values off Character.cc_f01_fixer")

    if ImGui.CollapsingHeader("Why is she not calling?") then
        for _, r in ipairs(gateRows()) do
            ImGui.Text((r.ok and "  OK   " or " NO    ") .. r.label)
            if r.detail ~= "" then ImGui.TextDisabled("         " .. r.detail) end
        end
        ImGui.TextWrapped("The trigger checks 24 s after a load, then every 20 s far away and every 5 s near. "
            .. "If every line is OK and the phone stays quiet, press MAKE HER CALL: that skips the trigger and rings.")
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
        ImGui.Separator()
        -- Pretends the gig upstairs is done, to hear her second answer on a
        -- save that has not played it. IT IS THE GAME'S OWN FACT: the gig's
        -- top phase waits on it to run its cleanup, so on this save the gig
        -- can no longer be played. Test, then reload without saving.
        if ImGui.Button("PRETEND THE GIG UPSTAIRS IS DONE (hil_01_finished = 1; do not save afterwards)") then
            set("hil_01_finished", 1)
        end
    end

    if ImGui.CollapsingHeader("Poses (look at her, then press one)") then
        ImGui.TextWrapped("Plays a sitting workspot on the NPC under the crosshair, at her seat. The yaw and the nudges move the seat the pose is played at; the numbers that look right go into the config. Props (a tablet, a glass, a knife) may or may not appear: that is part of the test.")
        pose.rigYaw = ImGui.SliderFloat("yaw", pose.rigYaw, -180.0, 180.0, "%.0f")
        pose.dx = ImGui.SliderFloat("nudge x", pose.dx, -1.0, 1.0, "%.2f")
        pose.dy = ImGui.SliderFloat("nudge y", pose.dy, -1.0, 1.0, "%.2f")
        pose.dz = ImGui.SliderFloat("nudge z", pose.dz, -0.5, 0.5, "%.2f")
        if ImGui.Button("REPLAY CURRENT WITH THESE NUMBERS") and pose.current ~= "(none)" and pose.current ~= "(released)" then
            playPose(pose.current)
        end
        ImGui.SameLine()
        if ImGui.Button("RELEASE HER") then releasePose() end
        ImGui.Text("current: " .. pose.current)
        ImGui.TextWrapped(pose.last)
        ImGui.Separator()
        for _, row in ipairs(POSES) do
            local label = row[1] .. (row[3] and "  [prop]" or "")
            if ImGui.Button(label) then playPose(row[1]) end
            ImGui.SameLine()
            ImGui.TextDisabled(row[2])
        end
    end

    if ImGui.CollapsingHeader("Teleports") then
        for _, t in ipairs(TELEPORTS) do
            if ImGui.Button(t[1]) then teleport(t[2], t[3], t[4]) end
        end
    end

    -- THE ROOM OF HER FIRST GIG, read only. Where V stands in the room's own
    -- frame (x across the door, y from the door line into the room, z above
    -- the floor), and what Gig04_Places.reds has done so far. Diagnosis, not
    -- a control: the gig ships no menu of its own.
    if ImGui.CollapsingHeader("Gig 04 room, read only") then
        local pl = Game.GetPlayer()
        if pl then
            local p = pl:GetWorldPosition()
            local dx, dy = p.x - (-1429.882), p.y - 1536.773
            local a = math.rad(-5.0)
            local fx, fy = -math.sin(a), math.cos(a)
            local ux, uy = fy, -fx
            local vx, vy = -fx, -fy
            ImGui.Text(string.format("room x %.2f  y %.2f  z %.2f   (y < 0 is the street side of the door line)",
                dx * ux + dy * uy, dx * vx + dy * vy, p.z - 18.193))
            -- IS THERE A NAVIGATION MESH UNDER V. An NPC walks the mesh and
            -- nothing else; a hand-built room has none unless the game baked
            -- one here. The game's own query, within 1 m of V.
            local nav = "navmesh under V: (query failed)"
            pcall(function()
                local r = Game.GetNavigationSystem():FindPointInSphereOnlyHumanNavmesh(
                    p, 1.0, Enum.new("NavGenAgentSize", "Human"), false)
                if r ~= nil then
                    local ok = tostring(r.status)
                    nav = string.format("navmesh under V: %s  (point %.2f, %.2f, %.2f)", ok, r.point.x, r.point.y, r.point.z)
                end
            end)
            ImGui.Text(nav)
            -- THE SAME QUERY ON THE STREET, 6 m in front of the door, as the
            -- control: if this one fails too, the query is wrong, not the room.
            local street = "navmesh on the street (6 m before the door): (query failed)"
            pcall(function()
                local sx = -1429.882 + ux * 0.0 + vx * -6.0
                local sy = 1536.773 + uy * 0.0 + vy * -6.0
                local r = Game.GetNavigationSystem():FindPointInSphereOnlyHumanNavmesh(
                    Vector4.new(sx, sy, 18.193, 1.0), 1.0, Enum.new("NavGenAgentSize", "Human"), false)
                if r ~= nil then
                    street = string.format("navmesh on the street (6 m before the door): %s", tostring(r.status))
                end
            end)
            ImGui.Text(street)
            -- THE SAME QUERY WITHIN 3 M OF V, point printed. Three readings
            -- tell three stories: a point at the room's floor height is the
            -- gig's own mesh; a point 0.5 to 1.5 m under the floor is the
            -- game's slab under the building, so the gig's file was not
            -- loaded; nothing within 3 m inside the room means the gig's
            -- file loaded and its tiles were refused.
            local wide = "navmesh within 3 m of V: (query failed)"
            pcall(function()
                local r = Game.GetNavigationSystem():FindPointInSphereOnlyHumanNavmesh(
                    p, 3.0, Enum.new("NavGenAgentSize", "Human"), false)
                if r ~= nil then
                    wide = string.format("navmesh within 3 m of V: %s  (point %.2f, %.2f, %.2f)",
                        tostring(r.status), r.point.x, r.point.y, r.point.z)
                end
            end)
            ImGui.Text(wide)
            -- THE PAVEMENT 1 M BEFORE THE DOOR is in a tile the gig rebuilds
            -- (the street 6 m out is in one it does not). OK here with no mesh
            -- in the room means the gig's tiles loaded but the room's part of
            -- them is wrong; failed here means the tiles were refused whole.
            local step = "navmesh 1 m before the door (the gig's own tile): (query failed)"
            pcall(function()
                local sx = -1429.882 + vx * -1.0
                local sy = 1536.773 + vy * -1.0
                local r = Game.GetNavigationSystem():FindPointInSphereOnlyHumanNavmesh(
                    Vector4.new(sx, sy, 18.193, 1.0), 1.0, Enum.new("NavGenAgentSize", "Human"), false)
                if r ~= nil then
                    step = string.format("navmesh 1 m before the door (the gig's own tile): %s  (point %.2f, %.2f, %.2f)",
                        tostring(r.status), r.point.x, r.point.y, r.point.z)
                end
            end)
            ImGui.Text(step)
        end
        -- DO RUN-TIME OBSTACLES BEND A PATH. Stand on open street with 10 m
        -- clear ahead, press once: the path from V to 8 m ahead is measured,
        -- a row of five columns is put across it 4 m ahead, and the path is
        -- measured again. A longer second path means obstacles carve the
        -- mesh and the room's fence can work where a mesh exists; the same
        -- length means they do not.
        if ImGui.Button("TEST: do obstacles bend a path (stand on open street)") then
            pcall(function()
                local pl = Game.GetPlayer()
                local p = pl:GetWorldPosition()
                local fwd = pl:GetWorldForward()
                local nav = Game.GetNavigationSystem()
                local agent = Enum.new("NavGenAgentSize", "Human")
                -- BOTH ENDS SNAPPED ONTO THE MESH: the first run aimed 8 m
                -- straight ahead into the building and found no mesh there.
                local s = nav:FindPointInSphereOnlyHumanNavmesh(p, 2.0, agent, false)
                local g = nav:FindPointInSphereOnlyHumanNavmesh(
                    Vector4.new(p.x + fwd.x * 8.0, p.y + fwd.y * 8.0, p.z, 1.0), 4.0, agent, false)
                if tostring(s.status) ~= "worldNavigationRequestStatus : OK (0)"
                    or tostring(g.status) ~= "worldNavigationRequestStatus : OK (0)" then
                    gig04PathTest = string.format("no mesh at an end: start %s, goal 8 m ahead %s. Face along open street and press again.",
                        tostring(s.status), tostring(g.status))
                    return
                end
                p = s.point
                local goal = g.point
                local before = nav:CalculatePathOnlyHumanNavmesh(p, goal, agent, 1.0)
                local len1 = before and before:CalculateLength() or -1
                local n1 = before and #before.path or -1
                gig04Obstacles = gig04Obstacles or {}
                local rx, ry = -fwd.y, fwd.x
                for i = -2, 2 do
                    local ox = p.x + fwd.x * 4.0 + rx * i * 1.2
                    local oy = p.y + fwd.y * 4.0 + ry * i * 1.2
                    local o = nav:AddObstacle(Vector4.new(ox, oy, p.z, 1.0), 0.9, 4.0, agent)
                    if o then table.insert(gig04Obstacles, o) end
                end
                local after = nav:CalculatePathOnlyHumanNavmesh(p, goal, agent, 1.0)
                local len2 = after and after:CalculateLength() or -1
                local n2 = after and #after.path or -1
                gig04PathTest = string.format("path before: %.2f m (%d points)   after the fence: %.2f m (%d points)   obstacles kept: %d",
                    len1, n1, len2, n2, #gig04Obstacles)
                print("[F01] " .. gig04PathTest)
            end)
        end
        if gig04PathTest then ImGui.Text(gig04PathTest) end
        -- THE NO-POLICE TAG on the three civilians' records, read back off
        -- TweakDB: TweakXL's `!append-once` was used on a CName list here
        -- for the first time (audit 2026-10-02).
        for _, rec in ipairs({ "cc_g04_stamps", "cc_g04_ligaya", "cc_g04_bayani" }) do
            local ok, tags = pcall(function() return TweakDB:GetFlat("Character." .. rec .. ".tags") end)
            local found = false
            if ok and tags then
                for _, t in ipairs(tags) do
                    if Game.NameToString(t) == "DoNotTriggerPrevention" then found = true end
                end
            end
            ImGui.Text(rec .. " no-police tag: " .. (found and "yes" or "NO"))
        end
        for _, f in ipairs({ "cc_g04_dbg_ligaya_here", "cc_g04_dbg_calm", "cc_g04_dbg_tier",
                             "cc_f01_talk_mode", "cc_g04_fixer_free", "cc_g04_offer_armed", "cc_g04_near_offer", "cc_g04_dbg_need", "cc_g04_dbg_body", "cc_g04_dbg_int",
                             "cc_g04_booth_on", "cc_g04_booth_heard", "cc_g04_stamps_hit", "cc_g04_stamps_fight", "cc_g04_stamps_down",
                             "cc_g04_shard_got", "cc_g04_shard_read", "cc_g04_flop_armed", "cc_g04_van_near",
                             "cc_g04_clue_blood", "cc_g04_clue_cuffs", "cc_g04_clue_bag",
                             "cc_g04_shard2_got", "cc_g04_shard2_read", "cc_g04_ep1",
                             "cc_g04_oa_armed", "cc_g04_dbg_oa_seen", "cc_g04_dbg_oa_hunting",
                             "cc_g04_dbg_oa_down", "cc_g04_dbg_oa_stray", "cc_g04_dbg_oa_strays",
                             "cc_g04_oa_clear", "cc_g04_room_off",
                             "cc_g04_dbg_stamps_mode", "cc_g04_stamps_talked",
                             "cc_g04_room_armed", "cc_g04_dbg_claws_turned", "cc_g04_dbg_claws_standing", "cc_g04_claws_clear",
                             "cc_g04_dbg_shielded", "cc_g04_room_done", "cc_g04_dbg_roused", "cc_g04_dbg_sent",
                             "cc_g04_dbg_door", "cc_g04_dbg_cell_door", "cc_g04_bayani_gone",
                             "cc_g04_dbg_gone_dist", "cc_g04_dbg_lost" }) do
            ImGui.Text(string.format("%d  %s", get(f), f))
        end
    end

    ImGui.Separator()
    ImGui.TextWrapped("Redscript, tweaks and the archive are read at launch. A change "
        .. "to any of them needs a full quit to desktop, not a mod reload.")
    ImGui.End()
end)
