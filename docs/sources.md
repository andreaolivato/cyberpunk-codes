# Where the knowledge comes from

**Check these BEFORE measuring anything.** This project has now twice spent a
session establishing something by playtest that was written down somewhere
public, and once built a bench that deviated from a working example for a reason
that turned out to be wrong. Reading first is cheaper than every alternative.

The order below is the order to try.

## 1. The REDmodding wiki

<https://wiki.redmodding.org/cyberpunk-2077-modding/>

The community's own documentation, and the most under-used source this project
has. It covers world editing, NPCs, communities, quests, scenes, animations and
the tooling, and it is maintained by the people who wrote the tools.

**Append `.md` to any page URL to get the verbatim markdown**, which is far more
useful than the rendered page. The full index is at
<https://wiki.redmodding.org/cyberpunk-2077-modding/llms.txt>.

Pages this project has used and should reread before touching the same ground:

| page | what it settles |
|---|---|
| `modding-guides/world-editing/ai-and-npcs/creating-communities` | the whole community workflow: entries, phases, time periods, markings, spot NodeRefs |
| `modding-guides/world-editing/ai-and-npcs/placing-aispot-nodes` | AI spots, supported rigs, `Is Infinite`, and that each spot NEEDS a unique NodeRef |
| `modding-guides/world-editing/object-spawner/exporting-from-object-spawner` | how a World Builder group becomes sectors and a streaming block |

**The wiki describes the UI, not the file format.** It tells you what a thing is
for and which tool does it; the byte-level answer comes from source 2 or 3.

## 2. The tools, which are open source and are the specification

When the wiki names a tool, read the tool. Its exporter is the authoritative
statement of what a working mod actually writes.

| tool | repo | what it answers |
|---|---|---|
| World Builder | `justarandomguyintheinternet/CP77_entSpawner` | what a node's fields are set to. `modules/classes/spawn/**` is one file per node type; `modules/ui/exportUI.lua` builds the always-loaded registry sector |
| the WolvenKit importer | `WolvenKit/Wolvenkit-Resources` | `Scripts/Internal/entSpawner/import_object_spawner.wscript`, which turns that export into sectors: NodeRefs, streaming values, bounds, the block |
| ArchiveXL | `psiberx/cp2077-archive-xl` | what the loader actually does. `src/App/Extensions/**` |
| Codeware | `psiberx/cp2077-codeware` | the native surface a mod can reach from script |

**A deviation from what these do needs evidence, not a rationale.** Backlog 29
shipped a community as the cooked node type in an always-loaded sector because
that shape had been read field by field in vanilla, and World Builder writes the
`_Streamable` type in an ordinary sector. Seven runs were spent before that
difference was noticed.

## 3. The game's own decompiled scripts

<https://codeberg.org/adamsmasher/cyberpunk>

Every scripted class and every native function signature the game exposes.
`orphans.swift` holds the natives. This is where
`GetGameObjectsFromSpawnerEntityID`, `CreateEntityReference` and the community
system's script surface were found.

Clone it once and grep it. It answers "can script even ask this" in seconds.

## 4. The shipped data

The game's own archives, read with WolvenKit's CLI. This is the most reliable
source and the slowest, and it is the right one for questions of the form "what
does a working example actually contain".

`BUILDING.md` has the extraction commands. `tools/_anchor_cache/` holds the
always-loaded sectors and is gitignored.

Two habits that paid off:

- **Check a rule by prediction.** The grid-cell formula was confirmed by
  predicting `exterior_2_8_1_1`'s value and finding it matched; the community id
  rule by predicting fabiola's `sourceObjectId` from her registered name.
- **Count across the whole corpus rather than reading one file.** "112 of 133
  uses write `None`" is worth more than one example, and it is what showed that
  ambient communities are activated by quest phases too.

## What NOT to treat as a source

- **Nexus mod pages and comments.** Useful for "someone has done this", useless
  for how.
- **This project's own older notes.** Three claims in `gotchas.md`,
  `architecture.md` and a generator header were confidently wrong and were
  corrected on 2026-08-23 and 24. Anything here that has not been measured says
  so; if it does not say so, check the section it came from.
