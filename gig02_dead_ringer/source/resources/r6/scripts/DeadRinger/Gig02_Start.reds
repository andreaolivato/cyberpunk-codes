module CyberpunkCodes.Gig02

import CyberpunkCodes.Shared.Gig02.*

public abstract class CCGig02StartRules {
    public static func SideContentFact() -> String { return "q101_enable_side_content"; }
    public static func PointOfNoReturnFact() -> String { return "q115_point_of_no_return"; }

    public static func IsFastTravelling(game: GameInstance) -> Bool {
        // cdpr's typo
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
        // 5 min
        return 300.0;
    }
}

public class DeadRingerStart extends ScriptableSystem {

    private let m_settled: Bool;
    private let m_step: Int32;
    private let m_ftDefer: Int32;

    private func OnAttach() -> Void {
        this.m_step = 0;
        this.Schedule(CCGig02StartRules.DelaySeconds(0));
    }

    public func Schedule(delay: Float) -> Void {
        let cb: ref<CCGig02StartTick> = new CCGig02StartTick();
        cb.system = this;
        GameInstance.GetDelaySystem(this.GetGameInstance()).DelayCallback(cb, delay, false);
    }

    private func Phone() -> ref<PhoneSystem> {
        return GameInstance.GetScriptableSystemsContainer(this.GetGameInstance())
            .Get(n"PhoneSystem") as PhoneSystem;
    }

    private func AlreadyRunning(qs: ref<QuestsSystem>) -> Bool {
        return qs.GetFactStr("cc_g02_start") > 0
            || qs.GetFactStr("cc_g02_started") > 0
            || qs.GetFactStr("cc_g02_accepted") > 0
            || qs.GetFactStr("cc_g02_done") > 0;
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
            this.Schedule(CCGig02StartRules.DelaySeconds(this.m_step));
            return;
        }

        if qs.GetFactStr("cc_g02_dev_hold") > 0 {
            this.m_step += 1;
            this.Schedule(CCGig02StartRules.DelaySeconds(this.m_step));
            return;
        }

        if this.AlreadyRunning(qs) {
            this.m_settled = true;
            return;
        }

        if CCGig02StartRules.IsFastTravelling(game) {
            // 60s cap
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
            if qs.GetFactStr(CCGig02StartRules.SideContentFact()) <= 0 {
                ready = false;
                this.NotifyBlocked(qs);
            }
            if qs.GetFactStr(CCGig02StartRules.PointOfNoReturnFact()) > 0 {
                ready = false;
            }
            if !phone.IsCallingEnabled() {
                ready = false;
            }
            if CCSharedWorld.IsUsingDevice(game, player) {
                ready = false;
            }
        }

        if ready {
            qs.SetFactStr("cc_g02_start", 1);
            this.m_settled = true;
            return;
        }

        this.m_step += 1;
        this.Schedule(CCGig02StartRules.DelaySeconds(this.m_step));
    }

    private func NotifyBlocked(qs: ref<QuestsSystem>) -> Void {
        if qs.GetFactStr("cc_g02_prologue_notified") > 0 {
            return;
        }
        qs.SetFactStr("cc_g02_prologue_notified", 1);
        CCSharedHud.NotifyTyped(this.GetGameInstance(),
            GetLocalizedTextByKey(n"cc-g02-blocked-side-content"),
            SimpleMessageType.Neutral, 6.0);
    }
}

public class CCGig02StartTick extends DelayCallback {
    public let system: wref<DeadRingerStart>;

    public func Call() -> Void {
        if IsDefined(this.system) {
            this.system.Tick();
        }
    }
}
