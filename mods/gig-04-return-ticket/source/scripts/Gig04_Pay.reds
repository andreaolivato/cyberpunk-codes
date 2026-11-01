// Return Ticket: the fee.
//
// THE SAME ROUTE AS GIG 02 AND GIG 03, because it is the one that has been
// played: a `QuestRewards` record (source/tweaks/rewards.yaml) handed to
// `RPGManager.GiveReward`, which is the call the game's own quest reward
// node makes. The money notice, the XP scaling and the Street Cred popup
// are then the game's. docs/architecture.md, "Paying the player".
//
// The quest phase says when, by setting `cc_g04_pay`, and carries on; this
// tick pays within a second. The phase does not wait for it, as gig 03's
// does not.
//
// PAID ONCE, LATCHED IN A FACT. A field would be gone on the next load and
// the player would be paid again every time they reloaded (gotcha 21).
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

        // EVERY SYSTEM FETCH IS CHECKED BEFORE IT IS USED. This attaches at
        // the main menu, where there is no player and no quest system.
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
        // Idle until the gig is running. One fact read every six seconds.
        if qs.GetFactStr("cc_g04_started") <= 0 {
            this.Schedule(6.0);
            return;
        }
        if qs.GetFactStr("cc_g04_pay") > 0 {
            let player: ref<PlayerPuppet> = ps.GetLocalPlayerMainGameObject() as PlayerPuppet;
            if IsDefined(player) {
                qs.SetFactStr("cc_g04_paid", 1);
                RPGManager.GiveReward(game, t"QuestRewards.sts_cc_g04_completion",
                                      Cast<StatsObjectID>(player.GetEntityID()));
                this.m_settled = true;
                return;
            }
        }
        // Every half second once her last call is connected, so the fee's
        // notice comes before the completion notice (the quest waits a
        // second between the two; audit 2026-10-02). Every three seconds
        // before that.
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
