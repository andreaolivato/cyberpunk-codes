// Spawning, proximity and NPC plumbing that has nothing to do with any one gig.
//
// VENDORED PER MOD AT BUILD TIME. This file declares `module
// CyberpunkCodes.Shared`, and tools\vendor-shared.ps1 rewrites that to
// `CyberpunkCodes.Shared.<Gig>` as it copies the file into each mod's script
// folder. That is not tidiness, it is the difference between two of our gigs
// coexisting and neither of them running:
//
//   same module + same class name, two files  ->  [SYM_REDEFINITION], and it
//       fails the WHOLE redscript bundle, so every other redscript mod the
//       player has installed stops working too
//   different module + same class name        ->  compiles clean
//
// Both were tested against scc on 2026-08-16 rather than assumed. So class
// names here do NOT need a per-gig prefix; the module rename is sufficient and
// is the only thing the vendoring step touches.
module CyberpunkCodes.Shared

public abstract class CCSharedWorld {

    // Spawn a puppet from a TweakDB character record at a position and yaw,
    // tagged so it can be found again through DynamicEntitySystem.
    //
    // Quest-graph questSpawnSet nodes can only reference EXISTING community
    // spawn phases, so they are unusable for an NPC a mod places itself. Every
    // NPC our gigs place is script-spawned through this.
    public static func Spawn(record: TweakDBID, pos: Vector4, yaw: Float,
                             tag: CName) -> EntityID {
        let spec: ref<DynamicEntitySpec> = new DynamicEntitySpec();
        spec.recordID = record;
        spec.position = pos;
        // Build the angles field by field: EulerAngles is a native struct with
        // no complete script definition, so passing constructor arguments is
        // undefined behaviour and the compiler warns about it.
        let angles: EulerAngles;
        angles.Yaw = yaw;
        spec.orientation = EulerAngles.ToQuat(angles);
        spec.persistState = false;
        spec.persistSpawn = false;
        spec.alwaysSpawned = false;
        spec.spawnInView = true;
        spec.active = true;
        spec.tags = [tag];
        return GameInstance.GetDynamicEntitySystem().CreateEntity(spec);
    }

    // A cylinder test, deliberately asymmetric in Z.
    //
    // THE ASYMMETRY IS LOAD-BEARING and it is not fussiness: Night City has
    // roads tunnelling under buildings, so a trigger whose floor reaches far
    // enough down fires for a player driving past underneath. Keep `below`
    // tight and let `above` be generous.
    public static func Near(pos: Vector4, anchor: Vector4, radiusXY: Float,
                            below: Float, above: Float) -> Bool {
        let dz: Float = pos.Z - anchor.Z;
        if dz < -below || dz > above {
            return false;
        }
        return Vector4.Distance2D(pos, anchor) <= radiusXY;
    }

    // Is the player currently in a device UI? Two separate blackboard flags,
    // because the terminal zoom and an ordinary device interaction are not the
    // same state and a beat that waits for "off the screen" must clear both.
    public static func IsUsingDevice(game: GameInstance,
                                     player: ref<PlayerPuppet>) -> Bool {
        let bb: ref<IBlackboard> = GameInstance.GetBlackboardSystem(game)
            .GetLocalInstanced(player.GetEntityID(), GetAllBlackboardDefs().PlayerStateMachine);
        if !IsDefined(bb) {
            return false;
        }
        if bb.GetBool(GetAllBlackboardDefs().PlayerStateMachine.IsUIZoomDevice) {
            return true;
        }
        return bb.GetBool(GetAllBlackboardDefs().PlayerStateMachine.IsInteractingWithDevice);
    }

    // Mute or unmute a base-game NPC's ambient barks.
    //
    // ALWAYS PAIR THE UNMUTE WITH A PATH THAT RUNS EVEN IF THE GIG ENDS EARLY.
    // Leaving this off on a base-game NPC is a permanently silent character for
    // the rest of that save, it is invisible until someone walks past hours
    // later, and nobody would ever attribute it to the mod.
    public static func SetVoiceset(obj: ref<GameObject>, on: Bool) -> Void {
        let ev: ref<entChangeVoicesetStateEvent> = new entChangeVoicesetStateEvent();
        ev.enableVoicesetLines = on;
        ev.enableVoicesetGrunts = true;
        if !on {
            let block: entVoicesetInputToBlock;
            block.input = n"greeting";
            block.blockSpecificVariation = false;
            block.variationNumber = 0u;
            ArrayPush(ev.inputsToBlock, block);
        }
        obj.QueueEvent(ev);
    }

    // Scatter a squad around a point, and drop anyone who cannot stand there.
    //
    // EVERY SPAWN POINT IS SNAPPED TO WALKABLE GROUND, and that is the whole
    // reason this exists. Playtest, on a version that scattered by pure
    // trigonometry: "there are 2 guards inside a wall and one outside on a ledge
    // that is impossible to reach." Both are one bug - a guard landed wherever
    // the circle happened to fall, geometry or no geometry. A guard inside a
    // wall cannot be fought and a guard on an unreachable ledge cannot be
    // finished, so both stall a room the player is supposed to clear.
    //
    // NavigationSystem.FindPointInSphereOnlyHumanNavmesh answers exactly the
    // right question, "give me a point near here that a human can stand on", and
    // it is what vanilla's own GetNearestNavmeshPointBelow is built from
    // (navigationSystem.swift:29). If it says OK we use ITS point; anything else
    // and that one is dropped rather than placed in a wall.
    //
    // A squad is allowed to come out one or two short. Five guards in a room
    // that can all be fought is a better encounter than seven where two are
    // furniture.
    //
    // The ring is passed in rather than fixed here: how tight it should be is a
    // property of the room, and the caller is the only thing that knows the
    // room. `radius` is the innermost ring and `step` the gap between three
    // concentric ones.
    //
    // Returns the ids actually placed, so the caller can set an attitude on
    // them (CCSharedAttitude) or hold them for later.
    public static func Scatter(game: GameInstance, records: array<TweakDBID>,
                               center: Vector4, count: Int32, tag: CName,
                               radius: Float, step: Float) -> array<EntityID> {
        let nav: ref<NavigationSystem> = GameInstance.GetNavigationSystem(game);
        let placed: array<EntityID>;
        let i: Int32 = 0;
        while i < count {
            let angle: Float = Cast<Float>(i) * 2.4;
            let r: Float = radius + Cast<Float>(i % 3) * step;
            let pos: Vector4 = new Vector4(
                center.X + CosF(angle) * r,
                center.Y + SinF(angle) * r,
                center.Z,
                1.0);
            // `walkable` rather than an early `continue`: REDSCRIPT HAS NO
            // `continue`. It compiles as far as "unresolved reference", which
            // reads like a missing function rather than a missing keyword.
            let walkable: Bool = true;
            if IsDefined(nav) {
                let found: NavigationFindPointResult =
                    nav.FindPointInSphereOnlyHumanNavmesh(pos, 2.0, NavGenAgentSize.Human, true);
                if Equals(found.status, worldNavigationRequestStatus.OK) {
                    pos = found.point;
                } else {
                    walkable = false;
                }
            }
            if walkable {
                ArrayPush(placed, CCSharedWorld.Spawn(
                    records[i % ArraySize(records)], pos, angle * 57.3, tag));
            }
            i += 1;
        }
        return placed;
    }
}
