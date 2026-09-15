// Gig 03, Acceptable Loss: what happens when the trace lands.
//
// The netrunner finds V the moment the security-room door opens, and in the
// Badlands a wanted player brings Militech, who are exactly who V has just
// stolen from. So the trace raises the wanted level to three stars and the
// response walks in on its own, and keeps coming until V is out of the
// Badlands. Nothing here spawns anybody: the base game's own prevention
// system does it, and it does it better than a scripted squad would. The
// guards inside the wire, and the three reinforcements, are Gig03_Alarm.reds.
//
// ---------------------------------------------------------------------------
// THE PLAYER HAS TO SEE IT HAPPEN
//
// The first build raised the stars four seconds after the shard was taken and
// showed nothing in between (the trigger has since moved to the door). Playtest, 2026-09-10: "there's no trace animation,
// just open the shard and get detected, player cannot understand what's
// happening." That is the whole beat missing: being traced is the moment the
// gig turns, and it arrived as an unexplained wanted level.
//
// So the bar runs first. `CCSharedHud.RunBar` is the base game's own HUD
// progress bar, the one it fills while a netrunner uploads to the player, and
// it is what the comic draws across pages 42 to 44: TRACING YOUR LOCATION with
// a number climbing. The stars land when it finishes, and a red banner says so.
//
// THE BAR AND THE HEAT SHARE ONE DURATION. `CCSharedHud.ShowBar(false)` picks
// the failure animation if the last progress it saw was under 96%, so a bar
// told five seconds and closed at four ends on FAILED. One constant drives
// both.
//
// ---------------------------------------------------------------------------
// IT POLLS, BECAUSE THAT IS WHAT THIS REPO DOES
//
// No gig here uses a quest fact listener; every trigger is a ScriptableSystem
// with a delayed callback, and one more of those is cheaper than one more
// pattern to maintain. The poll is idle outside the gig: it reads one fact,
// finds a zero, and reschedules.
//
// ONE-WAY, AND LATCHED IN A FACT. `cc_g03_heat_raised` is a real quest fact
// rather than a field, so it survives a reload. Without it, loading a save made
// after the trace would raise the stars again every time the save is loaded,
// which is gotcha 21's shape: a flag exercised only in the clean direction
// during testing, and wrong on every load afterwards.
//
// ---------------------------------------------------------------------------
// THE STARS STAY ON UNTIL V IS OUT OF THE BADLANDS, AND DROP THE MOMENT V IS
//
// Until 2026-09-11 the stars were raised once and shaking them was the
// player's business. The design changed that: the chase is the whole trip
// home, so the three stars come back every time the game lets them fade,
// until V crosses out of the Badlands, and on that crossing they go out at
// once. Two halves, and both are the game's own machinery:
//
//   RE-RAISING is `CCSharedPrevention.Wanted(game, 3)` again whenever the
//   heat reads below three. The prevention system fades a chase the player
//   has evaded (grey stars, then zero); this asks for three again on the next
//   three-second poll, with V's position as the crime point, so the response
//   comes to wherever V has got to. Nothing here fights the fade while it is
//   happening: the grey stars are still Heat_3 as far as the system is
//   concerned, and `Wanted` refuses to raise what is already raised.
//
//   DROPPING is `CCSharedPrevention.Clear`, which queues `SetWantedLevel`
//   with `Heat_0`. `OnSetWantedLevel` turns that into the game's own forced
//   de-escalation: four seconds of blinking stars, then nothing, with every
//   responder told to stand down (preventionSystem.swift). It is the route a
//   quest uses, which is what this is.
//
// WHICH SIDE OF THE LINE V IS ON comes from the game, not from a walked
// boundary: `PreventionSystem.GetCurrentDistrict().IsBadlands()`, which
// looks through a sub-district (Rocky Ridge, Red Peaks, the spaceport road)
// to its parent. Gig03_Places.reds reads it and writes `cc_g03_badlands_left`;
// this file only reads that fact. A null district is UNKNOWN, not outside,
// and is treated as still inside.
//
// AFTER A RELOAD the loop resumes from the facts: raised and not yet
// cleared means keep asking. A player who saves mid-chase and reloads is
// still being chased, which is what they saved.

module CyberpunkCodes.Gig03

import CyberpunkCodes.Shared.*

public abstract class CCG03TraceRules {
    // SET BY Gig03_Alarm.reds when the security-room door opens (or by the
    // two fallbacks behind it). This is what starts the bar.
    public static func TracedFact() -> String { return "cc_g03_alarm"; }
    // SET HERE WHEN THE BAR FINISHES. The guards, the reinforcements and the
    // stars all wait for it: until the trace is done, nobody knows where V
    // is. The design call, 2026-09-11: "the 3 stars and the enemies finding
    // V should be only triggered after the trace ends".
    public static func FoundFact() -> String { return "cc_g03_traced"; }
    // Our own latch, so this fires once per save.
    public static func RaisedFact() -> String { return "cc_g03_heat_raised"; }
    // Set when the gig ends, so the poll can stop for good.
    public static func DoneFact() -> String { return "cc_g03_done"; }
    // Written by Gig03_Places.reds when the game says V is out of the
    // Badlands. This is what ends the loop and drops the stars.
    public static func LeftFact() -> String { return "cc_g03_badlands_left"; }
    // Our own latch on the drop, so a reload after it does not drop again.
    public static func ClearedFact() -> String { return "cc_g03_heat_cleared"; }

    public static func Stars() -> Int32 { return 3; }

    // HOW LONG THE TRACE TAKES, and it is the bar's length as well as the
    // wait. Six seconds: long enough to read the header and watch the number
    // climb, short enough that it is tense rather than tedious. The comic shows
    // it at 22%, 87% and 100% over three pages.
    public static func DelaySeconds() -> Float { return 6.0; }

    // What the bar says while it fills, and what the banner says when it lands.
    public static func BarHeader() -> String { return "TRACING YOUR LOCATION"; }

    public static func PollSeconds() -> Float { return 5.0; }

    // THE CHASE CARS. The Badlands response's own Militech car
    // (`_wasteland_prevention`; a `_wasteland_heavy_prevention` exists
    // beside it), how many to keep in play or on their way, and where a new
    // one may appear: 80 to 220 m out, never within 50 m in a straight
    // line, so it arrives rather than pops.
    public static func Car() -> TweakDBID {
        return t"Vehicle.v_standard3_chevalier_emperor_militech_wasteland_prevention";
    }
    public static func CarsWanted() -> Int32 { return 3; }
    public static func CarRange() -> Vector2 { return new Vector2(80.0, 220.0); }
    public static func CarMinDirect() -> Float { return 50.0; }
    // How often the chase is re-asserted once it is on. The game's own fade
    // takes longer than this, so a gap is at most three seconds long.
    public static func LoopSeconds() -> Float { return 3.0; }
}

public class AcceptableLossTrace extends ScriptableSystem {

    // One-way. Once the stars have been asked for, or the gig is over, this
    // stops rescheduling and costs nothing for the rest of the session.
    private let m_settled: Bool;

    private func OnAttach() -> Void {
        this.Schedule(CCG03TraceRules.PollSeconds());
    }

    // ONE TICK IN FLIGHT AT A TIME. `Tick` can be called directly, by
    // Gig03_Alarm on the frame the door opens, while a scheduled tick is
    // still pending; without this the pending one would arrive later and
    // start a second poll loop beside the first. Every scheduled callback
    // carries the ticket it was issued with, and only the newest counts.
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
        // A direct call retires whatever was pending.
        this.m_ticket += 1;
        if this.m_settled {
            return;
        }

        let game: GameInstance = this.GetGameInstance();

        // EVERY SYSTEM FETCH IS CHECKED BEFORE IT IS USED. This attaches while
        // the game is still at the main menu, where there is no quest system,
        // and dereferencing that null flatlines the game before a save is even
        // loaded. Gig 01 shipped that crash once.
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

        // ALREADY RAISED: this is the loop, not the trace. Resumes here after
        // a reload too, because both facts are in the save.
        if qs.GetFactStr(CCG03TraceRules.RaisedFact()) > 0 {
            this.Loop(game, qs);
            return;
        }

        if qs.GetFactStr(CCG03TraceRules.TracedFact()) <= 0 {
            this.Schedule(CCG03TraceRules.PollSeconds());
            return;
        }

        // LATCH BEFORE ACTING, not after. The raise is deferred by the length
        // of the bar, and a second poll in that window would ask twice. The
        // loop starts once the bar has finished, so the first re-raise cannot
        // land before the first raise.
        qs.SetFactStr(CCG03TraceRules.RaisedFact(), 1);
        this.Schedule(CCG03TraceRules.DelaySeconds() + CCG03TraceRules.LoopSeconds());

        // THE BAR STARTS NOW, and the stars land when it finishes.
        CCSharedHud.RunBar(game, CCG03TraceRules.BarHeader(),
                           CCG03TraceRules.DelaySeconds());

        let cb: ref<CCG03HeatCall> = new CCG03HeatCall();
        cb.game = game;
        GameInstance.GetDelaySystem(game)
            .DelayCallback(cb, CCG03TraceRules.DelaySeconds(), false);
    }

    // THE CHASE, RE-ASSERTED. See the header.
    private func Loop(game: GameInstance, qs: ref<QuestsSystem>) -> Void {
        if qs.GetFactStr(CCG03TraceRules.LeftFact()) > 0 {
            // OUT OF THE BADLANDS. Drop the stars, once, and stop for good.
            qs.SetFactStr(CCG03TraceRules.ClearedFact(), 1);
            this.m_settled = true;
            if CCSharedPrevention.Clear(game) {
                qs.SetFactStr("cc_g03_dbg_heat_drop", 1);
            } else {
                // Nothing to drop: the player had already lost the stars in
                // the seconds between the last re-raise and the line.
                qs.SetFactStr("cc_g03_dbg_heat_drop", 2);
            }
            return;
        }
        // A save made during the six seconds of the bar has the raise latched
        // and the bar's end never reached. The trace is over by any reading
        // of that save, so say so, or the guards would never turn.
        if qs.GetFactStr(CCG03TraceRules.FoundFact()) <= 0 {
            qs.SetFactStr(CCG03TraceRules.FoundFact(), 1);
        }
        // STILL IN THE BADLANDS. If the game has let the chase fade, bring it
        // back, from wherever V is now.
        if CCSharedPrevention.Heat(game) < CCG03TraceRules.Stars() {
            if CCSharedPrevention.Wanted(game, CCG03TraceRules.Stars()) {
                qs.SetFactStr("cc_g03_dbg_reraised",
                              qs.GetFactStr("cc_g03_dbg_reraised") + 1);
            }
        } else {
            // AND TELL THEM WHERE V IS, every pass while the chase is on.
            // Stars alone are a search, and a search cannot put men on foot
            // round a V who is off the road (CCSharedPrevention.Locate has
            // the reading). Playtest 2026-09-15: "they try to find me but
            // can't cause I stay outside of the road".
            if CCSharedPrevention.Locate(game) {
                qs.SetFactStr("cc_g03_dbg_located",
                              qs.GetFactStr("cc_g03_dbg_located") + 1);
            }
            // AND KEEP CARS ON V. The game's own spawner sends few cars
            // after a V driving off the road (it wants a road near the
            // player, and falls back to men on foot); this asks it for one
            // of the Badlands' own Militech chase cars, spawned anywhere in
            // range and driven at V, whenever fewer than CarsWanted are in
            // play or on their way. Playtest 2026-09-15: "I'd like for
            // their vehicles to chase me through the desert".
            if CCSharedPrevention.Vehicles(game) < CCG03TraceRules.CarsWanted() {
                if CCSharedPrevention.Car(game, CCG03TraceRules.Car(),
                                          CCG03TraceRules.CarRange(),
                                          CCG03TraceRules.CarMinDirect()) {
                    qs.SetFactStr("cc_g03_dbg_cars",
                                  qs.GetFactStr("cc_g03_dbg_cars") + 1);
                }
            }
            // AND POINT EVERY CAR AT V OFF THE ROAD. The cars came and sat
            // on the tarmac (playtest 2026-09-15, "they just stay on the
            // road"): a chase car navigates traffic lanes. The follow
            // command with traffic off drives at V directly, and it is
            // re-sent every pass because the game's own chase command
            // takes the car back whenever its strategy changes.
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
        // CLOSE THE BAR FULL. ShowBar(false) writes 1.0 before it closes, so
        // the widget cannot end on its failure animation whatever the timings
        // drift to.
        CCSharedHud.ShowBar(this.game, false, "");

        // The banner is the game's own red system message, which is what it
        // uses for an alarm. It says what just happened in the words the site
        // would use.
        CCSharedHud.NotifyTyped(this.game,
            GetLocalizedTextByKey(n"cc-g03-traced-banner"),
            SimpleMessageType.Negative, 5.0);

        // Recorded so a playtest can tell "the stars did not come" from "this
        // never ran", which the star meter alone cannot say.
        if CCSharedPrevention.Wanted(this.game, CCG03TraceRules.Stars()) {
            qs.SetFactStr("cc_g03_dbg_heat", 1);
        } else {
            qs.SetFactStr("cc_g03_dbg_heat", 2);
        }

        // V IS FOUND. The guards and the reinforcements wait on this, and the
        // guard pass runs on this frame rather than on its next poll.
        qs.SetFactStr(CCG03TraceRules.FoundFact(), 1);
        let alarm: ref<AcceptableLossAlarm> = GameInstance.GetScriptableSystemsContainer(this.game)
            .Get(n"CyberpunkCodes.Gig03.AcceptableLossAlarm") as AcceptableLossAlarm;
        if IsDefined(alarm) {
            alarm.Tick();
        }
    }
}
