// Gig 01, Negative Balance
// Proximity watcher for arrival at the Arasaka office pin.
//
// This file used to carry a whole scripted map-pin layer (RegisterPin,
// UpdatePins, UpdateRoute and their state): a hand-placed BountyHuntVariant
// mappin plus a CustomPositionVariant waypoint to force GPS routing, written
// while native pins were believed impossible. Native pins DO work once the pin
// journal entry is activated by the quest phase (docs/map-pins-playbook.md),
// so that layer was switched off and has now been deleted. It can only fight
// the engine's own routing. Do not bring it back; fix the four ingredients.
//
// Everything else in the gig lives in Gig01_Encounter.reds (spawns, terminals,
// dialogue, epilogue, payout) and Gig01_OfficeComputer.reds (the ledger).

module CyberpunkCodes.Gig01

public class NegativeBalanceSystem extends ScriptableSystem {

    // Street point outside the compound. The spot the office map pin marks.
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

            // A FINISHED GIG COSTS THE SAVE NOTHING. Stop rescheduling once
            // cc_g01_done is set; NegativeBalanceStart's m_settled latch is the
            // model, and this system had no equivalent, so it polled once a
            // second for the rest of the playthrough.
            //
            // The stop is not persistent and does not need to be: OnAttach runs
            // on every load, one tick reads the fact and stops again. Clearing
            // cc_g01_done from the dev menu therefore does not restart the tick
            // within a session, only a reload does.
            if qs.GetFactStr("cc_g01_done") > 0 {
                return;
            }

            // Arrival at the office pin. NegativeBalanceEncounter also sets this
            // fact, on a wider radius around the compound entry, so in practice
            // that one fires first; this keeps the pin itself as a trigger in
            // case V approaches from a direction that misses the other check.
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
