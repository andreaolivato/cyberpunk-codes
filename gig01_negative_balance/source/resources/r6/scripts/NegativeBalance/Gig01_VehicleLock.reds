module CyberpunkCodes.Gig01

import CyberpunkCodes.Shared.Gig01.*

public class CCG01VehicleLock {

    public static func Restriction() -> TweakDBID {
        return t"GameplayRestriction.cc_g01_no_vehicle";
    }

    public static func WindowFact() -> CName { return n"cc_g01_vlock"; }

    public static func GaveUpFact() -> CName { return n"cc_g01_vlock_giveup"; }

    // 3 min
    public static func CapSeconds() -> Float { return 180.0; }

    public static func BannerGapSeconds() -> Float { return 10.0; }

    public static func DismountKey() -> String { return "cc-g01-vehicle-dismount"; }
    public static func DismountGapSeconds() -> Float { return 25.0; }

    public static func Dismount(game: GameInstance) -> Void {
        CCSharedHud.NotifyTyped(game,
                                GetLocalizedTextByKey(StringToName(CCG01VehicleLock.DismountKey())),
                                SimpleMessageType.Undefined, 4.0);
    }

    public static func Player(game: GameInstance) -> ref<GameObject> {
        return GameInstance.GetPlayerSystem(game).GetLocalPlayerMainGameObject();
    }

    public static func IsMounted(game: GameInstance) -> Bool {
        let player: ref<GameObject> = CCG01VehicleLock.Player(game);
        if !IsDefined(player) {
            return false;
        }
        return VehicleComponent.IsMountedToVehicle(game, player);
    }

    public static func GaveUp(game: GameInstance) -> Bool {
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        if !IsDefined(qs) {
            return true;
        }
        return qs.GetFact(CCG01VehicleLock.GaveUpFact()) > 0;
    }

    public static func WindowOpen(game: GameInstance) -> Bool {
        let qs: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game);
        if !IsDefined(qs) {
            return false;
        }
        return qs.GetFact(CCG01VehicleLock.WindowFact()) > 0;
    }

    public static func SetLock(game: GameInstance, on: Bool) -> Void {
        let player: ref<GameObject> = CCG01VehicleLock.Player(game);
        if !IsDefined(player) {
            return;
        }
        if on {
            StatusEffectHelper.ApplyStatusEffect(player, CCG01VehicleLock.Restriction());
        } else {
            StatusEffectHelper.RemoveStatusEffect(player, CCG01VehicleLock.Restriction());
        }
    }

    // metres
    public static func LookRange() -> Float { return 5.0; }

    public static func LookingAtVehicle(game: GameInstance) -> Bool {
        let player: ref<GameObject> = CCG01VehicleLock.Player(game);
        if !IsDefined(player) {
            return false;
        }
        let ts: ref<TargetingSystem> = GameInstance.GetTargetingSystem(game);
        if !IsDefined(ts) {
            return false;
        }
        let target: ref<GameObject> = ts.GetLookAtObject(player, false, false);
        if !IsDefined(target) {
            return false;
        }
        if !IsDefined(target as VehicleObject) {
            return false;
        }
        return Vector4.Distance(player.GetWorldPosition(), target.GetWorldPosition())
            <= CCG01VehicleLock.LookRange();
    }

    public static func Banner(game: GameInstance) -> Void {
        let evt: ref<UIInGameNotificationEvent> = new UIInGameNotificationEvent();
        evt.m_notificationType = UIInGameNotificationType.ActionRestriction;
        evt.m_overrideCurrentNotification = true;
        GameInstance.GetUISystem(game).QueueEvent(evt);
    }
}
