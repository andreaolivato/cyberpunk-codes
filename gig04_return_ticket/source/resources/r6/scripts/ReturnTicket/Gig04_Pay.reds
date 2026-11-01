module CyberpunkCodes.Gig04

public class ReturnTicketPay extends ScriptableSystem {

    private let m_settled: Bool;

    private func OnAttach() -> Void {
        this.Schedule(6.0);
    }

    public func Schedule(delay: Float) -> Void {
        let cb: ref<CCG04PayTick> = new CCG04PayTick();
        cb.system = this;
        GameInstance.GetDelaySystem(this.GetGameInstance()).DelayCallback(cb, delay, false);
    }

    public func Tick() -> Void {
        if this.m_settled {
            return;
        }
        let game: GameInstance = this.GetGameInstance();

        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        let ps: ref<PlayerSystem> = GameInstance.GetPlayerSystem(game);
        if !IsDefined(qs) || !IsDefined(ps) {
            this.Schedule(6.0);
            return;
        }
        if qs.GetFactStr("cc_g04_paid") > 0 {
            this.m_settled = true;
            return;
        }
        if qs.GetFactStr("cc_g04_started") <= 0 {
            this.Schedule(6.0);
            return;
        }
        if qs.GetFactStr("cc_g04_pay") > 0 {
            let player: ref<PlayerPuppet> = ps.GetLocalPlayerMainGameObject() as PlayerPuppet;
            if IsDefined(player) {
                // once
                qs.SetFactStr("cc_g04_paid", 1);
                RPGManager.GiveReward(game, t"QuestRewards.sts_cc_g04_completion",
                                      Cast<StatsObjectID>(player.GetEntityID()));
                this.m_settled = true;
                return;
            }
        }
        // hodan on the line
        if qs.GetFactStr("cc_g04_close_step") > 0 {
            this.Schedule(0.5);
        } else {
            this.Schedule(3.0);
        }
    }
}

public class CCG04PayTick extends DelayCallback {
    public let system: wref<ReturnTicketPay>;

    public func Call() -> Void {
        if IsDefined(this.system) {
            this.system.Tick();
        }
    }
}
