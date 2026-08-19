// Player-facing HUD feedback. See CCShared_World.reds for why the module name
// is rewritten per gig at build time.
module CyberpunkCodes.Shared

public abstract class CCSharedHud {

    // A warning banner, which is the right control for SYSTEM feedback: a
    // download progressing, a connection dropping, an alarm.
    //
    // IT IS NOT A WAY TO GIVE A CHARACTER A LINE. Text pushed from redscript is
    // a caption with no scnlocLocstringId, therefore no RUID, therefore nothing
    // a voiceover map can ever key on, so such a line is permanently unvoiceable.
    // Six beats in gig 01 were built that way and every one of them was silent
    // in game; the fix was to rebuild them as .scene resources, not to add a
    // playback layer. If a beat needs a spoken line, write a scene.
    public static func Notify(game: GameInstance, text: String) -> Void {
        CCSharedHud.NotifyTyped(game, text, SimpleMessageType.Undefined, 4.0);
    }

    // SimpleMessageType drives the colour of the banner: Neutral reads blue,
    // Negative red, Connection is the netrunner/link styling.
    public static func NotifyTyped(game: GameInstance, text: String,
                                   kind: SimpleMessageType, seconds: Float) -> Void {
        let msg: SimpleScreenMessage;
        msg.isShown = true;
        msg.duration = seconds;
        msg.message = text;
        msg.type = kind;
        GameInstance.GetBlackboardSystem(game)
            .Get(GetAllBlackboardDefs().UI_Notifications)
            .SetVariant(GetAllBlackboardDefs().UI_Notifications.WarningMessage, ToVariant(msg), true);
    }

    // ------------------------------------------------------- THE PROGRESS BAR
    //
    // The bar the base game draws while a netrunner is uploading to you, used
    // for any timed operation a gig wants to show: a download, a copy, a
    // sabotage.
    //
    // IT IS NOT ENTITY-ATTACHED, and the two wrong answers before that one are
    // both plausible enough to be worth recording. It was first taken for
    // another mod's UI, when it had been seen in many vanilla missions. Then it
    // was driven with UploadProgramProgressEvent, which really is a vanilla
    // upload bar, but is the quickhack indicator hanging off a TARGET ENTITY
    // through GameplayRoleComponent: a small bar over the thing being hacked. It
    // showed nothing, and would have been the wrong shape anyway.
    //
    // The one that works is a HUD widget driven straight off a blackboard, the
    // way subtitles are.
    // `UploadFromNPCToPlayerListener` (rpgManager.swift:3699) writes to
    // GetAllBlackboardDefs().UI_HUDProgressBar, read by
    // cyberpunk/UI/widgets/hud_progress_bar/HUD_progress_bar.swift. No entity is
    // needed, so it does not depend on the player being plugged into anything.
    //
    // Run one with RunBar(game, header, seconds). Close it with ShowBar(game,
    // false, "").
    public static func RunBar(game: GameInstance, header: String, seconds: Float) -> Void {
        CCSharedHud.ShowBar(game, true, header);
        CCSharedHud.BarStep(game, 0.0, seconds);
    }

    public static func ShowBar(game: GameInstance, started: Bool, header: String) -> Void {
        let bb: ref<IBlackboard> = GameInstance.GetBlackboardSystem(game)
            .Get(GetAllBlackboardDefs().UI_HUDProgressBar);
        if !IsDefined(bb) {
            return;
        }
        let d: ref<UI_HUDProgressBarDef> = GetAllBlackboardDefs().UI_HUDProgressBar;
        if !started {
            // FORCE IT FULL BEFORE CLOSING. HUDProgressBarController.Outro
            // (HUD_progress_bar.swift:379) picks the failure animation whenever
            // the last Progress it saw was < 0.96:
            //
            //   if valueSaved < 0.96 && GetFact("holofixer_on") == 0
            //       -> "Quickhack_Outro_Failed"
            //
            // A playtest copy bar ended on FAILED because the beat finished at
            // 3.2 s while the fill had been told 5.2 s, so it closed at ~60%.
            // Matching the two durations fixes that case; writing 1.0 here makes
            // it structurally impossible, whatever the timings drift to.
            bb.SetFloat(d.Progress, 1.0, true);
            bb.SetBool(d.Active, false, true);
            return;
        }
        bb.SetString(d.Header, header, true);
        bb.SetString(d.BottomText, "", true);
        bb.SetString(d.CompletedText, "COMPLETE", true);
        bb.SetFloat(d.Progress, 0.0, true);
        bb.SetBool(d.Active, true, true);
    }

    // Smooth fill. The widget does not animate itself - it draws whatever
    // Progress currently holds - so the bar only moves if something keeps
    // writing to it. 0.1 s steps are well under a frame budget and read as
    // continuous.
    public static func BarStep(game: GameInstance, elapsed: Float, total: Float) -> Void {
        let bb: ref<IBlackboard> = GameInstance.GetBlackboardSystem(game)
            .Get(GetAllBlackboardDefs().UI_HUDProgressBar);
        if !IsDefined(bb) || total <= 0.0 {
            return;
        }
        let p: Float = elapsed / total;
        if p > 1.0 {
            p = 1.0;
        }
        bb.SetFloat(GetAllBlackboardDefs().UI_HUDProgressBar.Progress, p, true);
        if elapsed < total {
            let cb: ref<CCSharedHudBarStep> = new CCSharedHudBarStep();
            cb.game = game;
            cb.elapsed = elapsed + 0.1;
            cb.total = total;
            GameInstance.GetDelaySystem(game).DelayCallback(cb, 0.1, false);
        }
    }
}

public class CCSharedHudBarStep extends DelayCallback {
    public let game: GameInstance;
    public let elapsed: Float;
    public let total: Float;
    public func Call() -> Void {
        CCSharedHud.BarStep(this.game, this.elapsed, this.total);
    }
}
