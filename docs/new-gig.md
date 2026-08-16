# Starting your own gig

From a clone of this repo to a gig that appears in the quest log with a working
map pin.

Read `docs/orientation.md` first if any of that was unfamiliar.

**What you need to be comfortable with:** editing Python, running PowerShell
commands, and reading JSON. You do not need C++, and you do not need to know
the engine. Everything specific to Cyberpunk is in the playbooks.

Scope warning: a gig that appears, tracks one objective and closes is a day or
two. A gig with voiced conversations, lipsync and a custom NPC is the rest of
this repo.

## What you will make

| File | Made by |
|---|---|
| `<name>.journal` | `gen_journal.py` |
| `en-us.json` | `gen_localization.py` |
| `<name>.questphase` | `gen_questphase.py` |
| `<name>.scene` | `gen_scenes.py`, if you want conversations |
| `*.reds` | you, if you need gameplay logic |
| `<name>.archive.xl` | you, by hand. The only one |

## 0. Build gig 01 first

Before writing anything of your own, install the toolchain from `BUILDING.md`
and build the gig that already works:

```powershell
.\tools\build-archive.ps1 gig-01
.\tools\deploy-dev.ps1 gig-01
```

Then load a save and check the gig appears.

This is worth the twenty minutes. It separates "my setup is wrong" from "my gig
is wrong", and those two failures look identical from the outside. Every step
below assumes a toolchain you have already seen work.

## 1. Copy the shape

```
mods/gig-02-your-gig/
  source/
    scripts/          your .reds
    tweaks/           your TweakXL yaml, if any
    wkit/raw/
      your_gig.archive.xl
      mod/your_gig/   the generators write here
```

The build scripts take the mod folder name and derive the rest, so
`tools\build-archive.ps1 gig-02` works once the folder exists.

Name it `gig-NN-something`. The deploy reads the redscript module name from that
number.

## 2. Claim a namespace first

Read `docs/conventions.md` and pick your prefixes before writing anything. They
end up referenced from generated JSON, redscript and the dev menu at once, so
changing them later is painful.

This project uses `cc` plus the gig number: facts `cc_g01_*`, records
`Character.cc_g01_*`, LocKeys `cc-g01-*`, module `CyberpunkCodes.Gig01`. Use your
own prefix so both mods can be installed together.

The redscript rule bites hardest. Two mods declaring the same class name in the
same module fail the player's *entire* redscript bundle, breaking every other
redscript mod they have. `docs/conventions.md` has the tested evidence.

## 3. Write the manifest

`<name>.archive.xl` sits next to your raw tree. It is YAML. Nothing loads without
it.

The best reference is the real one:
`mods/gig-01-negative-balance/source/wkit/raw/gig01_negative_balance.archive.xl`.
Every key there carries a comment saying why it exists. This is the map of it.

| Key | Registers |
|---|---|
| `journal:` | your `.journal`, merged by id path |
| `localization: onscreens:` | UI strings. Takes a **list** per locale |
| `localization: subtitles:` | scene dialogue. Scalar per locale |
| `localization: vomaps:` | voice clips. Scalar per locale |
| `localization: lipmaps:` | lipsync sets. Scalar per locale |
| `streaming: blocks:` | your own world sectors, if any |
| `quest: phases:` | your `.questphase`, with a `parent` |

Four things learned the hard way:

1. Register every locale, not just `en-us`. An English-only mod should point all
   nineteen at its English file. Otherwise a player in another language gets
   working dialogue and audio, and raw LocKeys for the title and objectives. It
   looks perfect in testing, because testing happens in English.
2. `onscreens` takes a list per locale. Its three siblings take a scalar.
3. Parent the quest phase twice, to `base\quest\cyberpunk2077.quest` and
   `ep1\quest\ep1_standalone.quest`. Otherwise it does not exist for players who
   start from Phantom Liberty.
4. Do not ship a world sector just to hold a marker node. A node in a mod sector
   never registers its global name, so nothing can reference it. See
   `docs/map-pins-playbook.md`.

## 4. Build the smallest thing that works

Do not start with a conversation. Start with a gig that appears and closes. That
proves the journal, the phase and the manifest agree, so every later problem is
a local one.

1. Journal: one quest, `"type": "StreetStory"`, one objective, no pins yet.
2. Strings: a title and one objective description. A raw LocKey in the quest log
   means your prefix does not match.
3. Quest phase: pause on a fact, activate quest and objective, wait on a second
   fact, succeed. Node helpers are in `questkit/questgraph.py`.
4. Build, deploy, then set that first fact by hand and watch the gig appear.

A **fact** is the quest system's global variable, and setting one is how you
trigger a phase without playing up to it. Open the Cyber Engine Tweaks console
in game and run:

```lua
Game.GetQuestsSystem():SetFactStr("your_fact_name", 1)
```

Read one back with `GetFactStr("your_fact_name")`. Facts persist in the save, so
a fact you set for a test is still set after a reload. That matters more than it
sounds: see gotcha 21.

Add the map pin only after that works, and follow `docs/map-pins-playbook.md`
exactly. The most commonly missed step is activating the pin entry.

## 5. Then

Dialogue is plain strings in your generators; write it however you like. Gig 01
adapted an existing comic, which is why its files cite one - your gig needs
nothing but its own script. Keeping that script in one authoritative place and
diffing the generators against it is the part worth copying.

| Want | Read |
|---|---|
| conversations, choices, phone calls | `docs/scene-playbook.md` |
| voices | `BUILDING.md` audio section, `questkit/voice.py` |
| mouths moving | `questkit/lipsync.py` |
| computer screens and shards | `docs/computer-ui-playbook.md` |
| contacts and message threads | `docs/journal-research.md` |
| shipping it | `docs/release-playbook.md` |
| what failed, and why | `docs/backlog.md` |

## Using the builders

`tools/questkit/` is the reusable half: scenes, quest graphs, journal and map
pins, the voice pipeline, the lipsync scorer. Each takes a `configure(...)` call
naming your paths and prefix. Each module has a usage sketch at the top.

Plain Python, no dependencies, runs on your machine. Nothing in it becomes a
player download.

Two honest caveats:

- It has had one consumer. The config surface was drawn around one gig and will
  have gaps. If it cannot express something yours needs, open an issue.
- It assumes you write Python. If you don't, the playbooks and the `.archive.xl`
  are still the useful part of this repo, and they don't require any of it.

## First two failures to expect

| Symptom | Usually |
|---|---|
| nothing appears, no error | a manifest path that doesn't match where the file landed. Read `red4ext\plugins\ArchiveXL\*.log` |
| it appears, but shows LocKeys | keys don't match, or that locale wasn't registered |

`docs/gotchas.md` has 28 of these. Best hour you can spend before starting.
