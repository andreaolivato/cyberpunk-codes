# Release playbook

Two procedures that pull in opposite directions. Shipping strips the debug
tooling out; starting the next gig puts it back. Both were done once by hand and
neither is obvious a month later.

## 1. What a Cyberpunk 2077 release is

A plain `.zip` whose internal structure mirrors the game root. Vortex extracts it
straight into the Cyberpunk folder; a manual installer drags it there.

No manifest, no metadata file, no FOMOD. FOMOD only earns its place when a mod
offers install-time choices, and this one has a single variant.

```
archive/pc/mod/gig01_negative_balance.archive
archive/pc/mod/gig01_negative_balance.archive.xl
r6/scripts/NegativeBalance/*.reds
r6/tweaks/NegativeBalance/*.yaml
```

The zip is not a package that gets opened. Its contents *are* the files that land
in the game folder. That explains most of the conventions:

- A `readme.txt` at the top of the zip becomes `Cyberpunk 2077\readme.txt`, loose
  beside the game executable. If every mod did that, the game root would fill up
  with other people's readmes.
- Docs that do ship go inside the mod's own folder. ArchiveXL, TweakXL and
  Codeware each ship a `LICENSE` at `red4ext\plugins\<name>\LICENSE`. If this mod
  ever ships one, `r6/scripts/NegativeBalance/README.md` is the place.
- A wrapper folder is fatal. `NegativeBalance/archive/...` instead of
  `archive/...` means Vortex installs nothing, or one level too deep, and the mod
  silently never loads.

## 2. Building it

```powershell
.\tools\build-release.ps1 gig-01 -Version 1.1.1
```

Writes `dist\NegativeBalance-1.1.1.zip`. `dist\` is gitignored.

The version lives in exactly two places: this command line and the Nexus page,
because a Cyberpunk mod zip has no manifest to hold it. The third place is the
one that is easy to forget: `CHANGELOG.md`, written before the
upload, not after.

The changelog doubles as the copy for the Nexus Changelog tab, so it is
player-facing. Keep the internal account of the same work in a development log
kept separately. A changelog that explains itself to developers
stops being readable by players.

Tag the release in git once the zip is uploaded: `gig-01/v<version>` on the
commit the zip was built from, in every repo that carries the source. The tag
is what a GitHub release attaches to, and it marks the exact source of the
shipped bytes, which matters because the packing is non-deterministic and a
rebuild can never prove it matches.

### It does not rebuild by default

WolvenKit's archive packing is non-deterministic. The same raw tree packed twice
gives the same byte count and a different hash every time (measured 2026-08-14),
so a rebuilt archive can never be proven to be the one that was playtested.

The script therefore ships what is already in `source\wkit\packed`, and diffs
every file against the copy deployed in the game folder, which is the build that
was played.

- plain files (`.xl`, `.reds`, `.yaml`) must hash-match
- the `.archive` is compared by size, because a hash match is not achievable

Pass `-Rebuild` when you want fresh output, and expect the archive line
to say "same size" rather than "identical".

Three things it refuses to package, each of which fails silently otherwise: a
wrapper folder, `source/cet-dev/`, and anything under `base\`.

Before building, deploy what you tested:

```powershell
.\tools\deploy-dev.ps1 gig-01 -NoDevMenu
```

`-NoDevMenu` produces the player's layout and deletes an already-deployed dev
menu. Without it, a plain re-deploy silently reinstalls the menu.

## 3. The mod page

- **Requirements: four, plus redscript.** RED4ext, ArchiveXL, TweakXL, Codeware.
  NOT Cyber Engine Tweaks, NOT Audioware, NOT mod_settings. Proven rather than
  assumed: on 2026-08-14 everything else was disabled in Vortex, CET was taken
  out of the loader, and the gig played end to end.
- **Tag it as AI-Generated Content.** This is a Nexus platform rule, not a
  licence question. Their generative-AI guidelines name voices explicitly, and
  undisclosed AI use is grounds for moderation. It is unrelated to what the
  voices cost or what rights the plan grants. Two separate questions, both of
  which have to be satisfied.
- Say the voices are AI in the description too. That is this project's own
  standing policy (`architecture.md`, "Voice"), and unlike the page tag it can
  travel with the files if a README ever ships.
- Permissions (reupload, modification, asset reuse) are set on the Nexus page,
  which is the normal mechanism for a story mod. The MIT licences ArchiveXL and
  friends ship suit libraries other people build on. This is content, not a
  library.

## 4. Getting a dev machine back

Releasing leaves the machine deliberately stripped. Reverse it before starting
the next gig, or the dev menu will be missing and nothing will say why.

**1. Put CET back in the loader.** Testing as a new user disables it by renaming,
so the file is still there:

```powershell
$g = "C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077"
Rename-Item "$g\bin\x64\plugins\cyber_engine_tweaks.asi.disabled" "cyber_engine_tweaks.asi"
```

Renaming rather than deleting is the point.
`bin\x64\plugins\cyber_engine_tweaks\` still holds your `bindings.json`,
`layout.ini` and `persistent.json`, so keybinds and window positions survive the
round trip.

**2. Re-enable the mods you disabled in Vortex**, if you want them back. For gig
work only Cyber Engine Tweaks matters; the rest were disabled to prove the
requirements list.

**3. Redeploy with the dev menu.** Plain `deploy-dev.ps1`, no flag:

```powershell
.\tools\deploy-dev.ps1 gig-01
```

That restores `bin\x64\plugins\cyber_engine_tweaks\mods\negative_balance_dev`.

**4. Check it came back.** CET overlay, window "Negative Balance [DEV]". If the
window is absent, CET did not load: check `bin\x64\plugins` for a stray
`.disabled` suffix before suspecting anything else.

### What the dev menu is for

Fact buttons and a quest-start button, teleport presets with in-game position
capture, journal and entry-hash dumps, FULL PIN DIAGNOSIS, a live Johnny spawn
bench, and `call_trace.log`, which opens, writes and closes per line and
therefore survives a hard crash, unlike CET's own buffered logs.

Two probes matter most, because their answers are not reliably discoverable from
files on disk:

- **CAPTURE THE NPC I'M LOOKING AT**, which writes a real position, yaw and
  record id to `captured_positions.txt`
- the character-record dumps

`Character.Mama_Welles` and her spot were found that way. Guessing either fails
silently.

### Without the dev menu, the logs are the diagnosis

Useful even on a player's machine, and the right thing to ask a bug reporter for.

| Log | Answers |
|---|---|
| `r6\logs\redscript_r*.log` | did our `.reds` compile |
| `red4ext\plugins\ArchiveXL\ArchiveXL-*.log` | pin resolution (`resolved to NodeRef`), localization merges |
| `red4ext\logs\red4ext.log` | did the plugins load at all |
| `%LOCALAPPDATA%\CD Projekt Red\Cyberpunk 2077\CrashInfo.json` | position, district and session length after a hard crash |
