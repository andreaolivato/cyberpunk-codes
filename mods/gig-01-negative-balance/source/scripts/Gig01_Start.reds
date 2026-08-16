// Gig 01 - Negative Balance: THE IN-GAME START.
//
// Until now the gig began only when the CET dev menu set cc_g01_start. This
// file is what sets it in a real playthrough. `cc_g01_start` is unchanged and
// is still the single entry point - the quest phase parks on it
// (gen_questphase.py: `step(add_pause_fact('cc_g01_start'))`) and the dev
// button still works, so nothing about testing changes.
//
// ---------------------------------------------------------------------------
// WHY A SCRIPT AND NOT A CONDITION NODE IN THE QUEST GRAPH
//
// Both work. The script wins on iteration: a change here costs a game restart,
// a change in the graph costs a regeneration of the whole questphase plus a
// rebuild and an archive swap - on the one mechanism whose failure mode is
// invisible. The graph stays exactly as it is, so this cannot break a gig that
// already plays end to end.
//
// ---------------------------------------------------------------------------
// THE GATE, AND WHY IT IS THIS SHORT
//
// Every extra condition is another way for the gig to never start, and "it
// never started" is the least debuggable thing a player can report: it looks
// identical to a broken install, a load-order clash or a missing requirement.
// So the rule used here is to gate on the fewest conditions that prevent an
// actually-nonsensical experience, not on everything that could be checked.
//
// 1. q101_enable_side_content > 0   - THE PROLOGUE IS OVER.
//
//    Not a guess. This is CDPR's own gate for side content, read off the
//    shipped data on 2026-08-14:
//      * base\open_world\minor_activities\open_world_minor_activities.questphase
//        - the ROOT of all 436 minor activities (every gig in the game) - waits
//        on it before running any of them;
//      * so does every fixer phase: dakota, dyno, el_capitan, mr_hands, padre,
//        wakako (base\open_world\fixers\*\phases\*.questphase);
//      * it is SET by base\quest\main_quests\part1\q101\phases\
//        q101_p2_meet_takemura.questphase, in the same cluster as radio_on and
//        the weather reset - the "V is home and the world reopens" beat of
//        Playing for Time, which is on the critical path and cannot be skipped;
//      * AND ep1\quest\ep1.questphase sets it itself for a Phantom Liberty
//        standalone start, which matters because our questphase is parented to
//        both base\quest\cyberpunk2077.quest and ep1\quest\ep1_standalone.quest.
//
//    So it is true in every playthrough that has an open world to play in, by
//    both entry routes, and it is already true on any existing save past that
//    point - install mid-Act-2 and the gig arms on the next load.
//
// 2. q115_point_of_no_return == 0   - AND THE ENDGAME HAS NOT STARTED.
//
//    Set by base\quest\main_quests\part1\q115\phases\q115_00_hanako.questphase
//    (Nocturne Op55N1). It is a one-way endgame flag that arrives strictly
//    after everything in (1), so it can never block a legitimate start - it can
//    only stop a two-hour gig being offered to a V who has no free roam left.
//
// 3. The phone is usable, and V is not in a menu or on a device screen.
//    PhoneSystem.IsCallingEnabled() is the game's own "may the phone ring now",
//    and is already the ring gate in Gig01_Holocall - so this is not a new
//    dependency, it is the same signal read one step earlier.
//
// 4. Nothing of this gig has run yet. See the latch below.
//
// That is the full list. There is no time-of-day condition: the comic
// opens at night, and a "prefer night, start anyway after 5 minutes" version
// was built and DROPPED on the design call the same day. It was flavour on the
// one mechanism whose failure mode is invisible, and its most likely effect in
// the field was a tester deciding the trigger was broken while it was in fact
// waiting. Do not add it back.
//
// WHAT IS DELIBERATELY *NOT* GATED, and it was researched rather than skipped:
// "has V met Nix" and "has V met Mama Welles". Both signals exist and were
// found in the shipped data - `codex_nix` (unlocks his codex entry, set in
// mq015_01_hook / mq016_02_afterlife) and `sq018_mama_welles_met` (unlocks
// hers, read by base\quest\character_entries.questphase). Both belong to
// OPTIONAL content, so both can stay 0 for the whole of a legitimate
// playthrough - and a gate that can stay false is a deadlock with no error
// message. They are in the CET dev menu's fact list if anyone wants to look at
// a real save; do not promote either to a gate without a reason that outweighs
// "the gig never started for some players".
//
module CyberpunkCodes.Gig01

import CyberpunkCodes.Shared.*

public abstract class CCGig01StartRules {
    // The two base-game facts. Both verified against shipped quest data
    // 2026-08-14 - see the header. Do not "tidy" these into guessed names.
    public static func SideContentFact() -> String { return "q101_enable_side_content"; }
    public static func PointOfNoReturnFact() -> String { return "q115_point_of_no_return"; }

    // THE POLL BACKS OFF: 24s -> 30 -> 30 -> 60 -> 5min -> 5min -> ...
    // (the agreed schedule, 2026-08-14. It replaced a flat 5 s poll).
    //
    // First look is late on purpose: OnAttach runs while the save is still
    // settling, and a phone call that arrives on top of a load screen is
    // exactly the "wrong moment" this file exists to avoid.
    //
    // After that the interval grows, because of what the gates actually are.
    // Three of the four are slow-moving facts - the prologue does not end
    // twice, and the point of no return arrives once - so a V who fails the
    // check at 24 s is overwhelmingly likely to be a V who is simply not there
    // yet, and re-asking every 5 seconds for the rest of the session buys
    // nothing. The one fast-moving gate is "V is in a menu or on a device", and
    // that one resolves in seconds, which is what the tight early steps cover.
    // The 5 min tail is the cheap standing watch for the case that matters:
    // installing mid-playthrough, or crossing the prologue boundary in-session.
    //
    // --------------------------------------------------------- FAST TRAVEL
    //
    // A PLAYER GOT ELENA'S CALL OVER A FAST-TRAVEL LOADING SCREEN (Nexus, 1.0.0,
    // 2026-08-15): he loaded a save, fast travelled within the first half minute,
    // and the ring played while he was still watching the loading screens.
    //
    // None of the four gates above sees it. OnAttach runs on EVERY session start
    // and the first check is 24 s later, so a fast travel begun in that window is
    // squarely in the way; `PhoneSystem.IsCallingEnabled()` stays true right
    // across the loading screen, and IsUsingDevice is about terminals.
    //
    // THE SIGNAL. `FastTravelSystem` publishes its own blackboard, and note the
    // spelling: the definition is `FastTRavelSystem`, capital R, CDPR's typo in
    // the shipped 2.31 script cache. Written the game's way on purpose - a
    // "corrected" name is simply a different field and reads as nothing at all.
    // Its fields are FastTravelStarted, FastTravelLoadingScreenStarted and
    // FastTravelLoadingScreenFinished; the pair below is "started, and the
    // screen has not come down yet".
    //
    // FAIL OPEN, ALWAYS. A missing blackboard answers false, not true. This is
    // one more way for the gig to never start (see THE GATE above) and it is a
    // signal nobody here has watched across a whole save, so every caller also
    // CAPS how long it may defer - see m_ftDefer. Worst case a latched flag
    // costs a couple of minutes, never the gig.
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

    // Index 0 is the first look after a load; the last value repeats forever.
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
        return 300.0;
    }
}

public class NegativeBalanceStart extends ScriptableSystem {

    // One-way latch. Once this is true the tick stops rescheduling itself, so
    // the trigger cannot fire twice, cannot re-arm after the gig completes, and
    // costs nothing for the rest of the session.
    private let m_settled: Bool;

    // How many checks have been scheduled so far; indexes DelaySeconds above.
    // Not persistent: a fresh load should start the backoff again from 24 s,
    // because a load is exactly when the answer is most likely to have changed.
    private let m_step: Int32;

    // How many checks in a row have been postponed because a fast travel was in
    // progress. THE CAP IS THE POINT: it bounds a signal we have not watched
    // across a whole save. Twelve deferrals at 5 s is a minute of loading screen,
    // which is longer than any fast travel; past that the flag is treated as
    // stuck and ignored, and the gig starts anyway. Reset to 0 the moment travel
    // is over, so a later fast travel gets the full budget again.
    private let m_ftDefer: Int32;

    private func OnAttach() -> Void {
        this.m_step = 0;
        this.Schedule(CCGig01StartRules.DelaySeconds(0));
    }

    public func Schedule(delay: Float) -> Void {
        let cb: ref<CCGig01StartTick> = new CCGig01StartTick();
        cb.system = this;
        GameInstance.GetDelaySystem(this.GetGameInstance()).DelayCallback(cb, delay, false);
    }

    private func Phone() -> ref<PhoneSystem> {
        return GameInstance.GetScriptableSystemsContainer(this.GetGameInstance())
            .Get(n"PhoneSystem") as PhoneSystem;
    }

    // Same two blackboard flags Gig01_Encounter reads, and for the same reason:
    // they are the reliable "V is looking at a screen" signal. Do not swap them
    // for wrapping the zoom interaction - that never fires for computers
    // (tested 2026-08-11).
    // ANY of these means the gig has already begun - or already finished - on
    // this save. cc_g01_start alone would be enough in practice; the other
    // three are here because the dev menu can set any fact to 0, and a trigger
    // that re-fires mid-gig would restart the quest phase from its first node.
    private func AlreadyRunning(qs: ref<QuestsSystem>) -> Bool {
        return qs.GetFactStr("cc_g01_start") > 0
            || qs.GetFactStr("cc_g01_started") > 0
            || qs.GetFactStr("cc_g01_accepted") > 0
            || qs.GetFactStr("cc_g01_done") > 0;
    }

    public func Tick() -> Void {
        if this.m_settled {
            return;
        }

        let game: GameInstance = this.GetGameInstance();

        // EVERY SYSTEM FETCH IS CHECKED BEFORE IT IS USED, not as a defensive
        // habit but as the fix for a hard crash on 2026-08-14.
        //
        // This system attaches and starts its clock while the game is still at
        // the MAIN MENU, where there is no player and no player system. The
        // first version called
        //   GameInstance.GetPlayerSystem(game).GetLocalPlayerMainGameObject()
        // straight out, and dereferencing that null flatlined the game 24 s
        // after launch - exactly one FirstCheck, before a save was ever loaded.
        // `AlreadyRunning(qs)` had the same shape one line earlier.
        //
        // Nothing about the menu is special-cased: "a system I need is not
        // there yet" and "the gates are not satisfied yet" want the same
        // answer, which is to come back later. So a missing system just
        // reschedules, and the backoff means the menu costs a handful of
        // no-op checks rather than a poll every 5 s.
        //
        // Gig01_Holocall never hit this because it never asks for the player
        // system - do not take its OnAttach as proof that a system is safe to
        // dereference at that point.
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        let ps: ref<PlayerSystem> = GameInstance.GetPlayerSystem(game);

        if !IsDefined(qs) || !IsDefined(ps) {
            this.m_step += 1;
            this.Schedule(CCGig01StartRules.DelaySeconds(this.m_step));
            return;
        }

        if this.AlreadyRunning(qs) {
            this.m_settled = true;
            return;
        }

        // MID-FAST-TRAVEL: come back shortly, and do NOT advance the backoff -
        // the answer is about to change and the next look wants to be soon, not
        // five minutes from now. Bounded by m_ftDefer; see the field.
        if CCGig01StartRules.IsFastTravelling(game) {
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
            if qs.GetFactStr(CCGig01StartRules.SideContentFact()) <= 0 {
                ready = false;
            }
            if qs.GetFactStr(CCGig01StartRules.PointOfNoReturnFact()) > 0 {
                ready = false;
            }
            if !phone.IsCallingEnabled() {
                ready = false;
            }
            if CCSharedWorld.IsUsingDevice(this.GetGameInstance(), player) {
                ready = false;
            }
        }

        if ready {
            qs.SetFactStr("cc_g01_start", 1);
            this.m_settled = true;
            return;
        }

        this.m_step += 1;
        this.Schedule(CCGig01StartRules.DelaySeconds(this.m_step));
    }
}

public class CCGig01StartTick extends DelayCallback {
    public let system: wref<NegativeBalanceStart>;

    public func Call() -> Void {
        if IsDefined(this.system) {
            this.system.Tick();
        }
    }
}
