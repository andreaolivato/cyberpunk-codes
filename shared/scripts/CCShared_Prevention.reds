// The player's wanted level. See CCShared_World.reds for why the module name is
// rewritten per gig at build time.
//
// ---------------------------------------------------------------------------
// THERE IS NO SETTER. THE WANTED LEVEL IS A QUEUED REQUEST
//
// Read out of the game's own decompiled scripts, 2026-09-09, after eight
// guessed method names were all refused in game:
//
//     public class SetWantedLevel extends ScriptableSystemRequest {
//       public edit let m_wantedLevel: EPreventionHeatStage;
//       public edit let m_forceGreyStars: Bool;
//       public edit let m_resetGreyStars: Bool;
//       public edit let m_forcePlayerPositionAsLastCrimePoint: Bool;
//     }
//
//     private final func OnSetWantedLevel(evt: ref<SetWantedLevel>)
//
// `PreventionSystem` exposes nothing public that changes the heat. It exposes a
// HANDLER, and the way to reach a handler is to queue the request its signature
// names. `QueueRequest` is a native on `ScriptableSystem`, and every system in
// the game is driven this way: build the request, set its fields, queue it.
//
// The handler then switches the prevention system on, takes the player's
// position as the last crime point, and calls ChangeHeatStage with the reason
// "QuestEvent". That is what a quest wants, and it is why nothing here has to
// touch the star UI.
//
// ---------------------------------------------------------------------------
// IT DOES NOT WORK FROM CYBER ENGINE TWEAKS, AND THAT IS THE POINT OF THIS FILE
//
// Measured 2026-09-09. The same three lines in CET Lua report success every
// time and change nothing: the request is built, `m_wantedLevel` reads back as
// `Heat_3`, `QueueRequest` is accepted, and `GetHeatStage()` still answers
// `Heat_0` afterwards. Eight spellings of the construction were tried and all
// eight behaved identically.
//
// The reading is that Lua cannot hand the native side a request object it will
// accept, and the native silently drops what it is given rather than failing.
// Nothing announces it, which is what made it look like the wrong API for two
// rounds of testing.
//
// So this lives in redscript, where `new SetWantedLevel()` is a real
// allocation. DO NOT try to move it back into the dev menu for convenience.

module CyberpunkCodes.Shared

public abstract class CCSharedPrevention {

    public static func System(game: GameInstance) -> ref<PreventionSystem> {
        return GameInstance.GetScriptableSystemsContainer(game)
            .Get(n"PreventionSystem") as PreventionSystem;
    }

    // What the system itself thinks the heat is, which is not always what the
    // star meter shows. Useful when a request appears to do nothing: the two
    // answers apart tell you whether the request failed or whether something
    // downstream is suppressing the display.
    public static func Heat(game: GameInstance) -> Int32 {
        let ps: ref<PreventionSystem> = CCSharedPrevention.System(game);
        if !IsDefined(ps) {
            return -1;
        }
        return Cast<Int32>(ps.GetHeatStageAsInt());
    }

    // Three stars is the only level any gig here asks for, but the argument is
    // open because the mapping is the game's, not ours.
    public static func Stage(stars: Int32) -> EPreventionHeatStage {
        switch stars {
            case 1: return EPreventionHeatStage.Heat_1;
            case 2: return EPreventionHeatStage.Heat_2;
            case 3: return EPreventionHeatStage.Heat_3;
            case 4: return EPreventionHeatStage.Heat_4;
            case 5: return EPreventionHeatStage.Heat_5;
            default: return EPreventionHeatStage.Heat_0;
        }
    }

    // RAISE ONLY, NEVER LOWER. A gig that dropped the player's heat would clear
    // a chase it did not start, and the player has no way to attribute that to
    // us. Asking for less than the player already has is treated as asking for
    // nothing.
    //
    // `m_forcePlayerPositionAsLastCrimePoint` matters: without it the responders
    // head for wherever the last crime happened, which on a fresh save is
    // nowhere in particular. With it they come to V, which is the beat.
    public static func Wanted(game: GameInstance, stars: Int32) -> Bool {
        let ps: ref<PreventionSystem> = CCSharedPrevention.System(game);
        if !IsDefined(ps) {
            return false;
        }
        if CCSharedPrevention.Heat(game) >= stars {
            return false;
        }
        let evt: ref<SetWantedLevel> = new SetWantedLevel();
        evt.m_wantedLevel = CCSharedPrevention.Stage(stars);
        evt.m_forcePlayerPositionAsLastCrimePoint = true;
        ps.QueueRequest(evt);
        return true;
    }

    // DROP THE STARS, the way a quest does. `OnSetWantedLevel` given `Heat_0`
    // while a chase is on queues the game's own
    // `PreventionForceDeescalateRequest`: the stars blink for four seconds and
    // go out, the responders stand down, and the reason is logged as
    // "QuestEvent". Read out of preventionSystem.swift, 2026-09-11. Given
    // Heat_0 with no chase on it returns without doing anything, so this is
    // safe to call when the heat is already gone.
    //
    // THIS LOWERS THE PLAYER'S HEAT, WHICH `Wanted` DELIBERATELY NEVER DOES.
    // A gig may only call it for stars it raised itself, at a moment its story
    // has told the player is the escape. Gig 03 calls it once, on the frame V
    // crosses out of the Badlands, and nowhere else.
    public static func Clear(game: GameInstance) -> Bool {
        let ps: ref<PreventionSystem> = CCSharedPrevention.System(game);
        if !IsDefined(ps) {
            return false;
        }
        if CCSharedPrevention.Heat(game) <= 0 {
            return false;
        }
        let evt: ref<SetWantedLevel> = new SetWantedLevel();
        evt.m_wantedLevel = EPreventionHeatStage.Heat_0;
        ps.QueueRequest(evt);
        return true;
    }

    // WHICH DISTRICT THE PLAYER IS IN, as the game itself tracks it. The
    // prevention system keeps a stack of the district trigger areas the
    // player is inside, and its top is the current district. `District` is a
    // script class with `IsBadlands()` and `IsDogTown()` on it, both of which
    // look through a sub-district to its parent, so a player at a named
    // Badlands landmark still reads as Badlands.
    //
    // NULL MEANS UNKNOWN, NOT "NOWHERE". The stack is not saved: after a
    // load it is empty until the player's own district trigger fires again,
    // which is normally the same frame, and a caller has to treat null as
    // "ask again later" rather than as "outside".
    public static func District(game: GameInstance) -> wref<District> {
        let ps: ref<PreventionSystem> = CCSharedPrevention.System(game);
        if !IsDefined(ps) {
            return null;
        }
        return ps.GetCurrentDistrict();
    }

    // TELL THE RESPONDERS WHERE V IS. Stars raised by a request are stars the
    // police are SEARCHING under: `m_policeKnowsPlayerLocation` is false
    // until a unit reports combat, and while it is false the system will not
    // put units on foot around the player (`TrySpawnPoliceOnFootFallback`
    // returns on it), which is the only way it has of reaching a player who
    // is off the road. Read out of preventionSystem.swift, 2026-09-15, on a
    // playtest where the Badlands response never found a V standing off the
    // tarmac: the cars had no road to spawn on and the foot units were not
    // allowed.
    //
    // The game's own units report combat through
    // `CombatStartedRequestToPreventionSystem`, a public static, and this is
    // that call made on the player's behalf: it sets the flag, records V's
    // position as the last known one, and turns the stars from searching to
    // active. Sent again every few seconds it keeps all three current, so
    // the search never drifts 175 m from V and is never called off for
    // distance.
    //
    // ONLY WHILE A CHASE IS ALREADY ON. With no chase, the same request runs
    // the crime pipeline ("EnterCombat") and raises heat by itself, which a
    // gig must never do by accident; the caller checks the heat first. A V
    // in a vehicle still gets no foot units (`m_isPlayerMounted` blocks the
    // fallback outright), which is the game's rule and not this one's.
    public static func Locate(game: GameInstance) -> Bool {
        let ps: ref<PreventionSystem> = CCSharedPrevention.System(game);
        if !IsDefined(ps) {
            return false;
        }
        let psys: ref<PlayerSystem> = GameInstance.GetPlayerSystem(game);
        if !IsDefined(psys) {
            return false;
        }
        let player: ref<GameObject> = psys.GetLocalPlayerMainGameObject();
        if !IsDefined(player) {
            return false;
        }
        PreventionSystem.CombatStartedRequestToPreventionSystem(game, player);
        return true;
    }

    // HOW MANY RESPONSE VEHICLES ARE IN PLAY OR ON THEIR WAY: the ones the
    // registry holds plus the spawn tickets it is still waiting on.
    public static func Vehicles(game: GameInstance) -> Int32 {
        let ps: ref<PreventionSystem> = CCSharedPrevention.System(game);
        if !IsDefined(ps) {
            return 0;
        }
        let reg: ref<PoliceAgentRegistry> = PreventionSystem.GetAgentRegistry(game);
        if !IsDefined(reg) {
            return 0;
        }
        return reg.GetTotalVehicleCount() + reg.GetPendingVehicleTicketsCount();
    }

    // ADD A CHASE CAR TO THE RESPONSE, through the game's own spawner.
    //
    // The prevention system spawns its cars with
    // `PreventionSpawnSystem.RequestChaseVehicle(vehicle, passengers,
    // strategy)` and books the ticket in its registry, and both halves are
    // public. Read out of preventionSystem.swift, 2026-09-15
    // (`SpawnPoliceVehicle`), on a playtest where the Badlands response sent
    // few cars after a V driving off the road: the system's own spawner
    // refuses a car when the nearest road is further than its table allows
    // and falls back to men on foot, who cannot catch a vehicle. This call
    // makes the request the system would have made, with the strategy that
    // spawns a car anywhere in range and drives it at the player
    // (`GetToPlayerFromAnywhere`, strategy 5), and books the ticket so the
    // car is registered and chases the way every other response car does.
    //
    // The passengers are the vehicle record's own prevention crew
    // (`PreventionPassengers`), the count drawn between the record's min
    // and max, which is what the system does. `range` is how far from the
    // player the spawn may be, in metres; `minDirect` the straight-line
    // minimum, so it never appears in view.
    //
    // ONLY WHILE A CHASE IS ON, and the caller keeps a cap: a car requested
    // with no chase would be an unregistered vehicle with nobody to stand it
    // down, and a car per tick would be a traffic jam.
    public static func Car(game: GameInstance, vehicle: TweakDBID,
                           range: Vector2, minDirect: Float) -> Bool {
        let ps: ref<PreventionSystem> = CCSharedPrevention.System(game);
        if !IsDefined(ps) || !ps.IsChasingPlayer() {
            return false;
        }
        let spawn: ref<PreventionSpawnSystem> = GameInstance.GetPreventionSpawnSystem(game);
        let reg: ref<PoliceAgentRegistry> = PreventionSystem.GetAgentRegistry(game);
        if !IsDefined(spawn) || !IsDefined(reg) {
            return false;
        }
        let rec: ref<Vehicle_Record> = TweakDBInterface.GetVehicleRecord(vehicle);
        if !IsDefined(rec) || rec.GetPreventionPassengersCount() <= 0 {
            return false;
        }
        let pool: array<wref<Character_Record>>;
        rec.PreventionPassengers(pool);
        let count: Int32 = RandRange(rec.MinVehiclePassengersCount(),
                                     rec.MaxVehiclePassengersCount() + 1);
        if count < 1 {
            count = 1;
        }
        let crew: array<TweakDBID>;
        let i: Int32 = 0;
        while i < count {
            ArrayPush(crew, pool[RandRange(0, ArraySize(pool))].GetID());
            i += 1;
        }
        let strategy: ref<GetToPlayerFromAnywhereStrategyRequest> =
            GetToPlayerFromAnywhereStrategyRequest.Create(range, minDirect);
        let ticket: Uint32 = spawn.RequestChaseVehicle(vehicle, crew, strategy);
        if ticket == 0u {
            return false;
        }
        reg.CreateTicket(ticket, vehiclePoliceStrategy.GetToPlayerFromAnywhere);
        return true;
    }

    // SEND EVERY RESPONSE CAR STRAIGHT AT V, OFF THE ROAD IF NEED BE.
    //
    // A response car chases on the road network: its chase behaviour
    // navigates traffic lanes, and a V who leaves the tarmac is watched from
    // the nearest road and never followed (playtest 2026-09-15, "they
    // always get spawned on the main road and they never come to the
    // desert"). The vehicle AI has a second way to go after a target,
    // `AIVehicleFollowCommand`, with a `useTraffic` switch; off, the car
    // drives at the target directly, which is how a quest car follows V
    // across the Badlands. Read out of aiDriveCommandHandler.swift: the
    // follow handler maps `useTraffic` straight into the driving behaviour.
    //
    // This sends that command to every car the registry holds, target V,
    // no traffic, the chase's own 3 to 10 m spacing. SENT AGAIN ON EVERY
    // CALL, because the prevention system re-issues its own chase command
    // to a car whenever its strategy changes, and the later command wins;
    // a caller on a three-second loop keeps the follow on top. Whether the
    // crew keeps shooting from a car under a follow command rather than a
    // chase is not established; the first playtest of this is the
    // measurement. Returns how many cars were sent the command.
    public static func Follow(game: GameInstance) -> Int32 {
        let ps: ref<PreventionSystem> = CCSharedPrevention.System(game);
        if !IsDefined(ps) || !ps.IsChasingPlayer() {
            return 0;
        }
        let reg: ref<PoliceAgentRegistry> = PreventionSystem.GetAgentRegistry(game);
        let psys: ref<PlayerSystem> = GameInstance.GetPlayerSystem(game);
        if !IsDefined(reg) || !IsDefined(psys) {
            return 0;
        }
        let player: ref<GameObject> = psys.GetLocalPlayerMainGameObject();
        if !IsDefined(player) {
            return 0;
        }
        let sent: Int32 = 0;
        let agents: array<ref<VehicleAgent>> = reg.GetVehicleList();
        let i: Int32 = 0;
        while i < ArraySize(agents) {
            let car: ref<VehicleObject> = agents[i].unit;
            if IsDefined(car) {
                let cmd: ref<AIVehicleFollowCommand> = new AIVehicleFollowCommand();
                cmd.target = player;
                cmd.needDriver = true;
                cmd.useTraffic = false;
                cmd.distanceMin = 3.0;
                cmd.distanceMax = 10.0;
                cmd.stopWhenTargetReached = false;
                cmd.secureTimeOut = 0.0;
                let evt: ref<AICommandEvent> = new AICommandEvent();
                evt.command = cmd;
                car.QueueEvent(evt);
                sent += 1;
            }
            i += 1;
        }
        return sent;
    }
}
