module CyberpunkCodes.Shared.Gig03

public abstract class CCSharedPrevention {

    public static func System(game: GameInstance) -> ref<PreventionSystem> {
        return GameInstance.GetScriptableSystemsContainer(game)
            .Get(n"PreventionSystem") as PreventionSystem;
    }

    public static func Heat(game: GameInstance) -> Int32 {
        let ps: ref<PreventionSystem> = CCSharedPrevention.System(game);
        if !IsDefined(ps) {
            return -1;
        }
        return Cast<Int32>(ps.GetHeatStageAsInt());
    }

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

    public static func Wanted(game: GameInstance, stars: Int32) -> Bool {
        let ps: ref<PreventionSystem> = CCSharedPrevention.System(game);
        if !IsDefined(ps) {
            return false;
        }
        // raise only
        if CCSharedPrevention.Heat(game) >= stars {
            return false;
        }
        let evt: ref<SetWantedLevel> = new SetWantedLevel();
        evt.m_wantedLevel = CCSharedPrevention.Stage(stars);
        evt.m_forcePlayerPositionAsLastCrimePoint = true;
        ps.QueueRequest(evt);
        return true;
    }

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

    public static func District(game: GameInstance) -> wref<District> {
        let ps: ref<PreventionSystem> = CCSharedPrevention.System(game);
        if !IsDefined(ps) {
            return null;
        }
        return ps.GetCurrentDistrict();
    }

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
                // off road
                cmd.useTraffic = false;
                // metres
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
