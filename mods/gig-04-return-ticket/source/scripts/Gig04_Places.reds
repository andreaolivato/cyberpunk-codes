// Gig 04, Return Ticket: Stamps's death, the Tyger Claws, and Bayani.
//
// Jobs the quest phase cannot do on its own, each a fact read and a fact
// written, on a one-second tick once the gig is running:
//
//   NOT THE THOUSAND. Paying Stamps is the game's own payment option, which
//   takes the money as V picks it (questkit.scene.payment_check). This
//   script took it until 2026-10-01, from the scene's "paid" exit; with
//   both, V would pay twice. What is left here is a readout of the number
//   his Body and Intelligence options ask for (ReadChecks).
//
//   HIS WOUNDS AND HIS DEATH. From the moment his entry is on, his body is
//   looked up in the community each tick. Before he has talked he cannot
//   die: the first wound or knockout sets `cc_g04_stamps_hit`, and the
//   phase reads it as the fight. After he has talked, found and not alive
//   sets `cc_g04_stamps_dead`, which picks Hodan's last call.
//
//   THE CLAWS. A community-placed NPC arrives with no quarrel with the player
//   and with his senses off as far as the player is concerned (gotchas 74 and
//   77), so each of the three is turned on V as his body streams in: attitude
//   AND senses, once per body, remembered by entity id. Only while
//   `cc_g04_room_armed` is set and V is within ArmRadius of the door, so a
//   Claw who streams in a minute after V walks past is caught on the next
//   tick rather than missed by a retry budget (CCShared_Attitude.reds's own
//   note on that failure).
//
// THE BODIES ARE FOUND THROUGH THE COMMUNITY NODE, gig 02's FindInCommunity:
// the community's NodeRef resolved, then GetGameObjectsFromSpawnerEntityID
// by entry name. The dynamic entity system has never heard of a community
// body, so CCSharedAttitude's own lookup falls through to FindEntityByID,
// which does.

module CyberpunkCodes.Gig04
import CyberpunkCodes.Shared.*

public abstract class CCG04Places {
    // tools/gig04/gen_community.py prints it; the two must agree.
    public static func CommunityRef() -> String { return "$/mod/cc_g04_cast/#cc_g04_cast_com"; }
    public static func StampsEntry() -> CName { return n"stamps"; }
    public static func ClawEntries() -> array<CName> {
        return [n"claw1", n"claw2", n"claw3"];
    }
    // THE DOOR (gig04_config.ROOM_DOOR), and how far from it the Claws are
    // turned. 60 m is about the distance a body streams in at.
    public static func Door() -> Vector4 { return new Vector4(-1429.882, 1536.773, 18.193, 1.0); }
    public static func ArmRadius() -> Float { return 60.0; }
    // THE CLAWS' VAN, the false lead (gig04_config.VAN, VAN_PIN): its entry,
    // the marker at its back doors, and how near V has to come for the
    // clue hunt to open.
    public static func VanEntry() -> CName { return n"van"; }
    public static func Van() -> Vector4 { return new Vector4(-1740.0, 1213.0, 18.22, 1.0); }
    public static func VanNear() -> Float { return 20.0; }
    // V HELD STILL while Johnny speaks (source/tweaks/restrictions.yaml,
    // gig 03's hold), for 30 ticks of one second at the most.
    public static func HoldRecord() -> TweakDBID { return t"GameplayRestriction.cc_g04_hold"; }
    public static func HoldCapTicks() -> Int32 { return 30; }
    // ORBITAL AIR'S THREE, one of two sets (gen_community.OA_PL, OA_BASE):
    // its own guards with Phantom Liberty, the game's corporate security
    // without it.
    public static func OAEntries(ep1: Bool) -> array<CName> {
        if ep1 {
            return [n"oa1", n"oa2", n"oa3"];
        }
        return [n"sec1", n"sec2", n"sec3"];
    }
    // Seconds a guard seen once may be missing, with V at the door, before
    // he counts as down; and seconds after which a guard never seen at all
    // counts as down (WatchOA).
    // 3, NOT 20, since 2026-10-25. Playtest: with Orbital Air killed fast,
    // Reynaldo stood in the cell "for at least 30 seconds... even after I
    // already killed everyone"; the log had his hall order 28 s after his
    // talk. Suspected, not proved: a guard who dies between two ticks is no
    // longer listed under the community by the next one, so he is never
    // found dead, only missing, and missing took 20 s. WatchOA now logs how
    // each guard was counted.
    public static func OAGoneTicks() -> Int32 { return 3; }
    public static func OAFloor() -> Int32 { return 90; }
    // THE LAST ONE: once the last guard standing has been out of V's
    // reach for OAStrayTicks seconds of the fight, he counts as down and is
    // called off (WatchOA, "THE STRAY"). Playtest 2026-10-02: every guard V
    // could see was dead and the game still said COMBAT, with "Fight off"
    // on screen, so one was alive somewhere V could not get at.
    public static func OAStrayTicks() -> Int32 { return 15; }
    // SECONDS FROM V'S "WE GOT COMPANY" BEFORE A GUARD STILL OUTSIDE IS
    // TURNED ON V anyway (OAInside). Each is turned the moment he is inside
    // the building; this is for one whose path did not bring him in. A
    // grace before they were told where V is stood here until 2026-10-25,
    // at 0 since the second "too much delay" (2026-10-14).
    public static func OAGoInTicks() -> Int32 { return 5; }
    // Stamps's stars are cleared only with V this near him.
    public static func StampsHeatRange() -> Float { return 40.0; }
    // How far V must be from Stamps before a fight he holds from his bar is
    // taken off him (StampsOutOfFights). The playtest of 2026-11-01 had him
    // at 410 m.
    public static func StampsCalmFrom() -> Float { return 100.0; }
    public static func CarEntry() -> CName { return n"oacar1"; }
    // The waiting spot's pose (gig04_config.RAIL_POSE).
    public static func RailPose() -> Vector4 { return new Vector4(-1477.823, 1548.843, 18.18, 1.0); }
    // THE BUILDING, in the room's frame: V inside it is what the guards'
    // persistent hunt is for (Hunt). `v` runs from the door line inward.
    public static func RoomU() -> Vector4 { return new Vector4(0.9961947, -0.0871557, 0.0, 0.0); }
    public static func RoomV() -> Vector4 { return new Vector4(-0.0871557, -0.9961947, 0.0, 0.0); }
    // LIGAYA'S STALL and STAMPS'S STOOL (gig04_config STALL_LIGAYA,
    // BAR_STAMPS), for the market's switch-off at the end.
    public static func Stall() -> Vector4 { return new Vector4(-1236.688, 1975.171, 7.867, 1.0); }
    // HODAN'S SOFA (tools/fixer01/fixer01_config.FIXER_POS), and how far
    // from it an in-person talk with her is over whatever her graph says.
    public static func FixerSofa() -> Vector4 { return new Vector4(3.227, 10.466, 15.294, 1.0); }
    public static func FixerAway() -> Float { return 100.0; }
    public static func Bar() -> Vector4 { return new Vector4(-1404.26, 1950.77, 23.38, 1.0); }
    // How far V has to be from both before Ligaya and Stamps are switched
    // off, and from the room and the route's end before a Bayani who cannot
    // be found counts as gone.
    public static func FarAway() -> Float { return 150.0; }
    // Seconds of the fight during which Stamps's attitude is written
    // whatever his health (a V may have wounded him before).
    public static func FightAttitudeTicks() -> Int32 { return 3; }
    // How near Ligaya's stall V comes before Hodan rings with the job, and
    // how far V must have been since her introduction first, measured flat
    // (gig04_config.OFFER_RADIUS, OFFER_ARM_RADIUS: Ligaya appears only once
    // V has been away, gotcha 132).
    public static func OfferRadius() -> Float { return 50.0; }
    public static func OfferArmRadius() -> Float { return 250.0; }
    public static func BayaniEntry() -> CName { return n"bayani"; }
    // HIS TWO STANDING SPOTS (gen_community BAYANI_STAND and BAYANI_BYE):
    // in the cell by its door through the fight, in the hall for his
    // goodbye. ByeSpot is the hall spot's place, and ByeArrived how near it
    // he counts as there (gig04_config BYE_ARRIVED): his goodbye waits on
    // `cc_g04_bye_here`.
    public static func StandSpotRef() -> String { return "$/mod/cc_g04_cast/#cc_g04_bayani_stand"; }
    public static func ByeSpotRef() -> String { return "$/mod/cc_g04_cast/#cc_g04_bayani_bye"; }
    public static func ByeSpot() -> Vector4 { return new Vector4(-1431.445, 1530.385, 18.193, 1.0); }
    public static func ByeArrived() -> Float { return 1.5; }
    // Seconds after his talk during which he is pulled out of his pose.
    public static func RouseTicks() -> Int32 { return 6; }
    // STAMPS GOES DOWN at this much health in the fight, in percent (gig
    // 02's merc, MercDownAt).
    public static func StampsDownAt() -> Float { return 33.0; }
    public static func StampsRecord() -> TweakDBID { return t"Character.cc_g04_stamps"; }
    public static func StampsShield() -> CName { return n"cc_g04_stamps"; }
    // THE BUILDING'S DOORS, the gig's own nodes (tools/gig04/gen_room.py):
    // the street door and the cell's.
    public static func DoorRef() -> String { return "$/mod/cc_g04_room/#cc_g04_room_door"; }
    public static func CellDoorRef() -> String { return "$/mod/cc_g04_room/#cc_g04_cell_door"; }
    // WHERE BAYANI RUNS TO: his sister's stall in Kabuki market, 3 m in
    // front of her (gig04_config.LEAVE_END), 820 m from the door.
    public static func LeaveSpot() -> Vector4 {
        return new Vector4(-1233.8, 1974.2, 7.87, 1.0);
    }
    // WHEN HE IS OUT OF SIGHT: behind V and this far off, or this far off
    // whichever way V faces.
    public static func GoneBehind() -> Float { return 30.0; }
    public static func GoneAnyway() -> Float { return 70.0; }
    public static func GoneAtEnd() -> Float { return 12.0; }
}

public class ReturnTicketPlaces extends ScriptableSystem {

    private let m_settled: Bool;
    // The Claws already turned on V, by entity id. NOT A ONE-SHOT LATCH: a
    // community body keeps its id across a respawn, and one that came back
    // would come back with the record's default attitude.
    private let m_turned: array<EntityID>;
    // Bayani's bodies made invulnerable, by entity id, for the same reason.
    private let m_shielded: array<EntityID>;
    // Bayani's bodies sent out of the room, by entity id.
    private let m_sent: array<EntityID>;
    // Seconds of RouseBayani so far (RouseTicks bounds it).
    private let m_roused: Int32;
    // Bayani's bodies sent to his standing spot in the cell, and to his
    // spot in the hall, by entity id (PlaceBayani).
    private let m_standSent: array<EntityID>;
    private let m_byeSent: array<EntityID>;
    // HIS WALK TO THE HALL (WalkToHall, TraceBye): each body sent, the tick
    // it was sent and where he stood then.
    private let m_walkSent: array<EntityID>;
    private let m_byeTick: Int32;
    private let m_byeFrom: Vector4;
    // HIS RUN (TraceRun): the tick it was ordered and where he stood then.
    private let m_runTick: Int32;
    private let m_runFrom: Vector4;
    // THE ORDER HE IS ON, so the next one can cancel it (PlaceBayani).
    private let m_bayaniCmd: ref<AIUseWorkspotCommand>;
    // Orbital Air's bodies already sent after V, by entity id (Hunt).
    private let m_hunting: array<EntityID>;
    // The street door forced open for Orbital Air, once it has worked.
    private let m_oaDoor: Bool;
    // Ticks Bayani could not be found while V was far from him, and ticks
    // the watch has run (WatchBayani).
    private let m_bayaniMissing: Int32;
    private let m_watchTicks: Int32;
    // Bayani's bodies seen since Orbital Air went down, by entity id
    // (SendBayaniOut): a body not seen before, after his run order has
    // gone out, is one a reload put back in the cell.
    private let m_seen: array<EntityID>;
    // THE COMMUNITY, RESOLVED ONCE A TICK (FindInCommunity): the tick count,
    // the tick it was last resolved on, and what it resolved to.
    private let m_tick: Int32;
    private let m_comTick: Int32;
    private let m_comId: EntityID;
    private let m_comOk: Bool;
    // ORBITAL AIR (WatchOA): the guards seen alive at least once, the ones
    // down, how long each seen one has been missing, and how long the
    // fight has been on. Fields, so a reload starts the count again.
    private let m_oaSeen: array<CName>;
    private let m_oaDown: array<CName>;
    private let m_oaMissing: array<Int32>;
    private let m_oaTicks: Int32;
    // THE STRAY (WatchOA): the last guard standing, where and how hurt he
    // was when the count started, and the seconds counted.
    private let m_strayNames: array<CName>;
    private let m_strayPos: array<Vector4>;
    private let m_strayHp: array<Float>;
    private let m_strayTicks: array<Int32>;
    // The room's Claws: seconds V has spent at the door with them armed.
    private let m_roomTicks: Int32;
    // The Claws left standing: for how many seconds none has moved or seen
    // V (ClawsClear).
    private let m_lastClawTicks: Int32;
    // THE TRACE (Trace): the last flags line written, and seconds Ligaya has
    // been missing from her stall with V near it.
    private let m_traceLast: String;
    // The hold (Hold): whether this session applied it, for how many ticks,
    // and whether the first pass of the session has run.
    private let m_holdOn: Bool;
    private let m_holdTicks: Int32;
    private let m_holdChecked: Bool;
    private let m_ligayaMissing: Int32;
    // Guards pushed into combat, and those whose hunt is persistent now.
    private let m_combat: array<EntityID>;
    private let m_persist: array<EntityID>;
    // The two doors given back their own closing, once.
    private let m_doorsBack: Bool;
    // The wait for her last call: when it began on the world clock, and
    // whether the railing has moved the clock on.
    // Orbital Air: seconds since they appeared, and the car locked.
    private let m_oaArmedTicks: Int32;
    // Orbital Air pulled out of their poses (OAOutOfPose), and the guards
    // already logged as turned on V (OAInside).
    private let m_oaRoused: array<EntityID>;
    private let m_oaTurnedLog: array<CName>;
    // Ticks since Orbital Air went down, for TraceAfterFight, and the bodies
    // DropDeadThreats has logged.
    private let m_afterTicks: Int32;
    private let m_threatsDropped: array<EntityID>;
    // The body of each car last locked: a car streamed back in is a new
    // body with its doors unlocked.
    private let m_carLocked: EntityID;
    private let m_vanLocked: EntityID;
    // STAMPS (StampsLife). All fields, none facts: a reload respawns him
    // and every one of these must be applied to the new body again.
    private let m_stampsId: EntityID;
    private let m_stampsMode: Int32;        // 0 no shield, 1 Invulnerable, 2 Immortal
    private let m_stampsFloor: Int32;       // ticks since he went down
    private let m_stampsRoused: Int32;      // ticks of the fast exit at the fight's start
    private let m_stampsNoDismember: Bool;
    private let m_stampsTouched: Bool;      // attitude written since the last reset
    private let m_stampsFightTicks: Int32;  // ticks of the fight so far
    private let m_stampsUnbled: Bool;       // his bleeding taken off after he talked
    private let m_stampsCalmLogged: Bool;   // StampsOutOfFights has logged

    private func OnAttach() -> Void {
        FTLog("[CC.Gig04] places watch attached");
        this.Schedule(5.0);
    }

    public func Schedule(delay: Float) -> Void {
        let cb: ref<CCG04PlacesTick> = new CCG04PlacesTick();
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
        this.m_tick += 1;
        // THE CLAWS' VAN IS LOCKED WHEREVER THE GIG IS: a save from before
        // the van existed has it parked in its lot from load, before the
        // quest's switch-off has ever run (audit 2026-10-13).
        this.m_vanLocked = this.LockCar(game, CCG04Places.VanEntry(), this.m_vanLocked);
        // HODAN FREE TO RING, `cc_g04_fixer_free`, which her three calls wait
        // on. Her graph keeps `cc_f01_talk_mode` at 1 while V talks to her in
        // person and at 2 on the phone. Leaving her in-person talk by fast
        // travel or a teleport may leave it at 1 for good (suspected,
        // playtest 2026-10-13: the gig's call never came at the stall), so
        // an in-person talk counts as over once V is FixerAway from her
        // sofa. A phone call is never overruled.
        let pf: ref<PlayerPuppet> = ps.GetLocalPlayerMainGameObject() as PlayerPuppet;
        if IsDefined(pf) {
            let mode: Int32 = qs.GetFactStr("cc_f01_talk_mode");
            let away: Bool = Vector4.Distance(pf.GetWorldPosition(), CCG04Places.FixerSofa()) > CCG04Places.FixerAway();
            this.SetFact(qs, "cc_g04_fixer_free", (mode <= 0 || (Equals(mode, 1) && away)) ? 1 : 0);
            this.WatchLigaya(game, qs, pf);
            this.Trace(game, qs, pf);
            this.Hold(game, qs, pf);
        }
        // DONE, AND THE MARKET LEFT BEHIND. The quest switches Ligaya and
        // Stamps off only once V is far from both (`cc_g04_market_far`), so
        // this keeps a slow tick going past the end until it has.
        if qs.GetFactStr("cc_g04_done") > 0 {
            if qs.GetFactStr("cc_g04_market_off") > 0 && qs.GetFactStr("cc_g04_room_off") > 0 {
                this.m_settled = true;
                return;
            }
            let pl: ref<PlayerPuppet> = ps.GetLocalPlayerMainGameObject() as PlayerPuppet;
            if IsDefined(pl) {
                this.WatchMarket(qs, pl);
                // BAYANI OUT OF SIGHT, still watched after the close: a V who
                // takes her call before he is gone closes the gig first, and
                // the cast's switch-off waits on `cc_g04_bayani_gone` (audit
                // 2026-10-13).
                if qs.GetFactStr("cc_g04_watch_gone") > 0 && qs.GetFactStr("cc_g04_bayani_gone") <= 0 {
                    this.WatchBayani(game, qs, pl);
                }
                this.SetFact(qs, "cc_g04_room_far",
                             Vector4.Distance(pl.GetWorldPosition(), CCG04Places.Door()) > CCG04Places.FarAway() ? 1 : 0);
            }
            // She keeps her shield and her face while she stands there.
            this.ShieldLigaya(game, qs);
            this.KeepLook(game, n"ligaya", n"service__vendor_wa_vendor_asian_03");
            this.Schedule(5.0);
            return;
        }
        // NOT STARTED: THE OFFER. Once her introduction is done, V within
        // OfferRadius of Ligaya's stall sets `cc_g04_near_offer`, which
        // starts her call (gen_questphase, "THE OFFER"; the design call,
        // 2026-10-13). Every two seconds once she has introduced herself,
        // every five before.
        if qs.GetFactStr("cc_g04_started") <= 0 {
            // LIGAYA KEEPS THE STALL FROM THE START (gen_questphase), so her
            // shield does too: a V who shot her before the gig would have no
            // client. And her face.
            this.ShieldLigaya(game, qs);
            this.KeepLook(game, n"ligaya", n"service__vendor_wa_vendor_asian_03");
            if qs.GetFactStr("cc_f01_intro_done") <= 0 {
                this.Schedule(5.0);
                return;
            }
            if qs.GetFactStr("cc_g04_near_offer") <= 0 {
                let pv: ref<PlayerPuppet> = ps.GetLocalPlayerMainGameObject() as PlayerPuppet;
                // ARMED once V has been OfferArmRadius from both the stall and
                // Stamps's bar since her introduction (`cc_g04_offer_armed`,
                // saved): the quest switches Stamps on at that moment. Read it
                // on the dev panel: 0 means V has not been far enough away yet.
                if IsDefined(pv)
                    && Vector4.Distance2D(pv.GetWorldPosition(), CCG04Places.Stall()) > CCG04Places.OfferArmRadius()
                    && Vector4.Distance2D(pv.GetWorldPosition(), CCG04Places.Bar()) > CCG04Places.OfferArmRadius() {
                    this.SetFact(qs, "cc_g04_offer_armed", 1);
                }
                // NOT IN A FIGHT AND NOT IN SOMEBODY ELSE'S SCENE (audit
                // 2026-10-13): the game's own gig checks the player's state
                // before its call. The scene tier
                // is the player state machine's HighLevel: 0 free, 1 the
                // lightest scene, above that a conversation or a cutscene.
                let tier: Int32 = IsDefined(pv)
                    ? pv.GetPlayerStateMachineBlackboard().GetInt(GetAllBlackboardDefs().PlayerStateMachine.HighLevel) : -1;
                let calm: Bool = IsDefined(pv) && !pv.IsInCombat() && tier <= EnumInt(gamePSMHighLevel.SceneTier1);
                // READOUTS for the dev menu: the scene tier, and calm.
                this.SetFact(qs, "cc_g04_dbg_tier", tier);
                this.SetFact(qs, "cc_g04_dbg_calm", calm ? 1 : 0);
                // A READOUT ONLY: whether Ligaya's body is at her stall.
                let ligaya: ref<ScriptedPuppet> = this.FindInCommunity(game, n"ligaya");
                let here: Bool = IsDefined(ligaya) && ligaya.IsAttached()
                    && Vector4.Distance(ligaya.GetWorldPosition(), CCG04Places.Stall()) < 6.0;
                this.SetFact(qs, "cc_g04_dbg_ligaya_here", here ? 1 : 0);
                if calm && qs.GetFactStr("cc_g04_offer_armed") > 0
                    && Vector4.Distance2D(pv.GetWorldPosition(), CCG04Places.Stall()) < CCG04Places.OfferRadius() {
                    qs.SetFactStr("cc_g04_near_offer", 1);
                }
            }
            // STAMPS FROM THE MOMENT HE IS AT HIS BAR, not from the job's
            // start: the quest switches him on at `cc_g04_offer_armed`, and
            // until the job began nothing shielded him (audit 2026-11-01: a
            // V who shot him then was told he was dead in her last call).
            let early: ref<PlayerPuppet> = ps.GetLocalPlayerMainGameObject() as PlayerPuppet;
            if qs.GetFactStr("cc_g04_offer_armed") > 0 && IsDefined(early) {
                this.WatchStamps(game, qs, early);
            }
            this.Schedule(2.0);
            return;
        }
        let player: ref<PlayerPuppet> = ps.GetLocalPlayerMainGameObject() as PlayerPuppet;
        if !IsDefined(player) {
            this.Schedule(2.0);
            return;
        }

        // STAMPS'S CHECKS, read out until he has talked.
        if qs.GetFactStr("cc_g04_stamps_talked") <= 0 {
            this.ReadChecks(qs, player);
        }

        this.WatchStamps(game, qs, player);

        // THE THREE INVENTED PEOPLE KEEP THEIR OWN FACES.
        this.KeepLook(game, n"ligaya", n"service__vendor_wa_vendor_asian_03");
        this.KeepLook(game, CCG04Places.BayaniEntry(), n"service__vendor_ma_vendor_asian_02");

        // LIGAYA CANNOT BE KILLED: her conversation is pinned to her body
        // and Bayani's run ends in front of her (audit 2026-10-01).
        this.ShieldLigaya(game, qs);

        // WHICH GUARDS ORBITAL AIR SENDS: its own with Phantom Liberty, the
        // game's corporate security without it. The quest reads this when
        // they arrive (gen_questphase, "Orbital Air").
        this.SetFact(qs, "cc_g04_ep1", IsEP1() ? 1 : 0);

        // V AT THE CLAWS' VAN, which opens the clue hunt.
        if qs.GetFactStr("cc_g04_flop_armed") > 0 {
            // ON FOOT: Johnny's line follows, with V held still for it.
            if Vector4.Distance(player.GetWorldPosition(), CCG04Places.Van()) < CCG04Places.VanNear()
                && !VehicleComponent.IsMountedToVehicle(game, player) {
                qs.SetFactStr("cc_g04_van_near", 1);
            }
        }

        // THE CLAWS, each once, while V is within reach of the door; and
        // Bayani, who cannot be killed; and the walls, which the Claws must
        // walk round.
        if qs.GetFactStr("cc_g04_room_armed") > 0
            && CCSharedWorld.Near(player.GetWorldPosition(), CCG04Places.Door(),
                                  CCG04Places.ArmRadius(), 20.0, 20.0) {
            // Every tick, Bayani's talk or not: a Claw who streams in late
            // is turned too (audit 2026-10-01: after the talk they stood
            // there passive).
            this.TurnGroup(game, qs, CCG04Places.ClawEntries());
            this.ShieldBayani(game, qs);
            // HE GETS UP ON "Yes. I can walk." and stands by the cell door
            // until the fight is over (the design call, 2026-10-14: "gets up.
            // stays still. Moves after fight"). The line raises
            // `cc_g04_bayani_up` (gen_scenes, build_room); the end of the
            // talk does the same job for a line that never raised it. Each
            // body once, a body a reload brings back included.
            if (qs.GetFactStr("cc_g04_bayani_up") > 0 || qs.GetFactStr("cc_g04_room_done") > 0)
                && qs.GetFactStr("cc_g04_oa_clear") <= 0 {
                this.PlaceBayani(game, false);
            }
            // THE CLAWS FIRST: the talk opens once all are down. No stray
            // rule here: idle Claws on their couches stand still and unhurt
            // by design, and it killed them while V was outside (playtest
            // 2026-10-13: "the goons inside disappear").
            if qs.GetFactStr("cc_g04_claws_clear") <= 0 {
                this.ClawsClear(game, qs, player);
            }
            // THE STREET DOOR OPEN FROM HERE ON, not only once Orbital Air
            // comes: the walking mesh crosses the door line now (gen_navmesh,
            // "the threshold"), and a Claw chasing V out to the street must
            // not walk into a shut door (audit 2026-10-02).
            if !this.m_oaDoor {
                this.m_oaDoor = this.OpenDoor(game, qs, CCG04Places.DoorRef(), "cc_g04_dbg_door") > 0;
            }
        }

        // ORBITAL AIR, on the street once V has talked to Bayani: turned on
        // V near the door, and counted down until all three are.
        if qs.GetFactStr("cc_g04_oa_armed") > 0 && qs.GetFactStr("cc_g04_oa_clear") <= 0 {
            // THE SET THE QUEST SWITCHED ON (`cc_g04_oa_set`), not re-derived.
            let set: Int32 = qs.GetFactStr("cc_g04_oa_set");
            let ep1: Bool = set > 0 ? Equals(set, 1) : qs.GetFactStr("cc_g04_ep1") > 0;
            let oa: array<CName> = CCG04Places.OAEntries(ep1);
            this.m_oaArmedTicks += 1;
            this.m_carLocked = this.LockCar(game, CCG04Places.CarEntry(), this.m_carLocked);
            if CCSharedWorld.Near(player.GetWorldPosition(), CCG04Places.Door(),
                                  CCG04Places.ArmRadius(), 20.0, 20.0) {
                // THE STREET DOOR OPEN, so they can come in: a closed door is
                // a wall to an NPC (Bayani's run, SendBayaniOut), and it
                // shuts behind V. Tried every tick until it has worked: a
                // door not attached yet reads 0 and is tried again.
                if !this.m_oaDoor {
                    this.m_oaDoor = this.OpenDoor(game, qs, CCG04Places.DoorRef(), "cc_g04_dbg_door") > 0;
                }
                // THEY RUN IN FIRST, THEN FIGHT (the design call, 2026-10-25:
                // "they appear where the player cannot see them, then become
                // hostile and ... run inside"). The quest sends each along
                // his path through the door on V's line; here each is pulled
                // out of his standing pose once, so the patrol does not wait
                // behind it (gotcha 135), and is turned on V once he is
                // inside the building, or once OAGoInTicks have passed
                // wherever he is. Turned on V on the street, they fought from
                // out there (playtest 2026-10-14).
                this.OAOutOfPose(game, oa);
                let ready: array<CName> = this.OAInside(game, oa);
                if ArraySize(ready) > 0 {
                    this.TurnGroup(game, qs, ready);
                    this.Hunt(game, qs, player, ready);
                }
            }
            this.WatchOA(game, qs, player, oa);
        }

        // ONCE ORBITAL AIR IS DOWN HE RUNS OUT, once per body; and once he
        // is out of V's sight the quest may switch the cast off. Until
        // 2026-10-01 this went on the end of his talk; the street was empty
        // then.
        if qs.GetFactStr("cc_g04_oa_clear") > 0 {
            // THE DEAD STAY DEAD after the fight too: a reload past the clear
            // put the guards and the Claws back on their feet (audit
            // 2026-10-13). Until the cast is switched off.
            if qs.GetFactStr("cc_g04_room_off") <= 0 {
                let set2: Int32 = qs.GetFactStr("cc_g04_oa_set");
                this.KeepDead(game, qs, CCG04Places.OAEntries(Equals(set2, 1)));
                this.KeepDead(game, qs, CCG04Places.ClawEntries());
                this.m_carLocked = this.LockCar(game, CCG04Places.CarEntry(), this.m_carLocked);
            }
            this.TraceAfterFight(game, qs, player);
            this.SendBayaniOut(game, qs);
            // TO HIS SPOT IN THE HALL once both doors are open (SendBayaniOut
            // has opened them when it has sent the body), each body once,
            // until his goodbye is over. THE WALK IS THE QUEST'S PATROL along
            // gen_room BYE_PATH since 2026-10-25 (WalkToHall raises
            // `cc_g04_bye_go`); the use-workspot order to the hall spot, which
            // did the walk until then and stopped him a step out of the cell
            // every time (the log of 2026-10-25), only holds him there once he
            // has arrived.
            if qs.GetFactStr("cc_g04_bye_done") <= 0 {
                let walker: ref<ScriptedPuppet> = this.FindInCommunity(game, CCG04Places.BayaniEntry());
                if IsDefined(walker) && ArrayContains(this.m_sent, walker.GetEntityID()) {
                    if qs.GetFactStr("cc_g04_bye_here") <= 0 {
                        this.WalkToHall(game, qs, walker);
                        this.TraceBye(game, walker);
                    } else {
                        this.PlaceBayani(game, true);
                    }
                }
            }
            // OUT OF HIS HALL POSE FOR THE RUN, only once his goodbye is
            // over: earlier, the fast exit would take him off his spot. His
            // hall order is cancelled first, or the run waits behind it.
            if qs.GetFactStr("cc_g04_bye_done") > 0 {
                this.ReleaseBayani(game);
                this.RouseBayani(game, qs);
                // AND ONLY NOW THE RUN: the quest's run order waits on this,
                // so it never arrives behind the hall hold (gen_questphase,
                // "HE RUNS OUT"; gotcha 134).
                if qs.GetFactStr("cc_g04_run_go") <= 0 {
                    qs.SetFactStr("cc_g04_run_go", 1);
                    this.m_runTick = this.m_tick;
                    let r: ref<ScriptedPuppet> = this.FindInCommunity(game, CCG04Places.BayaniEntry());
                    if IsDefined(r) {
                        this.m_runFrom = r.GetWorldPosition();
                    }
                    FTLog("[CC.Gig04] Bayani let go of the hall spot, the run can start");
                }
                this.TraceRun(game);
            }
            // ON HIS SPOT IN THE HALL, his goodbye is offered (gen_questphase,
            // "HIS GOODBYE"): a position, never an order's own end.
            if qs.GetFactStr("cc_g04_bye_here") <= 0 {
                let here: ref<ScriptedPuppet> = this.FindInCommunity(game, CCG04Places.BayaniEntry());
                if IsDefined(here) && here.IsAttached()
                    && Vector4.Distance2D(here.GetWorldPosition(), CCG04Places.ByeSpot()) < CCG04Places.ByeArrived() {
                    qs.SetFactStr("cc_g04_bye_here", 1);
                }
            }
            // SHIELDED ON HIS RUN TOO, not only near the room: a body that
            // comes back on the route is a new body (audit 2026-10-02).
            if qs.GetFactStr("cc_g04_mid_done") <= 0 {
                this.ShieldBayani(game, qs);
            }
            // WATCHED ONLY ONCE THE QUEST ASKS (`cc_g04_watch_gone`, set as V
            // leaves the drawn circle). The quest switches the cast off the
            // moment the fact goes up, so it must not go up while he is
            // still in the room with V (audit 2026-10-01).
            if qs.GetFactStr("cc_g04_watch_gone") > 0 && qs.GetFactStr("cc_g04_bayani_gone") <= 0 {
                this.WatchBayani(game, qs, player);
            }
        }

        // THE WAIT FOR HER CALL, MOVED ON AT THE RAILING: gig 02's Waits and
        // SkipAhead (Gig02_Encounter.reds). The quest's wait is two hours of
        // the world clock; this knows how much of it is left, and moves the
        // clock on by that much behind the fade (`cc_g04_rail_shift`).
        // THE START OF THE WAIT AND THE SKIP ARE FACTS, so they are saved: a
        // reload during the wait skipped the clock twice, or more than the
        // two hours, while they were script fields (audit 2026-10-13).
        if qs.GetFactStr("cc_g04_watch_gone") > 0 && qs.GetFactStr("cc_g04_close_step") <= 0 {
            let ts: ref<TimeSystem> = GameInstance.GetTimeSystem(game);
            if IsDefined(ts) {
                if qs.GetFactStr("cc_g04_wait_from") <= 0 {
                    qs.SetFactStr("cc_g04_wait_from", Cast<Int32>(ts.GetGameTimeStamp()));
                }
                if qs.GetFactStr("cc_g04_rail_shift") > 0 && qs.GetFactStr("cc_g04_rail_skipped") <= 0 {
                    qs.SetFactStr("cc_g04_rail_skipped", 1);
                    this.SkipAhead(ts, Cast<Float>(qs.GetFactStr("cc_g04_wait_from")), 7200.0);
                }
            }
        }

        // THE WAITING SPOT LET GO, gig 02's LetGo and StandUp
        // (Gig02_Encounter.reds): once her call has started, a pose the
        // quest cut before its release is released, and V is taken out of
        // the lean if he is still in it near the railing.
        if qs.GetFactStr("cc_g04_close_step") > 0 {
            if qs.GetFactStr("cc_g04_rail_taken") > 0 && qs.GetFactStr("cc_g04_rail_release") <= 0 {
                qs.SetFactStr("cc_g04_rail_release", 1);
            }
        }
        if qs.GetFactStr("cc_g04_rail_release") > 0
            && Vector4.Distance(player.GetWorldPosition(), CCG04Places.RailPose()) < 4.0 {
            let ws: ref<WorkspotGameSystem> = GameInstance.GetWorkspotSystem(game);
            if IsDefined(ws) && ws.IsActorInWorkspot(player)
                && qs.GetFactStr("cc_g04_close_step") > 0 {
                ws.SendFastExitSignal(player, new Vector3(0.0, 0.0, 0.0), false, false, false, true);
            }
        }

        // THE MARKET'S PAIR, switched off by the quest once V is far.
        if qs.GetFactStr("cc_g04_mid_done") > 0 {
            this.WatchMarket(qs, player);
            // THE TWO DOORS CLOSE THEMSELVES AGAIN once the cast is gone:
            // OpenDoor took their self-closing away, and a device's state
            // is in the save (audit 2026-10-02).
            if !this.m_doorsBack {
                this.m_doorsBack = this.CloseItselfAgain(game, CCG04Places.DoorRef())
                    && this.CloseItselfAgain(game, CCG04Places.CellDoorRef());
            }
        }
        // V FAR FROM THE VAN AND FROM THE BAR, for the quest's switch-offs
        // of the van and of a dead Stamps.
        let here: Vector4 = player.GetWorldPosition();
        // V FAR FROM THE ROOM, for the quest's switch-off of the Claws,
        // Orbital Air and the car out of V's sight (audit 2026-10-13: they
        // went the moment Bayani was out of sight, in front of a V on the
        // street).
        this.SetFact(qs, "cc_g04_room_far",
                     Vector4.Distance(here, CCG04Places.Door()) > CCG04Places.FarAway() ? 1 : 0);
        this.SetFact(qs, "cc_g04_flop_far",
                     Vector4.Distance(here, CCG04Places.Van()) > CCG04Places.FarAway() ? 1 : 0);
        this.SetFact(qs, "cc_g04_bar_far",
                     Vector4.Distance(here, CCG04Places.Bar()) > CCG04Places.FarAway() ? 1 : 0);

        this.Schedule(1.0);
    }

    // HE LEAVES BY HIMSELF, on the quest's own patrol order along the route
    // the room ships (gen_questphase, gen_room.LEAVE_PATH_REF). This opens
    // the two doors in his way first, once per body, through their
    // controllers (a closed door is a wall to him; the quest's own
    // ForceOpen action, the one a quest node would send). Playtest
    // 2026-10-01: a second community phase respawned him a few steps into
    // his walk; a scripted move order turned him on the spot and he
    // vanished; before both he knelt in Fear at the back wall (fixed on
    // the record, characters.yaml).
    private func SendBayaniOut(game: GameInstance, qs: ref<QuestsSystem>) -> Void {
        let bayani: ref<ScriptedPuppet> = this.FindInCommunity(game, CCG04Places.BayaniEntry());
        if !IsDefined(bayani) || !ScriptedPuppet.IsAlive(bayani) {
            return;
        }
        let id: EntityID = bayani.GetEntityID();
        // A BODY THE RUN ORDER HAS NOT SEEN: after a reload he is back in the
        // cell and the quest's one patrol order is spent. `cc_g04_bayani_ran`
        // says the quest has sent him once; this asks it to send him again
        // (gen_questphase, "AGAIN AFTER A RELOAD"). Decided the first tick a
        // body is seen, before the doors: on the clear itself that is before
        // the quest has sent him, so his first run is not doubled (audit
        // 2026-10-01, second pass).
        if !ArrayContains(this.m_seen, id) {
            ArrayPush(this.m_seen, id);
            if qs.GetFactStr("cc_g04_bayani_ran") > 0 {
                qs.SetFactStr("cc_g04_bayani_rerun", 1);
            }
        }
        if ArrayContains(this.m_sent, id) {
            return;
        }
        // BOTH DOORS, retried every tick until both report open (1 sent, 2
        // already open); a door not attached yet reads 0 (audit 2026-10-01).
        let cell: Int32 = this.OpenDoor(game, qs, CCG04Places.CellDoorRef(), "cc_g04_dbg_cell_door");
        let street: Int32 = this.OpenDoor(game, qs, CCG04Places.DoorRef(), "cc_g04_dbg_door");
        if cell <= 0 || street <= 0 {
            return;
        }
        ArrayPush(this.m_sent, id);
        qs.SetFactStr("cc_g04_dbg_sent", ArraySize(this.m_sent));
        FTLog("[CC.Gig04] both doors open, Bayani cleared to leave");
    }

    // LIGAYA, INVULNERABLE while the gig runs, each body once; a body whose
    // shield is gone (a respawn under the same id) is shielded again.
    // NOBODY ELSE ON STAMPS'S STOOL. Playtests 2026-10-14, twice, a
    // different woman each time: the crowd sat a passer-by on the stool with
    // him, after the game's own seat there was deleted (the manifest) and
    // with a crowd null area round the bar. Gig 02's answer at the Dewdrop
    // Inn (InnKeeper): any crowd body within a metre of the stool is
    // removed. `IsCrowd` is the whole test, so Stamps, the barkeep and any
    // quest character are left alone (gotcha 112).
    private func ClearStool(game: GameInstance, player: ref<PlayerPuppet>) -> Void {
        let stool: Vector4 = CCG04Places.Bar();
        if Vector4.Distance(player.GetWorldPosition(), stool) > 60.0 {
            return;
        }
        let query: TargetSearchQuery = TSQ_NPC();
        query.testedSet = TargetingSet.Complete;
        query.includeSecondaryTargets = false;
        query.ignoreInstigator = true;
        query.maxDistance = 60.0;
        query.filterObjectByDistance = true;
        let parts: array<TS_TargetPartInfo>;
        GameInstance.GetTargetingSystem(game).GetTargetParts(player, query, parts);
        let i: Int32 = 0;
        while i < ArraySize(parts) {
            let npc: ref<ScriptedPuppet> = TS_TargetPartInfo.GetComponent(parts[i]).GetEntity() as ScriptedPuppet;
            if IsDefined(npc) && !npc.IsPlayer() && npc.IsCrowd()
                && npc.GetRecordID() != CCG04Places.StampsRecord()
                && Vector4.Distance(npc.GetWorldPosition(), stool) < 1.0 {
                FTLog("[CC.Gig04] a passer-by on Stamps's stool, removed: " + TDBID.ToStringDEBUG(npc.GetRecordID()));
                this.DisposeByName(npc);
            }
            i += 1;
        }
    }

    // `Dispose` BY NAME, THROUGH CODEWARE, the long spelling gig 02 uses
    // (Codeware 1.17 has no one-line `Reflection.Call`).
    private func DisposeByName(body: ref<IScriptable>) -> Void {
        let cls: ref<ReflectionClass> = Reflection.GetClassOf(body);
        if !IsDefined(cls) {
            return;
        }
        let fn: ref<ReflectionMemberFunc> = cls.GetFunction(n"Dispose");
        if IsDefined(fn) {
            fn.Call(body);
        }
    }

    private func ShieldLigaya(game: GameInstance, qs: ref<QuestsSystem>) -> Void {
        let ligaya: ref<ScriptedPuppet> = this.FindInCommunity(game, n"ligaya");
        if !IsDefined(ligaya) || !ScriptedPuppet.IsAlive(ligaya) {
            return;
        }
        let gods: ref<GodModeSystem> = GameInstance.GetGodModeSystem(game);
        if !IsDefined(gods) {
            return;
        }
        let id: EntityID = ligaya.GetEntityID();
        if gods.HasGodMode(id, gameGodModeType.Invulnerable) {
            return;
        }
        gods.AddGodMode(id, gameGodModeType.Invulnerable, n"cc_g04_ligaya");
    }

    // THE MARKET LEFT BEHIND: `cc_g04_market_far` once V is FarAway from
    // both Ligaya's stall and Stamps's stool, so the quest switches the two
    // off where nobody sees it.
    private func WatchMarket(qs: ref<QuestsSystem>, player: ref<PlayerPuppet>) -> Void {
        if qs.GetFactStr("cc_g04_market_far") > 0 {
            return;
        }
        let here: Vector4 = player.GetWorldPosition();
        if Vector4.Distance(here, CCG04Places.Stall()) > CCG04Places.FarAway()
            && Vector4.Distance(here, CCG04Places.Bar()) > CCG04Places.FarAway() {
            qs.SetFactStr("cc_g04_market_far", 1);
        }
    }

    // A FACT WRITTEN ONLY WHEN IT CHANGES, for the ones read every tick.
    private func SetFact(qs: ref<QuestsSystem>, name: String, value: Int32) -> Void {
        if qs.GetFactStr(name) != value {
            qs.SetFactStr(name, value);
        }
    }

    // HE GETS UP AT ONCE. He sits on the floor in a community workspot, and
    // the patrol order alone waits for that pose's own slow exit before he
    // moves. Playtest 2026-10-01: "Leave the area" was up and he still sat
    // there; "make it much much faster". The workspot system's fast exit is
    // the signal the game's own takedown sends to pull a seated NPC out
    // (locomotionTakedown.swift), and gig 02 sends it to the player
    // (Gig02_Encounter.reds). Sent each second while he is still in a pose,
    // for the first RouseTicks seconds after the talk only: past that he is
    // running, and a pose he is in later is not this one. Forward in his own
    // space, toward the room; a slow exit if the fast one is refused; a
    // blend into a walk so the run starts from it.
    // `cc_g04_dbg_roused` counts the signals sent.
    private func RouseBayani(game: GameInstance, qs: ref<QuestsSystem>) -> Void {
        if this.m_roused >= CCG04Places.RouseTicks() {
            return;
        }
        let bayani: ref<ScriptedPuppet> = this.FindInCommunity(game, CCG04Places.BayaniEntry());
        if !IsDefined(bayani) || !ScriptedPuppet.IsAlive(bayani) {
            return;
        }
        // Counted from the first tick his body is there, not from the clear:
        // after a reload he may stream in late (audit 2026-10-01, second pass).
        this.m_roused += 1;
        if this.OutOfPose(game, bayani) {
            qs.SetFactStr("cc_g04_dbg_roused", qs.GetFactStr("cc_g04_dbg_roused") + 1);
        }
    }

    // BAYANI TO ONE OF HIS STANDING SPOTS. First the fast exit out of
    // whatever pose he is in: from the floor it is the get-up the game plays
    // when a seated NPC is pulled out, and an order sent to a body still in
    // its sitting pose waits for that pose's slow exit, which on 2026-10-14
    // held the order through the whole fight and dropped the next one (the
    // log: both sent, neither carried out when sent). Then the AI's own
    // use-workspot command, the one every behaviour tree issues when an NPC
    // takes a spot (gig 02's CCLab_UseWorkspot, which seats Char): it walks
    // him there, plays the pose's way in, and holds him in it, so nothing
    // sits him down again. Once per body, so a body a reload brings back is
    // sent again. `hall` false is the cell.
    private func PlaceBayani(game: GameInstance, hall: Bool) -> Void {
        let body: ref<ScriptedPuppet> = this.FindInCommunity(game, CCG04Places.BayaniEntry());
        if !IsDefined(body) || !body.IsAttached() || !ScriptedPuppet.IsAlive(body) {
            return;
        }
        let id: EntityID = body.GetEntityID();
        if hall ? ArrayContains(this.m_byeSent, id) : ArrayContains(this.m_standSent, id) {
            return;
        }
        let spotRef: String = hall ? CCG04Places.ByeSpotRef() : CCG04Places.StandSpotRef();
        let ai: ref<AIHumanComponent> = body.GetAIControllerComponent();
        if !IsDefined(ai) {
            return;
        }
        // THE ORDER BEFORE IS CANCELLED FIRST. A use-workspot order on a
        // spot that holds him never finishes, and the next order waits
        // behind it: after the fight he stood in the cell for a long while
        // with the hall order sent at once (playtest and log, 2026-10-14).
        // CANCEL, THEN THE FAST EXIT, then the order, since 2026-10-25: the
        // fast exit went first until then, and the cancel after it can start
        // the pose's own slow exit. The walk to the hall is not this order
        // any more (WalkToHall); this one only holds him once he is there.
        if IsDefined(this.m_bayaniCmd) {
            ai.CancelCommand(this.m_bayaniCmd);
        }
        this.OutOfPose(game, body);
        let cmd: ref<AIUseWorkspotCommand> = new AIUseWorkspotCommand();
        cmd.workspotNode = CreateNodeRef(spotRef);
        cmd.moveToWorkspot = true;
        cmd.jumpToEntry = false;
        cmd.idleOnlyMode = false;
        cmd.continueInCombat = true;
        ai.SendCommand(cmd);
        this.m_bayaniCmd = cmd;
        if hall {
            ArrayPush(this.m_byeSent, id);
        } else {
            ArrayPush(this.m_standSent, id);
        }
        FTLog("[CC.Gig04] Bayani sent to " + spotRef);
    }

    // HIS WALK TO THE HALL, once per body, once Orbital Air is down and both
    // doors are open: the order to the cell spot cancelled (gotcha 134), the
    // fast exit out of its pose (gotcha 135), then `cc_g04_bye_go`, on which
    // the quest sends him along gen_room BYE_PATH with the patrol order his
    // run uses (gen_questphase, "HIS GOODBYE"). Until 2026-10-25 the
    // use-workspot order to the hall spot did the walk, and the log had it
    // take one step out of the cell and stop in a pose, every time.
    // THE FAST EXIT AGAIN EACH TICK while he is still in a pose, for 40
    // ticks: one signal left him in the cell pose for 45 s while COMBAT
    // held after the fight (playtest and log, 2026-11-01, "posed=1"
    // throughout), where in the run before he was out of it in 4 s.
    private func WalkToHall(game: GameInstance, qs: ref<QuestsSystem>, body: ref<ScriptedPuppet>) -> Void {
        let id: EntityID = body.GetEntityID();
        if ArrayContains(this.m_walkSent, id) {
            if this.m_tick - this.m_byeTick <= 40 && this.OutOfPose(game, body) {
                FTLog(s"[CC.Gig04] Bayani still in a pose \(this.m_tick - this.m_byeTick) s into his walk, fast exit sent again");
            }
            return;
        }
        let ai: ref<AIHumanComponent> = body.GetAIControllerComponent();
        if IsDefined(ai) && IsDefined(this.m_bayaniCmd) {
            ai.CancelCommand(this.m_bayaniCmd);
        }
        this.m_bayaniCmd = null;
        this.OutOfPose(game, body);
        qs.SetFactStr("cc_g04_bye_go", 1);
        ArrayPush(this.m_walkSent, id);
        this.m_byeTick = this.m_tick;
        this.m_byeFrom = body.GetWorldPosition();
        FTLog("[CC.Gig04] Bayani's cell order cancelled, walking to the hall on the path");
    }

    // WHAT HE IS DOING while he should be walking to the hall: every two
    // ticks after the walk is ordered, for 40 ticks at most, until he is
    // there. Added 2026-10-25 when a playtest saw him stand in the cell and
    // the log could not say why: how far he is from the hall spot, how far
    // he has moved since the order, whether he is in a pose, and the AI's
    // own state for him (Relaxed, Alerted, Fear, Combat).
    private func TraceBye(game: GameInstance, body: ref<ScriptedPuppet>) -> Void {
        if !ArrayContains(this.m_walkSent, body.GetEntityID()) {
            return;
        }
        let since: Int32 = this.m_tick - this.m_byeTick;
        if since > 40 || since % 2 != 0 {
            return;
        }
        let ws: ref<WorkspotGameSystem> = GameInstance.GetWorkspotSystem(game);
        let posed: Bool = IsDefined(ws) && ws.IsActorInWorkspot(body);
        let state: String = EnumValueToString("gamedataNPCHighLevelState",
            Cast<Int64>(EnumInt(body.GetHighLevelStateFromBlackboard())));
        let here: Vector4 = body.GetWorldPosition();
        FTLog(s"[CC.Gig04] Bayani \(since) s into his walk: to hall \(Vector4.Distance(here, CCG04Places.ByeSpot())) m, moved \(Vector4.Distance(here, this.m_byeFrom)) m, posed=\(posed ? 1 : 0), state=\(state)");
    }

    // WHO HOLDS THE COMBAT after Orbital Air is down: every two ticks for 60
    // ticks of this session, whether V is still in combat, and each Claw and
    // guard: dead fact, body found, standing, distance to V, attitude to V,
    // whether he sees V, and the AI's own state for him. Added 2026-11-01
    // when a playtest stayed in COMBAT after the last guard died and the log
    // could not say who held it.
    // ITS SECOND HALF, since the playtest of 2026-11-01 that ran it: COMBAT
    // held for 35 s with all three Claws and all three guards dead, and
    // Bayani in his cell pose for as long. Each line now names every entry
    // in V's own threat list as well.
    private func TraceAfterFight(game: GameInstance, qs: ref<QuestsSystem>, player: ref<PlayerPuppet>) -> Void {
        this.m_afterTicks += 1;
        if this.m_afterTicks <= 90 && player.IsInCombat() {
            this.DropDeadThreats(player);
        }
        if this.m_afterTicks > 60 || this.m_afterTicks % 2 != 0 {
            return;
        }
        let set: Int32 = qs.GetFactStr("cc_g04_oa_set");
        let who: array<CName> = CCG04Places.ClawEntries();
        let oa: array<CName> = CCG04Places.OAEntries(Equals(set, 1));
        let j: Int32 = 0;
        while j < ArraySize(oa) {
            ArrayPush(who, oa[j]);
            j += 1;
        }
        let here: Vector4 = player.GetWorldPosition();
        let playerAgent: ref<AttitudeAgent> = player.GetAttitudeAgent();
        let line: String = s"[CC.Gig04] \(this.m_afterTicks) s after the fight: V combat=\(player.IsInCombat() ? 1 : 0)";
        let i: Int32 = 0;
        while i < ArraySize(who) {
            let name: String = NameToString(who[i]);
            line += s" | \(name) dead=\(qs.GetFactStr("cc_g04_dead_" + name))";
            let body: ref<ScriptedPuppet> = this.FindInCommunity(game, who[i]);
            if !IsDefined(body) {
                line += " none";
            } else {
                let agent: ref<AttitudeAgent> = body.GetAttitudeAgent();
                let att: String = "?";
                if IsDefined(agent) && IsDefined(playerAgent) {
                    att = EnumValueToString("EAIAttitude", Cast<Int64>(EnumInt(agent.GetAttitudeTowards(playerAgent))));
                }
                let senses: ref<SenseComponent> = body.GetSensesComponent();
                let sees: Bool = IsDefined(senses) && senses.IsAgentVisible(player);
                let state: String = EnumValueToString("gamedataNPCHighLevelState",
                    Cast<Int64>(EnumInt(body.GetHighLevelStateFromBlackboard())));
                line += s" up=\(ScriptedPuppet.IsActive(body) ? 1 : 0) d=\(Vector4.Distance(body.GetWorldPosition(), here)) \(att) sees=\(sees ? 1 : 0) \(state)";
            }
            i += 1;
        }
        let tt: ref<TargetTrackerComponent> = player.GetTargetTrackerComponent();
        if IsDefined(tt) {
            let threats: array<TrackedLocation> = tt.GetHostileThreats(false);
            line += s" || V's threats \(ArraySize(threats))";
            let k: Int32 = 0;
            while k < ArraySize(threats) {
                line += " | " + this.DescribeThreat(threats[k].entity, here);
                k += 1;
            }
        }
        FTLog(line);
    }

    // One entry of V's threat list for the log: its class, its record if it
    // is a character, whether it stands, and how far it is.
    private func DescribeThreat(et: wref<Entity>, here: Vector4) -> String {
        if !IsDefined(et) {
            return "gone";
        }
        let s: String = NameToString(et.GetClassName());
        let puppet: ref<ScriptedPuppet> = et as ScriptedPuppet;
        if IsDefined(puppet) {
            s += s" \(TDBID.ToStringDEBUG(puppet.GetRecordID())) up=\(ScriptedPuppet.IsActive(puppet) ? 1 : 0)";
        }
        s += s" d=\(Vector4.Distance(et.GetWorldPosition(), here))";
        return s;
    }

    // DEAD AND KNOCKED-OUT BODIES OFF V'S THREAT LIST, after the fight, each
    // tick V is in combat for 90 s. Only bodies that are down (`IsActive`
    // false, gotcha 111); a threat that stands is a fight and stays. The
    // removal is the target tracker's own (`MapThreat`, `RemoveThreat`,
    // targetTrackingComponent.swift). Logged once per body.
    private func DropDeadThreats(player: ref<PlayerPuppet>) -> Void {
        let tt: ref<TargetTrackerComponent> = player.GetTargetTrackerComponent();
        if !IsDefined(tt) {
            return;
        }
        let threats: array<TrackedLocation> = tt.GetHostileThreats(false);
        let k: Int32 = 0;
        while k < ArraySize(threats) {
            let puppet: ref<ScriptedPuppet> = threats[k].entity as ScriptedPuppet;
            if IsDefined(puppet) && !ScriptedPuppet.IsActive(puppet) {
                tt.RemoveThreat(tt.MapThreat(puppet));
                if !ArrayContains(this.m_threatsDropped, puppet.GetEntityID()) {
                    ArrayPush(this.m_threatsDropped, puppet.GetEntityID());
                    FTLog(s"[CC.Gig04] a down body taken off V's threats, \(this.m_afterTicks) s after the fight: \(TDBID.ToStringDEBUG(puppet.GetRecordID()))");
                }
            }
            k += 1;
        }
    }

    // WHAT HE IS DOING once his run is ordered (`cc_g04_run_go`): every two
    // ticks for 20 ticks. Added 2026-10-25 when he stood in the hall after
    // the run was ordered and the log ended at the order: how far he has
    // moved, how far he is from the street door, whether he is in a pose,
    // and the AI's own state for him.
    private func TraceRun(game: GameInstance) -> Void {
        let since: Int32 = this.m_tick - this.m_runTick;
        if since > 20 || since % 2 != 0 {
            return;
        }
        let body: ref<ScriptedPuppet> = this.FindInCommunity(game, CCG04Places.BayaniEntry());
        if !IsDefined(body) {
            FTLog(s"[CC.Gig04] Bayani \(since) s into his run: no body found");
            return;
        }
        let ws: ref<WorkspotGameSystem> = GameInstance.GetWorkspotSystem(game);
        let posed: Bool = IsDefined(ws) && ws.IsActorInWorkspot(body);
        let state: String = EnumValueToString("gamedataNPCHighLevelState",
            Cast<Int64>(EnumInt(body.GetHighLevelStateFromBlackboard())));
        let here: Vector4 = body.GetWorldPosition();
        FTLog(s"[CC.Gig04] Bayani \(since) s into his run: moved \(Vector4.Distance(here, this.m_runFrom)) m, to the street door \(Vector4.Distance(here, CCG04Places.Door())) m, posed=\(posed ? 1 : 0), state=\(state), roused=\(this.m_roused)");
    }

    // HIS HALL ORDER CANCELLED, once, as his goodbye ends, so the quest's
    // run order is the only one he has (PlaceBayani has why).
    private func ReleaseBayani(game: GameInstance) -> Void {
        if !IsDefined(this.m_bayaniCmd) {
            return;
        }
        let body: ref<ScriptedPuppet> = this.FindInCommunity(game, CCG04Places.BayaniEntry());
        if IsDefined(body) {
            let ai: ref<AIHumanComponent> = body.GetAIControllerComponent();
            if IsDefined(ai) {
                ai.CancelCommand(this.m_bayaniCmd);
                FTLog("[CC.Gig04] Bayani's hall order cancelled for the run");
            }
        }
        this.m_bayaniCmd = null;
    }

    // The workspot system's fast exit, for a body in a pose; true when it
    // was sent (RouseBayani has the account).
    private func OutOfPose(game: GameInstance, body: ref<ScriptedPuppet>) -> Bool {
        let ws: ref<WorkspotGameSystem> = GameInstance.GetWorkspotSystem(game);
        if !IsDefined(ws) || !ws.IsActorInWorkspot(body) {
            return false;
        }
        ws.SendFastExitSignal(body, new Vector3(0.0, 1.0, 0.0), false, true, false, true);
        return true;
    }

    // STAMPS, WHILE HE IS ALIVE: the shield while he talks, and the fight.
    //
    // THE FIGHT IS GIG 02'S MERC (Gig02_Encounter.reds, "the merc"), the
    // design call of 2026-10-01: "shoot him until he's down, but not
    // allowed to kill, and get the info". The booth's fourth button needs
    // no check and always works. Its exit sets `cc_g04_stamps_fight`.
    //
    //   before he talks            untouched              Immortal
    //   the fight                  neutral, Neutral       Immortal
    //   down, before his lines     friendly, Friendly     Invulnerable
    //   he has talked              neutral, Neutral       no shield
    //
    // HE CANNOT DIE BEFORE HE TALKS, and any attack is the fight. The
    // design call, 2026-10-02: "If I shoot him, he dies... he needs to stay
    // alive, wounded so he talks, exactly like gig02. That's the whole 3rd
    // option." Immortal rather than Invulnerable, so the wound lands and is
    // read: a hit from V (the OnHit wrap at the end of this file), or a
    // knockout (`IsActive` is false for unconscious and defeated alike,
    // gotcha 111), sets `cc_g04_stamps_hit` and the quest starts the fight. Invulnerable over
    // the conversation was tried for two builds and refused (playtest
    // 2026-10-01: "cannot wound Stamps, he's invincible, remove it").
    // FRIENDLY AS WELL AS SHIELDED while he is down, gig 01's rule: god
    // mode alone draws a health bar and invites a shot that does nothing.
    //
    // HEALTH IN PERCENT. `GetStatPoolValue` takes a `perc` flag, and the
    // game's own threshold tests pass true (adamSmasherComponent.swift,
    // "Health, true) > 30.00"). With false it returns points, and a
    // civilian's full health in points can be under StampsDownAt: he would
    // count as beaten on the fight's first tick and go straight back under
    // Invulnerable, which is one way to read the playtest above. Gig 02's
    // merc reads points; his record's health is not this one's.
    //
    // THE FIGHT: Immortal, so damage lands and death does not; neutral, so
    // he can be aimed at, written only until he is first hit (gig 02: after
    // that the game's own reaction is left alone). Out of his seat as it
    // starts. At StampsDownAt percent he goes down: the game's own Defeated
    // fall, then Bleeding to hold him there (gig 02's pose lab), and the
    // quest plays his lines three seconds later. `hp > 0.0` guards a body
    // still resolving, which reads 0 (gig 02's note on the same test).
    //
    // A KNOCKOUT OUTSIDE THE FIGHT is read by the down test as soon as the
    // fight starts, since he is still inactive: he goes to the floor and
    // the beaten scene plays the same way.
    //
    // AFTER HE TALKS the shield is off and he is neutral: V can finish him
    // or leave him, and `cc_g04_stamps_dead` picks her last call.
    //
    // DERIVED EVERY TICK from facts in the save (gotcha 21), and re-applied
    // to a new body: a reload mid-fight respawns him.
    private func StampsLife(game: GameInstance, qs: ref<QuestsSystem>, player: ref<PlayerPuppet>, stamps: ref<ScriptedPuppet>) -> Void {
        let id: EntityID = stamps.GetEntityID();
        if NotEquals(id, this.m_stampsId) {
            this.m_stampsId = id;
            this.m_stampsMode = 0;
            this.m_stampsFloor = 0;
            this.m_stampsRoused = 0;
            this.m_stampsNoDismember = false;
            this.m_stampsTouched = false;
            this.m_stampsFightTicks = 0;
            this.m_stampsUnbled = false;
        }
        let talked: Bool = qs.GetFactStr("cc_g04_stamps_talked") > 0;
        let fight: Bool = qs.GetFactStr("cc_g04_stamps_fight") > 0;
        let down: Bool = qs.GetFactStr("cc_g04_stamps_down") > 0;
        let pools: ref<StatPoolsSystem> = GameInstance.GetStatPoolsSystem(game);
        if !IsDefined(pools) {
            return;
        }
        let hp: Float = pools.GetStatPoolValue(Cast<StatsObjectID>(id), gamedataStatPoolType.Health, true);
        if fight && !down {
            this.m_stampsFightTicks += 1;
        }
        // KNOCKED OUT BEFORE THE FIGHT: the quest reads it as the fight. A
        // wound is read from his own hit event, from V only (the wrap on
        // NPCPuppet.OnHit at the end of this file). Only once V is looking
        // for him (`cc_g04_shard_read`, which opens "Find Stamps"): before
        // that, a stray shot from somebody else's fight started it (audit
        // 2026-10-02).
        if !talked && !fight && qs.GetFactStr("cc_g04_shard_read") > 0
            && !ScriptedPuppet.IsActive(stamps)
            && qs.GetFactStr("cc_g04_stamps_hit") <= 0 {
            qs.SetFactStr("cc_g04_stamps_hit", 1);
        }
        // NO STARS WHILE HE IS BEING BEATEN: a witness's call to the police
        // does not look at the victim's tag (aiStimReactionTask.swift,
        // CallPolice), so the heat is cleared through the fight, not only
        // as he falls (audit 2026-10-02).
        // ONLY NEAR HIM (audit 2026-10-13): a V who hit him and walked off
        // could not be wanted anywhere until he talked.
        // ONLY HEAT THE BEATING RAISED. The shared helper clears every star,
        // whatever raised them (CCShared_Prevention.reds sends Heat_0). So
        // V's stars are noted, saved, as the fight begins (`cc_g04_heat_at_fight`
        // is the stage plus one, 0 unset), and nothing is cleared for a V who
        // was already wanted (audit 2026-11-01).
        if !talked && (fight || qs.GetFactStr("cc_g04_stamps_hit") > 0)
            && qs.GetFactStr("cc_g04_heat_at_fight") <= 0 {
            qs.SetFactStr("cc_g04_heat_at_fight", CCSharedPrevention.Heat(game) + 1);
        }
        let mayClear: Bool = qs.GetFactStr("cc_g04_heat_at_fight") == 1;
        if !talked && mayClear && (fight || qs.GetFactStr("cc_g04_stamps_hit") > 0)
            && Vector4.Distance(player.GetWorldPosition(), stamps.GetWorldPosition())
               < CCG04Places.StampsHeatRange()
            && CCSharedPrevention.Heat(game) > 0 {
            CCSharedPrevention.Clear(game);
        }

        if fight && !down && this.m_stampsRoused < CCG04Places.RouseTicks() {
            this.m_stampsRoused += 1;
            this.OutOfPose(game, stamps);
        }
        // DOWN at StampsDownAt percent, or knocked out by V in the fight (a
        // choke takes no health; audit 2026-10-01). Before `down` is set
        // nothing of ours has made him inactive, so an inactive Stamps here
        // is V's doing.
        if fight && !down && !talked
            && ((hp > 0.0 && hp <= CCG04Places.StampsDownAt()) || !ScriptedPuppet.IsActive(stamps)) {
            qs.SetFactStr("cc_g04_stamps_down", 1);
            down = true;
            NPCPuppet.ChangeHighLevelState(stamps, gamedataNPCHighLevelState.Relaxed);
            // KNOCKED OUT RATHER THAN BEATEN: the Defeated fall below is the
            // state gig 02 measured a scene over; Unconscious inside a scene
            // never was (audit 2026-10-01, second pass), so it comes off.
            if ScriptedPuppet.IsUnconscious(stamps) {
                StatusEffectHelper.RemoveAllStatusEffectsByType(stamps, gamedataStatusEffectType.Unconscious);
            }
        }
        // HIS BLEEDING COMES OFF ONCE HE HAS TALKED, when his shield does: a
        // bleed with no shield may run him down on its own and set
        // `cc_g04_stamps_dead` for a V who spared him (audit 2026-10-01).
        // He stays on the floor.
        if talked && down && !this.m_stampsUnbled {
            StatusEffectHelper.RemoveStatusEffect(stamps, t"BaseStatusEffect.BleedingInfinite");
            this.m_stampsUnbled = true;
        }
        if down {
            this.m_stampsFloor += 1;
            // THE STARS GO: he was a civilian and the fight is over (gotcha
            // 117, the same request the game's quests send). Over his first
            // five seconds on the floor, not once: heat from the last shots
            // can rise a moment after he falls (audit 2026-10-01, second
            // pass). Not for a V who was wanted before the fight (mayClear).
            if this.m_stampsFloor <= 5 && !talked && mayClear {
                CCSharedPrevention.Clear(game);
            }
            if this.m_stampsFloor == 1 {
                StatusEffectHelper.ApplyStatusEffect(stamps, t"BaseStatusEffect.Defeated");
            }
            if this.m_stampsFloor == 3 && !talked {
                StatusEffectHelper.ApplyStatusEffect(stamps, t"BaseStatusEffect.BleedingInfinite");
            }
        }
        // NO LIMB OFF A MAN WHO CANNOT DIE (gig 02: a blade dismembers a
        // living target). From the first tick: he is Immortal from then.
        if !this.m_stampsNoDismember {
            let stats: ref<StatsSystem> = GameInstance.GetStatsSystem(game);
            if IsDefined(stats) {
                stats.AddModifier(Cast<StatsObjectID>(id),
                    RPGManager.CreateStatModifier(gamedataStatType.HitDismembermentFactor,
                                                  gameStatModifierType.Multiplier, 0.0));
                this.m_stampsNoDismember = true;
            }
        }

        let want: Int32 = 0;
        if !talked {
            if down {
                want = 1;
            } else {
                want = 2;
            }
        }
        // His attitude is written only in the fight and on the floor; before
        // the fight he is neutral, with a passive ganger's reactions
        // (characters.yaml).
        let inFight: Bool = fight && !down && !talked;

        let agent: ref<AttitudeAgent> = stamps.GetAttitudeAgent();
        let playerAgent: ref<AttitudeAgent> = player.GetAttitudeAgent();
        if IsDefined(agent) && IsDefined(playerAgent) {
            if Equals(want, 1) {
                agent.SetAttitudeGroup(n"friendly");
                agent.SetAttitudeTowards(playerAgent, EAIAttitude.AIA_Friendly);
                this.m_stampsTouched = true;
            }
            // Written while he is untouched, and for the fight's first
            // seconds whatever his health: a V may have wounded him before
            // picking the fight (audit 2026-10-01).
            // HOSTILE IN THE FIGHT, so he swings back: his record fights
            // with his fists (characters.yaml; the design call, 2026-10-13).
            // Pairwise, to V only. Written every tick of the fight: a
            // knockout or a reload can reset it.
            if inFight {
                agent.SetAttitudeTowards(playerAgent, EAIAttitude.AIA_Hostile);
                this.m_stampsTouched = true;
            }
            if Equals(want, 0) && this.m_stampsTouched {
                agent.SetAttitudeGroup(n"neutral");
                agent.SetAttitudeTowards(playerAgent, EAIAttitude.AIA_Neutral);
                this.m_stampsTouched = false;
            }
            // OUT OF ANY FIGHT BUT HIS OWN. Playtest 2026-11-01: after the
            // room's fight V stayed in COMBAT for 33 s, and V's own threat
            // list held one entry, Stamps, standing at his bar 410 m off.
            // His record is a Tyger Claw's, and the room's Claws come from
            // the same community; that the fight reached him through them
            // is inference. Outside his own fight he is taken off V's
            // threats, V off his, and he is neutral to V again.
            // NOT ONCE V HAS HIT HIM and his fight is about to start: his own
            // swing back is the fight. AND ONLY WITH V FAR FROM HIM
            // (StampsCalmFrom): near him, a fight with V is one V started,
            // and he should answer it however the gig stands.
            if !inFight && !Equals(want, 1)
                && (talked || qs.GetFactStr("cc_g04_stamps_hit") <= 0)
                && Vector4.Distance(player.GetWorldPosition(), stamps.GetWorldPosition())
                   > CCG04Places.StampsCalmFrom() {
                this.StampsOutOfFights(player, stamps, agent, playerAgent);
            }
        }

        let gods: ref<GodModeSystem> = GameInstance.GetGodModeSystem(game);
        // THE SHIELD READ OFF THE BODY, not only off the field: a community
        // body can come back under the same id (gotcha 122) without its god
        // mode, and the field still says it has one (audit 2026-11-01, the
        // check ShieldLigaya and ShieldBayani already make). Forgetting the
        // mode makes the block below add it again.
        if IsDefined(gods) && Equals(want, this.m_stampsMode)
            && ((Equals(want, 1) && !gods.HasGodMode(id, gameGodModeType.Invulnerable))
                || (Equals(want, 2) && !gods.HasGodMode(id, gameGodModeType.Immortal))) {
            this.m_stampsMode = 0;
        }
        if IsDefined(gods) && NotEquals(want, this.m_stampsMode) {
            if Equals(this.m_stampsMode, 1) {
                gods.RemoveGodMode(id, gameGodModeType.Invulnerable, CCG04Places.StampsShield());
            }
            if Equals(this.m_stampsMode, 2) {
                gods.RemoveGodMode(id, gameGodModeType.Immortal, CCG04Places.StampsShield());
            }
            if Equals(want, 1) {
                gods.AddGodMode(id, gameGodModeType.Invulnerable, CCG04Places.StampsShield());
            }
            if Equals(want, 2) {
                gods.AddGodMode(id, gameGodModeType.Immortal, CCG04Places.StampsShield());
            }
            this.m_stampsMode = want;
            qs.SetFactStr("cc_g04_dbg_stamps_mode", want);
        }
    }

    // STAMPS EACH TICK from the moment he is at his bar: his death, once and
    // only after he has talked (before that he is Immortal, StampsLife), his
    // shield and fight, his stool kept clear, and his face. His entry is on
    // until the cast is switched off at the end, which is after every read
    // of this.
    private func WatchStamps(game: GameInstance, qs: ref<QuestsSystem>, player: ref<PlayerPuppet>) -> Void {
        if qs.GetFactStr("cc_g04_stamps_dead") <= 0 {
            let stamps: ref<ScriptedPuppet> = this.FindInCommunity(game, CCG04Places.StampsEntry());
            // ATTACHED: `IsAlive` is false for a body that is streaming out
            // and no longer attached, which is not a death (audit
            // 2026-10-01, second pass; scriptedPuppet.swift `IsAlive`).
            if IsDefined(stamps) && stamps.IsAttached() {
                if !ScriptedPuppet.IsAlive(stamps) {
                    qs.SetFactStr("cc_g04_stamps_dead", 1);
                } else {
                    this.StampsLife(game, qs, player, stamps);
                }
            }
            this.ClearStool(game, player);
        }
        this.KeepLook(game, CCG04Places.StampsEntry(), n"service__vendor_ma_vendor_asian_01");
    }

    // Stamps off V's threat list and V off his, and his attitude to V back
    // to neutral if something turned it hostile (StampsLife has why).
    // Logged once per session.
    private func StampsOutOfFights(player: ref<PlayerPuppet>, stamps: ref<ScriptedPuppet>,
                                   agent: ref<AttitudeAgent>, playerAgent: ref<AttitudeAgent>) -> Void {
        let hostile: Bool = Equals(agent.GetAttitudeTowards(playerAgent), EAIAttitude.AIA_Hostile);
        if hostile {
            agent.SetAttitudeTowards(playerAgent, EAIAttitude.AIA_Neutral);
        }
        let listed: Bool = false;
        let tt: ref<TargetTrackerComponent> = player.GetTargetTrackerComponent();
        if IsDefined(tt) {
            let threats: array<TrackedLocation> = tt.GetHostileThreats(false);
            let k: Int32 = 0;
            while k < ArraySize(threats) {
                if threats[k].entity == stamps {
                    listed = true;
                }
                k += 1;
            }
            if listed {
                tt.RemoveThreat(tt.MapThreat(stamps));
            }
        }
        let his: ref<TargetTrackerComponent> = stamps.GetTargetTrackerComponent();
        let hunting: Bool = IsDefined(his) && his.HasHostileThreat(false);
        if hunting {
            TargetTrackingExtension.RemoveThreat(stamps, player);
        }
        if (hostile || listed || hunting) && !this.m_stampsCalmLogged {
            this.m_stampsCalmLogged = true;
            FTLog(s"[CC.Gig04] Stamps taken out of a fight not his: hostile=\(hostile ? 1 : 0) on V's list=\(listed ? 1 : 0) hunting=\(hunting ? 1 : 0)");
        }
    }

    // OUT OF V'S EYE LINE. `cc_g04_bayani_gone` goes to 1 when he is behind
    // V (against V's facing, which follows the camera) and GoneBehind off,
    // or GoneAnyway off, or at the end of his route with V GoneAtEnd off.
    // The quest's cast switch-off waits on it, so he never vanishes in view.
    // A BODY THAT CANNOT BE FOUND counts only with V GoneAnyway from both
    // the room and the route's end, for ten seconds running: a body that is
    // not spawned cannot be seen going, and without this a V who had
    // travelled away never got her last call (audit 2026-10-01; 70 m since
    // the second pass, which found 150 m held a V who waited by the
    // building). `cc_g04_dbg_gone_dist` is the
    // distance at the moment it went up.
    private func WatchBayani(game: GameInstance, qs: ref<QuestsSystem>, player: ref<PlayerPuppet>) -> Void {
        this.m_watchTicks += 1;
        let bayani: ref<ScriptedPuppet> = this.FindInCommunity(game, CCG04Places.BayaniEntry());
        if !IsDefined(bayani) {
            qs.SetFactStr("cc_g04_dbg_lost", qs.GetFactStr("cc_g04_dbg_lost") + 1);
            let here: Vector4 = player.GetWorldPosition();
            if Vector4.Distance(here, CCG04Places.Door()) > CCG04Places.GoneAnyway()
                && Vector4.Distance(here, CCG04Places.LeaveSpot()) > CCG04Places.GoneAnyway() {
                this.m_bayaniMissing += 1;
                if this.m_bayaniMissing >= 10 {
                    qs.SetFactStr("cc_g04_dbg_gone_dist", -1);
                    qs.SetFactStr("cc_g04_bayani_gone", 1);
                }
            } else {
                this.m_bayaniMissing = 0;
            }
            return;
        }
        this.m_bayaniMissing = 0;
        let here: Vector4 = player.GetWorldPosition();
        let there: Vector4 = bayani.GetWorldPosition();
        if there.Z < 1.0 {
            // a body with no position yet
            return;
        }
        let d: Float = Vector4.Distance(here, there);
        let to: Vector4 = Vector4.Normalize2D(there - here);
        let facing: Float = Vector4.Dot2D(player.GetWorldForward(), to);
        // At the end of his route he stands, so once V is a dozen metres
        // off he may go even in view (playtest 2026-10-01: V followed him
        // to the end and he stood there for good).
        let atEnd: Bool = Vector4.Distance2D(there, CCG04Places.LeaveSpot()) < 3.0;
        // AFTER FIVE MINUTES OF WATCHING, GoneBehind off is enough whichever
        // way V faces: a V who waits by the building, facing it, held her
        // last call for as long as he stood there (audit 2026-10-01, second
        // pass).
        let long: Bool = this.m_watchTicks > 300;
        if d > CCG04Places.GoneAnyway() || (d > CCG04Places.GoneBehind() && (facing < -0.1 || long))
            || (atEnd && d > CCG04Places.GoneAtEnd()) {
            qs.SetFactStr("cc_g04_dbg_gone_dist", Cast<Int32>(d));
            qs.SetFactStr("cc_g04_bayani_gone", 1);
        }
    }

    // MOVE THE TIME OF DAY ON by whatever is left of `wanted` seconds,
    // counted from `stamp`, never more than `wanted`: gig 02's SkipAhead,
    // the call the game's own Skip Time makes (`SetGameTimeByHMS`), with a
    // reason of its own.
    private func SkipAhead(ts: ref<TimeSystem>, stamp: Float, wanted: Float) -> Void {
        let left: Float = wanted;
        if stamp > 0.0 {
            left = wanted - (ts.GetGameTimeStamp() - stamp);
        }
        if left > wanted {
            left = wanted;
        }
        if left <= 0.0 {
            return;
        }
        let now: GameTime = ts.GetGameTime();
        // THE HOURS ARE NOT WRAPPED at midnight: the game's own Skip Time
        // passes hours above 23 to move into the next day
        // (timeSkipPopup.swift, Apply). Wrapped, a wait within two hours of
        // midnight set the clock back to the same day's small hours (audit
        // 2026-10-13).
        let total: Int32 = GameTime.Hours(now) * 3600 + GameTime.Minutes(now) * 60
            + GameTime.Seconds(now) + Cast<Int32>(left);
        ts.SetGameTimeByHMS(total / 3600, (total % 3600) / 60, total % 60,
                            n"cc_g04_waiting_spot");
    }

    // A DOOR GIVEN BACK ITS OWN CLOSING. False while the door cannot be
    // reached, so it is tried again.
    private func CloseItselfAgain(game: GameInstance, ref: String) -> Bool {
        let root: GlobalNodeRef;
        let g: GlobalNodeRef = ResolveNodeRef(CreateNodeRef(ref), root);
        if !GlobalNodeRef.IsDefined(g) {
            return false;
        }
        let door: ref<Door> = GameInstance.FindEntityByID(game, Cast<EntityID>(g)) as Door;
        if !IsDefined(door) {
            return false;
        }
        let ps: ref<DoorControllerPS> = door.GetDevicePS();
        if !IsDefined(ps) {
            return false;
        }
        ps.SetCloseItself(true);
        return true;
    }

    // THE DOOR, FORCED OPEN. The node is resolved by its long NodeRef (gotcha
    // 34), the entity found by id (gig 01's rule: FindEntityByID, not the
    // dynamic entity system), and the controller given the quest action by
    // name, which is public where the action builders are not.
    // It returns, and the debug fact reads, 1 when the action was sent, 2
    // when the door was already open, 0 when the node or the door could not
    // be reached, so a caller can try again.
    private func OpenDoor(game: GameInstance, qs: ref<QuestsSystem>, ref: String, fact: String) -> Int32 {
        let root: GlobalNodeRef;
        let g: GlobalNodeRef = ResolveNodeRef(CreateNodeRef(ref), root);
        if !GlobalNodeRef.IsDefined(g) {
            this.SetFact(qs, fact, 0);
            return 0;
        }
        let door: ref<Door> = GameInstance.FindEntityByID(game, Cast<EntityID>(g)) as Door;
        if !IsDefined(door) {
            this.SetFact(qs, fact, 0);
            return 0;
        }
        let ps: ref<DoorControllerPS> = door.GetDevicePS();
        if !IsDefined(ps) {
            this.SetFact(qs, fact, 0);
            return 0;
        }
        // IT STAYS OPEN. Both doors ship with `automaticallyClosesItself`,
        // and the quest's ForceOpen does not clear it (doorController.swift,
        // OnQuestForceOpen; only the plain ForceOpen does), so the door shut
        // again as soon as someone walked out through it (audit 2026-10-01,
        // second pass).
        ps.SetCloseItself(false);
        if ps.IsOpen() {
            this.SetFact(qs, fact, 2);
            return 2;
        }
        let action: ref<ScriptableDeviceAction> = ps.GetQuestActionByName(n"ForceOpen") as ScriptableDeviceAction;
        if !IsDefined(action) {
            this.SetFact(qs, fact, 0);
            return 0;
        }
        ps.ExecutePSAction(action, ps);
        this.SetFact(qs, fact, 1);
        return 1;
    }

    // BAYANI CANNOT BE KILLED. Playtest 2026-10-01: a grenade thrown at the
    // Claws wounded him. `GodModeSystem` is the game's own mechanism for a
    // quest NPC and `Invulnerable` is the harder of its two settings (gig
    // 01's Hoshino carries it the same way). Once per body, by entity id,
    // and re-done for a body that comes back under a new id.
    private func ShieldBayani(game: GameInstance, qs: ref<QuestsSystem>) -> Void {
        let bayani: ref<ScriptedPuppet> = this.FindInCommunity(game, CCG04Places.BayaniEntry());
        if !IsDefined(bayani) {
            return;
        }
        let id: EntityID = bayani.GetEntityID();
        let gods: ref<GodModeSystem> = GameInstance.GetGodModeSystem(game);
        if !IsDefined(gods) {
            return;
        }
        // BY THE SHIELD ITSELF, not by the id: a community body comes back
        // under the same id (gotcha 122) and nothing says its god mode came
        // with it (audit 2026-10-01, second pass).
        if gods.HasGodMode(id, gameGodModeType.Invulnerable) {
            return;
        }
        gods.AddGodMode(id, gameGodModeType.Invulnerable, n"cc_g04_bayani");
        ArrayPush(this.m_shielded, id);
        qs.SetFactStr("cc_g04_dbg_shielded", ArraySize(this.m_shielded));
    }

    // THE ROOM HAS NO NAVIGATION MESH and the game's run-time obstacles
    // bend no path (measured 2026-10-01, gotcha 128), so the Claws keep
    // to the street, where the mesh is. A fence of obstacles along the
    // walls stood here for two builds and did nothing.

    // ORBITAL AIR, COUNTED DOWN. A guard is down when his body is found
    // dead. A guard seen alive and then not found for OAGoneTicks seconds
    // while V is at the door counts as down too: a body can despawn. And
    // once the fight has been on for OAFloor seconds, a guard never seen at
    // all counts as down, so a body that never spawned (a reload after the
    // fight, a record that will not load) cannot hold the gig for ever.
    // `cc_g04_oa_clear` goes to 1 when all are down. The debug facts count
    // the seen and the down for the dev window.
    // A GUARD KNOCKED OUT IS DOWN as much as a dead one: `IsActive` is false
    // for dead, defeated and unconscious alike, where `IsAlive` stays true
    // for the last two (gotcha 111; audit 2026-10-01: a blunt weapon or a
    // non-lethal hack held the gig at "Fight off" for good). THE FLOOR'S
    // CLOCK RUNS ONLY WITH V AT THE DOOR, so a reload away from it cannot
    // clear guards nobody fought.
    private func WatchOA(game: GameInstance, qs: ref<QuestsSystem>, player: ref<PlayerPuppet>, entries: array<CName>) -> Void {
        if ArraySize(this.m_oaMissing) < ArraySize(entries) {
            ArrayResize(this.m_oaMissing, ArraySize(entries));
        }
        // THE SAME RADIUS AS THE HUNT (audit 2026-10-02: 40 here and 60
        // there stopped the clocks while the guards still hunted V).
        let near: Bool = CCSharedWorld.Near(player.GetWorldPosition(), CCG04Places.Door(),
                                            CCG04Places.ArmRadius(), 20.0, 20.0);
        if near {
            this.m_oaTicks += 1;
        }
        let late: Bool = this.m_oaTicks > CCG04Places.OAFloor();
        let i: Int32 = 0;
        while i < ArraySize(entries) {
            let e: CName = entries[i];
            if !ArrayContains(this.m_oaDown, e) {
                let body: ref<ScriptedPuppet> = this.FindInCommunity(game, e);
                if IsDefined(body) {
                    this.m_oaMissing[i] = 0;
                    if !ArrayContains(this.m_oaSeen, e) {
                        ArrayPush(this.m_oaSeen, e);
                    }
                    if !ScriptedPuppet.IsActive(body) {
                        ArrayPush(this.m_oaDown, e);
                        FTLog(s"[CC.Gig04] Orbital Air \(NameToString(e)) down: found down, fight tick \(this.m_oaTicks)");
                    }
                } else {
                    if ArrayContains(this.m_oaSeen, e) {
                        if near {
                            this.m_oaMissing[i] += 1;
                            if this.m_oaMissing[i] >= CCG04Places.OAGoneTicks() {
                                ArrayPush(this.m_oaDown, e);
                                FTLog(s"[CC.Gig04] Orbital Air \(NameToString(e)) down: missing \(this.m_oaMissing[i]) s, fight tick \(this.m_oaTicks)");
                            }
                        }
                    } else {
                        if late {
                            ArrayPush(this.m_oaDown, e);
                            FTLog(s"[CC.Gig04] Orbital Air \(NameToString(e)) down: never seen, fight tick \(this.m_oaTicks)");
                        }
                    }
                }
            }
            i += 1;
        }
        if near {
            this.Stray(game, qs, player, entries);
        }
        this.SetFact(qs, "cc_g04_dbg_oa_seen", ArraySize(this.m_oaSeen));
        this.SetFact(qs, "cc_g04_dbg_oa_down", ArraySize(this.m_oaDown));
        if ArraySize(this.m_oaDown) >= ArraySize(entries) {
            qs.SetFactStr("cc_g04_oa_clear", 1);
            FTLog(s"[CC.Gig04] Orbital Air clear, fight tick \(this.m_oaTicks)");
        }
    }

    // THE STRAY. Any guard still standing is a stray once he has spent
    // OAStrayTicks seconds of the fight, with V at the door, within a metre
    // and a half of one spot and not hurt. A guard who is fighting moves or
    // bleeds; one stuck in the geometry does neither. Playtest 2026-10-02:
    // every guard V could see was dead and the game still said COMBAT.
    // EVERY GUARD, not only the last one (audit 2026-10-02: two stuck ones
    // held the fight for good), and the count starts again whenever he
    // moves or is hurt, at any distance.
    //
    // NOT IN V'S VIEW: V facing within about 70 degrees of him holds the
    // count, up to three times its length, then he goes anyway (a guard in
    // a wall cannot be seen however V faces). He dies with the game's own
    // death animation and no instigator, so V is not credited and no heat
    // follows (NPCPuppet.Kill: a null instigator is allowed).
    // The counters are kept by entry name.
    private func Stray(game: GameInstance, qs: ref<QuestsSystem>, player: ref<PlayerPuppet>,
                       entries: array<CName>) -> Void {
        let pools: ref<StatPoolsSystem> = GameInstance.GetStatPoolsSystem(game);
        if !IsDefined(pools) {
            return;
        }
        let here: Vector4 = player.GetWorldPosition();
        let most: Int32 = 0;
        let i: Int32 = 0;
        while i < ArraySize(entries) {
            let e: CName = entries[i];
            if !ArrayContains(this.m_oaDown, e) {
                let body: ref<ScriptedPuppet> = this.FindInCommunity(game, e);
                if IsDefined(body) && ScriptedPuppet.IsActive(body) {
                    let pos: Vector4 = body.GetWorldPosition();
                    if pos.Z > 1.0 {
                        let k: Int32 = this.StrayIndex(e);
                        let hp: Float = pools.GetStatPoolValue(Cast<StatsObjectID>(body.GetEntityID()),
                                                               gamedataStatPoolType.Health, true);
                        // A GUARD WHO CAN SEE V IS FIGHTING, however still
                        // he stands (audit 2026-10-13: one in cover was
                        // counted as stuck).
                        let senses: ref<SenseComponent> = body.GetSensesComponent();
                        let sees: Bool = IsDefined(senses) && senses.IsAgentVisible(player);
                        if Equals(this.m_strayTicks[k], 0) || sees
                            || Vector4.Distance(pos, this.m_strayPos[k]) > 1.5
                            || hp < this.m_strayHp[k] - 0.5 {
                            this.m_strayPos[k] = pos;
                            this.m_strayHp[k] = hp;
                            this.m_strayTicks[k] = 1;
                        } else {
                            this.m_strayTicks[k] += 1;
                            let to: Vector4 = Vector4.Normalize2D(pos - here);
                            let inView: Bool = Vector4.Dot2D(player.GetWorldForward(), to) > 0.35;
                            if this.m_strayTicks[k] > CCG04Places.OAStrayTicks()
                                && (!inView || this.m_strayTicks[k] > 3 * CCG04Places.OAStrayTicks()) {
                                let npc: ref<NPCPuppet> = body as NPCPuppet;
                                if IsDefined(npc) {
                                    npc.Kill(null, false, false);
                                }
                                ArrayPush(this.m_oaDown, e);
                                this.m_strayTicks[k] = 0;
                                this.SetFact(qs, "cc_g04_dbg_oa_strays",
                                             qs.GetFactStr("cc_g04_dbg_oa_strays") + 1);
                            }
                        }
                        if this.m_strayTicks[k] > most {
                            most = this.m_strayTicks[k];
                        }
                    }
                }
            }
            i += 1;
        }
        this.SetFact(qs, "cc_g04_dbg_oa_stray", most);
    }

    private func StrayIndex(e: CName) -> Int32 {
        let k: Int32 = 0;
        while k < ArraySize(this.m_strayNames) {
            if Equals(this.m_strayNames[k], e) {
                return k;
            }
            k += 1;
        }
        ArrayPush(this.m_strayNames, e);
        ArrayPush(this.m_strayPos, new Vector4(0.0, 0.0, 0.0, 0.0));
        ArrayPush(this.m_strayHp, 0.0);
        ArrayPush(this.m_strayTicks, 0);
        return ArraySize(this.m_strayNames) - 1;
    }

    // ALL THE ROOM'S CLAWS DOWN, `cc_g04_claws_clear`, which opens Bayani's
    // talk (the design call, 2026-10-13: "first take out the claws, then
    // talk with the brother, then Orbital shows up, only after fighting is
    // done, then he moves"). A Claw is down when his dead fact is set
    // (KeepDead: dead or knocked out). A Claw never found once V has spent
    // 20 seconds at the door has not streamed in at all and does not hold
    // the talk.
    // THE ONES LEFT, STUCK: with V inside the building, Claws of whom none
    // has moved 1.5 m or seen V for 45 seconds do not hold the talk either
    // (audit 2026-10-13: one or two Claws stuck where V cannot reach them
    // held it for good). They are not killed: the general stray rule
    // killed idle Claws while V was outside (playtest 2026-10-13), and a
    // hiding one still fights. Each Claw's last place is kept by name
    // (StrayIndex).
    private func ClawsClear(game: GameInstance, qs: ref<QuestsSystem>, player: ref<PlayerPuppet>) -> Void {
        if qs.GetFactStr("cc_g04_claws_clear") > 0 {
            return;
        }
        if Vector4.Distance(player.GetWorldPosition(), CCG04Places.Door()) < 40.0 {
            this.m_roomTicks += 1;
        }
        let claws: array<CName> = CCG04Places.ClawEntries();
        let standing: Int32 = 0;
        let busy: Bool = false;
        let i: Int32 = 0;
        while i < ArraySize(claws) {
            if qs.GetFactStr("cc_g04_dead_" + NameToString(claws[i])) <= 0 {
                let body: ref<ScriptedPuppet> = this.FindInCommunity(game, claws[i]);
                if IsDefined(body) && body.IsAttached() {
                    if ScriptedPuppet.IsActive(body) {
                        standing += 1;
                        let k: Int32 = this.StrayIndex(claws[i]);
                        let senses: ref<SenseComponent> = body.GetSensesComponent();
                        if (IsDefined(senses) && senses.IsAgentVisible(player))
                            || Vector4.Distance(body.GetWorldPosition(), this.m_strayPos[k]) > 1.5 {
                            this.m_strayPos[k] = body.GetWorldPosition();
                            busy = true;
                        }
                    }
                } else {
                    if this.m_roomTicks < 20 {
                        standing += 1;
                    }
                }
            }
            i += 1;
        }
        if standing > 0 && !busy && this.InsideBuilding(player.GetWorldPosition()) {
            this.m_lastClawTicks += 1;
            if this.m_lastClawTicks > 45 {
                standing = 0;
            }
        } else {
            this.m_lastClawTicks = 0;
        }
        this.SetFact(qs, "cc_g04_dbg_claws_standing", standing);
        if Equals(standing, 0) {
            qs.SetFactStr("cc_g04_claws_clear", 1);
        }
    }

    // ORBITAL AIR COMES IN AFTER V. Playtest 2026-10-01: "Orbital security
    // isn't breaking in, they just stay outside". Hostile is an attitude:
    // with V inside and out of sight they had nothing to go after, and
    // stood at their posts. This does what the game's own quest command
    // `AIInjectCombatThreatCommand` does (aiInjectCombatThreatCommand.swift):
    // makes the guard hostile to V, puts V in the body's threat list, and
    // makes that threat persistent under the command's own source
    // (`AIThreatPersistenceSource.CommandInjectThreat`) while V is inside
    // the building, so the guard keeps V as his target without seeing him
    // and paths to him through the door and the room's floor, which is in
    // the game's walking mesh (gotcha 129).
    // THE ATTITUDE IS PAIRWISE AND SET FIRST. `AIActionHelper
    // .TryStartCombatWithTarget` was used here first; on a guard not yet
    // hostile (the shared helper writes the attitude 1.5 s late) it changes
    // the attitude of his whole GROUP to V's, which CCShared_Attitude exists
    // to avoid (audit 2026-10-01). DONE AGAIN for a body that has lost V
    // from its threat list, which a respawn under the same id does.
    // ORBITAL AIR OUT OF THEIR STANDING POSES, each body once, as they are
    // sent in: the fast exit, so the quest's patrol order meets a body that
    // is free to move (gotcha 135).
    private func OAOutOfPose(game: GameInstance, entries: array<CName>) -> Void {
        let i: Int32 = 0;
        while i < ArraySize(entries) {
            let guard: ref<ScriptedPuppet> = this.FindInCommunity(game, entries[i]);
            if IsDefined(guard) && ScriptedPuppet.IsActive(guard)
                && !ArrayContains(this.m_oaRoused, guard.GetEntityID()) {
                this.OutOfPose(game, guard);
                ArrayPush(this.m_oaRoused, guard.GetEntityID());
            }
            i += 1;
        }
    }

    // THE GUARDS READY TO FIGHT: those inside the building, or all of them
    // once OAGoInTicks have passed since V's line. Each is logged the tick
    // he is first turned, with where he was.
    private func OAInside(game: GameInstance, entries: array<CName>) -> array<CName> {
        let out: array<CName>;
        let late: Bool = this.m_oaArmedTicks > CCG04Places.OAGoInTicks();
        let i: Int32 = 0;
        while i < ArraySize(entries) {
            let guard: ref<ScriptedPuppet> = this.FindInCommunity(game, entries[i]);
            if IsDefined(guard) {
                let inside: Bool = this.InsideBuilding(guard.GetWorldPosition());
                if inside || late {
                    ArrayPush(out, entries[i]);
                    if !ArrayContains(this.m_oaTurnedLog, entries[i]) {
                        ArrayPush(this.m_oaTurnedLog, entries[i]);
                        FTLog(s"[CC.Gig04] Orbital Air \(NameToString(entries[i])) turned on V, \(inside ? "inside" : "still outside") after \(this.m_oaArmedTicks) s");
                    }
                }
            }
            i += 1;
        }
        return out;
    }

    private func Hunt(game: GameInstance, qs: ref<QuestsSystem>, player: ref<PlayerPuppet>, entries: array<CName>) -> Void {
        let src: ref<AIThreatPersistenceSource_Record> = TweakDBInterface.GetAIThreatPersistenceSourceRecord(t"AIThreatPersistenceSource.CommandInjectThreat");
        let inside: Bool = this.InsideBuilding(player.GetWorldPosition());
        let bayani: ref<ScriptedPuppet> = this.FindInCommunity(game, CCG04Places.BayaniEntry());
        let i: Int32 = 0;
        while i < ArraySize(entries) {
            let guard: ref<ScriptedPuppet> = this.FindInCommunity(game, entries[i]);
            if IsDefined(guard) && ScriptedPuppet.IsActive(guard) {
                let id: EntityID = guard.GetEntityID();
                let agent: ref<AttitudeAgent> = guard.GetAttitudeAgent();
                let playerAgent: ref<AttitudeAgent> = player.GetAttitudeAgent();
                // ONCE PER BODY, and again only for one whose attitude to V
                // has reset (a respawn under the same id). Re-injected every
                // second, V's place was known to them at all times and the
                // combat never dropped (audit 2026-10-13).
                let reset: Bool = IsDefined(agent) && IsDefined(playerAgent)
                    && NotEquals(agent.GetAttitudeTowards(playerAgent), EAIAttitude.AIA_Hostile);
                if !ArrayContains(this.m_hunting, id) || reset {
                    if IsDefined(agent) && IsDefined(playerAgent) {
                        agent.SetAttitudeTowards(playerAgent, EAIAttitude.AIA_Hostile);
                    }
                    TargetTrackingExtension.InjectThreat(guard, player);
                    if !ArrayContains(this.m_hunting, id) {
                        ArrayPush(this.m_hunting, id);
                    }
                    this.SetFact(qs, "cc_g04_dbg_oa_hunting", ArraySize(this.m_hunting));
                }
                // INTO COMBAT NOW, once per body, the way gig 03's alarm
                // does it (Gig03_Alarm.reds): they arrive standing in their
                // street poses (audit 2026-10-02).
                if !ArrayContains(this.m_combat, id) {
                    NPCPuppet.ChangeHighLevelState(guard, gamedataNPCHighLevelState.Combat);
                    ArrayPush(this.m_combat, id);
                }
                // NOT AT BAYANI: he is in the friendly group, and a guard
                // shooting at a man who cannot die keeps the fight going.
                if IsDefined(bayani) && IsDefined(agent) {
                    let bAgent: ref<AttitudeAgent> = bayani.GetAttitudeAgent();
                    if IsDefined(bAgent) {
                        agent.SetAttitudeTowards(bAgent, EAIAttitude.AIA_Neutral);
                    }
                }
                // PERSISTENT ONLY WHILE V IS INSIDE THE BUILDING: that is
                // when they cannot see V and must come in after V (playtest
                // 2026-10-01, "they just stay outside"). Off as soon as V is
                // out, so the game's own combat can end once nobody can see
                // V (audit 2026-10-02: persistence held COMBAT on for good
                // when a guard could not reach V). The game's own command
                // turns it off the same way when it ends
                // (aiInjectCombatThreatCommand.swift).
                let on: Bool = ArrayContains(this.m_persist, id);
                if IsDefined(src) && NotEquals(inside, on) {
                    TargetTrackingExtension.SetThreatPersistence(guard, player, inside,
                        Cast<Uint32>(src.EnumValue()));
                    if inside {
                        ArrayPush(this.m_persist, id);
                    } else {
                        ArrayRemove(this.m_persist, id);
                    }
                }
            }
            i += 1;
        }
    }

    // V INSIDE THE BUILDING: past the door line, inside its walls, on its
    // floor (the room's frame, gen_room.room_to_world).
    private func InsideBuilding(p: Vector4) -> Bool {
        let d: Vector4 = p - CCG04Places.Door();
        let u: Float = Vector4.Dot2D(d, CCG04Places.RoomU());
        let v: Float = Vector4.Dot2D(d, CCG04Places.RoomV());
        return v > 0.5 && v < 20.0 && AbsF(u) < 12.0 && AbsF(d.Z) < 3.0;
    }

    // A GROUP OF THE COMMUNITY TURNED ON V: the room's Claws and Orbital
    // Air's guards. Each body once, and AGAIN for one whose attitude
    // to V is not hostile any more: a community body comes back under the
    // same id (gotcha 122) with the record's default attitude and its
    // senses off (audit 2026-10-01).
    private func TurnGroup(game: GameInstance, qs: ref<QuestsSystem>, entries: array<CName>) -> Void {
        let playerObj: ref<GameObject> = GameInstance.GetPlayerSystem(game).GetLocalPlayerMainGameObject();
        let playerAgent: ref<AttitudeAgent>;
        if IsDefined(playerObj) {
            playerAgent = playerObj.GetAttitudeAgent();
        }
        this.KeepDead(game, qs, entries);
        let bayani: ref<ScriptedPuppet> = this.FindInCommunity(game, CCG04Places.BayaniEntry());
        let bAgent: ref<AttitudeAgent>;
        if IsDefined(bayani) {
            bAgent = bayani.GetAttitudeAgent();
        }
        let i: Int32 = 0;
        while i < ArraySize(entries) {
            let claw: ref<ScriptedPuppet> = this.FindInCommunity(game, entries[i]);
            // NOT AT BAYANI: he is in the friendly group, and the Claws round
            // his cell would fight him for good (audit 2026-10-13; Hunt does
            // the same for Orbital Air).
            if IsDefined(claw) && IsDefined(bAgent) && IsDefined(claw.GetAttitudeAgent()) {
                claw.GetAttitudeAgent().SetAttitudeTowards(bAgent, EAIAttitude.AIA_Neutral);
            }
            let lapsed: Bool = false;
            if IsDefined(claw) && IsDefined(playerAgent) && IsDefined(claw.GetAttitudeAgent()) {
                lapsed = NotEquals(claw.GetAttitudeAgent().GetAttitudeTowards(playerAgent), EAIAttitude.AIA_Hostile);
            }
            if IsDefined(claw) && ScriptedPuppet.IsActive(claw)
                && (!ArrayContains(this.m_turned, claw.GetEntityID()) || lapsed) {
                // HOSTILE TO THIS PLAYER AND NOBODY ELSE (CCShared_Attitude),
                // AND HIS EYES ON, which the attitude does not do (gotcha 77).
                CCSharedAttitude.Hostile(game, claw.GetEntityID());
                let senses: ref<SenseComponent> = claw.GetSensesComponent();
                if IsDefined(senses) {
                    senses.Toggle(true);
                }
                if !ArrayContains(this.m_turned, claw.GetEntityID()) {
                    ArrayPush(this.m_turned, claw.GetEntityID());
                }
                this.SetFact(qs, "cc_g04_dbg_claws_turned", ArraySize(this.m_turned));
            }
            i += 1;
        }
    }

    // THE DEAD STAY DEAD. The first time a body of one of these entries is
    // found down (dead, or knocked out: `IsActive` is false for both,
    // gotcha 111), `cc_g04_dead_<entry>` goes to 1. A body of that entry
    // found standing later is the community respawning it after a reload,
    // and it is put down again with no instigator, so V is not credited
    // (audit 2026-10-13: "dead Claws stand back up after a reload"). Gig 02
    // switches its dead merc's entry off for the same reason.
    private func KeepDead(game: GameInstance, qs: ref<QuestsSystem>, entries: array<CName>) -> Void {
        let i: Int32 = 0;
        while i < ArraySize(entries) {
            let body: ref<ScriptedPuppet> = this.FindInCommunity(game, entries[i]);
            if IsDefined(body) && body.IsAttached() {
                let fact: String = "cc_g04_dead_" + NameToString(entries[i]);
                // DOWN MEANS DEAD, BEATEN DOWN OR KNOCKED OUT, by name:
                // `IsActive` is also false for a body the game is switching
                // off as V leaves, which marked standing Claws as dead.
                let down: Bool = !ScriptedPuppet.IsAlive(body) || ScriptedPuppet.IsDefeated(body)
                    || ScriptedPuppet.IsUnconscious(body);
                if down {
                    if qs.GetFactStr(fact) <= 0 {
                        qs.SetFactStr(fact, 1);
                    }
                } else {
                    if qs.GetFactStr(fact) > 0 {
                        let npc: ref<NPCPuppet> = body as NPCPuppet;
                        if IsDefined(npc) {
                            npc.Kill(null, true, false);
                        }
                    }
                }
            }
            i += 1;
        }
    }

    // THE RIGHT FACE. A body of the gig's three invented people found in
    // any other look is given its own (playtest 2026-10-13: a red-haired
    // woman stood at the stall as Ligaya, on a save from before her look
    // was pinned, characters.yaml). The look is the one gen_community.
    // APPEARANCE gives each entry.
    private func KeepLook(game: GameInstance, entry: CName, look: CName) -> Void {
        let body: ref<ScriptedPuppet> = this.FindInCommunity(game, entry);
        if IsDefined(body) && body.IsAttached() {
            let now: CName = body.GetCurrentAppearanceName();
            if IsNameValid(now) && NotEquals(now, look) {
                body.ScheduleAppearanceChange(look);
            }
        }
    }

    // A CAR OF THE COMMUNITY, LOCKED, so V cannot drive off in a car the
    // quest switches off (audit 2026-10-13): Orbital Air's and the Claws'
    // van. The game's own quest door state (vehicleComponentPS.swift,
    // OnVehicleQuestChangeDoorStateEvent), queued the way VehicleComponent
    // queues it. Once per body: `done` is the body locked last, and the
    // body locked now is returned.
    private func LockCar(game: GameInstance, entry: CName, done: EntityID) -> EntityID {
        if !this.m_comOk {
            return done;
        }
        let locked: EntityID = done;
        let objects: array<ref<GameObject>>;
        GetGameObjectsFromSpawnerEntityID(this.m_comId, [entry], game, objects);
        let i: Int32 = 0;
        while i < ArraySize(objects) {
            let car: ref<VehicleObject> = objects[i] as VehicleObject;
            if IsDefined(car) && IsDefined(car.GetVehiclePS()) && car.GetEntityID() != done {
                let evt: ref<VehicleQuestChangeDoorStateEvent> = new VehicleQuestChangeDoorStateEvent();
                evt.newState = EQuestVehicleDoorState.LockAll;
                GameInstance.GetPersistencySystem(game).QueuePSEvent(car.GetVehiclePS().GetID(),
                    car.GetVehiclePS().GetClassName(), evt);
                locked = car.GetEntityID();
            }
            i += 1;
        }
        return locked;
    }

    // THE HOLD, gig 03's (Gig03_Places.reds, Hold): V held still while the
    // quest sets `cc_g04_hold`, around each of Johnny's two scenes (the design
    // call, 2026-10-14: "Block V's movement, then show johnny, then make him
    // talk"). Never in a vehicle. Capped, so a scene that never plays cannot
    // leave V rooted. Recomputed from facts every tick; on the first pass of
    // a session a removal goes out in case a load caught it held.
    private func Hold(game: GameInstance, qs: ref<QuestsSystem>, player: ref<PlayerPuppet>) -> Void {
        let asked: Bool = qs.GetFactStr("cc_g04_hold") > 0;
        if asked {
            this.m_holdTicks += 1;
        } else {
            this.m_holdTicks = 0;
        }
        let want: Bool = asked && this.m_holdTicks < CCG04Places.HoldCapTicks()
            && !VehicleComponent.IsMountedToVehicle(game, player);
        if want && !this.m_holdOn {
            StatusEffectHelper.ApplyStatusEffect(player, CCG04Places.HoldRecord());
            this.m_holdOn = true;
        } else if !want && (this.m_holdOn || !this.m_holdChecked) {
            StatusEffectHelper.RemoveStatusEffect(player, CCG04Places.HoldRecord());
            this.m_holdOn = false;
        }
        this.m_holdChecked = true;
    }

    // LIGAYA MISSING FROM HER STALL, with V within 120 m of it, for 15
    // ticks, between her switch-on and the end of her talk: `cc_g04_ligaya_
    // missing`, on which the quest switches her off and on again, at most
    // five times (`cc_g04_ligaya_retries`). Playtest 2026-10-14: switched
    // on with V 2 km away, in Charter Hill, she was still not at the stall.
    private func WatchLigaya(game: GameInstance, qs: ref<QuestsSystem>, player: ref<PlayerPuppet>) -> Void {
        if qs.GetFactStr("cc_f01_intro_done") <= 0 || qs.GetFactStr("cc_g04_stall_done") > 0
            || qs.GetFactStr("cc_g04_ligaya_missing") > 0 || qs.GetFactStr("cc_g04_ligaya_retries") >= 5
            || Vector4.Distance2D(player.GetWorldPosition(), CCG04Places.Stall()) > 120.0 {
            this.m_ligayaMissing = 0;
            return;
        }
        let ligaya: ref<ScriptedPuppet> = this.FindInCommunity(game, n"ligaya");
        if IsDefined(ligaya) && ligaya.IsAttached()
            && Vector4.Distance(ligaya.GetWorldPosition(), CCG04Places.Stall()) < 6.0 {
            this.m_ligayaMissing = 0;
            return;
        }
        this.m_ligayaMissing += 1;
        if this.m_ligayaMissing >= 15 {
            this.m_ligayaMissing = 0;
            qs.SetFactStr("cc_g04_ligaya_missing", 1);
            FTLog(s"[CC.Gig04] Ligaya missing at her stall: the quest switches her off and on (retry \(qs.GetFactStr("cc_g04_ligaya_retries") + 1))");
        }
    }

    // THE TRACE, read after a playtest: a line in CET's gamelog.log
    // (`[CC.Gig04]`) whenever one of the gig's flags changes, and every 10
    // ticks while V is within 400 m of the stall or the bar. Where V is, the
    // flags, and every body the community has spawned for Ligaya and Stamps:
    // alive, attached, distance from their place, look.
    private func Trace(game: GameInstance, qs: ref<QuestsSystem>, player: ref<PlayerPuppet>) -> Void {
        // ONLY WHILE LIGAYA CAN BE MISSING: from her switch-on with Hodan's
        // introduction to the end of her talk. Until 2026-10-15 it logged a
        // line every 10 s near the market for the rest of the save.
        if qs.GetFactStr("cc_f01_intro_done") <= 0 || qs.GetFactStr("cc_g04_stall_done") > 0 {
            return;
        }
        let p: Vector4 = player.GetWorldPosition();
        let dStall: Int32 = Cast<Int32>(Vector4.Distance2D(p, CCG04Places.Stall()));
        let dBar: Int32 = Cast<Int32>(Vector4.Distance2D(p, CCG04Places.Bar()));
        let flags: String = s"intro=\(qs.GetFactStr("cc_f01_intro_done")) armed=\(qs.GetFactStr("cc_g04_offer_armed")) near=\(qs.GetFactStr("cc_g04_near_offer")) free=\(qs.GetFactStr("cc_g04_fixer_free")) started=\(qs.GetFactStr("cc_g04_started")) stall=\(qs.GetFactStr("cc_g04_stall_done")) missing=\(qs.GetFactStr("cc_g04_ligaya_missing")) retries=\(qs.GetFactStr("cc_g04_ligaya_retries"))";
        let near: Bool = dStall < 400 || dBar < 400;
        if NotEquals(flags, this.m_traceLast) || (near && Equals(this.m_tick % 10, 0)) {
            this.m_traceLast = flags;
            this.FindInCommunity(game, n"ligaya");
            FTLog(s"[CC.Gig04] t=\(this.m_tick) V=(\(Cast<Int32>(p.X)),\(Cast<Int32>(p.Y)),\(Cast<Int32>(p.Z))) dStall=\(dStall) dBar=\(dBar) \(flags) community=\(this.m_comOk ? "ok" : "NOT RESOLVED") ligaya[\(this.BodyLine(game, n"ligaya", CCG04Places.Stall()))] stamps[\(this.BodyLine(game, CCG04Places.StampsEntry(), CCG04Places.Bar()))]");
        }
    }

    private func BodyLine(game: GameInstance, entry: CName, place: Vector4) -> String {
        if !this.m_comOk {
            return "-";
        }
        let objects: array<ref<GameObject>>;
        GetGameObjectsFromSpawnerEntityID(this.m_comId, [entry], game, objects);
        let line: String = s"bodies=\(ArraySize(objects))";
        let i: Int32 = 0;
        while i < ArraySize(objects) {
            let body: ref<ScriptedPuppet> = objects[i] as ScriptedPuppet;
            if IsDefined(body) {
                let q: Vector4 = body.GetWorldPosition();
                line += s" #\(i) alive=\(ScriptedPuppet.IsAlive(body) ? 1 : 0) attached=\(body.IsAttached() ? 1 : 0) d=\(Cast<Int32>(Vector4.Distance(q, place))) at=(\(Cast<Int32>(q.X)),\(Cast<Int32>(q.Y)),\(Cast<Int32>(q.Z))) look=\(NameToString(body.GetCurrentAppearanceName()))";
            }
            i += 1;
        }
        return line;
    }

    // A body of the community by entry name: alive if there is one, else
    // the first dead one, else null. Gig 02's FindInCommunity, returning
    // the puppet rather than its id.
    // THE COMMUNITY'S NODEREF IS RESOLVED ONCE A TICK, not once a call: the
    // Orbital Air fight looks up three bodies three times a tick.
    private func FindInCommunity(game: GameInstance, entry: CName) -> ref<ScriptedPuppet> {
        let dead: ref<ScriptedPuppet>;
        if this.m_comTick != this.m_tick {
            let nref: NodeRef = CreateNodeRef(CCG04Places.CommunityRef());
            let root: GlobalNodeRef;
            let g: GlobalNodeRef = ResolveNodeRef(nref, root);
            this.m_comOk = GlobalNodeRef.IsDefined(g);
            this.m_comId = Cast<EntityID>(g);
            this.m_comTick = this.m_tick;
        }
        if !this.m_comOk {
            return null;
        }
        let objects: array<ref<GameObject>>;
        GetGameObjectsFromSpawnerEntityID(this.m_comId, [entry], game, objects);
        let i: Int32 = 0;
        while i < ArraySize(objects) {
            let puppet: ref<ScriptedPuppet> = objects[i] as ScriptedPuppet;
            if IsDefined(puppet) {
                if ScriptedPuppet.IsAlive(puppet) {
                    return puppet;
                }
                if !IsDefined(dead) {
                    dead = puppet;
                }
            }
            i += 1;
        }
        return dead;
    }

    // THE NUMBER STAMPS'S CHECKS ASK FOR, and V's own two, for the dev
    // window: the game's own computation, the one the choice draws
    // (Build_ScriptConditionType.Evaluate). The content assignment and the
    // difficulty are gen_scenes.CHECK_ASSIGNMENT and CHECK_DIFFICULTY.
    private func ReadChecks(qs: ref<QuestsSystem>, player: ref<PlayerPuppet>) -> Void {
        let place: ref<ContentAssignment_Record> = TweakDBInterface.GetContentAssignmentRecord(t"DeviceContentAssignment.sts_wat_kab_03");
        if !IsDefined(place) {
            qs.SetFactStr("cc_g04_dbg_need", -1);
            return;
        }
        this.SetFact(qs, "cc_g04_dbg_need", RPGManager.GetBluelineBuildCheckValue(player, place, EGameplayChallengeLevel.MEDIUM));
        this.SetFact(qs, "cc_g04_dbg_body", RPGManager.GetBuildScore(player, TweakDBInterface.GetPlayerBuildRecord(t"PlayerBuilds.Solo")));
        this.SetFact(qs, "cc_g04_dbg_int", RPGManager.GetBuildScore(player, TweakDBInterface.GetPlayerBuildRecord(t"PlayerBuilds.Netrunner")));
    }
}

public class CCG04PlacesTick extends DelayCallback {
    public let system: wref<ReturnTicketPlaces>;

    public func Call() -> Void {
        if IsDefined(this.system) {
            this.system.Tick();
        }
    }
}

// A HIT ON STAMPS, seen from his own body: gig 02's merc wrap
// (Gig02_Encounter.reds, CCGig02MercHitWrap), filtered by record so it costs
// a comparison on any other body. It fires under the Immortal shield, since
// Immortal lets damage land. Only V's hits count, and only once V is looking
// for him and before he has talked or the fight has started (audit
// 2026-10-02: a health test read a car or a stray bullet the same).
// Marker: CCG04StampsHitWrap.
@wrapMethod(NPCPuppet)
protected cb func OnHit(evt: ref<gameHitEvent>) -> Bool {
    let r: Bool = wrappedMethod(evt);
    if Equals(this.GetRecordID(), CCG04Places.StampsRecord()) && IsDefined(evt.attackData) {
        let by: wref<GameObject> = evt.attackData.GetInstigator();
        if IsDefined(by) && by.IsPlayer() {
            let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGame());
            if IsDefined(qs) && qs.GetFactStr("cc_g04_shard_read") > 0
                && qs.GetFactStr("cc_g04_stamps_talked") <= 0
                && qs.GetFactStr("cc_g04_stamps_fight") <= 0
                && qs.GetFactStr("cc_g04_stamps_hit") <= 0 {
                qs.SetFactStr("cc_g04_stamps_hit", 1);
                // V's STARS AS THE FIGHT BEGINS, noted here at the first
                // hit: the tick that notes them otherwise comes up to a
                // second later, after this hit may have raised them (audit
                // 2026-11-01). StampsLife has the rule.
                if qs.GetFactStr("cc_g04_heat_at_fight") <= 0 {
                    qs.SetFactStr("cc_g04_heat_at_fight", CCSharedPrevention.Heat(this.GetGame()) + 1);
                }
            }
        }
    }
    return r;
}
