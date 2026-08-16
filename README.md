# Cyberpunk.Codes

A system for building story gigs (side quests) for Cyberpunk 2077: generators
for the journal, quest graph, scenes, voice and lipsync, reusable builders
under `tools/questkit/`, and the notes from working out how each subsystem
behaves.

It has built one gig so far: **Negative Balance**, a quest with map pins,
voiced conversations, lipsync and a custom NPC, published on
[Nexus Mods](https://www.nexusmods.com/cyberpunk2077/mods/32694). Its full
source is in this repo, and future gigs will be built with the same tools.

The documentation is the point of publishing this. It is written for modders
building their own quest mods: what each subsystem needs, the traps in it, and
the evidence, so the next person does not have to rediscover them.

Everything the game loads is generated from Python. Nothing is hand-edited JSON.

## How a build works

```
tools/gen_*.py   ->  JSON        one file per resource, in WolvenKit's
                                 text form of the game's binary format
WolvenKit        ->  binaries    .journal, .questphase, .scene, .ent
WolvenKit        ->  one .archive
ArchiveXL                        merges that archive into the game at
                                 launch, told what to merge by a small
                                 hand-written .archive.xl
```

`.reds` sit outside that chain: they ship as source and redscript compiles them
in the player's game.

## Start here

1. [`docs/orientation.md`](docs/orientation.md): what a gig is made of and what
   each core mod does. Skip if you've shipped a quest mod before.
2. [`docs/new-gig.md`](docs/new-gig.md): clone to a working gig with a map pin.

## Reference

| Doc | For |
|---|---|
| [`docs/gotchas.md`](docs/gotchas.md) | 28 things that cost hours each. Read before starting |
| [`docs/map-pins-playbook.md`](docs/map-pins-playbook.md) | Working map pins. Three ingredients, three failure modes |
| [`docs/scene-playbook.md`](docs/scene-playbook.md) | Conversations, choices, holocalls, lipsync |
| [`docs/computer-ui-playbook.md`](docs/computer-ui-playbook.md) | Mod content on a base-game computer, and shards |
| [`docs/journal-research.md`](docs/journal-research.md) | Contacts, messages, reply choices |
| [`docs/architecture.md`](docs/architecture.md) | Every decision and why, including dead ends |
| [`docs/conventions.md`](docs/conventions.md) | Naming, so two installed gigs never collide |
| [`docs/backlog.md`](docs/backlog.md) | Numbered research register. Look things up; don't read it through |
| [`BUILDING.md`](BUILDING.md) | Toolchain, dev loop, how to build it |
| [`CHANGELOG.md`](CHANGELOG.md) | What each release changed |

## Things that took longest to learn

- A map pin needs its own journal entry activated, not just its objective. An
  inactive pin is invisible, and every layer below then looks broken.
- A quest map pin can't be un-shown. Activating one registers it forever.
- Lipsync lands on the line's speaker, and only a scene can own one. Only a
  script can put a body where the player is. A workspot is what makes the actor
  render at all.
- A fact survives a save reload. A script field doesn't. Mixing them gives you a
  state machine that comes back half-reset. This shipped once and players found
  it.

## Layout

```
BUILDING.md     toolchain, dev loop, audio pipeline
docs/           playbooks, decisions, gotchas, research register
tools/
  questkit/     reusable builders: scenes, quest graphs, journal, pins,
                voice, lipsync
  gen_*.py      one gig's tables and dialogue, on top of those
shared/scripts/ redscript shared between gigs, vendored per mod at build time
mods/gig-01-negative-balance/
  docs/         story, quest design, full dialogue as text
  source/       redscript, TweakXL records, CET dev menu, generated resources
```

Nothing under `source/wkit/raw/` is edited by hand: change the generator and
re-run it. A quest graph with 124 nodes is not something anyone should hand-edit
as JSON.

`tools/questkit/` is the part that isn't about this story. Each module takes a
`configure(...)` call naming your paths and prefix. Plain Python, no
dependencies, runs on your machine, never becomes a player download.

It has had one consumer, so treat its shape as provisional. If it can't express
something your gig needs, open an issue.

## Building it from source

To play the mod, install the release from
[Nexus Mods](https://www.nexusmods.com/cyberpunk2077/mods/32694) like any other
mod; nothing in this repo is needed for that. Build from source when you have
changed something, or want to check that the pipeline works.

**You don't need to run the generators.** Their output is committed, and so is
the `.wem` audio, so a fresh clone builds a working mod with two commands:

```powershell
.\tools\build-archive.ps1 gig-01     # JSON -> resources -> packed .archive
.\tools\deploy-dev.ps1 gig-01        # copy into the game folder
```

Both need WolvenKit CLI and a copy of the game. See [`BUILDING.md`](BUILDING.md).

Run a generator only when you change what it produces:

| Generator | Also needs |
|---|---|
| `gen_journal`, `gen_localization`, `gen_scenes`, `gen_*_ent`, `gen_sector`, `gen_questphase` | nothing, they run on a clean clone |
| `gen_lipsync` | WolvenKit CLI and the game, to build its catalogue (~40 s, once) |
| `gen_voice` | Wwise, plus WAV masters, which are not committed |

The WAV masters are large and regenerable, so they aren't in the repo. That only
stops you re-voicing lines; it doesn't stop you building.

## Voices

Generated with ElevenLabs. Every line subtitled.

The pipeline does not care where a WAV came from: `tools/gen_voice.py` turns any
WAV into a `.wem` through Wwise and builds the `locVoiceoverMap` the game
resolves audio through, so recording real voice actors uses the same steps.
Audioware isn't required; players install nothing extra.

## Licence

Code is MIT. Story, dialogue and audio are not. See [`LICENSE`](LICENSE).

## Bug reports

Two places, depending on what broke:

- **The gig misbehaving in game** (a stuck quest, silent audio, a crash): the
  mod's [Nexus bugs tab](https://www.nexusmods.com/cyberpunk2077/mods/32694?tab=bugs),
  where players will find it.
- **The framework, a generator, a script or a doc** (a build fails on your
  machine, a doc is wrong): a GitHub issue on this repo.

Everything here was established against game 2.31 on one machine, so "this
does not work for me" is a useful report on its own: another mod list, other
hardware or another game version can all behave differently. Name your setup.

## Contributing

Pull requests are welcome, for the framework and for the gigs. Read
[`CONTRIBUTING.md`](CONTRIBUTING.md) first; the rule that matters most is edit
the generators, never their output.
