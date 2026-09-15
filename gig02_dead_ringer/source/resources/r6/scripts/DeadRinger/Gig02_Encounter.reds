module CyberpunkCodes.Gig02

import CyberpunkCodes.Shared.Gig02.*

public abstract class CCGig02Combat {
    public static func MercRecord() -> TweakDBID { return t"Character.cc_g02_merc"; }
    public static func MercTag() -> CName { return n"cc_g02_merc"; }
    public static func MercShield() -> CName { return n"cc_g02_merc"; }

    public static func TojiRecord() -> TweakDBID { return t"Character.cc_g02_toji"; }
    public static func TojiTag() -> CName { return n"cc_g02_toji"; }

    public static func ClawTag() -> CName { return n"cc_g02_claw"; }

    public static func CommunityRef() -> String {
        return "$/mod/cc_g02_cast/#cc_g02_cast_com";
    }

    public static func MercEntry() -> CName { return n"merc"; }
    public static func TojiEntry() -> CName { return n"toji"; }

    public static func CharRecord() -> TweakDBID { return t"Character.cc_g02_char"; }
    public static func CharTag() -> CName { return n"cc_g02_char"; }

    // max
    public static func ClawCount() -> Int32 { return 6; }

    // % health
    public static func MercDownAt() -> Float { return 33.0; }

}

@addMethod(Entity)
public native func Dispose() -> Void;

public class DeadRingerEncounter extends ScriptableSystem {

    private let m_mercId: EntityID;
    private let m_mercSpawned: Bool;
    // 0 none, 1 invulnerable, 2 immortal
    private let m_mercMode: Int32;
    private let m_mercTicks: Int32;
    private let m_fleeTicks: Int32;
    private let m_charSent: Bool;
    private let m_mercNoDismember: Bool;
    private let m_mercKillHp: Float;
    private let m_mercKilled: Bool;
    private let m_mercKillStage: Int32;
    private let m_mercKillTicks: Int32;
    private let m_mercFleeing: Bool;
    private let m_floorTicks: Int32;
    private let m_mercBlind: Bool = true;

    private let m_hitSpawned: Bool;
    private let m_tojiId: EntityID;
    private let m_claws: array<EntityID>;
    private let m_mercPin: NewMappinID;
    private let m_mercPinOn: Bool;
    private let m_wakakoHeld: Bool;
    private let m_apPin: NewMappinID;
    private let m_apPinOn: Bool;
    private let m_exfilDone: Bool;
    private let m_afterlifeTicks: Int32;
    private let m_clearTicks: Int32;
    // railing
    private let m_wait1Stamp: Float;
    // chair
    private let m_wait2Stamp: Float;
    private let m_leanShifted: Bool;
    private let m_sitShifted: Bool;
    private let m_shardTries: Int32;

    private func OnAttach() -> Void {
        this.ScheduleTick(6.0);
    }

    public func ScheduleTick(delay: Float) -> Void {
        let cb: ref<CCGig02Tick> = new CCGig02Tick();
        cb.system = this;
        GameInstance.GetDelaySystem(this.GetGameInstance()).DelayCallback(cb, delay, false);
    }

    private func Near(pos: Vector4, spot: Vector4, radius: Float) -> Bool {
        return CCSharedWorld.Near(pos, spot, radius, 6.0, 25.0);
    }

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

    private func FindInCommunity(entry: CName, aliveOnly: Bool) -> EntityID {
        let none: EntityID;
        let dead: EntityID;
        let game: GameInstance = this.GetGameInstance();
        let nref: NodeRef = CreateNodeRef(CCGig02Combat.CommunityRef());
        let root: GlobalNodeRef;
        let g: GlobalNodeRef = ResolveNodeRef(nref, root);
        if !GlobalNodeRef.IsDefined(g) {
            return none;
        }
        let objects: array<ref<GameObject>>;
        GetGameObjectsFromSpawnerEntityID(Cast<EntityID>(g), [entry], game,
                                          objects);
        let i: Int32 = 0;
        while i < ArraySize(objects) {
            let puppet: ref<ScriptedPuppet> = objects[i] as ScriptedPuppet;
            if IsDefined(puppet) {
                if ScriptedPuppet.IsAlive(puppet) {
                    return puppet.GetEntityID();
                }
                if !aliveOnly && !EntityID.IsDefined(dead) {
                    dead = puppet.GetEntityID();
                }
            }
            i += 1;
        }
        if EntityID.IsDefined(dead) {
            return dead;
        }
        return none;
    }

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

    private func ShowOrMove(game: GameInstance, on: Bool, id: NewMappinID,
                            pos: Vector4) -> NewMappinID {
        let spot: Vector4 = new Vector4(pos.X, pos.Y, pos.Z + 1.8, 1.0);
        if on {
            CCSharedMappins.Move(game, id, spot);
            return id;
        }
        return CCSharedMappins.Show(game, spot);
    }

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

        if !IsDefined(ps) || !IsDefined(qs) {
            this.ScheduleTick(2.0);
            return;
        }

        if qs.GetFactStr("cc_g02_closed") > 0 {
            this.Payout(qs);
        }
        if qs.GetFactStr("cc_g02_done") > 0 {
            this.HidePins(game);
            this.Payout(qs);
            let p: ref<PlayerPuppet> = ps.GetLocalPlayerMainGameObject() as PlayerPuppet;
            if IsDefined(p) && ArraySize(this.m_claws) > 0 {
                this.ReleaseClaws(game, p, true);
            }
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
        this.BriefRead(game, qs);
        if qs.GetFactStr("cc_g02_accepted") == 0 {
            this.ScheduleTick(1.0);
            return;
        }
        let pos: Vector4 = player.GetWorldPosition();

        this.Arrivals(qs, pos);
        this.AfterlifeClear(game, qs, pos);
        this.HoldWakako(qs, pos);
        this.Groups(game, qs, pos);
        this.Merc(game, qs, player, pos);
        this.Bystanders(game, qs, player);
        this.QueueShield(game, qs, player);
        this.InnKeeper(game, qs, player);
        this.ParlorKeeper(game, qs, player);
        this.Waits(game, qs, player, pos);
        this.Readers(game, qs);
        this.AccessPoint(game, qs, player, pos);
        this.Hit(game, qs, player, pos);

        this.ScheduleTick(1.0);
    }

    private func Waits(game: GameInstance, qs: ref<QuestsSystem>,
                       player: ref<PlayerPuppet>, pos: Vector4) -> Void {
        let ts: ref<TimeSystem> = GameInstance.GetTimeSystem(game);
        if !IsDefined(ts) {
            return;
        }

        if qs.GetFactStr("cc_g02_char_near") > 0
                && qs.GetFactStr("cc_g02_trace_done") == 0 {
            if this.m_wait1Stamp == 0.0 {
                this.m_wait1Stamp = ts.GetGameTimeStamp();
            }
            if qs.GetFactStr("cc_g02_lean_shift") > 0 && !this.m_leanShifted {
                this.m_leanShifted = true;
                // 30 game min
                this.SkipAhead(ts, this.m_wait1Stamp, 1800.0);
            }
        } else {
            this.LetGo(qs, "cc_g02_lean_taken", "cc_g02_lean_release");
        }

        if qs.GetFactStr("cc_g02_ap_breached") > 0
                && qs.GetFactStr("cc_g02_char_named") == 0 {
            if this.m_wait2Stamp == 0.0 {
                this.m_wait2Stamp = ts.GetGameTimeStamp();
            }
            if qs.GetFactStr("cc_g02_sit_shift") > 0 && !this.m_sitShifted {
                this.m_sitShifted = true;
                // 20 game min
                this.SkipAhead(ts, this.m_wait2Stamp, 1200.0);
            }
        } else {
            this.LetGo(qs, "cc_g02_sit_taken", "cc_g02_sit_release");
        }

        this.StandUp(game, qs, player, pos);
    }

    private func LetGo(qs: ref<QuestsSystem>, taken: String, release: String) -> Void {
        if qs.GetFactStr(taken) > 0 && qs.GetFactStr(release) == 0 {
            qs.SetFactStr(release, 1);
        }
    }

    private func StandUp(game: GameInstance, qs: ref<QuestsSystem>,
                         player: ref<PlayerPuppet>, pos: Vector4) -> Void {
        let atLean: Bool = qs.GetFactStr("cc_g02_lean_release") > 0
            && this.Near(pos, CCGig02Places.LeanPose(), 4.0);
        let atSit: Bool = qs.GetFactStr("cc_g02_sit_release") > 0
            && this.Near(pos, CCGig02Places.SitPose(), 4.0);
        if !atLean && !atSit {
            return;
        }
        let ws: ref<WorkspotGameSystem> = GameInstance.GetWorkspotSystem(game);
        if !IsDefined(ws) || !ws.IsActorInWorkspot(player) {
            return;
        }
        ws.SendFastExitSignal(player, new Vector3(0.0, 0.0, 0.0), false, false,
                              false, true);
    }

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
        let total: Int32 = GameTime.Hours(now) * 3600 + GameTime.Minutes(now) * 60
            + GameTime.Seconds(now) + Cast<Int32>(left);
        let day: Int32 = total % 86400;
        ts.SetGameTimeByHMS(day / 3600, (day % 3600) / 60, day % 60,
                            n"cc_g02_waiting_spot");
    }

    private func AfterlifeClear(game: GameInstance, qs: ref<QuestsSystem>,
                                pos: Vector4) -> Void {
        if qs.GetFactStr("cc_g02_wakako_2") == 0
            || qs.GetFactStr("cc_g02_afterlife_clear") > 0 {
            return;
        }
        if CCGig02StartRules.IsFastTravelling(game) {
            return;
        }
        this.m_afterlifeTicks += 1;
        if Vector4.Distance(pos, CCGig02Places.Afterlife()) > 100.0
            // 10 min cap
            || this.m_afterlifeTicks > 600 {
            qs.SetFactStr("cc_g02_afterlife_clear", 1);
        }
    }

    private func Arrivals(qs: ref<QuestsSystem>, pos: Vector4) -> Void {
        if qs.GetFactStr("cc_g02_called") > 0
            && qs.GetFactStr("cc_g02_afterlife_reached") == 0
            && this.Near(pos, CCGig02Places.Afterlife(), 40.0) {
            qs.SetFactStr("cc_g02_afterlife_reached", 1);
            return;
        }

        if qs.GetFactStr("cc_g02_wakako_2") > 0
            && qs.GetFactStr("cc_g02_inn_reached") == 0
            && this.Near(pos, new Vector4(-1177.83, 2039.69, 20.15, 1.0), 3.0) {
            qs.SetFactStr("cc_g02_inn_reached", 1);
        }

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

        if qs.GetFactStr("cc_g02_wakako_met") > 0
            && qs.GetFactStr("cc_g02_hit_reached") == 0
            && (this.Near(pos, CCGig02Places.HitSite(), 30.0)
                // from below
                || this.Near(pos, CCGig02Places.TojiPost(), 30.0)) {
            qs.SetFactStr("cc_g02_hit_reached", 1);
        }

        if qs.GetFactStr("cc_g02_hit_reached") > 0
            && qs.GetFactStr("cc_g02_dropped") == 0
            && (this.Near(pos, CCGig02Places.Trash(), 6.0)
                || this.Near(pos, CCGig02Places.TojiPost(), 25.0)) {
            qs.SetFactStr("cc_g02_dropped", 1);
        }
    }

    private func HoldWakako(qs: ref<QuestsSystem>, pos: Vector4) -> Void {
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

    private func Groups(game: GameInstance, qs: ref<QuestsSystem>,
                        pos: Vector4) -> Void {
        if qs.GetFactStr("cc_g02_afterlife_reached") == 0
            || qs.GetFactStr("cc_g02_lead_heard") > 0 {
            return;
        }

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

        if qs.GetFactStr("cc_g02_groups_done") > 0 {
            if qs.GetFactStr("cc_g02_group3_near") == 0
                && this.Near(pos, CCGig02Places.Group3(), radius) {
                qs.SetFactStr("cc_g02_group3_near", 1);
            }
            return;
        }

        let first: Int32 = qs.GetFactStr("cc_g02_group_first");
        if first == 0 {
            let d1: Float = Vector4.Distance(pos, CCGig02Places.Group1());
            let d2: Float = Vector4.Distance(pos, CCGig02Places.Group2());
            // nearer group wins
            if this.Near(pos, CCGig02Places.Group1(), radius) && d1 <= d2 {
                qs.SetFactStr("cc_g02_group_first", 1);
            } else {
                if this.Near(pos, CCGig02Places.Group2(), radius) {
                    qs.SetFactStr("cc_g02_group_first", 2);
                }
            }
            return;
        }

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
        if this.Near(pos, other, radius)
            && Vector4.Distance(pos, other) < Vector4.Distance(pos, done) {
            qs.SetFactStr("cc_g02_group_second", 1);
        }
    }

    private let m_briefTicks: Int32;

    private func BriefRead(game: GameInstance, qs: ref<QuestsSystem>) -> Void {
        if qs.GetFactStr("cc_g02_brief_read") > 0 || qs.GetFactStr("cc_g02_call1_done") == 0 {
            return;
        }
        this.m_briefTicks += 1;
        // 45s
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
            // crowd only
            if IsDefined(npc) && !npc.IsPlayer() && npc.IsCrowd()
                && Vector4.Distance(npc.GetWorldPosition(), door) < 22.0
                && !this.IsOurs(npc.GetRecordID())
                && !ArrayContains(this.m_calmed, npc.GetEntityID()) {
                ArrayPush(this.m_calmed, npc.GetEntityID());
                npc.Dispose();
            }
            i += 1;
        }
    }

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
                let atChair: Bool = npc.IsCrowd()
                    && Vector4.Distance(npc.GetWorldPosition(), chair) < 1.5;
                // the game's yoko
                let vendor: Bool = rec == t"Character.wat_kab_netrunner_01"
                    && Vector4.Distance(npc.GetWorldPosition(), inn) < 15.0;
                if atChair || vendor {
                    ArrayPush(this.m_calmed, npc.GetEntityID());
                    npc.Dispose();
                }
            }
            i += 1;
        }
        // char back in her chair
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
            this.ReleaseMerc(game);
            return;
        }
        if qs.GetFactStr("cc_g02_afterlife_reached") == 0 {
            return;
        }

        if !this.m_mercSpawned {
            this.m_mercId = this.FindInCommunity(CCGig02Combat.MercEntry(), true);
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
        let hp: Float = GameInstance.GetStatPoolsSystem(game)
            .GetStatPoolValue(Cast<StatsObjectID>(this.m_mercId),
                              gamedataStatPoolType.Health, false);

        if qs.GetFactStr("cc_g02_lead_heard") > 0 && !armed && !down {
            this.m_mercTicks += 1;
            // 60s
            if this.m_mercTicks > 60 {
                qs.SetFactStr("cc_g02_merc_armed", 1);
                armed = true;
            }
        }

        if !down && armed && hp > 0.0 && hp <= CCGig02Combat.MercDownAt() {
            qs.SetFactStr("cc_g02_merc_down", 1);
            down = true;
            NPCPuppet.ChangeHighLevelState(merc, gamedataNPCHighLevelState.Relaxed);
        }

        if down {
            this.m_floorTicks += 1;
            if this.m_floorTicks == 1 {
                StatusEffectHelper.ApplyStatusEffect(merc, t"BaseStatusEffect.Defeated");
            }
            // 2s after the fall
            if this.m_floorTicks == 3 {
                StatusEffectHelper.ApplyStatusEffect(merc, t"BaseStatusEffect.BleedingInfinite");
            }
            CCLab_StripAll(merc, "Items.cc_g02_shard");
            let ts: ref<TransactionSystem> = GameInstance.GetTransactionSystem(game);
            let shard: ItemID = ItemID.FromTDBID(CCGig02Shard.ShardItem());
            if this.m_floorTicks >= 3 && qs.GetFactStr("cc_g02_shard_planted") == 0
                && !ts.HasItem(merc, shard) && !ts.HasItem(player, shard) {
                if ts.GiveItem(merc, shard, 1) {
                    qs.SetFactStr("cc_g02_shard_planted", 1);
                }
            }
            if qs.GetFactStr("cc_g02_shard_taken") == 0
                && (ts.HasItem(player, shard) || qs.GetFactStr("cc_g02_proof_read") > 0) {
                qs.SetFactStr("cc_g02_shard_taken", 1);
            }
        }

        if qs.GetFactStr("cc_g02_merc_flee") > 0 {
            this.FleeMerc(game, merc, pos);
            return;
        }

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

        let killArmed: Bool = qs.GetFactStr("cc_g02_merc_kill_armed") > 0;
        if killArmed && qs.GetFactStr("cc_g02_merc_dead") == 0
            && !ScriptedPuppet.IsAlive(merc) {
            qs.SetFactStr("cc_g02_merc_dead", 1);
        }
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

        if IsDefined(agent) && IsDefined(playerAgent) {
            if armed && !down {
                let untouched: Bool = hp >= 99.0 || hp <= 0.0;
                if untouched {
                    agent.SetAttitudeGroup(n"neutral");
                    agent.SetAttitudeTowards(playerAgent, EAIAttitude.AIA_Neutral);
                }
                if !untouched && this.m_mercBlind {
                    let senses: ref<SenseComponent> = merc.GetSensesComponent();
                    if IsDefined(senses) {
                        // eyes on
                        senses.Toggle(true);
                    }
                    this.m_mercBlind = false;
                }
            } else {
                if killArmed {
                    agent.SetAttitudeGroup(n"neutral");
                    agent.SetAttitudeTowards(playerAgent, EAIAttitude.AIA_Neutral);
                } else {
                    agent.SetAttitudeGroup(n"friendly");
                    agent.SetAttitudeTowards(playerAgent, EAIAttitude.AIA_Friendly);
                }
            }
        }

        if IsDefined(gods) {
            let want: Int32 = 1;
            if this.m_mercKilled {
                want = 0;
            } else {
                if killArmed || (armed && !down) {
                    want = 2;
                }
            }
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

    private func FleeMerc(game: GameInstance, merc: ref<ScriptedPuppet>,
                          playerPos: Vector4) -> Void {
        this.m_mercFleeing = true;
        this.m_fleeTicks += 1;
        if Vector4.Distance(playerPos, merc.GetWorldPosition()) > 40.0
            // 45s
            || this.m_fleeTicks > 45 {
            this.ReleaseMerc(game);
        }
    }

    private func ReleaseMerc(game: GameInstance) -> Void {
        if !this.m_mercSpawned {
            return;
        }
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
        this.m_mercSpawned = false;
        this.m_mercMode = 0;
        this.m_mercNoDismember = false;
        this.m_mercFleeing = false;
        this.m_floorTicks = 0;
        this.m_mercBlind = true;
        this.m_fleeTicks = 0;
    }

    private func Readers(game: GameInstance, qs: ref<QuestsSystem>) -> Void {
        if qs.GetFactStr("cc_g02_merc_down") > 0
            && qs.GetFactStr("cc_g02_proof_read") == 0
            && CCGig02Shard.HasBeenRead(game, CCGig02Shard.ShardPath()) {
            qs.SetFactStr("cc_g02_proof_read", 1);
        }

    }

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
                    ps.CCGig02SetMinigame(t"minigame_v2.cc_g02_parlor");
                    if ps.CCGig02EaseBreach() {
                        let boxDevice: ref<AccessPoint> = dev as AccessPoint;
                        if IsDefined(boxDevice) {
                            boxDevice.CCGig02RefreshPrompt();
                        }
                    }
                    if ps.IsBreached() {
                        qs.SetFactStr("cc_g02_ap_breached", 1);
                        return;
                    }
                }
            }
            i += 1;
        }
    }

    private func Hit(game: GameInstance, qs: ref<QuestsSystem>,
                     player: ref<PlayerPuppet>, pos: Vector4) -> Void {
        if qs.GetFactStr("cc_g02_hit_reached") == 0 {
            return;
        }

        if !this.m_hitSpawned {
            if qs.GetFactStr("cc_g02_toji_dead") > 0 {
                this.m_hitSpawned = true;
            } else {
                this.SpawnHit(game);
                return;
            }
        }

        let toji: ref<ScriptedPuppet> =
            GameInstance.FindEntityByID(game, this.m_tojiId) as ScriptedPuppet;

        if !IsDefined(toji) && qs.GetFactStr("cc_g02_toji_dead") == 0 {
            this.m_tojiId = this.FindInCommunity(CCGig02Combat.TojiEntry(), false);
            toji = GameInstance.FindEntityByID(game, this.m_tojiId) as ScriptedPuppet;
        }

        if qs.GetFactStr("cc_g02_hit_armed") > 0
            && qs.GetFactStr("cc_g02_spotted") == 0
            && qs.GetFactStr("cc_g02_exfil_done") == 0
            && this.AnyClawFighting(game) {
            qs.SetFactStr("cc_g02_spotted", 1);
            CCSharedHud.NotifyTyped(game,
                GetLocalizedTextByKey(n"cc-g02-hud-spotted"),
                SimpleMessageType.Negative, 5.0);
        }

        if qs.GetFactStr("cc_g02_toji_dead") == 0
            && IsDefined(toji) && !ScriptedPuppet.IsAlive(toji) {
            qs.SetFactStr("cc_g02_toji_dead", 1);
            qs.SetFactStr("cc_g02_toji_met", 1);
        }

        if qs.GetFactStr("cc_g02_exfil_done") > 0 {
            this.SiteClear(qs, pos);
            this.ReleaseClaws(game, player, qs.GetFactStr("cc_g02_site_clear") > 0);
            return;
        }

        this.HostileToV(game, player, toji);

        if qs.GetFactStr("cc_g02_toji_dead") == 0 {

            if qs.GetFactStr("cc_g02_toji_met") == 0
                && IsDefined(toji)
                // whisper range
                && Vector4.Distance(pos, toji.GetWorldPosition()) < 6.0 {
                qs.SetFactStr("cc_g02_toji_met", 1);
            }

        }

        if qs.GetFactStr("cc_g02_exfil_armed") > 0 && !this.m_exfilDone {
            if this.OutsideHitArea(pos, 2.0) {
                this.m_exfilDone = true;
                qs.SetFactStr("cc_g02_exfil_done", 1);
            }
        }
    }

    public static func MercWasHit(game: GameInstance) -> Void {
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        if qs.GetFactStr("cc_g02_merc_kill_armed") > 0
            && qs.GetFactStr("cc_g02_merc_hit") == 0 {
            qs.SetFactStr("cc_g02_merc_hit", 1);
        }
    }

    public static func TojiDied(game: GameInstance) -> Void {
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        if !IsDefined(qs)
            || qs.GetFactStr("cc_g02_wakako_met") == 0
            || qs.GetFactStr("cc_g02_toji_dead") > 0 {
            return;
        }
        qs.SetFactStr("cc_g02_toji_met", 1);
        qs.SetFactStr("cc_g02_toji_dead", 1);
        if qs.GetFactStr("cc_g02_hit_reached") == 0 {
            qs.SetFactStr("cc_g02_hit_reached", 1);
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
        this.m_tojiId = this.FindInCommunity(CCGig02Combat.TojiEntry(), true);
        if !EntityID.IsDefined(this.m_tojiId) {
            let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
            let corpse: EntityID = this.FindInCommunity(CCGig02Combat.TojiEntry(), false);
            if EntityID.IsDefined(corpse) {
                this.m_tojiId = corpse;
                qs.SetFactStr("cc_g02_toji_placed", 1);
                qs.SetFactStr("cc_g02_toji_met", 1);
                qs.SetFactStr("cc_g02_toji_dead", 1);
                this.m_hitSpawned = true;
            }
            return;
        }
        GameInstance.GetQuestsSystem(game).SetFactStr("cc_g02_toji_placed", 1);

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

        this.m_hitSpawned = true;
    }

    private func SiteClear(qs: ref<QuestsSystem>, pos: Vector4) -> Void {
        if qs.GetFactStr("cc_g02_closed") == 0
            || qs.GetFactStr("cc_g02_site_clear") > 0 {
            return;
        }
        this.m_clearTicks += 1;
        // 80m, 5 min cap
        if this.OutsideHitArea(pos, 80.0) || this.m_clearTicks > 300 {
            qs.SetFactStr("cc_g02_site_clear", 1);
        }
    }

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
        let quiet: Bool = qs.GetFactStr("cc_g02_spotted") == 0;
        // 1 = kill, 2 = spare
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

@addMethod(AccessPointControllerPS)
public func CCGig02SetMinigame(id: TweakDBID) -> Void {
    if this.m_minigameDefinition != id {
        this.m_minigameDefinition = id;
    }
}

@addMethod(AccessPointControllerPS)
public func CCGig02EaseBreach() -> Bool {
    let container: ref<BaseSkillCheckContainer> = this.GetSkillCheckContainer();
    if !IsDefined(container) {
        return false;
    }
    let slot: ref<HackingSkillCheck> = container.GetHackingSlot();
    if !IsDefined(slot) {
        return false;
    }
    let check: ref<GameplaySkillCondition> = slot.GetBaseSkill();
    if !IsDefined(check) {
        return false;
    }
    let before: Int32 = check.GetRequiredLevel(this.GetGameInstance());
    // lowest attribute
    check.TrySetRequiredLevel(3);
    return check.GetRequiredLevel(this.GetGameInstance()) != before;
}

@addMethod(AccessPoint)
public func CCGig02RefreshPrompt() -> Void {
    let player: ref<GameObject> = GameInstance.GetPlayerSystem(this.GetGame())
        .GetLocalPlayerMainGameObject();
    if IsDefined(player) {
        this.RefreshInteraction(gamedeviceRequestType.Direct, player);
    }
}

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

@wrapMethod(NPCPuppet)
protected cb func OnHit(evt: ref<gameHitEvent>) -> Bool {
    let r: Bool = wrappedMethod(evt);
    if Equals(this.GetRecordID(), CCGig02Combat.MercRecord()) {
        DeadRingerEncounter.MercWasHit(this.GetGame());
    }
    return r;
}

@wrapMethod(NPCPuppet)
protected cb func OnDeath(evt: ref<gameDeathEvent>) -> Bool {
    let r: Bool = wrappedMethod(evt);
    if Equals(this.GetRecordID(), CCGig02Combat.TojiRecord()) {
        DeadRingerEncounter.TojiDied(this.GetGame());
    }
    return r;
}
