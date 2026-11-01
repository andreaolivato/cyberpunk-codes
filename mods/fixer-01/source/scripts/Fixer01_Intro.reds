// Fixer 01: when she first calls.
//
// WHAT THE PLAYER SEES. Nothing, until the first time V is in Charter Hill
// after the prologue. Then the phone rings, and it is a woman V has never
// met saying who she is and what she buys. After that her contact, her map
// icon and her card are there for the rest of the save.
//
// THE GAME'S OWN FIXERS ring the first time V enters their district after
// the prologue: Dino's phase waits on the City Center trigger and on
// `q101_enable_side_content` (docs/backlog.md, the gig 03 fixer switch),
// Wakako's on the Westbrook one. Hers is the same shape: the quest phase
// watches the game's two Charter Hill boxes and keeps `cc_f01_in_district`
// at 1 while V is inside, and this script reads that fact where it used to
// measure a 120 m circle round her seat (until 2026-09-21).
//
// THE SHAPE is gig 03's start trigger (Gig03_Start.reds): a scriptable
// system that ticks on a delay, checks a list of conditions and sets one
// fact once. The fact is `cc_f01_fixer_on`, which the quest phase waits on
// to place the call; the dev menu sets the same fact by hand. Until her
// introduction is done it then keeps `cc_f01_ring_ok`, which each retry of
// the call waits on (CanRing).
//
// THE CONDITIONS, in the order they are checked:
//   the prologue is over            q101_enable_side_content > 0
//   the story has not ended         q115_point_of_no_return == 0
//   the phone can take a call       PhoneSystem.IsCallingEnabled
//   V is not on a screen            CCSharedWorld.IsUsingDevice
//   V is not mid fast-travel        the FastTravel blackboard
//   V is in Charter Hill            cc_f01_in_district, kept by the phase
//
// THE TICK is 24 s after a load and then every 10 s while V is outside the
// district, every 3 s inside it, so the call comes within seconds of the
// guards clearing.

module CyberpunkCodes.Fixer01
import CyberpunkCodes.Shared.*

public abstract class Fixer01IntroRules {
    public static func Fact() -> String { return "cc_f01_fixer_on"; }
    public static func DoneFact() -> String { return "cc_f01_intro_done"; }
    public static func SideContentFact() -> String { return "q101_enable_side_content"; }
    public static func PointOfNoReturnFact() -> String { return "q115_point_of_no_return"; }
    // 1 while a retry of her first call may ring (CanRing).
    public static func RingOkFact() -> String { return "cc_f01_ring_ok"; }

    // 1 while V is inside Charter Hill, kept by the quest phase.
    public static func DistrictFact() -> String { return "cc_f01_in_district"; }
    // HER SOFA (tools/fixer01/fixer01_config.FIXER_POS) and how near it V
    // must be as well. The district fact alone was found at 1 with V in
    // Kabuki, 2.3 km away (playtest 2026-10-13): her graph sets it back to 0
    // only on an "outside" wait, which a teleport or a load can miss, and
    // her call then rang wherever V was. Charter Hill is well inside this.
    public static func Sofa() -> Vector4 { return new Vector4(3.227, 10.466, 15.294, 1.0); }
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

    // A RETRY'S CHECKS: the story not over, the phone taking calls, V not
    // on a screen, not mid fast-travel and not in combat. The district is not
    // asked: her first call was placed there already.
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
        // Her introduction is over: nothing more to watch for.
        if qs.GetFactStr(Fixer01IntroRules.DoneFact()) > 0 {
            this.m_settled = true;
            return;
        }
        // RUNG AND NOT YET ANSWERED: she rings again a minute after each
        // miss, wherever V is, and each ring waits on `cc_f01_ring_ok`,
        // kept here every 3 s (audit 2026-11-01: the retries skipped every
        // check above, and rang through main missions).
        if qs.GetFactStr(Fixer01IntroRules.Fact()) > 0 {
            qs.SetFactStr(Fixer01IntroRules.RingOkFact(), this.CanRing(game, qs, ps) ? 1 : 0);
            this.Schedule(3.0);
            return;
        }
        if Fixer01IntroRules.IsFastTravelling(game) {
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
        if qs.GetFactStr(Fixer01IntroRules.SideContentFact()) <= 0 {
            ready = false;
        }
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
