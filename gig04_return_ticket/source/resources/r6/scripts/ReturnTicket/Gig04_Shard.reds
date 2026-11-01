module CyberpunkCodes.Gig04

public abstract class CCG04Shard {
    public static func Count() -> Int32 { return 2; }

    public static func Path(i: Int32) -> String {
        if i == 1 {
            return "onscreens/emails/quests/street_stories/cc_g04_return_ticket/onscreens/cc_g04_shard_flop";
        }
        return "onscreens/emails/quests/street_stories/cc_g04_return_ticket/onscreens/cc_g04_shard_stamps";
    }

    public static func Prefix(i: Int32) -> String {
        if i == 1 {
            // claws
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
                        // 2 in a row
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

// read in the world
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
