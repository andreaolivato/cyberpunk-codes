module CyberpunkCodes.Gig04
import CyberpunkCodes.Shared.Gig04.*

public abstract class CCG04Places {
    public static func CommunityRef() -> String { return "$/mod/cc_g04_cast/#cc_g04_cast_com"; }
    public static func StampsEntry() -> CName { return n"stamps"; }
    public static func ClawEntries() -> array<CName> {
        return [n"claw1", n"claw2", n"claw3"];
    }
    // shop door
    public static func Door() -> Vector4 { return new Vector4(-1429.882, 1536.773, 18.193, 1.0); }
    // stream range
    public static func ArmRadius() -> Float { return 60.0; }
    public static func VanEntry() -> CName { return n"van"; }
    public static func Van() -> Vector4 { return new Vector4(-1740.0, 1213.0, 18.22, 1.0); }
    public static func VanNear() -> Float { return 20.0; }
    public static func HoldRecord() -> TweakDBID { return t"GameplayRestriction.cc_g04_hold"; }
    // 30s max
    public static func HoldCapTicks() -> Int32 { return 30; }
    public static func OAEntries(ep1: Bool) -> array<CName> {
        if ep1 {
            // phantom liberty
            return [n"oa1", n"oa2", n"oa3"];
        }
        // base game
        return [n"sec1", n"sec2", n"sec3"];
    }
    // 3s
    public static func OAGoneTicks() -> Int32 { return 3; }
    // 90s at the door
    public static func OAFloor() -> Int32 { return 90; }
    // 15s
    public static func OAStrayTicks() -> Int32 { return 15; }
    // 5s
    public static func OAGoInTicks() -> Int32 { return 5; }
    public static func StampsHeatRange() -> Float { return 40.0; }
    // metres
    public static func StampsCalmFrom() -> Float { return 100.0; }
    public static func CarEntry() -> CName { return n"oacar1"; }
    // waiting spot
    public static func RailPose() -> Vector4 { return new Vector4(-1477.823, 1548.843, 18.18, 1.0); }
    public static func RoomU() -> Vector4 { return new Vector4(0.9961947, -0.0871557, 0.0, 0.0); }
    public static func RoomV() -> Vector4 { return new Vector4(-0.0871557, -0.9961947, 0.0, 0.0); }
    public static func Stall() -> Vector4 { return new Vector4(-1236.688, 1975.171, 7.867, 1.0); }
    // hodan
    public static func FixerSofa() -> Vector4 { return new Vector4(3.227, 10.466, 15.294, 1.0); }
    public static func FixerAway() -> Float { return 100.0; }
    public static func Bar() -> Vector4 { return new Vector4(-1404.26, 1950.77, 23.38, 1.0); }
    public static func FarAway() -> Float { return 150.0; }
    public static func FightAttitudeTicks() -> Int32 { return 3; }
    public static func OfferRadius() -> Float { return 50.0; }
    public static func OfferArmRadius() -> Float { return 250.0; }
    public static func BayaniEntry() -> CName { return n"bayani"; }
    public static func StandSpotRef() -> String { return "$/mod/cc_g04_cast/#cc_g04_bayani_stand"; }
    public static func ByeSpotRef() -> String { return "$/mod/cc_g04_cast/#cc_g04_bayani_bye"; }
    public static func ByeSpot() -> Vector4 { return new Vector4(-1431.445, 1530.385, 18.193, 1.0); }
    public static func ByeArrived() -> Float { return 1.5; }
    public static func RouseTicks() -> Int32 { return 6; }
    // percent
    public static func StampsDownAt() -> Float { return 33.0; }
    public static func StampsRecord() -> TweakDBID { return t"Character.cc_g04_stamps"; }
    public static func StampsShield() -> CName { return n"cc_g04_stamps"; }
    public static func DoorRef() -> String { return "$/mod/cc_g04_room/#cc_g04_room_door"; }
    public static func CellDoorRef() -> String { return "$/mod/cc_g04_room/#cc_g04_cell_door"; }
    // 3m from ligaya
    public static func LeaveSpot() -> Vector4 {
        return new Vector4(-1233.8, 1974.2, 7.87, 1.0);
    }
    // behind v
    public static func GoneBehind() -> Float { return 30.0; }
    // any facing
    public static func GoneAnyway() -> Float { return 70.0; }
    public static func GoneAtEnd() -> Float { return 12.0; }
}

public class ReturnTicketPlaces extends ScriptableSystem {

    private let m_settled: Bool;
    private let m_turned: array<EntityID>;
    private let m_shielded: array<EntityID>;
    private let m_sent: array<EntityID>;
    private let m_roused: Int32;
    private let m_standSent: array<EntityID>;
    private let m_byeSent: array<EntityID>;
    private let m_walkSent: array<EntityID>;
    private let m_byeTick: Int32;
    private let m_byeFrom: Vector4;
    private let m_runTick: Int32;
    private let m_runFrom: Vector4;
    private let m_bayaniCmd: ref<AIUseWorkspotCommand>;
    private let m_hunting: array<EntityID>;
    private let m_oaDoor: Bool;
    private let m_bayaniMissing: Int32;
    private let m_watchTicks: Int32;
    private let m_seen: array<EntityID>;
    private let m_tick: Int32;
    private let m_comTick: Int32;
    private let m_comId: EntityID;
    private let m_comOk: Bool;
    private let m_oaSeen: array<CName>;
    private let m_oaDown: array<CName>;
    private let m_oaMissing: array<Int32>;
    private let m_oaTicks: Int32;
    private let m_strayNames: array<CName>;
    private let m_strayPos: array<Vector4>;
    private let m_strayHp: array<Float>;
    private let m_strayTicks: array<Int32>;
    private let m_roomTicks: Int32;
    private let m_lastClawTicks: Int32;
    private let m_traceLast: String;
    private let m_holdOn: Bool;
    private let m_holdTicks: Int32;
    private let m_holdChecked: Bool;
    private let m_ligayaMissing: Int32;
    private let m_combat: array<EntityID>;
    private let m_persist: array<EntityID>;
    private let m_doorsBack: Bool;
    private let m_oaArmedTicks: Int32;
    private let m_oaRoused: array<EntityID>;
    private let m_oaTurnedLog: array<CName>;
    private let m_afterTicks: Int32;
    private let m_threatsDropped: array<EntityID>;
    private let m_carLocked: EntityID;
    private let m_vanLocked: EntityID;
    private let m_stampsId: EntityID;
    // 1 invulnerable, 2 immortal
    private let m_stampsMode: Int32;
    private let m_stampsFloor: Int32;
    private let m_stampsRoused: Int32;
    private let m_stampsNoDismember: Bool;
    private let m_stampsTouched: Bool;
    private let m_stampsFightTicks: Int32;
    private let m_stampsUnbled: Bool;
    private let m_stampsCalmLogged: Bool;

    private func OnAttach() -> Void {
        FTLog("[CC.Gig04] places watch attached");
        this.Schedule(5.0);
    }

    public func Schedule(delay: Float) -> Void {
        let cb: ref<CCG04PlacesTick> = new CCG04PlacesTick();
        cb.system = this;
        GameInstance.GetDelaySystem(this.GetGameInstance()).DelayCallback(cb, delay, false);
    }

    public func Tick() -> Void {
        if this.m_settled {
            return;
        }
        let game: GameInstance = this.GetGameInstance();
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        let ps: ref<PlayerSystem> = GameInstance.GetPlayerSystem(game);
        if !IsDefined(qs) || !IsDefined(ps) {
            // main menu
            this.Schedule(6.0);
            return;
        }
        this.m_tick += 1;
        this.m_vanLocked = this.LockCar(game, CCG04Places.VanEntry(), this.m_vanLocked);
        let pf: ref<PlayerPuppet> = ps.GetLocalPlayerMainGameObject() as PlayerPuppet;
        if IsDefined(pf) {
            let mode: Int32 = qs.GetFactStr("cc_f01_talk_mode");
            let away: Bool = Vector4.Distance(pf.GetWorldPosition(), CCG04Places.FixerSofa()) > CCG04Places.FixerAway();
            this.SetFact(qs, "cc_g04_fixer_free", (mode <= 0 || (Equals(mode, 1) && away)) ? 1 : 0);
            this.WatchLigaya(game, qs, pf);
            this.Trace(game, qs, pf);
            this.Hold(game, qs, pf);
        }
        if qs.GetFactStr("cc_g04_done") > 0 {
            if qs.GetFactStr("cc_g04_market_off") > 0 && qs.GetFactStr("cc_g04_room_off") > 0 {
                this.m_settled = true;
                return;
            }
            let pl: ref<PlayerPuppet> = ps.GetLocalPlayerMainGameObject() as PlayerPuppet;
            if IsDefined(pl) {
                this.WatchMarket(qs, pl);
                if qs.GetFactStr("cc_g04_watch_gone") > 0 && qs.GetFactStr("cc_g04_bayani_gone") <= 0 {
                    this.WatchBayani(game, qs, pl);
                }
                this.SetFact(qs, "cc_g04_room_far",
                             Vector4.Distance(pl.GetWorldPosition(), CCG04Places.Door()) > CCG04Places.FarAway() ? 1 : 0);
            }
            this.ShieldLigaya(game, qs);
            this.KeepLook(game, n"ligaya", n"service__vendor_wa_vendor_asian_03");
            this.Schedule(5.0);
            return;
        }
        if qs.GetFactStr("cc_g04_started") <= 0 {
            this.ShieldLigaya(game, qs);
            this.KeepLook(game, n"ligaya", n"service__vendor_wa_vendor_asian_03");
            if qs.GetFactStr("cc_f01_intro_done") <= 0 {
                this.Schedule(5.0);
                return;
            }
            if qs.GetFactStr("cc_g04_near_offer") <= 0 {
                let pv: ref<PlayerPuppet> = ps.GetLocalPlayerMainGameObject() as PlayerPuppet;
                if IsDefined(pv)
                    && Vector4.Distance2D(pv.GetWorldPosition(), CCG04Places.Stall()) > CCG04Places.OfferArmRadius()
                    && Vector4.Distance2D(pv.GetWorldPosition(), CCG04Places.Bar()) > CCG04Places.OfferArmRadius() {
                    this.SetFact(qs, "cc_g04_offer_armed", 1);
                }
                let tier: Int32 = IsDefined(pv)
                    ? pv.GetPlayerStateMachineBlackboard().GetInt(GetAllBlackboardDefs().PlayerStateMachine.HighLevel) : -1;
                let calm: Bool = IsDefined(pv) && !pv.IsInCombat() && tier <= EnumInt(gamePSMHighLevel.SceneTier1);
                this.SetFact(qs, "cc_g04_dbg_tier", tier);
                this.SetFact(qs, "cc_g04_dbg_calm", calm ? 1 : 0);
                let ligaya: ref<ScriptedPuppet> = this.FindInCommunity(game, n"ligaya");
                let here: Bool = IsDefined(ligaya) && ligaya.IsAttached()
                    && Vector4.Distance(ligaya.GetWorldPosition(), CCG04Places.Stall()) < 6.0;
                this.SetFact(qs, "cc_g04_dbg_ligaya_here", here ? 1 : 0);
                if calm && qs.GetFactStr("cc_g04_offer_armed") > 0
                    && Vector4.Distance2D(pv.GetWorldPosition(), CCG04Places.Stall()) < CCG04Places.OfferRadius() {
                    qs.SetFactStr("cc_g04_near_offer", 1);
                }
            }
            let early: ref<PlayerPuppet> = ps.GetLocalPlayerMainGameObject() as PlayerPuppet;
            if qs.GetFactStr("cc_g04_offer_armed") > 0 && IsDefined(early) {
                this.WatchStamps(game, qs, early);
            }
            this.Schedule(2.0);
            return;
        }
        let player: ref<PlayerPuppet> = ps.GetLocalPlayerMainGameObject() as PlayerPuppet;
        if !IsDefined(player) {
            this.Schedule(2.0);
            return;
        }

        if qs.GetFactStr("cc_g04_stamps_talked") <= 0 {
            this.ReadChecks(qs, player);
        }

        this.WatchStamps(game, qs, player);

        this.KeepLook(game, n"ligaya", n"service__vendor_wa_vendor_asian_03");
        this.KeepLook(game, CCG04Places.BayaniEntry(), n"service__vendor_ma_vendor_asian_02");

        this.ShieldLigaya(game, qs);

        this.SetFact(qs, "cc_g04_ep1", IsEP1() ? 1 : 0);

        if qs.GetFactStr("cc_g04_flop_armed") > 0 {
            if Vector4.Distance(player.GetWorldPosition(), CCG04Places.Van()) < CCG04Places.VanNear()
                && !VehicleComponent.IsMountedToVehicle(game, player) {
                qs.SetFactStr("cc_g04_van_near", 1);
            }
        }

        if qs.GetFactStr("cc_g04_room_armed") > 0
            && CCSharedWorld.Near(player.GetWorldPosition(), CCG04Places.Door(),
                                  CCG04Places.ArmRadius(), 20.0, 20.0) {
            this.TurnGroup(game, qs, CCG04Places.ClawEntries());
            this.ShieldBayani(game, qs);
            if (qs.GetFactStr("cc_g04_bayani_up") > 0 || qs.GetFactStr("cc_g04_room_done") > 0)
                && qs.GetFactStr("cc_g04_oa_clear") <= 0 {
                this.PlaceBayani(game, false);
            }
            if qs.GetFactStr("cc_g04_claws_clear") <= 0 {
                this.ClawsClear(game, qs, player);
            }
            if !this.m_oaDoor {
                this.m_oaDoor = this.OpenDoor(game, qs, CCG04Places.DoorRef(), "cc_g04_dbg_door") > 0;
            }
        }

        if qs.GetFactStr("cc_g04_oa_armed") > 0 && qs.GetFactStr("cc_g04_oa_clear") <= 0 {
            let set: Int32 = qs.GetFactStr("cc_g04_oa_set");
            let ep1: Bool = set > 0 ? Equals(set, 1) : qs.GetFactStr("cc_g04_ep1") > 0;
            let oa: array<CName> = CCG04Places.OAEntries(ep1);
            this.m_oaArmedTicks += 1;
            this.m_carLocked = this.LockCar(game, CCG04Places.CarEntry(), this.m_carLocked);
            if CCSharedWorld.Near(player.GetWorldPosition(), CCG04Places.Door(),
                                  CCG04Places.ArmRadius(), 20.0, 20.0) {
                if !this.m_oaDoor {
                    this.m_oaDoor = this.OpenDoor(game, qs, CCG04Places.DoorRef(), "cc_g04_dbg_door") > 0;
                }
                this.OAOutOfPose(game, oa);
                let ready: array<CName> = this.OAInside(game, oa);
                if ArraySize(ready) > 0 {
                    this.TurnGroup(game, qs, ready);
                    this.Hunt(game, qs, player, ready);
                }
            }
            this.WatchOA(game, qs, player, oa);
        }

        if qs.GetFactStr("cc_g04_oa_clear") > 0 {
            if qs.GetFactStr("cc_g04_room_off") <= 0 {
                let set2: Int32 = qs.GetFactStr("cc_g04_oa_set");
                this.KeepDead(game, qs, CCG04Places.OAEntries(Equals(set2, 1)));
                this.KeepDead(game, qs, CCG04Places.ClawEntries());
                this.m_carLocked = this.LockCar(game, CCG04Places.CarEntry(), this.m_carLocked);
            }
            this.TraceAfterFight(game, qs, player);
            this.SendBayaniOut(game, qs);
            if qs.GetFactStr("cc_g04_bye_done") <= 0 {
                let walker: ref<ScriptedPuppet> = this.FindInCommunity(game, CCG04Places.BayaniEntry());
                if IsDefined(walker) && ArrayContains(this.m_sent, walker.GetEntityID()) {
                    if qs.GetFactStr("cc_g04_bye_here") <= 0 {
                        this.WalkToHall(game, qs, walker);
                        this.TraceBye(game, walker);
                    } else {
                        this.PlaceBayani(game, true);
                    }
                }
            }
            if qs.GetFactStr("cc_g04_bye_done") > 0 {
                this.ReleaseBayani(game);
                this.RouseBayani(game, qs);
                if qs.GetFactStr("cc_g04_run_go") <= 0 {
                    qs.SetFactStr("cc_g04_run_go", 1);
                    this.m_runTick = this.m_tick;
                    let r: ref<ScriptedPuppet> = this.FindInCommunity(game, CCG04Places.BayaniEntry());
                    if IsDefined(r) {
                        this.m_runFrom = r.GetWorldPosition();
                    }
                    FTLog("[CC.Gig04] Bayani let go of the hall spot, the run can start");
                }
                this.TraceRun(game);
            }
            if qs.GetFactStr("cc_g04_bye_here") <= 0 {
                let here: ref<ScriptedPuppet> = this.FindInCommunity(game, CCG04Places.BayaniEntry());
                if IsDefined(here) && here.IsAttached()
                    && Vector4.Distance2D(here.GetWorldPosition(), CCG04Places.ByeSpot()) < CCG04Places.ByeArrived() {
                    qs.SetFactStr("cc_g04_bye_here", 1);
                }
            }
            if qs.GetFactStr("cc_g04_mid_done") <= 0 {
                this.ShieldBayani(game, qs);
            }
            if qs.GetFactStr("cc_g04_watch_gone") > 0 && qs.GetFactStr("cc_g04_bayani_gone") <= 0 {
                this.WatchBayani(game, qs, player);
            }
        }

        // the railing
        if qs.GetFactStr("cc_g04_watch_gone") > 0 && qs.GetFactStr("cc_g04_close_step") <= 0 {
            let ts: ref<TimeSystem> = GameInstance.GetTimeSystem(game);
            if IsDefined(ts) {
                if qs.GetFactStr("cc_g04_wait_from") <= 0 {
                    qs.SetFactStr("cc_g04_wait_from", Cast<Int32>(ts.GetGameTimeStamp()));
                }
                if qs.GetFactStr("cc_g04_rail_shift") > 0 && qs.GetFactStr("cc_g04_rail_skipped") <= 0 {
                    qs.SetFactStr("cc_g04_rail_skipped", 1);
                    // 2 hours
                    this.SkipAhead(ts, Cast<Float>(qs.GetFactStr("cc_g04_wait_from")), 7200.0);
                }
            }
        }

        if qs.GetFactStr("cc_g04_close_step") > 0 {
            if qs.GetFactStr("cc_g04_rail_taken") > 0 && qs.GetFactStr("cc_g04_rail_release") <= 0 {
                qs.SetFactStr("cc_g04_rail_release", 1);
            }
        }
        if qs.GetFactStr("cc_g04_rail_release") > 0
            && Vector4.Distance(player.GetWorldPosition(), CCG04Places.RailPose()) < 4.0 {
            let ws: ref<WorkspotGameSystem> = GameInstance.GetWorkspotSystem(game);
            if IsDefined(ws) && ws.IsActorInWorkspot(player)
                && qs.GetFactStr("cc_g04_close_step") > 0 {
                ws.SendFastExitSignal(player, new Vector3(0.0, 0.0, 0.0), false, false, false, true);
            }
        }

        if qs.GetFactStr("cc_g04_mid_done") > 0 {
            this.WatchMarket(qs, player);
            if !this.m_doorsBack {
                this.m_doorsBack = this.CloseItselfAgain(game, CCG04Places.DoorRef())
                    && this.CloseItselfAgain(game, CCG04Places.CellDoorRef());
            }
        }
        let here: Vector4 = player.GetWorldPosition();
        this.SetFact(qs, "cc_g04_room_far",
                     Vector4.Distance(here, CCG04Places.Door()) > CCG04Places.FarAway() ? 1 : 0);
        this.SetFact(qs, "cc_g04_flop_far",
                     Vector4.Distance(here, CCG04Places.Van()) > CCG04Places.FarAway() ? 1 : 0);
        this.SetFact(qs, "cc_g04_bar_far",
                     Vector4.Distance(here, CCG04Places.Bar()) > CCG04Places.FarAway() ? 1 : 0);

        this.Schedule(1.0);
    }

    private func SendBayaniOut(game: GameInstance, qs: ref<QuestsSystem>) -> Void {
        let bayani: ref<ScriptedPuppet> = this.FindInCommunity(game, CCG04Places.BayaniEntry());
        if !IsDefined(bayani) || !ScriptedPuppet.IsAlive(bayani) {
            return;
        }
        let id: EntityID = bayani.GetEntityID();
        if !ArrayContains(this.m_seen, id) {
            ArrayPush(this.m_seen, id);
            if qs.GetFactStr("cc_g04_bayani_ran") > 0 {
                qs.SetFactStr("cc_g04_bayani_rerun", 1);
            }
        }
        if ArrayContains(this.m_sent, id) {
            return;
        }
        let cell: Int32 = this.OpenDoor(game, qs, CCG04Places.CellDoorRef(), "cc_g04_dbg_cell_door");
        let street: Int32 = this.OpenDoor(game, qs, CCG04Places.DoorRef(), "cc_g04_dbg_door");
        if cell <= 0 || street <= 0 {
            return;
        }
        ArrayPush(this.m_sent, id);
        qs.SetFactStr("cc_g04_dbg_sent", ArraySize(this.m_sent));
        FTLog("[CC.Gig04] both doors open, Bayani cleared to leave");
    }

    private func ClearStool(game: GameInstance, player: ref<PlayerPuppet>) -> Void {
        let stool: Vector4 = CCG04Places.Bar();
        if Vector4.Distance(player.GetWorldPosition(), stool) > 60.0 {
            return;
        }
        let query: TargetSearchQuery = TSQ_NPC();
        query.testedSet = TargetingSet.Complete;
        query.includeSecondaryTargets = false;
        query.ignoreInstigator = true;
        query.maxDistance = 60.0;
        query.filterObjectByDistance = true;
        let parts: array<TS_TargetPartInfo>;
        GameInstance.GetTargetingSystem(game).GetTargetParts(player, query, parts);
        let i: Int32 = 0;
        while i < ArraySize(parts) {
            let npc: ref<ScriptedPuppet> = TS_TargetPartInfo.GetComponent(parts[i]).GetEntity() as ScriptedPuppet;
            // crowd only
            if IsDefined(npc) && !npc.IsPlayer() && npc.IsCrowd()
                && npc.GetRecordID() != CCG04Places.StampsRecord()
                && Vector4.Distance(npc.GetWorldPosition(), stool) < 1.0 {
                FTLog("[CC.Gig04] a passer-by on Stamps's stool, removed: " + TDBID.ToStringDEBUG(npc.GetRecordID()));
                this.DisposeByName(npc);
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

    private func ShieldLigaya(game: GameInstance, qs: ref<QuestsSystem>) -> Void {
        let ligaya: ref<ScriptedPuppet> = this.FindInCommunity(game, n"ligaya");
        if !IsDefined(ligaya) || !ScriptedPuppet.IsAlive(ligaya) {
            return;
        }
        let gods: ref<GodModeSystem> = GameInstance.GetGodModeSystem(game);
        if !IsDefined(gods) {
            return;
        }
        let id: EntityID = ligaya.GetEntityID();
        if gods.HasGodMode(id, gameGodModeType.Invulnerable) {
            return;
        }
        gods.AddGodMode(id, gameGodModeType.Invulnerable, n"cc_g04_ligaya");
    }

    private func WatchMarket(qs: ref<QuestsSystem>, player: ref<PlayerPuppet>) -> Void {
        if qs.GetFactStr("cc_g04_market_far") > 0 {
            return;
        }
        let here: Vector4 = player.GetWorldPosition();
        if Vector4.Distance(here, CCG04Places.Stall()) > CCG04Places.FarAway()
            && Vector4.Distance(here, CCG04Places.Bar()) > CCG04Places.FarAway() {
            qs.SetFactStr("cc_g04_market_far", 1);
        }
    }

    private func SetFact(qs: ref<QuestsSystem>, name: String, value: Int32) -> Void {
        if qs.GetFactStr(name) != value {
            qs.SetFactStr(name, value);
        }
    }

    private func RouseBayani(game: GameInstance, qs: ref<QuestsSystem>) -> Void {
        if this.m_roused >= CCG04Places.RouseTicks() {
            return;
        }
        let bayani: ref<ScriptedPuppet> = this.FindInCommunity(game, CCG04Places.BayaniEntry());
        if !IsDefined(bayani) || !ScriptedPuppet.IsAlive(bayani) {
            return;
        }
        this.m_roused += 1;
        if this.OutOfPose(game, bayani) {
            qs.SetFactStr("cc_g04_dbg_roused", qs.GetFactStr("cc_g04_dbg_roused") + 1);
        }
    }

    private func PlaceBayani(game: GameInstance, hall: Bool) -> Void {
        let body: ref<ScriptedPuppet> = this.FindInCommunity(game, CCG04Places.BayaniEntry());
        if !IsDefined(body) || !body.IsAttached() || !ScriptedPuppet.IsAlive(body) {
            return;
        }
        let id: EntityID = body.GetEntityID();
        if hall ? ArrayContains(this.m_byeSent, id) : ArrayContains(this.m_standSent, id) {
            return;
        }
        let spotRef: String = hall ? CCG04Places.ByeSpotRef() : CCG04Places.StandSpotRef();
        let ai: ref<AIHumanComponent> = body.GetAIControllerComponent();
        if !IsDefined(ai) {
            return;
        }
        if IsDefined(this.m_bayaniCmd) {
            ai.CancelCommand(this.m_bayaniCmd);
        }
        this.OutOfPose(game, body);
        let cmd: ref<AIUseWorkspotCommand> = new AIUseWorkspotCommand();
        cmd.workspotNode = CreateNodeRef(spotRef);
        cmd.moveToWorkspot = true;
        cmd.jumpToEntry = false;
        cmd.idleOnlyMode = false;
        cmd.continueInCombat = true;
        ai.SendCommand(cmd);
        this.m_bayaniCmd = cmd;
        if hall {
            ArrayPush(this.m_byeSent, id);
        } else {
            ArrayPush(this.m_standSent, id);
        }
        FTLog("[CC.Gig04] Bayani sent to " + spotRef);
    }

    private func WalkToHall(game: GameInstance, qs: ref<QuestsSystem>, body: ref<ScriptedPuppet>) -> Void {
        let id: EntityID = body.GetEntityID();
        if ArrayContains(this.m_walkSent, id) {
            // 40s
            if this.m_tick - this.m_byeTick <= 40 && this.OutOfPose(game, body) {
                FTLog(s"[CC.Gig04] Bayani still in a pose \(this.m_tick - this.m_byeTick) s into his walk, fast exit sent again");
            }
            return;
        }
        let ai: ref<AIHumanComponent> = body.GetAIControllerComponent();
        if IsDefined(ai) && IsDefined(this.m_bayaniCmd) {
            ai.CancelCommand(this.m_bayaniCmd);
        }
        this.m_bayaniCmd = null;
        this.OutOfPose(game, body);
        qs.SetFactStr("cc_g04_bye_go", 1);
        ArrayPush(this.m_walkSent, id);
        this.m_byeTick = this.m_tick;
        this.m_byeFrom = body.GetWorldPosition();
        FTLog("[CC.Gig04] Bayani's cell order cancelled, walking to the hall on the path");
    }

    private func TraceBye(game: GameInstance, body: ref<ScriptedPuppet>) -> Void {
        if !ArrayContains(this.m_walkSent, body.GetEntityID()) {
            return;
        }
        let since: Int32 = this.m_tick - this.m_byeTick;
        if since > 40 || since % 2 != 0 {
            return;
        }
        let ws: ref<WorkspotGameSystem> = GameInstance.GetWorkspotSystem(game);
        let posed: Bool = IsDefined(ws) && ws.IsActorInWorkspot(body);
        let state: String = EnumValueToString("gamedataNPCHighLevelState",
            Cast<Int64>(EnumInt(body.GetHighLevelStateFromBlackboard())));
        let here: Vector4 = body.GetWorldPosition();
        FTLog(s"[CC.Gig04] Bayani \(since) s into his walk: to hall \(Vector4.Distance(here, CCG04Places.ByeSpot())) m, moved \(Vector4.Distance(here, this.m_byeFrom)) m, posed=\(posed ? 1 : 0), state=\(state)");
    }

    private func TraceAfterFight(game: GameInstance, qs: ref<QuestsSystem>, player: ref<PlayerPuppet>) -> Void {
        this.m_afterTicks += 1;
        if this.m_afterTicks <= 90 && player.IsInCombat() {
            this.DropDeadThreats(player);
        }
        if this.m_afterTicks > 60 || this.m_afterTicks % 2 != 0 {
            return;
        }
        let set: Int32 = qs.GetFactStr("cc_g04_oa_set");
        let who: array<CName> = CCG04Places.ClawEntries();
        let oa: array<CName> = CCG04Places.OAEntries(Equals(set, 1));
        let j: Int32 = 0;
        while j < ArraySize(oa) {
            ArrayPush(who, oa[j]);
            j += 1;
        }
        let here: Vector4 = player.GetWorldPosition();
        let playerAgent: ref<AttitudeAgent> = player.GetAttitudeAgent();
        let line: String = s"[CC.Gig04] \(this.m_afterTicks) s after the fight: V combat=\(player.IsInCombat() ? 1 : 0)";
        let i: Int32 = 0;
        while i < ArraySize(who) {
            let name: String = NameToString(who[i]);
            line += s" | \(name) dead=\(qs.GetFactStr("cc_g04_dead_" + name))";
            let body: ref<ScriptedPuppet> = this.FindInCommunity(game, who[i]);
            if !IsDefined(body) {
                line += " none";
            } else {
                let agent: ref<AttitudeAgent> = body.GetAttitudeAgent();
                let att: String = "?";
                if IsDefined(agent) && IsDefined(playerAgent) {
                    att = EnumValueToString("EAIAttitude", Cast<Int64>(EnumInt(agent.GetAttitudeTowards(playerAgent))));
                }
                let senses: ref<SenseComponent> = body.GetSensesComponent();
                let sees: Bool = IsDefined(senses) && senses.IsAgentVisible(player);
                let state: String = EnumValueToString("gamedataNPCHighLevelState",
                    Cast<Int64>(EnumInt(body.GetHighLevelStateFromBlackboard())));
                line += s" up=\(ScriptedPuppet.IsActive(body) ? 1 : 0) d=\(Vector4.Distance(body.GetWorldPosition(), here)) \(att) sees=\(sees ? 1 : 0) \(state)";
            }
            i += 1;
        }
        let tt: ref<TargetTrackerComponent> = player.GetTargetTrackerComponent();
        if IsDefined(tt) {
            let threats: array<TrackedLocation> = tt.GetHostileThreats(false);
            line += s" || V's threats \(ArraySize(threats))";
            let k: Int32 = 0;
            while k < ArraySize(threats) {
                line += " | " + this.DescribeThreat(threats[k].entity, here);
                k += 1;
            }
        }
        FTLog(line);
    }

    private func DescribeThreat(et: wref<Entity>, here: Vector4) -> String {
        if !IsDefined(et) {
            return "gone";
        }
        let s: String = NameToString(et.GetClassName());
        let puppet: ref<ScriptedPuppet> = et as ScriptedPuppet;
        if IsDefined(puppet) {
            s += s" \(TDBID.ToStringDEBUG(puppet.GetRecordID())) up=\(ScriptedPuppet.IsActive(puppet) ? 1 : 0)";
        }
        s += s" d=\(Vector4.Distance(et.GetWorldPosition(), here))";
        return s;
    }

    private func DropDeadThreats(player: ref<PlayerPuppet>) -> Void {
        let tt: ref<TargetTrackerComponent> = player.GetTargetTrackerComponent();
        if !IsDefined(tt) {
            return;
        }
        let threats: array<TrackedLocation> = tt.GetHostileThreats(false);
        let k: Int32 = 0;
        while k < ArraySize(threats) {
            let puppet: ref<ScriptedPuppet> = threats[k].entity as ScriptedPuppet;
            if IsDefined(puppet) && !ScriptedPuppet.IsActive(puppet) {
                tt.RemoveThreat(tt.MapThreat(puppet));
                if !ArrayContains(this.m_threatsDropped, puppet.GetEntityID()) {
                    ArrayPush(this.m_threatsDropped, puppet.GetEntityID());
                    FTLog(s"[CC.Gig04] a down body taken off V's threats, \(this.m_afterTicks) s after the fight: \(TDBID.ToStringDEBUG(puppet.GetRecordID()))");
                }
            }
            k += 1;
        }
    }

    private func TraceRun(game: GameInstance) -> Void {
        let since: Int32 = this.m_tick - this.m_runTick;
        if since > 20 || since % 2 != 0 {
            return;
        }
        let body: ref<ScriptedPuppet> = this.FindInCommunity(game, CCG04Places.BayaniEntry());
        if !IsDefined(body) {
            FTLog(s"[CC.Gig04] Bayani \(since) s into his run: no body found");
            return;
        }
        let ws: ref<WorkspotGameSystem> = GameInstance.GetWorkspotSystem(game);
        let posed: Bool = IsDefined(ws) && ws.IsActorInWorkspot(body);
        let state: String = EnumValueToString("gamedataNPCHighLevelState",
            Cast<Int64>(EnumInt(body.GetHighLevelStateFromBlackboard())));
        let here: Vector4 = body.GetWorldPosition();
        FTLog(s"[CC.Gig04] Bayani \(since) s into his run: moved \(Vector4.Distance(here, this.m_runFrom)) m, to the street door \(Vector4.Distance(here, CCG04Places.Door())) m, posed=\(posed ? 1 : 0), state=\(state), roused=\(this.m_roused)");
    }

    private func ReleaseBayani(game: GameInstance) -> Void {
        if !IsDefined(this.m_bayaniCmd) {
            return;
        }
        let body: ref<ScriptedPuppet> = this.FindInCommunity(game, CCG04Places.BayaniEntry());
        if IsDefined(body) {
            let ai: ref<AIHumanComponent> = body.GetAIControllerComponent();
            if IsDefined(ai) {
                ai.CancelCommand(this.m_bayaniCmd);
                FTLog("[CC.Gig04] Bayani's hall order cancelled for the run");
            }
        }
        this.m_bayaniCmd = null;
    }

    private func OutOfPose(game: GameInstance, body: ref<ScriptedPuppet>) -> Bool {
        let ws: ref<WorkspotGameSystem> = GameInstance.GetWorkspotSystem(game);
        if !IsDefined(ws) || !ws.IsActorInWorkspot(body) {
            return false;
        }
        ws.SendFastExitSignal(body, new Vector3(0.0, 1.0, 0.0), false, true, false, true);
        return true;
    }

    private func StampsLife(game: GameInstance, qs: ref<QuestsSystem>, player: ref<PlayerPuppet>, stamps: ref<ScriptedPuppet>) -> Void {
        let id: EntityID = stamps.GetEntityID();
        if NotEquals(id, this.m_stampsId) {
            this.m_stampsId = id;
            this.m_stampsMode = 0;
            this.m_stampsFloor = 0;
            this.m_stampsRoused = 0;
            this.m_stampsNoDismember = false;
            this.m_stampsTouched = false;
            this.m_stampsFightTicks = 0;
            this.m_stampsUnbled = false;
        }
        let talked: Bool = qs.GetFactStr("cc_g04_stamps_talked") > 0;
        let fight: Bool = qs.GetFactStr("cc_g04_stamps_fight") > 0;
        let down: Bool = qs.GetFactStr("cc_g04_stamps_down") > 0;
        let pools: ref<StatPoolsSystem> = GameInstance.GetStatPoolsSystem(game);
        if !IsDefined(pools) {
            return;
        }
        let hp: Float = pools.GetStatPoolValue(Cast<StatsObjectID>(id), gamedataStatPoolType.Health, true);
        if fight && !down {
            this.m_stampsFightTicks += 1;
        }
        if !talked && !fight && qs.GetFactStr("cc_g04_shard_read") > 0
            && !ScriptedPuppet.IsActive(stamps)
            && qs.GetFactStr("cc_g04_stamps_hit") <= 0 {
            qs.SetFactStr("cc_g04_stamps_hit", 1);
        }
        if !talked && (fight || qs.GetFactStr("cc_g04_stamps_hit") > 0)
            && qs.GetFactStr("cc_g04_heat_at_fight") <= 0 {
            qs.SetFactStr("cc_g04_heat_at_fight", CCSharedPrevention.Heat(game) + 1);
        }
        // 1 = no stars
        let mayClear: Bool = qs.GetFactStr("cc_g04_heat_at_fight") == 1;
        if !talked && mayClear && (fight || qs.GetFactStr("cc_g04_stamps_hit") > 0)
            && Vector4.Distance(player.GetWorldPosition(), stamps.GetWorldPosition())
               < CCG04Places.StampsHeatRange()
            && CCSharedPrevention.Heat(game) > 0 {
            CCSharedPrevention.Clear(game);
        }

        if fight && !down && this.m_stampsRoused < CCG04Places.RouseTicks() {
            this.m_stampsRoused += 1;
            this.OutOfPose(game, stamps);
        }
        if fight && !down && !talked
            && ((hp > 0.0 && hp <= CCG04Places.StampsDownAt()) || !ScriptedPuppet.IsActive(stamps)) {
            qs.SetFactStr("cc_g04_stamps_down", 1);
            down = true;
            NPCPuppet.ChangeHighLevelState(stamps, gamedataNPCHighLevelState.Relaxed);
            if ScriptedPuppet.IsUnconscious(stamps) {
                StatusEffectHelper.RemoveAllStatusEffectsByType(stamps, gamedataStatusEffectType.Unconscious);
            }
        }
        if talked && down && !this.m_stampsUnbled {
            StatusEffectHelper.RemoveStatusEffect(stamps, t"BaseStatusEffect.BleedingInfinite");
            this.m_stampsUnbled = true;
        }
        if down {
            this.m_stampsFloor += 1;
            // 5s
            if this.m_stampsFloor <= 5 && !talked && mayClear {
                CCSharedPrevention.Clear(game);
            }
            if this.m_stampsFloor == 1 {
                StatusEffectHelper.ApplyStatusEffect(stamps, t"BaseStatusEffect.Defeated");
            }
            if this.m_stampsFloor == 3 && !talked {
                StatusEffectHelper.ApplyStatusEffect(stamps, t"BaseStatusEffect.BleedingInfinite");
            }
        }
        if !this.m_stampsNoDismember {
            let stats: ref<StatsSystem> = GameInstance.GetStatsSystem(game);
            if IsDefined(stats) {
                stats.AddModifier(Cast<StatsObjectID>(id),
                    RPGManager.CreateStatModifier(gamedataStatType.HitDismembermentFactor,
                                                  gameStatModifierType.Multiplier, 0.0));
                this.m_stampsNoDismember = true;
            }
        }

        let want: Int32 = 0;
        if !talked {
            if down {
                want = 1;
            } else {
                want = 2;
            }
        }
        let inFight: Bool = fight && !down && !talked;

        let agent: ref<AttitudeAgent> = stamps.GetAttitudeAgent();
        let playerAgent: ref<AttitudeAgent> = player.GetAttitudeAgent();
        if IsDefined(agent) && IsDefined(playerAgent) {
            if Equals(want, 1) {
                agent.SetAttitudeGroup(n"friendly");
                agent.SetAttitudeTowards(playerAgent, EAIAttitude.AIA_Friendly);
                this.m_stampsTouched = true;
            }
            if inFight {
                agent.SetAttitudeTowards(playerAgent, EAIAttitude.AIA_Hostile);
                this.m_stampsTouched = true;
            }
            if Equals(want, 0) && this.m_stampsTouched {
                agent.SetAttitudeGroup(n"neutral");
                agent.SetAttitudeTowards(playerAgent, EAIAttitude.AIA_Neutral);
                this.m_stampsTouched = false;
            }
            if !inFight && !Equals(want, 1)
                && (talked || qs.GetFactStr("cc_g04_stamps_hit") <= 0)
                && Vector4.Distance(player.GetWorldPosition(), stamps.GetWorldPosition())
                   > CCG04Places.StampsCalmFrom() {
                this.StampsOutOfFights(player, stamps, agent, playerAgent);
            }
        }

        let gods: ref<GodModeSystem> = GameInstance.GetGodModeSystem(game);
        if IsDefined(gods) && Equals(want, this.m_stampsMode)
            && ((Equals(want, 1) && !gods.HasGodMode(id, gameGodModeType.Invulnerable))
                || (Equals(want, 2) && !gods.HasGodMode(id, gameGodModeType.Immortal))) {
            this.m_stampsMode = 0;
        }
        if IsDefined(gods) && NotEquals(want, this.m_stampsMode) {
            if Equals(this.m_stampsMode, 1) {
                gods.RemoveGodMode(id, gameGodModeType.Invulnerable, CCG04Places.StampsShield());
            }
            if Equals(this.m_stampsMode, 2) {
                gods.RemoveGodMode(id, gameGodModeType.Immortal, CCG04Places.StampsShield());
            }
            if Equals(want, 1) {
                gods.AddGodMode(id, gameGodModeType.Invulnerable, CCG04Places.StampsShield());
            }
            if Equals(want, 2) {
                gods.AddGodMode(id, gameGodModeType.Immortal, CCG04Places.StampsShield());
            }
            this.m_stampsMode = want;
            qs.SetFactStr("cc_g04_dbg_stamps_mode", want);
        }
    }

    private func WatchStamps(game: GameInstance, qs: ref<QuestsSystem>, player: ref<PlayerPuppet>) -> Void {
        if qs.GetFactStr("cc_g04_stamps_dead") <= 0 {
            let stamps: ref<ScriptedPuppet> = this.FindInCommunity(game, CCG04Places.StampsEntry());
            if IsDefined(stamps) && stamps.IsAttached() {
                if !ScriptedPuppet.IsAlive(stamps) {
                    qs.SetFactStr("cc_g04_stamps_dead", 1);
                } else {
                    this.StampsLife(game, qs, player, stamps);
                }
            }
            this.ClearStool(game, player);
        }
        this.KeepLook(game, CCG04Places.StampsEntry(), n"service__vendor_ma_vendor_asian_01");
    }

    private func StampsOutOfFights(player: ref<PlayerPuppet>, stamps: ref<ScriptedPuppet>,
                                   agent: ref<AttitudeAgent>, playerAgent: ref<AttitudeAgent>) -> Void {
        let hostile: Bool = Equals(agent.GetAttitudeTowards(playerAgent), EAIAttitude.AIA_Hostile);
        if hostile {
            agent.SetAttitudeTowards(playerAgent, EAIAttitude.AIA_Neutral);
        }
        let listed: Bool = false;
        let tt: ref<TargetTrackerComponent> = player.GetTargetTrackerComponent();
        if IsDefined(tt) {
            let threats: array<TrackedLocation> = tt.GetHostileThreats(false);
            let k: Int32 = 0;
            while k < ArraySize(threats) {
                if threats[k].entity == stamps {
                    listed = true;
                }
                k += 1;
            }
            if listed {
                tt.RemoveThreat(tt.MapThreat(stamps));
            }
        }
        let his: ref<TargetTrackerComponent> = stamps.GetTargetTrackerComponent();
        let hunting: Bool = IsDefined(his) && his.HasHostileThreat(false);
        if hunting {
            TargetTrackingExtension.RemoveThreat(stamps, player);
        }
        if (hostile || listed || hunting) && !this.m_stampsCalmLogged {
            this.m_stampsCalmLogged = true;
            FTLog(s"[CC.Gig04] Stamps taken out of a fight not his: hostile=\(hostile ? 1 : 0) on V's list=\(listed ? 1 : 0) hunting=\(hunting ? 1 : 0)");
        }
    }

    private func WatchBayani(game: GameInstance, qs: ref<QuestsSystem>, player: ref<PlayerPuppet>) -> Void {
        this.m_watchTicks += 1;
        let bayani: ref<ScriptedPuppet> = this.FindInCommunity(game, CCG04Places.BayaniEntry());
        if !IsDefined(bayani) {
            qs.SetFactStr("cc_g04_dbg_lost", qs.GetFactStr("cc_g04_dbg_lost") + 1);
            let here: Vector4 = player.GetWorldPosition();
            if Vector4.Distance(here, CCG04Places.Door()) > CCG04Places.GoneAnyway()
                && Vector4.Distance(here, CCG04Places.LeaveSpot()) > CCG04Places.GoneAnyway() {
                this.m_bayaniMissing += 1;
                if this.m_bayaniMissing >= 10 {
                    qs.SetFactStr("cc_g04_dbg_gone_dist", -1);
                    qs.SetFactStr("cc_g04_bayani_gone", 1);
                }
            } else {
                this.m_bayaniMissing = 0;
            }
            return;
        }
        this.m_bayaniMissing = 0;
        let here: Vector4 = player.GetWorldPosition();
        let there: Vector4 = bayani.GetWorldPosition();
        if there.Z < 1.0 {
            return;
        }
        let d: Float = Vector4.Distance(here, there);
        let to: Vector4 = Vector4.Normalize2D(there - here);
        let facing: Float = Vector4.Dot2D(player.GetWorldForward(), to);
        let atEnd: Bool = Vector4.Distance2D(there, CCG04Places.LeaveSpot()) < 3.0;
        let long: Bool = this.m_watchTicks > 300;
        if d > CCG04Places.GoneAnyway() || (d > CCG04Places.GoneBehind() && (facing < -0.1 || long))
            || (atEnd && d > CCG04Places.GoneAtEnd()) {
            qs.SetFactStr("cc_g04_dbg_gone_dist", Cast<Int32>(d));
            qs.SetFactStr("cc_g04_bayani_gone", 1);
        }
    }

    private func SkipAhead(ts: ref<TimeSystem>, stamp: Float, wanted: Float) -> Void {
        let left: Float = wanted;
        if stamp > 0.0 {
            left = wanted - (ts.GetGameTimeStamp() - stamp);
        }
        if left > wanted {
            left = wanted;
        }
        if left <= 0.0 {
            return;
        }
        let now: GameTime = ts.GetGameTime();
        let total: Int32 = GameTime.Hours(now) * 3600 + GameTime.Minutes(now) * 60
            + GameTime.Seconds(now) + Cast<Int32>(left);
        ts.SetGameTimeByHMS(total / 3600, (total % 3600) / 60, total % 60,
                            n"cc_g04_waiting_spot");
    }

    private func CloseItselfAgain(game: GameInstance, ref: String) -> Bool {
        let root: GlobalNodeRef;
        let g: GlobalNodeRef = ResolveNodeRef(CreateNodeRef(ref), root);
        if !GlobalNodeRef.IsDefined(g) {
            return false;
        }
        let door: ref<Door> = GameInstance.FindEntityByID(game, Cast<EntityID>(g)) as Door;
        if !IsDefined(door) {
            return false;
        }
        let ps: ref<DoorControllerPS> = door.GetDevicePS();
        if !IsDefined(ps) {
            return false;
        }
        ps.SetCloseItself(true);
        return true;
    }

    private func OpenDoor(game: GameInstance, qs: ref<QuestsSystem>, ref: String, fact: String) -> Int32 {
        let root: GlobalNodeRef;
        let g: GlobalNodeRef = ResolveNodeRef(CreateNodeRef(ref), root);
        if !GlobalNodeRef.IsDefined(g) {
            this.SetFact(qs, fact, 0);
            return 0;
        }
        let door: ref<Door> = GameInstance.FindEntityByID(game, Cast<EntityID>(g)) as Door;
        if !IsDefined(door) {
            this.SetFact(qs, fact, 0);
            return 0;
        }
        let ps: ref<DoorControllerPS> = door.GetDevicePS();
        if !IsDefined(ps) {
            this.SetFact(qs, fact, 0);
            return 0;
        }
        ps.SetCloseItself(false);
        if ps.IsOpen() {
            this.SetFact(qs, fact, 2);
            return 2;
        }
        let action: ref<ScriptableDeviceAction> = ps.GetQuestActionByName(n"ForceOpen") as ScriptableDeviceAction;
        if !IsDefined(action) {
            this.SetFact(qs, fact, 0);
            return 0;
        }
        ps.ExecutePSAction(action, ps);
        this.SetFact(qs, fact, 1);
        return 1;
    }

    private func ShieldBayani(game: GameInstance, qs: ref<QuestsSystem>) -> Void {
        let bayani: ref<ScriptedPuppet> = this.FindInCommunity(game, CCG04Places.BayaniEntry());
        if !IsDefined(bayani) {
            return;
        }
        let id: EntityID = bayani.GetEntityID();
        let gods: ref<GodModeSystem> = GameInstance.GetGodModeSystem(game);
        if !IsDefined(gods) {
            return;
        }
        if gods.HasGodMode(id, gameGodModeType.Invulnerable) {
            return;
        }
        gods.AddGodMode(id, gameGodModeType.Invulnerable, n"cc_g04_bayani");
        ArrayPush(this.m_shielded, id);
        qs.SetFactStr("cc_g04_dbg_shielded", ArraySize(this.m_shielded));
    }

    private func WatchOA(game: GameInstance, qs: ref<QuestsSystem>, player: ref<PlayerPuppet>, entries: array<CName>) -> Void {
        if ArraySize(this.m_oaMissing) < ArraySize(entries) {
            ArrayResize(this.m_oaMissing, ArraySize(entries));
        }
        let near: Bool = CCSharedWorld.Near(player.GetWorldPosition(), CCG04Places.Door(),
                                            CCG04Places.ArmRadius(), 20.0, 20.0);
        if near {
            this.m_oaTicks += 1;
        }
        let late: Bool = this.m_oaTicks > CCG04Places.OAFloor();
        let i: Int32 = 0;
        while i < ArraySize(entries) {
            let e: CName = entries[i];
            if !ArrayContains(this.m_oaDown, e) {
                let body: ref<ScriptedPuppet> = this.FindInCommunity(game, e);
                if IsDefined(body) {
                    this.m_oaMissing[i] = 0;
                    if !ArrayContains(this.m_oaSeen, e) {
                        ArrayPush(this.m_oaSeen, e);
                    }
                    if !ScriptedPuppet.IsActive(body) {
                        ArrayPush(this.m_oaDown, e);
                        FTLog(s"[CC.Gig04] Orbital Air \(NameToString(e)) down: found down, fight tick \(this.m_oaTicks)");
                    }
                } else {
                    if ArrayContains(this.m_oaSeen, e) {
                        if near {
                            this.m_oaMissing[i] += 1;
                            if this.m_oaMissing[i] >= CCG04Places.OAGoneTicks() {
                                ArrayPush(this.m_oaDown, e);
                                FTLog(s"[CC.Gig04] Orbital Air \(NameToString(e)) down: missing \(this.m_oaMissing[i]) s, fight tick \(this.m_oaTicks)");
                            }
                        }
                    } else {
                        if late {
                            ArrayPush(this.m_oaDown, e);
                            FTLog(s"[CC.Gig04] Orbital Air \(NameToString(e)) down: never seen, fight tick \(this.m_oaTicks)");
                        }
                    }
                }
            }
            i += 1;
        }
        if near {
            this.Stray(game, qs, player, entries);
        }
        this.SetFact(qs, "cc_g04_dbg_oa_seen", ArraySize(this.m_oaSeen));
        this.SetFact(qs, "cc_g04_dbg_oa_down", ArraySize(this.m_oaDown));
        if ArraySize(this.m_oaDown) >= ArraySize(entries) {
            qs.SetFactStr("cc_g04_oa_clear", 1);
            FTLog(s"[CC.Gig04] Orbital Air clear, fight tick \(this.m_oaTicks)");
        }
    }

    private func Stray(game: GameInstance, qs: ref<QuestsSystem>, player: ref<PlayerPuppet>,
                       entries: array<CName>) -> Void {
        let pools: ref<StatPoolsSystem> = GameInstance.GetStatPoolsSystem(game);
        if !IsDefined(pools) {
            return;
        }
        let here: Vector4 = player.GetWorldPosition();
        let most: Int32 = 0;
        let i: Int32 = 0;
        while i < ArraySize(entries) {
            let e: CName = entries[i];
            if !ArrayContains(this.m_oaDown, e) {
                let body: ref<ScriptedPuppet> = this.FindInCommunity(game, e);
                if IsDefined(body) && ScriptedPuppet.IsActive(body) {
                    let pos: Vector4 = body.GetWorldPosition();
                    if pos.Z > 1.0 {
                        let k: Int32 = this.StrayIndex(e);
                        let hp: Float = pools.GetStatPoolValue(Cast<StatsObjectID>(body.GetEntityID()),
                                                               gamedataStatPoolType.Health, true);
                        let senses: ref<SenseComponent> = body.GetSensesComponent();
                        let sees: Bool = IsDefined(senses) && senses.IsAgentVisible(player);
                        if Equals(this.m_strayTicks[k], 0) || sees
                            || Vector4.Distance(pos, this.m_strayPos[k]) > 1.5
                            || hp < this.m_strayHp[k] - 0.5 {
                            this.m_strayPos[k] = pos;
                            this.m_strayHp[k] = hp;
                            this.m_strayTicks[k] = 1;
                        } else {
                            this.m_strayTicks[k] += 1;
                            let to: Vector4 = Vector4.Normalize2D(pos - here);
                            // about 70 degrees
                            let inView: Bool = Vector4.Dot2D(player.GetWorldForward(), to) > 0.35;
                            if this.m_strayTicks[k] > CCG04Places.OAStrayTicks()
                                && (!inView || this.m_strayTicks[k] > 3 * CCG04Places.OAStrayTicks()) {
                                let npc: ref<NPCPuppet> = body as NPCPuppet;
                                if IsDefined(npc) {
                                    npc.Kill(null, false, false);
                                }
                                ArrayPush(this.m_oaDown, e);
                                this.m_strayTicks[k] = 0;
                                this.SetFact(qs, "cc_g04_dbg_oa_strays",
                                             qs.GetFactStr("cc_g04_dbg_oa_strays") + 1);
                            }
                        }
                        if this.m_strayTicks[k] > most {
                            most = this.m_strayTicks[k];
                        }
                    }
                }
            }
            i += 1;
        }
        this.SetFact(qs, "cc_g04_dbg_oa_stray", most);
    }

    private func StrayIndex(e: CName) -> Int32 {
        let k: Int32 = 0;
        while k < ArraySize(this.m_strayNames) {
            if Equals(this.m_strayNames[k], e) {
                return k;
            }
            k += 1;
        }
        ArrayPush(this.m_strayNames, e);
        ArrayPush(this.m_strayPos, new Vector4(0.0, 0.0, 0.0, 0.0));
        ArrayPush(this.m_strayHp, 0.0);
        ArrayPush(this.m_strayTicks, 0);
        return ArraySize(this.m_strayNames) - 1;
    }

    private func ClawsClear(game: GameInstance, qs: ref<QuestsSystem>, player: ref<PlayerPuppet>) -> Void {
        if qs.GetFactStr("cc_g04_claws_clear") > 0 {
            return;
        }
        if Vector4.Distance(player.GetWorldPosition(), CCG04Places.Door()) < 40.0 {
            this.m_roomTicks += 1;
        }
        let claws: array<CName> = CCG04Places.ClawEntries();
        let standing: Int32 = 0;
        let busy: Bool = false;
        let i: Int32 = 0;
        while i < ArraySize(claws) {
            if qs.GetFactStr("cc_g04_dead_" + NameToString(claws[i])) <= 0 {
                let body: ref<ScriptedPuppet> = this.FindInCommunity(game, claws[i]);
                if IsDefined(body) && body.IsAttached() {
                    if ScriptedPuppet.IsActive(body) {
                        standing += 1;
                        let k: Int32 = this.StrayIndex(claws[i]);
                        let senses: ref<SenseComponent> = body.GetSensesComponent();
                        if (IsDefined(senses) && senses.IsAgentVisible(player))
                            || Vector4.Distance(body.GetWorldPosition(), this.m_strayPos[k]) > 1.5 {
                            this.m_strayPos[k] = body.GetWorldPosition();
                            busy = true;
                        }
                    }
                } else {
                    if this.m_roomTicks < 20 {
                        standing += 1;
                    }
                }
            }
            i += 1;
        }
        if standing > 0 && !busy && this.InsideBuilding(player.GetWorldPosition()) {
            this.m_lastClawTicks += 1;
            // 45s
            if this.m_lastClawTicks > 45 {
                standing = 0;
            }
        } else {
            this.m_lastClawTicks = 0;
        }
        this.SetFact(qs, "cc_g04_dbg_claws_standing", standing);
        if Equals(standing, 0) {
            qs.SetFactStr("cc_g04_claws_clear", 1);
        }
    }

    private func OAOutOfPose(game: GameInstance, entries: array<CName>) -> Void {
        let i: Int32 = 0;
        while i < ArraySize(entries) {
            let guard: ref<ScriptedPuppet> = this.FindInCommunity(game, entries[i]);
            if IsDefined(guard) && ScriptedPuppet.IsActive(guard)
                && !ArrayContains(this.m_oaRoused, guard.GetEntityID()) {
                this.OutOfPose(game, guard);
                ArrayPush(this.m_oaRoused, guard.GetEntityID());
            }
            i += 1;
        }
    }

    private func OAInside(game: GameInstance, entries: array<CName>) -> array<CName> {
        let out: array<CName>;
        let late: Bool = this.m_oaArmedTicks > CCG04Places.OAGoInTicks();
        let i: Int32 = 0;
        while i < ArraySize(entries) {
            let guard: ref<ScriptedPuppet> = this.FindInCommunity(game, entries[i]);
            if IsDefined(guard) {
                let inside: Bool = this.InsideBuilding(guard.GetWorldPosition());
                if inside || late {
                    ArrayPush(out, entries[i]);
                    if !ArrayContains(this.m_oaTurnedLog, entries[i]) {
                        ArrayPush(this.m_oaTurnedLog, entries[i]);
                        FTLog(s"[CC.Gig04] Orbital Air \(NameToString(entries[i])) turned on V, \(inside ? "inside" : "still outside") after \(this.m_oaArmedTicks) s");
                    }
                }
            }
            i += 1;
        }
        return out;
    }

    private func Hunt(game: GameInstance, qs: ref<QuestsSystem>, player: ref<PlayerPuppet>, entries: array<CName>) -> Void {
        let src: ref<AIThreatPersistenceSource_Record> = TweakDBInterface.GetAIThreatPersistenceSourceRecord(t"AIThreatPersistenceSource.CommandInjectThreat");
        let inside: Bool = this.InsideBuilding(player.GetWorldPosition());
        let bayani: ref<ScriptedPuppet> = this.FindInCommunity(game, CCG04Places.BayaniEntry());
        let i: Int32 = 0;
        while i < ArraySize(entries) {
            let guard: ref<ScriptedPuppet> = this.FindInCommunity(game, entries[i]);
            if IsDefined(guard) && ScriptedPuppet.IsActive(guard) {
                let id: EntityID = guard.GetEntityID();
                let agent: ref<AttitudeAgent> = guard.GetAttitudeAgent();
                let playerAgent: ref<AttitudeAgent> = player.GetAttitudeAgent();
                let reset: Bool = IsDefined(agent) && IsDefined(playerAgent)
                    && NotEquals(agent.GetAttitudeTowards(playerAgent), EAIAttitude.AIA_Hostile);
                if !ArrayContains(this.m_hunting, id) || reset {
                    if IsDefined(agent) && IsDefined(playerAgent) {
                        agent.SetAttitudeTowards(playerAgent, EAIAttitude.AIA_Hostile);
                    }
                    TargetTrackingExtension.InjectThreat(guard, player);
                    if !ArrayContains(this.m_hunting, id) {
                        ArrayPush(this.m_hunting, id);
                    }
                    this.SetFact(qs, "cc_g04_dbg_oa_hunting", ArraySize(this.m_hunting));
                }
                if !ArrayContains(this.m_combat, id) {
                    NPCPuppet.ChangeHighLevelState(guard, gamedataNPCHighLevelState.Combat);
                    ArrayPush(this.m_combat, id);
                }
                if IsDefined(bayani) && IsDefined(agent) {
                    let bAgent: ref<AttitudeAgent> = bayani.GetAttitudeAgent();
                    if IsDefined(bAgent) {
                        agent.SetAttitudeTowards(bAgent, EAIAttitude.AIA_Neutral);
                    }
                }
                let on: Bool = ArrayContains(this.m_persist, id);
                if IsDefined(src) && NotEquals(inside, on) {
                    TargetTrackingExtension.SetThreatPersistence(guard, player, inside,
                        Cast<Uint32>(src.EnumValue()));
                    if inside {
                        ArrayPush(this.m_persist, id);
                    } else {
                        ArrayRemove(this.m_persist, id);
                    }
                }
            }
            i += 1;
        }
    }

    private func InsideBuilding(p: Vector4) -> Bool {
        let d: Vector4 = p - CCG04Places.Door();
        let u: Float = Vector4.Dot2D(d, CCG04Places.RoomU());
        let v: Float = Vector4.Dot2D(d, CCG04Places.RoomV());
        return v > 0.5 && v < 20.0 && AbsF(u) < 12.0 && AbsF(d.Z) < 3.0;
    }

    private func TurnGroup(game: GameInstance, qs: ref<QuestsSystem>, entries: array<CName>) -> Void {
        let playerObj: ref<GameObject> = GameInstance.GetPlayerSystem(game).GetLocalPlayerMainGameObject();
        let playerAgent: ref<AttitudeAgent>;
        if IsDefined(playerObj) {
            playerAgent = playerObj.GetAttitudeAgent();
        }
        this.KeepDead(game, qs, entries);
        let bayani: ref<ScriptedPuppet> = this.FindInCommunity(game, CCG04Places.BayaniEntry());
        let bAgent: ref<AttitudeAgent>;
        if IsDefined(bayani) {
            bAgent = bayani.GetAttitudeAgent();
        }
        let i: Int32 = 0;
        while i < ArraySize(entries) {
            let claw: ref<ScriptedPuppet> = this.FindInCommunity(game, entries[i]);
            if IsDefined(claw) && IsDefined(bAgent) && IsDefined(claw.GetAttitudeAgent()) {
                claw.GetAttitudeAgent().SetAttitudeTowards(bAgent, EAIAttitude.AIA_Neutral);
            }
            let lapsed: Bool = false;
            if IsDefined(claw) && IsDefined(playerAgent) && IsDefined(claw.GetAttitudeAgent()) {
                lapsed = NotEquals(claw.GetAttitudeAgent().GetAttitudeTowards(playerAgent), EAIAttitude.AIA_Hostile);
            }
            if IsDefined(claw) && ScriptedPuppet.IsActive(claw)
                && (!ArrayContains(this.m_turned, claw.GetEntityID()) || lapsed) {
                CCSharedAttitude.Hostile(game, claw.GetEntityID());
                let senses: ref<SenseComponent> = claw.GetSensesComponent();
                if IsDefined(senses) {
                    senses.Toggle(true);
                }
                if !ArrayContains(this.m_turned, claw.GetEntityID()) {
                    ArrayPush(this.m_turned, claw.GetEntityID());
                }
                this.SetFact(qs, "cc_g04_dbg_claws_turned", ArraySize(this.m_turned));
            }
            i += 1;
        }
    }

    private func KeepDead(game: GameInstance, qs: ref<QuestsSystem>, entries: array<CName>) -> Void {
        let i: Int32 = 0;
        while i < ArraySize(entries) {
            let body: ref<ScriptedPuppet> = this.FindInCommunity(game, entries[i]);
            if IsDefined(body) && body.IsAttached() {
                let fact: String = "cc_g04_dead_" + NameToString(entries[i]);
                let down: Bool = !ScriptedPuppet.IsAlive(body) || ScriptedPuppet.IsDefeated(body)
                    || ScriptedPuppet.IsUnconscious(body);
                if down {
                    if qs.GetFactStr(fact) <= 0 {
                        qs.SetFactStr(fact, 1);
                    }
                } else {
                    // respawn
                    if qs.GetFactStr(fact) > 0 {
                        let npc: ref<NPCPuppet> = body as NPCPuppet;
                        if IsDefined(npc) {
                            npc.Kill(null, true, false);
                        }
                    }
                }
            }
            i += 1;
        }
    }

    private func KeepLook(game: GameInstance, entry: CName, look: CName) -> Void {
        let body: ref<ScriptedPuppet> = this.FindInCommunity(game, entry);
        if IsDefined(body) && body.IsAttached() {
            let now: CName = body.GetCurrentAppearanceName();
            if IsNameValid(now) && NotEquals(now, look) {
                body.ScheduleAppearanceChange(look);
            }
        }
    }

    private func LockCar(game: GameInstance, entry: CName, done: EntityID) -> EntityID {
        if !this.m_comOk {
            return done;
        }
        let locked: EntityID = done;
        let objects: array<ref<GameObject>>;
        GetGameObjectsFromSpawnerEntityID(this.m_comId, [entry], game, objects);
        let i: Int32 = 0;
        while i < ArraySize(objects) {
            let car: ref<VehicleObject> = objects[i] as VehicleObject;
            if IsDefined(car) && IsDefined(car.GetVehiclePS()) && car.GetEntityID() != done {
                let evt: ref<VehicleQuestChangeDoorStateEvent> = new VehicleQuestChangeDoorStateEvent();
                evt.newState = EQuestVehicleDoorState.LockAll;
                GameInstance.GetPersistencySystem(game).QueuePSEvent(car.GetVehiclePS().GetID(),
                    car.GetVehiclePS().GetClassName(), evt);
                locked = car.GetEntityID();
            }
            i += 1;
        }
        return locked;
    }

    private func Hold(game: GameInstance, qs: ref<QuestsSystem>, player: ref<PlayerPuppet>) -> Void {
        let asked: Bool = qs.GetFactStr("cc_g04_hold") > 0;
        if asked {
            this.m_holdTicks += 1;
        } else {
            this.m_holdTicks = 0;
        }
        let want: Bool = asked && this.m_holdTicks < CCG04Places.HoldCapTicks()
            && !VehicleComponent.IsMountedToVehicle(game, player);
        if want && !this.m_holdOn {
            StatusEffectHelper.ApplyStatusEffect(player, CCG04Places.HoldRecord());
            this.m_holdOn = true;
        } else if !want && (this.m_holdOn || !this.m_holdChecked) {
            StatusEffectHelper.RemoveStatusEffect(player, CCG04Places.HoldRecord());
            this.m_holdOn = false;
        }
        this.m_holdChecked = true;
    }

    private func WatchLigaya(game: GameInstance, qs: ref<QuestsSystem>, player: ref<PlayerPuppet>) -> Void {
        if qs.GetFactStr("cc_f01_intro_done") <= 0 || qs.GetFactStr("cc_g04_stall_done") > 0
            || qs.GetFactStr("cc_g04_ligaya_missing") > 0 || qs.GetFactStr("cc_g04_ligaya_retries") >= 5
            || Vector4.Distance2D(player.GetWorldPosition(), CCG04Places.Stall()) > 120.0 {
            this.m_ligayaMissing = 0;
            return;
        }
        let ligaya: ref<ScriptedPuppet> = this.FindInCommunity(game, n"ligaya");
        if IsDefined(ligaya) && ligaya.IsAttached()
            && Vector4.Distance(ligaya.GetWorldPosition(), CCG04Places.Stall()) < 6.0 {
            this.m_ligayaMissing = 0;
            return;
        }
        this.m_ligayaMissing += 1;
        if this.m_ligayaMissing >= 15 {
            this.m_ligayaMissing = 0;
            qs.SetFactStr("cc_g04_ligaya_missing", 1);
            FTLog(s"[CC.Gig04] Ligaya missing at her stall: the quest switches her off and on (retry \(qs.GetFactStr("cc_g04_ligaya_retries") + 1))");
        }
    }

    private func Trace(game: GameInstance, qs: ref<QuestsSystem>, player: ref<PlayerPuppet>) -> Void {
        if qs.GetFactStr("cc_f01_intro_done") <= 0 || qs.GetFactStr("cc_g04_stall_done") > 0 {
            return;
        }
        let p: Vector4 = player.GetWorldPosition();
        let dStall: Int32 = Cast<Int32>(Vector4.Distance2D(p, CCG04Places.Stall()));
        let dBar: Int32 = Cast<Int32>(Vector4.Distance2D(p, CCG04Places.Bar()));
        let flags: String = s"intro=\(qs.GetFactStr("cc_f01_intro_done")) armed=\(qs.GetFactStr("cc_g04_offer_armed")) near=\(qs.GetFactStr("cc_g04_near_offer")) free=\(qs.GetFactStr("cc_g04_fixer_free")) started=\(qs.GetFactStr("cc_g04_started")) stall=\(qs.GetFactStr("cc_g04_stall_done")) missing=\(qs.GetFactStr("cc_g04_ligaya_missing")) retries=\(qs.GetFactStr("cc_g04_ligaya_retries"))";
        let near: Bool = dStall < 400 || dBar < 400;
        if NotEquals(flags, this.m_traceLast) || (near && Equals(this.m_tick % 10, 0)) {
            this.m_traceLast = flags;
            this.FindInCommunity(game, n"ligaya");
            FTLog(s"[CC.Gig04] t=\(this.m_tick) V=(\(Cast<Int32>(p.X)),\(Cast<Int32>(p.Y)),\(Cast<Int32>(p.Z))) dStall=\(dStall) dBar=\(dBar) \(flags) community=\(this.m_comOk ? "ok" : "NOT RESOLVED") ligaya[\(this.BodyLine(game, n"ligaya", CCG04Places.Stall()))] stamps[\(this.BodyLine(game, CCG04Places.StampsEntry(), CCG04Places.Bar()))]");
        }
    }

    private func BodyLine(game: GameInstance, entry: CName, place: Vector4) -> String {
        if !this.m_comOk {
            return "-";
        }
        let objects: array<ref<GameObject>>;
        GetGameObjectsFromSpawnerEntityID(this.m_comId, [entry], game, objects);
        let line: String = s"bodies=\(ArraySize(objects))";
        let i: Int32 = 0;
        while i < ArraySize(objects) {
            let body: ref<ScriptedPuppet> = objects[i] as ScriptedPuppet;
            if IsDefined(body) {
                let q: Vector4 = body.GetWorldPosition();
                line += s" #\(i) alive=\(ScriptedPuppet.IsAlive(body) ? 1 : 0) attached=\(body.IsAttached() ? 1 : 0) d=\(Cast<Int32>(Vector4.Distance(q, place))) at=(\(Cast<Int32>(q.X)),\(Cast<Int32>(q.Y)),\(Cast<Int32>(q.Z))) look=\(NameToString(body.GetCurrentAppearanceName()))";
            }
            i += 1;
        }
        return line;
    }

    private func FindInCommunity(game: GameInstance, entry: CName) -> ref<ScriptedPuppet> {
        let dead: ref<ScriptedPuppet>;
        if this.m_comTick != this.m_tick {
            let nref: NodeRef = CreateNodeRef(CCG04Places.CommunityRef());
            let root: GlobalNodeRef;
            let g: GlobalNodeRef = ResolveNodeRef(nref, root);
            this.m_comOk = GlobalNodeRef.IsDefined(g);
            this.m_comId = Cast<EntityID>(g);
            this.m_comTick = this.m_tick;
        }
        if !this.m_comOk {
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

    private func ReadChecks(qs: ref<QuestsSystem>, player: ref<PlayerPuppet>) -> Void {
        let place: ref<ContentAssignment_Record> = TweakDBInterface.GetContentAssignmentRecord(t"DeviceContentAssignment.sts_wat_kab_03");
        if !IsDefined(place) {
            qs.SetFactStr("cc_g04_dbg_need", -1);
            return;
        }
        this.SetFact(qs, "cc_g04_dbg_need", RPGManager.GetBluelineBuildCheckValue(player, place, EGameplayChallengeLevel.MEDIUM));
        this.SetFact(qs, "cc_g04_dbg_body", RPGManager.GetBuildScore(player, TweakDBInterface.GetPlayerBuildRecord(t"PlayerBuilds.Solo")));
        this.SetFact(qs, "cc_g04_dbg_int", RPGManager.GetBuildScore(player, TweakDBInterface.GetPlayerBuildRecord(t"PlayerBuilds.Netrunner")));
    }
}

public class CCG04PlacesTick extends DelayCallback {
    public let system: wref<ReturnTicketPlaces>;

    public func Call() -> Void {
        if IsDefined(this.system) {
            this.system.Tick();
        }
    }
}

@wrapMethod(NPCPuppet)
protected cb func OnHit(evt: ref<gameHitEvent>) -> Bool {
    let r: Bool = wrappedMethod(evt);
    if Equals(this.GetRecordID(), CCG04Places.StampsRecord()) && IsDefined(evt.attackData) {
        let by: wref<GameObject> = evt.attackData.GetInstigator();
        if IsDefined(by) && by.IsPlayer() {
            let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGame());
            if IsDefined(qs) && qs.GetFactStr("cc_g04_shard_read") > 0
                && qs.GetFactStr("cc_g04_stamps_talked") <= 0
                && qs.GetFactStr("cc_g04_stamps_fight") <= 0
                && qs.GetFactStr("cc_g04_stamps_hit") <= 0 {
                qs.SetFactStr("cc_g04_stamps_hit", 1);
                if qs.GetFactStr("cc_g04_heat_at_fight") <= 0 {
                    qs.SetFactStr("cc_g04_heat_at_fight", CCSharedPrevention.Heat(this.GetGame()) + 1);
                }
            }
        }
    }
    return r;
}
