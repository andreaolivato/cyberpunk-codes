# Orientation

The other docs assume you know what a questphase is. This one doesn't.

Skip it if you have shipped a quest mod before.

## What a gig is

A small side job. A fixer calls, a marker appears, you do the thing, the quest
log closes it. The base game ships hundreds.

A *street story* is the same shape with a different journal label. That is what
this project builds, because a mod cannot convincingly add itself to a fixer's
roster.

Making one means six subsystems agreeing with each other:

| Player sees | Subsystem |
|---|---|
| quest log, objectives ticking off | journal |
| map marker, distance, directions | map pins (also journal entries) |
| the mission advancing | quest phase, a node graph |
| characters talking, with choices | scenes |
| voices coming out of them | voiceover map |
| doors, terminals, NPCs reacting | redscript |

Most of the playbooks are about getting those six to agree.

## The tools

None are made by CD Projekt Red. All are community projects. The player installs
them; your mod declares which it needs.

| Tool | Does | Needed here for |
|---|---|---|
| RED4ext | loads native `.dll` plugins | the base the next three sit on |
| ArchiveXL | merges mod resources into the game's | loading our journal, quest phase, subtitles, voices, lipsync |
| TweakXL | adds records to the game database | our own NPC records |
| Codeware | extra scripting APIs | spawning NPCs at runtime |
| redscript | a language for the game's script system | gameplay logic |
| WolvenKit | converts resources to and from JSON, packs archives | the authoring pipeline |
| CET | Lua console and overlay | development only, never ships |

Merging matters more than it sounds. The old approach was to overwrite a
base-game file: one mod could do it, and a patch broke you. ArchiveXL merges, so
several mods can extend the same resource. This mod ships no base-game file at
all.

## How a gig gets built here

Four steps. Each one is a separate tool, and knowing which is which saves a lot
of confusion later.

**1. Python writes JSON.** One `.json` per resource, into
`source/wkit/raw/`.

That JSON is not a config file and not instructions. It is WolvenKit's **text
form of the game's binary format**, the way an `.svg` is a text form of a
picture. A `.questphase.json` is a quest phase, just readable.

**2. WolvenKit converts each JSON to its binary.** `.journal`, `.questphase`,
`.scene`, `.ent`. This is a format conversion, nothing more. WolvenKit does not
interpret or validate your logic.

**3. WolvenKit packs the binaries into one `.archive`.** That single file is
what a player installs.

**4. ArchiveXL merges it into the game at launch.** It reads a small
hand-written `.archive.xl` sitting next to the archive, which says what is
inside and where each piece belongs. Without that file nothing loads.

```
gen_*.py  ->  .json  ->  [WolvenKit]  ->  binaries  ->  [WolvenKit]  ->  .archive
                                                                            |
                                              .archive.xl  ->  [ArchiveXL] -+-> game
```

**redscript sits outside all of it.** `.reds` files are copied as source and
compiled by redscript inside the player's game when it starts. They are never
packed into the archive.

So the game receives three things: one binary `.archive`, one small YAML telling
ArchiveXL how to merge it, and redscript source.

Two consequences:

- Nothing under `source/wkit/raw/` is hand-written. It is generator output.
  Change the generator, re-run it.
- The `.archive.xl` is the one file you write by hand. See `docs/new-gig.md`.

## Glossary

| Term | Meaning |
|---|---|
| V | the player character |
| vanilla / base game | shipped by the developers, not by us |
| depot path | a file's path inside the game archives. Always backslashes |
| `.archive` | the game's package format. A mod is one of these plus a `.archive.xl` |
| journal | the game's record of quests, objectives, contacts, messages and pins |
| quest phase | a node graph driving a mission. `.questphase` |
| fact | a named integer in the save. The quest system's global variable |
| objective | one line in the quest log, with its own state and pins |
| scene | a conversation as a graph. The only line type that can carry audio |
| section / hub / choice | node types inside a scene: a run of lines, a menu, a branch |
| actor | a speaker in a scene. Not necessarily a visible body |
| NodeRef | a global name for a placed object, written `#some_name` |
| streaming sector | a chunk of world that loads when you are near. Three never unload |
| workspot | an animation slot an NPC stands in. Some characters only render inside one |
| TweakDB / TweakDBID | the game's record database, and a record id. Case sensitive |
| LocKey | a key into the localized string table |
| RUID / stringId | the 64-bit id on a scene line. Resolves its subtitle *and* its audio |
| voiceover map | `stringId -> .wem`. Flat and global, so a mod can supply its own |
| lipmap | which lipsync animation set belongs to which actor of which scene |
| `.wem` | the game's audio format. Made from WAV by Wwise |
| holocall | an in-fiction phone call. 2D audio, so speaker position is irrelevant |
| shard | a readable text item |
| mappin | the engine's word for a map marker |

## Next

| Goal | Read |
|---|---|
| build your own | `docs/new-gig.md` |
| build this one | `BUILDING.md` |
| avoid the traps | `docs/gotchas.md` |
| one subsystem | its playbook |
