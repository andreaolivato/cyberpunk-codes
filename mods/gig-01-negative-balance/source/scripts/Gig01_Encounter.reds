// Gig 01, Negative Balance: the encounter layer.
//
// Spawns Arasaka security at both locations, drives the estate malware upload
// and detects Hoshino's death. Positions were captured in-game; character
// records are real Arasaka/Arroyo/North Oak records taken from the game
// database.
//
// The office ledger is NOT here: it renders inside the real narrative
// computer's UI and sets cc_g01_terminal_done when V opens it, see
// Gig01_OfficeComputer.reds. That fact is set by the engine's AddFact, which
// increments, so it is compared with `> 0` below and never `== 1`.
//
// Quest logic (objectives, pins, journal) lives in the quest phase; this file
// only sets the facts it waits on:
//   cc_g01_office_reached, cc_g01_terminal_done, cc_g01_estate_reached,
//   cc_g01_hoshino_dead, cc_g01_malware_done, cc_g01_at_coyote

module CyberpunkCodes.Gig01

// Spawning, proximity, device state, voicesets and HUD banners live in
// shared\scripts. The build vendors them into this mod under a per-gig
// module name; see CCShared_World.reds for why that rename is mandatory.
import CyberpunkCodes.Shared.*

public abstract class CCGig01Places {
    // --- Arasaka Industrial Park (Arroyo) ---
    public static func CompoundEntry() -> Vector4 { return new Vector4(-189.371, -1464.500, 7.596, 1.0); }
    public static func InnerEntry() -> Vector4 { return new Vector4(-219.737, -1424.075, 14.604, 1.0); }
    public static func OfficeEntry() -> Vector4 { return new Vector4(-241.498, -1449.012, 14.600, 1.0); }
    public static func OfficeTerminal() -> Vector4 { return new Vector4(-251.915, -1456.364, 14.600, 1.0); }

    // Is V standing inside the Arasaka Industrial Park, by any route at all?
    //
    // Same job as InsideEstate below, and it exists for the same reason: the
    // guards used to be triggered by one 60 m sphere on the gate, and the site
    // does not fit inside it. The office terminal is 63.5 m from that anchor
    // and the terminal room door 67.7 m, so a player who reached the computer
    // without crossing the bubble found an empty building (Nexus, 1.1.3).
    //
    // FOUR CORNERS, WALKED AND CAPTURED in playtest 2026-08-17 (`compound_1`
    // to `compound_4` in captured_positions.txt). Convex, ~38,500 m2, and it
    // contains every post and every door this gig uses here, the terminal,
    // the shard and the map pin.
    //
    // The Z band is the same asymmetric rule as Near(): the captures span
    // 7.65 to 22.6, the office floor is at 14.6 and the ground floor at 8.6,
    // so the floor is set just below the lowest capture rather than at zero.
    // A band reaching further down would take in whatever passes underneath.
    public static func InsideCompound(pos: Vector4) -> Bool {
        if pos.Z < 2.0 || pos.Z > 45.0 {
            return false;
        }
        // Cheap rejection first: this runs on a tick that ticks everywhere in
        // the city, and the crossing test below is four iterations.
        if pos.X < -389.3 || pos.X > -113.0 || pos.Y < -1567.9 || pos.Y > -1299.6 {
            return false;
        }
        let xs: array<Float> = [-113.001, -282.899, -389.293, -239.160];
        let ys: array<Float> = [-1398.983, -1299.636, -1463.909, -1567.924];
        let n: Int32 = ArraySize(xs);
        let inside: Bool = false;
        let i: Int32 = 0;
        let j: Int32 = n - 1;
        while i < n {
            // Half-open rule, written as two Bools and an explicit xor, so a
            // point level with a vertex is counted once. Same shape as
            // InsideEstate; see it for why `!=` on Bools is not used.
            let above_i: Bool = ys[i] > pos.Y;
            let above_j: Bool = ys[j] > pos.Y;
            if (above_i && !above_j) || (!above_i && above_j) {
                let t: Float = (pos.Y - ys[i]) / (ys[j] - ys[i]);
                if pos.X < xs[i] + t * (xs[j] - xs[i]) {
                    inside = !inside;
                }
            }
            j = i;
            i += 1;
        }
        return inside;
    }

    // --- Arasaka estate, North Oak ---
    public static func EstateGate() -> Vector4 { return new Vector4(384.181, 1164.724, 220.643, 1.0); }
    // Two extra posts, captured in-game in playtest, 2026-08-12 ("spawn more guards
    // here" / "even more guards here"). The approach is ~30 m inside the gate,
    // the grounds spot sits between the side entrance and Hoshino - so the walk
    // from gate to target is now covered end to end instead of having a quiet
    // stretch in the middle.
    // ================================================== THE ROUTE IN, IN SIX
    // it was walked on 2026-08-15 and captured a point at every turn
    // (`entry-1` .. `entry-6` in captured_positions.txt). These are his feet;
    // the PINS are the same points raised 1.7 m, which is done once in
    // gen_journal.PIN_POS and deliberately not repeated here - a proximity test
    // wants the ground, a marker wants head height.
    //
    // THE CHAIN OF PINS *IS* THE PATH, because the game will not draw one.
    // Vanilla does have a forced-GPS-route mechanism -
    // `gameJournalQuestGuidanceMarker`, a child of the map pin, 44 of them
    // across 18 pins in the shipped journal - and it is unusable here: the
    // record is a bare `nodeRef` with NO offset, so a waypoint lands exactly on
    // a node the game already ships, and the nearest always-loaded node to five
    // of these six points is 52-75 m away. Shipping our own nodes is the route
    // that provably does not resolve. Full working in docs/map-pins-playbook.md.
    //
    // So: GPS off on all six, one marker visible at a time, each appearing as
    // the previous is reached. Six markers on screen together is the confusion
    // being fixed, not the fix (playtest: *"showing all the pins together is
    // madness"*).
    public static func WayInPoint(leg: Int32) -> Vector4 {
        switch leg {
            case 1: return new Vector4(369.781, 1178.338, 219.794, 1.0);
            case 2: return new Vector4(327.383, 1167.466, 219.520, 1.0);
            case 3: return new Vector4(306.727, 1154.487, 219.287, 1.0);
            case 4: return new Vector4(290.119, 1122.134, 218.901, 1.0);
            case 5: return new Vector4(276.470, 1089.549, 216.985, 1.0);
            default: return new Vector4(288.168, 1082.351, 225.525, 1.0);
        }
    }

    public static func WayInLegs() -> Int32 { return 6; }

    // The same point at head height. the capture was taken standing, so WayInPoint is
    // his feet; a marker at foot height on a slope sinks into the ground.
    public static func WayInMarker(leg: Int32) -> Vector4 {
        let p: Vector4 = CCGig01Places.WayInPoint(leg);
        return new Vector4(p.X, p.Y, p.Z + 1.7, 1.0);
    }

    // Has V reached waypoint `leg`?
    //
    // The radii are about PACE, not geometry: the first three points are on the
    // road and can be driven, the last three are a walk and a climb. The gaps
    // between consecutive points are 44 / 24 / 36 / 35 / 14 m, and every radius
    // is smaller than the gap ahead of it, so a normal walk cannot satisfy two
    // at once.
    //
    // WAYPOINT 6 IS THE ONE THAT NEEDS THE TIGHT ALTITUDE BAND. It is only 14 m
    // from waypoint 5 horizontally but 8.5 m ABOVE it - that is the climb. With
    // a loose band, standing at the bottom would read as being at the top and
    // the last marker would never be shown at all.
    public static func AtWayInPoint(pos: Vector4, leg: Int32) -> Bool {
        if leg >= 6 {
            return CCSharedWorld.Near(pos, CCGig01Places.WayInPoint(6), 12.0, 4.0, 6.0);
        }
        let radius: Float = 14.0;
        if leg <= 3 {
            radius = 18.0;
        }
        return CCSharedWorld.Near(pos, CCGig01Places.WayInPoint(leg), radius, 8.0, 8.0);
    }

    // The way INTO the house - waypoint 6, and the same point the last pin
    // marks. Getting to the estate and finding a door are two different
    // problems, and the gig used to jump straight from one to "find Hoshino",
    // who is inside, with no hint how to get there.
    //
    // MOVED 2026-08-15, from (273.981, 1084.395, 215.158). The old value was the
    // FOOT of the climb - where you start going up, not where you get in - so
    // the pin marked the bottom of a rock face and the objective completed
    // there. The foot of the climb is waypoint 5 now, which is what it was.
    public static func EstateWayIn() -> Vector4 { return CCGig01Places.WayInPoint(6); }
    public static func Hoshino() -> Vector4 { return new Vector4(300.102, 1054.556, 229.928, 1.0); }
    public static func EstateTerminal() -> Vector4 { return new Vector4(284.852, 1023.697, 224.928, 1.0); }

    // --- Epilogue ---
    public static func Coyote() -> Vector4 { return new Vector4(-1259.598, -989.166, 12.037, 1.0); }

    // Where the stand-in Mama Welles goes when the base-game one is absent.
    // This is the REAL Mama Welles' own spot, captured off the live NPC with the
    // dev menu's [CAPTURE THE NPC I'M LOOKING AT] (record confirmed as
    // Character.Mama_Welles in the capture log), so the stand-in lands exactly
    // on her mark. Note it is ~10 m from Coyote(), the bar marker is not where
    // she stands, which is why the earlier guessed offset was well wide.
    public static func MamaWelles() -> Vector4 { return new Vector4(-1262.178, -998.805, 12.057, 1.0); }
    public static func MamaWellesYaw() -> Float { return -80.3; }

    // The bar stools, captured in playtest, 2026-08-12. Coyote() is the base game's
    // bar MARKER and it sits at the pub's exit, ~10.4 m from here - fine for the
    // "you have arrived at El Coyote" check and the epilogue pin, wrong for
    // "walk to the bar and get a drink".
    //
    // Note it is only ~4 m from where Mama stands, so the trigger radius on this
    // one has to be tight (2 m) or the closing beat fires while V is still
    // standing where he talked to her, and the objective he was just given
    // completes itself without him moving.
    public static func BarStools() -> Vector4 { return new Vector4(-1258.193, -999.521, 12.037, 1.0); }

    // Horizontal proximity with an altitude band.
    //
    // A plain Vector4.Distance is 3D, but a large radius still swallows anything
    // directly underneath: the road to the North Oak estate runs through a
    // tunnel UNDER the house, so simply driving past was reading as "arrived"
    // (and spawning the estate guards). The band is deliberately asymmetric - 
    // being far BELOW an anchor means you are in the tunnel or on the road,
    // while being above it just means an upper floor or the terrace.
    // ============================================================== THE ESTATE
    // Is V standing inside the North Oak compound, by any route at all?
    //
    // THIS IS THE 1.0.0 BUG, not the pins. A player wrote in that he got over
    // the wall by double-jumping - which is a perfectly good way in and one that
    // predates this gig - and the way-in objective never completed, so he had to
    // walk back OUT to the marker and come in again. The objective was testing
    // "did you touch our pin", and what it means is "are you in".
    //
    // THE OUTLINE IS TRACED, NOT FITTED. the capture traced the inside of the wall on
    // 2026-08-15 and captured 20 points tight against it (`inside-*` in
    // captured_positions.txt, `2-correct` in place of `2`, both `5`s kept). It
    // is used exactly as walked: no convex hull and no radius. A hull over these
    // same points measures 9% larger, and all of that bulge is across the
    // concave west stretch - i.e. it would complete the objective for somebody
    // still standing outside, which is the one failure this must not have.
    //
    // The Z band is the other half. The captures span 219.7-225.9 and the
    // interior goes a little higher (the side entrance is at 229.9), so the band
    // is generous upwards and tight downwards - the same asymmetry, and for the
    // same reason, as Near() above: THE ROAD TUNNELS UNDER THIS HOUSE, and a
    // floor low enough to include it would complete the objective for a player
    // driving past underneath.
    public static func InsideEstate(pos: Vector4) -> Bool {
        // THE CEILING WAS 235.9 AND IT COST THE WHOLE ESTATE LEG. Two separate
        // player reports, 2026-08-25: they walked in, reached Hoshino, and the
        // journal still read "Get to the Arasaka estate in North Oak".
        //
        // Everything at the estate hangs off this one test. `cc_g01_estate_reached`
        // gates the guards, the Hoshino lookup, the greeting and every objective
        // after it, so a player standing somewhere this returns false for gets no
        // gig at all, silently, with no way to recover but to walk back out.
        //
        // 235.9 came from the captures that existed when it was written, which
        // topped out at 229.9, and it is only 2 m above the roof post captured
        // later. The estate's upper terraces are above it.
        //
        // THE FLOOR IS THE HALF THAT NEEDED TO BE TIGHT and it has not moved:
        // the road tunnels UNDER this hill, so a floor that reached down to it
        // would hand the estate to somebody driving past underneath. There is
        // nothing above the estate but sky, so the ceiling costs nothing and is
        // now well clear of anything anybody can stand on.
        if pos.Z < 213.7 || pos.Z > 280.0 {
            return false;
        }
        // Cheap rejection first: the tick runs everywhere in the city and the
        // ray cast below is 20 iterations.
        if pos.X < 245.1 || pos.X > 399.2 || pos.Y < 977.1 || pos.Y > 1166.9 {
            return false;
        }
        let xs: array<Float> = [
            339.379, 368.302, 391.452, 399.100, 387.793, 392.889, 363.870,
            346.593, 329.999, 307.952, 315.188, 299.594, 245.171, 269.290,
            291.898, 295.547, 296.802, 285.525, 322.571, 340.626];
        let ys: array<Float> = [
            1158.764, 1166.825, 1153.485, 1126.636, 1103.308, 1086.459, 1036.437,
            1038.424, 1007.784, 1020.564, 1009.689, 977.203, 1007.622, 1046.606,
            1082.425, 1080.882, 1083.118, 1092.534, 1155.241, 1160.340];

        // Standard crossing test: count how many edges a ray cast in -X from
        // the point crosses. Odd = inside.
        let n: Int32 = ArraySize(xs);
        let inside: Bool = false;
        let i: Int32 = 0;
        let j: Int32 = n - 1;
        while i < n {
            // Written as two Bools and an explicit xor rather than `!=` on
            // Bools: this is the half-open rule that makes a vertex belong to
            // exactly one of its two edges, so a point level with a vertex is
            // not counted twice.
            let above_i: Bool = ys[i] > pos.Y;
            let above_j: Bool = ys[j] > pos.Y;
            if (above_i && !above_j) || (!above_i && above_j) {
                // Safe: the test above guarantees ys[j] != ys[i].
                let t: Float = (pos.Y - ys[i]) / (ys[j] - ys[i]);
                if pos.X < xs[i] + t * (xs[j] - xs[i]) {
                    inside = !inside;
                }
            }
            j = i;
            i += 1;
        }
        return inside;
    }
}

public class NegativeBalanceEncounter extends ScriptableSystem {

    // Ticks until the next audit of a site's detail. Starts at 0, so the first
    // tick inside the region acts immediately.
    private let m_officeAudit: Int32;
    private let m_estateAudit: Int32;
    // True on a pass that moved the North Oak objective chain on by one step.
    // Not persisted, and it must not be: it is only ever read later in the SAME
    // pass that wrote it, and a remembered value would skip a step after a load.
    private let m_estateStepTaken: Bool;
    // THE ESTATE DETAIL IS FOUND, NOT SPAWNED, as of 2026-08-25. Thirty guards
    // stand at thirty authored posts placed by `cc_g01_estate`, the second
    // community this mod ships (tools/gig01/gen_estate_guards.py). What is left
    // here is finding them and making them enemies of V, which is the one thing
    // a community does NOT bring with it: a community NPC arrives with no
    // quarrel with the player, and an NPC with no quarrel never starts looking
    // (gotcha 74).
    //
    // How many have been found and turned so far, and whether the whole detail
    // is accounted for. The count is what the dev panel reads; the Bool is what
    // stops the tick asking again.
    // AND NEITHER OF THESE SURVIVES A RELOAD, which is correct rather than a
    // limitation. A field on this system does not persist (see the estate audit
    // in the tick, which relies on the same thing), so after a load the detail
    // is looked up and turned hostile again from scratch.
    //
    // That is exactly what is needed. The community re-places its bodies on
    // load and they come back with their records' own attitude, which is not
    // hostile to anybody: measured in August, twenty-two estate guards within
    // 200 m of the gate and zero of them enemies of V. Persisting "already
    // done" would remember a job whose result had been thrown away, and the
    // symptom would be guards who ignore the player only on a reloaded save.
    private let m_compoundFound: Int32;
    private let m_compoundAnnounced: Bool;
    private let m_estateFound: Int32;
    // The banner has been shown this session. NOT "the work is finished": see
    // the note where it is set.
    private let m_estateAnnounced: Bool;
    private let m_hoshinoId: EntityID;
    private let m_hoshinoSpawned: Bool;
    private let m_hoshinoSeenAlive: Bool;   // only then can we call him dead
    private let m_hoshinoGreeted: Bool;
    // Set the first time he is hit, and NOT persisted. See the tick.
    private let m_hoshinoProvoked: Bool;
    // Whether he is currently unkillable, and whether that has been given
    // back. Neither is persisted; both are re-derived from facts on load.
    private let m_hoshinoShielded: Bool;
    // Ticks since V reached him with no scene having finished. The dead man's
    // handle on the shield; see the tick.
    private let m_hoshinoMetTicks: Int32;
    private let m_downloadBusy: Bool;
    private let m_uploadBusy: Bool;
    private let m_sendBusy: Bool;
    private let m_talkBusy: Bool;
    private let m_barWaited: Int32;
    private let m_mamaMissingTicks: Int32;
    // TRUE while WE are holding `mama_is_talking` up to keep her small talk out
    // of the epilogue. It is the receipt that lets us clear a base-game fact we
    // do not own without clobbering somebody else's use of it. Not persistent -
    // which is the safe direction: after a reload we simply set it again on
    // the next tick, and never clear a 1 we did not write.
    private let m_mamaHeld: Bool;
    // TRUE while her VOICESET is muted - the "Look who it is" she says on sight,
    // which is a bark and not part of the dialogue scene, so `mama_is_talking`
    // does not touch it. Same receipt discipline as m_mamaHeld.
    private let m_mamaMuted: Bool;
    // Which waypoint the moving marker is currently on. Not the state itself -
    // cc_g01_wayin_leg is that, and it persists. This is only "where have I put
    // the marker since the game loaded", so a fresh load re-places it once.
    private let m_wayinShown: Int32;
    private let m_wayinMappin: NewMappinID;
    private let m_wayinMappinUp: Bool;
    private let m_epilogueBusy: Bool;
    private let m_ticks: Int32;
    // The shard beat (comic pp. 23-24). m_shardOpened is "the reader was raised
    // successfully", which is not the same as "the entry exists" - see the tick.
    private let m_shardOpened: Bool;
    private let m_shardTicks: Int32;
    private let m_shardWait: Int32;
    // How long the player has been left alone with the [F] prompt before the
    // gig gives up waiting and raises the reader itself. See the shard beat.
    private let m_shardGrace: Int32;
    // Ticks since the shard's journal entry went VISITED. Two of them cannot
    // pass while the reader is open, so this is "the popup has been closed"
    // for a read that happened anywhere, including out of the inventory.
    private let m_shardVisited: Int32;
    // Placement latch: 1 = no body found yet, 2 = placed. NOT a diagnostic -
    // this is what stops him being re-placed every tick, and what re-arms the
    // next beat. The cc_g01_dbg_lip_* facts that used to shadow it are gone.

    // THE FIRST TICK IS 0.5 s, NOT 6: A BUG FIX (2026-08-15).
    //
    // it was worked out from the test method: the tester was loading a save
    // parked right outside El Coyote. **For the first six seconds after ANY
    // load this system did nothing at all** - so he walked in, Mama greeted him
    // and her dialogue hub opened before our first tick had ever run. Nothing
    // downstream can win that race: the `mama_is_talking` hold, the voiceset
    // mute and the 200 m window are all evaluated in Tick, and Tick had not
    // happened yet.
    //
    // It explains every observation exactly, including the ones that looked
    // like they contradicted each other: approach slowly and it works (the tick
    // lands first), approach briskly and it does not, and "one time it was
    // perfect" is the run where he took more than six seconds to get inside.
    //
    // Six was never load-bearing - there is no comment on it and nothing
    // depends on the delay. The tick is null-safe by construction (it does
    // nothing at all unless the player resolves, and reschedules regardless),
    // which is why it has ticked harmlessly at the main menu since it was
    // written. So the cost of starting early is one no-op callback.
    //
    // A REAL PLAYER WALKS OR DRIVES TO THE BAR and has ticked hundreds of times
    // before arriving, so this was mostly invisible outside testing - but a
    // player who loads a save near El Coyote hits it exactly as the playtest did.
    private func OnAttach() -> Void {
        this.Schedule(0.5);
    }

    // TraceTagged() was here - the tag-population probe behind
    // cc_g01_dbg_lip_johnny / _hoshino. Gone with the rest of the lipsync
    // instrumentation, 2026-08-14.
    //
    // The lookup rule it taught is worth more than the probe was, and is
    // docs/gotchas.md #18: native game-system methods are declared in
    // **Codeware's** `Scripts\Codeware.Global.reds` (DynamicEntitySystem at
    // line 43422), not in the game's script cache - which does not contain the
    // string "DynamicEntitySystem" at all. `GetEntityIDs`, the obvious name and
    // the one this was first written with, does not exist; the real ones are
    // GetTagged / GetTaggedID / GetTaggedIDs / IsPopulated.
    public func Schedule(delay: Float) -> Void {
        let cb: ref<CCGig01EncounterTick> = new CCGig01EncounterTick();
        cb.system = this;
        GameInstance.GetDelaySystem(this.GetGameInstance()).DelayCallback(cb, delay, false);
    }

    // Ticks between audits of a site's unpopulated anchors. Four ticks is 6 s,
    // which is roughly how long it takes to walk far enough for another sector
    // to have streamed in.
    private func AuditTicks() -> Int32 { return 4; }

    // Called from the tick on every pass the player is inside a site's region.
    //
    // Cheap when there is nothing to do: a countdown, then one resolve and one
    // lookup, both of which return in the same tick. It is idempotent, so it
    // runs while V is on site rather than latching when it believes the job is
    // finished. A post that has not streamed in yet is simply asked for again.
    private func AuditSite(estate: Bool) -> Void {
        if estate {
            this.m_estateAudit -= 1;
            if this.m_estateAudit > 0 {
                return;
            }
            this.m_estateAudit = this.AuditTicks();
            // NO BUSY FLAG AND NO ATTEMPT BUDGET on this branch, and both
            // absences are deliberate. They belong to the spawn chain: it takes
            // seconds to run and it asks the navmesh for ground that may never
            // be streamed in, so a second chain on top of the first is a real
            // hazard and an anchor that never answers is a real dead end.
            //
            // Finding a community's bodies is neither. It is one resolve and
            // one query, it returns in the same tick, and a post that has not
            // streamed in yet WILL stream in as the player walks towards it.
            // Asking again every six seconds until the detail is complete is
            // the correct behaviour rather than a cost to be bounded.
            this.SpawnEstateSecurity();
            return;
        }
        this.m_officeAudit -= 1;
        if this.m_officeAudit > 0 {
            return;
        }
        this.m_officeAudit = this.AuditTicks();
        // Same as the estate branch above: no busy flag and no attempt budget,
        // because both belong to a spawn chain and this is a lookup.
        this.SpawnOfficeSecurity();
    }

    // FOUND RATHER THAN SPAWNED, 2026-08-25, exactly as the estate is.
    //
    // Five anchors and twenty guards used to be placed by a navmesh query each.
    // Three of those five anchors sit within fifteen metres of each other, so a
    // third of the site's guards were asked for in one corner of one building
    // while the yard, the second gate and every interior floor had nobody at
    // all.
    //
    // Thirty posts were walked and captured instead, sixteen of them off the
    // ground floor. The name is left alone because the tick, the proximity
    // tests and the dev menu all use it, and renaming it would be a sweep
    // across a working file for no gain.
    private func SpawnOfficeSecurity() -> Void {
        this.FindCompoundGuards();
    }

    private func SpawnEstateSecurity() -> Void {
        // HOSHINO FIRST, and separately. He is the objective, he is one entity,
        // and a guard arriving a second later costs nothing while a Hoshino
        // arriving late is the beat. Guarded by his own latch so a repeated pass
        // cannot put a second one on the terrace.
        //
        // Our own record (suit, armed, named).
        // YAW 140.8 = the captured 50.8 turned 90 degrees ANTICLOCKWISE.
        // playtest, 2026-08-14, from a screenshot: he delivered "Mmm? You lost,
        // merc?" with his back to V, facing out over the terrace. Yaw is
        // counter-clockwise seen from above, so anticlockwise is +90.
        // Same spot, and only the facing changed.
        // NOT ANY MORE. A COMMUNITY PLACES HIM.
        //
        // `gen_community.py` ships a community that stands him at this exact
        // position, and `gig01.questphase` switches its entry on when the
        // estate objective goes up. That replaced the two-bodies arrangement:
        // this spawn plus an invisible scene actor a kilometre away carrying
        // the voice, which is what the "half-way in a pillar" report was.
        //
        // Everything below still needs his EntityID for the attitude flip, the
        // death detection and the greeting, so the id is now FOUND rather than
        // returned by a spawn. FindHoshino() does that, and it is deliberately
        // retried on the tick rather than done once: the community places him
        // asynchronously and a single look on the frame the objective changed
        // would find nothing.
        //
        // The Neutral call moved with him: an administrator does not open fire
        // during his own conversation (playtest, 2026-08-12). See below.
        this.FindHoshino();
        // AND THE DETAIL, WHICH IS FOUND RATHER THAN SPAWNED, 2026-08-25.
        //
        // Six anchors and twenty-five guards used to be dropped onto whatever
        // walkable ground the navmesh offered within a couple of metres. The
        // huddle came from that query: nobody had ever said where a guard
        // should stand, so it answered "somewhere near here" and kept giving
        // nearly the same answer. Twenty-nine posts were walked and captured in
        // game instead, and a community stands a man on each of them facing the
        // way he was captured facing.
        //
        // What replaces the whole spawn chain is one resolve and one lookup,
        // below. `backlog.md` 31 is what the two sites used to be.
        this.FindEstateGuards();
    }

    // THE ESTATE DETAIL'S COMMUNITY, and the entries in it.
    //
    // These names must match tools/gig01/gen_estate_guards.py exactly. Redscript
    // cannot import Python, so the list is restated here, and because a restated
    // list is a list that drifts, THE GENERATOR READS THIS FILE AND REFUSES TO
    // WRITE IF THE TWO DISAGREE. That is the same guard the bench put on its
    // slot table after a scan measured against different coordinates than the
    // bodies had been placed at.
    //
    // Gotcha 73 is why it earns the trouble: a quest node or a lookup naming a
    // community entry that does not exist fails silently, and on 2026-08-25 a
    // renamed entry of exactly this kind loaded without a warning and then
    // crashed the game.
    public static func EstateCommunityRef() -> String {
        return "$/mod/cc_g01_estate/#cc_g01_estate_com";
    }

    // THE INDUSTRIAL PARK'S COMMUNITY, and the thirty posts in it.
    //
    // Same arrangement as the estate's above and cross-checked the same way:
    // `gen_compound_guards.py` parses this list and refuses to write when the
    // two disagree (gotcha 76).
    //
    // ALL THIRTY STAND STILL. Four of them walked a beat for one build on
    // 2026-08-25 and the beats did not work; see the note in
    // `gen_compound_guards.py` for what was tried and why it is not chased.
    //
    // The site had FIVE anchors and twenty men, and three of those anchors sat
    // within fifteen metres of each other, so a third of the guards were asked
    // for in one corner of one building and the yard, the second gate and every
    // interior floor had nobody. Sixteen of these thirty are off the ground
    // floor, which a navmesh query around a ground anchor could not produce at
    // all. Forty-six posts were captured and thinned to thirty for stealth;
    // `gen_compound_guards.py` has which went and why.
    public static func CompoundCommunityRef() -> String {
        return "$/mod/cc_g01_compound/#cc_g01_compound_com";
    }

    public static func CompoundEntries() -> array<CName> {
        return [
            n"gate03",
            n"gate2_01", n"gate2_02", n"gate2_03",
            n"inner02", n"inner03", n"inner04", n"inner05",
            n"inner06", n"inner07", n"inner08", n"inner09", n"inner10",
            n"inner11", n"inner12",
            n"deck02", n"deck03", n"deck04",
            n"inside10", n"inside11", n"inside12", n"inside14",
            n"inside15", n"inside16", n"inside17", n"inside18",
            n"office01", n"office02", n"office03", n"office04"
        ];
    }

    public static func EstateEntries() -> array<CName> {
        return [
            n"gate01", n"gate02", n"gate03",
            n"inner01", n"inner02", n"inner03", n"inner04", n"inner05",
            n"inner06", n"inner07", n"inner08", n"inner09", n"inner10",
            n"inner11", n"inner12", n"inner13", n"inner14", n"inner15",
            n"inner16", n"inner17",
            n"floor02", n"floor03", n"floor04", n"floor05",
            n"roof02",
            n"office01", n"office02", n"office03", n"office04"
        ];
    }

    // FIND THE BODIES THE COMMUNITY PLACED, AND MAKE THEM ENEMIES OF V.
    //
    // The attitude is the whole job. Measured 2026-08-25, three guards at one
    // post one at a time: two vanilla records at their default attitude stood
    // there and did nothing, and the same record with a hostile attitude applied
    // detected V on the ordinary ramp, slowly at distance and faster on
    // approach, and went to combat. `senseComponent.ShouldStartDetectingPlayer`
    // treats a hostile attitude as "start filling the meter", so with no
    // attitude there is no meter and no reaction (gotcha 74).
    //
    // The same reading was taken from the other end in August with the OLD
    // spawn: twenty-two estate guards within 200 m of the gate, and zero of them
    // hostile to V. These records do not initiate on their own.
    //
    // `CCSharedAttitude.Hostile` is pairwise, an enemy of THIS player and of
    // nobody else, and it retries for sixty seconds while a body streams in. It
    // asks `FindEntityByID` rather than the dynamic entity system, which it has
    // to: a community body is invisible to every DynamicEntitySystem lookup, and
    // that was silently costing every retry until 2026-08-25 (gotcha 71).
    //
    // Called from the audit on the tick, so a post that has not streamed in yet
    // is asked for again on the next pass. Idempotent: a guard who is already an
    // enemy of V is made one again, which costs a pairwise set.
    // BOTH DETAILS ARE MADE HOSTILE, and the alternative was tried and failed.
    //
    // The two ways an NPC can come at the player are alternatives, not a pair:
    //
    //   hostile attitude  -> detection ramp -> combat.  An ENEMY being spotted.
    //   security area     -> trespass warning.  A STRANGER being told to leave.
    //
    // The gig wanted the second at the industrial park: a call-out, somebody
    // walking over, and a fight only if V stays. THE SECURITY AREA WAS BUILT
    // AND IT DOES NOT DRIVE A MOD'S COMMUNITY. Every part of it was measured
    // correct in game on 2026-08-25: found, ON, attached, not disabled, typed
    // RESTRICTED exactly as vanilla's is, linked to the community, fed by
    // eighteen cameras, with its security system present, and reporting that
    // the player was INSIDE it, and the guards did nothing at all.
    //
    // Left neutral without it they are not inert, they are just NEUTRAL: they
    // notice somebody standing on top of them and eventually react, which is
    // what any neutral NPC in the game does. Playtest: *"I need to be like
    // touching it. If I stand like 1m out nothing happens"*.
    //
    // So hostile it is, at both sites, which is the behaviour that was working
    // before any of this and is not un-vanilla here: Gimme Danger's own guards
    // at this compound are hostile and attack on sight. `backlog.md` 31 has the
    // whole dead end and what was eliminated on the way.
    private func FindEstateGuards() -> Void {
        this.FindDetail(NegativeBalanceEncounter.EstateCommunityRef(),
                        NegativeBalanceEncounter.EstateEntries(), true);
    }

    // THE SAME JOB AT THE INDUSTRIAL PARK, and it is the same function.
    //
    // The two sites differ in which community they name and in which facts they
    // report through, and in nothing else. Writing it twice would be two copies
    // of the senses fix, two copies of the readback and two places for the next
    // finding to be applied to only one of them.
    private func FindCompoundGuards() -> Void {
        this.FindDetail(NegativeBalanceEncounter.CompoundCommunityRef(),
                        NegativeBalanceEncounter.CompoundEntries(), false);
    }

    // THE CAMERAS ARE NOT TOUCHED AT ALL, and that is a decision, 2026-08-25.
    //
    // This file briefly walked the site's eighteen cameras back up to ON while
    // the gig was here, and raised a banner when one of them saw V. Both are
    // gone at playtest's request, and the reasons are different for each.
    //
    // THE ALARM was dishonest. It said "a camera has eyes on you" and nothing
    // followed, because alerting our own community is exactly the thing that
    // does not work. A banner announcing a consequence that never arrives is
    // worse than no banner.
    //
    // THE RESTORE went with it because, once the alarm was gone, switching
    // another quest's devices on bought this gig nothing. It was only ever
    // insurance for a player who shot them out, and paying for that with a
    // permanent change to Gimme Danger's cameras is the wrong trade when our
    // own guards no longer depend on them.
    //
    // What was learned doing it is not lost: `backlog.md` 31 has the whole
    // camera investigation, and gotchas 82 and 83 have the two findings worth
    // keeping: that any base-game device can be addressed offline from its
    // NodeRef, and the full menu of what a camera will accept.

    private func FindDetail(reference: String, names: array<CName>,
                            estate: Bool) -> Void {
        let game: GameInstance = this.GetGameInstance();
        let nref: NodeRef = CreateNodeRef(reference);
        let root: GlobalNodeRef;
        let g: GlobalNodeRef = ResolveNodeRef(nref, root);
        if !GlobalNodeRef.IsDefined(g) {
            // The name did not resolve, so its sector is not loading and nothing
            // below can work. Worth telling apart from "resolved but empty": one
            // is a broken build, the other is a quest phase that has not
            // switched the community on yet.
            this.NoteGuards(game, estate, 1, 0, ArraySize(names));
            return;
        }
        let objects: array<ref<GameObject>>;
        GetGameObjectsFromSpawnerEntityID(Cast<EntityID>(g), names, game,
                                          objects);
        let found: Int32 = 0;
        let i: Int32 = 0;
        while i < ArraySize(objects) {
            let puppet: ref<ScriptedPuppet> = objects[i] as ScriptedPuppet;
            if IsDefined(puppet) && ScriptedPuppet.IsAlive(puppet) {
                CCSharedAttitude.Hostile(game, puppet.GetEntityID());
                // AND THE EYES ON, WHICH THE ATTITUDE DOES NOT DO.
                //
                // Playtest 2026-08-25: all thirty stood at their posts and none
                // of them ever noticed V. They fought when shot, and they joined
                // in when one of the estate's own NPCs raised the alarm, so they
                // were not inert. They simply never STARTED looking.
                //
                // That is the shape of a missing sense component rather than a
                // missing attitude. `ShouldStartDetectingPlayer` treats a hostile
                // attitude as "start filling the meter", and a meter on a
                // component that is switched off never fills however hostile the
                // NPC is. Hoshino's own TurnOnPlayer has done both since August
                // for exactly this reason; the guards were only given the first.
                //
                // Cheap, idempotent, and correct whether or not it is the cause.
                let senses: ref<SenseComponent> = puppet.GetSensesComponent();
                if IsDefined(senses) {
                    senses.Toggle(true);
                }
                found += 1;
            }
            i += 1;
        }
        // AND NOW READ BACK WHAT ACTUALLY TOOK, which is the whole point.
        //
        // `posts turned` counted the guards we ASKED about. It said 30 while not
        // one of them was reacting, because asking and landing are different
        // things and nothing here could tell them apart. Every wrong diagnosis
        // this project has made in the last week has had that shape.
        //
        // So: of the bodies standing there, how many are actually enemies of V,
        // and how many can actually see. Read off the puppets themselves rather
        // than off what we intended.
        this.ReadBackDetail(game, objects, estate);
        if found <= 0 {
            // NOBODY ALIVE THERE RIGHT NOW, which is not the same as nobody
            // ever having been there. The count keeps its high-water mark so
            // that a detail V has fought through does not read as a community
            // that never placed anybody: the code says what is true now, the
            // count says what was turned.
            this.NoteGuards(game, estate, 2, this.HighWater(estate),
                            ArraySize(names));
            return;
        }
        // ONLY THE BANNER IS LATCHED, and only on the full detail.
        //
        // A partial answer is the normal case rather than a fault: come in over
        // the back wall and the posts down at the gate are 90 m away and not
        // streamed, exactly as the old spawn's far anchors were not. So the
        // audit keeps asking until every post is accounted for, and the count
        // it reports is the highest it has seen rather than this pass's.
        if found > this.HighWater(estate) {
            this.SetHighWater(estate, found);
        }
        this.NoteGuards(game, estate, 3, this.HighWater(estate),
                        ArraySize(names));
        if !this.Announced(estate)
            && this.HighWater(estate) >= ArraySize(names) {
            // THE BANNER LATCHES, THE PASS DOES NOT.
            //
            // `m_estateDetailDone` used to stop the audit here, and that was
            // wrong for two reasons that only showed up in play. A guard who
            // streams in after the thirtieth was counted never gets his attitude
            // or his senses, and a guard whose state is reset by anything else
            // never gets them back. The pass is one resolve and one lookup, so
            // running it every few seconds while V is on the estate costs less
            // than the bug it prevents.
            this.SetAnnounced(estate);
            CCSharedHud.Notify(game, estate ? "Estate security on site"
                                            : "Arasaka security on site");
        }
    }

    // Per-site state, so one function can serve both. Small accessors rather
    // than an array: redscript arrays on a ScriptableSystem come back from an
    // old save at the wrong length, which is the trap at the top of
    // Gig01_Holocall.
    private func HighWater(estate: Bool) -> Int32 {
        if estate { return this.m_estateFound; }
        return this.m_compoundFound;
    }

    private func SetHighWater(estate: Bool, n: Int32) -> Void {
        if estate { this.m_estateFound = n; } else { this.m_compoundFound = n; }
    }

    private func Announced(estate: Bool) -> Bool {
        if estate { return this.m_estateAnnounced; }
        return this.m_compoundAnnounced;
    }

    private func SetAnnounced(estate: Bool) -> Void {
        if estate {
            this.m_estateAnnounced = true;
        } else {
            this.m_compoundAnnounced = true;
        }
    }

    // WHAT STATE ARE THEY ACTUALLY IN, measured on the bodies themselves.
    //
    // Three numbers, because there are three ways a guard who is standing at his
    // post can still ignore the player, and in game they look identical:
    //
    //   hostile   the pairwise attitude towards V actually landed. If this is
    //             low, `CCSharedAttitude` is not reaching these bodies at all.
    //   senses    the sense component exists and is enabled. If this is low,
    //             they are enemies who cannot see, which is precisely "they
    //             only react when I shoot one".
    //   working   they are inside a workspot. An NPC held in an infinite idle
    //             may not run perception at all, and the pose is the one thing
    //             that changed between the guard that WORKED on the bench and
    //             these thirty (the bench guard used a different idle, and
    //             gotcha 72 says a community does not reliably apply one, so he
    //             may simply have been standing free).
    //
    // Whichever of the three is the odd one out is the answer, and it costs one
    // pass rather than one playthrough per hypothesis.
    private func ReadBackDetail(game: GameInstance,
                                objects: array<ref<GameObject>>,
                                estate: Bool) -> Void {
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        if !IsDefined(qs) {
            return;
        }
        let player: ref<PlayerPuppet> = GameInstance.GetPlayerSystem(game)
            .GetLocalPlayerMainGameObject() as PlayerPuppet;
        if !IsDefined(player) {
            return;
        }
        let hostile: Int32 = 0;
        let seeing: Int32 = 0;
        let working: Int32 = 0;
        let i: Int32 = 0;
        while i < ArraySize(objects) {
            let puppet: ref<ScriptedPuppet> = objects[i] as ScriptedPuppet;
            if IsDefined(puppet) && ScriptedPuppet.IsAlive(puppet) {
                let agent: ref<AttitudeAgent> = puppet.GetAttitudeAgent();
                if IsDefined(agent)
                    && Equals(agent.GetAttitudeTowards(player.GetAttitudeAgent()),
                              EAIAttitude.AIA_Hostile) {
                    hostile += 1;
                }
                let senses: ref<SenseComponent> = puppet.GetSensesComponent();
                if IsDefined(senses) && senses.IsEnabled() {
                    seeing += 1;
                }
                if GameInstance.GetWorkspotSystem(game).IsActorInWorkspot(puppet) {
                    working += 1;
                }
            }
            i += 1;
        }
        let key: String = estate ? "cc_g01_dbg_estate" : "cc_g01_dbg_compound";
        if qs.GetFactStr(key + "_hostile") != hostile {
            qs.SetFactStr(key + "_hostile", hostile);
        }
        if qs.GetFactStr(key + "_senses") != seeing {
            qs.SetFactStr(key + "_senses", seeing);
        }
        if qs.GetFactStr(key + "_workspot") != working {
            qs.SetFactStr(key + "_workspot", working);
        }
    }

    // HOW FAR CAN A GUARD SEE? NOT READABLE, and not guessed at.
    //
    // Playtest 2026-08-25, and it is the most useful thing said about this all
    // day: *"if I stand right in front of a guard, but like attached to it, it
    // does the warning... but I need to be like touching it. If I stand like 1m
    // out nothing happens"*.
    //
    // So THE WARNING EXISTS. The guards are not inert and the machinery is not
    // missing; what is wrong is the DISTANCE at which they notice anybody. That
    // is a smaller and different problem from every one chased before it.
    //
    // AND THE POSE IS NOT THE CAUSE. The lab's button 3 takes all of them out
    // of their idle animation live, and playtest ran it: *"nothing changed with
    // press 3"*. That is the second time the workspot has been suspected and
    // cleared, and it should not be suspected a third time.
    //
    // `SenseComponent` has neither `GetMaxDistance` nor `IsPlayerCloseToNPC`,
    // so the range is not readable from here and no number is invented for it.
    // Two attempts at guessing a method name were made and both were caught by
    // the compiler, which is the only reason they cost nothing.

    // The readout, and it exists because every failure in this path is SILENT in
    // game: a post nobody is standing at looks exactly like a post the game has
    // not got round to placing yet.
    //
    //   0  nothing has looked yet
    //   1  the community name did not resolve. The sector is not loading
    //   2  resolved, but the spawner has no bodies. Either the quest phase has
    //      not activated the community, or nothing has streamed in yet
    //   3  found, and made hostile. cc_g01_dbg_estate_guards is how many
    private func NoteGuards(game: GameInstance, estate: Bool, code: Int32,
                            found: Int32, total: Int32) -> Void {
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        if !IsDefined(qs) {
            return;
        }
        // THE EXPECTED TOTAL IS PUBLISHED, NOT TYPED INTO THE PANEL.
        //
        // The panel said "of 30" as a literal, and the post count had just
        // changed from 30 to 29 because one of them landed a metre from a
        // base-game sniper. A hand-copied total is the same drift the entry-name
        // cross-check exists to stop (gotcha 76), one screen further out.
        let key: String = estate ? "cc_g01_dbg_estate" : "cc_g01_dbg_compound";
        if qs.GetFactStr(key + "_total") != total {
            qs.SetFactStr(key + "_total", total);
        }
        if qs.GetFactStr(key) != code {
            qs.SetFactStr(key, code);
        }
        if qs.GetFactStr(key + "_guards") != found {
            qs.SetFactStr(key + "_guards", found);
        }
    }

    // FIND THE BODY THE COMMUNITY PLACED, and keep looking until it is there.
    //
    // `GetGameObjectsFromSpawnerEntityID` asks the spawner system for one
    // entry's objects, which is exactly the question and does not care where he
    // is standing or whether anything else is nearby. The community NodeRef
    // resolves to the community's id; gotcha 69 is the whole join.
    //
    // Returns quietly when he is not there yet. The caller is a tick.
    // Hoshino's community, and the one diagnostic this beat needs.
    //
    // The names must match tools/gig01/gen_community.py exactly: the community
    // reference is what resolves to the id the spawner is asked about, and the
    // entry name is which of its entries to ask for. Both are stated in one
    // place there and repeated here because redscript cannot import Python.
    //
    // cc_g01_dbg_hoshino is the readout, and it exists because every failure in
    // this path is SILENT in game. A man who is not there looks exactly like a
    // man the game has not got round to placing yet:
    //
    //   0  nothing has looked yet
    //   1  the community name did not resolve. The sector is not loading, and
    //      nothing below this line can work
    //   2  resolved, but the spawner has no body for the entry. Either the
    //      quest phase has not activated it, or it is still being placed
    //   3  FOUND, and set neutral. This is the good one
    //   4  found, and dead
    public static func CommunityRef() -> String {
        return "$/mod/cc_g01_hoshino/#cc_g01_hoshino_com";
    }

    public static func Entry() -> CName { return n"hoshino"; }

    // MAKE HIM AN ENEMY OF V, and it is TWO things rather than one.
    //
    // Extracted 2026-08-25 so the dev lab drives the shipped path instead of a
    // copy of it. A bench that reimplements the thing it is testing measures its
    // own copy.
    //
    // OUT OF THE FRIENDLY GROUP FIRST. He is put in it while he is protected, to
    // keep the reticle off him, and an NPC left there is one the player still
    // cannot shoot, which would make the shield permanent by another route.
    // Back to `neutral`, his record's own `baseAttitudeGroup`, rather than to
    // n"hostile": the pairwise line is what makes him an enemy of V, and the
    // hostile GROUP would set him against the Arasaka guards as well.
    //
    // AND HIS EYES ON, which the attitude does not do. `enableSensesOnStart:
    // false` is the third peaceful field on his record, and an NPC who cannot
    // perceive V cannot shoot at him however hostile he is.
    public static func TurnOnPlayer(npc: ref<ScriptedPuppet>,
                                    player: ref<PlayerPuppet>) -> Void {
        if !IsDefined(npc) || !IsDefined(player) {
            return;
        }
        let agent: ref<AttitudeAgent> = npc.GetAttitudeAgent();
        if IsDefined(agent) {
            agent.SetAttitudeGroup(n"neutral");
            agent.SetAttitudeTowards(player.GetAttitudeAgent(),
                                     EAIAttitude.AIA_Hostile);
        }
        let senses: ref<SenseComponent> = npc.GetSensesComponent();
        if IsDefined(senses) {
            senses.Toggle(true);
        }
    }

    public static func Note(game: GameInstance, code: Int32) -> Void {
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        if IsDefined(qs) && qs.GetFactStr("cc_g01_dbg_hoshino") != code {
            qs.SetFactStr("cc_g01_dbg_hoshino", code);
        }
    }

    // FIND THE BODY THE COMMUNITY PLACED, and keep looking until it is there.
    //
    // `GetGameObjectsFromSpawnerEntityID` asks the spawner system for one
    // entry's objects, which is exactly the question and does not care where he
    // is standing or whether anything else is nearby. Gotcha 69 is the join.
    //
    // Returns quietly when he is not there yet. The caller is a tick, because
    // the community places him asynchronously and a single look on the frame the
    // objective changed would find nothing.
    private func FindHoshino() -> Void {
        if this.m_hoshinoSpawned {
            return;
        }
        let game: GameInstance = this.GetGameInstance();
        let nref: NodeRef = CreateNodeRef(NegativeBalanceEncounter.CommunityRef());
        let root: GlobalNodeRef;
        let g: GlobalNodeRef = ResolveNodeRef(nref, root);
        if !GlobalNodeRef.IsDefined(g) {
            NegativeBalanceEncounter.Note(game, 1);
            return;
        }
        let objects: array<ref<GameObject>>;
        GetGameObjectsFromSpawnerEntityID(Cast<EntityID>(g),
                                          [NegativeBalanceEncounter.Entry()],
                                          game, objects);
        let i: Int32 = 0;
        while i < ArraySize(objects) {
            let puppet: ref<ScriptedPuppet> = objects[i] as ScriptedPuppet;
            if IsDefined(puppet) && ScriptedPuppet.IsAlive(puppet) {
                this.m_hoshinoId = puppet.GetEntityID();
                this.m_hoshinoSpawned = true;
                CCSharedAttitude.Neutral(game, this.m_hoshinoId);
                NegativeBalanceEncounter.Note(game, 3);
                return;
            }
            i += 1;
        }
        NegativeBalanceEncounter.Note(game, 2);
    }

    // WHY HOSHINO IS NEUTRAL, which is the CCSharedAttitude.Neutral call in
    // FindHoshino above.
    //
    // He spawned hostile like the guards, so he opened fire during his own
    // conversation (playtest, 2026-08-12). That is wrong for the scene and
    // wrong for the character: the whole point of him is that he is an
    // administrator, not a soldier. He signs, he does not fight.
    //
    // Neutral until provoked. Shooting him flips him back by the game's own
    // reaction rules, so "until we attack" comes for free: we do not have to
    // watch for it. The retry budget behind that call, and why an attitude
    // cannot be set in the tick the spawn was asked for, are in
    // CCShared_Attitude.reds.



    // NO SCRIPT PLACES JOHNNY ANY MORE, and nothing here should start.
    //
    // Every beat is a scene actor, staged by its own scene in front of V and
    // facing V. The offsets live in tools/gig01/gen_scenes.py BEAT_STAGING and the
    // facing is computed, never written by hand.
    //
    // The two things a script route would have to solve, and why it no
    // longer has to:
    //   placement  `Teleport` ignores the position for a puppet and drops
    //              him on the player, so a script needs a workspot device.
    //              A scene needs nothing.
    //   the pose   moving a body between two workspots flashes the bind
    //              pose, which is the T-pose two players reported. A
    //              scene-placed actor arrives already posed.
    //
    // His face is still unset. SetJohnnyFace applied a preset from
    // ReactionComponent's own table (3/7 = disgust); see docs/backlog.md if
    // his expression ever reads blank.
    //
    public func DownloadStep(step: Int32) -> Void {
        switch step {
            case 0:
                // The big bottom-of-screen bar carries this beat now. The three
                // corner banners it replaced ("COPYING RECORDS 24%..." etc) are
                // gone: two progress readouts for one action is just noise, and
                // the design called for the old one to go once the bar worked.
                // 3.2 s is not arbitrary - it is exactly how long the two 1.6 s
                // steps below take, and the bar reports FAILED if it closes
                // under 96%.
                CCSharedHud.RunBar(this.GetGameInstance(), "COPYING LEDGER", 3.2);
                break;
            case 1: break;
            case 2:
                CCSharedHud.ShowBar(this.GetGameInstance(), false, "");
                // Having the data is not the end of the beat - but Johnny does
                // NOT appear yet.
                //
                // This used to call StartTerminalTalk() right here, which spawned
                // him half a metre from V and started a ~32 s conversation WHILE
                // V could still be nose-to-screen in the device zoom. the playtest hit
                // a hard input lock at this exact point on 2026-08-12 (pressed C
                // to leave the terminal, nothing responded).
                //
                // Not proven to be the cause, but spawning a puppet on top of a
                // player who is locked in a UI is a bad idea on its own, and the
                // staging was wrong anyway: he should arrive when V turns away
                // from the screen, not while V is reading it. Tick now waits for
                // IsUsingDevice to go false - the playbook's reliable "off the
                // screen" signal - before starting the exchange.
                GameInstance.GetQuestsSystem(this.GetGameInstance())
                    .SetFactStr("cc_g01_ledger_copied", 1);
                break;
            default: return;
        }

        if step < 2 {
            let cb: ref<CCGig01DownloadStep> = new CCGig01DownloadStep();
            cb.system = this;
            cb.step = step + 1;
            GameInstance.GetDelaySystem(this.GetGameInstance()).DelayCallback(cb, 1.6, false);
        }
    }

    // THE SEND. Nix has agreed and asked who is paying; V pays and the ledger
    // goes out. Comic pp. 26-27 for the call, p30 for the money-transfer toast.
    //
    // Three beats, then cc_g01_ledger_sent, which completes "Answer Nix's call"
    // and hands over to "Wait for Nix to call back".
    public func SendStep(step: Int32) -> Void {
        let key: String;
        let kind: SimpleMessageType = SimpleMessageType.Connection;
        switch step {
            case 0: key = "cc-g01-hud-send-01"; break;
            case 1: key = "cc-g01-hud-send-02"; break;
            case 2:
                key = "cc-g01-hud-send-03";
                // THE MONEY DOES NOT MOVE HERE ANY MORE (2026-09-03). V used
                // to pay Nix during the send, i.e. before Nix had done a
                // thing; the design call is that he pays on delivery, after
                // the message with the location lands and V has thanked him.
                // PayNix() below does it, on a fact the quest phase sets.
                GameInstance.GetQuestsSystem(this.GetGameInstance())
                    .SetFactStr("cc_g01_ledger_sent", 1);
                break;
            default: return;
        }

        CCSharedHud.NotifyTyped(this.GetGameInstance(), GetLocalizedTextByKey(StringToName(key)), kind, 2.5);

        if step < 2 {
            let nxt: ref<CCGig01SendStep> = new CCGig01SendStep();
            nxt.system = this;
            nxt.step = step + 1;
            GameInstance.GetDelaySystem(this.GetGameInstance()).DelayCallback(nxt, 1.8, false);
        }
    }

    // StartLegendTalk() used to live here (comic p28, the crosswalk). It became
    // gig01_legend.scene on 2026-08-13, and that scene was deleted on
    // 2026-09-05: the recast could not cast it out of vanilla recordings.
    // SendStep still sets cc_g01_ledger_sent, which is now read only by the
    // Nix call.
    //
    // Stage Johnny at the office desk, then run the comic's p22 exchange.
    //
    // Placement is deliberately different from the street beat. V is at a
    // terminal, nose to a screen against a wall, so "1.8 m ahead" would put
    // Johnny inside the desk or the wall. He goes almost entirely to the SIDE,
    // barely forward - leaning at the end of the desk, in frame the moment V
    // turns away from the screen.
    //
    // The 2.5 s wait is the staging latency: spawn, ~2 s to stream in, then the
    // workspot that makes him render. Speaking before that would put the first
    // line over an empty room, which is the bug the Elena beat had.
    public func StartTerminalTalk() -> Void {
        // V is off the screen. That is a real player action, so the journal gets
        // to say so - "Disconnect from the terminal" completes here.
        GameInstance.GetQuestsSystem(this.GetGameInstance())
            .SetFactStr("cc_g01_terminal_left", 1);
        // ...and that fact is now ALL this does. The exchange itself is
        // gig01_terminal.scene, which brings its own Johnny and its own timing.
        // The staging latency this method used to hand-tune (spawn, ~2 s to
        // stream in, then the workspot) belongs to the scene system now.
    }

    // ------------------------------------------------------------- subtitles
    // Spoken lines go through the game's real subtitle panel, not the warning
    // banner. BaseSubtitlesGameController listens on the UIGameData blackboard:
    // ShowDialogLine takes an array<scnDialogLineData>, HideDialogLine an
    // array<CRUID>.
    //
    // Two rules taken from that controller, both load-bearing:
    //   * scnDialogLineType.OwnerlessRegular is the one type IsMainDialogLine
    //     accepts WITHOUT a speaker GameObject, so Johnny and Mama Welles can
    //     talk without an entity to hang the line on. speakerName is the label.
    //   * A line id stays in m_pendingShowLines until it is HIDDEN, and a
    //     second Show with an id already pending is silently dropped. So every
    //     Show must be preceded by a Hide or only the first line ever appears.
    //     All our lines share the default CRUID, which real scene lines never
    //     use, so they reuse one widget and our Hide cannot remove a game line.
    //
    // The line's `duration` only drives the text-reveal animation; nothing
    // auto-removes it, hence the explicit hide after the last line.

    // ShowSubtitle(speakerKey, textKey, seconds) and SpeakAs(speaker, ...) were
    // here: the caption API, pushing scnDialogLineData onto the UIGameData
    // blackboard. They worked, and they are DELETED rather than kept as a
    // convenience, because a caption can never carry audio - no locstring RUID,
    // so nothing for the voiceover map to key on - and leaving the API in the
    // tree invites the next beat to produce a permanently silent line. If text
    // is needed, write a .scene. See BUILDING.md.
    //
    // HideSubtitle went with them on 2026-08-14. Its last caller was
    // CCGig01JohnnyLeave, which cleared the panel after the script's Johnny had
    // spoken; with no scripted captions left there is no panel to clear.

    // Plays a scripted exchange, one line every few seconds. Text comes from our
    // localization so it stays translatable; ids 0..3 are Hoshino's scene,
    // 10..16 the El Coyote epilogue.
    // THE SCRIPTED-CAPTION ROUTE IS GONE, and this is the record of why.
    //
    // Line(index) pushed dialogue onto the screen through the UIGameData
    // blackboard. It worked, it carried a speaker name, and it could NEVER be
    // voiced: a caption has no scnlocLocstringId, so there is no RUID, so the
    // voiceover map has nothing to key on. playtesting covered the 2026-08-13 build
    // and reported every one of those beats silent - Johnny's "Fucking
    // Arasaka", the whole terminal exchange, the crosswalk, V's reply to
    // Hoshino, "Ledger's closed.", "No more payouts." That is the mechanism
    // working as designed, not six separate bugs.
    //
    // All of them are .scene resources now, played by the quest phase:
    //
    //   gig01_arasaka   comic p11, after Elena's call
    //   gig01_terminal  comic pp. 22 + 25, the office desk
    //   gig01_legend    comic p28, the crosswalk
    //   gig01_kill      comic p45, over Hoshino's body
    //   gig01_malware   comic p51, the estate terminal
    //   gig01_hoshino   V's reply, added to the scene that already existed
    //
    // WHAT DID NOT MOVE: the quest facts. cc_g01_terminal_left,
    // cc_g01_malware_talk, cc_g01_hoshino_dead and the rest are still set here,
    // and the quest phase waits on them. Presentation moved; progression did
    // not. That is deliberate and it is why a misbehaving scene cannot make the
    // gig unfinishable.

    // Screen beats for the estate malware upload, spaced out by delayed callbacks.
    public func UploadStep(step: Int32) -> Void {
        switch step {
            case 0:
                // The real vanilla upload bar, on the terminal V is plugged
                // into. 12.5 s covers the five beats below at 2.5 s each.
                CCSharedHud.RunBar(this.GetGameInstance(),
                    "SABOTAGE: UPLOADING MALWARE TO THE NETWORK", 10.0);
                break;
            case 1: break;
            case 2: break;
            case 3: break;
            case 4:
                CCSharedHud.ShowBar(this.GetGameInstance(), false, "");
                // V and Johnny, comic p51, are gig01_malware.scene now. It
                // is NOT entered on the fact below: the upload finishes while V
                // is still in the device zoom, and staging an actor on a player
                // locked in a UI is what soft-locked the office beat once. Tick
                // sets cc_g01_malware_talk when IsUsingDevice goes false, and
                // the quest phase waits on that.
                GameInstance.GetQuestsSystem(this.GetGameInstance()).SetFactStr("cc_g01_malware_done", 1);
                this.m_uploadBusy = false;
                break;
        }
        if step < 4 {
            let cb: ref<CCGig01UploadStep> = new CCGig01UploadStep();
            cb.system = this;
            cb.step = step + 1;
            GameInstance.GetDelaySystem(this.GetGameInstance()).DelayCallback(cb, 2.5, false);
        }
    }

    // ================================================ THE MOVING WAY-IN MARKER
    //
    // ONE marker, registered by this script, moved up the hill as V reaches
    // each waypoint. `obj_wayin` deliberately carries NO journal pins at all.
    //
    // ------------------------------------------------------------------------
    // WHY NOT SIX JOURNAL PINS, ONE ACTIVE. THAT WAS BUILT AND IT DOES NOT WORK.
    // ------------------------------------------------------------------------
    // The first attempt authored six `gameJournalQuestMapPin` entries under the
    // objective and called `JournalManager.ChangeEntryState(..., Inactive, ...)`
    // on the five that should be hidden. it was playtested and photographed all
    // six on screen at 150/150/125/90/70/30 m.
    //
    // The call is not in doubt - it is the same one the quest graph's journal
    // node makes, the path is the one the graph activates with, and the
    // activation half demonstrably works. **A quest map pin does not go away
    // when its entry is set Inactive.** Read the map-pin playbook's ingredient 2
    // ("the quest phase ACTIVATES the pin entry") for what that means now: it
    // was measured while a patched cooked-mappin table was in play, and the
    // honest current statement is that the pin's entry state gets it REGISTERED
    // and the parent objective being active is what makes it RENDER. There is no
    // route back.
    //
    // Vanilla agrees, which is the other half of the answer: 288 shipped
    // objectives carry 2 pins, and one carries 28. `q104_02_av_chase/
    // follow_tracks` is six waypoints down a road and `q202_nomads/cross_border`
    // is seven across a river - CDPR draws routes as pins and shows them ALL AT
    // ONCE. The thing the design does not want is the thing the journal does.
    //
    // So the marker is not a journal entry. `MappinSystem.RegisterMappin` takes
    // a position directly - which also disposes of the anchor problem, since
    // there is nothing to resolve and no offset to compute - and
    // `SetMappinPosition` moves it. Documented by psiberx (who wrote Codeware
    // and ArchiveXL) as a supported thing for mods to do.
    //
    // THE COST, and it is real: the objective loses its journal distance
    // readout, because it no longer owns a pin. The marker draws its own
    // distance, which is what the player actually reads.
    private func ShowWayInMarker(leg: Int32) -> Void {
        let spot: Vector4 = CCGig01Places.WayInMarker(leg);
        if this.m_wayinMappinUp {
            CCSharedMappins.Move(this.GetGameInstance(), this.m_wayinMappin, spot);
            return;
        }
        this.m_wayinMappin = CCSharedMappins.Show(this.GetGameInstance(), spot);
        this.m_wayinMappinUp = true;
    }

    // Take it down. Called when the objective completes, and from outside the
    // "gig is running" branch as well - the discipline ReleaseMama earned: a
    // marker we registered and never removed would sit on the map for the rest
    // of the save, and nobody would attribute it to us.
    private func HideWayInMarker() -> Void {
        if !this.m_wayinMappinUp {
            return;
        }
        CCSharedMappins.Hide(this.GetGameInstance(), this.m_wayinMappin);
        this.m_wayinMappinUp = false;
        this.m_wayinShown = 0;
    }

    // ----------------------------------------------------------- Mama Welles
    // Prefer the real one. She IS usually in El Coyote Cojo, but not reliably
    // (time of day + quest state), so the epilogue looks for her first and only
    // spawns a stand-in when she is not there. Two Mama Welles in one
    // bar is worse than either alternative.
    //
    // The record is `Character.Mama_Welles`: capital M and W. Confirmed
    // 2026-08-11 by inspecting the live NPC with the dev menu's look-at dump;
    // every lowercase spelling returns false from TweakDB, so this is
    // case-sensitive and must not be "tidied up".

    private func MamaRecord() -> TweakDBID {
        return t"Character.Mama_Welles";
    }

    // Finds a live Mama Welles near the player. The base-game one OR the one we
    // spawned, since both carry the same record. Pattern lifted from
    // sensorDevice.swift's targeting query.
    // Mute or unmute an NPC's voiceset LINES. Declared in Codeware's native
    // dump (`entChangeVoicesetStateEvent`, three fields); the quest-graph twin
    // is questChangeVoicesetState_NodeType, which is how vanilla does it.
    // SECOND ATTEMPT, and it names the input rather than switching everything
    // off. `enableVoicesetLines = false` alone did NOT stop "Look who it is"
    // in game (playtest, 2026-08-15), so the blanket flag is either ignored or
    // does not cover greetings.
    //
    // `inputsToBlock` is the other half of the same event, and the name to put
    // in it is not a guess: base\quest\tertiary_characters\vsets\
    // vset_mama_welles.scene declares its entry points as `greeting`,
    // `greeting_var_1` and `greeting_var_2`. The base input is blocked with
    // blockSpecificVariation off, which should cover the variants with it.
    //
    // THE SCENE'S 2.6 s LEAD DOES NOT DEPEND ON THIS WORKING. If this is still
    // ignored, her greeting lands in the gap and reads as an exchange; if it
    // starts working, the gap is a beat of silence. Neither outcome is broken,
    // which is the only reason it is worth one more try on a mechanism that has
    // already failed once.
    // Give Mama Welles back everything we took: the base-game fact and her
    // voiceset. Extracted so the release can be called from OUTSIDE the "gig is
    // running" branch as well as inside it - see the call in Tick().
    private func ReleaseMama(qs: ref<QuestsSystem>, player: ref<PlayerPuppet>) -> Void {
        if this.m_mamaHeld {
            qs.SetFactStr("mama_is_talking", 0);
            this.m_mamaHeld = false;
        }
        if this.m_mamaMuted {
            let mamaVo: ref<GameObject> = this.FindMamaWelles(player);
            if IsDefined(mamaVo) {
                CCSharedWorld.SetVoiceset(mamaVo, true);
            }
            // Cleared even if she could not be found, so a despawned Mama does
            // not leave this latched and block the retry when she comes back.
            // Her voiceset state does not survive her entity anyway.
            this.m_mamaMuted = false;
        }
    }

    private func FindMamaWelles(player: ref<PlayerPuppet>) -> ref<GameObject> {
        let query: TargetSearchQuery = TSQ_NPC();
        query.testedSet = TargetingSet.Complete;   // through walls: she is indoors
        query.includeSecondaryTargets = false;
        query.ignoreInstigator = true;
        query.maxDistance = 60.0;
        query.filterObjectByDistance = true;

        let parts: array<TS_TargetPartInfo>;
        GameInstance.GetTargetingSystem(this.GetGameInstance()).GetTargetParts(player, query, parts);

        let i: Int32 = 0;
        while i < ArraySize(parts) {
            let target: ref<GameObject> = TS_TargetPartInfo.GetComponent(parts[i]).GetEntity() as GameObject;
            let puppet: ref<ScriptedPuppet> = target as ScriptedPuppet;
            if IsDefined(puppet) && puppet.GetRecordID() == this.MamaRecord() {
                return puppet;
            }
            i += 1;
        }
        return null;
    }

    // SpawnMamaWelles AND DespawnMamaWelles WERE HERE, deleted 2026-08-18.
    //
    // They put our own Character.Mama_Welles on her captured mark when the
    // base-game one was not in the bar, and removed it again afterwards. The
    // case they covered is now prevented rather than handled: Gig01_Start waits
    // for sq018 (Heroes), which is the quest that both unlocks the bar's door
    // and puts Mama in it, so V cannot reach the epilogue on a save where she
    // is missing. Confirmed in play across times of day, 2026-08-18, and the
    // world data agrees: she has no community entry, so nothing about her is
    // hour-driven. docs/backlog.md 19.
    //
    // The PROBE stayed. `cc_g01_mama_present` still answers 1 or 2, because
    // entering gig01_epilogue with nobody to acquire leaves the scene holding
    // an unresolved actor and that crashed the game at teardown in August. On 2
    // the quest phase now skips the epilogue instead of playing a stand-in.

    // ----------------------------------------------------------------- payout
    // Elena never pays V. She never learns it was V, and the design note in
    // design.md deliberately left the gig unpaid. the design called for a reward
    // anyway (2026-08-11), so it is framed as what V skims while inside
    // Hoshino's payment network rather than anything Elena hands over. That
    // keeps the ending's silence intact.
    //
    // Guarded by a FACT, not a script field: script fields reset on load, and a
    // reward that re-grants every time the save is reloaded is a money printer.
    // SPLIT IN TWO, 2026-09-03, because the eddies were arriving in the wrong
    // scene. They used to land with the Street Cred at the end of the gig, in
    // El Coyote, where nothing on screen explains a payment; the money is
    // skimmed off Hoshino's network by the malware Nix attached, so it now
    // arrives the moment the upload finishes at his terminal. That is also
    // where the vanilla currency animation reads as an event rather than as
    // an afterthought.
    //
    // No banner over either half. Changing the player's money drives the
    // game's own eddies counter, and Street Cred draws its own popup; the
    // 'reward' string is retired with the notification it carried.
    // TWELVE AND A HALF THOUSAND, raised from 2500 on 2026-09-03. The number is
    // set against what V pays Nix, not chosen on its own: PayNix takes 15000 on
    // delivery, so the gig nets the player 2500 DOWN. That is deliberate and it
    // is kept small. No vanilla gig ends with the player poorer, so a large
    // loss reads as a bug; a small one reads as V eating the cost of a job he
    // took for nothing, which is where the ending already sits. Change either
    // number and the other has to be reconsidered.
    private func GiveSkim(player: ref<PlayerPuppet>, qs: ref<QuestsSystem>) -> Void {
        qs.SetFactStr("cc_g01_skimmed", 1);
        CCSharedRewards.Pay(this.GetGameInstance(), player, 12500, 0);
    }

    private func GiveReward(player: ref<PlayerPuppet>, qs: ref<QuestsSystem>) -> Void {
        qs.SetFactStr("cc_g01_rewarded", 1);
        CCSharedRewards.Pay(this.GetGameInstance(), player, 0, 300);
    }

    // ------------------------------------------------------- paying the fixer
    // V's fee to Nix, moved here 2026-09-03. It used to come out during the
    // send, before Nix had read a line of the ledger; the design call is that
    // V pays on DELIVERY, after the message with Hoshino's name and the
    // estate lands and V has thanked him.
    //
    // NOTHING IS DRAWN BY THIS FUNCTION, and that is the point. It used to
    // raise a banner of our own ("Transferred to Nix. Fifteen thousand, up
    // front."), which is a mod's text over a moment the game already
    // animates: changing the player's money is what drives the eddies
    // counter, so the transaction alone gives the vanilla currency update.
    //
    // Guarded by a FACT, not a script field, for the reason GiveReward gives
    // above: a field resets on load, and a charge that re-applies on every
    // reload empties the player's account.
    private func PayNix(player: ref<PlayerPuppet>, qs: ref<QuestsSystem>) -> Void {
        qs.SetFactStr("cc_g01_nix_paid", 1);
        GameInstance.GetTransactionSystem(this.GetGameInstance())
            .RemoveItemByTDBID(player, t"Items.money", 15000);
    }

    // ------------------------------------------------------------------ tick
    public func Tick() -> Void {
        let game: GameInstance = this.GetGameInstance();
        let player: ref<PlayerPuppet> = GameInstance.GetPlayerSystem(game)
            .GetLocalPlayerMainGameObject() as PlayerPuppet;

        // Set at the very end of the pass below, once the gig is finished AND
        // everything this system took has been given back. See it for the rule.
        let stop: Bool = false;

        if IsDefined(player) {
            let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
            let pos: Vector4 = player.GetWorldPosition();
            let accepted: Bool = qs.GetFactStr("cc_g01_accepted") == 1;

            // WHERE AM I, AND DOES THE ESTATE THINK I AM INSIDE IT?
            //
            // Deliberately outside every gate, including `accepted`. The whole
            // estate leg hangs off one boundary test, and when that test is
            // wrong the symptom is that NOTHING happens: no guards, no Hoshino,
            // no objective, and nothing on screen to say why. Two player reports
            // on 2026-08-25 were exactly that, and the ceiling that caused it
            // could not be read off any file because the ground it was wrong
            // about is the base game's.
            //
            // A diagnostic gated on the thing it measures is gotcha 17, and this
            // project has paid for it four times, so this one is gated on
            // nothing at all.
            //
            //   _pz         the player's height, whole metres
            //   _estate_in  1 if the traced outline accepts this spot
            //   _at_estate  1 if ANY arm of the arrival test accepts it, which
            //               is the condition the whole leg actually waits on
            let inOutline: Bool = CCGig01Places.InsideEstate(pos);
            let atEstateNow: Bool = inOutline
                || CCSharedWorld.Near(pos, CCGig01Places.EstateGate(), 45.0, 12.0, 25.0)
                || CCSharedWorld.Near(pos, CCGig01Places.Hoshino(), 70.0, 12.0, 60.0);
            qs.SetFactStr("cc_g01_dbg_pz", Cast<Int32>(pos.Z));
            qs.SetFactStr("cc_g01_dbg_estate_in", inOutline ? 1 : 0);
            qs.SetFactStr("cc_g01_dbg_at_estate", atEstateNow ? 1 : 0);

            // RELEASE MAMA WELLES EVEN WHEN THE GIG IS NO LONGER RUNNING.
            //
            // Everything that takes something from her lives inside the
            // `accepted && !done` branch below - which means the moment
            // cc_g01_done is set, that branch stops running and the release
            // inside it can never fire. In practice the gig sets
            // cc_g01_mama_talked minutes before cc_g01_done and releases her on
            // the next tick, so this has probably never bitten. "Probably" is
            // not good enough for a base-game NPC we have muted: the failure is
            // a permanently silent Mama Welles, it is invisible until someone
            // walks into that bar hours later, and no playtest would ever
            // attribute it to us.
            //
            // So the release is checked FIRST and outside the gate. It costs two
            // Bool reads on a tick that is doing far more than that anyway, and
            // it only does anything if we are still holding something we should
            // not be.
            if !accepted || qs.GetFactStr("cc_g01_done") > 0 {
                this.ReleaseMama(qs, player);
                // A DespawnMamaWelles call sat here until 2026-08-18, to take
                // our stand-in down on any route that closed the gig without
                // finishing the epilogue. There is no stand-in to take down now.
            }

            // ...and the same discipline for the way-in marker, for the same
            // reason. It is OUR mappin, registered at runtime, and the journal
            // knows nothing about it - so nothing else will ever take it down.
            // A marker left registered sits on the map for the rest of the save.
            //
            // Checked outside the gate and on three conditions rather than one:
            // the objective is done, the gig is done, or the gig is not running.
            // HideWayInMarker returns immediately when there is nothing up, so
            // this is two Bool reads on a tick that is doing far more.
            if qs.GetFactStr("cc_g01_wayin_reached") > 0
                || !accepted
                || qs.GetFactStr("cc_g01_done") > 0 {
                this.HideWayInMarker();
            }

            // The tag-population diagnostic (cc_g01_dbg_lip_johnny /
            // _hoshino, via TraceTagged) was here. It answered its question -
            // the tags ARE populated, which is how `type: Tag` was proven dead
            // rather than merely unproven - and went with the rest of the
            // lipsync instrumentation on 2026-08-14. The finding is in
            // docs/backlog.md 2j; the rule it taught, that a diagnostic must not
            // be gated on anything downstream of what it measures, is docs/gotchas.md #17.

            // NOTHING HERE PLACES JOHNNY, and there is no window to arm.
            //
            // The block that used to sit here moved the scene's Johnny in
            // front of V, and it went with the rest of the script route on
            // 2026-08-17. Each beat's scene now offsets him from an
            // `around_player` marker, turns him to face V with a computed yaw,
            // and glitches him out 250 ms before it ends. The offsets are
            // tools/gig01/gen_scenes.py BEAT_STAGING; the mechanism is
            // docs/backlog.md 9.

            if accepted && qs.GetFactStr("cc_g01_done") == 0 {
                // Arrive at the compound: mark the objective, look for the
                // detail.
                //
                // TWO TESTS, NOT ONE, AND THE LOOKUP ONE IS THE WIDER OF THEM.
                //
                // It used to be a single 60 m sphere on CompoundEntry, and the
                // site does not fit inside it: the office terminal is 63.5 m
                // from that anchor and the terminal room door 67.7 m. A player
                // who reached the computer without crossing the bubble found an
                // empty building.
                //
                // THE OUTLINE, NOT A SPHERE. InsideCompound is the four walked
                // corners; being anywhere in the industrial park counts, by
                // whatever route. The 60 m sphere on the gate stays as well,
                // so arriving at the marked entrance still reads as arriving
                // before the outline is crossed.
                let atOffice: Bool = CCGig01Places.InsideCompound(pos)
                    || Vector4.Distance(pos, CCGig01Places.CompoundEntry()) < 60.0;
                if atOffice && qs.GetFactStr("cc_g01_office_reached") == 0 {
                    qs.SetFactStr("cc_g01_office_reached", 1);
                }
                // THE LOOKUP STARTS EARLIER THAN ARRIVING, so the posts nearest
                // the gate have streamed in by the time V reaches them.
                //
                // AND IT STOPS WHEN THE COMPOUND LEG IS OVER, which is what
                // `cc_g01_left_compound` means and what this had no test for.
                // Field report, 2026-08-21: a save whose objective was already
                // "get to the Arasaka residence" was driven back past the
                // compound, and the whole office detail spawned again, banner
                // and all.
                //
                // WHY NO IN-SESSION LATCH STOPS IT, and this is the part worth
                // carrying to the next site of this shape. Anything this system
                // remembers is a plain field on a ScriptableSystem, so it is
                // empty again after a load and the site reads as untouched.
                // docs/gotchas.md 21 is the same lesson: state that has to
                // outlive a reload belongs in a fact. So a fact decides whether
                // there should be a visit at all.
                if qs.GetFactStr("cc_g01_left_compound") == 0
                    && (atOffice
                        || Vector4.Distance(pos, CCGig01Places.CompoundEntry()) < 100.0) {
                    this.AuditSite(false);
                }

                // The office ledger lives on the narrative computer's own screen
                // (Gig01_OfficeComputer.reds). Opening it sets cc_g01_ledger_read;
                // the download then plays once V is off the screen and ITS last
                // step sets cc_g01_terminal_done.
                //
                // It starts the moment the file is opened, no waiting for V to
                // step away, and deliberately no combat/enemy condition.
                //
                // Tradeoff, by the design call: the device zoom hides the HUD, so
                // any beat that lands while V is still reading is not seen. The
                // sequence is short enough to be mostly caught on the way out. If
                // it turns out none of it is visible, gate ONLY the banners (not
                // the fact) on PlayerStateMachine.IsUIZoomDevice going false - 
                // that flag is the reliable "off the screen" signal, unlike
                // wrapping the zoom interaction, which never fires for computers.
                if qs.GetFactStr("cc_g01_ledger_read") > 0
                    && qs.GetFactStr("cc_g01_terminal_done") <= 0
                    && !this.m_downloadBusy {
                    this.m_downloadBusy = true;
                    this.DownloadStep(0);
                }

                // Johnny's terminal exchange, held until V is OFF the screen.
                // See DownloadStep case 2 for why: he used to spawn on top of a
                // player still locked in the device zoom, which is both wrong
                // staging and a plausible cause of the input lock the playtest hit.
                if qs.GetFactStr("cc_g01_ledger_copied") > 0
                    && qs.GetFactStr("cc_g01_terminal_done") <= 0
                    && !this.m_talkBusy
                    && !CCSharedWorld.IsUsingDevice(this.GetGameInstance(), player) {
                    this.m_talkBusy = true;
                    this.StartTerminalTalk();
                }

                // THE SHARD IN THE DESK, comic pp. 23-24.
                //
                // The object is the game's own shard case container, placed by
                // tools/gig01/gen_sector.py in this mod's own sector, holding
                // Items.cc_g01_shard. It has Take and Read on it, and reading
                // it opens the gig's note. The .archive.xl deletes the vanilla
                // shard that stood there, so the desk carries one.
                //
                // docs/shard-playbook.md is the recipe; docs/backlog.md 6 is
                // the history, including the routes that failed.
                //
                // Four facts, four owners, no guessing about who sets what:
                //   cc_g01_shard_found  HERE  - V is at the desk
                //   cc_g01_shard_open   quest - the find line is over
                //   cc_g01_shard_read   HERE or Gig01_Shard's close wrap
                //   the objective split - the quest phase, "Search the desks"
                //                         then "Read the shard"
                //
                // WHY THIS STILL MEASURES PROXIMITY. The prompt is the player's
                // to press, and pressing it is the SECOND objective. This one
                // is "he has found it", which is what raises that objective and
                // what plays V's line about it, and neither should wait on an
                // interaction the player may not perform for a while.

                // 2.0 m of the shard itself, not 5 m of the terminal: V has to
                // cross the room to it, so it reads as finding something rather
                // than as the objective completing itself while he stands at the
                // screen he was already using.
                if qs.GetFactStr("cc_g01_terminal_done") > 0
                    && qs.GetFactStr("cc_g01_shard_found") == 0
                    && Vector4.Distance(pos, CCG01Shard.ObjectSpot()) <= 2.0 {
                    qs.SetFactStr("cc_g01_shard_found", 1);
                }

                // "BRING JOHNNY TO THE SHARD" was here - drop the script's
                // Johnny on cc_g01_shard_found so the open window re-staged him
                // beside V at the desk. Deleted 2026-08-14: the shard beat is
                // gig01_shard_read, which spawns its own actor when it starts,
                // and its own scene stages him. A scene-owned body needs no
                // re-staging because it did not exist a moment earlier.

                // ANTI-STALL, and it now measures from THE SHARD.
                //
                // It used to count 30 s within 5 m of the TERMINAL, and playtesting
                // caught what that means: the terminal is ~7 m from the shard,
                // so "Search the office desk" could complete itself while V
                // stood at the screen he had just finished using, without ever
                // walking over. An anti-stall that fires where the objective is
                // not is indistinguishable from a bug.
                //
                // 4 m of the shard for 45 s: close enough that V is demonstrably
                // hunting for it, and the 2 m trigger above would have fired
                // already if the object were there. So this can only run when
                // the shard itself is missing - a sector that did not stream
                // - which is the one case it exists for.
                if qs.GetFactStr("cc_g01_terminal_done") > 0
                    && qs.GetFactStr("cc_g01_shard_found") == 0
                    && Vector4.Distance(pos, CCG01Shard.ObjectSpot()) <= 4.0 {
                    this.m_shardWait += 1;
                    if this.m_shardWait > 30 {
                        CCSharedHud.Notify(this.GetGameInstance(), "Shard not found - taking the beat");
                        qs.SetFactStr("cc_g01_shard_found", 1);
                    }
                }

                // 2. THE PLAYER READS IT. The shard on that desk is a real
                //    container now, with "F Take / R Read" on it, so the
                //    normal path is that they press R and the wrap on
                //    PopupsManager.OnShardReadClosed sets cc_g01_shard_read.
                //
                //    THE AUTOMATIC READER IS A FALLBACK NOW, NOT THE ROUTE.
                //    It used to fire the instant cc_g01_shard_open arrived,
                //    which is what "reading on proximity" meant, and it would
                //    now snatch the beat out of the player's hands a second
                //    after they walked up to the desk.
                //
                //    THE INTENDED BEHAVIOUR, and this clock must not get in
                //    its way. [R] reads the shard where it lies and finishes
                //    the objective. [F] takes it, and "Read the shard" then
                //    STAYS UP until the player reads it out of the inventory,
                //    which raises the same reader and runs the same close
                //    callback.
                //
                //    So the clock is a last resort, not a nudge: 200 ticks,
                //    about five minutes of gameplay. At 40 it would have
                //    changed the objective while the player was still walking
                //    to their backpack, which is exactly the thing this beat
                //    was split in two to avoid. Ticks do not advance while a
                //    menu is open, so time spent in the inventory is free.
                //
                //    What it actually protects against is the shard being
                //    dropped or disassembled, which are both one click away
                //    and would otherwise leave nothing to read at all.
                //
                //    Raising it from the tick rather than from the quest graph
                //    is also what lets it be RETRIED: GetEntryByString returns
                //    null if the journal has not resolved our merged entry
                //    yet, and a quest node that fired into nothing would
                //    strand the gig here.
                //
                //    A player who reads the shard BEFORE the quest reaches
                //    cc_g01_shard_open is covered by the same fallback: the
                //    close wrap is gated on that fact so it will not have
                //    counted, and this raises our own reader once the quest
                //    catches up. CCG01Shard.Open needs no object, so it works
                //    whether or not the shard has already been taken.
                if qs.GetFactStr("cc_g01_shard_open") > 0
                    && qs.GetFactStr("cc_g01_shard_read") == 0
                    && !this.m_shardOpened {
                    this.m_shardGrace += 1;
                    if this.m_shardGrace > 200 {
                        this.m_shardOpened = CCG01Shard.Open(game);
                    }
                }

                // 2b. READ FROM ANYWHERE, and this is the one that carries the
                //     [F] case. Gig01_Shard's wrap on OnShardReadClosed only
                //     covers the reader raised at the container; playtest,
                //     2026-08-22, taking the shard and reading it out of the
                //     backpack did not complete the objective.
                //
                //     CCG01Shard.HasBeenRead asks the JOURNAL instead, which
                //     does not care where the reader came from.
                //
                //     TWO TICKS, AND THE DELAY IS DOING REAL WORK. The entry
                //     is marked visited when the popup OPENS, not when it
                //     closes. Ticks do not advance while a modal popup has the
                //     game paused, so counting two of them cannot happen until
                //     the player has actually shut the reader - which is the
                //     same trick the anti-stall below uses, and the reason V's
                //     next lines do not start underneath it.
                if qs.GetFactStr("cc_g01_shard_open") > 0
                    && qs.GetFactStr("cc_g01_shard_read") == 0
                    && CCG01Shard.HasBeenRead(game) {
                    this.m_shardVisited += 1;
                    if this.m_shardVisited > 1 {
                        qs.SetFactStr("cc_g01_shard_read", 1);
                    }
                }

                // 3. ANTI-STALL. Gig01_Shard's wrap on
                //    PopupsManager.OnShardReadClosed sets cc_g01_shard_read, and
                //    that is the intended path. If the popup is ever dismissed
                //    by a route that does not run that callback, the gig would
                //    sit forever on an objective the player has already done.
                //    The count is in TICKS, and ticks do not advance while a
                //    modal popup has the game paused, so this cannot fire while
                //    the player is still reading - 20 ticks is 30 s of gameplay
                //    with the shard already dismissed.
                if this.m_shardOpened && qs.GetFactStr("cc_g01_shard_read") == 0 {
                    this.m_shardTicks += 1;
                    if this.m_shardTicks > 20 {
                        qs.SetFactStr("cc_g01_shard_read", 1);
                    }
                }

                // The ledger goes to Nix, in the street, once he has agreed to
                // dig and asked who is paying. This is the handover the gig used
                // to do off-screen - see gen_scenes.build_nix_brief.
                // cc_g01_ledger_send IS SET FROM INSIDE THE CALL as of
                // 2026-09-03, by a fact node in gig01_nix_brief.scene right
                // after V says he is sending the files. It used to be
                // cc_g01_nixbrief_done, i.e. the call HANGING UP, so V
                // announced a transfer and then made it to nobody; the scene
                // now holds on cc_g01_ledger_sent (set by the last send beat
                // below) and Nix answers once it lands.
                if qs.GetFactStr("cc_g01_ledger_send") > 0
                    && qs.GetFactStr("cc_g01_ledger_sent") == 0
                    && !this.m_sendBusy {
                    this.m_sendBusy = true;
                    this.SendStep(0);
                }

                // ...AND THE FEE GOES OUT WHEN HIS FINDINGS LAND. The quest
                // phase sets cc_g01_pay_nix once the player has opened the
                // message thread and tapped the reply, so the money leaves
                // V's account as a thank-you rather than as a deposit.
                if qs.GetFactStr("cc_g01_pay_nix") > 0
                    && qs.GetFactStr("cc_g01_nix_paid") == 0 {
                    this.PayNix(player, qs);
                }

                // Arrive at the estate. Horizontal radius + altitude band, NOT a
                // 90 m sphere: the tunnelled road passes under the house and used
                // to count as arriving. The gate sits ~9 m lower than the house
                // and ~139 m away horizontally, so the two anchors are checked
                // separately rather than with one big radius.
                if qs.GetFactStr("cc_g01_nix_done") == 1 {
                    // THE OUTLINE COUNTS TOO. The two spheres are the signposted
                    // way in; InsideEstate is the twenty walked points, and it
                    // is what makes a player who came over the wall or in from
                    // the back get the same estate as one who drove to the gate.
                    // Same correction as the way-in objective got in 1.1.0, now
                    // applied to the guards.
                    // TWO SPHERES, THE SHAPE THE OFFICE ALREADY HAD.
                    //
                    // Arriving and spawning were one test here, at 45 m on the
                    // gate, so the squads began to arrive at the moment the
                    // player was close enough to watch them arrive. Field
                    // report, 1.2.3: *"as I move towards the gate I see it
                    // empty first, then they appear."*
                    //
                    // ARRIVING is the gate itself. This has been 45, then 20,
                    // and 25 is where two design calls meet.
                    //
                    // BACK TO 45, AND IT IS NOT THE SAME 45. It went 45, 20,
                    // 25, 35, 45 across one evening of playtests, which looks
                    // like indecision and is not: the thing it was measured
                    // against changed underneath it.
                    //
                    // The original 45 was condemned for flipping the objective
                    // "a car's length short of the gate". At that point arriving
                    // and spawning were ONE test, so 45 m was also where the
                    // squads began to appear, and what the report was really
                    // describing was the guards materialising at the same moment
                    // the objective changed. Splitting the two (spawning at
                    // 120 m, see below) fixed that, and each tightening after it
                    // was chasing a fault that had already been fixed. 20 put
                    // the fight before the side road on the right came into
                    // view; 25 and 35 were walked and driven and were still
                    // short of it.
                    //
                    // So the number is the same and the behaviour is not. The
                    // guards are in place long before V reaches this sphere.
                    //
                    // Not tighter than 20 in any case: the tick is 1.5 s and a
                    // car covers about 30 m in one, so a smaller sphere could be
                    // stepped over between two samples. The outline below is the
                    // backstop for that.
                    //
                    // THE HOSHINO SPHERE'S CEILING WENT 25 -> 60 for the same
                    // reason as the outline's above: 25 m over his floor stops
                    // short of the upper terraces, and this arm is the backstop
                    // for anybody the outline misses. Being within 70 m of the
                    // man is being at the estate whatever floor you are on.
                    let atEstate: Bool =
                        CCSharedWorld.Near(pos, CCGig01Places.EstateGate(), 45.0, 12.0, 25.0)
                        || CCSharedWorld.Near(pos, CCGig01Places.Hoshino(), 70.0, 12.0, 60.0)
                        || CCGig01Places.InsideEstate(pos);
                    //
                    // ONE STEP PER PASS, AND THE FLAG BELOW IS WHY.
                    //
                    // The quest phase waits on this fact, then raises the
                    // way-in objective, then waits on the NEXT fact. Both of
                    // those facts are satisfied by the same test, being inside
                    // the grounds, so a player who arrives by any route other
                    // than the gate sets both on this one pass. The second wait
                    // is armed a moment after the fact it is waiting for has
                    // already changed, and a fact that does not change again is
                    // a wait that never completes (gotchas.md 54).
                    //
                    // Driving to the gate hides it completely: the gate is
                    // OUTSIDE the traced outline, so arriving there cannot also
                    // mean being inside, and the two facts are a walk apart.
                    // That is the only route this has ever been tested on here,
                    // which is why it took two player reports to surface.
                    let justArrived: Bool = false;
                    if atEstate {
                        if qs.GetFactStr("cc_g01_estate_reached") == 0 {
                            qs.SetFactStr("cc_g01_estate_reached", 1);
                            justArrived = true;
                        }
                    }

                    // SPAWNING starts much further out, and 120 m is measured
                    // rather than picked. The North Oak fast travel point reads
                    // 116.5 m from the gate, and the design call is that a
                    // player landing there should already be inside the spawn
                    // sphere, so the estate fills while he walks to his car
                    // instead of while he looks at it. 120 m clears that
                    // landing by a few metres.
                    //
                    // The office pair is 100 against 60. This one is wider in
                    // both halves because the estate approach is a driveable
                    // hill rather than a walk through an industrial park.
                    //
                    // The altitude band is the same 12 below and 25 above the
                    // gate that the arrival test uses, and it is doing the same
                    // job: the tunnelled road passes under this hill, and a
                    // floor that reaches down to it would populate the estate
                    // for a player driving underneath who never comes up.
                    //
                    // AND IT STOPS ONCE V IS CLEAR OF THE ESTATE, for the reason
                    // given at the office spawn above: the per-anchor mask is a
                    // field and does not survive a reload, so without a fact in
                    // front of it a later drive past North Oak would repopulate
                    // an estate the player has already finished with.
                    //
                    // `cc_g01_escaped` is the estate's equivalent of
                    // `cc_g01_left_compound`: set once the upload is done and V
                    // is 160 m clear of Hoshino.
                    if qs.GetFactStr("cc_g01_escaped") == 0
                        && (atEstate
                            || CCSharedWorld.Near(pos, CCGig01Places.EstateGate(), 120.0, 12.0, 25.0)) {
                        this.AuditSite(true);
                    }

                    // Reaching the door into the house. playtest, 2026-08-12: the
                    // gig jumped straight from "get to the estate" to "find
                    // Hoshino", who is inside, with no hint how to get in - so
                    // the player stands outside a wall. This is his captured
                    // way-in point, pinned as its own objective.
                    //
                    // TWO WAYS TO SATISFY IT NOW, and the second is the fix for
                    // the 1.0.0 report. Touching the way-in point is the
                    // signposted route; BEING INSIDE THE COMPOUND, by whatever
                    // route, is what the objective actually means. A player who
                    // double-jumped the wall used to be stuck outside the
                    // objective while standing in the garden, and had to walk
                    // back out to the marker to clear it.
                    //
                    // 6 m on the point: generous enough that arriving at it
                    // counts, tight enough that it is not satisfied from the
                    // garden - and the boundary test covers the garden anyway.
                    //
                    // `!justArrived` holds this back to the NEXT pass when both
                    // conditions came true together. 1.5 s is far longer than
                    // the quest phase needs to walk four nodes and arm the wait,
                    // and on the gate route it changes nothing, because the two
                    // are already a walk apart.
                    let justFoundWayIn: Bool = false;
                    //
                    // AND A THIRD WAY: STANDING AT HOSHINO. Whatever route got
                    // somebody to the man, they are inside, and the objective
                    // telling them to find a way in is behind them.
                    //
                    // This is the arm that makes the ladder finish for a player
                    // who skipped everything: arriving sets `estate_reached` on
                    // one pass, this sets `wayin_reached` on the next, and the
                    // greeting fires on the one after that, so the phase walks
                    // its objectives in order at 1.5 s a step instead of parking
                    // on a wait that was armed after its fact had already changed
                    // (gotchas.md 54, which is what the one-step-per-pass rule
                    // above exists for).
                    if !justArrived
                        && qs.GetFactStr("cc_g01_estate_reached") > 0
                        && qs.GetFactStr("cc_g01_wayin_reached") == 0
                        && (CCSharedWorld.Near(pos, CCGig01Places.EstateWayIn(), 6.0, 4.0, 4.0)
                            || CCGig01Places.InsideEstate(pos)
                            || CCSharedWorld.Near(pos, CCGig01Places.Hoshino(),
                                                  25.0, 12.0, 60.0)) {
                        qs.SetFactStr("cc_g01_wayin_reached", 1);
                        justFoundWayIn = true;
                    }
                    this.m_estateStepTaken = justArrived || justFoundWayIn;

                    // ...and the route there, ONE MARKER AT A TIME.
                    //
                    // THE LEG IS A FACT, NOT A FIELD (docs/gotchas.md #21). A
                    // `let` on this system is gone after a reload, and the
                    // journal's pin states are not - so a remembered leg would
                    // come back as 0 against a journal already showing leg 5,
                    // and the first tick would drag the marker back down the
                    // hill. The fact and the journal are both in the save and
                    // stay in step.
                    //
                    // Evaluated FURTHEST FIRST and never allowed to go
                    // backwards. The tick is 1.5 s and the first three points
                    // are on a road, so a player in a car can cover a whole leg
                    // between two samples; taking the highest waypoint he
                    // qualifies for means a missed sample SKIPS a marker
                    // instead of stalling on one.
                    if qs.GetFactStr("cc_g01_estate_reached") > 0
                        && qs.GetFactStr("cc_g01_wayin_reached") == 0 {
                        // The pin the graph put up with the objective. An unset
                        // fact means exactly that.
                        let leg: Int32 = qs.GetFactStr("cc_g01_wayin_leg");
                        if leg < 1 {
                            leg = 1;
                        }
                        let want: Int32 = leg;
                        let k: Int32 = CCGig01Places.WayInLegs();
                        while k >= 1 {
                            if CCGig01Places.AtWayInPoint(pos, k) {
                                // Reaching waypoint k shows waypoint k+1. The
                                // last one has nothing after it - arriving
                                // there is the objective, handled above.
                                let next: Int32 = k + 1;
                                if next > CCGig01Places.WayInLegs() {
                                    next = CCGig01Places.WayInLegs();
                                }
                                if next > want {
                                    want = next;
                                }
                                break;
                            }
                            k -= 1;
                        }
                        if want != leg {
                            qs.SetFactStr("cc_g01_wayin_leg", want);
                        }
                        // m_wayinShown starts at 0, so this fires on the first
                        // tick of the window and again on the first tick after
                        // any reload - which is when the marker does not exist
                        // and has to be put back.
                        if this.m_wayinShown != want {
                            this.m_wayinShown = want;
                            this.ShowWayInMarker(want);
                        }
                    }
                }

                // Hoshino: make sure he is hostile, greet the player once, and
                // only call him dead after we have actually seen him alive - 
                // otherwise a streamed-out NPC (e.g. driving past) reads as a
                // corpse and skips half the mission.
                // KEEP LOOKING UNTIL THE COMMUNITY HAS PLACED HIM. The
                // quest phase activates the entry when the estate objective
                // goes up, and placement is asynchronous, so one look on the
                // frame the objective changed would find nothing and this beat
                // would wait for ever.
                if !this.m_hoshinoSpawned
                   && qs.GetFactStr("cc_g01_estate_reached") > 0 {
                    this.FindHoshino();
                }
                if this.m_hoshinoSpawned && qs.GetFactStr("cc_g01_hoshino_dead") == 0 {
                    // FindEntityByID, NOT DynamicEntitySystem.GetEntity.
                    //
                    // That system only knows entities IT spawned, and he is
                    // placed by a community now. The old call returned null for
                    // a body standing in plain sight, which would have read as
                    // "streamed out" and skipped half the mission.
                    let hoshino: ref<ScriptedPuppet> =
                        GameInstance.FindEntityByID(this.GetGameInstance(),
                                                    this.m_hoshinoId) as ScriptedPuppet;

                    if IsDefined(hoshino) && ScriptedPuppet.IsAlive(hoshino) {
                        this.m_hoshinoSeenAlive = true;
                        // THE SetAttitudeGroup(n"hostile") THAT WAS HERE IS
                        // GONE, AND IT HAD BEEN OVERRIDING A FIX FOR TEN DAYS.
                        //
                        // He is spawned neutral, deliberately: he opened fire
                        // during his own conversation (playtest, 2026-08-12) and
                        // the point of him is that he is an administrator rather
                        // than a soldier. See the comment by that spawn.
                        //
                        // This block predates that fix (`c9fd9a7`, 2026-08-11,
                        // against `eaf853e`, 2026-08-12) and is not gated on the
                        // estate, on the player's position or on being provoked,
                        // so it undid the neutral spawn about 1.5 s later, every
                        // session. Measured 2026-08-21: walk up to an untouched
                        // Hoshino standing at his desk and he reads Relaxed and
                        // HOSTILE.
                        //
                        // n"hostile" is a GROUP, not "hostile to the player", and
                        // a member of it is at war with every other group in the
                        // room including its own. CCShared_Attitude.reds carries
                        // the playtest that established this. It is why he leaves
                        // his desk and crosses the estate as a combatant: the
                        // same run measured him 96.2 m from where he starts.
                        //
                        // AND THE PAIRWISE LINE IS GONE TOO, ON THE NEXT
                        // READING. Removing only the group was not enough:
                        // playtest, 2026-08-21, he still crossed the estate and
                        // reached V at the gate. An NPC who holds V as an enemy
                        // engages V once he is aware of him, and a firefight
                        // around him is what makes him aware.
                        //
                        // Nothing here replaces it, because his record already
                        // does this job and does it better. `hoshino.yaml` sets
                        // `baseAttitudeGroup: neutral`, `reactionPreset:
                        // ReactionPresets.NoReaction` and `enableSensesOnStart:
                        // false`, and its own comment records why: "shooting him
                        // flips him hostile through the game's own damage
                        // reaction, so 'peaceful until attacked' needs no
                        // script". Every runtime attitude call this block has
                        // ever made was overriding three record fields that were
                        // set deliberately to say the same thing.
                        //
                        // So he stands at his desk and does not join a fight he
                        // is not part of. docs/backlog.md 22.
                        //
                        // WHAT DOES NOT COME FOR FREE IS HIM FIGHTING BACK, and
                        // `hoshino.yaml` has been wrong about that since it was
                        // written. Its comment says "shooting him flips him
                        // hostile through the game's own damage reaction, so
                        // 'peaceful until attacked' needs no script", and that
                        // was never tested with the runtime call removed,
                        // because the runtime call was always there overriding
                        // it. Playtest, 2026-08-21, with it gone: he takes the
                        // shot and does nothing at all.
                        //
                        // The reason is one of the three fields that make him
                        // peaceful. `reactionPreset: ReactionPresets.NoReaction`
                        // removes the damage reaction along with every other
                        // one, so there is nothing left to flip him.
                        //
                        // So the flip is scripted, once, on the first sign that
                        // he has been hit. Health is a percentage from the stat
                        // pool, so anything under full means damage: his own
                        // record cannot regenerate it, and nothing else here
                        // touches him.
                        //
                        // ONE-WAY AND ONCE. m_hoshinoProvoked is a field rather
                        // than a fact deliberately: it must not survive a reload,
                        // because he is respawned at full health by the same
                        // reload and a remembered flip would make him hostile
                        // before he had been touched, which is the bug this
                        // whole line of work started from.
                        let hostileNow: Bool = this.m_hoshinoProvoked;
                        if !hostileNow {
                            let hp: Float = GameInstance.GetStatPoolsSystem(game)
                                .GetStatPoolValue(Cast<StatsObjectID>(this.m_hoshinoId),
                                                  gamedataStatPoolType.Health, false);
                            // THREE WAYS IN, and the second is the one the
                            // story wants. He turns on V when the conversation
                            // ends, because the ledger is closed and he knows
                            // what V came for; being shot first is the other
                            // route to the same fight, for a player who never
                            // let him speak.
                            //
                            // cc_g01_hoshino_talked is set by the quest graph on
                            // the talked branch of the fork, after his last
                            // line. See gen_questphase.py, which carries why the
                            // 2026-08-14 attempt at this failed and why the same
                            // thing works now.
                            // `hp > 0.0` GUARDS A READING, NOT A STATE, and
                            // it is the fix for 2026-09-03: *"hoshino no
                            // longer attacks after V talks... he's killable
                            // but doesn't react"*.
                            //
                            // GetStatPoolValue on a body that is still
                            // resolving answers 0, which is indistinguishable
                            // from "shot to pieces" to a `< 99.0` test. On a
                            // tick where that happened he was marked provoked
                            // before anyone had touched him, TurnOnPlayer
                            // fired while the shield was still up, and the
                            // friendly attitude this block re-asserts every
                            // tick immediately overwrote it. After the
                            // conversation the shield lifts, so he becomes
                            // killable - and nothing ever makes him hostile
                            // again, because the flip below was a one-shot
                            // that had already been spent.
                            //
                            // A dead man reads 0 too, and this block does not
                            // run for one: the enclosing test is
                            // cc_g01_hoshino_dead == 0 and IsAlive().
                            hostileNow = (hp > 0.0 && hp < 99.0)
                                || qs.GetFactStr("cc_g01_hoshino_talked") > 0
                                || qs.GetFactStr("cc_g01_dbg_hoshino_fight") > 0;
                        }
                        // ------------------------------------ UNKILLABLE
                        //
                        // UNTIL HE HAS SAID HIS PIECE. The design call,
                        // 2026-08-21: a sniper shot or a quickhack from across
                        // the garden should not be able to delete the scene the
                        // whole leg is built around.
                        //
                        // `GodModeSystem` is the base game's own mechanism for a
                        // quest-critical NPC, and `Invulnerable` is the harder of
                        // its two settings: no damage at all, rather than damage
                        // that cannot finish him. Immortal was the other
                        // candidate and is wrong here, because health dropping is
                        // what the fight-back check reads, so it would produce an
                        // enemy who is hostile and cannot be killed.
                        //
                        // GIVING IT BACK IS THE PART THAT MATTERS, and it is
                        // written the way ReleaseMama is for the same reason: a
                        // shield left on is a Hoshino who can never die, which is
                        // a gig that can never finish. So the release is NOT a
                        // one-shot beside the flip. It is re-checked every tick
                        // against facts that are in the save, so a missed tick,
                        // a reload mid-scene or a skipped scene all still reach
                        // it on the next pass.
                        //
                        // docs/gotchas.md 21 is the rule being obeyed: a latch
                        // that is only ever set in the clean direction is one
                        // nobody tests in the dirty one.
                        // THE DEAD MAN'S HANDLE, and it is here for a save
                        // made before this shipped.
                        //
                        // `cc_g01_hoshino_talked` is set by a quest node added
                        // in 1.2.4. A player who loads a 1.2.3 save in which he
                        // has ALREADY been talked to is past that node forever:
                        // the fact can never arrive, and every condition below
                        // stays true for the rest of the save. He would respawn
                        // protected and stay protected, which is a gig that
                        // cannot be finished, from an upgrade rather than from
                        // anything the player did.
                        //
                        // So reaching him starts a clock. Two minutes with V
                        // stood in front of him and no scene having finished
                        // means the scene is not coming, and the shield is not
                        // worth a stuck save. A real conversation takes seconds;
                        // the only cost on a legacy save is that he is briefly
                        // unshootable on content that is already behind them.
                        //
                        // NOT PERSISTED, so a reload restarts the clock. That is
                        // correct: a reload also respawns him, and the question
                        // is being asked again from the start.
                        if qs.GetFactStr("cc_g01_hoshino_met") > 0
                            && qs.GetFactStr("cc_g01_hoshino_talked") == 0 {
                            this.m_hoshinoMetTicks += 1;
                        }
                        let wantShield: Bool = qs.GetFactStr("cc_g01_hoshino_talked") == 0
                            && qs.GetFactStr("cc_g01_hoshino_dead") == 0
                            && qs.GetFactStr("cc_g01_done") == 0
                            && this.m_hoshinoMetTicks < 80
                            && !hostileNow;
                        //
                        // AND THE RETICLE, WHICH IS A SEPARATE THING FROM THE
                        // DAMAGE. Playtest, 2026-08-21: *"other friendlies you
                        // cannot even target with the pistol. In this case it
                        // seems that he can be targeted, just doesn't suffer."*
                        //
                        // God mode decides whether damage lands and nothing
                        // else. On its own it produces the worst of the three
                        // states: the game locks on, draws a health bar, invites
                        // the shot, and then ignores it.
                        //
                        // `TargetingComponent.Toggle(false)` WAS TRIED HERE AND
                        // DOES NOT WORK. It compiles, the component resolves by
                        // name, and in play he is still targetable, still takes
                        // the shot and still plays the pain reaction. Removed
                        // rather than left in: a call with no effect is a thing
                        // someone later debugs for nothing. docs/backlog.md 22.
                        //
                        // WHAT DECIDES THE RETICLE IS THE ATTITUDE, which is the
                        // design call's own suggestion: *"spawn him as a friendly
                        // and then change its status completely after we speak."*
                        // A friendly NPC is the one the game will not let the
                        // player lock onto, and friendly is a state he can be put
                        // into and taken out of, unlike anything on his record.
                        //
                        // BOTH HALVES OF THE ATTITUDE, because they answer
                        // different questions. The GROUP is which side he is on,
                        // and it is what the reticle reads. The PAIRWISE value is
                        // what he thinks of V specifically. Setting only one has
                        // failed here twice in different directions.
                        //
                        // Being in the friendly group is safe for him in a way it
                        // would not be for the guards: he is an Arasaka
                        // administrator standing among Arasaka security, so a
                        // group that makes him their ally is what he already is.
                        // The warning in CCShared_Attitude.reds is about
                        // n"hostile", which puts an NPC at war with every other
                        // group including his own side.
                        let gods: ref<GodModeSystem> = GameInstance.GetGodModeSystem(game);
                        let shieldAgent: ref<AttitudeAgent> = hoshino.GetAttitudeAgent();
                        if wantShield {
                            // RE-ASSERTED EVERY TICK rather than once on the
                            // transition. An attitude set on an entity that is
                            // still resolving silently does nothing, which is the
                            // whole reason CCShared_Attitude retries, and one
                            // missed call here means a targetable Hoshino for the
                            // rest of the visit. It is two calls a second and a
                            // half.
                            if IsDefined(shieldAgent) && IsDefined(player.GetAttitudeAgent()) {
                                shieldAgent.SetAttitudeGroup(n"friendly");
                                shieldAgent.SetAttitudeTowards(player.GetAttitudeAgent(),
                                                               EAIAttitude.AIA_Friendly);
                            }
                        }
                        if IsDefined(gods) {
                            if wantShield && !this.m_hoshinoShielded {
                                gods.AddGodMode(this.m_hoshinoId,
                                                gameGodModeType.Invulnerable,
                                                n"cc_g01_hoshino");
                                this.m_hoshinoShielded = true;
                            }
                            if !wantShield && this.m_hoshinoShielded {
                                gods.RemoveGodMode(this.m_hoshinoId,
                                                   gameGodModeType.Invulnerable,
                                                   n"cc_g01_hoshino");
                                this.m_hoshinoShielded = false;
                            }
                        }

                        // RE-ASSERTED EVERY TICK, exactly like the friendly
                        // attitude above and for the same reason: an attitude
                        // set on an entity that is still resolving silently
                        // does nothing. It was a one-shot until 2026-09-03,
                        // which meant a single early or lost call left him
                        // permanently peaceful with no way back. Two calls a
                        // second on one NPC, and only while he is alive and
                        // the gig is at the estate.
                        if hostileNow {
                            this.m_hoshinoProvoked = true;
                            NegativeBalanceEncounter.TurnOnPlayer(hoshino, player);
                        }
                        // His exchange is a real scene now (gig01_hoshino.scene,
                        // run by the quest phase). All this does is say "V is
                        // in front of him"; the words and the choice of opening
                        // line live in the scene.
                        //
                        // MEASURED FROM THE MAN, NOT FROM HIS CAPTURED SPOT.
                        //
                        // This used to read Vector4.Distance(pos, Places.Hoshino()),
                        // the fixed point the marker is anchored to, so a Hoshino
                        // who had walked out of that sphere could not be greeted
                        // at all however close V stood to him, and the quest phase
                        // waits on this fact before playing his scene. The same
                        // 2026-08-21 run measured him 96.2 m from that point.
                        //
                        // Fixing where he goes is the other half and is above.
                        // This half holds even if some future beat moves him on
                        // purpose. docs/backlog.md 22.
                        //
                        // EIGHT METRES. This has been 12, then 4, and both
                        // ends were measured against the wrong thing.
                        //
                        // 12 looked too far, but the run that produced that
                        // reading had Hoshino walking to the gate, so what fired
                        // early was his POSITION and not the radius. 4 was the
                        // correction and it is too tight to be comfortable: the
                        // design call, 2026-08-21, is that V has to stand in his
                        // face for it.
                        //
                        // 8 is a room's width rather than a courtyard's, and it
                        // is measured from the man, so the reading that condemned
                        // 12 does not apply to it. Now that he stays at his desk
                        // this is the first honest test of the radius on its own.
                        //
                        // Missing it does not strand the gig. Killing him sets
                        // cc_g01_hoshino_met itself, in the branch below, so the
                        // quest phase moves on; what is lost is the scene.
                        //
                        // `m_estateStepTaken` is the same one-step-per-pass rule
                        // as the two facts above, for the same reason: the wait
                        // on cc_g01_hoshino_met is armed straight after the
                        // way-in wait completes, and a player who lands next to
                        // Hoshino can satisfy both on one pass.
                        // AND ON HIS OWN FLOOR, which the radius alone cannot
                        // say. Reported 2026-08-25: standing on the floor BELOW
                        // him started his conversation, with V nowhere near him
                        // and unable to see him.
                        //
                        // `Vector4.Distance` is 3D, so a player one floor down
                        // is inside an 8 m sphere with room to spare. The estate
                        // is stacked at 4 m intervals, read off the captured
                        // posts: the grounds at 220.9, the office level at
                        // 225.9, HIS floor at 229.9, and the roof at 233.9. Two
                        // of those sit within 8 m of him vertically.
                        //
                        // So the test is horizontal with an altitude band, which
                        // is what `Near` is for and what the estate region test
                        // above already uses. 2.0 m below and 2.0 m above his
                        // own floor: a player standing in front of him is 0 to
                        // 0.5 m down, because his spot is at floor height and
                        // the sitting animation lifts him onto the cushion, and
                        // the floors above and below are excluded with 1.5 m to
                        // spare at the roof and 2.0 m at the floor below.
                        //
                        // Above is deliberately as generous as below rather than
                        // tighter: standing on a step or a piece of furniture on
                        // his own floor should still count, and the roof is far
                        // enough away that it costs nothing.
                        if !this.m_estateStepTaken
                            && !this.m_hoshinoGreeted
                            && CCSharedWorld.Near(pos, hoshino.GetWorldPosition(),
                                                  8.0, 2.0, 2.0) {
                            this.m_hoshinoGreeted = true;
                            qs.SetFactStr("cc_g01_hoshino_met", 1);
                        }

                    } else {
                        // IsDefined, NOT DynamicEntitySystem.IsSpawned: he is
                        // community-placed now and that system never knew him.
                        // The entity survives death as a corpse, which is what
                        // makes this the right test: it separates "he is dead"
                        // from "he streamed out", which is the distinction this
                        // whole branch exists for.
                        if this.m_hoshinoSeenAlive
                            && IsDefined(GameInstance.FindEntityByID(
                                this.GetGameInstance(), this.m_hoshinoId))
                            && Vector4.Distance(pos, CCGig01Places.Hoshino()) < 120.0 {
                            // Anti-stall: the quest phase waits on
                            // cc_g01_hoshino_met before the scene, so a kill
                            // from across the garden must still set it or the
                            // graph sits forever on a conversation that can no
                            // longer happen.
                            //
                            // DEAD IS WRITTEN FIRST, AND THE ORDER IS THE WHOLE
                            // POINT. It used to be the other way round, and the
                            // scene played anyway: a corpse delivered "Mmm? You
                            // lost, merc?" (playtest, 2026-08-15). The graph now
                            // forks on cc_g01_hoshino_dead the instant
                            // cc_g01_hoshino_met releases its pause, so if `met`
                            // landed first there is a window - however small -
                            // in which the fork reads a dead Hoshino as alive
                            // and enters the conversation regardless.
                            //
                            // Setting the ANSWER before the QUESTION is the same
                            // rule as cc_g01_mama_present, which is written
                            // before cc_g01_mama_reached for exactly this
                            // reason. docs/gotchas.md #17: ask what sets the
                            // gate, and whether it runs before or after.
                            qs.SetFactStr("cc_g01_hoshino_dead", 1);
                            qs.SetFactStr("cc_g01_hoshino_met", 1);
                            // "Ledger's closed." is gig01_kill.scene now, and
                            // the quest phase plays it off the fact just set.
                        }
                    }
                }

                // Johnny over the body (comic p45) used to be spawned here and
                // spoken 5 s later, the delay hand-tuned so V's own kill line's
                // subtitle HIDE would not wipe it - all our captions shared one
                // CRUID and therefore one widget. gig01_kill.scene carries both
                // lines now and sections cannot collide, so the whole dance is
                // gone along with cc_g01_johnny_hoshino.

                // Estate terminal: upload the malware (after Hoshino is down).
                //
                // Proximity is no longer enough, V has to actually plug in
                // (playtest, 2026-08-12). Walking past a terminal and having a
                // netrunner intrusion start by itself reads as the gig playing
                // itself; the upload is a deliberate act and should need one.
                //
                // Radius went 2.0 -> 3.0 at the same time. It is now a
                // precondition rather than the trigger, and the spot V stands on
                // to use a device is not necessarily the captured coordinate.
                if qs.GetFactStr("cc_g01_hoshino_dead") == 1
                    && qs.GetFactStr("cc_g01_malware_done") == 0
                    && !this.m_uploadBusy
                    && Vector4.Distance(pos, CCGig01Places.EstateTerminal()) < 3.0
                    && CCSharedWorld.IsUsingDevice(this.GetGameInstance(), player) {
                    this.m_uploadBusy = true;
                    this.UploadStep(0);
                }

                // ...and the p51 exchange, once V is OFF the terminal.
                //
                // Same signal and same reason as the office beat: IsUsingDevice
                // going false is the reliable "off the screen" test, and staging
                // an actor on a player locked in a device zoom is what
                // soft-locked the office once. The quest phase waits on this
                // fact before entering gig01_malware.scene, so the scene can
                // never start under the zoom.
                if qs.GetFactStr("cc_g01_malware_done") > 0
                    && qs.GetFactStr("cc_g01_malware_talk") == 0
                    && !CCSharedWorld.IsUsingDevice(this.GetGameInstance(), player) {
                    qs.SetFactStr("cc_g01_malware_talk", 1);
                }

                // Nix only calls once V is clear of the compound, reading a
                // ledger in a guarded building is no time for a conversation.
                //
                // Measured from the TERMINAL, not the compound entry. The
                // terminal is ~63.5 m inside the entry, so an entry-anchored
                // radius has to clear that before it can mean anything, which is
                // why this used to be 150 m and felt like a hike. From the
                // terminal, 110 m is roughly 46 m past the entry: a short walk
                // out, and it still cannot fire anywhere inside the building.
                if qs.GetFactStr("cc_g01_terminal_done") > 0
                    && qs.GetFactStr("cc_g01_left_compound") == 0
                    && Vector4.Distance(pos, CCGig01Places.OfficeTerminal()) > 110.0 {
                    qs.SetFactStr("cc_g01_left_compound", 1);
                }

                // Escape: clear of the estate grounds after the upload. Measured
                // from Hoshino, and the gate is ~139 m from him, so this has to
                // clear that to mean "past the gate", 160 m is ~21 m beyond it.
                // 250 m was simply a long walk for no reason. No combat condition.
                if qs.GetFactStr("cc_g01_malware_done") == 1
                    && qs.GetFactStr("cc_g01_escaped") == 0
                    && Vector4.Distance(pos, CCGig01Places.Hoshino()) > 160.0 {
                    qs.SetFactStr("cc_g01_escaped", 1);
                }

                // ARRIVING at El Coyote, which is a different thing from reaching
                // Mama. cc_g01_at_coyote used to do both jobs, so "Talk to Mama
                // Welles" only appeared once V was already standing in front of
                // her and the conversation started in the same breath - the
                // objective flashed past unread (playtest, 2026-08-12).
                //
                // 15 m off the bar marker is inside the pub without being the
                // street. The objective changes as V walks in, which is when it
                // is useful.
                if qs.GetFactStr("cc_g01_escaped") == 1
                    && qs.GetFactStr("cc_g01_at_coyote") == 0
                    && CCSharedWorld.Near(pos, CCGig01Places.Coyote(), 15.0, 5.0, 5.0) {
                    qs.SetFactStr("cc_g01_at_coyote", 1);
                }

                // ---------------------------------------------- HER SMALL TALK
                //
                // `mama_is_talking` IS VANILLA'S OWN GATE, not a lever we
                // invented. Read off the shipped file on 2026-08-15:
                // base\quest\tertiary_characters\default_dialogues\
                // mama_welles_default.scene holds a pause node whose condition
                // is "player is close AND mama_is_talking < 1", and NOTHING in
                // that scene ever sets the fact. It is set from outside, by
                // whatever story content currently owns her - which is
                // what we are while the epilogue runs.
                //
                // This is what §3e could not find in August. `InteractionSet-
                // EnableEvent` failed because her chit-chat is not an
                // interaction prompt, it is a scene, and a scene is stopped by
                // its own entry condition. Blocking the scene takes BOTH things
                // Playtest report: the greeting she says on sight, and the "I'll
                // have a drink" / "What's happening in the area?" buttons, which
                // are that scene's choice hub.
                //
                // HOLDING IT IS THE DANGEROUS PART, so the hold is bounded three
                // ways. A fact left at 1 would leave a base-game character mute
                // for the rest of the save - the exact risk that got
                // SetInteractions deleted - and this one would do it silently.
                //   * only after V reaches El Coyote,
                //   * only until the epilogue conversation is done,
                //   * and only while he is actually NEAR the bar. Wander off and
                //     it is released; come back and it is set again. So even a
                //     gig abandoned forever costs her nothing once V leaves.
                // Every other path through this file releases it, below.
                // THE WINDOW OPENS EARLY, WHICH IS THE FIX FOR THE PACING
                // BUG. playtest, 2026-08-15: *"if I approach her slower, the
                // default options disappear, but at standard pacing, they are
                // still there at the beginning."*
                //
                // That sentence is a stopwatch. It says the switch works and
                // arrives LATE - so the only question is how much runway it has.
                // It used to open on cc_g01_at_coyote, which fires 15 m from the
                // bar marker, and this system ticks every 1.5 s. A player
                // walking in at normal speed covers that in two or three ticks,
                // and her greeting fires the moment he is inside her own
                // trigger radius. Approach slowly and we win the race; approach
                // normally and we lose it by a tick.
                //
                // So stop racing. The window now opens on cc_g01_escaped - V is
                // clear of the estate and the epilogue is the next beat - with a
                // generous 200 m around the bar, which he crosses long before he
                // is anywhere near her. There is no cost to being early: the
                // only thing being held off is her small talk, and every bound
                // that made this safe is unchanged - it still closes on
                // cc_g01_mama_talked, still releases the moment he leaves the
                // area, and still only ever clears a 1 it wrote itself.
                let holdMama: Bool = qs.GetFactStr("cc_g01_escaped") > 0
                    && qs.GetFactStr("cc_g01_mama_talked") == 0
                    && Vector4.Distance(pos, CCGig01Places.Coyote()) < 200.0;
                // ONLY EVER CLEAR WHAT WE SET. m_mamaHeld is the receipt.
                // The fact belongs to the base game and other content sets it
                // for its own reasons; clearing it because our window happens to
                // be shut would switch her small talk back on in the middle of
                // somebody else's scene. Writing a shared flag without asking
                // who else writes it is docs/gotchas.md #15, and this is the
                // first shared flag in this gig that is not ours at all.
                if holdMama {
                    if qs.GetFactStr("mama_is_talking") <= 0 {
                        qs.SetFactStr("mama_is_talking", 1);
                        this.m_mamaHeld = true;
                    }
                    // "LOOK WHO IT IS" IS A BARK, NOT THE DIALOGUE SCENE, which
                    // is why blocking the scene left it standing. It comes from
                    // base\quest\tertiary_characters\vsets\vset_mama_welles
                    // .scene, whose entry points are literally `greeting`,
                    // `greeting_var_1`, `greeting_var_2` - and that file carries
                    // NO fact conditions at all, so there is nothing to gate.
                    //
                    // It is switched off at the entity instead.
                    // entChangeVoicesetStateEvent is the engine's own switch and
                    // vanilla drives the same fields from the quest graph
                    // (questChangeVoicesetState_NodeType, same three params), so
                    // this is the intended mechanism rather than a trick.
                    //
                    // LINES ONLY. Grunts stay on - they are effort and pain
                    // sounds, nothing to do with greeting the player, and the
                    // less of a base-game NPC we switch off the better.
                    // MUTE THE MOMENT SHE EXISTS, AND AGAIN IF SHE COMES BACK.
                    //
                    // The latch is dropped whenever she cannot be found, which
                    // is not the same as "she is gone for good" - the query
                    // reaches 60 m and the window now opens at 200, so for the
                    // whole walk in she simply is not there yet. Dropping it
                    // means the FIRST tick that can see her mutes her, and a
                    // Mama who streams out and back gets muted again rather than
                    // greeting V with a stale latch saying we had handled it.
                    let mamaVo: ref<GameObject> = this.FindMamaWelles(player);
                    if IsDefined(mamaVo) {
                        if !this.m_mamaMuted {
                            CCSharedWorld.SetVoiceset(mamaVo, false);
                            this.m_mamaMuted = true;
                        }
                    } else {
                        this.m_mamaMuted = false;
                    }
                } else {
                    this.ReleaseMama(qs, player);
                }

                // Epilogue. Walk up to Mama Welles, the real one if she is in
                // the bar, our stand-in only if she is not.
                if qs.GetFactStr("cc_g01_escaped") == 1
                    && qs.GetFactStr("cc_g01_mama_reached") == 0
                    && !this.m_epilogueBusy
                    && Vector4.Distance(pos, CCGig01Places.Coyote()) < 60.0 {

                    // One query finds either of them: our stand-in carries the
                    // same record as the base-game NPC.
                    let mama: ref<GameObject> = this.FindMamaWelles(player);

                    if IsDefined(mama) {
                        this.m_mamaMissingTicks = 0;
                        // Trigger on HER, wherever she actually is, so this can
                        // never fire from the street and does not care whether
                        // she wandered off her mark.
                        if Vector4.Distance(pos, mama.GetWorldPosition()) < 3.5 {
                            this.m_epilogueBusy = true;
                            // FOUND HER, AND SHE CAN ONLY BE THE REAL ONE NOW.
                            // The query matches on the record, and until
                            // 2026-08-18 our own stand-in carried the same one,
                            // so "found" did not settle which. Nothing of ours
                            // wears that record any more.
                            //
                            //   1  the base-game Mama is in the bar. The quest
                            //      phase plays gig01_epilogue, which ACQUIRES
                            //      her - and acquiring her is what shuts her
                            //      ordinary bar conversation up. That was the
                            //      1.0.0 bug: our scene spawned a copy under the
                            //      floor and never claimed her, so her chit-chat
                            //      could win the approach (backlog 7d).
                            //   2  she is not, and the phase skips the epilogue.
                            //      Written below, not here.
                            //
                            // GETTING THIS WRONG IS NOT COSMETIC. gig01_epilogue
                            // spawns nobody; entering it with no base-game Mama
                            // to acquire leaves the scene holding an actor that
                            // never resolved, which is what crashed the
                            // game at scene teardown in August. That is why the
                            // fact survived the simplification that deleted the
                            // stand-in it used to choose.
                            //
                            // Set BEFORE cc_g01_mama_reached: that fact releases
                            // the phase into the fork, and the fork reads this
                            // one.
                            qs.SetFactStr("cc_g01_mama_present", 1);
                            qs.SetFactStr("cc_g01_mama_reached", 1);
                        }
                    } else {
                        // Only conclude she is absent after a good many misses.
                        // Right after stepping inside the interior NPCs may not
                        // have streamed in yet, and this branch now costs the
                        // player a conversation rather than swapping in a
                        // stand-in, so it is worth being slow about. Measured
                        // against her own spot, not the bar marker, which sits
                        // ~10 m away from it.
                        //
                        // 30 ticks at 1.5 s is about 45 s of standing in the bar
                        // with no Mama Welles in range. The count used to spawn
                        // our own copy of her at tick 4 and fall back here at
                        // 30; there is nothing to spawn now, so 30 is the only
                        // threshold left.
                        if Vector4.Distance(pos, CCGig01Places.MamaWelles()) < 15.0 {
                            this.m_mamaMissingTicks += 1;
                            // LAST RESORT, AND IT SHOULD BE UNREACHABLE. The gig
                            // does not start until sq018 has succeeded, and that
                            // is the quest that puts her in the bar. If it fires
                            // anyway, 2 tells the quest phase to skip the
                            // epilogue and send V to the counter: an ending
                            // missing one conversation, rather than a scene
                            // waiting forever for an actor that cannot arrive
                            // and taking the ending with it.
                            if this.m_mamaMissingTicks >= 30 {
                                this.m_epilogueBusy = true;
                                qs.SetFactStr("cc_g01_mama_present", 2);
                                qs.SetFactStr("cc_g01_mama_reached", 1);
                            }
                        }
                    }
                }
            }

            // JOHNNY IS PLACED BY HIS SCENE, not from here. Each beat's
            // scene stages him in front of V and facing V, using the
            // measured properties of an `around_player` marker: it sits on
            // the player and carries the player's rotation. See
            // tools/gig01/gen_scenes.py BEAT_STAGING and docs/backlog.md 9.
            //
            // The seven staging windows and the whole lift that used to
            // live here are gone. A scene-placed actor arrives already
            // posed, so there is nothing to find, lift, retry or glitch.

            // Johnny gets the last word, and it is the last word that ends the
            // gig. He is not an actor in the epilogue scene - his character
            // record id is not discoverable offline and guessing TweakDBIDs is
            // how this project broke itself before - so his line stays on the
            // subtitle route and fires when the scene has finished.
            // Johnny's closing line moved INTO gig01_epilogue.scene, where he is
            // a present actor rather than an ownerless subtitle, so there is
            // nothing to play here any more - only the fact that closes the gig.
            //
            // THIS ALSO CARRIES THE SKIP. `cc_g01_epilogue_scene_done` is set by
            // the quest graph on both branches of the Mama fork, the played one
            // and the skipped one, so an epilogue that never ran still reaches
            // the bar. See gen_questphase.py at the fan-in.
            if qs.GetFactStr("cc_g01_epilogue_scene_done") > 0
                && qs.GetFactStr("cc_g01_mama_talked") == 0 {
                qs.SetFactStr("cc_g01_mama_talked", 1);
            }

            // THE ENDING. V's last line to Mama is "Nova. I'll get a drink." - so
            // the gig gives him an objective to go and get one, and Johnny is
            // waiting at the counter for the comic's final exchange.
            //
            // The BAR STOOLS, not Coyote() - that constant is the base game's bar
            // marker and it sits at the pub's exit. 2 m, deliberately tight: the
            // stools are only ~4 m from where Mama stands, so anything looser
            // completes the objective before V has taken a step.
            //
            // THE ENDING MUST ALWAYS BE REACHABLE. This is the third shape of
            // this trigger and the previous one STRANDED THE GIG: it deferred
            // while a choice hub was on screen, so Johnny never appeared and the
            // quest never closed (playtest, trace ends at cc_g01_mama_talked with
            // no cc_g01_bar_reached).
            //
            // The deferral is gone. It was solving a presentation problem - his
            // lines competing with the bar's drink menu - and it solved it by
            // risking the one thing that must never fail. A busy screen is worse
            // than nothing only until you compare it with an unfinishable gig.
            //
            // Two ways in now, and the second cannot fail:
            //   * 4.0 m of the stools. Still inside the 4.05 m to where Mama
            //     stands, so it cannot fire on the spot the epilogue just played.
            //   * ANYWHERE in the bar, ~45 s after the conversation ends. If the
            //     stool spot is somehow unreachable - a different stretch of
            //     counter, furniture in the way - the gig still closes.
            if qs.GetFactStr("cc_g01_mama_talked") > 0
                && qs.GetFactStr("cc_g01_bar_reached") == 0 {
                this.m_barWaited += 1;
            }
            if qs.GetFactStr("cc_g01_mama_talked") > 0
                && qs.GetFactStr("cc_g01_bar_reached") == 0
                && (CCSharedWorld.Near(pos, CCGig01Places.BarStools(), 4.0, 3.0, 3.0)
                    || (this.m_barWaited > 30
                        && CCSharedWorld.Near(pos, CCGig01Places.Coyote(), 15.0, 5.0, 5.0))) {
                // The fact is now ALL this does. The quest phase waits on it and
                // plays gig01_bar.scene, which brings its own Johnny (a scene
                // actor standing at the counter, so his line has a speaker close
                // enough to be HEARD - a world line plays from the speaker's
                // position, which is why the caption route could never be
                // voiced). No SpawnJohnny here any more: two Johnnys at the bar
                // is the one way this beat could look worse than it did.
                qs.SetFactStr("cc_g01_bar_reached", 1);
            }

            // THE SKIM, the moment the malware is in. Same fact the quest
            // phase completes the upload objective on, so the money and the
            // objective land together.
            if qs.GetFactStr("cc_g01_malware_done") > 0
                && qs.GetFactStr("cc_g01_skimmed") <= 0 {
                this.GiveSkim(player, qs);
            }

            // Outside the guard above, which only runs while the gig is open:
            // the quest phase sets cc_g01_done as the epilogue objective closes.
            if qs.GetFactStr("cc_g01_done") > 0 && qs.GetFactStr("cc_g01_rewarded") <= 0 {
                this.GiveReward(player, qs);
            }

            // A FINISHED GIG COSTS THE SAVE NOTHING. Nothing in this file used
            // to check cc_g01_done, so this tick kept rescheduling itself every
            // 1.5 s for the rest of the playthrough, running proximity maths
            // against places V has already left. NegativeBalanceStart's
            // m_settled latch is the model.
            //
            // THE CONDITIONS ARE THE POINT, not the fact on its own. Everything
            // this system takes from the world is given back higher up the same
            // tick - Mama's voiceset and `mama_is_talking`, the way-in mappin,
            // our stand-in - and stopping before those had run would latch each
            // one on for the rest of the save, which is the exact class of bug
            // this stop is meant to end. So the receipts are read here rather
            // than assumed, and the reward is one of them: the tick has to
            // survive long enough to pay it.
            //
            // In practice all of them are clear on the first tick after
            // cc_g01_done, so this is one extra pass and then silence.
            //
            // Not persistent, and it does not need to be: OnAttach schedules
            // again on the next load, one tick re-checks and stops. Clearing
            // cc_g01_done from the dev menu does not restart the tick within a
            // session - reload.
            if qs.GetFactStr("cc_g01_done") > 0
                && qs.GetFactStr("cc_g01_rewarded") > 0
                && !this.m_mamaHeld
                && !this.m_mamaMuted
                && !this.m_wayinMappinUp {
                stop = true;
            }
        }
        if !stop {
            this.Schedule(1.5);
        }
    }
}

public class CCGig01EncounterTick extends DelayCallback {
    public let system: wref<NegativeBalanceEncounter>;
    public func Call() -> Void {
        if IsDefined(this.system) { this.system.Tick(); }
    }
}



// CCGig01JohnnyProbe / CCGig01JohnnyDissolve / CCGig01JohnnyWorkspotProbe /
// CCGig01JohnnyLeave were here, driving the script-owned Johnny. Deleted
// 2026-08-14 with the path they served - see the note above SpawnJohnny's
// former home.

// CCGig01MakeNeutral, CCGig01MakeHostile and CCGig01UploadBarStep were here.
// Their work moved into shared/scripts (CCShared_Attitude, CCShared_Hud), and
// those modules carry their own callbacks, so a gig never sees them.

public class CCGig01SendStep extends DelayCallback {
    public let system: wref<NegativeBalanceEncounter>;
    public let step: Int32;
    public func Call() -> Void {
        if IsDefined(this.system) { this.system.SendStep(this.step); }
    }
}

public class CCGig01DownloadStep extends DelayCallback {
    public let system: wref<NegativeBalanceEncounter>;
    public let step: Int32;
    public func Call() -> Void {
        if IsDefined(this.system) { this.system.DownloadStep(this.step); }
    }
}

public class CCGig01UploadStep extends DelayCallback {
    public let system: wref<NegativeBalanceEncounter>;
    public let step: Int32;
    public func Call() -> Void {
        if IsDefined(this.system) { this.system.UploadStep(this.step); }
    }
}
