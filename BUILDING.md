# Building

Everything the game loads is generated from the scripts in `tools/`. Nothing
under `mods/*/source/wkit/raw/` is written by hand: change the generator and
re-run it. The one exception is `gig01_negative_balance.archive.xl`, which is
hand-authored source that happens to live in the same directory.

## How the generators are laid out

`tools/questkit/` is the reusable half and `tools/gen_*.py` is one gig's half.

| module | holds |
|---|---|
| `questkit/scene.py` | the `Scene` builder, subtitle and lipmap writers, Johnny presets |
| `questkit/questgraph.py` | the quest-graph `Builder` and its `add_*` node helpers |
| `questkit/journal.py` | journal handles, map-pin maths, objectives, contacts |
| `questkit/voice.py` | WAV to WEM through Wwise, and the `locVoiceoverMap` writer |
| `questkit/lipsync.py` | the vanilla lipsync catalogue and the length-matching scorer |

Each questkit module takes a `configure(...)` call naming one mod's output paths
and its LocKey prefix. A second gig imports them and writes only its own tables,
dialogue and graph.

The quest-graph builder keeps its graph in one module-level instance, so it
builds one graph per process. That is why the generators are scripts rather
than libraries.

Shared **redscript** works differently, because `.reds` ship as source and are
compiled in the player's game. It lives in `shared/scripts`, and
`tools/vendor-shared.ps1` copies it into each mod at build time under a per-gig
module name. Read `docs/conventions.md` before touching it: two mods declaring
the same class in the same module fail the player's ENTIRE redscript bundle,
not just this one.

## Checking a change

One check, and it does not need the game:

```powershell
.\tools\check-scripts-repo.ps1 gig-01 # redscript compiles, nothing deployed
```

For a quick check while working, regenerate and run `git status`. An empty
result means the output is byte-identical, so the packed archive is unaffected
and nothing needs rebuilding or replaying.

## Requirements

**This is Windows-only.** The build scripts are PowerShell and WolvenKit is a
Windows tool. Cyberpunk itself runs elsewhere, but this toolchain does not.

Versions are what it was built and tested against. Newer usually works; if
something behaves oddly, check these first.

| Need | Version | Get it |
|---|---|---|
| Cyberpunk 2077 | 2.31, Steam | default path `C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077` |
| Python | 3.13 | https://www.python.org/downloads/ Standard library only, nothing to `pip install` |
| WolvenKit GUI + Console | 8.20.0 | https://github.com/WolvenKit/WolvenKit/releases Keep both at the same version |
| RED4ext | 1.30.0 | https://github.com/WopsS/RED4ext/releases |
| ArchiveXL | 1.27.1 | https://github.com/psiberx/cp2077-archive-xl/releases |
| TweakXL | 1.11.4 | https://github.com/psiberx/cp2077-tweak-xl/releases |
| Codeware | 1.20.3 | https://github.com/psiberx/cp2077-codeware/releases |
| redscript | ships with the game | `engine\tools\scc.exe` |
| Cyber Engine Tweaks | 1.37.1 | https://github.com/maximegmd/CyberEngineTweaks/releases Dev menu only, never shipped |

The CLI is expected at
`%LOCALAPPDATA%\Programs\WolvenKit.CLI\WolvenKit.CLI.exe`. If yours is
elsewhere, set `WOLVENKIT_CLI` or pass `-Cli`.

The four RED4ext-based mods above are also what a *player* installs to run the
finished gig. Audioware is not among them: a scene line resolves its own audio
through a mod-supplied `locVoiceoverMap`, so players install nothing extra for
the voices.

### If a script will not run

Windows blocks PowerShell scripts by default. The first one you try fails with
"cannot be loaded because running scripts is disabled on this system." Allow
them for your own account, once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

If you downloaded the repo as a zip rather than cloning it, Windows also marks
every file as coming from the internet. Clear that, once:

```powershell
Get-ChildItem -Recurse | Unblock-File
```

## Dev loop

```powershell
python .\tools\gen_journal.py         # contacts, quest, objectives, pins, POI
python .\tools\gen_localization.py    # all LocKey strings
python .\tools\gen_voice.py           # WAV -> WEM (Wwise) + voiceover map
                                      #  + durations.json. Run BEFORE gen_scenes:
                                      #  it writes the sidecar gen_scenes paces
                                      #  voiced lines from. `--placeholder`
                                      #  substitutes tones for missing takes
python .\tools\gen_lipsync.py         # casts a VANILLA lipsync animation of
                                      #  about the right length for every line
                                      #  Johnny, Hoshino and Mama Welles say,
                                      #  into source\lipsync_picks.json. Ships
                                      #  NO animation data - the animation name
                                      #  a line carries is free-form, so it just
                                      #  points at one the game already has.
                                      #  Between gen_voice (durations) and
                                      #  gen_scenes (which reads the picks).
                                      #  `--rebuild` re-extracts its catalogue
python .\tools\gen_scenes.py          # FOURTEEN .scene conversations - EVERY line
                                      #  in the gig is a scene line, because a
                                      #  scene line is the only kind that can
                                      #  carry audio. Their text lives INSIDE
                                      #  the scene, not in the localization
                                      #  resource. Run AFTER gen_voice.py: it
                                      #  paces sections from durations.json
python .\tools\gen_shard_ent.py       # the physical data shard on the office
                                      #  desk: a HealthConsumable-class .ent
                                      #  with an interaction + mesh. A mod
                                      #  .ent can only name a class the GAME
                                      #  ships - see the file's header
python .\tools\gen_sector.py          # the world sector + streaming block that
                                      #  put the shard entity on the office
                                      #  desk. Rarely re-run - only when the
                                      #  shard moves - but it is the authority
                                      #  on that position, not the JSON
python .\tools\gen_questphase.py      # quest graph (objective + PIN activation
                                      #  + scene nodes)
.\tools\build-archive.ps1 gig-01      # JSON sources -> resources -> packed archive
.\tools\deploy-dev.ps1 gig-01         # copy scripts+lua+archive into game dir
.\tools\deploy-dev.ps1 gig-01 -NoDevMenu   # ...as a PLAYER gets it: no CET dev
                                      #  menu, and it DELETES an already-
                                      #  deployed one. Without this a plain
                                      #  re-deploy silently reinstalls the menu
.\tools\build-release.ps1 gig-01 -Version 1.1.1   # the release .zip, into dist\
                                      #  Refuses a wrapper folder, the dev menu,
                                      #  or any base\ override. Does NOT rebuild
                                      #  by default: WolvenKit packing is NON-
                                      #  DETERMINISTIC (same inputs, same size,
                                      #  new hash), so it ships the bytes that
                                      #  were TESTED and diffs every file against
                                      #  the deployed build. -Rebuild to force
.\tools\check-scripts.ps1             # offline redscript compile check. Compiles
                                      #  the DEPLOYED tree and REFUSES to run if
                                      #  the repo differs from it, so the order
                                      #  is always deploy, THEN check
.\tools\check-scripts.ps1 -SelfTest   # prove the check can still detect breakage
.\tools\check-scripts-repo.ps1 gig-01 # compile the REPO instead, vendoring on
                                      #  the way in, writing nothing to the game
                                      #  folder. This is the one to use while
                                      #  refactoring: the checker above would
                                      #  make you deploy over a working install
                                      #  just to find out whether it compiles
.\tools\vendor-shared.ps1 -Dst <dir> -Gig Gig01   # copy shared\scripts under a
                                      #  per-gig module. Called by deploy-dev
                                      #  and build-release; rarely run by hand
python .\tools\dump_dialogue.py       # every spoken line as plain text, read out
                                      #  of the generators rather than their
                                      #  output, so it cannot drift from what
                                      #  ships. `--screens` adds the SMS threads,
                                      #  terminal, shard and HUD text
python .\tools\find_pin_anchors.py <x> <y> <z>   # find a pin anchor. Scans the
                                      #  game's ALWAYS-LOADED sectors and prints
                                      #  each node's position for ANCHOR_POS. An
                                      #  anchor in any OTHER sector is not
                                      #  streamed in when the quest needs it and
                                      #  the pin never appears. See
                                      #  docs/map-pins-playbook.md
```

**There is no cooked-mappin step.** Pins anchor to base-game nodes in the game's
`always_loaded_*` sectors and ArchiveXL computes the position; the tables are
`ANCHOR_POS` / `PIN_POS` in `gen_journal.py`. The mod ships **no base-game
files**. See `docs/map-pins-playbook.md`.

## Reload rules

| Changed | What it takes |
|---|---|
| `.archive` | quit the game, deploy, relaunch - the game holds the file open |
| `.reds` | restart the game |
| CET `.lua` | "Reload All Mods" in the CET overlay, no restart |

**Deploy before running `check-scripts.ps1`.** It compiles the *deployed*
scripts, not the repo, so running it first faithfully compiles the previous
version and reports success on untested code. It now compares every repo `.reds`
against its deployed twin and refuses to run when they differ, but keep the
order right anyway. See `docs/gotchas.md` #12.

## Audio toolchain

Only needed if you are adding or replacing voice lines.

**Wwise 2019.2.15** - CLI at `Authoring\x64\Release\bin\WwiseConsole.exe`. This
is the ONLY way to produce a `.wem`:

- WolvenKit cannot. `import` on a wav answers *"Use WolvenKit to import opus"*
  and imports nothing.
- REDmod cannot. `resource-import` lists no audio format at all, and its
  `customSounds` overrides audio *events*, not `.wem`.

**The version matters.** The community reports that newer Wwise emits `.wem`
the game will not play. Install Authoring + the Windows platform only; no
plug-ins are needed (Vorbis is core, not a plug-in) and no SDK.

`gen_voice.py` reads the console path from `WWISE_CONSOLE` if it is set, and
otherwise looks in the default install location.

### Extracting vanilla audio to listen to it

```powershell
$WK = "$env:LOCALAPPDATA\Programs\WolvenKit.CLI\WolvenKit.CLI.exe"
& $WK unbundle "<game>\archive\pc\content\lang_en_voice.archive" -o <dir> -r "<stringId hex>"
& $WK export <dir> -o <out> -gp "<game>"      # -> .Ogg
```

**Do not use `WolvenKit.CLI wwise -w`** - it is broken in 8.20.0 and dies with
`Type System.IO.FileInfo cannot be created without a custom binder`. `export`
with `-gp` is the working wem -> Ogg path.

## Reference material

- **Other mods, for structure.** Deceptious's Californication and OneMoreLight
  are the best worked examples of journal + questphase + scene + streamingsector
  together. Re-extract them from `archive\pc\mod\*.archive` with WolvenKit.
- **Decompiled game scripts**: https://codeberg.org/adamsmasher/cyberpunk - the
  source of truth for scripted UI wraps (`worldMap.swift`, `quest_log/*.swift`).
- **Extracted base-game data is cache, never committed.** `tools/_anchor_cache/`
  (streaming sectors) is rebuilt automatically by `tools/find_pin_anchors.py`,
  and is handy for grepping world data. It and `mods/*/source/wkit/_research/`
  are gitignored. Keep it that way: shipping extracted game data is what gets a
  mod taken down.
- **TweakDB ids are CASE-SENSITIVE and are not reliably discoverable from the
  files on disk.** These were found by runtime inspection using the CET dev
  menu's dump buttons: `Character.Mama_Welles`, `Character.Elcoyote_Barman`,
  `Character.q000_kid_coyote_staffer`.

## Where things live

```
docs/           playbooks, architecture decisions, the gotcha list
tools/          every generator; nothing in the game is authored by hand
mods/
  gig-01-negative-balance/
    docs/       story, quest design, the dialogue as plain text
    source/
      scripts/  redscript (.reds)
      tweaks/   TweakXL records (.yaml)
      cet-dev/  the CET dev menu - never shipped to players
      wkit/raw/ generated resources, packed into the .archive
```
