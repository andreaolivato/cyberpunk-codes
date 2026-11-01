module CyberpunkCodes.Fixer01
import CyberpunkCodes.Shared.Fixer01.*

public abstract class Fixer01IntroRules {
    public static func Fact() -> String { return "cc_f01_fixer_on"; }
    public static func DoneFact() -> String { return "cc_f01_intro_done"; }
    public static func SideContentFact() -> String { return "q101_enable_side_content"; }
    public static func PointOfNoReturnFact() -> String { return "q115_point_of_no_return"; }
    public static func RingOkFact() -> String { return "cc_f01_ring_ok"; }

    public static func DistrictFact() -> String { return "cc_f01_in_district"; }
    // hers
    public static func Sofa() -> Vector4 { return new Vector4(3.227, 10.466, 15.294, 1.0); }
    // metres
    public static func NearRadius() -> Float { return 900.0; }

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

}

public class Fixer01Intro extends ScriptableSystem {
    private let m_settled: Bool;
    private let m_ftDefer: Int32;

    private func OnAttach() -> Void {
        // after a load
        this.Schedule(24.0);
    }

    public func Schedule(delay: Float) -> Void {
        let cb: ref<Fixer01IntroTick> = new Fixer01IntroTick();
        cb.system = this;
        GameInstance.GetDelaySystem(this.GetGameInstance()).DelayCallback(cb, delay, false);
    }

    private func Phone() -> ref<PhoneSystem> {
        return GameInstance.GetScriptableSystemsContainer(this.GetGameInstance())
            .Get(n"PhoneSystem") as PhoneSystem;
    }

    private func CanRing(game: GameInstance, qs: ref<QuestsSystem>, ps: ref<PlayerSystem>) -> Bool {
        let player: ref<PlayerPuppet> = ps.GetLocalPlayerMainGameObject() as PlayerPuppet;
        let phone: ref<PhoneSystem> = this.Phone();
        if !IsDefined(player) || !IsDefined(phone) {
            return false;
        }
        return qs.GetFactStr(Fixer01IntroRules.PointOfNoReturnFact()) <= 0
            && phone.IsCallingEnabled()
            && !CCSharedWorld.IsUsingDevice(game, player)
            && !Fixer01IntroRules.IsFastTravelling(game)
            && !player.IsInCombat();
    }

    public func Tick() -> Void {
        if this.m_settled {
            return;
        }
        let game: GameInstance = this.GetGameInstance();
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        let ps: ref<PlayerSystem> = GameInstance.GetPlayerSystem(game);
        if !IsDefined(qs) || !IsDefined(ps) {
            this.Schedule(20.0);
            return;
        }
        if qs.GetFactStr(Fixer01IntroRules.DoneFact()) > 0 {
            this.m_settled = true;
            return;
        }
        // rung, no answer yet
        if qs.GetFactStr(Fixer01IntroRules.Fact()) > 0 {
            qs.SetFactStr(Fixer01IntroRules.RingOkFact(), this.CanRing(game, qs, ps) ? 1 : 0);
            this.Schedule(3.0);
            return;
        }
        if Fixer01IntroRules.IsFastTravelling(game) {
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
        if !IsDefined(player) || !IsDefined(phone) {
            this.Schedule(20.0);
            return;
        }
        if qs.GetFactStr(Fixer01IntroRules.DistrictFact()) <= 0
            || Vector4.Distance2D(player.GetWorldPosition(), Fixer01IntroRules.Sofa()) > Fixer01IntroRules.NearRadius() {
            this.Schedule(10.0);
            return;
        }
        let ready: Bool = true;
        // still in prologue
        if qs.GetFactStr(Fixer01IntroRules.SideContentFact()) <= 0 {
            ready = false;
        }
        // story over
        if qs.GetFactStr(Fixer01IntroRules.PointOfNoReturnFact()) > 0 {
            ready = false;
        }
        if !phone.IsCallingEnabled() {
            ready = false;
        }
        if CCSharedWorld.IsUsingDevice(game, player) {
            ready = false;
        }
        if ready {
            qs.SetFactStr(Fixer01IntroRules.Fact(), 1);
            this.Schedule(3.0);
            return;
        }
        this.Schedule(5.0);
    }
}

public class Fixer01IntroTick extends DelayCallback {
    public let system: wref<Fixer01Intro>;

    public func Call() -> Void {
        if IsDefined(this.system) {
            this.system.Tick();
        }
    }
}
