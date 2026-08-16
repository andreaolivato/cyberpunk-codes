// Gig 01, Negative Balance: the office doors the base game ships switched off.
//
// REPORTED, Nexus 1.1.x, 2026-08-15: "the path routed me to a door that
// wouldn't open and every other door or access that i tried just sent me around
// the outside but not into the building", from a player whose save is early and
// who has not done the main quests in this district.
//
// He is right, and it is not our route that is wrong. Read out of the shipped
// streaming sectors: every door in the Arasaka Industrial Park is authored
// inside `loc_q112_arasaka_industrial_park_warehouse`, and the five below carry
// `deviceState: DISABLED` as their initial state. `q112` is "Gimme Danger"
// (confirmed from the VO corpus: Takemura, the parade floats, "We break into
// Arasaka Industrial Park"), so the base game switches them on during that
// mission and they stay on afterwards.
//
// The measurement that made it a finding rather than a suspicion: across all 46
// cached exterior sectors there are 96 doors, 87 ON and 9 DISABLED, and all 9 of
// the disabled ones are in this one compound. Confirmed in game on a
// pre-"Gimme Danger" save, 2026-08-16: all five report DISABLED when they
// stream in.
//
// Every playtest of this gig had run on a late save where "Gimme Danger" was
// long done, so these doors were open for months of testing and were never
// anybody's variable. Nothing in the mod touches them, so nothing in the mod
// pointed at them. Gigs 02-04 should watch for the same class of blind spot: not
// a latch the gig itself sets (docs/gotchas.md #21), but a base-game device
// state an earlier main quest already changed.
//
// ---------------------------------------------------------------------------
// WHAT THIS FILE DOES
//
// While the gig is live, and only then, it walks those doors up to ON. It never
// switches anything off. Opening a door the base game will open later is
// harmless; closing one is not, and a restore that ran at the wrong moment
// would shut a player inside a building with no way to attribute it to us.
// There is deliberately no restore.
//
// The vehicle gates (three `gate_1`, also DISABLED) are left alone. V walks in;
// nothing in the gig needs a truck gate, and they are a large visible change
// for no gain.
//
// ---------------------------------------------------------------------------
// TWO STEPS, NOT ONE, AND A FRAME BETWEEN THEM. THIS IS THE WHOLE FILE
//
// Measured in game on 2026-08-16, one action at a time:
//
//     DISABLED  --ActionQuestForceEnabled-->  OFF  --ActionQuestForceON-->  ON
//
// Neither action alone is enough. `ForceEnabled` takes the door out of DISABLED
// and leaves it OFF, and an OFF door offers the player no interaction at all:
// no prompt, not even a "Locked" one. Only ON is a working door.
//
// **And `ExecutePSAction` is DEFERRED.** The state does not change in the frame
// the action is sent. That cost two rounds of testing: the first build sent
// `ForceEnabled` and read the state straight back, saw DISABLED, and concluded
// nothing had happened - while the door was in fact OFF by the time anyone
// looked at it. A CET probe then sent five actions in one frame to find the
// right one, read the state after each, and "proved" that only a direct
// `SetDeviceState` worked. It proved nothing: every read was of the state before
// its own action, and the five actions raced. The door it ran on ended up
// reporting EDeviceStatus 4294967294, which is not a state at all.
//
// So the two steps CANNOT be sent together and hoped for. This runs one step per
// pass, half a second apart, re-reading the state each time:
//
//     pass 0   DISABLED -> send ForceEnabled
//     pass 1   OFF      -> send ForceON
//     pass 2   ON       -> stop
//
// It is written as "look at the state, take one step towards ON" rather than as
// a fixed sequence, so it is correct from whatever state a door is in. A door
// already OFF (this project's own earlier build left five of them that way on
// one save) starts at step two; a door already ON costs one read and stops.
//
// CAPPED AT SIX PASSES, three seconds. A pump that cannot end is worse than a
// door that does not open, and this one runs on a base-game device.
//
// ---------------------------------------------------------------------------
// ONE HOOK. THE SECOND ONE WAS SHIPPED, MEASURED, AND IS GONE
//
// The previous build hooked `GameAttached` and `SetDefaultDoorState`, because
// neither one's timing could be established offline, and had each record which
// of them did the work. The answer came back on the first run: everything was
// route 1. `SetDefaultDoorState` never fired, for any door in the game, so it is
// deleted rather than left in as insurance nobody has seen work.
//
// `DoorControllerPS.OnGameAttached(GameAttachedEvent)` does NOT exist, which the
// compiler said before any of this was written. Do not reach for it.
//
// ---------------------------------------------------------------------------
// WHEN IT RUNS
//
// `GameAttached` fires when a door's persistent state attaches, which is when
// its sector streams in, which is when the player arrives. So it needs no new
// save and no restart: load a save with the gig running, go to the office, and
// the doors are dealt with on the way in.
//
// It will NOT act on a door that is ALREADY streamed in. Switching
// `cc_g01_accepted` on from the dev menu while standing at the door does nothing
// until the sector reloads. That is a testing trap, not a player-facing one: a
// player accepts the gig on Elena's call and travels here afterwards.
//
// Two facts, both quest facts and so both persistent in the save:
//
//   cc_g01_doors_opened     how many of the five this save has taken to ON
//   cc_g01_dbg_door_state   what the last door reported when it streamed in:
//                           1 DISABLED, 2 ON, 3 OFF, 4 UNPOWERED, 9 other
//   cc_g01_dbg_door_giveup  pumps that ran out of passes. Must stay 0

module CyberpunkCodes.Gig01

public abstract class CCG01Doors {

    // THE DOORS, every one read out of the sector rather than captured in game.
    // The authored node position IS the door position, so there is nothing to
    // calibrate. Confirmed in game: the look-at dump of index 1 reported
    // -219.790, -1423.176, 14.600 against the -219.8, -1423.2, 14.6 below.
    //
    // The two that matter are the two the gig's own route depends on, and they
    // sit within 2 m of positions this mod already had:
    //
    //   index 0  =  CCGig01Places.OfficeEntry()  (1.8 m)
    //   index 1  =  CCGig01Places.InnerEntry()   (0.9 m)
    //
    // 2 and 3 are the other two doors on the office floor, 4 is the ground
    // floor. They are here because the report was that EVERY route led back
    // outside: fixing only the two we walk ourselves would leave a player who
    // approaches from another side exactly where the reporter was.
    //
    // NOT here, deliberately: the door into the terminal room itself
    // (-256.3, -1450.8, 14.6). It ships ON. What is shut is the way onto the
    // office floor, not the office.
    public static func Count() -> Int32 { return 5; }

    public static func Pos(i: Int32) -> Vector4 {
        switch i {
            case 0: return new Vector4(-241.9, -1450.7, 14.6, 1.0);  // {glass_door_k}
            case 1: return new Vector4(-219.8, -1423.2, 14.6, 1.0);  // single_sliding_door_1
            case 2: return new Vector4(-252.6, -1443.3, 14.6, 1.0);  // {door}
            case 3: return new Vector4(-265.3, -1435.8, 14.6, 1.0);  // {door}
            default: return new Vector4(-260.9, -1452.2, 8.6, 1.0);  // double_door_simple_1
        }
    }

    // Tight, because it can be. The nearest door we do NOT want is 9 m away, and
    // these positions are authored rather than paced out, so there is no capture
    // error to absorb.
    public static func Radius() -> Float { return 3.0; }

    public static func IsOurDoor(pos: Vector4) -> Bool {
        let i: Int32 = 0;
        while i < CCG01Doors.Count() {
            if Vector4.Distance(pos, CCG01Doors.Pos(i)) <= CCG01Doors.Radius() {
                return true;
            }
            i += 1;
        }
        return false;
    }

    // OUR OWN encoding, not `EnumInt`. The numeric values behind EDeviceStatus
    // are not written down anywhere readable, and the game prints OFF as 0,
    // so an EnumInt in a fact would be indistinguishable from a fact nobody
    // ever set.
    public static func StateCode(st: EDeviceStatus) -> Int32 {
        if Equals(st, EDeviceStatus.DISABLED) { return 1; }
        if Equals(st, EDeviceStatus.ON) { return 2; }
        if Equals(st, EDeviceStatus.OFF) { return 3; }
        if Equals(st, EDeviceStatus.UNPOWERED) { return 4; }
        return 9;
    }

    public static func MaxPasses() -> Int32 { return 6; }

    // Is this one of ours, and does the gig want it open? Called on every door
    // attach in the game, so it is ordered cheapest-first: the position test
    // throws out the whole world before a fact is read.
    public static func OnAttached(ps: ref<DoorControllerPS>) -> Void {
        if !IsDefined(ps) {
            return;
        }
        let owner: ref<GameObject> = ps.GetOwnerEntityWeak() as GameObject;
        if !IsDefined(owner) || !CCG01Doors.IsOurDoor(owner.GetWorldPosition()) {
            return;
        }
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(ps.GetGameInstance());
        if !IsDefined(qs) {
            return;
        }
        // ONLY WHILE THE GIG IS LIVE. cc_g01_accepted is the point at which the
        // player has been sent here, and it never returns to 0 on a real save.
        // A player who never takes the gig gets the compound the base game gave
        // him.
        if qs.GetFactStr("cc_g01_accepted") <= 0 {
            return;
        }
        qs.SetFactStr("cc_g01_dbg_door_state",
                      CCG01Doors.StateCode(ps.GetDeviceState()));
        CCG01Doors.Pump(ps, 0);
    }

    // One step towards ON, then come back and look again. See the header for
    // why this is a pump and not two lines in a row.
    public static func Pump(ps: ref<DoorControllerPS>, pass: Int32) -> Void {
        if !IsDefined(ps) {
            // The sector unloaded under us. Nothing to do and nothing wrong:
            // the next attach starts a fresh pump.
            return;
        }
        let game: GameInstance = ps.GetGameInstance();
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        if !IsDefined(qs) {
            return;
        }

        if Equals(ps.GetDeviceState(), EDeviceStatus.ON) {
            // Only count a door WE moved. A door that was already ON when it
            // streamed in - every door on a post-"Gimme Danger" save - arrives
            // here at pass 0 and is not ours to claim.
            if pass > 0 {
                qs.SetFactStr("cc_g01_doors_opened",
                              qs.GetFactStr("cc_g01_doors_opened") + 1);
            }
            return;
        }

        if pass >= CCG01Doors.MaxPasses() {
            qs.SetFactStr("cc_g01_dbg_door_giveup",
                          qs.GetFactStr("cc_g01_dbg_door_giveup") + 1);
            return;
        }

        if ps.IsDisabled() {
            ps.ExecutePSAction(ps.ActionQuestForceEnabled(), ps);
        } else {
            ps.ExecutePSAction(ps.ActionQuestForceON(), ps);
        }

        let cb: ref<CCG01DoorPump> = new CCG01DoorPump();
        cb.ps = ps;
        cb.pass = pass + 1;
        GameInstance.GetDelaySystem(game).DelayCallback(cb, 0.5, false);
    }
}

public class CCG01DoorPump extends DelayCallback {
    public let ps: wref<DoorControllerPS>;
    public let pass: Int32;

    public func Call() -> Void {
        CCG01Doors.Pump(this.ps, this.pass);
    }
}

// Fires when a door's persistent state attaches, which is when its sector
// streams in. The only hook: see the header for the one that was measured and
// deleted.
@wrapMethod(DoorControllerPS)
public func GameAttached() -> Void {
    wrappedMethod();
    CCG01Doors.OnAttached(this);
}
