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

public struct CCSpawnPoint {
    public let record: TweakDBID;
    public let pos: Vector4;
    public let yaw: Float;
}

public abstract class CCGig01Places {
    // --- Arasaka Industrial Park (Arroyo) ---
    public static func CompoundEntry() -> Vector4 { return new Vector4(-189.371, -1464.500, 7.596, 1.0); }
    public static func InnerEntry() -> Vector4 { return new Vector4(-219.737, -1424.075, 14.604, 1.0); }
    public static func OfficeEntry() -> Vector4 { return new Vector4(-241.498, -1449.012, 14.600, 1.0); }
    public static func TerminalRoomEntry() -> Vector4 { return new Vector4(-255.481, -1451.869, 14.600, 1.0); }
    public static func OfficeTerminal() -> Vector4 { return new Vector4(-251.915, -1456.364, 14.600, 1.0); }
    public static func OfficeGuardPost() -> Vector4 { return new Vector4(-245.680, -1452.315, 14.600, 1.0); }

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
    // contains every anchor this gig uses here: all five doors, all five guard
    // posts, the terminal, the shard and the map pin.
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
    public static func EstateApproach() -> Vector4 { return new Vector4(373.462, 1139.073, 220.932, 1.0); }
    public static func EstateGrounds() -> Vector4 { return new Vector4(321.122, 1077.105, 225.933, 1.0); }
    public static func EstateGarden() -> Vector4 { return new Vector4(340.924, 1033.924, 225.956, 1.0); }
    public static func EstateSideEntry() -> Vector4 { return new Vector4(312.434, 1042.762, 229.939, 1.0); }
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
        if pos.Z < 213.7 || pos.Z > 235.9 {
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

    // WHICH ANCHORS AT EACH SITE HAVE BEEN POPULATED, one bit per squad.
    //
    // A single "the site is done" Bool is what made the estate half-empty when
    // approached from behind, and the explanation is worth keeping: Hoshino is
    // placed straight at his captured position, while every GUARD has to pass
    // FindPointInSphereOnlyHumanNavmesh first. That query only answers where
    // the navmesh is streamed in. Come over the back wall and the gate, the
    // approach and the grounds are far away and unstreamed, so those squads
    // were dropped - and the site latched anyway on the two that did land.
    //
    // Per anchor, so an anchor that failed is asked again as the player moves
    // and its sector streams in. An anchor is only ever populated once, so
    // clearing a compound and standing in it cannot spawn a second wave.
    //
    // A mask rather than an array: redscript arrays on a ScriptableSystem come
    // back from an old save at the wrong length, which is the trap written up
    // at the top of Gig01_Holocall. An Int32 cannot be the wrong length. Bit()
    // is a table because redscript has no `<<` (it has `&` and `|`).
    private let m_officeMask: Int32;
    private let m_estateMask: Int32;
    // A staggered spawn chain is running for that site. Separate from the mask
    // because the chain takes seconds and the tick is 1.5 s, so without this a
    // second chain would start on top of the first.
    private let m_officeBusy: Bool;
    private let m_estateBusy: Bool;
    // Ticks until the next audit of the site's unpopulated anchors. Starts at
    // 0, so the first tick inside the region acts immediately.
    private let m_officeAudit: Int32;
    private let m_estateAudit: Int32;
    // Squad attempts made at this site this session. Bounded: an anchor whose
    // navmesh never answers is one we cannot populate, and asking every six
    // seconds for the rest of the visit buys nothing.
    private let m_officeTries: Int32;
    private let m_estateTries: Int32;
    private let m_hoshinoId: EntityID;
    private let m_hoshinoSpawned: Bool;
    private let m_hoshinoSeenAlive: Bool;   // only then can we call him dead
    private let m_hoshinoGreeted: Bool;
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

    // ---------------------------------------------------------------- spawning
    // Scatters a squad around a point so it reads as a patrol, not a lineup.
    //
    // RETURNS HOW MANY WERE ACTUALLY PLACED, and the caller has to read it.
    //
    // Every guard below is dropped when the navmesh query fails, which is
    // correct on its own. What was wrong is that nothing counted: the latch
    // saying the site was populated was set BEFORE any of this ran, so a
    // navmesh that was not ready yet binned all twenty guards and the gig
    // recorded the job as done. The player then walks into an empty compound
    // and there is no second chance for the rest of the save. This is the same
    // shape as docs/gotchas.md #21: a latch set on intent rather than on
    // outcome.
    private func SpawnSquad(center: Vector4, count: Int32, tag: CName, estate: Bool) -> Int32 {
        let records: array<TweakDBID>;
        if estate {
            records = [
                t"Character.nok_security_security2_ranged2_ajax_wa",
                t"Character.arasaka_agent_fshotgun2_tactician_wa_rare",
                t"Character.arasaka_ranger1_ranged2_shingen_ma",
                t"Character.nok_arasaka_fast_sniper_long_range_m_medium",
                t"Character.arasaka_netrunner_netrunner2_yukimura_ma_rare"
            ];
        } else {
            records = [
                t"Character.sts_std_arr_12_security_guard1_ranged1_nue_ma",
                t"Character.sts_std_arr_10_security_shotgun_mb",
                t"Character.arasaka_guard2_melee1_baton_wa",
                t"Character.arr_arasaka_ranger1_melee2_knife_ma",
                t"Character.arasaka_2020guard_ranged1_2020nue_ma"
            ];
        }

        // EVERY SPAWN POINT IS SNAPPED TO WALKABLE GROUND.
        //
        // playtest, 2026-08-13: "there are 2 guards inside a wall and one outside
        // on a ledge that is impossible to reach." Both are the same bug - the
        // scatter was pure trigonometry around a captured point, so a guard
        // landed wherever the circle happened to fall, geometry or no geometry.
        // A guard inside a wall cannot be fought and a guard on an unreachable
        // ledge cannot be finished, so both stall a room the player is supposed
        // to clear.
        //
        // NavigationSystem.FindPointInSphereOnlyHumanNavmesh answers exactly the
        // right question - "give me a point near here that a human can stand on"
        // - and it is what vanilla's own GetNearestNavmeshPointBelow is built
        // from (navigationSystem.swift:29). Ask it for a point within 2 m of the
        // scattered spot: if it says OK we use ITS point, and if it says
        // anything else we DROP that guard rather than place him in a wall.
        //
        // A squad is allowed to come out one or two short. Five guards in a room
        // that can all be fought is a better encounter than seven where two are
        // furniture.
        let nav: ref<NavigationSystem> = GameInstance.GetNavigationSystem(this.GetGameInstance());
        let placed: Int32 = 0;
        let i: Int32 = 0;
        while i < count {
            let angle: Float = Cast<Float>(i) * 2.4;
            // Tighter than the old 2.5-6.5 m: the office rooms are small, and
            // most of the wall cases were the outer ring reaching through one.
            let radius: Float = 1.8 + Cast<Float>(i % 3) * 1.4;
            let pos: Vector4 = new Vector4(
                center.X + CosF(angle) * radius,
                center.Y + SinF(angle) * radius,
                center.Z,
                1.0);
            // `walkable` rather than an early `continue`: REDSCRIPT HAS NO
            // `continue`. It compiles as far as "unresolved reference", which
            // reads like a missing function rather than a missing keyword.
            let walkable: Bool = true;
            if IsDefined(nav) {
                let found: NavigationFindPointResult =
                    nav.FindPointInSphereOnlyHumanNavmesh(pos, 2.0, NavGenAgentSize.Human, true);
                if Equals(found.status, worldNavigationRequestStatus.OK) {
                    pos = found.point;
                } else {
                    walkable = false;
                }
            }
            if walkable {
                let id: EntityID = CCSharedWorld.Spawn(records[i % ArraySize(records)], pos, angle * 57.3, tag);
                // COMPOUND GUARDS ONLY. playtest, 2026-08-13: inside the Arasaka
                // compound he could walk among the guards and they never challenged
                // him, while the estate detail behaves correctly.
                //
                // Both squads take the identical spawn path and nothing here ever
                // set an attitude, so each guard inherited whatever his record
                // defaults to - and the two record lists are the only difference.
                // The compound list is mostly `sts_*`, i.e. street-story security
                // guards staged by their own quests, which default to an
                // affiliation that does not treat V as an enemy. The estate list is
                // Arasaka combat archetypes, which do.
                //
                // Fixed by asserting the attitude rather than by swapping records:
                // ordinary compound security and an elite estate detail are meant to
                // look different, and trading that away to fix an attitude bug would
                // flatten the two tiers into one.
                if !estate {
                    this.SetHostile(id);
                }
                placed += 1;
            }
            i += 1;
        }
        return placed;
    }

    // ------------------------------------------------- ONE SQUAD PER CALLBACK
    //
    // TWENTY ENTITIES IN ONE TICK IS THE BUG A REPORTER DESCRIBED: *"when I
    // reached the area where the NPCs should have been, they simply weren't
    // there. I checked the emails on the computer, turned around, and the NPCs
    // suddenly spawned directly in front of me."*
    //
    // `CreateEntity` queues rather than creates - this file already knows that,
    // which is why MakeHostile retries for ten seconds waiting for a body to
    // resolve - so asking for twenty at the moment the player arrives means
    // twenty bodies resolving somewhere behind him while he walks on. The estate
    // asked for twenty-six.
    //
    // So the squads are spread over a callback chain instead, and the trigger
    // moved further out (see the tick) so the walk in absorbs the work. Nothing
    // else about the placement changed: same anchors, same sizes, same order.
    //
    // The table is written out rather than passed in, because the chain has to
    // be resumable from a step index and a callback cannot carry an array.
    private func SquadSteps(estate: Bool) -> Int32 {
        if estate { return 6; }
        return 5;
    }

    private func SquadCenter(estate: Bool, step: Int32) -> Vector4 {
        if estate {
            switch step {
                case 0: return CCGig01Places.EstateGate();
                case 1: return CCGig01Places.EstateApproach();
                case 2: return CCGig01Places.EstateGrounds();
                case 3: return CCGig01Places.EstateGarden();
                case 4: return CCGig01Places.EstateSideEntry();
                default: return CCGig01Places.EstateTerminal();
            }
        }
        switch step {
            case 0: return CCGig01Places.CompoundEntry();
            case 1: return CCGig01Places.InnerEntry();
            case 2: return CCGig01Places.OfficeEntry();
            case 3: return CCGig01Places.OfficeGuardPost();
            default: return CCGig01Places.TerminalRoomEntry();
        }
    }

    private func SquadSize(estate: Bool, step: Int32) -> Int32 {
        if estate {
            switch step {
                case 0: return 4;
                case 1: return 4;
                case 2: return 4;
                case 3: return 6;
                case 4: return 4;
                default: return 3;
            }
        }
        switch step {
            case 0: return 4;
            case 1: return 4;
            case 2: return 4;
            case 3: return 5;
            default: return 3;
        }
    }

    // A second between squads: five office squads take four seconds, six estate
    // squads five. Both are comfortably inside the walk the widened trigger now
    // buys, and neither asks the engine for more than six bodies at once.
    private func SquadGap() -> Float { return 1.0; }

    // How many times one squad may be asked for again WITHIN ONE PASS when the
    // navmesh answered nothing at all. Five seconds, then the pass moves on
    // rather than stalling the whole site on one anchor; the audit below comes
    // back to it.
    private func MaxSquadTries() -> Int32 { return 5; }

    // Ticks between audits of a site's unpopulated anchors. Four ticks is 6 s,
    // which is roughly how long it takes to walk far enough for another sector
    // to have streamed in.
    private func AuditTicks() -> Int32 { return 4; }

    // Squad attempts allowed at one site per session, across all audits. The
    // stop that makes an unpopulatable anchor cost a bounded amount rather than
    // one attempt a second for as long as the player stands there.
    private func MaxSquadAttempts() -> Int32 { return 60; }

    // One bit per squad anchor. A table, because redscript has no `<<`. Six
    // entries covers both sites; SquadSteps is 5 and 6.
    private func Bit(i: Int32) -> Int32 {
        switch i {
            case 0: return 1;
            case 1: return 2;
            case 2: return 4;
            case 3: return 8;
            case 4: return 16;
            default: return 32;
        }
    }

    // Every anchor at this site has been populated at least once.
    private func SiteFull(estate: Bool) -> Bool {
        let mask: Int32 = estate ? this.m_estateMask : this.m_officeMask;
        let i: Int32 = 0;
        while i < this.SquadSteps(estate) {
            if (mask & this.Bit(i)) == 0 {
                return false;
            }
            i += 1;
        }
        return true;
    }

    private func MarkAnchor(estate: Bool, step: Int32) -> Void {
        if estate {
            this.m_estateMask = this.m_estateMask | this.Bit(step);
        } else {
            this.m_officeMask = this.m_officeMask | this.Bit(step);
        }
    }

    private func AnchorDone(estate: Bool, step: Int32) -> Bool {
        let mask: Int32 = estate ? this.m_estateMask : this.m_officeMask;
        return (mask & this.Bit(step)) != 0;
    }

    public func SpawnStep(estate: Bool, step: Int32, tries: Int32, placed: Int32) -> Void {
        // Skip anchors already populated. Done here rather than by the caller
        // so an audit can start at 0 every time and still cost nothing for the
        // anchors that are already dealt with.
        let s: Int32 = step;
        while s < this.SquadSteps(estate) && this.AnchorDone(estate, s) {
            s += 1;
        }
        if s >= this.SquadSteps(estate) {
            this.FinishSpawn(estate, placed);
            return;
        }
        let budget: Int32 = estate ? this.m_estateTries : this.m_officeTries;
        if budget >= this.MaxSquadAttempts() {
            this.FinishSpawn(estate, placed);
            return;
        }
        if estate {
            this.m_estateTries += 1;
        } else {
            this.m_officeTries += 1;
        }

        let n: Int32 = this.SpawnSquad(this.SquadCenter(estate, s),
                                       this.SquadSize(estate, s),
                                       n"cc_g01_guard", estate);
        // An empty squad means the navmesh was not ready at that anchor, not
        // that the anchor is bad: every one of them was walked and captured.
        // Ask again a few times, then leave the bit CLEAR and move on, so the
        // audit picks it up once the player has walked closer.
        let nextStep: Int32 = s + 1;
        let nextTries: Int32 = 0;
        if n > 0 {
            this.MarkAnchor(estate, s);
        } else {
            if tries < this.MaxSquadTries() && s == step {
                nextStep = s;
                nextTries = tries + 1;
            }
        }
        let cb: ref<CCGig01SpawnStep> = new CCGig01SpawnStep();
        cb.system = this;
        cb.estate = estate;
        cb.step = nextStep;
        cb.tries = nextTries;
        cb.placed = placed + n;
        GameInstance.GetDelaySystem(this.GetGameInstance())
            .DelayCallback(cb, this.SquadGap(), false);
    }

    // THE BANNER GOES HERE, at the end, and that is the other half of the fix.
    // It used to be the last line of SpawnOfficeSecurity, which ran in the tick
    // the entities were merely REQUESTED in - so "Arasaka security on site"
    // announced a compound that was still empty.
    //
    // The latch is set here too, and only on a real placement. A chain that
    // placed nobody leaves it clear, so the tick starts another one.
    public func FinishSpawn(estate: Bool, placed: Int32) -> Void {
        // The chain runs on delayed callbacks, so its last link can land after
        // the player has quit to the menu. Gig01_Start's header is the reason
        // this is checked rather than assumed: dereferencing a system that is
        // not there yet flatlined the game once already.
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGameInstance());
        if !IsDefined(qs) {
            this.m_officeBusy = false;
            this.m_estateBusy = false;
            return;
        }
        // The fact ACCUMULATES across audits, because a site can be filled in
        // more than one pass now: enter the estate over the back wall and the
        // near anchors populate at once while the gate fills in as you walk
        // back down to it. A per-pass value would read as the site emptying.
        let key: String = estate ? "cc_g01_dbg_estate_guards" : "cc_g01_dbg_office_guards";
        if estate {
            this.m_estateBusy = false;
        } else {
            this.m_officeBusy = false;
        }
        if placed <= 0 {
            return;
        }
        qs.SetFactStr(key, qs.GetFactStr(key) + placed);
        if estate {
            CCSharedHud.Notify(this.GetGameInstance(), "Estate security on site");
        } else {
            CCSharedHud.Notify(this.GetGameInstance(), "Arasaka security on site");
        }
    }

    // Called from the tick on every pass the player is inside a site's region.
    //
    // Cheap when there is nothing to do: one Bool, one loop over at most six
    // bits, and a counter. It only starts a chain when an anchor is still
    // unpopulated, no chain is running, and the audit countdown has run out.
    //
    // This replaces a single "the site is done" latch, which is what left the
    // estate half-empty when entered from behind. See m_estateMask.
    private func AuditSite(estate: Bool) -> Void {
        if this.SiteFull(estate) {
            return;
        }
        if estate {
            if this.m_estateBusy {
                return;
            }
            this.m_estateAudit -= 1;
            if this.m_estateAudit > 0 {
                return;
            }
            this.m_estateAudit = this.AuditTicks();
            if this.m_estateTries >= this.MaxSquadAttempts() {
                return;
            }
            this.m_estateBusy = true;
            this.SpawnEstateSecurity();
            return;
        }
        if this.m_officeBusy {
            return;
        }
        this.m_officeAudit -= 1;
        if this.m_officeAudit > 0 {
            return;
        }
        this.m_officeAudit = this.AuditTicks();
        if this.m_officeTries >= this.MaxSquadAttempts() {
            return;
        }
        this.m_officeBusy = true;
        this.SpawnOfficeSecurity();
    }

    private func SpawnOfficeSecurity() -> Void {
        this.SpawnStep(false, 0, 0, 0);
    }

    private func SpawnEstateSecurity() -> Void {
        // HOSHINO FIRST, and outside the chain. He is the objective, he is one
        // entity, and a guard arriving a second later costs nothing while a
        // Hoshino arriving late is the beat. Guarded by his own latch so a
        // retried chain cannot put a second one on the terrace.
        //
        // Our own record (suit, armed, named).
        // YAW 140.8 = the captured 50.8 turned 90 degrees ANTICLOCKWISE.
        // playtest, 2026-08-14, from a screenshot: he delivered "Mmm? You lost,
        // merc?" with his back to V, facing out over the terrace. Yaw is
        // counter-clockwise seen from above, so anticlockwise is +90.
        // Same spot - only the facing changed.
        if !this.m_hoshinoSpawned {
            this.m_hoshinoId = CCSharedWorld.Spawn(t"Character.cc_g01_hoshino",
                CCGig01Places.Hoshino(), 140.8, n"cc_g01_hoshino");
            this.m_hoshinoSpawned = true;
            this.SetNeutral(this.m_hoshinoId);
        }
        this.SpawnStep(true, 0, 0, 0);
    }

    // WHY HOSHINO IS SPAWNED NEUTRAL, which is the SetNeutral call above.
    //
    // He spawned hostile like the guards, so he opened fire during his own
    // conversation (playtest, 2026-08-12). That is wrong for the scene and
    // wrong for the character: the whole point of him is that he is an
    // administrator, not a soldier. He signs, he does not fight.
    //
    // Neutral until provoked. AttitudeAgent.SetAttitudeGroup is how vanilla
    // moves an NPC between sides (aiRole.swift:232, dynamicSpawnSystem
    // .swift:72 sets n"hostile" the same way). Shooting him flips him back
    // by the game's own reaction rules, so "until we attack" comes for free:
    // we do not have to watch for it.

    // HOW LONG AN ATTITUDE MAY TAKE TO STICK. 1.5 s a try, so this is 60 s.
    //
    // It was 6 tries, 10.5 s, and that budget was sized on this machine against
    // the old all-at-once burst. On a slower one, or a heavily modded load
    // order, a guard that takes longer than that to stream in keeps his
    // record's default attitude, and the compound list is mostly `sts_*`
    // street-story security which does not treat V as an enemy. The symptom is
    // "the guards ignore me" - the 2026-08-13 bug arriving by a new route, from
    // a budget rather than from a missing call.
    //
    // The cost of the higher cap is only paid by a guard who never resolves at
    // all: everyone else returns on the try that finds him. With the burst now
    // staggered, that should be the first or second.
    private func MaxAttitudeTries() -> Int32 { return 40; }

    // Move a spawned NPC out of the hostile group so he will not open fire.
    //
    // The entity streams in asynchronously, so this cannot run in the same tick
    // as the spawn - hence the delayed retry. Same lesson as Johnny: a dynamic
    // entity is not resolvable in the tick you asked for it.
    private func SetNeutral(id: EntityID) -> Void {
        let cb: ref<CCGig01MakeNeutral> = new CCGig01MakeNeutral();
        cb.system = this;
        cb.target = id;
        cb.tries = 0;
        GameInstance.GetDelaySystem(this.GetGameInstance()).DelayCallback(cb, 1.5, false);
    }

    public func MakeNeutral(id: EntityID, tries: Int32) -> Void {
        let obj: ref<GameObject> = GameInstance.GetDynamicEntitySystem().GetEntity(id) as GameObject;
        if IsDefined(obj) {
            let agent: ref<AttitudeAgent> = obj.GetAttitudeAgent();
            if IsDefined(agent) {
                agent.SetAttitudeGroup(n"neutral");
                return;
            }
        }
        // Not streamed in yet. Try a few more times rather than silently give up
        // and leave him shooting through his own dialogue.
        if tries < this.MaxAttitudeTries() {
            let cb: ref<CCGig01MakeNeutral> = new CCGig01MakeNeutral();
            cb.system = this;
            cb.target = id;
            cb.tries = tries + 1;
            GameInstance.GetDelaySystem(this.GetGameInstance()).DelayCallback(cb, 1.5, false);
        }
    }

    // The mirror of SetNeutral, and it needs the same delayed retry for the same
    // reason: the entity streams in asynchronously, so nothing is resolvable in
    // the tick it was requested in.
    private func SetHostile(id: EntityID) -> Void {
        let cb: ref<CCGig01MakeHostile> = new CCGig01MakeHostile();
        cb.system = this;
        cb.target = id;
        cb.tries = 0;
        GameInstance.GetDelaySystem(this.GetGameInstance()).DelayCallback(cb, 1.5, false);
    }

    // Both halves, deliberately. SetAttitudeGroup is how vanilla moves an NPC
    // between sides (dynamicSpawnSystem.swift:72 sets n"hostile" exactly like
    // this), and SetAttitudeTowards forces the pairing with V regardless of what
    // the group would have resolved to - which is the half that covers a record
    // whose own affiliation is the problem. It is the same pair already used on
    // Hoshino in Tick, and that one is confirmed working in game.
    public func MakeHostile(id: EntityID, tries: Int32) -> Void {
        let obj: ref<GameObject> = GameInstance.GetDynamicEntitySystem().GetEntity(id) as GameObject;
        if IsDefined(obj) {
            let agent: ref<AttitudeAgent> = obj.GetAttitudeAgent();
            let player: ref<PlayerPuppet> = GetPlayer(this.GetGameInstance()) as PlayerPuppet;
            if IsDefined(agent) && IsDefined(player) {
                // HOSTILE TO V, NOT HOSTILE TO EVERYONE.
                //
                // This used to also call SetAttitudeGroup(n"hostile") and playtesting
                // caught what that means: "those guards start killing existing
                // NPCs... this happens only after they see me and start shooting
                // at me." Of course they do - n"hostile" is not "hostile to the
                // player", it is a GROUP, and a member of it is at war with
                // every other group in the room, Arasaka colleagues included.
                // The moment combat woke them up they picked targets by group
                // and their own side qualified.
                //
                // SetAttitudeTowards is the pairwise version and it is the one
                // that was wanted all along: it makes this guard an enemy of
                // THIS player and changes nothing else, so the guards stay
                // Arasaka to each other. Their record's own affiliation is left
                // exactly as it was.
                agent.SetAttitudeTowards(player.GetAttitudeAgent(), EAIAttitude.AIA_Hostile);
                return;
            }
        }
        if tries < this.MaxAttitudeTries() {
            let cb: ref<CCGig01MakeHostile> = new CCGig01MakeHostile();
            cb.system = this;
            cb.target = id;
            cb.tries = tries + 1;
            GameInstance.GetDelaySystem(this.GetGameInstance()).DelayCallback(cb, 1.5, false);
        }
    }


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
                this.RunUploadBar("COPYING LEDGER", 3.2);
                break;
            case 1: break;
            case 2:
                this.ShowUploadBar(false, "");
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
                // V pays Nix up front - the comic puts the transfer on screen,
                // so it happens for real rather than being implied. Same
                // TransactionSystem the payout uses, in the other direction.
                let player: ref<PlayerPuppet> = GetPlayer(this.GetGameInstance()) as PlayerPuppet;
                if IsDefined(player) {
                    GameInstance.GetTransactionSystem(this.GetGameInstance())
                        .RemoveItemByTDBID(player, t"Items.money", 15000);
                }
                CCSharedHud.NotifyTyped(this.GetGameInstance(), GetLocalizedTextByKey(n"cc-g01-hud-paid"),
                                 SimpleMessageType.Money, 4.0);
                GameInstance.GetQuestsSystem(this.GetGameInstance())
                    .SetFactStr("cc_g01_ledger_sent", 1);
                // Johnny's p28 beat follows while Nix works, so the wait is
                // not dead air - but the quest phase drives it now
                // (gig01_legend.scene, gated on the fact set just above)
                // rather than a delayed callback chaining captions.
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

    // StartLegendTalk() used to live here (comic p28, the crosswalk). Removed
    // 2026-08-13: it is gig01_legend.scene now, entered by the quest phase on
    // cc_g01_ledger_sent, which SendStep still sets exactly as before.
    //
    // THE BIG BOTTOM-OF-SCREEN PROGRESS BAR - the one the game shows while an
    // enemy netrunner is uploading a quickhack onto V.
    //
    // THIS IS THE THIRD ATTEMPT AT THIS WIDGET AND THE FIRST CORRECT ONE. Worth
    // recording what the wrong two were, because they are both plausible:
    //
    //   1. I first called it another mod's UI. Wrong - it had been seen it in
    //      many vanilla missions.
    //   2. Then I drove UploadProgramProgressEvent, which really is a vanilla
    //      upload bar - but it is the quickhack indicator that hangs on a TARGET
    //      ENTITY via GameplayRoleComponent, i.e. a small bar over the thing you
    //      are hacking. It showed nothing here and would have been the wrong
    //      shape anyway.
    //
    // a follow-up clarification named it exactly: "the same UI used when a
    // netrunner is tracking you". That one is NOT entity-attached at all - it is
    // a HUD widget driven straight off a blackboard, the same way our subtitles
    // are. `UploadFromNPCToPlayerListener` (rpgManager.swift:3699) writes to
    // GetAllBlackboardDefs().UI_HUDProgressBar, read by
    // cyberpunk/UI/widgets/hud_progress_bar/HUD_progress_bar.swift.
    //
    // No entity needed, so this also no longer depends on V being plugged in.
    private func ShowUploadBar(started: Bool, header: String) -> Void {
        let bb: ref<IBlackboard> = GameInstance.GetBlackboardSystem(this.GetGameInstance())
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
            // the playtest copy bar ended on FAILED because the beat finished at
            // 3.2 s while the fill had been told 5.2 s, so it closed at ~60%.
            // Matching the two durations fixes that case; writing 1.0 here
            // makes it structurally impossible, whatever the timings drift to.
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
    public func UploadBarStep(elapsed: Float, total: Float) -> Void {
        let bb: ref<IBlackboard> = GameInstance.GetBlackboardSystem(this.GetGameInstance())
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
            let cb: ref<CCGig01UploadBarStep> = new CCGig01UploadBarStep();
            cb.system = this;
            cb.elapsed = elapsed + 0.1;
            cb.total = total;
            GameInstance.GetDelaySystem(this.GetGameInstance()).DelayCallback(cb, 0.1, false);
        }
    }

    private func RunUploadBar(header: String, seconds: Float) -> Void {
        this.ShowUploadBar(true, header);
        this.UploadBarStep(0.0, seconds);
    }

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
                this.RunUploadBar("SABOTAGE: UPLOADING MALWARE TO THE NETWORK", 10.0);
                break;
            case 1: break;
            case 2: break;
            case 3: break;
            case 4:
                this.ShowUploadBar(false, "");
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
        let ms: ref<MappinSystem> = GameInstance.GetMappinSystem(this.GetGameInstance());
        if !IsDefined(ms) {
            return;
        }
        let spot: Vector4 = CCGig01Places.WayInMarker(leg);
        if this.m_wayinMappinUp {
            // MOVE the one we already have. Registering a second and dropping
            // the first would leave the old one on screen for a frame and, if
            // the unregister ever missed, forever.
            ms.SetMappinPosition(this.m_wayinMappin, spot);
            return;
        }
        // `MappinData`, NOT `gamemappinsMappinData`. The journal resource spells
        // it the long way and redscript does not know that name at all
        // (`unresolved type`); the script-visible struct is the short one, and
        // it carries exactly five fields - mappinType, variant, debugCaption,
        // visibleThroughWalls, scriptData. There is no `active`: a registered
        // mappin is live by definition, and the journal's `active` flag belongs
        // to the authored pin, not to this.
        let data: MappinData;
        // The same two ids our journal pins carry, so it reads as the gig's own
        // objective marker rather than something a mod bolted on.
        data.mappinType = t"Mappins.QuestStaticMappinDefinition";
        data.variant = gamedataMappinVariant.QuestGiverVariant;
        data.visibleThroughWalls = true;
        this.m_wayinMappin = ms.RegisterMappin(data, spot);
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
        let ms: ref<MappinSystem> = GameInstance.GetMappinSystem(this.GetGameInstance());
        if IsDefined(ms) {
            ms.UnregisterMappin(this.m_wayinMappin);
        }
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
    private func GiveReward(player: ref<PlayerPuppet>, qs: ref<QuestsSystem>) -> Void {
        qs.SetFactStr("cc_g01_rewarded", 1);

        GameInstance.GetTransactionSystem(this.GetGameInstance())
            .GiveItemByTDBID(player, t"Items.money", 2500);
        RPGManager.AwardExperienceInstantly(player, 300, gamedataProficiencyType.StreetCred);

        CCSharedHud.NotifyTyped(this.GetGameInstance(), GetLocalizedTextByKey(n"cc-g01-reward"), SimpleMessageType.Money, 4.0);
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
                // Arrive at the compound: mark the objective, populate the site.
                //
                // TWO TESTS, NOT ONE, AND THE SPAWN ONE IS THE WIDER OF THEM.
                //
                // It used to be a single 60 m sphere on CompoundEntry, and the
                // site does not fit inside it: the office terminal is 63.5 m
                // from that anchor and the terminal room door 67.7 m. A player
                // who reached the computer without crossing the bubble found an
                // empty building, which is half of the report quoted on
                // SpawnStep. So the office is measured from the BUILDING as
                // well as from the gate.
                //
                // The spawn test is wider again, because the squads are now
                // spread over a callback chain and that chain needs runway. 100 m
                // on the gate is roughly 85 m out from the map pin: far enough
                // that the walk in absorbs the work, close enough that nothing
                // populates a compound the player is only driving past.
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
                // Spawning starts EARLIER than arriving, because the squads are
                // spread over a callback chain and that chain needs runway.
                if atOffice
                    || Vector4.Distance(pos, CCGig01Places.CompoundEntry()) < 100.0 {
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

                // THE SHARD IN THE DESK, comic pp. 23-24. Three steps, and the
                // quest phase owns the middle of the sandwich - see
                // Gig01_Shard.reds for what the reader actually is.
                //
                // THE SHARD IS THE ONE ALREADY LYING ON THAT DESK, and V
                // reading it is what sets cc_g01_shard_found - see the
                // ReadAction wrap in Gig01_Shard.reds.
                //
                // WE SHIPPED OUR OWN AND IT NEVER RENDERED. The .ent attached,
                // the prompt worked, but the mesh was never visible - playtesting
                // twice, with screenshots. The trace then settled what had
                // actually happened: cc_g01_shard_found came from the 30-second
                // proximity fallback below, not from a pickup, so the object was
                // doing nothing at all.
                //
                // Two dead ends and one sitting in plain sight. the playtest had
                // already pointed at it: "the shard is already in the room so
                // maybe you can use its location and override the content." The
                // room ships a readable shard on the desk the objective already
                // sends V to. It renders, it has a prompt, it is lit, it is
                // scannable - every property that was hard to reproduce. The
                // only thing wrong with it is what it says, and text is the one
                // part we can replace outright.
                //
                // So: no spawn. The pin marks that shard, the player reads it,
                // and the wrap swaps our note in for its own.
                //
                // (tools/gig01/gen_shard_ent.py and cc_g01_shard.ent stay in the tree.
                // They are a WORKING recipe for a custom interactable - the
                // prompt half is proven - and gigs 02-04 may want one somewhere
                // that has no convenient shard. Nothing spawns it today).

                // THE SHARD IS READ BY WALKING UP TO IT. the design call after
                // seven attempts at an [F] prompt: "let's put back the duplicate
                // shard, and start reading it on proximity rather than action."
                //
                // The object is real, visible and pinned - tools/gig01/gen_sector.py
                // places it, and that file records everything that was ruled out
                // on the way to giving up on the prompt. What could never be
                // raised was the INTERACTION; being there and being findable
                // both work.
                //
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

                // 2. The quest phase plays V's "A data shard..." line and then
                //    sets cc_g01_shard_open. Raising the reader from the tick
                //    rather than from the quest graph is what lets it be
                //    RETRIED: GetEntryByString can return null if the journal
                //    has not resolved our merged entry yet, and a quest node
                //    that fired into nothing would strand the gig here.
                if qs.GetFactStr("cc_g01_shard_open") > 0
                    && qs.GetFactStr("cc_g01_shard_read") == 0
                    && !this.m_shardOpened {
                    this.m_shardOpened = CCG01Shard.Open(game);
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
                if qs.GetFactStr("cc_g01_nixbrief_done") > 0
                    && qs.GetFactStr("cc_g01_ledger_sent") == 0
                    && !this.m_sendBusy {
                    this.m_sendBusy = true;
                    this.SendStep(0);
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
                    if CCSharedWorld.Near(pos, CCGig01Places.EstateGate(), 45.0, 12.0, 25.0)
                        || CCSharedWorld.Near(pos, CCGig01Places.Hoshino(), 70.0, 12.0, 25.0)
                        || CCGig01Places.InsideEstate(pos) {
                        if qs.GetFactStr("cc_g01_estate_reached") == 0 {
                            qs.SetFactStr("cc_g01_estate_reached", 1);
                        }
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
                    if qs.GetFactStr("cc_g01_estate_reached") > 0
                        && qs.GetFactStr("cc_g01_wayin_reached") == 0
                        && (CCSharedWorld.Near(pos, CCGig01Places.EstateWayIn(), 6.0, 4.0, 4.0)
                            || CCGig01Places.InsideEstate(pos)) {
                        qs.SetFactStr("cc_g01_wayin_reached", 1);
                    }

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
                if this.m_hoshinoSpawned && qs.GetFactStr("cc_g01_hoshino_dead") == 0 {
                    let des: ref<DynamicEntitySystem> = GameInstance.GetDynamicEntitySystem();
                    let hoshino: ref<ScriptedPuppet> = des.GetEntity(this.m_hoshinoId) as ScriptedPuppet;

                    if IsDefined(hoshino) && ScriptedPuppet.IsAlive(hoshino) {
                        this.m_hoshinoSeenAlive = true;
                        let agent: ref<AttitudeAgent> = hoshino.GetAttitudeAgent();
                        if IsDefined(agent) {
                            agent.SetAttitudeGroup(n"hostile");
                            agent.SetAttitudeTowards(player.GetAttitudeAgent(), EAIAttitude.AIA_Hostile);
                        }
                        // His exchange is a real scene now (gig01_hoshino.scene,
                        // run by the quest phase). All this does is say "V is
                        // in front of him"; the words and the choice of opening
                        // line live in the scene.
                        if !this.m_hoshinoGreeted
                            && Vector4.Distance(pos, CCGig01Places.Hoshino()) < 12.0 {
                            this.m_hoshinoGreeted = true;
                            qs.SetFactStr("cc_g01_hoshino_met", 1);
                        }

                    } else {
                        if this.m_hoshinoSeenAlive && des.IsSpawned(this.m_hoshinoId)
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

public class CCGig01SpawnStep extends DelayCallback {
    public let system: wref<NegativeBalanceEncounter>;
    public let estate: Bool;
    public let step: Int32;
    public let tries: Int32;
    public let placed: Int32;
    public func Call() -> Void {
        if IsDefined(this.system) {
            this.system.SpawnStep(this.estate, this.step, this.tries, this.placed);
        }
    }
}

public class CCGig01MakeNeutral extends DelayCallback {
    public let system: wref<NegativeBalanceEncounter>;
    public let target: EntityID;
    public let tries: Int32;
    public func Call() -> Void {
        if IsDefined(this.system) { this.system.MakeNeutral(this.target, this.tries); }
    }
}

public class CCGig01MakeHostile extends DelayCallback {
    public let system: wref<NegativeBalanceEncounter>;
    public let target: EntityID;
    public let tries: Int32;
    public func Call() -> Void {
        if IsDefined(this.system) { this.system.MakeHostile(this.target, this.tries); }
    }
}

public class CCGig01UploadBarStep extends DelayCallback {
    public let system: wref<NegativeBalanceEncounter>;
    public let elapsed: Float;
    public let total: Float;
    public func Call() -> Void {
        if IsDefined(this.system) { this.system.UploadBarStep(this.elapsed, this.total); }
    }
}

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
