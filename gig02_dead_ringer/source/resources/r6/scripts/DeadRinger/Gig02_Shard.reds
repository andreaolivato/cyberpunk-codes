module CyberpunkCodes.Gig02

public abstract class CCGig02Shard {
    public static func ShardPath() -> String {
        return "onscreens/emails/quests/street_stories/cc_g02_dead_ringer/onscreens/cc_g02_shard_note";
    }

    public static func ShardItem() -> TweakDBID { return t"Items.cc_g02_shard"; }

    public static func ShardOpenFact() -> CName { return n"cc_g02_merc_down"; }
    public static func ShardReadFact() -> CName { return n"cc_g02_proof_read"; }

    public static func HasBeenRead(game: GameInstance, path: String) -> Bool {
        let jm: ref<JournalManager> = GameInstance.GetJournalManager(game);
        if !IsDefined(jm) {
            return false;
        }
        let entry: ref<JournalEntry> = jm.GetEntryByString(path, "gameJournalOnscreen");
        if !IsDefined(entry) {
            return false;
        }
        // visited, not active
        return jm.IsEntryVisited(entry);
    }

    public static func Open(game: GameInstance, path: String) -> Bool {
        let jm: ref<JournalManager> = GameInstance.GetJournalManager(game);
        if !IsDefined(jm) {
            return false;
        }
        jm.ChangeEntryState(path, "gameJournalOnscreen",
                            gameJournalEntryState.Active, JournalNotifyOption.Notify);
        let entry: ref<JournalOnscreen> =
            jm.GetEntryByString(path, "gameJournalOnscreen") as JournalOnscreen;
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
protected cb func OnShardRead(evt: ref<NotifyShardRead>) -> Bool {
    let result: Bool = wrappedMethod(evt);
    let game: GameInstance = this.GetPlayerControlledObject().GetGame();
    let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
    let ours: String = GetLocalizedTextByKey(n"cc-g02-shard-title");
    if IsDefined(qs) && qs.GetFact(n"cc_g02_done") == 0
        // both forms
        && (Equals(evt.title, ours) || Equals(GetLocalizedText(evt.title), ours)) {
        qs.SetFact(n"cc_g02_shard_open", 1);
    }
    return result;
}

@wrapMethod(PopupsManager)
protected cb func OnShardReadClosed(data: ref<inkGameNotificationData>) -> Bool {
    let result: Bool = wrappedMethod(data);
    let game: GameInstance = this.GetPlayerControlledObject().GetGame();
    let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
    if !IsDefined(qs) {
        return result;
    }
    if qs.GetFact(n"cc_g02_done") > 0 {
        return result;
    }
    if qs.GetFact(n"cc_g02_shard_open") > 0
        && qs.GetFact(CCGig02Shard.ShardReadFact()) == 0 {
        qs.SetFact(CCGig02Shard.ShardReadFact(), 1);
    }
    return result;
}
