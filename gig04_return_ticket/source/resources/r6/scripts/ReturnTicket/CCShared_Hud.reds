module CyberpunkCodes.Shared.Gig04

public abstract class CCSharedHud {

    public static func Notify(game: GameInstance, text: String) -> Void {
        // 4s
        CCSharedHud.NotifyTyped(game, text, SimpleMessageType.Undefined, 4.0);
    }

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
            // full before closing
            bb.SetFloat(d.Progress, 1.0, true);
            bb.SetBool(d.Active, false, true);
            return;
        }
        bb.SetString(d.Header, header, true);
        bb.SetString(d.BottomText, "", true);
        bb.SetString(d.CompletedText,
            GetLocalizedTextByKey(n"Story-base-gameplay-gui-widgets-hud_progress_bar-hud_progress_bar-_localizationString11"),
            true);
        bb.SetFloat(d.Progress, 0.0, true);
        bb.SetBool(d.Active, true, true);
    }

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
