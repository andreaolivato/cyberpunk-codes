// Fixer 01: when her introduction call ended, on the game's clock.
//
// Her graph sets `cc_f01_intro_done` as her introduction call ends. This
// writes the world clock at that moment into `cc_f01_intro_time`, in whole
// seconds of game time (`TimeSystem.GetGameTimeStamp`, the clock the HUD
// shows and skipping time advances), once, and never again.
//
// WHY A SCRIPT. A quest fact is an integer and no quest node writes the
// clock into one. The fact is there for a gig that paces its own start
// from her call rather than from its own install (the design call,
// 2026-10-01: a player who installs a gig a week after meeting her should be
// counted from her call, not from the install). No gig reads it today: gig
// 04 starts from a place. 0 means the call has not been taken, and a gig
// treats it as "do not start yet". On a save where the
// call was taken before this file shipped, the stamp is written on the first
// load with it, so that save counts from that load.
//
// The tick is five seconds, so the stamp is within five seconds of the call
// ending; a gig's day is measured in hours and does not notice.

module CyberpunkCodes.Fixer01

public abstract class Fixer01StampRules {
    public static func DoneFact() -> String { return "cc_f01_intro_done"; }
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
