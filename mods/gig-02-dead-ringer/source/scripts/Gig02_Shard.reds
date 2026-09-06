// Gig 02, Dead Ringer: the one thing V reads.
//
// THE MERC'S COMMUNICATION SHARD (comic pp. 27 and 29), a real ITEM as well
// as text, because it is carried between legs. The relay is not read by V any
// more (2026-09-05): it is uploaded to Char, who answers by text.
//
// ---------------------------------------------------------------------------
// A SHARD'S TEXT IS A JOURNAL ENTRY, not an item and not a file.
//
// `ReadAction.CompleteAction` (cyberpunk/items/actions/readAction.swift) is the
// whole of it, and it is four lines:
//
//     ChangeEntryState(path, "gameJournalOnscreen", Active, Notify);
//     entry = GetEntryByString(path, "gameJournalOnscreen");
//     evt = new NotifyShardRead(); evt.title/.text/.m_imageId/.entry = ...;
//     UISystem.QueueEvent(evt);
//
// `NotifyShardRead` IS the reader overlay, and a mod can raise it directly. The
// item record, the loot container and the TweakDB work a "real" shard needs are
// all upstream of that event and none of them is required to raise it.
//
// What going through the journal buys, rather than faking a popup: the entry
// lands in the Shards list and stays re-readable, the read is persistent, and
// the quest can observe all of it.
//
// ---------------------------------------------------------------------------
// WHY THE CLOSE CALLBACK IS WRAPPED
//
// The entry goes Active, and IsEntryVisited goes true, when the popup OPENS.
// Both are therefore useless as "he has read it": V's next lines would start
// under a modal popup that pauses the game and hides subtitles.
// `PopupsManager.OnShardReadClosed` is the only signal that means closed, so
// that is what sets the facts the quest waits on.

module CyberpunkCodes.Gig02

public abstract class CCGig02Shard {
    // Authored by tools/gig02/gen_journal.py, and the three have to stay in
    // step. A wrong path fails silently: GetEntryByString returns null and no
    // popup appears.
    public static func ShardPath() -> String {
        return "onscreens/emails/quests/street_stories/cc_g02_dead_ringer/onscreens/cc_g02_shard_note";
    }

    // The one item the gig hands over: the shard off the merc.
    public static func ShardItem() -> TweakDBID { return t"Items.cc_g02_shard"; }

    // Set by the quest phase when the beat wants a reader open.
    // Down is enough: the shard is in his pocket from that moment and can be
    // read before he has said a word (2026-09-05).
    public static func ShardOpenFact() -> CName { return n"cc_g02_merc_down"; }
    // Set by the wrap at the bottom of this file when a reader is CLOSED.
    public static func ShardReadFact() -> CName { return n"cc_g02_proof_read"; }

    // HAS THE PLAYER READ IT, WHEREVER THEY READ IT.
    //
    // The close callback below only covers the reader the game raises in the
    // world. A player who takes the shard with [F] and reads it out of the
    // backpack has still read it, and the beat has to notice. Gig 01 shipped
    // an objective that stayed up for exactly that case.
    //
    // VISITED RATHER THAN ACTIVE, and the distinction is the whole point. An
    // entry goes Active when a shard is merely PICKED UP, so a state check
    // would credit a player who took it and never read a word.
    public static func HasBeenRead(game: GameInstance, path: String) -> Bool {
        let jm: ref<JournalManager> = GameInstance.GetJournalManager(game);
        if !IsDefined(jm) {
            return false;
        }
        let entry: ref<JournalEntry> = jm.GetEntryByString(path, "gameJournalOnscreen");
        if !IsDefined(entry) {
            return false;
        }
        return jm.IsEntryVisited(entry);
    }

    // Raise the reader. Returns false if the journal entry did not resolve, so
    // the caller can try again on a later tick rather than swallow it.
    public static func Open(game: GameInstance, path: String) -> Bool {
        let jm: ref<JournalManager> = GameInstance.GetJournalManager(game);
        if !IsDefined(jm) {
            return false;
        }
        // Notify, not Silent: this is also the "new shard" notification, and
        // the entry has to be Active before it shows up in the Shards list.
        jm.ChangeEntryState(path, "gameJournalOnscreen",
                            gameJournalEntryState.Active, JournalNotifyOption.Notify);
        let entry: ref<JournalOnscreen> =
            jm.GetEntryByString(path, "gameJournalOnscreen") as JournalOnscreen;
        if !IsDefined(entry) {
            return false;
        }
        // GetTitle/GetDescription return finished display strings: the journal
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

// The close signal, for both readers.
//
// IT FIRES FOR EVERY SHARD THE PLAYER EVER READS, so each half is gated on its
// own open fact. Without that it would complete an objective the first time V
// closed some unrelated shard picked up in the street.
//
// NOTHING INTERCEPTS ANY OTHER SHARD. Gig 01 once suppressed the vanilla popup
// for shards read near its own beat and a playtest called it correctly: a
// player who presses R on a shard has asked the game for that shard, and eating
// the popup gives them nothing where the game promised something. Our own
// reader needs no interception: `Open` fills a NotifyShardRead with our title
// and text, and vanilla draws it exactly as it draws any other.
// OUR SHARD, BY ITS TITLE. The reader opens through this callback for every
// shard, ours included, and the event carries the title it will draw. A match
// against our own title string marks the popup as ours, and the close callback
// below counts only a popup so marked (2026-09-05: any-shard counting was
// judged wrong, and the journal's visited flag never fired for a read the game
// opened from the item).
@wrapMethod(PopupsManager)
protected cb func OnShardRead(evt: ref<NotifyShardRead>) -> Bool {
    let result: Bool = wrappedMethod(evt);
    let game: GameInstance = this.GetPlayerControlledObject().GetGame();
    let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
    // The title may arrive resolved or as a LocKey# string; both are compared.
    let ours: String = GetLocalizedTextByKey(n"cc-g02-shard-title");
    if IsDefined(qs) && qs.GetFact(n"cc_g02_done") == 0
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
    // Cheapest first, and the first one is "is this gig over". A finished gig
    // should read no facts at all on somebody else's shard.
    if qs.GetFact(n"cc_g02_done") > 0 {
        return result;
    }
    // ANY SHARD POPUP CLOSING WHILE HE IS DOWN COUNTS, which is gig 01's
    // rule. A stricter version (2026-09-05, morning) also asked the journal
    // whether OUR entry had been visited, and a read from the loot list and a
    // read from the journal's shards both went undetected in play: the visited
    // flag was only ever seen on the reader our own script raises. The
    // journal poll in Gig02_Encounter.Readers is the second signal, as in
    // gig 01.
    if qs.GetFact(n"cc_g02_shard_open") > 0
        && qs.GetFact(CCGig02Shard.ShardReadFact()) == 0 {
        qs.SetFact(CCGig02Shard.ShardReadFact(), 1);
    }
    return result;
}
