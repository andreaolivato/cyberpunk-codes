# Computer / terminal UI playbook (game 2.31)

How to put mod content on a base-game computer's screen. Established
2026-08-11 while moving gig 01's office ledger off on-screen messages and onto
the real narrative computer. Everything here was read out of the decompiled
scripts, not guessed. An earlier attempt guessed `GetFiles`, `OnInstantiated`
and `OnActionEngineering`, none of which exist, and broke the script bundle.

Source of truth (https://codeberg.org/adamsmasher/cyberpunk):

| File | What it gives you |
|---|---|
| `cyberpunk/devices/masters/computerController.swift` | `ComputerControllerPS`, the data model + the `Request*` methods |
| `cyberpunk/devices/masters/computer.swift` | the `Computer` device: routes UI events to the PS |
| `cyberpunk/devices/UI/computer/computerGameController.swift` | `OpenDocument`, `ResolveQuestInfo` |
| `cyberpunk/devices/UI/computer/computerDocumentController.swift` | how title/content are rendered |
| `orphans.swift` | the structs: `ComputerSetup`, `GenericDataContent`, `DataElement`, `SDocumentAdress`, `QuestInfo` |

Fastest way to read them: `git clone --depth 1` the repo (29 MB) and grep. The
struct definitions all live in `orphans.swift`, not next to the classes.

## The data model

```
ComputerControllerPS
  m_computerSetup : ComputerSetup            // protected persistent
      m_filesStructure : [GenericDataContent] // persistent
      m_mailsStructure : [GenericDataContent] // persistent
      m_filesMenu / m_mailsMenu / ...         // persistent Bool, tab toggles
GenericDataContent   // native struct: name: String, content: [DataElement]
DataElement          // native struct, see persistence warning below
SDocumentAdress      // folderID / documentID, both DEFAULT TO -1, not 0
```

`ComputerControllerPS extends TerminalControllerPS extends MasterControllerPS
extends ScriptableDeviceComponentPS extends SharedGameplayPS`, so
`GetOwnerEntityWeak()`, `GetGameInstance()` and `GetID()` are all available.

A tab is only offered when its structure array is non-empty
(`GetMenuButtonWidgets`), and a `DataElement` is only listed when
`IsDataElementValid` passes: `isEnabled && (journalPath.IsValid() ||
IsStringValid(title))`.

## Where to hook

The UI never reads `m_computerSetup` directly. It queues events onto the
`Computer` entity, which forwards them to three non-final PS methods that
turn the setup into widget packages on the device blackboard:

- `RequestFileThumbnailWidgetsUpdate(blackboard)`: the file list
- `RequestMenuButtonWidgetsUpdate(blackboard)`: the tab buttons
- `RequestMainMenuButtonWidgetsUpdate(blackboard)`: the main-menu buttons

`@wrapMethod` those three, top the data up before calling `wrappedMethod`, and
your content appears whichever menu the player opens first. There is no need to
hook `LogicReady`, `GameAttached` or any UI class.

Identify *your* device by its owner's world position:

```reds
let owner: ref<GameObject> = this.GetOwnerEntityWeak() as GameObject;
Vector4.Distance(owner.GetWorldPosition(), TARGET) <= 6.0
```

Add helpers with `@addMethod(ComputerControllerPS)`: they compile into the
class, so `protected`/`private` members like `m_computerSetup` are reachable.

## Making "reading it" a quest trigger: no hook needed

`ComputerInkGameController.OpenDocument` ends with `ResolveQuestInfo`, which is
literally:

```
if IsNameValid(questInfo.factName) { AddFact(game, questInfo.factName, 1); }
```

So a `DataElement` with `questInfo.factName = n"your_fact"` sets the fact the
moment the player opens it. This is CDPR's own mechanism for
document-reading-advances-a-quest; do not write a hook for it.

**`AddFact` INCREMENTS, it does not set.** (`cyberpunk/global/vardDB.swift`:
`SetFact(name, GetFact(name) + count)`). Re-reading takes the fact to 2, 3, ...
so every consumer must test `> 0`, never `== 1`:

- quest phase: fine as-is, `gen_questphase.add_pause_fact` already emits
  `comparisonType: 'Greater'` against `0`.
- redscript: use `qs.GetFactStr(...) > 0`.

## The HUD is hidden while the screen is up

Entering a device screen pushes `UIGameContext.DeviceZoom`
(`deviceBase.swift:1352`), which takes the HUD with it, so
`SimpleScreenMessage` banners fired while the player is reading are invisible.
There is no query API for the active UI context on `UISystem`. **Use the player
state machine blackboard instead:**

```reds
GameInstance.GetBlackboardSystem(game)
    .GetLocalInstanced(player.GetEntityID(), GetAllBlackboardDefs().PlayerStateMachine)
    .GetBool(GetAllBlackboardDefs().PlayerStateMachine.IsUIZoomDevice)
```

`deviceBase.SetZoomBlackboardValues` drives that (plus `IsInteractingWithDevice`
and `UIZoomDeviceID`) for every device zoom, whichever way it is entered or left.

DO NOT try to detect the exit by wrapping `OnToggleZoomInteraction` and reading
`IsAdvancedInteractionModeOn()`. It looks right and it compiles, but closing a
computer screen does not route through that action, so it never fires, tested
2026-08-11. A quest step waiting on it appears to be a dead trigger.

For coloured banners, set `SimpleScreenMessage.type`:
`SimpleMessageType.Neutral` (blue), `Negative` (red), `Connection` (netrunner
styling), plus Police/Money/Relic/etc.

## The big HUD progress bar (CORRECTED 2026-08-12)

This section used to say **"there is no stock generic HUD progress BAR, the
only one is the quickhack upload bar, bound to `UploadProgramProgressEvent` and
a target's `GameplayRoleComponent`"**, and recommended sequencing percentage
banners instead. That was wrong, and it cost two failed attempts before
playtesting identified the widget by description: "the same UI used when a netrunner
is tracking you".

There IS a stock generic bar. The wide one across the bottom with a percentage.
It is blackboard-driven, needs no entity, and is written exactly the way our
subtitles are:

```reds
let bb = GameInstance.GetBlackboardSystem(game).Get(GetAllBlackboardDefs().UI_HUDProgressBar);
let d  = GetAllBlackboardDefs().UI_HUDProgressBar;
bb.SetString(d.Header, "COPYING LEDGER", true);
bb.SetString(d.CompletedText, "COMPLETE", true);
bb.SetFloat(d.Progress, 0.0, true);
bb.SetBool(d.Active, true, true);
// ...then write Progress repeatedly (0.1 s steps) to fill it...
bb.SetFloat(d.Progress, 1.0, true);
bb.SetBool(d.Active, false, true);
```

Source: `UploadFromNPCToPlayerListener` (`rpgManager.swift:3699`) writes it;
`cyberpunk/UI/widgets/hud_progress_bar/HUD_progress_bar.swift` reads it.
Fields: `Header`, `BottomText`, `CompletedText`, `FailedText`, `Active`,
`Progress`, `ProgressBump`, `MessageType`.

**Two traps, both hit in practice:**

1. **It does not animate itself.** The widget draws whatever `Progress` holds,
   so a single write leaves a frozen bar. Something must keep writing, 0.1 s
   steps read as continuous.
2. **It plays a FAILED outro unless you finish above 96%.**
   `HUDProgressBarController.Outro` (`HUD_progress_bar.swift:379`):
   ```
   if valueSaved < 0.96 && GetFact("holofixer_on") == 0 -> "Quickhack_Outro_Failed"
   ```
   So the fill duration must match how long the beat actually runs, and it is
   worth writing `Progress = 1.0` immediately before `Active = false` so a
   timing drift cannot produce a spurious "FAILED".

**The other bar is a different widget, for a different job.**
`UploadProgramProgressEvent` → the target's `GameplayRoleComponent` is real, but
it is the small indicator that hangs on the ENTITY being hacked, not the
bottom-of-screen bar. If you want that one instead, note the `QuickHack`
context dereferences `evt.action.GetInteractionIcon()` unconditionally and
`ScriptableDeviceAction` is abstract, so only the `PhoneCall` context is safely
drivable from a mod.

## Text and localization

`ComputerDocumentWidgetController.Initialize` uses plain
`inkTextRef.SetText(...)`, not `SetLocalizedText`. Pass finished display
strings, so resolve our LocKeys in script:
`GetLocalizedTextByKey(n"cc-g01-file-title")`. Real newline characters are the
line breaks. Not the two-character `\n` escape.

## Persistence warning (the one real trap)

`m_filesStructure` is persistent, but inside `DataElement` **only `isEnabled`,
`wasRead` and `isEncrypted` are persistent**, `title`, `content`,
`documentName`, `owner` and `date` are not. A save/reload can therefore hand a
pushed element back blank, which means:

- a search by `documentName` misses it, and
- appending again grows the array by one folder on every load.

Mitigation used in `Gig01_OfficeComputer.reds`: search by `documentName` first;
failing that, if the last folder holds a single element that is `isEnabled`
but has no title and no `documentName`, rewrite that blank in place instead of
appending. A blank element is invisible to the vanilla UI anyway, so the repair
cannot clobber anything the player can see.

VERIFIED 2026-08-11 (playtest): after a save/reload the file does NOT duplicate.
So on 2.31 the engine does not hand back a half-restored element, and the repair
branch never fires in practice. It stays as a cheap guard, it cannot run unless
a blank actually appears, but it is not load-bearing, and nothing new should be
built on the assumption that these arrays half-persist.

The related trap that IS real: `questInfo` is not persistent either, so a
document whose quest trigger lives only in `questInfo.factName` can come back
inert after a reload and then opening the file fires nothing at all. Carry a
second trigger off `wasRead`, which IS persistent, see `CCG01PromoteRead` in
`Gig01_OfficeComputer.reds`.

## Worked example

`mods/gig-01-negative-balance/source/scripts/Gig01_OfficeComputer.reds`: ~150
lines, three wraps, no UI classes touched, no trigger hook.

---

# Shards (the OTHER way to put text on screen)

Established 2026-08-13 for gig 01's comic pp. 23-24. Read this before deciding
between a computer document and a shard. They are different objects and the
choice is a narrative one, not a technical one.

**A shard's text is a JOURNAL ENTRY, not an item and not a file.** That single
fact is what makes a custom shard cheap. `ReadAction.CompleteAction`
(`cyberpunk/items/actions/readAction.swift`) is the entire mechanism:

```
ChangeEntryState(path, "gameJournalOnscreen", gameJournalEntryState.Active, Notify);
entry = GetEntryByString(path, "gameJournalOnscreen") as JournalOnscreen;
evt = new NotifyShardRead();
evt.entry = entry; evt.title = entry.GetTitle();
evt.text = entry.GetDescription(); evt.m_imageId = entry.GetIconID();
GameInstance.GetUISystem(game).QueueEvent(evt);
```

`NotifyShardRead` is the reader overlay. Everything a "real" shard has that
this does not. A TweakDB item record, an `ItemSecondaryAction` carrying
`.journalEntry`, a loot container, a `ShardCaseContainer` on a desk, sits
*upstream* of that event. A mod can raise it directly and skip all of it.

What you still get by doing it this way rather than faking a popup: the entry
lands in the Shards list and stays re-readable, the read is persistent
(`PopupsManager.ShardRead` calls `SetEntryVisited`), and the quest can observe
it.

## Authoring the entry

Copy a shipped street story's shape. Gig 01 copied `sts_bls_ina_03`. Folder
types matter and are not all the same class:

```
onscreens                     gameJournalPrimaryFolderEntry
  emails                      gameJournalFolderEntry
    quests                    gameJournalFolderEntry
      street_stories          gameJournalFolderEntry
        <quest id>            gameJournalFolderEntry
          onscreens           gameJournalOnscreenGroup     <- the leaf group
            <shard id>        gameJournalOnscreen          <- title/description
```

`title` and `description` are LocKeys (bare keys, no `LocKey#`: gotcha 1),
`iconID` 0, `tag` `None`. The tags you see in the data (`world`, `notes`,
`articles`...) belong to the *generic collectible* shards under
`onscreens/emails/generic/shards`; quest shards do not use them.

`GetTitle()` / `GetDescription()` return finished display strings, the journal
resolves the LocKeys, so nothing is localized by hand. Real newlines are the
line breaks, same as the computer documents above.

## Knowing when it has been READ (the one real trap)

**The entry goes `Active`, and `IsEntryVisited` goes true, when the popup
OPENS.** Both are therefore useless as "the player has read it": a quest step
waiting on either resumes while the shard is still on screen, under a modal
popup that pauses the game and hides subtitles, so the next lines are spoken
into nothing.

The close signal is `PopupsManager.OnShardReadClosed`. Wrap it:

```reds
@wrapMethod(PopupsManager)
protected cb func OnShardReadClosed(data: ref<inkGameNotificationData>) -> Bool {
    let result: Bool = wrappedMethod(data);
    // ...gate on your own "we opened it" fact: this fires for EVERY shard the
    // player ever reads, including ones they picked up in the street.
    return result;
}
```

The popup pauses the game (`PauseGameState` → `SystemRequestsHandler.PauseGame`
+ `UIGameContext.ModalPopup`), so DelaySystem ticks do not advance while it is
up, which is what makes a tick-counted anti-stall safe: it cannot expire while
the player is still reading.

## Putting a PHYSICAL object in the world (three routes, two of them wrong)

Gig 01 needed a shard V could see on a desk and press F on. This took three
attempts, and the two failures are documented because other mods will hit them.

**1. `DynamicEntitySystem.CreateEntity` + `DynamicEntitySpec.templatePath` - 
HALF works, and the half that fails is silent.** The entity attaches, script
callbacks fire, an `InteractionComponent` publishes its choice and the prompt
appears, and the mesh never renders. Twice, with screenshots. That spec is
an NPC/device spawner; it is what this repo uses for Johnny and his workspot
device, both of which are invisible by design, so the gap had never shown.

Declaring the mesh in the template's `resolvedDependencies` (Flags `Soft`, the
way the shipped shard does) is *necessary*. An empty list means the resource is
never streamed, but it was not sufficient here.

**2. `exEntitySpawner.Spawn(path, transform)`: the one other mods use, and
redscript cannot see it.** CyberScript places every prop this way
(`mod/modules/housing.lua`, `npc.lua`), so it is proven, but it is a Codeware
native registered for CET Lua only. A redscript probe fails to compile with
`unresolved reference 'exEntitySpawner'`. If your mod is Lua, use it; if it is
redscript, it does not exist.

**3. A `worldEntityNode` in your own streaming sector, what the game does.**
`worldEntityNode` (template resref + `appearanceName`) plus a matching
`nodeData` entry carrying the position. Copy both shapes field-for-field from a
shipped sector; `tools/gig01/gen_sector.py` is a worked generator.

Two things to check before blaming the node:

- **`version: 62`** on the sector, not 0.
- **The streaming block's box must cover the point.** Gig 01's is infinite, so
  its sector is always resident, which is also why the "custom marker nodes do
  not resolve" finding in `map-pins-playbook.md` is about NodeRef *resolution*
  and not about streaming. The sector loads fine; it is only useless as a pin
  anchor.

The object is then in the world from load, not from the quest step. For a prop
that belongs in the room anyway that is the right trade; gate the *behaviour* on
a fact instead.

## Worked example

`mods/gig-01-negative-balance/source/scripts/Gig01_Shard.reds` (one wrap for the
journal takeover, one for the object's press) plus `onscreens()` in
`tools/gig01/gen_journal.py`, the entity in `tools/gig01/gen_shard_ent.py`, its placement in
`tools/gig01/gen_sector.py`, and the three-fact handshake in `tools/gig01/gen_questphase.py`.
