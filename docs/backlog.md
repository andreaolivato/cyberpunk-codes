# Research register: questions asked, and how each one closed

**Read the title literally. The filename is misleading.** This started as a
backlog and is now mostly the opposite.

It is a numbered register of every question this project spent real effort on,
each carrying the evidence that closed it. Most are closed. Perhaps a tenth is
still open.

That makes it long, and it is meant to be looked things up in rather than read.
Use the index below.

## DO NOT RENUMBER ANYTHING IN THIS FILE

Section numbers here are cited from 43 places across the tree, including
shipped redscript (`Gig01_Encounter.reds`, `Gig01_Holocall.reds`), the CET dev
menu, six generators, and `architecture.md` and `scene-playbook.md`. A comment
reading "see `backlog.md 3d`" is a real reference, so:

- **never renumber a section**, even to tidy a gap (2f sits between 2i and 2h,
  and 2e has an `-orig` and a `-bis`; leave all of it alone);
- **never delete a section** once anything cites it. Mark it closed instead;
- **append** new sections with the next free number.

This is the same rule `gotchas.md` carries, for the same reason, and it is
written down here because the numbering earned that protection without ever
being given it.

## What is actually still open

| § | Item |
|---|---|
| 4 | Housekeeping: the toolkit split left three loose ends (`gen_localization` unsplit, the gig-01 anchors stated twice, and the attitude and Johnny-placement redscript still inline) |
| 6 | The `[F]` interaction prompt on a mod-placed object. UNSOLVED and deliberately parked; seven approaches ruled out, each with its outcome |
| 10h | The questphase is registered under two quest roots. Deliberate. Measured against a player's log in 14: only one root is ever patched, so it is not a fault |
| 10i | Reload crashes on heavily modded installs. Two reporters, same symptom. No mechanism found; the A/B test is now deterministic, see 14 |
| 15 | Holocall lines play flat. ANSWERED AND BUILT 2026-08-19. Vanilla keeps the line's magnitude spectrum and discards its phase, which is why no EQ ever sounded right; `tools/questkit/phone.py` does the same. Built and deployed, awaiting a playtest |
| 16 | Johnny appears while V is driving, staged for a V standing still. Gate the three free-roaming beats on movement state, with a bound so the gig cannot stall |
| 17 | The spawned guards huddle where the navmesh dropped them and do not react to V. A hostile attitude is not perception; 11 is the structural fix and is unsolved |
| 21 | A second gig needs its generators in a subdirectory. Agreed; what is left is the export allowlist line, the `sys.path` hop and the docs that list the loop |

Everything else is closed. Two entries look open and are not: 2f (re-time
scenes from real clip length) shipped as `durations.json`, and 0b is the
release checklist, all of it struck through.

## Closed, and what each one still answers

| § | Closed question |
|---|---|
| 0, 0b | The gig plays end to end; the release checklist |
| 1 | Subtitle speaker-name styling. Fell out of the scene conversion |
| 2a-2i | The voice route: why a mod voiceover map works and Audioware is not needed; why reusing vanilla takes does not scale (3 of 59 lines matched) |
| 2j | Lipsync, whole mechanism. Includes `type: Tag` being dead, and a crash that took a session to attribute |
| 3, 3b | Johnny's apparition: the workspot is what makes him render at all |
| 3c, 3d, 3e | Three features deliberately NOT built. The reasoning is the value |
| 5 | Three refinements from playing the finished gig |
| 7, 8 | Post-release bug reports and their fixes, including the office doors |
| 9 | Placing a scene actor relative to the player. Corrects two claims this register had wrong, and deletes the burial-and-lift workaround built on them |
| 11 | A node this mod ships CAN be addressed by name, in the long form only. Corrects the map-pin playbook, and opens communities as the route to a mod-placed NPC. Its one open half closed in 20 |
| 13 | Three properties the game silently rejects, and the field that was credited with fixing Hoshino for months without ever running |
| 14 | The world grid, derived: cell size, the rldGridCell packing, and why a whole-map streaming box was wrong |
| 15 | The holocall treatment: baked into separate assets, and a phase effect rather than a filter. Includes the two wrong answers |
| 20 | A pin CAN anchor to a node this mod ships, and a mod CAN ship an always-loaded sector to keep it resolvable. Also why the drawn route built on it was reverted |
| 18 | El Coyote Cojo is shut until Heroes is finished, measured across three saves. The gig waits for it and says so |
| 19 | The Mama Welles stand-in, and the whole fallback path behind it, deleted |
| 10 | The 1.2.0 bug pass: a fast-travel lock bound to the wrong state, a gig that never switched itself off, the guard spawn, a decline that answered, and (10k) a voice-only actor buried into the room below. 10h and 10i are the two still open |

`architecture.md` holds the same findings organised by subsystem rather than by
the question that produced them, and is the better read if you are looking for
how something works rather than how it was settled.

## For whoever maintains this

An item belongs here only once someone has spent effort on it; vague ideas go in
`design.md`. When an item closes, mark it closed in place rather than deleting
it.

---

## 0. The gig is PLAYED and WORKING: 2026-08-13

Playtest, end to end, fully voiced: *"Gig is perfect... Johnny seems great now...
glitch out is good... nothing's silent it all works"*, and after the last fix,
*"Mama welles work. it's all working."*

54 voiced clips, 11 scenes, no scripted captions, no known stalls. Every
mechanism this file used to list as unverified is confirmed in game: the
voiceover map, the player actor, `around_player`, the scene/script split for
Johnny, and the buried voice-only actor.

**The habits that earned their keep, for whoever picks this up:**

- **"Silent" and "quiet" are different bugs.** Ask which. Mama Welles produced
  three reports of one symptom, and each named a different subsystem.
- **If a line is blank or missing, read `red4ext\plugins\ArchiveXL\*.log`
  FIRST.** A bad localization resource reports there and nowhere else.
- **Send audio as one reel in script order**, not as N files. It is what made a
  voice bug diagnosable in a single listen.
- **A comment that closes off a route may be inference, not evidence.** One such
  comment cost this gig every spoken V line for months.

---

## 0b. RELEASE WORK: the only thing between this and a Nexus upload

Researched 2026-08-14. The in-game start is DONE: see
`architecture.md`, "The in-game start", which
carries the two base-game facts it gates on and the evidence for each. What is
below is everything else.

- ~~A real bug, one line to fix.~~ FIXED 2026-08-14. The `.archive.xl`
  registered `subtitles`, `vomaps` and `lipmaps` under all 19 locales but
  **`onscreens` only under `en-us`**, so a non-English player got working spoken
  dialogue, audio and lip sync, and raw LocKeys for the gig title, every
  objective, the contacts and the shard text. Unplayable in eighteen languages
  while looking perfect in testing, because testing happens in English. All four
  keys now register the same 19 locales.

  **Correction to this entry's own instruction, which said "fix in the
  generator, not the file": the `.archive.xl` is not generated**. Nothing
  writes it, `build-archive.ps1` only reads its filename to derive the archive
  name, and the "never hand-edit `source/wkit/raw/`" rule is about the `.json`
  resources the generators emit. The `.xl` is hand-authored source and editing
  it directly is correct.

  Check it rather than trusting memory: `onscreens` takes a list per locale
  while its three siblings take a scalar. Both forms are ArchiveXL's; the list
  form was kept because it was the one already proven working here.
- ~~THE ONLY CODE LEFT: the release script.~~ DONE 2026-08-14 - 
  `tools/build-release.ps1`. `.\tools\build-release.ps1 gig-01 -Version 1.0.0`
  writes `dist/NegativeBalance-1.0.0.zip`: 11 files, 2.01 MB, the three trees
  and nothing else.

  Three things it refuses to do, each of which fails silently otherwise: ship a
  wrapper folder (Vortex would install nothing, or one level too deep), ship
  `source/cet-dev/`, or ship anything under `base\`.

  **It does NOT rebuild by default, and it is the finding.** WolvenKit's
  packing is non-deterministic: the same raw tree packed twice gives the
  same 2338816 bytes and a different hash every time. So a rebuild can never be
  proven identical to the archive that was playtested. The script therefore
  packages what is already in `packed\` and **compares every file to the copy
  deployed in the game folder**: the one that was played. Plain files must
  hash-match; the archive is compared by size, because a hash match is not
  achievable. `-Rebuild` is there when you want fresh output anyway.
- **Verified on 2026-08-14 by testing as a new user would.** Everything except
  the mod and its four requirements was disabled in Vortex and CET was taken out
  of the loader entirely; the gig ran end to end. **That is the requirements list
  proven, not assumed.**
- **Not a blocker, but it belongs on the mod page:** the AI voices are disclosed.
  That is this project's own standing policy (`architecture.md`, "Voice"), and
  it is also a Nexus platform rule: their generative-AI guidelines name voices
  explicitly, and undisclosed use is grounds for moderation.
- **Debug stripping is one folder.** `source/cet-dev/` must not ship. The
  `.reds` are already clean, `Notify()` is player-facing HUD, not debug.
- **Requirements are four**: RED4ext, ArchiveXL, TweakXL, Codeware (plus
  redscript). NOT CET, NOT Audioware, NOT mod_settings.
- **The cooked mappin tables, SOLVED and confirmed in game 2026-08-14.** The
  mod used to ship a 4343-entry replacement of `03_night_city.mappins` /
  `.poimappins`. It no longer ships any base-game file: 141 files, none
  under `base\`. Pins anchor to base-game nodes in the game's own
  `always_loaded_*` sectors and ArchiveXL computes the position. No plugin, no
  new dependency, no load-order conflict, nothing to go stale on a game patch.
  `docs/map-pins-playbook.md` has the recipe, and `architecture.md` ("Three
  routes that fail, and how to tell them apart from the log") has the three
  routes that failed first, with the log line each one produces.

---

## 1. Standard subtitle styling: DONE, confirmed 2026-08-13

Playtest: *"Subtitle name styling is perfect and confirmed."*

**It was never built; it fell out of the scene conversion.** The workaround was
`scnDialogLineVisualStyle.alwaysCinematicNoSpeaker`, needed because a `regular`
line requires a speaker `GameObject` the subtitle system can reach and every
speaker used to be a voice-only actor a kilometre away. Once positional speakers
moved close and V got a player actor, every line had a reachable speaker, so
`regular` / `innerDialog` work and the name widget appears. Only
`AlwaysCinematicNoSpeaker` hides it (`subtitlesControllers.swift:169`).

**The generalisable bit:** a workaround can outlive its cause silently. This one
was still in the generator months after the thing it worked around had a proper
fix available. When a subsystem changes, grep for the workarounds it justified.

---

## 2. Voice

**Status:** route decided 2026-08-12, Wwise installed, nothing built yet.

### 2a. The integration route: DECIDED, and the earlier answer here was WRONG

**Scene lines are voiced through a mod-supplied voiceover map.** Not through
Audioware, and not through `customVoEvent`.

What this entry used to say. That Audioware cannot voice a scene line, therefore
"a voiced scene is one whose lines are driven from script alongside the scene" - 
had a true premise and a false conclusion. It only ever considered the Audioware
and `customVoEvent` angles. It never considered the path the game itself uses.

The three facts that settle it, all verified 2026-08-12:

1. **`ArchiveXL`'s `localization:` section accepts four keys, not two**:
   `onscreens`, `subtitles`, `lipmaps` and `vomaps`. (Source: its own
   `src/App/Extensions/Localization/Config.cpp`. Our `.archive.xl` currently
   declares only the first two).
2. **A voiceover map is a flat global registry.** `base\localization\en-us\
   voiceovermap.json` deserialises to a `locVoiceoverMap`: a list of
   `locVoLineEntry { stringId, femaleResPath, maleResPath }` and nothing else.
   **No scene, quest or actor scoping.** There are five of them, the plain one,
   `_1`, `_helmet`, `_holocall` and `_rewinded`.
3. **That `stringId` is the same number a scene line already carries** as
   `scnlocLocstringId.ruid`, and the same one our subtitle resource is keyed by.
   Proven by joining the two: subtitle `stringId` 2198303577515892736 →
   `1e81f174e64e2000` → `civ_mid_m_21_enus_25_00_afterlife_global_scene_f_
   1e81f174e64e2000.wem`.

So: ship a `.wem` per line, ship a vomap pointing our RUIDs at them, and declare
it under `localization: vomaps:`. The scene system then plays them natively.
Gender variants are picked by the engine. No script driver, no Audioware, and
`lipmaps` available later if lipsync is ever wanted.

**CONFIRMED IN GAME.** A mod-registered vomap IS consulted. For holocall lines
on 2026-08-12, and decisively for WORLD lines too.

Mama Welles was audible but "low and far, like almost cannot hear it" from a
speaker a kilometre away. That is distance attenuation, which proves the map
resolved her clip at all.

**AUDIOWARE IS NOT NEEDED AT ALL, and never was.** This entry used to reserve it
for the ~24 scripted-caption beats, on the grounds that nothing in the scene
system can voice a caption. True, and the answer was to stop having captions.
All of them were rebuilt as scenes on 2026-08-13 (2i), so the mod ships no
Audioware dependency and players install nothing extra.

### 2b. The vanilla VO corpus: BUILT, and it closed the reuse question

Reusing recorded game lines was the plan for V, Johnny, Mama and Nix. It does not
work, and here is the evidence rather than the opinion.

**The corpus is cheap to rebuild** (do not commit it: it is extracted game data,
same rule as `_anchor_cache`):

1. `unbundle` `archive\pc\content\lang_en_text.archive` (7 MB, 3087 files) and
   `convert serialize` `base\localization\en-us\subtitles` → 75,261 entries of
   `{stringId, femaleVariant, maleVariant}`.
2. `archiveinfo -l` on `lang_en_voice.archive` → 84,567 `.wem` paths. **The
   filename is the index**:
   `<speaker>_<questOrScene>_<f|m>_<stringId as 16 hex digits>.wem`.
3. Join on the hex of the stringId → **61,724 spoken lines with speaker, text,
   gender variants and audio path.**

Pool sizes: V 13,289 · Johnny ~2,500 · Mama Welles 149 · Nix 82. Directories are
`vo`, `vo_helmet`, `vo_holocall` (2,939 lines have a phone-filtered variant; V
has none, correctly, V is not the voice on the other end of the call).

**The result: 3 of the gig's 59 lines have a verbatim match from the right
speaker.** Character-similarity finds nothing usable.

The plot-carrying lines have no vanilla equivalent and never will: "It's a
production line.", "No money, no bodies.", "We know one.", "They always think
names beat bullets."

Rewriting the gig into whatever vanilla happens to own would destroy the
comic-verbatim rule. The design call, 2026-08-12: do not bend the dialogue,
generate our own.

To audition a candidate:
`unbundle lang_en_voice.archive -r "<hex>"` then
`export <dir> -o <out> -gp "<game>"` → Ogg. Duration is readable from the last
Ogg page's granulepos ÷ sample rate, no dependencies.

### 2c. The three vanilla lines we ARE keeping: CONFIRMED

They need no rewriting at all, because the comic already wrote them (it was made
from in-game screenshots, so some of its dialogue *is* vanilla dialogue). Point
the scene line's `locstringId` at the vanilla `stringId` and **emit no subtitle
entry of our own**. Vanilla's registration supplies both text and audio. Nothing
is shipped and nothing is redistributed.

| key | line | stringId (hex) | source |
|---|---|---|---|
| `b01` | "How's things, V?" | `30b57ed4cf7df000` | `nix_scene_nix_default`, has a `vo_holocall` variant, 1.537 s |
| `on1` | "Where." | `1a29d24a3944d000` | `v_mq035`, both body types |
| `on2` | "On my way." | `10c4df245528d000` | `v_q003`, both body types |

(Seven more takes of "Where." and four more of "On my way." exist if the chosen
one reads wrong; they are in the corpus).

**ALL THREE ARE BUILT**: `gen_scenes.add_line(..., vanilla_sid=...)`. Every
reuse is printed at generation time so the missing subtitle entry always reads as
a decision.

`on1` and `on2` landed 2026-08-13. The blocker recorded here was right: they were
`add_option` entries, and a hub option is UI text, not a spoken event, pointing
one at a vanilla stringId changes the button and plays nothing. What unblocked
them was V getting a player actor, which turned both options into real
sections carrying real `scnDialogLineEvent`s. Two lines of this gig are now
spoken by the actual V, both body types, with nothing generated and nothing
shipped.

### 2d. Who gets a voice: CLOSED, it was answered directly

Deferred 2026-08-12, settled 2026-08-13 when the design supplied voice ids for
Johnny, Nix, Mama Welles and both Vs. Everyone in the gig gets a voice. Ids are
in `BUILDING.md`; do not re-open the question and do not re-run the
"an original AI voice will not sound like Johnny" argument, he heard the
candidates and picked.

What remains is not a decision, it is conversion work: a line can only be
voiced if it lives in a `.scene`. See 2i.

### 2e. Prove the pipeline: FULLY CONFIRMED, experiment collapsed 2026-08-13

**Resolved.** The mod voiceover map is consulted for world lines as well as
holocall ones, and the only variable is distance.

Proof came from a different scene than the one built to test it. Mama Welles was
described as *"low and far, like almost cannot hear it"* from a speaker a
kilometre away. Audible at all means the map resolved her clip; quiet means
attenuation rather than routing.

`gig01_hoshino`'s two-actor experiment (`h01` buried, `h02` a visible duplicate)
was therefore never needed and is collapsed to one buried actor. Keeping the
duplicate would have been a visible second Hoshino for no remaining information.

The original two-way experiment follows.

### 2e-orig. Prove the pipeline: HALF CONFIRMED IN GAME 2026-08-12

**Elena's voiced lines PLAY.** The vomap route is real: a mod-registered
`locVoiceoverMap` is consulted, and a scene line resolves its audio from it with
no script driver and no Audioware. That was the whole unverified link in 2a and
it is now closed.

**Hoshino's did not**, and the cause is not the audio. Elena's lines are
`holocall=True`: 2D, through the phone. Hoshino's play from a world emitter,
and every voice-only actor in `gen_scenes.py` is parked at the scene marker plus
`(1000, 1000, -100)`: a kilometre away and a hundred metres down, so it does not
duplicate the NPC the player can see. Subtitles never cared about that. Audio
does.

`#q113_dvc_arasaka_estate_camera_010` turns out to sit 4.7 m from Hoshino's
actual spot (`find_pin_anchors`), so the marker was always in the right room - 
only the offset was wrong.

**Shipped as a two-way experiment**, because one thing is still
unknown: whether a *hidden* emitter is audible at all, or whether world lines
ignore a mod vomap. `gig01_hoshino` now has two actors:

| line | actor | why |
|---|---|---|
| `h01` | buried 2.5 m under the floor | the fix we want, close enough to hear, hidden |
| `h02` | standing at the marker, visible | the control; guaranteed audible if the mechanism works at all |

| heard | conclusion |
|---|---|
| both | keep h01's offset, delete the second actor |
| h02 only | burial is occluded, try a horizontal offset behind the player instead |
| neither | not a distance problem: world lines are not consulting our vomap, and the `_holocall` map is a separate registration |

There is a visible duplicate Hoshino during the scene. **That is a diagnostic,
not a design**. Collapse it back to one actor as soon as the answer is known.

### 2e-bis. Original placeholder-stage notes

Built and deployed 2026-08-12. Ten placeholder tones: Elena's 8 lines and
Hoshino's 2. Each cut to the length `gen_scenes` would have paced that line at,
and pitched by a hash of the line key so they are distinguishable by ear. Every
piece of the chain is exercised: `gen_voice.py` → Wwise → `.wem` → vomap →
`vomaps:` in the `.archive.xl` → `durations.json` → re-timed sections.

What to watch, in order of what it tells you:

| observed | conclusion |
|---|---|
| tones during Elena's call AND at Hoshino | the route works; go to 2g |
| Elena only | holocall lines resolve, world ones do not, suspect the emitter, not the map |
| Hoshino only | the `_holocall` vomap is a separate registration and ours is not standing in for it |
| nothing anywhere | read `red4ext\plugins\ArchiveXL\*.log` FIRST; then suspect the missing 16-byte `hash` chunk (see `gen_voice.py`) |
| subtitles vanish | the vomap registration broke the subtitle one, they are siblings under the same `localization:` key |

Also in this build, independently: **Nix's `b01` is the first reused vanilla
line** (2c). It is a separate mechanism from the vomap and can pass or fail on
its own. If you hear Nix say "How's things, V?" in his real voice, the reuse
route is proven too.

The `gen_voice.py` → `gen_scenes.py` ORDER MATTERS: the first writes the duration
sidecar the second paces from. Running them the other way round re-times to the
previous run's audio.

### 2f. Re-time scenes from real clip length

`tools/gen_scenes.py` paces every line with a character-count estimate
(`MS_BASE 1200 + 55ms/char`) because nothing is voiced. With audio,
`scnDialogLineEvent.duration` / `startTime` / `sectionDuration` must come from
the real clip or lines will cut off or drag. Feed measured durations in as a JSON
sidecar (line key → ms) produced when the audio is generated.

### 2g. Generate the voices: DONE

Every line is voiced. The voices are generated with ElevenLabs, disclosed on
the mod page, and subtitles are always on. `tools/gen_voice.py` turns a wav
into a `.wem` and a voiceover-map entry, and that half of the pipeline is the
same for any custom audio, whatever produced the wav.

The route went through several generators before settling. Those notes are
not kept here.

### 2i. Convert the caption beats: DONE 2026-08-13

All of them. `Gig01_Encounter.Line()` and `CCGig01LineStep` are deleted; the gig
has no scripted captions left and 52 voiced lines. Method and the table of what
became what are in `BUILDING.md`; the enabling discovery
(`scnWorldMarker.type = "Tag"` / `around_player`, which stages a scene at the
player) is in `docs/scene-playbook.md`.

**What is left is verification, not work.** Five of the new scenes depend on
`around_player`, which no mod is known to have used. Failure modes, in order of
how much they matter:

| symptom | means | next |
|---|---|---|
| the gig stalls at a beat | that scene never STARTED - the tag did not resolve | swap that one to a fixed NodeRef; V's position is roughly known for the two terminal beats |
| a line is silent but the gig continues | the scene ran, the actor did not stage | check the offset, then `red4ext\plugins\ArchiveXL\*.log` |
| Johnny pops out instead of glitching | the scene despawned him before the exit cue | the SCENE times that cue, 250 ms before its last section ends; check `stage_johnny(first, last)` names the right sections |

The old table of five beats and their entry points is gone with them. If a
conversion ever has to be undone, the shape it was undone FROM is in git.

### 2h. What has to be installed

Recorded in `BUILDING.md` under Audio toolchain so it sits with the rest of
the environment. Summary: Wwise 2019.2.15 (Authoring + Windows platform only,
no plug-ins, no SDK) for WAV to WEM. Nothing else. ArchiveXL is already present,
and Audioware is not a dependency.

---

## 2j. Lipsync: DONE, CONFIRMED IN GAME 2026-08-14

**Nothing in this section is open.** It is kept for gigs 02-04, because the
mechanism below is reusable and was expensive to establish.

Full account: `docs/architecture.md`, "LIPSYNC: the whole mechanism, and one gamble left
to test", and the entry that resolved it. The heading here said "ONE THING LEFT
TO TEST" for a day after the thing was tested; corrected 2026-08-14.

**Settled and reusable by gigs 02-04, do not re-derive:**

- The chain is `.anims` set -> `base\localization\<lang>.lipmap` (ArchiveXL key
  `lipmaps`) -> `scnActorDef.lipsyncAnimSet` -> the line's
  `female/maleLipsyncAnimationName`.
- **`lipmap.scenePaths[i]` is FNV1a64 of the scene's depot path** - all 3495
  vanilla entries verified. `sceneEntries[i].actorVoiceTags[j]` is parallel to
  `animSets[j]`.
- Vanilla's `resouresReferences.lipsyncAnimSets` name paths that exist in NO
  archive, so the lipmap must be the live channel.
- A `.anims` round-trips byte-identically through WolvenKit, but we ship none:
  the animation NAME is free-form, so a line just names an animation inside a
  vanilla set. `tools/gen_lipsync.py` casts by clip length; worst error in the
  gig is 270 ms over two lines.
- Rig mismatch does not matter - `generic_facial_lipsync_gestures.anims` is
  rigged to the player's head and played on arbitrary NPCs, and every lipsync
  anim in the game has the same 344 joints / 414 tracks.
- `scnAdditionalSpeakerRole.OnlyLipsync` hangs a line's lipsync on a SECOND
  actor. Vanilla uses it for V's third-person doubles.

### `type: Tag` IS DEAD: tested and proven 2026-08-14. Do not retry it

`IsPopulated(n"cc_g01_johnny")` was true at the moment `gig01_arasaka` ran
(`cc_g01_dbg_lip_johnny = 2` in the trace, 4 s before the scene) and the scene
still did not bind that body. **The scene system's `findInWorld` resolver does
not read the DynamicEntitySystem tag registry.** Our tag name, our timing and
our spawn were all correct; the mechanism is not there.

The dangling additional speaker, meanwhile, crashes at scene teardown - 
deterministically, 4.3 s after scene entry in both runs, to a tenth of a second.
`BRIDGE_SCENES` is empty; the machinery is kept but declares nothing.

That closes the reading table below without needing it. What remains open is one
step earlier, and it now has a diagnostic shipped for it:

### LIPSYNC IS DONE AND SHIPPED: 2026-08-14. *"Everything is perfect."*

Every Johnny beat is scene-owned, lipsynced, placed by the script and glitching
in and out: arasaka, terminal (p25 merged back in), shard_read, legend, graves,
kill, malware, bar. **Recipe: `docs/scene-playbook.md`, "THE SPLIT-OWNERSHIP
RECIPE"**. It matches the shipped code, not the first draft.

**Hoshino and Mama Welles keep voice-only speakers and get no visible
lipsync. That is not a TODO.** A scene actor exists only while its scene runs;
both of them must exist before anyone speaks (V finds and shoots Hoshino; Mama
lives in that bar). Nothing can be made to work there without changing what
those beats ARE.

*Corrected 2026-08-17: this said BURIED speakers, and Hoshino's is not buried
any more. Burying one under a fixed anchor put a body in the room below the
terrace, so his stands a kilometre away with 2D lines instead. See 10k, and 12
for Mama's, which still is. The point of this paragraph, that neither can be the
visible body, is unchanged.*

**DONE 2026-08-14**: the dead script path and the lipsync diagnostics are
deleted, ~360 lines out of `Gig01_Encounter.reds` plus their facts from the CET
menu. Compiles clean.

**The deletion paid for itself immediately.** Porting placement from
`SpawnJohnny` to `PlaceSceneJohnny` had dropped one line, `dev.orientation` on
the workspot device, so Johnny faced world-yaw-0 in every beat regardless of
where V stood. Most beats looked right BY LUCK; the two that did not were the
ones where V's facing is fixed by the furniture (the office desk) or by the
approach (over Hoshino's body). playtesting reported both on 2026-08-14 and the fix
was one line, sitting in a comment in the code about to be deleted. **When
porting a routine, carry over what its comments record, not only the code**,
and read dead code once before deleting it.

**Closed, both of them, playtest, 2026-08-14: *"No problem for johnny."***

- **No facial expression on the scene actor. WILL NOT DO.** The deleted
  `SpawnJohnny` took a preset as its fourth argument (7 = disgust for "Fucking
  Arasaka...") and `SetJohnnyFace` applied it via `AnimFeature_FacialReaction` - 
  category 3, idle from `ReactionComponent.SelectFacialEmotion`'s own table (3/7
  disgust, 3/1 aggressive). Nothing sets one now, the gig has been playtested
  through several times, and it never came up. Kept only because it is the one
  capability the script path had that the scene path does not, if a future gig
  wants it, that is the recipe, and it needs the GameObject `FindSceneJohnny`
  already returns.
- **`gen_lipsync` casts by LENGTH only.** Phonemes are borrowed from an
  unrelated vanilla line and it reads as real lip sync at conversational
  distance. Worst length error in the gig is 270 ms across two lines. Nothing to
  fix; recorded here so nobody "improves" it away.

### ANSWERED 2026-08-14: the lipsync data works. *"Perfectly lip synced"*

Confirmed in game on the scene's own visible Johnny. Everything below this line
is settled and reusable by gigs 02-04; what is left is not lipsync at all, it is
the placement problem this gig already had.

**THE ONE REMAINING TASK: put the words on the body you can see.** A scene actor
lipsyncs; the body the player looks at in eleven of fourteen scenes is spawned
by `Gig01_Encounter`, and the scene cannot reach it.

| route | status |
|---|---|
| `findInWorld` + `type: Tag` | DEAD. Tag registered, actor unbound, crashes at teardown. Do not revisit |
| **scene spawns, script teleports** | LIVE. `TeleportationFacility.Teleport(obj, pos, angles)` and the `FindMamaWelles` targeting-query find are both compiler-confirmed |
| leave it | the safe floor, already built: lipsync data everywhere, visible only at `gig01_bar` |

**Solve the EXIT before moving the body.** The script owns Johnny's calibrated
0.25 s `johnny_teleport_start` glitch-out, which approved in playtest by ear across
three values; a scene-spawned Johnny is despawned by the scene and would POP.
Two untested candidates: `scnSpawnDespawnEntityParams.keepAlive = 1` so the
actor outlives the scene and the script can dissolve him as it does today, or a
`scneventsSocket` firing a quest node inside the scene shortly before its exit.
Neither is tried; the first is one field.

Also unsolved and inherent: **he materialises at the `around_player` marker,
which lands behind V.** The teleport fixes where he ends up, not where he
appears, so expect a visible hop unless the move happens before he renders.

### The question this answered (kept for the reading table)

Nothing has tested this yet. Every mouth in the gig belongs to a buried actor,
so "no mouth moved" was the expected result either way. `build_arasaka` now
ships a deliberate second Johnny - the scene's own, solid
(`JOHNNY_SOLID`), standing at the marker, and he is the SPEAKER; the script's
see-through one still appears beside V.

**Run it from the CET dev menu: "LIPSYNC TEST: play Johnny's arasaka line HERE,
NOW"** (fact `cc_g01_dev_lipsync`). No replay needed - it enters the scene where
V is standing and its exit socket goes nowhere, so it cannot advance the quest.
He waits 4 s, says one line, waits 3 s; he may be BEHIND you, because an
`around_player` marker cannot be aimed.

| observed | conclusion | next |
|---|---|---|
| **the SOLID Johnny's mouth moves** | the whole chain works - lipmap, RUID key, borrowed animation, the lot | collapse the duplicate, then solve one-body placement (below). This is the win |
| both stand there mute | the data does not reach the animation system | the direct `resouresReferences.lipsyncAnimSets` ref is the suspect - vanilla's are dangling, so the lipmap may be the only channel, and it is keyed by `voicetagId`. Try a scene whose actor voicetag is unambiguous, or drop the direct ref entirely |
| the solid one never appears | the `around_player` marker put him somewhere unreachable | not a lipsync result - re-run with the offset raised, or accept that only a fixed-anchor scene can host this test |
| anything goes silent or crashes | not expected - nothing else changed | `CrashInfo.json` first, then the ArchiveXL log |

**Collapse the duplicate as soon as it has answered.** A visible second Johnny
is a diagnostic, not a design - `build_hoshino` shipped exactly this shape in
2026-08-12 and was collapsed the moment the answer arrived.

### THE BODY DOUBLE CRASHED THE GAME (the account, kept for the reasoning)

Played, crashed 3 s into `gig01_arasaka` - the first bridged scene. Evidence and
how it was located: `docs/architecture.md`, "the body double CRASHES the game".
Both halves
of the bridge are off together, because they are one switch and it is not
established which of them did it:

1. the `findInWorld` + `actorRef.type = Tag` actor, or
2. `additionalSpeakers` naming an actorId whose actor never acquired - a null
   performer dereferenced when the line plays, which fits the timing exactly.

**Do not re-derive the false comfort that led here.** Vanilla's `OnlyLipsync`
doubles (`v_male_tpp` / `v_female_tpp`) are `spawnDespawn` actors that always
exist, so shipped data contains NO example of an additional speaker that fails
to acquire. "Vanilla has a field for it" was read as "vanilla does this", twice
in one change, and the half that could crash did.

**Where a future attempt should start, in order of cheapness:**

- **Separate the two halves.** Ship the Tag actor with an EMPTY
  `additionalSpeakers` and see whether it still crashes. That is a one-line
  change in `add_body_double`'s caller and it settles which half is fatal - it
  is the experiment that should have been run first and was not.
- **If (2) is the culprit**, the bridge is alive: any acquisition that CANNOT
  fail is then safe. Mama Welles already has one - `spawnSet` / `#mama_welles`,
  copied from `mama_welles_default.scene` - and it never got tested because the
  crash is four beats earlier. Try the epilogue alone.
- **If (1) is the culprit**, `Tag` acquisition is dead and the remaining idea is
  `DynamicEntitySystem.AssignTag` on a found NPC plus a spawnSet-style
  acquisition, or moving the visible body into the scene (tried 2026-08-13,
  broke placement - see item 3).

### ANSWERED: yes. The lipsync data works: confirmed in game 2026-08-14

The table below was the decision tree while this was unknown. The row that
matched was the first one; it is kept because the other rows say what to check
if a FUTURE gig's mouths stay shut.

The build now differs from the last known-good gig by lipsync data ONLY: the
`.lipmap`, the `resouresReferences.lipsyncAnimSets` refs, a real `voicetagId` on
each speaking actor, and an animation name on 16 lines. Verified after
regenerating - no `OnlyLipsync` anywhere, every actor back to `spawnDespawn`.

| observed | conclusion | next |
|---|---|---|
| **Johnny's mouth moves at the bar** ("Good. Let her sleep.") | the whole chain works; only the visible-body bridge is missing | go at the bridge with the split experiment above |
| everything plays, no mouth moves anywhere | the data resolves but is not applied, or is not resolving at all | suspect the direct `lipsyncAnimSets` ref being ignored in favour of the lipmap, whose key is the actor's `voicetagId`. (The `cc_g01_dbg_lip_*` facts this row used to send you to are deleted, they answered their question and the answer is the banner above). |
| **it crashes in `gig01_arasaka` again** | lipsync data itself is fatal, and the bridge was never the whole story | strip it: revert `gen_scenes.py`'s lipsync hunks and drop `lipmaps` from the `.archive.xl`. Then this is a written finding, not a feature |
| Hoshino or Mama go SILENT | the new `voicetagId` on their actors (was 0) | revert just that - the one field this change touched that audio could plausibly care about |

### ONE BODY INSTEAD OF TWO: the question, and it has two real answers

*"Are you sure there's no way to spawn the actual body in the correct position
compared to V by retrieving more data so we don't need both bodies?"*
(2026-08-14.) He is right that two bodies is the smell, and there are two routes
out. Both are now backed by a compiler probe rather than by reasoning.

**Route 1. If tag acquisition works, the second body was never needed.** The
double is a `findInWorld` actor that receives lipsync; make the SPEAKER that
same `findInWorld` actor and there is one body: script-placed, scene-spoken,
lipsynced. The double is only the SAFE way to ask the same question, if
acquisition fails, a double loses lipsync while a speaker loses the line's audio,
subtitle and name. So: prove it with the double, then collapse to one actor.
That is exactly what the `gig01_arasaka` build tests.

**Route 2. If tags do NOT resolve: let the SCENE spawn him and the SCRIPT move
him.** The scene already does this at the bar, so the machinery exists
(`add_johnny` + `add_workspot_node` + `fire_workspot`). The two missing pieces
are both confirmed, not assumed:

- **Finding a scene-spawned actor from script** - the `FindMamaWelles` pattern
  already in `Gig01_Encounter.reds`: a `TargetSearchQuery` walking
  `GetTargetParts` and matching `puppet.GetRecordID()`. There is exactly one
  `Character.Silverhand` in the world, so the match is unambiguous.
- **Moving him** - `GameInstance.GetTeleportationFacility(game)
  .Teleport(obj: ref<GameObject>, pos: Vector4, angles: EulerAngles)`.
  **Confirmed by the compiler 2026-08-14.** Note `TeleportPuppetToPosition`,
  the obvious guess, does NOT exist - `check-scripts.ps1` rejects it.

Cost of route 2, so nobody starts it thinking it is free:

- the workspot has to be re-fired after the move, since he renders only in one
- the exit FX moves back to the script, which already owns that code
- the failure mode becomes LOUD: a Johnny in the wrong place, rather than a
  mouth that does not move

Do it only if route 1 is dead.

**Not spent, but it exists:** `DynamicEntitySystem` has
`AssignTag(id, tag)`, `GetTagged`, `GetTaggedID(s)` and `IsPopulated` - the full
native class is declared in `red4ext\plugins\Codeware\Scripts\Codeware.Global
.reds` line 43422, which is where to look before guessing any of those names.
(`GetEntityIDs`, the obvious guess, does not exist). If tag acquisition works
from script but not from a scene, tagging the REAL Mama Welles is a one-line
experiment.

## 3. Johnny's ghost beside V: BUILT AND CONFIRMED 2026-08-13

**Status: done.** He appears beside V at six beats, see-through, correctly
placed, speaks with his own voice and glitches out on the calibrated 0.25 s cut.
Playtest: *"Johnny seems great now... glitch out is good."*

**SUPERSEDED 2026-08-14. The split below is now SCENE-owns-the-body,
SCRIPT-places-it.** The table described a script-spawned ghost with a buried
scene actor supplying the words, which worked and could never lipsync: **lipsync
lands on the line's SPEAKER, and only a scene can own one.** There is one Johnny
per beat now, he is the scene's, and `Gig01_Encounter.PlaceSceneJohnny` moves
him. The current recipe is `docs/scene-playbook.md`, "THE SPLIT-OWNERSHIP
RECIPE"; the shape that was superseded is below for the record.

| | owner, 2026-08-13 | owner, now |
|---|---|---|
| the body | script (`SpawnJohnny`, deleted) | the SCENE, as the line's speaker |
| placement | script, player-relative maths | script, same maths, in `PlaceSceneJohnny` |
| facing | the workspot device's `orientation` | unchanged, and the one thing the port forgot |
| visibility | the script workspot + `silverhand_default` | the script workspot, on the scene's actor |
| exit | `johnny_teleport_start`, delete 0.25 s later | same FX and same 0.25 s, but the SCENE times it |
| voice + subtitle | a scene actor buried 2.5 m, `inner=True` | the same actor, now visible and lipsynced |

Do not move placement into a scene. It was tried on 2026-08-13 and put him
behind V: a scene `spawnOffset` is in the marker's frame, `ahead`/`aside` are in
the player's, and an `around_player` marker's rotation is not knowable. Vanilla
does not do it either (`sts_pac_cvi_02_johnny.scene` gives its actor its own
spawn-marker node and a zero offset). **That is still true and is why the script
keeps placement in the split above.**

*Half of it stopped being true on 2026-08-16. An `around_player` marker's
rotation IS knowable: five runs measured +Y as forward and +X as right in V's
own frame, so a horizontal offset can be aimed and `yaw_to_face_player` computes
the facing from it. See "What it fixes" further down this section. What survives
is the practical split, since the script already holds the placement maths.*

The research below is what got him on screen and is kept for gigs 02-04.

Everything needed is shipped data. Headlines:

- **`Character.Silverhand`**: confirmed four independent ways.
- **`appearance: "silverhand_default"`** buys the whole see-through, rim-lit,
  glitching look. No status effect, no runtime toggle.
- Reference scene: `base\open_world\street_stories\heywood\glenn\
  sts_hey_gle_04\scenes\sts_hey_gle_04_johnny.scene`. Its quest side is a single
  `questSceneNodeDefinition`.
- **Line styling `innerDialog`** + `Vo_Expression_InnerDialog`, which is what 20
  of 25 Johnny scenes use, and it shows his name, so this doubles as the fix for
  item 1.

**Plan the workspot as part of the job, not as polish.**
`phantomVisibleStates` is `["RootMotion", "Workspot"]`, which suggests the
phantom renders only in those states. A Johnny in a plain idle could be
**invisible**. Unverifiable offline (native, no scripted API). Every vanilla
scene that spawns him follows immediately with a
`questUseWorkspotNodeDefinition`. Whether a mod-authored `worldWorkspotNode`
resolves as a NodeRef is untested, and mod-sector marker nodes already fail for
map pins, so prefer reusing a base-game workspot NodeRef, found the same way pin
anchors are.

Also copy from vanilla:

- `interruptionScenarios` with
  `scnCheckSpeakersDistanceInterruptCondition { Greater, 6 }`, so the scene
  pauses if V walks off. We emit an empty list: right for a distant speaker,
  wrong for one standing beside V.
- a `questCameraFocus_ConditionType { inverted: 1 }` wait, so he does not
  visibly pop out.

**Ration him.** The comic gives him pp. 11, 28, 30, 43, 45 and 63, but he is a
commentator, not a companion. Best spots: after Elena's call, over Hoshino's
body, and the last line at El Coyote. If only one can be staged reliably, spend
it on the ending: that is the emotional close the gig is built toward.

Neither existing mod is a route: AMM spawns a solid opaque posable body with
no dialogue, Here's Johnny recycles vanilla voice lines and ships no source.
No public mod renders a see-through Johnny.

---

## 3b. Johnny: the workspot: PLAYED AND CONFIRMED 2026-08-13

**It works.** Playtest: *"Johnny seems great now... glitch out is good."* The
script route renders the see-through apparition via `PlayInDeviceSimple`, and
`johnny_teleport_start` + a 0.25 s delete gives the vanish. The reading table
below is spent. The answer was "all visible", but the mechanism notes are kept
for gigs 02-04.

## 3b-orig. Johnny: the workspot: the pre-playtest notes, kept as reference

**Superseded by 3b above, which is the played-and-confirmed version.** Nothing
here is open; the heading said "NOT YET PLAYED" until 2026-08-14, two days after
it was played. Method detail is in `scene-playbook.md` ("THE FIX" and "The
script route").

### What ships now

| beat | route | appearance | workspot |
|---|---|---|---|
| after Elena's call | dynamic spawn beside V | `silverhand_default` (ghost) | script, `PlayInDeviceSimple` |
| Hoshino's lounge | scene actor | `silverhand_default` (ghost) | scene, `playAtActorLocation` |
| El Coyote (the close) | scene actor | `silverhand_riot__not_blendable` (solid) | scene, `playAtActorLocation` |

**The appearance split is the experiment, not indecision.** Visibility is gated
by STATE, the see-through look by APPEARANCE, and they are separate mechanisms.
The blendable appearance renders nothing unless the phantom system drives it, so
it only works if the workspot lands; the blendable-free one renders regardless.
Two ghosts test the hypothesis by two independent routes, and the solid one
guarantees at least one Johnny on screen. Placed on the epilogue deliberately,
because that is the last line of the comic and does not get to be the experiment.

### ANSWERED: the workspot IS the gate

The experiment ran and the hypothesis held: **a workspot is what makes the
apparition render**, because `phantomVisibleStates` is `["RootMotion",
"Workspot"]`. A body with no workspot is both invisible and
**untargetable**, so a script cannot even find it to place it, which is the
deadlock that looks like "he vanished".

The `cc_g01_dbg_johnny` / `_ws` facts that measured this were deleted on
2026-08-14 with the script-owned spawner. Their answers are above; if a future
gig needs the measurement again, the shape was 1 = never resolved, 2 = the call
was made, 3 = called but not in a workspot, 4 = in a workspot.

Swapping ghost→solid is one constant per scene in `tools/gen_scenes.py`
(`JOHNNY_GHOST` / `JOHNNY_SOLID`); the machinery does not change.

### Knobs that exist but are deliberately untouched

None of these is open work. The gig plays end to end with all three as they
are. They are listed so nobody thinks they were overlooked.

- The animation is `johnny__stand_ground__stand_around__02`, picked off a survey
  of all 27 shipped Johnny scenes. It reads fine in every room. If a future gig
  wants another, two vetted alternatives are at `WORKSPOT_JOHNNY` in
  `gen_scenes.py`.
- `interruptionScenarios` is deliberately still empty, see the playbook. Copying
  vanilla's would break every scene here while the other speakers are voice-only
  actors a kilometre away.
- The `questCameraFocus_ConditionType { inverted: 1 }` wait (so he never visibly
  pops out on camera) is not built. playtesting settled the underlying question
  himself, *"it's ok that Jonny disappers and reappers"*, so this is polish
  nobody has asked for.

### CORRECTION to what was written earlier about `.ent` editing

An earlier note in this file claimed `compiledData` is authoritative and that
hand-editing the `components` array is what crashed the game. That was wrong,
and it was asserted without testing. Four controlled round-trip experiments
(2026-08-12) establish the opposite:

- `compiledData` is a RedPackage buffer mirroring `components` exactly - chunk 0
  is the root entity, chunks 1..N are the components in the same order, plus a
  CruidDict mapping chunk INDEX to CRUID.
- **`components` is the master. WolvenKit regenerates `compiledData`, the
  CruidDict and every handle from it on write.** Deleting the phantom component
  from `components` alone produced a fully consistent 104-component file with no
  dangling handles.
- Editing `compiledData` instead throws `ArgumentOutOfRangeException` and emits
  **no file at all** - so a build script that does not check for a missing output
  silently ships a stale archive.
- A no-edit JSON round-trip is byte-identical, so the pipeline itself is sound.
- Vanilla `johnny.ent` is 29,943 bytes, not 500 KB. The big number was the
  JSON representation.

So why our build crashed is UNRESOLVED. Do not repeat the edit assuming it is
safe, and do not repeat the earlier explanation assuming it is true. If the
entity route is revisited, redo it through the CLI and diff the output.

Also verified, and it closes an option that sounded promising: **ArchiveXL
cannot delete a component.** Its `MergeComponents` only replaces (match on
`name` + `id.unk00`) or appends. It CAN replace `PhantomEntity7436`
(id 2201504208988090368) with a different component of the same name - untested,
and of limited use since the state enum has no "always visible" value.

### Two findings that should decide the approach

**Every working Johnny in every published mod is a WORKSPOT Johnny.** Deceptious
places him at guitars, record players, a motel bed, a Dogtown dance spot and a
car seat - never free-standing, never walking. He appears never to have fought
the phantom component because he never triggered it. That is the strongest
available evidence that the workspot route is the intended one.

**Nobody has ever published the see-through apparition.** Zero hits for
`phantomVisibleStates` or any mod deliberately using the phantom component;
community demand runs the opposite way (three separate mods strip Johnny's
glitch FX). If the workspot route yields the real apparition, this gig would be
the first to do it - which is a reason to try, and a reason not to expect
someone else's recipe to exist.

**Visibility is gated by STATE, not appearance.** That is why blendable-free
appearances changed nothing: two separate mechanisms. The see-through look lives
in the mesh appearances (`blendable` / `default_blendable`), which is what the
phantom system blends to once a visible state is satisfied. AMM's Johnny is solid
*by choice* - it deliberately selects the `not_blendable` variants.

Note `MoveOnSpline` is a third, UNUSED gate: Johnny lists only RootMotion and
Workspot, but the enum has three values.

**Do not redistribute another mod's `silverhand.ent`.** Check the licence of
anything you ship; an assumed licence is not a licence, and plenty of popular
mods carry none at all. The recipe is reproducible clean-room from Takemura's
entity if it is ever needed.

### Evidence that the quest/scene route is right (survey, 2026-08-12)

Deceptious places Johnny in five apartments AND in a moving vehicle, fully solid
and normal-looking, using no custom entity at all:

- **The Passenger** ships a 14 KB `.archive`. That cannot contain an entity,
  mesh or appearance - it is pure quest graph referencing the base-game record.
- **Here's Johnny** is 298 KB, two files, no `.reds`, no CET, no TweakXL. Its
  behaviour is a questphase + scene + workspot fingerprint: "spawns at one of
  three spots", guitar playing "similar to the iguana & cat event in H10" (a
  workspot animation), interaction points wired to choice nodes, and reused
  base-game VO.
- Both mods' pages, changelogs and bug tabs contain zero reports of Johnny
  being invisible. Here's Johnny has 0 bugs filed.

So a scene/quest-instantiated Johnny renders. Our problem is the spawn path, not
a missing component.

**Invisibility is per-variant and per-spawn-path, not a property of Johnny.** The
redmodding wiki's AMM guide says of `johnny_mirror`: *"The spawned Johnny will be
invisible, you'll need to scan his feet shadow"* - that is the mirror-scene
variant, dynamically spawned outside its scene. Meanwhile AMM's ORDINARY Johnny
spawn is visible: its appearance addon tells users to "spawn Johnny Silverhand,
make sure he's in the center of the screen and use the Scan tab", which you
cannot do to something you cannot see.

**Expect SOLID, not see-through.** Vanilla's apparition look is a separable FX
layer over an otherwise ordinary solid character - the "Glitch Effect Removal"
mod strips it with a single archive. Deceptious's Johnny looks completely normal
because he is the same solid character with the FX layer untouched. So "he
appears at all" is the win; the glitch look is a separate, later question.

`gamePhantomEntityComponent` is publicly undocumented - it appears in the
wiki's component list as a bare name with no explanation anywhere. Our own dump
of the real `.ent` files is ahead of anything published, so do not expect to find
an answer by searching; read shipped data.

## 3c. UNKNOWN CALLER → Elena Ortega: CLOSED, will not do

**Decided 2026-08-12 (playtest): leave it as it is.** Keeping the research below
because the "why not" is the useful part, but this is not a task any more - 
do not reopen it without a new reason.

The deciding trade: the only workable route costs a permanent "Unknown
Caller" entry in V's contacts list, and Elena never calls again, so nothing ever
corrects it. That is a lasting wart for an effect that lands once for a few
seconds. The subtitle-reveal half alone is worse than doing nothing, her
subtitle reading "Unknown Caller" under a header reading "Elena Ortega" is a
visible contradiction rather than a missing flourish.

Also: the portrait already falls back to the unknown-caller image
(`RequestAvatarOrUnknown`, our contact has no avatar), so the call reads as a
stranger regardless. A quest handing the player a contact before the caller
introduces themselves is ordinary game convention.



the request (2026-08-12): Elena's call should show UNKNOWN CALLER while it
rings, then become "Elena Ortega" once she says her name, precisely how
the comic plays it.

**There is no redscript hook.** Researched and settled; do not re-search:

- The displayed name is `JournalContact.GetLocalizedName(journalMgr)` - 
  `public final native`, so unwrappable.
- Every consumer is `final` too: `IncomingCallLogicController.SetCallInfo`
  (the ringing UI), `HoloAudioCallLogicController.StartAudiocall` /
  `ShowIncomingContact`, and the `hudPhoneAvatarController` equivalents.
- The two call sites are `newHudPhoneGameController` lines 956 and 1071, both
  inside `final` methods.
- Even with a hook, the name is written once when the call starts, so a
  mid-call swap would additionally need a forced repaint.

The portrait is already right for free: `RequestAvatarOrUnknown` falls back to
the unknown-caller image because our contact has no avatar.

Three ways forward, none of them free:

1. **Contact named "Unknown Caller"**: header is canon for the whole call
   (she IS unknown caller throughout the comic). Cost: she stays "Unknown
   Caller" in the contacts list for the rest of the playthrough, and she has no
   later calls to fix it.
2. **Two scene actors**: a `Character` record named "Unknown Caller" speaks her
   first line, the named record speaks the rest, so the *subtitle* does the
   reveal. Costs nothing structural and works today. The phone header still says
   whatever the contact says, so pair it with (1) or accept the mismatch.
3. **Leave it.** Her name is on the call UI from the ring; the reveal is only in
   her dialogue.

Recommendation: (1) + (2) together. Header reads UNKNOWN CALLER throughout,
subtitle changes from "Unknown Caller" to "Elena Ortega" on her introduction.
That is the comic's staging and needs no UI hooks at all. Needs the design call on
the contacts-list cost.

## 3d. Nix's call as a real VIDEO holocall: CLOSED, will not do

**Decided 2026-08-13 (playtest): skip it, and the code is removed.** Keeping the
research below because the "why not" is the useful part, but this is not a task
any more.

### The deciding reason: video and vanilla's dialogue options are the same switch

`questTriggerCallRequest` has no `prefabNodeRef`, so a script-issued Video call
points at a studio that was never staged and **hard-crashes the game the moment
the player answers** (docs/gotchas.md #10). The only route to a real video feed
is therefore to let vanilla's own per-contact holocall phase own the call.

Handing the call to vanilla, though, hands over all of it, including Nix's
standard small-talk dialogue options, precisely the clutter already
rejected in 3e. There is no version of this that takes the video and leaves
the options. One switch, both consequences.

So a static avatar is not a defect to be fixed; it is the price of not having
vanilla's conversation on top of ours. It is also the right look for Elena, who
is UNKNOWN CALLER in the comic.

### What was removed

`Gig01_Holocall.StageHolocallStudio`, `UnstageHolocallStudio`,
`HoloActivateFact`, the `questPhoneCallMode.Video` branch, and the dev fact
`cc_g01_call_video` (also gone from the CET menu). Every call is Audio, with no
flag left to turn Video back on by accident. A switch whose only outcomes were
"crash" or "vanilla's options" is a hazard, not an option.

The research that produced them follows.

## 3e. Vanilla dialogue options during our beats: CLOSED, will not do

Mama Welles offers her normal conversation right through the epilogue, and Nix
offers two small-talk options during our call. **Decided 2026-08-12 (playtest):
leave both as they are.**

Neither is load-bearing: the epilogue fires on PROXIMITY, not on the player
picking an option, so our scene always plays. It is clutter, not a fault.

**What was tried and does not work, do not rebuild it:**

- `InteractionSetEnableEvent { enable: false }` queued on the NPC. This is
  vanilla's own mechanism for interaction prompts (`VehicleComponent
  .ToggleInteraction`, `vehicleComponent.swift:2594`, uses it for a car's trunk
  and hood) and it does switch those off. It does not touch an NPC's
  dialogue. Removed from the code entirely, because a failed re-enable would
  leave a base-game NPC mute for the rest of the save - real risk, no benefit.
- Holding our beat back while a choice hub was on screen
  (`UIInteractions.DialogChoiceHubs`, vanilla's `AreChoiceHubsActive` test).
  This WORKED and was far worse: it stranded the gig at the bar, because the
  menu never cleared and Johnny never appeared. **Never gate quest completion on
  a presentation concern.**

Nix's options are structural: he is a base-game *callable* contact, so a real
call to him offers his standard conversation. Nothing short of making the contact
non-callable would hide them, and it is a persistent change to a base-game
contact for a cosmetic gain.

If it is ever revisited, the one untried idea is swapping the epilogue to our own
**stand-in** Mama, who has no vanilla dialogue at all. Rejected for now because
it risks two Mama Welles in the bar during the final beat of the gig, which is a
much more visible failure.

## 4. Housekeeping

- **The source `.archive.xl` needs committing.** `.gitignore` had a bare
  `*.archive.xl` that swallowed the hand-authored file in `source/wkit/raw/` - 
  where the journal, quest-phase parents and the localization/subtitles
  registration are declared. Fixed and now untracked; a fresh clone before this
  would have built a mod with silently blank scene dialogue.
- `design.md`'s dialogue section is a draft with `[REWRITE]` markers, not the
  source. The story's own script is the source: keep one authoritative text for
  every line (for this gig, the comic transcript) and diff the generators
  against it. Three of four conversations had drifted from it before anyone
  checked.
- Gigs 02-04 are not started. Everything in `docs/*-playbook.md` is written to be
  reusable by them. The generators are no longer gig-01-specific: the
  builders moved to `tools/questkit/` on 2026-08-16 (scenes, quest graph, journal
  and map pins), each taking a `configure(...)` call for one mod's paths and
  naming, so gig 02 imports them instead of forking about 1,930 lines. What is
  still outstanding there:

  - `gen_voice.py` and `gen_lipsync.py` keep their machinery inline. Neither can
    be verified by regenerating and diffing on a machine without Wwise, and
    `gen_lipsync` currently exits 1 anyway (see below), so both were left alone
    rather than refactored blind.
  - The gig-01 anchors are stated twice, in `gen_scenes.py` and
    `gen_questphase.py`, with three comments warning they must be kept in step.
    Fold them into a per-gig config module when gig 02 gives that config a
    second consumer to be shaped by.
  - `shared/scripts` is still empty. Extracting the generic redscript helpers out
    of `Gig01_Encounter.reds` (spawning, hostility, scene-Johnny placement,
    notifications, proximity tests: roughly 500 of its 2,567 lines) WOULD change
    a shipped file, since `.reds` ship as source. `conventions.md` already
    settles the mechanism: vendor per mod at build time under the mod's own
    namespace, so it never becomes a runtime dependency.

- **`gen_lipsync.py` cannot be re-run: it exits 1 on its own guard. CLOSED
  2026-08-18, and it was already fixed.** The guard was repaired on 2026-08-16,
  when it stopped reading `dynamicEntityUniqueName` and started reading
  `actorName`, which every actor carries. What was missing was the proof this
  entry asks for, and it has now been produced: `python tools/gen_lipsync.py`
  runs clean and rewrites `lipsync_picks.json` byte-identically, 16 lines across
  10 scene/actor pairs. The account of the fault below is kept because the shape
  of it generalises. Original entry:

- **`gen_lipsync.py` cannot be re-run: it exits 1 on its own guard.** Pre-existing,
  confirmed on pristine `HEAD`. `_check_actor_names` reads
  `spawnDespawnParams.dynamicEntityUniqueName` off every scene actor, but Mama
  Welles is acquired by `add_spawnset_actor` (spawnSet, `#mama_welles`), which
  does not populate that field, so her name reads as `None` and the guard
  rejects a picks file that is correct. Nothing shipped is affected: the
  committed `lipsync_picks.json` predates the regression and the gig is
  lipsynced properly in game. The fix is to teach the guard about spawnSet
  actors, and the proof is that re-running then rewrites `lipsync_picks.json`
  byte-identically.

## 5. Refinements from playing the finished gig: BUILT AND PLAYED

All three built the same day they were decided, and all three have since been
played. Details and reasoning: `docs/architecture.md`, entry "the three refinements from
playing it". Nothing here is open.

### 5a. The way-in pin: DONE

`enableGPS` is per-pin now (`NO_GPS` in `gen_journal.py`); `pin_wayin` is the
only member, so the marker stays put and the road route is gone. the
instruction was to remove the navigation, not move the rock, and his question
("is that really the standard?") is answered in `map-pins-playbook.md`: of 4277
vanilla quest pins, 131 turn GPS off, and the only two street-story pins that do
are on `sts_cct_dtn_04`'s `clear_out_roof`.

**CLOSED 2026-08-14, Playtest: *"pin hoshino and pin malware are good."*** They
are inside the estate grounds and could have taken the same flag; they were
offered and he judged them fine as they are. Do not "fix" them.

### 5b. Compound guards: DONE

`SetHostile` / `MakeHostile` mirror `SetNeutral` / `MakeNeutral`, retry included;
`SpawnSquad` threads the `EntityID` it used to discard and applies them to the
compound squads only. Records were not swapped. The two tiers look different on
purpose.

**If it does not take:** the next thread is whatever security-area or reaction
preset the estate records carry and the `sts_*` ones do not. Setting the
attitude group AND the attitude towards the player is already both halves of
what vanilla does, so a failure here means detection, not attitude.

### 5c. The Nix thread: DONE, and the shard is real

The shard is a genuine shard, read through the game's own reader, after playtesting
overruled the cheaper terminal-document plan: *"due to the dialogue, we need to
have the shard... let's do it properly"*. It cost far less than expected, because
**a shard's text is a journal entry, not an item**: see
`computer-ui-playbook.md`, second half, which is written for gigs 02-04 to reuse.

**THE COMIC-VERBATIM RULE HAS BEEN BENT FIVE TIMES. THIS IS THE LIST.** All five
came from playtesting, all on 2026-08-13, all after playing the beat in question. The rule
still holds everywhere it is not listed here. A lift is granted, never inferred.

| # | what changed | from | to |
|---|---|---|---|
| 1 | V's ask, Nix brief call (p26) | "Need to know where they are." | "Someone's signing off on every one of these." / "Find me the name. And how we make it stop." |
| 2 | V at the shard (p24) | "So that's where we fit." | "They're not sending their own. They're paying mercs." |
| 3 | Nix's callback (p29) | "Hoshino's the choke point." | "Arasaka pays mercs to flatline debtors after insuring them." / "One exec signs off on all of it. Hoshino." |
| 4 | V's last line (p63) | "She'll never know." | "She'll never know how many people died for a clean ledger." |
| 5 | V on p25 | "I need a netrunner." + two lines CUT | "We need a netrunner to find who's responsible." |

The reasoning is one reasoning, kept because it predicts which
lines will need it: **a comic can leave the reader to close a gap, because the
page they need is still in their hand. A player has spent sixty pages' worth of
gig since.** Every one of the four is a line whose referent had gone cold - 
"where they are", "where we fit", "you were right", "she'll never know".

Untouched and staying that way: Johnny's lines, the terminal exchange, the
estate, Mama Welles, and Nix's remaining lines. The invented `"On my way."`
**stays**: an explicit design call; do not remove it later for not being in the comic.

**Not spent, but it exists:** a real TweakDB shard ITEM, one V
could carry, drop and re-read from his backpack, was never built, because the
reader does not need one. If a future gig wants the item as well, the missing
piece is a vanilla shard's record id + its `ItemSecondaryAction`. **The record
id part of that is WRONG and was corrected 2026-08-14:** item TweakDBIDs sit in
the sector's `instanceData`, e.g. `Items.generic_hanako_flowers_shard` on the
office desk. Read the world data, do not guess and do not assume it needs a
live probe.


## 6. The shard prompt - UNSOLVED, deliberately parked (2026-08-14)

The shard on the office desk is read on proximity, not with an [F] prompt,
because a prompt on a mod-placed object could not be made to work in eight
attempts. Full account: `docs/architecture.md`, "the shard, and eight rounds of being
wrong about it". The short version:

**The object renders.** A `worldEntityNode` in our own sector, following
`GeneralShadowsFix`'s conventions exactly: path under
`mod\worlds\03_night_city\_compiled\default\`, category Exterior, level 1,
a real +-5000 streaming box (float-max is NOT "infinite"), sector version 62,
and an entity node's nodeData flags rather than a trigger area's.

**The interaction does not, and nobody knows why.** A verbatim copy of the
working vanilla container is inert in a mod-added sector, while the same file
renders fine as a plain entity.

Verbatim means: same template, same appearance, all 53 fields of its instance
data, same node flags, produced mechanically rather than retyped. Every route
was instrumented:

| fact | value | meaning |
|---|---|---|
| `cc_g01_dbg_shard_class` | 1 | the entity class attaches |
| `cc_g01_dbg_shard_ui` | 3 | hotspot definition loads, no layer ever activates |
| `cc_g01_dbg_shard_item` | 1 | no `ShardCaseContainer` takes control near that desk |

**Where to start if it is revisited:** whatever binds a container to the loot
system is not in the node, the template or the instance data. Find that and the
prompt follows. Do NOT start by writing another bespoke entity.

**Settled, do not re-derive:**

- a shard's prompt belongs to the LOOT system, not to `SetSingleChoice`;
- `exEntitySpawner` is CET-Lua only and invisible to redscript;
- `DynamicEntitySystem` + `templatePath` attaches an entity but never renders a
  mesh - it is an NPC/device spawner;
- a mod `.ent` may only name an entity class the game ships;
- an entity template must declare its mesh in `resolvedDependencies`.

**Not a candidate:** using the vanilla shard for the interaction. It works end to
end, but its loot-list title is "The Flowers of Silence" and playtesting rejected it
on sight - "people will not understand it." Renaming that item globally would
change it everywhere it appears in the game.

## 7. Post-release bug reports - Nexus 1.0.0, filed 2026-08-15

Five reports from players after the release, plus one playtesting found while testing
the fixes (Hoshino speaking after being killed). **All six are confirmed in game
and shipped in 1.1.0.** Five are recorded in the internal chronology rather than
here, and named below so the list is complete: ghost calls after a reload, the
call landing on
a fast-travel loading screen, Nix replying instantly, North Oak navigation, and
the dead man talking.

**§7d stays, and it is fixed too.** It keeps its entry because the one part that
is NOT fixed - her "Look who it is" bark - carries a table of three failed
mechanisms, and that table is what stops a fourth attempt.

The lesson the fixed three left behind, because it will be back: **a fact
survives a load and a script field does not.**

Anything remembering "this already happened" in a `let` on a ScriptableSystem
forgets it the moment the player reloads. Every `cc_g01_*` fact comes back
exactly as it was.

### 7d. Mama Welles' own dialogue wins the first approach - FIXED, confirmed in game

> In the Coyote Cojo, the conversation with Mama Welles was initially blocked by
> her default remarks; it took a 2nd approach before the option to talk on
> something quest-related became available.

**This reopens §3e**, which closed this exact symptom on 2026-08-12 as "clutter,
not a fault". The reasoning was that *"the epilogue fires on PROXIMITY, not on
the player picking an option, so our scene always plays."*

A player has now found the case where it does not. Her default conversation gets
there first, and our scene does not appear until the second approach.

#### CAUSE FOUND 2026-08-15, and it is not the trigger radius

The first guess in this entry was that `cc_g01_mama_reached` fires at 3.5 m,
inside her talk range, so it is a race. **That is not it. There is no race,
because our scene never claims her at all.**

Read off the shipped files rather than reasoned about. Vanilla's own quest scene
with her, `base\quest\side_quests\sq018\scenes\sq018_01_mama_welles.scene`,
declares her as a first-class actor:

```
acquisitionPlan : spawnSet
actorName       : Mama_Welles
spawnSetParams  : entryName "mama_welles", reference "#mama_welles"
voicetagId      : 1704188817181679616
```

**Ours (`gig01_epilogue.scene`) does not:**

```
acquisitionPlan : spawnDespawn
dynamicEntityUniqueName : mama_welles      (a COPY the scene spawns itself)
spawnSetParams  : entryName None, reference 0
```

Our scene spawns its own Mama, buried 2.5 m under the floor to be heard, and
only borrows the real one's body for lip sync. So **the real Mama Welles is
never taken as an actor and is never busy.** Her default conversation is free to
start the moment V walks up, every time, and the two then compete for the choice
hub. Which one the player gets is arbitrary, precisely what was reported.

The buried-copy design is why she was silent in August and it fixed that, but
it fixed it by opting out of the mechanism that would also have solved this one.

**The fix is vanilla's own shape: take her as the actor.** Same `entryName`,
same `reference`, same voicetag we already carry in the lipmap. Taking her locks
her, and a quest scene that owns an NPC is what stops her default dialogue in
every gig in the game. Audio comes from her real position, which is correct and
is what vanilla does. The silence was the (1000, 1000, -100) default, not the
use of a real actor.

**The one real risk, and it is why this was not shipped blind:** a `spawnSet`
acquisition finds a community entry, not a script-spawned NPC. So
`Gig01_Encounter`'s stand-in path. Spawn our own Mama if the real one is missing
after 4 ticks. Stops being a fallback and becomes a dead end: the scene node
would wait for an actor that cannot arrive, and the ending would never play. That
path exists because someone saw her absent. Before this ships, either confirm
she is reliably present or give the quest graph a branch that skips the epilogue
scene when she is not.

#### The build, and the one thing that stopped it (2026-08-15)

Agreed shape (playtest): probe whether the real Mama is in the bar, and branch.
Present → take her as the scene's actor. Absent → play the same beat with our
own. `Gig01_Encounter.FindMamaWelles()` already answers the probe, from 60 m,
through walls; it only needs to publish the answer as `cc_g01_mama_present`.

**The present half is straightforward** and copies vanilla's `sq018_01` actor
verbatim (dumped and diffed against ours: the only differences are
`acquisitionPlan`, the two `spawnSetParams` fields, and four zeroed
`spawnDespawnParams` values).

**The absent half hit a wall, and it is a known one.** A scene's spawned actor
is placed by `spawnOffset`, which is relative to the scene's marker - 
`ANCHOR_MAMA` / `#sq018_pepevodka`. The position is fine, because the offset onto
her mark is already known and merely needs un-burying (`OFFSET_MAMA` Z + 2.5).
**The FACING is not**, because the offset's orientation is relative to that
node's rotation, which is not knowable offline: the same trap as `around_player`
(docs/gotchas.md #15 and #16), one step removed.

Our scenes also cannot correct it at run time: `section()` emits
`'actorBehaviors': []`, so nothing turns an actor to face the person talking to
them. Vanilla's own `mama_welles_default.scene` carries 30
`scnSectionInternalsActorBehavior` entries; ours carry none.

So a scene-placed stand-in would stand on the right spot facing an arbitrary
fixed direction, in the last beat of the gig. Two ways out:

1. **Read the anchor's rotation.** `#sq018_pepevodka` is not in an always-loaded
   sector, so `find_pin_anchors.py` cannot see it; it means extracting whichever
   sector holds it and reading the node's quaternion, then composing.
2. **Use the workspot device for the stand-in only**: `gen_workspot_ent.py` plus
   a `PlaceSceneMama` alongside `PlaceSceneJohnny`. The device carries world-space
   position AND orientation, precisely the problem being solved, and it is
   proven twice in this gig. This is option B's machinery applied to the one half
   that needs it, with option A everywhere else.

**BUILT 2026-08-15. Deployed, compiling, NOT YET PLAYED.** The workspot device
turned out not to be needed at all. What follows was the plan, kept only for the
parts that survived it.

1. `gen_scenes.py`: `add_spawnset_actor()`, vanilla's `sq018_01` shape verbatim.
   Split `build_epilogue()` into one function emitting two scenes so the words
   cannot drift: `gig01_epilogue` (real Mama, `spawnSet`) and
   `gig01_epilogue_standin` (today's buried `spawnDespawn` actor, unchanged).
   Register the second in the build list.
2. `gen_workspot_ent.py`: a second component, `cc_g01_mama_stand`.
   **NOT Johnny's workspot.** `WORKSPOT_JOHNNY` is
   `base\workspots\main_characters\johnny\...`: his own rig. Use the generic
   one already researched and named in that file's own comments:
   `common\ground\generic__stand_ground__think__01`, which is what the shipped
   scene `sts_hey_gle_04_johnny.scene` uses.
3. `Gig01_Encounter.reds`: publish `cc_g01_mama_present` (1/0) at the same
   moment as `cc_g01_mama_reached`, and add `PlaceSceneMama`, a copy of
   `PlaceSceneJohnny` with its own device id field (gotcha 15: never share a
   field between two placers) and no glitch FX: no `johnny_teleport_end`, no
   `m_lipFxPending`, no dissolve. Her spot and yaw already exist as
   `CCGig01Places.MamaWelles()` / `MamaWellesYaw()`, so the placement maths is a
   constant, not player-relative.
4. `gen_questphase.py`: branch on `cc_g01_mama_present` into one of the two
   scene nodes, re-merge after. Two nodes, two DIFFERENT scenes, each with a
   connected exit: not the duplicate-node shape that crashed the game on load in
   August. Keep the post-generation "one node per scene" assertion valid.

**First thing to check on the next launch is that a save LOADS**, before playing
anything - that is the failure mode a bad quest graph produces, and it hits every
player whether or not the gig is running.

Also discovered while costing it: a second `.scene` means new RUIDs, so
`gen_voice` (vomap + `durations.json`) and `gen_lipsync` (picks) each need an
alias, `gig01_epilogue_standin` reuses `gig01_epilogue`'s clips. The vomap keys
`stringId -> wem path`, so two RUIDs may point at the same `.wem`: **no audio is
regenerated**, which also keeps the voices off the seed roulette.

#### THE ACTUAL SWITCH: `mama_is_talking` (found 2026-08-15, after a failed test)

Acquiring her as the scene's actor did not remove her small talk. the
screenshot settled it: our option ("Long night. She okay?") sits in the SAME hub
as "I'll have a drink." and "What's happening in the area?", and she still speaks
her own greeting on sight. So the vanilla options were never a competing scene
fighting us for the actor. **They are her default dialogue's own choice hub, and
owning the actor does not close it.**

The acquisition is still right: our option now appears on the first approach
rather than the second. It just does not do this job.

**What does:** `base\quest\tertiary_characters\default_dialogues\
mama_welles_default.scene` gates its own start on a pause node reading

```
player distance < X   AND   mama_is_talking < 1
```

and nothing in that scene ever sets `mama_is_talking`. It is written from
outside, by whatever story content currently owns her. That is vanilla's own
"she is busy, do not start small talk" flag, and holding it up is the supported
way to do exactly what §3e wanted. It takes both halves at once, because the
greeting and the buttons are the same scene.

Held in `Gig01_Encounter` from arrival at El Coyote until the epilogue
conversation is done, and bounded three ways.

A base-game fact left at 1 would leave Mama Welles mute for the rest of the
save, silently. That is the risk that got `SetInteractions` deleted.

- only after `cc_g01_at_coyote`;
- only until `cc_g01_mama_talked`;
- only while V is within 60 m of the bar - wander off and it is released, come
  back and it is set again, so an abandoned gig costs her nothing.

It also only ever clears a 1 it wrote itself (`m_mamaHeld`). The fact is not
ours; another quest may be holding it for its own scene, and clearing that
because our window happens to be shut would switch her small talk back on inside
somebody else's beat.

Related facts in the same file, for whoever needs them next:
`mama_welles_default_talked`, `mama_welles_dd_holo`, and the
`holo_v_calls_mama_welles_*` pair that drives her holocall.

#### The greeting: THREE mechanisms failed. Shipped answer is a 2.6 s gap

"Look who it is" is a voiceset bark, not part of the dialogue scene that
`mama_is_talking` blocks. Its source is
`base\quest\tertiary_characters\vsets\vset_mama_welles.scene`, whose entry points
are literally `greeting` / `greeting_var_1` / `greeting_var_2`, and which carries
**no fact conditions at all** - so there is nothing to gate.

| attempt | what it was | result |
|---|---|---|
| 1 | `entChangeVoicesetStateEvent { enableVoicesetLines: false }` queued at her GameObject | no effect |
| 2 | same event, `inputsToBlock = [greeting]` | no effect |
| 3 | `questVoicesetManagerNodeDefinition` + `questChangeVoicesetState_NodeType`, puppetRef `#mama_welles`, from the quest graph | STALLED THE GIG |

Attempt 3 is the important one. It is vanilla's own mechanism and it looked
like the right answer - Codeware shows the state lives on
`scnVoicesetComponentPS` (`areVoicesetLinesEnabled`, persistent), which explains
why events queued at the ENTITY did nothing. The node never handed control on,
though: the chain never reached the pause on `cc_g01_mama_reached`, so the epilogue
never played. Playtest: *"our actions never spawn"*. Reverted the same evening.

Most likely cause, and it generalises: an object-manager node waits for its
`puppetRef` to resolve, and `#mama_welles` is a scene spawn-set reference.
That it resolves for scene acquisition - proven in game - does not make it
resolvable for a quest node, whose sector may not even be streamed when the node
runs. Same distinction that cost three builds on map pins.

**SHIPPED: the scene gives her line room instead of fighting it.** 2.6 s of
`lead_ms` on the epilogue's first section, so her greeting lands in the gap and
the beat reads as an exchange - she notices V, then softens. the
suggestion, confirmed in game: *"It lands in the gap. It's a good outcome."* It
needs nothing suppressed, which is why it is the version that cannot break.

Do not spend a fourth attempt on this without new evidence.

#### Dead ends, checked so nobody checks them again

- **`IsGenericTalkInteractionEnabled` is a native GETTER with no setter**
  (declared in the decompiled dump as
  `public final native const func IsGenericTalkInteractionEnabled() -> Bool`).
  It reads the state; there is nothing to flip. This was the planned route, and
  it does not exist.
- **Her default scene has no fact gate we can use.** Extracted and read
  (`base\quest\tertiary_characters\default_dialogues\mama_welles_default.scene`):
  its only enabled interruption scenario is "walk more than 7 m away", and the
  one fact-driven scenario (`holo_interrupt_call`, for incoming holocalls) ships
  with `enabled: 0`.
- **Her `.ent` has no dialogue component to switch off**: a stock NPC with a
  `gameinteractionsComponent`, which is what `InteractionSetEnableEvent` already
  failed against in §3e.
- **Hiding her and spawning our own** (the proposal, 2026-08-15): both
  halves are broken. `enteventsSetVisibility` hides the mesh and leaves a
  talkable invisible woman; there is no supported despawn for a world-placed NPC
  from redscript; and making a script-spawned NPC a scene actor by Tag is
  docs/gotchas.md #17, which hard-crashed the game. Superseded by the fix above,
  which gets the same result. Us owning the conversation - by taking the NPC the
  game already placed instead of fighting her.

### 7e / 7f. North Oak navigation, and Hoshino talking after death - BOTH FIXED

Confirmed in game 2026-08-15 and shipped in 1.1.0. Deleted from here per this
file's convention; the account, including the two mechanisms that failed first,
is in `docs/architecture.md` under the three North Oak entries of that date.

The two findings that outlived the bugs, both now in docs/gotchas.md and the map-pins
playbook, because they will come back on gigs 02-04:

- **A quest map pin cannot be un-shown** (gotcha 23). One marker at a time is a
  `MappinSystem.RegisterMappin` job, and that call takes a world position - no
  anchor, no offset, so the always-loaded-sector rule does not apply to it.
- **A forced GPS route is real and unusable.**
  `gameJournalQuestGuidanceMarker`, a child of the map pin, 44 of them in the
  shipped journal. It has no offset, so it can only point at nodes the game
  already ships, and there were none within 50 m of five of our six waypoints.
  **Do not spend time on `GPSForcedPathVariant`** - zero of the 4277
  shipped quest pins use it.

---

## 8. Post-release bug reports - Nexus 1.1.x, filed 2026-08-15

Two reports from one player, the first confirmed by a second player who pinned
it to "Gimme Danger", the Takemura warehouse mission. One is a real and previously unknown
blocker; the other does not reproduce against the shipped code and needs a
version confirmed before anything is built.

### 8a. THE OFFICE DOORS ARE SHIPPED DISABLED - the gig is unplayable before "Gimme Danger"

> "i couldn't find any way into the Arasaka warehouse. the path routed me to a
> door that wouldn't open and every other door or access that i tried just sent
> me around the outside but not into the building... this game file is quite
> early in the game atm, so i've not done any real missions in here yet"

**The reporter's own guess is right.** Read off the shipped streaming sectors,
not reasoned about. Every door in the Arasaka Industrial Park is a
`DoorControllerPS` inside `loc_q112_arasaka_industrial_park_warehouse`, and
these carry `deviceState: DISABLED` as their authored initial state:

| position | debugName | what it is to us |
|---|---|---|
| -241.9, -1450.7, 14.6 | `{glass_door_k}` | `CCGig01Places.OfficeEntry()`, 1.8 m away |
| -219.8, -1423.2, 14.6 | `single_sliding_door_1` | `CCGig01Places.InnerEntry()`, 0.9 m away |
| -252.6, -1443.3, 14.6 | `{door}` | the other door onto the office floor |
| -265.3, -1435.8, 14.6 | `{door}` | office floor, west end |
| -260.9, -1452.2, 8.6 | `double_door_simple_1` | ground floor |
| -277.9 / -287.8 / -297.6, ~-1425, 8.6 | `gate_1` x3 | the compound vehicle gates |

**The measurement that makes this conclusive: across all 46 cached exterior
sectors there are 96 doors, 87 `ON` and 9 `DISABLED`, and all 9 disabled ones
are in this one compound.**

`DISABLED` is not a common authoring state that happens to mean nothing. It is
what the base game uses here and almost nowhere else. `q112` is "Gimme
Danger", confirmed from the VO corpus: Takemura, the parade floats, "We break
into Arasaka Industrial Park".

The shape of the failure matches the report exactly. The door into the terminal
room itself (-256.3, -1450.8, 14.6) is `ON`, so it is not the office that is
shut, it is both doors that get you onto the office floor. A player who
walks the compound finds every route leading back outside.

Why no playtest has ever seen it: testing runs from a late-game save where
"Gimme Danger" is long done and those doors have been switched on and persisted.
This is the same blind spot as gotcha 21, one step further out - not "a fact the
gig already set", but **a base-game device state some earlier quest already
changed**.

**BUILT AND CONFIRMED IN GAME 2026-08-16** on a real pre-"Gimme Danger" save.
`mods/gig-01-negative-balance/source/scripts/Gig01_OfficeDoors.reds`. Ships as
1.1.3. The script route, chosen over the quest-graph one: five doors matched by
owner position the way `Gig01_OfficeComputer.reds` matches the narrative
computer, walked up to ON while `cc_g01_accepted > 0`. One way, no restore,
because opening a door the base game will open later is harmless and closing one
is not.

**THE MECHANISM, and it took three builds to get right because each wrong answer
looked like a right one:**

```
DISABLED  --ActionQuestForceEnabled-->  OFF  --ActionQuestForceON-->  ON
```

Neither action alone is enough. `ForceEnabled` takes the door out of DISABLED and
leaves it OFF, and an OFF door offers the player nothing at all: no prompt,
not even a "Locked" one. Only ON is a working door.

**`ExecutePSAction` IS DEFERRED, and the finding applies to every device, not
just these doors.** The
state does not change in the frame the action is sent, and every mistake below
came from reading it back too soon:

- Build 1 sent `ForceEnabled` and gated on `IsDisabled()`. On the test save it
  appeared to do nothing at all. It had in fact moved all five doors from
  DISABLED to OFF, and then refused to touch them again on the next load because
  they were no longer disabled. **A fix that half-worked read exactly like a fix
  that never ran.**
- A CET probe then sent five candidate actions in ONE frame and read the state
  after each, "proving" that only a direct `SetDeviceState` had any effect. It
  proved nothing. Every read was of the state before its own action, the five
  actions raced, and the door it ran on ended up reporting `EDeviceStatus`
  4294967294, which is not a state. Do not test deferred actions in a loop.
- One action per click, with the state read on a LATER click, gave the answer in
  two tries: `ForceON` on an OFF door, confirmed by the door opening.

So the shipped code is a pump: one step per pass, half a second apart,
re-reading the state each time, capped at six passes. It is written as "look at
the state, take one step towards ON" rather than as a fixed sequence, so it is
correct from whatever state a door is in - including the OFF doors build 1 left
behind on a save.

**ONE HOOK. The second was shipped, measured, and deleted.** Build 1 hooked both
`GameAttached` and `SetDefaultDoorState`, because neither one's timing could be
established offline, and recorded which of them did the work. Everything came
back route 1: `SetDefaultDoorState` never fired for any door in the game. That
is what the two-hook trace was for, and having got its answer the dead hook is
gone rather than left in as insurance nobody has seen work.

**What the compiler settled before a line was written**, because the device API
is not discoverable from files on disk:

- `DoorControllerPS.OnGameAttached(GameAttachedEvent)` does not exist. The
  obvious hook is not there. `ScriptableDeviceComponentPS` has a method of that
  name but not with that signature.
- `GameAttached()` and `SetDefaultDoorState()` both wrap on `DoorControllerPS`.
- `IsDisabled()`, `GetDeviceState()`, `SetDeviceState(EDeviceStatus)`,
  `GetGameInstance()`, `GetOwnerEntityWeak()`, `ExecutePSAction`,
  `ActionQuestForceEnabled()`, `ActionQuestForceON()`,
  `ActionToggleActivation()` all resolve.
- `TSQ_ALL()` + `Device.GetDevicePS()` compiles as a way to find devices from
  the player side. Not needed once a hook existed.

**The route not taken**, kept because it is the vanilla way and gigs 02-04 may
want it: a `questDeviceManager_NodeType` node in the quest phase. The doors are
addressable, each carrying a full `QuestPrefabRefHash` ending in
`#loc_q112_arasaka_industrial_park_warehouse_devices/...`, params `objectRef` /
`deviceControllerClass` / `deviceAction`
(`quest/DeviceManager_NodeTypeParams.hpp` in the vendored RED4ext SDK). Passed
over because it needs a new node type in the generator and rests on an unknown
this project has been burned by: whether a mod-authored NodeRef resolves into an
ordinary streamed sector. The map-pin work only ever proved the always-loaded
case.

**Two facts, in the CET menu**: `cc_g01_doors_opened` (how many of the five this
save took to ON), `cc_g01_dbg_door_state` (what the last one reported on
stream-in: 1 DISABLED, 2 ON, 3 OFF, 4 UNPOWERED, 9 other) and
`cc_g01_dbg_door_giveup`, which must stay 0. On a post-"Gimme Danger" save
`_opened` is 0 and `_state` is 2, and it is the correct result rather than a
failure.

**CONFIRMED ON THE EARLY SAVE 2026-08-16** and shipped as 1.1.3. The save was
parked at the door, and the door worked after a plain load with no fast travel,
which incidentally confirms that loading a save is itself an attach and the
hook does not need the sector to cycle.

**The doors are never closed again. That is a decision, not an omission.**

A door can only be touched while its sector is streamed, which is when the
player is standing among them. So a restore's failure mode is shutting somebody
inside a building, with nothing to connect it to us. Opening one that the base
game opens later has no equivalent failure mode. If it is ever revisited,
the workable shape is to restore ON ATTACH when `cc_g01_done > 0`, so it fires as
the player arrives from outside, plus a position guard for the reload-while-inside
case. Untested residual risk, stated rather than hidden: a player who does this
gig and later plays "Gimme Danger" meets a compound whose five pedestrian doors
already work. Quest device nodes set state explicitly and would set them ON
again, so it should not break, but nobody has played that sequence.

**The CET device probe buttons (`DUMP`, `FORCE 1/2/3`) are kept** in
`source/cet-dev/`, which never ships. They cost nothing and they are the fastest
route to an answer the next time a base-game device does not behave. The two
diagnostic facts stay in the shipped script for the same reason: they are what
makes the next player report about this diagnosable.

### 8b. Ghost calls reported again - DOES NOT REPRODUCE against 1.1.x

> "i get two unanswerable calls every time i start the game"

**The 1.1.0 fix is present and correct in every shipped zip from 1.1.0 on**
(verified by reading `Gig01_Holocall.reds` out of `dist/NegativeBalance-1.1.*.zip`).
More than that, the reported symptom cannot be produced by the current code
from the save state the same message describes:

- The reporter is at the office, so `cc_g01_accepted` is set. The quest phase
  parks on `add_pause_fact('cc_g01_call_done')` before it sets
  `cc_g01_accepted`, so having the objective at all proves `cc_g01_call_done`
  is set, precisely the guard that sends Elena's call to state 9 on load.
- Both Nix calls are still at `<prefix>_request = 0` at that point in the graph,
  and `Step()` returns immediately on that.

So a current install has no call it is able to place. The likely explanation is
a stale `r6\scripts\NegativeBalance\Gig01_Holocall.reds` left from 1.0.0.
**Get the version confirmed before building anything.**

One thing to look at if the version does come back as 1.1.1 or later: 1.1.1
added the only path in the file that hangs up a ringing call
(`IsFastTravelling` while in state 1 or 4). It can only fire on a call that is
pending, which this save has none of, so it would point at an odd fact
state rather than at that code. It is still the first place to look, because it
is the only ring-and-die path left.

## 9. Placing a scene actor relative to the player: SOLVED

Filed 2026-08-16, from a Nexus report of Johnny appearing in a T-pose for
about a second. The T-pose turned out to be a symptom. This section is the
cause, and it is the most reusable finding here: any mod that wants
a scene character to appear next to the player, facing them, anywhere in the
world, can stop working around the problem described below because the problem
does not exist.

### What this project believed, and how wrong it was

A scene's `sceneLocation` can be a `scnWorldMarker` of type `Tag` with the tag
`around_player`, which stages the scene at the player instead of at a fixed
world node. `scene-playbook.md` and `gen_scenes.py` both carried two claims
about it:

1. the marker "IS NOT ON THE PLAYER", it "lands a few metres to one side";
2. the marker's rotation is "not knowable", so a horizontal `spawnOffset`
   cannot be aimed and an actor "ends up in front, behind or sideways
   depending on where the player happens to be looking".

Both are false. The evidence behind them was one playtest sentence about how a
voice SOUNDED, from an actor who was 2.5 m underground at the time: *"still
feels very far, like on the right of where I am"*. That is the floor between
listener and speaker, not a horizontal offset. It was written up as fact, given
a `DO NOT`, and never measured.

### The measurements

Two quest facts written from redscript at the moment the scene spawns its
actor, read off a debug menu. Distance and bearing from the player, bearing in
world terms, and height difference.

| `spawnOffset.position` | Result | Runs |
|---|---|---|
| (0, 0, −2.5) | 0.00 m horizontally, 2.50 m below V | 2, facings 175° apart |
| (0, 2, 0) | 2.00 m away, 0° off dead ahead | 2, facings 180° apart |
| (1.1, 1.8, 0) | 2.10 m away, 32° off ahead, on the RIGHT | 1 |
| (−1.1, 2.4, 0) | 2.64 m away, 24° off ahead, on the LEFT | 1 |

The two-run pairs are the load-bearing ones. In each pair the bearing from the
player's own facing stayed the same while the bearing in world terms moved by
180°, which is only possible if the marker turns with the player.

So, for a scene staged on `around_player`:

- the marker sits at the player's **exact** x and y;
- the marker **carries the player's rotation**;
- in `spawnOffset.position`, **+Y is forward and +X is right**, in the player's
  own frame;
- `spawnOffset.orientation` is in that same frame.

### The recipe

Set two fields on the actor's `spawnDespawnParams`:

```python
spawnOffset.position    = (aside, ahead, 0.0)
spawnOffset.orientation = yaw_to_face_player((aside, ahead, 0.0))
```

`aside` is positive to the right, `ahead` is positive forward, both in metres.
`yaw_to_face_player` lives in `tools/questkit/scene.py`:

```python
def yaw_to_face_player(offset):
    return math.degrees(math.atan2(offset[0], -offset[1]))
```

and the quaternion it becomes is a plain rotation about Z:

```python
half = math.radians(yaw) / 2.0
{'$type': 'Quaternion', 'i': 0, 'j': 0,
 'k': math.sin(half), 'r': math.cos(half)}
```

**Do not type the yaw by hand.** A fixed 180 is the obvious guess, it is
correct only when the actor is dead ahead, and it fails quietly everywhere
else: at (1.1, 1.8) it left the actor looking 32° past the player's shoulder,
which reads on screen as talking to nobody. The helper returns 180 for the
dead-ahead case, so the guess is a special case of the formula.

Yaw is counter-clockwise seen from above, which is where the sign in the
formula comes from.

### What it fixes

Everything below existed to work around a marker believed to be unaimable, and
none of it is needed:

| Was needed | Why it existed |
|---|---|
| Actor buried 2.5 m down | straight down is the one offset that needs no knowledge of the marker's rotation |
| A second, script-spawned body | the buried actor could not be seen |
| An invisible workspot device entity | the only way script can place a puppet, since `Teleport` ignores the position for one |
| Arrival and exit effects | to cover the moment the script lifted him |
| A 40 m targeting query, 6.6 times a second, up to 90 s per beat | to find the actor again after the scene spawned him |

Removing them removes the T-pose with them. The pose came from the handover
between the scene's workspot and the script's, and with the scene placing the
actor there is no handover. Confirmed in game: the actor arrives already posed.

It also removes a class of failure worth naming for anyone doing this on a
heavily modded install. The script route searched for any entity within 40 m
whose record matched, which on a large load order can find another mod's copy
of the same character. Scene placement never searches.

### What is still true from the old advice

- A line's speaker must be a scene actor for lipsync and for a mod voiceover
  map to key on it. That has not changed, and it is why the words were in a
  scene in the first place.
- Audio falls off with distance rather than switching off, so a speaker who
  must be heard has to actually be near the listener.
- Vanilla's one shipped Johnny scene staged on a Tag marker
  (`sts_pac_cvi_02_johnny.scene`) gives its actor its own `spawnMarkerNodeRef`
  and a zero offset, so there is still no vanilla precedent for offsetting off
  a Tag marker. That is an absence of precedent. It works, measured five times.

### The general lesson

`gotchas.md` #31. A claim that forecloses an approach earns a measurement
before it earns a `DO NOT`, because a wrong "impossible" is never retested. Two
facts and a debug menu settled in ten minutes what three months of reasoning
had settled wrongly.

---

## 10. Post-release bug pass: Nexus 1.1.3, plus a read-through. 2026-08-16/17

Two Nexus reports opened this, and reading the tree for anything of the same
shape found four more that nobody had reported. Which is which is stated for
each item, because it decides what a changelog may claim.

### 10a. Fast travel blocked for the rest of the save: REPORTED, FIXED

*"every fast travel point unavailable after ignoring the phone a few times"*,
in play 2026-08-16. The only item on this list a player hit and could describe.

`Gig01_Holocall.ApplyLock()` asked for `AddFastTravelLock` whenever a call was
in state 1, and the comment beside it called state 1 "ringing". It is not. It is
"we rang, and we are waiting to see whether it is answered", and that wait is
the entire retry back-off: 24 s, 30, 30, 60, then 300 s from the fifth ring
onward. The phone itself rings for eight seconds.

So a lock meant to cover eight seconds covered five-minute stretches with one
tick of daylight between them. It was wrong from the first ring too, just less
visibly: 24 s of lock for 8 s of ringing.

Fixed by bounding the lock to the ring rather than to the state. `m_waited` is
counted in live ticks and the live tick is 0.2 s, so the ring window is 45
ticks. State 4 (V dialling out) is genuinely dialling for its whole length and
keeps its lock throughout. The unconditional first pass stays: locks are saved,
so a stuck one has to be lifted on load (`gotchas.md` #24).

**A CONVERSATION IS NOT LOCKED, AND THAT IS NOT A SIDE EFFECT OF THIS FIX.**
Raised 2026-08-17 on seeing a fast travel terminal offer a destination during
Elena's call. Both versions ask for the lock on states 1 and 4 only, and an
answered call is state 2 then 3, so a conversation was never covered in 1.1.3
either. What changed is that the old lock leaked past the ring and often was
never lifted, so any call following an ignored ring inherited a lock that made
it look deliberate.

Leaving it that way is a decision, and there is now a measurement behind it.
Playtest, 2026-08-17: fast travelling mid-call, the call carries on across the
loading screen and the beat completes. So the terminal being usable costs
nothing.

Locking a conversation would cost something. State 3 waits on `<prefix>_end`
from the quest phase and has NO timeout, so a lock held there would outlive any
scene that failed to finish, which is this same bug arriving by a new route. If
it is ever wanted, it has to be bounded by a tick cap the way the ring is, never
by the state alone.

### 10b. The mod never switched itself off: FOUND BY READING, FIXED

Nothing anywhere checked `cc_g01_done`. After the gig finished:

- three systems kept rescheduling for the rest of the save. `NegativeBalance`
  every 1.0 s, `NegativeBalanceEncounter` every 1.5 s, `NegativeBalanceHolocall`
  every 2.0 s. Only `NegativeBalanceStart` latched off, and it was the model
  copied.
- the door and computer wraps were gated on `cc_g01_accepted`, which never
  returns to 0. So the five Arasaka office doors were still pumped up to ON on
  every sector attach, and the ledger was still rewritten into the office
  computer on every visit.

**The honest framing, which matters for a changelog.** This was found while
investigating a Steam Deck report of choppiness after completing the gig.
Measured, the idle cost is about twenty fact reads a second, which does not
obviously explain a stutter. It is done because a finished side gig should cost
a save nothing, not because it is proven to fix that report.

Two ordering constraints made this more than adding a fact check:

- the holocall tick may only stop AFTER `ApplyLock` has had its one
  unconditional pass, or the fix in 10a strands the very lock it exists to
  lift;
- the encounter tick may only stop once it has given back everything it took:
  `mama_is_talking`, her voiceset, the way-in mappin, our stand-in, and the
  payout. Stopping on the fact alone would latch each of those on for the rest
  of the save, which is the class of bug the stop is meant to end.

Neither stop is persistent, and neither needs to be. `OnAttach` runs on every
load, one tick re-checks and stops again. Clearing `cc_g01_done` from the dev
menu therefore does not restart a tick within a session; reload.

### 10c. The office guards: REPORTED, three faults in one place, FIXED

*"when I reached the area where the NPCs should have been, they simply weren't
there. I checked the emails on the computer, turned around, and the NPCs
suddenly spawned directly in front of me."*

- **The trigger missed the room.** One 60 m sphere on `CompoundEntry`. Measured:
  the office terminal is 63.5 m from that anchor and the terminal room door
  67.7 m. Anyone who reached the computer without crossing the bubble found an
  empty building. The office is now measured from the building as well as the
  gate (the terminal at 25 m), and the spawn test is wider again, 100 m on the
  gate, so the walk in has runway.
- **Twenty entities in one tick**, requested at the moment the player arrives.
  They are spread over a callback chain now, one squad a second.
- **A silently binned squad never returned.** Each guard is placed only if
  `FindPointInSphereOnlyHumanNavmesh` answers OK, and `m_officeSpawned` was set
  BEFORE the spawning, so a navmesh that was not ready binned all twenty and the
  gig recorded the job as done. `SpawnSquad` returns a count now, an empty squad
  is asked for again up to five times, and the site latches only on a non-zero
  total.

`Notify("Arasaka security on site")` also fired in the tick the entities were
requested in, announcing an empty compound. It moved to the end of the chain.

Written up as `gotchas.md` #32, because all three generalise.

Two facts report the outcome for testing: `cc_g01_dbg_office_guards` and
`cc_g01_dbg_estate_guards`, the counts actually placed.

**Second pass, 2026-08-17, after playing it.** The first fix worked and left two
things half done, both found in play.

The two spheres became **the outline**. Four corners of the industrial park were
walked and captured (`compound_1` to `compound_4`), giving a convex ~38,500 m2
polygon that contains every anchor the gig uses here, and
`CCGig01Places.InsideCompound` is now what says "V is on site". The 60 m sphere
on the gate stays alongside it so arriving at the marked entrance still counts
before the outline is crossed. The estate got the same treatment: its trigger
is now the gate at 45 m, or Hoshino at 70 m, **or `InsideEstate`**, the twenty
points that were already walked for the way-in objective in 1.1.0. A player who
comes over the back wall gets the same estate as one who drove to the gate.

And **the site latch became one bit per anchor**, which is the fix for the
report that entering the estate the back way gave Hoshino but no guards. The
difference between them is the whole explanation: Hoshino is placed straight at
his captured position, while every guard first has to pass
`FindPointInSphereOnlyHumanNavmesh`, and that query only answers where the
navmesh is streamed in. Come in from behind and the gate, the approach and the
grounds are far away and unstreamed, so those squads were dropped - and the site
latched anyway on the two that did land.

Now each anchor carries its own bit, an anchor that failed is asked again every
six seconds while V is on site, and an anchor is only ever populated once, so
clearing a compound and standing in it cannot produce a second wave. Bounded at
60 squad attempts per site per session, so an anchor that can never be populated
costs a fixed amount rather than one attempt a second forever.

The mask is an `Int32` and not an `array<Bool>` on purpose: arrays on a
`ScriptableSystem` come back from an older save at the wrong length, which is
the trap at the top of `Gig01_Holocall.reds`. An `Int32` cannot be the wrong
length. It needs a `Bit(i)` lookup table because **redscript has no `<<`**;
`&` and `|` are fine. Both were established by compiling a throwaway file
rather than by assuming.

The two debug facts ACCUMULATE now, because a site can fill in over several
passes.

### 10d. The estate squad: same burst, one size bigger. FIXED

26 entities in one tick. Its trigger geometry was already sound (the gate at
45 m or Hoshino at 70 m, and the estate terminal is 34 m from Hoshino), so this
was the burst only, not the gap. Same chain. Hoshino himself is spawned first
and outside the chain, guarded by his own latch so a retried chain cannot put a
second one on the terrace.

### 10e. The attitude retry budget: FOUND BY READING, WIDENED

Every spawned guard gets `SetHostile`, which retried up to seven times at 1.5 s.
That 10.5 s budget was sized on the development machine against the
all-at-once burst. A guard who takes longer than that to stream in keeps his
record's default attitude, and the compound list is mostly `sts_*` street-story
security which does not treat V as an enemy, so the symptom would be "the guards
ignore me": the 2026-08-13 bug arriving by a new route, from a budget rather
than from a missing call. Now 40 tries, 60 s. Only a guard who never resolves at
all pays for the higher cap.

### 10f. The Mama Welles stand-in: A DEFENSIVE CHANGE, NOT A BUG FIX

`DespawnMamaWelles` ran only on the epilogue's own path, on
`cc_g01_epilogue_scene_done`. It is now also called from the "not accepted, or
done" branch, next to `ReleaseMama` and `HideWayInMarker`, which sit outside
the gate for the same reason: anything this gig takes from the world should be
given back by every path out of it, not only the expected one.

**Read that as symmetry, not as a bug.** The reasoning that produced it was
that an epilogue finishing by an unusual route could leave our duplicate
standing in El Coyote. Nobody has ever seen that happen, no player reported it,
and no test has produced it. It was inferred from reading the code and it
remains inferred.

So it is deliberately NOT in the 1.2.0 changelog. A changelog entry would tell
players a bug existed, and the honest position is that we do not know whether
it ever did. `gotchas.md` #31 cuts both ways: an impression is not a
measurement, and that applies to a bug you think you have found as much as to
one you think you have ruled out.

### 10g. Johnny's exit flash, as a scene event: BUILT

Scene-placing Johnny (section 9) removed the script that used to play
`johnny_teleport_start` on him and delete him 0.25 s later, so the actor popped
when the scene exited.

`scneventsVFXEvent` is the replacement, and it passes the `gotchas.md` #17 test
by measurement rather than by looking right: 1161 of the 7067 `.scene` files in
`basegame_4_gamedata.archive` carry one. Every field was copied from
`q101_07c_johnny_triggers.scene`, which plays this exact effect on Johnny twice.

Two traps settled there, written up in `scene-playbook.md` and `gotchas.md` #33:
`effectInstanceId` is `4294967295`, not zero, because zero is a real index into
the scene's own `effectDefinitions`; and a named effect needs no declaration
anywhere, because it resolves against the performer's own entity.

`questkit.scene.Scene.fire_vfx` emits it, and `stage_johnny` fires one on all
seven beats 250 ms before the last section ends, the same number as the
`cc_g01_johnny_exit` cue. The cue stays: it costs one quest node and it is the
only signal a future script could use.

### 10k. Hoshino appeared in the wrong place, then vanished: REPORTED, FIXED

Nexus, against 1.1.3: *"For me he just spawned out of no where on the first
floor, though he was half-way in a pillar. Once I selected one of the dialog
options, he disappeared and is now no where to be found."*

**The body in that report is the scene's, not the one you fight.** The gig ships
two Hoshinos while `gig01_hoshino.scene` runs, and both carry
`Character.cc_g01_hoshino`: the one `Gig01_Encounter` spawns at captured
coordinates and the player shoots, and the one the scene spawns so his words
carry audio and a name over the subtitle. Arriving from nowhere, standing inside
geometry and vanishing when the dialogue ends are properties of a scene actor,
which is created when its scene starts and deleted when it exits.

The scene's one was buried at `(0, 0, -2.5)` from `ANCHOR_ESTATE`, on the
assumption that 2.5 m below a marker is under the floor. **Measured in game,
2026-08-17, and it is not.** The anchor resolves to (297.0, 1051.0, 229.2). The
burial point is (297.0, 1051.0, 226.7), which is 3.2 m below the terrace the
conversation happens on, and teleporting there puts you in a furnished room with
a window onto that terrace. That is the room the report describes.

Two reasons the assumption failed, and both generalise:

- **A marker's height is not a floor.** `ANCHOR_ESTATE` is a security camera, so
  its height is a mounting height. What is 2.5 m below it is whatever the
  building puts there. `gotchas.md` #36.
- **The number was never checkable at the desk.** The anchor's transform is in
  no file: cooked sectors store their node refs as hashes, and the one place the
  name is spelled out is the always-loaded name registry, which is a list of
  names and carries no positions. Searched for the string and for the FNV1a64 of
  three spellings across all 2356 quest sectors, all 2402 interior sectors and
  the exteriors covering the estate, with no hit. `ResolveNodeRef` in game
  answers in a second, and section 11 already had the probe.

**The fix removes the body rather than moving it.** The scene's Hoshino now
stands where every other voice-only actor in `gen_scenes.py` stands, a kilometre
out and a hundred metres down, so there is nothing to see, walk into or watch
disappear. His lines are made non-positional to stay audible, which is how Elena
and Nix have always worked. Burying him deeper was the alternative and it had no
safe depth: the road tunnels under the North Oak villa.

**Which field makes a line 2D, separated at last.** `inner=True` sets
`voExpression` and `visualStyle` together, and every previous reading came from
a line with both. So his two lines shipped routed differently in the same
conversation: h01 with the VO expression alone, h02 with both. Both were
audible, and both subtitles read "Hoshino: ..." in ordinary styling. So
`voExpression: Vo_Expression_InnerDialog` carries the 2D behaviour on its own,
and `visualStyle: innerDialog` changes nothing visible for a speaker who is not
Johnny. `questkit.scene.Scene.section` takes `inner_vo` for this, and both of
his lines use it.

Verified in the same run by counting rather than by looking: a targeting query
with `TargetingSet.Complete` reaches through walls, and it never saw more than
one body carrying his record at any point in the approach or the conversation.

### 10h. The double quest-phase registration: OPEN, not a known bug

The mod's `.archive.xl` registers the questphase under the base game's quest
root AND under Phantom Liberty's standalone one. That is deliberate, so a
Phantom Liberty standalone start gets the gig. Nobody has confirmed what happens
on a save where both roots are live, if that is even possible. Written down so
it is not re-derived.

### 10j. Long-pressing T declined the call, then answered it. FIXED

Reported in play 2026-08-17: holding T to decline Elena's call answers it
instead. The first reading of this blamed vanilla, and the dev menu's call trace
settled it in one look. It is this gig's bug.

```
289.6  phonecall_elena_ortega_with_player = 1   ring
291.8  phonecall_elena_ortega_with_player = 3   Rejected
293.3  phonecall_elena_ortega_with_player = 2   Talking
```

The decline lands at 291.8 exactly as it should, so the input works and
`isRejectable` is not involved (it is read in one place, and only decides
whether the button hint is drawn).

What follows is vanilla's input handling, read out of
`newHudPhoneGameController.script`: `PhoneReject` fires on
`BUTTON_HOLD_COMPLETE` while the key is still down, and `PhoneInteract` fires
again on `BUTTON_RELEASED` when it comes up, whose incoming-call branch queues
a plain pickup with **no hold check at all**. That is the 2 at 293.3, a second
and a half later.

`PhoneSystem.OnPickupPhone` does guard against this, but only by phase: it
ignores anything once the call has left `IncomingCall`. Vanilla gets there
because its per-contact holocall phase reacts to `Rejected` and ends the call.
**This file never reacted to `Rejected` at all**, so the chrome stayed up, still
answerable, and the key release answered it.

Fixed by ending the call ourselves on the next tick, 0.2 s later, which is
comfortably inside the 1.5 s the trace measured, and then waiting out the
ordinary back-off in a new state 5 rather than dropping to state 0, which would
re-ring the phone immediately. It also fixes what a decline FELT like: the ring
stopped but the banner stayed, because nothing except the 8 s timeout was going
to take it down.

The general point is the one this register keeps relearning. The first
explanation was a plausible read of vanilla source that would have led to
patching a base-game system for every call in the game. A trace the project
already writes disproved it in one look. `gotchas.md` #31.

### 10i. The reload crashes: NOT ACCEPTED, no mechanism found

Reporter A, 400+ mods: crashes roughly every second save reload, against a
baseline of one in twenty before installing.

The mod ships **no native code**, so it cannot fault directly; it can only ask
the engine to do something heavy. The only heavy thing it does at load is the
spawn burst in 10c and 10d, which those fixes reduce.

Logs and an A/B test with the mod's three folders removed are the only thing
that can settle it. If their redscript log shows a compile failure that changes
everything, and would explain unrelated mods breaking too.

---

## 11. Can a node this mod ships be addressed by name? YES, measured 2026-08-17. Fully closed by 20

The question decides how a mod places a custom NPC who has to speak. A scene
acquires an actor through a NodeRef, and so does every quest node that could
keep one hidden until the gig wants him. If a name we ship never registers,
such an NPC must be TWO bodies: one the script spawns and the player can shoot,
one the scene spawns so the words carry audio and lipsync.

`map-pins-playbook.md` said it never registers. **That is wrong, and this
section is the correction.**

### The finding

**A node in a mod sector DOES register a global name, provided the name is
written as a full path. The short form does not.**

| Name written as | `ResolveNodeRef` |
|---|---|
| `$/03_night_city/#c_santo_domingo/arroyo/#cc_g01_probe_full` | resolves, and reaches a LIVE ENTITY |
| `#cc_g01_probe_bare` | nothing at all |

The base game only ever writes the long form: every one of the 33506 nodeRefs
in `always_loaded_0` is a full path. This project only ever wrote the short
one, which is why the map-pin attempt failed and why the failure was read as
"mod nodes cannot be named" rather than "that spelling is not a name".

Naming is also what makes a node LOAD. Named probes were found in the world;
anonymous ones at the same kind of spot, four metres away, were not.

### The probe, which is reusable in ten minutes

`Gig01_Lab.reds`. Four steps, each failing differently, and the codes are the
point:

```
CreateNodeRef(path) -> ResolveNodeRef(nref, root) -> Cast<EntityID> -> FindEntityByID
  1  the name meant nothing
  2  resolved, not an entity id
  3  a real entity id, nothing streamed
  4  a live entity
```

`ResolveNodeRef` takes a **`GlobalNodeRef`** as its second argument, not the
`GlobalNodeID` the game's own `.script` sources appear to pass. The compiler
rejects the latter outright; a default-constructed local is the root.

**READ CODE 3 WITH SUSPICION ON A LONG NAME.** An absolute `$/...` path is
hashed rather than looked up, so ANY long string comes back 3, including one
that was never shipped. Only 4 is evidence. On a short name the distinction is
real: base-game short names read 3, ours read 1. A run without a long-form
negative control is void, and the first run here was exactly that.

### What a mod sector will and will not hold

- **Many nodes.** An earlier failure to load more than one was self-inflicted:
  `variantIndices` was written as one entry per node on the guess that it
  indexed them. It does not. The game's own `always_loaded_0` has 5285 nodes,
  15024 instances, and writes `[0]`. Indices pointing into an empty variant
  table silently drop everything after the first node.
- **Props, through `worldEntityNode`.** The shard has always worked this way.
- **NOT people.** Two different character entity templates were placed as
  `worldEntityNode` and neither instantiated. That fits the shipped data: a
  real exterior sector holds 25 entity nodes, 77 static meshes and 71 smart
  objects, and NO NPCs at all.

### How NPCs actually get into the world

Communities, and they are shippable. `always_loaded_0` holds exactly two node
types: 4500 `worldStaticMarkerNode` (the spots) and 785
`worldCompiledCommunityAreaNode` (which entry and phase uses which spot).

The characters themselves live in a `.community` resource, of which 4033 ship:

```
communitySpawnEntry
  characterRecordId : TweakDBID     <- a record we already ship
  entryName         : CName
  phases[] -> phaseName, appearances[]
    timePeriods[] -> quantity, hour, markings[], spotNodeRefs[]
```

`characterRecordId` takes our own `Character.cc_g01_hoshino`, and
`spotNodeRefs` takes NodeRefs, which the finding above says can be ours. The
quest side is `questCommunityTemplate_NodeType`, in 1395 shipped questphases,
which reactivates an entry by name against a spawner reference.

So the honest statement is not "a mod cannot place an NPC". It is that
`worldEntityNode` is the wrong node type for one.

**Placing one is UNSOLVED.** How a `.community` resource gets bound to the world
was not established, and nothing here should be read as a recipe.

### What it is worth, and the half that 20 later closed

**ANSWERED IN 20, 2026-08-18: a pin DOES anchor to a node this mod ships, in
the long form, and a mod can ship an always-loaded sector so that it resolves
from anywhere.** The paragraph below is what this section said before that was
measured, and it is kept because the question it asks is the one 20 answers.
Note that the drawn route built on the finding was reverted; the anchoring is
what survives.

A pin cannot currently anchor to a node a mod ships, which is why gig 01 draws
its route to the North Oak estate as a chain of markers advanced by script.
Whether a pin resolves against a LONG-FORM name has not been tested. If it
does, that whole layer becomes unnecessary.

Nothing else here is a recipe. One body per speaking NPC instead of two would
follow from placing an NPC in the world, and that is unsolved.

### On testing this yourself

The probe above is cheap to re-run and it is easy to run badly. Four attempts
here failed on the BENCH rather than on the engine: a sector field guessed to
mean something it did not, probes placed where furniture could hide them, a
negative control in a different shape from the thing under test, and an entity
template that was invisible by design.

What worked was one build that tested every suspect at once, with each variable
as its own labelled slot, positions in open air where nothing can occlude,
detection by script THROUGH WALLS rather than by eye, and one slot holding an
object known to exist as a calibration. A bench that can only be read by
looking at something cannot tell absence from occlusion.

---

## 12. The Mama Welles stand-in is buried the same way Hoshino was


**CLOSED 2026-08-18, and then made moot the same day. The stand-in itself is
deleted; see 19.** The fix below was correct and shipped for a few hours before
the thing it fixed was removed. It is kept because the reasoning is reusable and
because 19 rests on it: what it established about burial is 10k's finding, and
that outlives this scene.

**FIXED 2026-08-18, and the fix is not confirmed in game yet.** What follows
is the case as it stood; the change and how to test it are at the end.

`gig01_epilogue_standin` is the variant that plays when the base-game Mama
Welles is not in El Coyote, and its speaker is a body buried 2.5 m below
`OFFSET_MAMA`. That is the shape 10k has just shown can put a man in the room
below, and the fix there is two lines: park the actor at the default offset and
route her lines through `inner_vo`.

Two things make it a weaker case than Hoshino's, and they are why it waited:

- Her burial is better founded. `#sq018_pepevodka` was chosen for having an
  IDENTITY orientation, its position was measured, and the offset is computed
  onto her real mark rather than assumed, so the 2.5 m goes down from the floor
  she stands on and not from a mounting bracket.
- Her scene cannot be reached in a test run. It plays only when the base-game
  Mama is absent, so shipping the change means shipping a path no playtest
  covers, and the failure mode if the 2D routing does not hold for her is a
  silent epilogue.

The design call, 2026-08-17: leave it until it can be tested, or until a report
says a second Mama Welles appears in the bar. Nobody has reported one.

### What changed, 2026-08-18

The second objection went away: a save with no Mama Welles in El Coyote Cojo now
exists, so the variant can be played. With the path testable, the argument for
leaving a known burial in place was only the first objection, and 10k answers
that one. A better-founded burial is still a burial. The room below her is a
room a player can be standing in, and the failure is a body appearing in it.

The change is 10k's, applied to her:

- Her speaker moves from `(-1.668, 2.505, -3.584)` off `ANCHOR_MAMA` to the
  voice-only default, `(1000, 1000, -100)`, where every other unseen speaker in
  `gen_scenes.py` stands.
- Both her lines get `inner_vo`, so they play 2D and stay audible from there.
- The real-Mama variant is untouched and deliberately so. She stands two metres
  from V on her own community mark, which is where vanilla plays these lines
  from, so hers stay positional. `_epilogue` now routes on `real_mama`, and the
  only file that changed is `gig01_epilogue_standin.scene.json`.

`OFFSET_MAMA` is gone. Its measurement is kept in the comment where it stood,
because the number was right and the technique was what was wrong.

### How to test it

Load the save where she is absent from the bar, play to the epilogue, and watch
for three things:

- both her lines audible, at ordinary volume rather than distant;
- her name over each subtitle, in ordinary styling and not Johnny's relic
  register. `visualStyle` is untouched, so this is a check that `inner_vo` does
  what 10k measured on a second speaker;
- no second Mama Welles anywhere, including the floor below.

Silence is the failure this was weighed against, and it means the 2D routing did
not carry to her. The stand-in `Gig01_Encounter` spawns is unaffected either
way, so the visible Mama in the room is not evidence about any of this.

## 13. `securityAreaType` on Hoshino has never applied. FIXED 2026-08-18

**CONFIRMED IN GAME 2026-08-18.** The TweakXL log for the 1.2.1 build is clean:
all three yaml files read, import completed, no `Unknown property` line and no
error of any kind in 21 lines. The records did apply rather than being skipped,
which is the thing to check when a TweakXL log goes quiet: TweakDB went from
193,354 records to 193,358 and from 3,306,462 flats to 3,306,730. The four
pre-fix runs on 2026-08-17 each logged all three errors.

TweakXL rejects three properties across our two Character records, and has done
so on every run since they were written:

```
Character.cc_g01_elena:   Unknown property isPlayerCompanion.
Character.cc_g01_hoshino: Unknown property securityAreaType.
Character.cc_g01_hoshino: Unknown property isPlayerCompanion.
```

Found while reading a player's log bundle, then confirmed against this machine's
own TweakXL log on the shipped build. Not a player-side fault and not a game
version difference: the reporter and this machine both run 2.31.

Two of the three are harmless. `isPlayerCompanion: false` sets the field to the
value it already holds by default, so both lines are no-ops and can go.

The third matters for what the record's own comment claims. `hoshino.yaml`
documents `securityAreaType: Safe` as the fix that stopped him raising a
trespass alarm. The game has been discarding that line the whole time, which
means the behaviour every playtest confirmed came from the other three fields
alone: `reactionPreset: ReactionPresets.NoReaction`, `baseAttitudeGroup:
neutral` and `enableSensesOnStart: false`. The comment credits a line that never
ran.

Two things to settle:

- What 2.31 actually calls the field, if it still exists. `securityAreaType` was
  read off a 2.31 script dump, so the name is either wrong for the record type
  or the property lives somewhere other than Character.
- Whether it is worth having at all, given the observed behaviour is already
  correct without it.

### What was done, 2026-08-18

All three lines are gone: `isPlayerCompanion` from both records and
`securityAreaType` from Hoshino. Removing a line the game was already
discarding cannot change behaviour, and removing a line that set a field to its
own default cannot either, so this is a correction to the record and to what the
record claims rather than a behaviour change.

`hoshino.yaml`'s comment now credits the three fields that actually run,
`reactionPreset`, `baseAttitudeGroup` and `enableSensesOnStart`, and says that
the fourth never did.

The first question stays open and is now the only one: what 2.31 calls that
field, if it exists on Character at all. Do not put the line back on a guess.
The second question answers itself, because the behaviour every playtest
confirmed was produced without it.

**How to confirm:** the TweakXL log after a load should carry no `Unknown
property` line for `Character.cc_g01_elena` or `Character.cc_g01_hoshino`, and
Hoshino should still stand there without raising an alarm or opening fire until
he is shot. See 17 for the guards around him, which is a different item.

A wider lesson for records generally: TweakXL logs a rejected property as an
error and then applies the rest of the record, so a record can look like it
worked while quietly dropping a line. A property is only known to have applied
if the TweakXL log is clean for that record.

## 14. Narrow the shard sector's streaming box. DONE 2026-08-18, and the grid cell with it

**CONFIRMED IN GAME 2026-08-18:** the shard renders on the office desk and can
be interacted with, on the narrowed sector. The local test in this section is
therefore passed. What it does not settle is 10i, which needs the A/B.

The mod ships one sector, `cc_g01_world.streamingsector`, holding one
`worldEntityNode`: the data shard on the office desk. Its descriptor in
`cc_g01_world.streamingblock` currently reads:

```
streamingBox  Min (-5000, -5000, -5000)  Max (5000, 5000, 5000)
rldGridCell   129182
level         1
```

Both of those values were copied wholesale from GeneralShadowsFix, an installed
world-edit mod that works, and `gen_sector.py` says so in its comments. Neither
was derived from where our content actually is.

For GeneralShadowsFix a whole-map box is correct, because it edits the whole
map. For one shard on one desk in Heywood it means the sector is in range from
every position in the game and stays resident for the entire session.
`rldGridCell` is the same problem in a different field: a spatial bucket
belonging to another mod's sectors, attached to ours.

### Why this is worth changing without a proof

Two crash dumps from a heavily modded install were decoded on 2026-08-17. Both
are access violations inside the game executable, on engine job-worker threads,
with no mod DLL anywhere on the crashing thread's stack. One fired while the
world was mounting, the other seconds after it finished. Both are therefore in
the world streamer.

The sector above is the only thing this mod puts into the world streamer. That
is a coincidence of subsystem, not a mechanism, and no mechanism has been found.
What makes it worth acting on regardless is that the change is cheap, it is
locally testable, and the two values being wrong is not in doubt even if their
consequence is.

One measurement that raises rather than settles the question: at the first
crash the player's last recorded position was 92 m from `SHARD_POS`, inside the
node's own 164.710114 m `MaxStreamingDistance`, so the entity and its six
components were live. At the second crash the player was 790 m away and the node
was not live, while the sector still was.

### The change

- Replace the streaming box with one that encloses `SHARD_POS` plus the node's
  streaming distance, rather than the map.
- Derive `rldGridCell` from the shard's position instead of hardcoding another
  mod's constant. If how to derive it cannot be established, that is itself the
  finding, and it belongs here.

### How to verify

Locally: deploy, walk to the office, confirm the shard still renders and still
fires the proximity read in `Gig01_Encounter`. A sector that stops loading shows
up immediately as a missing shard.

For the crash question it cannot be verified here, because it only appears on a
load order in the hundreds. It needs the A/B in 10i.

### Related

- **10i** is the same symptom from a different reporter, and is the item this
  would close or eliminate. A second report arrived on 2026-08-17 with the same
  shape: crashes on save reload, on a 222-mod install. Both reporters describe
  the same before-and-after. The second report came with two crash dumps and a
  save that crashes on load reliably rather than intermittently, which turns
  10i's statistical A/B into a deterministic one. Ask for that A/B on that save.
- **10h** already records the questphase registered under two quest roots. That
  was re-checked against a player's log on 2026-08-17 and is not a fault: across
  38 phase-patch events only `base\quest\cyberpunk2077.quest` is ever patched,
  `ep1\quest\ep1_standalone.quest` never appears, and the phase merges exactly
  once per load.

### One stale comment to fix while in the file

`gen_sector.py`'s docstring said the gig had a second, hand-authored sector
holding two quest markers. That sector was deleted on 2026-08-14 and only one
ships now, which the `.archive.xl` states correctly. Removed 2026-08-18.

## THE ANSWER, 2026-08-18. Both values are derived now

Neither value needed a guess in the end. `all.streamingblock` from
`basegame_3_nightcity.archive` holds 23,689 shipped sector descriptors, each
carrying a grid cell, a streaming box and a sector path, and 21,332 of those
paths state their own grid coordinates in the filename. That is enough to read
the scheme off directly rather than infer it.

### The grid

```
a cell is 64 m across at level 0, doubling per level:  W = 64 * 2^level
a sector's cell index is (floor(x/W), floor(y/W), floor(z/W))
rldGridCell = (i + S/2) + S*(j + S/2) + S^2*(k + S/2)
```

`S` is how many cells the per-axis field holds: `2^(8 - level)` for an Exterior
sector, `2^(9 - level)` for Interior and Navigation ones, which sit one level
finer. So each axis is a fixed-width field with its origin in the middle, and
the cell id is those three fields packed into one integer.

**No exceptions.** Every one of the 21,332 named descriptors matches, across
seven exterior levels, five interior levels and one navigation level. The cell
size was fitted separately, by checking that a sector's own content box falls
inside the cell its name claims: 64 m at level 0 matches 6,514 of 6,517
descriptors, and 128 m at level 1 matches all 6,414.

The check that matters is a prediction rather than a fit. Feeding `SHARD_POS`
into the formula returns the cell that the vanilla sector covering that same
position actually carries, and it does so at all three levels tried:
`exterior_-4_-23_0_0`, `exterior_-2_-12_0_1` and `exterior_-1_-6_0_2`. Ours is
Exterior at level 1, which gives cell index `(-2, -12, 0)` and
**`rldGridCell = 1055294`**, replacing the borrowed 129182.

One more fact, free from the same read and worth having for a future sector:
**`rldGridCell` 0 is legal.** 2,354 shipped Quest sectors carry it, together
with a float-max streaming box. That is the game's own shape for a sector that
is not on the exterior grid. It is not the shape for this one.

### The box

Derived from the node instead of from the map: a cube centred on `SHARD_POS`,
reaching the node's own `MaxStreamingDistance` (164.710114 m) plus 50 m of
headroom, so the sector is resident before the shard comes into range rather
than in the same moment. That is about 430 m a side, against 10,000 before.

For scale, the vanilla level-1 sector sharing our cell carries a
613 x 583 x 514 m box, so this is an ordinary size for a neighbourhood.

### What is not answered

Whether any of this touches 10i. The two values were wrong and are now right,
which was true before the crash question was asked and is why it was worth doing
without a proof. The A/B on the reliable save is still what would settle it.

### How to verify locally

Deploy, walk to the office, confirm the shard renders and still fires the
proximity read. A sector that stopped loading shows up immediately as a missing
shard, and that failure is the whole local test.

## 15. Holocall lines are missing the phone filter. MEASURED AND BUILT 2026-08-18

**The answer is the section after this one.** What follows first is the entry
as it was written, kept because one of its two guesses was wrong in a way worth
seeing: the effect is not a telephone band-pass.

Vanilla holocall audio is not the same recording played flat. A voice arriving
through V's phone is band-limited and processed: thinner, with the low end
rolled off and a compressed, slightly distorted quality that reads as a radio
link rather than a person in the room. The effect is consistent enough that a
player identifies a call as a call with their eyes shut.

This mod's holocall lines have none of it. Every clip `gen_voice.py` produces is
a flat studio recording, and the same file is used whether the line is spoken by
an actor standing in a room or by a caller on the phone. The result is a caller
who sounds like they are in the room.

### What is already in place

The generator knows which lines are which. `gen_scenes.py` marks a section
`holocall=True`, which sets `scnDialogLineVoParams.isHolocallSpeaker` and makes
the line play 2D through the phone. Roughly a dozen sections carry it. Nothing
downstream reads that flag: `gen_voice.py` renders and converts every line
identically.

Each line also has its own RUID, and a RUID belongs to one line in one scene, so
a line that is a holocall is never also a world line. Whatever is done to a
holocall clip cannot affect a world clip by accident.

### Two routes, and the first one to check

**Find out how vanilla does it before building anything.** The game ships
`voiceovermap_holocall.json` alongside `voiceovermap.json` in
`base\localization\en-us\`, and the existence of a separate map for the same
lines suggests the filter is baked into separate pre-rendered assets rather than
applied at runtime. That is a suggestion and not a measurement. Settle it by
pulling one vanilla line that appears in both maps and comparing the two `.wem`
files: if the holocall one is audibly filtered, the answer is baked assets, and
the question becomes whether ArchiveXL's `localization:` section can register a
holocall map at all. Our `.archive.xl` declares `vomaps:` and nothing else, and
whether a sibling key exists is unknown.

**Bake the filter into our own WAVs.** This works regardless of how vanilla does
it, because our holocall lines resolve through our own vomap either way. Process
the clip after ElevenLabs returns it and before the `.wem` conversion, gated on
the same flag the scene generator already sets. A first approximation of the
effect is a band-pass around roughly 300 Hz to 3.5 kHz with light compression
and a small amount of saturation. The values are a starting point, not a
measurement: derive them by analysing a vanilla holocall clip rather than by
taste.

The second route is the one to build. The first is worth an hour first, because
if vanilla's filter is a runtime effect keyed off `isHolocallSpeaker`, then the
mod is missing a flag somewhere and baking would double the processing.

### Constraints

- Whatever does the processing has to run on the default Python 3.13 with no new
  dependency, which is the rule the rest of the voice tooling already follows. A
  band-pass and a compressor on a 16-bit mono WAV are writable against the
  standard library.
- Filtered clips change the audio the scene is timed against, so regenerate
  `durations.json` and re-run `gen_scenes.py` in that order after any change.
- Approval before deploy applies as it does to any voice work: judge the
  filtered WAVs first.

### Related

- `scene-playbook.md` covers holocalls and the voiceover map, including the
  `_holocall` sibling maps.
- **2a** is why a mod voiceover map is the audio route at all.
- **2f** is the clip-length re-timing that `durations.json` closed.

## THE ANSWER, 2026-08-19. It is not a filter, and that took three attempts

**Read this rather than the entry above.** The entry proposed a telephone
band-pass and asked whether vanilla bakes the effect or applies it at runtime.
Vanilla bakes it. The effect is not a band-pass, and it is not an EQ at all.

Two intermediate answers were wrong on the way here, and both are kept below
because the way they were wrong is the useful part.

### Vanilla bakes it, and a mod cannot register a variant

The game ships four processed versions of a voiced line, in four sibling
directories under `base\localization\<lang>\`, with a voiceover map for each: `vo`,
`vo_holocall`, `vo_helmet`, `vo_rewinded`. A twin carries the SAME filename as
its `vo` original, so the same stringId. Of the 78,026 English `vo` clips, 3,036
have a holocall twin, and every one of the 2,981 ids in
`voiceovermap_holocall.json` is present in the main maps as well.

`vo_corpus.py` has known this since it was written: it drops the three processed
directories when building a reference set, and says why. Nobody had joined it to
this question.

`volanguagedatamap.json` is what the engine loads, and its `en-us` entry lists
all five map chunks in one array:

```
base\localization\en-us\voiceovermap.json
base\localization\en-us\voiceovermap_1.json
base\localization\en-us\voiceovermap_helmet.json
base\localization\en-us\voiceovermap_holocall.json
base\localization\en-us\voiceovermap_rewinded.json
```

ArchiveXL appends to that array and to nothing else. Its localization parser
accepts exactly `onscreens`, `subtitles`, `vomaps`, `lipmaps` and `extend`
(`src/App/Extensions/Localization/Config.cpp`). So a mod gets one clip per RUID
and has to bake in whatever treatment the line needs. That costs nothing here,
because a RUID belongs to one line in one scene.

`isHolocallSpeaker` routes a line into the phone UI and makes it play 2D. It
applies no filter, which is why ours had sounded like the room.

### The mechanism: magnitude kept, waveform discarded

The decisive measurement is a same-source comparison. Take a vanilla `vo` clip,
run our filter over it, and compare BOTH results against the same original.

| | correlation with the source |
|---|---|
| vanilla's holocall | 0.22 to 0.38 |
| our filter, which is a known linear filter | 0.48 to 0.58 |

Per-frequency coherence says it more sharply: **0.02 above 500 Hz for vanilla,
against 0.20 for a known linear filter measured the same way.** That estimator
is biased low, which is why the linear filter was run through it as a control,
and the ratio is what matters. Vanilla is an order of magnitude less linear than
any filter can be.

So vanilla keeps the source's short-time MAGNITUDE spectrum and throws its phase
away. Everything else in the assets follows from that one fact, and none of it
had an explanation before:

- the two stereo channels decorrelated, sample correlation about 0.04, while
  their envelopes track at 0.96: two independent draws of the phase;
- the output running about 100 ms long and about 9 ms late: the STFT;
- crest factor falling from 19-23 dB to 15-17.6 dB: random phase is less peaky
  than speech, so this was never the limiter it was first read as.

### Wrong answer 1: fitting the magnitude of the wrong channel

The first build measured the LEFT channel, taking a median of per-frame ratios,
and fitted a biquad cascade to 0.79 dB rms. It measured as correct and sounded,
in the field report, *"just a tad different"*.

Two errors, both pushing the same way. **A mono clip has to match the stereo
MID, (L+R)/2, not one channel**, because that is what a mono clip is heard as,
and vanilla's decorrelated channels cancel by 4 to 9 dB through the low mids
when summed. And **the estimator has to be energy-weighted**, because a median
of per-frame ratios under-weights exactly the frames where the processing bites
hardest.

Together those made the target about 10 dB too shallow in the low mids and 3 dB
too generous at 1 kHz.

### Wrong answer 2: the corrected magnitude, still only a filter

Refitting to the mid-channel target deepened the scoop by 10 dB and shrank the
1 kHz lift by 3 dB. Per-clip spread across the seven pairs is 2 to 4 dB from
200 Hz up, so the shape is a property of the processing rather than of a
performance, and the fit reproduces it to 1.17 dB rms with both sample rates
converging on the same filter.

On vanilla's own source the tone was then within 2 to 4 dB. It still sounded
wrong, because tone was never the thing that was missing.

### What shipped

`tools/questkit/phone.py`, standard library only on the default Python 3.13:

1. the fitted EQ cascade, high-pass at 216 Hz plus four bells and a top shelf;
2. **the smear**, an STFT that keeps each bin's magnitude and rotates its phase
   towards noise by `SMEAR`, Hann in and out at a quarter hop so it sums to
   unity and `SMEAR = 0` is exactly transparent, verified at 7e-10;
3. a gentle compressor with look-ahead, a soft clip aimed at a crest target, and
   a gate that zeroes the pauses the way vanilla's do.

`SMEAR = 0.35` is an ear decision, made against vanilla's own Regina take
filtered and levelled to sit beside it. 0.5 was *"a bit too much"*, 0.25 too
little, and 0.35 was called *"basically same as the vanilla"*.

The rotation is drawn from a fixed seed, so the same master always produces the
same file. Verified by md5 across two runs, which is what makes it safe for the
filtered takes to be gitignored rather than committed.

### Two things tried and dropped, so they are not tried again

- **A drifting delay ("warble")**, a fraction of a millisecond at a few Hz. It
  destroys waveform coherence while leaving the voice natural, and it explains
  something the smear does not: that the best single time-alignment between a
  vanilla pair only correlates at 0.33 to 0.46. It lost the ear test and the
  code is gone.
- **Smearing only above a crossover**, tried at 800 Hz on the theory that an
  even smear costs the voice its body. Flat won. The code is gone.

### The build route

`gen_scenes` records which line keys are holocalls, from the same `holocall=True`
that sets `isHolocallSpeaker`, so there is one source of truth and it cannot
drift. `gen_voice` filters those masters into `source/audio/holocall/`, keeping
the filename, and hands THAT file to Wwise. The master is never touched.

The derived folder is gitignored, on the `placeholder/` precedent: derived by a
committed tool from a committed input, and reproducible. A filename suffix was
considered and rejected, because `__m` already means "the male-V take" and a
second suffix on the same axis would need `__holofilter__m`; a listing of
`source/audio/` also stops telling you at a glance which lines have real audio.

**Masters are always dry.** A pre-filtered take in `source/audio/` would be
filtered twice and nothing would catch it.

### Cost and blast radius

`gen_voice` end to end: 31 s, of which the filter is most of it. Of the 114
`.wem` in the tree, exactly 17 changed, so Wwise is deterministic for unchanged
inputs and there is no churn. `durations.json` regenerated identical across all
59 entries and `gen_scenes` regenerates byte-identically, so **the instruction in
the entry above to re-time the scenes does not apply to this change**: the filter
is sample-for-sample the same length.

### One thing deliberately not reproduced

Vanilla's holocall assets are stereo. Ours stay mono, because a holocall plays
2D through the phone UI either way, and the mid is what the measurement targets.

### Related

- **2a** is why a mod voiceover map is the audio route at all.
- **2f** is the clip-length re-timing that `durations.json` closed.
- `gotchas.md` 41 states the four-variant asset system and the mechanism, for
  gigs 02-04.
- `scene-playbook.md` covers holocalls and the voiceover map.

## 16. Johnny appears while V is driving. Reported 2026-08-18, open

Field report against 1.2.0, from a player who finished the gig: *"Even though I
know he's an engram and how all that works, but the game got me used to seeing
Johnny when he talks. It was weird him talking to me while riding a bike."*

The beat is `gig01_arasaka`, his answer as Elena's call drops. That call can be
answered anywhere, including on a bike at speed.

### Why it looks wrong

Every Johnny beat is a scene actor on an `around_player` marker, placed once at
a fixed offset in V's own frame at the moment the scene starts. `gig01_arasaka`
is `(-0.8, 2.6)`: 0.8 m to V's left and 2.6 m ahead, facing computed by
`yaw_to_face_player`. That staging was measured for a V standing still, and it
holds for a V walking.

On a bike it does not. The apparition is placed in world space and then stays
there while V rides away, so he arrives at one specific spot, is passed within a
second, and keeps talking from nowhere. The design call, 2026-08-18, is that
sprinting has the same problem in a smaller size.

### What to build

Hold the appearance until V is neither driving nor sprinting, then play it.

Three things to settle before writing it:

- **Where the gate goes.** The scenes are entered from the quest phase, which
  waits on a fact. A gate belongs on the script side that sets the fact, not
  inside the scene, because a scene cannot look at the player's movement state.
  `Gig01_Holocall.reds` already defers an action this way with `m_ftDefer`,
  which counts ticks and gives up at 150, so the shape exists to copy.
- **Which beats need it.** Of the seven in `BEAT_STAGING`, four fire where V is
  necessarily stationary and indoors (`gig01_terminal`, `gig01_shard_read`,
  `gig01_malware`, `gig01_kill`). The three that fire wherever V happens to be
  are `gig01_arasaka`, `gig01_legend` and `gig01_graves`. Gate those three.
- **The bound, which matters more than the gate.** A beat that never fires
  stalls the gig, because the quest phase is waiting on its fact. A player who
  drives from the call straight to the compound without dismounting must still
  reach the next objective. So the hold needs a cap and a decision about what
  happens when the cap runs out: fire it anyway, or drop that beat's staging
  and let the line play as inner dialogue with no body.

### Unverified

Which query answers "V is driving" has not been checked in this project.
Mounted state and the vehicle-related player states are both candidates and
neither has been compiled here. Establish it the way the redscript facts in 10c
were established, by compiling a throwaway file, rather than by assuming a name.

### Related

- **9** is where the player-relative placement came from, including the five
  runs that measured the marker's frame. The offsets themselves are correct and
  should not be re-derived; this is about when to use them.
- **3** is the apparition itself.

## 17. The spawned guards do not react to V. Reported 2026-08-18, open

Two observations from the same field report, one underlying question:

*"When I first approached the North Oak compound most of the outside security
was just standing together in a group. I did optical camo, so don't know if they
would have tried to shoot on sight."*

*"Upstairs to take out the bad guy (can't remember his name). His security /
bodyguard just let me stand there right in his face (the bodyguard and bad guy).
Was sort of expecting combat when the bodyguard saw me."*

The design call, 2026-08-18: these are the same item. The guards need to behave
like guards.

### What is actually shipped

Both squads are placed by `SpawnSquad` in `Gig01_Encounter.reds`, which asks
`FindPointInSphereOnlyHumanNavmesh` for a point near an anchor and creates the
entity through `GetDynamicEntitySystem`. Each one then gets
`SetAttitudeTowards(player, AIA_Hostile)`, retried for up to 60 s (10e).

That produces both symptoms directly.

**The huddle** is the placement. One sphere per anchor, and a navmesh query that
answers with whatever walkable point it finds first, gives a squad standing
where they were dropped. Nothing gives them a post to hold, a patrol to walk or
an idle to play, so a group is what a group of them looks like.

**The lack of reaction** is the deeper half. An attitude says how an NPC feels
about V once he notices V. It is not perception, it is not an AI role, and it is
not a reason to initiate anything. A community-placed vanilla guard arrives with
all of that from the encounter that owns him; an entity created through
`DynamicEntitySystem` arrives with none of it and holds his record's defaults.

Hoshino standing there is separate and is correct: he is deliberately
`SetNeutral` until provoked, because he is an administrator rather than a
soldier, and that is documented where it is done. The bodyguard next to him is
an ordinary member of the estate squad and was set hostile, so his standing
still is the fault.

### The confound, and what it does not excuse

The first observation was made under optical camo, so it is no evidence about
whether they would have opened fire. The second has no confound at all: V was
face to face with a hostile guard and nothing happened.

### Where to start

- **Measure before building.** Establish whether a spawned guard reacts to V at
  all, or only once shot. That is one playtest with the dev menu, walking into
  an ungated compound without camo, and it decides whether this is a perception
  problem or a behaviour problem.
- **Check what a spawned entity is missing.** Senses, an AI role and a security
  area are the three candidates. 13 is the neighbouring finding: three
  properties on our own Character records are silently rejected by TweakXL,
  `securityAreaType` among them, so the vocabulary in this area is not yet
  established for 2.31. The guards use vanilla `sts_*` records rather than ours,
  so their defaults are vanilla's, which makes it worth reading what an `sts_*`
  security record actually carries.
- **11 is the structural answer and is unsolved.** Communities are how the game
  places an NPC with behaviour attached, and the finding there is that a mod's
  own NodeRefs can be addressed, while binding a `.community` resource to the
  world was not established. If it can be, both symptoms are fixed at once,
  because a community entry brings the spots and the phase with it.
- **The cheap version, if that stays unsolved.** Place each guard at a captured
  position instead of a navmesh point, the way Hoshino already is, so a squad
  stands on posts rather than in a heap. Then add a scripted proximity check
  that forces combat when V is close and visible, which is a workaround and
  should be written up as one.

### Related

- **10c** and **10d** are the spawn faults already fixed here: the trigger
  geometry, the burst, the silently binned squad and the per-anchor latch.
- **10e** widened the attitude retry budget for the symptom "the guards ignore
  me", which is worth re-reading because it is the same sentence as this report
  arriving from a different cause. The budget is not the problem this time: the
  bodyguard was standing next to V long after any retry would have finished.

## 18. El Coyote Cojo is shut until "Heroes" is done. Measured and FIXED 2026-08-18

**CONFIRMED IN GAME 2026-08-18:** on a pre-Heroes save the on-screen message
appears and nothing starts, and a full run on a post-Heroes save plays end to
end. Both halves of the gate are therefore exercised.

The gig ends in El Coyote Cojo. A player reported the bar's entrance would not
open on an old save, so the ending was unreachable: the same shape as 8a, where
the office doors ship disabled and a main quest switches them on.

It is not the same cause, and it is not a lock, a seal or a time of day.

### What the door actually is

`double_door_simple_1` at (-1260.358, -984.223, 12.034), in
`exterior_-20_-16_0_0`, with a `worldStaticGpsLocationEntranceMarkerNode` 0.27 m
away, which is what a mapped entrance looks like in a sector. The sector ships it
`deviceState: ON`, `initialDoorState: CLOSED`, `isLocked: 0`.

In game it reported `DISABLED`. So unlike the office doors, this one ships on and
something in the base game's progression switches it off and persists that into
the save. Reading the world files could never have found this; it took the dev
menu's device dump.

### The measurement

Three saves, 2026-08-18, each dumped with the dev menu's quest-state button
against the journal, and the door observed at the same time:

| sq018 (Heroes) | q112_01 old friend | q112_02 industrial park | the door |
|---|---|---|---|
| Active | Active | Inactive | shut |
| Active | Succeeded | Active | shut |
| **Succeeded** | Succeeded | Active | **open** |

sq018 is the only column that moves with the door. The Gimme Danger objectives
rule themselves out on the same three rows: `q112_01` changes between the first
two while the door stays shut, and `q112_02` is Active in both the second and the
third, one shut and one open.

**Succeeded, not Active.** Two of the three saves are mid-Heroes with the bar
still closed, which fits the quest's own shape: Heroes sends V to the bar, and
the door opens once the ofrenda is done.

The prior agreed with the result before the test, which is worth stating because
it means this is not a pattern found by trawling. sq018 owns the place:
`#sq018_mp_el_coyote_entrance`, `#sq018_mp_el_coyote_back_entrance` and the
`03_el_coyote_funeral` objective are all its.

Two limits on the evidence, neither of which changes the conclusion. The door
readings for the three saves are by eye rather than by probe, and the 224-path
bulk dump was run on the third save only, so another quest moving in lockstep is
not formally excluded.

### How to ask the question again

`quests/side_quest/sq018_jackie`, class `gameJournalQuest`. That path is
extracted rather than guessed: it is in the string table of
`cooked_journal.journal`, next to the objective ids `01_go_to_el_coyote`,
`01_visit_el_coyote` and `03_el_coyote_funeral`.

The dev menu has two buttons for this now, added the same day:

- **LOG: which gating quests has this save done** prints five labelled entries,
  Heroes plus the three Gimme Danger objectives that gate the office doors.
- **LOG: every quest path the journal spells out (224)** is the bulk version.
  209 of the 224 resolved to an entry on the save it was run against.

The 224 are every quest path the base game holds as plain text. That is not
every quest in the game: only 6 side quests and 5 main-quest entries survive as
strings, the rest being hashes. A path that is absent proves nothing.

### The fix, and the one that was rejected

**The gig now waits for Heroes.** `Gig01_Start` gained a fifth gate,
`CCGig01StartRules.HeroesDone`, and Elena does not ring until sq018 reads
Succeeded.

It fails OPEN, deliberately. A null journal manager, a missing entry or a journal
that has not resolved yet all answer "carry on". The cost of being wrong that way
is a player meeting a shut door on an old save, which is visible and reportable.
The cost of being wrong the other way is a gig that never starts, which is
indistinguishable from a broken install and is the failure the whole of
`Gig01_Start`'s header is written against.

**The player is told, once.** The design call, 2026-08-18: a silent hold is the
same experience as the 8a bug. So when every other gate has passed and only
Heroes is missing, the gig says so on screen, latched on the fact
`cc_g01_heroes_notified` so it cannot repeat every session. The check is last in
the list precisely so the message can be specific: it can never fire at the main
menu, in the prologue, or over a loading screen.

**Forcing the door was rejected.** The machinery already exists in
`Gig01_OfficeDoors` and the dev menu confirmed it works on this door:
`ForceEnabled` took it out of DISABLED and it read ON afterwards. It was rejected
anyway, because the bar's people belong to sq018 as much as its door does. A
forced door opens onto an empty room and the closing scene of the gig plays to
nobody. Gating on the quest makes the door question disappear rather than
answering it, which is one mechanism instead of two.

### Still to do

- The requirement belongs on the mod page and in the changelog.
- A playtest on a pre-Heroes save: the message appears once, Elena never rings,
  and the gig arms on the next check after Heroes completes.
- **12 is downstream of this.** The stand-in Mama Welles exists for a bar with no
  Mama in it, and part of why she is absent may simply be that the bar was shut.
  The stand-in stays: this gate makes her rarer, not unnecessary, because she can
  still be absent by time of day.

## 19. The Mama Welles stand-in is deleted. 2026-08-18

**CONFIRMED IN GAME 2026-08-18:** the epilogue plays correctly with the real
Mama Welles on a full run. The skip branch is by construction unreachable on
such a save, so it is untested and expected to stay that way.

The gig carried a whole second path for an El Coyote Cojo with no Mama Welles in
it: a second scene (`gig01_epilogue_standin`), a script that spawned our own copy
of her on her captured mark, a despawner, a body double, an alias so the two
variants shared four recordings, and a branch in the quest graph. All of it is
gone. 12 and 7d are the history; this is the removal.

### Why it existed, and how much of that was true

*"She is not dependably in El Coyote Cojo, time of day and quest state"*
(playtesting, 2026-08-11). Half right.

**Time of day: no.** Every community entry within 80 m of the bar counter uses
the `Day` time period, all 151 of them. That is a real finding rather than a
quirk of the format, because the control says otherwise: across the 785 community
areas in `always_loaded_0` the periods are Day (5227), 6:00 PM (94), Morning
(51), Evening (38), Night (38), 6:00 AM (37) and 10:00 PM (8), and 12 of those
areas use Night. El Coyote uses none of them.

**Quest state: yes, and it is the same quest as the door.** Mama has no community
entry at all. Every node in the world data carrying her name is sq018 quest
design under the bar's own prefab: `#sq018_pr_mama_welles...`,
`#sq018_01_drink_mama_welles`, `#sq018_mama_welles_signet`,
`sq018_01_sm_mama_welles`, `mama_sm_welles_default`. The bar's community phases
say the same: `funeral`, `ofrenda`, `paying_respect`, `q000_kid_bar`, all quest
names with no ambient variant.

Confirmed in play, 2026-08-18, across times of day on a post-Heroes save: she is
there every time.

So 18's start gate does not merely make the fallback rarer. It removes the
condition the fallback was written for, because the gig cannot begin until the
quest that puts her in the bar has finished.

### What went, and what deliberately stayed

Gone: `build_epilogue_standin`, the `SCENE_ALIASES` entry, the body double,
`SpawnMamaWelles`, `DespawnMamaWelles`, the `m_mamaSpawned` and `m_mamaId`
fields, the four-tick spawn attempt, and the second scene node in the quest
graph. The subtitle count drops from 70 to 64 and the voiceover map from 63
entries to 59, which is the four aliased lines and their gendered pairs.

**The probe stayed, and the tri-state fact with it.** `cc_g01_mama_present` still
answers 1 or 2. `gig01_epilogue` acquires the real Mama and spawns nobody, so
entering it when she is absent leaves the scene holding an actor that never
resolved, and that crashed the game at teardown in August. The fork is the guard
against that crash, and the guard is worth keeping even when the branch behind it
should be unreachable.

**On 2 the quest phase now skips the epilogue** and goes straight to the fan-in,
so V walks to the counter for Johnny's closing lines without the Mama
conversation. The design call, 2026-08-18: an ending missing one conversation
beats a crash, and beats carrying a second scene and a duplicate NPC for a case
nobody should reach.

The skip lands on the same node the scene's exit lands on, and that matters:
`cc_g01_epilogue_scene_done` is what `Gig01_Encounter` reads before setting
`cc_g01_mama_talked`, which is the fact the next objective waits on. Routed
anywhere else, the skip would strand the gig on `obj_mama`.

The absent branch also got slower. It used to spawn our stand-in at four misses
and fall back at thirty; with nothing to spawn, thirty is the only threshold
left, about 45 s of standing in the bar with no Mama in range.

### What this costs if the reasoning is wrong

One conversation, on a save where she is absent despite Heroes being complete.
The gig still finishes. That is the trade taken deliberately, against a
fallback that cost a scene, a spawner, a despawner, a body double, an alias and
a graph branch to maintain.

### Related

- **18** is the gate that makes this safe, and this entry depends on it entirely.
- **12** was fixing the stand-in's burial on the same day it was deleted. The fix
  was correct and is now moot. What survives from it is the finding it rested on,
  which is 10k's: a marker's height is not a floor.
- **7d** is why the real Mama must be ACQUIRED rather than stood next to.

---

## 20. The pin lab: three things that were impossible are not. ANSWERED AND CLOSED 2026-08-18

11 left one question open, and it was the cheapest thing on the register: does
a quest map pin resolve against a LONG-FORM NodeRef of a node this mod ships?
It was answered, along with four follow-ups, over five in-game rounds against a
bench built for the purpose.

**The feature it was aimed at was built and then REVERTED.** Read this section
for the findings, not for a recipe for a route.

### What is now known, and all of it is measured

| | |
|---|---|
| A pin CAN anchor to a node this mod ships | long form only, short form is not a name |
| A mod CAN ship an `AlwaysLoaded` sector | and its nodes resolve from anywhere on the map |
| Node type is not a factor | marker node and entity node behaved identically |
| Guidance markers work from a mod | the game draws a real walking route through them |
| A guidance chain is absolute | it cannot be used for a long approach |
| A route waypoint must be off the ground | and one bad waypoint silences the whole route |

The first two are the valuable ones and they are written up in `gotchas.md` 39,
because they are not about this gig: they remove the rule that a pin's anchor
must be a base-game node in one of the game's three always-loaded sectors, which
is the constraint that has shaped every pin decision in this project. The route
findings are `gotchas.md` 40.

### The readings

Every slot was read from ArchiveXL's own log, which names each pin and says
which of three outcomes it got. `resolved to NodeRef` is a working anchor,
`Can't resolve ... position` means the name resolved and the node was not
streamed, `Can't resolve ... reference` means the name meant nothing, and NO
LINE AT ALL means the pin carried no usable reference and was never requested.

Round 1, six pins activated in one instant with the player across the city:

| slot | log | reads as |
|---|---|---|
| base-game anchor, calibration | `resolved to NodeRef` | the bench is sound |
| ours, marker node, long form | `position` | **the name resolved** |
| ours, entity node, long form | `position` | node type is not the variable |
| ours, marker node, short form | *no line at all* | not even requested |
| ours, in an Exterior sector | `position` | cold, as expected |
| ours, in an `AlwaysLoaded` sector | `resolved to NodeRef` | **works from anywhere** |

`position` rather than `reference` is the whole finding. Every earlier attempt
got `reference` and was written up as "a mod's nodes cannot be named"; they were
all written short. Re-reading warm, after teleporting onto the cold nodes,
returned byte-identical numbers: resolution happens once, at activation, and is
cached.

The route rounds then separated three suspects that had been changed together,
one at a time, and landed on the waypoints' height: the same twelve points drew
no route at V's own foot level and drew one raised 1.7 m. A half-chain test in
the same run showed the second half drawing alone while the full chain drew
nothing, which is where "one bad waypoint silences the whole route" comes from.

### Why the way-in route was built and then reverted

The gig draws its route to the North Oak estate as a chain of markers advanced
by script, and the point of all this was to replace it with a route the game
draws. It was built: an always-loaded sector of marker nodes, two pins on the
gig's own objective and guidance markers between them.

In play it was worse than what it replaced. From the gate the route drew
correctly; a few paces along it vanished, returned, and then drew a loop running
back down the road. Cutting the chain to the five waypoints covering the rocks
and the wall did not rescue it. Playtest, 2026-08-18: *"Completely broken... it
looked you were close but now nothing works ever."*

The cause is `gotchas.md` 40 and it is structural rather than a tuning problem:
the chain is absolute, and a player walking along one is routed back to its
start. A gig's approach is exactly the case guidance markers are not for.

**Everything was reverted the same evening.** The shipped tree is byte-identical
to 1.2.1 and the script marker is what runs. What survives is this section,
gotchas 39 and 40, and the corrections to `map-pins-playbook.md`.

### What this would still be worth using for

Not the way in. Two things where the same findings apply cleanly:

- **A pin anywhere, for gigs 02 to 04.** Ship one always-loaded sector of
  marker nodes and put pins wherever the design wants them, with no offset
  arithmetic and no hunting for a base-game anchor nearby. This is the finding
  worth carrying forward and it costs one sector.
- **A short discontinuity**, if a future gig has one: a staircase, a ladder, a
  single climb, covered by two or three markers with the ordinary router doing
  everything either side. That is what the 44 shipped markers are all doing.

### Closed alongside it

**Hoshino's pin will not take a GPS route.** It is the one pin in the gig with
`enableGPS` off, and the recorded reason was that the road solver drew to the
wrong side of the estate wall. Re-checked in play 2026-08-18: the route is bad
even entering by the gate, so it is not the wall and not the approach direction.
Guidance markers cannot help either, because a fixed chain cannot serve a player
who may enter from any direction. The pin stays without a route.

### Related

- **11** is the question this answers, and its "what is still open" paragraph
  is now closed by the table above.
- **9** is the player-relative placement work, which is the other half of how
  this gig positions things.
- **`gotchas.md` 39 and 40** are the same findings stated as rules, which is
  the form to reach for when building rather than when reading history.


## 21. Generators for a second gig need a subdirectory, and the export allowlist has to follow. AGREED 2026-08-19, not built

`tools/gen_*.py` are one gig's generators rather than a library. Each hardcodes
its mod folder, its LocKey prefix and its resource names, and gig 01 has taken
all the flat filenames. The half that no gig owns is `tools/questkit/`, which
they import.

The decision is a per-gig subdirectory, `tools/gig02/` and so on, rather than a
per-gig suffix on flat names.

Someone starting from a clone of the public repo is not affected either way, and
`new-gig.md` tells them to copy the generators they need and re-point their
constants, or edit them in place. This item is about a repo holding more than
one gig at once.

### Three things move with it

**The export allowlist.** `tools/export-public.ps1` allows generators with a
pattern that stops at the first slash, so nothing in a subdirectory ships at
all. `tools/questkit/` hit exactly this and needed its own line; the comment
above that line records what it cost, which was an export that shipped
generators whose imports could not resolve. The break appears only for someone
who clones the public repo, never here. A subdirectory needs its own allowlist
line written at the same time as the subdirectory, not after.

**The sys.path hop.** A generator that imports `questkit` puts its own directory
on `sys.path`, and today that directory is `tools/`. From `tools/gig02/` it
inserts the subdirectory instead, so `questkit` stops resolving. The insert has
to go up one level. Sibling imports within the subdirectory keep working, since
a script's own directory is on the path already.

**The docs that list the loop.** `BUILDING.md` names each generator by path, and
`new-gig.md` section 5 gives the run order the same way. Both describe gig 01's
flat layout.

### How it gets verified

`check-clone.ps1` already runs the generators from a fresh export with none of
this machine's caches, which is precisely the condition a missing allowlist line
fails under. Pointing it at the second gig's generators covers this without
anything new being written, and it is the same check that caught the
`rebuild_cache` split.

### Related

- **4** is the other half of the toolkit split, and lists what stayed inline in
  gig 01 rather than moving into `questkit`.
- `docs/new-gig.md` states the copy-and-re-point rule for a reader starting from
  a clone, which holds whatever this decides.
