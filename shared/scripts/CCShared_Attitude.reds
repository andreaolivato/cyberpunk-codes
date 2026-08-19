// Making a script-spawned NPC hostile or neutral, and waiting for him to exist.
//
// See CCShared_World.reds for why the module name is rewritten per gig at build
// time.
//
// THE PROBLEM THIS SOLVES IS TIMING, NOT ATTITUDE. `CreateEntity` queues rather
// than creates, so the puppet is not resolvable in the tick it was asked for.
// Setting an attitude straight after a spawn silently does nothing, and the
// symptom is a guard who ignores the player.
module CyberpunkCodes.Shared

public abstract class CCSharedAttitude {

    // HOW LONG AN ATTITUDE MAY TAKE TO STICK. 1.5 s a try, so this is 60 s.
    //
    // It was 6 tries, 10.5 s, and that budget was sized on one machine against
    // an all-at-once spawn burst. On a slower one, or a heavily modded load
    // order, a guard who takes longer than that to stream in keeps his record's
    // default attitude. For a street-story security record that default does
    // not treat the player as an enemy, so the symptom is "the guards ignore
    // me": the original bug arriving by a new route, from a budget rather than
    // from a missing call.
    //
    // The cost of the higher cap is only paid by an entity that never resolves
    // at all. Everyone else returns on the try that finds him.
    public static func MaxTries() -> Int32 { return 40; }

    // Move a spawned NPC out of the hostile group so he will not open fire.
    public static func Neutral(game: GameInstance, id: EntityID) -> Void {
        CCSharedAttitude.Schedule(game, id, false, 0);
    }

    // Make him an enemy of the player, and of nobody else. See Apply.
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

    // One attempt, then reschedule itself if the body is not there yet.
    public static func Apply(game: GameInstance, id: EntityID, hostile: Bool,
                             tries: Int32) -> Void {
        let obj: ref<GameObject> = GameInstance.GetDynamicEntitySystem().GetEntity(id) as GameObject;
        if IsDefined(obj) {
            let agent: ref<AttitudeAgent> = obj.GetAttitudeAgent();
            if IsDefined(agent) {
                if hostile {
                    // HOSTILE TO THE PLAYER, NOT HOSTILE TO EVERYONE.
                    //
                    // An earlier version also called SetAttitudeGroup(n"hostile")
                    // and playtesting caught what that means: "those guards start
                    // killing existing NPCs... this happens only after they see
                    // me and start shooting at me." n"hostile" is not "hostile to
                    // the player", it is a GROUP, and a member of it is at war
                    // with every other group in the room, its own colleagues
                    // included. The moment combat woke them up they picked
                    // targets by group and their own side qualified.
                    //
                    // SetAttitudeTowards is the pairwise version and it is the
                    // one that was wanted: it makes this NPC an enemy of THIS
                    // player and changes nothing else, leaving his record's own
                    // affiliation exactly as it was.
                    let player: ref<PlayerPuppet> = GetPlayer(game) as PlayerPuppet;
                    if IsDefined(player) {
                        agent.SetAttitudeTowards(player.GetAttitudeAgent(), EAIAttitude.AIA_Hostile);
                        return;
                    }
                } else {
                    // SetAttitudeGroup is how vanilla moves an NPC between sides
                    // (dynamicSpawnSystem.swift:72 sets n"hostile" exactly this
                    // way).
                    agent.SetAttitudeGroup(n"neutral");
                    return;
                }
            }
        }
        // Not streamed in yet. Try again rather than silently give up and leave
        // him shooting through his own dialogue.
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
