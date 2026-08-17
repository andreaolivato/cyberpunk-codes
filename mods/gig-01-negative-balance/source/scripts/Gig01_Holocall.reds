// Gig 01 - Negative Balance: Elena's opening holocall.
//
// The call CHROME (ring, avatar, name, "Connection 541.44.10") and the call
// DIALOGUE are two separate systems. This file drives the chrome; the words are
// in mod\negative_balance\scenes\gig01_elena_call.scene, played by the quest
// phase's scene node.
//
// Vanilla drives the chrome from the quest graph, through a per-contact
// holocall phase that a scene talks to with facts (a real gig briefing scene
// sets holo_<contact>_calls_v_start_activate and waits on ..._start_done).
//
// CORRECTION, 2026-08-12: this file used to continue "mods have no such phase
// for their own contacts", and that was read for months as "mods cannot use
// them at all". Both halves need separating:
//   * TRUE for Elena. She is a contact we merged in, so no vanilla phase exists
//     for her and this system is the only way to ring the player.
//   * FALSE for Nix, and for any BASE-GAME contact. base\quest\holocalls\nix\
//     ships a full phase + scene, lives in the base quest graph, and is
//     triggered by setting holo_nix_calls_v_start_activate. It even gives a
//     real VIDEO holocall, which the scripted route below cannot.
// See docs/backlog.md 3d. The mistake was generalising from the only contact
// that had been tried.
//
// This system therefore plays that part for OUR contacts, using PhoneSystem's
// own request type:
//
//   questTriggerCallRequest { caller, addressee, callPhase, callMode, ... }
//   -> PhoneSystem.OnTriggerCall  (cyberpunk/systems/phoneSystem.swift:79)
//
// The handshake, in order:
//   1. quest phase sets cc_g01_call_request  -> we queue IncomingCall, phone rings
//   2. player answers -> PhoneSystem writes phonecall_elena_ortega_with_player
//      (GetPhoneCallFactName: "phonecall_" + caller + "_with_" + addressee,
//      both lowercased) with questPhoneTalkingState: Ended 0, Initializing 1,
//      Talking 2, Rejected 3
//   3. on Talking we queue StartCall - the chrome only becomes a holocall on
//      that phase, answering alone does not do it - and set cc_g01_call_talking,
//      which is what the quest phase waits on before entering the scene
//   4. scene ends -> quest phase sets cc_g01_call_end -> we queue EndCall and
//      set cc_g01_call_done
//
// ADDRESSEE: n"elena_ortega" is the journal contact's id, not a display name.
// HudPhoneGameController.GetIncomingContact walks JournalManager.GetContacts and
// matches JournalContact.GetId() against it, so a contact merged in by
// ArchiveXL works exactly like a base-game one - that is also where the avatar
// (PhoneAvatars.Avatar_Unknown) and the displayed name come from.
//
// The phone rings for 8 seconds and then times out (HudPhoneGameController's
// m_TimeoutPeroid), so an unanswered call is normal, not an error: we simply
// ring again. Without that the gig would dead-end on a missed call.
//
// ---------------------------------------------------------------------------
// WHY THIS IS AN AUDIO CALL AND NOT A VIDEO HOLOCALL (crash, 2026-08-11)
//
// The first build asked for questPhoneCallMode.Video and the game hard-crashed
// the instant the player answered - on StartCall, not on the ring.
//
// Video means the phone draws a LIVE RENDER of the caller into
// HudPhoneAvatarController.m_HolocallRenderTexture, and vanilla stages a body
// for that render to point at. base\cinematics\scene_blocks\
// sb_holocall_initializer.scene does it with questCallContact_NodeType, which
// carries a field the scripted route simply does not have:
//
//     prefabNodeRef: "#holocalls_studio"     mode: Video     phase: StartCall
//
// questTriggerCallRequest has no prefabNodeRef. There is no way to point a
// script-issued Video call at a holocall studio, so it renders a caller that
// was never staged. Audio has no render texture at all
// (HudPhoneAvatarController.RefreshView only shows it for EHudAvatarMode
// .Holocall), which is why the scripted route is safe in Audio and not in Video.
//
// This also happens to be the right look: Elena is UNKNOWN CALLER in the comic,
// so there is no face to show. showAvatar keeps her contact portrait on screen
// next to the waveform.
//
// A VIDEO holocall is NOT POSSIBLE HERE, and the reason is design, not effort.
// Closed 2026-08-13, the design call - see docs/backlog.md 3d before reopening it.
//
// The only route to a live video feed is to let vanilla's own per-contact
// holocall phase own the call - the ones under base/quest/holocalls/, driven by
// holo_nix_calls_v_start_activate. Handing the call to vanilla hands it ALL of
// vanilla's call, including Nix's standard small-talk dialogue options - which
// is the exact thing already rejected as clutter in 3e. There is no version of
// this that takes the video and leaves the options.
//
// So: every call this mod makes is Audio, with the contact portrait on screen.
// That is also the right look for Elena, who is UNKNOWN CALLER in the comic.
module CyberpunkCodes.Gig01

public class NegativeBalanceHolocall extends ScriptableSystem {

    // TWO calls run through this one system, indexed 0 = Elena, 1 = Nix. They
    // never overlap in the quest graph, but the state is per-call so a future
    // gig can add a third without another copy of the state machine.
    //
    // Character.Nix is the REAL record, captured off the live NPC in Afterlife
    // with the dev menu (hash 0x44F307AA, length 13). The contact id used as the
    // call addressee is the journal contact's id, "nix" - his contact is a
    // base-game one that our conversation merges into.

    // 0 idle, 1 ringing, 2 answered (holding one tick), 3 talking, 4 dialling
    // out, 5 declined and waiting out the back-off, 9 finished.
    //
    // State 2 exists purely so a crash can be attributed. Raising the call UI
    // and letting the quest phase into the scene used to happen in the same
    // tick, which made "answering crashes" impossible to narrow down. Now the
    // facts land a tick apart: cc_g01_call_answered means the call UI came up,
    // cc_g01_call_talking means the scene was allowed to start.
    private let m_state: array<Int32>;
    private let m_waited: array<Int32>;
    // Consecutive ticks a ring has been held back because a fast travel is in
    // progress. One counter for the whole system, because the quest graph never
    // has two calls in flight at once. Capped - see FastTravelClear().
    private let m_ftDefer: Int32;
    // Ticks of quiet still owed after a fast travel ends, so the phone does not
    // ring on the frame the loading screen lifts. ~3 s at the live cadence.
    private let m_ftSettle: Int32;
    // Whether OUR fast-travel lock is currently applied. Recomputed from the
    // call states every tick, never remembered across a load - see ApplyLock().
    private let m_ftLocked: Bool;
    // Has ApplyLock run once this session? Forces the first pass through, so a
    // lock saved by a previous session is lifted even when nothing is ringing.
    private let m_ftKnown: Bool;
    // How many times this call has rung without being picked up. Drives the
    // back-off in RetrySeconds(); see it for why this exists.
    private let m_rings: array<Int32>;

    private func OnAttach() -> Void {
        // Sizing happens in Tick, which self-heals; see the note there. This
        // only starts the clock.
        this.Schedule(8.0);
    }

    // ------------------------------------------------------ per-call config
    // Index 2 is Nix's FIRST call (comic pp. 26-27), where V hands over the
    // ledger and hires him; index 1 is his callback (pp. 29-30) with Hoshino's
    // location. Both are the same contact - they are two conversations, not two
    // people - so they share a PhoneFact and must never overlap. They cannot:
    // the quest phase runs them in sequence.
    private func Contact(call: Int32) -> CName {
        if call == 0 { return n"elena_ortega"; }
        // cc_g01_nix, NOT the base game's "nix". Both Nix calls go through a
        // contact we author, for the reason in gen_journal.py: ringing the real
        // one drags his ordinary phone conversation into ours - small talk
        // during the call, and vanilla hang-up options afterwards, so V had to
        // hang up on a man who had already hung up. A mod contact has no
        // conversation behind it. Same name, same avatar, none of the baggage.
        return n"cc_g01_nix";
    }

    // Fact prefix. The quest phase drives <prefix>_request and <prefix>_end;
    // this system answers with <prefix>_talking and <prefix>_done.
    private func Prefix(call: Int32) -> String {
        if call == 0 { return "cc_g01_call"; }
        if call == 1 { return "cc_g01_nixcall"; }
        return "cc_g01_nixbrief";
    }

    // WHO PLACES THE CALL. Call 2 is V ringing Nix to hand over the ledger, and
    // the comic is explicit about it (p26: V calls, Nix picks up). Having Nix
    // spontaneously ring V to ask for a ledger he does not know exists reads
    // backwards - the design call, 2026-08-12.
    //
    // PhoneSystem decides this purely from `caller` (OnTriggerCall:85-99):
    //   caller != "player"  -> plays ui_phone_incoming_call, V has to answer
    //   caller == "player"  -> plays ui_phone_initiation_call, V is dialling,
    //                          and contactName is taken from `addressee`
    // So a player-placed call is the same request with the two names swapped.
    private func PlayerInitiated(call: Int32) -> Bool {
        return call == 2;
    }

    // Written by the GAME, not by us: PhoneSystem.GetPhoneCallFactName builds
    // "phonecall_" + first + "_with_" + second, both lowercased, and SetPhoneFact
    // (phoneSystem.swift:204) picks the ORDER from isPlayerCalling. So a
    // V-placed call reports on phonecall_player_with_nix, not the reverse - get
    // this wrong and the state machine waits on a fact nothing ever writes.
    private func PhoneFact(call: Int32) -> String {
        if call == 0 { return "phonecall_elena_ortega_with_player"; }
        // Follows the contact id, which is now cc_g01_nix. GetPhoneCallFactName
        // lowercases both halves and SetPhoneFact picks the ORDER from
        // isPlayerCalling, so a V-placed call reports on the reverse name.
        if this.PlayerInitiated(call) { return "phonecall_player_with_cc_g01_nix"; }
        return "phonecall_cc_g01_nix_with_player";
    }

    // How many calls this gig has. Used for BOTH the array sizing and the tick
    // loop, so adding one is a single number - the previous version had the
    // bound written as a literal 2 in two places, which is the shape of
    // mistake that made Nix's call silently no-op once before.
    private func CallCount() -> Int32 { return 3; }

    // ------------------------------------------------------------- CADENCE
    // Two rates: 0.2 s while a call is IN FLIGHT, 2.0 s when none is.
    //
    // "In flight" is Step's own answer - request fact set, state not 9 - so the
    // fast rate covers the whole call and nothing else. The 2.0 s rate is what
    // this system costs when the player is simply playing the game: three fact
    // reads, twice a second at worst, and every one of them returns early.
    //
    // WHY, 2026-08-14. Playtest: pressing T to Elena's first word measured
    // 2.6-3.0 s, "too much pause", and nearly all of it was here. The game
    // writes phonecall_elena_ortega_with_player = Talking the instant the player
    // answers; this machine only notices on its next tick (case 1), and then
    // holds a further whole tick in case 2 before setting <prefix>_talking,
    // which is the fact the quest phase is waiting on to enter the scene.
    // At 2.0 s that is one partial tick plus one full one - traced at 1.9, 2.1
    // and 2.3 s. At 0.2 s it is at most 0.4 s. The scene's own 700 ms lead is
    // the rest of the delay and is deliberate.
    //
    // Case 2 is NOT collapsed into case 1. It exists so a crash can be
    // attributed - _answered means the call UI came up, _talking means the scene
    // was allowed to start - and it still lands them a tick apart, just a
    // shorter tick.
    //
    // docs/gotchas.md #15 is about exactly this change: speeding this tick up on
    // 2026-08-13 shrank a Johnny spawn window bounded by cc_g01_call_done below
    // the encounter's 1.5 s tick and he stopped appearing. Checked again before
    // this edit - every staging window is now bounded by cc_g01_johnny_done or
    // by a quest-phase fact, and the only window still bounded by a fact THIS
    // file writes (beat 3, closing on cc_g01_nixcall_done) closes and opens beat
    // 7 in the same encounter tick, so there is no window to lose.
    private func TickLive() -> Float { return 0.2; }
    private func TickIdle() -> Float { return 2.0; }

    // The two timers below are counted in LIVE ticks, and a call in state 1 or 4
    // always reports live, so they are exact. They were written as raw tick
    // counts against the old 2.0 s cadence (12 and 1); leaving them alone would
    // have re-rung a ringing phone after 2.4 s and cut V's dial tone to 0.2 s.
    // Whenever the cadence moves, these move with it.
    private func DialToneTicks() -> Int32 { return 10; }     // ~2 s

    // HOW LONG THE PHONE ACTUALLY RINGS, which is not how long state 1 lasts.
    //
    // HudPhoneGameController's m_TimeoutPeroid rings for 8 s and then gives up.
    // State 1 outlives that by the whole retry back-off, so anything scoped to
    // "the phone is ringing" has to be measured here rather than off the state.
    // A second of margin covers the tick the ring was placed on and the tick
    // that notices it timed out. See ApplyLock(), which is the only caller and
    // the reason this exists.
    private func RingSeconds() -> Float { return 9.0; }

    // In LIVE ticks, derived the same way RetryTicks is, so a change to the
    // cadence carries both with it.
    private func RingTicks() -> Int32 {
        return Cast<Int32>(this.RingSeconds() / this.TickLive());
    }

    // HOW LONG BEFORE RINGING AGAIN, by how many times it has already rung.
    //
    // A missed call must never strand the gig - Elena's call is the only way in,
    // so this can never give up. A fixed 24 s, though, meant a player who does
    // not want to answer is asked again every 24 seconds for the rest of the save.
    // So it backs off (playtest, 2026-08-14): 24s, 30s, 30s, 60s, then 5 minutes
    // from then on.
    //
    // DELIBERATELY does NOT tell a decline from a ring-out. The phone reports
    // questPhoneTalkingState.Rejected separately and it would be easy to branch
    // on - the design call is that it is not worth the second code path. Someone
    // reaching for their phone and missing, and someone waving it away, both
    // want the same thing: less often.
    private func RetrySeconds(rings: Int32) -> Float {
        if rings <= 1 { return 24.0; }
        if rings <= 3 { return 30.0; }
        if rings <= 4 { return 60.0; }
        return 300.0;
    }

    // In LIVE ticks, because a call in state 1 always reports live. Derived
    // rather than written out, so the cadence and these numbers cannot drift
    // apart the way they did when the tick moved from 2.0 s to 0.2 s.
    private func RetryTicks(rings: Int32) -> Int32 {
        return Cast<Int32>(this.RetrySeconds(rings) / this.TickLive());
    }

    public func Schedule(delay: Float) -> Void {
        let cb: ref<CCGig01HolocallTick> = new CCGig01HolocallTick();
        cb.system = this;
        GameInstance.GetDelaySystem(this.GetGameInstance()).DelayCallback(cb, delay, false);
    }

    private func Phone() -> ref<PhoneSystem> {
        return GameInstance.GetScriptableSystemsContainer(this.GetGameInstance())
            .Get(n"PhoneSystem") as PhoneSystem;
    }

    // May a call ring right now, as far as fast travel is concerned?
    //
    // Same report as the one Gig01_Start answers - a ring landing on a loading
    // screen - reaching this file because the quest graph can arm a call at any
    // moment and the player may fast travel a second later. The read itself is
    // CCGig01StartRules.IsFastTravelling; see it for the blackboard and its
    // spelling.
    //
    // THE CAP MATTERS MORE HERE THAN THERE. A call this system refuses to place
    // is a beat the quest phase is waiting on, so a flag that never cleared
    // would strand the gig rather than merely delay its start. 150 live ticks is
    // ~30 s, comfortably past any fast travel; after that the flag is treated as
    // stuck and the phone rings regardless.
    private func FastTravelClear() -> Bool {
        if CCGig01StartRules.IsFastTravelling(this.GetGameInstance()) {
            // Owe some quiet on the far side too. Ringing on the frame the
            // loading screen lifts is the same complaint one second later.
            this.m_ftSettle = 15;
            if this.m_ftDefer >= 150 {
                return true;
            }
            this.m_ftDefer += 1;
            return false;
        }
        this.m_ftDefer = 0;
        if this.m_ftSettle > 0 {
            this.m_ftSettle -= 1;
            return false;
        }
        return true;
    }

    // VANILLA ALREADY SHIPS A COMPLETE HOLOCALL FOR NIX, and it is fact-driven.
    //
    // This corrects a load-bearing assumption at the top of this file: "vanilla
    // drives the chrome from a per-contact holocall phase that mods do not get".
    // Mods DO get it. `base\quest\holocalls\<contact>\<contact>_holocall
    // .questphase` exists for ~60 contacts including nix, sits in the base quest
    // graph, and waits on a fact. Setting that fact runs
    // StageHolocallStudio / UnstageHolocallStudio / HoloActivateFact lived here.
    // They set holo_nix_calls_v_start_activate to ask vanilla to stage the
    // holocall studio, gated behind the dev fact cc_g01_call_video. Removed
    // 2026-08-13: the experiment cannot pay off (see the note at the top), and
    // an unstaged Video call hard-crashes the game, so leaving a switch for it
    // in the tree is a hazard rather than an option. The research that produced
    // them is preserved in docs/backlog.md 3d.

    // caller = Elena, addressee = the player: she is the one calling V.
    private func Call(call: Int32, phase: questPhoneCallPhase) -> Void {
        let req: ref<questTriggerCallRequest> = new questTriggerCallRequest();
        if this.PlayerInitiated(call) {
            req.caller = n"player";
            req.addressee = this.Contact(call);
        } else {
            req.caller = this.Contact(call);
            req.addressee = n"player";
        }
        req.callPhase = phase;
        // ALWAYS Audio. Video is closed, tried and ruled out, because the only
        // route to it hands the whole call to vanilla's per-contact phase and
        // brings Nix's standard dialogue options with it. See the note at the
        // top of this file and docs/backlog.md 3d.
        //
        // It is also the dangerous one: a Video call with nothing staged HARD
        // CRASHES the game the moment the player answers (docs/gotchas.md #10),
        // which is why no flag is left here to turn it back on by accident.
        req.callMode = questPhoneCallMode.Audio;
        // Rejectable so the phone shows its normal answer/reject prompt. The
        // first build set this false and the incoming call came up with no
        // on-screen invitation to press anything - answering worked, but only
        // if you already knew to. UNCONFIRMED that this is the cause; it is the
        // one flag on the request that plausibly drives that prompt. Rejecting
        // is harmless either way: the state machine treats anything short of
        // Talking as "ring again".
        // Rejectable only for calls that actually ring at V. Offering
        // ANSWER / REJECT on a call he placed himself would be nonsense.
        req.isRejectable = !this.PlayerInitiated(call);
        req.showAvatar = true;                     // her contact portrait, UNKNOWN CALLER
        req.visuals = questPhoneCallVisuals.Default;
        // OFF FOR EVERY CALL, and the history is the reason.
        //
        // TriggerCall (phoneSystem.swift:109) turns this into
        // PhoneManager.ApplyPhoneCallRestriction(true) on any non-EndCall phase
        // and (false) on EndCall.
        //
        // It used to be `this.PlayerInitiated(call)`, set on 2026-08-12 as a
        // guess: once V really placed the call, the phone also offered Nix's
        // ordinary conversation options alongside our scene's, and "restriction"
        // was the cheapest plausible lever. It was marked UNVERIFIED at the time
        // and never was verified.
        //
        // That problem was solved elsewhere and properly: the gig now rings its
        // OWN `cc_g01_nix` contact rather than the base-game one, and a mod
        // contact has no vanilla conversation behind it to offer (see Contact()).
        // So this flag has been fixing nothing since.
        //
        // What it WAS still doing, reported in playtest 2026-08-15: the first Nix
        // call could not be hurried along with the skip button while the second
        // one could, and the only difference between them was this line. The
        // game's own blackboard carries `FastForward` and `FastForwardHintActive`
        // beside `PhoneNoTexting` and `PhoneNoCalling`, so a phone restriction
        // suppressing the skip is the expected shape.
        //
        // Restriction is what vanilla's questCallContact_NodeType sets, but
        // vanilla is staging a full holocall; this is an Audio call carrying a
        // scene, and it needs the player able to page through it.
        //
        // CONFIRMED in playtest 2026-08-15: the call still dials out as V
        // placing it, and it can now be hurried. docs/gotchas.md #26.
        req.isPlayerTriggered = false;
        this.Phone().QueueRequest(req);
    }

    public func Tick() -> Void {
        // SELF-HEAL THE STATE ARRAYS, every tick, before anything reads them.
        //
        // These are persistent fields on a ScriptableSystem and they are sized
        // in OnAttach, which only runs when the system is FIRST attached. A save
        // made against an earlier build of this file carries the old field
        // layout forward, and the arrays came back too short - so Elena (index
        // 0) worked and Nix (index 1) read and wrote out of bounds.
        //
        // Out-of-bounds writes in redscript are silently dropped, so the state
        // never advanced past 0: the phone rang on every tick and the code never
        // looked to see whether it had been answered. Symptom in the trace was
        // exact - phonecall_nix_with_player reached Talking and
        // cc_g01_nixcall_answered never followed.
        //
        // Never size a persistent array once and trust it across script changes.
        // Sized independently, not in one loop keyed off m_state. That is the
        // same trap one level down: a NEW array added later would never be
        // filled once m_state was already long enough, and out-of-bounds writes
        // are silent.
        while ArraySize(this.m_state) < this.CallCount() { ArrayPush(this.m_state, 0); }
        while ArraySize(this.m_waited) < this.CallCount() { ArrayPush(this.m_waited, 0); }
        while ArraySize(this.m_rings) < this.CallCount() { ArrayPush(this.m_rings, 0); }

        let call: Int32 = 0;
        let live: Bool = false;
        while call < this.CallCount() {
            // Step answers "is this call in flight?", which is the whole cadence
            // decision. It used to be `state == 3` here - hanging up only - and
            // the rest of the call ran at 2 s. playtest, 2026-08-13, "the pause
            // between 'wait... that's' and Johnny saying 'fucking Arasaka' is
            // too long" bought the hang-up half of this; 2026-08-14, "too much
            // pause" after answering, buys the other half. Same fix, applied to
            // the whole call instead of one state of it.
            if this.Step(call) {
                live = true;
            }
            call += 1;
        }
        this.ApplyLock();

        // STOP FOR GOOD ONCE THE GIG IS OVER, but only AFTER ApplyLock has had
        // its one unconditional pass. The order matters: that pass is what lifts
        // a fast-travel lock saved by a previous session (docs/gotchas.md #24),
        // and stopping before it would strand exactly the lock this system
        // exists to clean up. m_ftKnown is set by the call above, so by the time
        // this is read the pass has happened.
        //
        // Every call is finished by then anyway - the gig cannot close with one
        // in flight - so nothing is cut off mid-ring. Not persistent: OnAttach
        // schedules again on the next load, one tick lifts any stale lock and
        // stops. Clearing cc_g01_done from the dev menu does not restart it
        // within a session.
        if GameInstance.GetQuestsSystem(this.GetGameInstance()).GetFactStr("cc_g01_done") > 0 {
            return;
        }

        this.Schedule(live ? this.TickLive() : this.TickIdle());
    }

    // ------------------------------------------- BLOCK FAST TRAVEL WHILE RINGING
    //
    // A player suggested this in the Nexus comments and said vanilla and other
    // mods do it. He is right on both counts, and the game has a dedicated API:
    //
    //   FastTravelSystem.AddFastTravelLock(name, gameInstance, reason)
    //   FastTravelSystem.RemoveFastTravelLock(name, gameInstance, reason)
    //
    // with `GameplayRestriction.BlockFastTravel` shipped as the reason record -
    // CDPR would not have a TweakDB entry for it if this were not the intended
    // route. It is the RIGHT half of the fix the fast-travel gate only patched
    // from the other side: that stops a call landing on a loading screen, this
    // stops the loading screen landing on a call.
    //
    // ONLY WHILE RINGING (1) OR DIALLING (4), which is what was asked
    // for. Not during a conversation - a lock's blast radius should be the
    // smallest window that solves the problem.
    //
    // "RINGING" IS NOT THE SAME AS "STATE 1", and reading it as if it were
    // BROKE FAST TRAVEL FOR THE REST OF THE SAVE. Reported in play 2026-08-16:
    // every fast travel point unavailable after ignoring the phone a few times.
    //
    // State 1 is "we rang, and we are waiting to see whether it is answered",
    // and that wait is the entire back-off in RetrySeconds: 24 s, 30, 30, 60,
    // then 300 s from the fifth ring onward. The phone itself rings for 8 s. So
    // asking for the lock on state 1 alone covered five-minute stretches with
    // one tick of daylight between them, and it was wrong from the first ring
    // too, just less visibly: 24 s of lock for 8 s of ringing.
    //
    // The lock is therefore bounded by m_waited, which counts the live ticks
    // this call has spent in state 1 and is exact because a call in state 1
    // always reports live. State 4 is genuinely dialling for its whole length
    // (DialToneTicks, then it connects), so it keeps its lock throughout.
    // docs/gotchas.md #24.
    //
    // DERIVED, NEVER REMEMBERED. The safety argument rests on that. The lock
    // is recomputed from the call states on every tick, so:
    //   * `EvaluateFastTravelLocksOnRestore` in the game's own code says locks
    //     are SAVED and re-applied on load - a stuck one would follow the player
    //     forever, and "I can't fast travel any more" is a mod-breaking report
    //     with nothing to connect it to a phone call;
    //   * m_ftLocked is a plain field, so after a load it reads false while any
    //     saved lock is real. The first tick therefore recomputes: no call in
    //     flight means we ask for the removal even though we do not think we
    //     hold one. Removing a lock that is not there is a no-op; leaving one
    //     that is, is not.
    // This is docs/gotchas.md #21 applied deliberately rather than tripped over.
    private func ApplyLock() -> Void {
        let want: Bool = false;
        let call: Int32 = 0;
        while call < this.CallCount() {
            if this.m_state[call] == 1 && this.m_waited[call] <= this.RingTicks() {
                want = true;
            }
            if this.m_state[call] == 4 {
                want = true;
            }
            call += 1;
        }
        // The early-out must NOT apply to the first pass of a session, or the
        // paragraph above is a lie: after a load both `want` and m_ftLocked read
        // false, the states match, and a lock saved by the previous session
        // would never be lifted. m_ftKnown forces exactly one unconditional
        // pass, which issues a harmless removal on every normal load and the
        // load-bearing one on the abnormal load.
        // Written out rather than `want == this.m_ftLocked`, because REDSCRIPT
        // HAS NO OperatorEqual FOR Bool. The error it gives is
        // `[NO_MATCHING_OVERLOAD] ... expected 'TweakDBID', given 'Bool'` -
        // which names the first overload in the table and sends you looking at
        // the TweakDBID on the next line instead of at the comparison.
        let unchanged: Bool = (want && this.m_ftLocked)
            || (!want && !this.m_ftLocked);
        if this.m_ftKnown && unchanged {
            return;
        }
        this.m_ftKnown = true;
        let game: GameInstance = this.GetGameInstance();
        if want {
            FastTravelSystem.AddFastTravelLock(n"cc_g01_call", game,
                                               t"GameplayRestriction.BlockFastTravel");
        } else {
            FastTravelSystem.RemoveFastTravelLock(n"cc_g01_call", game,
                                                  t"GameplayRestriction.BlockFastTravel");
        }
        this.m_ftLocked = want;
    }

    // One call's state machine. Every fact name is derived from Prefix(call), so
    // Elena and Nix run the same code against different facts.
    //
    // Returns TRUE while this call is in flight - its request fact is set and it
    // has not finished - which is what picks the tick cadence in Tick(). Reading
    // it off the state machine rather than re-reading the fact in Tick keeps the
    // two definitions of "in flight" from drifting apart.
    private func Step(call: Int32) -> Bool {
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGameInstance());
        let p: String = this.Prefix(call);

        if qs.GetFactStr(p + "_request") <= 0 || this.m_state[call] == 9 {
            return false;
        }

        // GHOST CALLS AFTER A RELOAD, and the whole of the fix (Nexus 1.0.0,
        // two reporters, 2026-08-15): *"after a reload I had 2 'ghost' phone
        // calls that died before pickup"*.
        //
        // m_state is a plain field on a ScriptableSystem and DOES NOT SURVIVE A
        // LOAD. Every fact that drives it does. So on load each call came back
        // in state 0 with its <prefix>_request still 1 from the first time
        // round, and state 0's job is to ring the phone - one ghost per call
        // that had already happened, which matches the two that were
        // reported. They "died before pickup" because the rest of the machine
        // caught up in the same second: state 3 waits on <prefix>_end, also
        // still 1, so the call hung itself up ~0.4 s after it started ringing.
        //
        // <prefix>_done is written when a call finishes and it persists, so ask
        // the save instead of remembering. DERIVE, DO NOT REMEMBER - that is
        // the rule, and Gig01_Start's AlreadyRunning() is the same rule already
        // applied to the same class of field.
        if qs.GetFactStr(p + "_done") > 0 {
            this.m_state[call] = 9;
            return false;
        }

        // ...AND HANG UP IF THE TRAVEL STARTS WHILE IT IS ALREADY RINGING.
        //
        // playtest, 2026-08-15: the gate below only stops a call being PLACED
        // during a fast travel. A call that is already ringing when the player
        // fast travels keeps ringing right across the loading screen, which is
        // the same complaint from the other direction.
        //
        // So take it back. The player loses nothing: EndCall clears the chrome
        // and the sound, the state machine drops to 0, and the ordinary retry
        // rings again once he has landed. Nothing about the gig can be missed
        // this way - a missed call has never been able to strand it.
        //
        // The ring is NOT counted as ignored. m_rings drives the back-off (24s,
        // 30, 30, 60, then 5 min) and it is meant to measure "the player keeps
        // waving this away". We pulled this one, so give the count back, or a
        // couple of fast travels would push Elena's only way into the gig out to
        // a five-minute wait.
        //
        // ONLY WHILE RINGING (1) OR DIALLING OUT (4). A call in state 3 is a
        // conversation with a scene playing and the quest phase waiting on
        // <prefix>_end; hanging that up would strand the beat, which is a far
        // worse outcome than a ring over a loading screen.
        if this.m_state[call] == 1 || this.m_state[call] == 4 {
            if CCGig01StartRules.IsFastTravelling(this.GetGameInstance()) {
                this.Call(call, questPhoneCallPhase.EndCall);
                this.m_state[call] = 0;
                this.m_waited[call] = 0;
                if this.m_rings[call] > 0 {
                    this.m_rings[call] -= 1;
                }
                return true;
            }
        }

        switch this.m_state[call] {
            case 0:
                // Ring, but only when the phone would actually be usable - in
                // combat or mid-menu the call is dropped on the floor - and not
                // over a fast-travel loading screen.
                if this.Phone().IsCallingEnabled() && this.FastTravelClear() {
                    // CLEAR THE GAME'S OWN CALL FACT FIRST. It persists, and it
                    // persists at Talking (2) once a call has been answered.
                    // A call resumed after a mid-call save would otherwise find
                    // it already at Talking on the very next tick, walk straight
                    // past case 1 and answer itself before the phone had rung.
                    // 0 is Ended, which is what the game writes on hang-up.
                    qs.SetFactStr(this.PhoneFact(call), 0);
                    if this.PlayerInitiated(call) {
                        // V IS DIALLING. IncomingCall first, then StartCall a
                        // beat later - it is NOT skipped.
                        //
                        // The first cut went straight to StartCall on the
                        // reasoning that there is no ring and nothing to answer.
                        // True, but it also lost the dial tone: OnTriggerCall
                        // (phoneSystem.swift:81) gates BOTH call sounds behind
                        //     shouldPlayIncomingCallSound = callPhase == IncomingCall
                        // and for a player-placed call the sound it would have
                        // played is ui_phone_initiation_call - V dialling out.
                        // the playtest got a silent connect.
                        //
                        // So: IncomingCall for the tone, then connect ourselves
                        // ~2 s later (DialToneTicks). We must NOT wait for
                        // Talking the way an
                        // incoming call does - that transition comes from
                        // OnPickupPhone, which needs the player to answer, and
                        // nobody answers a call they placed.
                        this.Call(call, questPhoneCallPhase.IncomingCall);
                        this.m_state[call] = 4;
                        this.m_waited[call] = 0;
                    } else {
                        this.Call(call, questPhoneCallPhase.IncomingCall);
                        this.m_state[call] = 1;
                        this.m_waited[call] = 0;
                        this.m_rings[call] += 1;
                    }
                }
                break;
            case 1:
                if qs.GetFactStr(this.PhoneFact(call)) == EnumInt(questPhoneTalkingState.Talking) {
                    qs.SetFactStr(p + "_answered", 1);
                    this.Call(call, questPhoneCallPhase.StartCall);
                    this.m_state[call] = 2;
                } else {
                    if qs.GetFactStr(this.PhoneFact(call))
                        == EnumInt(questPhoneTalkingState.Rejected) {
                        // DECLINED. END THE CALL OURSELVES, AND DO IT NOW.
                        //
                        // Reported in play 2026-08-17: long-pressing T to
                        // decline answered the call instead. It is this file's
                        // bug, not the game's, and the dev menu's call trace
                        // shows the whole thing:
                        //
                        //   289.6  phonecall_..._with_player = 1   ring
                        //   291.8  phonecall_..._with_player = 3   Rejected
                        //   293.3  phonecall_..._with_player = 2   Talking
                        //
                        // The decline lands at 291.8, exactly as it should.
                        // What follows is vanilla's own input handling:
                        // `PhoneReject` fires on BUTTON_HOLD_COMPLETE while
                        // the key is still down, and `PhoneInteract` fires
                        // again on BUTTON_RELEASED when it comes up, whose
                        // incoming-call branch queues a plain pickup with no
                        // hold check at all. That is the 2 at 293.3, a second
                        // and a half later.
                        //
                        // `PhoneSystem.OnPickupPhone` only ignores it once the
                        // call has left the IncomingCall phase - and vanilla
                        // gets there because its per-contact holocall phase
                        // reacts to Rejected and ends the call. We never did,
                        // so the chrome stayed up, still answerable, and the
                        // release answered it.
                        //
                        // So: end the call on the next tick, 0.2 s later,
                        // which is comfortably inside the 1.5 s the trace
                        // measured. It also fixes what the decline FELT like -
                        // the ring stopped but the banner stayed, because
                        // nothing but the 8 s timeout was going to take it
                        // down.
                        this.Call(call, questPhoneCallPhase.EndCall);
                        this.m_state[call] = 5;
                        this.m_waited[call] = 0;
                    } else {
                        // Rang out. Wait and try again; a missed call must not
                        // strand the gig. The phone itself rings for 8 s, so
                        // the shortest wait has to comfortably outlast that or
                        // we would re-ring a phone that is still ringing.
                        //
                        // The wait GROWS with each unanswered ring - see
                        // RetrySeconds. It never stops, it just stops nagging.
                        this.m_waited[call] += 1;
                        if this.m_waited[call] > this.RetryTicks(this.m_rings[call]) {
                            this.m_state[call] = 0;
                            this.m_waited[call] = 0;
                        }
                    }
                }
                break;
            case 5:
                // Declined, chrome down, waiting out the back-off.
                //
                // A separate state rather than dropping straight to 0, because
                // 0's job is to ring: going there would re-ring the phone 0.2 s
                // after the player waved it away. The wait is the same one an
                // unanswered ring gets, and m_rings was already counted when we
                // rang, so declining and ignoring back off identically. That is
                // deliberate; see RetrySeconds.
                this.m_waited[call] += 1;
                if this.m_waited[call] > this.RetryTicks(this.m_rings[call]) {
                    this.m_state[call] = 0;
                    this.m_waited[call] = 0;
                }
                break;
            case 4:
                // DIALLING. ~2 s of ui_phone_initiation_call, then we connect
                // the call ourselves. Only player-placed calls get here.
                //
                // This was `>= 1`, i.e. one tick, back when a tick WAS 2 s. The
                // dial tone is a length, not a tick - it is how long V spends
                // with the phone to his ear - so it is now counted out in ticks
                // instead of being one.
                this.m_waited[call] += 1;
                if this.m_waited[call] >= this.DialToneTicks() {
                    qs.SetFactStr(p + "_answered", 1);
                    this.Call(call, questPhoneCallPhase.StartCall);
                    this.m_state[call] = 2;
                }
                break;
            case 2:
                // The call UI has survived a whole tick (0.2 s now, not 2 s).
                // Only now let the quest phase into the scene. cc_g01_no_scene
                // is the other half of the bisect: set it from the dev menu to
                // answer the phone with no scene behind it at all.
                if qs.GetFactStr("cc_g01_no_scene") <= 0 {
                    qs.SetFactStr(p + "_talking", 1);
                }
                this.m_state[call] = 3;
                break;
            case 3:
                if qs.GetFactStr(p + "_end") > 0 {
                    this.Call(call, questPhoneCallPhase.EndCall);
                    qs.SetFactStr(p + "_done", 1);
                    this.m_state[call] = 9;
                }
                break;
        }
        // Reached only with the request fact set and the call unfinished: in
        // flight, so Tick() keeps the fast cadence.
        return true;
    }
}

public class CCGig01HolocallTick extends DelayCallback {
    public let system: wref<NegativeBalanceHolocall>;
    public func Call() -> Void {
        if IsDefined(this.system) { this.system.Tick(); }
    }
}
