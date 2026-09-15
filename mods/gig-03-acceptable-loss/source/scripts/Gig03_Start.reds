// Gig 03, Acceptable Loss: THE IN-GAME START.
//
// `cc_g03_start` is the single entry point. The quest phase parks on it and this
// file is what sets it in a real playthrough; the dev menu can set it too, so
// nothing about testing changes.
//
// Copied from Gig02_Start.reds, which carries the full account of the poll
// backoff, the fast-travel deferral and why every system fetch is null-checked.
// This header records only what is different.
//
// ---------------------------------------------------------------------------
// THE GATE, AND THE ONE CONDITION THIS GIG ADDS
//
// Every extra condition is another way for the gig to never start, and "it
// never started" is the least debuggable thing a player can report: it looks
// identical to a broken install, a load-order clash or a missing requirement.
// So the rule is to gate on the fewest conditions that prevent an actually
// nonsensical experience.
//
// 1. q101_enable_side_content > 0   - the prologue is over. CDPR's own gate.
// 2. q115_point_of_no_return == 0   - the endgame has not started.
// 3. The phone is usable, and V is not in a menu or on a device screen.
// 4. Nothing of this gig has run yet.
//
// 5. DINO HAS BEEN IN TOUCH. This one is new, and it is a story condition
//    rather than a technical one: the gig opens with him handing V a corporate
//    job, and V taking that from a fixer they have never spoken to reads wrong.
//
//    It is cheap to satisfy. Dino calls V on his own the first time the
//    player spends time in City Center after the prologue ("Ya don't know
//    me, but you will. Name's Dino"), so for most saves past Act 1 this is
//    already true by the time the other four gates are. His fixer phase is
//    gated on `q101_enable_side_content` like every fixer's but Regina's
//    (docs/architecture.md), so gate 1 and this one open together.
//
//    THE FIXER WAS REGINA JONES UNTIL 2026-09-15, and this gate was the same
//    check on `contacts/regina_jones`. Her street door was locked on an early
//    save and Gig03_ReginaDoor.reds unlocked it; no door is known at Dino's
//    bar (the sector holds none within 45 m of his stool), so that file is
//    gone. If a playtest finds one, tools/cc_doors measures it and the file
//    is in git history.
//
// ---------------------------------------------------------------------------
// WHY A SCRIPT AND NOT A CONDITION NODE IN THE QUEST GRAPH
//
// Both work. The script wins on iteration: a change here costs a game restart, a
// change in the graph costs regenerating the whole questphase plus a rebuild and
// an archive swap, on the one mechanism whose failure is silent.

module CyberpunkCodes.Gig03

import CyberpunkCodes.Shared.*

public abstract class CCGig03StartRules {
    // Both verified against shipped quest data by gig 01 on 2026-08-14. Do not
    // "tidy" these into guessed names: a guessed fact reads as 0 forever, which
    // here means the gig never starts for anybody.
    public static func SideContentFact() -> String { return "q101_enable_side_content"; }
    public static func PointOfNoReturnFact() -> String { return "q115_point_of_no_return"; }

    // HIS CONTACT ENTRY, read out of `base\journal\cooked_journal.journal` on
    // 2026-09-15 rather than guessed (`contacts/dino_dinovic`, beside
    // `contacts/regina_jones`). A guessed path resolves to nothing, and
    // because the check below fails OPEN that would silently remove the gate
    // rather than break the gig, which is the worse of the two mistakes to
    // leave undetected.
    public static func DinoContactPath() -> String { return "contacts/dino_dinovic"; }

    // MID-FAST-TRAVEL. NOTE THE SPELLING: the blackboard definition is
    // `FastTRavelSystem`, with a capital R, which is CDPR's typo in the shipped
    // 2.31 script cache. Written the game's way on purpose: a "corrected" name
    // is a different field and reads as nothing at all.
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

    // HAS DINO EVER BEEN IN TOUCH?
    //
    // FAIL OPEN. A null journal manager, a null entry or a journal that has not
    // resolved yet all answer "true, carry on" rather than "block". The cost of
    // a false positive is V being offered a job by a fixer they have not met,
    // which is a story wrinkle. The cost of a false negative is a gig that never
    // starts and looks like a broken install. When in doubt, let them play.
    //
    // A CONTACT IS NOT A QUEST, so this does not test for Succeeded. The entry
    // exists in the journal resource from the start and it is its STATE that
    // moves: Inactive until he makes contact, Active afterwards. Testing for
    // "not Inactive" rather than "is Active" keeps a third state, if one exists,
    // on the permissive side.
    public static func DinoKnown(game: GameInstance) -> Bool {
        let jm: ref<JournalManager> = GameInstance.GetJournalManager(game);
        if !IsDefined(jm) {
            return true;
        }
        let entry: wref<JournalEntry> =
            jm.GetEntryByString(CCGig03StartRules.DinoContactPath(), "gameJournalContact");
        if !IsDefined(entry) {
            return true;
        }
        return !Equals(jm.GetEntryState(entry), gameJournalEntryState.Inactive);
    }

    // THE POLL BACKS OFF: 24 s -> 30 -> 30 -> 60 -> 5 min -> 5 min -> ...
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

public class AcceptableLossStart extends ScriptableSystem {

    // One-way latch. Once true the tick stops rescheduling itself, so the
    // trigger cannot fire twice and costs nothing for the rest of the session.
    private let m_settled: Bool;

    // How many checks have been scheduled; indexes DelaySeconds above. Not
    // persistent: a fresh load should start the backoff again from 24 s, because
    // a load is exactly when the answer is most likely to have changed.
    private let m_step: Int32;

    // How many checks in a row have been postponed for a fast travel. THE CAP IS
    // THE POINT: it bounds a signal nobody has watched across a whole save.
    private let m_ftDefer: Int32;

    private func OnAttach() -> Void {
        this.m_step = 0;
        this.Schedule(CCGig03StartRules.DelaySeconds(0));
    }

    public func Schedule(delay: Float) -> Void {
        let cb: ref<CCGig03StartTick> = new CCGig03StartTick();
        cb.system = this;
        GameInstance.GetDelaySystem(this.GetGameInstance()).DelayCallback(cb, delay, false);
    }

    private func Phone() -> ref<PhoneSystem> {
        return GameInstance.GetScriptableSystemsContainer(this.GetGameInstance())
            .Get(n"PhoneSystem") as PhoneSystem;
    }

    // ANY of these means the gig has already begun, or already finished, on this
    // save. `cc_g03_start` alone would be enough in practice; the others are
    // here because the dev menu can set any fact to 0, and a trigger that
    // re-fired mid-gig would restart the quest phase from its first node.
    private func AlreadyRunning(qs: ref<QuestsSystem>) -> Bool {
        return qs.GetFactStr("cc_g03_start") > 0
            || qs.GetFactStr("cc_g03_called") > 0
            || qs.GetFactStr("cc_g03_done") > 0;
    }

    public func Tick() -> Void {
        if this.m_settled {
            return;
        }

        let game: GameInstance = this.GetGameInstance();

        // EVERY SYSTEM FETCH IS CHECKED BEFORE IT IS USED, and that is the fix
        // for a hard crash gig 01 hit on 2026-08-14 rather than a defensive
        // habit. This system attaches and starts its clock while the game is
        // still at the MAIN MENU, where there is no player and no player system,
        // and dereferencing that null flatlines the game 24 s after launch,
        // before a save has been loaded at all.
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        let ps: ref<PlayerSystem> = GameInstance.GetPlayerSystem(game);

        if !IsDefined(qs) || !IsDefined(ps) {
            this.m_step += 1;
            this.Schedule(CCGig03StartRules.DelaySeconds(this.m_step));
            return;
        }

        // HOLD THE TRIGGER, for testing anything that is not the gig itself.
        // Deliberately does NOT set m_settled, because settling is one-way and
        // this has to be releasable without a reload.
        if qs.GetFactStr("cc_g03_dev_hold") > 0 {
            this.m_step += 1;
            this.Schedule(CCGig03StartRules.DelaySeconds(this.m_step));
            return;
        }

        if this.AlreadyRunning(qs) {
            this.m_settled = true;
            return;
        }

        // MID-FAST-TRAVEL: come back shortly, and do NOT advance the backoff.
        if CCGig03StartRules.IsFastTravelling(game) {
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
            if qs.GetFactStr(CCGig03StartRules.SideContentFact()) <= 0 {
                ready = false;
            }
            if qs.GetFactStr(CCGig03StartRules.PointOfNoReturnFact()) > 0 {
                ready = false;
            }
            if !CCGig03StartRules.DinoKnown(game) {
                ready = false;
                this.NotifyBlocked(qs);
            }
            if !phone.IsCallingEnabled() {
                ready = false;
            }
            if CCSharedWorld.IsUsingDevice(game, player) {
                ready = false;
            }
        }

        if ready {
            qs.SetFactStr("cc_g03_start", 1);
            this.m_settled = true;
            return;
        }

        this.m_step += 1;
        this.Schedule(CCGig03StartRules.DelaySeconds(this.m_step));
    }

    // TELL THE PLAYER ONCE, AND ONLY ONCE PER SAVE.
    //
    // A player who installs this on a save where Dino has never called gets
    // silence forever and no way to tell a requirement from a broken install.
    //
    // The latch is a FACT rather than a field, because a field is gone on the
    // next load and the player would collect this message every session. It is a
    // real fact, so a tester can clear it from the dev menu and see the message
    // again without a new save.
    private func NotifyBlocked(qs: ref<QuestsSystem>) -> Void {
        if qs.GetFactStr("cc_g03_dino_notified") > 0 {
            return;
        }
        qs.SetFactStr("cc_g03_dino_notified", 1);
        CCSharedHud.NotifyTyped(this.GetGameInstance(),
            GetLocalizedTextByKey(n"cc-g03-blocked-no-dino"),
            SimpleMessageType.Neutral, 6.0);
    }
}

public class CCGig03StartTick extends DelayCallback {
    public let system: wref<AcceptableLossStart>;

    public func Call() -> Void {
        if IsDefined(this.system) {
            this.system.Tick();
        }
    }
}
