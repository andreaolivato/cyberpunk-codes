# NCR Quest & Voice Slots: guide for quest modders

NCR Quest & Voice Slots is a shared base for quest mods on console and on
the mod.io version of the game. It does two things for a quest mod:

- its quest starts on the first load after the mod is installed, wherever V
  is;
- its characters speak with the mod's own recordings, in every dubbed
  language.

This guide is for game 2.5.

Does your quest also need a shaded area on the minimap, for an objective like
"Leave the area"? That is the other shared base, NCR Map Areas. Its guide is
[ncr-map-areas.md](ncr-map-areas.md).

## Why a shared base

On console a mod can't add to a base-game file. It can only replace it.
When two mods replace the same file, only one copy is used, and the other
mod stops working.

A quest mod needs two base-game files:

- a quest that runs in every save, to start the mod's own quest from;
- the game's index of voice maps, to find the mod's recordings.

This package replaces both files once. Quest mods plug into it and replace
neither.

Most quest mods should use Deceptious Quest Core instead. Its quests start
at V's apartment, which suits most quests. Use this package if your quest
has to start wherever V is, or if your characters have recorded voices.
The two packages replace different files, so a player can install both.

## Slots

The package has 200 numbered slots, `slot_001` to `slot_200`. A slot is a
set of names that the package waits for. Your mod ships files under those
names, and the package finds them.

For slot 17:

| What | Name |
|---|---|
| your quest | `mod\ncr_slots\quest\slot_017.questphase` |
| the claim object | `$/03_night_city/#ncr_slots/#ncr_slot_017` |
| the claim fact | `ncr_slot_017` |
| your voice map, one per language | `mod\ncr_slots\vo\slot_017_<language>.json` |

Slot numbers are always three digits.

## Step 1: take a slot

1. Open the slot list (`ncr-slot-registry.md`).
2. Pick a free number.
3. Add a line with your mod's name and your name, and send it in.

Take the slot before you release. Two mods on the same slot break each
other.

## Step 2: ship your quest under the slot's name

Your quest phase goes at `mod\ncr_slots\quest\slot_017.questphase`.

It is the phase you would otherwise start from a base-game quest. The
package plays it once, on the first load where your mod is installed and
claimed. It keeps running in the save like any quest phase.

Your phase decides when the story begins. It can start at once, or wait on
a fact, a place or a time of day. Gig 01 waits on its own fact, which its
script sets once the player has finished the right base-game quests.

## Step 3: claim the slot

The package opens a slot when either of these is true. Use one.

### Without scripts: the claim object

Ship one invisible object named after your slot, in a map file the game
loads everywhere. Where the object stands does not matter.

1. Write the two files with the tool in this repo:

   ```
   python tools/console/make_slot_claim.py 17 -o <your WolvenKit project's raw folder>
   ```

   It writes `mod\ncr_slots\claims\slot_017.streamingsector.json` and
   `slot_017.streamingblock.json`.

2. Convert them to game files with WolvenKit (`convert deserialize`), and
   pack them with your mod.

3. Name the block in your `.archive.xl`:

   ```yaml
   streaming:
     blocks:
       - mod\ncr_slots\claims\slot_017.streamingblock
   ```

If your mod already ships a block, add the sector's descriptor to your own
block instead. With the game's own loader, a mod with several blocks
crashed the game on PC 2.5.

How it works: the package's slot waits on the game's own
`questNodeLoadingCondition`, which asks whether a named world object is
loaded. The base game uses it in Kerry's quest to wait for his laptop. The
block loads your sector everywhere: category `AlwaysLoaded` and a streaming
box with no bounds. The object's name has to be the long form, starting
with `$/`. A short name like `#ncr_slot_017` does not register for an
object a mod ships.

### With a script: the claim fact

Set the fact `ncr_slot_017` to 1 each time a save loads. In the language of
the game's own script compiler:

```
@wrapMethod(PlayerPuppet)
event OnGameAttached() -> Bool {
    var result: Bool = OnGameAttached();
    GameInstance.GetQuestsSystem(this.GetGame()).SetFactStr("ncr_slot_017", 1);
    return result;
}
```

Compile it with REDmod's `validate-mod-scripts -compile`, as mod.io's guide
says for any script.

## Step 4: voices

Skip this step if your mod has no recorded voices of its own. Lines that
use the game's own recordings need nothing.

The package lists one voice map per slot for each of the 11 dubbed
languages: `de-de`, `en-us`, `es-es`, `fr-fr`, `it-it`, `jp-jp`, `kr-kr`,
`pl-pl`, `pt-br`, `ru-ru`, `zh-cn`.

1. Make your voice map the way you would for ArchiveXL's `vomaps`.
2. Ship a copy for each language at
   `mod\ncr_slots\vo\slot_017_<language>.json`.
3. Where you have no dub for a language, ship your en-us map under that
   language's name. A player in that language then hears your English
   recordings. Without the copy they hear nothing for those lines.

The console's loader ignores the `localization: vomaps:` key of an
`.archive.xl`. Your `subtitles` and `onscreens` keys still load as usual.

## Scripts: rules the console loader adds

These were measured with the game's own mod loader on PC 2.5. They hold for
any console mod, whether or not it uses this package.

- Never declare an engine class the game's scripts leave out, unless no
  other mod can declare it too. Two mods declaring one class make the
  loader refuse every mod's scripts.
- Never rely on a wrap of a method another mod may wrap. When two mods wrap
  the same method, only one of the wraps runs, and nothing reports it.
- To run code when a save loads, give your ScriptableSystem an
  `OnPlayerAttach` instead of wrapping `PlayerPuppet.OnGameAttached`:

  ```
  private export function OnPlayerAttach(request: PlayerAttachRequest) {
      var player: GameObject = request.owner;
      if( ( ( player ) != NULL ) ) {
          var game: GameInstance = player.GetGame();
          // your code; this game instance reaches the quest system
      }
  }
  ```

  A mod's ScriptableSystem receives it without being registered anywhere.
  Inside it, `this.GetGameInstance()` reaches no quest system; the player's
  `GetGame()` does.
- To know that the player read your shard, check the fact
  `ncr_shard_read:<title>`, with your shard entry's own `GetTitle()` as the
  title. This package wraps the shard popup and sets that fact for every
  read, so no quest mod needs a wrap of its own there. A read from a loot
  list leaves the journal's visited flag unset, so the flag alone misses it.

## Tweaks: a field a record does not declare

The base game hangs some values on its records as extra fields, for example
the `journalEntry` of a shard's read action. With the console loader, such a
field written inside a cloned record is dropped. Write it as its own line:

```yaml
ObjectAction.my_shard_read:
  $base: Items.generic_hanako_flowers_shard_inline0
ObjectAction.my_shard_read.journalEntry: onscreens/.../my_shard_note
```

## What your mod must not ship

- `base\quest\bugfixing\additional_content_bugfixing.questphase`
- `base\localization\volanguagedatamap.json`

Either one would replace the package's copy and break every mod in a slot.

## Your mod page

mod.io has no requirement system for Cyberpunk 2077 yet. Its own guide
says to name required mods in the description. Write that your mod needs
NCR Quest & Voice Slots, and link to it.

## How the package works

For anyone who wants to check it.

- The start: the package's copy of
  `additional_content_bugfixing.questphase` adds to it the way the game's
  own patches do. Every save ends that quest on its last wait, node 46.
  The package keeps the node's number and changes what it waits for:
  "the fact `ncr_slots_installed` is 0". On the first load it sets the
  fact, opens 200 waits, one per slot, and goes back to waiting on 46. A
  save remembers a quest by node number, so after an uninstall the save is
  on the game's own node 46 again, where the game's next patch expects it.
  Slot 17 waits for "the object is loaded, or the fact is set", then plays
  your quest phase.
- An empty slot never asks for a file that isn't there.
- The voices: the package's copy of `volanguagedatamap.json` adds 200
  entries per dubbed language, one per slot. An entry with no file behind
  it is skipped (measured on PC with the game's own loader).
- Measured on PC 2.5 with the game's own mod loader, the route mod.io gives
  for local tests: the game loads with all 2,200 voice entries, a slot opens
  on its object or its fact, an unclaimed slot stays shut, and a quest in
  slot 1 plays with its own voices. Uninstalled, a save made with the
  package loads, and an imitation patch that adds content after node 46
  runs in it. Reinstalled on that save, a slot still opens.

## Local testing

mod.io's local test route, measured on PC 2.5:

1. Put each mod in its own folder in `<game>\r6\c77\`, for example
   `<game>\r6\c77\NCRQuestVoiceSlots\` and `<game>\r6\c77\<YourMod>\`.
2. In each folder: `about.json`, the compiled `final.redscripts` and
   `final.redscripts.h64` if the mod has scripts, an `archive\` folder with
   the archive and its `.archive.xl` and `.archive.json`, and a `tweaks\`
   folder of `.json` tweaks.
3. Launch the game with `-LoadScriptMods`.

`-logScripts` writes `<game>\ScriptLogger.log`, which names each script mod
the loader read.
