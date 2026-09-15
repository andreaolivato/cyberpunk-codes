// Gig 03, Acceptable Loss: the mission log on the cabinet.
//
// The terminal says the log Dino wants is not on the network: it is on a
// shard in the security room. This watches what the player does with that
// shard. Until 2026-09-11 it was also what told the gig V had been found;
// the trace now starts at the security-room door (Gig03_Alarm.reds), and the
// shard being taken or read is what opens the "get out" objective.
//
// The object itself is placed by tools/gig03/gen_sector.py, its item record is
// source/tweaks/shard.yaml, and its text is a journal entry written by
// tools/gig03/gen_journal.py. Read docs/shard-playbook.md before changing any
// of the four: they fail independently and three of the four fail invisibly.
//
// ---------------------------------------------------------------------------
// TAKEN OR READ, EITHER ONE, AND THE DIFFERENCE MATTERS
//
// The design calls for V to be discovered when the shard is TAKEN OR READ,
// whichever happens first. Those are two different journal states and reading
// the wrong one gets the beat wrong in one direction or the other:
//
//   ACTIVE   the shard has been PICKED UP. Set by taking it with [F], and also
//            by reading it, because reading activates the entry too.
//   VISITED  the shard has been READ, wherever the reader was raised: at the
//            container, out of the backpack, or from the Shards list.
//
// So Active is "got it" and Visited is "read it", and Active is true in both
// cases. That is exactly the pair this gig wants: the escape objective opens
// on Active, and the reading objective closes on Visited.
//
// A state check on Active alone would close the READING objective for a player
// who took the shard and never opened it, which is the case gig 01 shipped
// wrong once.
//
// ---------------------------------------------------------------------------
// WHY THE CLOSE CALLBACK IS HERE AS WELL AS THE JOURNAL CHECK
//
// `IsEntryVisited` goes true when the reader OPENS, not when it closes. A beat
// that resumed on it would start under a modal popup that pauses the game and
// hides subtitles. `PopupsManager.OnShardReadClosed` is the only signal that
// means closed, so it is what sets the read fact when the reader was raised in
// the world.
//
// It does NOT fire for a shard read out of the backpack. That is why the poll
// below exists as well, and why it waits two ticks: the popup pauses the game,
// DelaySystem does not advance while it is up, and counting two ticks cannot
// happen until the reader has actually been shut. That turns the open signal
// into a close signal without a second callback.

module CyberpunkCodes.Gig03

public abstract class CCG03Shard {
    // Authored by tools/gig03/gen_journal.py. A wrong path fails silently:
    // GetEntryByString returns null and nothing ever completes.
    public static func Path() -> String {
        return "onscreens/emails/quests/street_stories/cc_g03_acceptable_loss/onscreens/cc_g03_shard_log";
    }

    // Set by the quest phase when the shard beat is live, so nothing here reads
    // a fact off somebody else's shard in the rest of the game.
    public static func ArmedFact() -> CName { return n"cc_g03_data"; }
    // The shard is in V's hands, by either route. This opens "get out".
    public static func GotFact() -> CName { return n"cc_g03_shard_got"; }
    // The shard has been read and the reader shut.
    public static func ReadFact() -> CName { return n"cc_g03_shard_read"; }
    public static func DoneFact() -> CName { return n"cc_g03_done"; }

    public static func Entry(game: GameInstance) -> ref<JournalEntry> {
        let jm: ref<JournalManager> = GameInstance.GetJournalManager(game);
        if !IsDefined(jm) {
            return null;
        }
        return jm.GetEntryByString(CCG03Shard.Path(), "gameJournalOnscreen");
    }

    // PICKED UP, by taking it or by reading it.
    public static func HasBeenTaken(game: GameInstance) -> Bool {
        let jm: ref<JournalManager> = GameInstance.GetJournalManager(game);
        let entry: ref<JournalEntry> = CCG03Shard.Entry(game);
        if !IsDefined(jm) || !IsDefined(entry) {
            return false;
        }
        if jm.IsEntryVisited(entry) {
            return true;
        }
        return Equals(jm.GetEntryState(entry), gameJournalEntryState.Active);
    }

    // READ, wherever the reader was raised.
    public static func HasBeenRead(game: GameInstance) -> Bool {
        let jm: ref<JournalManager> = GameInstance.GetJournalManager(game);
        let entry: ref<JournalEntry> = CCG03Shard.Entry(game);
        if !IsDefined(jm) || !IsDefined(entry) {
            return false;
        }
        return jm.IsEntryVisited(entry);
    }
}

public class AcceptableLossShard extends ScriptableSystem {

    private let m_settled: Bool;
    // How many ticks the read has been true for. Two, for the reason in the
    // header: the popup pauses the game, so two ticks cannot both happen while
    // the reader is still up.
    private let m_readTicks: Int32;

    private func OnAttach() -> Void {
        this.Schedule(5.0);
    }

    public func Schedule(delay: Float) -> Void {
        let cb: ref<CCG03ShardTick> = new CCG03ShardTick();
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

        if qs.GetFactStr("cc_g03_done") > 0 {
            this.m_settled = true;
            return;
        }

        // NOT ARMED YET. The beat is live from the moment the terminal has been
        // read, which is when the player is told where the shard is. Before
        // that this costs one fact read every five seconds.
        if qs.GetFactStr("cc_g03_data") <= 0 {
            this.Schedule(5.0);
            return;
        }

        // A faster poll once it matters: the objective changing is the beat,
        // and five seconds of silence after picking the shard up reads as
        // broken.
        if qs.GetFactStr("cc_g03_shard_got") <= 0 && CCG03Shard.HasBeenTaken(game) {
            qs.SetFactStr("cc_g03_shard_got", 1);
            // THE LAST NET UNDER THE ALARM. The door (Gig03_Alarm.reds) and
            // the cabinet (Gig03_Places.reds) both fire before the shard can
            // be in hand; if neither did, the alarm goes up here so the
            // stars can never arrive after the shard.
            if qs.GetFactStr("cc_g03_dbg_alarm_src") <= 0 {
                qs.SetFactStr("cc_g03_dbg_alarm_src", 3);
            }
            CCG03Alarm.Raise(game);
        }

        if qs.GetFactStr("cc_g03_shard_read") <= 0 {
            if CCG03Shard.HasBeenRead(game) {
                this.m_readTicks += 1;
                if this.m_readTicks >= 2 {
                    qs.SetFactStr("cc_g03_shard_read", 1);
                }
            } else {
                this.m_readTicks = 0;
            }
        }

        if qs.GetFactStr("cc_g03_shard_read") > 0 {
            this.m_settled = true;
            return;
        }
        this.Schedule(1.0);
    }
}

public class CCG03ShardTick extends DelayCallback {
    public let system: wref<AcceptableLossShard>;

    public func Call() -> Void {
        if IsDefined(this.system) {
            this.system.Tick();
        }
    }
}

// THE READER BEING SHUT, when it was raised in the world.
//
// Gated cheapest-first, and the first test is "is this gig over": a finished
// gig should read no facts at all on somebody else's shard.
@wrapMethod(PopupsManager)
protected cb func OnShardReadClosed(data: ref<inkGameNotificationData>) -> Bool {
    let result: Bool = wrappedMethod(data);
    let game: GameInstance = this.GetPlayerControlledObject().GetGame();
    let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
    if IsDefined(qs)
        && qs.GetFact(n"cc_g03_done") <= 0
        && qs.GetFact(n"cc_g03_data") > 0
        && qs.GetFact(n"cc_g03_shard_read") == 0
        && CCG03Shard.HasBeenRead(game) {
        qs.SetFact(n"cc_g03_shard_got", 1);
        qs.SetFact(n"cc_g03_shard_read", 1);
        if qs.GetFact(n"cc_g03_dbg_alarm_src") <= 0 {
            qs.SetFact(n"cc_g03_dbg_alarm_src", 3);
        }
        CCG03Alarm.Raise(game);
    }
    return result;
}
