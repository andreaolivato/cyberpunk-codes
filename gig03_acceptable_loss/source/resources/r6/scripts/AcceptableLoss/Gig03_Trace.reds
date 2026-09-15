module CyberpunkCodes.Gig03

import CyberpunkCodes.Shared.Gig03.*

public abstract class CCG03TraceRules {
    // bar starts
    public static func TracedFact() -> String { return "cc_g03_alarm"; }
    // bar ended
    public static func FoundFact() -> String { return "cc_g03_traced"; }
    public static func RaisedFact() -> String { return "cc_g03_heat_raised"; }
    public static func DoneFact() -> String { return "cc_g03_done"; }
    public static func LeftFact() -> String { return "cc_g03_badlands_left"; }
    public static func ClearedFact() -> String { return "cc_g03_heat_cleared"; }

    public static func Stars() -> Int32 { return 3; }

    public static func DelaySeconds() -> Float { return 6.0; }

    public static func BarHeader() -> String { return "TRACING YOUR LOCATION"; }

    public static func PollSeconds() -> Float { return 5.0; }

    public static func Car() -> TweakDBID {
        return t"Vehicle.v_standard3_chevalier_emperor_militech_wasteland_prevention";
    }
    public static func CarsWanted() -> Int32 { return 3; }
    public static func CarRange() -> Vector2 { return new Vector2(80.0, 220.0); }
    public static func CarMinDirect() -> Float { return 50.0; }
    public static func LoopSeconds() -> Float { return 3.0; }
}

public class AcceptableLossTrace extends ScriptableSystem {

    private let m_settled: Bool;

    private func OnAttach() -> Void {
        this.Schedule(CCG03TraceRules.PollSeconds());
    }

    private let m_ticket: Int32;

    public func Schedule(delay: Float) -> Void {
        this.m_ticket += 1;
        let cb: ref<CCG03TraceTick> = new CCG03TraceTick();
        cb.system = this;
        cb.ticket = this.m_ticket;
        GameInstance.GetDelaySystem(this.GetGameInstance()).DelayCallback(cb, delay, false);
    }

    public func Ticket() -> Int32 { return this.m_ticket; }

    public func Tick() -> Void {
        this.m_ticket += 1;
        if this.m_settled {
            return;
        }

        let game: GameInstance = this.GetGameInstance();

        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        if !IsDefined(qs) {
            this.Schedule(CCG03TraceRules.PollSeconds());
            return;
        }

        if qs.GetFactStr(CCG03TraceRules.DoneFact()) > 0
            || qs.GetFactStr(CCG03TraceRules.ClearedFact()) > 0 {
            this.m_settled = true;
            return;
        }

        if qs.GetFactStr(CCG03TraceRules.RaisedFact()) > 0 {
            this.Loop(game, qs);
            return;
        }

        if qs.GetFactStr(CCG03TraceRules.TracedFact()) <= 0 {
            this.Schedule(CCG03TraceRules.PollSeconds());
            return;
        }

        qs.SetFactStr(CCG03TraceRules.RaisedFact(), 1);
        this.Schedule(CCG03TraceRules.DelaySeconds() + CCG03TraceRules.LoopSeconds());

        CCSharedHud.RunBar(game, CCG03TraceRules.BarHeader(),
                           CCG03TraceRules.DelaySeconds());

        let cb: ref<CCG03HeatCall> = new CCG03HeatCall();
        cb.game = game;
        GameInstance.GetDelaySystem(game)
            .DelayCallback(cb, CCG03TraceRules.DelaySeconds(), false);
    }

    private func Loop(game: GameInstance, qs: ref<QuestsSystem>) -> Void {
        if qs.GetFactStr(CCG03TraceRules.LeftFact()) > 0 {
            qs.SetFactStr(CCG03TraceRules.ClearedFact(), 1);
            this.m_settled = true;
            if CCSharedPrevention.Clear(game) {
                qs.SetFactStr("cc_g03_dbg_heat_drop", 1);
            } else {
                qs.SetFactStr("cc_g03_dbg_heat_drop", 2);
            }
            return;
        }
        // save during the bar
        if qs.GetFactStr(CCG03TraceRules.FoundFact()) <= 0 {
            qs.SetFactStr(CCG03TraceRules.FoundFact(), 1);
        }
        if CCSharedPrevention.Heat(game) < CCG03TraceRules.Stars() {
            if CCSharedPrevention.Wanted(game, CCG03TraceRules.Stars()) {
                qs.SetFactStr("cc_g03_dbg_reraised",
                              qs.GetFactStr("cc_g03_dbg_reraised") + 1);
            }
        } else {
            if CCSharedPrevention.Locate(game) {
                qs.SetFactStr("cc_g03_dbg_located",
                              qs.GetFactStr("cc_g03_dbg_located") + 1);
            }
            if CCSharedPrevention.Vehicles(game) < CCG03TraceRules.CarsWanted() {
                if CCSharedPrevention.Car(game, CCG03TraceRules.Car(),
                                          CCG03TraceRules.CarRange(),
                                          CCG03TraceRules.CarMinDirect()) {
                    qs.SetFactStr("cc_g03_dbg_cars",
                                  qs.GetFactStr("cc_g03_dbg_cars") + 1);
                }
            }
            qs.SetFactStr("cc_g03_dbg_followed", CCSharedPrevention.Follow(game));
        }
        this.Schedule(CCG03TraceRules.LoopSeconds());
    }
}

public class CCG03TraceTick extends DelayCallback {
    public let system: wref<AcceptableLossTrace>;
    public let ticket: Int32;

    public func Call() -> Void {
        if IsDefined(this.system) && this.ticket == this.system.Ticket() {
            this.system.Tick();
        }
    }
}

public class CCG03HeatCall extends DelayCallback {
    public let game: GameInstance;

    public func Call() -> Void {
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.game);
        if !IsDefined(qs) {
            return;
        }
        CCSharedHud.ShowBar(this.game, false, "");

        CCSharedHud.NotifyTyped(this.game,
            GetLocalizedTextByKey(n"cc-g03-traced-banner"),
            SimpleMessageType.Negative, 5.0);

        if CCSharedPrevention.Wanted(this.game, CCG03TraceRules.Stars()) {
            qs.SetFactStr("cc_g03_dbg_heat", 1);
        } else {
            qs.SetFactStr("cc_g03_dbg_heat", 2);
        }

        qs.SetFactStr(CCG03TraceRules.FoundFact(), 1);
        let alarm: ref<AcceptableLossAlarm> = GameInstance.GetScriptableSystemsContainer(this.game)
            .Get(n"CyberpunkCodes.Gig03.AcceptableLossAlarm") as AcceptableLossAlarm;
        if IsDefined(alarm) {
            alarm.Tick();
        }
    }
}
