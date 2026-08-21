// Gig 01: keep V on foot while one of Johnny's beats is playing.
//
// THE PROBLEM (docs/backlog.md 16). Field report against 1.2.0: *"the game got
// me used to seeing Johnny when he talks. It was weird him talking to me while
// riding a bike."* Every Johnny beat is a scene actor placed once, at a fixed
// offset in V's own frame, at the moment the scene starts. On foot that stages
// him beside V. On a bike V is past him inside a second and the rest of the
// line arrives from a point that is receding.
//
// Burying him does not help, and that was the first idea. A scene actor is one
// fixed point in the world whether it sits 2.6 m ahead or 2.5 m under, so the
// audio recedes either way. Elena and Nix only sound right on the move because
// they are holocalls going through the phone system rather than world speakers.
//
// Holding the beat until V stops does not help either, for two of the three.
// gig01_arasaka and gig01_graves are replies to a call that has just ended, so
// a wait of minutes lands them out of context, which is worse than the fault
// being fixed. Only gig01_legend can be held, and it is handled separately
// because it does not follow a call.
//
// SO THE FIX IS TO KEEP V ON FOOT rather than to move Johnny or delay him:
// refuse to ring while V is riding, and refuse to let V mount up between
// picking up and the beat finishing. Both halves live in Gig01_Holocall.reds,
// which already owns the calls; this file is the vocabulary they use.
//
// WHY OUR OWN RESTRICTION RECORD, and this is the part that took the longest.
// GameplayRestriction.VehicleNoInteraction does exactly the right thing, and it
// is SAVABLE with no useful duration: applied, saved, quit to desktop,
// relaunched and loaded, it came back still blocking. A player who uninstalls
// the mod while it happens to be applied is then left with a save that cannot
// enter a vehicle and nothing of ours to lift it. So we ship a clone with
// `savable: false` (source/tweaks/vehiclelock.yaml), measured 2026-08-21 to
// block just the same and to leave nothing behind. docs/gameplay-restrictions.md
// has the whole family and how it was measured.
//
// WHAT WAS TRIED AND CRASHED THE GAME. A @wrapMethod on
// VehicleComponent.DetermineInteractionState, to suppress the prompt from
// script and store nothing at all. It compiles and it crashes on load, because
// that method runs as a script TASK on a job worker thread and the hook read
// the quest system from there. Do not rebuild it. See docs/gotchas.md.
//
// NO TIMER OF ITS OWN. Everything here is static and is called from the
// holocall system's existing tick, which already runs only while the gig is
// live, already backs off to 2 s when nothing is in flight, and already stops
// rescheduling for good once cc_g01_done is set. Adding a second background
// system for this would have been a permanent cost for a minute of work three
// times in a playthrough.

module CyberpunkCodes.Gig01

import CyberpunkCodes.Shared.*

public class CCG01VehicleLock {

    // OURS, not the base game's. See the header.
    public static func Restriction() -> TweakDBID {
        return t"GameplayRestriction.cc_g01_no_vehicle";
    }

    // THE CONTRACT WITH THE QUEST GRAPH. The graph sets this to 1 when V picks
    // up a call that a Johnny beat follows, and back to 0 once that beat has
    // finished. Nothing here decides when a window opens; it only makes the
    // world match the fact.
    public static func WindowFact() -> CName { return n"cc_g01_vlock"; }

    // Set once if the cap below ever fires, and then honoured forever.
    //
    // WITHOUT THIS THE SEATBELT IS WORSE THAN THE FAULT. Quest facts are saved.
    // A window fact stuck at 1 would mean the cap firing on every single load,
    // so the player would lose vehicles for the first few minutes of every
    // session for the rest of that save. One failure, one recovery, never again.
    public static func GaveUpFact() -> CName { return n"cc_g01_vlock_giveup"; }

    // THE SEATBELT, AND IT IS ONLY A SEATBELT. The real answer is that a beat
    // must not be able to fail to fire; this is what happens if one does anyway.
    // Three minutes is far longer than any beat (the longest is under 15 s with
    // its glitch in and out) and short enough that a player who hits it is
    // inconvenienced rather than stuck.
    public static func CapSeconds() -> Float { return 180.0; }

    // How long before the same message may be shown again. Long enough that
    // walking a street of parked cars says it once, not once per car.
    public static func BannerGapSeconds() -> Float { return 10.0; }

    // The nudge when a call is waiting on V dismounting. Longer gap than the
    // blocked message, because that one answers something the player just did
    // and this one interrupts something they are still doing.
    public static func DismountKey() -> String { return "cc-g01-vehicle-dismount"; }
    public static func DismountGapSeconds() -> Float { return 25.0; }

    public static func Dismount(game: GameInstance) -> Void {
        CCSharedHud.NotifyTyped(game,
                                GetLocalizedTextByKey(StringToName(CCG01VehicleLock.DismountKey())),
                                SimpleMessageType.Undefined, 4.0);
    }

    public static func Player(game: GameInstance) -> ref<GameObject> {
        return GameInstance.GetPlayerSystem(game).GetLocalPlayerMainGameObject();
    }

    // IS V IN OR ON A VEHICLE. Measured 2026-08-21 with the dev menu, on foot
    // and again on a car and a bike: this returns false, then true for both.
    //
    // The PSM Vehicle blackboard int was the other candidate and is NOT used,
    // because it is not a boolean: it reads 0 on foot, 1 in a car and 6 on a
    // bike, so any test written against it is a guess about which values mean
    // mounted. This one is a plain Bool for both.
    public static func IsMounted(game: GameInstance) -> Bool {
        let player: ref<GameObject> = CCG01VehicleLock.Player(game);
        if !IsDefined(player) {
            // FAIL OPEN. Every uncertainty in this file lets the gig proceed:
            // a call that never rings strands the gig, and a beat that never
            // fires strands it harder. Being wrong about the staging is a
            // cosmetic fault; being wrong about progression is not.
            return false;
        }
        return VehicleComponent.IsMountedToVehicle(game, player);
    }

    // HAS THE SEATBELT ALREADY FIRED ON THIS SAVE. Checked around every reason
    // to lock, not just the fact, so one give-up covers all of them.
    public static func GaveUp(game: GameInstance) -> Bool {
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        if !IsDefined(qs) {
            return true;
        }
        return qs.GetFact(CCG01VehicleLock.GaveUpFact()) > 0;
    }

    // IS THE QUEST GRAPH'S WINDOW OPEN. Derived every tick and never remembered,
    // which is what makes the whole thing safe: there is no latch to get stuck
    // and no second copy of the truth to drift from the first.
    //
    // This is only half the answer. The graph cannot open its window until V
    // picks up, so the seconds while the phone is RINGING are not covered here.
    // Gig01_Holocall.RingingForBeat covers those, and the two are OR-ed in
    // UpdateVehicleLock. Reported in playtest 2026-08-21: on foot, phone rings,
    // and V could get on a bike and answer from it.
    public static func WindowOpen(game: GameInstance) -> Bool {
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        if !IsDefined(qs) {
            return false;
        }
        return qs.GetFact(CCG01VehicleLock.WindowFact()) > 0;
    }

    public static func SetLock(game: GameInstance, on: Bool) -> Void {
        let player: ref<GameObject> = CCG01VehicleLock.Player(game);
        if !IsDefined(player) {
            return;
        }
        if on {
            StatusEffectHelper.ApplyStatusEffect(player, CCG01VehicleLock.Restriction());
        } else {
            StatusEffectHelper.RemoveStatusEffect(player, CCG01VehicleLock.Restriction());
        }
    }

    // HOW CLOSE A VEHICLE HAS TO BE before saying anything about it.
    //
    // Playtest 2026-08-21: *"I got the 'Not right now' message while passing
    // nowhere near vehicles."* GetLookAtObject has no range of its own worth
    // relying on, so glancing down a street at a parked car fifty metres away
    // was enough. A little over normal interaction reach, so the message
    // arrives about when the prompt would have.
    public static func LookRange() -> Float { return 5.0; }

    // IS V LOOKING AT A VEHICLE, CLOSE ENOUGH TO HAVE GOT INTO IT.
    //
    // The restriction takes the prompt away entirely rather than refusing it,
    // so there is no key press to answer and no interaction to hook: the
    // message has to be driven by where V is looking.
    //
    // That turns out to be better than a key press would have been. It fires
    // when the prompt should have appeared and did not, so the player never
    // gets as far as pressing anything and wondering why nothing happened.
    //
    // GetLookAtObject is the same call the dev menu uses for its NPC and device
    // probes, so it is established in this project. THE RANGE IS NOT: it will
    // hand back something across the street, which is the bug above.
    public static func LookingAtVehicle(game: GameInstance) -> Bool {
        let player: ref<GameObject> = CCG01VehicleLock.Player(game);
        if !IsDefined(player) {
            return false;
        }
        let ts: ref<TargetingSystem> = GameInstance.GetTargetingSystem(game);
        if !IsDefined(ts) {
            return false;
        }
        let target: ref<GameObject> = ts.GetLookAtObject(player, false, false);
        if !IsDefined(target) {
            return false;
        }
        if !IsDefined(target as VehicleObject) {
            return false;
        }
        return Vector4.Distance(player.GetWorldPosition(), target.GetWorldPosition())
            <= CCG01VehicleLock.LookRange();
    }

    // THE BLOCKED MESSAGE, and it is the base game's own rather than ours.
    //
    // Two earlier versions were rejected in playtest 2026-08-21, and both were
    // the same two blackboard slots on UI_Notifications:
    //   OnscreenMessage  cyan, left of centre, *"invisible if I don't look at
    //                    it"*
    //   WarningMessage   red with a warning sign, top of screen, *"reads too
    //                    much as warning"*
    // Position and colour belong to the widget, so no value pushed at either
    // one changes either property. A third answer had to be a third system.
    //
    // UIInGameNotificationEvent is that system, and vanilla drives it from
    // CheckWeaponAgainstGameplayRestrictions, the notification for trying to use
    // the wrong weapon while driving. A gameplay restriction refusing an action
    // is exactly our case, so this is the game's own idiom for it rather than a
    // mod imitating one.
    //
    // IT CARRIES NO WORDS OF OURS. It reads "ACTION BLOCKED", canned, and it
    // reads the same for every member of the type enum: ActionRestriction,
    // GenericNotification, SandevistanInCallRestriction and CombatRestriction
    // were all tried and were identical. So the type below is chosen for being
    // the honest description rather than for any visible difference, and there
    // is no point trying others.
    //
    // That is a feature here. A canned system message is one players already
    // recognise, so it reads as the game refusing rather than as this mod being
    // broken, which was the whole problem with the prompt simply vanishing.
    public static func Banner(game: GameInstance) -> Void {
        let evt: ref<UIInGameNotificationEvent> = new UIInGameNotificationEvent();
        evt.m_notificationType = UIInGameNotificationType.ActionRestriction;
        evt.m_overrideCurrentNotification = true;
        GameInstance.GetUISystem(game).QueueEvent(evt);
    }
}
