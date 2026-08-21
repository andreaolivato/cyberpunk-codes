# Gameplay restrictions: taking a control away from the player

`GameplayRestriction.*` is the base game's vocabulary for switching off one
thing the player can normally do: driving, sprinting, opening the menu, using
the phone, drawing a weapon. A quest that needs the player to stand still and
listen uses these rather than fighting the input system.

There are 100 of them in 2.31. This file lists the vocabulary, says how to apply
one, and says what has actually been measured versus what is only a name.

**Read the "what is established" table before using anything here.** The record
names below are extracted from the game and are real. What each one actually
stops has been measured for a handful and for no others.

## They are status effects, not a lock API

Every `GameplayRestriction.*` record is a `gamedataStatusEffect_Record`. The
fields are the status-effect fields: `duration`, `packages`, `gameplayTags`,
`statusEffectType`, `maxStacks`, `savable`. So one is put on and taken off the
player the way any status effect is:

```swift
StatusEffectHelper.ApplyStatusEffect(player, t"GameplayRestriction.NoDriving");
StatusEffectHelper.RemoveStatusEffect(player, t"GameplayRestriction.NoDriving");
```

Fast travel is the exception, and it is the one this project ships. It has its
own named-lock API, and a named lock is reference counted by name, so two
holders cannot clear each other's:

```swift
FastTravelSystem.AddFastTravelLock(n"cc_g01_call", game,
                                   t"GameplayRestriction.BlockFastTravel");
```

Only three records carry the `restrictionName` field that pairs with that API:
`BlockFastTravel`, `BlockFastTravelQuest` and `PhoneCall`. Everything else is
applied as a plain status effect, with no name attached and no reference count.

## The hazard, before the list

A status effect with `savable` set is written into the save file. A restriction
this mod applies and then forgets it is holding therefore survives a reload, and
the player loses that control for the rest of that save.

**This is measured, not theoretical.** `VehicleNoInteraction` was applied, the
game was saved, quit to desktop, relaunched and loaded, and it came back still
blocking. It has no useful duration either, so it does not expire on its own.
Treat every record here as savable until one has been shown otherwise.

A guard that runs on the first pass of every session fixes the reload case, and
it is cheap. Nothing fixes the case where the player uninstalls the mod while a
lock is applied, because no script is left to lift it. Reinstalling and loading
once clears it, which makes it recoverable rather than fatal, and it is still
not a thing to ship on purpose.

## Ship your own record instead, with saving turned off

`savable` is a field on the record, so the fix is to clone the one you want and
turn it off. Four lines, no hook, nothing left in anyone's save:

```yaml
GameplayRestriction.cc_g01_no_vehicle:
  $base: GameplayRestriction.VehicleNoInteraction
  savable: false
```

**Measured 2026-08-21, on all three things that could have gone wrong.**

- **The clone still blocks.** The game's gate reads a gameplay tag rather than a
  record id, so a clone inherits the behaviour. This was the half that could
  have made the whole approach pointless.
- **It is not written to the save.** Applied, saved, quit to desktop,
  relaunched, loaded: gone, and V could drive.
- **Every line applied.** The TweakXL log is clean, and the counts moved by
  exactly one record and twenty-four flats, which is a full status-effect
  record. A rejected `savable` would have been twenty-three flats and an error
  line. `backlog.md` 13 is why that second check is not optional: a record can
  apply while one property is silently discarded, and behaviour alone will not
  tell you.

Do this for any restriction a mod applies. The base-game records are built for
quests that always run to completion inside a save the player cannot uninstall;
a mod is neither of those things.

The failure is not hypothetical, and it has a known shape here:

- `gotchas.md` 21 is the general version, that a one-way flag gets exercised
  exactly once and only in the clean direction.
- `ApplyLock` in `Gig01_Holocall.reds` is the worked guard. A plain script field
  does not survive a load while the saved effect does, so on the first pass of
  every session the script recomputes and issues a removal for a lock it does
  not believe it holds. Removing an absent lock costs nothing. Leaving a present
  one does not.

Copy that shape rather than writing a fresh lock. Anything that applies a
restriction should also have a hard time cap and a way to force it off.

## What is established, and what is only a name

| Claim | Status |
|---|---|
| The 100 record names below exist in 2.31 | Extracted from the game, reproducible, see the last section |
| They are status-effect records with the fields listed above | Extracted |
| `BlockFastTravel` blocks fast travel through the named-lock API | Shipped and played since 1.1.0 |
| `VehicleNoInteraction` stops V getting into a vehicle | Measured in game 2026-08-21 |
| `NoDriving` and `VehicleNoSummoning` apply and remove cleanly, and are not the ones that block entry | Measured in game 2026-08-21 |
| `StatusEffectHelper.ApplyStatusEffect` / `RemoveStatusEffect` is the working route | Measured in game 2026-08-21 |
| `DoStatusEffectsAllowMounting` is the game's own gate on getting into a vehicle | Found in the 2.31 script bundle, on `gamevehicleVehicleMountableComponent` |
| `VehicleNoInteraction` is savable, and does not time out | Measured 2026-08-21: applied, saved, quit to desktop, relaunched, loaded, still blocking |
| A restriction blocks silently, with no refusal message | Measured 2026-08-21 on all three vehicle records |
| Whether the other 97 are savable | **Not measured.** Assume they are until one is checked |
| What any other individual record actually stops | **Not measured.** The names are suggestive and nothing more |

The flat values are hashed in `tweakdb.bin`, so no amount of reading files will
say which control a given record takes away, nor whether it is `savable`. That
is measured by applying one and trying the control. See "How to measure one".

## The vocabulary

Grouped by area. `_inline` sub-records are omitted; they are internal parts of
the record above them, not things to apply.

### Vehicles

`NoDriving`, `VehicleNoSummoning`, `VehicleNoInteraction`, `VehicleSummoning`,
`CustomVehicleSummon`, `VehicleBlockExit`, `VehicleCombatBlockExit`,
`VehicleBlockRadioInput`, `VehicleCombat`, `VehicleCombatNoInterruptions`,
`VehicleFPP`, `VehicleOnlyForward`, `VehicleScene`, `VehicleSceneFpp`,
`VehicleSceneFppOnlyForward`, `DriverCombatFirearms`, `DriverCombatBikeWeapons`,
`AllowFastForwardInVehicle`

**`VehicleNoInteraction` is the one that stops V getting in**, measured in game
on 2026-08-21. It blocks silently: the prompt is absent and no refusal message
is shown, so anything shipping this has to say why on the mod's own account.
`SimpleScreenMessage` on the `UI_Notifications` blackboard is the plain route.
`Interactions.vehicle_door_quest_locked`, with `QuestLockAllVehDoors` and the
`questLOCKey` field, is the route that puts wording on the prompt itself, at the
cost of working one vehicle at a time. No record is named for blocking entry, so the useful one is named
for the interaction rather than for the act. `NoDriving` and `VehicleNoSummoning`
both apply and remove without error and neither blocks entry, so the obvious
name is the wrong one here.

### Saying why, when a restriction refuses something

A restriction blocks silently. The prompt is absent and nothing explains it,
which reads to a player as a broken mod rather than as the game saying no. It is
worth fixing, and the first two answers are both wrong:

| route | what the player sees |
|---|---|
| `UI_Notifications.OnscreenMessage` | cyan, left of centre. Easy to miss entirely |
| `UI_Notifications.WarningMessage` | red with a warning sign, top of screen. Reads as an alarm |
| **`UIInGameNotificationEvent`** | **"ACTION BLOCKED", the base game's own** |

Position and colour belong to the widget, so no value pushed at the first two
changes either. `SimpleMessageType` does not help: every member was tried and
they were indistinguishable.

The third is the one to use, because it is what vanilla itself sends when a
gameplay restriction refuses an action, from
`CheckWeaponAgainstGameplayRestrictions`:

```swift
let evt: ref<UIInGameNotificationEvent> = new UIInGameNotificationEvent();
evt.m_notificationType = UIInGameNotificationType.ActionRestriction;
evt.m_overrideCurrentNotification = true;
GameInstance.GetUISystem(game).QueueEvent(evt);
```

It carries no words of yours, and the type enum makes no visible difference:
`ActionRestriction`, `GenericNotification`, `SandevistanInCallRestriction` and
`CombatRestriction` all read "ACTION BLOCKED". Pick the honest one and move on.

Being canned is the point. A message players already recognise reads as the game
refusing, which is exactly what a silent block fails to convey. Where a message
has to carry your own words, telling the player what to do rather than that they
cannot, this is the wrong tool and one of the first two slots is what is left.


`VehicleBlockExit` is the mirror of it and blocks leaving, which is a different
job. The underlying gate is `DoStatusEffectsAllowMounting(GameObject)`, which
reads the player's status effects, and `BlockMountVehicle` exists as a name in
the script bundle with no matching TweakDB record, which is the shape of a
gameplay tag rather than a record id.

### Phone

`NoPhone`, `PhoneCall`, `PhoneCallDeviceActionRestrictions`, `PhoneInterrupted`,
`PhoneNoCalling`, `PhoneNoTexting`

`PhoneCall` is what vanilla applies while a call is live, so dumping the
player's effects during a base-game call says what the game itself considers
incompatible with talking.

### Movement and stance

`NoMovement`, `NoJump`, `NoSprint`, `ForceStand`, `ForceStandKeepState`,
`ForceStandWithDodge`, `ForceCrouch`, `ForceCrouchNoMovementOnlyFirearms`,
`Tier2Locomotion`, `Tier2LocomotionSlow`, `Tier2LocomotionFast`,
`FocusModeLocomotion`, `SandstormLocomotion`

The `Tier2*` set is the story-tier locomotion the game uses for scripted walks.

### Combat and weapons

`NoCombat`, `NoWeapons`, `Firearms`, `FirearmsNoUnequipNoSwitch`,
`OneHandedFirearms`, `Melee`, `FistFight`, `NoQuickMelee`, `NoGrenadeOrGadget`,
`ForceAim`, `InfiniteAmmo`, `BlockSmartWeapons`, `GrappleNoBreakFree`,
`ShootingRangeCompetition`

### Cyberware, health and progression

`NoCyberware`, `NoDangerousCyberware`, `NoDangerousPerks`, `NoSecondHeart`,
`CerberusNoSandevistan`, `NoHealing`, `PreventLowHealthOverlay`,
`NoEncumbrance`, `NoCrafting`

### Menus, UI and scanning

`BlockAllMenu`, `BlockAllHubMenu`, `LockInHubMenu`, `NoRadialMenus`,
`NoScanning`, `NoPhotoMode`, `NoTimeDisplay`, `NoTimeSkip`, `NoZooming`,
`DeviceControlZoomLock`

### World interaction

`NoWorldInteractions`, `BlockDeviceInteractions`, `BlockTrafficInteractions`,
`OnlyOpenDoor`, `SecurityLocker`

`OnlyOpenDoor` is the narrow one: every interaction off except a door.

### Camera and view

`NoCameraControl`, `CinematicCamera`, `BinocularView`

### Fast travel

`BlockFastTravel`, `BlockFastTravelQuest`

### Carrying a body

`BodyCarryingGeneric`, `BodyCarryingFriendly`, `BodyCarryingNoDrop`,
`BodyCarryingForceDrop`, `BodyCarryingCanSprint`, `BodyCarryingWoundedSoldier`,
`BodyCarryingActionRestriction`, `BodyCarryingBodyMasterPerk5`

### Set pieces and modes

`Braindance`, `Cyberspace`, `MetroRide`, `InDaClub`, `SpaceShuttleInterior`,
`FastForward`, `FastForwardCrouchLock`, `FastForwardHintActive`,
`AllowTracingInTier2`, `AllowTracingInTier3`, `AllowTracingInTier4`,
`AllowTracingInTier5`

## Which ones vanilla drives from script

39 of the 100 are named as string literals in `final.redscripts`, which means
the base game applies them from a script the mod can read and follow:

`BlockAllHubMenu`, `BlockAllMenu`, `BlockDeviceInteractions`, `BlockFastTravel`,
`BodyCarryingActionRestriction`, `BodyCarryingBodyMasterPerk5`,
`BodyCarryingCanSprint`, `BodyCarryingFriendly`, `BodyCarryingGeneric`,
`BodyCarryingNoDrop`, `BodyCarryingWoundedSoldier`, `Braindance`,
`DriverCombatBikeWeapons`, `DriverCombatFirearms`, `FastForward`,
`FastForwardCrouchLock`, `FastForwardHintActive`, `Firearms`,
`FirearmsNoUnequipNoSwitch`, `FistFight`, `FocusModeLocomotion`, `ForceCrouch`,
`InfiniteAmmo`, `NoCameraControl`, `NoJump`, `NoMovement`, `NoRadialMenus`,
`NoScanning`, `NoWeapons`, `NoWorldInteractions`, `PhoneCall`,
`PhoneCallDeviceActionRestrictions`, `SecurityLocker`, `Tier2Locomotion`,
`Tier2LocomotionFast`, `Tier2LocomotionSlow`, `VehicleCombat`,
`VehicleCombatNoInterruptions`, `VehicleNoInteraction`

The other 61, `NoDriving` and `VehicleNoSummoning` among them, are applied from
quest graphs instead. That is not a warning about them. It means the way to
learn what one does is to apply it, because there is no script to read.

## How to measure one

Four questions, and only the first is about the control itself:

1. **What does it stop?** Apply it, then try the control.
2. **Is it `savable`?** Apply it, save, quit to desktop, load, then list the
   player's active effects. Anything still there is savable, and savable is what
   turns a forgotten lock into a permanent one.
3. **What does the player see?** A refusal message from the base game reads as
   the game saying no. A prompt that is silently absent reads as a broken mod.
   This decides whether a restriction is usable in shipped content at all.
4. **Does it interact with anything already applied?** `maxStacks` and
   `immunityStats` are real fields, so a restriction applied twice or applied
   over a base-game one is worth checking rather than assuming.

Gig 01's CET dev menu carries a worked example under "Vehicle lock lab", which
applies three vehicle restrictions, lists every active effect, and has a button
that clears everything it can apply. Copy the shape for any other area.

## Reproducing the list

`tweakdb.bin` holds no plain strings, which is why `BUILDING.md` says TweakDB
ids are not reliably discoverable from files on disk. That is true of the game's
own files and not of the whole machine: Cyber Engine Tweaks ships its own string
table, and the game ships the decompressor for it.

- The table is `tweakdbstr.kark` in CET's `tweakdb` folder.
- The format is the four bytes `KARK`, then the uncompressed size as a
  little-endian `uint32`, then Kraken-compressed data.
- `oo2ext_7_win64.dll`, in the game's `bin` folder, decompresses it through
  `OodleLZ_Decompress`.

Around 187 MB of text comes out, holding every TweakDB record id and every flat
name. Grepping it for `^GameplayRestriction\.[A-Za-z0-9_]+$` produces this list.
The same route answers any other "what is this record called" question without
starting the game.

It gives names only. Values stay hashed, so what a record *does* still has to be
measured in game.

## Related

- `docs/gotchas.md` 21, a one-way flag exercised only in the clean direction
- `docs/backlog.md` 16, the open item this vocabulary was extracted for
- `Gig01_Holocall.reds`, `ApplyLock`, the reload-safe guard to copy
