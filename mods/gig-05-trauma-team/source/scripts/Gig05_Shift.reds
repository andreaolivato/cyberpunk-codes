// Trauma Team: what the quest graph cannot do by itself on a shift.
//
//   the ad      `cc_g05_ad_go` once, wherever V is, after the prologue
//               and before the end.
//   the fight   while `cc_g05_fight_on`: the Scavs, the crew and the client
//               are found by entry name and set against each other with the
//               four calls the game's MaxTac drop makes on each unit
//               (backlog 47; Gig03_Alarm.reds), aimed at the crew and the
//               client as well as V. Only the lead fights; the soldier and
//               the medic keep their poses. `cc_g05_site_clear` when no Scav
//               is left standing. The police are off for the whole shift.
//   the pay     not here: the quest graph hands over each call's reward
//               record and the kit with the game's own reward node
//               (gen_questphase.py), so the game draws its own notices.
//   the shift   at the shelves: the uniform into V's backpack if it is not
//               there, and on V (the Outfit slot). The clock is noted at
//               boarding. `cc_g05_off_duty`, changing back after the shift:
//               the uniform off and what V wore before back on. At the pad,
//   saving      locked while V is aboard (`cc_g05_aboard`), the way the
//               game's own Autodrive locks it while the car drives itself
//               (autoDriveSystem.swift, SaveLocksManager). On the ground,
//               between flights, V can save.
//   a load      a save made during a shift loads with the ride restriction
//               off: the graph applies it, but a load drops nothing it
//               applied, and the clone is unsavable only on paper until
//               measured (docs/gameplay-restrictions.md).
//
// THE QUEST NODES DO THE REST: who is hostile to whom as groups
// (source/tweaks/characters.yaml, gen_questphase), who shoots at whom first
// (the Heywood fight's combat-target nodes), the client held at 1 percent.
// This file puts on top what a community body arrives without: its senses
// (gotcha 77) and a quarrel with the people it is meant to fight (gotcha 74).
//
// EVERYTHING A SESSION NEEDS IS RE-READ FROM FACTS, never kept in a field
// across a load (gotcha 21). The one exception is what V wore and carried before
// the shift: an item is not a number, so those are persistent fields.

module CyberpunkCodes.Gig05

public abstract class CCG05Shift {
    // tools/gig05/gen_community.py prints it; the two must agree.
    public static func CommunityRef() -> String { return "$/mod/cc_g05_cast/#cc_g05_cast_com"; }
    public static func ScavEntries() -> array<CName> {
        return [n"scav1", n"scav2", n"scav3", n"scav4", n"scav5"];
    }
    public static func CrewEntries() -> array<CName> {
        return [n"lead", n"soldier", n"medic"];
    }
    // THE ROOF CREW: the same three, a second set of bodies on their posts,
    // on while the AV is down on the roof (gen_community.py, ROOF_CREW).
    public static func RoofCrewEntries() -> array<CName> {
        return [n"lead_r", n"soldier_r", n"medic_r"];
    }
    public static func ClientEntry() -> CName { return n"client"; }
    public static func Ride() -> TweakDBID { return t"GameplayRestriction.cc_g05_ride"; }
    public static func PoliceLock() -> CName { return n"cc_g05_shift"; }
    // Game hours between one shift's end and the recruiter's return.
    public static func RestHours() -> Int32 { return 12; }
    // SHE COMES BACK ONLY WITH V THIS FAR AWAY, so she does not appear in plain
    // sight. gig05_config.py, RECRUITER.
    public static func Recruiter() -> Vector4 { return new Vector4(-1335.3, 1743.9, 18.2, 1.0); }
    public static func RecruiterGap() -> Float { return 60.0; }
    // No Scav standing for this many ticks in a row, after at least this many
    // ticks of fight, is a clear roof. A body still streaming in reads as
    // none, so one empty tick proves nothing.
    public static func ClearTicks() -> Int32 { return 3; }
    public static func MinFightTicks() -> Int32 { return 10; }
    // A CALL WHERE NO SCAV EVER APPEARED counts as clear after this long, so a call
    // that failed to stream cannot hold the shift for good.
    public static func NoShowTicks() -> Int32 { return 60; }
    public static func ShieldTicks() -> Int32 { return 4; }
    // THE FOUR LANDINGS, gig05_config.py's. A skip stops this far short of one.
    // THE FLIGHT HOME loops round the pad, so its stop is a point on the path about
    // 300 m from the end of it, not a distance from the pad. Playtest 2026-11-04:
    // 420 m from the pad left over a kilometre of flying.
    public static func WarpStop(i: Int32) -> Float { return i == 4 ? 90.0 : 420.0; }
    public static func WarpSpeed() -> Float { return 8.0; }
    // THE SKIP ENDS ANYWAY after this many quarter-second ticks: the longest flight
    // is about 12 s at WarpSpeed. A stop missed would leave the screen black.
    public static func WarpTicks() -> Int32 { return 120; }
    public static func Landing(i: Int32) -> Vector4 {
        if i == 1 { return new Vector4(-2148.7, 477.7, 95.8, 1.0); }
        if i == 2 { return new Vector4(-2370.2, 419.2, 8.7, 1.0); }
        if i == 3 { return new Vector4(-1971.5, 1213.5, 8.9, 1.0); }
        return new Vector4(-1082.6, 1751.1, 129.2, 1.0);
    }
    public static func LiftX() -> Float { return -1261.5; }
    public static func LiftY() -> Float { return 1769.0; }
    public static func RoofLine() -> Float { return 128.5; }
    // THE WAY UP counts only here: the car, the walkway and the locker room.
    public static func OnWayUp(pos: Vector4) -> Bool {
        return pos.X > -1325.0 && pos.X < -1255.0 && pos.Y > 1755.0 && pos.Y < 1775.0;
    }
    public static func StreetLine() -> Float { return 19.5; }
    public static func Outfit() -> TweakDBID { return t"Items.Trauma_Team_Outfit"; }
    public static func Gun() -> TweakDBID { return t"Items.Preset_Dian_Trauma"; }
    public static func SaveLock() -> CName { return n"cc_g05_aboard"; }

    // THE KEYPAD OF THE GIG'S LIFT. It has two stops, so a press sends the car to the
    // other one. The screen's own buttons hold their action by weak reference, and with
    // V back in the car after stepping out the lower one no longer reached the lift
    // (2026-11-04, a watch on LiftControllerPS.OnGoToFloor). Only this lift, found by
    // where it stands: gig05_config.py, LIFT_XY.
    // THE RIDE IS 111 m. At the template's 2.5 m/s it took 44 s; at this speed, 32 s.
    // Sent before every move, since the lift's own setting comes from the
    // template (the design call, 2026-11-06).
    public static func Hurry(ps: ref<LiftControllerPS>, game: GameInstance) -> Void {
        let quick: ref<QuestSetLiftSpeed> = ps.ActionQuestSetLiftSpeed();
        quick.SetProperties(3.5);
        GameInstance.GetPersistencySystem(game).QueuePSEvent(ps.GetID(), ps.GetClassName(), quick);
    }

    // A CALL PANEL brings the car to its own stop. The game's own call did nothing on
    // this lift, so the press goes straight to the lift (gotcha 162).
    public static func CallPanelPress(owner: wref<GameObject>) -> Bool {
        let panel: ref<ElevatorFloorTerminal> = owner as ElevatorFloorTerminal;
        if !IsDefined(panel) {
            return false;
        }
        let at: Vector4 = panel.GetWorldPosition();
        if AbsF(at.X - CCG05Shift.LiftX()) > 10.0 || AbsF(at.Y - CCG05Shift.LiftY()) > 10.0 {
            return false;
        }
        let parents: array<ref<DeviceComponentPS>>;
        let panelPS: ref<ElevatorFloorTerminalControllerPS> = panel.GetDevicePS();
        if !IsDefined(panelPS) {
            return false;
        }
        panelPS.GetParents(parents);
        let i: Int32 = 0;
        while i < ArraySize(parents) {
            let ps: ref<LiftControllerPS> = parents[i] as LiftControllerPS;
            if IsDefined(ps) {
                if !ps.IsMoving() {
                    CCG05Shift.Hurry(ps, panel.GetGame());
                    let move: ref<QuestGoToFloor> = ps.ActionQuestGoToFloor();
                    move.SetProperties(at.Z > 100.0 ? 1 : 0);
                    GameInstance.GetPersistencySystem(panel.GetGame()).QueuePSEvent(ps.GetID(), ps.GetClassName(), move);
                }
                return true;
            }
            i += 1;
        }
        return false;
    }

    public static func KeypadPress(owner: wref<GameObject>) -> Bool {
        let lift: ref<LiftDevice> = owner as LiftDevice;
        if !IsDefined(lift) {
            return CCG05Shift.CallPanelPress(owner);
        }
        let at: Vector4 = lift.GetWorldPosition();
        if AbsF(at.X - CCG05Shift.LiftX()) > 1.0 || AbsF(at.Y - CCG05Shift.LiftY()) > 1.0 {
            return false;
        }
        let ps: ref<LiftControllerPS> = lift.GetDevicePS();
        if IsDefined(ps) && !ps.IsMoving() {
            CCG05Shift.Hurry(ps, lift.GetGame());
            let move: ref<QuestGoToFloor> = ps.ActionQuestGoToFloor();
            move.SetProperties(ps.GetActiveFloor() == 0 ? 1 : 0);
            GameInstance.GetPersistencySystem(lift.GetGame()).QueuePSEvent(ps.GetID(), ps.GetClassName(), move);
        }
        return true;
    }
}

public class TraumaTeamShift extends ScriptableSystem {

    private let m_fresh: Bool;
    private let m_tick: Int32;
    private let m_fightTicks: Int32;
    private let m_emptyTicks: Int32;
    private let m_comTick: Int32;
    private let m_comOk: Bool;
    private let m_comId: EntityID;
    // THE OUTFIT V WORE BEFORE THE SHIFT, put back after it, the weapon slot the
    // team's SMG went into (0 to 2), and what it put aside there. Saved with the
    // game: a save taken in uniform still changes back to the right clothes.
    private persistent let m_before: ItemID;
    private persistent let m_gunSlot: Int32;
    private persistent let m_gunBefore: ItemID;
    private let m_locked: Bool;
    private let m_policeOff: Bool;
    private let m_shieldTick: Int32;
    private let m_warping: Bool;
    private let m_warpTicks: Int32;
    private let m_scavsSeen: Bool;

    private func OnAttach() -> Void {
        this.m_fresh = true;
        this.m_comTick = -1;
        this.Schedule(6.0);
    }

    public func Schedule(delay: Float) -> Void {
        let cb: ref<CCG05ShiftTick> = new CCG05ShiftTick();
        cb.system = this;
        GameInstance.GetDelaySystem(this.GetGameInstance()).DelayCallback(cb, delay, false);
    }

    public func Tick() -> Void {
        let game: GameInstance = this.GetGameInstance();
        // EVERY SYSTEM FETCH IS CHECKED BEFORE IT IS USED. This attaches at
        // the main menu, where there is no player and no quest system.
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        let ps: ref<PlayerSystem> = GameInstance.GetPlayerSystem(game);
        if !IsDefined(qs) || !IsDefined(ps) {
            this.Schedule(6.0);
            return;
        }
        let player: ref<PlayerPuppet> = ps.GetLocalPlayerMainGameObject() as PlayerPuppet;
        if !IsDefined(player) {
            this.Schedule(6.0);
            return;
        }
        this.m_tick += 1;

        if this.m_fresh {
            this.m_fresh = false;
            this.AfterLoad(qs, player);
        }
        this.Ad(qs);
        let fighting: Bool = qs.GetFactStr("cc_g05_fight_on") > 0;
        if fighting {
            this.Fight(game, qs, player);
        } else {
            this.m_fightTicks = 0;
            this.m_emptyTicks = 0;
            this.m_scavsSeen = false;
        }
        this.Shift(game, qs, player);
        this.Park(game, qs);
        this.Regroup(game, qs);
        this.Ready(game, qs, player);
        this.DevDownScavs(game, qs);
        this.Warp(game, qs, player);
        this.AtLift(game, qs, player);
        this.NextShift(game, qs, player);

        if this.m_warping {
            this.Schedule(0.25);
        } else {
            if fighting || qs.GetFactStr("cc_g05_on_shift") > 0
                    || qs.GetFactStr("cc_g05_on_roof") > 0
                    || qs.GetFactStr("cc_g05_hired") > 0 && qs.GetFactStr("cc_g05_shift_done") <= 0 {
                this.Schedule(1.0);
            } else {
                this.Schedule(3.0);
            }
        }
    }

    // ---------------------------------------------------------------- a load
    private func AfterLoad(qs: ref<QuestsSystem>, player: ref<PlayerPuppet>) -> Void {
        qs.SetFactStr("cc_g05_warp", 0);
        if qs.GetFactStr("cc_g05_on_shift") > 0 {
            StatusEffectHelper.RemoveStatusEffect(player, CCG05Shift.Ride());
        } else {
            // A lock left by a shift the save was taken in the middle of.
            this.Police(true);
        }
    }

    // THE POLICE OFF FOR THE SHIFT, the request quests send to keep the NCPD
    // out of a scripted fight (preventionSystem.swift, a named lock on the
    // system; it stays off while any lock is held). Playtest 2026-11-03: at
    // the street call V had heat, with no shot fired by V, and the NCPD and a
    // nearby Trauma Team squad turned on V; in combat the boarding prompt
    // never showed.
    private func Police(on: Bool) -> Void {
        let req: ref<TogglePreventionSystem> = new TogglePreventionSystem();
        req.sourceName = CCG05Shift.PoliceLock();
        req.isActive = on;
        let ps: ref<PreventionSystem> = GameInstance.GetScriptableSystemsContainer(this.GetGameInstance()).Get(n"PreventionSystem") as PreventionSystem;
        if IsDefined(ps) {
            ps.QueueRequest(req);
        }
        this.m_policeOff = !on;
    }

    // THE GAME'S OWN TRAUMA TEAM SCENE OFF FOR THE SHIFT. Call 2 stands on a spot of
    // the city scene `cs_trauma_team_intervention`, run by Downtown's phase whatever the
    // map says (the spot's NodeRef), and playtest 2026-11-05 met a second AV and crew
    // there. The scene waits on `cs_cct_dtn_intervention_disabled` above 0 while it
    // runs. The game sets that fact itself as well, so `cc_g05_scene_off_N` records
    // which ones this gig set, and only those are put back.
    private func CityScenes(qs: ref<QuestsSystem>, onShift: Bool) -> Void {
        let scenes: array<String>;
        ArrayPush(scenes, "cs_cct_dtn_intervention_disabled");
        let i: Int32 = 0;
        while i < ArraySize(scenes) {
            let mine: String = "cc_g05_scene_off_" + IntToString(i);
            if onShift {
                if qs.GetFactStr(scenes[i]) <= 0 {
                    qs.SetFactStr(scenes[i], 1);
                    qs.SetFactStr(mine, 1);
                }
            } else {
                if qs.GetFactStr(mine) > 0 {
                    qs.SetFactStr(scenes[i], 0);
                    qs.SetFactStr(mine, 0);
                }
            }
            i += 1;
        }
    }

    // ------------------------------------------------------------- the shift
    private func Shift(game: GameInstance, qs: ref<QuestsSystem>, player: ref<PlayerPuppet>) -> Void {
        let onShift: Bool = qs.GetFactStr("cc_g05_on_shift") > 0;
        // SAVING, locked aboard and only aboard.
        let aboard: Bool = qs.GetFactStr("cc_g05_aboard") > 0;
        if aboard && !this.m_locked {
            SaveLocksManager.RequestSaveLockAdd(game, CCG05Shift.SaveLock());
            this.m_locked = true;
        } else {
            if !aboard && this.m_locked {
                SaveLocksManager.RequestSaveLockRemove(game, CCG05Shift.SaveLock());
                this.m_locked = false;
            }
        }

        if onShift && !this.m_policeOff {
            this.Police(false);
        } else {
            if !onShift && this.m_policeOff {
                this.Police(true);
            }
        }

        this.CityScenes(qs, onShift);

        // THE UNIFORM GOES ON AS IT ARRIVES (`cc_g05_suit_up`, set with the kit).
        // Playtest 2026-11-03: the item card showed the uniform and V stood there
        // without it. `cc_g05_off_duty` is the change back at the shelves after the
        // shift: off it all comes. Left there, the uniform stays on V.
        let wear: Bool = qs.GetFactStr("cc_g05_off_duty") <= 0
            && (onShift || qs.GetFactStr("cc_g05_suit_up") > 0);
        if wear && qs.GetFactStr("cc_g05_dressed") <= 0 {
            qs.SetFactStr("cc_g05_dressed", 1);
            this.Dress(game, player);
        }

        if !wear && qs.GetFactStr("cc_g05_dressed") > 0 {
            qs.SetFactStr("cc_g05_dressed", 0);
            this.Undress(game, player);
        }
    }

    private func Equipment(game: GameInstance) -> ref<EquipmentSystem> {
        return GameInstance.GetScriptableSystemsContainer(game).Get(n"EquipmentSystem") as EquipmentSystem;
    }

    // THE UNIFORM ON: into the backpack if missing (Career Opportunities may
    // have given it already), then onto the Outfit slot, the request the
    // game's own scene stash uses (invisibleSceneStash.swift).
    private func Dress(game: GameInstance, player: ref<PlayerPuppet>) -> Void {
        let ts: ref<TransactionSystem> = GameInstance.GetTransactionSystem(game);
        let eq: ref<EquipmentSystem> = this.Equipment(game);
        if !IsDefined(ts) || !IsDefined(eq) {
            return;
        }
        // THE COPY V HOLDS, found by record: `HasItem` on a bare record id
        // misses an item the quest gave, and a second copy was handed over
        // (2026-11-04, the item list after a shift).
        let outfit: ItemID = this.FindItem(ts, player, CCG05Shift.Outfit());
        if !ItemID.IsValid(outfit) {
            ts.GiveItem(player, ItemID.FromTDBID(CCG05Shift.Outfit()), 1);
            outfit = this.FindItem(ts, player, CCG05Shift.Outfit());
        }
        let data: ref<EquipmentSystemPlayerData> = EquipmentSystem.GetData(player);
        if IsDefined(data) {
            this.m_before = data.GetItemInEquipSlot(gamedataEquipmentArea.Outfit, 0);
        }
        let req: ref<EquipRequest> = new EquipRequest();
        req.owner = player;
        req.slotIndex = 0;
        req.itemID = outfit;
        eq.QueueRequest(req);
        this.Arm(ts, eq, data, player);
    }

    // THE TEAM'S SMG IN A WEAPON SLOT, so the step-off draws it. Playtest
    // 2026-11-03: given by the kit, it stayed in the backpack and V stepped
    // off with V's own gun. The first empty slot, or the first slot with
    // its weapon put aside until the shift ends.
    private func Arm(ts: ref<TransactionSystem>, eq: ref<EquipmentSystem>,
                     data: ref<EquipmentSystemPlayerData>, player: ref<PlayerPuppet>) -> Void {
        if !IsDefined(data) {
            return;
        }
        let gun: ItemID = this.FindItem(ts, player, CCG05Shift.Gun());
        if !ItemID.IsValid(gun) {
            ts.GiveItem(player, ItemID.FromTDBID(CCG05Shift.Gun()), 1);
            gun = this.FindItem(ts, player, CCG05Shift.Gun());
        }
        if !ItemID.IsValid(gun) {
            return;
        }
        let i: Int32 = 0;
        while i < 3 {
            if data.GetItemInEquipSlot(gamedataEquipmentArea.Weapon, i) == gun {
                this.m_gunSlot = i;
                this.m_gunBefore = ItemID.None();
                return;
            }
            i += 1;
        }
        let slot: Int32 = -1;
        i = 0;
        while i < 3 && slot < 0 {
            if !ItemID.IsValid(data.GetItemInEquipSlot(gamedataEquipmentArea.Weapon, i)) {
                slot = i;
            }
            i += 1;
        }
        this.m_gunBefore = ItemID.None();
        if slot < 0 {
            slot = 0;
            this.m_gunBefore = data.GetItemInEquipSlot(gamedataEquipmentArea.Weapon, 0);
        }
        this.m_gunSlot = slot;
        let req: ref<EquipRequest> = new EquipRequest();
        req.owner = player;
        req.slotIndex = slot;
        req.itemID = gun;
        eq.QueueRequest(req);
    }

    private func FindItem(ts: ref<TransactionSystem>, player: ref<PlayerPuppet>, record: TweakDBID) -> ItemID {
        let items: array<wref<gameItemData>>;
        if ts.GetItemList(player, items) {
            for item in items {
                if IsDefined(item) && ItemID.GetTDBID(item.GetID()) == record {
                    return item.GetID();
                }
            }
        }
        return ItemID.None();
    }

    private func GunSlot(player: ref<PlayerPuppet>) -> Int32 {
        let data: ref<EquipmentSystemPlayerData> = EquipmentSystem.GetData(player);
        if !IsDefined(data) {
            return 0;
        }
        let i: Int32 = 0;
        while i < 3 {
            if ItemID.GetTDBID(data.GetItemInEquipSlot(gamedataEquipmentArea.Weapon, i)) == CCG05Shift.Gun() {
                return i;
            }
            i += 1;
        }
        return 0;
    }

    // V's own weapon back in the slot the SMG borrowed.
    private func Disarm(eq: ref<EquipmentSystem>, player: ref<PlayerPuppet>) -> Void {
        if ItemID.IsValid(this.m_gunBefore) {
            let back: ref<EquipRequest> = new EquipRequest();
            back.owner = player;
            back.slotIndex = this.m_gunSlot;
            back.itemID = this.m_gunBefore;
            eq.QueueRequest(back);
        } else {
            // A SLOT THAT WAS EMPTY GOES BACK TO EMPTY, if the SMG is still in it.
            let slot: Int32 = this.GunSlot(player);
            let data: ref<EquipmentSystemPlayerData> = EquipmentSystem.GetData(player);
            if IsDefined(data) && ItemID.GetTDBID(data.GetItemInEquipSlot(gamedataEquipmentArea.Weapon, slot)) == CCG05Shift.Gun() {
                let off: ref<UnequipRequest> = new UnequipRequest();
                off.owner = player;
                off.slotIndex = slot;
                off.areaType = gamedataEquipmentArea.Weapon;
                eq.QueueRequest(off);
            }
        }
        this.m_gunBefore = ItemID.None();
        // HANDS EMPTY ON THE STREET: the weapon put back in the slot was
        // drawn as it went in (playtest 2026-11-04, a katana out at the kerb).
        let away: ref<EquipmentSystemWeaponManipulationRequest> = new EquipmentSystemWeaponManipulationRequest();
        away.owner = player;
        away.requestType = EquipmentManipulationAction.UnequipWeapon;
        eq.QueueRequest(away);
    }

    // THE UNIFORM OFF, and V's own outfit back if V wore one.
    private func Undress(game: GameInstance, player: ref<PlayerPuppet>) -> Void {
        let eq: ref<EquipmentSystem> = this.Equipment(game);
        if !IsDefined(eq) {
            return;
        }
        if ItemID.IsValid(this.m_before) && ItemID.GetTDBID(this.m_before) != CCG05Shift.Outfit() {
            let back: ref<EquipRequest> = new EquipRequest();
            back.owner = player;
            back.slotIndex = 0;
            back.itemID = this.m_before;
            eq.QueueRequest(back);
        } else {
            let off: ref<UnequipRequest> = new UnequipRequest();
            off.owner = player;
            off.slotIndex = 0;
            off.areaType = gamedataEquipmentArea.Outfit;
            eq.QueueRequest(off);
        }
        this.m_before = ItemID.None();
        this.Disarm(eq, player);
    }

    // WHERE THE LIFT HAS TAKEN V. The quest waits on these two: V rides the
    // game's lift with its own keypad, so nothing tells the quest but the height.
    private func AtLift(game: GameInstance, qs: ref<QuestsSystem>, player: ref<PlayerPuppet>) -> Void {
        let pos: Vector4 = player.GetWorldPosition();
        let z: Float = pos.Z;
        if qs.GetFactStr("cc_g05_hired") > 0 && qs.GetFactStr("cc_g05_on_roof") <= 0
                && z > CCG05Shift.RoofLine() && CCG05Shift.OnWayUp(pos) {
            qs.SetFactStr("cc_g05_on_roof", 1);
            // CAREER OPPORTUNITIES MAY HAVE GIVEN THE UNIFORM: no second copy, and no
            // card for what V already has.
            let ts: ref<TransactionSystem> = GameInstance.GetTransactionSystem(game);
            if IsDefined(ts) && ItemID.IsValid(this.FindItem(ts, player, CCG05Shift.Outfit())) {
                qs.SetFactStr("cc_g05_kit", 1);
            }
        }
        if qs.GetFactStr("cc_g05_on_shift") > 0 && qs.GetFactStr("cc_g05_at_street") <= 0
                && z < CCG05Shift.StreetLine() {
            qs.SetFactStr("cc_g05_at_street", 1);
        }
    }

    // THE NEXT SHIFT, RestHours after the last one ended. `cc_g05_rest_start` is
    // the quest saying a shift has just ended. A save finished on 1.0.0 never
    // had it, so `cc_g05_rest_from` is 0 there and its V is posted at once.
    private func NextShift(game: GameInstance, qs: ref<QuestsSystem>, player: ref<PlayerPuppet>) -> Void {
        if qs.GetFactStr("cc_g05_shift_done") <= qs.GetFactStr("cc_g05_posted")
                || qs.GetFactStr("cc_g05_next_shift") > 0
                || qs.GetFactStr("q115_point_of_no_return") > 0 {
            return;
        }
        let ts: ref<TimeSystem> = GameInstance.GetTimeSystem(game);
        if !IsDefined(ts) {
            return;
        }
        let hour: Int32 = Cast<Int32>(ts.GetGameTimeStamp() / 3600.0);
        if qs.GetFactStr("cc_g05_rest_start") > 0 {
            qs.SetFactStr("cc_g05_rest_start", 0);
            qs.SetFactStr("cc_g05_rest_from", hour);
            return;
        }
        let began: Int32 = qs.GetFactStr("cc_g05_rest_from");
        if began > 0 && hour - began < CCG05Shift.RestHours() {
            return;
        }
        if Vector4.Distance(player.GetWorldPosition(), CCG05Shift.Recruiter()) < CCG05Shift.RecruiterGap() {
            return;
        }
        qs.SetFactStr("cc_g05_rest_from", 0);
        qs.SetFactStr("cc_g05_next_shift", 1);
    }

    // THE SKIP: `cc_g05_warp` is the flight (1 to 4), set by the quest under a
    // fade. The world runs at WarpSpeed until V is WarpStop from that flight's
    // landing, then `cc_g05_warp_done`. Not kept across a load: a load clears
    // the dilation, and AfterLoad clears the fact.
    private func Warp(game: GameInstance, qs: ref<QuestsSystem>, player: ref<PlayerPuppet>) -> Void {
        let i: Int32 = qs.GetFactStr("cc_g05_warp");
        if i <= 0 {
            return;
        }
        let ts: ref<TimeSystem> = GameInstance.GetTimeSystem(game);
        if !IsDefined(ts) {
            return;
        }
        if !this.m_warping {
            this.m_warping = true;
            this.m_warpTicks = 0;
            ts.SetTimeDilation(n"cc_g05_warp", CCG05Shift.WarpSpeed());
        }
        this.m_warpTicks += 1;
        let p: Vector4 = player.GetWorldPosition();
        let to: Vector4 = CCG05Shift.Landing(i);
        p.Z = 0.0;
        to.Z = 0.0;
        if Vector4.Distance(p, to) < CCG05Shift.WarpStop(i) || this.m_warpTicks > CCG05Shift.WarpTicks() {
            ts.UnsetTimeDilation(n"cc_g05_warp");
            this.m_warping = false;
            qs.SetFactStr("cc_g05_warp", 0);
            qs.SetFactStr("cc_g05_warp_done", 1);
        }
    }

    // THE AV LEVELLED WHERE IT LANDED. `cc_g05_park` is set by the quest
    // as a flight ends: the AV is put back on its own spot, flat, facing the
    // way it faces, and the fact is cleared. Playtest 2026-11-03: off the
    // flight home the AV stood on the deck tipped about 40 degrees. A run in
    // which the AV had been moved by accident stood level after the move.
    private func Park(game: GameInstance, qs: ref<QuestsSystem>) -> Void {
        if qs.GetFactStr("cc_g05_park") <= 0 || !this.ResolveCommunity() {
            return;
        }
        qs.SetFactStr("cc_g05_park", 0);
        let avs: array<ref<GameObject>>;
        GetGameObjectsFromSpawnerEntityID(this.m_comId, [n"av"], game, avs);
        if ArraySize(avs) == 0 || !IsDefined(avs[0]) {
            return;
        }
        let at: EulerAngles;
        at.Pitch = 0.0;
        at.Roll = 0.0;
        at.Yaw = avs[0].GetWorldYaw();
        let tf: ref<TeleportationFacility> = GameInstance.GetTeleportationFacility(game);
        if IsDefined(tf) {
            tf.Teleport(avs[0], avs[0].GetWorldPosition(), at);
        }
    }

    // V STEPS OFF READY. `cc_g05_shield` 1 from the quest as the AV comes
    // down: V cannot be hurt from then. `cc_g05_ready` 1 as V is let go: the
    // game's own request draws the team's SMG from its slot (Arm),
    // and the shield lasts ShieldTicks more while V finds cover. Playtest
    // 2026-11-03: V was shot before the step-off had finished, and then,
    // with the shield from the step-off, already hurt on touchdown.
    private func Ready(game: GameInstance, qs: ref<QuestsSystem>, player: ref<PlayerPuppet>) -> Void {
        let gms: ref<GodModeSystem> = GameInstance.GetGodModeSystem(game);
        if this.m_shieldTick > 0 && this.m_tick - this.m_shieldTick >= CCG05Shift.ShieldTicks() {
            this.m_shieldTick = 0;
            if IsDefined(gms) {
                gms.RemoveGodMode(player.GetEntityID(), gameGodModeType.Invulnerable, n"cc_g05_ready");
            }
        }
        if qs.GetFactStr("cc_g05_shield") == 1 {
            qs.SetFactStr("cc_g05_shield", 0);
            if IsDefined(gms) {
                gms.AddGodMode(player.GetEntityID(), gameGodModeType.Invulnerable, n"cc_g05_ready");
            }
        }
        // 2 at the pad after the last flight: the shield ends, no weapon.
        let ready: Int32 = qs.GetFactStr("cc_g05_ready");
        if ready <= 0 {
            return;
        }
        qs.SetFactStr("cc_g05_ready", 0);
        this.m_shieldTick = this.m_tick;
        if ready != 1 {
            return;
        }
        let eqs: ref<EquipmentSystem> = this.Equipment(game);
        if IsDefined(eqs) {
            let req: ref<EquipmentSystemWeaponManipulationRequest> = new EquipmentSystemWeaponManipulationRequest();
            req.owner = player;
            // The team's SMG, in whichever slot it is in now (a load
            // forgets the field).
            let slot: Int32 = this.GunSlot(player);
            if slot == 1 {
                req.requestType = EquipmentManipulationAction.RequestWeaponSlot2;
            } else {
                if slot == 2 {
                    req.requestType = EquipmentManipulationAction.RequestWeaponSlot3;
                } else {
                    req.requestType = EquipmentManipulationAction.RequestWeaponSlot1;
                }
            }
            eqs.QueueRequest(req);
        }
    }

    // THE LEAD WALKS BACK TO THE AV once the call is clear, before the
    // boarding swaps the men on the ground for the men who ride (playtest
    // 2026-11-03: the crew vanished from the roof and stood in the cabin).
    // The game's own move order, aimed at the AV itself, walking.
    // `cc_g05_regroup` 1 from the quest; 2 once sent.
    private func Regroup(game: GameInstance, qs: ref<QuestsSystem>) -> Void {
        if qs.GetFactStr("cc_g05_regroup") != 1 || !this.ResolveCommunity() {
            return;
        }
        qs.SetFactStr("cc_g05_regroup", 2);
        let avs: array<ref<GameObject>>;
        GetGameObjectsFromSpawnerEntityID(this.m_comId, [n"av"], game, avs);
        let lead: ref<ScriptedPuppet> = this.FindInCommunity(game, CCG05Shift.RoofCrewEntries()[0]);
        if ArraySize(avs) == 0 || !IsDefined(avs[0]) || !IsDefined(lead) {
            return;
        }
        let target: AIPositionSpec;
        AIPositionSpec.SetEntity(target, avs[0]);
        let cmd: ref<AIMoveToCommand> = new AIMoveToCommand();
        cmd.movementTarget = target;
        cmd.movementType = moveMovementType.Walk;
        cmd.desiredDistanceFromTarget = 3.5;
        cmd.finishWhenDestinationReached = true;
        AIComponent.SendCommand(lead, cmd);
    }

    // FOR TESTING ONLY: `cc_g05_dev_down` (the dev menu) kills every Scav
    // still standing, the game's own ForceKill, so the rest of a shift can be
    // played without winning the fight. Cleared as it is used.
    private func DevDownScavs(game: GameInstance, qs: ref<QuestsSystem>) -> Void {
        if qs.GetFactStr("cc_g05_dev_down") <= 0 {
            return;
        }
        qs.SetFactStr("cc_g05_dev_down", 0);
        let scavs: array<CName> = CCG05Shift.ScavEntries();
        let i: Int32 = 0;
        while i < ArraySize(scavs) {
            let s: ref<ScriptedPuppet> = this.FindInCommunity(game, scavs[i]);
            if IsDefined(s) && ScriptedPuppet.IsAlive(s) {
                StatusEffectHelper.ApplyStatusEffect(s, t"BaseStatusEffect.ForceKill");
            }
            i += 1;
        }
    }

    // ---------------------------------------------------------------- the ad
    private func Ad(qs: ref<QuestsSystem>) -> Void {
        if qs.GetFactStr("cc_g05_ad_go") > 0 {
            return;
        }
        // The game's own two facts for "after the prologue" and "before the
        // end" (docs/architecture.md, "The two base-game facts").
        if qs.GetFactStr("q101_enable_side_content") <= 0 {
            return;
        }
        if qs.GetFactStr("q115_point_of_no_return") > 0 {
            return;
        }
        // ANYWHERE IN THE CITY (the design call, 2026-11-03): within 1.5 km
        // of the Medical Center, a V who never went back to Watson never
        // heard of the job.
        qs.SetFactStr("cc_g05_ad_go", 1);
    }

    // ------------------------------------------------------------- the fight
    private func Fight(game: GameInstance, qs: ref<QuestsSystem>, player: ref<PlayerPuppet>) -> Void {
        this.m_fightTicks += 1;
        // THE ONE WHO FIGHTS, the lead, free to roam. The soldier stands
        // guard at the AV with a rifle and the medic kneels at the client;
        // both stay out of it (the design call, 2026-11-03; their records
        // are in a group the gang has no quarrel with). Playtest 2026-11-03:
        // a fighting soldier told to hold his ground (`AIHoldPositionCommand`,
        // the police roadblock's order) still walked 15 m in 45 s.
        let crew: array<ref<ScriptedPuppet>>;
        let names: array<CName> = CCG05Shift.RoofCrewEntries();
        let i: Int32 = 0;
        let lead: ref<ScriptedPuppet> = this.FindInCommunity(game, names[0]);
        if IsDefined(lead) && ScriptedPuppet.IsAlive(lead) {
            ArrayPush(crew, lead);
        }
        let client: ref<ScriptedPuppet> = this.FindInCommunity(game, CCG05Shift.ClientEntry());

        let standing: Int32 = 0;
        let scavs: array<CName> = CCG05Shift.ScavEntries();
        i = 0;
        while i < ArraySize(scavs) {
            let scav: ref<ScriptedPuppet> = this.FindInCommunity(game, scavs[i]);
            if IsDefined(scav) && ScriptedPuppet.IsAlive(scav) && !ScriptedPuppet.IsDefeated(scav) {
                standing += 1;
                this.m_scavsSeen = true;
                this.Wake(scav, player);
                let j: Int32 = 0;
                while j < ArraySize(crew) {
                    this.Quarrel(scav, crew[j]);
                    j += 1;
                }
                if IsDefined(client) && ScriptedPuppet.IsAlive(client) {
                    this.Quarrel(scav, client);
                }
            }
            i += 1;
        }

        if standing == 0 {
            this.m_emptyTicks += 1;
        } else {
            this.m_emptyTicks = 0;
        }
        let due: Int32 = this.m_scavsSeen ? CCG05Shift.MinFightTicks() : CCG05Shift.NoShowTicks();
        if this.m_emptyTicks >= CCG05Shift.ClearTicks() && this.m_fightTicks >= due
                && qs.GetFactStr("cc_g05_site_clear") <= 0 {
            qs.SetFactStr("cc_g05_site_clear", 1);
        }
    }

    // THE FOUR CALLS, on a Scav, aimed at V (Gig03_Alarm.reds).
    private func Wake(npc: ref<ScriptedPuppet>, player: ref<PlayerPuppet>) -> Void {
        let agent: ref<AttitudeAgent> = npc.GetAttitudeAgent();
        if IsDefined(agent) {
            agent.SetAttitudeTowards(player.GetAttitudeAgent(), EAIAttitude.AIA_Hostile);
        }
        let senses: ref<SenseComponent> = npc.GetSensesComponent();
        if IsDefined(senses) {
            senses.Toggle(true);
        }
        TargetTrackingExtension.InjectThreat(npc, player, 1.0, -1.0);
        NPCPuppet.ChangeHighLevelState(npc, gamedataNPCHighLevelState.Combat);
    }

    // THE SAME, BOTH WAYS, between a Scav and one of ours. Pairwise, never
    // `SetAttitudeGroup(n"hostile")`, which once set guards on their own
    // colleagues (backlog 22). Both directions are set because which one the
    // engine reads for a given decision is not written down (gotcha 78).
    private func Quarrel(scav: ref<ScriptedPuppet>, other: ref<ScriptedPuppet>) -> Void {
        let a: ref<AttitudeAgent> = scav.GetAttitudeAgent();
        let b: ref<AttitudeAgent> = other.GetAttitudeAgent();
        if IsDefined(a) && IsDefined(b) {
            a.SetAttitudeTowards(b, EAIAttitude.AIA_Hostile);
            b.SetAttitudeTowards(a, EAIAttitude.AIA_Hostile);
        }
        let senses: ref<SenseComponent> = other.GetSensesComponent();
        if IsDefined(senses) {
            senses.Toggle(true);
        }
        TargetTrackingExtension.InjectThreat(scav, other, 1.0, -1.0);
        TargetTrackingExtension.InjectThreat(other, scav, 1.0, -1.0);
        NPCPuppet.ChangeHighLevelState(other, gamedataNPCHighLevelState.Combat);
    }

    // THE COMMUNITY'S ID, resolved once a tick.
    private func ResolveCommunity() -> Bool {
        if this.m_comTick != this.m_tick {
            let nref: NodeRef = CreateNodeRef(CCG05Shift.CommunityRef());
            let root: GlobalNodeRef;
            let g: GlobalNodeRef = ResolveNodeRef(nref, root);
            this.m_comOk = GlobalNodeRef.IsDefined(g);
            this.m_comId = Cast<EntityID>(g);
            this.m_comTick = this.m_tick;
        }
        return this.m_comOk;
    }

    // A body of the community by entry name: alive if there is one, else
    // the first dead one, else null. Gig 04's FindInCommunity
    // (Gig04_Places.reds).
    private func FindInCommunity(game: GameInstance, entry: CName) -> ref<ScriptedPuppet> {
        let dead: ref<ScriptedPuppet>;
        if !this.ResolveCommunity() {
            return null;
        }
        let objects: array<ref<GameObject>>;
        GetGameObjectsFromSpawnerEntityID(this.m_comId, [entry], game, objects);
        let i: Int32 = 0;
        while i < ArraySize(objects) {
            let puppet: ref<ScriptedPuppet> = objects[i] as ScriptedPuppet;
            if IsDefined(puppet) {
                if ScriptedPuppet.IsAlive(puppet) {
                    return puppet;
                }
                if !IsDefined(dead) {
                    dead = puppet;
                }
            }
            i += 1;
        }
        return dead;
    }
}

public class CCG05ShiftTick extends DelayCallback {
    public let system: wref<TraumaTeamShift>;

    public func Call() -> Void {
        if IsDefined(this.system) {
            this.system.Tick();
        }
    }
}

@wrapMethod(DeviceInkGameControllerBase)
protected cb func OnDeviceActionCallback(e: ref<inkPointerEvent>) -> Bool {
    if e.IsAction(n"click") && CCG05Shift.KeypadPress(this.GetOwnerEntity() as GameObject) {
        return true;
    }
    return wrappedMethod(e);
}

@wrapMethod(DeviceInkGameControllerBase)
protected cb func OnExecuteButtonAction(widget: wref<inkWidget>) -> Bool {
    if CCG05Shift.KeypadPress(this.GetOwnerEntity() as GameObject) {
        return true;
    }
    return wrappedMethod(widget);
}
