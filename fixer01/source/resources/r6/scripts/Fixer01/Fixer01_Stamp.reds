module CyberpunkCodes.Fixer01

public abstract class Fixer01StampRules {
    public static func DoneFact() -> String { return "cc_f01_intro_done"; }
    // game seconds
    public static func TimeFact() -> String { return "cc_f01_intro_time"; }
}

public class Fixer01Stamp extends ScriptableSystem {
    private let m_settled: Bool;

    private func OnAttach() -> Void {
        this.Schedule(10.0);
    }

    public func Schedule(delay: Float) -> Void {
        let cb: ref<Fixer01StampTick> = new Fixer01StampTick();
        cb.system = this;
        GameInstance.GetDelaySystem(this.GetGameInstance()).DelayCallback(cb, delay, false);
    }

    public func Tick() -> Void {
        if this.m_settled {
            return;
        }
        let game: GameInstance = this.GetGameInstance();
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        let ts: ref<TimeSystem> = GameInstance.GetTimeSystem(game);
        if !IsDefined(qs) || !IsDefined(ts) {
            this.Schedule(20.0);
            return;
        }
        if qs.GetFactStr(Fixer01StampRules.TimeFact()) > 0 {
            this.m_settled = true;
            return;
        }
        if qs.GetFactStr(Fixer01StampRules.DoneFact()) > 0 {
            let now: Int32 = Cast<Int32>(ts.GetGameTimeStamp());
            // 0 = call not taken
            if now < 1 {
                now = 1;
            }
            qs.SetFactStr(Fixer01StampRules.TimeFact(), now);
            this.m_settled = true;
            return;
        }
        this.Schedule(5.0);
    }
}

public class Fixer01StampTick extends DelayCallback {
    public let system: wref<Fixer01Stamp>;

    public func Call() -> Void {
        if IsDefined(this.system) {
            this.system.Tick();
        }
    }
}
