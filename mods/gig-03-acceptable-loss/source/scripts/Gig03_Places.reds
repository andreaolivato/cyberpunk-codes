// Gig 03, Acceptable Loss: where the player is, and what that advances.
//
// Most of the gig's objectives complete by the player being somewhere. This is
// the one poll that decides them, so there is one place to look when an
// objective sticks, and one place where the geometry is written down. It also
// carries the three things that happen to the player's inventory: the fee, the
// shard being destroyed, and the advance being taken back.
//
// ---------------------------------------------------------------------------
// OUT OF THE BADLANDS IS A QUESTION FOR THE GAME, NOT FOR A POLYGON
//
// The objective after the compound is "leave the Badlands", and the stars stay
// on until then. The line is the game's own: the prevention system keeps the
// district the player is standing in, read off the district trigger areas,
// and `District.IsBadlands()` looks through a named sub-district to its
// parent. `CCSharedPrevention.District` wraps it. A null answer is unknown
// (the stack is empty for a frame or two after a load), and unknown is treated
// as still inside, so a reload on the road cannot end the chase early.
//
// ---------------------------------------------------------------------------
// JOHNNY WAITS FOR V TO BE ON FOOT
//
// The argument on the way home is staged beside V, and a V at the wheel
// leaves the body behind on the road (gig 01's backlog 16, reported by
// players). Leaving the Badlands is almost always done by car, so the beat
// waits for two things: the stars are gone, and V is not in a vehicle. Both
// are certain to happen (the last leg into Dino's bar is on foot), and
// the heat half is capped at ten minutes in case the drop is ever refused, so
// a wait that exists to stage a body cannot stall the gig (gotcha 104).
//
// ---------------------------------------------------------------------------
// THE PERIMETER IS A REAL POLYGON, NOT A RADIUS
//
// The compound was WALKED, corner by corner, in order, so the ten points below
// close into the fence as it stands. A circle around the middle would have to
// be 45 m to cover the far corners and would then reach 20 m past the wall on
// the short sides, which is the difference between "inside the wire" meaning
// something and meaning nothing.
//
// `Inside()` is an even-odd crossing test in the XY plane with a separate
// height check, and the height check is deliberately asymmetric: the Badlands
// has ground under it, and a test whose floor reaches far enough down fires for
// a player driving through a culvert. Same reasoning as CCSharedWorld.Near.
//
// ---------------------------------------------------------------------------
// LEAVING IS NOT THE OPPOSITE OF ARRIVING
//
// `cc_g03_escaped` is not simply "outside the polygon". A player who steps over
// the wall and back is not escaping, and one shot dead at the gate has not
// escaped either. So the test is outside the wire AND more than 60 m from the
// middle of it, which is far enough that the compound is behind them rather
// than around them.
//
// ---------------------------------------------------------------------------
// EVERY FACT HERE IS ONE-WAY
//
// Nothing in this file ever sets a fact back to 0. Objectives that un-complete
// themselves when the player wanders are worse than objectives that complete a
// little early, and a fact that can go backwards is a quest phase that can run
// a node twice. Gotcha 21.

module CyberpunkCodes.Gig03

import CyberpunkCodes.Shared.*

public abstract class CCG03Places {

    // THE WALKED PERIMETER, in order. Same ten corners as gig03_config.py and
    // the dev menu's census; if one of the three changes, all three must.
    public static func Corners() -> Int32 { return 10; }

    public static func Corner(i: Int32) -> Vector4 {
        switch i {
            case 0: return new Vector4(-94.603, -5182.958, 87.070, 1.0);
            case 1: return new Vector4(-93.260, -5191.834, 87.070, 1.0);
            case 2: return new Vector4(-63.751, -5188.975, 87.070, 1.0);
            case 3: return new Vector4(-58.180, -5240.128, 87.198, 1.0);
            case 4: return new Vector4(-62.299, -5241.255, 87.106, 1.0);
            case 5: return new Vector4(-62.074, -5245.433, 87.133, 1.0);
            case 6: return new Vector4(-125.795, -5250.342, 87.042, 1.0);
            case 7: return new Vector4(-130.538, -5205.756, 87.096, 1.0);
            case 8: return new Vector4(-138.655, -5207.188, 87.074, 1.0);
            default: return new Vector4(-141.365, -5185.973, 87.026, 1.0);
        }
    }

    // The middle of the compound, used for the arrival and escape distances.
    public static func Middle() -> Vector4 {
        return new Vector4(-97.052, -5213.984, 87.1, 1.0);
    }

    public static func Terminal() -> Vector4 {
        return new Vector4(-133.173, -5193.786, 88.564, 1.0);
    }

    // DINO'S STOOL, at his bar in Downtown: the AI spot his own community
    // entry sits him on, read out of the shipped sector on 2026-09-15 (the
    // same number as gig03_config.DINO_POS and gen_community.py). Nobody
    // has stood at it in play yet; the first playtest of the bar leg is what
    // checks it.
    public static func Dino() -> Vector4 {
        return new Vector4(-1969.884, 377.748, 8.046, 1.0);
    }

    // THE SWAP RADIUS. Within this distance of the stool, in plan, the game's
    // own Dino is taken out and ours put in, so it has to be far enough that
    // the stool is not yet in view. 35 m is a desk guess for a bar under a
    // tech shell (Regina's swap was keyed to a street door 48 m below her
    // floor); replace it with a measured one if a playtest sees the swap.
    public static func SwapRadius() -> Float { return 35.0; }

    // LEFT THE BAR: this far from the stool again, in plan, or well above or
    // below it. Everything that would look wrong done in front of him waits
    // on this. THE SAME CIRCLE IS DRAWN ON THE MINIMAP as the "leave the
    // bar" zone (gen_community.py ships it as a 16-gon inscribed in it, so
    // the outline goes up to 0.7 m before this fires); gig03_config.py's
    // DINO_LEAVE_RADIUS is the one number, and if one changes all three
    // must. The same as the swap-in radius on purpose.
    public static func LeaveRadius() -> Float { return 35.0; }

    // APPROACHING: inside the swap radius, at his level.
    public static func AtBar(pos: Vector4) -> Bool {
        let him: Vector4 = CCG03Places.Dino();
        return AbsF(pos.Z - him.Z) < 6.0
            && Vector4.Distance2D(pos, him) <= CCG03Places.SwapRadius();
    }

    public static func LeftDino(pos: Vector4) -> Bool {
        let him: Vector4 = CCG03Places.Dino();
        if AbsF(pos.Z - him.Z) > 10.0 {
            return true;
        }
        return Vector4.Distance2D(pos, him) > CCG03Places.LeaveRadius();
    }

    // EVEN-ODD CROSSING, in XY. Ground across the compound runs 87.03 to 87.20,
    // so 6 m of headroom covers the walkways and the roof edge without reaching
    // anything below.
    public static func Inside(pos: Vector4) -> Bool {
        let mid: Vector4 = CCG03Places.Middle();
        if pos.Z < mid.Z - 4.0 || pos.Z > mid.Z + 12.0 {
            return false;
        }
        let crossings: Bool = false;
        let n: Int32 = CCG03Places.Corners();
        let j: Int32 = n - 1;
        let i: Int32 = 0;
        while i < n {
            let a: Vector4 = CCG03Places.Corner(i);
            let b: Vector4 = CCG03Places.Corner(j);
            // NotEquals, not `!=`: redscript has no inequality operator for
            // Bool, and the error it gives instead names TweakDBID, which is
            // the overload it fell back to.
            if NotEquals((a.Y > pos.Y), (b.Y > pos.Y))
                && (pos.X < (b.X - a.X) * (pos.Y - a.Y) / (b.Y - a.Y) + a.X) {
                crossings = !crossings;
            }
            j = i;
            i += 1;
        }
        return crossings;
    }

    // ARRIVING is generous on purpose: it is what closes "get to the site", and
    // the player can see the compound from well outside it. 80 m in plan.
    public static func Arrived(pos: Vector4) -> Bool {
        return Vector4.Distance2D(pos, CCG03Places.Middle()) <= 80.0;
    }

    // ESCAPED. Outside the wire is not enough; see the header.
    public static func Escaped(pos: Vector4) -> Bool {
        if CCG03Places.Inside(pos) {
            return false;
        }
        return Vector4.Distance2D(pos, CCG03Places.Middle()) > 60.0;
    }

    public static func AtTerminal(pos: Vector4) -> Bool {
        return CCSharedWorld.Near(pos, CCG03Places.Terminal(), 5.0, 3.0, 3.0);
    }

    // THE CABINET THE SHARD STANDS ON, in the security room. Captured
    // 2026-09-09. Being within TWO metres of it means being in the room,
    // past the door, which is the fallback alarm for a door that was somehow
    // already open (Gig03_Alarm.reds has the door itself).
    //
    // TWO METRES, NOT FOUR. The door is 3.15 m from the cabinet, so a 4 m
    // radius reached through the wall to the doorstep and the fallback fired
    // on a player standing at the closed door: playtest 2026-09-15, "the
    // trace started before I opened the door" (`cc_g03_dbg_alarm_src` reads
    // 2 for that). Two metres is inside the room and nowhere else.
    public static func Cabinet() -> Vector4 {
        return new Vector4(-95.621, -5211.431, 87.135, 1.0);
    }

    public static func AtCabinet(pos: Vector4) -> Bool {
        return CCSharedWorld.Near(pos, CCG03Places.Cabinet(), 2.0, 2.5, 2.5);
    }

    // WHAT THE CLIENT'S ADVANCE WAS, and what V pays back for destroying the
    // ledger. The fee was 12,500 (half of 25,000); the advance is a fifth of
    // the whole job. Taken out of the wallet, capped at what is in it.
    public static func Advance() -> Int32 { return 5000; }

    // How long the on-foot wait tolerates the stars staying up before it
    // stops waiting for them: 300 ticks of two seconds.
    public static func HeatWaitTicks() -> Int32 { return 300; }

    // THE RESTRICTION RECORD: NoMovement, cloned with saving off
    // (source/tweaks/restrictions.yaml, and docs/gameplay-restrictions.md
    // for why the clone).
    public static func HoldRecord() -> TweakDBID {
        return t"GameplayRestriction.cc_g03_hold";
    }

    // The cap on the hold, in ticks of two seconds: thirty seconds.
    public static func HoldCapTicks() -> Int32 { return 15; }


    // AT HIM: within 4 m of the stool, at his level. He sits with the bar
    // in front of him, so V arrives from beside or behind the stool.
    public static func AtDino(pos: Vector4) -> Bool {
        return CCSharedWorld.Near(pos, CCG03Places.Dino(), 4.0, 3.0, 3.0);
    }

    // THE FEE IS A REWARD RECORD, NOT A NUMBER HERE.
    //
    // `source/tweaks/rewards.yaml` carries it: 12,500 eddies, and the base
    // record's 1,000 XP and 1,136 Street Cred scaled to the player's level.
    // Handing the money over directly instead puts it in the wallet and shows
    // nothing at all, which is what this gig did first.
    public static func Reward() -> TweakDBID {
        return t"QuestRewards.sts_cc_g03_completion";
    }
}

public class AcceptableLossPlaces extends ScriptableSystem {

    private let m_settled: Bool;
    // The game's own Dino bodies disposed this session, by id, and how many
    // times each. NOT A ONE-SHOT LATCH: a community body keeps its id
    // across respawns (its ids are fixed per entry, gotcha 64), so a body
    // that is put back after a dispose is the same id seen again, and a
    // keeper that remembered ids for good ignored him for the rest of the
    // session. The count caps a fight that could otherwise run all night.
    private let m_disposed: array<EntityID>;
    private let m_disposedTimes: array<Int32>;
    // Ticks spent waiting for the stars to go before Johnny's ride beat. A
    // field on purpose: a reload starts the count again, and the question is
    // being asked again from the start.
    private let m_heatWaitTicks: Int32;
    // The shard's destruction has been scheduled this session.
    private let m_destroyScheduled: Bool;
    // THE HOLD, for Johnny at V's door. Whether this session believes the
    // restriction is on V, how many ticks it has been, and whether the
    // first-pass cleanup has run. All three are session fields on purpose:
    // the record is not savable, so a load starts with nothing applied and
    // nothing believed (docs/gameplay-restrictions.md).
    private let m_holdOn: Bool;
    private let m_holdTicks: Int32;
    private let m_holdChecked: Bool;

    private func OnAttach() -> Void {
        this.Schedule(6.0);
    }

    public func Schedule(delay: Float) -> Void {
        let cb: ref<CCG03PlacesTick> = new CCG03PlacesTick();
        cb.system = this;
        GameInstance.GetDelaySystem(this.GetGameInstance()).DelayCallback(cb, delay, false);
    }

    public func Tick() -> Void {
        if this.m_settled {
            return;
        }
        let game: GameInstance = this.GetGameInstance();

        // EVERY SYSTEM FETCH IS CHECKED BEFORE IT IS USED. This attaches at the
        // main menu, where there is no player and no quest system, and
        // dereferencing that null flatlines the game before a save is loaded.
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        let ps: ref<PlayerSystem> = GameInstance.GetPlayerSystem(game);
        if !IsDefined(qs) || !IsDefined(ps) {
            this.Schedule(6.0);
            return;
        }

        if qs.GetFactStr("cc_g03_done") > 0 {
            // THE HOLD COMES OFF HERE TOO. The graph sets `cc_g03_johnny_done`
            // and `cc_g03_done` in the same frame, so the first tick after
            // Johnny's scene sees the gig finished and settled here, before
            // the hold below could read the release: playtest 2026-09-15,
            // "I was never unlocked". Removing an absent effect costs
            // nothing, so it is done on the way out whether or not this
            // session believes it holds one.
            let held: ref<GameObject> = ps.GetLocalPlayerMainGameObject();
            if IsDefined(held) {
                StatusEffectHelper.RemoveStatusEffect(held, CCG03Places.HoldRecord());
                if qs.GetFactStr("cc_g03_dbg_hold") == 1 {
                    qs.SetFactStr("cc_g03_dbg_hold", 2);
                }
            }
            this.m_settled = true;
            return;
        }
        // Idle until the gig is running. One fact read every six seconds.
        if qs.GetFactStr("cc_g03_start") <= 0 {
            this.Schedule(6.0);
            return;
        }

        let player: ref<GameObject> = ps.GetLocalPlayerMainGameObject();
        if !IsDefined(player) {
            this.Schedule(6.0);
            return;
        }
        let pos: Vector4 = player.GetWorldPosition();

        if qs.GetFactStr("cc_g03_arrived") <= 0 {
            if CCG03Places.Arrived(pos) {
                qs.SetFactStr("cc_g03_arrived", 1);
            }
        } else if qs.GetFactStr("cc_g03_inside") <= 0 {
            if CCG03Places.Inside(pos) {
                qs.SetFactStr("cc_g03_inside", 1);
            }
        } else if qs.GetFactStr("cc_g03_terminal") <= 0 {
            if CCG03Places.AtTerminal(pos) {
                qs.SetFactStr("cc_g03_terminal", 1);
            }
        }

        // THE SECURITY ROOM, AS A FALLBACK. The door is the trigger
        // (Gig03_Alarm.reds); this catches a player who is standing at the
        // cabinet with no door event behind them, and it fires before the
        // shard can be picked up because the cabinet is inside the radius.
        if qs.GetFactStr("cc_g03_data") > 0
            && qs.GetFactStr("cc_g03_alarm") <= 0 {
            if CCG03Places.AtCabinet(pos) {
                if qs.GetFactStr("cc_g03_dbg_alarm_src") <= 0 {
                    qs.SetFactStr("cc_g03_dbg_alarm_src", 2);
                }
                CCG03Alarm.Raise(game);
            }
        }

        // ESCAPING IS ONLY WATCHED ONCE THE SHARD IS IN HAND. Before that the
        // player is free to walk in and out of the compound while scouting, and
        // "escaped" would fire on the way in.
        if qs.GetFactStr("cc_g03_shard_got") > 0
            && qs.GetFactStr("cc_g03_escaped") <= 0 {
            if CCG03Places.Escaped(pos) {
                qs.SetFactStr("cc_g03_escaped", 1);
            }
        }

        // OUT OF THE BADLANDS. Asked of the game, once the compound is behind
        // V. Gig03_Trace.reds drops the stars on this fact.
        //
        // WHETHER V IS IN A VEHICLE AT THAT MOMENT is written first, as
        // `cc_g03_mounted` (1 in one, 2 on foot), because the graph reads it
        // on the frame `badlands_left` arrives to decide whether to put "Get
        // out of the vehicle" on screen. Playtest, 2026-09-11: "after I escape
        // the Badlands I have no indication to leave the vehicle". Written
        // before the trigger fact, never after, so the graph cannot read it
        // unset.
        if qs.GetFactStr("cc_g03_escaped") > 0
            && qs.GetFactStr("cc_g03_badlands_left") <= 0 {
            let district: wref<District> = CCSharedPrevention.District(game);
            if IsDefined(district) && !district.IsBadlands() {
                if VehicleComponent.IsMountedToVehicle(game, player) {
                    qs.SetFactStr("cc_g03_mounted", 1);
                } else {
                    qs.SetFactStr("cc_g03_mounted", 2);
                }
                qs.SetFactStr("cc_g03_badlands_left", 1);
            }
        }

        // ON FOOT, AND THE STARS GONE, before Johnny speaks. See the header.
        if qs.GetFactStr("cc_g03_badlands_left") > 0
            && qs.GetFactStr("cc_g03_on_foot") <= 0 {
            let mounted: Bool = VehicleComponent.IsMountedToVehicle(game, player);
            let heat: Int32 = CCSharedPrevention.Heat(game);
            if heat > 0 {
                this.m_heatWaitTicks += 1;
            }
            let heatOk: Bool = heat <= 0
                || this.m_heatWaitTicks >= CCG03Places.HeatWaitTicks();
            if !mounted && heatOk {
                qs.SetFactStr("cc_g03_on_foot", 1);
            }
        }

        // THE SHARD IS DESTROYED, three seconds into Johnny's scene, so it
        // lands while he is still talking and before V answers him.
        if qs.GetFactStr("cc_g03_loyal") > 0
            && qs.GetFactStr("cc_g03_shard_destroyed") <= 0
            && !this.m_destroyScheduled {
            this.m_destroyScheduled = true;
            let cb: ref<CCG03DestroyCall> = new CCG03DestroyCall();
            cb.game = game;
            GameInstance.GetDelaySystem(game).DelayCallback(cb, 3.0, false);
        }

        // THE ADVANCE, TAKEN BACK. Set by the graph as Dino's loud scene
        // ends, the same moment the fee lands on the other ending.
        if qs.GetFactStr("cc_g03_docked") > 0
            && qs.GetFactStr("cc_g03_dock_paid") <= 0 {
            this.Dock(game, qs, player as PlayerPuppet);
        }

        // THE SWAP, ON THE WAY IN. Coming within the swap radius of his stool
        // is what takes the game's own Dino out and puts ours in, so by the
        // time the stool is in view the body sitting there is already the
        // right one. Playtest 2026-09-10, on Regina: done at the scene
        // instead, "as I enter the room it goes from her default pose to our
        // body and I can see the jump".
        if qs.GetFactStr("cc_g03_unlock_dino") > 0
            && qs.GetFactStr("cc_g03_at_bar") <= 0 {
            if CCG03Places.AtBar(pos) {
                qs.SetFactStr("cc_g03_at_bar", 1);
            }
        }

        // THE HANDOVER. Only once the gig has sent V there, so standing at
        // Dino's bar earlier in the save does nothing. This starts his scene;
        // the money comes AFTER it (below), not here.
        if qs.GetFactStr("cc_g03_unlock_dino") > 0
            && qs.GetFactStr("cc_g03_delivered") <= 0 {
            if CCG03Places.AtDino(pos) {
                qs.SetFactStr("cc_g03_delivered", 1);
            }
        }

        // THE FEE, once his scene has ended. Set by the graph on the calm
        // scene's exit, the way `cc_g03_docked` is set on the loud one's, so
        // both endings settle up at the same moment: after he has said his
        // piece and before V walks out. Playtest 2026-09-15: "the eddies
        // arrive too early... they should arrive after we talk with Dino,
        // before we exit the pub". Until then the fee landed at the stool,
        // as the scene started.
        if qs.GetFactStr("cc_g03_pay_due") > 0
            && qs.GetFactStr("cc_g03_paid") <= 0 {
            this.Pay(game, qs);
        }

        // AND WHEN THE PLAYER LEAVES. Everything that would look wrong done in
        // front of them waits on this: putting the game's own Dino back, and
        // Johnny's last word. Playtest 2026-09-10, on Regina: "our body
        // disappears, stays empty a bit, then the old default body appears,
        // all while I'm still there".
        //
        // ON FOOT ONLY. Johnny is staged beside V, and a V at the wheel
        // leaves him on the road (gig 01's backlog 16); so a V who drives
        // out of the area is not "left" until they get out of the car. And
        // the moment it fires, V IS HELD STILL (below), so V cannot walk
        // past him: the design call, 2026-09-15, "trigger stop movement,
        // after the movement stop trigger Johnny, after he glitches out
        // remove the movement block".
        if qs.GetFactStr("cc_g03_delivered") > 0
            && qs.GetFactStr("cc_g03_left_dino") <= 0 {
            if CCG03Places.LeftDino(pos)
                && !VehicleComponent.IsMountedToVehicle(game, player) {
                qs.SetFactStr("cc_g03_left_dino", 1);
            }
        }

        // THE HOLD. Wanted from the moment V has left until Johnny's scene
        // has ended (`cc_g03_johnny_done`, set by the graph on its exit), and
        // for thirty seconds at the very most, so a scene that never plays
        // cannot leave V rooted. Recomputed from facts on every tick rather
        // than remembered, the shape gig 01's ApplyLock has: a plain field
        // does not survive a load, so on the first pass of a session a
        // removal is issued for a hold this session does not believe it
        // holds. Removing an absent effect costs nothing.
        this.Hold(game, qs, player);

        // THE GAME'S OWN DINO, IF HE LINGERS. The quest graph switches his
        // community entry off at the swap and ours on, and a body that is
        // already sitting there does not always go with the switch: playtest
        // 2026-09-11, on Regina, "now there are two Reginas". Gig 02's Wakako
        // had the same and its ParlorKeeper is this. Between the swap and the
        // player leaving, any `Character.dyno` within 20 m of his stool is
        // disposed. Ours is `Character.cc_g03_dino` and is never touched.
        //
        // AFTER THE GRAPH HAS SWITCHED, NOT ON THE APPROACH. `cc_g03_swapped`
        // is set by the graph once his entry is off and his phase's gate is
        // held; this ran on `cc_g03_at_bar` until 2026-09-20, which is set
        // on THIS tick, a frame or more before the graph acts on it. A body
        // disposed while its entry is still on is put straight back by the
        // community under the same id, and the id was then ignored for the
        // rest of the session: two Dinos, reported on Nexus.
        if qs.GetFactStr("cc_g03_swapped") > 0
            && qs.GetFactStr("cc_g03_left_dino") <= 0 {
            this.DinoKeeper(game, player as PlayerPuppet, pos);
        }

        // A steady two seconds once the gig is live. Every test above is
        // arithmetic on one position, so this costs nothing worth measuring, and
        // an objective that takes four seconds to notice the player has arrived
        // reads as broken.
        this.Schedule(2.0);
    }

    private func Hold(game: GameInstance, qs: ref<QuestsSystem>,
                      player: ref<GameObject>) -> Void {
        let want: Bool = qs.GetFactStr("cc_g03_left_dino") > 0
            && qs.GetFactStr("cc_g03_johnny_done") <= 0
            && this.m_holdTicks < CCG03Places.HoldCapTicks();
        if want {
            this.m_holdTicks += 1;
        }
        if want && !this.m_holdOn {
            StatusEffectHelper.ApplyStatusEffect(player, CCG03Places.HoldRecord());
            this.m_holdOn = true;
            qs.SetFactStr("cc_g03_dbg_hold", 1);
        } else if !want && (this.m_holdOn || !this.m_holdChecked) {
            StatusEffectHelper.RemoveStatusEffect(player, CCG03Places.HoldRecord());
            this.m_holdOn = false;
            if qs.GetFactStr("cc_g03_dbg_hold") == 1 {
                qs.SetFactStr("cc_g03_dbg_hold", 2);
            }
        }
        this.m_holdChecked = true;
    }

    // THREE WAYS TO FIND HIM, and the first two are the ones that work on a
    // stool.
    //
    // Playtest 2026-09-15, on a save made before the choice: "there are two
    // of them, default + ours", with the game's own Dino still offering his
    // bar chat under our scene. The census below, which is gig 02's
    // ParlorKeeper and found a standing Wakako and a standing Regina, did not
    // find him: a body the AI holds in a sitting workspot is not one the
    // targeting system hands back for a player standing over it. So the
    // first route asks the spawner system directly for the entry the game's
    // own community placed, the way gig 02 finds its merc
    // (`FindInCommunity`): the community's id, the entry `dyno`, and dispose
    // whatever it returns. That does not care where the body is or what it
    // is doing. The second route asks the same system for the entry's FIXED
    // ids (deterministic per entry, gotcha 64) and looks each one up, for a
    // body the first route stops listing. The census stays as the third,
    // widened from live NPCs to any puppet, for a body the spawner no longer
    // owns.
    //
    // WHY THE KEEPER FAILED UNTIL 2026-09-20, in one line: it ran before
    // the graph had switched his entry off, so the community put him back,
    // and it never looked at that id again. See the caller. The routes were
    // never the fault, but the readouts below are what says which of them
    // found him, for the next report.
    private func DinoKeeper(game: GameInstance, player: ref<PlayerPuppet>,
                            pos: Vector4) -> Void {
        if !IsDefined(player) {
            return;
        }
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        if !IsDefined(qs) {
            return;
        }
        let him: Vector4 = CCG03Places.Dino();
        if Vector4.Distance(pos, him) > 40.0 {
            return;
        }
        // THE COMMUNITY'S OWN ID, read off the registry item in
        // always_loaded_1 (`sourceObjectId` of the `#dyno` area node, the
        // same number the registry repeats as its `communityId`). NOT the
        // hash of "#dyno": a compiled community area node has no NodeRef at
        // all (its `QuestPrefabRefHash` is 0), and resolving the short form
        // found nothing (playtest 2026-09-15, the second pair of Dinos).
        // Codeware's `EntityID.FromHash` builds the id from the number
        // directly, so nothing has to resolve.
        let spawner: EntityID = EntityID.FromHash(17285452288567170630ul);
        let objects: array<ref<GameObject>>;
        GetGameObjectsFromSpawnerEntityID(spawner, [n"dyno"], game, objects);
        qs.SetFactStr("cc_g03_dbg_dino_seen", ArraySize(objects));
        let k: Int32 = 0;
        while k < ArraySize(objects) {
            this.RemoveDino(game, qs, objects[k] as ScriptedPuppet, 1);
            k += 1;
        }
        let ids: array<EntityID>;
        GetFixedEntityIdsFromSpawnerEntityID(spawner, [n"dyno"], game, ids);
        k = 0;
        while k < ArraySize(ids) {
            this.RemoveDino(game, qs,
                            GameInstance.FindEntityByID(game, ids[k]) as ScriptedPuppet, 2);
            k += 1;
        }
        // A crosshair query by default; Complete is what makes it a census
        // (the same lesson as the guard count in Gig03_Trace). Any puppet,
        // not TSQ_NPC's live ones only, and secondary parts included, so the
        // net is as wide as the system allows.
        let query: TargetSearchQuery;
        query.searchFilter = TSF_Any(IntEnum<TSFMV>(2));
        query.testedSet = TargetingSet.Complete;
        query.includeSecondaryTargets = true;
        query.ignoreInstigator = true;
        query.maxDistance = 40.0;
        query.filterObjectByDistance = true;
        let parts: array<TS_TargetPartInfo>;
        GameInstance.GetTargetingSystem(game).GetTargetParts(player, query, parts);
        let i: Int32 = 0;
        while i < ArraySize(parts) {
            let obj: ref<GameObject> = TS_TargetPartInfo.GetComponent(parts[i]).GetEntity() as GameObject;
            let npc: ref<ScriptedPuppet> = obj as ScriptedPuppet;
            if IsDefined(npc) && !npc.IsPlayer()
                && Vector4.Distance(npc.GetWorldPosition(), him) < 20.0 {
                this.RemoveDino(game, qs, npc, 3);
            }
            i += 1;
        }
    }

    // ONE BODY OUT, IF IT IS HIS. Only `Character.dyno` is ever touched,
    // whichever route handed it over: ours is `Character.cc_g03_dino`, a
    // record of its own. Up to five times per id, counted, because the
    // community keeps an id across respawns and a body that comes back is
    // the same id seen again.
    //
    // BY NAME, THROUGH CODEWARE, so nothing is declared. `Dispose` is a
    // game command the script bundle never wrote down; a mod that declares
    // it itself collides with any other mod that does (gig 02 did until
    // 2026-09-11, and the compiler warned on the pair). Codeware is a
    // requirement already, and its Reflection calls the command as the game
    // has it.
    private func RemoveDino(game: GameInstance, qs: ref<QuestsSystem>,
                            body: ref<ScriptedPuppet>, route: Int32) -> Void {
        if !IsDefined(body) || body.GetRecordID() != t"Character.dyno" {
            return;
        }
        let id: EntityID = body.GetEntityID();
        let at: Int32 = -1;
        let j: Int32 = 0;
        while j < ArraySize(this.m_disposed) && at < 0 {
            if this.m_disposed[j] == id {
                at = j;
            }
            j += 1;
        }
        if at < 0 {
            ArrayPush(this.m_disposed, id);
            ArrayPush(this.m_disposedTimes, 0);
            at = ArraySize(this.m_disposed) - 1;
        }
        if this.m_disposedTimes[at] >= 5 {
            return;
        }
        this.m_disposedTimes[at] += 1;
        qs_dbg_count(game, "cc_g03_dbg_dino_disposed");
        qs.SetFactStr("cc_g03_dbg_dino_route", route);
        Reflection.Call(body, n"Dispose");
    }

    // PAID ONCE, LATCHED IN A FACT. A field would be gone on the next load and
    // the player would be paid again every time they reloaded a save made
    // standing at his bar. Gotcha 21's shape.
    //
    // NOT PAID AT ALL on the loyal ending: V destroyed the thing he was
    // paying for. `Dock` is that ending's counterpart.
    private func Pay(game: GameInstance, qs: ref<QuestsSystem>) -> Void {
        if qs.GetFactStr("cc_g03_paid") > 0 || qs.GetFactStr("cc_g03_loyal") > 0 {
            return;
        }
        let ps: ref<PlayerSystem> = GameInstance.GetPlayerSystem(game);
        if !IsDefined(ps) {
            return;
        }
        let player: ref<PlayerPuppet> = ps.GetLocalPlayerMainGameObject() as PlayerPuppet;
        if !IsDefined(player) {
            return;
        }
        qs.SetFactStr("cc_g03_paid", 1);
        // The game's own reward route, which is what a quest reward node calls,
        // so the transfer notice and the Street Cred popup are vanilla's.
        RPGManager.GiveReward(game, CCG03Places.Reward(),
                              Cast<StatsObjectID>(player.GetEntityID()));
    }

    // THE ADVANCE COMES OUT OF V'S WALLET, once, latched in a fact. The
    // game's own money readout shows the change (see below). The
    // amount is capped at what V has, so a broke V loses everything they
    // have and nothing they do not, and the fact records what was taken.
    private func Dock(game: GameInstance, qs: ref<QuestsSystem>,
                      player: ref<PlayerPuppet>) -> Void {
        if !IsDefined(player) {
            return;
        }
        let ts: ref<TransactionSystem> = GameInstance.GetTransactionSystem(game);
        if !IsDefined(ts) {
            return;
        }
        qs.SetFactStr("cc_g03_dock_paid", 1);
        let have: Int32 = ts.GetItemQuantity(player, MarketSystem.Money());
        let take: Int32 = CCG03Places.Advance();
        if have < take {
            take = have;
        }
        if take > 0 {
            ts.RemoveItem(player, MarketSystem.Money(), take);
        }
        qs.SetFactStr("cc_g03_dbg_docked", take);
        // NO BANNER OF OURS. The game's own money readout, the popup the fee
        // arrives on, fires for any change to the wallet that is not flagged
        // silent (CurrencyChangeInventoryCallback in the shipped scripts),
        // and RemoveItem has no silent flag, so "-5,000" and the new total
        // are drawn by the game. A reward record cannot do this: GiveReward
        // skips any currency quantity that is not above zero. The design
        // call, 2026-09-15: no custom text over the game's own.
    }
}

// THE SHARD, DESTROYED. The item leaves the backpack and a red banner says
// so; there is nothing in V's hands to animate. Latched in a fact so a
// reload does not try to remove what is already gone.
public class CCG03DestroyCall extends DelayCallback {
    public let game: GameInstance;

    public func Call() -> Void {
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.game);
        let psys: ref<PlayerSystem> = GameInstance.GetPlayerSystem(this.game);
        if !IsDefined(qs) || !IsDefined(psys) {
            return;
        }
        if qs.GetFactStr("cc_g03_shard_destroyed") > 0 {
            return;
        }
        let player: ref<PlayerPuppet> = psys.GetLocalPlayerMainGameObject() as PlayerPuppet;
        if !IsDefined(player) {
            return;
        }
        qs.SetFactStr("cc_g03_shard_destroyed", 1);
        let ts: ref<TransactionSystem> = GameInstance.GetTransactionSystem(this.game);
        if IsDefined(ts) && ts.RemoveItemByTDBID(player, t"Items.cc_g03_shard", 1) {
            qs.SetFactStr("cc_g03_dbg_destroyed", 1);
        } else {
            // The shard was not in the backpack: read in place and left on the
            // cabinet, most likely. The banner still says what V decided.
            qs.SetFactStr("cc_g03_dbg_destroyed", 2);
        }
        CCSharedHud.NotifyTyped(this.game,
            GetLocalizedTextByKey(n"cc-g03-destroyed-banner"),
            SimpleMessageType.Negative, 5.0);
    }
}

public class CCG03PlacesTick extends DelayCallback {
    public let system: wref<AcceptableLossPlaces>;

    public func Call() -> Void {
        if IsDefined(this.system) {
            this.system.Tick();
        }
    }
}

// One more on a readback fact, so a playtest can tell "the body was found
// and disposed" from "nothing was found".
public static func qs_dbg_count(game: GameInstance, fact: String) -> Void {
    let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
    if IsDefined(qs) {
        qs.SetFactStr(fact, qs.GetFactStr(fact) + 1);
    }
}
