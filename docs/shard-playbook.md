# Shards: a readable object in the world, with Take and Read

How to put a shard on a desk that the player can see, walk up to, pick up with
[F] or read in place with [R], which carries your own title and your own text,
and whose reading your quest can wait on.

All of it is measured in game. Several of the field names are misleading, and
every one of those is called out where it matters.

Read `computer-ui-playbook.md` first if you have not decided between a shard
and a computer document. They are different objects and the choice is a
narrative one.

## A shard is four separate things

They are independent, they fail independently, and three of the four are
invisible when they are wrong.

| | what it is | where it lives |
|---|---|---|
| the TEXT | a journal onscreen entry | your `.journal` |
| the ITEM | a TweakDB record | your `.yaml` |
| the OBJECT | a named node in your own streaming sector | your `.streamingsector` |
| the READ | a journal state your quest waits on | your redscript |

A shard that renders but offers nothing is the OBJECT half done. A shard that
offers a prompt but shows somebody else's title is the ITEM half done. Both
look identical to "it does not work".

## 1. The text: a journal entry

**A shard's text is a JOURNAL ENTRY, not an item and not a file.** Copy a
shipped street story's shape. The folder types matter and are not all the same
class:

```
onscreens                     gameJournalPrimaryFolderEntry
  emails                      gameJournalFolderEntry
    quests                    gameJournalFolderEntry
      street_stories          gameJournalFolderEntry
        <quest id>            gameJournalFolderEntry
          onscreens           gameJournalOnscreenGroup     <- the leaf group
            <shard id>        gameJournalOnscreen          <- title/description
```

`title` and `description` are LocKeys, bare keys with no `LocKey#` prefix
(gotcha 1). `iconID` 0, `tag` `None`. The tags in the shipped data (`world`,
`notes`, `articles`) belong to the generic collectible shards under
`onscreens/emails/generic/shards`; quest shards do not use them.

Real newlines are the line breaks. `GetTitle()` and `GetDescription()` return
finished display strings, so nothing is localized by hand.

**The title of this entry is what the player sees on the object**, in the loot
line under the crosshair and on the scanner panel. See part 2.

## 2. The item: one record, and one property that is not the obvious one

```yaml
ObjectAction.my_shard_read:
  $base: Items.generic_hanako_flowers_shard_inline0
  journalEntry: onscreens/emails/quests/street_stories/<quest>/onscreens/<shard id>

Items.my_shard:
  $base: Items.Shard1
  displayName: my-shard-item
  localizedDescription: my-shard-item-desc
  itemSecondaryAction: ObjectAction.my_shard_read
```

**`itemSecondaryAction` is the line the whole thing hangs off.** It names an
ObjectAction record whose `journalEntry` flat is the path from part 1. All 335
shards in the game are built this way.

Three things about that, none of which is guessable from the field names:

- **The title on screen is the JOURNAL ENTRY's title, not the item's name.**
  In both places it appears. The vanilla shard's `DisplayName` accessor returns
  nothing at all and it still shows a title.
- **`objectActions` is a different property and it is not this one.** The
  vanilla shard's is `[ItemAction.Drop, ItemAction.Disassemble]`, with no read
  action in it. Overriding it does nothing useful and silently costs the player
  Disassemble.
- **`localizedName` is empty on the vanilla shard.** Setting it changes
  nothing.

**Base it on `Items.Shard1`, the game's plain shard.** It carries exactly what
is needed: `displayName`, `localizedDescription`, `itemType`, `quality`,
`itemSecondaryAction`. Cloning a shard that already has a story attached, such
as `Items.generic_hanako_flowers_shard`, inherits every inline child the base
had, and those children keep pointing at the base's content. That produces a
record which applies in full and still shows somebody else's shard.

`displayName` and `localizedDescription` still matter: they are the inventory
name and the flavour line under the scanner title.

## 3. The object: a NAMED node in your own sector

```
worldEntityNode
  entityTemplate   base\gameplay\loot\shard_cases\shard_case_container.ent
  appearanceName   shard_case_container_kitsch_c
  instanceData     the whole ShardCaseContainer chunk, itemTDBID = Items.my_shard

nodeData
  Position           where it stands
  QuestPrefabRefHash $/03_night_city/#c_<district>/<area>/#my_shard_container
  Uk10 1056, Uk11 10762, UkFloat1 50
```

and the same NodeRef again in the sector's own `nodeRefs`.

### The two things that are not optional

**NAME THE NODE.** `QuestPrefabRefHash` as a full `$/03_night_city/...` path,
repeated in `nodeRefs`. This is not decoration and it is not only about
addressing the node later:

> **An unnamed node in a mod sector does not load at all.**

Measured against a deliberate control: eight named objects were found in the
world and three unnamed ones were absent, standing four metres apart in the
same row. Every vanilla node that carries gameplay state is named, and no
purely visual one is: 118 of 118 entity nodes, 8 of 8 device nodes, 150 of 150
smart objects, 0 of 279 static meshes.

A short-form name (`#my_shard`) is enough to make the node LOAD, but only the
long form RESOLVES against the NodeRef registry, so write the long form.

**LIFT THE INSTANCE DATA WHOLE.** All 53 fields of a shipped container's
`ShardCaseContainer` chunk, copied mechanically from a vanilla sector rather
than retyped. A node without it renders an oversized flat grey slab and offers
nothing, because the container's defaults are not a container.

Two habits that follow. Read the source sector off disk in your generator and
copy the chunk in code, because a copy made by hand is not a copy. And give
every lifted `HandleId` a fresh, file-unique value, since handle ids resolve
within the file.

### What turned out NOT to matter

Each was varied on its own against an otherwise identical object, and none
made any difference:
`appearanceName` (a node with none still draws and still prompts),
`sourcePrefabHash`, `Pivot`, the vanilla `MaxStreamingDistance`, the sector's
`level` (0 and 1 both work), the container's `useAreaLoot` flag, and writing a
name into the container's own `displayName` instance field.

### Removing the original, if you are replacing one

ArchiveXL can delete and mutate nodes in a shipped sector but cannot ADD to
one, so your own sector is the only place a new node can go. To take the
original out:

```yaml
streaming:
  sectors:
    - path: base\worlds\03_night_city\_compiled\default\<sector>.streamingsector
      expectedNodes: 1242
      nodeDeletions:
        - index: 591
          type: worldEntityNode
```

**Both numbers count INSTANCES, not nodes** (gotcha 47). A sector has a `nodes`
table of distinct things and a `nodeData` table of placements; they are not the
same length. Getting it wrong is refused cleanly and logged to
`red4ext\plugins\ArchiveXL\ArchiveXL.log`, but the line is written when the
sector STREAMS IN, not at startup, so it does not appear until the player is
near the place being patched.

### Routes that do not work, so you do not spend a day on them

- **`DynamicEntitySystem.CreateEntity` + `templatePath`.** The entity attaches,
  script callbacks fire, a prompt can be published, and the mesh never renders.
  It is an NPC and device spawner, not a prop placer.
- **`exEntitySpawner.Spawn`.** What other mods place props with, and a Codeware
  native registered for CET Lua only. From redscript it is
  `unresolved reference`. If your mod is Lua, use it.
- **A bespoke `.ent` of your own with a scripted interaction.** A mod `.ent`
  may only name an entity class the game already ships, and a hand built
  interactable does not raise a loot prompt. Use the game's container.

## 4. Knowing when it has been read

**`IsEntryVisited` and the entry going `Active` are both true when the popup
OPENS, not when it closes.** A quest step waiting on either resumes while the
shard is still on screen, under a modal popup that pauses the game and hides
subtitles, so the next lines are spoken into nothing.

There are two ways a shard gets read and you need both.

**Read in place with [R].** `PopupsManager.OnShardReadClosed` fires. Wrap it,
and gate it on a fact of your own, because it fires for every shard the player
ever reads:

```reds
@wrapMethod(PopupsManager)
protected cb func OnShardReadClosed(data: ref<inkGameNotificationData>) -> Bool {
    let result: Bool = wrappedMethod(data);
    // gate on your own "the beat has started" fact
    return result;
}
```

**Taken with [F] and read from the backpack, or from the Shards list.** That
callback DOES NOT FIRE. It only covers the reader raised at the container,
and the result is indistinguishable from a permanent stall.

Ask the journal instead, which does not care where the reader came from:

```reds
let entry = jm.GetEntryByString(path, "gameJournalOnscreen");
return jm.IsEntryVisited(entry);
```

then let **two ticks** pass before acting on it. The popup pauses the game
(`PauseGameState`), so DelaySystem ticks do not advance while it is up, and
counting two of them cannot happen until the reader has actually been shut.
That converts the open signal into a close signal without another callback.

**Visited, not `Active`.** An entry goes `Active` when the shard is merely
PICKED UP, so a state check completes your objective for a player who took it
and read nothing.

## Two objectives, not one

If the object has both Take and Read on it, the player can walk away holding an
unread shard. One objective cannot describe both halves:

- **"Search the desks"** until the shard is found, on a proximity check.
- **"Read the shard"** from then until it has been read, with no map pin,
  because the shard may now be in the backpack and a marker on an empty desk
  points at nothing.

Keep an anti-stall behind it, and make it LONG. It exists for the shard being
dropped or disassembled, both of which are one click away and leave nothing to
read. A short one changes the objective while the player is still walking to
their backpack, which defeats the split.

## Checklist

- [ ] journal entry authored, folder classes right, bare LocKeys
- [ ] `Items.<id>` on `Items.Shard1`, not on a shard with a story
- [ ] `itemSecondaryAction` points at YOUR action record
- [ ] that record's `journalEntry` is your onscreen path
- [ ] node `QuestPrefabRefHash` is a full `$/...` path
- [ ] the same string is in the sector's `nodeRefs`
- [ ] instance data lifted whole, `itemTDBID` set to your item
- [ ] HandleIds renumbered to be unique in the file
- [ ] `version: 62` on the sector
- [ ] the streaming block's box covers the point
- [ ] read detected BOTH ways, and gated on your own fact
- [ ] the original node deleted, with INSTANCE counts

## When it does not work

| symptom | cause |
|---|---|
| nothing at the spot at all | the node has no name |
| an oversized flat grey slab, no prompt | no instance data |
| renders, prompt works, wrong title | `itemSecondaryAction` still points at the base item's |
| two shards on the desk | the sector patch was refused; check the ArchiveXL log for INSTANCE counts |
| objective never completes after [F] | only the close callback is hooked; add the journal check |
| the next lines play under the popup | you waited on `Active` or on `IsEntryVisited` without the tick delay |

## Worked example

Gig 01's shard on the Arasaka office desk, end to end:

- text: `onscreens()` in `tools/gig01/gen_journal.py`
- item: `mods/gig-01-negative-balance/source/tweaks/shard.yaml`
- object: `tools/gig01/gen_sector.py`, which lifts the container off the vanilla
  sector and names it
- deletion of the original: the `streaming.sectors` block in
  `gig01_negative_balance.archive.xl`
- read detection: `CCG01Shard.HasBeenRead` and the `OnShardReadClosed` wrap in
  `Gig01_Shard.reds`, consumed by the shard beat in `Gig01_Encounter.reds`
- the two objectives: `tools/gig01/gen_questphase.py`

## Related

- `computer-ui-playbook.md`: the other way to put text on screen, and how to
  choose
- `docs/gotchas.md` 47 and 48: the ArchiveXL instance counts, and reading a
  record back as evidence
- `docs/backlog.md` 6: the whole history, including everything that failed
