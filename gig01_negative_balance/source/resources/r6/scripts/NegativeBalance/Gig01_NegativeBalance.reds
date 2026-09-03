module CyberpunkCodes.Gig01

public class NegativeBalanceSystem extends ScriptableSystem {

    // on the street
    private func OfficePin() -> Vector4 {
        return new Vector4(-177.761, -1472.829, 7.477, 1.0);
    }

    private func OnAttach() -> Void {
        this.ScheduleTick(5.0);
    }

    public func ScheduleTick(delay: Float) -> Void {
        let callback: ref<CCGig01TickCallback> = new CCGig01TickCallback();
        callback.system = this;
        GameInstance.GetDelaySystem(this.GetGameInstance()).DelayCallback(callback, delay, false);
    }

    public func Tick() -> Void {
        let game: GameInstance = this.GetGameInstance();
        let player: ref<PlayerPuppet> = GameInstance.GetPlayerSystem(game)
            .GetLocalPlayerMainGameObject() as PlayerPuppet;

        if IsDefined(player) {
            let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);

            if qs.GetFactStr("cc_g01_done") > 0 {
                return;
            }

            if qs.GetFactStr("cc_g01_accepted") == 1 && qs.GetFactStr("cc_g01_office_reached") == 0 {
                if Vector4.Distance(player.GetWorldPosition(), this.OfficePin()) < 25.0 {
                    qs.SetFactStr("cc_g01_office_reached", 1);
                }
            }
        }
        this.ScheduleTick(1.0);
    }
}

public class CCGig01TickCallback extends DelayCallback {
    public let system: wref<NegativeBalanceSystem>;

    public func Call() -> Void {
        if IsDefined(this.system) {
            this.system.Tick();
        }
    }
}
