module CyberpunkCodes.Shared.Gig04

public abstract class CCSharedMappins {

    public static func Show(game: GameInstance, spot: Vector4) -> NewMappinID {
        let ms: ref<MappinSystem> = GameInstance.GetMappinSystem(game);
        let id: NewMappinID;
        if !IsDefined(ms) {
            return id;
        }
        let data: MappinData;
        data.mappinType = t"Mappins.QuestStaticMappinDefinition";
        data.variant = gamedataMappinVariant.QuestGiverVariant;
        data.visibleThroughWalls = true;
        return ms.RegisterMappin(data, spot);
    }

    public static func Move(game: GameInstance, id: NewMappinID, spot: Vector4) -> Void {
        let ms: ref<MappinSystem> = GameInstance.GetMappinSystem(game);
        if IsDefined(ms) {
            ms.SetMappinPosition(id, spot);
        }
    }

    public static func Hide(game: GameInstance, id: NewMappinID) -> Void {
        let ms: ref<MappinSystem> = GameInstance.GetMappinSystem(game);
        if IsDefined(ms) {
            ms.UnregisterMappin(id);
        }
    }
}
