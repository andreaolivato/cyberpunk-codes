// Paying the player. See CCShared_World.reds for why the module name is
// rewritten per gig at build time.
module CyberpunkCodes.Shared

public abstract class CCSharedRewards {

    // Eddies and Street Cred, the two a side gig hands out.
    //
    // GUARD THE CALL WITH A FACT, NOT A SCRIPT FIELD. Script fields reset on
    // load, so a reward gated by one is re-granted every time the player reloads
    // the save, which is a money printer. The fact is the only thing that
    // survives, and the guard belongs in the gig because the fact name does.
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
