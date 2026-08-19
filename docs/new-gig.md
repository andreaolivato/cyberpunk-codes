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

The generators named there are gig 01's own. Each hardcodes its paths and its
prefix, so you copy the ones you need and re-point their constants, or edit
them in place if you are not keeping gig 01. The half that no gig owns is
`tools/questkit/`, which they import.

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
    audio/            your WAV masters, if the gig is voiced
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
4. Anchor a map pin to a base-game node rather than to a marker node of your
   own. A node you ship CAN be named, but only in the long
   `$/03_night_city/#district/area/#node` form, and whether a pin resolves
   against one has not been tested. The short `#node` form registers nothing,
   which is what made this look impossible for months. See
   `docs/map-pins-playbook.md` and `gotchas.md` #34.

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

## 5. The run order

Every generator writes into your raw tree, and two of them read what another
wrote. Run them in this order.

```powershell
python .\tools\gen_journal.py         # quest, objectives, pins, POI
python .\tools\gen_localization.py    # every LocKey string
python .\tools\gen_voice.py           # WAVs to .wem, voiceover map, durations
python .\tools\gen_lipsync.py         # a vanilla mouth animation per line
python .\tools\gen_scenes.py          # the .scene conversations
python .\tools\gen_questphase.py      # the quest graph
.\tools\build-archive.ps1 gig-02      # JSON to resources to one packed archive
.\tools\deploy-dev.ps1 gig-02         # copy it all into the game folder
.\tools\check-scripts.ps1             # offline redscript compile, if you ship .reds
```

Only two of those orderings carry weight, and both are about `gen_scenes`:

- `gen_voice` writes `durations.json`, which `gen_scenes` reads to pace each
  section from the real clip. Without it a line is timed by a character-count
  estimate instead, so a section can move on before the audio finishes.
- `gen_lipsync` writes `lipsync_picks.json`, which `gen_scenes` reads to put an
  animation name on each line.

Both sidecars are optional. A gig with no audio runs `gen_scenes` on its own and
everything works except that nobody speaks.

Skip what your gig does not have. An unvoiced gig with no conversations needs
only `gen_journal`, `gen_localization` and `gen_questphase`. This repo's
`gen_shard_ent.py` and `gen_sector.py` exist for one physical object gig 01
puts on a desk, so they are examples rather than steps.

Two rules about the loop itself:

- `check-scripts.ps1` compiles the DEPLOYED scripts, not your repo, so deploy
  first or it will faithfully compile the previous version and report success on
  untested code. `check-scripts-repo.ps1 gig-02` compiles the repo instead and
  writes nothing to the game folder.
- An `.archive` change needs the game quit before you deploy, because the game
  holds the file open. A `.reds` change needs a restart. A CET `.lua` change
  needs neither. `BUILDING.md`, "Reload rules".

## 6. Adding voices

One constraint decides the shape of everything below, so read it before
recording anything: a line can only be voiced if it lives in a scene. A scene
line carries a `scnlocLocstringId` RUID, and the game resolves both its subtitle
and its audio from that one number. Text pushed from redscript is a caption with
no RUID, so no voiceover map can ever key on it. A beat that needs a voice has
to be built as a scene rather than as a script that prints text.

Nothing in the pipeline cares what produced the WAV. A microphone, a hired actor
and a text-to-speech model all enter at step 3.

Players install nothing extra for any of it. Audio resolves natively through a
`locVoiceoverMap` your mod supplies, so Audioware is not a dependency.

### What you need first

Wwise 2019.2.15, Authoring plus the Windows platform. Nothing else can write a
`.wem`: WolvenKit answers "Use WolvenKit to import opus" and imports nothing,
and REDmod's `resource-import` lists no audio format at all. The version
matters, because newer Wwise is reported to emit `.wem` the game will not play.
No plug-ins are needed, since Vorbis is core Wwise rather than an add-on, and no
SDK. `gen_voice.py` reads the console path from the `WWISE_CONSOLE` environment
variable if it is set, and otherwise looks in the default install location.

### The steps

1. **Say which lines are voiced.** The `CAST` table in your copy of
   `gen_voice.py` maps each character to the scenes and line keys they speak.
   Those keys are `gen_scenes`' own line keys, so a typo stops the run instead of
   producing a line that is silently never voiced. Add a `(scene, key)` pair to
   `GENDERED` for any line that needs its own male take.

2. **Prove the route with tones, before a single recording exists.**

   ```powershell
   python .\tools\gen_voice.py --placeholder
   python .\tools\gen_scenes.py
   .\tools\build-archive.ps1 gig-02
   .\tools\deploy-dev.ps1 gig-02
   ```

   That synthesises a tone for every line at the length the estimate would have
   given it, pitched by a hash of the line key so lines are distinguishable by
   ear. In game you hear a beep where each line goes. Every failure after this
   point is about one recording rather than about the pipeline.

3. **Put the real takes in your mod's `source\audio\`,** named
   `<scene>__<key>.wav`. A gendered line takes a second file,
   `<scene>__<key>__m.wav`, for the male variant. A real take always wins over a
   placeholder of the same name, so the two can coexist while you replace them a
   few at a time. Placeholders live in a subfolder of their own and are not
   tracked, so a directory listing shows which lines have a real recording.

4. **Convert.** `python .\tools\gen_voice.py` runs every WAV through Wwise
   headlessly, checks that each `.wem` it wrote really is Wwise Vorbis, then
   writes `durations.json` and the voiceover map. It stops and names the files if
   a line has no audio at all.

   The conversion, the `.wem` check and the voiceover map itself live in
   `tools/questkit/voice.py`, which every gig imports rather than forks.

   **Lines that arrive on V's phone are treated automatically, and you tag
   nothing.** `gen_voice` asks the scene builder which sections were written
   `holocall=True`, which is the same argument that sets `isHolocallSpeaker` and
   makes the line play through the phone UI, so the audio and the game can never
   disagree about which lines are calls. Those masters are run through
   `tools/questkit/phone.py` into `source\audio\holocall\`, keeping the
   filename, and Wwise converts that copy. Your master is never touched.

   The treatment is not an EQ, and this matters if you ever reach for one: the
   base game keeps a line's magnitude spectrum and discards its phase, so a
   filter alone cannot sound like a call however hard it is pushed. `phone.py`
   carries the measurement and `gotchas.md` 42 the finding.

   The derived folder is gitignored, because a committed tool over a committed
   master reproduces it byte for byte. **Keep your masters dry.** A take that
   has already been processed would be processed twice and nothing would catch
   it.

5. **Re-run `gen_scenes.py`.** Until you do, the scenes still hold the estimated
   timings rather than the measured ones. `gen_voice` prints this reminder when
   it finishes.

6. **Register the map.** `localization: vomaps:` in your `.archive.xl` points at
   the generated voiceover map, and `lipmaps:` at the lipsync map. Both take a
   scalar per locale. Section 3 has the rest of the manifest.

7. **Build and deploy.** `build-archive.ps1` refuses to pack when any WAV is
   newer than its `.wem`, and names the offenders. That guard is there because a
   conversion failed silently once and the build carried on and packed the
   previous run's audio, which nothing downstream can detect.

### The masters are committed here, and yours need not be

This repo tracks both: 114 WAV masters and the `.wem` built from them. That is a
choice rather than a requirement, and it costs repo size to make the audio
rebuildable from source by anyone who clones it.

The alternative is to track only the `.wem`, which are what the mod actually
ships. A clone then builds a working mod with no WAV present at all, and
`gen_voice.py` is only needed when the dialogue changes. It says so by name when
a line has no audio, rather than failing as though something were broken.

Either way, `build-archive.ps1` packs from the `.wem`, so a gig that has not run
`gen_voice` since its last dialogue change is caught by the staleness guard
rather than shipping the previous run's audio.

### Two things that arrive with audio

- **Mouths.** `gen_lipsync.py` casts a vanilla animation of roughly the right
  length onto each line. The mod ships no animation data, because the animation
  name a line carries is free-form and can simply point at one the game already
  owns. `docs/scene-playbook.md` covers it.
- **Phone calls.** A holocall is not the clean take played through a filter at
  runtime. Vanilla ships a separately processed recording for every line that
  arrives on V's phone, so the treatment is baked into the asset.
  `tools/questkit/phone.py` bakes an equivalent into a copy and leaves your
  master alone.

## 7. Then

Dialogue is plain strings in your generators; write it however you like. Gig 01
adapted an existing comic, which is why its files cite one - your gig needs
nothing but its own script. Keeping that script in one authoritative place and
diffing the generators against it is the part worth copying.

| Want | Read |
|---|---|
| conversations, choices, phone calls | `docs/scene-playbook.md` |
| voices | section 6 above, then `BUILDING.md` audio toolchain |
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

`docs/gotchas.md` has 41 of these. Best hour you can spend before starting.
