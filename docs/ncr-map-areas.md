# NCR Map Areas: guide for quest modders

NCR Map Areas draws quest areas on the minimap and the world map on console
and on the mod.io version of the game. An area is the shaded zone the game
shows for objectives like "Leave the area".

This guide is for game 2.5.

Does your quest also need to start anywhere, or speak with recorded voices?
That is the other shared base, NCR Quest & Voice Slots. Its guide is
[ncr-quest-voice-slots.md](ncr-quest-voice-slots.md).

## Why a shared base

On PC, ArchiveXL draws a quest pin's area from the trigger area the pin points
at. The game's own mod loader has nothing that does this. Without ArchiveXL,
the minimap reads area outlines from one base-game file only:

`base\worlds\03_night_city\_compiled\default\03_night_city.mappins`

On console a mod can't add to a base-game file. It can only replace it. When
two mods replace the same file, only one copy is used.

This package replaces that file once, with every registered area added. Quest
mods name the package as a requirement and never ship the file themselves.

The file stores each area's corners itself. It does not point to a file
another mod could supply. So an area can't be reserved and filled in later.
Your area goes into the package, and players get it with the next release.

## What your mod needs

The PC route, unchanged:

1. A `worldTriggerAreaNode` in an always-loaded sector of your mod, with the
   area's outline.
2. A quest map pin whose `reference` is that node, with a zero offset.
3. The pin's objective active and tracked.

The map pins playbook has the node's fields:
[map-pins-playbook.md](map-pins-playbook.md), "A quest area drawn on the
minimap".

The minimap draws the area while the objective is tracked and V stands
inside it.

## Step 1: send your area

Open an issue, or a pull request against `tools/console/map_areas.json`,
with one entry:

```json
{
  "mod": "Your Mod",
  "author": "you",
  "added": "2026-11-01",
  "pins": ["quests/minor_quest/your_quest/phase_main/obj_leave/pin_leave"],
  "position": [-391.5, 1265.2, 21.4],
  "height": 90.0,
  "outline": [[-20.0, -15.0], [25.0, -15.0], [25.0, 30.0], [-20.0, 30.0]]
}
```

- `pins`: the journal path of every pin that draws this area. A path is the
  ids from the journal's root down to the pin, joined with `/`.
- `position`: the trigger area node's world position.
- `height`: the outline's height in metres, above `position`.
- `outline`: the corners in X and Y, relative to `position`, in order around
  the shape.

## Step 2: name the package on your mod page

mod.io has no requirement system for Cyberpunk 2077 yet. Write that your mod
needs NCR Map Areas, and link to it.

## What your mod must not ship

`base\worlds\03_night_city\_compiled\default\03_night_city.mappins`

Your copy would replace the package's copy. Every other mod's areas would
disappear, and so would yours on the next game patch.

## Game patches

The file also holds the game's own pins. When a patch adds or moves them, the
package is rebuilt from the patched file. A player on an old copy keeps every
area but loses the positions of the patch's new pins until then.

## How the package works

For anyone who wants to check it.

- The package's file is the player's own table from Phantom Liberty, which
  also lists every base-game pin. One entry is added per pin in the registry.
- Each entry is filed under the hash of the pin's journal path: Murmur3, 32
  bit, seed `0x5EEDBA5E`. The build checks that no hash is already taken.
- `tools/console/build_areas.py` builds the package from the game files on
  the build machine, so nothing in it is typed by hand.

Measured on PC 2.5 with the game's own mod loader:

- The package loads from its own folder with no scripts in it.
- A pin listed in the table takes its position from the table.
- Dead Ringer's way out, a pin on a trigger area, is drawn as a shaded area.
- A pin on a plain marker with an entry in the table did not draw an area.
  Point your pin at the trigger area node.

## Local testing

The same route as NCR Quest & Voice Slots:

1. Put each mod in its own folder in `<game>\r6\c77\`, for example
   `<game>\r6\c77\NCRMapAreas\`.
2. The package's folder has `about.json` and an `archive\` folder with
   `ncr_map_areas.archive`.
3. Launch the game with `-LoadScriptMods`.
