module CyberpunkCodes.Gig01

public class NegativeBalanceHolocall extends ScriptableSystem {

    private let m_state: array<Int32>;
    private let m_waited: array<Int32>;
    private let m_ftDefer: Int32;
    private let m_ftSettle: Int32;
    private let m_ftLocked: Bool;
    private let m_ftKnown: Bool;
    private let m_rings: array<Int32>;
    private let m_vlHeld: Float;
    private let m_vlLast: Float;
    private let m_vlBanner: Float;
    private let m_mountDefer: Int32;
    private let m_mountBlocked: Bool;
    private let m_dismountBanner: Float;

    private func OnAttach() -> Void {
        this.Schedule(8.0);
    }

    private func Contact(call: Int32) -> CName {
        if call == 0 { return n"elena_ortega"; }
        return n"cc_g01_nix";
    }

    private func Prefix(call: Int32) -> String {
        if call == 0 { return "cc_g01_call"; }
        if call == 1 { return "cc_g01_nixcall"; }
        // v rings nix
        return "cc_g01_nixbrief";
    }

    private func PlayerInitiated(call: Int32) -> Bool {
        return call == 2;
    }

    private func PublishRingOk(qs: ref<QuestsSystem>) -> Bool {
        if qs.GetFactStr("cc_g01_ring_want") <= 0 {
            qs.SetFactStr("cc_g01_ring_ok", 0);
            return false;
        }
        let ok: Bool = this.Phone().IsCallingEnabled() && this.FastTravelClear()
            && this.MountedClear(1);
        qs.SetFactStr("cc_g01_ring_ok", ok ? 1 : 0);
        return true;
    }

    private func PhoneFact(call: Int32) -> String {
        if call == 0 { return "phonecall_elena_ortega_with_player"; }
        if this.PlayerInitiated(call) { return "phonecall_player_with_cc_g01_nix"; }
        return "phonecall_cc_g01_nix_with_player";
    }

    private func CallCount() -> Int32 { return 3; }

    private func TickLive() -> Float { return 0.2; }
    private func TickIdle() -> Float { return 2.0; }

    // 2s
    private func DialToneTicks() -> Int32 { return 10; }
    // 3s
    private func ChromeWaitTicks() -> Int32 { return 15; }

    // game gives up at 8s
    private func RingSeconds() -> Float { return 9.0; }

    private func RingTicks() -> Int32 {
        return Cast<Int32>(this.RingSeconds() / this.TickLive());
    }

    private func RetrySeconds(rings: Int32) -> Float {
        if rings <= 1 { return 24.0; }
        if rings <= 3 { return 30.0; }
        if rings <= 4 { return 60.0; }
        return 300.0;
    }

    private func RetryTicks(rings: Int32) -> Int32 {
        return Cast<Int32>(this.RetrySeconds(rings) / this.TickLive());
    }

    public func Schedule(delay: Float) -> Void {
        let cb: ref<CCGig01HolocallTick> = new CCGig01HolocallTick();
        cb.system = this;
        GameInstance.GetDelaySystem(this.GetGameInstance()).DelayCallback(cb, delay, false);
    }

    private func Phone() -> ref<PhoneSystem> {
        return GameInstance.GetScriptableSystemsContainer(this.GetGameInstance())
            .Get(n"PhoneSystem") as PhoneSystem;
    }

    private func MountedClear(call: Int32) -> Bool {
        if !CCG01VehicleLock.IsMounted(this.GetGameInstance()) {
            this.m_mountDefer = 0;
            return true;
        }
        if call == 0 {
            return false;
        }
        this.m_mountBlocked = true;
        if this.m_mountDefer >= this.MountedCapTicks() {
            return true;
        }
        this.m_mountDefer += 1;
        return false;
    }

    private func MountedCapTicks() -> Int32 {
        return Cast<Int32>(90.0 / this.TickLive());
    }

    private func FastTravelClear() -> Bool {
        if CCGig01StartRules.IsFastTravelling(this.GetGameInstance()) {
            this.m_ftSettle = 15;
            if this.m_ftDefer >= 150 {
                return true;
            }
            this.m_ftDefer += 1;
            return false;
        }
        this.m_ftDefer = 0;
        if this.m_ftSettle > 0 {
            this.m_ftSettle -= 1;
            return false;
        }
        return true;
    }

    private func Call(call: Int32, phase: questPhoneCallPhase) -> Void {
        let req: ref<questTriggerCallRequest> = new questTriggerCallRequest();
        if this.PlayerInitiated(call) {
            req.caller = n"player";
            req.addressee = this.Contact(call);
        } else {
            req.caller = this.Contact(call);
            req.addressee = n"player";
        }
        req.callPhase = phase;
        req.callMode = questPhoneCallMode.Audio;
        req.isRejectable = !this.PlayerInitiated(call);
        req.showAvatar = true;
        req.visuals = questPhoneCallVisuals.Default;
        req.isPlayerTriggered = false;
        this.Phone().QueueRequest(req);
    }

    public func Tick() -> Void {
        while ArraySize(this.m_state) < this.CallCount() { ArrayPush(this.m_state, 0); }
        while ArraySize(this.m_waited) < this.CallCount() { ArrayPush(this.m_waited, 0); }
        while ArraySize(this.m_rings) < this.CallCount() { ArrayPush(this.m_rings, 0); }

        let call: Int32 = 0;
        let live: Bool = false;
        while call < this.CallCount() {
            if this.Step(call) {
                live = true;
            }
            call += 1;
        }
        if this.PublishRingOk(GameInstance.GetQuestsSystem(this.GetGameInstance())) {
            live = true;
        }
        this.ApplyLock();
        this.UpdateVehicleLock();

        if GameInstance.GetQuestsSystem(this.GetGameInstance()).GetFactStr("cc_g01_done") > 0 {
            return;
        }

        this.m_vlLast = live ? this.TickLive() : this.TickIdle();
        this.Schedule(this.m_vlLast);
    }

    private func ApplyLock() -> Void {
        let want: Bool = false;
        let call: Int32 = 0;
        while call < this.CallCount() {
            if this.m_state[call] == 1 && this.m_waited[call] <= this.RingTicks() {
                want = true;
            }
            if this.m_state[call] == 4 {
                want = true;
            }
            call += 1;
        }
        if GameInstance.GetQuestsSystem(this.GetGameInstance())
            .GetFactStr("cc_g01_ringing") > 0 {
            want = true;
        }
        let unchanged: Bool = (want && this.m_ftLocked)
            || (!want && !this.m_ftLocked);
        if this.m_ftKnown && unchanged {
            return;
        }
        this.m_ftKnown = true;
        let game: GameInstance = this.GetGameInstance();
        if want {
            FastTravelSystem.AddFastTravelLock(n"cc_g01_call", game,
                                               t"GameplayRestriction.BlockFastTravel");
        } else {
            FastTravelSystem.RemoveFastTravelLock(n"cc_g01_call", game,
                                                  t"GameplayRestriction.BlockFastTravel");
        }
        this.m_ftLocked = want;
    }

    private func RingingForBeat() -> Bool {
        let call: Int32 = 0;
        while call < this.CallCount() {
            if this.m_state[call] == 1 && this.m_waited[call] <= this.RingTicks() {
                return true;
            }
            if this.m_state[call] == 4 {
                return true;
            }
            call += 1;
        }
        return false;
    }

    private func UpdateVehicleLock() -> Void {
        let game: GameInstance = this.GetGameInstance();
        let player: ref<GameObject> = CCG01VehicleLock.Player(game);
        if !IsDefined(player) {
            return;
        }
        let want: Bool = !CCG01VehicleLock.GaveUp(game)
            && (CCG01VehicleLock.WindowOpen(game) || this.RingingForBeat());

        if want {
            this.m_vlHeld += this.m_vlLast;
            if this.m_vlHeld >= CCG01VehicleLock.CapSeconds() {
                GameInstance.GetQuestsSystem(game).SetFact(CCG01VehicleLock.GaveUpFact(), 1);
                want = false;
            }
        } else {
            this.m_vlHeld = 0.0;
            if GameInstance.GetQuestsSystem(game).GetFact(CCG01VehicleLock.GaveUpFact()) > 0
                && !CCG01VehicleLock.WindowOpen(game)
                && !this.RingingForBeat() {
                GameInstance.GetQuestsSystem(game).SetFact(CCG01VehicleLock.GaveUpFact(), 0);
            }
        }

        let applied: Bool = StatusEffectSystem.ObjectHasStatusEffect(
            player, CCG01VehicleLock.Restriction());
        let matches: Bool = (want && applied) || (!want && !applied);
        if !matches {
            CCG01VehicleLock.SetLock(game, want);
        }

        if !want {
            this.m_vlBanner = 0.0;
            if this.m_dismountBanner > 0.0 {
                this.m_dismountBanner -= this.m_vlLast;
            } else {
                if this.m_mountBlocked {
                    CCG01VehicleLock.Dismount(game);
                    this.m_dismountBanner = CCG01VehicleLock.DismountGapSeconds();
                }
            }
            this.m_mountBlocked = false;
            return;
        }
        this.m_mountBlocked = false;

        if this.m_vlBanner > 0.0 {
            this.m_vlBanner -= this.m_vlLast;
            return;
        }
        if CCG01VehicleLock.IsMounted(game) {
            return;
        }
        if CCG01VehicleLock.LookingAtVehicle(game) {
            CCG01VehicleLock.Banner(game);
            this.m_vlBanner = CCG01VehicleLock.BannerGapSeconds();
        }
    }

    private func Step(call: Int32) -> Bool {
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGameInstance());
        let p: String = this.Prefix(call);

        // 9 = finished
        if qs.GetFactStr(p + "_request") <= 0 || this.m_state[call] == 9 {
            return false;
        }

        if qs.GetFactStr(p + "_done") > 0 {
            this.m_state[call] = 9;
            return false;
        }

        if this.m_state[call] == 1 || this.m_state[call] == 4 {
            if CCGig01StartRules.IsFastTravelling(this.GetGameInstance()) {
                this.Call(call, questPhoneCallPhase.EndCall);
                this.m_state[call] = 0;
                this.m_waited[call] = 0;
                if this.m_rings[call] > 0 {
                    this.m_rings[call] -= 1;
                }
                return true;
            }
        }

        switch this.m_state[call] {
            case 0:
                if this.Phone().IsCallingEnabled() && this.FastTravelClear()
                    && this.MountedClear(call) {
                    qs.SetFactStr(this.PhoneFact(call), 0);
                    if this.PlayerInitiated(call) {
                        this.Call(call, questPhoneCallPhase.IncomingCall);
                        this.m_state[call] = 4;
                        this.m_waited[call] = 0;
                    } else {
                        this.Call(call, questPhoneCallPhase.IncomingCall);
                        this.m_state[call] = 1;
                        this.m_waited[call] = 0;
                        this.m_rings[call] += 1;
                    }
                }
                break;
            // rings, then waits
            case 1:
                if qs.GetFactStr(this.PhoneFact(call)) == EnumInt(questPhoneTalkingState.Talking) {
                    qs.SetFactStr(p + "_answered", 1);
                    this.Call(call, questPhoneCallPhase.StartCall);
                    this.m_state[call] = 2;
                    this.m_waited[call] = 0;
                } else {
                    if qs.GetFactStr(this.PhoneFact(call))
                        == EnumInt(questPhoneTalkingState.Rejected) {
                        this.Call(call, questPhoneCallPhase.EndCall);
                        this.m_state[call] = 5;
                        this.m_waited[call] = 0;
                    } else {
                        this.m_waited[call] += 1;
                        if this.m_waited[call] > this.RetryTicks(this.m_rings[call]) {
                            this.m_state[call] = 0;
                            this.m_waited[call] = 0;
                        }
                    }
                }
                break;
            // declined
            case 5:
                this.m_waited[call] += 1;
                if this.m_waited[call] > this.RetryTicks(this.m_rings[call]) {
                    this.m_state[call] = 0;
                    this.m_waited[call] = 0;
                }
                break;
            // dialling
            case 4:
                this.m_waited[call] += 1;
                if this.m_waited[call] >= this.DialToneTicks() {
                    qs.SetFactStr(p + "_answered", 1);
                    this.Call(call, questPhoneCallPhase.StartCall);
                    this.m_state[call] = 2;
                    this.m_waited[call] = 0;
                }
                break;
            case 2:
                this.m_waited[call] += 1;
                if qs.GetFactStr(this.PhoneFact(call))
                    == EnumInt(questPhoneTalkingState.Talking)
                    || this.m_waited[call] >= this.ChromeWaitTicks() {
                    if qs.GetFactStr("cc_g01_no_scene") <= 0 {
                        qs.SetFactStr(p + "_talking", 1);
                    }
                    this.m_state[call] = 3;
                }
                break;
            case 3:
                if qs.GetFactStr(p + "_end") > 0 {
                    this.Call(call, questPhoneCallPhase.EndCall);
                    qs.SetFactStr(p + "_done", 1);
                    this.m_state[call] = 9;
                }
                break;
        }
        return true;
    }
}

public class CCGig01HolocallTick extends DelayCallback {
    public let system: wref<NegativeBalanceHolocall>;
    public func Call() -> Void {
        if IsDefined(this.system) { this.system.Tick(); }
    }
}
