// Gig 03, Acceptable Loss: the security-room door, and what opening it does.
//
// Until 2026-09-11 the trace started when the shard was taken or read. The
// design moved it to the DOOR: V is found the moment the security room is
// opened, the trace runs, every Militech guard in the compound turns on V,
// and three more arrive. Taking or reading the shard is then only what opens
// the "get out" objective.
//
// Two files share the work. This one is the door and the guards. The bar, the
// banner and the stars stay in Gig03_Trace.reds, which now watches the alarm
// fact rather than the shard.
//
// THE ORDER IS DOOR, BAR, THEN EVERYTHING. The door sets `cc_g03_alarm` and
// the bar starts; six seconds later the bar ends, Gig03_Trace.reds sets
// `cc_g03_traced`, and on THAT the stars land, the guard pass below runs, and
// the graph switches the reinforcements on. Until the trace is done nobody
// knows where V is, so nothing here turns a guard on the door itself (the
// design call, 2026-09-11, after a first build that did).
//
// ---------------------------------------------------------------------------
// THE DOOR IS A BASE-GAME DEVICE, AND THE HOOK IS WHO EXECUTED THE ACTION
//
// Captured in playtest, 2026-09-11: a `Door` at -92.705, -5212.610, 87.155,
// appearance `doors_single_neomilitary_n`, `DoorControllerPS`, entity id
// 8010341909243357489. The shipped sector says it starts CLOSED, is
// INTERACTIVE, `automaticallyClosesItself`, and `doorTriggerSide OUTSIDE`:
// a proximity door, which opens for whoever walks into its trigger.
//
// THAT LAST FIELD IS WHY THE FIRST BUILD WAS WRONG. It wrapped
// `DoorControllerPS.OnSetIsOpened`, which runs on every change of the open
// state whoever caused it. Playtest, 2026-09-11: "as soon as I was detected
// by a guard the trace started". The guard who spotted V ran for the security
// room, the door opened for him, and the hook could not tell him from V.
//
// The door ENTITY's action handlers can. `Door.OnToggleOpen`, `OnForceOpen`,
// `OnActionDemolition` and `OnActionEngineering` are `cb` handlers that carry
// the action, and `evt.GetExecutor()` is who did it: the player pressing the
// prompt or walking into the trigger, the player quickhacking it, the player
// forcing it with Body or Technical Ability. A guard walking through is an
// executor who is not the player, and is ignored. `On*` event handlers run on
// the main thread (gotcha 44), and vanilla's own door reads the executor in
// exactly these four for `m_whoOpened`.
//
// The toggle is only counted when it OPENS (`IsOpen()` on the PS already
// reads the new state); the three forcing routes are counted as they land,
// because the door opens a moment after them.
//
// The test is the entity's position, the way gig 01's
// office doors identify a door, and it runs cheapest-first: the whole rest of
// the game's doors are thrown out by one distance before a fact is read.
//
// It is ARMED by `cc_g03_data`, the terminal having said where the shard is.
// Before that the door is a door, so a player who explores the room early is
// not traced while they are still reading the terminal. The door closes
// itself, so the same player opens it again on the way back, which is when
// it counts. Gig03_Places.reds carries a second trigger at the cabinet for a
// door that is somehow already standing open, and Gig03_Shard.reds sets the
// alarm alongside the shard as the last net, so the stars can never arrive
// AFTER the shard is in hand.
//
// ---------------------------------------------------------------------------
// THE GUARDS ARE THE BASE GAME'S, AND THEY DO NOT ATTACK ON THEIR OWN
//
// The census on 2026-09-09 counted six Militech inside the wire on an early
// save and none of them hostile to V. They are the site's own community, and
// a community NPC arrives with no quarrel with the player and his senses
// switched off as far as the player is concerned (gotchas 74 and 77). So
// "every guard identifies V" is four calls per guard, and the four are what
// the game's own MaxTac drop makes on each unit as it lands
// (psychoSquadAVSystem.swift, `HandleAVLanding`):
//
//   SetAttitudeTowards(player, Hostile)       an enemy, of THIS player only
//   senses.Toggle(true)                       the eyes on (gotcha 77)
//   TargetTrackingExtension.InjectThreat      he knows where V is, exactly
//   NPCPuppet.ChangeHighLevelState(Combat)    and he acts on it now
//
// The first two are this project's measured pair. The last two are why the
// guards come running rather than start a detection ramp from wherever they
// stand: the design says V is FOUND, not spotted.
//
// Vanilla's helper `AIActionHelper.TryChangingAttitudeToHostile` is not used
// because it refuses for a record that is not `IsAggressive`, which a
// guard standing at a post may not be. The pairwise set is unconditional.
//
// WHO IS TURNED: any NPC inside the walked perimeter whose record name
// carries "militech", plus the three reinforcements this gig ships, whose
// records are Militech too. The five civilians in the tents (homeless,
// lowlife, junkie, worker, per the census) are not touched, and neither is
// anybody outside the wire, so the road past the compound stays the road.
//
// The threat is injected once per guard, on the tick he is first seen, and
// again on every tick while V is still INSIDE the wire. Outside it the guards
// keep whatever they have: inside, they always know; outside, they have to
// find you, and the stars take over.
//
// ---------------------------------------------------------------------------
// IT POLLS, BECAUSE THAT IS WHAT THIS REPO DOES
//
// One fact read every five seconds while nothing is happening. Two seconds
// once the alarm is up and V is within reach of the compound. It stops for
// good when V is out of the Badlands or the gig ends. Nothing here is a
// field the save could lose: the alarm is a fact, and the per-guard "already
// turned" list is rebuilt from the bodies on the next tick after a load.

module CyberpunkCodes.Gig03

import CyberpunkCodes.Shared.*

public abstract class CCG03Alarm {
    // THE SECURITY-ROOM DOOR, captured in playtest 2026-09-11.
    public static func DoorPos() -> Vector4 {
        return new Vector4(-92.705, -5212.610, 87.155, 1.0);
    }

    // Tight: the next door in this compound is five metres away.
    public static func DoorRadius() -> Float { return 2.5; }

    public static func IsOurDoor(pos: Vector4) -> Bool {
        return Vector4.Distance(pos, CCG03Alarm.DoorPos()) <= CCG03Alarm.DoorRadius();
    }

    // The door has been opened. Starts the bar; turns nobody.
    public static func AlarmFact() -> String { return "cc_g03_alarm"; }
    // The bar has finished. This is what the guard pass waits on.
    public static func FoundFact() -> String { return "cc_g03_traced"; }
    public static func ArmedFact() -> String { return "cc_g03_data"; }
    public static func DoneFact() -> String { return "cc_g03_done"; }
    public static func LeftFact() -> String { return "cc_g03_badlands_left"; }

    // How far from the middle of the compound the guard pass still runs. The
    // walked perimeter is about 85 m across, and a guard chasing V out of the
    // gate is still worth turning if he streamed in late.
    public static func ReachMetres() -> Float { return 160.0; }

    // The search sphere for the guard pass, from the player. Covers the whole
    // compound from any point inside it.
    public static func SearchMetres() -> Float { return 120.0; }

    public static func IdlePoll() -> Float { return 5.0; }
    public static func LivePoll() -> Float { return 2.0; }

    // Is this record one of the site's soldiers. The census read them all as
    // `Character.bls_se_militech_*`, and the reinforcements this gig ships are
    // three of the same records.
    public static func IsMilitech(npc: ref<ScriptedPuppet>) -> Bool {
        let name: String = StrLower(TDBID.ToStringDEBUG(npc.GetRecordID()));
        return StrContains(name, "militech");
    }

    // THE FOUR CALLS. See the header for where each comes from.
    public static func TurnOnPlayer(game: GameInstance, npc: ref<ScriptedPuppet>,
                                    player: ref<PlayerPuppet>, injectThreat: Bool) -> Void {
        let agent: ref<AttitudeAgent> = npc.GetAttitudeAgent();
        if IsDefined(agent) && IsDefined(player) {
            agent.SetAttitudeTowards(player.GetAttitudeAgent(), EAIAttitude.AIA_Hostile);
        }
        let senses: ref<SenseComponent> = npc.GetSensesComponent();
        if IsDefined(senses) {
            senses.Toggle(true);
        }
        if injectThreat && IsDefined(player) {
            TargetTrackingExtension.InjectThreat(npc, player, 1.0, -1.0);
            NPCPuppet.ChangeHighLevelState(npc, gamedataNPCHighLevelState.Combat);
        }
    }

    // Set the alarm, once, and wake the trace so the bar starts on this frame
    // rather than on the trace system's next poll.
    public static func Raise(game: GameInstance) -> Void {
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        if !IsDefined(qs) {
            return;
        }
        if qs.GetFactStr(CCG03Alarm.AlarmFact()) > 0 {
            return;
        }
        qs.SetFactStr(CCG03Alarm.AlarmFact(), 1);
        // FULL MODULE NAME, or the container answers null (gotcha 50). The
        // trace runs the bar; it wakes this system itself when the bar ends.
        let trace: ref<AcceptableLossTrace> = GameInstance.GetScriptableSystemsContainer(game)
            .Get(n"CyberpunkCodes.Gig03.AcceptableLossTrace") as AcceptableLossTrace;
        if IsDefined(trace) {
            trace.Tick();
        }
    }

    // Called from every door action in the game, so it is ordered
    // cheapest-first: the position test throws out the whole world before
    // the executor is looked at and before a fact is read.
    //
    // `mustBeOpen` is the toggle case: a toggle can close a door as well as
    // open it, and closing one is not the beat.
    public static func OnDoorAction(door: ref<Door>, executor: wref<GameObject>,
                                    mustBeOpen: Bool) -> Void {
        if !IsDefined(door) || !CCG03Alarm.IsOurDoor(door.GetWorldPosition()) {
            return;
        }
        // THE PLAYER, AND NOBODY ELSE. A guard on his way through opens this
        // door too, and he is not the one being traced.
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
        // Recorded so a playtest can tell "the door fired" from "the cabinet
        // fallback fired": 1 is the door, Gig03_Places writes 2.
        if qs.GetFactStr("cc_g03_dbg_alarm_src") <= 0 {
            qs.SetFactStr("cc_g03_dbg_alarm_src", 1);
        }
        CCG03Alarm.Raise(game);
    }
}

// The four ways a player opens a door, each carrying who did it.
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
    // Guards already given the four calls, by id. A field, so a reload
    // forgets it and every body standing there is turned again on the first
    // tick, which is the safe direction: turning a guard twice costs four
    // calls, and missing one costs the beat.
    private let m_turned: array<EntityID>;

    private func OnAttach() -> Void {
        this.Schedule(CCG03Alarm.IdlePoll());
    }

    // ONE TICK IN FLIGHT AT A TIME. `Tick` can be called directly, by
    // Gig03_Alarm on the frame the door opens, while a scheduled tick is
    // still pending; without this the pending one would arrive later and
    // start a second poll loop beside the first. Every scheduled callback
    // carries the ticket it was issued with, and only the newest counts.
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
        // A direct call retires whatever was pending.
        this.m_ticket += 1;
        if this.m_settled {
            return;
        }
        let game: GameInstance = this.GetGameInstance();

        // EVERY SYSTEM FETCH IS CHECKED BEFORE IT IS USED. This attaches at the
        // main menu, where there is no quest system and no player.
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
        // NOT UNTIL THE TRACE HAS FINISHED. The door alone turns nobody.
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
            // Out of reach of the compound. The stars are the chase now.
            this.Schedule(CCG03Alarm.IdlePoll());
            return;
        }

        this.TurnTheGuards(game, qs, player, pos);
        this.Schedule(CCG03Alarm.LivePoll());
    }

    private func TurnTheGuards(game: GameInstance, qs: ref<QuestsSystem>,
                               player: ref<PlayerPuppet>, pos: Vector4) -> Void {
        // A crosshair query by default; Complete is what makes it a census
        // (the same lesson as the guard count in the dev menu).
        let query: TargetSearchQuery = TSQ_NPC();
        query.testedSet = TargetingSet.Complete;
        query.includeSecondaryTargets = false;
        query.ignoreInstigator = true;
        query.maxDistance = CCG03Alarm.SearchMetres();
        query.filterObjectByDistance = true;
        let parts: array<TS_TargetPartInfo>;
        GameInstance.GetTargetingSystem(game).GetTargetParts(player, query, parts);

        // Inside the wire they always know where V is. Outside, they keep
        // what they have and have to look.
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
        // READ BACK, because "asked" and "landed" are different numbers
        // (gotcha 78): how many Militech are standing there, and how many of
        // them have been turned at least once.
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
