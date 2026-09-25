module CyberpunkCodes.Gig03

import CyberpunkCodes.Shared.Gig03.*

public abstract class CCG03Places {

    public static func Corners() -> Int32 { return 10; }

    public static func Corner(i: Int32) -> Vector4 {
        switch i {
            case 0: return new Vector4(-94.603, -5182.958, 87.070, 1.0);
            case 1: return new Vector4(-93.260, -5191.834, 87.070, 1.0);
            case 2: return new Vector4(-63.751, -5188.975, 87.070, 1.0);
            case 3: return new Vector4(-58.180, -5240.128, 87.198, 1.0);
            case 4: return new Vector4(-62.299, -5241.255, 87.106, 1.0);
            case 5: return new Vector4(-62.074, -5245.433, 87.133, 1.0);
            case 6: return new Vector4(-125.795, -5250.342, 87.042, 1.0);
            case 7: return new Vector4(-130.538, -5205.756, 87.096, 1.0);
            case 8: return new Vector4(-138.655, -5207.188, 87.074, 1.0);
            default: return new Vector4(-141.365, -5185.973, 87.026, 1.0);
        }
    }

    public static func Middle() -> Vector4 {
        return new Vector4(-97.052, -5213.984, 87.1, 1.0);
    }

    public static func Terminal() -> Vector4 {
        return new Vector4(-133.173, -5193.786, 88.564, 1.0);
    }

    // his stool
    public static func Dino() -> Vector4 {
        return new Vector4(-1969.884, 377.748, 8.046, 1.0);
    }

    // desk guess
    public static func SwapRadius() -> Float { return 35.0; }

    // same as swap
    public static func LeaveRadius() -> Float { return 35.0; }

    public static func AtBar(pos: Vector4) -> Bool {
        let him: Vector4 = CCG03Places.Dino();
        return AbsF(pos.Z - him.Z) < 6.0
            && Vector4.Distance2D(pos, him) <= CCG03Places.SwapRadius();
    }

    public static func LeftDino(pos: Vector4) -> Bool {
        let him: Vector4 = CCG03Places.Dino();
        if AbsF(pos.Z - him.Z) > 10.0 {
            return true;
        }
        return Vector4.Distance2D(pos, him) > CCG03Places.LeaveRadius();
    }

    public static func Inside(pos: Vector4) -> Bool {
        let mid: Vector4 = CCG03Places.Middle();
        if pos.Z < mid.Z - 4.0 || pos.Z > mid.Z + 12.0 {
            return false;
        }
        let crossings: Bool = false;
        let n: Int32 = CCG03Places.Corners();
        let j: Int32 = n - 1;
        let i: Int32 = 0;
        while i < n {
            let a: Vector4 = CCG03Places.Corner(i);
            let b: Vector4 = CCG03Places.Corner(j);
            if NotEquals((a.Y > pos.Y), (b.Y > pos.Y))
                && (pos.X < (b.X - a.X) * (pos.Y - a.Y) / (b.Y - a.Y) + a.X) {
                crossings = !crossings;
            }
            j = i;
            i += 1;
        }
        return crossings;
    }

    public static func Arrived(pos: Vector4) -> Bool {
        return Vector4.Distance2D(pos, CCG03Places.Middle()) <= 80.0;
    }

    public static func Escaped(pos: Vector4) -> Bool {
        if CCG03Places.Inside(pos) {
            return false;
        }
        return Vector4.Distance2D(pos, CCG03Places.Middle()) > 60.0;
    }

    public static func AtTerminal(pos: Vector4) -> Bool {
        return CCSharedWorld.Near(pos, CCG03Places.Terminal(), 5.0, 3.0, 3.0);
    }

    public static func Cabinet() -> Vector4 {
        return new Vector4(-95.621, -5211.431, 87.135, 1.0);
    }

    public static func AtCabinet(pos: Vector4) -> Bool {
        // door is 3.15m away
        return CCSharedWorld.Near(pos, CCG03Places.Cabinet(), 2.0, 2.5, 2.5);
    }

    // a fifth
    public static func Advance() -> Int32 { return 5000; }

    // 10 min
    public static func HeatWaitTicks() -> Int32 { return 300; }

    public static func HoldRecord() -> TweakDBID {
        return t"GameplayRestriction.cc_g03_hold";
    }

    // 30s
    public static func HoldCapTicks() -> Int32 { return 15; }

    public static func AtDino(pos: Vector4) -> Bool {
        return CCSharedWorld.Near(pos, CCG03Places.Dino(), 4.0, 3.0, 3.0);
    }

    public static func Reward() -> TweakDBID {
        return t"QuestRewards.sts_cc_g03_completion";
    }
}

public class AcceptableLossPlaces extends ScriptableSystem {

    private let m_settled: Bool;
    private let m_disposed: array<EntityID>;
    private let m_disposedTimes: array<Int32>;
    private let m_heatWaitTicks: Int32;
    private let m_destroyScheduled: Bool;
    private let m_holdOn: Bool;
    private let m_holdTicks: Int32;
    private let m_holdChecked: Bool;

    private func OnAttach() -> Void {
        this.Schedule(6.0);
    }

    public func Schedule(delay: Float) -> Void {
        let cb: ref<CCG03PlacesTick> = new CCG03PlacesTick();
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
            this.Schedule(6.0);
            return;
        }

        if qs.GetFactStr("cc_g03_done") > 0 {
            let held: ref<GameObject> = ps.GetLocalPlayerMainGameObject();
            if IsDefined(held) {
                StatusEffectHelper.RemoveStatusEffect(held, CCG03Places.HoldRecord());
                if qs.GetFactStr("cc_g03_dbg_hold") == 1 {
                    qs.SetFactStr("cc_g03_dbg_hold", 2);
                }
            }
            this.m_settled = true;
            return;
        }
        if qs.GetFactStr("cc_g03_start") <= 0 {
            this.Schedule(6.0);
            return;
        }

        let player: ref<GameObject> = ps.GetLocalPlayerMainGameObject();
        if !IsDefined(player) {
            this.Schedule(6.0);
            return;
        }
        let pos: Vector4 = player.GetWorldPosition();

        if qs.GetFactStr("cc_g03_arrived") <= 0 {
            if CCG03Places.Arrived(pos) {
                qs.SetFactStr("cc_g03_arrived", 1);
            }
        } else if qs.GetFactStr("cc_g03_inside") <= 0 {
            if CCG03Places.Inside(pos) {
                qs.SetFactStr("cc_g03_inside", 1);
            }
        } else if qs.GetFactStr("cc_g03_terminal") <= 0 {
            if CCG03Places.AtTerminal(pos) {
                qs.SetFactStr("cc_g03_terminal", 1);
            }
        }

        if qs.GetFactStr("cc_g03_data") > 0
            && qs.GetFactStr("cc_g03_alarm") <= 0 {
            if CCG03Places.AtCabinet(pos) {
                if qs.GetFactStr("cc_g03_dbg_alarm_src") <= 0 {
                    // 2 = cabinet
                    qs.SetFactStr("cc_g03_dbg_alarm_src", 2);
                }
                CCG03Alarm.Raise(game);
            }
        }

        if qs.GetFactStr("cc_g03_shard_got") > 0
            && qs.GetFactStr("cc_g03_escaped") <= 0 {
            if CCG03Places.Escaped(pos) {
                qs.SetFactStr("cc_g03_escaped", 1);
            }
        }

        if qs.GetFactStr("cc_g03_escaped") > 0
            && qs.GetFactStr("cc_g03_badlands_left") <= 0 {
            let district: wref<District> = CCSharedPrevention.District(game);
            if IsDefined(district) && !district.IsBadlands() {
                if VehicleComponent.IsMountedToVehicle(game, player) {
                    // vehicle
                    qs.SetFactStr("cc_g03_mounted", 1);
                } else {
                    // on foot
                    qs.SetFactStr("cc_g03_mounted", 2);
                }
                qs.SetFactStr("cc_g03_badlands_left", 1);
            }
        }

        if qs.GetFactStr("cc_g03_badlands_left") > 0
            && qs.GetFactStr("cc_g03_on_foot") <= 0 {
            let mounted: Bool = VehicleComponent.IsMountedToVehicle(game, player);
            let heat: Int32 = CCSharedPrevention.Heat(game);
            if heat > 0 {
                this.m_heatWaitTicks += 1;
            }
            let heatOk: Bool = heat <= 0
                || this.m_heatWaitTicks >= CCG03Places.HeatWaitTicks();
            if !mounted && heatOk {
                qs.SetFactStr("cc_g03_on_foot", 1);
            }
        }

        if qs.GetFactStr("cc_g03_loyal") > 0
            && qs.GetFactStr("cc_g03_shard_destroyed") <= 0
            && !this.m_destroyScheduled {
            this.m_destroyScheduled = true;
            let cb: ref<CCG03DestroyCall> = new CCG03DestroyCall();
            cb.game = game;
            // into johnny's scene
            GameInstance.GetDelaySystem(game).DelayCallback(cb, 3.0, false);
        }

        if qs.GetFactStr("cc_g03_docked") > 0
            && qs.GetFactStr("cc_g03_dock_paid") <= 0 {
            this.Dock(game, qs, player as PlayerPuppet);
        }

        if qs.GetFactStr("cc_g03_unlock_dino") > 0
            && qs.GetFactStr("cc_g03_at_bar") <= 0 {
            if CCG03Places.AtBar(pos) {
                qs.SetFactStr("cc_g03_at_bar", 1);
            }
        }

        if qs.GetFactStr("cc_g03_unlock_dino") > 0
            && qs.GetFactStr("cc_g03_delivered") <= 0 {
            if CCG03Places.AtDino(pos) {
                qs.SetFactStr("cc_g03_delivered", 1);
            }
        }

        if qs.GetFactStr("cc_g03_pay_due") > 0
            && qs.GetFactStr("cc_g03_paid") <= 0 {
            this.Pay(game, qs);
        }

        if qs.GetFactStr("cc_g03_delivered") > 0
            && qs.GetFactStr("cc_g03_left_dino") <= 0 {
            if CCG03Places.LeftDino(pos)
                && !VehicleComponent.IsMountedToVehicle(game, player) {
                qs.SetFactStr("cc_g03_left_dino", 1);
            }
        }

        this.Hold(game, qs, player);

        if qs.GetFactStr("cc_g03_swapped") > 0
            && qs.GetFactStr("cc_g03_left_dino") <= 0 {
            this.DinoKeeper(game, player as PlayerPuppet, pos);
        }

        this.Schedule(2.0);
    }

    private func Hold(game: GameInstance, qs: ref<QuestsSystem>,
                      player: ref<GameObject>) -> Void {
        let want: Bool = qs.GetFactStr("cc_g03_left_dino") > 0
            && qs.GetFactStr("cc_g03_johnny_done") <= 0
            && this.m_holdTicks < CCG03Places.HoldCapTicks();
        if want {
            this.m_holdTicks += 1;
        }
        if want && !this.m_holdOn {
            StatusEffectHelper.ApplyStatusEffect(player, CCG03Places.HoldRecord());
            this.m_holdOn = true;
            qs.SetFactStr("cc_g03_dbg_hold", 1);
        } else if !want && (this.m_holdOn || !this.m_holdChecked) {
            StatusEffectHelper.RemoveStatusEffect(player, CCG03Places.HoldRecord());
            this.m_holdOn = false;
            if qs.GetFactStr("cc_g03_dbg_hold") == 1 {
                qs.SetFactStr("cc_g03_dbg_hold", 2);
            }
        }
        this.m_holdChecked = true;
    }

    private func DinoKeeper(game: GameInstance, player: ref<PlayerPuppet>,
                            pos: Vector4) -> Void {
        if !IsDefined(player) {
            return;
        }
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        if !IsDefined(qs) {
            return;
        }
        let him: Vector4 = CCG03Places.Dino();
        if Vector4.Distance(pos, him) > 40.0 {
            return;
        }
        // his community
        let spawner: EntityID = EntityID.FromHash(17285452288567170630ul);
        let objects: array<ref<GameObject>>;
        GetGameObjectsFromSpawnerEntityID(spawner, [n"dyno"], game, objects);
        qs.SetFactStr("cc_g03_dbg_dino_seen", ArraySize(objects));
        let k: Int32 = 0;
        while k < ArraySize(objects) {
            this.RemoveDino(game, qs, objects[k] as ScriptedPuppet, 1);
            k += 1;
        }
        let ids: array<EntityID>;
        GetFixedEntityIdsFromSpawnerEntityID(spawner, [n"dyno"], game, ids);
        k = 0;
        while k < ArraySize(ids) {
            this.RemoveDino(game, qs,
                            GameInstance.FindEntityByID(game, ids[k]) as ScriptedPuppet, 2);
            k += 1;
        }
        let query: TargetSearchQuery;
        query.searchFilter = TSF_Any(IntEnum<TSFMV>(2));
        query.testedSet = TargetingSet.Complete;
        query.includeSecondaryTargets = true;
        query.ignoreInstigator = true;
        query.maxDistance = 40.0;
        query.filterObjectByDistance = true;
        let parts: array<TS_TargetPartInfo>;
        GameInstance.GetTargetingSystem(game).GetTargetParts(player, query, parts);
        let i: Int32 = 0;
        while i < ArraySize(parts) {
            let obj: ref<GameObject> = TS_TargetPartInfo.GetComponent(parts[i]).GetEntity() as GameObject;
            let npc: ref<ScriptedPuppet> = obj as ScriptedPuppet;
            if IsDefined(npc) && !npc.IsPlayer()
                && Vector4.Distance(npc.GetWorldPosition(), him) < 20.0 {
                this.RemoveDino(game, qs, npc, 3);
            }
            i += 1;
        }
    }

    private func RemoveDino(game: GameInstance, qs: ref<QuestsSystem>,
                            body: ref<ScriptedPuppet>, route: Int32) -> Void {
        if !IsDefined(body) || body.GetRecordID() != t"Character.dyno" {
            return;
        }
        let id: EntityID = body.GetEntityID();
        let at: Int32 = -1;
        let j: Int32 = 0;
        while j < ArraySize(this.m_disposed) && at < 0 {
            if this.m_disposed[j] == id {
                at = j;
            }
            j += 1;
        }
        if at < 0 {
            ArrayPush(this.m_disposed, id);
            ArrayPush(this.m_disposedTimes, 0);
            at = ArraySize(this.m_disposed) - 1;
        }
        // five per id
        if this.m_disposedTimes[at] >= 5 {
            return;
        }
        this.m_disposedTimes[at] += 1;
        qs_dbg_count(game, "cc_g03_dbg_dino_disposed");
        qs.SetFactStr("cc_g03_dbg_dino_route", route);
        this.DisposeByName(body);
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

    private func Pay(game: GameInstance, qs: ref<QuestsSystem>) -> Void {
        if qs.GetFactStr("cc_g03_paid") > 0 || qs.GetFactStr("cc_g03_loyal") > 0 {
            return;
        }
        let ps: ref<PlayerSystem> = GameInstance.GetPlayerSystem(game);
        if !IsDefined(ps) {
            return;
        }
        let player: ref<PlayerPuppet> = ps.GetLocalPlayerMainGameObject() as PlayerPuppet;
        if !IsDefined(player) {
            return;
        }
        qs.SetFactStr("cc_g03_paid", 1);
        RPGManager.GiveReward(game, CCG03Places.Reward(),
                              Cast<StatsObjectID>(player.GetEntityID()));
    }

    private func Dock(game: GameInstance, qs: ref<QuestsSystem>,
                      player: ref<PlayerPuppet>) -> Void {
        if !IsDefined(player) {
            return;
        }
        let ts: ref<TransactionSystem> = GameInstance.GetTransactionSystem(game);
        if !IsDefined(ts) {
            return;
        }
        qs.SetFactStr("cc_g03_dock_paid", 1);
        let have: Int32 = ts.GetItemQuantity(player, MarketSystem.Money());
        let take: Int32 = CCG03Places.Advance();
        // wallet cap
        if have < take {
            take = have;
        }
        if take > 0 {
            ts.RemoveItem(player, MarketSystem.Money(), take);
        }
        qs.SetFactStr("cc_g03_dbg_docked", take);
    }
}

public class CCG03DestroyCall extends DelayCallback {
    public let game: GameInstance;

    public func Call() -> Void {
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.game);
        let psys: ref<PlayerSystem> = GameInstance.GetPlayerSystem(this.game);
        if !IsDefined(qs) || !IsDefined(psys) {
            return;
        }
        if qs.GetFactStr("cc_g03_shard_destroyed") > 0 {
            return;
        }
        let player: ref<PlayerPuppet> = psys.GetLocalPlayerMainGameObject() as PlayerPuppet;
        if !IsDefined(player) {
            return;
        }
        qs.SetFactStr("cc_g03_shard_destroyed", 1);
        let ts: ref<TransactionSystem> = GameInstance.GetTransactionSystem(this.game);
        if IsDefined(ts) && ts.RemoveItemByTDBID(player, t"Items.cc_g03_shard", 1) {
            qs.SetFactStr("cc_g03_dbg_destroyed", 1);
        } else {
            qs.SetFactStr("cc_g03_dbg_destroyed", 2);
        }
        CCSharedHud.NotifyTyped(this.game,
            GetLocalizedTextByKey(n"cc-g03-destroyed-banner"),
            SimpleMessageType.Negative, 5.0);
    }
}

public class CCG03PlacesTick extends DelayCallback {
    public let system: wref<AcceptableLossPlaces>;

    public func Call() -> Void {
        if IsDefined(this.system) {
            this.system.Tick();
        }
    }
}

public static func qs_dbg_count(game: GameInstance, fact: String) -> Void {
    let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
    if IsDefined(qs) {
        qs.SetFactStr(fact, qs.GetFactStr(fact) + 1);
    }
}
