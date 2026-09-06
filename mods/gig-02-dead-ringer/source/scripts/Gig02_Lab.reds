// THE POSE LAB, 2026-09-04. Global functions the CET dev menu calls, so the
// compiler validates every engine call and the Lua only presses buttons.
//
// Why it exists: three playtests of the merc's kneel read as a snap from
// standing to the ground, through a scene-side workspot, then a scene node
// sending him to a spot of ours. The lab spawns a body at the merc's post,
// where the cast sector ships one AI spot per candidate pose, and tries every
// lever the engine has for moving a body into a pose: the AI's own use-workspot
// command with and without the walk-in, the workspot system's stop, the
// knock-down status effects with and without recovery, and the high-level
// state. See docs/design.md, "The pose lab".
//
// NOTHING HERE IS USED BY THE GIG, and that is enforced rather than assumed:
// the two functions the gig did call, `CCLab_UseWorkspot` and `CCLab_StripAll`,
// moved into Gig02_Encounter.reds on 2026-09-06 (they keep their names because
// the menu calls them too). So this file is dev tooling only, and
// build-release.ps1 drops it from the zip along with the menu itself.

// A body at a place, facing a way. Tagged so the lab can find and remove it.
public func CCLab_Spawn(record: String, x: Float, y: Float, z: Float, yaw: Float) -> EntityID {
    let spec: ref<DynamicEntitySpec> = new DynamicEntitySpec();
    spec.recordID = TDBID.Create(record);
    spec.position = new Vector4(x, y, z, 1.0);
    spec.orientation = EulerAngles.ToQuat(new EulerAngles(0.0, 0.0, yaw));
    spec.persistState = false;
    spec.persistSpawn = false;
    spec.alwaysSpawned = false;
    spec.spawnInView = true;
    spec.active = true;
    spec.tags = [n"cc_g02_lab"];
    return GameInstance.GetDynamicEntitySystem().CreateEntity(spec);
}

public func CCLab_Despawn(id: EntityID) -> Void {
    GameInstance.GetDynamicEntitySystem().DeleteEntity(id);
}

// THE SAME RECORD, STANDING IN FRONT OF THE PLAYER, facing back at him
// (2026-09-06, backlog 42). The other half of the appearance A/B: the quest
// arm puts Char in the holocall studio and this puts a second body of the same
// record a few metres away, so both are seen at once and under one light.
//
// THE APPEARANCE IS DELIBERATELY NOT SET HERE. The question is what a body of
// `Character.cc_g02_char` wears when nothing but the record decides, which is
// the closest thing to what the studio body may be getting. `appearanceName`
// on the spec is the knob to add if that turns out to be worth a second
// button.
//
// Placed by the player's own forward vector rather than by a captured spot, so
// it works anywhere: run it in daylight on a street and again in the netrunner
// chair room, and the lighting stops being a variable.
public func CCLab_SpawnInFront(record: String, distance: Float) -> EntityID {
    let none: EntityID;
    let player: ref<PlayerPuppet> = GameInstance.GetPlayerSystem(GetGameInstance())
        .GetLocalPlayerMainGameObject() as PlayerPuppet;
    if !IsDefined(player) {
        return none;
    }
    let pos: Vector4 = player.GetWorldPosition();
    let fwd: Vector4 = player.GetWorldForward();
    let at: Vector4 = new Vector4(pos.X + fwd.X * distance,
                                  pos.Y + fwd.Y * distance,
                                  pos.Z, 1.0);
    // Facing the player. The body stands along V's forward, so turning it a
    // half circle from V's own yaw points it back at him. No trigonometry:
    // `AtanOf` does not exist in redscript and the first version of this line
    // used it (2026-09-06).
    let yaw: Float = player.GetWorldYaw() + 180.0;
    return CCLab_Spawn(record, at.X, at.Y, at.Z, yaw);
}

// Out of whatever workspot the body is in, through its exit animation.
public func CCLab_StopWorkspot(npc: ref<GameObject>) -> Void {
    GameInstance.GetWorkspotSystem(npc.GetGame()).StopNpcInWorkspot(npc);
}

// Knock-downs: Defeated, DefeatedWithRecover, Knockdown, KnockdownInfinite, Sleep.
public func CCLab_Status(npc: ref<GameObject>, id: String, apply: Bool) -> Void {
    if apply {
        StatusEffectHelper.ApplyStatusEffect(npc, TDBID.Create(id));
    } else {
        StatusEffectHelper.RemoveStatusEffect(npc, TDBID.Create(id));
    }
}

public func CCLab_Relax(npc: ref<GameObject>, relaxed: Bool) -> Void {
    if relaxed {
        NPCPuppet.ChangeHighLevelState(npc, gamedataNPCHighLevelState.Relaxed);
    } else {
        NPCPuppet.ChangeHighLevelState(npc, gamedataNPCHighLevelState.Combat);
    }
}

// The bodies the lab spawned, so the menu can act on them after a reload.
public func CCLab_Find(game: GameInstance) -> array<EntityID> {
    return GameInstance.GetDynamicEntitySystem().GetTaggedIDs(n"cc_g02_lab");
}

// THE SHARD IN HIS POCKET. A Defeated body opens the game's own loot list when
// looked at; whatever is in the NPC's inventory is on it. This puts an item
// there, so the lab can show the shard beside his ammo and eddies before the
// gig does it for real (2026-09-05).
public func CCLab_GiveItem(npc: ref<GameObject>, item: String, count: Int32) -> Bool {
    let ts: ref<TransactionSystem> = GameInstance.GetTransactionSystem(npc.GetGame());
    return ts.GiveItem(npc, ItemID.FromTDBID(TDBID.Create(item)), count);
}

public func CCLab_HasItem(obj: ref<GameObject>, item: String) -> Bool {
    let ts: ref<TransactionSystem> = GameInstance.GetTransactionSystem(obj.GetGame());
    return ts.HasItem(obj, ItemID.FromTDBID(TDBID.Create(item)));
}

// HIS GUN OFF THE LOOT LIST. The same list shows the weapon a Defeated body
// carries, which reads as robbing a corpse; this removes every weapon item.
public func CCLab_StripWeapons(npc: ref<GameObject>) -> Int32 {
    let ts: ref<TransactionSystem> = GameInstance.GetTransactionSystem(npc.GetGame());
    let items: array<wref<gameItemData>>;
    ts.GetItemList(npc, items);
    let removed: Int32 = 0;
    let i: Int32 = 0;
    while i < ArraySize(items) {
        let id: ItemID = items[i].GetID();
        if RPGManager.IsItemWeapon(id) {
            ts.RemoveItem(npc, id, items[i].GetQuantity());
            removed += 1;
        }
        i += 1;
    }
    return removed;
}

// WHERE THE CROSSHAIR LANDS ON STATIC GEOMETRY (2026-09-05): the same ray the
// parlor scan uses, for measuring a machine that is a static mesh and so has
// no entity to capture. Returns the hit with W = 1, or W = 0 for no hit within
// 40 m. The dev menu writes it to captured_positions.txt.
public func CCLab_RayHit(player: ref<GameObject>) -> Vector4 {
    let none: Vector4 = new Vector4(0.0, 0.0, 0.0, 0.0);
    let puppet: ref<PlayerPuppet> = player as PlayerPuppet;
    if !IsDefined(puppet) {
        return none;
    }
    let cam: ref<CameraComponent> = puppet.GetFPPCameraComponent();
    if !IsDefined(cam) {
        return none;
    }
    let m: Matrix = cam.GetLocalToWorld();
    let from: Vector4 = Matrix.GetTranslation(m);
    let to: Vector4 = from + Matrix.GetAxisY(m) * 40.0;
    let hit: TraceResult;
    if GameInstance.GetSpatialQueriesSystem(player.GetGame()).SyncRaycastByCollisionGroup(
           from, to, n"Static", hit, false, false) {
        let p: Vector4 = Cast<Vector4>(hit.position);
        return new Vector4(p.X, p.Y, p.Z, 1.0);
    }
    return none;
}

// THE NODE PROBE, backlog 11's recipe: does a named node reach a live entity?
// W = 1 with the entity's position; W = 0.5 when the name resolves and no
// entity is behind it (the node is not streamed, or never instantiated);
// W = 0 when the name means nothing.
public func CCLab_NodeEntity(player: ref<GameObject>, path: String) -> Vector4 {
    let nref: NodeRef = CreateNodeRef(path);
    let root: GlobalNodeRef;
    let g: GlobalNodeRef = ResolveNodeRef(nref, root);
    if !GlobalNodeRef.IsDefined(g) {
        return new Vector4(0.0, 0.0, 0.0, 0.0);
    }
    let id: EntityID = Cast<EntityID>(g);
    let ent: ref<Entity> = GameInstance.FindEntityByID(player.GetGame(), id);
    if !IsDefined(ent) {
        return new Vector4(0.0, 0.0, 0.0, 0.5);
    }
    let p: Vector4 = ent.GetWorldPosition();
    return new Vector4(p.X, p.Y, p.Z, 1.0);
}

// EVERY QUEST MAP PIN THE GAME HOLDS RIGHT NOW, one line each: variant,
// whether the engine treats it as an AREA pin (the minimap's outline
// controller is chosen on that), whether it is the tracked one, and where.
// This is how the area test is read without guessing from the minimap.
public func CCLab_MappinReport(player: ref<GameObject>) -> array<String> {
    let out: array<String>;
    let ms: ref<MappinSystem> = GameInstance.GetMappinSystem(player.GetGame());
    if !IsDefined(ms) {
        ArrayPush(out, "no mappin system");
        return out;
    }
    let pins: array<ref<IMappin>>;
    ms.GetMappins(gamemappinsMappinTargetType.World, pins);
    let me: Vector4 = player.GetWorldPosition();
    let i: Int32 = 0;
    while i < ArraySize(pins) {
        let m: ref<IMappin> = pins[i];
        if IsDefined(m) && m.IsQuestMappin() {
            let p: Vector4 = m.GetWorldPosition();
            ArrayPush(out, "quest pin  variant=" +
                EnumValueToString("gamedataMappinVariant", Cast<Int64>(EnumInt(m.GetVariant()))) +
                "  area=" + ToString(m.IsQuestAreaMappin()) +
                "  tracked=" + ToString(m.IsPlayerTracked()) +
                "  at " + FloatToStringPrec(p.X, 1) + ", " + FloatToStringPrec(p.Y, 1) +
                ", " + FloatToStringPrec(p.Z, 1) +
                "  (" + FloatToStringPrec(Vector4.Distance(me, p), 0) + " m from V)");
        }
        i += 1;
    }
    ArrayPush(out, ToString(ArraySize(pins)) + " world mappins in all");
    return out;
}

