module CyberpunkCodes.Gig01

public abstract class CCG01Doors {

    public static func Count() -> Int32 { return 5; }

    public static func Pos(i: Int32) -> Vector4 {
        switch i {
            case 0: return new Vector4(-241.9, -1450.7, 14.6, 1.0);
            case 1: return new Vector4(-219.8, -1423.2, 14.6, 1.0);
            case 2: return new Vector4(-252.6, -1443.3, 14.6, 1.0);
            case 3: return new Vector4(-265.3, -1435.8, 14.6, 1.0);
            // ground floor
            default: return new Vector4(-260.9, -1452.2, 8.6, 1.0);
        }
    }

    // nearest other door 9m
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

    public static func StateCode(st: EDeviceStatus) -> Int32 {
        if Equals(st, EDeviceStatus.DISABLED) { return 1; }
        if Equals(st, EDeviceStatus.ON) { return 2; }
        if Equals(st, EDeviceStatus.OFF) { return 3; }
        if Equals(st, EDeviceStatus.UNPOWERED) { return 4; }
        return 9;
    }

    // 3s
    public static func MaxPasses() -> Int32 { return 6; }

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
        if qs.GetFactStr("cc_g01_accepted") <= 0 {
            return;
        }
        if qs.GetFactStr("cc_g01_done") > 0 {
            return;
        }
        qs.SetFactStr("cc_g01_dbg_door_state",
                      CCG01Doors.StateCode(ps.GetDeviceState()));
        CCG01Doors.Pump(ps, 0);
    }

    public static func Pump(ps: ref<DoorControllerPS>, pass: Int32) -> Void {
        if !IsDefined(ps) {
            return;
        }
        let game: GameInstance = ps.GetGameInstance();
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        if !IsDefined(qs) {
            return;
        }

        if Equals(ps.GetDeviceState(), EDeviceStatus.ON) {
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

@wrapMethod(DoorControllerPS)
public func GameAttached() -> Void {
    wrappedMethod();
    CCG01Doors.OnAttached(this);
}
