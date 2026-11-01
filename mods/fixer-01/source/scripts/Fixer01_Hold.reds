// V HELD STILL WHILE JOHNNY SPEAKS after her introduction call (the design
// call, 2026-10-15), gig 04's Hold copied whole (Gig04_Places.reds). The
// quest sets `cc_f01_hold` around Johnny's scene; this applies
// `GameplayRestriction.cc_f01_hold` while it is up, never with V in a
// vehicle, and for at most HoldCapTicks seconds, so a scene that never plays
// cannot leave V rooted. On the first pass of a session a removal goes out
// in case a load caught it held.

module CyberpunkCodes.Fixer01

public abstract class Fixer01HoldRules {
    public static func Fact() -> String { return "cc_f01_hold"; }
    public static func Record() -> TweakDBID { return t"GameplayRestriction.cc_f01_hold"; }
    public static func CapTicks() -> Int32 { return 30; }
}

public class Fixer01Hold extends ScriptableSystem {
    private let m_ticks: Int32;
    private let m_on: Bool;
    private let m_checked: Bool;

    private func OnAttach() -> Void {
        this.Schedule(5.0);
    }

    public func Schedule(delay: Float) -> Void {
        let cb: ref<Fixer01HoldTick> = new Fixer01HoldTick();
        cb.system = this;
        GameInstance.GetDelaySystem(this.GetGameInstance()).DelayCallback(cb, delay, false);
    }

    public func Tick() -> Void {
        let game: GameInstance = this.GetGameInstance();
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        let ps: ref<PlayerSystem> = GameInstance.GetPlayerSystem(game);
        if !IsDefined(qs) || !IsDefined(ps) {
            this.Schedule(5.0);
            return;
        }
        let player: ref<PlayerPuppet> = ps.GetLocalPlayerMainGameObject() as PlayerPuppet;
        if !IsDefined(player) {
            this.Schedule(5.0);
            return;
        }
        // A HOLD SAVED UP IS DROPPED on the first pass of a session. The cap
        // counts in a field, which a load resets, and only Johnny's scene
        // ending lowers the fact: a save made while it was up would root V
        // for the cap's length on every load (audit 2026-11-01).
        if !this.m_checked && qs.GetFactStr(Fixer01HoldRules.Fact()) > 0 {
            qs.SetFactStr(Fixer01HoldRules.Fact(), 0);
        }
        let asked: Bool = qs.GetFactStr(Fixer01HoldRules.Fact()) > 0;
        if asked {
            this.m_ticks += 1;
        } else {
            this.m_ticks = 0;
        }
        let want: Bool = asked && this.m_ticks < Fixer01HoldRules.CapTicks()
            && !VehicleComponent.IsMountedToVehicle(game, player);
        if want && !this.m_on {
            StatusEffectHelper.ApplyStatusEffect(player, Fixer01HoldRules.Record());
            this.m_on = true;
        } else if !want && (this.m_on || !this.m_checked) {
            StatusEffectHelper.RemoveStatusEffect(player, Fixer01HoldRules.Record());
            this.m_on = false;
        }
        this.m_checked = true;
        // A SECOND while the quest asks, five otherwise: a fact read every
        // five seconds for the rest of the save.
        this.Schedule(asked ? 1.0 : 5.0);
    }
}

public class Fixer01HoldTick extends DelayCallback {
    public let system: wref<Fixer01Hold>;
    public func Call() -> Void {
        if IsDefined(this.system) {
            this.system.Tick();
        }
    }
}
