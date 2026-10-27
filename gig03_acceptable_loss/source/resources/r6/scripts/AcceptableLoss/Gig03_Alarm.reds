module CyberpunkCodes.Gig03

import CyberpunkCodes.Shared.Gig03.*

public abstract class CCG03Alarm {
    // security room
    public static func DoorPos() -> Vector4 {
        return new Vector4(-92.705, -5212.610, 87.155, 1.0);
    }

    // tight
    public static func DoorRadius() -> Float { return 2.5; }

    public static func IsOurDoor(pos: Vector4) -> Bool {
        return Vector4.Distance(pos, CCG03Alarm.DoorPos()) <= CCG03Alarm.DoorRadius();
    }

    public static func AlarmFact() -> String { return "cc_g03_alarm"; }
    public static func FoundFact() -> String { return "cc_g03_traced"; }
    public static func ArmedFact() -> String { return "cc_g03_data"; }
    public static func DoneFact() -> String { return "cc_g03_done"; }
    public static func LeftFact() -> String { return "cc_g03_badlands_left"; }

    public static func ReachMetres() -> Float { return 160.0; }

    // whole compound
    public static func SearchMetres() -> Float { return 120.0; }

    public static func IdlePoll() -> Float { return 5.0; }
    public static func LivePoll() -> Float { return 2.0; }

    public static func IsMilitech(npc: ref<ScriptedPuppet>) -> Bool {
        let name: String = StrLower(TDBID.ToStringDEBUG(npc.GetRecordID()));
        return StrContains(name, "militech");
    }

    public static func TurnOnPlayer(game: GameInstance, npc: ref<ScriptedPuppet>,
                                    player: ref<PlayerPuppet>, injectThreat: Bool) -> Void {
        let agent: ref<AttitudeAgent> = npc.GetAttitudeAgent();
        if IsDefined(agent) && IsDefined(player) {
            agent.SetAttitudeTowards(player.GetAttitudeAgent(), EAIAttitude.AIA_Hostile);
        }
        let senses: ref<SenseComponent> = npc.GetSensesComponent();
        if IsDefined(senses) {
            // eyes on
            senses.Toggle(true);
        }
        if injectThreat && IsDefined(player) {
            // knows where v is
            TargetTrackingExtension.InjectThreat(npc, player, 1.0, -1.0);
            NPCPuppet.ChangeHighLevelState(npc, gamedataNPCHighLevelState.Combat);
        }
    }

    public static func Raise(game: GameInstance) -> Void {
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        if !IsDefined(qs) {
            return;
        }
        if qs.GetFactStr(CCG03Alarm.AlarmFact()) > 0 {
            return;
        }
        qs.SetFactStr(CCG03Alarm.AlarmFact(), 1);
        let trace: ref<AcceptableLossTrace> = GameInstance.GetScriptableSystemsContainer(game)
            .Get(n"CyberpunkCodes.Gig03.AcceptableLossTrace") as AcceptableLossTrace;
        if IsDefined(trace) {
            trace.Tick();
        }
    }

    public static func OnDoorAction(door: ref<Door>, executor: wref<GameObject>,
                                    mustBeOpen: Bool) -> Void {
        if !IsDefined(door) || !CCG03Alarm.IsOurDoor(door.GetWorldPosition()) {
            return;
        }
        // not the guards
        if !IsDefined(executor) || !executor.IsPlayer() {
            return;
        }
        let ps: ref<DoorControllerPS> = door.GetDevicePS();
        if mustBeOpen && (!IsDefined(ps) || !ps.IsOpen()) {
            return;
        }
        let game: GameInstance = door.GetGame();
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        if !IsDefined(qs) {
            return;
        }
        if qs.GetFactStr(CCG03Alarm.DoneFact()) > 0
            || qs.GetFactStr(CCG03Alarm.ArmedFact()) <= 0 {
            return;
        }
        if qs.GetFactStr("cc_g03_dbg_alarm_src") <= 0 {
            // 1 = door
            qs.SetFactStr("cc_g03_dbg_alarm_src", 1);
        }
        CCG03Alarm.Raise(game);
    }
}

public abstract class CCG03Keycard {
    public static func Keycard() -> TweakDBID { return t"Keycards.ina_05_keycard"; }

    public static func Unlock(ps: ref<DoorControllerPS>) -> Void {
        let door: ref<Entity> = ps.GetOwnerEntityWeak();
        if !IsDefined(door) || !CCG03Alarm.IsOurDoor(door.GetWorldPosition()) {
            return;
        }
        if !ps.IsLocked() && !ps.IsSealed() && !ps.IsSkillCheckActive() {
            return;
        }
        let game: GameInstance = ps.GetGameInstance();
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        if !IsDefined(qs) || qs.GetFactStr("cc_g03_start") <= 0
            || qs.GetFactStr(CCG03Alarm.DoneFact()) > 0 {
            return;
        }
        let player: ref<GameObject> = GetPlayer(game);
        let ts: ref<TransactionSystem> = GameInstance.GetTransactionSystem(game);
        if !IsDefined(player) || !IsDefined(ts)
            || !ts.HasItem(player, ItemID.FromTDBID(CCG03Keycard.Keycard())) {
            return;
        }
        let checks: ref<BaseSkillCheckContainer> = ps.GetSkillCheckContainer();
        if IsDefined(checks) {
            CCG03Keycard.Pass(checks.GetEngineeringSlot());
            CCG03Keycard.Pass(checks.GetDemolitionSlot());
            CCG03Keycard.Pass(checks.GetHackingSlot());
        }
        ps.SetIsLocked(false);
        ps.SetIsSealed(false);
        ps.TurnAuthorizationModuleOFF();
        // door stays shut
        ps.ExecutePSAction(ps.ActionQuestForceUnlock(), ps);
    }

    public static func Pass(slot: ref<SkillCheckBase>) -> Void {
        if IsDefined(slot) && slot.IsActive() {
            slot.SetIsActive(false);
            slot.SetIsPassed(true);
            slot.CheckPerformed();
        }
    }
}

@wrapMethod(DoorControllerPS)
public func GetActions(out actions: array<ref<DeviceAction>>, context: GetActionsContext) -> Bool {
    CCG03Keycard.Unlock(this);
    return wrappedMethod(actions, context);
}

@wrapMethod(Door)
protected cb func OnToggleOpen(evt: ref<ToggleOpen>) -> Bool {
    let result: Bool = wrappedMethod(evt);
    CCG03Alarm.OnDoorAction(this, evt.GetExecutor(), true);
    return result;
}

@wrapMethod(Door)
protected cb func OnForceOpen(evt: ref<ForceOpen>) -> Bool {
    let result: Bool = wrappedMethod(evt);
    CCG03Alarm.OnDoorAction(this, evt.GetExecutor(), false);
    return result;
}

@wrapMethod(Door)
protected cb func OnActionDemolition(evt: ref<ActionDemolition>) -> Bool {
    let result: Bool = wrappedMethod(evt);
    CCG03Alarm.OnDoorAction(this, evt.GetExecutor(), false);
    return result;
}

@wrapMethod(Door)
protected cb func OnActionEngineering(evt: ref<ActionEngineering>) -> Bool {
    let result: Bool = wrappedMethod(evt);
    CCG03Alarm.OnDoorAction(this, evt.GetExecutor(), false);
    return result;
}

public class AcceptableLossAlarm extends ScriptableSystem {

    private let m_settled: Bool;
    private let m_turned: array<EntityID>;

    private func OnAttach() -> Void {
        this.Schedule(CCG03Alarm.IdlePoll());
    }

    private let m_ticket: Int32;

    public func Schedule(delay: Float) -> Void {
        this.m_ticket += 1;
        let cb: ref<CCG03AlarmTick> = new CCG03AlarmTick();
        cb.system = this;
        cb.ticket = this.m_ticket;
        GameInstance.GetDelaySystem(this.GetGameInstance()).DelayCallback(cb, delay, false);
    }

    public func Ticket() -> Int32 { return this.m_ticket; }

    public func Tick() -> Void {
        this.m_ticket += 1;
        if this.m_settled {
            return;
        }
        let game: GameInstance = this.GetGameInstance();

        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        let psys: ref<PlayerSystem> = GameInstance.GetPlayerSystem(game);
        if !IsDefined(qs) || !IsDefined(psys) {
            this.Schedule(CCG03Alarm.IdlePoll());
            return;
        }

        if qs.GetFactStr(CCG03Alarm.DoneFact()) > 0
            || qs.GetFactStr(CCG03Alarm.LeftFact()) > 0 {
            this.m_settled = true;
            return;
        }
        if qs.GetFactStr(CCG03Alarm.FoundFact()) <= 0 {
            this.Schedule(CCG03Alarm.IdlePoll());
            return;
        }

        let player: ref<PlayerPuppet> = psys.GetLocalPlayerMainGameObject() as PlayerPuppet;
        if !IsDefined(player) {
            this.Schedule(CCG03Alarm.IdlePoll());
            return;
        }
        let pos: Vector4 = player.GetWorldPosition();
        if Vector4.Distance2D(pos, CCG03Places.Middle()) > CCG03Alarm.ReachMetres() {
            this.Schedule(CCG03Alarm.IdlePoll());
            return;
        }

        this.TurnTheGuards(game, qs, player, pos);
        this.Schedule(CCG03Alarm.LivePoll());
    }

    private func TurnTheGuards(game: GameInstance, qs: ref<QuestsSystem>,
                               player: ref<PlayerPuppet>, pos: Vector4) -> Void {
        let query: TargetSearchQuery = TSQ_NPC();
        query.testedSet = TargetingSet.Complete;
        query.includeSecondaryTargets = false;
        query.ignoreInstigator = true;
        query.maxDistance = CCG03Alarm.SearchMetres();
        query.filterObjectByDistance = true;
        let parts: array<TS_TargetPartInfo>;
        GameInstance.GetTargetingSystem(game).GetTargetParts(player, query, parts);

        let inside: Bool = CCG03Places.Inside(pos);

        let turned: Int32 = 0;
        let seen: Int32 = 0;
        let i: Int32 = 0;
        while i < ArraySize(parts) {
            let obj: ref<GameObject> = TS_TargetPartInfo.GetComponent(parts[i]).GetEntity() as GameObject;
            let npc: ref<ScriptedPuppet> = obj as ScriptedPuppet;
            if IsDefined(npc) && !npc.IsPlayer() && ScriptedPuppet.IsAlive(npc)
                && CCG03Alarm.IsMilitech(npc)
                && Vector4.Distance2D(npc.GetWorldPosition(), CCG03Places.Middle()) <= CCG03Alarm.ReachMetres() {
                seen += 1;
                let id: EntityID = npc.GetEntityID();
                let first: Bool = !ArrayContains(this.m_turned, id);
                if first {
                    ArrayPush(this.m_turned, id);
                    turned += 1;
                }
                CCG03Alarm.TurnOnPlayer(game, npc, player, first || inside);
            }
            i += 1;
        }
        qs.SetFactStr("cc_g03_dbg_guards_seen", seen);
        qs.SetFactStr("cc_g03_dbg_guards_turned", ArraySize(this.m_turned));
    }
}

public class CCG03AlarmTick extends DelayCallback {
    public let system: wref<AcceptableLossAlarm>;
    public let ticket: Int32;

    public func Call() -> Void {
        if IsDefined(this.system) && this.ticket == this.system.Ticket() {
            this.system.Tick();
        }
    }
}
