// Map markers a script registers at runtime, as opposed to the pins a gig
// authors in its journal. See CCShared_World.reds for why the module name is
// rewritten per gig at build time.
//
// A runtime marker is the right tool when the position is not known until the
// gig is running, or when it moves. It carries no localized caption: the
// journal pin is the one that can be named, and this one only has a debug
// caption that players never see.
module CyberpunkCodes.Shared

public abstract class CCSharedMappins {

    // Put one on the map and hand back its id. Keep that id: it is the only way
    // to move or remove the marker afterwards.
    public static func Show(game: GameInstance, spot: Vector4) -> NewMappinID {
        let ms: ref<MappinSystem> = GameInstance.GetMappinSystem(game);
        let id: NewMappinID;
        if !IsDefined(ms) {
            return id;
        }
        // `MappinData`, NOT `gamemappinsMappinData`. A journal resource spells it
        // the long way and redscript does not know that name at all
        // (`unresolved type`); the script-visible struct is the short one, and it
        // carries exactly five fields - mappinType, variant, debugCaption,
        // visibleThroughWalls, scriptData. There is no `active`: a registered
        // mappin is live by definition, and a journal pin's `active` flag
        // belongs to the authored pin, not to this.
        let data: MappinData;
        // The same two ids a gig's journal pins carry, so it reads as the gig's
        // own objective marker rather than something a mod bolted on.
        data.mappinType = t"Mappins.QuestStaticMappinDefinition";
        data.variant = gamedataMappinVariant.QuestGiverVariant;
        data.visibleThroughWalls = true;
        return ms.RegisterMappin(data, spot);
    }

    // MOVE the marker already on screen rather than registering a second one and
    // dropping the first: that would leave the old one visible for a frame and,
    // if the unregister ever missed, for the rest of the save.
    public static func Move(game: GameInstance, id: NewMappinID, spot: Vector4) -> Void {
        let ms: ref<MappinSystem> = GameInstance.GetMappinSystem(game);
        if IsDefined(ms) {
            ms.SetMappinPosition(id, spot);
        }
    }

    // ALWAYS PAIR A Show WITH A Hide THAT RUNS EVEN IF THE GIG ENDS EARLY. A
    // marker registered and never removed sits on the map for the rest of that
    // save, and nobody would attribute it to the mod.
    public static func Hide(game: GameInstance, id: NewMappinID) -> Void {
        let ms: ref<MappinSystem> = GameInstance.GetMappinSystem(game);
        if IsDefined(ms) {
            ms.UnregisterMappin(id);
        }
    }
}
