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
}
