module CyberpunkCodes.Gig03

import CyberpunkCodes.Shared.Gig03.*

public abstract class CCGig03StartRules {
    public static func SideContentFact() -> String { return "q101_enable_side_content"; }
    // endgame
    public static func PointOfNoReturnFact() -> String { return "q115_point_of_no_return"; }

    public static func DinoContactPath() -> String { return "contacts/dino_dinovic"; }

    public static func IsFastTravelling(game: GameInstance) -> Bool {
        // cdpr typo
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

    public static func DinoKnown(game: GameInstance) -> Bool {
        let jm: ref<JournalManager> = GameInstance.GetJournalManager(game);
        // fail open
        if !IsDefined(jm) {
            return true;
        }
        let entry: wref<JournalEntry> =
            jm.GetEntryByString(CCGig03StartRules.DinoContactPath(), "gameJournalContact");
        if !IsDefined(entry) {
            return true;
        }
        return !Equals(jm.GetEntryState(entry), gameJournalEntryState.Inactive);
    }

    public static func DelaySeconds(step: Int32) -> Float {
        if step <= 0 {
            return 24.0;
        }
        if step == 1 || step == 2 {
            return 30.0;
        }
        if step == 3 {
            return 60.0;
        }
        // 5 min
        return 300.0;
    }
}

public class AcceptableLossStart extends ScriptableSystem {

    private let m_settled: Bool;
    private let m_step: Int32;
    private let m_ftDefer: Int32;

    private func OnAttach() -> Void {
        this.m_step = 0;
        this.Schedule(CCGig03StartRules.DelaySeconds(0));
    }

    public func Schedule(delay: Float) -> Void {
        let cb: ref<CCGig03StartTick> = new CCGig03StartTick();
        cb.system = this;
        GameInstance.GetDelaySystem(this.GetGameInstance()).DelayCallback(cb, delay, false);
    }

    private func Phone() -> ref<PhoneSystem> {
        return GameInstance.GetScriptableSystemsContainer(this.GetGameInstance())
            .Get(n"PhoneSystem") as PhoneSystem;
    }

    private func AlreadyRunning(qs: ref<QuestsSystem>) -> Bool {
        return qs.GetFactStr("cc_g03_start") > 0
            || qs.GetFactStr("cc_g03_called") > 0
            || qs.GetFactStr("cc_g03_done") > 0;
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
            this.Schedule(CCGig03StartRules.DelaySeconds(this.m_step));
            return;
        }

        if qs.GetFactStr("cc_g03_dev_hold") > 0 {
            this.m_step += 1;
            this.Schedule(CCGig03StartRules.DelaySeconds(this.m_step));
            return;
        }

        if this.AlreadyRunning(qs) {
            this.m_settled = true;
            return;
        }

        if CCGig03StartRules.IsFastTravelling(game) {
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
            if qs.GetFactStr(CCGig03StartRules.SideContentFact()) <= 0 {
                ready = false;
            }
            if qs.GetFactStr(CCGig03StartRules.PointOfNoReturnFact()) > 0 {
                ready = false;
            }
            if !CCGig03StartRules.DinoKnown(game) {
                ready = false;
                this.NotifyBlocked(qs);
            }
            if !phone.IsCallingEnabled() {
                ready = false;
            }
            if CCSharedWorld.IsUsingDevice(game, player) {
                ready = false;
            }
        }

        if ready {
            qs.SetFactStr("cc_g03_start", 1);
            this.m_settled = true;
            return;
        }

        this.m_step += 1;
        this.Schedule(CCGig03StartRules.DelaySeconds(this.m_step));
    }

    private func NotifyBlocked(qs: ref<QuestsSystem>) -> Void {
        if qs.GetFactStr("cc_g03_dino_notified") > 0 {
            return;
        }
        qs.SetFactStr("cc_g03_dino_notified", 1);
        CCSharedHud.NotifyTyped(this.GetGameInstance(),
            GetLocalizedTextByKey(n"cc-g03-blocked-no-dino"),
            SimpleMessageType.Neutral, 6.0);
    }
}

public class CCGig03StartTick extends DelayCallback {
    public let system: wref<AcceptableLossStart>;

    public func Call() -> Void {
        if IsDefined(this.system) {
            this.system.Tick();
        }
    }
}
