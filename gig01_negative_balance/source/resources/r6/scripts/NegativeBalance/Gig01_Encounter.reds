module CyberpunkCodes.Gig01

import CyberpunkCodes.Shared.Gig01.*

public abstract class CCGig01Places {
    // arroyo
    public static func CompoundEntry() -> Vector4 { return new Vector4(-189.371, -1464.500, 7.596, 1.0); }
    public static func InnerEntry() -> Vector4 { return new Vector4(-219.737, -1424.075, 14.604, 1.0); }
    public static func OfficeEntry() -> Vector4 { return new Vector4(-241.498, -1449.012, 14.600, 1.0); }
    public static func OfficeTerminal() -> Vector4 { return new Vector4(-251.915, -1456.364, 14.600, 1.0); }

    public static func InsideCompound(pos: Vector4) -> Bool {
        if pos.Z < 2.0 || pos.Z > 45.0 {
            return false;
        }
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

    // north oak
    public static func EstateGate() -> Vector4 { return new Vector4(384.181, 1164.724, 220.643, 1.0); }
    public static func WayInPoint(leg: Int32) -> Vector4 {
        switch leg {
            case 1: return new Vector4(369.781, 1178.338, 219.794, 1.0);
            case 2: return new Vector4(327.383, 1167.466, 219.520, 1.0);
            case 3: return new Vector4(306.727, 1154.487, 219.287, 1.0);
            case 4: return new Vector4(290.119, 1122.134, 218.901, 1.0);
            // foot of the climb
            case 5: return new Vector4(276.470, 1089.549, 216.985, 1.0);
            // top of the climb
            default: return new Vector4(288.168, 1082.351, 225.525, 1.0);
        }
    }

    public static func WayInLegs() -> Int32 { return 6; }

    public static func WayInMarker(leg: Int32) -> Vector4 {
        let p: Vector4 = CCGig01Places.WayInPoint(leg);
        return new Vector4(p.X, p.Y, p.Z + 1.7, 1.0);
    }

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

    public static func EstateWayIn() -> Vector4 { return CCGig01Places.WayInPoint(6); }
    public static func Hoshino() -> Vector4 { return new Vector4(300.102, 1054.556, 229.928, 1.0); }
    public static func EstateTerminal() -> Vector4 { return new Vector4(284.852, 1023.697, 224.928, 1.0); }

    // marker, not where she stands
    public static func Coyote() -> Vector4 { return new Vector4(-1259.598, -989.166, 12.037, 1.0); }

    // at the bar
    public static func MamaWelles() -> Vector4 { return new Vector4(-1262.178, -998.805, 12.057, 1.0); }
    public static func MamaWellesYaw() -> Float { return -80.3; }

    public static func BarStools() -> Vector4 { return new Vector4(-1258.193, -999.521, 12.037, 1.0); }

    public static func InsideEstate(pos: Vector4) -> Bool {
        // road tunnel below
        if pos.Z < 213.7 || pos.Z > 280.0 {
            return false;
        }
        if pos.X < 245.1 || pos.X > 399.2 || pos.Y < 977.1 || pos.Y > 1166.9 {
            return false;
        }
        let xs: array<Float> = [
            // traced along the wall
            339.379, 368.302, 391.452, 399.100, 387.793, 392.889, 363.870,
            346.593, 329.999, 307.952, 315.188, 299.594, 245.171, 269.290,
            291.898, 295.547, 296.802, 285.525, 322.571, 340.626];
        let ys: array<Float> = [
            1158.764, 1166.825, 1153.485, 1126.636, 1103.308, 1086.459, 1036.437,
            1038.424, 1007.784, 1020.564, 1009.689, 977.203, 1007.622, 1046.606,
            1082.425, 1080.882, 1083.118, 1092.534, 1155.241, 1160.340];

        let n: Int32 = ArraySize(xs);
        let inside: Bool = false;
        let i: Int32 = 0;
        let j: Int32 = n - 1;
        while i < n {
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
}

public class NegativeBalanceEncounter extends ScriptableSystem {

    private let m_officeAudit: Int32;
    private let m_estateAudit: Int32;
    private let m_estateStepTaken: Bool;
    private let m_compoundFound: Int32;
    private let m_compoundAnnounced: Bool;
    private let m_estateFound: Int32;
    private let m_estateAnnounced: Bool;
    private let m_hoshinoId: EntityID;
    private let m_hoshinoSpawned: Bool;
    private let m_hoshinoSeenAlive: Bool;
    private let m_hoshinoGreeted: Bool;
    private let m_hoshinoProvoked: Bool;
    private let m_hoshinoShielded: Bool;
    private let m_hoshinoMetTicks: Int32;
    private let m_downloadBusy: Bool;
    private let m_uploadBusy: Bool;
    private let m_sendBusy: Bool;
    private let m_talkBusy: Bool;
    private let m_barWaited: Int32;
    private let m_mamaMissingTicks: Int32;
    private let m_mamaHeld: Bool;
    private let m_mamaMuted: Bool;
    private let m_wayinShown: Int32;
    private let m_wayinMappin: NewMappinID;
    private let m_wayinMappinUp: Bool;
    private let m_epilogueBusy: Bool;
    private let m_ticks: Int32;
    private let m_shardOpened: Bool;
    private let m_shardTicks: Int32;
    private let m_shardWait: Int32;
    private let m_shardGrace: Int32;
    private let m_shardVisited: Int32;

    private func OnAttach() -> Void {
        this.Schedule(0.5);
    }

    public func Schedule(delay: Float) -> Void {
        let cb: ref<CCGig01EncounterTick> = new CCGig01EncounterTick();
        cb.system = this;
        GameInstance.GetDelaySystem(this.GetGameInstance()).DelayCallback(cb, delay, false);
    }

    // 6s
    private func AuditTicks() -> Int32 { return 4; }

    private func AuditSite(estate: Bool) -> Void {
        if estate {
            this.m_estateAudit -= 1;
            if this.m_estateAudit > 0 {
                return;
            }
            this.m_estateAudit = this.AuditTicks();
            this.SpawnEstateSecurity();
            return;
        }
        this.m_officeAudit -= 1;
        if this.m_officeAudit > 0 {
            return;
        }
        this.m_officeAudit = this.AuditTicks();
        this.SpawnOfficeSecurity();
    }

    private func SpawnOfficeSecurity() -> Void {
        this.FindCompoundGuards();
    }

    private func SpawnEstateSecurity() -> Void {
        this.FindHoshino();
        this.FindEstateGuards();
    }

    public static func EstateCommunityRef() -> String {
        return "$/mod/cc_g01_estate/#cc_g01_estate_com";
    }

    public static func CompoundCommunityRef() -> String {
        return "$/mod/cc_g01_compound/#cc_g01_compound_com";
    }

    // 30 guards
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

    // 29 guards
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

    private func FindEstateGuards() -> Void {
        this.FindDetail(NegativeBalanceEncounter.EstateCommunityRef(),
                        NegativeBalanceEncounter.EstateEntries(), true);
    }

    private func FindCompoundGuards() -> Void {
        this.FindDetail(NegativeBalanceEncounter.CompoundCommunityRef(),
                        NegativeBalanceEncounter.CompoundEntries(), false);
    }

    private func FindDetail(reference: String, names: array<CName>,
                            estate: Bool) -> Void {
        let game: GameInstance = this.GetGameInstance();
        let nref: NodeRef = CreateNodeRef(reference);
        let root: GlobalNodeRef;
        let g: GlobalNodeRef = ResolveNodeRef(nref, root);
        if !GlobalNodeRef.IsDefined(g) {
            // 1 = sector not loading
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
                let senses: ref<SenseComponent> = puppet.GetSensesComponent();
                if IsDefined(senses) {
                    senses.Toggle(true);
                }
                found += 1;
            }
            i += 1;
        }
        this.ReadBackDetail(game, objects, estate);
        if found <= 0 {
            // 2 = no bodies yet
            this.NoteGuards(game, estate, 2, this.HighWater(estate),
                            ArraySize(names));
            return;
        }
        if found > this.HighWater(estate) {
            this.SetHighWater(estate, found);
        }
        // 3 = found, hostile
        this.NoteGuards(game, estate, 3, this.HighWater(estate),
                        ArraySize(names));
        if !this.Announced(estate)
            && this.HighWater(estate) >= ArraySize(names) {
            this.SetAnnounced(estate);
            CCSharedHud.Notify(game, GetLocalizedTextByKey(estate
                ? n"cc-g01-hud-estate-security" : n"cc-g01-hud-arasaka-security"));
        }
    }

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

    private func NoteGuards(game: GameInstance, estate: Bool, code: Int32,
                            found: Int32, total: Int32) -> Void {
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        if !IsDefined(qs) {
            return;
        }
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

    public static func CommunityRef() -> String {
        return "$/mod/cc_g01_hoshino/#cc_g01_hoshino_com";
    }

    public static func Entry() -> CName { return n"hoshino"; }

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

    public func DownloadStep(step: Int32) -> Void {
        switch step {
            case 0:
                CCSharedHud.RunBar(this.GetGameInstance(),
                    // two 1.6s steps
                    GetLocalizedTextByKey(n"cc-g01-hud-copy-ledger"), 3.2);
                break;
            case 1: break;
            case 2:
                CCSharedHud.ShowBar(this.GetGameInstance(), false, "");
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

    public func SendStep(step: Int32) -> Void {
        let key: String;
        let kind: SimpleMessageType = SimpleMessageType.Connection;
        switch step {
            case 0: key = "cc-g01-hud-send-01"; break;
            case 1: key = "cc-g01-hud-send-02"; break;
            case 2:
                key = "cc-g01-hud-send-03";
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

    public func StartTerminalTalk() -> Void {
        GameInstance.GetQuestsSystem(this.GetGameInstance())
            .SetFactStr("cc_g01_terminal_left", 1);
    }

    public func UploadStep(step: Int32) -> Void {
        switch step {
            case 0:
                CCSharedHud.RunBar(this.GetGameInstance(),
                    GetLocalizedTextByKey(n"UI-QuestNotifications-sts_sabotaging"), 10.0);
                break;
            case 1: break;
            case 2: break;
            case 3: break;
            case 4:
                CCSharedHud.ShowBar(this.GetGameInstance(), false, "");
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

    private func ShowWayInMarker(leg: Int32) -> Void {
        let spot: Vector4 = CCGig01Places.WayInMarker(leg);
        if this.m_wayinMappinUp {
            CCSharedMappins.Move(this.GetGameInstance(), this.m_wayinMappin, spot);
            return;
        }
        this.m_wayinMappin = CCSharedMappins.Show(this.GetGameInstance(), spot);
        this.m_wayinMappinUp = true;
    }

    private func HideWayInMarker() -> Void {
        if !this.m_wayinMappinUp {
            return;
        }
        CCSharedMappins.Hide(this.GetGameInstance(), this.m_wayinMappin);
        this.m_wayinMappinUp = false;
        this.m_wayinShown = 0;
    }

    private func MamaRecord() -> TweakDBID {
        return t"Character.Mama_Welles";
    }

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
            this.m_mamaMuted = false;
        }
    }

    private func FindMamaWelles(player: ref<PlayerPuppet>) -> ref<GameObject> {
        let query: TargetSearchQuery = TSQ_NPC();
        // through walls
        query.testedSet = TargetingSet.Complete;
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

    private func GiveSkim(player: ref<PlayerPuppet>, qs: ref<QuestsSystem>) -> Void {
        qs.SetFactStr("cc_g01_skimmed", 1);
        CCSharedRewards.Pay(this.GetGameInstance(), player, 12500, 0);
    }

    private func GiveReward(player: ref<PlayerPuppet>, qs: ref<QuestsSystem>) -> Void {
        qs.SetFactStr("cc_g01_rewarded", 1);
        CCSharedRewards.Pay(this.GetGameInstance(), player, 0, 300);
    }

    private func PayNix(player: ref<PlayerPuppet>, qs: ref<QuestsSystem>) -> Void {
        qs.SetFactStr("cc_g01_nix_paid", 1);
        GameInstance.GetTransactionSystem(this.GetGameInstance())
            // nix's fee
            .RemoveItemByTDBID(player, t"Items.money", 15000);
    }

    public func Tick() -> Void {
        let game: GameInstance = this.GetGameInstance();
        let player: ref<PlayerPuppet> = GameInstance.GetPlayerSystem(game)
            .GetLocalPlayerMainGameObject() as PlayerPuppet;

        let stop: Bool = false;

        if IsDefined(player) {
            let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
            let pos: Vector4 = player.GetWorldPosition();
            let accepted: Bool = qs.GetFactStr("cc_g01_accepted") == 1;

            let inOutline: Bool = CCGig01Places.InsideEstate(pos);
            let atEstateNow: Bool = inOutline
                || CCSharedWorld.Near(pos, CCGig01Places.EstateGate(), 45.0, 12.0, 25.0)
                || CCSharedWorld.Near(pos, CCGig01Places.Hoshino(), 70.0, 12.0, 60.0);
            qs.SetFactStr("cc_g01_dbg_pz", Cast<Int32>(pos.Z));
            qs.SetFactStr("cc_g01_dbg_estate_in", inOutline ? 1 : 0);
            qs.SetFactStr("cc_g01_dbg_at_estate", atEstateNow ? 1 : 0);

            if !accepted || qs.GetFactStr("cc_g01_done") > 0 {
                this.ReleaseMama(qs, player);
            }

            if qs.GetFactStr("cc_g01_wayin_reached") > 0
                || !accepted
                || qs.GetFactStr("cc_g01_done") > 0 {
                this.HideWayInMarker();
            }

            if accepted && qs.GetFactStr("cc_g01_done") == 0 {
                let atOffice: Bool = CCGig01Places.InsideCompound(pos)
                    || Vector4.Distance(pos, CCGig01Places.CompoundEntry()) < 60.0;
                if atOffice && qs.GetFactStr("cc_g01_office_reached") == 0 {
                    qs.SetFactStr("cc_g01_office_reached", 1);
                }
                if qs.GetFactStr("cc_g01_left_compound") == 0
                    && (atOffice
                        || Vector4.Distance(pos, CCGig01Places.CompoundEntry()) < 100.0) {
                    this.AuditSite(false);
                }

                if qs.GetFactStr("cc_g01_ledger_read") > 0
                    && qs.GetFactStr("cc_g01_terminal_done") <= 0
                    && !this.m_downloadBusy {
                    this.m_downloadBusy = true;
                    this.DownloadStep(0);
                }

                if qs.GetFactStr("cc_g01_ledger_copied") > 0
                    && qs.GetFactStr("cc_g01_terminal_done") <= 0
                    && !this.m_talkBusy
                    && !CCSharedWorld.IsUsingDevice(this.GetGameInstance(), player) {
                    this.m_talkBusy = true;
                    this.StartTerminalTalk();
                }

                if qs.GetFactStr("cc_g01_terminal_done") > 0
                    && qs.GetFactStr("cc_g01_shard_found") == 0
                    && Vector4.Distance(pos, CCG01Shard.ObjectSpot()) <= 2.0 {
                    qs.SetFactStr("cc_g01_shard_found", 1);
                }

                if qs.GetFactStr("cc_g01_terminal_done") > 0
                    && qs.GetFactStr("cc_g01_shard_found") == 0
                    && Vector4.Distance(pos, CCG01Shard.ObjectSpot()) <= 4.0 {
                    this.m_shardWait += 1;
                    // 45s
                    if this.m_shardWait > 30 {
                        CCSharedHud.Notify(this.GetGameInstance(),
                                           GetLocalizedTextByKey(n"cc-g01-hud-shard-missing"));
                        qs.SetFactStr("cc_g01_shard_found", 1);
                    }
                }

                if qs.GetFactStr("cc_g01_shard_open") > 0
                    && qs.GetFactStr("cc_g01_shard_read") == 0
                    && !this.m_shardOpened {
                    this.m_shardGrace += 1;
                    // 5 min
                    if this.m_shardGrace > 200 {
                        this.m_shardOpened = CCG01Shard.Open(game);
                    }
                }

                if qs.GetFactStr("cc_g01_shard_open") > 0
                    && qs.GetFactStr("cc_g01_shard_read") == 0
                    && CCG01Shard.HasBeenRead(game) {
                    this.m_shardVisited += 1;
                    if this.m_shardVisited > 1 {
                        qs.SetFactStr("cc_g01_shard_read", 1);
                    }
                }

                if this.m_shardOpened && qs.GetFactStr("cc_g01_shard_read") == 0 {
                    this.m_shardTicks += 1;
                    if this.m_shardTicks > 20 {
                        qs.SetFactStr("cc_g01_shard_read", 1);
                    }
                }

                if qs.GetFactStr("cc_g01_ledger_send") > 0
                    && qs.GetFactStr("cc_g01_ledger_sent") == 0
                    && !this.m_sendBusy {
                    this.m_sendBusy = true;
                    this.SendStep(0);
                }

                if qs.GetFactStr("cc_g01_pay_nix") > 0
                    && qs.GetFactStr("cc_g01_nix_paid") == 0 {
                    this.PayNix(player, qs);
                }

                if qs.GetFactStr("cc_g01_nix_done") == 1 {
                    let atEstate: Bool =
                        CCSharedWorld.Near(pos, CCGig01Places.EstateGate(), 45.0, 12.0, 25.0)
                        || CCSharedWorld.Near(pos, CCGig01Places.Hoshino(), 70.0, 12.0, 60.0)
                        || CCGig01Places.InsideEstate(pos);
                    let justArrived: Bool = false;
                    if atEstate {
                        if qs.GetFactStr("cc_g01_estate_reached") == 0 {
                            qs.SetFactStr("cc_g01_estate_reached", 1);
                            justArrived = true;
                        }
                    }

                    if qs.GetFactStr("cc_g01_escaped") == 0
                        && (atEstate
                            || CCSharedWorld.Near(pos, CCGig01Places.EstateGate(), 120.0, 12.0, 25.0)) {
                        this.AuditSite(true);
                    }

                    let justFoundWayIn: Bool = false;
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

                    if qs.GetFactStr("cc_g01_estate_reached") > 0
                        && qs.GetFactStr("cc_g01_wayin_reached") == 0 {
                        let leg: Int32 = qs.GetFactStr("cc_g01_wayin_leg");
                        if leg < 1 {
                            leg = 1;
                        }
                        let want: Int32 = leg;
                        let k: Int32 = CCGig01Places.WayInLegs();
                        while k >= 1 {
                            if CCGig01Places.AtWayInPoint(pos, k) {
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
                        if this.m_wayinShown != want {
                            this.m_wayinShown = want;
                            this.ShowWayInMarker(want);
                        }
                    }
                }

                if !this.m_hoshinoSpawned
                   && qs.GetFactStr("cc_g01_estate_reached") > 0 {
                    this.FindHoshino();
                }
                if this.m_hoshinoSpawned && qs.GetFactStr("cc_g01_hoshino_dead") == 0 {
                    let hoshino: ref<ScriptedPuppet> =
                        GameInstance.FindEntityByID(this.GetGameInstance(),
                                                    this.m_hoshinoId) as ScriptedPuppet;

                    if IsDefined(hoshino) && ScriptedPuppet.IsAlive(hoshino) {
                        this.m_hoshinoSeenAlive = true;
                        let hostileNow: Bool = this.m_hoshinoProvoked;
                        if !hostileNow {
                            let hp: Float = GameInstance.GetStatPoolsSystem(game)
                                .GetStatPoolValue(Cast<StatsObjectID>(this.m_hoshinoId),
                                                  gamedataStatPoolType.Health, false);
                            hostileNow = (hp > 0.0 && hp < 99.0)
                                || qs.GetFactStr("cc_g01_hoshino_talked") > 0
                                || qs.GetFactStr("cc_g01_dbg_hoshino_fight") > 0;
                        }
                        if qs.GetFactStr("cc_g01_hoshino_met") > 0
                            && qs.GetFactStr("cc_g01_hoshino_talked") == 0 {
                            this.m_hoshinoMetTicks += 1;
                        }
                        let wantShield: Bool = qs.GetFactStr("cc_g01_hoshino_talked") == 0
                            && qs.GetFactStr("cc_g01_hoshino_dead") == 0
                            && qs.GetFactStr("cc_g01_done") == 0
                            // 2 min
                            && this.m_hoshinoMetTicks < 80
                            && !hostileNow;
                        let gods: ref<GodModeSystem> = GameInstance.GetGodModeSystem(game);
                        let shieldAgent: ref<AttitudeAgent> = hoshino.GetAttitudeAgent();
                        if wantShield {
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

                        if hostileNow {
                            this.m_hoshinoProvoked = true;
                            NegativeBalanceEncounter.TurnOnPlayer(hoshino, player);
                        }
                        if !this.m_estateStepTaken
                            && !this.m_hoshinoGreeted
                            && CCSharedWorld.Near(pos, hoshino.GetWorldPosition(),
                                                  8.0, 2.0, 2.0) {
                            this.m_hoshinoGreeted = true;
                            qs.SetFactStr("cc_g01_hoshino_met", 1);
                        }

                    } else {
                        if this.m_hoshinoSeenAlive
                            && IsDefined(GameInstance.FindEntityByID(
                                this.GetGameInstance(), this.m_hoshinoId))
                            && Vector4.Distance(pos, CCGig01Places.Hoshino()) < 120.0 {
                            qs.SetFactStr("cc_g01_hoshino_dead", 1);
                            qs.SetFactStr("cc_g01_hoshino_met", 1);
                        }
                    }
                }

                if qs.GetFactStr("cc_g01_hoshino_dead") == 1
                    && qs.GetFactStr("cc_g01_malware_done") == 0
                    && !this.m_uploadBusy
                    && Vector4.Distance(pos, CCGig01Places.EstateTerminal()) < 3.0
                    && CCSharedWorld.IsUsingDevice(this.GetGameInstance(), player) {
                    this.m_uploadBusy = true;
                    this.UploadStep(0);
                }

                if qs.GetFactStr("cc_g01_malware_done") > 0
                    && qs.GetFactStr("cc_g01_malware_talk") == 0
                    && !CCSharedWorld.IsUsingDevice(this.GetGameInstance(), player) {
                    qs.SetFactStr("cc_g01_malware_talk", 1);
                }

                if qs.GetFactStr("cc_g01_terminal_done") > 0
                    && qs.GetFactStr("cc_g01_left_compound") == 0
                    && Vector4.Distance(pos, CCGig01Places.OfficeTerminal()) > 110.0 {
                    qs.SetFactStr("cc_g01_left_compound", 1);
                }

                if qs.GetFactStr("cc_g01_malware_done") == 1
                    && qs.GetFactStr("cc_g01_escaped") == 0
                    // 21m past the gate
                    && Vector4.Distance(pos, CCGig01Places.Hoshino()) > 160.0 {
                    qs.SetFactStr("cc_g01_escaped", 1);
                }

                if qs.GetFactStr("cc_g01_escaped") == 1
                    && qs.GetFactStr("cc_g01_at_coyote") == 0
                    && CCSharedWorld.Near(pos, CCGig01Places.Coyote(), 15.0, 5.0, 5.0) {
                    qs.SetFactStr("cc_g01_at_coyote", 1);
                }

                let holdMama: Bool = qs.GetFactStr("cc_g01_escaped") > 0
                    && qs.GetFactStr("cc_g01_mama_talked") == 0
                    && Vector4.Distance(pos, CCGig01Places.Coyote()) < 200.0;
                if holdMama {
                    if qs.GetFactStr("mama_is_talking") <= 0 {
                        qs.SetFactStr("mama_is_talking", 1);
                        this.m_mamaHeld = true;
                    }
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

                if qs.GetFactStr("cc_g01_escaped") == 1
                    && qs.GetFactStr("cc_g01_mama_reached") == 0
                    && !this.m_epilogueBusy
                    && Vector4.Distance(pos, CCGig01Places.Coyote()) < 60.0 {

                    let mama: ref<GameObject> = this.FindMamaWelles(player);

                    if IsDefined(mama) {
                        this.m_mamaMissingTicks = 0;
                        if Vector4.Distance(pos, mama.GetWorldPosition()) < 3.5 {
                            this.m_epilogueBusy = true;
                            qs.SetFactStr("cc_g01_mama_present", 1);
                            qs.SetFactStr("cc_g01_mama_reached", 1);
                        }
                    } else {
                        if Vector4.Distance(pos, CCGig01Places.MamaWelles()) < 15.0 {
                            this.m_mamaMissingTicks += 1;
                            // 45s in the bar
                            if this.m_mamaMissingTicks >= 30 {
                                this.m_epilogueBusy = true;
                                // 2 = skip the epilogue
                                qs.SetFactStr("cc_g01_mama_present", 2);
                                qs.SetFactStr("cc_g01_mama_reached", 1);
                            }
                        }
                    }
                }
            }

            if qs.GetFactStr("cc_g01_epilogue_scene_done") > 0
                && qs.GetFactStr("cc_g01_mama_talked") == 0 {
                qs.SetFactStr("cc_g01_mama_talked", 1);
            }

            if qs.GetFactStr("cc_g01_mama_talked") > 0
                && qs.GetFactStr("cc_g01_bar_reached") == 0 {
                this.m_barWaited += 1;
            }
            if qs.GetFactStr("cc_g01_mama_talked") > 0
                && qs.GetFactStr("cc_g01_bar_reached") == 0
                && (CCSharedWorld.Near(pos, CCGig01Places.BarStools(), 4.0, 3.0, 3.0)
                    || (this.m_barWaited > 30
                        && CCSharedWorld.Near(pos, CCGig01Places.Coyote(), 15.0, 5.0, 5.0))) {
                qs.SetFactStr("cc_g01_bar_reached", 1);
            }

            if qs.GetFactStr("cc_g01_malware_done") > 0
                && qs.GetFactStr("cc_g01_skimmed") <= 0 {
                this.GiveSkim(player, qs);
            }

            if qs.GetFactStr("cc_g01_done") > 0 && qs.GetFactStr("cc_g01_rewarded") <= 0 {
                this.GiveReward(player, qs);
            }

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
