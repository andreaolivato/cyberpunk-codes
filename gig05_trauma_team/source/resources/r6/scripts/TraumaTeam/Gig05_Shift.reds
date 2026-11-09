module CyberpunkCodes.Gig05

public abstract class CCG05Shift {
    public static func CommunityRef() -> String { return "$/mod/cc_g05_cast/#cc_g05_cast_com"; }
    public static func ScavEntries() -> array<CName> {
        return [n"scav1", n"scav2", n"scav3", n"scav4", n"scav5"];
    }
    public static func CrewEntries() -> array<CName> {
        return [n"lead", n"soldier", n"medic"];
    }
    public static func RoofCrewEntries() -> array<CName> {
        return [n"lead_r", n"soldier_r", n"medic_r"];
    }
    public static func ClientEntry() -> CName { return n"client"; }
    public static func Ride() -> TweakDBID { return t"GameplayRestriction.cc_g05_ride"; }
    public static func PoliceLock() -> CName { return n"cc_g05_shift"; }
    // game hours
    public static func RestHours() -> Int32 { return 12; }
    // nisha
    public static func Recruiter() -> Vector4 { return new Vector4(-1335.3, 1743.9, 18.2, 1.0); }
    public static func RecruiterGap() -> Float { return 60.0; }
    public static func ClearTicks() -> Int32 { return 3; }
    // 10s
    public static func MinFightTicks() -> Int32 { return 10; }
    // 60s
    public static func NoShowTicks() -> Int32 { return 60; }
    public static func ShieldTicks() -> Int32 { return 4; }
    public static func WarpStop(i: Int32) -> Float { return i == 4 ? 90.0 : 420.0; }
    // x8
    public static func WarpSpeed() -> Float { return 8.0; }
    // 30s
    public static func WarpTicks() -> Int32 { return 120; }
    // 4 = home
    public static func Landing(i: Int32) -> Vector4 {
        // hotel roof
        if i == 1 { return new Vector4(-2148.7, 477.7, 95.8, 1.0); }
        // by the water
        if i == 2 { return new Vector4(-2370.2, 419.2, 8.7, 1.0); }
        // kabuki plaza
        if i == 3 { return new Vector4(-1971.5, 1213.5, 8.9, 1.0); }
        return new Vector4(-1082.6, 1751.1, 129.2, 1.0);
    }
    public static func LiftX() -> Float { return -1261.5; }
    public static func LiftY() -> Float { return 1769.0; }
    public static func RoofLine() -> Float { return 128.5; }
    public static func OnWayUp(pos: Vector4) -> Bool {
        return pos.X > -1325.0 && pos.X < -1255.0 && pos.Y > 1755.0 && pos.Y < 1775.0;
    }
    public static func StreetLine() -> Float { return 19.5; }
    public static func Outfit() -> TweakDBID { return t"Items.cc_g05_outfit"; }
    public static func Gun() -> TweakDBID { return t"Items.Preset_Dian_Trauma"; }
    public static func SaveLock() -> CName { return n"cc_g05_aboard"; }

    public static func Hurry(ps: ref<LiftControllerPS>, game: GameInstance) -> Void {
        let quick: ref<QuestSetLiftSpeed> = ps.ActionQuestSetLiftSpeed();
        // 32s ride
        quick.SetProperties(3.5);
        GameInstance.GetPersistencySystem(game).QueuePSEvent(ps.GetID(), ps.GetClassName(), quick);
    }

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
                    // 1 = top
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
    private persistent let m_before: ItemID;
    private persistent let m_gunSlot: Int32;
    private persistent let m_gunBefore: ItemID;
    private let m_locked: Bool;
    private let m_policeOff: Bool;
    private let m_shieldTick: Int32;
    private let m_warping: Bool;
    private let m_warpTicks: Int32;
    private let m_scavsSeen: Bool;
    private let m_helmet: ref<TraumaTeamHelmet>;
    private let m_hudWorn: Bool;
    private let m_visorOpen: Bool;
    private let m_lDown: Bool;
    private let m_lToken: Int32;
    private let m_hudLoop: Bool;
    private let m_changedKnown: Bool;
    private let m_changedWas: Int32;

    private func OnAttach() -> Void {
        this.m_fresh = true;
        this.m_comTick = -1;
        this.Schedule(6.0);
    }

    private cb func OnKey(evt: ref<KeyInputEvent>) {
        if NotEquals(evt.GetKey(), EInputKey.IK_L) {
            return;
        }
        if Equals(evt.GetAction(), EInputAction.IACT_Press) {
            if !this.m_lDown {
                this.m_lDown = true;
                this.m_lToken += 1;
                let cb: ref<CCG05VisorHold> = new CCG05VisorHold();
                cb.system = this;
                cb.token = this.m_lToken;
                GameInstance.GetDelaySystem(this.GetGameInstance()).DelayCallback(cb, 0.5, false);
            }
        } else {
            if Equals(evt.GetAction(), EInputAction.IACT_Release) {
                this.m_lDown = false;
                this.m_lToken += 1;
            }
        }
        return;
    }

    public func VisorHeld(token: Int32) -> Void {
        if !this.m_lDown || token != this.m_lToken || !this.m_hudWorn {
            return;
        }
        let game: GameInstance = this.GetGameInstance();
        let ui: ref<IBlackboard> = GameInstance.GetBlackboardSystem(game).Get(GetAllBlackboardDefs().UI_System);
        if IsDefined(ui) && ui.GetBool(GetAllBlackboardDefs().UI_System.IsInMenu) {
            return;
        }
        this.m_visorOpen = !this.m_visorOpen;
        let player: ref<PlayerPuppet> = GameInstance.GetPlayerSystem(game).GetLocalPlayerMainGameObject() as PlayerPuppet;
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        if IsDefined(player) && IsDefined(qs) {
            if !this.m_visorOpen {
                this.m_helmet.HideAll();
                this.m_hudWorn = false;
            }
            this.Helmet(game, qs, player);
        }
    }

    private let m_offDutyKnown: Bool;
    private let m_offDutyWas: Int32;
    private let m_offDutyAt: Float;

    private func ChangingBack(game: GameInstance, qs: ref<QuestsSystem>) -> Bool {
        let now: Float = EngineTime.ToFloat(GameInstance.GetSimTime(game));
        let v: Int32 = qs.GetFactStr("cc_g05_off_duty");
        if this.m_offDutyKnown && this.m_offDutyWas <= 0 && v > 0 {
            this.m_offDutyAt = now;
        }
        this.m_offDutyKnown = true;
        this.m_offDutyWas = v;
        return v > 0 && this.m_offDutyAt > 0.0 && now - this.m_offDutyAt < 3.0;
    }

    public func HelmetLoop() -> Void {
        let game: GameInstance = this.GetGameInstance();
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        let ps: ref<PlayerSystem> = GameInstance.GetPlayerSystem(game);
        if !IsDefined(qs) || !IsDefined(ps) || !IsDefined(this.m_helmet) || !this.m_hudWorn {
            this.m_hudLoop = false;
            return;
        }
        if this.ChangingBack(game, qs) {
            this.m_helmet.HideAll();
            this.m_hudWorn = false;
            this.m_visorOpen = false;
            this.m_hudLoop = false;
            return;
        }
        let player: ref<PlayerPuppet> = ps.GetLocalPlayerMainGameObject() as PlayerPuppet;
        if IsDefined(player) && !this.m_visorOpen && !this.m_helmet.IsShown() {
            this.Helmet(game, qs, player);
        }
        if IsDefined(player) {
            this.m_helmet.Poll(player);
        }
        let cb: ref<CCG05HelmetLoop> = new CCG05HelmetLoop();
        cb.system = this;
        GameInstance.GetDelaySystem(game).DelayCallback(cb, 0.25, false);
    }

    public func Schedule(delay: Float) -> Void {
        let cb: ref<CCG05ShiftTick> = new CCG05ShiftTick();
        cb.system = this;
        GameInstance.GetDelaySystem(this.GetGameInstance()).DelayCallback(cb, delay, false);
    }

    public func Tick() -> Void {
        let game: GameInstance = this.GetGameInstance();
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
        this.Helmet(game, qs, player);
        this.RoofTraffic(game, qs, player);

        if this.m_warping {
            this.Schedule(0.25);
        } else {
            if fighting || qs.GetFactStr("cc_g05_on_shift") > 0
                    || qs.GetFactStr("cc_g05_on_roof") > 0
                    || qs.GetFactStr("cc_g05_hired") > 0 && qs.GetFactStr("cc_g05_shift_done") <= 0 {
                this.Schedule(1.0);
            } else {
                // idle
                this.Schedule(3.0);
            }
        }
    }

    private func AfterLoad(qs: ref<QuestsSystem>, player: ref<PlayerPuppet>) -> Void {
        GameInstance.GetCallbackSystem().RegisterCallback(n"Input/Key", this, n"OnKey");
        qs.SetFactStr("cc_g05_warp", 0);
        if qs.GetFactStr("cc_g05_on_shift") > 0 {
            StatusEffectHelper.RemoveStatusEffect(player, CCG05Shift.Ride());
        } else {
            this.Police(true);
        }
    }

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

    private func CityScenes(qs: ref<QuestsSystem>, onShift: Bool) -> Void {
        let scenes: array<String>;
        // downtown
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
                // put back
                if qs.GetFactStr(mine) > 0 {
                    qs.SetFactStr(scenes[i], 0);
                    qs.SetFactStr(mine, 0);
                }
            }
            i += 1;
        }
    }

    private func Shift(game: GameInstance, qs: ref<QuestsSystem>, player: ref<PlayerPuppet>) -> Void {
        let onShift: Bool = qs.GetFactStr("cc_g05_on_shift") > 0;
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

        let changed: Int32 = qs.GetFactStr("cc_g05_changed");
        if this.m_changedKnown && this.m_changedWas <= 0 && changed > 0 {
            qs.SetFactStr("cc_g05_dressed", 0);
        }
        this.m_changedKnown = true;
        this.m_changedWas = changed;

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

    private func Dress(game: GameInstance, player: ref<PlayerPuppet>) -> Void {
        let ts: ref<TransactionSystem> = GameInstance.GetTransactionSystem(game);
        let eq: ref<EquipmentSystem> = this.Equipment(game);
        if !IsDefined(ts) || !IsDefined(eq) {
            return;
        }
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
        // all full
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

    private func Disarm(eq: ref<EquipmentSystem>, player: ref<PlayerPuppet>) -> Void {
        if ItemID.IsValid(this.m_gunBefore) {
            let back: ref<EquipRequest> = new EquipRequest();
            back.owner = player;
            back.slotIndex = this.m_gunSlot;
            back.itemID = this.m_gunBefore;
            eq.QueueRequest(back);
        } else {
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
        let away: ref<EquipmentSystemWeaponManipulationRequest> = new EquipmentSystemWeaponManipulationRequest();
        away.owner = player;
        away.requestType = EquipmentManipulationAction.UnequipWeapon;
        eq.QueueRequest(away);
    }

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

    private func Helmet(game: GameInstance, qs: ref<QuestsSystem>, player: ref<PlayerPuppet>) -> Void {
        if !IsDefined(this.m_helmet) {
            this.m_helmet = new TraumaTeamHelmet();
        }
        let worn: Bool = false;
        let data: ref<EquipmentSystemPlayerData> = EquipmentSystem.GetData(player);
        if IsDefined(data) && !this.ChangingBack(game, qs) {
            let on: ItemID = data.GetItemInEquipSlot(gamedataEquipmentArea.Outfit, 0);
            worn = ItemID.IsValid(on) && ItemID.GetTDBID(on) == CCG05Shift.Outfit();
        }
        if !worn {
            this.m_helmet.HideAll();
            this.m_hudWorn = false;
            this.m_visorOpen = false;
            return;
        }
        if this.m_visorOpen {
            this.m_helmet.Hide();
            this.m_helmet.ShowNote(game);
            return;
        }
        this.m_helmet.Show(player, !this.m_hudWorn);
        this.m_helmet.Update(game);
        this.m_hudWorn = true;
        if !this.m_hudLoop {
            this.m_hudLoop = true;
            let cb: ref<CCG05HelmetLoop> = new CCG05HelmetLoop();
            cb.system = this;
            GameInstance.GetDelaySystem(game).DelayCallback(cb, 0.25, false);
        }
    }

    private let m_nextFly: array<Float>;
    private let m_wasFlying: array<Bool>;

    private func RoofTraffic(game: GameInstance, qs: ref<QuestsSystem>, player: ref<PlayerPuppet>) -> Void {
        let now: Float = EngineTime.ToFloat(GameInstance.GetSimTime(game));
        if ArraySize(this.m_nextFly) < 2 {
            this.m_nextFly = [now + RandRangeF(40.0, 90.0), now + RandRangeF(70.0, 150.0)];
            this.m_wasFlying = [false, false];
        }
        let p: Vector4 = player.GetWorldPosition();
        let onRoof: Bool = p.Z > CCG05Shift.RoofLine() - 2.0 && p.X > -1396.0 && p.X < -1257.0
            && p.Y > 1739.0 && p.Y < 1826.0;
        let k: Int32 = 0;
        while k < 2 {
            let fact: String = "cc_g05_fly_x" + IntToString(k);
            let flying: Bool = qs.GetFactStr(fact) > 0;
            if this.m_wasFlying[k] && !flying {
                this.m_nextFly[k] = now + RandRangeF(60.0, 150.0);
            }
            this.m_wasFlying[k] = flying;
            if !onRoof && !flying {
                this.m_nextFly[k] = MaxF(this.m_nextFly[k], now + RandRangeF(40.0, 90.0));
            }
            if onRoof && !flying && now >= this.m_nextFly[k] {
                qs.SetFactStr(fact, 1);
                this.m_wasFlying[k] = true;
            }
            k += 1;
        }
    }

    private func AtLift(game: GameInstance, qs: ref<QuestsSystem>, player: ref<PlayerPuppet>) -> Void {
        let pos: Vector4 = player.GetWorldPosition();
        let z: Float = pos.Z;
        if qs.GetFactStr("cc_g05_hired") > 0 && qs.GetFactStr("cc_g05_on_roof") <= 0
                && z > CCG05Shift.RoofLine() && CCG05Shift.OnWayUp(pos) {
            qs.SetFactStr("cc_g05_on_roof", 1);
            let ts: ref<TransactionSystem> = GameInstance.GetTransactionSystem(game);
            if IsDefined(ts) && ItemID.IsValid(this.FindItem(ts, player, CCG05Shift.Outfit())) {
                qs.SetFactStr("cc_g05_kit", 1);
            }
        }
        if qs.GetFactStr("cc_g05_on_shift") > 0 && qs.GetFactStr("cc_g05_at_street") <= 0
                && z < CCG05Shift.StreetLine() {
            qs.SetFactStr("cc_g05_at_street", 1);
        }
        this.ClearShaft(game, player);
    }

    private let m_shaftCleared: array<EntityID>;

    private func ClearShaft(game: GameInstance, player: ref<PlayerPuppet>) -> Void {
        let axis: Vector4 = new Vector4(CCG05Shift.LiftX(), CCG05Shift.LiftY(), 0.0, 1.0);
        let at: Vector4 = player.GetWorldPosition();
        at.Z = 0.0;
        if Vector4.Distance(at, axis) > 60.0 {
            return;
        }
        let query: TargetSearchQuery = TSQ_NPC();
        query.testedSet = TargetingSet.Complete;
        query.includeSecondaryTargets = false;
        query.ignoreInstigator = true;
        query.maxDistance = 80.0;
        query.filterObjectByDistance = true;
        let parts: array<TS_TargetPartInfo>;
        GameInstance.GetTargetingSystem(game).GetTargetParts(player, query, parts);
        let i: Int32 = 0;
        while i < ArraySize(parts) {
            let car: ref<VehicleObject> = TS_TargetPartInfo.GetComponent(parts[i]).GetEntity() as VehicleObject;
            if IsDefined(car) && !ArrayContains(this.m_shaftCleared, car.GetEntityID()) {
                let p: Vector4 = car.GetWorldPosition();
                let flat: Vector4 = new Vector4(p.X, p.Y, 0.0, 1.0);
                if Vector4.Distance(flat, axis) < 4.5 && p.Z < CCG05Shift.RoofLine() - 20.0
                        && !car.IsPlayerVehicle()
                        && VehicleComponent.GetNumberOfOccupiedSlots(game, car) == 0 {
                    ArrayPush(this.m_shaftCleared, car.GetEntityID());
                    this.DisposeByName(car);
                }
            }
            i += 1;
        }
    }

    private func DisposeByName(body: ref<IScriptable>) -> Void {
        let cls: ref<ReflectionClass> = Reflection.GetClassOf(body);
        if !IsDefined(cls) {
            return;
        }
        let fn: ref<ReflectionMemberFunc> = cls.GetFunction(n"Dispose");
        if IsDefined(fn) {
            fn.Call(body);
        }
    }

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
        // flat distance
        p.Z = 0.0;
        to.Z = 0.0;
        if Vector4.Distance(p, to) < CCG05Shift.WarpStop(i) || this.m_warpTicks > CCG05Shift.WarpTicks() {
            ts.UnsetTimeDilation(n"cc_g05_warp");
            this.m_warping = false;
            qs.SetFactStr("cc_g05_warp", 0);
            qs.SetFactStr("cc_g05_warp_done", 1);
        }
    }

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
        this.Engines(avs[0], false);
        let at: EulerAngles;
        at.Pitch = 0.0;
        at.Roll = 0.0;
        at.Yaw = avs[0].GetWorldYaw();
        let tf: ref<TeleportationFacility> = GameInstance.GetTeleportationFacility(game);
        if IsDefined(tf) {
            tf.Teleport(avs[0], avs[0].GetWorldPosition(), at);
        }
    }

    private func EnginesAt(game: GameInstance, on: Bool) -> Void {
        if !this.ResolveCommunity() {
            return;
        }
        let avs: array<ref<GameObject>>;
        GetGameObjectsFromSpawnerEntityID(this.m_comId, [n"av"], game, avs);
        if ArraySize(avs) > 0 && IsDefined(avs[0]) {
            this.Engines(avs[0], on);
        }
    }

    private func Engines(av: ref<GameObject>, on: Bool) -> Void {
        if on {
            GameObject.PlaySoundEvent(av, n"q001_sc_00c_trauma_arrives_intro_av_engines_loop");
        } else {
            GameObject.PlaySoundEvent(av, n"q001_sc_00c_trauma_arrives_intro_av_engines_loop_stop");
        }
    }

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
            this.EnginesAt(game, true);
            if IsDefined(gms) {
                gms.AddGodMode(player.GetEntityID(), gameGodModeType.Invulnerable, n"cc_g05_ready");
            }
        }
        let ready: Int32 = qs.GetFactStr("cc_g05_ready");
        if ready <= 0 {
            return;
        }
        qs.SetFactStr("cc_g05_ready", 0);
        this.m_shieldTick = this.m_tick;
        // 2 = pad, no weapon
        if ready != 1 {
            return;
        }
        let eqs: ref<EquipmentSystem> = this.Equipment(game);
        if IsDefined(eqs) {
            let req: ref<EquipmentSystemWeaponManipulationRequest> = new EquipmentSystemWeaponManipulationRequest();
            req.owner = player;
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

    private func Ad(qs: ref<QuestsSystem>) -> Void {
        if qs.GetFactStr("cc_g05_ad_go") > 0 {
            return;
        }
        if qs.GetFactStr("q101_enable_side_content") <= 0 {
            return;
        }
        // before the end
        if qs.GetFactStr("q115_point_of_no_return") > 0 {
            return;
        }
        qs.SetFactStr("cc_g05_ad_go", 1);
    }

    private func Fight(game: GameInstance, qs: ref<QuestsSystem>, player: ref<PlayerPuppet>) -> Void {
        this.m_fightTicks += 1;
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

public class CCG05VisorHold extends DelayCallback {
    public let system: wref<TraumaTeamShift>;
    public let token: Int32;

    public func Call() -> Void {
        if IsDefined(this.system) {
            this.system.VisorHeld(this.token);
        }
    }
}

public class CCG05HelmetLoop extends DelayCallback {
    public let system: wref<TraumaTeamShift>;

    public func Call() -> Void {
        if IsDefined(this.system) {
            this.system.HelmetLoop();
        }
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
