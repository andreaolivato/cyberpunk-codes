module CyberpunkCodes.Shared.Gig02

public abstract class CCSharedAttitude {

    // 60s
    public static func MaxTries() -> Int32 { return 40; }

    public static func Neutral(game: GameInstance, id: EntityID) -> Void {
        CCSharedAttitude.Schedule(game, id, false, 0);
    }

    public static func Hostile(game: GameInstance, id: EntityID) -> Void {
        CCSharedAttitude.Schedule(game, id, true, 0);
    }

    public static func Schedule(game: GameInstance, id: EntityID, hostile: Bool,
                                tries: Int32) -> Void {
        let cb: ref<CCSharedAttitudeRetry> = new CCSharedAttitudeRetry();
        cb.game = game;
        cb.target = id;
        cb.hostile = hostile;
        cb.tries = tries;
        GameInstance.GetDelaySystem(game).DelayCallback(cb, 1.5, false);
    }

    public static func Apply(game: GameInstance, id: EntityID, hostile: Bool,
                             tries: Int32) -> Void {
        let obj: ref<GameObject> = GameInstance.GetDynamicEntitySystem()
            .GetEntity(id) as GameObject;
        if !IsDefined(obj) {
            obj = GameInstance.FindEntityByID(game, id) as GameObject;
        }
        if IsDefined(obj) {
            let agent: ref<AttitudeAgent> = obj.GetAttitudeAgent();
            if IsDefined(agent) {
                if hostile {
                    let player: ref<PlayerPuppet> = GetPlayer(game) as PlayerPuppet;
                    if IsDefined(player) {
                        agent.SetAttitudeTowards(player.GetAttitudeAgent(), EAIAttitude.AIA_Hostile);
                        return;
                    }
                } else {
                    agent.SetAttitudeGroup(n"neutral");
                    return;
                }
            }
        }
        if tries < CCSharedAttitude.MaxTries() {
            CCSharedAttitude.Schedule(game, id, hostile, tries + 1);
        }
    }
}

public class CCSharedAttitudeRetry extends DelayCallback {
    public let game: GameInstance;
    public let target: EntityID;
    public let hostile: Bool;
    public let tries: Int32;
    public func Call() -> Void {
        CCSharedAttitude.Apply(this.game, this.target, this.hostile, this.tries);
    }
}
