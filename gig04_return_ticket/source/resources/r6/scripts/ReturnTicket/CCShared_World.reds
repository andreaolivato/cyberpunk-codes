module CyberpunkCodes.Shared.Gig04

public abstract class CCSharedWorld {

    public static func Spawn(record: TweakDBID, pos: Vector4, yaw: Float,
                             tag: CName) -> EntityID {
        let spec: ref<DynamicEntitySpec> = new DynamicEntitySpec();
        spec.recordID = record;
        spec.position = pos;
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

    public static func Near(pos: Vector4, anchor: Vector4, radiusXY: Float,
                            below: Float, above: Float) -> Bool {
        let dz: Float = pos.Z - anchor.Z;
        if dz < -below || dz > above {
            return false;
        }
        return Vector4.Distance2D(pos, anchor) <= radiusXY;
    }

    public static func InSafeArea(game: GameInstance, point: Vector4) -> Bool {
        let mgr: ref<SafeAreaManager> = GameInstance.GetSafeAreaManager(game);
        if !IsDefined(mgr) {
            return false;
        }
        return mgr.IsPointInSafeArea(point);
    }

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

    public static func Scatter(game: GameInstance, records: array<TweakDBID>,
                               center: Vector4, count: Int32, tag: CName,
                               radius: Float, step: Float) -> array<EntityID> {
        let placed: array<EntityID>;
        let player: ref<GameObject> = GameInstance.GetPlayerSystem(game)
            .GetLocalPlayerMainGameObject();
        if !IsDefined(player) {
            return placed;
        }
        let nav: ref<NavigationSystem> = GameInstance.GetNavigationSystem(game);
        let i: Int32 = 0;
        while i < count {
            // radians
            let angle: Float = Cast<Float>(i) * 2.4;
            let r: Float = radius + Cast<Float>(i % 3) * step;
            let pos: Vector4 = new Vector4(
                center.X + CosF(angle) * r,
                center.Y + SinF(angle) * r,
                center.Z,
                1.0);
            // no continue in redscript
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
