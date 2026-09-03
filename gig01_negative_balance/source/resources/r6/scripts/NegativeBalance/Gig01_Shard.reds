module CyberpunkCodes.Gig01

public abstract class CCG01Shard {
    public static func Path() -> String {
        return "onscreens/emails/quests/street_stories/cc_g01_negative_balance/onscreens/cc_g01_shard_note";
    }

    // on the desk
    public static func ObjectSpot() -> Vector4 {
        return new Vector4(-244.931305, -1454.17786, 15.3999996, 1.0);
    }

    public static func ItemId() -> TweakDBID { return t"Items.cc_g01_shard"; }

    public static func HasBeenRead(game: GameInstance) -> Bool {
        let jm: ref<JournalManager> = GameInstance.GetJournalManager(game);
        if !IsDefined(jm) {
            return false;
        }
        let entry: ref<JournalEntry> =
            jm.GetEntryByString(CCG01Shard.Path(), "gameJournalOnscreen");
        if !IsDefined(entry) {
            return false;
        }
        return jm.IsEntryVisited(entry);
    }

    public static func OpenFact() -> CName { return n"cc_g01_shard_open"; }
    public static func ReadFact() -> CName { return n"cc_g01_shard_read"; }

    public static func Open(game: GameInstance) -> Bool {
        let jm: ref<JournalManager> = GameInstance.GetJournalManager(game);
        if !IsDefined(jm) {
            return false;
        }
        jm.ChangeEntryState(CCG01Shard.Path(), "gameJournalOnscreen",
                            gameJournalEntryState.Active, JournalNotifyOption.Notify);
        let entry: ref<JournalOnscreen> =
            jm.GetEntryByString(CCG01Shard.Path(), "gameJournalOnscreen") as JournalOnscreen;
        if !IsDefined(entry) {
            return false;
        }
        let evt: ref<NotifyShardRead> = new NotifyShardRead();
        evt.entry = entry;
        evt.title = entry.GetTitle();
        evt.text = entry.GetDescription();
        evt.m_imageId = entry.GetIconID();
        evt.isCrypted = false;
        GameInstance.GetUISystem(game).QueueEvent(evt);
        return true;
    }
}

@wrapMethod(PopupsManager)
protected cb func OnShardReadClosed(data: ref<inkGameNotificationData>) -> Bool {
    let result: Bool = wrappedMethod(data);
    let game: GameInstance = this.GetPlayerControlledObject().GetGame();
    let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
    if IsDefined(qs)
        && qs.GetFact(n"cc_g01_done") <= 0
        && qs.GetFact(CCG01Shard.OpenFact()) > 0
        && qs.GetFact(CCG01Shard.ReadFact()) == 0 {
        qs.SetFact(CCG01Shard.ReadFact(), 1);
    }
    return result;
}
