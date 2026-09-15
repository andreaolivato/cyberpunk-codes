module CyberpunkCodes.Gig03

public abstract class CCG03Shard {
    public static func Path() -> String {
        return "onscreens/emails/quests/street_stories/cc_g03_acceptable_loss/onscreens/cc_g03_shard_log";
    }

    public static func ArmedFact() -> CName { return n"cc_g03_data"; }
    public static func GotFact() -> CName { return n"cc_g03_shard_got"; }
    public static func ReadFact() -> CName { return n"cc_g03_shard_read"; }
    public static func DoneFact() -> CName { return n"cc_g03_done"; }

    public static func Entry(game: GameInstance) -> ref<JournalEntry> {
        let jm: ref<JournalManager> = GameInstance.GetJournalManager(game);
        if !IsDefined(jm) {
            return null;
        }
        return jm.GetEntryByString(CCG03Shard.Path(), "gameJournalOnscreen");
    }

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

        if qs.GetFactStr("cc_g03_data") <= 0 {
            this.Schedule(5.0);
            return;
        }

        if qs.GetFactStr("cc_g03_shard_got") <= 0 && CCG03Shard.HasBeenTaken(game) {
            qs.SetFactStr("cc_g03_shard_got", 1);
            if qs.GetFactStr("cc_g03_dbg_alarm_src") <= 0 {
                // 3 = shard
                qs.SetFactStr("cc_g03_dbg_alarm_src", 3);
            }
            CCG03Alarm.Raise(game);
        }

        if qs.GetFactStr("cc_g03_shard_read") <= 0 {
            if CCG03Shard.HasBeenRead(game) {
                this.m_readTicks += 1;
                // reader shut
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
