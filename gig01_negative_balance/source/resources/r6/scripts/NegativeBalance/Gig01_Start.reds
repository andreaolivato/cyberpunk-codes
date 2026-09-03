module CyberpunkCodes.Gig01

import CyberpunkCodes.Shared.Gig01.*

public abstract class CCGig01StartRules {
    // prologue over
    public static func SideContentFact() -> String { return "q101_enable_side_content"; }
    public static func PointOfNoReturnFact() -> String { return "q115_point_of_no_return"; }

    public static func HeroesPath() -> String { return "quests/side_quest/sq018_jackie"; }

    public static func HeroesDone(game: GameInstance) -> Bool {
        let jm: ref<JournalManager> = GameInstance.GetJournalManager(game);
        if !IsDefined(jm) {
            return true;
        }
        let entry: wref<JournalEntry> =
            jm.GetEntryByString(CCGig01StartRules.HeroesPath(), "gameJournalQuest");
        if !IsDefined(entry) {
            return true;
        }
        return Equals(jm.GetEntryState(entry), gameJournalEntryState.Succeeded);
    }

    public static func IsFastTravelling(game: GameInstance) -> Bool {
        let defs: ref<FastTRavelSystemDef> = GetAllBlackboardDefs().FastTRavelSystem;
        let bb: ref<IBlackboard> = GameInstance.GetBlackboardSystem(game).Get(defs);
        if !IsDefined(bb) {
            return false;
        }
        if !bb.GetBool(defs.FastTravelStarted) {
            return false;
        }
        return !bb.GetBool(defs.FastTravelLoadingScreenFinished);
    }

    public static func DelaySeconds(step: Int32) -> Float {
        if step <= 0 {
            // first look
            return 24.0;
        }
        if step == 1 || step == 2 {
            return 30.0;
        }
        if step == 3 {
            return 60.0;
        }
        // 5 min, repeats
        return 300.0;
    }
}

public class NegativeBalanceStart extends ScriptableSystem {

    private let m_settled: Bool;
    private let m_step: Int32;
    private let m_ftDefer: Int32;

    private func OnAttach() -> Void {
        this.m_step = 0;
        this.Schedule(CCGig01StartRules.DelaySeconds(0));
    }

    public func Schedule(delay: Float) -> Void {
        let cb: ref<CCGig01StartTick> = new CCGig01StartTick();
        cb.system = this;
        GameInstance.GetDelaySystem(this.GetGameInstance()).DelayCallback(cb, delay, false);
    }

    private func Phone() -> ref<PhoneSystem> {
        return GameInstance.GetScriptableSystemsContainer(this.GetGameInstance())
            .Get(n"PhoneSystem") as PhoneSystem;
    }

    private func AlreadyRunning(qs: ref<QuestsSystem>) -> Bool {
        return qs.GetFactStr("cc_g01_start") > 0
            || qs.GetFactStr("cc_g01_started") > 0
            || qs.GetFactStr("cc_g01_accepted") > 0
            || qs.GetFactStr("cc_g01_done") > 0;
    }

    private func NotifyBlocked(qs: ref<QuestsSystem>) -> Void {
        if qs.GetFactStr("cc_g01_heroes_notified") > 0 {
            return;
        }
        qs.SetFactStr("cc_g01_heroes_notified", 1);
        CCSharedHud.NotifyTyped(this.GetGameInstance(),
            "Negative Balance is waiting: finish \"Heroes\" for Jackie first.",
            SimpleMessageType.Neutral, 6.0);
    }

    public func Tick() -> Void {
        if this.m_settled {
            return;
        }

        let game: GameInstance = this.GetGameInstance();

        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        let ps: ref<PlayerSystem> = GameInstance.GetPlayerSystem(game);

        if !IsDefined(qs) || !IsDefined(ps) {
            this.m_step += 1;
            this.Schedule(CCGig01StartRules.DelaySeconds(this.m_step));
            return;
        }

        if qs.GetFactStr("cc_g01_dev_hold") > 0 {
            this.m_step += 1;
            this.Schedule(CCGig01StartRules.DelaySeconds(this.m_step));
            return;
        }

        if this.AlreadyRunning(qs) {
            this.m_settled = true;
            return;
        }

        if CCGig01StartRules.IsFastTravelling(game) {
            // 60s max
            if this.m_ftDefer < 12 {
                this.m_ftDefer += 1;
                this.Schedule(5.0);
                return;
            }
        } else {
            this.m_ftDefer = 0;
        }

        let player: ref<PlayerPuppet> = ps.GetLocalPlayerMainGameObject() as PlayerPuppet;
        let phone: ref<PhoneSystem> = this.Phone();
        let ready: Bool = true;

        if !IsDefined(player) || !IsDefined(phone) {
            ready = false;
        } else {
            if qs.GetFactStr(CCGig01StartRules.SideContentFact()) <= 0 {
                ready = false;
            }
            if qs.GetFactStr(CCGig01StartRules.PointOfNoReturnFact()) > 0 {
                ready = false;
            }
            if !phone.IsCallingEnabled() {
                ready = false;
            }
            if CCSharedWorld.IsUsingDevice(this.GetGameInstance(), player) {
                ready = false;
            }
            if ready && !CCGig01StartRules.HeroesDone(game) {
                ready = false;
                this.NotifyBlocked(qs);
            }
        }

        if ready {
            qs.SetFactStr("cc_g01_start", 1);
            this.m_settled = true;
            return;
        }

        this.m_step += 1;
        this.Schedule(CCGig01StartRules.DelaySeconds(this.m_step));
    }
}

public class CCGig01StartTick extends DelayCallback {
    public let system: wref<NegativeBalanceStart>;

    public func Call() -> Void {
        if IsDefined(this.system) {
            this.system.Tick();
        }
    }
}
