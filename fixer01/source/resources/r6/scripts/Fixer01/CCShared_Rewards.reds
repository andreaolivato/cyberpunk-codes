module CyberpunkCodes.Shared.Fixer01

public abstract class CCSharedRewards {

    public static func Pay(game: GameInstance, player: ref<PlayerPuppet>,
                           eddies: Int32, streetCred: Int32) -> Void {
        if eddies > 0 {
            GameInstance.GetTransactionSystem(game).GiveItemByTDBID(player, t"Items.money", eddies);
        }
        if streetCred > 0 {
            RPGManager.AwardExperienceInstantly(player, streetCred, gamedataProficiencyType.StreetCred);
        }
    }
}
