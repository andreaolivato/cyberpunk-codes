// Gig 01, Negative Balance: the data shard in the office desk (comic pp. 23-24).
//
// EVERYTHING HERE WAS READ OUT OF THE DECOMPILED SCRIPTS. Sources
// (https://codeberg.org/adamsmasher/cyberpunk):
//   cyberpunk/items/actions/readAction.swift, what reading a shard IS
//   cyberpunk/UI/fullscreen/notification/popupManager.swift, PopupsManager.ShardRead
//   cyberpunk/UI/fullscreen/notification/shardsNotification.swift, the popup itself
//   core/systems/journalManager.swift, the four methods used below
//
// THE FINDING THAT MADE THIS CHEAP: a shard's text is a JOURNAL ENTRY, not an
// item. `ReadAction.CompleteAction` is four lines long - 
//
//     ChangeEntryState(path, "gameJournalOnscreen", Active, Notify);
//     entry = GetEntryByString(path, "gameJournalOnscreen");
//     evt = new NotifyShardRead(); evt.title/.text/.m_imageId/.entry = ...;
//     UISystem.QueueEvent(evt);
//
//, and that `NotifyShardRead` is the reader overlay drawn on comic p24. The
// item record, the loot container and the TweakDB work that a "real" shard
// would need are all upstream of that event, and none of them are required to
// raise it. So the gig authors the journal entry (gen_journal.py, SHARD_PATH)
// and raises the event itself.
//
// What we get for free by doing it the game's way rather than faking a popup:
// the entry lands in the Shards list and stays re-readable, the read is
// persistent (SetEntryVisited), and the quest can observe all of it.
//
// WHY THE CLOSE CALLBACK IS WRAPPED. The entry goes Active, and IsEntryVisited
// goes true, when the popup OPENS. Both are therefore useless as "he has read
// it": V's next two lines would start under a modal popup that pauses the game
// and hides subtitles. `PopupsManager.OnShardReadClosed` is the only signal
// that means closed, so that is what sets the fact the quest waits on.

module CyberpunkCodes.Gig01

// THE OBJECT IS SET DRESSING WITH A QUEST MARKER ON IT, which is all it has
// to be. Reading it is proximity (Gig01_Encounter), so nothing here hooks it.
//
// REMOVED 2026-08-14, after seven attempts at an [F] prompt: the wraps on
// HealthConsumable (OnGameAttached / OnInteractionChoiceEvent), the
// CCG01ShardUiProbe that sampled GetActiveInputLayers, and the
// ShardCaseContainer item swap with its CCG01ShardItemSwap callback. Every one
// of them was live code that did nothing, and keeping dead hooks around invites
// the next person to debug them. What they established is written up in
// tools/gen_sector.py's header - read that before trying again.
public abstract class CCG01Shard {
    // Authored by tools/gen_journal.py - keep the two in step. A wrong path
    // fails silently: GetEntryByString returns null and no popup appears.
    public static func Path() -> String {
        return "onscreens/emails/quests/street_stories/cc_g01_negative_balance/onscreens/cc_g01_shard_note";
    }

    // Where tools/gen_sector.py places the shard, and what the proximity check
    // in Gig01_Encounter measures against. Captured in game standing ON that
    // desk, so z is the surface.
    public static func ObjectSpot() -> Vector4 {
        return new Vector4(-245.654, -1454.667, 15.400, 1.0);
    }

    // Set by the quest phase once V's "A data shard..." line has played.
    public static func OpenFact() -> CName { return n"cc_g01_shard_open"; }
    // Set by the wrap below when the reader is CLOSED; the quest waits on it.
    public static func ReadFact() -> CName { return n"cc_g01_shard_read"; }

    // Raise the reader. Returns false if the journal entry did not resolve, so
    // the caller can try again on a later tick rather than swallow it.
    public static func Open(game: GameInstance) -> Bool {
        let jm: ref<JournalManager> = GameInstance.GetJournalManager(game);
        if !IsDefined(jm) {
            return false;
        }
        // Notify, not Silent: this is also the "new shard" notification, and the
        // entry has to be Active before it shows up in the Shards list.
        jm.ChangeEntryState(CCG01Shard.Path(), "gameJournalOnscreen",
                            gameJournalEntryState.Active, JournalNotifyOption.Notify);
        let entry: ref<JournalOnscreen> =
            jm.GetEntryByString(CCG01Shard.Path(), "gameJournalOnscreen") as JournalOnscreen;
        if !IsDefined(entry) {
            return false;
        }
        // GetTitle/GetDescription return finished display strings - the journal
        // resolves our LocKeys, so nothing is localized by hand here.
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

// NOTHING INTERCEPTS OTHER SHARDS ANY MORE.
//
// There used to be two wraps here - PopupsManager.OnShardRead and
// ReadAction.CompleteAction - that suppressed the vanilla popup for any shard
// read near the office and set cc_g01_shard_found instead. They existed when
// READING THE VANILLA SHARD was the mechanism.
//
// With the beat on proximity they are actively wrong, and playtesting called it:
// "why? What is this useful for? Seems like bad coding." The report is right. A player
// who presses R on the Hanako shard has asked the game for that shard, and
// eating the popup gives them nothing where the game promised something - then
// our note arrives later from an unrelated trigger. Removed 2026-08-14.
//
// Our own reader needs no interception: CCG01Shard.Open fills a NotifyShardRead
// with OUR title and text and queues it, and vanilla draws it exactly as it
// draws any other.

// The close signal. This fires for EVERY shard the player ever reads, so it is
// gated on our own open fact: without that it would complete our objective the
// first time V closed some unrelated shard he picked up in the street.
@wrapMethod(PopupsManager)
protected cb func OnShardReadClosed(data: ref<inkGameNotificationData>) -> Bool {
    let result: Bool = wrappedMethod(data);
    let game: GameInstance = this.GetPlayerControlledObject().GetGame();
    let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
    // Cheapest first, and the first one is "is this gig over". A finished gig
    // should read no facts at all on somebody else's shard.
    if IsDefined(qs)
        && qs.GetFact(n"cc_g01_done") <= 0
        && qs.GetFact(CCG01Shard.OpenFact()) > 0
        && qs.GetFact(CCG01Shard.ReadFact()) == 0 {
        qs.SetFact(CCG01Shard.ReadFact(), 1);
    }
    return result;
}
