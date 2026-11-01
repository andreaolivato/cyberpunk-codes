// Gig 04, Return Ticket: the two shards.
//
// Stamps's shard is on the ledge by his couch, and the Tyger Claws' is on the
// ground behind their van. This watches what the player does with each: taken, or
// read, or both. Each closes an objective in the quest phase.
//
// Gig 03's Gig03_Shard.reds, re-pointed, with its alarm taken out and run
// once per shard: nothing happens to V for reading either. Read that file's
// header for why there are two journal states and two signals; the account
// is not repeated here. The objects are placed by tools/gig04/gen_sector.py,
// their item records are source/tweaks/shard.yaml, and their text is two
// journal entries written by tools/gig04/gen_journal.py.
// docs/shard-playbook.md covers all four.
//
//   ACTIVE   the shard has been PICKED UP, by taking it or by reading it.
//   VISITED  the shard has been READ, wherever the reader was raised.
//
// `IsEntryVisited` goes true when the reader OPENS. The close callback below
// is the only signal that means closed for a shard read in the world; a shard
// read out of the backpack has no such callback, which is what the two-tick
// poll is for (the popup pauses the game, so two ticks cannot both happen
// while the reader is still up).
//
// THE FACTS, per shard: `<prefix>_armed` (set by the quest phase when the
// beat is live), `<prefix>_got` and `<prefix>_read` (set here). Stamps's
// shard is `cc_g04_shard`, the Claws' is `cc_g04_shard2`.

module CyberpunkCodes.Gig04

public abstract class CCG04Shard {
    // Authored by tools/gig04/gen_journal.py (SHARD_ID, SHARD2_ID). A wrong
    // path fails silently: GetEntryByString returns null and nothing ever
    // completes.
    public static func Count() -> Int32 { return 2; }

    public static func Path(i: Int32) -> String {
        if i == 1 {
            return "onscreens/emails/quests/street_stories/cc_g04_return_ticket/onscreens/cc_g04_shard_flop";
        }
        return "onscreens/emails/quests/street_stories/cc_g04_return_ticket/onscreens/cc_g04_shard_stamps";
    }

    public static func Prefix(i: Int32) -> String {
        if i == 1 {
            return "cc_g04_shard2";
        }
        return "cc_g04_shard";
    }

    public static func Entry(game: GameInstance, i: Int32) -> ref<JournalEntry> {
        let jm: ref<JournalManager> = GameInstance.GetJournalManager(game);
        if !IsDefined(jm) {
            return null;
        }
        return jm.GetEntryByString(CCG04Shard.Path(i), "gameJournalOnscreen");
    }

    // PICKED UP, by taking it or by reading it.
    public static func HasBeenTaken(game: GameInstance, i: Int32) -> Bool {
        let jm: ref<JournalManager> = GameInstance.GetJournalManager(game);
        let entry: ref<JournalEntry> = CCG04Shard.Entry(game, i);
        if !IsDefined(jm) || !IsDefined(entry) {
            return false;
        }
        if jm.IsEntryVisited(entry) {
            return true;
        }
        return Equals(jm.GetEntryState(entry), gameJournalEntryState.Active);
    }

    // READ, wherever the reader was raised.
    public static func HasBeenRead(game: GameInstance, i: Int32) -> Bool {
        let jm: ref<JournalManager> = GameInstance.GetJournalManager(game);
        let entry: ref<JournalEntry> = CCG04Shard.Entry(game, i);
        if !IsDefined(jm) || !IsDefined(entry) {
            return false;
        }
        return jm.IsEntryVisited(entry);
    }
}

public class ReturnTicketShard extends ScriptableSystem {

    private let m_settled: Bool;
    // Ticks each shard has read as visited in a row (see the header).
    private let m_readTicks: array<Int32>;

    private func OnAttach() -> Void {
        ArrayResize(this.m_readTicks, CCG04Shard.Count());
        this.Schedule(5.0);
    }

    public func Schedule(delay: Float) -> Void {
        let cb: ref<CCG04ShardTick> = new CCG04ShardTick();
        cb.system = this;
        GameInstance.GetDelaySystem(this.GetGameInstance()).DelayCallback(cb, delay, false);
    }

    public func Tick() -> Void {
        if this.m_settled {
            return;
        }
        let game: GameInstance = this.GetGameInstance();
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        if !IsDefined(qs) {
            this.Schedule(5.0);
            return;
        }

        if qs.GetFactStr("cc_g04_done") > 0 {
            this.m_settled = true;
            return;
        }

        // EACH SHARD ONLY ONCE ITS BEAT IS LIVE. Before that this costs one
        // fact read per shard every five seconds, and nothing here reads a
        // fact off somebody else's shard in the rest of the game.
        if ArraySize(this.m_readTicks) < CCG04Shard.Count() {
            ArrayResize(this.m_readTicks, CCG04Shard.Count());
        }
        let live: Bool = false;
        let open: Bool = false;
        let i: Int32 = 0;
        while i < CCG04Shard.Count() {
            let p: String = CCG04Shard.Prefix(i);
            if qs.GetFactStr(p + "_armed") > 0 {
                live = true;
                if qs.GetFactStr(p + "_got") <= 0 && CCG04Shard.HasBeenTaken(game, i) {
                    qs.SetFactStr(p + "_got", 1);
                }
                if qs.GetFactStr(p + "_read") <= 0 {
                    open = true;
                    if CCG04Shard.HasBeenRead(game, i) {
                        this.m_readTicks[i] += 1;
                        if this.m_readTicks[i] >= 2 {
                            qs.SetFactStr(p + "_read", 1);
                        }
                    } else {
                        this.m_readTicks[i] = 0;
                    }
                }
            } else {
                open = true;
            }
            i += 1;
        }

        if !open {
            this.m_settled = true;
            return;
        }
        this.Schedule(live ? 1.0 : 5.0);
    }
}

public class CCG04ShardTick extends DelayCallback {
    public let system: wref<ReturnTicketShard>;

    public func Call() -> Void {
        if IsDefined(this.system) {
            this.system.Tick();
        }
    }
}

// THE READER BEING SHUT, when it was raised in the world. Gated cheapest
// first, and the first test is "is this gig over".
@wrapMethod(PopupsManager)
protected cb func OnShardReadClosed(data: ref<inkGameNotificationData>) -> Bool {
    let result: Bool = wrappedMethod(data);
    let game: GameInstance = this.GetPlayerControlledObject().GetGame();
    let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
    if IsDefined(qs) && qs.GetFact(n"cc_g04_done") <= 0 {
        let i: Int32 = 0;
        while i < CCG04Shard.Count() {
            let p: String = CCG04Shard.Prefix(i);
            if qs.GetFactStr(p + "_armed") > 0
                && qs.GetFactStr(p + "_read") == 0
                && CCG04Shard.HasBeenRead(game, i) {
                qs.SetFactStr(p + "_got", 1);
                qs.SetFactStr(p + "_read", 1);
            }
            i += 1;
        }
    }
    return result;
}
