module CyberpunkCodes.Fixer01

public abstract class Fixer01HoldRules {
    public static func Fact() -> String { return "cc_f01_hold"; }
    public static func Record() -> TweakDBID { return t"GameplayRestriction.cc_f01_hold"; }
    // 30s
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
        // saved hold
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
