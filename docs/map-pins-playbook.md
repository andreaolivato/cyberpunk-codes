# Map pins playbook (game 2.31 + Phantom Liberty)

How to give a mod-added quest a real map pin. Established by experiment on
2026-08-11. Follow it exactly and pins work first time.

Background and dead ends: `architecture.md`. A worked example of how every
layer below looks broken when the pin entry is never activated:
`docs/axl-mappin-bug-report.md`, a withdrawn bug report kept as a caution.

## The three ingredients

All three must be true. There were four until 2026-08-14; the fourth was
patching the game's cooked mappin tables, and ArchiveXL does that itself. See
`architecture.md`, "The cooked tables are NOT needed".

### 1. The pin entry exists in your journal file

- `gameJournalQuestMapPin` as a child of the objective, at
  `quests/street_stories/<quest>/<phase>/<objective>/<pin_id>`
- `gameJournalPointOfInterestMappin` under
  `points_of_interest/street_stories/<quest>`, for the gig icon
- the quest needs `"type": "StreetStory"` or it presents as a main quest
- pin `mappinData`: `mappinType = Mappins.QuestStaticMappinDefinition`,
  `variant = QuestGiverVariant`, `active = 1`, `visibleThroughWalls = 1`

### 2. The quest phase activates the pin entry

This is the most commonly missed step.

Activating quest, phase and objective is not enough. Pin entries are journal
entries with their own state, and an Inactive pin is invisible: the engine never
queries the mappin system for it.

In `tools/gen_questphase.py`, call `add_journal('gameJournalQuestMapPin', ...)`
alongside the objective, and `add_journal('gameJournalPointOfInterestMappin',
POI, ...)` when the gig starts.

Activation is irreversible. Activating registers the pin; setting it back to Inactive
does not take the marker off the map. See "A pin cannot be un-shown" below.

### 3. The pin references a base-game node in an always-loaded sector

The `offset` is the exact vector from that node to the target.

- `reference.reference` on a quest pin, `staticNodeRef` on the POI
- two tables in `tools/gen_journal.py`: `ANCHOR_POS` (each anchor's world
  position) and `PIN_POS` (where the pin must end up)
- the generator subtracts them, so the anchor's distance from the target does
  not matter. Only its recorded position has to be right
- find one with `python tools/find_pin_anchors.py <x> <y> <z>`, which prints the
  name and the position to paste in

## The anchor must never unload

ArchiveXL computes the position as `GetNodeTransform(anchor) + offset`, and
`GetNodeTransform` needs the node to exist as an instance. Its streaming sector
must be loaded.

A quest activates its pins while V is on the far side of the city. So an anchor
that only streams in when you are nearby cannot place a pin you have not already
walked to.

Night City has exactly three sectors the engine never unloads:
`always_loaded_0/1/2.streamingsector`, `category: AlwaysLoaded`, float-max
streaming box. They hold 5211 globally-named nodes between them. Those are the
only safe anchors. Every pin in gig 01 found one within 53 m.

Confirmed in game 2026-08-14, all nine pins plus the POI:

```
[Journal] Cooked mappin #1684563311 (.../obj_office/pin_office) resolved to NodeRef #16197545746536188403.
```

## Three routes that fail

All tried in game on 2026-08-14. The log line tells the three apart.

| What you shipped | Log | Why |
|---|---|---|
| anchor in an ordinary `exterior_*` sector | `Can't resolve ... position` | name resolved, node not streamed in |
| no NodeRef, world coords in `offset` | *(no line at all)* | a quest pin with no reference is never spawned as a mappin, so nothing is asked for |
| a marker node you ship yourself | `Can't resolve ... reference` | a node in a mod sector never registers its global name |

`position` means the name resolved and the node was not there. `reference` means
the name meant nothing.

Shipping your own marker nodes is the tempting one, and it does not work.
Californication and OneMoreLight both do it, and playtesting confirmed their pins
are broken in game too, so they were never the precedent they looked like. This
repo's original note said custom marker nodes do not resolve. It was overturned
once on an unverified assumption and cost three test sessions.

Corollary for the corpus habit: counting uses in shipped mods is evidence only
if their case is your case, and only if the thing you are copying actually
works. Check both.

## Reading the log

ArchiveXL hooks `GetMappinData` and `GetPoiData` and builds the cooked entry when
the base tables miss. Nothing is patched into the game's own files. It logs what
it did for every pin, by name, into
`red4ext\plugins\ArchiveXL\ArchiveXL.log`:

```
[Journal] Cooked mappin #<hash> (<journal path>) requested...
[Journal] Cooked mappin #<hash> (<journal path>) resolved to NodeRef #<h>
[Journal] Cooked mappin #<hash> (<journal path>) resolved to static offset.
[Journal] Can't resolve mappin #<hash> (<path>) reference.      <- no pin
[Journal] Can't resolve mappin #<hash> (<path>) position.       <- no pin
```

Read that log before theorising about a missing pin.

A healthy pin logs `resolved to NodeRef #<hash>`. Anything else is a bug. No
`requested` line at all for a hash means either the base lookup answered it
(something is still shipping cooked tables) or the entry was never collected.

## A pin that must not draw a route: `enableGPS`

`enableGPS` is a per-pin field on `gameJournalQuestMapPin`. Set it to 0 and the
marker stays put while the GPS stops drawing a road route to it.

Use it for any objective the player cannot drive to: a roof, a ledge, a climb,
somewhere inside a property. The route solver snaps to the nearest road, so for
a target above or behind an obstacle it draws directions to the wrong side of
it, which is worse than no directions. Gig 01's way-in pin sits on a rock you
climb over, and was routing the player along a road below the house (playtest,
2026-08-13).

This is vanilla's own answer. Of all 4277 quest map pins in the shipped journal,
4145 have `enableGPS` 1 and 131 have 0. The zeros are objectives you are already
at or cannot drive to: `q005_heist/hide`, `wait_jackie_in_elevator`,
`sq030_judy_romance/lake/exploration`, `explore_church_entrance`, the tutorial's
tag-the-guard markers, and every race, where a road route would fight the track.

Only two street-story pins in the whole game turn it off, and both are on
`sts_cct_dtn_04`'s `clear_out_roof`: one `NPCVariant` pin and one
`QuestGiverVariant`, the same variant gig 01 uses. CDPR hit this once, in a gig,
and solved it with the flag rather than by moving the marker.

There is no pedestrian-routing variant to switch to. `gamedataMappinVariant`
changes the icon, not the router. The choice is route or no route.

## A pin cannot be un-shown

Measured in game on 2026-08-15, twice, with screenshots.

`obj_wayin` was authored with six `gameJournalQuestMapPin` children, one per
waypoint up a hillside, and `Gig01_Encounter` called

```reds
jm.ChangeEntryState(path, "gameJournalQuestMapPin",
                    gameJournalEntryState.Inactive, JournalNotifyOption.DoNotNotify);
```

on the five that should be hidden. All six stayed on screen, at
150/150/125/90/70/30 m.

The call is not in doubt. It is the same one the quest graph's journal node
makes, against the same path the graph activates with, and the activating half
demonstrably works.

So the honest statement of ingredient 2 is: the pin entry's state gets the pin
REGISTERED, and the parent objective being Active is what makes it RENDER. There
is no route back through the journal.

Vanilla never tries. Of the shipped objectives, 2673 carry one pin, 288 carry
two, and the tail runs to 28. The multi-pin ones are exactly the case you would
want to sequence: `q104_02_av_chase/finding_courier/follow_tracks` is six
waypoints down a road, `q202_nomads/temp_river/cross_border` is seven across a
river. CDPR shows them all at once.

If a design needs one marker at a time, the journal is the wrong tool. Read the
next section rather than looking for the flag.

### The tool that does work: register your own mappin

```reds
let ms: ref<MappinSystem> = GameInstance.GetMappinSystem(game);
let data: MappinData;                       // NOT gamemappinsMappinData
data.mappinType = t"Mappins.QuestStaticMappinDefinition";
data.variant = gamedataMappinVariant.QuestGiverVariant;
data.visibleThroughWalls = true;
let id: NewMappinID = ms.RegisterMappin(data, worldPosition);
ms.SetMappinPosition(id, somewhereElse);
ms.UnregisterMappin(id);
```

Four things that matter, all of them paid for:

- **`MappinData`, not `gamemappinsMappinData`.** The journal resource spells it
  the long way; redscript does not know that name and says `unresolved type`.
  The script struct has five fields, `mappinType`, `variant`, `debugCaption`,
  `visibleThroughWalls`, `scriptData`, and no `active`.
- **It takes a world position.** No NodeRef, no anchor, no offset, so the
  always-loaded-sector problem does not arise. This is the only way to put a
  marker where the game ships no node.
- **`SetMappinPosition` moves it**, so a route is one mappin, not N.
- **Nothing else removes it.** It is not a journal entry, so no
  objective completing and no quest ending takes it down. Unregister it on every
  exit path, including "the gig is no longer running", or it sits on the
  player's map for the rest of the save.

Costs, so the trade is made with open eyes:

- the objective loses its journal distance readout, since it no longer owns a pin
- the marker carries no localized caption, only a debug one
- whether a registered mappin survives a save and load is unverified. If it
  does, a reload re-registers and you get a duplicate

If that duplicate turns up, there are two ways out. Persist the id, so a reload
can unregister the one it inherited before registering a new one. Or sweep with
Codeware's `MappinSystem.GetAllMappins` and remove the strays. The first is
better, because it does not have to guess which markers are yours.

Note the shape, which is gotcha 21: the id is a script field and does not survive
a load, while the marker it refers to might.

## A forced GPS route: the mechanism exists and a mod cannot use it

Asked in playtest on 2026-08-15: *"study if possible to provide a specific path
for the GPS instead of using the auto GPS"*. The answer is "yes, and not usable here",
recorded here so it does not get re-researched.

The class is `gameJournalQuestGuidanceMarker`, and it is a child of the map pin.
Not of the objective, and not of the quest. Found by grepping the shipped
`cooked_journal.journal` for `waypoint`, which turns up `gps_waypoint_01/02/03`
under `mq018_writer`:

```json
{ "$type": "gameJournalQuestGuidanceMarker",
  "id": "gps_waypoint_01",
  "isPortal": 0,
  "nodeRef": "#mq018_mp_gps_amustement_01",
  "pathfindingType": "Auto" }
```

The whole corpus is 44 markers under 18 pins. `pathfindingType` is `Navmesh`
(23) or `Auto` (21); `isPortal` is 1 on four. They chain, 1 to 4 per pin, in
order, and CDPR uses them where the router would otherwise embarrass itself: the
Dollhouse exit, the Lair escape, the Atlantis staircase, Rogue's back rooms.

**Why we cannot use it: the record has no offset.** It is a bare `nodeRef`, so a
waypoint lands exactly on a node the game already ships. Our pins get their
position from `ANCHOR_POS + offset`, which is what makes a distant anchor
harmless. A guidance marker has no such escape.

So it needs real base-game nodes at the waypoints, and a North Oak hillside has
none. Measured with `find_pin_anchors.py` for gig 01's six way-in points:

| Waypoint | Nearest always-loaded node |
|---|---|
| inside the gate | 20 m |
| the other five | 52-75 m |

A route drawn through points 50-75 m off is worse than no route, and shipping
our own marker nodes provably does not resolve.

So the chain of pins is the path. One pin active at a time, advanced by script as
the player reaches each: `Gig01_Encounter.ShowWayInMarker`. It is not a route
line on the minimap, but it is the nearest thing a mod can build.

Two things to re-check before concluding otherwise on a future gig:

1. **Does the target sit near base-game nodes?** Interiors and quest areas are
   dense with them; a hillside is not. Run `find_pin_anchors.py` on the actual
   waypoints first. Two-minute answer.
2. **`gamedataMappinVariant.GPSForcedPathVariant` is a dead end.** The enum
   member exists, it is named exactly right, and zero of the 4277 shipped quest
   pins use it (checked in the journal's own name table). That is gotcha 17 to
   the letter, and the same shape as `gameEntityReferenceType.Tag`, which
   crash-killed the game.

Reproducing the survey (nothing is committed, this is cache):

```powershell
$WK = "$env:LOCALAPPDATA\Programs\WolvenKit.CLI\WolvenKit.CLI.exe"
& $WK unbundle "<game>\archive\pc\content\basegame_4_gamedata.archive" -o . -r ".*\.journal$"
& $WK convert serialize ".\base\journal\cooked_journal.journal" -o .\out
```

One file comes out, `base\journal\cooked_journal.journal` at 4.8 MB, and
serializes to about 71 MB of JSON. That is the whole game's journal, and the
answer to most "what does vanilla actually do here?" questions about journal
data.

In this repo: `NO_GPS` in `tools/gen_journal.py`, currently `{'pin_wayin'}`.

## Adding a pin to a new gig

1. Author the pin and POI entries in the gig's journal JSON.
2. Add the activation steps to that gig's quest-phase generator.
3. `python tools/find_pin_anchors.py <x> <y> <z>`, then paste the anchor's name
   and position into `ANCHOR_POS`.
4. Put the target's world coordinates in `PIN_POS`. The generator computes the
   offset.
5. `tools/build-archive.ps1`, `tools/deploy-dev.ps1`, restart the game.
6. Check `ArchiveXL.log` for one `resolved to NodeRef` line per pin.

The mod ships no base-game files. If `source/wkit/raw/base/` ever reappears,
something has gone wrong. That directory is what this approach removed.

## Verifying in game

CET dev menu, **FULL PIN DIAGNOSIS**, dumps in one click: every entry's
existence, state and hash, the objective's `distanceToNearestMappin`, its cooked
positions, the same for a tracked base-game quest as a control, and the player's
distance to target.

`distanceToNearestMappin = -1` means the engine has no mappin. Check ingredient
2 or 3 first, and read `ArchiveXL.log`.

**`cookedMultiData` is a red herring.** The retired `patch_cooked_mappins.py`
also wrote that per-objective table, and when the journal distance went missing
it looked like the cause. It was not. The entire game has five `cookedMultiData`
entries, three of them 98-position collect-the-graffiti objectives, and all 73
vanilla street stories show distance and directions without one. Distance and
routing come from the per-pin `cookedData`, which ArchiveXL supplies. Confirmed
in game 2026-08-14: km and GPS directions both work with no multi-data at all.
