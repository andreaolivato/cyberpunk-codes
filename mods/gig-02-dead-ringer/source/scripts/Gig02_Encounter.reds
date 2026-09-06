// Gig 02, Dead Ringer: the encounter layer.
//
// Arrivals, the merc, the relay, the hit and the payout. Quest logic
// (objectives, pins, journal, scenes) lives in the quest phase; this file only
// sets the facts that phase waits on, and its header lists which side owns
// which.
//
// ===========================================================================
// THE TWO NPC PROBLEMS THIS GIG HAS, AND THEY ARE OPPOSITES
// ===========================================================================
//
// THE MERC MUST BE BEATEN AND MUST NOT DIE. He is the only source for the
// proof, so the leg cannot survive him dying, and a player who empties a
// shotgun into a downed man must not be able to end the gig by accident. Gig 01
// needed the inverse, an NPC who could be killed and would stay dead, so
// nothing here was a known quantity.
//
// TOJI MUST DIE AND NOBODY ELSE HAS TO. Everyone around him is scenery with a
// gun, and the gig is over cleanly only if none of them ever sees V - going in
// OR coming out. Nobody stands down and nobody is told anything: Wakako's
// order is that the killing is never to be heard of, so the whole ending is
// decided by whether `cc_g02_spotted` was ever set. See design.md, "The
// redesign of 2026-08-27", for what this replaced and why.
//
// ===========================================================================
// EVERY BODY IN THIS GIG IS SCRIPT-SPAWNED ONTO NAVMESH, AND NOT A COMMUNITY
// ===========================================================================
//
// design.md asks for the Tyger Claws as the mod's own community, so their
// attitude is the mod's to change. THE ATTITUDE HALF OF THAT IS TRUE EITHER
// WAY: `CCSharedAttitude` takes an EntityID and works on a dynamic spawn, which
// is the case it was written for. What a community additionally needs is
// POSTS, a walked and captured position per body, and nobody could walk this
// street.
//
// `CCSharedWorld.Scatter` asks the navigation system for a point a human can
// stand on and drops anyone it cannot place, so every Claw who appears can be
// reached and fought. A community authored at guessed coordinates would put
// some of them inside walls, which is unfightable and unfinishable.
//
// THE COST IS THE HUDDLE. Gig 01 shipped a scatter and replaced it with thirty
// walked posts precisely because a navmesh query answers "somewhere near here"
// and keeps giving nearly the same answer. This is a first pass and that trade
// is accepted; converting to a community is a job for whoever can capture the
// posts. design.md carries it.

module CyberpunkCodes.Gig02

// Spawning, proximity, attitude, HUD banners and the payout live in
// shared\scripts. The build vendors them into this mod under a per-gig module
// name; see CCShared_World.reds for why that rename is mandatory.
import CyberpunkCodes.Shared.*

public abstract class CCGig02Combat {
    // The merc, comic pp. 15-30.
    public static func MercRecord() -> TweakDBID { return t"Character.cc_g02_merc"; }
    public static func MercTag() -> CName { return n"cc_g02_merc"; }
    // His own god-mode source name. A source is what a shield is tracked by, so
    // it has to be the same string going on and coming off.
    public static func MercShield() -> CName { return n"cc_g02_merc"; }

    // Toji, comic pp. 85-88.
    public static func TojiRecord() -> TweakDBID { return t"Character.cc_g02_toji"; }
    public static func TojiTag() -> CName { return n"cc_g02_toji"; }

    public static func ClawTag() -> CName { return n"cc_g02_claw"; }

    // THE COMMUNITY THIS GIG SHIPS, and the entries the scenes acquire from it.
    //
    // KEEP IN STEP WITH tools/gig02/gen_community.py. The reference is written
    // LONG FORM because that is the only form a name this mod ships resolves
    // under (gotcha 34), and the entry names are the strings the scenes ask for.
    public static func CommunityRef() -> String {
        return "$/mod/cc_g02_cast/#cc_g02_cast_com";
    }

    public static func MercEntry() -> CName { return n"merc"; }
    public static func TojiEntry() -> CName { return n"toji"; }

    // CHAR, in the netrunner's chair at the Dewdrop Inn. Not fought, not armed,
    // and spawned for one reason: the chair's own occupant is ambient crowd and
    // was therefore a different woman every load.
    public static func CharRecord() -> TweakDBID { return t"Character.cc_g02_char"; }
    public static func CharTag() -> CName { return n"cc_g02_char"; }

    // HOW MANY CLAWS. The comic's scan tags a group at 50 m and Johnny says
    // "quite a few"; six is enough to read as a den and few enough that a
    // player who is spotted can still fight out. Scatter drops anyone it cannot
    // place, so this is a ceiling rather than a promise.
    public static func ClawCount() -> Int32 { return 6; }

    // HE STOPS FIGHTING AT A THIRD OF HIS HEALTH, and that is where the
    // begging scene takes him. He is Immortal until then, so the number is
    // reached rather than skipped by a lucky headshot.
    public static func MercDownAt() -> Float { return 33.0; }

}

// `Dispose` is a native every entity has (CET calls it on any entity and the
// dev menu's DISPOSE button proved it removes the door crowd), but the game's
// script bundle does not declare it, so it is declared here.
@addMethod(Entity)
public native func Dispose() -> Void;

public class DeadRingerEncounter extends ScriptableSystem {

    // ---- the merc ----------------------------------------------------------
    private let m_mercId: EntityID;
    private let m_mercSpawned: Bool;
    // WHICH SHIELD IS ON HIM: 0 none, 1 Invulnerable, 2 Immortal.
    //
    // A plain Bool was wrong and the failure was a stall rather than a wart. He
    // starts Invulnerable, and the transition into the fight has to REMOVE that
    // and ADD Immortal; with one flag the second add was skipped because he was
    // "already shielded", so he took no damage at all, his health never fell,
    // the threshold below never fired and the gig stopped at "Beat the merc
    // down" with a man who could not be hurt.
    private let m_mercMode: Int32;
    // Counts ticks since V reached the queue with the merc still standing. THE
    // DEAD MAN'S HANDLE: see the comment by ReleaseMerc.
    private let m_mercTicks: Int32;
    // Ticks since V told him to go. Not persisted: a reload before the call to
    // Wakako puts him back on the floor and starts the count again, which is
    // right, because the player is looking at the street again too.
    private let m_fleeTicks: Int32;
    // Char has been sent back to her chair once the stranger in it was removed.
    private let m_charSent: Bool;
    // Has his dismemberment been switched off yet. A script field, so a reload
    // does it again, which is the right direction.
    private let m_mercNoDismember: Bool;
    // His health on the last tick with the kill armed: a drop is the shot.
    private let m_mercKillHp: Float;
    private let m_mercKilled: Bool;
    private let m_mercKillStage: Int32;
    private let m_mercKillTicks: Int32;
    // Has he been told to run yet. One stimulus, once.
    private let m_mercFleeing: Bool;
    // Ticks since he went down: the fall, then Bleeding, then the shard.
    private let m_floorTicks: Int32;
    // Are his eyes still off. Starts true because his record starts them off;
    // set false the once, when he is hit.
    private let m_mercBlind: Bool = true;

    // ---- the hit -----------------------------------------------------------
    private let m_hitSpawned: Bool;
    private let m_tojiId: EntityID;
    private let m_claws: array<EntityID>;

    // ---- the markers -------------------------------------------------------
    //
    // A SCRIPT-SPAWNED TARGET IN A CROWD IS NOT FINDABLE WITHOUT ONE, and this
    // gig has two of them: a merc among the queue outside Afterlife, and Toji
    // among six Tyger Claws. Both were shipped without a marker and the first
    // playtest could not identify either.
    //
    // A JOURNAL PIN CANNOT DO THIS. A journal pin's position comes from a fixed
    // base-game node, and both of these men are placed by a navmesh query at
    // runtime and can then walk. A registered mappin takes a world position and
    // can be MOVED, which is what gig 01 built `CCSharedMappins` for.
    //
    // Kept as an id plus a flag rather than re-registering each tick: a second
    // Show would leave the first marker on screen, and if the Hide ever missed
    // it would stay there for the rest of the save.
    private let m_mercPin: NewMappinID;
    private let m_mercPinOn: Bool;
    // TOJI HAS NO MARKER OF OURS, 2026-09-06. The quest area drawn on the
    // minimap covers the den and the stairs, and the design call was that two
    // markers on one man is one too many. The pair of fields that carried his
    // marker went with it.

    // ---- Char ----------------------------------------------------------------
    //
    // No fields. She is an entry in this gig's community, switched on and off
    // by the quest phase, and nothing in this script holds or touches her.

    // ---- borrowed base-game characters --------------------------------------
    //
    // DID WE SET THE FACT, and therefore may we clear it. It is not ours: it
    // belongs to the base game and other content sets it for its own reasons,
    // so clearing it because our window happens to be shut would switch her
    // small talk back on in the middle of somebody else's scene. Gig 01 learned
    // that on Mama Welles.
    private let m_wakakoHeld: Bool;

    // ---- the access point --------------------------------------------------
    // The marker on the box, while the breach objective is up.
    private let m_apPin: NewMappinID;
    private let m_apPinOn: Bool;

    // ---- the way out -------------------------------------------------------
    private let m_exfilDone: Bool;

    // ---- readers -----------------------------------------------------------
    // A journal entry may not resolve on the first tick after a load, so both
    // readers retry rather than swallow a null. Bounded, so a path that is
    // simply wrong does not retry for the rest of the session.
    private let m_shardTries: Int32;

    private func OnAttach() -> Void {
        this.ScheduleTick(6.0);
    }

    public func ScheduleTick(delay: Float) -> Void {
        let cb: ref<CCGig02Tick> = new CCGig02Tick();
        cb.system = this;
        GameInstance.GetDelaySystem(this.GetGameInstance()).DelayCallback(cb, delay, false);
    }

    // A cylinder around a place. See CCGig02Places for why the radii are
    // generous and why the Z band is asymmetric.
    private func Near(pos: Vector4, spot: Vector4, radius: Float) -> Bool {
        return CCSharedWorld.Near(pos, spot, radius, 6.0, 25.0);
    }

    // Place ONE body near a point, on ground a human can stand on and OUTSIDE
    // the club's safe area.
    //
    // TWO WAYS THIS USED TO FAIL AND BOTH WERE INVISIBLE IN GAME.
    //
    // The first is geometry. `Scatter` with a count of one tries exactly one
    // point, and if the navigation system refuses it the call returns nothing
    // and the body never appears. That looks the same as a trigger that never
    // fired.
    //
    // The second is the safe area, and it cost this leg its whole first
    // playtest. The merc used to spawn on the Afterlife ENTRANCE MARKER, which
    // is the door, and the door is inside the club's no-weapons zone. He was
    // there, he was marked, and he could not be fought, because the player
    // could not draw. `CCSharedWorld.InSafeArea` asks the game instead of
    // reasoning about where the line is.
    //
    // Sixteen candidates: four rings out from the spot, four directions each,
    // nearest first, so a body that CAN stand in the middle of its group does.
    private func SpawnOne(game: GameInstance, record: TweakDBID, center: Vector4,
                          tag: CName) -> EntityID {
        let nav: ref<NavigationSystem> = GameInstance.GetNavigationSystem(game);
        let rings: array<Float> = [0.0, 1.5, 3.0, 6.0];
        let ring: Int32 = 0;
        while ring < ArraySize(rings) {
            let dir: Int32 = 0;
            while dir < 4 {
                let angle: Float = Cast<Float>(dir) * 1.5708;
                let spot: Vector4 = new Vector4(
                    center.X + CosF(angle) * rings[ring],
                    center.Y + SinF(angle) * rings[ring],
                    center.Z, 1.0);
                // `ok` rather than an early continue: REDSCRIPT HAS NO
                // `continue`, and it fails as "unresolved reference", which
                // reads like a missing function rather than a missing keyword.
                let ok: Bool = true;
                if IsDefined(nav) {
                    let found: NavigationFindPointResult =
                        nav.FindPointInSphereOnlyHumanNavmesh(
                            spot, 2.0, NavGenAgentSize.Human, true);
                    if Equals(found.status, worldNavigationRequestStatus.OK) {
                        spot = found.point;
                    } else {
                        ok = false;
                    }
                }
                if ok && CCSharedWorld.InSafeArea(game, spot) {
                    ok = false;
                }
                if ok {
                    // FACING BACK AT THE SPOT HE WAS PLACED AROUND, so a man
                    // put down on the far side of his group still looks like
                    // part of it.
                    return CCSharedWorld.Spawn(record, spot,
                                               angle * 57.3 + 180.0, tag);
                }
                dir += 1;
            }
            ring += 1;
        }
        let none: EntityID;
        return none;
    }

    // FIND A BODY THE COMMUNITY PLACED, by entry name.
    //
    // `GetGameObjectsFromSpawnerEntityID` asks the spawner system for one
    // entry's objects, which is exactly the question: it does not care where
    // the body is standing or what else is nearby. Gotcha 69 is the join
    // between the community and the name a scene asks for.
    //
    // RETURNS NOTHING QUIETLY WHEN HE IS NOT THERE YET, and the caller is a
    // tick for that reason: the community places bodies asynchronously, so a
    // single look on the frame the objective changed finds nobody. The quest
    // phase also has to have ACTIVATED the entry first.
    private func FindInCommunity(entry: CName) -> EntityID {
        let none: EntityID;
        let game: GameInstance = this.GetGameInstance();
        let nref: NodeRef = CreateNodeRef(CCGig02Combat.CommunityRef());
        let root: GlobalNodeRef;
        let g: GlobalNodeRef = ResolveNodeRef(nref, root);
        if !GlobalNodeRef.IsDefined(g) {
            // The community's sector is not loading. Nothing below this line
            // can work, and it is worth telling the dev menu apart from "the
            // entry is off".
            return none;
        }
        let objects: array<ref<GameObject>>;
        GetGameObjectsFromSpawnerEntityID(Cast<EntityID>(g), [entry], game,
                                          objects);
        let i: Int32 = 0;
        while i < ArraySize(objects) {
            let puppet: ref<ScriptedPuppet> = objects[i] as ScriptedPuppet;
            if IsDefined(puppet) && ScriptedPuppet.IsAlive(puppet) {
                return puppet.GetEntityID();
            }
            i += 1;
        }
        return none;
    }

    // Place ONE body ON a walked post, facing a given way.
    //
    // THE DIFFERENCE FROM SpawnOne IS THAT THIS ONE DOES NOT WANDER. SpawnOne
    // widens its search until something takes, which is right for a body whose
    // anchor is a base-game marker nobody has stood on. A post that HAS been
    // stood on wants the opposite: put him there, or as near as the navigation
    // system will allow, and keep the facing that was chosen for him.
    //
    // A guard who ends up two metres off his mark still holds the step. One
    // placed eleven metres away by a widening ring is standing somewhere
    // nobody chose, which is the huddle this replaced.
    private func SpawnPost(game: GameInstance, record: TweakDBID, post: Vector4,
                           yaw: Float, tag: CName) -> EntityID {
        let spot: Vector4 = post;
        let nav: ref<NavigationSystem> = GameInstance.GetNavigationSystem(game);
        if IsDefined(nav) {
            let found: NavigationFindPointResult =
                nav.FindPointInSphereOnlyHumanNavmesh(
                    post, 2.5, NavGenAgentSize.Human, true);
            if Equals(found.status, worldNavigationRequestStatus.OK) {
                spot = found.point;
            }
        }
        return CCSharedWorld.Spawn(record, spot, yaw, tag);
    }

    // Register a marker over a body, or move the one already there, and hand
    // back the id to keep. The caller owns the "is one showing" flag, because a
    // marker registered twice is two markers and only one of them can ever be
    // removed again.
    //
    // 1.8 m UP, so it floats over his head rather than sitting in his shoes.
    // That number is a guess at head height and is the one thing here most
    // worth adjusting by eye.
    private func ShowOrMove(game: GameInstance, on: Bool, id: NewMappinID,
                            pos: Vector4) -> NewMappinID {
        let spot: Vector4 = new Vector4(pos.X, pos.Y, pos.Z + 1.8, 1.0);
        if on {
            CCSharedMappins.Move(game, id, spot);
            return id;
        }
        return CCSharedMappins.Show(game, spot);
    }

    // EVERYTHING THIS SYSTEM TOOK, GIVEN BACK, and it runs even if the gig
    // ends early. A marker registered and never removed sits on the map for
    // the rest of that save, and nobody would ever attribute it to the mod.
    //
    // THE ACCESS POINT'S MARKER WAS MISSING FROM HERE until 2026-09-06. It is
    // taken down inside `AccessPoint`, which lives below the `done` gate in
    // the tick, so a gig that ended while the breach objective was up left
    // that marker on the map for good. Gig 01's tick reads its receipts before
    // it stops for exactly this reason; this is the same list.
    //
    // Wakako's small-talk flag is the base game's, so it is only cleared if
    // `m_wakakoHeld` says we are the ones who set it. Gig 01 learned that on
    // Mama Welles.
    private func HidePins(game: GameInstance) -> Void {
        if this.m_mercPinOn {
            CCSharedMappins.Hide(game, this.m_mercPin);
            this.m_mercPinOn = false;
        }
        if this.m_apPinOn {
            CCSharedMappins.Hide(game, this.m_apPin);
            this.m_apPinOn = false;
        }
        if this.m_wakakoHeld {
            GameInstance.GetQuestsSystem(game).SetFactStr("wakako_default_temp_off", 0);
            this.m_wakakoHeld = false;
        }
    }

    public func Tick() -> Void {
        let game: GameInstance = this.GetGameInstance();
        let ps: ref<PlayerSystem> = GameInstance.GetPlayerSystem(game);
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);

        // EVERY SYSTEM FETCH IS CHECKED BEFORE IT IS USED. This system attaches
        // at the main menu, where there is no player, and dereferencing that
        // null flatlined gig 01 twenty-four seconds after launch.
        if !IsDefined(ps) || !IsDefined(qs) {
            this.ScheduleTick(2.0);
            return;
        }

        // A FINISHED GIG COSTS THE SAVE NOTHING. Stop rescheduling once the
        // payout has landed. Not persistent and it does not need to be: OnAttach
        // runs on every load, one tick reads the fact and stops again.
        // THE FEE LANDS AFTER HER CLOSING CALL AND BEFORE THE GIG ENDS
        // (playtest 2026-09-05): `closed` is set the moment the call is over,
        // and the phase then plays Johnny and completes the quest.
        if qs.GetFactStr("cc_g02_closed") > 0 {
            this.Payout(qs);
        }
        if qs.GetFactStr("cc_g02_done") > 0 {
            this.HidePins(game);
            this.Payout(qs);
            // ...but keep ticking until it has actually landed. Payout refuses
            // when there is no player yet, which is the state one tick after a
            // load, and a single attempt that lost that race would be a gig
            // that finished and never paid.
            if qs.GetFactStr("cc_g02_paid") == 0 {
                this.ScheduleTick(2.0);
            }
            return;
        }

        let player: ref<PlayerPuppet> = ps.GetLocalPlayerMainGameObject() as PlayerPuppet;
        if !IsDefined(player) {
            this.ScheduleTick(2.0);
            return;
        }
        // BEFORE THE ACCEPTED GATE: the brief is read before the gig is
        // accepted, and acceptance waits on it (playtest 2026-09-04, sixth:
        // the probe showed visited and closed, and the fact stayed 0, because
        // this ran below the gate).
        this.BriefRead(game, qs);
        if qs.GetFactStr("cc_g02_accepted") == 0 {
            this.ScheduleTick(1.0);
            return;
        }
        let pos: Vector4 = player.GetWorldPosition();

        this.Arrivals(qs, pos);
        this.HoldWakako(qs, pos);
        this.Groups(game, qs, pos);
        this.Merc(game, qs, player, pos);
        this.Bystanders(game, qs, player);
        this.QueueShield(game, qs, player);
        this.InnKeeper(game, qs, player);
        this.ParlorKeeper(game, qs, player);
        this.Readers(game, qs);
        this.AccessPoint(game, qs, player, pos);
        this.Hit(game, qs, player, pos);

        this.ScheduleTick(1.0);
    }

    // ======================================================== arrivals
    //
    // Each of these is gated on the objective before it, so a player who
    // happens to walk past Wakako's parlor on the way to Afterlife does not
    // complete a leg he has not reached yet.
    private func Arrivals(qs: ref<QuestsSystem>, pos: Vector4) -> Void {
        if qs.GetFactStr("cc_g02_called") > 0
            && qs.GetFactStr("cc_g02_afterlife_reached") == 0
            && this.Near(pos, CCGig02Places.Afterlife(), 40.0) {
            qs.SetFactStr("cc_g02_afterlife_reached", 1);
            // AND NOTHING ELSE ON THIS TICK. "Reached Afterlife" and "is
            // standing with a group" are both true of one sample of the world,
            // and two consecutive quest waits that one sample satisfies is the
            // bug gig 01 shipped and two players reported: the journal skips a
            // step and the beat between them never plays. The `return` holds
            // the next gate back a pass.
            return;
        }

        // RIGHT IN FRONT OF YOKO, not from the street.
        //
        // This was 12 m, on the reasoning that every other spot in the gig is a
        // base-game marker and needs a generous radius to allow for the
        // difference between "the right room" and "where the player stands".
        // The netrunner's spot is not one of those: it was walked to and
        // captured, so it IS where the player stands, and 12 m around it
        // reaches out of the shop. Playtest, 2026-08-26: the conversation with
        // Yoko started from outside.
        //
        // 3 m, which is a little more than the 2.5 m from that spot to Yoko
        // herself, so the beat opens with V standing at her counter.
        if qs.GetFactStr("cc_g02_wakako_2") > 0
            && qs.GetFactStr("cc_g02_inn_reached") == 0
            // ON YOKO'S OWN SPOT, 3 m (2026-09-05). The doorway was captured at
            // (-1178.785, 2035.979): 2.0 m from the spot in front of her, so any
            // circle there reached the door, and 3.8 m from her own spot, where
            // V at her counter is 2.9 m. Her spot is wat_kab_netrunner_01_ws_idle.
            && this.Near(pos, new Vector4(-1177.83, 2039.69, 20.15, 1.0), 3.0) {
            qs.SetFactStr("cc_g02_inn_reached", 1);
        }

        // CHAR'S CHAIR, ONCE: the handover. Her verdict is a text message half
        // an in-game hour later, so there is no second visit (2026-09-03).
        // `to_char` is set by the graph, so this cannot fire on the walk past
        // her to Yoko.
        if qs.GetFactStr("cc_g02_to_char") > 0
            && qs.GetFactStr("cc_g02_char_near") == 0
            && this.Near(pos, CCGig02Places.Char(), 3.0) {
            qs.SetFactStr("cc_g02_char_near", 1);
        }

        if qs.GetFactStr("cc_g02_trace_done") > 0
            && qs.GetFactStr("cc_g02_parlor_reached") == 0
            && this.Near(pos, CCGig02Places.Parlor(), 20.0) {
            qs.SetFactStr("cc_g02_parlor_reached", 1);
        }

        // THE OFFICE OPENS ONCE THE RELAY IS CRACKED. Its note carries the
        // face now; the attendant and her camera log are gone (2026-09-03).
        // LEAVING THE PARLOR after her order, measured the way arriving is
        // (the same 20 m from the marker), so the community swap back to
        // the game's own Wakako happens out of sight (2026-09-05).
        if qs.GetFactStr("cc_g02_wakako_met") > 0
            && qs.GetFactStr("cc_g02_left_parlor") == 0
            && !this.Near(pos, CCGig02Places.Parlor(), 20.0) {
            qs.SetFactStr("cc_g02_left_parlor", 1);
        }
        if qs.GetFactStr("cc_g02_char_named") > 0
            && qs.GetFactStr("cc_g02_office_reached") == 0
            && this.Near(pos, CCGig02Places.Office(), 8.0) {
            qs.SetFactStr("cc_g02_office_reached", 1);
        }

        // THE TOP OF THE STAIRS, OR THE BOTTOM OF THEM.
        //
        // 30 m rather than the 45 the flat street used: the staircase falls
        // 19 m over 85 m, so a radius that covered the whole site would also
        // cover the bottom, and arriving would count as having got down.
        //
        // BUT ARRIVING FROM BELOW HAD TO BE ADDED, and it is the kind of hole
        // this gig keeps falling into. `Near` deliberately keeps its FLOOR
        // tight - 6 m - so that a road tunnelling under a trigger cannot fire
        // it. The top of these stairs is 19 m above the bottom, so a player who
        // drove to the foot of them and walked up was below that floor the
        // whole way and never armed the beat: no spawn, no Toji, no objective
        // moving, and nothing on screen to say why.
        //
        // The pin is on the top and most players will go there. This is for the
        // ones who do not.
        if qs.GetFactStr("cc_g02_wakako_met") > 0
            && qs.GetFactStr("cc_g02_hit_reached") == 0
            && (this.Near(pos, CCGig02Places.HitSite(), 30.0)
                || this.Near(pos, CCGig02Places.TojiPost(), 30.0)) {
            qs.SetFactStr("cc_g02_hit_reached", 1);
        }

        // DOWN, EITHER BY JUMPING OR BY WALKING IT.
        //
        // The pin is on the trash pile, which is the comic's route and the one
        // that gets past the men holding the lower steps. But a player who
        // fought their way down the stairs instead is also down, and an
        // objective that only a jump can close would strand them on a step with
        // nothing left to do.
        //
        // So: on the trash, OR anywhere near Toji's level at the bottom. The
        // second test is what makes this unstallable.
        if qs.GetFactStr("cc_g02_hit_reached") > 0
            && qs.GetFactStr("cc_g02_dropped") == 0
            && (this.Near(pos, CCGig02Places.Trash(), 6.0)
                || this.Near(pos, CCGig02Places.TojiPost(), 25.0)) {
            qs.SetFactStr("cc_g02_dropped", 1);
        }
    }

    // ================================================ the real Wakako's own talk
    //
    // HER DEFAULT DIALOGUE IS NOT OURS AND OWNING THE ACTOR DOES NOT CLOSE IT.
    // Playtest, 2026-08-26, screenshot: our line "Someone set up a relay in your
    // parlor." plays while "Tell me about Westbrook." and "How many husbands did
    // you have again?" sit in the same hub above it. Those are her own default
    // conversation's choices, and a mod acquiring her as a scene actor does not
    // take them away. Gig 01 established the same thing on Mama Welles.
    //
    // THE SWITCH IS THE GAME'S OWN AND IT IS NAMED FOR THIS JOB.
    // `base\open_world\fixers\wakako\scenes\wakako_okada_default.scene`
    // gates its branches on `wakako_default_temp_off`: 0 runs her small talk, 1
    // is the "she is busy" path. Vanilla writes it from outside, from whatever
    // story content currently owns her, so holding it up is the supported way
    // rather than a trick. Read out of the shipped scene, not guessed.
    //
    // BOUNDED THREE WAYS, because a base-game fact left at 1 leaves Wakako mute
    // for the rest of the save and nothing would ever attribute it to this mod:
    //
    //   only once V has reached her office
    //   only until the conversation is done
    //   only while V is within 60 m, so wandering off releases it and coming
    //   back sets it again, and an abandoned gig costs her nothing
    //
    // And it only ever clears a 1 it wrote itself.
    private func HoldWakako(qs: ref<QuestsSystem>, pos: Vector4) -> Void {
        // HELD FROM THE MOMENT THE GIG SENDS V TO HER, not from arriving.
        //
        // This was gated on `office_reached`, which is set when V is eight
        // metres from her desk - and by then her own greeting has already
        // started. A fact that gates a scene's START cannot close a hub that
        // is already open, so the options stayed up. Playtest, 2026-08-27,
        // screenshot: her "Tell me about Westbrook." sitting over our line.
        //
        // Gig 01 holds Mama Welles's flag from ARRIVING AT THE BAR rather than
        // from reaching her, for exactly this reason. `char_named` is this
        // gig's equivalent: it is set when the relay's note names the man,
        // which is when the journal starts pointing at her office. Sixty metres then
        // covers the whole parlor, so the flag is up long before V is close
        // enough for her to say anything.
        let want: Bool = qs.GetFactStr("cc_g02_char_named") > 0
            && qs.GetFactStr("cc_g02_wakako_met") == 0
            && Vector4.Distance(pos, CCGig02Places.Office()) < 60.0;
        if want {
            if qs.GetFactStr("wakako_default_temp_off") <= 0 {
                qs.SetFactStr("wakako_default_temp_off", 1);
                this.m_wakakoHeld = true;
            }
        } else {
            if this.m_wakakoHeld {
                qs.SetFactStr("wakako_default_temp_off", 0);
                this.m_wakakoHeld = false;
            }
        }
    }

    // ======================================================== the three groups
    //
    // There are always three knots of people standing outside Afterlife, and
    // the leg is now three of them to walk to and overhear rather than one
    // conversation that plays on arrival and then a hunt for a stranger in a
    // crowd. THE MAN TALKING IN THE THIRD GROUP IS THE MERC.
    //
    // WHAT THIS SIDE OWNS: which spot the player actually walked to, and when.
    // The quest phase owns the conversations and the journal, and the two meet
    // at three facts.
    //
    //   cc_g02_group_first    1 or 2, whichever of the first two was reached
    //   cc_g02_group_second   the other one, and only after the first is done
    //   cc_g02_group3_near    the last group, once both are done
    //
    // ONLY ONE IS EVER ARMED AT A TIME, which is what stops a player standing
    // between two groups from queueing both conversations onto one moment. The
    // phase has one scene for the first overheard conversation and one for the
    // second; it cannot play them at once, and a second scene entered while the
    // first is running is a beat nobody hears.
    private func Groups(game: GameInstance, qs: ref<QuestsSystem>,
                        pos: Vector4) -> Void {
        if qs.GetFactStr("cc_g02_afterlife_reached") == 0
            || qs.GetFactStr("cc_g02_lead_heard") > 0 {
            return;
        }

        // REPORT WHETHER EACH SPOT IS FIGHTABLE, once, the first time the
        // player is here. Inside a safe area the player cannot draw a weapon,
        // so a group placed in one cannot host the fight that ends this leg.
        // These three facts exist purely so the dev menu can say so out loud
        // rather than leaving it to be discovered by punching at a man who
        // cannot be hit.
        if qs.GetFactStr("cc_g02_safe_checked") == 0 {
            qs.SetFactStr("cc_g02_safe_checked", 1);
            if CCSharedWorld.InSafeArea(game, CCGig02Places.Group1()) {
                qs.SetFactStr("cc_g02_safe_g1", 1);
            }
            if CCSharedWorld.InSafeArea(game, CCGig02Places.Group2()) {
                qs.SetFactStr("cc_g02_safe_g2", 1);
            }
            if CCSharedWorld.InSafeArea(game, CCGig02Places.Group3()) {
                qs.SetFactStr("cc_g02_safe_g3", 1);
            }
        }

        let radius: Float = CCGig02Places.GroupRadius();

        // The last group, once the other two are done.
        if qs.GetFactStr("cc_g02_groups_done") > 0 {
            if qs.GetFactStr("cc_g02_group3_near") == 0
                && this.Near(pos, CCGig02Places.Group3(), radius) {
                qs.SetFactStr("cc_g02_group3_near", 1);
            }
            return;
        }

        let first: Int32 = qs.GetFactStr("cc_g02_group_first");
        if first == 0 {
            // WHICHEVER IS NEARER, not whichever is tested first. The two
            // groups stand within sight of each other, so a player who walks
            // between them is inside both radii and the order of the tests
            // would otherwise decide which conversation they get.
            let d1: Float = Vector4.Distance(pos, CCGig02Places.Group1());
            let d2: Float = Vector4.Distance(pos, CCGig02Places.Group2());
            if this.Near(pos, CCGig02Places.Group1(), radius) && d1 <= d2 {
                qs.SetFactStr("cc_g02_group_first", 1);
            } else {
                if this.Near(pos, CCGig02Places.Group2(), radius) {
                    qs.SetFactStr("cc_g02_group_first", 2);
                }
            }
            return;
        }

        // THE OTHER ONE, AND NOT BEFORE THE FIRST CONVERSATION HAS FINISHED.
        // `cc_g02_talk_a_done` is set by the quest phase when that scene exits,
        // so this cannot arm while somebody is still talking.
        if qs.GetFactStr("cc_g02_talk_a_done") == 0
            || qs.GetFactStr("cc_g02_group_second") > 0 {
            return;
        }
        let other: Vector4 = CCGig02Places.Group2();
        let done: Vector4 = CCGig02Places.Group1();
        if first == 2 {
            other = CCGig02Places.Group1();
            done = CCGig02Places.Group2();
        }
        // AND NEARER THAN THE ONE ALREADY HEARD. The two spots are 3.6 m apart,
        // so a radius wide enough to be caught while walking covers both of
        // them: without this the second conversation would start the moment the
        // first one ended, without the player moving a step, and the two pins
        // would be decoration. Comparing the two distances is what actually
        // means "he has walked over to the other group".
        if this.Near(pos, other, radius)
            && Vector4.Distance(pos, other) < Vector4.Distance(pos, done) {
            qs.SetFactStr("cc_g02_group_second", 1);
        }
    }

    // ======================================================== Char
    //
    // SHE IS NOT IN THIS FILE AT ALL, and that is the point of the conversion.
    //
    // Char is an entry in this gig's community. `gen_community.py` stands her
    // beside the netrunner's chair at the Dewdrop Inn, the quest phase switches
    // the entry on when Wakako sends V to her and off once the trace is
    // delivered, and `gig02_handover` and `gig02_trace` acquire that body as
    // their actor. Nothing here holds her, spawns her or removes her.
    //
    // What that bought, and each of these was a separate bug report: her mouth
    // moves, scanning her returns HER name instead of whichever passer-by was
    // sitting in the chair, and she is the same woman every load.
    //
    // SHE STANDS BESIDE THE CHAIR RATHER THAN IN IT. A community places the
    // body at its spot and does not put that body into the spot's workspot,
    // which gig 01 measured the hard way. Seating her is the quest-node
    // workspot route on top of this, and design.md carries it as open work.

    // ======================================================== the merc
    //
    // THE WHOLE LIFECYCLE, in the order it happens:
    //
    //   spawned, before V speaks   neutral   friendly to V   Invulnerable
    //   V has put the question     neutral   hostile to V    Immortal
    //   health below the threshold friendly  friendly to V   Invulnerable
    //   the leg is over            despawned
    //
    // FOUR SYSTEMS AND NONE OF THEM SUBSTITUTES FOR ANOTHER. The attitude GROUP
    // decides the reticle, the pairwise value decides what he thinks of V, god
    // mode decides whether damage lands, and only the second row lets him be
    // hurt at all. Gig 01's register records a failure for every one of those
    // set without the others.
    //
    // `Immortal` RATHER THAN `Invulnerable` FOR THE FIGHT, and this is the one
    // place the two differ in a way that matters. Invulnerable takes no damage
    // at all; Immortal takes damage that cannot finish him, so his health falls
    // and the threshold below can read it. Gig 01 wanted the opposite and said
    // so: Immortal was wrong THERE because something read Hoshino's health to
    // decide he had been provoked.
    // THE BRIEF HAS BEEN READ AND THE PHONE IS CLOSED. The graph waits on
    // `cc_g02_brief_read` before the gig and Johnny (playtest 2026-09-04: he
    // spoke over an unopened message). Visited is the journal's own flag for
    // the message; closed is the phone's contacts panel being down again, read
    // off the UI blackboard, so he waits until the thread is put away.
    private let m_briefTicks: Int32;

    private func BriefRead(game: GameInstance, qs: ref<QuestsSystem>) -> Void {
        if qs.GetFactStr("cc_g02_brief_read") > 0 || qs.GetFactStr("cc_g02_call1_done") == 0 {
            return;
        }
        // THE FLOOR. If the journal never reports the message visited (playtest
        // 2026-09-04: it did not, once), the gig must not wait forever.
        this.m_briefTicks += 1;
        if this.m_briefTicks > 45 {
            qs.SetFactStr("cc_g02_brief_read", 1);
            return;
        }
        let jm: ref<JournalManager> = GameInstance.GetJournalManager(game);
        if !IsDefined(jm) {
            return;
        }
        let entry: wref<JournalEntry> = jm.GetEntryByString(
            "contacts/cc_g02_wakako/cc_g02_wakako_conv/cc_g02_msg_04", "gameJournalPhoneMessage");
        if !IsDefined(entry) || !jm.IsEntryVisited(entry) {
            return;
        }
        let bb: ref<IBlackboard> = GameInstance.GetBlackboardSystem(game).Get(GetAllBlackboardDefs().UI_ComDevice);
        if IsDefined(bb) && bb.GetBool(GetAllBlackboardDefs().UI_ComDevice.ContactsActive) {
            return;
        }
        qs.SetFactStr("cc_g02_brief_read", 1);
    }

    // WHOEVER ELSE STANDS AT THE DOOR DOES NOT TURN ON V. Three playtests
    // (2026-09-04) had the game's own queue shoot back when the merc was shot,
    // and answering brings the police. The graph switches the two vanilla
    // communities off the way Rogue's date does, and the sector carries a
    // crowd null area; this is the guarantee underneath both: while the gig
    // owns the door, every NPC within 22 m of the posts that is not ours is
    // made friendly to V and given a bystander's reactions, so gunfire makes
    // it run rather than shoot. Once per body, remembered by id.
    private let m_calmed: array<EntityID>;

    private func Bystanders(game: GameInstance, qs: ref<QuestsSystem>,
                            player: ref<PlayerPuppet>) -> Void {
        if qs.GetFactStr("cc_g02_accepted") == 0 || qs.GetFactStr("cc_g02_merc_done") > 0 {
            return;
        }
        let door: Vector4 = new Vector4(-1470.2, 1046.0, 22.7, 1.0);
        if Vector4.Distance(player.GetWorldPosition(), door) > 60.0 {
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
        let playerAgent: ref<AttitudeAgent> = player.GetAttitudeAgent();
        let i: Int32 = 0;
        while i < ArraySize(parts) {
            let obj: ref<GameObject> = TS_TargetPartInfo.GetComponent(parts[i]).GetEntity() as GameObject;
            let npc: ref<ScriptedPuppet> = obj as ScriptedPuppet;
            if IsDefined(npc) && !npc.IsPlayer()
                && Vector4.Distance(npc.GetWorldPosition(), door) < 22.0
                && !this.IsOurs(npc.GetRecordID())
                && !ArrayContains(this.m_calmed, npc.GetEntityID()) {
                ArrayPush(this.m_calmed, npc.GetEntityID());
                // GONE, not calmed. Playtest 2026-09-04 (fifth): the CET
                // Dispose button removed all eleven bodies at the door at once,
                // where no community switch had moved one. Same call here.
                npc.Dispose();
            }
            i += 1;
        }
    }

    // THE DEWDROP INN IS OURS FOR THE LEG (2026-09-05). Two bodies that are
    // not ours are disposed while it runs, the way the door queue is: the
    // game's vendor Yoko if her entry lingers after the switch, and anyone
    // the crowd puts in Char's chair. Once per body, remembered by id.
    private func InnKeeper(game: GameInstance, qs: ref<QuestsSystem>,
                           player: ref<PlayerPuppet>) -> Void {
        if qs.GetFactStr("cc_g02_wakako_2") == 0 || qs.GetFactStr("cc_g02_trace_done") > 0 {
            return;
        }
        let inn: Vector4 = CCGig02Places.Inn();
        if Vector4.Distance(player.GetWorldPosition(), inn) > 40.0 {
            return;
        }
        let chair: Vector4 = CCGig02Places.Char();
        let query: TargetSearchQuery = TSQ_NPC();
        query.testedSet = TargetingSet.Complete;
        query.includeSecondaryTargets = false;
        query.ignoreInstigator = true;
        query.maxDistance = 40.0;
        query.filterObjectByDistance = true;
        let parts: array<TS_TargetPartInfo>;
        GameInstance.GetTargetingSystem(game).GetTargetParts(player, query, parts);
        let i: Int32 = 0;
        while i < ArraySize(parts) {
            let obj: ref<GameObject> = TS_TargetPartInfo.GetComponent(parts[i]).GetEntity() as GameObject;
            let npc: ref<ScriptedPuppet> = obj as ScriptedPuppet;
            if IsDefined(npc) && !npc.IsPlayer() && !this.IsOurs(npc.GetRecordID())
                && !ArrayContains(this.m_calmed, npc.GetEntityID()) {
                let rec: TweakDBID = npc.GetRecordID();
                let atChair: Bool = Vector4.Distance(npc.GetWorldPosition(), chair) < 1.5;
                let vendor: Bool = rec == t"Character.wat_kab_netrunner_01"
                    && Vector4.Distance(npc.GetWorldPosition(), inn) < 15.0;
                if atChair || vendor {
                    ArrayPush(this.m_calmed, npc.GetEntityID());
                    npc.Dispose();
                }
            }
            i += 1;
        }
        // CHAR BACK INTO HER CHAIR. She arrives while a stranger holds the
        // seat and the AI parks her beside it; once the chair is clear she is
        // sent to her own spot with the AI's use-workspot command, once.
        if !this.m_charSent {
            i = 0;
            while i < ArraySize(parts) {
                let obj: ref<GameObject> = TS_TargetPartInfo.GetComponent(parts[i]).GetEntity() as GameObject;
                let npc: ref<ScriptedPuppet> = obj as ScriptedPuppet;
                if IsDefined(npc) && npc.GetRecordID() == t"Character.cc_g02_char"
                    && Vector4.Distance(npc.GetWorldPosition(), chair) < 4.0 {
                    this.m_charSent = CCLab_UseWorkspot(npc, "$/mod/cc_g02_cast/#cc_g02_char_spot", true, false, false);
                }
                i += 1;
            }
        }
    }

    // THE QUEUE CANNOT BE AIMED AT (design call 2026-09-05: "the same state
    // of Hoshino before we finish talking"). Gig 01's recipe on Hoshino,
    // field for field: the attitude GROUP friendly, which is what the
    // reticle reads, the pairwise attitude to V friendly, and Invulnerable
    // god mode, all re-asserted every tick because an attitude set on a body
    // still resolving does nothing. On every one of our seven queue bodies,
    // for as long as the door is ours; the merc is the one exception and
    // keeps his own rules.
    private func QueueShield(game: GameInstance, qs: ref<QuestsSystem>,
                             player: ref<PlayerPuppet>) -> Void {
        if qs.GetFactStr("cc_g02_accepted") == 0 || qs.GetFactStr("cc_g02_merc_done") > 0 {
            return;
        }
        let door: Vector4 = CCGig02Places.Afterlife();
        if Vector4.Distance(player.GetWorldPosition(), door) > 60.0 {
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
        let gods: ref<GodModeSystem> = GameInstance.GetGodModeSystem(game);
        let i: Int32 = 0;
        while i < ArraySize(parts) {
            let obj: ref<GameObject> = TS_TargetPartInfo.GetComponent(parts[i]).GetEntity() as GameObject;
            let npc: ref<ScriptedPuppet> = obj as ScriptedPuppet;
            if IsDefined(npc) && this.IsQueue(npc.GetRecordID()) {
                let agent: ref<AttitudeAgent> = npc.GetAttitudeAgent();
                if IsDefined(agent) && IsDefined(player.GetAttitudeAgent()) {
                    agent.SetAttitudeGroup(n"friendly");
                    agent.SetAttitudeTowards(player.GetAttitudeAgent(), EAIAttitude.AIA_Friendly);
                }
                if IsDefined(gods) && !gods.HasGodMode(npc.GetEntityID(), gameGodModeType.Invulnerable) {
                    gods.AddGodMode(npc.GetEntityID(), gameGodModeType.Invulnerable, n"cc_g02_queue");
                }
            }
            i += 1;
        }
    }

    private func IsQueue(rec: TweakDBID) -> Bool {
        return rec == t"Character.cc_g02_queue_a" || rec == t"Character.cc_g02_queue_b"
            || rec == t"Character.cc_g02_queue_c" || rec == t"Character.cc_g02_queue_d"
            || rec == t"Character.cc_g02_queue_e" || rec == t"Character.cc_g02_queue_f"
            || rec == t"Character.cc_g02_queue_g";
    }

    // WAKAKO IS OURS FOR THE LEG (2026-09-05), the Inn's rule again: the
    // game's own Wakako is disposed if she lingers after the community
    // switch, from Char's verdict until the order is given. Her doorman is
    // the game's and is left alone. Once per body, remembered by id.
    private func ParlorKeeper(game: GameInstance, qs: ref<QuestsSystem>,
                              player: ref<PlayerPuppet>) -> Void {
        if qs.GetFactStr("cc_g02_trace_done") == 0 || qs.GetFactStr("cc_g02_wakako_met") > 0 {
            return;
        }
        let office: Vector4 = CCGig02Places.Office();
        if Vector4.Distance(player.GetWorldPosition(), office) > 40.0 {
            return;
        }
        let query: TargetSearchQuery = TSQ_NPC();
        query.testedSet = TargetingSet.Complete;
        query.includeSecondaryTargets = false;
        query.ignoreInstigator = true;
        query.maxDistance = 40.0;
        query.filterObjectByDistance = true;
        let parts: array<TS_TargetPartInfo>;
        GameInstance.GetTargetingSystem(game).GetTargetParts(player, query, parts);
        let i: Int32 = 0;
        while i < ArraySize(parts) {
            let obj: ref<GameObject> = TS_TargetPartInfo.GetComponent(parts[i]).GetEntity() as GameObject;
            let npc: ref<ScriptedPuppet> = obj as ScriptedPuppet;
            if IsDefined(npc) && !npc.IsPlayer() && !this.IsOurs(npc.GetRecordID())
                && !ArrayContains(this.m_calmed, npc.GetEntityID()) {
                let rec: TweakDBID = npc.GetRecordID();
                if rec == t"Character.wakako_okada"
                    && Vector4.Distance(npc.GetWorldPosition(), office) < 20.0 {
                    ArrayPush(this.m_calmed, npc.GetEntityID());
                    npc.Dispose();
                }
            }
            i += 1;
        }
    }

    private func IsOurs(rec: TweakDBID) -> Bool {
        return rec == t"Character.cc_g02_merc"
            || rec == t"Character.cc_g02_queue_a" || rec == t"Character.cc_g02_queue_b"
            || rec == t"Character.cc_g02_queue_c" || rec == t"Character.cc_g02_queue_d"
            || rec == t"Character.cc_g02_queue_e"
            || rec == t"Character.cc_g02_queue_f" || rec == t"Character.cc_g02_queue_g"
            || rec == t"Character.cc_g02_yoko" || rec == t"Character.cc_g02_char"
            || rec == t"Character.cc_g02_wakako" || rec == t"Character.cc_g02_huscle";
    }

    private func Merc(game: GameInstance, qs: ref<QuestsSystem>,
                      player: ref<PlayerPuppet>, pos: Vector4) -> Void {
        if qs.GetFactStr("cc_g02_wakako_2") > 0 {
            // The leg is over: V has called it in and is on his way to the
            // Dewdrop Inn. Take the body away rather than leaving a shielded,
            // friendly Wraith outside Afterlife for the rest of the save.
            this.ReleaseMerc(game);
            return;
        }
        if qs.GetFactStr("cc_g02_afterlife_reached") == 0 {
            return;
        }

        if !this.m_mercSpawned {
            // HE IS THE COMMUNITY'S BODY NOW, not a spawn of this script's.
            //
            // He used to be spawned here while a separate, invisible scene
            // actor a kilometre away carried his voice and his lipsync. That is
            // what made his mouth not move, and it is the same choice that made
            // Char unscannable and the handover unanimatable. One body now:
            // the community stands him with the third group, the quest phase
            // switches the entry on, and the scenes speak through him.
            //
            // NOTHING IS SPAWNED ANYWHERE. If the entry is off, or the sector
            // is not loading, he is simply not found and this retries next
            // tick. `cc_g02_merc_placed` is what tells those apart in the dev
            // menu.
            this.m_mercId = this.FindInCommunity(CCGig02Combat.MercEntry());
            if EntityID.IsDefined(this.m_mercId) {
                this.m_mercSpawned = true;
                qs.SetFactStr("cc_g02_merc_placed", 1);
            }
            return;
        }

        let merc: ref<ScriptedPuppet> =
            GameInstance.FindEntityByID(game, this.m_mercId) as ScriptedPuppet;
        if !IsDefined(merc) {
            return;
        }

        // NO "WALK UP TO HIM" GATE ANY MORE. The player has just stood in his
        // group and listened to him describe the job, so the confrontation
        // opens straight off the end of that conversation. The old
        // `cc_g02_merc_near` wait existed because the lead used to be
        // anonymous chatter somewhere else entirely.

        // THE MARKER. Up from the moment the gig asks for him and gone the
        // moment he is down. Without it he is one body in a queue outside
        // Afterlife and there is nothing to tell him from the crowd, which is
        // exactly what the first playtest reported.
        // AND IT COMES OFF ON EITHER FORK. `merc_down` only ever arrives on the
        // fight one; a player who talked him out of the shard would otherwise
        // be left with a marker over a man there is nothing left to do with.
        let wantPin: Bool = qs.GetFactStr("cc_g02_lead_heard") > 0
            && qs.GetFactStr("cc_g02_shard_taken") == 0
            && qs.GetFactStr("cc_g02_merc_done") == 0;
        if wantPin {
            this.m_mercPin = this.ShowOrMove(game, this.m_mercPinOn,
                                             this.m_mercPin,
                                             merc.GetWorldPosition());
            this.m_mercPinOn = true;
        } else {
            if this.m_mercPinOn {
                CCSharedMappins.Hide(game, this.m_mercPin);
                this.m_mercPinOn = false;
            }
        }

        let armed: Bool = qs.GetFactStr("cc_g02_merc_armed") > 0;
        let down: Bool = qs.GetFactStr("cc_g02_merc_down") > 0;
        // READ ONCE, USED THREE TIMES: the two beating stages below and the
        // "has he been touched yet" test that decides whether he can see.
        let hp: Float = GameInstance.GetStatPoolsSystem(game)
            .GetStatPoolValue(Cast<StatsObjectID>(this.m_mercId),
                              gamedataStatPoolType.Health, false);

        // THE CLOCK, and it is the dead man's handle.
        //
        // `cc_g02_merc_down` is set below, by this file. But `cc_g02_merc_armed`
        // is set by a QUEST NODE, and a save made before this version existed is
        // past that node forever: the fact can never arrive, he stays
        // Invulnerable and friendly, and the gig cannot be finished. Nothing in
        // normal testing finds that, because testing starts from a clean save
        // and goes forward.
        //
        // So being here starts a clock. Three minutes with the merc standing and
        // nothing having happened means nothing is going to, and the shield is
        // dropped. A real fight takes seconds. NOT PERSISTED, so a reload
        // restarts it, which is right: a reload respawns him too.
        if armed && !down {
            this.m_mercTicks += 1;
        }
        let stuck: Bool = this.m_mercTicks > 180;

        // STAGE ONE: beaten down.
        if !down && armed && !stuck && hp <= CCGig02Combat.MercDownAt() {
            qs.SetFactStr("cc_g02_merc_down", 1);
            down = true;
            NPCPuppet.ChangeHighLevelState(merc, gamedataNPCHighLevelState.Relaxed);
        }

        // ON THE FLOOR, ALIVE. The pose lab (2026-09-05) tried the AI's own
        // workspot command in four shapes, nine poses and five knock-downs; the
        // one transition that reads as a fall and leaves a body that is hurt
        // rather than dead is the game's own Defeated fall followed by
        // Bleeding. The shard goes into his pocket when he says to take it
        // (given before the fall it never appeared in the list). Counted on a script field, so a reload re-applies the
        // floor state to a body that respawned standing.
        if down {
            this.m_floorTicks += 1;
            if this.m_floorTicks == 1 {
                StatusEffectHelper.ApplyStatusEffect(merc, t"BaseStatusEffect.Defeated");
            }
            if this.m_floorTicks == 3 {
                StatusEffectHelper.ApplyStatusEffect(merc, t"BaseStatusEffect.BleedingInfinite");
            }
            // HIS OWN LOOT GOES: the fall generates his record's drops (weapons
            // one time, a skill shard the next, playtest 2026-09-05), and the
            // list on his body should hold our shard and nothing else. Every
            // tick, because a drop can land a tick late.
            CCLab_StripAll(merc, "Items.cc_g02_shard");
            let ts: ref<TransactionSystem> = GameInstance.GetTransactionSystem(game);
            let shard: ItemID = ItemID.FromTDBID(CCGig02Shard.ShardItem());
            // THE SHARD FROM THE FALL. Given later, the loot list the player is
            // already looking at does not refresh until they look away and
            // back (playtest 2026-09-05), so it is there from the start and
            // his lines catch up with it.
            if this.m_floorTicks >= 3 && qs.GetFactStr("cc_g02_shard_planted") == 0
                && !ts.HasItem(merc, shard) && !ts.HasItem(player, shard) {
                if ts.GiveItem(merc, shard, 1) {
                    qs.SetFactStr("cc_g02_shard_planted", 1);
                }
            }
            // TAKEN OR READ. Reading a shard off a body (R) consumes it into the
            // journal's shards and it is gone from the list, so a read is the
            // take (playtest 2026-09-05). Nothing later needs the item itself:
            // the journal entry is what travels.
            if qs.GetFactStr("cc_g02_shard_taken") == 0
                && (ts.HasItem(player, shard) || qs.GetFactStr("cc_g02_proof_read") > 0) {
                qs.SetFactStr("cc_g02_shard_taken", 1);
            }
        }


        // ...UNTIL V TELLS HIM TO GO.
        //
        // The proof is read and in the inventory by now, so nothing downstream
        // needs him. He stays on the ground and is taken out of the world once
        // the player is not looking at him; see FleeMerc for why he is not
        // stood up.
        //
        // THE GIG NEVER WAITS ON ANY OF THIS. The quest phase sets the fact and
        // carries straight on to the call.
        if qs.GetFactStr("cc_g02_merc_flee") > 0 {
            this.FleeMerc(game, merc, pos);
            return;
        }

        // NO FLOOR STATE ANY MORE, 2026-09-03. `BaseStatusEffect.Defeated` held
        // him in a knocked-down physics state that snapped upright when
        // released, and it is gone: the begging scene puts him on one knee with
        // a vanilla workspot, which animates its own entry and exit.

        // NO DISMEMBERMENT. He is unkillable through the fight, so a kill
        // cannot take a limb, but a blade can on a living target. The hit
        // dismemberment factor goes to zero once, the first tick she exists.
        if !this.m_mercNoDismember {
            let stats: ref<StatsSystem> = GameInstance.GetStatsSystem(game);
            if IsDefined(stats) {
                stats.AddModifier(Cast<StatsObjectID>(this.m_mercId),
                    RPGManager.CreateStatModifier(
                        gamedataStatType.HitDismembermentFactor,
                        gameStatModifierType.Multiplier, 0.0));
                this.m_mercNoDismember = true;
            }
        }

        // THE PLAYER CHOSE TO FINISH IT. The shield comes off below, and the
        // moment he is dead the graph moves on.
        let killArmed: Bool = qs.GetFactStr("cc_g02_merc_kill_armed") > 0;
        if killArmed && qs.GetFactStr("cc_g02_merc_dead") == 0
            && !ScriptedPuppet.IsAlive(merc) {
            qs.SetFactStr("cc_g02_merc_dead", 1);
        }
        // HE DIES WHERE HE LIES (playtest 2026-09-05, twice: shot on the
        // floor, he stood up before falling again). The death task plays
        // an animated death unless it decides on a ragdoll, and it decides
        // on a ragdoll when the puppet is flagged to skip its death
        // animation (aiDeathReactionTask.ShouldUseRagdoll). NPCPuppet.Kill
        // with skipNPCDeathAnim sets exactly that flag. So once the kill is
        // armed he is Immortal (damage lands, death does not), the first
        // hit takes the shield off, and Kill drops him from the pose he is
        // in. The first attempt applied ForceKillFromRagdoll instead, which
        // is the effect the task checks to NOT ragdoll a body that already
        // is; on a body that is not, it is the stand-up.
        //
        // IN STAGES, ONE PER TICK (playtest 2026-09-05, third report: with
        // the shield removed and Kill called in the same tick he could not
        // be killed at all, however many shots). The god mode system and
        // the stat pool both take requests, so removing the shield and
        // zeroing his health in one call may land in the wrong order. Now
        // the hit only takes the shield off; Kill is the next tick; if he
        // is still alive two ticks later the game's own ForceKill effect
        // goes on; and after that the shield simply stays off, so ordinary
        // shots end it even if the pose does not survive. The hit itself is
        // read two ways: a hit event on his body (the wrap at the bottom of
        // this file sets `cc_g02_merc_hit`), and health falling between two
        // ticks. `cc_g02_merc_kill_stage` says how far this got, for the
        // dev menu.
        if killArmed && ScriptedPuppet.IsAlive(merc) {
            let hit: Bool = qs.GetFactStr("cc_g02_merc_hit") > 0
                || (this.m_mercKillHp > 0.0 && hp < this.m_mercKillHp - 0.5);
            if Equals(this.m_mercKillStage, 0) && hit {
                let godsNow: ref<GodModeSystem> = GameInstance.GetGodModeSystem(game);
                if Equals(this.m_mercMode, 2) {
                    godsNow.RemoveGodMode(this.m_mercId, gameGodModeType.Immortal,
                                          CCGig02Combat.MercShield());
                }
                if Equals(this.m_mercMode, 1) {
                    godsNow.RemoveGodMode(this.m_mercId, gameGodModeType.Invulnerable,
                                          CCGig02Combat.MercShield());
                }
                this.m_mercMode = 0;
                this.m_mercKilled = true;
                this.m_mercKillStage = 1;
                this.m_mercKillTicks = 0;
                qs.SetFactStr("cc_g02_merc_kill_stage", 1);
            } else {
                if Equals(this.m_mercKillStage, 1) {
                    let body: ref<NPCPuppet> = merc as NPCPuppet;
                    if IsDefined(body) {
                        body.Kill(player, true, false);
                    }
                    this.m_mercKillStage = 2;
                    qs.SetFactStr("cc_g02_merc_kill_stage", 2);
                } else {
                    if Equals(this.m_mercKillStage, 2) {
                        this.m_mercKillTicks += 1;
                        if this.m_mercKillTicks >= 2 {
                            StatusEffectHelper.ApplyStatusEffect(merc, t"BaseStatusEffect.ForceKill");
                            this.m_mercKillStage = 3;
                            qs.SetFactStr("cc_g02_merc_kill_stage", 3);
                        }
                    }
                }
            }
            this.m_mercKillHp = hp;
        }

        let agent: ref<AttitudeAgent> = merc.GetAttitudeAgent();
        let playerAgent: ref<AttitudeAgent> = player.GetAttitudeAgent();
        let gods: ref<GodModeSystem> = GameInstance.GetGodModeSystem(game);

        // RE-ASSERTED EVERY TICK rather than once on the transition. An attitude
        // set on an entity that is still resolving silently does nothing, which
        // is the whole reason CCSharedAttitude retries, and one missed call here
        // is a targetable or a hostile merc for the rest of the visit. It is two
        // calls a second.
        if IsDefined(agent) && IsDefined(playerAgent) {
            if armed && !down && !stuck {
                // HE DOES NOT START IT. He has no reason to: as far as he
                // knows the job was legitimate and V is a stranger who asked
                // him a question. Playtest, 2026-08-26: "they should not attack
                // us, they have no reason to, and they don't know we will
                // attack them."
                //
                // NEUTRAL IS WHAT MAKES HIM HITTABLE WITHOUT MAKING HIM
                // HOSTILE. Friendly is untargetable - the game will not lock
                // on - and hostile means he opens fire on sight. Neutral is
                // the third state: he stands there, he can be aimed at, and
                // he reacts to being hit like anyone else would.
                //
                // AND ATTITUDE ALONE WAS NOT ENOUGH. Playtest, 2026-08-26,
                // against exactly this: "she targets V immediately."
                //
                // The body is a Wraith, and a Wraith's own record makes him an
                // enemy of the player through the reaction system, which does
                // not consult the pairwise attitude before deciding it has seen
                // a threat. Writing Neutral once a second loses a race against
                // an NPC who has already decided.
                //
                // SO HE IS DEAFENED AND BLINDED UNTIL V HITS HIM. With his
                // senses component off there is nothing to react TO: he cannot
                // perceive the player, so he cannot open on him. He is still
                // solid, still targetable and still takes damage - the only
                // thing removed is his ability to notice anything, which is
                // exactly the state the beat wants. He thinks the job was
                // legitimate and a stranger just asked him a question.
                //
                // THE MOMENT HE IS HIT, HE GETS THEM BACK and the script
                // stops touching his attitude at all. Health below full is the
                // signal, because it cannot be anything other than V: nothing
                // else in this scene can hurt him.
                let untouched: Bool = hp >= 99.0;
                if untouched {
                    agent.SetAttitudeGroup(n"neutral");
                    agent.SetAttitudeTowards(playerAgent, EAIAttitude.AIA_Neutral);
                }
                // HIS EYES GO ON WHEN HE IS HIT, and only then. His record
                // ships `enableSensesOnStart: false`, so he starts unable to
                // perceive V at all - that is where the "he does not start
                // it" behaviour lives now, and a record cannot lose a race to
                // a reaction preset the way a per-tick write did.
                if !untouched && this.m_mercBlind {
                    let senses: ref<SenseComponent> = merc.GetSensesComponent();
                    if IsDefined(senses) {
                        senses.Toggle(true);
                    }
                    this.m_mercBlind = false;
                }
            } else {
                if killArmed {
                    // Killable and a target again, in the neutral group: his
                    // kill brought no police in play (2026-09-05), which is
                    // the measurement backlog 24 asked for.
                    agent.SetAttitudeGroup(n"neutral");
                    agent.SetAttitudeTowards(playerAgent, EAIAttitude.AIA_Neutral);
                } else {
                    // Before the fight and after he has begged: friendly, which
                    // is also what makes him untargetable. God mode alone
                    // produces the worst of the three states: the game locks
                    // on, draws a health bar, invites the shot and ignores it.
                    agent.SetAttitudeGroup(n"friendly");
                    agent.SetAttitudeTowards(playerAgent, EAIAttitude.AIA_Friendly);
                }
            }
        }

        if IsDefined(gods) {
            // WHICH SHIELD HE SHOULD HAVE RIGHT NOW, derived every tick from
            // facts that are in the save. A missed tick, a reload mid-fight and
            // a scene that never played all reach the right answer on the next
            // pass, which is the rule gotcha 21 exists for.
            //
            //   before V speaks   Invulnerable   a stray shot cannot start it
            //   the fight         Immortal       damage lands, death does not
            //   he is down        Invulnerable   a shotgun cannot end the gig
            //   the clock ran out none           see m_mercTicks above
            // Immortal only while the fight is on. Once he is down he talks,
            // and goes back to a shield that ignores everything, so a shotgun
            // cannot end the gig over a man who has already answered.
            //   the kill is armed Immortal       the hit is read, Kill does the rest
            let want: Int32 = 1;
            if stuck || this.m_mercKilled {
                want = 0;
            } else {
                if killArmed || (armed && !down) {
                    want = 2;
                }
            }
            // BOTH ARE HELD UNDER THE SAME SOURCE, so the one coming off has to
            // be named by type: removing a shield by source alone is not
            // something this project has measured.
            if NotEquals(want, this.m_mercMode) {
                if Equals(this.m_mercMode, 1) {
                    gods.RemoveGodMode(this.m_mercId, gameGodModeType.Invulnerable,
                                       CCGig02Combat.MercShield());
                }
                if Equals(this.m_mercMode, 2) {
                    gods.RemoveGodMode(this.m_mercId, gameGodModeType.Immortal,
                                       CCGig02Combat.MercShield());
                }
                if Equals(want, 1) {
                    gods.AddGodMode(this.m_mercId, gameGodModeType.Invulnerable,
                                    CCGig02Combat.MercShield());
                }
                if Equals(want, 2) {
                    gods.AddGodMode(this.m_mercId, gameGodModeType.Immortal,
                                    CCGig02Combat.MercShield());
                }
                this.m_mercMode = want;
            }
        }
    }

    // Let him go, WITHOUT STANDING HIM UP ON SCREEN.
    //
    // THE STAND-UP LOOKED WRONG AND THERE IS NO GOOD VERSION OF IT. A defeated
    // NPC is held in a knocked-down physics state; clearing `Defeated` releases
    // that and the body snaps upright with no transition, because the game has
    // no "get up off the floor and run" animation exposed to a mod. Playtest,
    // 2026-08-26: "the animation where he gets up is terrible."
    //
    // Making it look right would mean an authored animation and a workspot to
    // play it from, which is a piece of work this project has not done and
    // which buys four seconds of one beat.
    //
    // SO THE BEAT SURVIVES AND THE ANIMATION DOES NOT. V tells him to go, the
    // exchange plays, and he is simply not there any more once the player has
    // turned away. What the player sees is: he is on the ground, V lets him
    // live, and later there is nobody in the street. Nothing on screen is wrong,
    // and the story beat - V had a choice and took it - is the part that was
    // being bought.
    //
    // Deleting the whole thing is the alternative and it is one line: drop the
    // `gig02_dismiss` scene from gen_questphase and this function with it.
    //
    // 25 M OR THIRTY SECONDS. Distance first, because that is the case where
    // the player genuinely cannot see him; the clock is for a player who stands
    // over him and never leaves, and both are far enough from the conversation
    // that a body vanishing is not something anyone is looking at.
    private func FleeMerc(game: GameInstance, merc: ref<ScriptedPuppet>,
                          playerPos: Vector4) -> Void {
        // HE RUNS THE WAY A BYSTANDER RUNS, 2026-09-03. His record carries no
        // reactions at all (so he never opened on V by himself), so the first
        // flee tick gives him a civilian's reaction preset and a fright, and
        // the game's own panic behaviour, animated, takes him off the street.
        // If that does not take on a Wraith body, the distance and the clock
        // below still remove him once the player is not looking.
        // HE DOES NOT GET UP, 2026-09-05. Taking the two effects off made him
        // stand in one frame (the lab showed it), so letting him go is V not
        // shooting, one line, and the next objective. He stays on the floor,
        // shielded, until the quest phase retires his entry with the queue.
        this.m_mercFleeing = true;
        this.m_fleeTicks += 1;
        if Vector4.Distance(playerPos, merc.GetWorldPosition()) > 40.0
            || this.m_fleeTicks > 45 {
            this.ReleaseMerc(game);
        }
    }

    // Release everything this script put ON him. See the note inside: the
    // body itself belongs to the community and the quest phase retires it.
    private func ReleaseMerc(game: GameInstance) -> Void {
        if !this.m_mercSpawned {
            return;
        }
        // TAKE THE SHIELD OFF BEFORE THE BODY. A god mode left registered
        // against an entity id that no longer exists is not something anyone
        // here has measured, and the two lines cost nothing.
        let gods: ref<GodModeSystem> = GameInstance.GetGodModeSystem(game);
        if IsDefined(gods) {
            gods.RemoveGodMode(this.m_mercId, gameGodModeType.Immortal,
                               CCGig02Combat.MercShield());
            gods.RemoveGodMode(this.m_mercId, gameGodModeType.Invulnerable,
                               CCGig02Combat.MercShield());
        }
        if this.m_mercPinOn {
            CCSharedMappins.Hide(game, this.m_mercPin);
            this.m_mercPinOn = false;
        }
        // THE BODY IS NOT DELETED HERE ANY MORE, and that is the point of the
        // whole conversion. He belongs to the community; `DeleteEntity` on a
        // community body would take him out from under the system that owns
        // him. THE QUEST PHASE DEACTIVATES THE ENTRY, which is the supported
        // way and is also what stops a reload bringing him back.
        //
        // What is left here is everything that IS ours: the shield, the marker,
        // and the flags that have to reset so a reload can find him again.
        this.m_mercSpawned = false;
        this.m_mercMode = 0;
        this.m_mercNoDismember = false;
        this.m_mercFleeing = false;
        this.m_floorTicks = 0;
        this.m_mercBlind = true;
        this.m_fleeTicks = 0;
    }

    // ======================================================== the two readers
    //
    // Both are raised from here rather than from the quest phase, because a
    // quest node cannot queue a UI event. The phase sets the open fact and this
    // watches for it.
    private func Readers(game: GameInstance, qs: ref<QuestsSystem>) -> Void {
        // THE MERC'S SHARD. V takes it off him as well as reading it, because
        // Wakako asks for it to be carried to her netrunner, so it has to exist
        // in the inventory between two legs.
        // NOTHING IS HANDED OVER AND NOTHING OPENS BY ITSELF, 2026-09-05. The
        // shard is in his pocket from the moment he is down (see Merc), the
        // player takes it off him through the game's own loot list, and reads
        // it from there or from the journal's shards. The reader wrap in
        // Gig02_Shard.reds sets `proof_read` on either route, and this poll
        // is the second signal, as in gig 01: the journal's own visited flag.
        if qs.GetFactStr("cc_g02_merc_down") > 0
            && qs.GetFactStr("cc_g02_proof_read") == 0
            && CCGig02Shard.HasBeenRead(game, CCGig02Shard.ShardPath()) {
            qs.SetFactStr("cc_g02_proof_read", 1);
        }


    }

    // ======================================================== the access point
    //
    // THE PARLOR BEAT IS A BREACH (design call 2026-09-05). The mod places the
    // game's own access point on the parlor's wall (gen_sector.py), the
    // player jacks in and plays the game's own code grid, and this is the
    // half that notices: a marker on the box while the objective is up, and
    // the device's own answer to "was it breached" polled once a second.
    //
    // `AccessPointControllerPS.IsBreached()` is the game's own flag, set on
    // the Succeeded state of the minigame (accessPointController.swift,
    // OnNPCBreachEvent), and it persists, so a reload after the breach reads
    // true again. The wrap on FinalizeNetrunnerDive at the bottom of this
    // file is the second signal, for the frame the grid closes.
    private func AccessPoint(game: GameInstance, qs: ref<QuestsSystem>,
                             player: ref<PlayerPuppet>, pos: Vector4) -> Void {
        if qs.GetFactStr("cc_g02_parlor_reached") == 0
            || qs.GetFactStr("cc_g02_ap_breached") > 0 {
            if this.m_apPinOn {
                CCSharedMappins.Hide(game, this.m_apPin);
                this.m_apPinOn = false;
            }
            return;
        }
        let box: Vector4 = CCGig02Places.AccessPoint();
        if !this.m_apPinOn {
            this.m_apPin = this.ShowOrMove(game, false, this.m_apPin, box);
            this.m_apPinOn = true;
        }
        if Vector4.Distance(pos, box) > 30.0 {
            return;
        }
        let query: TargetSearchQuery = TSQ_ALL();
        query.testedSet = TargetingSet.Complete;
        query.includeSecondaryTargets = false;
        query.ignoreInstigator = true;
        query.maxDistance = 30.0;
        query.filterObjectByDistance = true;
        let parts: array<TS_TargetPartInfo>;
        GameInstance.GetTargetingSystem(game).GetTargetParts(player, query, parts);
        let i: Int32 = 0;
        while i < ArraySize(parts) {
            let obj: ref<GameObject> = TS_TargetPartInfo.GetComponent(parts[i]).GetEntity() as GameObject;
            let dev: ref<Device> = obj as Device;
            if IsDefined(dev) && Vector4.Distance(dev.GetWorldPosition(), box) < 2.5 {
                let ps: ref<AccessPointControllerPS> = dev.GetDevicePS() as AccessPointControllerPS;
                if IsDefined(ps) {
                    // THE GRID'S OWN DAEMON (source/tweaks/minigame.yaml): the
                    // device ships no stored state, so its minigame is named
                    // here, every tick the objective is up. Idempotent.
                    ps.CCGig02SetMinigame(t"minigame_v2.cc_g02_parlor");
                    if ps.IsBreached() {
                        qs.SetFactStr("cc_g02_ap_breached", 1);
                        return;
                    }
                }
            }
            i += 1;
        }
    }

    // ======================================================== the hit
    //
    // Toji, his company, the stealth condition and the stand-down.
    private func Hit(game: GameInstance, qs: ref<QuestsSystem>,
                     player: ref<PlayerPuppet>, pos: Vector4) -> Void {
        // THE STREET IS POPULATED THE MOMENT V ARRIVES, not after the approach
        // conversation, and the difference matters: the comic has V scan a
        // street that already has people in it, and men who stream in while the
        // player is looking at the spot are men who appear out of nothing.
        //
        // `hit_reached` is a 45 m radius, which is far enough to be out of the
        // way and near enough that the navmesh the spawn needs is streamed in.
        // Spawning from across the city would simply fail: Scatter asks the
        // navigation system for a standable point, and there is nothing to ask
        // about in a sector that is not loaded.
        if qs.GetFactStr("cc_g02_hit_reached") == 0 {
            return;
        }

        if !this.m_hitSpawned {
            // NOT AFTER HE IS ALREADY DEAD. `hit_reached` stays 1 for the rest
            // of the save, so without this a reload after the kill would stand
            // Toji back up alive on the street he was killed on. Gotcha 21: a
            // latch is exercised once by testing, always in the clean
            // direction, so this path has to be reasoned about at the desk.
            if qs.GetFactStr("cc_g02_toji_dead") > 0 {
                return;
            }
            this.SpawnHit(game);
            return;
        }

        let toji: ref<ScriptedPuppet> =
            GameInstance.FindEntityByID(game, this.m_tojiId) as ScriptedPuppet;

        // SEEN, ON THE WAY IN OR THE WAY OUT (playtest 2026-09-05: killed
        // Toji unseen, seen while leaving, and got the quiet ending). This
        // used to sit inside the block that runs only while Toji is alive, so
        // nothing watched the Claws once he was dead. It watches from the
        // objective going up until V is clear.
        if qs.GetFactStr("cc_g02_hit_armed") > 0
            && qs.GetFactStr("cc_g02_spotted") == 0
            && qs.GetFactStr("cc_g02_exfil_done") == 0
            && this.AnyClawFighting(game) {
            qs.SetFactStr("cc_g02_spotted", 1);
            CCSharedHud.NotifyTyped(game,
                GetLocalizedTextByKey(n"cc-g02-hud-spotted"),
                SimpleMessageType.Negative, 5.0);
        }

        // IS HE DEAD. THIS IS THE ONE THING THE QUEST WAITS FOR, so it is read
        // before any of the early returns below can skip a tick.
        //
        // It used to sit lower, under the `exfil_done` return, where a player
        // who killed him and moved 70 m off could in principle cross that line
        // before the tick noticed the body. Moved up on 2026-09-06 so the
        // ordering cannot matter either way.
        //
        // `toji_met` is written alongside it. Nothing in the flow reads it any
        // more, and the dev menu still shows it.
        if qs.GetFactStr("cc_g02_toji_dead") == 0
            && IsDefined(toji) && !ScriptedPuppet.IsAlive(toji) {
            qs.SetFactStr("cc_g02_toji_dead", 1);
            qs.SetFactStr("cc_g02_toji_met", 1);
        }

        // THE DEN STANDS DOWN ONCE V IS CLEAR (design question 2026-09-06:
        // "after the gig they should be back to normal behaviour"). These
        // Claws are OURS, spawned by SpawnHit and not persistent, so nothing
        // of the game's is touched; but the hostile attitude below was
        // re-asserted every tick for as long as this system ticked, which is
        // until the fee lands. Now it stops at `exfil_done`, each man goes
        // back to the neutral attitude his record starts with, and once the
        // closing call is over (`closed`) the bodies are deleted. V is 70 m
        // up the stairs by then. Toji is the community's and is switched off
        // by the phase with the rest of the cast.
        if qs.GetFactStr("cc_g02_exfil_done") > 0 {
            this.ReleaseClaws(game, player, qs.GetFactStr("cc_g02_closed") > 0);
            return;
        }

        // THEY ARE V'S ENEMIES, AND SAY SO (playtest 2026-09-05: "I'm right in
        // their face and they do nothing"). A gang record on its own turf
        // leaves a stranger alone until provoked; these men are a den on a
        // job, so every one of them, Toji included, holds a hostile attitude
        // to V, re-asserted every tick the way Hoshino's shield is, because
        // an attitude set on a body still resolving does nothing. Hostile
        // means they shoot when they SEE him; seeing him is still on their
        // senses, which is the stealth beat.
        this.HostileToV(game, player, toji);

        if qs.GetFactStr("cc_g02_toji_dead") == 0 {
            // SPOTTED. The soft outcome, and the one this pass ships: the Claws
            // simply never stand down, so the player fights their way out and
            // the message is not delivered cleanly. design.md offers a hard
            // fail as the alternative and this is deliberately not it: an
            // untestable fail state that fires wrongly ends the gig with no
            // recourse, and the soft one degrades instead.
            //
            // NOT WATCHED UNTIL THE OBJECTIVE EXISTS. `hit_armed` is set when
            // the approach conversation ends, which is when the journal starts
            // asking for a quiet kill. Watching earlier would fail the player
            // for something that happened while they were driving in, before
            // anything had told them stealth was the ask.
            // NO MARKER OF OURS ON HIM ANY MORE (playtest 2026-09-06: "two
            // markers to mark Toji's location, feels weird"). The journal's
            // own pin on the objective already sits on his post, so the
            // script one doubled it. The fields stay so the hide paths below
            // are still sound on a save where it was once shown.

            // CLOSE ENOUGH TO WHISPER. The quest phase waits on this before the
            // face-to-face, and only plays it while he is alive.
            if qs.GetFactStr("cc_g02_toji_met") == 0
                && IsDefined(toji)
                && Vector4.Distance(pos, toji.GetWorldPosition()) < 6.0 {
                qs.SetFactStr("cc_g02_toji_met", 1);
            }

            // ...AND THE ANTI-STALL, which is the other half of the same wait.
            // A player who shoots him from a roof never gets close enough, and
            // the phase would sit forever on a conversation that can no longer
            // happen.
            //
        }

        // THE STAND-DOWN IS GONE, 2026-08-27, and this is where it was.
        //
        // Every surviving Claw used to stop being hostile the instant Toji
        // dropped, on the reading that they had watched a sanctioned killing
        // and knew better than to argue with it. Playtest killed it with two
        // sentences: they do not know V, they do not know he works for Wakako,
        // and the reaction to bullets is bullets.
        //
        // So nobody stands down. Unseen, they never know anything happened;
        // seen, it is a firefight and stays one. What replaced the beat is the
        // walk out below, and the order Wakako gives in her office changed to
        // match: end him quietly and let nobody ever hear of it. design.md
        // carries the whole reasoning.

        // THE WAY OUT, AND IT IS HALF THE STEALTH BEAT.
        //
        // Getting in unseen was the whole objective and getting out again was
        // not asked for at all, which meant the quiet run ended the moment the
        // shot landed. Now leaving is its own objective with its own pin, back
        // at the top of the stairs where V came in.
        //
        // ONE FACT COVERS BOTH OUTCOMES: `exfil_done` goes up when V is clear
        // of the site, seen or not, and the quest phase reads `spotted` to
        // decide which closing call plays. Being seen used to count as done
        // on its own, so Wakako rang while V was still in the den with the
        // Claws shooting (playtest 2026-09-05). Now the call waits for V to
        // leave either way; being seen only changes the objective's words,
        // which the phase does on its own branch.
        if qs.GetFactStr("cc_g02_exfil_armed") > 0 && !this.m_exfilDone {
            // OUT OF THE AREA, ANY WAY OUT (playtest 2026-09-06: "there are
            // many escapes", and a distance from the bottom step only measured
            // one of them). The area is the widened hull of the corners walked
            // in play, CCGig02Area.X, the same shape the way-out pin's
            // trigger area node carries; 2 m past its edge counts as out, so
            // the drawn line and the leg's end agree.
            if this.OutsideHitArea(pos, 2.0) {
                this.m_exfilDone = true;
                qs.SetFactStr("cc_g02_exfil_done", 1);
            }
        }
    }

    // THE HIT ON HIS BODY, as the game reports it. The wrap at the bottom of
    // this file calls this for every hit on a Character.cc_g02_merc.
    public static func MercWasHit(game: GameInstance) -> Void {
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        if qs.GetFactStr("cc_g02_merc_kill_armed") > 0
            && qs.GetFactStr("cc_g02_merc_hit") == 0 {
            qs.SetFactStr("cc_g02_merc_hit", 1);
        }
    }

    private func HostileToV(game: GameInstance, player: ref<PlayerPuppet>,
                            toji: ref<ScriptedPuppet>) -> Void {
        let mine: ref<AttitudeAgent> = player.GetAttitudeAgent();
        if !IsDefined(mine) {
            return;
        }
        if IsDefined(toji) && ScriptedPuppet.IsAlive(toji) && IsDefined(toji.GetAttitudeAgent()) {
            toji.GetAttitudeAgent().SetAttitudeTowards(mine, EAIAttitude.AIA_Hostile);
        }
        let i: Int32 = 0;
        while i < ArraySize(this.m_claws) {
            let npc: ref<ScriptedPuppet> =
                GameInstance.FindEntityByID(game, this.m_claws[i]) as ScriptedPuppet;
            if IsDefined(npc) && ScriptedPuppet.IsAlive(npc) && IsDefined(npc.GetAttitudeAgent()) {
                npc.GetAttitudeAgent().SetAttitudeTowards(mine, EAIAttitude.AIA_Hostile);
            }
            i += 1;
        }
    }

    private func SpawnHit(game: GameInstance) -> Void {
        // TOJI FIRST, ON HIS OWN, so his id is known and never confused with a
        // Claw's. He is the only person who has to die and the only one the
        // gig ever asks about.
        // TOJI IS THE COMMUNITY'S BODY, standing at the bottom of the stairs.
        // Not spawned here: he has a line, so he is a scene actor, and a scene
        // actor that also has to be killed comes from the community. The Claws
        // around him have no lines and stay a script spawn.
        this.m_tojiId = this.FindInCommunity(CCGig02Combat.TojiEntry());
        if !EntityID.IsDefined(this.m_tojiId) {
            // Nowhere the navmesh will take him this tick. Try again on the
            // next one rather than marking the site spawned with no target in
            // it, which would be a hit with nobody to kill.
            return;
        }
        GameInstance.GetQuestsSystem(game).SetFactStr("cc_g02_toji_placed", 1);

        // ...AND HIS COMPANY, ONE TO A WALKED POST DOWN THE STAIRS.
        //
        // THIS WAS A SCATTER AND THE SCATTER WAS THE PROBLEM. Six bodies asked
        // of the navigation system around one point come out huddled, because a
        // navmesh query answers "somewhere near here" and keeps giving nearly
        // the same answer. Gig 01 shipped exactly that and replaced it with
        // thirty walked posts for exactly this reason.
        //
        // Now that the staircase has been walked there are five real posts, one
        // per landing, each facing back up at whoever is coming down. That is
        // what makes the descent an encounter rather than a crowd: they are
        // spread over 70 m and 18 m of height, so they have to be dealt with
        // one at a time, which is what the drop onto the trash exists to avoid.
        let clawRecords: array<TweakDBID>;
        ArrayPush(clawRecords, t"Character.tyger_claws_gangster2_ranged2_shingen_ma");
        ArrayPush(clawRecords, t"Character.tyger_claws_gangster1_ranged1_nue_ma");
        ArrayPush(clawRecords, t"Character.tyger_claws_gangster2_ranged2_copperhead_wa");
        let i: Int32 = 0;
        while i < CCGig02Places.ClawPosts() {
            let id: EntityID = this.SpawnPost(
                game, clawRecords[i % ArraySize(clawRecords)],
                CCGig02Places.ClawPost(i), CCGig02Places.ClawYaw(i),
                CCGig02Combat.ClawTag());
            if EntityID.IsDefined(id) {
                ArrayPush(this.m_claws, id);
            }
            i += 1;
        }

        // NOBODY IS MADE HOSTILE HERE, and that is the whole stealth premise.
        // They keep their records' own affiliation, which means they behave
        // like the Tyger Claws they are: they react to V if they see him and
        // ignore him if they do not. Forcing them hostile on spawn would delete
        // the objective before the player reached the street.
        this.m_hitSpawned = true;
    }

    // Has any of OUR OWN Claws gone into combat?
    //
    // ASKING THE NPCs RATHER THAN THE PLAYER is what keeps the objective
    // honest: V's own combat state would fail this stealth beat for an NCPD
    // firefight two streets away, and the question is whether the men around
    // Toji have seen him.
    //
    // COMBAT, NOT ALERTED, and the enum offers both. A Claw who heard something
    // and went to look has not spotted anybody; a Claw who is fighting has.
    // Alerted would be the harsher reading and would fire on a thrown object or
    // a dead body found late, neither of which is being seen.
    //
    // `GetHighLevelStateFromBlackboard` is the method that resolves, which was
    // established with the compiler as an oracle: `IsInCombat` is not on
    // ScriptedPuppet at all, and NPCPuppet's is a static that takes the puppet.
    // See docs/scene-playbook.md, "Validating offline".
    private func ReleaseClaws(game: GameInstance, player: ref<PlayerPuppet>,
                              remove: Bool) -> Void {
        let mine: ref<AttitudeAgent> = player.GetAttitudeAgent();
        let des: ref<DynamicEntitySystem> = GameInstance.GetDynamicEntitySystem();
        let i: Int32 = 0;
        while i < ArraySize(this.m_claws) {
            let npc: ref<ScriptedPuppet> =
                GameInstance.FindEntityByID(game, this.m_claws[i]) as ScriptedPuppet;
            if IsDefined(npc) {
                if !remove && IsDefined(mine) && IsDefined(npc.GetAttitudeAgent()) {
                    npc.GetAttitudeAgent().SetAttitudeTowards(mine, EAIAttitude.AIA_Neutral);
                }
                if remove && IsDefined(des) {
                    des.DeleteEntity(this.m_claws[i]);
                }
            }
            i += 1;
        }
        if remove {
            ArrayClear(this.m_claws);
        }
    }

    // Point in polygon by ray casting on X and Y, then the distance to the
    // nearest edge. Both on the captured corners; Z is ignored, the stairs
    // drop 28 m over their length and the area is the same area at any height.
    private func OutsideHitArea(pos: Vector4, margin: Float) -> Bool {
        let xs: array<Float> = CCGig02Area.X();
        let ys: array<Float> = CCGig02Area.Y();
        let n: Int32 = ArraySize(xs);
        let inside: Bool = false;
        let nearest: Float = 1000000.0;
        let i: Int32 = 0;
        while i < n {
            let j: Int32 = (i + 1) % n;
            let x1: Float = xs[i];
            let y1: Float = ys[i];
            let x2: Float = xs[j];
            let y2: Float = ys[j];
            // No Bool `!=` in redscript: spelled out as an exclusive or.
            let above1: Bool = y1 > pos.Y;
            let above2: Bool = y2 > pos.Y;
            if (above1 && !above2) || (!above1 && above2) {
                let xi: Float = x1 + (pos.Y - y1) * (x2 - x1) / (y2 - y1);
                if xi > pos.X {
                    inside = !inside;
                }
            }
            let dx: Float = x2 - x1;
            let dy: Float = y2 - y1;
            let len2: Float = dx * dx + dy * dy;
            let t: Float = 0.0;
            if len2 > 0.0 {
                t = ((pos.X - x1) * dx + (pos.Y - y1) * dy) / len2;
                if t < 0.0 {
                    t = 0.0;
                }
                if t > 1.0 {
                    t = 1.0;
                }
            }
            let ex: Float = pos.X - (x1 + t * dx);
            let ey: Float = pos.Y - (y1 + t * dy);
            let d: Float = SqrtF(ex * ex + ey * ey);
            if d < nearest {
                nearest = d;
            }
            i += 1;
        }
        return !inside && nearest > margin;
    }

    private func AnyClawFighting(game: GameInstance) -> Bool {
        let i: Int32 = 0;
        while i < ArraySize(this.m_claws) {
            let npc: ref<ScriptedPuppet> =
                GameInstance.FindEntityByID(game, this.m_claws[i]) as ScriptedPuppet;
            if IsDefined(npc) && ScriptedPuppet.IsAlive(npc)
                && Equals(npc.GetHighLevelStateFromBlackboard(),
                          gamedataNPCHighLevelState.Combat) {
                return true;
            }
            i += 1;
        }
        return false;
    }

    // ======================================================== the payout
    //
    // GUARDED ON A FACT, NEVER ON A SCRIPT FIELD. A field resets on load, so a
    // reward gated by one is granted again every time the player reloads the
    // save, which is a money printer. The fact is the only thing that survives.
    private func Payout(qs: ref<QuestsSystem>) -> Void {
        if qs.GetFactStr("cc_g02_paid") > 0 {
            return;
        }
        let game: GameInstance = this.GetGameInstance();
        let ps: ref<PlayerSystem> = GameInstance.GetPlayerSystem(game);
        if !IsDefined(ps) {
            return;
        }
        let player: ref<PlayerPuppet> = ps.GetLocalPlayerMainGameObject() as PlayerPuppet;
        if !IsDefined(player) {
            return;
        }
        qs.SetFactStr("cc_g02_paid", 1);
        // THE GAME'S OWN REWARD, THE GAME'S OWN WAY (design call 2026-09-06).
        // The fee used to be a flat 3,000 eddies and 300 Street Cred through
        // the shared pay call, doubled if the merc died.
        // Four completion records of the kind Wakako's gigs carry, in
        // tweaks/rewards.yaml: 9,300 / 7,000 / 4,700 / 3,500 eddies by outcome,
        // 1,000 level XP and 1,136 Street Cred XP on all four, the XP scaled
        // to the player's level by the game because the record name begins
        // with `sts_`. RPGManager.GiveReward is what the quest reward node
        // calls, so the money notice and the telemetry are vanilla's.
        let quiet: Bool = qs.GetFactStr("cc_g02_spotted") == 0;
        let killed: Bool = qs.GetFactStr("cc_g02_merc_fate") == 1;
        let reward: TweakDBID = t"QuestRewards.sts_cc_g02_completion_loud_spare";
        if quiet && killed {
            reward = t"QuestRewards.sts_cc_g02_completion_quiet_kill";
        } else {
            if quiet {
                reward = t"QuestRewards.sts_cc_g02_completion_quiet_spare";
            } else {
                if killed {
                    reward = t"QuestRewards.sts_cc_g02_completion_loud_kill";
                }
            }
        }
        RPGManager.GiveReward(game, reward, Cast<StatsObjectID>(player.GetEntityID()));
    }
}

public class CCGig02Tick extends DelayCallback {
    public let system: wref<DeadRingerEncounter>;
    public func Call() -> Void {
        if IsDefined(this.system) {
            this.system.Tick();
        }
    }
}

// TWO FUNCTIONS THE GIG CALLS, moved out of Gig02_Lab.reds on 2026-09-06 so
// that the lab is dev tooling and nothing else and the release can drop it.
// The names stay `CCLab_*` because the CET dev menu calls both of these too.
//
// THE AI'S OWN WAY INTO A POSE: the command every behaviour tree issues when
// an NPC takes a spot. `move` walks the body to the spot first; `jump` skips
// the entry animation and starts on the idle. Char takes her chair with it.
public func CCLab_UseWorkspot(npc: ref<GameObject>, spotRef: String, move: Bool, jump: Bool, idleOnly: Bool) -> Bool {
    let puppet: ref<ScriptedPuppet> = npc as ScriptedPuppet;
    if !IsDefined(puppet) {
        return false;
    }
    let cmd: ref<AIUseWorkspotCommand> = new AIUseWorkspotCommand();
    cmd.workspotNode = CreateNodeRef(spotRef);
    cmd.moveToWorkspot = move;
    cmd.jumpToEntry = jump;
    cmd.idleOnlyMode = idleOnly;
    cmd.continueInCombat = false;
    let ai: ref<AIHumanComponent> = puppet.GetAIControllerComponent();
    if !IsDefined(ai) {
        return false;
    }
    ai.SendCommand(cmd);
    return true;
}

// EVERYTHING BUT OURS. A downed body's loot list is whatever his record
// dropped at the fall (weapons one time, a skill shard the next) plus what we
// put there; this leaves only the item named (2026-09-05). The merc's shard is
// the only thing that should be on him when the player searches the body.
public func CCLab_StripAll(npc: ref<GameObject>, keep: String) -> Int32 {
    let ts: ref<TransactionSystem> = GameInstance.GetTransactionSystem(npc.GetGame());
    let keepId: TweakDBID = TDBID.Create(keep);
    let items: array<wref<gameItemData>>;
    ts.GetItemList(npc, items);
    let removed: Int32 = 0;
    let i: Int32 = 0;
    while i < ArraySize(items) {
        let id: ItemID = items[i].GetID();
        if ItemID.GetTDBID(id) != keepId {
            ts.RemoveItem(npc, id, items[i].GetQuantity());
            removed += 1;
        }
        i += 1;
    }
    return removed;
}

// THE DEVICE'S MINIGAME, SET FROM OUTSIDE. `m_minigameDefinition` is a
// protected persistent field of the controller state; an added method compiles
// into the class and can write it (the computer playbook's rule for reaching
// a device's private members). Persistent, so it survives a save.
@addMethod(AccessPointControllerPS)
public func CCGig02SetMinigame(id: TweakDBID) -> Void {
    if this.m_minigameDefinition != id {
        this.m_minigameDefinition = id;
    }
}

// THE SECOND SIGNAL FOR THE BREACH: the frame the code grid closes with a
// win on OUR box. `FinalizeNetrunnerDive` is public and not final on
// AccessPointControllerPS (accessPointController.swift), and the owner is the
// device entity, so the box is told apart from every other access point in
// the city by where it stands (the computer playbook's own rule).
@wrapMethod(AccessPointControllerPS)
public func FinalizeNetrunnerDive(state: HackingMinigameState) -> Void {
    wrappedMethod(state);
    if Equals(state, HackingMinigameState.Succeeded) {
        let owner: ref<GameObject> = this.GetOwnerEntityWeak() as GameObject;
        if IsDefined(owner)
            && Vector4.Distance(owner.GetWorldPosition(), CCGig02Places.AccessPoint()) < 3.0 {
            let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGameInstance());
            if IsDefined(qs) && qs.GetFactStr("cc_g02_ap_breached") == 0 {
                qs.SetFactStr("cc_g02_ap_breached", 1);
            }
        }
    }
}

// A HIT ON THE MERC, seen from his own body (2026-09-05). The encounter's
// tick reads health between ticks, which is the same thing a step later;
// this is the game's own hit event, and it fires under the Immortal shield
// too, since Immortal lets damage land. Filtered by record so it costs
// nothing on any other body. Marker: CCGig02MercHitWrap.
@wrapMethod(NPCPuppet)
protected cb func OnHit(evt: ref<gameHitEvent>) -> Bool {
    let r: Bool = wrappedMethod(evt);
    if Equals(this.GetRecordID(), CCGig02Combat.MercRecord()) {
        DeadRingerEncounter.MercWasHit(this.GetGame());
    }
    return r;
}
