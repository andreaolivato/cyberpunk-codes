// Gig 02, Dead Ringer: THE IN-GAME START.
//
// `cc_g02_start` is the single entry point. The quest phase parks on it and
// this file is what sets it in a real playthrough; the dev menu can set it too,
// so nothing about testing changes.
//
// ---------------------------------------------------------------------------
// THE GATE, AND WHY IT IS SHORTER THAN GIG 01'S
//
// Every extra condition is another way for the gig to never start, and "it
// never started" is the least debuggable thing a player can report: it looks
// identical to a broken install, a load-order clash or a missing requirement.
// So the rule is to gate on the fewest conditions that prevent an actually
// nonsensical experience.
//
// 1. q101_enable_side_content > 0   - THE PROLOGUE IS OVER.
//
//    CDPR's own gate for side content, and not a guess: the root phase of all
//    436 minor activities waits on it, every fixer phase waits on it, it is set
//    on the critical path of Playing for Time, and Phantom Liberty's standalone
//    start sets it itself. So it is true in every playthrough that has an open
//    world to play in, by both entry routes.
//
// 2. q115_point_of_no_return == 0   - AND THE ENDGAME HAS NOT STARTED.
//
//    A one-way endgame flag that arrives strictly after everything in (1), so
//    it can never block a legitimate start. It can only stop a two-hour gig
//    being offered to a V with no free roam left.
//
// 3. The phone is usable, and V is not in a menu or on a device screen.
//    `PhoneSystem.IsCallingEnabled()` is the game's own "may the phone ring
//    now". THE GIG OPENS ON A MESSAGE RATHER THAN A CALL, so this is softer
//    than it looks: a message that lands a beat early is a message, not an
//    interruption. It is here so the notification does not arrive on top of a
//    load screen.
//
// 4. Nothing of this gig has run yet. See AlreadyRunning below.
//
// THAT IS THE WHOLE LIST, and it is one condition shorter than gig 01's. Gig 01
// also waits for "Heroes" to be finished, because it ends in a bar that quest
// unlocks. This gig ends on a Japantown street that is open from the start, and
// four of its five places are open world. There is nothing to wait for.
//
// No time-of-day condition either. Gig 01 built one, dropped it the same day,
// and wrote down why: it was flavour on the one mechanism whose failure mode is
// invisible, and its most likely effect in the field was a tester deciding the
// trigger was broken while it was in fact waiting. Do not add it.
//
// ---------------------------------------------------------------------------
// WHY A SCRIPT AND NOT A CONDITION NODE IN THE QUEST GRAPH
//
// Both work. The script wins on iteration: a change here costs a game restart,
// a change in the graph costs regenerating the whole questphase plus a rebuild
// and an archive swap, on the one mechanism whose failure is silent.

module CyberpunkCodes.Gig02

import CyberpunkCodes.Shared.*

public abstract class CCGig02StartRules {
    // Both verified against shipped quest data by gig 01 on 2026-08-14. Do not
    // "tidy" these into guessed names: a guessed fact reads as 0 forever, which
    // here means the gig never starts for anybody.
    public static func SideContentFact() -> String { return "q101_enable_side_content"; }
    public static func PointOfNoReturnFact() -> String { return "q115_point_of_no_return"; }

    // MID-FAST-TRAVEL, and this exists because gig 01 shipped without it. A
    // player loaded a save, fast travelled inside the first half minute, and
    // took the opening call over the loading screen.
    //
    // NOTE THE SPELLING: the blackboard definition is `FastTRavelSystem`, with
    // a capital R, which is CDPR's typo in the shipped 2.31 script cache.
    // Written the game's way on purpose: a "corrected" name is a different
    // field and reads as nothing at all.
    //
    // FAIL OPEN, ALWAYS. A missing blackboard answers false, not true. This is
    // one more way for the gig to never start, and it is a signal nobody here
    // has watched across a whole save, so the caller also CAPS how long it may
    // defer. Worst case a latched flag costs a couple of minutes, never the gig.
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

    // THE POLL BACKS OFF: 24 s -> 30 -> 30 -> 60 -> 5 min -> 5 min -> ...
    //
    // First look is late on purpose: OnAttach runs while the save is still
    // settling. After that the interval grows, because two of the three gates
    // are slow-moving facts, and the prologue does not end twice, so a V who
    // fails at 24 s is overwhelmingly likely to be a V who is simply not there
    // yet. The one fast-moving gate is "V is in a menu", and that resolves in
    // seconds, which is what the tight early steps cover. The 5 min tail is the
    // cheap standing watch for installing mid-playthrough.
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

public class DeadRingerStart extends ScriptableSystem {

    // One-way latch. Once this is true the tick stops rescheduling itself, so
    // the trigger cannot fire twice, cannot re-arm after the gig completes, and
    // costs nothing for the rest of the session.
    private let m_settled: Bool;

    // How many checks have been scheduled; indexes DelaySeconds above. Not
    // persistent: a fresh load should start the backoff again from 24 s,
    // because a load is exactly when the answer is most likely to have changed.
    private let m_step: Int32;

    // How many checks in a row have been postponed for a fast travel. THE CAP
    // IS THE POINT: it bounds a signal nobody has watched across a whole save.
    // Twelve deferrals at 5 s is a minute of loading screen, longer than any
    // fast travel; past that the flag is treated as stuck and ignored.
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

    // ANY of these means the gig has already begun, or already finished, on
    // this save. `cc_g02_start` alone would be enough in practice; the others
    // are here because the dev menu can set any fact to 0, and a trigger that
    // re-fired mid-gig would restart the quest phase from its first node.
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

        // EVERY SYSTEM FETCH IS CHECKED BEFORE IT IS USED, and that is the fix
        // for a hard crash gig 01 hit on 2026-08-14 rather than a defensive
        // habit. This system attaches and starts its clock while the game is
        // still at the MAIN MENU, where there is no player and no player
        // system, and dereferencing that null flatlines the game 24 s after
        // launch, before a save has been loaded at all.
        //
        // Nothing about the menu is special-cased: "a system I need is not there
        // yet" and "the gates are not satisfied yet" want the same answer, which
        // is to come back later.
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        let ps: ref<PlayerSystem> = GameInstance.GetPlayerSystem(game);

        if !IsDefined(qs) || !IsDefined(ps) {
            this.m_step += 1;
            this.Schedule(CCGig02StartRules.DelaySeconds(this.m_step));
            return;
        }

        // HOLD THE TRIGGER, for testing anything that is not the gig itself.
        // Set cc_g02_dev_hold to 1 and the gig will not offer itself; clear it
        // and the next check picks up where it left off. Deliberately does NOT
        // set m_settled, because settling is one-way and this has to be
        // releasable without a reload.
        if qs.GetFactStr("cc_g02_dev_hold") > 0 {
            this.m_step += 1;
            this.Schedule(CCGig02StartRules.DelaySeconds(this.m_step));
            return;
        }

        if this.AlreadyRunning(qs) {
            this.m_settled = true;
            return;
        }

        // MID-FAST-TRAVEL: come back shortly, and do NOT advance the backoff.
        // The answer is about to change, so the next look wants to be soon
        // rather than five minutes away.
        if CCGig02StartRules.IsFastTravelling(game) {
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

    // TELL THE PLAYER ONCE, AND ONLY ONCE PER SAVE.
    //
    // A player who installs this on a prologue save and gets silence forever
    // has no way to tell a requirement from a broken install. Gig 01 learned
    // that from a bug report about a shut door and no explanation.
    //
    // The latch is a FACT rather than a field, because a field is gone on the
    // next load and the player would collect this message every session for as
    // long as the prologue sits unfinished. It is a real fact, so a tester can
    // clear it from the dev menu and see the message again without a new save.
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
