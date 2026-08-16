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

    private let m_officeSpawned: Bool;
    private let m_estateSpawned: Bool;
    private let m_hoshinoId: EntityID;
    private let m_hoshinoSpawned: Bool;
    private let m_hoshinoSeenAlive: Bool;   // only then can we call him dead
    private let m_hoshinoGreeted: Bool;
    private let m_downloadBusy: Bool;
    private let m_uploadBusy: Bool;
    private let m_sendBusy: Bool;
    private let m_talkBusy: Bool;
    private let m_barWaited: Int32;
    private let m_mamaId: EntityID;
    private let m_mamaSpawned: Bool;
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
    private let m_lipMove: Int32;
    private let m_lipAhead: Float;      // this beat's placement offsets, hand-
    private let m_lipAside: Float;      // tuned against real geometry
    private let m_lipFastRunning: Bool;  // the 0.15 s placement poll is armed
    private let m_lipFastTries: Int32;   // bounded at 40 (~6 s)
    private let m_lipWsId: EntityID;    // the scene Johnny's OWN workspot device
    private let m_lipWsSpawned: Bool;
    private let m_lipFxPending: Bool;   // fire the arrival glitch next poll
    private let m_lipBeat: Int32;       // which staging is armed, so one beat
    private let m_lipDone: Bool;        // cannot stage itself twice

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
    private func SpawnSquad(center: Vector4, count: Int32, tag: CName, estate: Bool) -> Void {
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
            }
            i += 1;
        }
    }

    private func SpawnOfficeSecurity() -> Void {
        this.SpawnSquad(CCGig01Places.CompoundEntry(), 4, n"cc_g01_guard", false);
        this.SpawnSquad(CCGig01Places.InnerEntry(), 4, n"cc_g01_guard", false);
        this.SpawnSquad(CCGig01Places.OfficeEntry(), 4, n"cc_g01_guard", false);
        this.SpawnSquad(CCGig01Places.OfficeGuardPost(), 5, n"cc_g01_guard", false);
        this.SpawnSquad(CCGig01Places.TerminalRoomEntry(), 3, n"cc_g01_guard", false);
        CCSharedHud.Notify(this.GetGameInstance(), "Arasaka security on site");
    }

    private func SpawnEstateSecurity() -> Void {
        this.SpawnSquad(CCGig01Places.EstateGate(), 4, n"cc_g01_guard", true);
        this.SpawnSquad(CCGig01Places.EstateApproach(), 4, n"cc_g01_guard", true);
        this.SpawnSquad(CCGig01Places.EstateGrounds(), 4, n"cc_g01_guard", true);
        this.SpawnSquad(CCGig01Places.EstateGarden(), 6, n"cc_g01_guard", true);
        this.SpawnSquad(CCGig01Places.EstateSideEntry(), 4, n"cc_g01_guard", true);
        this.SpawnSquad(CCGig01Places.EstateTerminal(), 3, n"cc_g01_guard", true);

        // Hoshino himself. Our own record (suit, armed, named).
        // YAW 140.8 = the captured 50.8 turned 90 degrees ANTICLOCKWISE.
        // playtest, 2026-08-14, from a screenshot: he delivered "Mmm? You lost,
        // merc?" with his back to V, facing out over the terrace. Yaw is
        // counter-clockwise seen from above, so anticlockwise is +90.
        // Same spot - only the facing changed.
        this.m_hoshinoId = CCSharedWorld.Spawn(t"Character.cc_g01_hoshino",
            CCGig01Places.Hoshino(), 140.8, n"cc_g01_hoshino");
        this.m_hoshinoSpawned = true;
        // ...and NOT shooting at V while they talk.
        //
        // He spawned hostile like the guards, so he opened fire during his own
        // conversation (playtest, 2026-08-12). That is wrong for the scene and
        // wrong for the character: the whole point of him is that he is an
        // administrator, not a soldier. He signs, he does not fight.
        //
        // Neutral until provoked. AttitudeAgent.SetAttitudeGroup is how vanilla
        // moves an NPC between sides (aiRole.swift:232, dynamicSpawnSystem
        // .swift:72 sets n"hostile" the same way). Shooting him flips him back
        // by the game's own reaction rules, so "until we attack" comes for free -
        // we do not have to watch for it.
        this.SetNeutral(this.m_hoshinoId);
        CCSharedHud.Notify(this.GetGameInstance(), "Estate security on site");
    }

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
        if tries < 6 {
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
        if tries < 6 {
            let cb: ref<CCGig01MakeHostile> = new CCGig01MakeHostile();
            cb.system = this;
            cb.target = id;
            cb.tries = tries + 1;
            GameInstance.GetDelaySystem(this.GetGameInstance()).DelayCallback(cb, 1.5, false);
        }
    }

    // ---------------------------------------------------------------- Johnny
    // Johnny's apparition, spawned NEXT TO V wherever V happens to be.
    //
    // A .scene actor cannot do this: it spawns at the scene's fixed marker, so
    // a beat that can happen anywhere - like the moment Elena's location lands -
    // would materialise him in an Arroyo car park while V is across the city.
    // The dynamic-entity route has no such limit, which is how AMM and friends
    // put him on screen.
    //
    // Character.Silverhand and silverhand_default are the VERIFIED ids from
    // vanilla scene data (docs/scene-playbook.md, "Johnny's apparition"); the
    // appearance is what buys the see-through, rim-lit, glitching look.
    //
    // The trade-off vs a scene actor: no dialogue choices and no lipsync here.
    // What we DO get is a real GameObject to hang the line on, which means the
    // subtitle can name him - the scene line does that now.
    // ahead / aside are metres in V's frame. They are arguments rather than
    // constants because the right staging depends on the room: out in the open
    // he can stand in front of V, but at the office terminal V is nose-to-screen
    // against a desk and anything "ahead" is inside the wall.
    // ======================================================================
    // THE ONE THING BEING TESTED, 2026-08-14. Everything else is untouched.
    // ======================================================================
    //
    // Lipsync works, and it works on the SCENE'S actor (playtest: "the second
    // johnny is perfectly lip synced"). The scene's actor is the one this gig
    // cannot place: a `.scene` is baked before the game runs, so it cannot say
    // "in front of V", only "somewhere around the marker" - and an
    // `around_player` marker's rotation is not knowable. He lands behind V.
    //
    // the proposal, and it is the right one: read V's position and facing
    // at RUNTIME and put him in front. The script can do that maths - it does
    // it in SpawnJohnny below, and has since August. What it has never done is
    // MOVE a body the scene owns.
    //
    // So this is the single untested step, and nothing else changes: find the
    // scene's Johnny and teleport him to the spot SpawnJohnny would have used.
    // The script's own Johnny still spawns, the scene still spawns its own, and
    // there are still two of them - collapsing to one is the NEXT change, and
    // only if this one works.
    //
    // TWO SILVERHANDS, AND TELLING THEM APART. Both carry
    // Character.Silverhand, so the record alone is ambiguous. Ours is the one
    // whose EntityID is m_johnnyId; anything else with that record is the
    // scene's. That is the whole discriminator and it is exact.
    //
    // Read `cc_g01_dbg_lip_move` in call_trace.log:
    //   1 = no second Silverhand found - the scene's actor is not there, or the
    //       targeting query cannot see him
    //   2 = found him and called Teleport
    //
    // `Teleport` is confirmed by the compiler and has NEVER BEEN RUN. The real
    // unknown is not the call, it is whether it survives the workspot he is
    // standing in - the animation may fight it or snap him back. That is what
    // one press of the dev button answers.
    // Poll every 0.15 s until he is placed, instead of waiting on the 1.5 s
    // encounter tick.
    //
    // THE HOP IS A SAMPLING PROBLEM, not a placement one. The scene stages him
    // at the around_player marker - behind V, unaimable - and he is visible the
    // instant his workspot starts. Everything after that is correct; the only
    // thing wrong is that the correction arrives up to 1.5 s late and the player
    // watches it happen. At 0.15 s it lands inside his arrival dissolve.
    //
    // Bounded twice over: it stops as soon as he is placed, and after 40 tries
    // (6 s) regardless, so a beat that never stages an actor cannot leave a
    // callback chain running for the rest of the session.
    // The scene's Johnny glitches out just before the scene removes him, so the
    // vanish happens behind the flash instead of being a pop. Same effect and
    // the same 0.25 s cut approved in playtest for the script-spawned one; only the
    // body it is fired on has changed.
    //
    // Finds him again rather than holding a reference: the scene owns this
    // entity and may have disposed of it already if anything ran long. A miss
    // is silent and costs exactly the pop we are trying to avoid, which is why
    // this is not worth guarding harder.
    public func LipExitJohnny() -> Void {
        let player: ref<PlayerPuppet> = GameInstance.GetPlayerSystem(this.GetGameInstance())
            .GetLocalPlayerMainGameObject() as PlayerPuppet;
        if !IsDefined(player) {
            return;
        }
        let johnny: ref<GameObject> = this.FindSceneJohnny(player);
        if IsDefined(johnny) {
            GameObjectEffectHelper.StartEffectEvent(johnny, n"johnny_teleport_start");
        }
    }

    // Arms the placement for ONE beat. Every Johnny beat calls this instead of
    // SpawnJohnny, with the offsets that beat used to spawn him at.
    //
    // Resetting is the whole job: eight beats share these fields, and a beat
    // that inherited the last one's device would put Johnny at the previous
    // beat's position - the device is spawned AT a spot and the workspot is
    // what moves him to it. LipReset deletes it; do not "optimise" that away.
    private func ArmLipPlacement(beat: Int32, ahead: Float, aside: Float) -> Void {
        // ONLY m_lipFastRunning guards this. It used to also return when
        // m_lipMove == 2, and that was a LATCH THAT KILLED EVERY LATER BEAT.
        //
        // m_lipMove goes to 2 on placement and only back to 0 when the poll
        // sees the scene's exit cue. If the poll expires first, the flag sticks
        // at 2 for the rest of the playthrough and no later window can ever
        // arm. That is exactly what happened once gig01_netrunner was merged
        // in: gig01_terminal became a 25-SECOND scene, the poll's 30 s budget
        // started before the scene did, and it burned out mid-conversation -
        // so Johnny was missing from "Ledger's closed." and "No more payouts."
        // (playtest, 2026-08-14).
        //
        // Re-arming from scratch every time the poll is idle costs one find per
        // tick and cannot latch. LipReset below clears the previous staging.
        if this.m_lipFastRunning {
            return;
        }
        // ONE STAGING PER BEAT. Without this the re-arm above would restart the
        // 0.15 s poll on every 1.5 s tick for as long as the window is open -
        // and some windows stay open for minutes of walking (kill's runs until
        // the malware is uploaded). A 40 m targeting query six times a second
        // for that long is not free.
        //
        // The beat id is what makes it safe to re-arm at all: a DIFFERENT beat
        // always stages, the same one never stages twice.
        if this.m_lipBeat == beat && this.m_lipDone {
            return;
        }
        this.LipReset();
        this.m_lipBeat = beat;
        this.m_lipDone = false;
        this.m_lipAhead = ahead;
        this.m_lipAside = aside;
        this.m_lipFastRunning = true;
        this.m_lipFastTries = 0;
        // Clear the scene's exit signal before the beat, so a later staging
        // cannot inherit a set fact and glitch him out the instant he arrives.
        GameInstance.GetQuestsSystem(this.GetGameInstance())
            .SetFactStr("cc_g01_johnny_exit", 0);
        this.PlaceSceneJohnnyFast();
    }

    // Back to "nothing staged": the device goes, the bookkeeping goes, and
    // m_lipMove returns to 0 so the next beat's window can arm.
    private func LipReset() -> Void {
        if this.m_lipWsSpawned {
            GameInstance.GetDynamicEntitySystem().DeleteEntity(this.m_lipWsId);
            this.m_lipWsSpawned = false;
        }
        this.m_lipMove = 0;
        this.m_lipFxPending = false;
    }

    public func PlaceSceneJohnnyFast() -> Void {
        let player: ref<PlayerPuppet> = GameInstance.GetPlayerSystem(this.GetGameInstance())
            .GetLocalPlayerMainGameObject() as PlayerPuppet;
        if !IsDefined(player) {
            this.m_lipFastRunning = false;
            return;
        }
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGameInstance());
        if this.m_lipFxPending {
            // One poll after placement: the workspot idle is running now, so
            // the arrival glitch plays over a posed body instead of a T-pose.
            this.m_lipFxPending = false;
            let arrived: ref<GameObject> = this.FindSceneJohnny(player);
            if IsDefined(arrived) {
                GameObjectEffectHelper.StartEffectEvent(arrived, n"johnny_teleport_end");
            }
        }
        if this.m_lipMove != 2 {
            this.PlaceSceneJohnny(player, this.m_lipAhead, this.m_lipAside);
        } else {
            // PLACED - now the same poll watches for the scene telling us it is
            // about to remove him, and fires his exit glitch within 150 ms.
            //
            // This replaced a DelayCallback scheduled at placement time, which
            // could not work and did not: it was anchored to the one moment in
            // the beat that VARIES. Measured 2026-08-14 - placement landed 5.5 s
            // into a 7.8 s scene, so the exit fired 5 s after the scene had
            // already deleted him and he simply popped.
            //
            // cc_g01_johnny_exit is set by the SCENE, from an events socket
            // 250 ms before its last section ends (gen_scenes.build_arasaka).
            // The scene knows its own length exactly; this script never has to.
            if qs.GetFactStr("cc_g01_johnny_exit") > 0 {
                this.LipExitJohnny();
                this.m_lipFastRunning = false;
                this.m_lipDone = true;
                // Tear the staging down so the NEXT beat can arm. Without this
                // m_lipMove stays 2 for the rest of the playthrough and every
                // later Johnny stays buried under the floor, silent and unseen.
                this.LipReset();
                return;
            }
        }
        this.m_lipFastTries += 1;
        // 200 tries = 30 s, and the number matters. It was 40 (6 s), armed at
        // cc_g01_johnny_cue - which fires from inside Elena's call, up to seven
        // seconds before the arasaka scene exists at all. The poll was dead
        // before the actor was born, every time, and placement fell back to the
        // 1.5 s tick. The window this runs inside is bounded by johnny_done, so
        // 30 s is "until the beat is over" rather than a timeout anyone waits on.
        // 600 tries = 90 s, comfortably longer than the longest beat
        // (gig01_terminal is 25 s of dialogue and the poll arms before it
        // starts). This is "until the beat is over", not a timeout anyone
        // waits on - it stops the moment the exit cue arrives.
        if this.m_lipFastTries > 600 {
            this.m_lipFastRunning = false;
            // Give up on THIS beat rather than hammering the query for the rest
            // of the window. 90 s is far longer than any beat takes to start.
            this.m_lipDone = true;
            return;
        }
        let again: ref<CCGig01LipPlace> = new CCGig01LipPlace();
        again.system = this;
        GameInstance.GetDelaySystem(this.GetGameInstance())
            .DelayCallback(again, 0.15, false);
    }

    private func FindSceneJohnny(player: ref<PlayerPuppet>) -> ref<GameObject> {
        // Same shape as FindMamaWelles, which is proven in game. TSQ_NPC with
        // the complete targeting set so walls do not hide him.
        let query: TargetSearchQuery = TSQ_NPC();
        query.testedSet = TargetingSet.Complete;
        query.includeSecondaryTargets = false;
        query.ignoreInstigator = true;
        query.maxDistance = 40.0;
        query.filterObjectByDistance = true;

        let parts: array<TS_TargetPartInfo>;
        GameInstance.GetTargetingSystem(this.GetGameInstance())
            .GetTargetParts(player, query, parts);

        let i: Int32 = 0;
        while i < ArraySize(parts) {
            let target: ref<GameObject> = TS_TargetPartInfo.GetComponent(parts[i]).GetEntity() as GameObject;
            let puppet: ref<ScriptedPuppet> = target as ScriptedPuppet;
            // The script used to spawn a SECOND Silverhand, so this had to
            // exclude its own by EntityID or it would find that one and place it
            // instead of the scene's. There is only one Johnny now, so the
            // exclusion went with the path that created the ambiguity.
            if IsDefined(puppet)
                && puppet.GetRecordID() == t"Character.Silverhand" {
                return puppet;
            }
            i += 1;
        }
        return null;
    }

    // Put the scene's Johnny `ahead` metres along V's facing, `aside` metres to
    // the right of it, turned back towards V. The offsets come from the
    // script-owned SpawnJohnny this replaced; they were tuned by hand against
    // real geometry and are not to be re-derived.
    private func PlaceSceneJohnny(player: ref<PlayerPuppet>, ahead: Float,
                                  aside: Float) -> Void {
        let johnny: ref<GameObject> = this.FindSceneJohnny(player);
        if !IsDefined(johnny) {
            this.m_lipMove = 1;
            return;
        }
        // ONCE PER APPEARANCE, not once per tick. m_lipMove goes back to 1 the
        // moment he is gone, which re-arms this for the next beat. Without it
        // the poll would re-place him every 0.15 s for the length of the scene.
        if this.m_lipMove == 2 {
            return;
        }
        let pos: Vector4 = player.GetWorldPosition();
        let fwd: Vector4 = player.GetWorldForward();
        let spot: Vector4 = new Vector4(
            pos.X + fwd.X * ahead - fwd.Y * aside,
            pos.Y + fwd.Y * ahead + fwd.X * aside,
            pos.Z,
            1.0);
        let toV: Vector4 = new Vector4(pos.X - spot.X, pos.Y - spot.Y, 0.0, 1.0);
        let angles: EulerAngles;
        angles.Yaw = Vector4.Heading(toV);

        // =================================================================
        // NOT `Teleport`. IT MOVES HIM TO V, NOT TO THE POSITION IT IS GIVEN.
        // =================================================================
        //
        // Measured 2026-08-14, and this is why the diagnostic existed:
        //     cc_g01_dbg_lip_want = 210   the spot asked for IS 2.1 m from V
        //     cc_g01_dbg_lip_err  = 210   he ended up 2.1 m FROM that spot
        // Two equal numbers, and the only point 2.1 m from the spot that V can
        // be standing on is V. So the maths was right all along and
        // `TeleportationFacility.Teleport(obj, pos, angles)` - which compiles,
        // and which does move him - ignores the position for a puppet and puts
        // him on the player. Do not reach for it again to place an NPC.
        //
        // THE PROVEN TOOL WAS ALREADY IN THIS FILE. `SpawnJohnny` does not
        // position Johnny by teleporting him either: it spawns an invisible
        // workspot DEVICE at the spot and calls PlayInDeviceSimple, and the
        // workspot places him. That is confirmed in game since 2026-08-12 and
        // it is what puts the script's Johnny exactly where he belongs.
        //
        // So do the same thing to the scene's Johnny. It also earns the
        // apparition for free: `phantomVisibleStates` is
        // ["RootMotion","Workspot"], so a workspot is what makes the
        // see-through appearance render at all.
        // ITS OWN device and its own bookkeeping. m_johnnyWsId belongs to
        // SpawnJohnny, and during this beat BOTH are running - sharing the
        // field would have one of them stealing the other's device. That is
        // exactly the class of bug that broke Johnny three times in one evening
        // (docs/gotchas.md #15: when you write a field, look up who else reads
        // it).
        // THE DEVICE'S ORIENTATION IS WHAT HE ENDS UP FACING, and leaving it out
        // is why he had his back to V. playtest, 2026-08-14: "when I read the
        // shard... he's not facing V, he's from behind", and the same at
        // "Ledger's closed."
        //
        // The workspot plays THROUGH this device, so the device's transform wins
        // over whatever orientation the puppet has. With no orientation set the
        // spec gets identity - yaw 0 - so Johnny faced world north in every
        // beat, regardless of where V was standing. That is why most beats
        // looked right: V happened to be facing the right way. It was luck, not
        // placement, and the two beats that failed are the two where V's facing
        // is fixed by the furniture (the office desk) or by the approach (over
        // Hoshino's body).
        //
        // `angles` above already holds the heading from the spot back to V. It
        // was computed and then never used - the line below is the whole fix.
        //
        // THIS WAS KNOWN AND WAS LOST IN THE PORT. The script-owned SpawnJohnny
        // carried this exact line and a comment recording the same symptom found
        // on 2026-08-12; when placement moved to the scene-owned path the
        // position came across and the orientation did not. When porting a
        // routine, port what its comments say it learned, not only what it does.
        let des: ref<DynamicEntitySystem> = GameInstance.GetDynamicEntitySystem();
        if !this.m_lipWsSpawned {
            let dev: ref<DynamicEntitySpec> = new DynamicEntitySpec();
            dev.templatePath = r"mod\\negative_balance\\entity\\cc_g01_workspot.ent";
            dev.position = spot;
            dev.orientation = EulerAngles.ToQuat(angles);
            dev.persistState = false;
            dev.persistSpawn = false;
            dev.alwaysSpawned = false;
            dev.spawnInView = true;
            dev.active = true;
            dev.tags = [n"cc_g01_lip_ws"];
            this.m_lipWsId = des.CreateEntity(dev);
            this.m_lipWsSpawned = true;
            return;      // let it stream in; the next tick puts him in it
        }
        let device: ref<GameObject> = des.GetEntity(this.m_lipWsId) as GameObject;
        if !IsDefined(device) {
            return;      // still streaming - try again next tick
        }
        GameInstance.GetWorkspotSystem(this.GetGameInstance())
            .PlayInDeviceSimple(device, johnny, false, n"cc_g01_johnny_stand");

        // ...AND MATERIALISE HIM HERE, so the arrival reads as deliberate.
        //
        // He is already visible at the marker by the time we move him, so the
        // move is seen. Firing his own arrival effect at the DESTINATION covers
        // it: the glitch happens where he ends up rather than where he came
        // from, which is the same cut-on-the-flash trick as his exit.
        //
        // `johnny_teleport_end` is the arriving counterpart of
        // `johnny_teleport_start`, and both are declared in johnny.ent's
        // entEffectSpawnerComponent - shipped names, not guesses. A wrong CName
        // does nothing at all and is indistinguishable from the bug you are
        // fixing, so they come from that list only (docs/scene-playbook.md).
        // THE ARRIVAL FX IS DEFERRED ONE POLL: the deferral is the T-pose fix.
        //
        // playtest, 2026-08-14: *"during the glitch he has his arms like open
        // like the da vinci man"*. That is the bind pose: the effect used to
        // fire in the same frame as PlayInDeviceSimple, before the workspot's
        // idle had taken over the skeleton, so the glitch played over an
        // unanimated puppet. 150 ms later he is standing properly and the
        // glitch reads as it does everywhere else.
        //
        // NOTHING ABOUT THE ANIMATION CHANGES - the design asked for the appear/
        // disappear to be left alone if touching it caused problems, and this
        // does not touch it. Only when the effect starts.
        this.m_lipFxPending = true;

        // ...AND BOOK HIS EXIT NOW, because nothing else will.
        //
        // A scene despawns its spawnDespawn actors the frame it exits, so the
        // scene's Johnny POPS - and calibrated in playtest the alternative by ear
        // across three values in August: glitch, then delete 0.25 s later,
        // cutting on the flash. That calibration is not being thrown away just
        // because the body changed owner.
        //
        // HIS EXIT IS NOT BOOKED HERE ANY MORE, which is the fix rather than
        // an omission. It used to be a DelayCallback at placement + 7.29 s -
        // the scene's length minus the calibrated cut - which anchored the one
        // fixed thing in the beat to the one thing that varies. Measured
        // 2026-08-14: placement landed 5.5 s into a 7.8 s scene, so the glitch
        // was scheduled for five seconds after the scene had deleted him.
        //
        // The scene fires `cc_g01_johnny_exit` from an events socket 250 ms
        // before its last section ends, and the poll above catches it within
        // 150 ms. No constant is mirrored between the two files now.
        this.m_lipMove = 2;
    }

    // ======================================================================
    // THE SCRIPT-OWNED JOHNNY IS GONE. Deleted 2026-08-14, after the playthrough.
    // ======================================================================
    //
    // SpawnJohnny, ProbeJohnny, EnterJohnnyWorkspot, SetJohnnyFace,
    // ProbeJohnnyWorkspot, LeaveJohnny, DissolveJohnny, DespawnJohnny,
    // JohnnyObject, the m_johnny* fields and the cc_g01_dbg_johnny* facts all
    // lived between here and the next section. They had been inert since every
    // beat became scene-owned - m_johnnySpawned could no longer become true -
    // and were kept only as a fallback until playtesting had covered the gig through.
    // He has, twice, and the verdict was "Perfect", so live code that does
    // nothing is now just an invitation to debug it.
    //
    // What that path knew, and where it survives:
    //
    //   placement    ArmLipPlacement / PlaceSceneJohnny above. The offsets were
    //                copied from its SpawnJohnny calls and are not to be
    //                re-derived; `Teleport` is NOT the way to place a puppet
    //                (it ignores the position and drops him on the player), so
    //                the workspot device is.
    //   FACING       the device's orientation is what he ends up facing. This
    //                is the one thing the port lost, and it cost the 2026-08-14
    //                "he's from behind" report - see PlaceSceneJohnny.
    //   the exit     glitch on johnny_teleport_start, delete 0.25 s later,
    //                calibrated by ear across 1.2 / 0.45 / 0.25 s. The scene
    //                times it now (LipExitJohnny); the 0.25 s is unchanged.
    //   his face     SetJohnnyFace applied a facial preset from
    //                ReactionComponent's own table (3/7 = disgust, 3/1 =
    //                aggressive). Nothing sets one on the scene's actor - see
    //                docs/backlog.md if his expression ever reads blank.
    //
    // Johnny's own FX names, which are shipped and must never be guessed:
    // johnny_teleport_start / johnny_teleport_end / johnny_appear_glitch /
    // johnny_spawn_slow / johnny_spawn_normal / johnny_spawn_fast / glitch /
    // johnny_glitch_idle_01..03. A wrong CName does NOTHING and looks exactly
    // like the bug you are chasing.

    // CloseAfter(fact, seconds) and SetFactNow lived here. They delayed a
    // quest-advancing fact until a caption had been read, because the objective
    // banner, the completion UI and the reward notification all draw OVER a
    // subtitle and once ate a line whole. Removed 2026-08-13 with the captions:
    // the quest phase owns that timing now (a scene tail plus an add_delay), and
    // the rule survives in gen_questphase.py where it is enforced.

    // REMOVED, both of them, and worth saying why so nobody rebuilds them:
    //
    // SetInteractions(obj, enable) queued an InteractionSetEnableEvent to switch
    // an object's interaction prompts off - the way VehicleComponent hides a
    // car's trunk prompt. It does NOT suppress an NPC's dialogue: Mama Welles
    // kept offering her normal conversation right through the epilogue
    // (playtest, 2026-08-12). Deleted rather than left in place, because a failed
    // re-enable would leave a base-game NPC mute for the rest of the save - a
    // real risk in exchange for nothing. the design call: accept vanilla's options.
    //
    // ChoiceHubUp() read UIInteractions.DialogChoiceHubs to hold a beat back
    // while a menu was on screen. It worked, and it STRANDED THE GIG - Johnny
    // never appeared at the bar and the quest could not close. Presentation is
    // not worth gating completion on.
    //
    // "V is plugged into something" - the estate terminal's upload waits on this.
    //
    // There is NO query API for the active UI context on UISystem, so this reads
    // the player state machine blackboard, which `deviceBase
    // .SetZoomBlackboardValues` drives for every device zoom however it is
    // entered or left (docs/computer-ui-playbook.md).
    //
    // Two flags, not one. IsUIZoomDevice is the screen actually being up;
    // IsInteractingWithDevice is the broader "engaged with a device" state and
    // covers anything there that does not zoom. Either counts as plugged in -
    // being strict here risks a gig that cannot be finished, and the failure
    // would look like nothing at all happening.
    //
    // DO NOT swap this for wrapping OnToggleZoomInteraction and reading
    // IsAdvancedInteractionModeOn(). It looks right and it compiles, and closing
    // a computer screen does not route through it, so it never fires - tested
    // 2026-08-11 and written up in the playbook.
    // ------------------------------------------------------------------- HUD
    // SimpleMessageType drives the colour of the banner: Neutral reads blue,
    // Negative red, Connection is the netrunner/link styling.
    // The ledger download, played once V is off the terminal screen (the HUD is
    // hidden while the device zoom is up). The last step sets
    // cc_g01_terminal_done, so the "get clear of the compound" objective only
    // appears after the data is actually away.
    // THREE steps, not five. "SENDING TO NIX... / SENT." used to be steps 3 and
    // 4 and it was invented: in the comic V copies the records, unplugs, and
    // only works out on the way out that he needs a netrunner (p25), then calls
    // Nix from the street (p26). Nothing is transmitted from inside the
    // building - which is also why the gig already holds Nix's call until V is
    // clear of the compound.
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

    private func SpawnMamaWelles() -> Void {
        if !IsDefined(TweakDBInterface.GetCharacterRecord(this.MamaRecord())) {
            return;
        }
        this.m_mamaId = CCSharedWorld.Spawn(this.MamaRecord(), CCGig01Places.MamaWelles(),
            CCGig01Places.MamaWellesYaw(), n"cc_g01_mama");
        this.m_mamaSpawned = true;
    }

    // Only ever removes OUR stand-in. m_mamaSpawned is false when the real Mama
    // Welles was found, so the base-game NPC is never deleted.
    public func DespawnMamaWelles() -> Void {
        if this.m_mamaSpawned {
            GameInstance.GetDynamicEntitySystem().DeleteEntity(this.m_mamaId);
            this.m_mamaSpawned = false;
        }
    }

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

            // MOVE THE SCENE'S JOHNNY IN FRONT OF V.
            //
            // Gated on the arasaka beat's own window. (The dev-button route is
            // gone - see gen_questphase.py: a scene node cannot be entered from
            // two places, which is why neither shortcut button ever worked).
            // NOT gated on anything the test measures - if no second Silverhand
            // is found, that is RECORDED as 1 rather than silently skipped.
            //
            // Outside the `accepted` block on purpose: gating a diagnostic
            // behind a fact set downstream of the beat is the mistake that
            // wasted a whole run on 2026-08-14.
            //
            // Deliberately excludes gig01_bar, whose Johnny is a scene actor
            // already placed correctly by a FIXED anchor 1.65 m from the
            // stools. Moving him in front of V would break a working beat.
            //
            // 1.8 / 1.1 are SpawnJohnny's own street numbers: ahead and to the
            // right, in shot without blocking the view.
            // (the arasaka beat's placement is armed from its own window inside
            // the `accepted` block below, where SpawnJohnny used to be)

            if accepted && qs.GetFactStr("cc_g01_done") == 0 {
                // Arrive at the compound: mark the objective, populate the site.
                if Vector4.Distance(pos, CCGig01Places.CompoundEntry()) < 60.0 {
                    if qs.GetFactStr("cc_g01_office_reached") == 0 {
                        qs.SetFactStr("cc_g01_office_reached", 1);
                    }
                    if !this.m_officeSpawned {
                        this.m_officeSpawned = true;
                        this.SpawnOfficeSecurity();
                    }
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
                // (tools/gen_shard_ent.py and cc_g01_shard.ent stay in the tree.
                // They are a WORKING recipe for a custom interactable - the
                // prompt half is proven - and gigs 02-04 may want one somewhere
                // that has no convenient shard. Nothing spawns it today).

                // THE SHARD IS READ BY WALKING UP TO IT. the design call after
                // seven attempts at an [F] prompt: "let's put back the duplicate
                // shard, and start reading it on proximity rather than action."
                //
                // The object is real, visible and pinned - tools/gen_sector.py
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
                // and ArmLipPlacement(6, ...) places him. A scene-owned body
                // needs no re-staging because it did not exist a moment earlier.

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
                    if CCSharedWorld.Near(pos, CCGig01Places.EstateGate(), 45.0, 12.0, 25.0)
                        || CCSharedWorld.Near(pos, CCGig01Places.Hoshino(), 70.0, 12.0, 25.0) {
                        if qs.GetFactStr("cc_g01_estate_reached") == 0 {
                            qs.SetFactStr("cc_g01_estate_reached", 1);
                        }
                        if !this.m_estateSpawned {
                            this.m_estateSpawned = true;
                            this.SpawnEstateSecurity();
                        }
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
                            // WHICH MAMA DID WE JUST FIND? The query matches on
                            // the record, and OUR stand-in carries the same one,
                            // so "found" alone does not answer it - m_mamaSpawned
                            // does. This is the whole point of the fact:
                            //
                            //   1  the base-game Mama is in the bar. The quest
                            //      phase plays gig01_epilogue, which ACQUIRES
                            //      her - and acquiring her is what shuts her
                            //      ordinary bar conversation up. That was the
                            //      1.0.0 bug: our scene spawned a copy under the
                            //      floor and never claimed her, so her chit-chat
                            //      could win the approach (backlog 7d).
                            //   2  she is not, and this is our own stand-in. The
                            //      phase plays gig01_epilogue_standin instead.
                            //
                            // GETTING THIS WRONG IS NOT COSMETIC. gig01_epilogue
                            // spawns nobody; entering it with no base-game Mama
                            // to acquire leaves the scene holding an actor that
                            // never resolved, which is what crashed the
                            // game at scene teardown in August.
                            //
                            // Set BEFORE cc_g01_mama_reached: that fact releases
                            // the phase into the fork, and the fork reads this
                            // one.
                            if this.m_mamaSpawned {
                                qs.SetFactStr("cc_g01_mama_present", 2);
                            } else {
                                qs.SetFactStr("cc_g01_mama_present", 1);
                            }
                            qs.SetFactStr("cc_g01_mama_reached", 1);
                        }
                    } else {
                        // Only conclude she is absent after a few misses: right
                        // after stepping inside, the interior NPCs may not have
                        // streamed in yet, and spawning on the first miss would
                        // double her up. Measured against her own spot, not the
                        // bar marker, which sits ~10 m away from it.
                        if Vector4.Distance(pos, CCGig01Places.MamaWelles()) < 15.0 {
                            this.m_mamaMissingTicks += 1;
                            if !this.m_mamaSpawned && this.m_mamaMissingTicks >= 4 {
                                this.SpawnMamaWelles();
                            }
                            // Last resort. If she is neither found nor spawnable
                            // after a good while, play the epilogue anyway rather
                            // than strand the final objective, an ending that
                            // cannot be finished is worse than one without her.
                            if this.m_mamaMissingTicks >= 30 {
                                this.m_epilogueBusy = true;
                                // Neither found nor spawnable. 2 = play the
                                // stand-in variant, which spawns its own speaker
                                // and therefore still runs with nobody in the
                                // room; the real-Mama variant would sit waiting
                                // for an actor that cannot arrive and take the
                                // ending with it.
                                qs.SetFactStr("cc_g01_mama_present", 2);
                                qs.SetFactStr("cc_g01_mama_reached", 1);
                            }
                        }
                    }
                }
            }

            // ---------------------------------------------------- JOHNNY
            //
            // THE SCRIPT OWNS HIS BODY AGAIN, and the scenes own his words.
            //
            // The first cut of the caption conversion made him a present actor
            // inside each scene, positioned by a spawnOffset copied from the
            // SpawnJohnny call it replaced. That was a unit error: `ahead` and
            // `aside` are FORWARD and SIDEWAYS in the player's frame, and a
            // Transform's X and Y are map axes, so he stopped tracking which way
            // V faces. Playtest: "before Johnny appeared right in front of V, now
            // it seems he's behind." It cannot be fixed by choosing better
            // numbers - the rotation of an around_player marker is not knowable,
            // and vanilla's only Tag-staged Johnny scene does not offset from it
            // at all (its actor carries its own spawnMarkerNodeRef).
            //
            // So: SpawnJohnny does the placement (real player-relative maths),
            // the script workspot renders the apparition, DissolveJohnny gives
            // him the calibrated 0.25 s exit - all three confirmed in game - and
            // the scene's own Johnny actor is buried 2.5 m down, purely so the
            // line has a speaker close enough to be HEARD and a Character record
            // to take his name from.
            //
            // Each beat spawns him on the fact its scene waits on, so he is
            // standing there before the scene starts talking.
            // BOUNDED BY johnny_done, LIKE THE OTHER TWO - and this one is a
            // REGRESSION FIX, 2026-08-13: "Johnny no longer appears to say
            // 'fucking Arasaka', what happened??"
            //
            // What happened is that this window used to close on
            // cc_g01_call_done, and earlier the same day the holocall tick was
            // sped up from 2.0 s to 0.2 s while a call is hanging up - to close
            // the silence before this very line. That turned a window with up to
            // two seconds of slack into one about a fifth of a second wide,
            // and the encounter tick only runs every 1.5 s. The spawn became a
            // race against a timer it usually lost.
            //
            // A staging window must be bounded by the beat, never by a timer
            // somewhere else that happens to be nearby. johnny_done is the
            // quest phase's own "he is finished here" signal: it is set to 0
            // before the arasaka scene and to 1 after it, which marks out this
            // window and nothing else.
            //
            // terminal_left <= 0 keeps it from reopening at the office, where
            // johnny_cue is still set and johnny_done goes back to 0.
            if qs.GetFactStr("cc_g01_johnny_cue") > 0
                && qs.GetFactStr("cc_g01_terminal_left") <= 0
                && qs.GetFactStr("cc_g01_johnny_done") <= 0 {
                // ============================================================
                // NO SCRIPT-SPAWNED JOHNNY IN THIS BEAT ANY MORE. 2026-08-14.
                // ============================================================
                //
                // There is ONE Johnny here now: the scene's own actor. He is
                // the line's SPEAKER, so he lipsyncs (which a script-spawned
                // body can never do - nothing can bind a scene line to it), and
                // this script does the two jobs the scene cannot: it PLACES him
                // in front of V, and it gives him his exit glitch.
                //
                // The old call was `SpawnJohnny(player, 1.8, 1.1, 7)`, and its
                // numbers live on in PlaceSceneJohnny - they were tuned by hand
                // against real geometry and are not to be re-derived.
                //
                // What is lost with it: the facial preset (arg 7, "disgust"),
                // which SetJohnnyFace applied to the script's puppet. Nothing
                // sets a face on the scene's actor yet. Worth restoring if his
                // expression reads blank, and it is the same helper - it just
                // needs the found GameObject rather than m_johnnyId.
                this.ArmLipPlacement(1, 1.8, 1.1);   // beat 1: arasaka
            }
            // THE SCRIPT-OWNED JOHNNY'S LIVENESS CHECK WAS HERE - "marked
            // spawned but does not resolve -> respawn", plus a per-tick
            // re-assertion of his workspot. Deleted 2026-08-14 with the body it
            // watched; the scene owns and removes its own actor now.
            //
            // Its two lessons are in docs/gotchas.md #15: treat absence as
            // meaningful only after the entity has resolved once, and "still
            // there" is not "still
            // visible" - `phantomVisibleStates` is ["RootMotion","Workspot"], so
            // he renders only while workspotted.

            // THE WINDOWS ARE BOUNDED BY cc_g01_johnny_done, NOT BY THE SCENE
            // THAT OPENED THEM. Playtest, twice: "Johnny must stay present until
            // the last dialogue, not disappear after the first one", and then
            // "I didn't see Johnny staying there to wait for the shard".
            //
            // The first fix was in the quest phase - stop setting johnny_done
            // between beats - and it was necessary but not sufficient. These
            // conditions ALSO closed early: the office one ended at
            // cc_g01_terminal_done, which the graph sets the moment the p22
            // conversation is over, so from p25 onward nothing was re-staging
            // him. Anything that removed him after that - a scene taking over
            // the actor, a streaming hiccup - was permanent.
            //
            // Bounding both windows by johnny_done instead makes the tick
            // SELF-HEALING: SpawnJohnny returns immediately when he is already
            // there, and if he ever goes missing inside a window he is back
            // within one tick. The quest phase owns exactly one signal for "he
            // is finished here", which is what it was always meant to be.
            //
            // The two windows must not overlap, hence ledger_sent on the first:
            // both call SpawnJohnny with different offsets and whichever ran
            // first would win, putting the street Johnny at the office's
            // nose-to-the-wall offset.
            // ONE WINDOW PER SCENE NOW, NOT ONE PER STAGING.
            //
            // That distinction did not exist while the SCRIPT owned the body:
            // one spawn covered the desk conversation, the walk to the shard and
            // the "Figures." beat, and he simply stayed. A scene-owned body is
            // different - each scene spawns and removes its own, so each scene
            // needs its own staging.
            //
            // playtest, 2026-08-14: *"Johnny doesn't re-appear after we read the
            // shard."* The window below used to run from cc_g01_terminal_left
            // all the way to johnny_done, covering BOTH scenes - and
            // ArmLipPlacement's one-staging-per-beat guard is what made that
            // fatal: the terminal scene set m_lipDone for beat 2, and every
            // later call in the same window was refused. He was never staged
            // for the shard beat at all.
            //
            // shard_found closes the first window, so it ends when V walks off
            // to the desk - which is also exactly where he should stop being
            // there ("look for the shard, Johnny no longer there").
            if qs.GetFactStr("cc_g01_terminal_left") > 0
                && qs.GetFactStr("cc_g01_shard_found") <= 0
                && qs.GetFactStr("cc_g01_ledger_sent") <= 0
                && qs.GetFactStr("cc_g01_johnny_done") <= 0 {
                // Almost entirely to the SIDE: V is nose to a screen against a
                // wall, so "ahead" would be inside it.
                this.ArmLipPlacement(2, 0.5, 1.4);   // beat 2: terminal (p22+p25)
            }
            // ...and back for "Figures." the moment the reader closes.
            // cc_g01_shard_read is set by Gig01_Shard's wrap on the popup
            // closing, and the quest phase enters gig01_shard_read on it - so
            // this arms as the scene starts and he is placed ~300 ms in, before
            // V's first line. He stays until the scene's own exit cue, 250 ms
            // before it ends, which is 2 s after "Figures."
            //
            // V is at the desk here, not against a wall, so he gets the street
            // offset rather than the nose-to-the-screen one.
            if qs.GetFactStr("cc_g01_shard_read") > 0
                && qs.GetFactStr("cc_g01_ledger_sent") <= 0
                && qs.GetFactStr("cc_g01_johnny_done") <= 0 {
                this.ArmLipPlacement(6, 1.6, 1.0);   // beat 6: the shard, p24
            }
            // Through the crosswalk AND the whole of Nix's callback - he has two
            // lines at the end of it.
            if qs.GetFactStr("cc_g01_ledger_sent") > 0
                && qs.GetFactStr("cc_g01_nixcall_done") <= 0
                && qs.GetFactStr("cc_g01_johnny_done") <= 0 {
                this.ArmLipPlacement(3, 1.8, 1.1);   // beat 3: the crosswalk
            }
            // ...and back once the phone is DOWN, for p30's two lines.
            // cc_g01_nixcall_done is the call actually hanging up, and the
            // quest phase enters gig01_graves on it - so this arms as that
            // scene starts. Its own window, because one staging per SCENE is
            // the rule now: the crosswalk used to consume this one and Johnny
            // never appeared for the call at all (playtest, 2026-08-14).
            if qs.GetFactStr("cc_g01_nixcall_done") > 0
                && qs.GetFactStr("cc_g01_johnny_done") <= 0 {
                this.ArmLipPlacement(7, 1.8, 1.1);   // beat 7: p30, the graves
            }
            if qs.GetFactStr("cc_g01_hoshino_dead") > 0
                && qs.GetFactStr("cc_g01_malware_done") <= 0 {
                this.ArmLipPlacement(4, 1.6, 1.0);   // beat 4: kill
            }
            if qs.GetFactStr("cc_g01_malware_talk") > 0
                && qs.GetFactStr("cc_g01_escaped") <= 0 {
                this.ArmLipPlacement(5, 1.6, 1.0);   // beat 5: malware
            }

            // The script-owned dissolve on cc_g01_johnny_done was here. The
            // scene times its own exit now - it fires cc_g01_johnny_exit from an
            // events socket 250 ms before its last section ends, and the
            // placement poll catches it within 150 ms (LipExitJohnny). That is
            // the fix from 2026-08-14 for anchoring a fixed thing to a varying
            // one, so this had nothing left to do.

            // Johnny gets the last word, and it is the last word that ends the
            // gig. He is not an actor in the epilogue scene - his character
            // record id is not discoverable offline and guessing TweakDBIDs is
            // how this project broke itself before - so his line stays on the
            // subtitle route and fires when the scene has finished.
            // Johnny's closing line moved INTO gig01_epilogue.scene, where he is
            // a present actor rather than an ownerless subtitle, so there is
            // nothing to play here any more - only the fact that closes the gig
            // and the stand-in cleanup.
            if qs.GetFactStr("cc_g01_epilogue_scene_done") > 0
                && qs.GetFactStr("cc_g01_mama_talked") == 0 {
                qs.SetFactStr("cc_g01_mama_talked", 1);
                this.DespawnMamaWelles();
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
        }
        this.Schedule(1.5);
    }
}

public class CCGig01EncounterTick extends DelayCallback {
    public let system: wref<NegativeBalanceEncounter>;
    public func Call() -> Void {
        if IsDefined(this.system) { this.system.Tick(); }
    }
}

// Fast placement poll for the scene's Johnny. The 1.5 s encounter tick is far
// too coarse for this one job: he materialises at the around_player marker and
// then visibly hops when the tick gets round to moving him. playtest, 2026-08-14:
// *"the glitch appeared behind, and then moved... feels a bit weird."*
// See PlaceSceneJohnnyFast.
public class CCGig01LipPlace extends DelayCallback {
    public let system: wref<NegativeBalanceEncounter>;
    public func Call() -> Void {
        if IsDefined(this.system) { this.system.PlaceSceneJohnnyFast(); }
    }
}

// Fires the scene Johnny's exit glitch 0.25 s before the scene disposes of him.
// See LipExitJohnny.
public class CCGig01LipExit extends DelayCallback {
    public let system: wref<NegativeBalanceEncounter>;
    public func Call() -> Void {
        if IsDefined(this.system) { this.system.LipExitJohnny(); }
    }
}

// CCGig01JohnnyProbe / CCGig01JohnnyDissolve / CCGig01JohnnyWorkspotProbe /
// CCGig01JohnnyLeave were here, driving the script-owned Johnny. Deleted
// 2026-08-14 with the path they served - see the note above SpawnJohnny's
// former home.

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
