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
| 10i | Reload crashes on heavily modded installs. Two reporters, same symptom. No mechanism found; the A/B test is now deterministic, see 14 |

**27 closed on 2026-08-25 and shipped in 1.3.0.** Route A was built and it
worked: Hoshino has a real body in this mod's own sector, the script finds it
instead of a spawned copy, the scene takes him as a first-class actor, and his
mouth moves. That retires the two-body arrangement for gigs 02 to 04 as well.
This table and 27's own heading both still said OPEN on 2026-09-05, eleven days
and two releases after the fix.

**29 closed NEGATIVE on 2026-08-24** after nine runs. A community this mod
ships spawns nobody, with both area-node shapes, both quest node types, the
identity link verified and every prerequisite proven present. Do not place NPCs
with a community. 27's route A has a shipped precedent instead, and 29 has it.

**11 closed on 2026-08-23**, by reading rather than by building. A `.community`
resource is never bound to the world because it never ships: its contents are
copied at cook time into a `worldCommunityRegistryNode` in an always-loaded
sector, keyed by a 64-bit id the mod writes on both sides. 28 has the recipe and
the measurements.

**6 closed on 2026-08-22 and shipped in 1.2.5**, after standing open since
2026-08-14. The shard on the office desk has a Take and Read prompt, carries
this mod's own title and text, and the desk holds one shard. `shard-playbook.md`
is the recipe.

**3d closed on 2026-08-23 and shipped in 1.2.6.** Both of Nix's conversations
put him on the phone as a live rendered image, in a studio this mod opens
itself, on a contact this mod invented, with none of the base game's small talk
in either direction. Every branch played, including declining it, ignoring it,
ignoring it five times, and being on a bike when it rings.

It had been reopened on 2026-08-22 after standing closed since 2026-08-13, and
that is the part worth carrying forward. It was closed the first time on one
measured fact with an untested inference stacked on it, and the inference did
not survive reading the game's own files. Same shape as 6, which stood closed
as impossible for eight days. Two of the three faults found while building it
were the same mistake in miniature: a number that measured the wrong thing, and
a symptom that named the wrong system.

Everything else is closed. Two entries look open and are not: 2f (re-time
scenes from real clip length) shipped as `durations.json`, and 0b is the
release checklist with all of it struck through. 11 is genuinely half open, and
its heading says which half.

17, 22, 23, 24 and 25 all closed on 2026-08-21 and shipped in 1.2.4. Two of
them closed without being fixed, which is worth knowing before reopening
either: the guard huddle in 17 was accepted by the design call as reading like
kill teams, and the police response in 24 turned out to be the base game's
residents rather than anything this mod places.

## Closed, and what each one still answers

| § | Closed question |
|---|---|
| 0, 0b | The gig plays end to end; the release checklist |
| 1 | Subtitle speaker-name styling. Fell out of the scene conversion |
| 2a-2i | The voice route: why a mod voiceover map works and Audioware is not needed; why reusing vanilla takes does not scale (3 of 59 lines matched) |
| 2j | Lipsync, whole mechanism. Includes `type: Tag` being dead, and a crash that took a session to attribute |
| 3, 3b | Johnny's apparition: the workspot is what makes him render at all |
| 3c, 3e | Two features deliberately NOT built. The reasoning is the value. 3e's Nix half was solved in the shipped build and the entry did not say so |
| 3d | Reopened. See the open table above |
| 5 | Three refinements from playing the finished gig |
| 7, 8 | Post-release bug reports and their fixes, including the office doors |
| 9 | Placing a scene actor relative to the player. Corrects two claims this register had wrong, and deletes the burial-and-lift workaround built on them |
| 11 | A node this mod ships CAN be addressed by name, in the long form only. Corrects the map-pin playbook, and opens communities as the route to a mod-placed NPC. Its one open half closed in 20 |
| 13 | Three properties the game silently rejects, and the field that was credited with fixing Hoshino for months without ever running |
| 14 | The world grid, derived: cell size, the rldGridCell packing, and why a whole-map streaming box was wrong |
| 15 | The holocall treatment: baked into separate assets, and a phase effect rather than a filter. Includes the two wrong answers |
| 4 | The toolkit split, finished: a config module per gig, and the generic redscript out of gig 01 |
| 21 | One gig per subdirectory under `tools/`, and the two export patterns that had to follow |
| 20 | A pin CAN anchor to a node this mod ships, and a mod CAN ship an always-loaded sector to keep it resolvable. Also why the drawn route built on it was reverted |
| 16 | Johnny is staged where V is standing, so the fix is to keep V on foot rather than to move or delay him. Also: a base-game restriction that is savable, and the three ways to put a message on screen |
| 18 | El Coyote Cojo is shut until Heroes is finished, measured across three saves. The gig waits for it and says so |
| 19 | The Mama Welles stand-in, and the whole fallback path behind it, deleted |
| 10 | The 1.2.0 bug pass: a fast-travel lock bound to the wrong state, a gig that never switched itself off, the guard spawn, a decline that answered, and (10k) a voice-only actor buried into the room below. 10i is the one still open |
| 32 | The gig is absent from every New Game Plus save: a phase parented to a file path is not in the graph an NG+ session runs. One line in the manifest |

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

Deferred 2026-08-12, settled 2026-08-13. Everyone in the gig gets a voice; the
casting is settled, do not re-open the question.

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

`tools/gig01/gen_scenes.py` paces every line with a character-count estimate
(`MS_BASE 1200 + 55ms/char`) because nothing is voiced. With audio,
`scnDialogLineEvent.duration` / `startTime` / `sectionDuration` must come from
the real clip or lines will cut off or drag. Feed measured durations in as a JSON
sidecar (line key → ms) produced when the audio is generated.

### 2g. Voice every line: DONE

Every line is voiced, the casting is stated on the mod page, and subtitles are
always on. `tools/gig01/gen_voice.py` turns a wav into a `.wem` and a
voiceover-map entry, and that half of the pipeline is the same for any custom
audio, whatever produced the wav.

**Superseded 2026-08-27:** every live line was re-recorded by a voice actor for
1.4.0. The half described here did not change, which is the point of it.

How the wavs were made changed several times before settling. Those notes are
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
  vanilla set. `tools/gig01/gen_lipsync.py` casts by clip length; worst error in the
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

### The pool was the problem, not the technique. 2026-08-23

**Reopened by a playtest of the first video holocall**, where Nix's face is in
close-up on the phone rather than two metres away in a dark office:
*"the lipsync is really really bad compared to what we did with Johnny...
especially for the shorter sentences."*

The obvious reading is that the technique had met its ceiling. It had not. The
whole difference between Johnny and Nix was HOW MANY ANIMATIONS THEY COULD BE
CAST FROM.

| | sets in the pool | worst scene, before | after |
|---|---|---|---|
| Johnny | 209 | 270 ms | unchanged |
| Nix | **7**, holding 1, 2, 5, 18, 19, 21 and 31 animations | 1477 ms | **210 ms** |

One `.anims` set serves a whole scene, so a four-line Nix scene was choosing
from at most 31 candidates. It landed 386 ms long on an 880 ms line: the mouth
still moving for nearly half a second after the words stopped, which is what
"really bad" was describing. Johnny, casting from 209 sets, lands inside 30 ms
on almost every line he has.

**The fix is one regex.** `gen_lipsync.CHARACTERS['nix']['regex']` now matches
every male civilian set as well as his own seven: 1199 sets instead of 7.
Borrowing is safe for the reason already in that file's docstring, and Hoshino
has borrowed a civilian's since 1.2.0.

**And one change to the scorer, which is the half that matters for short
lines.** Sets were ranked on the SUM OF MILLISECONDS across a scene, so a
400 ms miss on a four second line counted the same as a 400 ms miss on an
880 ms one. They are not the same: the first is a mouth slightly out of step,
the second is a mouth moving in silence. `questkit.lipsync._score` now ranks
sets on relative error, with a 400 ms floor so one very short line cannot own
the whole scene's score. Per-line choice is unaffected, because dividing by a
length that is fixed for that line cannot reorder its candidates.

What that bought on the line that prompted this, `gig01_nix_brief/b05`, wanted
at 880 ms:

```
before          1266 ms     386 over    44% too long
pool widened     966 ms      86 over    10% too long
+ relative       833 ms      47 under    5% short, and short is the safe side
```

Every line in that scene now runs slightly UNDER its clip. The scene's absolute
total went from 210 ms to 227 ms and that is the right trade: overshoot is what
reads as broken, undershoot reads as somebody finishing a sentence.

**Only Nix's six scene/actor pairs changed.** Johnny, Mama Welles and Hoshino
pick exactly what they picked before, which is the check that says the scorer
change did not disturb anything that was already good.

**Not yet judged in play.** The numbers are better; whether a civilian's facial
performance suits Nix in close-up is a question only a playtest answers, and
the picks file is committed so reverting is one `git checkout`.

#### And one line had no mouth at all, for a different reason

Playtest, after the pool was widened: *"just the first phrase when he says
how's things v, he's completely immobile, no mouth movement at all. The rest
are all good."*

`gig01_nix_brief/b01` is the one line in the gig that reuses a vanilla
recording whole (2c). It points at vanilla's `stringId` and gets the text and
the audio for nothing. It also has no `.wav` of ours, so no entry in
`durations.json`, so `gen_lipsync._wanted()` never asked for it, so it shipped
with an empty animation name. Nothing errored: the actor was configured, the
set resolved, the other four lines moved perfectly, and that one face sat still.

**It had been like that since 1.2.0** and nobody could see it, because until
the call became a video the line played behind a static contact portrait.

The duration turned out to be free. Vanilla baked a lipsync animation for that
exact line, `f_30B57ED4CF7DF000` in `nix_default`, and it is 1533 ms against
the 1537 ms this project had written down by hand. So the fix reads the length
out of the animation and casts the line with the rest of the scene; b01 now
matches to 0 ms and the other four are untouched. Gotcha 59.

Worth noticing what the shape of that bug is, because it is not specific to
lipsync: **any list built from "the things we generated" silently omits the
things we borrowed.**

#### What is still true, and what to try next if this is not enough

The mouth still says a different sentence. That part IS the technique's
ceiling: these are real recorded performances of other words, and only baked
animation would fix it.

**The untried lever is matching on the WORDS.** Each animation is named
`f_<stringId>`, and that stringId resolves to the vanilla line's text through
the English text table this repo already caches in `tools/_vo_cache/text_json`.
Scoring on syllable count, and on which vowels fall where, is the difference
between "a mouth moving" and "a mouth that looks like it is saying roughly
that". It matters most exactly where the complaint was: at one or two
syllables, the eye can count mouth openings, and at four seconds nobody can.

Duration is a decent proxy for syllable count, which is why widening the pool
helped as much as it did. It is a proxy, though, and the real thing is
available for the cost of one lookup table.

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

Swapping ghost→solid is one constant per scene in `tools/gig01/gen_scenes.py`
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

## 3d. A real VIDEO holocall: SOLVED, SHIPPED IN THE GIG, PLAYED 2026-08-23

**Both of Nix's conversations put him on screen**, in a studio this mod opens
itself, on a contact this mod invented, speaking this gig's own lines in his
own voice with his mouth moving. No base-game contact, no base-game holocall
phase, no small talk in either direction, no crash. Playtest: *"Everything
seems to be working."*

Playtest on the release build, benches removed, no dev menu: *"The playthrough
works perfectly. Test approved."* Every branch played, including declining it,
letting it ring out, ignoring it five times into the audio fallback, and being
on a bike when it rings.

**Two benches proved this and both were removed for 1.2.6.** Everything below
that names `gen_holoown_phase.py`, `gen_holotest_phase.py`, `build_holoown`,
`build_holotest` or `Gig01_HoloLab.reds` is describing what they did, not
pointing at a file. They are in the commit before `gig-01/v1.2.6` if a future
question needs them; do not rebuild them from memory. The shipped worked
example is `gen_questphase.nix_call()`.

The account below is in the order it was found, because most of it is about
what does NOT work and why. If you only want the recipe, it is in
`scene-playbook.md`; if you want the traps, gotchas 50 to 59.

**Measured in game, 2026-08-22, run one.** A mod sets one base-game fact and
gets a real video holocall: Nix rendered live on the phone, moving. No dialogue
options. No crash. The call ends cleanly on a second fact.

The 2026-08-13 account is kept at the bottom, unchanged. The facts in it are
still facts; the inference stacked on them is what has gone.

### Run one, 2026-08-22. What was measured

The whole run is one press of `holo_nix_calls_v_start_activate`, from a dev
menu, standing in the street 8.5 km from the studio, with no quest phase of
ours involved.

| observed | result |
|---|---|
| Nix's face on the phone, rendered live and moving | **yes** |
| his dialogue options | **none** |
| a crash | **none** |
| words | **none, and that is the point** |

"No words" is the finding rather than a gap. It is what the shipped files
predicted: the staging phase supplies the studio and the chrome, and the
CALLING quest supplies the dialogue. Nobody was calling.

The handshake ran exactly as `qb_holocall_initializer.questphase` says it
should, and the trace is worth keeping because it is the contract a mod has to
honour:

```
holo-A1: set holo_nix_calls_v_start_activate = 1
  +0.1  holo_setup_active = 1          the studio takes the lock
  +0.4  phonecall_nix_with_player = 1  the phone rings
  +2.0  holo_setup_started = 1         staged
        holo_setup_active = 0          lock released
        holo_nix_calls_v_start_done = 1   <- what a caller waits on
        phonecall_nix_with_player = 2  Talking
  ... 27 seconds of a live video call with nothing to say ...
holo-A2: set holo_nix_calls_v_end_activate = 1
  +0.3  holo_setup_started = 0
        phonecall_nix_with_player = 0
```

An unanswered ring is handled too: the first attempt timed out after about six
seconds and came back `holo_nix_calls_v_rejected = 1` with the lock released,
so a missed call is not a dead end.

### What this settles, and what it does not

**Settled.** Video is available to a mod. It does not require vanilla's
dialogue, it does not require vanilla's contact conversation, and it does not
crash. 3d's deciding reason is gone.

**Not settled, and it is the next build.** Whether OUR words play over it with
lipsync. Vanilla's gig briefings do exactly that, and the mechanism is visible
in `ma_std_arr_03_holocall_brief.scene`: the briefing scene acquires the SAME
body the holocall phase staged, through `acquisitionPlan: spawnSet` on its own
actor. Our scenes spawn their actors instead. So the open question is not
whether a mod can speak over a staged call, it is whether our generator can
emit an actor acquired from a spawn set, and whether lipsync lands on a body
the scene did not spawn (gotcha 16 says lipsync lands on the scene's own
actor, and "acquired" versus "spawned" has never been tested).

### Two instrument findings from the same run, both reusable

**A redscript class in a module is registered under its FULL module-qualified
name.** `ScriptableSystemsContainer.Get(n"NegativeBalanceHoloLab")` returns
null; `Get(n"CyberpunkCodes.Gig01.NegativeBalanceHoloLab")` returns the system.
Every class this project ships appears in the compiled bundle as
`CyberpunkCodes.Gig01.<Name>`, never bare. This cost two rounds of the bench
being unreachable, and it had never bitten before because nothing in the tree
had ever looked up one of its own systems by name; the only lookups are for
base-game systems, which carry no module. It also rules out reaching a mod
class as a CET Lua global, because a dotted name is not an identifier and CET
has no `_G` to go through.

**Backlog 11's warning about long paths is exact, and this run reproduced it.**
Every `$/03_night_city/...` probe read 3, INCLUDING the control naming a node
nothing ships. Only the short-form probes carried information: `#holocalls_studio`
and `#nix_holocall_camera` read 3, `#cc_g01_not_a_node_at_all` read 1, and
`#nix_sm_holocall` read 1 as well, so the marker Nix's own scene names as its
location is not a registered name and the call works anyway.

Everything studio-side read "nothing streamed" from 8.5 km away, which is
correct rather than a failure: the studio is one Quest sector and it is only in
memory during a call or while standing in it. Camera reads have to happen with
a call up.

### Run three, 2026-08-22. A mod's OWN character renders too

Spawning `Character.cc_g01_elena` onto the studio spot during a staged Nix call
puts her on the phone. Both bodies show, because the spot is one spot and Nix
was already on it: the screenshot is V standing in the studio with Elena
planted inside a cross-legged Nix, and the phone broadcasting the pair.

So the feed carries whoever is standing there, and a character the game ships
no setup for is not excluded. What is NOT solved is having ours there INSTEAD
of the base-game caller, because the room, the lighting and the camera only
appear as part of staging that caller.

Two smaller results from the same run:

- **The camera is what makes the picture.** Toggling
  `RenderToTextureCamera` on `#nix_holocall_camera` during a live call read
  `enabled before=yes after=no`, so vanilla does enable it, and a mod can
  switch it. Probing it mid-call returned `probe 4 LIVE gameObject at
  (5894.005371, 6134.676758, 0.746895)`, matching the sector file to six
  decimals, and `comps` listed `[RenderToTextureCamera]`. Only the ACTIVE
  contact's setup instantiates: Mama Welles' camera stayed unstreamed
  throughout.
- **`holocallInitializerPath` is empty on every character record**, Nix's
  included, so route 3 above is dead. The game does not use the per-character
  hook, and neither does `scnActorDef.holocallInitScn` in any scene read here.

A body will not spawn into the studio through `CCSharedWorld.Spawn`: that
helper sets `alwaysSpawned = false`, so the entity waits for a player who is
8.5 km away by definition. The lab builds its own spec with `alwaysSpawned`
on. The helper's default is right for every gig NPC and wrong for this.

### Run four, 2026-08-22. THE BENCH PASSED. Every piece works

Playtest: *"Yes, it works. Lipsync is bad but I think it's still a super
improvement."* All three observations, in order:

| asked | answer |
|---|---|
| do his lips move | **yes**, "weirdly but they do" |
| are our words in his voice | **yes** |
| does his face stay on screen through them | **yes** |

So a mod CAN put a real video holocall on screen for a base-game contact, with
its own dialogue, its own voice takes and its own lipsync, and no vanilla
conversation attached. 3d is answered.

**The lipsync looks approximate because that is this technique's ceiling, not
because the pick is poor.** The bench's two lines matched to 87 ms and 107 ms,
193 ms total, which is the best error of any Nix scene in the gig. The
animations are real recorded Nix performances of DIFFERENT sentences, chosen by
length, because baking our own is out of reach (2j). The mouth therefore moves
plausibly and says something else. Nothing in the picker will fix that; only
baked animation would, and that is still out of reach.

> **WRONG, and corrected 2026-08-23 the same day it was written.** The pick WAS
> poor. "193 ms, the best error of any Nix scene" was true and it was being
> compared against the wrong thing: the other Nix scenes, all of which were
> casting out of the same seven-file pool. Against Johnny, who lands inside 30
> ms, it is six times worse. Widening the pool took the same two lines to 27 ms
> without touching the picker at all. See 2j, "The pool was the problem".
>
> This is gotcha 31's shape exactly: an impression ("it looks about as good as
> this can get") written up as a measurement, with a real number next to it
> that measured something else.

### THE MOD-OWNED HOLOCALL: the route that works in BOTH directions

**Proven on the bench 2026-08-23.** Nix rendered live on the phone, in a studio
this mod opened, speaking this gig's own lines in his own voice with his mouth
moving, on a contact this mod invented. No base-game contact, no base-game
holocall phase, no small talk, no crash.

This supersedes the vanilla-phase route below for anything outgoing, and is
probably the right route for everything.

#### Why the vanilla phase is not enough

**A mod cannot make V CALL a base-game contact.** `nix_default.scene`, the
contact's own small talk, is the thing that SETS
`holo_v_calls_nix_start_activate` and waits on `..._start_done`. That fact is
its private handshake with the studio, not a public entry point. Vanilla quests
that ring a fixer do it by adding a branch INSIDE that conversation, which is
why it carries hooks like `q305_nix_return_call` and `q305_nix_details_explained`.

A mod cannot add a branch to a base-game scene. So setting the fact by hand
stages the studio and dials, and then Nix's own conversation owns the call: the
options appear, our scene never starts, `_start_done` never arrives, and the
gig stalls with the objective still reading "Call Nix". Measured in a
playthrough, and the latch confirmed `_start_done` never moves even watched
every frame for twenty-four seconds.

The incoming half works because the contact's conversation is not involved.

#### The recipe, all of it mod-owned

Five things, and the mod supplies every one:

1. **OPEN THE STUDIO.** It is a `category: Quest` sector with no streaming box
   and it does NOT load by proximity: standing 2.8 m from the spot, its camera
   still probes 3, "nothing streamed". Only a quest node pulls it in.
   `add_prefab_variant` shows the two variants vanilla shows,
   `#holocalls_studio_lighting` and `#<contact>_holocall_setup`. The second is
   what brings the camera, the lookat and the workspot into existence.
2. **SWITCH THE CAMERA ON.** `RenderToTextureCamera`, shipped disabled, on the
   setup's camera node. `add_toggle_component` emits vanilla's own node for it.
   **Read the state back**: `enable: 1` in a file is not evidence.
3. **ISSUE THE CALL FROM THE GRAPH**, not from script. `add_call_contact`
   emits `questCallContact_NodeType`, which carries `prefabNodeRef:
   #holocalls_studio` and is the ONLY thing that tells the phone where the feed
   comes from. `questTriggerCallRequest` has no such field, which is what
   gotcha 10 was really about all along.
   **Its caller and addressee are JOURNAL PATHS**, so `contacts/cc_g01_nix` is
   as valid as `contacts/nix`. That is what removes the small talk in both
   directions, and it is the whole reason this route exists.
4. **PUT OUR OWN BODY ON THE SPOT**, as the SCENE's own actor, spawned at
   offset (0, 0, 0) from `#holocall_marker` with `forceMaxVisibility`. The
   scene owning the actor is what makes the lipsync land with no borrowing.
5. **SPEAK.** An ordinary scene, `isHolocallSpeaker: 1`,
   `voExpression: Vo_Expression_Phone`, its own lipsync set.

`gen_questphase.nix_call()` and `gen_scenes.nix_actor()` are the worked
example. `gen_holoown_phase.py` and `build_holoown` were the bench that proved
it, removed for 1.2.6, so everything below that names them is history.

#### Four things that are easy to get wrong, all of them measured

- **CAMERA HEIGHT IS POSE, NOT CONTACT.** The 59 setups share one floor spot
  and differ in where the camera sits, because each is framed on that contact's
  pose. `#nix_holocall_camera` is at z 0.75 because Nix SITS cross-legged;
  `#mama_welles_holocall_camera` is at 1.52 because she STANDS. A plain spawned
  NPC stands, so Nix's own camera frames the air above his head. The bench uses
  Mama Welles' setup with our Nix standing in it; nothing about it is hers
  except the name.
- **THE BODY IS CULLED AT RANGE.** With the studio open, the camera live and
  running, and the player 8.5 km away, the ROOM rendered into the phone and the
  body did not. `forceMaxVisibility` on the actor's spawn params is what
  vanilla's studio actors carry, and it is what fixes it.
- **YAW AND OFFSET ARE IN THE MARKER'S FRAME.** `#holocall_marker` carries its
  own rotation of about -141 degrees, so a yaw reasoned from world coordinates
  points the wrong way. 180 was derived from "the camera is at -Y" and put him
  back to the lens; 0 is correct, and it was found by looking at him.
- **A SCRIPT-ISSUED VIDEO CALL DOES NOT CRASH.** Measured twice, with a body
  and with the studio open. It draws an empty frame. Gotcha 10's crash was
  never about the missing `prefabNodeRef` causing a fault; the field is what
  points the phone at the feed, and without it there is simply no picture.

#### The new quest node types, and they are the reusable part

`questgraph.b.node` takes the type as a FREE STRING, so emitting a node type
this project has never shipped is a matter of getting the fields right rather
than of the builder supporting it. That was the opening this whole session was
started to test, and four now exist:

| helper | node type | what it does |
|---|---|---|
| `add_phone_restriction` | `questSetPhoneRestriction_NodeType` | lock or unlock the phone, BY SOURCE |
| `add_prefab_variant` | `questTogglePrefabVariant_NodeType` | show or hide a world prefab variant. This is what makes a Quest sector exist |
| `add_toggle_component` | `questEntityManagerToggleComponent_NodeType` | switch a component on a world entity |
| `add_call_contact` | `questCallContact_NodeType` | ring the phone WITH a feed, for any journal contact |

Read every name out of the contact's own holocall scene. Prefab refs, variant
names and restriction sources are all load-bearing and none is guessable; a
wrong one is a silent no-op.

#### Two bugs in two-year-old tooling, both found by this

- **`questgraph.cname(None)` emitted `$value: null`**, where the game writes
  the string `"None"`. It never bit because every node the builder had ever
  emitted passed a real string; the component toggle's `gameEntityReference`
  carries three empty ones and is the first that did not. A node the game
  cannot read is a PHASE THAT SILENTLY DOES NOT RUN: ArchiveXL still logs
  "Merged phase" because the file went in, there is no error anywhere, and the
  dev fact simply sits there. It cost an afternoon. `questkit.scene.cname` had
  always been correct; the two were never reconciled. Gotcha 53.
- **A quest phase has a POSITION and nothing reports it.** A bench phase parked
  mid-chain looks exactly like a broken button: the dev fact stays 1, pressing
  it again changes nothing, and there is no error. The fix is a breadcrumb
  fact after every node, and the bench phase writes `cc_g01_dev_holoown_step`
  1 to 9. Gotcha 54.

### WIRED INTO THE GIG, 2026-08-23. Both Nix calls, and what a missed one does

The bench became the gig. `gen_questphase.nix_call()` is one block used twice:
`cc_g01_nixbrief`, V ringing Nix with the ledger, and `cc_g01_nixcall`, his
callback with Hoshino's address. `nix_actor(holo=True)` stopped acquiring
vanilla's studio body and spawns its own, so both scenes are the shape
`build_holoown` proved. **Not played yet.**

#### The question the wiring was actually about

Everything in the recipe above was proven with a tester pressing a button to
connect the call. The gig has a player who can decline, or be in a firefight,
or simply not hear the phone. So the question that had to be answered before
any of it could ship was what an unanswered call does, and the honest starting
position was that it stalls the gig for ever: the waits that report a pick-up
do not report a ring-out, and a quest phase that stops has no error path.

**The base game had already answered it, and reading the answer beat all three
options this was going to choose between.** `nix_holocall.scene`, nodes 356 to
444:

```
ring, isRejectable 1
  |-- questPhonePickUp, releaseOnRejection 0    answered
  |-- questPhonePickUp, releaseOnRejection 1    answered or declined
  `-- questRealtimeDelay 6.015 s                rang out
        -> scnXorNode
             -> questConditionNodeDefinition, questPhonePickUp again
                  True  -> the conversation
                  False -> holo_nix_calls_v_rejected = 1, hang up, unstage
```

Three things in that are worth more than the specific numbers:

- **The re-read at the end.** Which arm woke you is not the question. A
  declined call reports Rejected and then reports Talking a second and a half
  later (gotcha 10j), so vanilla asks the phone again, with a condition node,
  at the moment it needs the answer. This project found 10j the hard way and
  then guessed at the fix; the game had the general form of it all along.
- **Vanilla's timer is SHORTER than the phone's own.** 6.015 s against the
  phone's 8, so the graph decides rather than discovering the ring has already
  gone. Ours is longer, 10 s, deliberately: it wants the chrome fully down
  before it hangs up and rings again.
- **`isRejectable` is per call node and vanilla flips it from a fact.** Six of
  the seven call nodes in that scene are non-rejectable; only the one behind
  `holo_nix_calls_v_rejectable` offers ANSWER / DECLINE.

#### What a quest phase has instead of an XOR

`scnXorNode` is a scene node. A quest graph has no equivalent, and the
substitute is three parts (gotcha 55):

| part | node | what it stops |
|---|---|---|
| cut the losers | `questCutControlNodeDefinition` | the arm that lost firing minutes later, into the middle of the scene |
| decide once | `questConditionNodeDefinition` | a pause node's arm-and-wait semantics, where a branch can be taken twice |
| claim the race | a fact, checked then set per arm | two arms completing on the same frame sending two tokens down one chain |

`questgraph.add_race2` is all three in one call and is used five times. Only
the first of those three was actually needed for the ring race, because the
phone dies at 8 s and the timer is at 10, so the arms cannot collide. The other
two are there because the studio race and the ring-gate race have no such
argument and a beat half an hour into a gig is the wrong place to be relying on
one.

#### Four things that can never complete, and the cap on each

| wait | cap | what losing means |
|---|---|---|
| the studio streams in | 20 s | no video this time; the audio call instead |
| the phone may ring | 90 s | ring anyway |
| the player picks up | 10 s | hang up, wait 30 s, ring again |
| five rings missed | no cap | the audio call instead |

**The floor under all of it is the route that has shipped since 1.2.0.** The
graph sets `<prefix>_request` and `Gig01_Holocall.reds` rings an ordinary audio
call, with the back-off ladder that never gives up and the guards three
playtests bought. Two mechanisms, so a fault in the new one cannot end a
playthrough.

#### What stayed in the script, and why it is not all of it

The script no longer places Nix's calls. It keeps two jobs:

- **`cc_g01_ring_ok`.** Three playtest fixes are script questions and a graph
  cannot ask any of them: is the phone usable at all, is a fast travel in
  progress, is V on a bike. The graph raises `cc_g01_ring_want`, the script
  answers, and the graph waits for the answer with a 90 second cap.
- **`cc_g01_ringing`.** The fast-travel lock, which is the one thing here that
  takes something away from the player. The script used to derive the ring
  window from its own state machine and got it wrong in a way that broke fast
  travel for the rest of the save (10a). The graph knows exactly when the phone
  is ringing, so it says so, and the window is a fact rather than arithmetic.

Deleted with the old route: `VideoCall()`, `HoloFact()`, `VideoStageTicks()`,
state 10, and the video branches of `Call()` and `PhoneFact()`. All of it drove
the base game's per-contact phase, which is the route that cannot do outgoing.

#### One deliberate difference from vanilla, flagged for the playtest

`applyPhoneRestriction` is **0** on all seven of our call nodes and 1 on all
seven of vanilla's. It buys nothing measured: it is not what blocks the skip on
a video call, and this mod's calls have never carried one. Against that, a
restriction applied by a call that is then abandoned is a phone that stays
broken for the rest of the save, and gotcha 52 is about how hard a sourced one
is to remove. Worth checking in play whether anything about the call feels
loose without it.

#### Played 2026-08-23. The outgoing call works. The pick-up condition does not

Two runs. The first proved nothing: `deploy-dev.ps1` does not build the
archive, that step was skipped, and the game ran new redscript against the
previous build's graph, so both calls took their old path (gotcha 57).

The second run, on the real build:

| | |
|---|---|
| the studio opens and streams in | **yes**, both calls, `_step` 3 within two seconds |
| `questNodeLoadingCondition` clears | **yes** |
| the outgoing call (V rings Nix) | **works**, end to end |
| the incoming call (Nix rings V) | rings, is answerable, and then nothing |

**`questPhonePickUp_ConditionType` reports nothing.** Playtest: *"I can see T
and long press T. I tried to tap T and I just hung up."* The trace says what
really happened, and it is not what it looked like:

```
756.1  cc_g01_nixcall_video = 1                    the studio is there
756.1  cc_g01_nixcall_step  = 3
758.0  phonecall_cc_g01_nix_with_player = 1        ringing
758.0  cc_g01_nixcall_step  = 4
761.7  phonecall_cc_g01_nix_with_player = 2        ANSWERED, on time
767.7  phonecall_cc_g01_nix_with_player = 0        the game gives up
769.6  cc_g01_nixcall_step  = 5                    our 10 s timer, one ring missed
```

The tap worked. The pick-up condition did not fire on it, so the graph never
issued StartCall and never started the scene, and the player sat on a
connected, silent call for six seconds until the game dropped it. From his side
that is "tapping T hung up on me", which is the right description of what he
saw and points at the wrong thing entirely.

**The fact was right there the whole time**, and it is what
`Gig01_Holocall.reds` has watched since 1.0. The ring race now waits on
`phonecall_<caller>_with_<addressee> > 1` (the player did something) and
re-reads `== 2` (he answered), which is the same two-step shape as before with
a signal that can be watched in the dev menu. Gotcha 58, and it carries the
clear-before-ringing rule that comes with a persistent fact.

The two condition helpers are kept in `questgraph.py` with the measurement in
their docstrings. They are vanilla's own nodes and they work in vanilla's own
scene; the difference has not been found. Candidates: the condition resolves
against a scene's context rather than a phase's, or it tracks the call object
the scene's own call node created.

#### Third run: it works

Playtest, 2026-08-23: *"Everything seems to be working."* Both of Nix's
conversations put him on screen, in a studio this mod opens, on a contact this
mod invented, speaking this gig's lines in his own voice with his mouth moving,
answered from the phone in the ordinary way. 3d is done.

**What that run covered:** the outgoing call end to end, the incoming call end
to end, and the studio opening and closing twice in one playthrough without
either call interfering with the other.

#### Fourth run: every path, including the ones that were only reasoned about

Played 2026-08-23. The four branches that had never been exercised all behave:

| path | |
|---|---|
| declining the callback with a long press | **works** |
| letting it ring out | **works** |
| five missed rings falling back to the audio call | **works** |
| the ring gate while V is on a bike | **works** |

The decline is the one worth calling out, because it is 10j's ground and 10j
has bitten twice. Ending the call from the graph the moment the re-read says
"not answered" is what makes it behave: the banner goes, and the key coming
back up cannot answer a call that is already over.

**So the whole beat is played, in every branch it has.** Nothing in it can
strand a playthrough by any route that has been found, and the audio fallback
underneath has now been reached deliberately and seen to work.

#### The three faults this took, and what each one really was

Worth keeping together, because all three presented as "the feature does not
work" and none of them was:

| what it looked like | what it was |
|---|---|
| nothing we did was applied | the archive was never rebuilt; `deploy-dev.ps1` only copies (gotcha 57) |
| tapping T hung up on me | the tap worked; the graph could not see it (gotcha 58) |
| the beat does nothing at all | earlier in the session, a malformed CName stopping the phase (gotcha 53) |

The common thread is that a quest phase reports nothing when it goes wrong, so
every fault arrives wearing the costume of the thing under test. Two of the
three were diagnosed in minutes from the dev menu's fact trace and the third
from a file timestamp. Neither is a debugger; both beat one here.

### THE SKIP: closed 2026-08-23. It is the game's behaviour, and we match it

**A video holocall cannot be fast-forwarded, in vanilla either.** Confirmed in
play: *"You are right and I was wrong. Cannot skip video also in vanilla."* So
the gig loses nothing by matching it, and there is nothing here to fix.

Getting to that took most of a morning and eliminated a wrong suspect, which is
worth writing down because the suspect was extremely plausible.

**What the difference looked like.** Two calls, one instrument, one session:

```
Elena  (skips)      elena=2   locks=[]
bench  (will not)   nix=2     locks=[PhoneCall,PhoneCallDeviceActionRestrictions]
```

Our own calls carry no phone restriction, because `Gig01_Holocall.reds` sets
`isPlayerTriggered = false` on purpose; a staged holocall carries two. The
project's own note from 2026-08-15 said the restriction was what stopped the
first Nix call being hurried. Everything pointed one way.

**It was wrong, and the disproof is clean.** The release node below takes both
locks off for the whole call, and the skip still does not work:

```
57.8  locked    locks=[PhoneCall, PhoneCallDeviceActionRestrictions]
58.1  connected locks=[]
60.3  still     locks=[]
```

The remaining difference is the call MODE, and the game's fast-forward logic
has two independent gates, visible in the compiled scripts:
`IsBlockedByPhoneCallRestriction` (now excluded) and `PhoneBBStateBlockingFF`,
which asks the phone what kind of call is up.

### A phone restriction is released BY ITS SOURCE, and that is a new capability

Worth keeping even though it did not buy the skip, because it is the first
quest node type this project has emitted outside the four it started with.

`qb_holocall_initializer.questphase` locks the phone through
`questSetPhoneRestriction_NodeType` with `forcedApply: 1` and a NAMED SOURCE
(`NPC_phonecall`, or `nix_phonecall` in the per-contact copy). A forced,
sourced restriction is tracked by that source, so removing the RECORD does
nothing: measured twice, through both `StatusEffectHelper.RemoveStatusEffect`
and `StatusEffectSystem.RemoveStatusEffect`, twice each. One of the two locks
comes off that way and `GameplayRestriction.PhoneCall` never does.

The release is the same node with `applyPhoneRestriction: 0` and the same
source string, which is now `questgraph.add_phone_restriction`. **The source
string is load-bearing**: wrong source, silent no-op.

`b.node` taking the type as a free string is what made this a matter of getting
four fields right rather than of the builder supporting it, exactly as the
session was opened to test.

### The bench for the last question, built 2026-08-22 and RUN. It passed

The one thing still open is whether OUR words move HIS mouth. `gig01_holotest`
answers it, and nothing in the gig is touched:

- `gen_scenes.build_holotest` makes a two-line scene whose speaker is acquired
  from the `nix_holo` spawn set, the way `ma_std_arr_03_holocall_brief.scene`
  acquires the NCPD dispatcher. Both takes are md5-identical copies of Nix's
  existing ones under bench keys.
- `gen_holotest_phase.py` gives it a quest phase of its own, entered on
  `cc_g01_dev_holotest` and nothing else. A separate resource, because a second
  scene node inside the gig's phase crashed the game on load and a second edge
  into an existing one silently does nothing.
- `gen_lipsync.py` now covers Nix. The entry excluding him said a holocall
  "draws a static contact portrait, not a rendered caller", which run one
  disproved. His picks come from the game's own `nix.anims` sets.
- **It must come out before any release.** The `.archive.xl` entry says so and
  lists everything to remove.

The body double is deliberately NOT the route. It was built for this exact
shape in August and crashed the game twice, deterministically 4.3 s in at scene
teardown, when an additional speaker's actor never acquired. The studio body
has to be the speaker.

### Four bench faults, and every one of them looked like a finding

This is the part to read before building the next bench. Four separate rounds
of testing measured the bench rather than the game, and each one arrived
disguised as a result about the holocall.

- **The bench was unreachable, twice.** A redscript class in a module is
  registered under its FULL module-qualified name, so
  `Get(n"NegativeBalanceHoloLab")` is null and
  `Get(n"CyberpunkCodes.Gig01.NegativeBalanceHoloLab")` is the system. What
  saved it was a control: `PhoneSystem` resolved by name in the same press, so
  the container was fine and only the name was wrong. Gotcha 50.
- **The probe read nothing and said `?`.** `GetAllBlackboardDefs()` is nil in
  CET's sandbox; it is `Game.GetAllBlackboardDefs()`. The pcall swallowed it
  into a question mark, so a whole run's comparison was of two unknowns. It
  reports which of three things was missing now. A probe that cannot say why it
  failed is worse than no probe.
- **The bench died after one run.** A quest phase's progress is SAVED, so a
  linear dev branch runs once per SAVE and not once per load, which is what its
  comment claimed. The dev fact sat at 1 with nothing listening, which looks
  exactly like a broken button. Vanilla's holocall phase loops; ours does now.
  Gotcha 51.
- **Two buttons were both called "run the bench".** The plain one got pressed,
  which is the only sensible thing to do, and the experiment never ran. There
  is one button now and it does the whole sequence, probe included. A bench
  that needs the right button in the right order measures the instructions.

The common thread is that all four were caught by reading state back rather
than by trusting that a call had worked, and the two that were NOT caught that
way (the module name, the duplicate button) cost the most time.

### What the files said before any of this was run

The section below was written from the shipped data alone, before the bench
existed. It is kept because it predicted the result, and because the mechanism
is the part a future gig needs.

### The two claims, separated

**Still true, and measured:** a call issued from script with
`questTriggerCallRequest` and `questPhoneCallMode.Video` hard crashes the game
the moment the player answers (`gotchas.md` 10). That request type carries no
`prefabNodeRef`, so nothing tells the phone where to point a camera.

**Not true, and never tested:** that the only way to get a video feed is to
hand the whole call to vanilla's per-contact holocall phase, and that doing so
drags that contact's small-talk options in with it. Both halves fail on the
shipped data.

### What the shipped data says

Read on 2026-08-22 with WolvenKit CLI out of `basegame_3_nightcity.archive`
and `basegame_4_gamedata.archive`, plus CET's decompressed TweakDB string
table.

**The video feed is one global render target.** All three shipped
`base\cinematics\cameras\holocall_camera*.ent` carry a
`gameuiHolocallCameraComponent` named `RenderToTextureCamera`, shipped
`isEnabled: 0`, and all three write to the same
`base\cinematics\cameras\holocall_camera_render_texture.dtex`. Nothing about
the feed is per-contact. Enabling any one of those components should fill it.

**The holocall studio is a real room, and it is one room.** It sits off the map
at about (5894.2, 6135.8, 0), and the whole of it is a single Quest sector,
`quest_ec82d0423d8f1435.streamingsector`: 639 nodes, 59 per-contact setups
under `$/03_night_city/ne2/#holocalls_studio`. The setups are near-identical.
51 of the 59 workspots are the same point, and `#holocall_marker` in
`always_loaded_2` is that same point, which follows from only one person ever
being on a holocall at once. Nix's camera and Mama Welles' camera are 15 cm
apart and both are copies of the same `.ent`.

**Vanilla stages it with ordinary quest nodes.** `nix_holocall.scene` is a copy
of the shipped template `base\cinematics\scene_blocks\
sb_holocall_initializer.scene`, with the placeholder `NPC` replaced by `nix`
throughout. It activates the `nix_holo` spawn set, puts the body in
`#nix_holocall_workspot`, shows two prefab variants, enables
`RenderToTextureCamera` on `#nix_holocall_camera` through
`questEntityManagerToggleComponent_NodeType`, and issues
`questCallContact_NodeType` with `mode: Video` and
`prefabNodeRef: "#holocalls_studio"`. `base\quest\graph_templates\
qb_holocall_initializer.questphase` is the matching quest-phase template, and
every `base\quest\holocalls\<contact>\<contact>_holocall.questphase` is a copy
of it with the contact's name substituted into ten fact names.

**The staging phase supplies no dialogue at all.** `nix_holocall.scene` holds
two dialogue lines and no choice nodes. The words come from the CALLING quest.
A shipped gig briefing, `ma_std_arr_03_holocall_brief.scene`, does exactly
this: it sets `holo_ncpd_dispatcher_calls_v_start_activate`, waits on
`..._start_done`, speaks its own lines through its own actor, then sets
`..._end_activate` and waits on `..._end_done`. That is the entire contract,
and it is the shape a mod would copy.

**The small talk belongs to the contact, not to the call.** Nix's ordinary
phone conversation is `base\quest\tertiary_characters\default_dialogues\
nix_default.scene`, which carries an entry point named `holocall_in` and four
choice nodes. It is a per-character default dialogue, reached by a different
route from the holocall phase.

The gig already proved the practical half of that in playtest and wrote the
result into shipped code without the register catching up: `Gig01_Holocall.reds`
`Contact()` rings `cc_g01_nix` rather than the base game's `nix`, and its
comment records why. "A mod contact has no conversation behind it. Same name,
same avatar, none of the baggage." So a mod that wants video does not have to
accept vanilla's options, because it does not have to use vanilla's contact.

**Every Character record carries a `holocallInitializerPath` flat.** The TweakDB
string table has one for all 7433 character records, including this gig's
`Character.cc_g01_elena`. `scnActorDef` carries the matching
`holocallInitScn` field. That is the game's own per-character hook for "which
scene stages this person's holocall", and it is writable by a mod. What the
base-game records actually hold is a runtime read, because TweakDB values stay
hashed on disk.

### What follows, if the bench agrees

Three routes exist where the register said there were none.

1. **A base-game contact, vanilla staging, our words.** Set
   `holo_<contact>_calls_v_start_activate`, play our own scene, set
   `..._end_activate`. Costs nothing to try and is one fact.
2. **Our own contact, our own staging.** Ship a copy of
   `qb_holocall_initializer.questphase` and of `sb_holocall_initializer.scene`
   with our fact names, enable a studio camera, put our own body on the studio
   spot. No base-game contact is involved anywhere.
3. **`holocallInitializerPath` on our own Character record**, pointing at our
   own initializer scene. The sanctioned hook rather than a workaround, if it
   turns out to be honoured for a mod record.

Lipsync is not expected to be a separate problem. The caller in the studio is
the SCENE's own actor, which is the condition gotcha 16 states, so the
`animLipsyncMapping` route that 2j already ships applies unchanged.

### The bench

`Gig01_HoloLab.reds` plus a section of the CET dev menu, both added 2026-08-22.
It runs entirely outside the quest: load any save, open the menu, work down the
list. Nothing has to be started and no beat has to be reached.

The redscript is one method, `Run(cmd, a1, a2, a3) -> String`, so a new
experiment is a new BUTTON rather than a new build. Redscript needs a quit to
desktop and Lua does not.

| button | what it tests |
|---|---|
| SELF-TEST | that the bench is wired up, before ten buttons fail for one reason |
| PROBE, 10 paths | that a mod can address the studio by name. Two of the ten are names nothing ships and MUST read 1 |
| PROBE, components | that a studio camera really carries `RenderToTextureCamera`, so "not found" later is a finding rather than a broken instrument |
| READ, `holocallInitializerPath` | what the base-game records actually hold |
| TEST A | vanilla's phase, fired by one fact from a mod. Does video appear, and do Nix's options appear with it |
| TEST B | the camera alone, with no call at all |
| TEST C | driving the chrome ourselves, with the contact and the mode as free text, and the three phases as separate buttons |
| SPAWN | our own Elena on the studio spot, facing the camera |
| TELEPORT | into the studio, to see the room rather than infer it |

`holo_setup_active` is a mutex on the studio and a test that leaves it at 1
blocks every later test, so there is a button that clears the whole `holo_*`
set, and the live readout shows all ten facts.

The trace file carries the base-game handshake facts now
(`holo_setup_started`, `holo_setup_active`, the four `holo_nix_calls_v_*`, and
`phonecall_nix_with_player`), because `call_trace.log` writes and closes per
line and this is the one area of the game known to hard crash.

### What is still unknown

- Whether the base-game holocall quest phases are live on an ordinary save, or
  whether their parent graph has to be entered first. The readout answers this
  in one press: if `holo_setup_started` never moves, the phase never ran.
- Whether the studio sector streams in when a mod asks, rather than when a
  vanilla scene anchored inside it asks. `#nix_sm_holocall`, the marker Nix's
  scene is located at, is in neither the studio sector nor the always-loaded
  ones.
- Whether the crash in `gotchas.md` 10 is caused by the missing
  `prefabNodeRef` or by the phone finding an empty render texture. TEST C
  separates them: same call, camera on and camera off.
- What a mod-shipped `.questphase` copy of the template does, which is only
  worth building once the bench says the mechanism works at all.

### The 2026-08-13 account, kept

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

**Nix's half was solved since, and this section never said so.** The gig
stopped ringing the base-game `nix` and rings its own `cc_g01_nix` instead,
which has no conversation behind it to offer. `Gig01_Holocall.reds` `Contact()`
carries the change and the reason, and it is in the shipped build. Where those
options come from was read off disk on 2026-08-22:
`base\quest\tertiary_characters\default_dialogues\nix_default.scene`, entry
point `holocall_in`, four choice nodes. They hang off the CHARACTER, so a
contact this mod invents has nothing there. Mama Welles at the bar is a
different mechanism and is still as described above.

That matters beyond tidiness. 3d was closed on the belief that a video holocall
and these options arrive together, and they do not.

If it is ever revisited, the one untried idea is swapping the epilogue to our own
**stand-in** Mama, who has no vanilla dialogue at all. Rejected for now because
it risks two Mama Welles in the bar during the final beat of the gig, which is a
much more visible failure.

## 4. Housekeeping. DONE 2026-08-19

**The account of what each item became is the last subsection here.** What
follows first is the entry as it stood, so the bullets below still describe the
tree before 2026-08-19: `shared/scripts` is no longer empty and the anchors are
no longer stated twice.

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
  entry asks for, and it has now been produced: `python tools/gig01/gen_lipsync.py`
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

### DONE 2026-08-19. What each loose end turned into

Every item above is closed. Taken in order:

**The `.archive.xl` and the `gen_lipsync` guard** closed earlier, and their
accounts are above.

**`design.md`'s dialogue draft is gone.** It held a rival copy of the script
with `[VDB: check]` and `[REWRITE]` annotations, and three of the four
conversations had already drifted from it. What replaced it says where the two
authoritative texts are: `docs/dialogue.txt`, generated from the scenes so it
cannot disagree with them, and `gen_scenes.py` for the reasoning behind each
line. Both annotations are explained there rather than deleted, because what
they were asking is worth keeping: reuse-only was measured (3 of 59 lines) and
the rewrites happened in the generator.

**The anchors are stated once**, in `tools/gig01/gig01_config.py`, along with
the paths, the LocKey prefix and the quest id. That file is the whole of what a
second gig re-points: `gen_journal`, `gen_localization`, `gen_questphase` and
`gen_scenes` now import it rather than each spelling out
`mods/gig-01-negative-balance/source/wkit/raw/mod/negative_balance`.

**`gen_localization` is split.** The onscreens envelope is
`questkit/localization.py`; what stays in the gig is 87 strings. The CR2W header
went the same way into `questkit/cr2w.py`, which removed the tenth copy of the
WolvenKit and game version numbers: they move together every time either is
updated, and ten places is ten chances to miss one.

**`gen_lipsync.pick` moved too.** The search, the scoring and the two failures
worth stopping on are the same for any gig; the cast and the list of lines that
want a mouth are not. `gen_voice` was left alone deliberately: what is inline in
it is the cast tables, and its machinery is already `questkit/voice.py`.

**The generic redscript is out.** `Gig01_Encounter.reds` went from 2,276 lines
to 2,010, and `shared/scripts/` from two modules to five:

| Module | What moved into it |
|---|---|
| `CCShared_World` | `Scatter`, the navmesh-snapped squad placement, next to `Spawn` which was already there |
| `CCShared_Attitude` | hostile and neutral, and the retry that waits 60 s for a spawned body to stream in |
| `CCShared_Hud` | the upload progress bar, next to the warning banner |
| `CCShared_Mappins` | markers registered at runtime, and the rule about always pairing one with a Hide |
| `CCShared_Rewards` | eddies and Street Cred |

Three DelayCallback classes went with them, so a gig no longer declares its own.
The playtest evidence attached to each piece moved with the code rather than
being summarised: the guards in walls that produced the navmesh snap, the
attitude budget that produced the 60 s, and the progress bar that closed on
FAILED are all in the shared files now.

What deliberately stayed in the gig: the ring the squad scatters on (how tight
it should be is a property of the room), the record lists, `CCGig01Places`, the
latches, and the fact guard on the payout.

**How it was verified.** `check-scripts-repo.ps1` compiles the repo through the
vendoring; a second check runs every generator on a clean tree and compares byte
for byte, and it caught the one real mistake in this pass: three new modules had
never been committed, so a fresh checkout got an ImportError. Same
trap as `questkit/phone.py`, and the same check found it. The archive rebuilds to
the same 2,256 KB.

**What this does not prove.** Nothing here was playtested. Every generated file
is byte-identical, so the archive is the one that was played; the redscript is
not, and the two behaviours to watch on the next play are the compound guards
turning hostile and the way-in marker appearing and clearing.

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


## 6. The shard prompt - SOLVED 2026-08-22, and it ships

**The shard on the office desk has a Take and Read prompt.** It is the game's
own shard case container, in a sector this mod ships, holding this mod's item,
standing where the desk's original shard stood, and the `.archive.xl` deletes
that original so the desk carries one. The account below is kept in full,
because most of it is still true and the parts that are not are marked.

### The recipe, in three lines

- **NAME THE NODE.** `QuestPrefabRefHash` as a full `$/03_night_city/...` path,
  repeated in the sector's own `nodeRefs`. This is what the whole section was
  missing. An unnamed node in a mod sector DOES NOT LOAD AT ALL.
- **BRING THE INSTANCE DATA ACROSS WHOLE**, all 53 fields, lifted
  mechanically.
- **POINT `itemSecondaryAction` AT YOUR OWN ACTION RECORD**, whose
  `journalEntry` names your onscreen entry. That, and not any name field, is
  where a shard's title and text come from.

**`docs/shard-playbook.md` is the authority now.** It carries the whole recipe
written for a stranger: the journal entry, the item record, the named node, the
read detection, a checklist and a symptom table. This section keeps the
history, including everything that failed on the way. Gotchas 47, 48 and 49
carry the individual traps.

**PLAYED END TO END, 2026-08-22.** Both routes: read in place with [R], and
taken with [F] then read out of the inventory. Also read from the Shards list
in the journal. All three complete the beat, and the gig runs to its end
afterwards.

### What the 2026-08-14 account got wrong, and what stands

The section used to open with the paragraph below, and its central claim, that
a verbatim copy of the working container is inert in a mod sector, was FALSE.
The copy was inert because its node had no name, and naming was never varied.
Everything else here stands and is worth keeping.

---

The shard on the office desk is read on proximity, not with an [F] prompt,
because a prompt on a mod-placed object could not be made to work. Every route
tried is below, with its outcome, so that a future attempt starts after them
rather than among them.

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

### What was tried, and what each one did

| route | outcome |
|---|---|
| `DynamicEntitySystem` + `templatePath` | entity attaches, prompt works, **the mesh never renders**. It is an NPC and device spawner, not a prop placer |
| `exEntitySpawner.Spawn` | a Codeware native for **CET Lua only**. `unresolved reference` from redscript |
| `worldEntityNode` in a mod sector | **renders**, once the sector copies a working mod's conventions field for field |
| a scripted interaction on that node | class attaches, component resolves, hotspot definition loads, choice published on the default AND `Loot` layers, collider on "Interaction Object", targeting component present, and `GetActiveInputLayers` never reports one active layer |
| a **verbatim** copy of the working vanilla container | same template, same appearance, all 53 instance fields, same node flags, produced mechanically rather than retyped. **Equally inert** |
| swapping the item on the vanilla container | never ran: no `ShardCaseContainer` takes control within 12 m of that desk |

**Where to start if it is revisited:** whatever binds a container to the loot
system is not in the node, the template or the instance data. Find that and the
prompt follows. Do NOT start by writing another bespoke entity.

### Method notes, which cost more than the fix

These are why the account above is trustworthy, and each was a wasted round.

- **Copy the thing that works, first.** The office desk had a working shard on
  it the whole time. Rounds went into debugging a bespoke design instead of
  diffing it against the shipped one twenty centimetres away.
- **A copy made by hand is not a copy.** The first "verbatim" container was read
  off a dump and retyped: eight of fifty-three fields, `persistentState`
  missing. It looked like a copy in the diff. The second was produced by a
  script reading the vanilla sector, which is what the word has to mean.
- **Never gate your only evidence on the thing you are testing.** Two
  diagnostics in a row wrote their fact INSIDE the check under test, so "never
  ran" and "ran and was rejected" looked identical, and those need opposite
  fixes. Set the evidence unconditionally, then narrow.
- **A probe that samples at the wrong moment is not a probe.** The first hotspot
  reading ran two seconds after the entity attached, with V nowhere near the
  desk. Hotspot layers activate off screen-centre distance. It was a correct
  answer to a useless question.
- **A look-at capture returns the aim ray's hit point**, not an entity origin,
  and a prefab-instanced node's runtime transform need not be where its node
  says. Two attempts died on a 1 m radius test against such a point. Identify a
  thing by what it IS, not by where you think it is.

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

### 2026-08-22: the vanilla sector, read off disk

Everything above stands. What follows is new, and it is where the next reading
comes from.

The office desk is in `exterior_-4_-23_0_0.streamingsector`, in
`basegame_3_nightcity.archive`. The shard on it is that sector's node 527, a
`worldEntityNode` on `base\gameplay\loot\shard_cases\shard_case_container.ent`,
appearance `shard_case_container_kitsch_c`, holding
`Items.generic_hanako_flowers_shard`. Its nodeData entry differs from the one
this mod ships in three fields, and no previous round varied any of them:

| field | vanilla | ours |
|---|---|---|
| `QuestPrefabRefHash` | a full `$/03_night_city/...` NodeRef, repeated in the sector's own `nodeRefs` | `0` |
| `sourcePrefabHash` | `17977730056932040999` | `0` |
| `Pivot` | the origin of the prefab it was instanced from | `(0, 0, 0)` |

**The name is the suspect.** Counted across that whole sector, every node type
carrying gameplay state is named and every purely visual one is not:

| node type | named / total |
|---|---|
| `worldEntityNode` | 118 / 118 |
| `worldDeviceNode` | 8 / 8 |
| `worldSmartObjectNode` | 150 / 150 |
| `worldStaticMeshNode` | 0 / 279 |
| `worldStaticLightNode` | 0 / 272 |
| `worldStaticDecalNode` | 0 / 166 |

A container carries a `persistentState` (`ShardCaseContainerPS`, in its own
instance data), persistent state has to be keyed to something that survives a
save, and the node's name is the only candidate in the file. Section 11 already
proved the other half: a node this mod ships DOES register a global name, in
the long `$/...` form only. That was measured for scene acquisition and has
never been applied to the shard.

`persistentNodes` is empty and `persistentNodeIndex` is 0 in the vanilla sector
as well as ours, so those two are not it.

**What ArchiveXL 1.27 can do to a shipped sector**, read out of its own string
table: `nodeDeletions`, `nodeMutations` (position, orientation, scale, mesh,
material, effect, entityTemplate, appearance, meshAppearance, recordID),
`instanceDeletions`, `instanceMutations`, `actorDeletions`, `actorMutations`.
There is no addition. That closes the third route listed for this section: a
mod cannot append a node to a vanilla sector, so its own sector is the only
place one can go. It also means the vanilla container's `itemTDBID` cannot be
rewritten from an `.archive.xl`, because that field is not on the mutation
list.

Deleting the vanilla node IS available, and `expectedNodes: 939` with
`index: 527` is in the `.archive.xl` now. That is how the desk ends up with one
shard rather than two.

### A second finding, about the text rather than the prompt

`Items.cc_g01_shard` clones the vanilla shard, and a clone inherits
`objectActions`. **That is the field the reader is driven from**: `ReadAction`
resolves its journal entry through `GetJournalEntryFromAction(TweakDBID)`, off
the ACTION record rather than off the item, and the base item's action is an
inline record whose `journalEntry` flat points at The Flowers of Silence.

So the record as it stood would have shown our title in the loot list and
opened the vanilla text. `source/tweaks/shard.yaml` now ships
`ObjectAction.cc_g01_shard_read` and points `objectActions` at it. Named rather
than inline, because a generated inline name cannot be checked from the dev
menu or grepped for in the TweakXL log.

The flats were listed by decompressing CET's `tweakdbstr.kark`, which is the
route in `gameplay-restrictions.md`. It gives names and not values, so what
`journalEntry` points at is inferred from the title rather than read, and the
override needs the dev menu's "shard item record" readout to confirm it applied.

### The bench

Twelve objects in one line in the street outside the compound gate, three
metres apart at chest height, plus a working vanilla container in the office as
slot 0. `tools/gig01/gen_bench.py` builds them, `Gig01_LootBench.reds` reads
them, and the dev menu draws the table. The slot numbers are the same in all
four places.

| slot | what it varies |
|---|---|
| 0 | CONTROL: a vanilla container in the office, untouched |
| 1 | the inert copy, NAMED in the long form |
| 2 | the inert copy, anonymous |
| 3 | `sourcePrefabHash` and `Pivot` alone |
| 4 | NAMED in the short form, which section 11 says does not register |
| 5 | named, prefab hash, pivot and the vanilla streaming distance |
| 6 | the same, holding `Items.cc_g01_shard` |
| 7 | the same, in a sector whose only difference is `level: 0` |
| 8 | named, with no instance data at all |
| 9 | named, on the street story's own shard case template |
| 10 | named, on the gig's bespoke `cc_g01_shard.ent` |
| 11 | anonymous, on the bespoke entity: the configuration that ships today |
| 12 | the desk, after the `.archive.xl` deletes the vanilla shard |

Five numbers per slot, and the first three are written on every sample before
any condition is tested: `seen`, `kind`, `ref`, then `aim` and `hub`. `hub` is
the answer, and it is the number of interaction choices offered while the
player was looking at that object.

**Two calibrations, and a run is void without both.** Slot 0 must read a
prompt, or the detector is broken. Slot 11 must be found at all, or the bench
sector did not load and nothing else in the table means anything.

### Run one, 2026-08-22. It moved the question

| slot | seen | kind | ref | aim | hub | |
|---|---|---|---|---|---|---|
| 0 | 0 | 0 | 3 | 0 | 0 | CONTROL, never reached |
| 1 | 1 | 3 | 4 | 0 | 0 | named long |
| 2 | 0 | 0 | 0 | 0 | 0 | anonymous |
| 3 | 0 | 0 | 0 | 0 | 0 | prefab hash only |
| 4 | 1 | 3 | 1 | 2 | 0 | named short |
| 5 | 1 | 3 | 4 | 2 | 0 | all vanilla |
| 6 | 1 | 3 | 4 | 3 | 0 | all vanilla, our item |
| 7 | 1 | 3 | 4 | 5 | 0 | level 0 |
| 8 | 1 | 3 | 4 | 0 | 0 | no instance data |
| 9 | 1 | 3 | 4 | 1 | 0 | street story case |
| 10 | 1 | 2 | 4 | 0 | 0 | our bespoke entity, named |
| 11 | 0 | 0 | 0 | 0 | 0 | our bespoke entity, anonymous |
| 12 | 2 | 3 | 4 | 0 | 0 | the desk |

**A NAME IS WHAT MAKES A NODE LOAD.** Every named slot was found and every
anonymous one was absent, 8 out of 8 against 0 out of 3, with the two kinds
standing four metres apart in the same row. Section 11 said this in passing
about its own probes; it is now measured against a deliberate control.

Note what the name does NOT have to be. Slot 4 carries a short-form name, which
reads `ref` 1, meaning nothing registered it, and it loaded anyway. So loading
follows from the node carrying a name at all, and resolving follows from the
long form. Two different things.

**The thing that loads is a real container that draws nothing.** `kind` 3 on
every container slot, so the `ShardCaseContainer` class attaches and the
targeting system can see it. Playtest, 2026-08-22: *"I don't see anything"*, and
a screenshot from inside the compound shows an empty street. So the object is
there, it is the right class, it is targetable, and it has no visible body.

That is worth stating as a symptom rather than a theory, because a shard case
has NO mesh component: `shard_case_container.ent` carries an
`entPlaceholderComponent` named "root" and thirteen gameplay components, and
every visual comes from the appearance. Slots 13 and 14 vary the appearance
name to test it.

**No prompt on any of the five that were looked at, AND THE RUN IS VOID ON
THAT POINT.** Slot 0 was never reached, so there is no reading off a working
container, and "these offer nothing" cannot be told from "the probe cannot see
a prompt". This is the failure mode the bench design was supposed to prevent
and it happened anyway, because the calibration needed the player to go
somewhere. `cc_g01_bench_anyhub` is the fix: the largest prompt seen anywhere
at any time, whatever it belonged to, so a door on the way past calibrates the
probe with nobody doing anything.

**The sector patch did not run**, and that is gotcha 47: `expectedNodes` and
`index` count instances, not nodes. Corrected to 1242 and 591.

Three changes followed: pins on every slot, since there was nothing on screen
to walk towards and five of eleven were never looked at; every number kept as a
best-ever within a run rather than a snapshot, so a walk and then a visit to
the office build one table; and the bench moved into
`cc_g01_world.streamingsector`, the one sector this project has ever got to
render, so that "did the sector load" stops being a second unknown.

### Run two, 2026-08-22. THE PROMPT WORKS

**A container this mod places in its own sector renders, and it offers
"F Take / R Read".** Photographed on four separate slots. The section's opening
claim, that a copy of the working vanilla container is inert in a mod sector,
is wrong as of this run, and what made the difference is the node's NAME.

The recipe, stated so it can be built from:

- a `worldEntityNode` in a mod sector, on
  `base\gameplay\loot\shard_cases\shard_case_container.ent`;
- **NAMED**, `QuestPrefabRefHash` a full `$/03_night_city/...` path, repeated
  in the sector's own `nodeRefs`;
- carrying the vanilla node's `instanceData`, the whole 53-field
  `ShardCaseContainer` chunk, lifted mechanically.

What turned out NOT to be needed, each measured against a slot that omits it:

| | |
|---|---|
| `appearanceName` | not needed. Slot 14 has none and draws the right case and prompts |
| `sourcePrefabHash`, `Pivot` | not needed for a prompt |
| the vanilla `MaxStreamingDistance` | not needed |
| sector `level` | 0 and 1 both work |

What IS needed, and it is the one that bites:

- **The instance data.** Slot 8 is named and has none, and it renders as an
  oversized flat grey slab with no prompt at all. The template's own defaults
  are not a container.
- **The name.** Slots 2, 3 and 11 are anonymous and were absent again, second
  run running.

**The desk is right.** Slot 12 read `ref` 3, down from 4, so the `.archive.xl`
deletion of the vanilla shard took once the instance numbers were corrected.
Slot 15 read `seen` 1 with `aim` 24, so the gig's own shard survived the bench
moving into its sector. One shard on that desk.

**The prompt readout was wrong, and the run is still readable because of the
screenshots.** Slot 0, the working vanilla container, read `aim` 81 and `hub` 0
while the screen showed "F Take / R Read". A container's prompt is the LOOT
hub, and `UIInteractionsDef` carries several side by side: the probe read
`InteractionChoiceHub` alone. It now reads that, `LootData` and
`ActiveChoiceHubID` and takes the largest.

**A name does not have to RESOLVE, only to exist.** Slot 4 carries the short
form, reads `ref` 1 (nothing registered it), and was photographed with a
working prompt. So the node-name effect on loading and on loot is separate from
the NodeRef registry that section 11 measured. The long form is still what to
ship, being the only spelling the base game uses.

**`Items.cc_g01_shard` applies in full**, read live off TweakDB, 2026-08-22:

| flat | value |
|---|---|
| `Items.cc_g01_shard.displayName` | `LocKey(17972147436644121231ull)`, which is `cc-g01-shard-item`, "Data shard" |
| `Items.cc_g01_shard.objectActions` | `[ObjectAction.cc_g01_shard_read]` |
| `ObjectAction.cc_g01_shard_read.journalEntry` | our own onscreen path |
| `Items.generic_hanako_flowers_shard_inline0.journalEntry` | `onscreens/emails/generic/shards/night_city_people/generic_hanako_flowers`, untouched |

That reading also caught a mistake: overriding `objectActions` REPLACES the
array rather than adding to it, and the base item's array is
`[ItemAction.Drop, <inline read action>]`. The first cut listed only the read
action, which would have shipped a shard the player cannot drop.
`ItemAction.Drop` is back in `shard.yaml`.

**THE LOOT LINE IS THE SHARD'S JOURNAL TITLE. It is not the item's name, and
it never was.** Read off the game's own files, so it cost no playtest:

- `base\journal\cooked_journal.journal`, entry `generic_hanako_flowers`, has
  `title: LocKey#7190` and `description: LocKey#7189`.
- `base\localization\en-us\onscreens\onscreens_final.json` resolves
  `LocKey#7190` to "The Flowers of Silence. A biography of Hanako Arasaka.",
  word for word the string on screen. `LocKey#7189` is the shard's BODY text,
  which is different again.
- `Items.generic_hanako_flowers_shard`'s own DisplayName accessor returns
  `None`. The vanilla item has no name at all and still shows that title.

That also settles which item the container holds, which three rounds could not.
The tooltip's bottom line is "Recovered from a desk in the Arasaka office in
Arroyo", and the vanilla journal's description is the biography's opening
sentence, so that line can only be `Items.cc_g01_shard.localizedDescription`.
Confirmed independently by the look-at probe: `THIS IS SLOT 6 (0.0 m off)`,
`itemTDBID = Items.cc_g01_shard`.

Every name field on the item was therefore the wrong tree, including the two
this section previously recorded as suspects. The record applies in full and
always did:

| flat | value | ours |
|---|---|---|
| `Items.cc_g01_shard.displayName` | `LocKey(17972147436644121231ull)` | yes, FNV1a64 of `cc-g01-shard-item` |
| `Items.cc_g01_shard.localizedDescription` | `LocKey(13831536494401013575ull)` | yes |
| `Items.cc_g01_shard.objectActions` | `[ObjectAction.cc_g01_shard_read]` | yes |
| `ObjectAction.cc_g01_shard_read.journalEntry` | our onscreen path | yes |

**The question is now narrow.** The game resolves a shard's journal entry and
lands on the VANILLA one, although our action names ours. ROADS 1 to 5, five
live TweakDB rewrites tried in one session, changed nothing on screen.

**FOUND IT: `itemSecondaryAction`.** The item record read back live gave it
away, once the line was read to the end rather than truncated:

```
Items.generic_hanako_flowers_shard.objectActions
  [ItemAction.Drop, ItemAction.Disassemble]
```

No read action in it. A shard reaches its reader through
`itemSecondaryAction`, which names an inline ObjectAction record
(`Items.<shard>_inline0`) whose `journalEntry` flat is the onscreen path. All
335 shards ship that way. A `$base` clone inherits `itemSecondaryAction` still
pointing at the BASE item's inline record, so it shows the base item's shard
whatever is overridden on the clone itself. Gotcha 48.

`shard.yaml` now sets `itemSecondaryAction: ObjectAction.cc_g01_shard_read`,
and no longer overrides `objectActions`, which was the wrong property and was
silently costing Disassemble.

**What the same run ruled out, each with its own slot.** Every one still read
the vanilla title:

| | |
|---|---|
| slot 18, our item alone, 20 m from anything | AREA LOOT IS NOT IT |
| slot 19, our item, area loot off | nor the flag |
| slot 16, name on the container, our item | container `displayName` is not read |
| slot 17, name on the container, vanilla item | nor does it override the item |
| ROADS 1 to 6, six live TweakDB rewrites | no change |

**Three of those roads never ran, and the bench said they had.** CET's Lua
sandbox has no `_G`, so the helper that built a LocKey threw, and the `pcall`
around each road turned that into a silent FAILED in the log nobody read.
ROADS 2, 3 and 5 were reported as tried without executing a line. That is the
same shape as the method note at the top of this section about gating evidence
on the thing under test, in a new place.

**A note on `inline0`, because the readout is misleading.** After ROAD 1,
`Items.cc_g01_shard_inline0.journalEntry` reads as our path. `TweakDB:SetFlat`
CREATES a flat whether or not the record exists, so that is the button's own
value echoed back, not a discovery. `inline0 objectActionUI` stayed MISSING,
which is what says the record still does not exist.

**The Lua blackboard probe did not discriminate**, and is worth recording as a
dead end rather than repeating. CET returns `InteractionChoiceHub`, `LootData`,
`ActiveInteractions` and `DialogChoiceHubs` as opaque userdata whose fields do
not read from Lua, and `ActiveChoiceHubID` sat at -1 with a loot prompt on
screen, so -1 is its "no hub" sentinel. The redscript now reads the two hubs
and tests the id for `> 0`.

**Delete the bench once this closes**: `tools/gig01/gen_bench.py`,
`Gig01_LootBench.reds`, the two bench sectors, the bench block, its line in the
`.archive.xl` and the dev menu panel. Keep the sector patch.

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

The two spheres became **the outline**. Four corners of the compound were
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

### 10h. The double quest-phase registration: CLOSED 2026-08-19, both parents verified

The mod's `.archive.xl` registers the questphase under the base game's quest
root AND under Phantom Liberty's standalone one. That is deliberate, so a
Phantom Liberty standalone start gets the gig.

Nothing is duplicated. One questphase file, `mod\negative_balance\quest\gig01.questphase`,
is named twice because there are two possible parents and a save loads one of
them. This is not the kind of duplication item 4 lists, where the gig-01 anchors
are two copies of the same values that can drift apart.

**Both parents are shipped resources, checked here 2026-08-19.** An FNV1a64
lookup of each path against the archive file tables finds
`base\quest\cyberpunk2077.quest` in `basegame_4_gamedata.archive` and
`ep1\quest\ep1_standalone.quest` in `ep1_2_gamedata.archive`. The standalone
start is a base-game feature rather than a separate product: Phantom Liberty
requires Cyberpunk 2077, and the standalone start is a new-game option that
begins in Dogtown with a pre-made V. Vanilla's compiled scripts carry
`IsExpansionStandalone`, `m_standaloneButton`, `m_ep1StandaloneTutorial` and six
`EP1_Standalone_*_StartingBuild` records, one per lifepath and body variant.

The runtime behaviour was measured against a player's log on 2026-08-17: across
38 phase-patch events only `base\quest\cyberpunk2077.quest` is ever patched,
`ep1\quest\ep1_standalone.quest` never appears, and the phase merges exactly
once per load. Dropping the ep1 line would remove the gig for standalone-start
players and would gain nothing.

The reusable part is the check, not the answer: any depot path can be confirmed
to exist by hashing it FNV1a64 (lowercase, backslash separators, and forward
slashes do not match) and searching the `RDAR` index at the offset in the
archive header. `new-gig.md` states the two-parent rule for a new gig.

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

### A DETERMINISTIC REPRO, AND A MECHANISM THAT FITS. 2026-08-25

A third reporter, on **1.2.6**, with an A/B that is the best evidence this item
has ever had:

| | |
|---|---|
| died at the North Oak estate, reloaded the last checkpoint | crash to desktop, **5 of 5** |
| same save, same section, mod removed entirely | no crash, **0 of 4** |

Not reproduced on the development machine, so there are no local dumps. What
follows is read off 1.2.6's own source rather than off a stack.

**The estate spawn chain ran on delayed callbacks and had no guard against the
world going away.** `SpawnEstateSecurity` called `SpawnStep(true, 0, 0, 0)`,
which placed one squad through `CCSharedWorld.Scatter` and then scheduled the
next link a second later, six times. The audit re-armed the chain every few
seconds for as long as the player was on site, and the "already populated"
state was a FIELD on a ScriptableSystem, so it did not survive a reload and
every anchor read as empty again.

Dying and reloading a checkpoint tears the world down with links of that chain
still in flight. `Scatter` asks the navigation system for a point and then asks
Codeware to create an entity, so a stale link lands on a world that is
unloading or half re-mounted and does both.

**The file already knew about this class of fault and guarded the wrong half.**
`FinishSpawn` opens by checking the QuestsSystem exists, with a comment saying
that dereferencing a system that is not there had "flatlined the game once
already". `SpawnStep`, which is the half that touches the navmesh and spawns
entities, had no such test.

That also explains the shape the earlier reports never did. 10i's two decoded
dumps were access violations on engine job-worker threads in the world
streamer, with no mod DLL on the stack, one while the world was mounting. A
callback spawning into a mounting world is that, and it is why the trigger is
specifically death-and-reload rather than ordinary play.

**It is a mechanism that fits, not a proof.** Nothing here was traced to a
stack, and the reporter's dumps have not been read.

### WHAT 1.3.0 DOES ABOUT IT

The chain is deleted rather than guarded. Both sites are communities, so the
reload path is one `ResolveNodeRef` and one `GetGameObjectsFromSpawnerEntityID`
that return in the same tick, and the mod spawns nobody at all. The bodies are
placed by the game's own community system, which is what it does for its own
NPCs everywhere.

`CCSharedWorld.Scatter` keeps a guard anyway, because it stays in the shared
library and the next gig that drives it from a callback would walk into the
same trap.

**1.3.0 also puts SIX always-loaded sectors into the world streamer where 1.2.6
had one**, three communities with an area sector and a registry sector each. The
registry sectors carry a whole-map box by recipe (66 part 2). That is new load
in the exact subsystem the dumps point at, so this must be A/B tested rather
than assumed: a build that removes one crash and adds another would read as
unchanged.

### THE TEST THAT SETTLES IT

Give the reporter a 1.3.0 build and ask for the same protocol they already ran:
die at the estate, reload the last checkpoint, five times. Their A/B is
deterministic, which is what every earlier round of this item lacked.

Worth attempting on the development machine too, on 1.3.0, since the sequence
has never been tried here: reach the estate, die, reload the last checkpoint,
five times.

---

## 11. Two questions under one number. Both are now closed

**Read this first, because the number covers two things and only one of them
is finished.**

| | |
|---|---|
| **Can a node this mod ships be addressed by name?** | **CLOSED.** Yes, measured 2026-08-17, in the LONG form only. 20 then confirmed a map pin anchors to one. |
| **What binds a `.community` resource to the world?** | **CLOSED.** Answered in 28 on 2026-08-23: nothing binds it, because a `.community` resource never ships. The guards at both sites are placed this way from 1.3.0. |

They arrived together because the first was asked in order to answer the
second, and the heading said "fully closed" for months while the table above
listed 11 as open. Both were half right.

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

## 15. Holocall lines are missing the phone filter. DONE, RELEASED IN 1.2.2 ON 2026-08-19

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
the clip before the `.wem` conversion. A first approximation of the
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

## 16. Johnny appears while V is driving. Reported 2026-08-18, FIXED 2026-08-21

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

## THE ANSWER, 2026-08-21. Keep V on foot, rather than moving Johnny

Three things were wrong with the plan above, and the third one is the useful
finding.

**Holding a beat is wrong for two of the three.** `gig01_arasaka` and
`gig01_graves` are replies to a call that has just ended. A wait of minutes
lands them out of context, which is a worse beat than the one being fixed. Only
a beat that is not a reply can be held.

**Burying him does not help.** A scene actor is one fixed point in the world
whether it sits 2.6 m ahead or 2.5 m under, so the audio recedes from a moving V
either way. Elena and Nix only sound right on the move because they are
holocalls going through the phone system rather than world speakers. There is no
version of this that plays the line acceptably to a rider.

**So the answer is not about Johnny at all.** Keep V on foot for the few seconds
the beat needs, with two gates:

- the phone does not ring while V is riding, and
- V cannot get into a vehicle between a call starting and its beat ending.

Three windows, declared by the quest graph as `cc_g01_vlock` and enforced from
the holocall system's existing tick. Elena's call to `gig01_arasaka`, Nix's
brief to `gig01_legend`, Nix's callback to `gig01_graves`. The ring itself is
covered by a separate test, because the graph cannot open a window until V picks
up.

Elena's ring gate is deliberately uncapped: before that call there is no journal
entry, no objective and no pin, so the player cannot perceive a wait. The two
Nix gates are capped at 90 s, because an objective on screen is telling the
player to make or take the call.

### The restriction has to be your own

`GameplayRestriction.VehicleNoInteraction` does the blocking, and it is savable
with no useful duration: applied, saved, quit to desktop, relaunched and loaded,
it comes back still blocking. Uninstall the mod while it is applied and the save
can never enter a vehicle again, with nothing left to lift it.

`savable` is a field on the record, so ship a clone with it off. Four lines of
yaml, measured three ways: the clone still blocks, nothing reaches the save, and
the TweakXL log is clean with the counts moving by exactly one record and
twenty-four flats. See 13 for why the last check is not optional.

### A restriction blocks silently, and that reads as a broken mod

Three ways to put a message on screen, and only the third is right for this:
`OnscreenMessage` is cyan and left of centre and easy to miss entirely,
`WarningMessage` is red at the top and reads as an alarm, and
`UIInGameNotificationEvent` gives the base game's own "ACTION BLOCKED". The
third is what vanilla sends when a gameplay restriction refuses an action. It
carries no words of yours and every member of its type enum looks the same.

`docs/gameplay-restrictions.md` has all of it, plus the route to reading TweakDB
record names off disk that produced the record list without starting the game.

### One dead end worth not repeating

A `@wrapMethod` on `VehicleComponent.DetermineInteractionState`, to suppress the
prompt from script and store nothing at all. It compiles and crashes the game on
load, because that method runs as a script task on a job worker thread.
`gotchas.md` 44 has the tell to grep for before wrapping anything.

### Safeties, and one that was wrong first time

The lock is derived every pass from the window fact and from what is actually
applied to the player, never from a remembered flag, so there is no latch to
stick. A three-minute cap covers a window fact that never closes.

Firing the cap sets `cc_g01_vlock_giveup`, without which the seatbelt becomes
the fault: quest facts are saved, so a window fact stuck at 1 would cost the
player the first three minutes of every session for the rest of that save.

**That fact was permanent in the first version and that was too blunt.** One
local failure would have disabled all three windows for the whole playthrough.
It is cleared the moment nothing wants a lock at all, a state a stuck window
fact never reaches and a healthy one reaches seconds after every beat.

### Played end to end 2026-08-21, and shipped in 1.2.3

The ring gate on foot and riding, declining and ringing out, all three windows,
the beats staged beside a stationary V, the message at a vehicle and its absence
away from one, and the dismount prompt.

## 17. The spawned guards do not react to V. Reported 2026-08-18, MEASURED, FIXED and CLOSED 2026-08-21. The huddle was accepted as-is

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


### CORRECTION, read at the desk 2026-08-21: the estate squad is never made hostile

The paragraph above says both squads get `SetAttitudeTowards(player, AIA_Hostile)`
and that the bodyguard "was set hostile, so his standing still is the fault".
That is not what ships. `SpawnSquad` applies the attitude inside `if !estate`,
so the office detail gets it and the estate detail gets nothing at all
(`Gig01_Encounter.reds`, the block whose comment is headed COMPOUND GUARDS ONLY).

The reasoning behind that block is on the record and was sound when it was
written: playtesting on 2026-08-13 found the compound guards ignoring V while
the estate detail behaved correctly, and read the difference off the two record
lists. The compound list is mostly `sts_*` street-story security, whose default
affiliation does not treat V as an enemy; the estate list is Arasaka combat
archetypes, which do. Asserting the attitude only where the default was wrong
follows from that.

So the estate bodyguard was standing on his record's default, not on an
attitude this mod set. Two things follow.

- The 2026-08-13 reading is now contradicted by the 2026-08-18 one, on the same
  squad. Either the defaults changed under a game update, or the earlier reading
  was of a guard who happened to react and was generalised.
- Whether asserting hostility on the estate squad too would fix it is untested,
  and it is the cheapest thing to try. It is also not obviously the right fix:
  if the office squad is hostile and ALSO does not react, the attitude was never
  the lever, and the huddle and the missing reaction have one cause rather than
  two.

The bench reads both squads the same way, so one walk answers this.

### CORRECTION: no squad anchor sits on Hoshino

The report puts a bodyguard "right in his face" upstairs with Hoshino. The
nearest estate anchor to `Hoshino()` is `EstateSideEntry`, about 16 m away, and
the scatter reaches 1.8 m out from an anchor. So the man beside him is probably
not ours, and if he is vanilla then none of this section applies to the second
observation.

The bench reports whether whatever V is aiming at carries our tag, which settles
it before any of the rest is worth arguing about.

### The bench, built 2026-08-21

`Gig01_Bench.reds` plus the dev menu's "Estate bench" panel. It reads, per quarter second:

- every tagged guard within 200 m
- how many of them read back hostile to V
- how many are Alerted, and how many are in Combat
- for whatever V is aiming at: its attitude, its high-level state, how many
  threats its target tracker holds, and whether it is one of ours

The high-level state is what separates the two explanations this section offers.
A guard who is Relaxed with V in front of him never noticed, which is
perception. One who is Alerted or in Combat and still does nothing has noticed
and will not act, which is behaviour.

The threat count is the stronger reading of the two, because it is the list the
combat AI picks targets from. Hostile on paper with an empty tracker is this
section answered outright. `TargetTrackerComponent` has no `IsThreat` in 2.31
whatever the name suggests; `GetHostileThreats(true)` is the call that compiles.

The panel shows a vanilla NPC through the same row, which is the control. A
bench that can only read the suspect cannot tell an empty field from a field
that is always empty, which is the lesson 11 paid for.


### MEASURED 2026-08-21, and it is the attitude after all

Read off the estate readout in one playthrough, walking in without camo.

| where | guards within 200 m | hostile to V | alerted | in combat |
|---|---|---|---|---|
| approaching the gate | 12 | 0 | 0 | 0 |
| at the gate | 22 | 0 | 0 | 0 |
| in the grounds, standing among them | 25 | 0 | 0 | 0 |
| once a fight had started by other means | 20 | 20 | 0 | 20 |

So the reaction is in the records and it is intact. The last row is the whole
squad flipping together the moment combat exists. What none of them ever does is
start it, because not one of them held V as an enemy: twenty-five of them, at
6.3 m, with V in the open.

That settles the question this section opened with. It is not perception. A
guard who is Relaxed with V standing in front of him has nothing to perceive V
*as*. The three candidates listed above, senses, an AI role and a security area,
did not need to be examined, because the field that was supposed to be set was
not set.

The 2026-08-13 reading that produced the `if !estate` was of a squad in the last
row's state, not the first.

### FIXED 2026-08-21, awaiting verification

The `if !estate` is gone from `SpawnSquad`, so both squads get the pairwise
`CCSharedAttitude.Hostile`. The record lists are untouched, which keeps the two
tiers of security looking different, and that was the reason the guard was
written the way it was.

Open, from the same design call: the estate detail should read as *more*
alert inside the grounds than at the gate. The inner anchors already draw the
harder archetypes (sniper, netrunner, shotgun tactician) against the plainer
ranged guards outside, so the tiering exists in the records. What "more hostile"
should mean beyond that is not defined yet, and detection range is the obvious
candidate.

The huddle is NOT addressed and is still open. This section always held two
faults, and only the attitude one is fixed: they still stand where the navmesh
query dropped them, with no post, patrol or idle. 11 remains the structural
answer and remains unsolved.

### CLOSED 2026-08-21: both halves, and the second was not fixed

The attitude half is fixed and confirmed in play: the estate detail is hostile
at the gate and inside, and the readout that measured twenty-two guards and zero
hostile now measures them all.

**The huddle was accepted rather than fixed, by the design call.** *"It's ok,
sounds like kill teams. More difficult."* A squad standing in a tight group
where the navmesh dropped them reads as a fireteam holding a position, and it
makes the fight harder rather than worse. Nothing about it was changed.

That matters for what it does to 11. The huddle was the standing reason to want
communities working, because a community entry brings spots and a phase with it
and would place these guards with somewhere to stand. Nothing else here needs
that now, so **11 loses its last consumer in gig 01** and stays open as research
for a future gig rather than as a blocker for this one.

**"More alert inside than at the gate" was dropped.** *"Ignore, they plenty
aggressive."* The tiering that already exists in the record lists, harder
archetypes on the inner anchors, turned out to be enough once the attitude was
set, so nothing needs a detection range.


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


## 21. Generators for a second gig need a subdirectory, and the packaging has to follow. DONE 2026-08-19

`tools/gen_*.py` are one gig's generators rather than a library. Each hardcodes
its mod folder, its LocKey prefix and its resource names, and gig 01 has taken
all the flat filenames. The half that no gig owns is `tools/questkit/`, which
they import.

The decision is a per-gig subdirectory, `tools/gig02/` and so on, rather than a
per-gig suffix on flat names.

Someone starting from a clone of this repo is not affected either way, and
`new-gig.md` tells them to copy the generators they need and re-point their
constants, or edit them in place. This item is about a repo holding more than
one gig at once.

### Three things move with it

**The packaging.** Whatever selects which files are packaged has to learn
about a new subdirectory at the moment it is created. `tools/questkit/` was the
first one here, and until its rule was written the package carried generators
whose imports could not resolve. The break never appears on the machine that
built it, only in a fresh checkout, which is the reason the check below runs
from one.

**The sys.path hop.** A generator that imports `questkit` puts its own directory
on `sys.path`, and today that directory is `tools/`. From `tools/gig02/` it
inserts the subdirectory instead, so `questkit` stops resolving. The insert has
to go up one level. Sibling imports within the subdirectory keep working, since
a script's own directory is on the path already.

**The docs that list the loop.** `BUILDING.md` names each generator by path, and
`new-gig.md` section 5 gives the run order the same way. Both describe gig 01's
flat layout.

### How it gets verified

A check already runs the generators from a fresh checkout with none of this
machine's caches, which is precisely the condition a missing packaging rule
fails under. Pointing it at the second gig's generators covers this without
anything new being written, and it is the same check that caught the
`rebuild_cache` split.

### Related

- **4** is the other half of the toolkit split, and lists what stayed inline in
  gig 01 rather than moving into `questkit`.
- `docs/new-gig.md` states the copy-and-re-point rule for a reader starting from
  a clone, which holds whatever this decides.

### DONE 2026-08-19. Gig 01 moved first, so the layout could be tested

Waiting for gig 02 would have meant writing a packaging rule for a directory
that did not exist. Gig 01's generators moved to `tools/gig01/` instead, ten
files: the seven that write a resource, plus `gen_lipsync`, `gen_voice` and
`dump_dialogue`. `find_pin_anchors.py` and `vo_corpus.py` stayed flat: they read
the game rather than one gig, so they belong beside `questkit/`.

**The path hop.** Each generator that imports `questkit` now puts its parent
directory on `sys.path` explicitly, rather than relying on its own directory
being `tools\`. Sibling imports (`gen_lipsync` reading `gen_voice`) keep working
untouched, because a script's own directory is on the path already. `REPO` is
one `dirname` deeper in all ten, and every output path is derived from it, so
that line is the one to check first if a generator ever writes to the wrong
tree.

**A rule that selects by path breaks when the path changes**, and a per-gig
subdirectory changes every one of them at once. Anything matching on
`tools/<file>.py` has to be rewritten to match wherever in `tools/` a gig now
keeps that file, and matching on the filename rather than the full path is what
survives the next move.

**What verified it.** A check makes a clean tree, deletes the caches, runs
every generator and compares the output byte for byte. It passes. Its generator
directory is now a variable at the top.

**One thing it turned up.** `docs/dialogue.txt` was stale: it still carried
`gig01_epilogue_standin`, the scene deleted with the stand-in in 19.
Regenerating it as part of this dropped that scene and four lines, and the file now reads 60 spoken lines across 14 scenes. Nothing
shipped in the archive was affected; the .scene resources have been regenerated
many times since, and all of them came out byte-identical here.

## 22. Hoshino's marker does not follow him once he moves. Reported, MEASURED at 96 m, FIXED and CLOSED 2026-08-21. The marker never needed to move

Field report, playing the estate without stealth: V enters the residence, kills a
guard, and Hoshino joins the fight rather than waiting to be spoken to. V kills
him during the fight, before the conversation. **The objective marker stays where
he started while he is somewhere else entirely.**

### Why it happens

Hoshino's marker is anchored to a captured position, not to Hoshino. The whole
placement layer works this way: `CCGig01Places.Hoshino()` is a fixed point taken
in game with the dev menu, and `pin_hoshino` is activated alongside `obj_hoshino`
by the quest phase. Nothing reads where the man is standing at the time.

That is correct for the intended path, where he stands at his desk and waits.
It is wrong the moment he walks, and combat is not the only thing that moves him.

He is `SetNeutral` until provoked, deliberately, because he is an administrator
rather than a soldier. That is what lets him join a fight that starts near him
rather than reacting only to being shot himself.

### Two candidate fixes, and they are not equivalent

**Hold him in place.** Keep him at the captured position through any combat that
starts around him, so the marker stays right by construction. Cheaper, and it
keeps a single source of truth for where he is. It also makes him behave less
like a person in a firefight, which may read badly in exactly the playthrough
that triggered this.

**Make the marker follow him.** A mappin bound to the entity rather than to a
position. 20 established that a pin can anchor to a node this mod ships and that
`ShowWayInPin` takes a world position, so the question is whether a pin can track
a moving entity rather than a point, which is not established. This is the more
correct fix and the more unknown one.

### A third option, which may be the same as the first

**Sit him down.** Reported as a nice-to-have from the same playthrough: an
administrator at his desk should probably be sitting at it. A seated NPC is in a
workspot, and an NPC in a workspot is not walking anywhere, so this may be the
"hold him in place" fix arriving in a form that also looks better rather than
worse.

That is a guess about the mechanism and not a measurement. What is established
is that a scene can carry its own workspot with `playAtActorLocation`, which is
what makes Johnny render at all (2j and 3b). Whether the same shape holds a
placed NPC in a chair through combat starting near him is not established, and
"he sits until shot at, then stands up and joins in" would leave the marker
exactly as wrong as it is now.

### What is not yet known

Whether the marker being wrong actually costs the player anything here. If he is
already dead when they notice, the objective completes on his death and the stale
marker is visible for seconds. If they are hunting a live Hoshino who has walked
off, it is a real navigation fault. The report does not separate those, and which
one it is decides how much this deserves.

### Related

- **17** is the neighbouring item, and the same playthrough produced both: guards
  that do not behave like guards, and an exec who behaves more like one than the
  staging expects.
- **20** is what is known about pins anchoring to something this mod ships.
- **9** is the placement layer these captured positions belong to.


### CORRECTION, read at the desk 2026-08-21: he is not neutral, and the cause is a leftover

This section says Hoshino "is `SetNeutral` until provoked, deliberately", and so
does the comment beside the spawn. Neither describes what runs.

He is spawned neutral, once. The encounter tick then does this to him on every
pass, for as long as he is alive and the gig is open:

```
agent.SetAttitudeGroup(n"hostile");
agent.SetAttitudeTowards(player.GetAttitudeAgent(), EAIAttitude.AIA_Hostile);
```

The block is not gated on the estate, on V's position or on being provoked. It
is a sibling of the estate branch, so it runs from the first tick after he
spawns, about 1.5 s after the neutral call.

`git log -L` on the two dates it apart. The forcing lines are from `c9fd9a7`,
2026-08-11. The neutral spawn is from `eaf853e`, 2026-08-12, the commit whose
own comment records the playtest that produced it: he "opened fire during his
own conversation", so he was changed to spawn neutral. That change did not
remove the tick that overrides it a second and a half later. The fix and the
thing it was fixing have both been in the file since, and the comment explaining
the fix has been describing behaviour that does not happen.

### Why that is the likely mechanism, not just an untidiness

`SetAttitudeGroup(n"hostile")` is the call `CCShared_Attitude.reds` documents as
the wrong one, in a comment written from a playtest: *"those guards start
killing existing NPCs... this happens only after they see me and start shooting
at me."* `n"hostile"` is a GROUP, and a member of it is at war with every other
group in the room, its own side included. That is why the guards use the
pairwise `SetAttitudeTowards` and nothing else.

Hoshino is in that group. So "Hoshino joins the fight rather than waiting to be
spoken to" is what a full combatant at war with the estate detail would do, and
the report reaches this section as a marker complaint because the marker is the
part the player could see.

If that is right, the fix is neither of the two this section proposed. Dropping
`SetAttitudeGroup(n"hostile")` and keeping the pairwise line leaves him an enemy
of V and of nobody else, which is what the shared helper exists to provide, and
removes the reason he was crossing the estate. Holding him in place or making
the marker track him would both be treating the symptom.

Dropping the forcing entirely, so the neutral spawn means what its comment says,
is the larger version and is a design question rather than a bug fix: it decides
whether he shoots back at all before the conversation.

**Nothing has been changed yet.** The bench reads his attitude and his
high-level state, so a player who walks up to an untouched Hoshino and reads
HOSTILE off the panel has confirmed this without a code change, and one who
reads neutral has refuted it.

### A second consequence, which is worse than the marker

`cc_g01_hoshino_met` is set by V coming within 12 m of `CCGig01Places.Hoshino()`,
the captured point, and not within 12 m of Hoshino. The quest phase waits on
that fact before playing `gig01_hoshino.scene`.

So a Hoshino who has walked out of that sphere cannot be greeted at all, however
close V stands to him. The stale marker points at a spot that is also the only
place the conversation can start. Killing him still closes the gig, because the
death branch sets `cc_g01_hoshino_met` itself, so this strands the conversation
rather than the gig.

This is what decides the question this section left open, about whether the
wrong marker costs the player anything. It costs them the scene.

### What the bench measures for this

His distance from the captured point every quarter second, and the peak. Under
12 m and only the marker is wrong. Over 12 m and the conversation is unreachable
by the time the player follows him.


### MEASURED 2026-08-21, and the correction above is confirmed

Two readings, one playthrough.

**Standing at his desk, before anything was shot: Relaxed, and HOSTILE.** That
is the leftover doing exactly what the correction predicted, on a save where
nothing had provoked him. His own record says `baseAttitudeGroup: neutral`,
`reactionPreset: NoReaction` and `enableSensesOnStart: false`, so every field
that was set deliberately said peaceful, and a runtime call ran over all three
1.5 s after he spawned.

**Once a fight started: 96.2 m from his captured spot, in Combat.** He crossed
the estate and died by the front gate, about 20 m from `EstateGate()`. This
section asked whether the stale marker costs the player anything. At 96 m it
costs them the whole conversation, because the greeting fires at 12 m from the
captured point.

### FIXED 2026-08-21, awaiting verification

Two changes, and the second holds whatever the first turns out to do.

**`agent.SetAttitudeGroup(n"hostile")` is gone from the tick.** The pairwise
`SetAttitudeTowards` stays, so shooting him still starts a fight and he is an
enemy of V and of nobody else. The neutral spawn now means what its comment has
claimed since 2026-08-12.

**The greeting measures from the man, not from his spot.**
`Vector4.Distance(pos, hoshino.GetWorldPosition())` rather than
`Vector4.Distance(pos, CCGig01Places.Hoshino())`. A Hoshino who moves for any
reason can still be talked to.

### The marker itself is still anchored, deliberately

`pin_hoshino` is baked into the journal at (300.102, 1054.556, 229.928) by
`gen_journal.py` and activated with `obj_hoshino` by the quest phase. Making it
follow him means either regenerating that layer or putting a second, scripted
pin on top of it, and the second is what would ship soonest:
`CCSharedMappins.Show` / `.Move` is proven and is what draws the way-in markers
already, so a pin that tracks a moving entity is not the unknown this section
assumed. Two markers on screen at once is the cost.

Not built, because the fix above is meant to stop him leaving in the first
place. A neutral NPC in a firefight still moves, so this is not closed: the
number to re-read is the peak in section 3 of the readout. Under 12 m and the
marker never needed to follow him. Still tens of metres and it does.

### A separate thing the same playthrough found

His scanner name reads "HOSHINO SOLDIER". `displayName` was set to our own
LocKey and the scanner reads `fullDisplayName`, which was still the bodyguard
base's. Both are set now, and the TweakXL log is the check, per 13.


### SECOND ROUND, 2026-08-21: removing the group was not enough

Playtest after the fix above: he still crossed the estate and reached V at the
gate. Dropping `SetAttitudeGroup(n"hostile")` left the pairwise
`SetAttitudeTowards(player, AIA_Hostile)` in place, and an NPC who holds V as an
enemy engages V once he is aware of him. A firefight around him is what makes
him aware, so the outcome was unchanged.

**The whole forced-attitude block is gone now, and nothing replaces it.** His
record already does the job: `baseAttitudeGroup: neutral`, `reactionPreset:
ReactionPresets.NoReaction`, `enableSensesOnStart: false`, and `hoshino.yaml`
has said since it was written that "shooting him flips him hostile through the
game's own damage reaction, so 'peaceful until attacked' needs no script". Every
runtime attitude call this tick ever made was overriding three fields set
deliberately to say the same thing.

The greeting is 4 m rather than 12, by the design call: twelve started the
conversation across a courtyard. Not tighter, because the tick is 1.5 s and V
walking covers about six metres in one. Missing it costs the scene and not the
gig, since the kill branch sets `cc_g01_hoshino_met` itself.

### The name, and what reading the log was worth

`fullDisplayName` was accepted. The TweakXL log for the run is clean, no
unknown-property line, and the record and flat counts move. The scanner still
read "HOSHINO SOLDIER".

Both name fields were correct and the role was appended anyway, so it was never
coming from a name field. `skipDisplayArchetype` is what suppresses it, on the
same record in the same string table, beside `archetypeName` and `archetypeData`.

This is 13 arriving from the other direction. That entry is about a property the
game silently discards; this is a property the game accepts that was not the
right property. A clean log rules out one explanation and confirms nothing about
the other, and only the scanner in game separated them.


### THIRD ROUND, 2026-08-21: he stays put, and now he looks frightened

Playtest: *"Stays put, yes. But now looks all scared and defenceless."*

The staying put is the fix working. The cowering is a new symptom of it and is
not yet diagnosed, so nothing has been changed on a guess.

Two candidates, and the readout separates them without a code change, because
section 3 already prints his high-level state.

- **His attitude group.** `baseAttitudeGroup: neutral` puts him on the civilian
  side, and a civilian in a firefight goes into Fear. If the readout says
  **Fear** during the fight, this is it, and the fix is a group that is neither
  a civilian nor an enemy.
- **His reaction preset.** `ReactionPresets.NoReaction` was chosen when he was
  still being forced hostile at runtime, and the conditions it was chosen under
  no longer exist. `ReactionPresets.Corpo_Passive` is the one the base game
  keeps for exactly this character, an executive who does not fight.

`Corpo_Passive` was NOT applied on the strength of that reasoning. The preset is
one of the three fields that stopped him opening fire during his own
conversation, which is the worst regression available here, and the state
reading costs one glance at a panel that is already open.

### And the fourth item is still worth doing for a different reason

Seating him was parked as a nice-to-have, and as a way to hold him in place that
he no longer needs. The cowering gives it a second reason: a man at a desk is
not standing in the open with nothing to do when the shooting starts. What is
established is that a scene can carry its own workspot through
`playAtActorLocation` (2j and 3b). Whether that survives combat starting nearby
is not.

### FOURTH ROUND, 2026-08-21: he stands calmly, and he would not fight back either

Playtest: *"It's ok, doesn't engage. But now doesn't even engage after I shoot
him once."*

The cowering is gone and no field was changed to fix it, so the Fear reading was
never taken and the two candidates above are both moot. Standing calmly was what
removing the forced attitude produced once it settled.

**`hoshino.yaml` has been wrong about the damage reaction since it was written.**
Its comment says "shooting him flips him hostile through the game's own damage
reaction, so 'peaceful until attacked' needs no script". That was never tested,
because the runtime call that made him hostile anyway was in the tick the whole
time, overriding it. With the call gone he takes the shot and does nothing.

The cause is one of the three fields that make him peaceful:
`reactionPreset: ReactionPresets.NoReaction` removes the damage reaction along
with every other reaction, so there is nothing left to flip him.

### The flip is scripted now, once, on the first sign of damage

Health as a percentage from the stat pool, so anything under full means he has
been hit. Nothing here regenerates it and nothing else touches him.

Two things happen together, and the second is the one that is easy to miss:

- his attitude to V goes hostile, pairwise as everywhere else here.
- **his senses are switched on.** `enableSensesOnStart: false` is the third
  peaceful field, and an NPC who cannot perceive V cannot shoot at him however
  hostile he is. `SenseComponent.Toggle(true)`.

`m_hoshinoProvoked` is a FIELD and not a fact, deliberately. It must not survive
a reload: the same reload respawns him at full health, and a remembered flip
would make him hostile before he had been touched, which is the bug this whole
line of work started from.

The dev menu has a "FORCE FIGHT" button that flips him with no shot fired, for
testing the fight without having to land one. It is one-way within a session,
same as the real thing.



### FIFTH ROUND, 2026-08-21: he turns on V when the conversation ends

The design call, after the fight-back fix: being shot should not be the only way
in. He should turn on V when he has finished speaking.

**This was tried on 2026-08-14 and withdrawn, and the reason it failed then is
the reason it works now.** It was built as an attitude flip on a fact set after
his scene, and it did nothing observable, because `enableSensesOnStart: false`
leaves him hostile and never looking. The playtest verdict: *"Still doesn't
attack but it's ok let's not complicate things."* The comment left in
`gen_questphase.py` in its place said the only way to make him fight would be
turning senses on, which was what kept him peaceful through his own
conversation, and to leave it alone.

That was correct while the encounter forced him hostile on every tick, because
senses on at any point meant senses on during the scene. That force is gone, so
the flip is a single event at a moment the graph chooses, and turning his senses
on after his last line cannot reach back into a scene that has finished.

### What ships

`cc_g01_hoshino_talked`, set by a `questSetVar` node between the scene's output
and the objective rejoin, so it is **on the talked branch only**. The dead
branch reaches the same rejoin without passing through it, which is right: a
corpse needs no attitude, and the kill scene forks on `cc_g01_hoshino_dead`.

The encounter reads it beside his health, and both routes do the same two
things: attitude to V hostile, and `SenseComponent.Toggle(true)`. Three ways in
altogether, counting the dev menu's FORCE FIGHT button.

### The general lesson, which is why this is written up at length

A finding that closed as "impossible, do not try again" was true of the
conditions it was measured in and not of the mechanism. Nothing about senses
changed between August 14th and today. What changed is that a second piece of
code stopped fighting the first.

Worth checking, before re-testing anything this register has closed: whether the
thing that made it fail is still there.


### SIXTH ROUND, 2026-08-21: unkillable until he has spoken

The design call, after the flip landed: *"could we make him invincible until we
have the conversation? So players cannot kill him from afar like with quickhacks,
or sniper."* The beat the whole leg is built around should not be deletable from
outside the building by a player who never learns it was there.

`GodModeSystem`, which is the base game's own mechanism for a quest-critical
NPC. `AddGodMode(id, gameGodModeType.Invulnerable, n"cc_g01_hoshino")` while he
has not spoken, removed the moment he has.

**`Invulnerable` rather than `Immortal`, and the choice is load-bearing.**
Immortal takes damage that cannot finish him, so his health drops, and his
health is what the fight-back check reads. It would produce an NPC who is
hostile and cannot be killed.

**The release is derived every tick from facts, not latched beside the flip.**

```reds
let wantShield: Bool = qs.GetFactStr("cc_g01_hoshino_talked") == 0
    && qs.GetFactStr("cc_g01_hoshino_dead") == 0
    && qs.GetFactStr("cc_g01_done") == 0
    && !hostileNow;
```

A shield left on is a Hoshino who can never die, which is a gig that can never
finish, and it is exactly the class of fault a playthrough from a clean save
cannot find: it only shows up on the path where something went wrong earlier.
Deriving it from facts means a missed tick, a reload part-way through the scene
and a scene that never played all reach the release on the next pass. Same
discipline as `ReleaseMama`, same rule as `gotchas.md` 21.

### What this closes, and one thing it leaves

*"Fights back when shot => not unless we've already finished talking."* That was
still true after the fifth round and is now unreachable: he cannot be hurt
before the conversation, so there is no shot to fight back from.

The health route stays in the code as the safety net for the case where
`cc_g01_hoshino_talked` never arrives, on an old save mid-scene for instance.
Why it did not fire on its own was never established, and the two candidates
were never separated: a 1.5 s tick against a kill that lands inside one, or the
stat pool not reading the way the code assumes. **If the health route is ever
relied on again, measure that first rather than trusting this paragraph.**

### The recipe is now in the scene playbook

All four parts of it, written for a modder who has never seen this gig:
`docs/scene-playbook.md`, "An NPC who turns on the player when the conversation
ends". The design call that sent it there: this is the machinery a choice-based
gig needs, where the conversation's ending is what decides whether V kills him.

### CLOSED 2026-08-21: he stays at his desk, so the marker is right where it is

Confirmed in play across four rounds. He holds his position, he stands calmly
rather than cowering, he cannot be killed before he speaks, and he turns on V
when the conversation ends.

**The marker was never the fault and no marker work shipped.** This section
opened asking whether to hold him in place or make the pin track him, and called
that "not a free choice". It was a false choice: he was moving because a
runtime call from 2026-08-11 was overriding his own record, and with that gone
the anchored pin at (300.102, 1054.556, 229.928) is simply correct. The
`CCSharedMappins.Show` / `.Move` route sketched above was never built.

The greeting still measures from the man rather than from the spot, at 8 m. That
stays: it costs nothing, and it means a future beat that moves him on purpose
does not silently break the conversation.

**The general shape, which is the part worth carrying.** Two of the four
symptoms reported here, the wandering and the stale marker, were one cause. A
third, "he does not fight back", was a consequence of removing that cause and
only became visible once it was gone. A fourth, the cowering, resolved itself
and was never diagnosed, because the reading that would have diagnosed it was
never needed.

Fixing a cause exposes what it was hiding. Reading the whole list of symptoms as
a list of jobs would have produced a marker system, a hold-in-place system and a
combat trigger, all to work around one line.



### SEVENTH ROUND, 2026-08-21: the reticle is a separate thing from the damage

Playtest: *"other friendlies you cannot even target with the pistol. In this
case it seems that he can be targeted, just doesn't suffer."*

Correct, and the middle state is the worst of the three. God mode decides
whether damage lands and says nothing about whether the game locks on, draws a
health bar and lets the player line up a shot. Inviting the shot and then
ignoring it reads as a broken NPC; refusing the lock reads as a story NPC.

### What was researched, and what it is not

There is **no record field for this.** The full flat list on
`Character.cpz_arasaka_bodyguard_ranged3_kenshin_mb_rare` was read off CET's
string table and searched: `defaultCrosshair`, `hideUIDetection`,
`hideUIElements`, `uiNameplate` and `threatTrackingPreset` are all about what is
DRAWN, and `quest` is a persistence flag rather than a protection one. Nothing
matching `targetab` exists anywhere in TweakDB outside the smart gun's own
angle stats.

`gameGodModeType` carries `Invulnerable` and `Immortal` and neither touches the
reticle.

### What it is

`TargetingComponent`, on the puppet, switched off while he is protected.

```reds
let aim: ref<TargetingComponent> =
    hoshino.FindComponentByName(n"TargetingComponent") as TargetingComponent;
aim.Toggle(false);
```

Three dead ends on the way, all resolved by the compiler rather than by
guessing, and worth recording because the next probe here will hit the same
ones:

- `ScriptedPuppet.GetTargetingComponent()` does not exist. The accessor of that
  name in the cache belongs to the PLAYER, whose targeting component is the
  thing that FINDS targets rather than the thing that IS one.
- `TargetingComponent.ToggleTargeting()` does not exist either, despite
  `ToggleTargeting` being a real string in the cache.
- `Toggle(Bool)` is the method, the same shape as `SenseComponent.Toggle` two
  rounds earlier. Components in this codebase toggle; they do not have bespoke
  verbs.

**The component is fetched BY NAME and a wrong name fails silently**, returning
null and toggling nothing, with the only symptom being a reticle that still
locks on. Both casings appear in the game's string table, so both are tried.

### Unverified in game at time of writing

It compiles and the shape is right. Whether the name binds, and whether
switching the component off is enough on its own, is one playtest: aim a pistol
at him before the conversation and see whether the reticle takes hold.


### EIGHTH ROUND, 2026-08-21: the targeting component does nothing, the attitude is what the reticle reads

`TargetingComponent.Toggle(false)` was built, shipped and played. **It does not
work.** Playtest: *"still possible to target, shoot him, and he has the pain
reaction."* It compiles, the component resolves by name, and the reticle is
unaffected. Removed rather than left in, because a call with no effect is
something someone later debugs for nothing.

That closes the component route, and it is worth stating plainly since the
research above made it look like the answer: nothing in TweakDB controls
targetability, and the one component that appeared to is not it either.

### What is being tried instead

The design call's own suggestion: *"spawn him as a friendly and then change its
status completely after we speak."* A friendly NPC is the one the game will not
let the player lock onto, and unlike anything on his record it is a state he can
be moved in and out of.

**Both halves of the attitude, because they answer different questions.**

| | what it says | what reads it |
|---|---|---|
| `SetAttitudeGroup(n"friendly")` | which side he is on | the reticle |
| `SetAttitudeTowards(player, AIA_Friendly)` | what he thinks of V | his own AI |

Setting only one has already failed here twice in opposite directions: the
pairwise value alone left him targetable, and earlier in this same section the
GROUP alone (`n"hostile"`) sent him to war with his own security.

**The friendly group is safe for HIM and would not be for the guards.** He is an
Arasaka administrator standing among Arasaka security, so a group that makes him
their ally is what he already is. The warning in `CCShared_Attitude.reds` is
specifically about `n"hostile"`, which puts an NPC at war with every other group
including his own side.

**RE-ASSERTED EVERY TICK, not once on the transition.** An attitude set on an
entity that is still resolving does nothing, which is the whole reason the
shared helper retries at all, and one missed call means a targetable Hoshino for
the rest of the visit. Two calls every 1.5 s is not worth optimising.

**And the flip takes him out of the group before it makes him hostile.** An NPC
left in the friendly group is one the player still cannot shoot, which would
turn the shield into a permanent one by a second route, and that failure would
look nothing like the first. He goes back to `neutral`, his record's own
`baseAttitudeGroup`, and the pairwise line is what makes him an enemy of V.

### CONFIRMED IN PLAY 2026-08-21

Both halves. The reticle refuses him while he is protected, and he fights
properly after the flip. *"Works perfectly."*

### The dead man's handle, added before shipping

`cc_g01_hoshino_talked` is set by a quest node that did not exist in 1.2.3. A
player who loads a 1.2.3 save in which he has ALREADY been talked to is past
that node forever, so the fact can never arrive and every shield condition stays
true for the rest of the save. He would respawn protected and stay protected:
an unfinishable gig produced by an upgrade rather than by anything the player
did.

So reaching him starts a clock. Two minutes with V in front of him and no scene
having finished means the scene is not coming, and the shield drops. A real
conversation takes seconds, and the only cost on a legacy save is that he is
briefly unshootable on content already behind them.

It is a field rather than a fact, so a reload restarts the clock, which is
right: a reload respawns him too and the question is being asked again from the
start.

**Nothing found this. It was reasoned at the desk**, and it is the class of
fault the project's own testing cannot see, because testing always starts from a
clean pre-gig save and goes forward. `gotchas.md` 21 again.

## 23. The estate guards populate while V watches. Reported, FIXED and CONFIRMED IN PLAY 2026-08-21

Field report from the 1.2.3 playthrough: *"as I move towards the gate I see it
empty first, then they appear. It'd be nicer if the trigger was further so when
I arrive I already see them there."*

### Why it happens

The two sites trigger differently, and only one of them was given runway.

The office compound spawns at **100 m** from `CompoundEntry` while "arrived" is
60 m, so the squads are already standing there by the time the player is close
enough to look. The comment on it is explicit that the callback chain needs the
head start.

The estate has no such margin. `AuditSite(true)` fires from the same test that
sets `cc_g01_estate_reached`: 45 m from `EstateGate`, 70 m from Hoshino, or
anywhere inside the twenty walked points of `InsideEstate`. So the spawn begins
at the moment of arrival rather than before it, and the squads are spread over a
callback chain, which is what makes the filling-in visible.

### What to build

Give the estate the same shape the office already has: a wider sphere that only
starts the spawn, kept separate from the narrower one that counts as arriving.
The office version is two lines and the estate can copy it.

Two things to settle:

- **How much further.** The office uses 100 against 60, so a margin of about
  40 m. The estate approach is a driveable hill rather than a compound,
  so V closes the distance faster and may need more. This is measurable in game
  rather than worth guessing.
- **Not so far that it populates a compound the player is driving past.** The
  office comment already names this trade-off, and North Oak has through roads.

### Related

- **10c** and **10d** are the spawn faults already fixed, including why the chain
  is spread over callbacks in the first place.
- **17** is the other half of the same approach: they spawn in a huddle and do
  not react. Fixing where they stand and when they appear are separate from
  making them behave like guards, and all three are the same walk up to the gate.


### FIXED 2026-08-21, awaiting verification

Two spheres now, the shape the office already had.

| | was | is |
|---|---|---|
| spawning starts | 45 m from the gate | 120 m from the gate |
| arriving, and the objective flips | 45 m from the gate | 20 m from the gate |

The outline and the 70 m sphere on Hoshino are unchanged, and both still count
as arriving, so a player who came over the back wall gets the same estate.

**120 m is the fast travel point.** It reads 116.5 m from the gate on the
readout, and the design call is that a player landing there should already be
inside the spawn sphere, so the estate fills while he walks to his car rather
than while he looks at it. 120 clears that landing by a few metres. The office
pair is 100 against 60; this one is wider in both halves because the approach is
a driveable hill rather than a walk through the compound.

**20 m rather than 45 is a second report from the same run.** At 45 the
objective changed to "Find a way into the residence" a car's length short of the
gate, and the design call is that it should change when the player reaches it.
Screenshots caught the flip between the 50 m and 45 m marks. Not tighter than
20: the tick is 1.5 s and a car covers about 30 m in one, so a smaller sphere
could be stepped over between two samples, and the outline is the backstop.

The altitude band stays 12 below and 25 above the gate. Widening the radius to
120 m widens what a floor reaching down to the tunnelled road would catch, and
that road passes under this hill.

### The measurement this was going to be built on was wrong, and the bench was at fault

The readout's fill counter latched on the OFFICE squad and then refused to
measure again, reporting "first guard at 2775.5 m" from the estate gate, which
is V standing in the compound three kilometres away. Both sites share
the `n"cc_g01_guard"` tag and the 200 m filter is 200 m from the PLAYER, not
from the estate.

The numbers were real and measured the wrong site, which is the failure mode
worth naming: a bench that answers is not a bench that answered the question.
It now ignores anything beyond 400 m of the estate gate. The peak speed had the
same shape of fault and read 11255 m/s, because a fast travel is a position
delta like any other; it now discards anything above 60 m/s.

Neither mattered in the end. The distance came from the field report instead.

### CONFIRMED IN PLAY 2026-08-21, and the arrival radius came back to 45 m

The guards are in place when V lands at the North Oak fast travel point, and the
objective changes at the gate. Both confirmed.

The arrival radius went 45, 20, 25, 35, 45 across one evening. That reads as
indecision and is not: what it was being measured against changed underneath it.

The original 45 was condemned for flipping the objective "a car's length short
of the gate". Arriving and spawning were ONE test at that point, so 45 m was
also where the squads began appearing, and what the report described was the
guards materialising at the same moment the objective changed. Splitting the two
fixed that, and every tightening after it was chasing a fault that had already
been fixed: 20 put the fight before the side road came into view, and 25 and 35
were both still short of it.

**Same number, different behaviour, and the lesson is about the measurement
rather than the number.** A value condemned by a playtest was condemned along
with everything else that was true at the time. When the thing it was coupled to
is decoupled, the old verdict does not carry over, and re-deriving it costs one
run.


## 24. NCPD responds to the estate firefight. Reported and CLOSED 2026-08-21, not ours

Field report: *"police showed up once I started killing the guards."*

### The thing it is not

**This mod spawns no civilians anywhere near the estate.** Every record in
`SpawnSquad` is a security archetype: `nok_security_*`, `arasaka_agent_*`,
`arasaka_ranger*`, `nok_arasaka_fast_sniper_*`, `arasaka_netrunner_*` at the
estate, and `sts_std_arr_*`, `arasaka_guard2_*`, `arr_arasaka_ranger1_*`,
`arasaka_2020guard_*` at the office. The only other two people this gig places
are Hoshino and the Mama Welles stand-in, and she is in El Coyote Cojo.

So nobody is killing bystanders this mod put in their way. That was the worry
and it can be closed.

### The likely mechanism, unmeasured

An attitude here is PAIRWISE. `CCSharedAttitude.Hostile` calls
`SetAttitudeTowards(player, AIA_Hostile)`, which makes a guard an enemy of V and
changes nothing else. That is deliberate: the group version made them shoot
each other, which is the playtest recorded in `CCShared_Attitude.reds`.

The crime system reads the world rather than that pairwise relationship. A
vanilla `sts_*` or `nok_security_*` record keeps its own `baseAttitudeGroup`, so
as far as the prevention system is concerned V is gunning down Arasaka staff in
a residential district, and North Oak is about the most policed one there is.

**It is probably not new.** Before 2026-08-21 the estate squad was not made
hostile at all, so the same kills were the same crime, and the fight is simply
bigger now that they shoot back.

### What to try, in order

- **Confirm it is not new.** One run on 1.2.3 with the same fight settles
  whether the current build caused it. Cheapest thing here and it should come
  first.
- **Read what the guards actually are.** `baseAttitudeGroup` on the shipped
  records, by the string-table route in `gameplay-restrictions.md` for the field
  names, then in game for the values.
- **Do not reach for the hostile GROUP.** It is the obvious fix and it is ruled
  out already: members of `n"hostile"` are at war with every other group in the
  room, their own colleagues included.
- **Look at PreventionSystem.** Whether a fight can be marked as quest combat so
  it does not register as a crime is not established, and it is the shape a
  vanilla gig would use.

### Is it even wrong?

Worth asking before building anything. V is shooting up an Arasaka estate in
North Oak. Police arriving is arguably correct, and the gig has no escape beat
that a wanted level would break: the objective after Hoshino is a terminal
inside the house, and then leaving.

The report reads as surprise rather than as a complaint, so the design call is
open. If it stays, it should stay on purpose.

### Related

- **17**, where the pairwise attitude was chosen and why the group was not.
- **22**, Hoshino, who is neutral in earnest now, which makes killing him the one
  kill here that is unambiguously a civilian murder.

### CLOSED 2026-08-21: base-game residents, killed by a grenade

The reporter's own follow-up: *"I think this was because I launched a bomb and
killed civilians that were already inside the residence, not spawned by
[this mod]."*

So the crime was real and the victims were real, and neither was this mod's
doing. The North Oak residence is populated by the base game, and an explosive
in a courtyard does not check affiliations. Nothing above needed building.

The section stays for the part that is still worth having written down: this mod
places no civilians anywhere near either site, and the pairwise-attitude
reasoning that made the question worth asking is correct and is why the hostile
GROUP is still ruled out.

**Despawning the residents was raised and declined.** They belong to the base
game's world, not to this gig, and removing them for the duration would be this
mod reaching into a district it does not own for a cosmetic reason. A player who
grenades a house gets what a player who grenades a house gets.

## 25. A finished site repopulates after a reload. Reported, FIXED and CONFIRMED IN PLAY 2026-08-21

Field report: a save whose objective was already "get to the Arasaka residence",
so the compound leg was long finished, driven back past the compound.
The whole office detail spawned again, banner and all.

### Why the latch did not hold

The site is guarded by `m_officeMask`, a per-anchor bitmask recording which
anchors are populated, and within a session it works. **It is a plain field on a
ScriptableSystem, so a load leaves it empty and every anchor reads as
unpopulated again.** The proximity test then does what it is written to do.

`docs/gotchas.md` 21 is the same lesson from the other end, and `Gig01_Holocall`
carries it too: state that has to outlive a reload belongs in a fact. The mask
was never wrong for the job it was written for, which is deciding what still
needs filling during one visit. What was missing is a test for whether there
should be a visit at all.

Nothing in the tick asked whether the leg was over. `cc_g01_accepted` and
`cc_g01_done` were the only gates on the whole block, and both are true for the
entire gig, so every site stayed armed from acceptance to the epilogue.

### The fix

One fact in front of each spawn, and both already existed for the quest graph.

| site | armed while |
|---|---|
| the office compound | `cc_g01_left_compound == 0` |
| the North Oak estate | `cc_g01_escaped == 0` |

`cc_g01_left_compound` is set once the ledger is read and V is 110 m clear of
the terminal, and the quest graph already advances `obj_nix` on it, so any save
that has heard from Nix has it set. `cc_g01_escaped` is its equivalent at the
estate, set once the upload is done and V is 160 m clear of Hoshino.

Both are facts, so they survive the reload the mask does not.

### The doors were left alone, deliberately

`Gig01_OfficeDoors` is gated on `cc_g01_accepted` and `cc_g01_done`, the same
pair, so on the face of it it has the same fault. It does not have the same
consequence and the obvious tightening carries a risk the spawn fix does not.

The hook only ever switches a door ON, and only when one streams in DISABLED.
A door this gig has already opened is open, so a later visit does nothing
observable. Gating it on `cc_g01_left_compound` would mean a player who leaves
the compound and goes back for the shard finds a door that is off again, and a
lockout is worse than an invisible no-op.

### The general shape, for the next gig

Any site a gig populates needs two different pieces of state, and they are not
interchangeable.

- **Which anchors still need filling on this visit.** A field is right. It is
  cheap, it is per-visit, and it is meant to be forgotten.
- **Whether this leg of the gig is still running.** A fact is the only thing
  that can answer it, because the question outlives the session.

Getting the second one from the first is the bug in this section, and it is
invisible until someone reloads and goes back.

### Related

- **10c**, **10d** and **10e**, the spawn faults fixed before this one, all
  within a session.
- **21** in `gotchas.md`, a latch exercised only in the clean direction.

### CONFIRMED IN PLAY 2026-08-21

A save already past the compound leg, driven back past the compound: no
spawn, no banner. The estate half is the same code and the same two facts, so it
is covered by the same change; it has not been separately provoked.


## 26. The North Oak objective stops for anyone who does not use the gate. Reported 2026-08-24, FIXED and CONFIRMED IN PLAY the same day

Two Nexus reports, hours apart, describing one fault:

> "North Oak estate objective doesn't update even after you get inside, by the
> rocks or double jump doesn't matter it doesn't update and you cant kill
> Hoshino."

> "I don't know what to do; the marker is getting stuck at the gates in North
> Oak."

### Why every playtest here passed

The North Oak leg is three waits in a row: reach the estate, find a way in,
find Hoshino. The encounter tick samples the player's position every 1.5 s, and
two of those three are satisfied by the SAME test, being inside the traced
outline of the grounds.

Driving to the gate hides that completely. The gate sits OUTSIDE the outline, so
arriving there cannot also mean being inside, and the two facts land a walk
apart. That is the route every test run here has ever taken, which is why the
gig has been played end to end a dozen times without anyone meeting this.

Come over the wall, or up the rocks, or double jump in, and both facts are
written on ONE pass. The phase is parked on the first of them. It fires,
completes the objective, raises the next one, and only then arms the wait on a
fact that changed a moment ago. Nothing will change it again, so the phase
stops there for the rest of the save.

This is gotcha 54 arriving from the other direction. That entry is about a dev
button setting a fact that is already set; this is the gig setting a fact before
anything is listening. Same rule underneath: **a fact that does not CHANGE is
not a change, and a pause node is armed when the token reaches it, not before.**

### The fix

One step per pass. Setting `cc_g01_estate_reached` marks the pass, and
`cc_g01_wayin_reached` is held to the next one; the pair then marks the pass
against `cc_g01_hoshino_met`, which sits behind the same shape one step further
on and could bite a player who lands next to Hoshino.

1.5 s is far longer than the phase needs to walk four nodes and arm a wait, and
on the gate route it changes nothing at all, because the steps were already
seconds apart.

The flag is a field and not a fact, deliberately. It is written and read inside
one pass, and a remembered value would skip a step after a load.

**CONFIRMED IN PLAY 2026-08-24**, over the wall by double jump, without going
near the gate: the objective moved through "find a way in" to "Find Hoshino"
correctly. The gate route was unchanged.

### The general rule, for gigs 02 to 04

**Two consecutive waits in a quest phase must not be satisfiable by one sample
of the world.** Either separate what they measure, or hold the second back a
pass. Reaching a place and being inside it are the obvious pair, and the reason
this was invisible is that the signposted route separates them by itself.


## 27. Hoshino's lipsync plays on a body nobody can see. CLOSED 2026-08-25, confirmed in play, shipped in 1.3.0

**Closing note, added 2026-09-05.** Route A was taken and it worked: Hoshino is
placed in this mod's sector, the script finds the placed body instead of a
spawned one, the scene takes him as a first-class actor, and his mouth moves.
Confirmed in playtest on 2026-08-25 and shipped the same release, which also
sat him on the couch. The title said OPEN for eleven days and two releases
after the fact; everything below is the reasoning as it stood before the fix,
kept because the two-body problem is what every later gig inherits.

**The data is not the problem.** `gig01_hoshino/h01` and `h02` have animations
picked and shipped like every other line in the gig, and the same machinery
demonstrably moves Johnny's mouth on all seven of his beats and moved Nix's in
close-up on the phone in 1.2.6 (2j, 3d). Hoshino's animations play. They play on
the wrong body.

### Why there are two of him

A custom NPC who has to be found, spoken to and shot needs to exist for minutes
before his conversation starts, so `Gig01_Encounter` spawns him at his captured
position and the player meets that body. The conversation cannot use it. A scene
acquires its own actors, and the only acquisition this project has working for a
custom character is `spawnDespawn`, where the scene spawns a fresh copy.

So the scene spawns a second Hoshino a kilometre out and a hundred metres down,
which is where every voice-only actor in this gig stands, and buys the audio back
by making his lines non-positional (`inner_vo`, and the 2026-08-17 playtest that
separated `voExpression` from `visualStyle` is in `scene-playbook.md`). The
lipsync rides the scene's speaker, so it rides the buried one.

The visible Hoshino stands there with a closed mouth. Two Nexus-facing symptoms
follow: his mouth does not move, and his name over the subtitle comes from an
actor that is not him.

### The bridge that was built for exactly this, and why it is switched off

`questkit/scene.py` carries `add_body_double`, which adds a second actor to a
scene that never speaks and receives the line's lipsync through
`scnAdditionalSpeakerRole.OnlyLipsync`. Vanilla does this. Ours pointed at the
script-spawned body with a `findInWorld` actor whose `actorRef.type` is `Tag`,
matching the CName in the `DynamicEntitySpec`.

**Tested at `gig01_arasaka` on 2026-08-14 and it failed both ways at once.**

```
 96.7  cc_g01_dbg_johnny      = 1     script spawns him
 98.2  cc_g01_dbg_lip_johnny  = 2     the tag IS registered
 99.8  cc_g01_dbg_johnny_ws   = 4     he is in his workspot, visible
102.2  cc_g01_call_done       = 1     the scene is entered
       (line plays, mouth still)
106.5  crash
```

The entity was present under our tag at the moment the scene ran, and the scene
still did not animate it: the scene system's `findInWorld` resolver does not read
the dynamic-entity tag registry. The crash was deterministic, 4.3 s after entry
both times, which is scene TEARDOWN disposing of an additional speaker whose
actor never acquired.

**`gameEntityReferenceType.Tag` is unusable from a scene.** Zero of 7067 shipped
scenes use it. The machinery stays, one constant away from usable
(`BRIDGE_SCENES`), because the failure was in the acquisition and not in the
double.

### What has changed since, and it is why this is worth reopening

Both of these landed AFTER the bridge was tested, and neither was available to it:

- **A node this mod ships DOES register a global name**, in the long
  `$/03_night_city/...` form (11, naming half, closed 2026-08-17).
- **A map pin can anchor to one of our own nodes**, and a mod can ship an
  always-loaded sector to keep it resolvable (20, 2026-08-18).

So "the scene cannot address our body" was measured against the one addressing
mode that does not work, and the mode that does work was not known yet.

### Route A: give him a real body in the world

Place Hoshino as an entity node in this mod's own sector, the way the shard
container on the office desk is placed (6, and `shard-playbook.md`), instead of
spawning him from script. He then has a NodeRef, and the scene acquires him as a
first-class actor the way vanilla acquires Mama Welles (7d). Mouth, name and
audio all come off the body the player is looking at, and the two-body
arrangement stops being something gigs 02 to 04 inherit.

**What it costs.** Everything `Gig01_Encounter` does to him is built on the
script owning his `EntityID`: the neutral spawn, the god-mode shield before his
conversation, the attitude flip when it ends, and the death detection. All of it
would need to find him another way. There is precedent for that in this mod, in
`Gig01_OfficeDoors` and `Gig01_OfficeComputer`, which both match their target by
the position of its owner.

**The residual unknown.** A mod sector streams by proximity. That is fatal for a
map pin wanted from across the city, which is why pins anchor to base-game nodes,
and it is harmless here: the scene only runs with V standing in front of him, so
the sector is certainly streamed. Say that out loud before building, because it
is the reason the same idea was rejected for pins.

### Route B: swap the two for the length of the conversation

Hide the script's Hoshino when the scene starts, let the scene place its own
VISIBLE Hoshino on the same mark with a workspot, and swap back when it ends.
This uses only proven machinery: every Johnny beat since 2026-08-17 places a
visible scene actor at a computed offset and yaw and glitches him out before the
scene ends (9), and `build_hoshino` itself shipped a visible duplicate for one
playtest on 2026-08-12.

Cheaper by an order of magnitude, fixes nothing structurally, and its risk is a
visible pop at each end.

### THE DECISION: route A. Taken 2026-08-24

**A, not B.** B was offered first as a cheap measurement and was declined, and
the reasoning holds up: B buys one answer and leaves the arrangement it measures
in place, while the arrangement is the thing every later gig inherits. A custom
NPC who has to be found, spoken to and shot is not a gig 01 peculiarity, it is
the shape of a story gig.

So the two-body arrangement is what gets fixed, and Hoshino is the first case
rather than the only one.

**What still has to be measured on the way, and B was the cheap way to do it.**
Nothing has ever confirmed that our lipsync moves THIS character's mouth. Johnny
and Nix prove the pipeline, not this record and not this animation pool. Under A
that confirmation arrives at the end instead of at the start, so a result of "his
mouth still does not move" will have two candidate causes at once, the
acquisition and the pool. Separate them before reading it.

**Count the pool before judging his mouth.** Hoshino draws from
`civ_(high|mid)_m_\d+_jap_\d+` only, and that filter has never been counted. 3d
is the finding that a small pool is what makes lipsync read as broken, measured
on Nix at 386 ms of overshoot on an 880 ms line and fixed by widening him to all
1192 male civilian sets. A bad result from a small pool looks exactly like a bad
result from a wrong body.

**The route, in the order the unknowns fall:**

1. **Count Hoshino's animation pool.** Offline, minutes, and it decides whether
   the widening from 3d has to happen at the same time.
2. **Place him as an entity node in this mod's sector** and confirm he is there,
   visible and named, before any scene work. The shard container is the worked
   example (6, `shard-playbook.md`), and the naming form that resolves is the
   long one (11).
3. **Move what the script does to him off the spawned `EntityID`.** The neutral
   spawn, the shield, the attitude flip and the death detection all have to find
   the placed body instead. `Gig01_OfficeDoors` and `Gig01_OfficeComputer` are
   the precedent, both matching by the position of the owner.
4. **Then the scene takes him as a first-class actor**, and only then is the
   mouth question askable.

Steps 2 and 3 are each a bench with a visible result, so neither has to be
believed on paper. Step 4 is the one that has failed before, by a different
route, and it is deliberately last.
---

## 28. What binds a `.community` resource to the world. ANSWERED 2026-08-23, by reading. Nothing binds it, because it never ships

**The open half of 11 is closed.** The question was wrong in its premise, which
is why five sessions of looking for the reference never found one.

**A `.community` file is an authoring artifact. It does not ship and nothing at
runtime reads one.** At cook time its whole `communityCommunityTemplateData`,
characters included, is copied into a `worldCommunityRegistryNode` that lives in
an always-loaded sector. That node is what the community system reads.

So the piece in the middle was never missing. It was a node type nobody here
had looked at, in a sector this project had already read twice.

### The four parts, and how they find each other

| part | where it lives | what it holds |
|---|---|---|
| `worldAISpotNode` | an ordinary streaming sector | one spot: a position, a yaw, and a `.workspot` |
| `worldCompiledCommunityAreaNode` | an always-loaded sector | which entry and phase uses which spot, spots named by hash |
| `worldCommunityRegistryNode` | the same always-loaded sector | the characters, the phases, the quantities, and a record per spot |
| `gameCommunityID` | both of the two above | the 64-bit key that joins them |

The key is `worldCompiledCommunityAreaNode.sourceObjectId.hash` on one side and
`worldCommunityRegistryItem.communityId.entityId.hash` on the other.

**It is NOT opaque, and this section said it was until 29 was built.** It is
FNV1a64 of the community's own NodeRef with the '#' characters removed, the same
rule as a spot's, and the ref must be registered in its sector's `nodeRefs`.
Measured: `always_loaded_0` registers
`$/03_night_city/c_pacifica/coastview/#pcv_01/.../#mq025_com_fabiola` and the
area node beside it carries exactly that hash. A quest node reaches the same
community through the same string, so a mod that invents a key nothing is named
after has a community nothing can address. Gotcha 62.

**And a community has to be ACTIVATED from a quest node**, even an ambient
open-world one: gotcha 63. `entryActiveOnStart` governs the entry inside a
running community and does not start it.

Spots are named rather than keyed: `spotNodeIds[].hash` is a
`worldGlobalNodeID`, and

```
worldGlobalNodeID.hash = FNV1a64(the node's NodeRef with every '#' removed)
```

That is measured, not inferred. Hashing all 33506 NodeRefs in `always_loaded_0`
and intersecting with the 5604 distinct spot ids its community nodes reference
returns 3767 matches; the rest name spots in sectors that were not hashed.
Reversing the map gives readable pairs, `{mq025_com_fabiola}` against
`$/03_night_city/c_pacifica/coastview/#pcv_01/.../#mq025_ws_announcer_06_fight`.

The refs are LONG-FORM paths, which is the same spelling 11 found to be the only
one a mod node registers under, so the two findings agree.

### Where vanilla keeps it

`always_loaded_1` holds exactly one `worldCommunityRegistryNode`, `debugName`
`community_registry`, and it is large:

| | |
|---|---|
| `communitiesData` | 8540 `worldCommunityRegistryItem`, one per community |
| `workspotsPersistentData` | 97359 `AISpotPersistentData`, one per spot |
| `spawnSetNameToCommunityID` | 329 entries mapping a name to a community id |

4853 of the 4854 spot references resolved out of `always_loaded_0` also carry an
`AISpotPersistentData` record, so that array is part of the recipe rather than
an optimisation. Its `worldPosition` is a `FixedPoint`: `Bits` is the metre
value times 131072, checked against three axes of a spot whose node position is
known.

### `spawnSetNameToCommunityID`, which answers a different open question

The names in it are `#padre_holo`, `#nix_holo`, `#mama_welles_holo`: 59 of the
329 are the holocall studio spawn sets. That is the table a scene's
`acquisitionPlan: spawnSet` resolves through, which means **a scene acquires an
actor from a COMMUNITY, not from a node**. The open question this answers was
whether a scene can bind to a node the mod names, and it does not work that way
for anyone.

It also means the two-bodies problem has a route: a community we ship, plus a
name in this table, is a body a scene can acquire.

### What Phantom Liberty does, and why a mod cannot copy it

EP1 ships its own `ep1/always_loaded_0.streamingsector` (4146 marker nodes and
nothing else) and then **replaces** `always_loaded_1` wholesale with a bigger
one: 10289 registry items against 8540, 122794 spot records against 97359, 404
spawn-set names against 329. CDPR merged Dogtown into the single registry.

A mod must not do that. It would carry 8540 communities it does not own and
conflict with every other world mod. The mod route is a second registry node in
a sector of its own.

### The one thing still unmeasured

**Does the game read more than one `worldCommunityRegistryNode`?** Vanilla ships
exactly one and EP1 kept it that way, so the shipped data cannot answer it.

The tooling says yes. World Builder (`CP77_entSpawner`) has a Community
spawnable whose export writes a `worldCompiledCommunityAreaNode_Streamable` plus
a separate `<project>_always_loaded` sector, category `AlwaysLoaded`, holding
one `worldCommunityRegistryNode` with exactly the two arrays above, and hands
that sector to ArchiveXL like any other. Its `sourceObjectId` is
`FNV1a64(nodeRef minus '#')`, which is the same rule measured above and arrived
at independently. The REDmodding wiki documents the workflow as working.

That is other people's evidence. It is strong enough to build on and not strong
enough to write into a playbook, so 29 is the bench.

### Two claims elsewhere that this corrects

- `architecture.md`: "Quest-graph `questSpawnSet` nodes only reference existing
  community spawn phases and are unusable for custom NPCs." A community can hold
  `Character.cc_g01_hoshino` as easily as a vanilla record.
- `gotchas.md` 35 says the characters live in a `.community` resource. They live
  in the registry node; the `.community` file is where an author edits them.

### How it was found, which is the reusable part

By asking whether anyone had done it before looking for the mechanism, which is
the order `sources.md` sets and it was the right one. The REDmodding
wiki has a page called "Creating Communities". It documents the UI and says
nothing about node types, but it named the tool, and the tool is open source, so
the export function is the specification. Twenty minutes of reading Lua replaced
five sessions of guessing at a resource reference that does not exist.

The confirmation then came from data already on this machine. Nothing in this
section needed the game running.

---

## 29. Does the game read a `worldCommunityRegistryNode` a MOD ships? **SOLVED, YES. 2026-08-24, run 12.** A community this mod ships spawns our own character, unarmed, exactly as the wiki promised

28 answers everything else about placing a community by reading. This is the
one part shipped data cannot answer, because vanilla ships exactly one registry
node and Phantom Liberty replaced it rather than adding a second.

### Run 1, 2026-08-23. Clean controls, nobody spawned, and it proved less than it looked like

```
0 CAL 1    1 ours 0    2 vanl 0    3 mark 0    4 NEG 0    distance 0.0 m
```

Everything that could void the run behaved. The calibration NPC was found, the
negative slot stayed empty, the player was standing on the line, ArchiveXL
merged both streaming blocks with no error, and a round trip through WolvenKit
showed every field arriving intact: the community id matching on both sides,
all five hour bands, `entryActiveOnStart` 1 on all three entries, the spot refs
and the persistent records.

**It is not an answer, because three things in the chain were ours rather than
the game's, and any one of them produces exactly this reading.**

- The spot nodes were copied from a CROWD workspot in Heywood. A real quest
  community spot at this same estate differs in five fields:
  `isWorkspotInfinite`, `useCrowdBlacklist`, `useCrowdWhitelist`,
  `snapToGround` and `MaxStreamingDistance`.
- `crowdCreationRegistry` was written null where vanilla's registry node
  carries an object.
- Nothing in the run could separate "the registry node is not read" from "the
  registry node is read and our SPOTS are wrong", because every spot in it was
  ours. That is the same gap the pin lab's round 3 had, and it is the one that
  costs a round every time.

One suspect died for free: `spotDef` is null on the vanilla community spot too,
so writing null was never a deviation.

### Run 2, built the same day. The decisive slot

Two slots added, both at vanilla workspots at the estate 44 and 46 m from the
line, and the three deviations above removed.

| slot | | |
|---|---|---|
| 5 | `#q113_ws_arasaka_estate_investigation_002`, driven by an entry of OURS | the game's own spot node and the game's own persistent record, copied whole, so the ONLY mod-authored thing left in that path is the registry node |
| 6 | `..._001`, driven by nobody | the negative control for the pair |

Neither spot is referenced by any of the 2510 communities in the three
always-loaded sectors, checked rather than assumed, so both should be empty.

**Slot 5 is what decides it.** Filling while 1 to 3 stay empty means a mod's
registry node IS read and our spot nodes are the fault, which is a much smaller
problem. Staying empty with clean controls means it is not read.

### Run 2, 2026-08-23. Zero again, controls clean, and the vanilla spot did not change it

```
0 CAL 1   1 ours 0   2 vanl 0   3 mark 0   4 NEG 0   5 VSPOT 0   6 VCTL 0
distance 0.7 m
```

The deployed archive was checked rather than trusted: unbundled back out of
`archive\pc\mod`, it carried all four entries, `vanspot` pointing at
`#q113_ws_arasaka_estate_investigation_002`, the crowd registry as an object,
four persistent records, and the five spot fields matching the vanilla node.
Gotcha 57's fault could not have been this one.

So the game's own spot node, carrying the game's own persistent record, driven
by an entry in a registry node of ours, put nobody on the ground.

**That is a strong negative and it is still not the answer**, because ONE
assumption underneath it has never been measured on this build: that our
ALWAYS-LOADED SECTOR IS ACTUALLY LOADED. ArchiveXL merging a streaming block is
not the same as the game loading the sector the block names, and a sector that
silently never loads gives exactly this reading. Gotcha 39 measured a mod's
always-loaded sector working on 2026-08-18, but that was a different sector
built by a generator that no longer exists, and this one carries two node types
nothing here has ever shipped.

### Run 3, built the same day. The residency instrument

One vanilla stool in each of the two sectors, at slots 7 and 8, asked for by
name rather than counted:

| | |
|---|---|
| 7 | a `worldEntityNode` in the ALWAYS-LOADED sector |
| 8 | the same node in the Exterior sector |

`ResolveNodeRef` reaches a live entity, code 4, only if the sector is loaded and
the node instantiated. **Only 4 carries information**: an absolute `$/...` name
is hashed rather than looked up, so any long string returns 3 including one
nothing ships, which is backlog 11's warning.

- **Slot 7 reads 4** and the always-loaded sector is live, the zeroes above are
  real, and the answer to 29 is no.
- **Slot 7 reads anything else** and two runs measured a sector that was never
  there, and 29 is still open with a different question in front of it.

Slot 8 is the comparison: the Exterior sector is the ordinary case this project
has shipped since 1.2.0, so it should read 4 and says the probe works.

### Run 3, 2026-08-23. The residency instrument said nothing, and it exposed two bench faults

```
0 CAL 1  1 ours 0  2 vanl 0  3 mark 0  4 NEG 0  5 VSPOT 0  6 VCTL 0
7 PROP always-loaded 3   8 PROP exterior 3   distance 0.4 m
```

**Fault one: 3 is the uninformative value and the bench had no control for it.**
Both stools read 3, "an entity id but nothing streamed", which is also exactly
what a long-form name nothing ships returns, because an absolute `$/...` path is
hashed rather than looked up. Backlog 11 says this in as many words and the
instrument was built without the control anyway. The run cannot distinguish "our
sectors are not loaded" from "this probe never reaches a live entity".

**Fault two, and it reaches backwards into runs 1 and 2: the calibration slot
was where the player stands.** The teleport put V on slot 0, so slot 0 counted
whatever was within two metres of his own feet. It read 1 in all three runs and
there is now no way to tell whether that was the spawned NPC or the player. The
one thing the bench had that was supposed to make the zeroes believable is the
one thing that cannot be believed.

Playtest, run 3: *"spawn no longer works, previously it did."* A guard is
visible beside V in run 2's screenshot and absent in run 3's, which fits a
second, smaller problem with the same cause: the NPC was being spawned onto the
exact spot the player was standing on, and 0.4 m of overlap is not the same as
0.7 m.

The old lab kept its calibration 70 m from its probes for precisely this reason.
That file was read before this bench was designed.

### Run 4, built the same day

Four changes, three of them removing bench faults rather than testing anything:

| | |
|---|---|
| the player stands 4 m SHORT of slot 0 | nothing he stands on is a slot, so slot 0 can only be the NPC, and the spawn has room |
| probe 9, a BASE-GAME node 14 m away, same shape, long form | **MUST read 4.** If it does not, probes 7 and 8 say nothing and never did |
| probe 10, a long-form name nothing ships | expected 3, which is the demonstration that 3 is not evidence |
| one streaming block per sector, and float-max reach on both stools | the shipped shard carries exactly one descriptor per block; matching it stops the shape being a variable |

### Run 4, 2026-08-23. THE INSTRUMENT WORKED, AND IT MOVED THE QUESTION

```
0 CAL 1   1..6 all 0
7 PROP our always-loaded 3  not there    8 PROP our exterior 3  not there
9 CTL base-game          4  LIVE        10 CTL never shipped   3
distance from the stand point 0.8 m
```

Every control did its job for the first time. The calibration guard is visible
in the screenshot and the player is 4 m off slot 0, so `0 CAL 1` is the NPC and
not him. The base-game node reads 4, so a long-form name DOES reach a live
entity. The never-shipped name reads 3, so **3 means NOT THERE** rather than
"cannot tell".

**Both of our stools read 3. Neither of this bench's two sectors is delivering
a node at all, so runs 1 to 4 said nothing whatever about communities.** Three
rounds of zeroes were the zeroes of a world file that never arrived.

ArchiveXL merges all three streaming blocks with no error, and the Exterior
sector's `rldGridCell` was checked by prediction against `all.streamingblock`:
1074242, which is exactly what vanilla's `exterior_2_8_1_1` carries. So the
block, the bucket and the descriptor are not the fault.

### Run 5, built the same day. Two candidates, one variable apart

The gig's own shard sector has worked since 1.2.0, so the difference is in this
bench. Two things about it differ from every node this project has got to load.

| | |
|---|---|
| **the instance flags** | the shard container and the base-game sprinkler that probe 7 resolves BOTH carry `Uk10 1056, Uk11 10762`. The stool copied for run 4 carries `Uk11 20490`. `gen_sector.py` already records a trigger area's flags as one of the two reasons the shard did not appear |
| **the name path** | every named node this project has loaded is named for the district it stands in. These stand in North Oak and are named `#c_santo_domingo/arroyo`, because the prefix was copied rather than thought about |

Six props, each one variable from its neighbour, plus three controls:

| probe | sector | name | flags |
|---|---|---|---|
| 1 | Exterior | Arroyo | stool, `Uk11 20490` |
| 2 | Exterior | Arroyo | **shard, `Uk11 10762`** |
| 3 | Exterior | **North Oak** | stool |
| 4 | Exterior | **North Oak** | **shard** |
| 5 | always-loaded | Arroyo | shard |
| 6 | always-loaded | **North Oak** | shard |
| 7 | base-game sprinkler, MUST read 4 | | |
| 8 | a name nothing ships, expected 3 | | |
| 9 | **the gig's own shard container** | | |

**Probe 9 is the one that matters if the matrix comes back empty.** It reads 3
from the garden and must read 4 at the office, and it answers "do this mod's
sectors work AT ALL in this build" without depending on anything the bench
authored. Read it by pressing the office teleport at the end of the run.

### Run 5, 2026-08-23. Both candidates dead, and the shard proves the machinery is fine

At the bench, all six props read 3. At the office, `9 CTL the gig's own shard`
reads **4 LIVE**, and the base-game sprinkler correctly falls to 3 at 2567 m.

So the flags are not it, the name path is not it, and **this mod's world files
work perfectly in this build**: the shard node is a live entity 2.5 km from the
bench. Only the two sectors this bench ships deliver nothing.

Four things were checked offline afterwards and all four came back clean:

- **The grid cells.** Predicted 1074242 for the bench and 1055294 for the
  shard; vanilla's `exterior_2_8_1_1` and `exterior_-2_-12_0_1` carry exactly
  those. Both vanilla boxes contain our points.
- **The blocks.** All three descriptors are identical in shape, and ArchiveXL's
  `OnStreamingWorldLoad` appends every one to `blockRefs`, so "only the first
  mod block counts" is not a rule.
- **`variantIndices: [0]` with an empty `variantNodes`** is what vanilla writes
  for `always_loaded_0` (5285 nodes) and for `exterior_4_15_3_0` (287), so
  backlog 11's warning does not apply to it.
- **Both prop templates exist** in `basegame_3_nightcity.archive`.

### Run 6, built the same day. The pattern nobody had looked at

Every node that has ever probed 4 in this project carries `instanceData`, a
whole entity chunk: the shard container, and the base-game sprinkler probe 7
resolves. Every node reading 3 has `instanceData: null`.

`ResolveNodeRef` ends at `FindEntityByID`. **A node with no entity payload may
stream in, render, and never register an entity at all**, in which case 3 is
what it reads while standing in plain sight, and every "not there" in runs 4
and 5 is an artefact rather than a finding.

Probes 10 and 11 are a whole vanilla sprinkler node, entity chunk and all,
lifted mechanically into each of the two sectors. Nothing about them is
authored here except the debug name.

| reading | meaning |
|---|---|
| 10 and 11 read 4 | our sectors DO load, the stools were never probeable, and the community question reopens with a bench that works |
| 10 and 11 read 3 | our sectors really are dead, and the next question is why a sector built by this generator differs from one built by `gen_sector.py` |

### Run 6, 2026-08-23. THE BENCH IS SOUND, and the answer is no

At the bench, and then from the office 2567 m away:

| probe | at the bench | at the office |
|---|---|---|
| 9, the gig's own shard | 3 | **4 LIVE** |
| 10, our sprinkler, Exterior sector | **4 LIVE** | 3 |
| 11, our sprinkler, ALWAYS-LOADED sector | **4 LIVE** | **4 LIVE** |
| 1 to 6, the stools | 3 | 3 |

**Both of this bench's sectors load and their nodes instantiate.** Probe 11 is a
live entity from the far side of the city, which is what an always-loaded
sector is for, and probe 10 correctly goes dark at range, which is what an
Exterior one is for. The instrument now reads all four states.

**The stools were never a measurement.** The only difference between them and
the sprinklers is `instanceData`, and that decides whether a node registers an
ENTITY at all. See gotcha 60.

### So: a mod's `worldCommunityRegistryNode` does not put anyone on the ground

Everything the community needed was present and proven present:

- the registry node, resident everywhere, in a sector whose nodes are live
- the community area node beside it in the same sector
- three spots of ours in an Exterior sector that is loaded at the bench
- a fourth entry pointing at a VANILLA spot, with the game's own persistent
  record for it copied whole
- four entries, `entryActiveOnStart` 1 on all four, all five named time bands,
  quantity 1, `alwaysSpawned` at vanilla's default, the player standing 4 to
  16 m away for minutes at a time

Nobody spawned, at any slot, in any run. The negative slot stayed empty and the
calibration NPC was found every time.

**The configuration matched vanilla's majority**, which was read at the time as
meaning no quest node was needed. Of vanilla's 8540 registry items, 4726 have
`entryActiveOnStart` on for every entry, and 23077 of 26655 phases carry the
same `alwaysSpawned` default ours does.

**That inference was wrong and the next section is the correction.**
`entryActiveOnStart` governs the entry inside a community that is already
running. Vanilla activates the community itself from a quest phase, ambient
open-world populations included.

### Reading afterwards: the bench was wrong in two ways, and both are measured

The six runs above are a negative about a bench that could not have worked. Both
faults were found by reading shipped data, not by another playtest.

#### 1. A community's identity is the hash of its own NodeRef

`always_loaded_0` registers this in its `nodeRefs` table:

```
$/03_night_city/c_pacifica/coastview/#pcv_01/.../#mq025_com_fabiola
```

and the community area node beside it carries `sourceObjectId`
12672209401641994660. **FNV1a64 of that ref with its '#' characters removed is
12672209401641994660 exactly.** Same rule as a spot's `worldGlobalNodeID`, and
the same rule World Builder uses from the other end: its community spawnable
labels the field "CommunityID (NodeRef)", exports it as the node's own ref, and
derives `sourceObjectId` from it.

Runs 1 to 6 named the area node `#cc_g01_cl_area` and hashed
`#cc_g01_cl_community` into the id. **Two different strings.** The id pointed at
nothing, and no quest node could have addressed it either.

Two more things fall out of the same reading, and both are needed:

- **The name goes in the sector's `nodeRefs` table.** That table is not parallel
  to anything: `always_loaded_0` registers 33506 names against 15024 instances,
  so a name can be listed without being attached to a node. Vanilla's community
  area node instances carry NO name at all, 785, 1265 and 460 of them, and the
  community's name is a standalone entry. This bench now attaches it to the area
  node as well, which is what World Builder does.
- **The area's box must contain the spots it references.** The old box was 60 m
  across and centred on slot 2; the vanilla spot at slot 5 was 50 m outside it.

#### 2. A community has to be ACTIVATED, and `entryActiveOnStart` does not do it

`base/open_world/community/city_centre/corpo_plaza/pop_cct_cpz_phase.questphase`
is 2158 bytes and does exactly one thing:

```
questSpawnManagerNodeDefinition
  actions[0].type = questCommunityTemplate_NodeType
    action                  Activate
    communityEntryName      None
    communityEntryPhaseName None
    spawnerReference        #cct_cpz_com
```

That is an AMBIENT open-world population community, the least quest-like thing
in the game, and vanilla still switches it on from a quest phase. **52 such
phases ship under `base/open_world/community/`.** So `entryActiveOnStart`
governs the entry inside a running community; it does not start the community,
and the 4726-of-8540 statistic above was being read as "no quest needed" when it
means nothing of the kind.

Across a 12-file sample of the 1394 questphases that use the node type:

| | |
|---|---|
| `action` | Deactivate 97, Activate 41, Reactivate 18, ResetKillCount 3 |
| `spawnerReference` | long form 105, short form 54 |
| entry / phase | `None` / `None` in 112 of 133, meaning the whole community |

`questSpawnManagerNodeDefinition` carries exactly `$type`, `actions`, `id`,
`sockets` in all 158 occurrences, with the ordinary three sockets.

### Run 7, built 2026-08-23. The first one that could work

| | |
|---|---|
| one name for the community | the area node carries it, the sector registers it, `sourceObjectId` is its hash, the registry repeats that hash, and the quest node addresses the same string. Checked in the built archive: all three agree |
| a quest phase | `gen_commlab_phase.py`. One press walks Activate whole, Reactivate whole, Activate entry `ours`, Activate entry `vanilla`, with a breadcrumb after each |
| the area box | now derived from the spots it references, so every entry is inside it |
| **a direct answer** | `GetGameObjectsFromSpawnerEntityID(id, entryNames, game, out objects)`. Asking the spawner system for the community's own id says whether the game KNOWS our community, whether or not a body is standing anywhere |
| the stools are gone | gotcha 60 explains them and they only added rows |

**`cc_g01_cl_known` is the row to read first, and it is what every previous run
lacked.** Counting bodies cannot tell "the registry was never read" from "it was
read and nobody spawned". This can.

### Run 7, 2026-08-24. Everything correct, and still nobody

At the bench, and then from the office 2567 m away:

```
the game knows it: 0 body/ies      community name resolves: YES
quest phase step: 9 of 9
0 CAL 1   1 ours 0  2 vanl 0  3 mark 0  4 NEG 0  5 VSPOT 0  6 VCTL 0
1 our exterior sector      4 LIVE  (3 at the office, correctly)
2 our always-loaded sector 4 LIVE  (4 at the office, correctly)
3 CTL base-game            4 LIVE  (3 at the office, correctly)
4 CTL never shipped        3
```

**Every prerequisite is now proven present, and that is what makes this run
different from the six before it:**

- the community's name RESOLVES, so the id link that was broken in runs 1 to 6
  is fixed and the three identifiers agree
- the quest phase reached step 9, so all four activations fired: Activate whole,
  Reactivate whole, Activate entry `ours`, Activate entry `vanilla`
- both sectors are live, at the bench and at range, in the pattern each is meant
  to have
- the negative control is empty and the calibration NPC is found
- one entry drives a VANILLA spot with the game's own persistent record

Nobody spawned at any of the four spots.

### The instrument that did not do its job, and this is the fourth of these

**`GetGameObjectsFromSpawnerEntityID` returns SPAWNED objects, so 0 means "no
bodies" and not "the community is unknown."** It was added to separate "the
registry was never read" from "it was read and nothing spawned", and it cannot:
both give 0. That is the same class of miss as gotcha 60, made while writing the
warning about gotcha 60.

Two things would fix it and neither has been run:

- **`GetFixedEntityIdsFromSpawnerEntityID`**, the sibling call. A community's
  fixed entity ids are deterministic per entry and may exist before anything
  spawns, so a non-empty answer would mean the registry was read.
- **A VANILLA community as a control**, asked the same way with the player
  standing in its crowd. Without it, a 0 from our own community cannot be told
  from a call that returns 0 for everything.

**Read the slot counts rather than that row.** With `4 NEG` empty and `0 CAL`
found, the seven zeroes are a real "nobody spawned". What is not established is
WHY, and the two candidates need different next steps.

### Run 8, built 2026-08-24. The one deviation this bench made on purpose

Playtest, on being told 7 was a clean negative: *"Have you read wolvenkit info
... They work with communities and spawn NPCs ... it's possible."*

Correct, and the answer was two steps away for the whole of 29. The REDmodding
wiki names World Builder, World Builder is open source, and its exporter plus
`import_object_spawner.wscript` are a complete statement of what a working
community mod writes. Reading both found one difference:

| runs 1 to 7, community A | World Builder, community B |
|---|---|
| `worldCompiledCommunityAreaNode` | `worldCompiledCommunityAreaNode_Streamable` |
| in the ALWAYS-LOADED sector | in an ordinary streaming sector |
| `MaxStreamingDistance` float-max, `UkFloat1` 1550, flags 32 / 512 | 200, 250, 1024 / 512 |

`worldCompiledCommunityAreaNode_Streamable` is a real class, confirmed by round
trip: the plain node plus one field, `streamingDistance`. **The plain one is what
the game's COOKER emits into always_loaded. A mod does not cook.** Writing the
cooked form may be writing something nothing reads.

This bench chose the cooked form deliberately, and the reason is in the run 7
generator header: it had been read field by field in vanilla. That is a good
reason to trust what a field MEANS and a bad reason to ignore what a working
example DOES. `docs/sources.md` now carries the rule and the sources.

**Run 8 ships both communities, one variable apart, in one build.** A is
unchanged. B is `_Streamable`, in the Exterior sector, with World Builder's
instance values, its own name, id, registry item, two entries and two AI spots
at slots 9 and 10. The quest phase activates both.

| reading | meaning |
|---|---|
| slot 9 or 10 fills, 1 to 3 do not | **the node type and its sector are the answer.** A mod ships communities the World Builder way and this closes yes |
| 1 to 3 fill and 9, 10 do not | the opposite, and surprising |
| both fill | it never mattered and something else in run 7 did |
| neither fills, controls clean | the deviation was not it either, and the next source to read is ArchiveXL's own sector handling |

### Run 8, 2026-08-24. Both shapes, nobody

```
A bodies 0   B bodies 0      names resolve: A yes  B yes
quest phase step: 99 (all done)
0 CAL 1   1..3 A 0   4 NEG 0   5 A VSPOT 0   6 VCTL 0   9,10 B 0
probes: our exterior 4 LIVE, our always-loaded 4 LIVE,
        base-game 4 LIVE, never shipped 3
```

**World Builder's shape spawned nobody either.** The node type and the sector it
sits in are not the answer. Every activation fired, both names resolve, both
sectors are live, every control is clean.

### What ArchiveXL's source says, and it changes the reading

`src/App/Extensions/WorldStreaming/Extension.cpp` carries
`OnRegisterSpots`, a hook on the game's `AIWorkspotManager::RegisterSpots` whose
only job is to **MERGE** a mod's `AISpotPersistentData` into the existing array
rather than replace it, growing the array and clearing its sorted flag first.

That patch exists for exactly one reason: so that a mod's own sector can bring
AI spots to the community system. **The route is supported by design.** So eight
runs of nothing are far more likely to be something still wrong in this bench's
data than proof the engine refuses.

Codeware 1.20.3 is installed, above the 1.15.0 the wiki asks for, so the missing
requirement is not that either.

### The working examples, pulled apart 2026-08-24. NONE OF THEM SHIPS A COMMUNITY

Three published quest mods are staged on this machine and all three place NPCs.
Their sectors were extracted and read node by node:

| mod | its sector | what is in it |
|---|---|---|
| Californication | `californication.streamingsector`, Quest, level 255 | 2 `worldAISpotNode`, 1 `worldStaticMarkerNode`, 1 `worldTriggerAreaNode` |
| One More Light | `one_more_light.streamingsector`, AlwaysLoaded, level 255 | 2 trigger areas, 1 marker |
| Deceptious Quest Core | AlwaysLoaded, level 0 | 1 trigger area |

**Not one community node, not one registry node, between them.** The claim that
modders place NPCs with communities is about World Builder, and no mod on this
machine uses it.

What they do instead, and Californication is the complete worked example:

- **ship their own AI spots** for the workspot an NPC should use, named
  long-form and nested under a real vanilla prefab path
  (`.../loc_sq030_love_shack_prefabTPTXF5Q/.../#nq_cali_ws_judy_sit`)
- **REACTIVATE ONE OF THE GAME'S OWN spawn sets** rather than creating one:

```
questSpawnSet_NodeType
  action     Reactivate        action     Activate
  entryName  judy              entryName  van
  phaseName  dlc3_judy_sleep   phaseName  None
  reference  #judy             reference  #judy_vehicle
```

- **spawn the speaking actor from the scene**, `acquisitionPlan: spawnDespawn`,
  which is what this project already does

Two things follow. Californication's Judy sitting on a cliff is a modded AI spot
plus a vanilla community switched on, and that is the shipped precedent for 27's
route A. And **`questSpawnSet_NodeType` is a node type this bench never emitted
across eight runs**: same four fields as the community node under different
names, `reference` where the other says `spawnerReference`, in 473 shipped
questphases.

### Run 9, built 2026-08-24

The bench phase now drives both communities with `questSpawnSet_NodeType` as
well, five more actions after the seven it already had, breadcrumbs throughout.
Nothing else changed.

If the spawn-set node is what reaches a mod's registry, that is the answer. If
it is not, then eight runs plus two node types plus both area-node shapes have
failed, no local mod contradicts it, and 29 should close negative with the
Californication route written up as what to do instead.

### Run 9, 2026-08-24. `questSpawnSet_NodeType` changed nothing

Byte for byte the same reading as run 8:

```
A bodies 0   B bodies 0      names resolve: A yes  B yes
quest phase step: 99 (all done)
0 CAL 1   1..3 A 0   4 NEG 0   5 A VSPOT 0   6 VCTL 0   9,10 B 0
probes: our exterior 4 LIVE, our always-loaded 4 LIVE,
        base-game 4 LIVE, never shipped 3
```

### CLOSED NEGATIVE. What nine runs covered

| | |
|---|---|
| identity | the community's id IS the hash of its own registered NodeRef, on all three sides, verified in the built archive |
| area node | both `worldCompiledCommunityAreaNode` in an always-loaded sector and `worldCompiledCommunityAreaNode_Streamable` in a streaming one |
| activation | `questCommunityTemplate_NodeType` Activate, Reactivate and per-entry, AND `questSpawnSet_NodeType` the same ways. Twelve actions, all fired |
| spots | our AI spots, our marker, and a VANILLA workspot with the game's own persistent record |
| residency | both sectors probe as live entities, one of them from 2567 m |
| controls | negative slot empty and calibration NPC found in every run |
| time | all five named hour bands |

**No NPC ever appeared.** This project should not place NPCs with a community,
and nothing further here is worth a playtest.

**This is not "the engine refuses".** ArchiveXL carries a hook whose only job is
to merge a mod's `AISpotPersistentData` into the game's array, so somebody built
for this. The honest statement is that this bench could not do it, that no
published mod on this machine does it, and that the cost has stopped being worth
the answer.

**The one thing never tried** is producing a community from World Builder itself,
in game, and diffing its files against these. That is the only cheap move left
and it needs the tool rather than more reasoning.

### What to do instead, and it is better for 27 anyway

Californication is a shipped mod that puts Judy sitting on a cliff at a spot it
ships itself. Three parts, none of them a community:

1. **Its own `worldAISpotNode`** for the workspot, named long-form and nested
   under a real vanilla prefab path, in a `category: Quest` sector.
2. **`questSpawnSet_NodeType` against one of the GAME'S OWN spawn sets**:
   `Reactivate`, entry `judy`, phase `dlc3_judy_sleep`, reference `#judy`.
3. **A scene actor** with `acquisitionPlan: spawnDespawn`, which is what this
   project already emits for every speaking NPC.

27 chose route A, a real body for Hoshino in this mod's own sector. That is the
same shape as Judy on the cliff, and it has a worked example that ships. Start
there rather than here.

### Stop guessing and get a working example

Every round since run 5 has been a hypothesis about what World Builder does
differently, and two of the three were wrong. The reasoning has run out of
cheap discriminators.

**The next step is a real World Builder community to diff against**, either
exported from the tool on this machine or extracted from a published mod that
ships one. Field by field against ours, the way the shard container was lifted
rather than retyped. That is offline work and it ends the guessing.

Until that exists, this section should not be read as "communities do not work
for mods". It should be read as "this bench has not managed one, and ArchiveXL
contains a patch that only makes sense if they do".

### The protocol

Pre-gig save. The quest phase runs ONCE PER SAVE LOAD, so reload to arm it
again (gotcha 54's sibling: a linear dev branch fires once and then sits).

1. `TELEPORT: the community lab line`. You land 4 m short of slot 0.
2. `ARM the quest phase`, and watch `quest phase step` reach **99**. It takes
   about five seconds.
3. `WATCH: on`, half a minute.
4. `SPAWN the calibration NPC`.
5. Read the panel, then the office teleport and read it again.

Read it in this order:

| row | meaning |
|---|---|
| **the game knows it** | anything but 0 and a mod's registry node IS read. THE ANSWER |
| community name resolves | must be yes, or the id is wrong again and nothing else counts |
| quest phase step | 9 means all four activations ran. Stuck below 9 is a phase parked mid-chain |
| `4 NEG` | 0, or the garden is not empty and the run is void |
| `0 CAL` | 1 after the spawn |
| probe 3 | LIVE at the bench, or no probe means anything |
| probe 4 | 3, which is what makes 3 mean "not there" |
| probes 1 and 2 | LIVE, our two sectors. 2 stays LIVE at the office |

**If `the game knows it` is above 0**, a mod can place a community NPC and the
next question is scene acquisition through `spawnSetNameToCommunityID`, which
the bench already registers as `#cc_g01_cl_spawnset`.

**If it is 0 with the step at 9 and every control clean**, a mod's registry node
is not read, the two-bodies arrangement is permanent, and this closes.

### The bench

Five positions in a line in the estate garden in North Oak, 4 m apart, on the
teleport this mod already has. The garden is chosen because V has stood on that
exact point, so the ground height is measured, and because a pre-gig save has
nothing of ours there.

| slot | what stands there | what it separates |
|---|---|---|
| 0 | a script-spawned NPC, put there by the bench | CALIBRATION. The detector, in the same shape as the thing under test |
| 1 | our AI spot + `Character.cc_g01_hoshino` | the whole question, with our own character record |
| 2 | our AI spot + a vanilla `Character` record | whether OUR record is the fault rather than the community |
| 3 | our marker spot + the same vanilla record | whether the spot NODE TYPE is the fault |
| 4 | nothing is shipped here at all | NEGATIVE CONTROL |
| 5 | a VANILLA workspot + the same vanilla record | whether the registry node is read at all, with nothing of ours below it |
| 6 | the vanilla workspot beside it, driven by nobody | NEGATIVE CONTROL for the pair |
| 7 | a vanilla stool in the ALWAYS-LOADED sector, PROBED not counted | whether that sector is loaded at all |
| 8 | the same stool in the Exterior sector | the comparison, and proof the probe works |

Slots 1, 2 and 3 are three entries of one community, so the main question is
asked once and the three differences read separately.

`tools/gig01/gen_commlab.py` writes two sectors and a block,
`Gig01_CommLab.reds` does the scanning, and the dev menu has the buttons. The
generator's header is the authority on all three and on how to remove them.

### The protocol

Load a pre-gig save. Nothing needs setting up.

1. `TELEPORT: the community lab line`.
2. Read the **distance to slot 0** in the panel. Under 20 m or the run says
   nothing.
3. `WATCH: on`, and leave it running for half a minute while standing on the
   line. A community entry waits for a player to be near, so a single scan
   taken the instant after a teleport can read 0 for a community that works.
4. Look along the line. Slots are 4 m apart in the order above.
5. `SPAWN the calibration NPC`, and watch slot 0 go to 1.
6. `REPORT to the log`, quit so CET flushes, and read `ArchiveXL.log` for the
   two `cc_g01_commlab` sectors merging.

### How to read it

**Slot 4 first, then slot 0.** Both are controls and both can void the run.

| reading | meaning |
|---|---|
| slot 4 is not 0 | VOID. Something is wandering the garden and every other count is suspect |
| slot 0 stays 0 after the spawn | VOID. The detector is broken, not the community |
| 1, 2 and 3 all 0, controls clean | a mod's registry node is not read. The two-bodies arrangement is permanent and gigs 02 to 04 inherit it |
| 2 or 3 counts, 1 does not | the community works and `Character.cc_g01_hoshino` is the problem, which is a TweakXL question and a much smaller one |
| 3 counts, 1 and 2 do not | the AI spot node is wrong, not the community. `spotDef` is written null here where vanilla carries an `AITrafficExternalWorkspotDefinition`, and that is the first suspect |
| any of 1, 2, 3 counts | **the answer is yes**, and the next thing to test is scene acquisition through `spawnSetNameToCommunityID`, which the bench already registers as `#cc_g01_cl_spawnset` |

### What was already spent, and on what

One fault, and it was the one this project has written down twice.

**HandleIds are file-wide within a sector.** Three AI spot nodes each numbering
their inner `AIActionSpot` chunk 1 is three collisions, and WolvenKit refuses
the file from inside the CName converter of the NEXT node, reporting that
node's `$type` line. It reads as a wrong class name and is nothing of the sort.
The generator now renumbers every handle in document order as a final pass.

### Removing it

`tools/gig01/gen_commlab.py` is untracked on purpose, so that a dev bench
nobody else needs is not carried around with the generators that matter. Same
reason `gen_pinlab.py` was never committed. The three deletes, the `.archive.xl` line
and the `init.lua` block are listed in the generator's header, and no shipped
generator is touched, so the rollback is a delete rather than a diff to read.

---

## 29-ADDENDUM, 2026-08-24. Three questions answered by reading, and run 10

Asked after the close: the wiki says communities work, so how do THEY load one,
why does ours not work, and do the docs agree with Californication?

### How is a World Builder community loaded? By NOTHING. Shipping it is loading it

The import script (`import_object_spawner.wscript`) writes the sectors, one
`all.streamingblock`, and an `.xl` that registers that block. **That is the
whole loading story, and it is the same mechanism this bench already uses.**
There is no loader key, no quest requirement, no extra registration.

And the wiki is explicit that **no activation is needed**: "Initial Phase Name
and Active On Start are only of interest for quest modding, so ignore those for
now." A plain World Builder community spawns from `entryActiveOnStart` alone.
That corrects the inference behind runs 7 to 9's quest phase (gotcha 63 is
amended): vanilla's 52 open-world activation phases exist to CONTROL ambient
communities, not because a community cannot start without one.

### Is ArchiveXL support real, and is it installed? Yes and yes

Commit `833df3bc`, 2024-10-31, "Add community registrty merging": the
`AIWorkspotManager::RegisterSpots` hook that merges a mod's spot records into
the game's array instead of letting a second registry clobber it. That is the
ONLY community-specific code in ArchiveXL, it exists precisely so World Builder
communities can work, and it long predates the installed 1.27.1. Version is not
the problem.

### Do the docs agree with Californication? No. They are two different routes

| | the wiki / World Builder | Californication |
|---|---|---|
| the community | CREATE your own, registry node and all | REUSE a vanilla spawn set (`#judy`), ship none |
| the character | any record, yours included | whoever vanilla's entry names |
| activation | none needed | `questSpawnSet_NodeType` Reactivate |
| the spot | own `worldAISpotNode`, used BY the community | own `worldAISpotNode`, used by a SCENE workspot node |

The docs never mention Californication's route; Californication never uses the
docs' route. Both are real. The docs' route is the one that would give Hoshino
his own record in a persistent body, which is why it kept being worth runs.

### Why does ours not work then? Down to four differences, and run 10 ships them

Runs 7 to 9 built the registry to VANILLA's cooked layout. A World Builder
registry differs, and a WolvenKit round trip eliminated half the list: the
export's missing keys (`initializers`, `spawnInView`, `alwaysSpawned`,
`prefetchAppearance`, `crowdEntries`) deserialize to exactly the defaults
vanilla writes explicitly, so they never reached the game as differences.

What remains, all now matched byte for byte in run 10:

| | runs 7 to 9 (vanilla layout) | run 10 (World Builder layout) |
|---|---|---|
| registry sector | level 255, float-max box | **level 1, +-99999 box** |
| registry node | long-form NAME, in `nodeRefs` | **unnamed uint64 hash, registered nowhere** |
| instance ranges | max float-max, ukfloat 17.32 | **max 17.32, ukfloat 99999999, inverted** |
| `crowdCreationRegistry` | empty object | **null** |
| `spawnSetNameToCommunityID` | two entries | **empty** |
| B's spots | vanilla estate copy, finite | **WB minimal, `isWorkspotInfinite` 1** |

The quest phase stays, as prodding, but per the wiki B should spawn WITHOUT it:
walk to the line and look at slots 9 and 10 before arming anything.

If run 10 also spawns nobody, the byte-level shape is exhausted and the residue
is environmental: something World Builder's runtime half (it is a CET mod)
does at spawn time that the files alone do not, which would itself be the
finding, because the wiki's claim is that the FILES suffice.

---

## 29-ADDENDUM-2, 2026-08-24 evening. Run 10 failed, the wiki's promise is now in question, and the search for a runtime spawner came back empty

### Run 10: World Builder's byte-exact shape, and still nobody

Read before arming AND after: all zeros both times, step 99, every control
clean. **Community B did not spawn on its own, which is what the wiki promises
a World Builder community does.** So either the wiki's claim needs a piece the
files do not show, or something environmental is missing.

### The logs say NOTHING, and that is a finding

Every log from the session was swept: red4ext, ArchiveXL, Codeware, TweakXL,
redscript, CET. Not one line about communities, registries or spawning. **The
game has no error path for a community it ignores.** The panel facts remain the
only instrument, and the next-run upgrade is RedHotTools, which is already
installed: its world inspector can show whether the registry node instance is
actually attached, live.

### There is no runtime spawner node to ship. Checked, not assumed

The suspicion was that `sourceObjectId` being an ENTITY id meant a spawner
node somewhere references the `.community` by path, and the bench never shipped
one. Hunted properly:

- `worldPopulationSpawnerNode` exists, but it is a SINGLE-NPC spawner
  (`objectRecordId` one Character record, `spawnOnStart`, `alwaysSpawned`); no
  community reference on it.
- fabiola's community name appears in NO sector: not the 2356 quest sectors,
  not the 175 grid sectors covering her spot, all binary-grepped raw (validated
  against a sector with known strings). It exists ONLY in `always_loaded_0`'s
  `nodeRefs` table and as the hash in her area node and registry item.

**So a vanilla community's prefab compiles away entirely.** The area node plus
the registry item ARE the whole compiled community, and that is exactly what
this bench ships. There is no missing node type.

One false positive caught on the way: `cct_cpz_com` greps into
`cct_cpz_commemorative_park`. Substring matches on short names are gotcha 60's
shape again; fabiola's conclusion stands because her name is long and exact.

### The two moves left, and neither is another blind run

1. **A real World Builder community mod's files.** "Personal Mechanics" (Nexus
   26885) ships World Builder community NPCs by its own description. Nexus
   downloads need the account, so this is a request to the design: download it
   through Vortex, and the diff against our files is an hour of offline work
   and decisive either way.
2. **RedHotTools next run**: inspect `cc_g01_commlab_al` live, confirm the
   registry node instance attaches, and look at what sits at the community's
   coordinates. That turns "the game says nothing" into a reading.

Until one of those lands, the honest status line is: ten byte-faithful runs,
no spawn, no error, no local counter-example, and one Nexus mod page claiming
the route works.

---

## 29-ADDENDUM-3, 2026-08-24. Personal Mechanics opened, and it disagrees with runs 1 to 10 in exactly two ways

The design downloaded Personal Mechanics (Nexus 26885), the first WORKING World
Builder community mod this bench has ever had in its hands. Pulled apart file by
file. Its `pmp_vic_mec` sector is one community and one AI spot, the smallest
possible worked example, and its community id was verified to the digit:
`FNV1a64('$/mod/pmp_vic_mec/pmp_vic_mec_mec')`.

### What it confirms

- The registry is EXACTLY run 10's: AlwaysLoaded level 1, +-99999 box, unnamed
  uint64 registry node, inverted ranges 17.32 / 1e8, uk10 32, null crowd
  registry, empty spawn sets, debugName "registry". **The registry is retired
  as a suspect.**
- The id rule (gotcha 62) holds for a shipped mod.
- Its entries carry the FULL key set with `entryActiveOnStart` 1, like runs
  7 to 9.
- **Its quest phase ACTIVATES the communities**: `questCommunityTemplate_NodeType`,
  Activate, entry None, phase None, the long community ref, exactly the node
  this bench has emitted since run 7. It even Deactivates a VANILLA community
  (Kabuki open-world) to clear space, and pairs Deactivate/Activate per shop.
  So shipped practice arms communities even though the wiki says it is
  unnecessary; gotcha 63's amendment gets its own amendment.

### The two things it does that no run ever tried

| | runs 1 to 10 | Personal Mechanics |
|---|---|---|
| ref root | `$/03_night_city/...` | **`$/mod/<sector>/#<name>`** |
| the community's sector | Exterior (or the registry's) | **AlwaysLoaded level 1, local ~300 m box, cell 0** |

Every name this project has EVER shipped is rooted `$/03_night_city/`, because
that is what vanilla writes and what backlog 11 measured resolving. World
Builder roots everything under `$/mod/`, and the community system may well
resolve through machinery that cares which root a name hangs from. And its
community-plus-spots sectors are AlwaysLoaded with small local boxes, a
combination nothing here ever shipped: spots always sat in the Exterior sector.

Its instance values are 120 / 100 / 1024 / 512 on both the community node and
the spot, minor against the two above.

### Run 11, built and deployed 2026-08-24

Community B moves into its own `cc_g01_commlab_b` sector that mirrors
`pmp_vic_mec` exactly: AlwaysLoaded level 1, cell 0, a 300 m local box, the
`_Streamable` area node and both AI spots inside it, every ref rooted
`$/mod/cc_g01_commlab_b/#...`, Personal Mechanics' instance values throughout.
The quest phase and the panel follow the new ref. Community A and all controls
unchanged.

If slots 9 and 10 fill, the root and the sector were the answer, ten runs of
"no" become "yes with the right root", and 29 reopens as SOLVED. If they stay
empty, the diff against a working mod is exhausted at the file level and the
next stop is RedHotTools on the live world.

---

## 29-ADDENDUM-4, 2026-08-24. Run 11 fails, PM's Lua is innocent, and the A/B is now installed

### Run 11: the exact mirror of a working mod, and still nobody

Unarmed zeros, armed to step 99 zeros, calibration found. Community B was a
field-for-field mirror of `pmp_vic_mec`: the `$/mod/` root, the AlwaysLoaded
level-1 sector with a local box, their instance values, their activation node.

### Personal Mechanics' Lua does NOT spawn its NPCs. Checked line by line

Its `init.lua` is 85 lines: a settings page that writes two facts
(`personalmechanics_h10_enabled`, `personalmechanics_viktor_enabled`) and
nothing else. No spawn call anywhere. The Car Mod Shop Lua is vehicle-shop
logic. **The mechanic NPCs are pure community files plus a quest phase**, so
the mirror was of the right thing and the file-level comparison is genuinely
exhausted.

Their character records were read too: full standalone `gamedataCharacter_Record`
entries with crowd `entityTemplatePath`s, `isBumpable: False`,
`crowdMemberSettings`. Worth copying if a record-level difference ever becomes
the suspect, but slot 2/10 always carried a vanilla record, so records alone
cannot explain eleven empty runs.

### The question that decides everything: does PM work on THIS machine?

It has never been installed here; the zip was downloaded for dissection. If its
own mechanics do not spawn on this machine either, then eleven runs were
measuring the ENVIRONMENT, not the files, and every conclusion since run 1
needs re-reading in that light.

**Installed 2026-08-24, manually, not through Vortex:**

- `archive/pc/mod/PersonalMechanics.archive`, `personalmechanics.xl`,
  `personalmechanics_p.xl`
- CET `mods/Personal Mechanics/` and `mods/Car Mod Shop/`
- `r6/tweaks/Personal Mechanics/`

Remove by deleting exactly those. The bench stays deployed beside it.

**The test costs one trip.** Its Viktor's-garage mechanic (`pmp_vic_mec`) is at
(-1572, 1260), the back alley by Viktor's clinic in Little China; the Miguel
shop (`oficina_wat_miguel`) is 450 m east at (-1120, 1201).

**Do not save during the test session.** PM's quest phase Deactivates a vanilla
Kabuki community as part of its setup, and community state persists in a save.
Load the pre-gig save, look, quit without saving.

| PM's mechanic | meaning |
|---|---|
| spawns | communities DO work here, the difference is real and still in our data, and RedHotTools can diff the two live communities side by side |
| does not spawn | the environment was the variable all along, eleven runs were sound negatives about nothing, and the suspect list is the installed loader stack |

---

## 29-ADDENDUM-5, 2026-08-24 evening. PERSONAL MECHANICS SPAWNS ON THIS MACHINE, and the diff names two suspects this bench never questioned

### The A/B landed

Playtest screenshot: Miguel's shop in Kabuki, and there he stands, service
icons overhead, spawned by pure community files plus a quest phase, on this
machine, in the same session where our community sits empty. (The Viktor spot
was empty; his location is behind their settings toggle and their own notes
say it applies on fast travel, so Miguel is the reading that counts.)

**Communities work here. The environment is innocent. The difference is real
and in our data.**

### The mechanical diff, ours against their working item

Field for field, defaults excluded, two structural differences survive, and
every working example anywhere does the opposite of this bench:

| | every run since 1 | fabiola, PM, the wiki's screenshots |
|---|---|---|
| `appearances` | EMPTY | at least one named appearance |
| `timePeriods` per phase | five, all sharing one spot | ONE |

Both were this bench's own inventions in run 1, and both survived eleven
rebuilds unquestioned: the empty appearances because the wiki called the field
optional, the five periods as "so time of day cannot be the fault". A
constant carried from run 1 is invisible to every A/B built after it.

### Run 12, built, deploy pending the game closing

Community B's two entries become: `Character.miguel` with
`citizen__aldecaldos_ma_mechanic_04`, THEIR exact proven pair, possible
because their mod is now installed beside the bench; and
`Character.cc_g01_hoshino` with `default`. One period, `Day`, one spot each.
Everything else stays run 11's PM mirror.

| slots 9 and 10 | meaning |
|---|---|
| both fill | the empty appearances or the five periods were the whole story since run 1 |
| miguel only | our RECORD or its `default` appearance is the last difference, and their record yaml is the template to copy |
| neither | the community DATA is exhausted and the difference is in how the two mods' sectors reach the game, which RedHotTools can now compare live |

---

## 29-ADDENDUM-6, 2026-08-24 night. RUN 12 SPAWNS. The answer is YES

Three screenshots, one timeline, and the first one is the whole result:

| time | state | slot 9 (`ours_b`, HOSHINO) | slot 10 (`miguel_b`) | spawner reports |
|---|---|---|---|---|
| 7:20 | UNARMED, step 0 | **1** | **1** | **B bodies 1** |
| 7:22 | armed, step 99 | 1 | 0 | B bodies 1 |
| 7:24 | after calibration | 1 | 0 | B bodies 1 |

**Both entries spawned on save load with no quest node**, which is what the
wiki promised all along. `GetGameObjectsFromSpawnerEntityID` went non-zero for
the first time in twelve runs. And the arming sequence, whose per-entry
Activate names only `ours_b`, visibly switched `miguel_b` OFF: the quest-node
control half works too, demonstrated by accident.

**Slot 9 is `Character.cc_g01_hoshino`.** Our own record, our own community,
our own sector, standing in the world. The two-bodies arrangement has its
replacement mechanism.

### The recipe, the whole stack that run 12 shipped

Relative to vanilla-copying, every one of these was necessary to reach here,
and the last two were the final fix:

1. ONE name for the community; its id is FNV1a64 of that name minus '#'
   (gotcha 62), the name registered in the sector's `nodeRefs`.
2. The registry node in an AlwaysLoaded sector: level 1, +-99999 box, unnamed
   uint64 instance, ranges 17.32 / 1e8, uk10 32, uk11 512.
3. The community area node (`_Streamable`) WITH its AI spots in their own
   AlwaysLoaded level-1 sector, small local box, grid cell 0.
4. Every ref rooted **`$/mod/<sector>/#<name>`**, not `$/03_night_city/`.
5. **`appearances` NON-EMPTY** on every phase. `default` works for a record
   that inherits one.
6. **ONE time period** per phase, e.g. `Day`, one spot per entry.

Points 5 and 6 were the run-12 change; 3 and 4 were run 11's. Which of the
four is individually load-bearing is unisolated and OPTIONAL to isolate: the
stack is cheap to ship whole, and it is what the working mod ships.

Not required, measured across the runs: a quest phase (spawns unarmed), the
`$/03_night_city` root, Exterior spot sectors, the five-period construction,
crowd registries, spawn-set tables. Conflict with a second community mod: none,
ours spawned with Personal Mechanics installed and its Miguel standing in
Kabuki in the same session.

### What is still open, small and cheap

- `miguel_b` off after arming: the bench phase's Reactivate plus
  entry-Activate deactivates unnamed entries. Understand before using the
  nodes in a gig.
- Which of the four stack layers is individually necessary, if anyone cares.
- The payoff: 27's route A, Hoshino as ONE body from a community, with the
  scene acquiring him. That is the next build.

---

## 29-ADDENDUM-7, 2026-08-24. RUN 13 IS BUILT: the scene half of route A

Run 12 answered "can a community this mod ships stand our own character in the
world". Run 13 asks the other half, and it is the payoff of the whole line:
**can a SCENE take that body instead of spawning its own?** Built and deployed,
not yet played.

### How a scene finds a community, read rather than guessed

`spawnSetNameToCommunityID` in vanilla's registry node holds 329 rows, each one
a `CName` written WITH its '#' against a community id. The join a `spawnSet`
actor walks is:

```
scnActorDef.spawnSetParams.reference  ->  a nameReference in that table
-> communityId  ->  the community  ->  the entry named by entryName
```

`#mama_welles` maps to 5541929579920624075, and no NodeRef anywhere in the three
always-loaded sectors hashes to it, so her community's area node lives in the El
Coyote bar's own sector. The id is therefore the ordinary FNV1a64 of a community
node's long ref (gotcha 62 again) and this table exists to turn a short readable
name into it. Registering a name of ours in a registry node of ours is all a
scene should need.

Which SPELLING the scene must carry is not established, and it is the one thing
the two sources disagree on. Vanilla's 329 names are short; a short form is
exactly what a mod's own node names do not resolve under (gotcha 34). So the
bench registers two names for one community and gives each bench scene one of
them. Two names, two community entries, two bodies, one session.

### What run 13 ships

Community B, unchanged in every part gotcha 66 lists, plus:

- a third entry `talk_b`, a second `Character.cc_g01_hoshino` at slot 11
- `spawnSetNameToCommunityID` carrying `#cc_g01_cl_community_b` and
  `$/mod/cc_g01_commlab_b/#cc_g01_cl_community_b`, both against B's id. **This
  is the one deviation from the shape that worked**, so slots 9 and 10 are now
  a regression check as well as a control: read them before reading anything
  about the scenes.
- an AI spot at slot 12 that no community owns, for the workspot question below

Three bench scenes, three buttons off the armed quest phase, parallel rather
than chained so a scene that stalls costs only its own reading:

| button | scene | what it asks |
|---|---|---|
| PLAY 1 | `gig01_cl_short` | a `spawnSet` actor, entry `ours_b`, reference SHORT |
| PLAY 2 | `gig01_cl_long` | a `spawnSet` actor, entry `talk_b`, reference LONG |
| PLAY 3 | `gig01_cl_ws` | an ordinary spawned actor put into our own AI spot node, which is item 30 and is independent of the other two |

Nothing is spawned by the first two: `specRecordId` is 0 on a `spawnSet` actor,
so the body is found or the scene has no speaker at all.

Every line points at a RECORDED VANILLA stringId, so no subtitle resource is
written and no `.archive.xl` line changes. ArchiveXL takes one subtitle file per
locale and the gig already uses it. The text on screen is Nix's "How's things,
V?" coming out of Hoshino, which is the point: **a subtitle names its speaker**,
so a line that appears at all is a line whose actor was acquired.

### The reading, and it is one row against one slot

`cc_g01_cl_near` counts bodies within 5 m of the player that are NOT standing in
a bench slot. That exclusion is what makes it independent of where the player
parks, and it is the only row on the panel that separates the two cases route A
exists to separate:

| slot 9 | unaccounted bodies | meaning |
|---|---|---|
| 1 | 0 | **HE WAS TAKEN. One body. This is the answer** |
| 1 | 1 | a second body was spawned beside the player: today's arrangement |
| 0 | 1 | taken AND moved, which is still one body and still a result |
| 1 | 0, and `cc_g01_cl_sc1` stuck at 1 | the scene entered and never came out, which is what an actor that cannot be acquired looks like from outside |

### The protocol

Load a pre-gig save.

1. `TELEPORT: the community lab line`, then `ARM the quest phase`. Wait for the
   step to read 99.
2. `TELEPORT: between the run-13 spots`. Slots 9 to 12 are within 10 m. **Check
   slots 9, 10 and 11 first**: the spawn-set table is new and 9 and 10 spawning
   is what says it did no harm.
3. `WATCH: on`.
4. `PLAY 1`. Watch slot 9. Read the panel.
5. `PLAY 2`. Watch slot 11.
6. `PLAY 3`. Watch slot 12: a body should appear there on the first line, or on
   the second, or never. Which of the two says which spelling of a mod's own
   node name a quest workspot node resolves.
7. `REPORT to the log`, quit so CET flushes.

Each button fires once per save load, like everything else in this phase.

### RUN 16: the combination is clean too. EVERYTHING THE GIG NEEDS IS NOW PROVED

2026-08-24, 22:40. `ARM -> QUEST OFF -> QUEST ON -> PLAY 1 -> REPORT`, nothing
else touched:

```
quest control OFF ours_b   1        ON ours_b   1
entry 9 across scene 1: before 1  after 1
entry 9  ours_b  bodies 1  alive 1
```

and a panel shot taken between the two presses catches the half-way state:
entry 9 at `0 bodies, 0 alive` with 10 and 11 still at 1, which is `Deactivate`
doing exactly one thing.

So an entry switched off, switched back on, and then acquired by a scene is
still standing and still alive afterwards. **Run 14's vanishing body does not
reproduce**, and the suspect named in run 15 is cleared.

### What is left of run 14's anomaly, and why it is not being chased

Run 14's order was OFF, ON, shoot slot 11, PLAY 1, PLAY 2, PLAY 3, REPORT. Runs
15 and 16 have now cleared the scene on its own and the toggle-plus-scene
combination. What remains unexplained is some part of: killing a DIFFERENT
community member while the others stand around, or the two extra scenes, one of
which acquires an actor that was dead by then.

**The gig does none of that.** It has one community entry, and the only person
shot is that same one. Chasing this would cost a test session on a case gig 01
cannot reach. Logged here so it is a decision rather than an oversight; if a
later gig has two community NPCs and shoots one, start from run 14.

### The four things a gig needs, and where each was measured

| what the gig needs | proved by |
|---|---|
| he appears when the story wants him | run 14, `Activate` on one entry |
| he is not there before, and can be removed after | run 14, `Deactivate`, and it leaves the other entries alone |
| he survives the conversation that speaks through him | runs 15 and 16, before 1 / after 1 |
| he can be shot and killed, and the body stays | run 14, entry 11 at `bodies 1, alive 0` |

Plus, from run 13c: the scene acquires him rather than spawning a double, and a
scene can place an actor in an AI spot node this mod ships.

`entryActiveOnStart: 0` is ignored (run 14), so the gig's phase has to Deactivate
on entry rather than relying on the field. There is a window between save load
and that node running in which he exists; it has not been measured, and it is the
one thing worth checking early in the gig build rather than late.

### RUN 15: the scene gives the body back. It is the quest toggle that does not

2026-08-24, 22:35. One press, PLAY 1, with no quest control touched:

```
entry 9 across scene 1: before 1 after 1
entry 9  ours_b  bodies 1  alive 1
scene 1                  played and exited
quest control ON / OFF / whole      0 / 0 / 0
```

**The acquiring scene returns what it borrowed.** He was there before it, there
after it, and still alive at the report. So the scene half of route A is clean
and nothing about it needs changing.

That leaves the OFF/ON cycle as the cause of run 14's vanishing body, and it
narrows further than that. Run 14's own sequence was OFF, ON, shoot slot 11, then
all three scenes, and the playtest saw slot 9 filled immediately after the ON. So
`Activate` does hand back a body; something later in that run took it away again,
and PLAY 1 on its own now provably does not.

**The remaining suspect is the combination: an entry activated BY A QUEST NODE
and then acquired by a scene.** That is exactly what the gig would do, so it has
to be pinned down before any of this ships.

**It needs no build.** The bench already has the buttons and the latch:

    ARM  ->  QUEST OFF  ->  QUEST ON  ->  PLAY 1  ->  REPORT

`cc_g01_cl_b4` keeps overwriting while scene 1 has not started, so it holds the
count from just after the ON, and `cc_g01_cl_af` is written once at the exit.
"1 before, 0 after" names the combination. "1 before, 1 after" clears it and
moves the suspicion to the shot, which would be a stranger result and a smaller
problem.

### RUN 14 RAN. Quest control works, a community body can be killed, and one new hole

2026-08-24, 22:24. Final report, after OFF, then ON, then shooting slot 11, then
all three scenes:

```
entry 9  ours_b  (ships OFF at start)  bodies 0  alive 0
entry 10 miguel_b (ships on)           bodies 1  alive 1
entry 11 talk_b  (ships on)            bodies 1  alive 0
quest control ON  ours_b   1
quest control OFF ours_b   1
workspot short 1  long 1
scene 1 / 2 / 3            all "played and exited"
probes                     4 / 4 / 4 / 3
```

**1. `entryActiveOnStart: 0` IS IGNORED.** Slot 9 held a live body on a fresh
load with the entry shipped off. Whatever that field governs, it is not whether
a mod's community spawns the entry. The wiki calls it "only of interest for
quest modding", which is exactly the case it fails in.

**2. `Deactivate` on one entry WORKS, and it does not touch the others.**
Playtest: *"9 is now 0, the 10/11 stay 1"*. That is the answer to the question
run 12 raised by accident, and it is the good one: a per-entry action addresses
that entry alone, so a gig's NPC does not switch off the rest of its own cast.
Whatever run 12 saw was not this.

**3. `Activate` on one entry WORKS.** *"9 is now 1"*. So the pair is a switch, and
that is the shape a gig needs: ship the community, deactivate at quest start,
activate at the beat.

**4. A COMMUNITY BODY CAN BE SHOT AND KILLED.** Entry 11 after the shot: `bodies
1, alive 0`. The story requires it and nothing had ever tested it.

Note what would have happened without the per-entry probe: the positional count
for slot 11 reads **0** in the same report, because a dead NPC drops out of the
targeting query the slot counts use. Counting bodies would have said "he
vanished". The spawner still holds him and `ScriptedPuppet.IsAlive` says he is
dead. Gotcha 64's limit cuts the other way here, and this is the instrument that
gets past it.

**5. Both workspot spellings work.** `workspot short 1 long 1`, from the two
"Work Started" breadcrumbs. The footnote from run 13c closes: a mod's own AI spot
node can be addressed either way.

### The new hole, and it is on the critical path

**Entry 9 has NO BODY at the end of the run**, after being activated by the quest
node and then used by scene 1. In run 13c the body survived its scene: slot 9
read 1 with scene 1 at "played and exited". The difference is that this time he
had been through a Deactivate/Activate cycle first.

So one of two things removes him, and this run cannot separate them:

- the acquiring scene releases or despawns the body when it ends, and 13c only
  looked healthy because the entry had never been toggled
- an entry activated BY A QUEST NODE holds its body differently from one that was
  active at start

**It matters more than any of the four results above**, because the gig's beat is
talk to Hoshino and then shoot him. A Hoshino who evaporates when the
conversation ends is not shootable.

Cheap to settle and it does not need anyone to watch: the bench now latches entry
9's body count when scene 1 is entered and again when it exits, into
`cc_g01_cl_b4` and `cc_g01_cl_af`. Two numbers on the panel, and the run says
which of the two causes it is.

### RUN 14, BUILT: quest control, which is what actually blocks the gig

Run 13c proved a scene takes a community body. It did not make gig 01 possible,
because of what run 12 established and nobody had followed through: **a mod's
community spawns on save load with no quest node.** For a bench that was the
result. For a shipped gig it means Hoshino standing at the North Oak estate from
the moment a player installs the mod, before Elena has called, and again after
he is dead.

Community state also persists in saves, so getting this wrong in a release is
not a patch, it is something stuck in people's saves.

So `ours_b` now ships `entryActiveOnStart: 0` and run 14 asks three things:

| button | asks |
|---|---|
| `QUEST: switch ours_b ON` | can an entry held off at start be switched on when the story wants it |
| `QUEST: switch ours_b OFF again` | and off afterwards, which the kill beat needs |
| `QUEST: activate the WHOLE community` | what runs 1 to 13 did, kept as the control |

`miguel_b` and `talk_b` ship ON, and they are the DETECTOR for the other half:
run 12 saw a per-entry Activate switch the UNNAMED entries off, by accident and
never explained. If activating `ours_b` alone empties 10 and 11, that is a gig
whose NPC turns off the rest of its own cast, and it has to be understood before
any of this ships.

### The instrument changed too, and it is a better one

`GetGameObjectsFromSpawnerEntityID` takes an ARRAY OF ENTRY NAMES, so it answers
for ONE entry rather than for the whole community. That is better than counting
bodies at a position for both of run 14's questions:

- **is this entry spawned right now**, which is the quest-control question and
  does not care where the body is standing
- **is that body alive**, via `ScriptedPuppet.IsAlive` on what the spawner hands
  back. A dead NPC may drop out of the targeting query the slot counts use, so a
  slot going to 0 after a shot is ambiguous and this is not.

The second one answers a question the gig's story requires and nothing has ever
tested: **can a community body be shot?** Hoshino has to die at the end of that
beat. Shoot slot 10 or 11 and the panel says whether the spawner still has him
and whether he is alive.

Not on this bench, deliberately: **lipsync.** Testing it here would mean giving a
bench line its own recording and lipmap entry, and the lipmap is one file per
locale that the shipped generator owns, so a bench that wanted one would have to
edit shipped code. The real Hoshino's lines are recorded and already have
lipsync casting, so an acquired body's mouth is a gig-build question. It is the
one thing run 14 knowingly leaves open.

### RUN 13c: IT WORKS. A SCENE TAKES A COMMUNITY BODY, AND A MOD'S OWN AI SPOT HOLDS A SCENE ACTOR

2026-08-24, 21:40. Both questions answered yes in one session. The panel caught
mid-run, with scene 3 still playing, is the whole result:

```
0 CAL   script-spawn                          1
9 B ours_b   HOSHINO, short-name scene        1
10 B miguel_b Personal Mechanics              1
11 B talk_b   HOSHINO, long-name scene        1
12 WS  spot no community owns                 1     <- OUR AI SPOT, OCCUPIED
1 our exterior sector          4 LIVE
2 our always-loaded sector     4 LIVE
3 CTL base-game, MUST be LIVE  4 LIVE
4 CTL never shipped, expect 3  3
distance from the stand point: 0.8 m
unaccounted bodies within 5 m of you: 0
scene 1 SHORT name, takes slot 9    played and exited
scene 2 LONG name,  takes slot 11   played and exited
scene 3 workspot,   into slot 12    ENTERED, no exit yet
```

All four controls correct. All three scenes ran. **All three spoke** (playtest,
2026-08-24).

#### 1. A scene acquires a body a mod's community placed. 27 route A passes

Slots 9 and 11 still hold their bodies AFTER their scenes played and exited, and
`unaccounted bodies` never left 0. A `spawnSet` actor carries `specRecordId` 0,
so nothing can be spawned: the scene either finds the body or has no speaker at
all. Both scenes had one.

**The subtitle is the proof, and it is why the lines matter.** These scenes write
`visualStyle: regular`, and 10k measured that a regular line needs a speaker
GameObject the subtitle system can reach or the line is resolved and then dropped
on the floor. A line that appeared is a line whose actor was acquired.

**Both spellings work**, which settles the question the two names were registered
to answer: scene 1 asks for `#cc_g01_cl_community_b` and scene 2 for
`$/mod/cc_g01_commlab_b/#cc_g01_cl_community_b`, both are rows in
`spawnSetNameToCommunityID`, and both spoke. So the match is on the string as
registered, and a mod may use whichever form it likes provided the same string is
in the table. This is not the NodeRef resolution of gotcha 34 and does not
contradict it.

#### 2. A scene CAN put its actor into an AI spot node the mod ships. Item 30 passes

Slot 12 reads 1 while scene 3 is running, and it is the instrument rather than an
eyewitness that proves the move: scene 3 spawns its actor 2 m in front of the
player, so a workspot node that did nothing would leave him there and
`unaccounted bodies within 5 m` would read 1. It reads 0 while slot 12, nine
metres away, reads 1. He was moved into
`$/mod/cc_g01_commlab_b/#cc_g01_cl_spot_ws` by `questUseWorkspotParamsV1`.

Slot 12 is back to 0 in the report fourteen seconds later, with scene 3 at
"played and exited". That is correct: a `spawnDespawn` actor is removed when its
scene ends, so this reading only exists while the scene runs.

**`questkit/scene.py`'s `add_workspot_node()` docstring was wrong.** It said
`questUseWorkspotParamsV1` points at a node in a streaming sector and is
"unusable: a mod's own world nodes do not resolve". Californication was the
evidence against it; this is the measurement.

WHICH SPELLING moved him is NOT established. Scene 3 fires the same spot twice,
short form on its first line and long on its second, and at the time the panel
could not say which one landed: catching it meant watching a two-second event
while reading a panel, and it was missed, which is a fair thing to ask of an
instrument rather than of a person.

**The bench now answers it by itself.** `questUseWorkspotNodeDefinition`
declares a "Work Started" output, so each of the two nodes hangs a fact off its
own: `cc_g01_cl_ws_short` and `cc_g01_cl_ws_long`, both on the panel and in the
log. Nothing needs re-running for its own sake; the answer arrives free with
whatever the bench is next used for. It matters only for style, since one of
them works and the node can be addressed either way in a gig.

#### What this does not yet say

The counts prove a body was acquired and not duplicated. They say nothing about
whether the scene took OWNERSHIP well enough for gig use: whether he turns to
face the player, whether lipsync drives his mouth, whether his community
behaviour stops while the scene owns him, and whether he can still be shot
afterwards. Those are gig01's questions and they need eyes, not counters.

### RUN 13a, the same night: THE BENCH WAS IN THE AIR, and it always had been

First look at run 13 in game, and it did not get as far as pressing a button.
Three NPCs and both residency sprinklers were hanging in the sky over the
estate. The panel meanwhile read exactly what it was supposed to: B bodies 2,
names resolve, step 99, slot 9 = 1, slot 11 = 1.

**The sprinklers have not changed since run 6**, which dates the fault: every
run of this bench from the sixth on has placed things past the end of the
terrace, and no run could see it.

Surveyed afterwards against the game's own node placements in the cached
exterior sectors, median z of everything within 4 m:

```
x        332    340    348    356    364    372    380
y 1042  225.9  225.9  225.9  223.1  221.4  224.0      .
y 1034  225.9  225.9  225.9      .  221.3      .      .
y 1026  226.0  226.0  227.0  214.6      .      .      .
```

`.` is no vanilla node within 4 m in any cached sector. The garden is x 328 to
352 at z 225.9. The bench line ran from x 340 to x 380 at that same z, so slots
7 to 12 were over a drop, and slot 4, the negative control, is just past the
edge as well.

**Why no probe caught it**, and this is the lesson rather than the bug: the scan
counts a body within 2 m of its slot, and a body 20 m up is 0 m from a slot that
is also 20 m up. Both numbers came from one wrong constant, so they agreed with
each other perfectly. That is the same shape as the empty `appearances` that
survived eleven runs. `gotchas.md` 67.

Slots 7 to 12 are now a second row on the surveyed terrace, y 1027.924, x
332.924 to 348.924, and the watching teleport lands in front of them instead of
26 m past the end of the garden. Community A's slots 0 to 3 were always on it
and did not move.

**Run 12's result is unaffected.** The community did spawn our own character
from a mod-shipped registry node; it spawned him in mid-air, which is a
placement fault and not a community one. Nothing in `gotchas.md` 66 changes.

What the run did NOT establish, because no button was pressed before the fault
was spotted: anything at all about scene acquisition.

### What run 13 DID bank, from the report CET flushed on quit

The bench was in the air, but its readings were still good, and one of them is
the check this run most needed. `negative_balance_dev.log`, 20:57:08:

```
commlab A 0/1  B 3/1  step 99
commlab  9 B ours_b   HOSHINO, short-name scene  1
commlab 10 B miguel_b Personal Mechanics         1
commlab 11 B talk_b   HOSHINO, long-name scene   1
commlab 12 WS  spot no community owns            0
commlab bodies with the player                   0
commlab probe 1 our exterior sector          4
commlab probe 2 our always-loaded sector     4
commlab probe 3 CTL base-game, MUST be LIVE  4
commlab probe 4 CTL never shipped, expect 3  3
```

- **THREE entries, three bodies.** Adding `spawnSetNameToCommunityID` to the
  registry node did not break the spawn, which was the one deviation from the
  shape gotcha 66 proved. `GetGameObjectsFromSpawnerEntityID` returned 3.
- **A third entry works**, so the community is not limited to what run 12
  happened to ship.
- Slot 12 reads 0, which is right: nothing is shipped into it and only a scene
  can put anyone there.
- All four probes correct, so the instrument was sound. It was the shared height
  that was wrong, not the readings.
- **The count is time-dependent.** A panel shot at 20:56:15 read slot 10 as 0 and
  B bodies 2; forty seconds later both were full. Give it a moment before
  reading, or a late entry looks like a dead one.

All three scenes read 0, so nothing whatever was established about acquisition.

### RUN 13b: the PLAY buttons were dead, and one body stood in a wall

Second look in game. Two bodies on the lawn, one inside a wall, and nothing
spoke. The panel read step 99 with all three scenes at "not played", which reads
exactly like a tester who did not press the buttons. He did.

**A quest phase's output node is `type: Terminating`, and reaching it takes the
phase's armed pause nodes with it.** Run 13 hung the three scene waits off the
same socket that fed the output, so the phase ended the instant the arming chain
finished and all three buttons were dead before anyone touched one. The graph
made it plain once it was dumped:

```
STEP-99 node 29  Out -> 4 connections
   -> In on 30 Output          <- Terminating. This ends the phase.
   -> In on 31 PauseCondition cc_g01_cl_play1
   -> In on 35 PauseCondition cc_g01_cl_play2
   -> In on 39 PauseCondition cc_g01_cl_play3
```

A bench phase has no reason to terminate at all; its job is to sit there holding
armed waits. The output node stays so the resource keeps its `Out1` socket, and
nothing reaches it.

**The placement was wrong a second time, in the opposite direction.** 13a asked
"is there ground here" and moved everything onto the terrace. It never asked "is
there anything solid here", so one body ended up inside a wall. The survey now
reads the game's own node DEBUG NAMES and separates them:

- soft: `lawn_squ_*`, `lawn_rec_*`, `distr_water_sprinkler_*`, `light_*`,
  `spotlight_*`. Open garden, and their z is the ground.
- hard: `hedge_*`, `*_pillar_*`, `*_wall_*`, `*_floor_*`, `*walkway*`,
  `cargo_crate_*`, `coverObject_*`, `*planter*`, `*_apartment_*`, `*_office_*`.

A point qualifies with no hard node within 3 m and open garden within 4 m. The
six spots now carry their own surveyed z rather than one shared constant. It is
still evidence and not proof: a mesh's node position is its ORIGIN, so a 6 m wall
is one point and this test can be fooled. The dev menu's CAPTURE HERE settles it
in one press, and the panel now says so.

**What the survey turned up unasked: community A's slots 2 and 3 are inside the
house** (`int_nkt_jp_apartment_a_pillar_*`, `int_mlt_office_floor_*`, z 228.4)
and slot 4 is over the drop. A has never spawned anybody in twelve runs and
three of its five spots were never viable, so those runs say less about A than
they appear to.

Also added: the generator now compares its slot table against the redscript
scan's copy and refuses to write if they differ by more than 2 mm. Two tables,
one truth, and a scan measuring against a different point than the one a body
was placed at is a bench that lies. Proved to bite by injecting a 1 m drift.

### Two things this run is knowingly gambling on

- **The new positions are surveyed, not captured.** They come from the game's
  own node placements rather than from a position the player has stood on, so
  they are much better evidence than run 13's first attempt and still not proof.
  If the bodies are on the ground but sunk or floating by a metre, that is what
  the dev menu's position capture is for.
- **Personal Mechanics is still installed and `miguel_b` still uses its
  `Character.miguel`.** Removing that mod means removing the entry first.

---

## 30. Reusing a VANILLA community, and a mod-owned workspot node. 2026-08-24

Asked after 29 closed: can we test the Californication framework, and would
reusing one of the game's communities break it?

### Would it break the community? YES, and persistently. But we do not need it

`#judy` is ONE community with ONE entry, `entryActiveOnStart` 0, and **129
phases**: `default`, `q004_02_judy_at_the_bar`, `q105_judys_bed`,
`sq026_08_judys_kitchen`, `sq030_09_hut_pier_sit` and so on, one per story beat.
`#judy_vehicle` is the same shape with 15 phases for her van.

**That is how the base game moves a story character around**, so activating an
entry or setting a phase MOVES THAT CHARACTER, and community state is saved. Get
it wrong and Judy stands somewhere for the rest of the save, or appears before
her quest wants her.

Californication mitigates it the careful way: it picks `dlc3_judy_sleep`, a
phase that exists in her list and that the base game's own quests do not appear
to drive. That is the pattern if it is ever done: **a phase vanilla never
activates**, and never one named for a quest.

**But this project does not want that half at all.** `characterRecordId` lives
in the vanilla registry entry, which a mod cannot edit, so reusing `#judy` gives
you Judy. For Hoshino we need our own record, so the community half is both
risky and useless here.

### The half that matters, and a fourth stale claim

Californication's scene puts its actor into **a workspot node the MOD ships**:

```
questUseWorkspotParamsV1
  function        UseWorkspot
  instant         1     jumpToEntry 1    teleport 1
  changeWorkspot  1     enableIdleMode 1  isWorkspotInfinite 1
  workspotNode    #nq_cali_ws_judy_sit        <- ITS OWN AI SPOT NODE
```

The node is `worldAISpotNode` in Californication's own `category: Quest` sector,
named long-form and referenced SHORT here.

**`questkit/scene.py`'s `add_workspot_node()` says this is impossible.** Its
docstring reads: *"questUseWorkspotParamsV1 points at a `workspotNode` NodeRef
in a streaming sector. Unusable - a mod's own world nodes do not resolve."* That
is the same stale claim as gotchas 2 and 35 and `find_pin_anchors.py`, written
before 34, 39 and 61, and **a shipped mod disproves it**.

This project therefore uses `scnUseSceneWorkspotParamsV1` with
`playAtActorLocation: 1`, which plays the workspot wherever the actor happens to
have spawned. That is why a playtest reported Hoshino *"half-way in a pillar"*.

### What is worth testing, and it touches nothing vanilla

**Can a scene put its own actor into an AI spot node this mod ships?** A
mod-owned spot, our own character, our own scene. No vanilla community, no
persistent change to anything of the game's, no risk.

If it works it does not remove the second body, and that should not be oversold:
27's route A still needs a persistent one. What it does fix is WHERE the scene
body stands and what pose it holds, which is a real reported bug and which every
gig from 02 on inherits.

**CLOSED 2026-08-24, and the answer is YES.** Run 13c: a scene spawned its actor
2 m in front of the player, `questUseWorkspotParamsV1` with `workspotNode`
naming our own spot moved him nine metres into it, and the bench read slot 12 at
1 with nothing left beside the player. 29-ADDENDUM-7 has the readings and
`gotchas.md` 69 the recipe.

`questkit/scene.py` now carries `Scene.add_world_workspot_node()` and its
`add_workspot_node()` docstring no longer claims a mod's own world nodes cannot
be used. Both shapes are valid and the choice is what the beat needs: the scene
instance holds the pose where the actor already stands, the world node puts him
somewhere specific.

WHICH SPELLING landed is not established: the bench fires the same spot twice,
short then long, and the counter cannot say which one moved him. It matters only
for style.

---

## 31. THE GUARDS, by community. Asked 2026-08-24, BUILT AND SHIPPED 2026-08-25

**Read the close at the end of this item first.** What follows it is the working
in order, including two features that were built, measured and taken back out.
Two of the sections below are written in the present tense about things that no
longer exist, and both are marked.

Hoshino is one body now, placed by a community this mod ships. The obvious next
question is whether the compound and estate guards should be too, and this
project's own notes already argue that they should.

### Why it is more than tidiness

The guards are placed by `Gig01_Encounter` through `DynamicEntitySystem`, and 17
recorded what that costs:

> an entity created through `DynamicEntitySystem` arrives without the senses,
> role and security area a community-placed guard gets for free

**A community-placed guard gets that for free.** If that is true, converting
them would fix the two things 17 accepted as-is and blamed on placement:

- **the huddle.** Three of five office squads stand within 15 m of each other
  because a navmesh query puts them there. A community places each entry at an
  authored spot, with a facing, which is what a post is.
- **the warning phase.** There is none, because there is no security area: no
  "you shouldn't be here", no call-out, no walk over to look, just a meter
  filling. That was called the same wall as the community question, and it is
  not any more: what blocked communities was whether the game reads authored
  world data a mod ships, and the answer is yes (`gotchas.md` 66 and 69).

That is not a measurement. A security area is a different system from a
community and nothing here has shipped one. What HAS changed is that the reason
it was called impossible no longer holds.

### BUILT 2026-08-25, not yet played

One entry, `guard_test`, in Hoshino's own community:
`Character.arasaka_guard2_melee1_baton_wa` at (298.251, 1021.907, 224.952) with
yaw -120.89. That is a VANILLA workspot position at this estate, one of the two
`q113_ws_arasaka_estate_investigation_*` spots read out of `exterior_4_15_3_0`
and referenced by no community, so the ground, the facing and the sightlines are
the game's own rather than anything inferred. The record is one of the three the
encounter already spawns, so nothing about him is ours except where he stands.

The quest phase switches him with Hoshino, as a SECOND per-entry action rather
than one action on the whole community: a per-entry action leaves the others
alone (run 14) and the gig should not learn a habit that only works while it
owns every entry.

`cc_g01_dbg_guard` reports 0 not there, 1 standing, 2 dead, on the dev panel and
in the log, with a teleport to his post. **That row only says he EXISTS.**
Whether he BEHAVES is the question, and no counter can answer it: walk up to
him, then to a script-spawned one a short distance away, and see whether either
challenges, looks, or reacts.

`GUARD_TEST = True` in `gen_community.py` is the switch, and it must be False
before any release.

### THE SECURITY AREA IS AUTHORABLE, and the wiki documents it. 2026-08-25

The claim this item inherited was that a security area "is authored into the
level around the guards, not set on a character we spawn", and that it was the
same wall as the community question. **The wiki has a page on building one**:
`modding-guides/world-editing/devices/creating-security-areas`. Two device
entities and a connection:

| | |
|---|---|
| the system | `base\gameplay\devices\security_systems\security_system.ent`, spawned as a Device, unique NodeRef |
| the area | `base\gameplay\devices\security_systems\security_area\security_area_1.ent`, unique NodeRef, and **no rotation at all**: roll, pitch and yaw must be 0 |
| its shape | `Entity Instance Data -> area -> outline`, copied from a Dummy Area's outline |
| its type | `controller -> persistentState -> securityAreaType`, default Hostile |
| the link to the area | device connection, class `SecurityAreaControllerPS`, pointing at the system |
| **the link to OUR NPCs** | device connection on the security area, class **`CommunityProxyPS`**, pointing at the COMMUNITY's NodeRef |

and the constraint: the community, the security area and the security system
must all be in the same group.

`CommunityProxyPS` is the piece that matters here. It is described as the link
to add "when your security area should alert NPCs in your custom community" -
which is exactly the shape this project now has: a community it ships, with its
own NodeRef, and no alerting attached to it.

**What the wiki does NOT say** is whether a security area is REQUIRED for a
community NPC to notice the player at all. Asked directly, it answers that the
behaviour of a community with no linked security area is undocumented. So this
is a documented route to the warning phase, not yet an explanation of why the
bench guards are inert.

### What the guard bench has actually shown, and what it has not

Playtest 2026-08-25, and the first two readings were not about guards at all:

- **"Provoke does nothing"** and **"none of the 3 guards do anything"** were the
  same fault, and it was mine. Every lab watcher and the whole Hoshino tick
  block sit inside `if accepted && ...`, which is "the player has taken this
  job". The
  lab exists to run with NO GIG RUNNING, so none of it ever executed. The
  comment fifteen lines above that gate states the rule it broke: a diagnostic
  must not be gated on anything downstream of what it measures (`gotchas.md`
  17). Hoshino still appeared and spoke because the community places him and the
  scene acquires him; neither needs the script.
- So **the earlier "he saw me and challenged me" reading is now doubtful too**.
  It was taken at the estate with the gig NOT accepted, so our script was not
  running then either, and the estate carries vanilla NPCs. It may have been one
  of theirs.

The lab now runs outside that gate and reports Hoshino's find code and whether
the provoke actually applied, so the next run says which of those it is.

### THE GUARD QUESTION IS ANSWERED, 2026-08-25, and the answer is the ATTITUDE

Three variants, one post, one at a time, with no gig running so the estate is
empty of the encounter's own guards:

| | | |
|---|---|---|
| guard 1 | `arasaka_guard2_melee1_baton_wa`, record default | stands there |
| guard 2 | the SAME record, `CCSharedAttitude.Hostile` applied when found | **works** |
| guard 3 | `sts_std_arr_12_security_guard1_ranged1_nue_ma`, record default | stands there |

1 and 3 differ only in which vanilla record they use, and both are inert. 2 is 1
plus one line of script. **So it is the attitude, and the record decides
nothing.**

And what "works" looks like, playtest: *"if I approach the meter fills a bit,
slowly as I approach then faster until they become aggressive and switches to
combat"*. That is the ordinary base-game detection ramp, at base-game rates: a
community-placed guard perceives exactly like one of the game's own.

It also confirms from the other end what was written up in August:
`senseComponent.ShouldStartDetectingPlayer` treats a hostile attitude as "start
filling the meter". No attitude, no meter, no reaction, which is precisely what
guards 1 and 3 do.

### The trespass warning is a DIFFERENT system, and it is not missing by accident

The thing this item was really after ("you shouldn't be here", the call-out, the
walk over, and only then a fight) does not come from the community and never
would have. It happens to somebody who is **not** an enemy yet, and being an
enemy is exactly what makes guard 2 work. The two are alternatives:

- hostile attitude -> detection ramp -> combat. An ENEMY being spotted.
- security area -> trespass warning. A STRANGER being told to leave.

So the security area above is a real feature to build if the compound should
feel like somewhere V is trespassing, and it is not needed to make guards fight.

### What this means for converting the gig's guards

Less than it looked. The guards were never short of senses; what a
`DynamicEntitySystem` NPC was short of is a reliably applied attitude, and
`CCShared_Attitude.reds` could not see a community body at all until 2026-08-25
(gotcha 71), which is a bug in the same area that was fixed the same day.

**Check whether the existing script-spawned guards behave before converting
twenty of them.** If they do, this item is a feel question about posts and
facing rather than a behaviour one.

### THE BLOCKER IS POSITIONS, AND THEY DO NOT EXIST. Measured 2026-08-25

Converting the guards is not mechanical work waiting to be done. It is blocked
on something nobody has authored.

Searched the cached sectors for `worldAISpotNode` within 120 m of
`CCGig01Places.OfficeGuardPost()` (-245.680, -1452.315, 14.600): **five spots,
all 53 to 87 m away, all belonging to q112's infiltration setup.** The compound
has no authored guard posts at all.

**That is also the huddle's cause, stated properly.** The encounter asks the
navmesh for "somewhere near this anchor" and the navmesh obliges with nearly the
same answer each time, because there is nothing else to go on. Three of five
office squads landing within 15 m of each other is not a bug in the query; it is
what happens when a query stands in for a level designer.

So a community conversion needs roughly twenty decisions about WHERE A GUARD
SHOULD STAND (sightlines, cover, who watches the gate, who watches the yard)
and a survey for flat walkable ground cannot make them. It would produce twenty
men in a grid.

**The route is a capture pass.** Walk the compound, stand where each guard
belongs, face the way he should face, and press CAPTURE HERE with a name. The
dev menu already writes `name = { x, y, z, yaw }` to
`captured_positions.txt`, and the conversion after that IS mechanical: one
community entry per captured post, exactly the shape Hoshino already uses.

### The shape of it, and why it is not the next build

**Test ONE guard first.** One community entry beside Hoshino's, at an authored
post, and then stand in front of him: does he challenge, does he look, does he
react differently from the spawned ones two metres away. That is a small build
against a bench that already exists, and it answers the whole question before
anything is committed to.

Converting all of them is a much bigger thing than Hoshino was:

- Hoshino is ONE entry. The compound and estate run to twenty-odd, each needing
  a captured position and facing.
- Every one of them puts community state in players' saves.
- The quest phase has to switch them the way it switches Hoshino, and the
  window that does not matter for one man at an empty estate may matter for a
  compound the player drives past.
- `securityAreaType` on a character record is discarded by 2.31 (13), so
  whatever produces the warning phase is not that field.

### What run 14 already says about it

A per-entry `Activate`/`Deactivate` addresses that entry alone and leaves the
others untouched, measured. So a squad can be a community with one entry per
guard and be switched as a group or one at a time, which is the shape this
would need.

### THE POSTS EXIST, AND THE ESTATE IS CONVERTED. 2026-08-25, not yet played

The capture pass happened. Thirty-five points were walked at the North Oak
residence and thirty are in use: five were dropped on the tester's own
instruction, four of them superseded by a later pass over the same ground and
one sitting 2.7 m from the couch Hoshino waits on.

They cover ground the old spawn could not reach at all. Two of them are on the
ROOF, which a navmesh query around a ground anchor never produces.

| where | posts |
|---|---|
| the front gate, outside | 3 |
| just inside the gate | 3 |
| the grounds and the drive | 8 |
| the terrace, 225 m | 6 |
| the first floor, 229.9 m | 4 |
| the roof, 233.9 m | 2 |
| the office end, 224.9 m | 4 |

`tools/gig01/gen_estate_guards.py` ships them as `cc_g01_estate`, a SECOND
community, built by `questkit/community.py` which is gotcha 66 lifted out of
`gen_community.py` unchanged. Hoshino's two sectors are byte-identical after
that lift, which is the check that says the shared recipe did not disturb the
community that already worked.

**Its own community rather than thirty more entries in Hoshino's**, for two
reasons. A whole-community quest action switches all thirty in one node, where
naming entries one at a time would be thirty nodes at each of three beats and
one node carrying thirty actions is a shape nothing here has read off a working
example. And the security area below links to ONE community, which must not be
the one holding the man V is there to talk to.

**They stand with their arms crossed, not browsing a shelf.** The idle Hoshino
used before he sat down is `generic__stand_ground__look_at_products__03`, a shop
browser: fine for one man waiting on a terrace, wrong for thirty armed guards.
`generic__stand_ground_arms_crossed__stand_around__02` is on the same
`common\ground\` shelf, which is the part gotcha 72 found to matter, and it is
one of the 64 workspots the cached sectors attach to their own AI spots. If the
pose does not take at all the loss is small, because a community places the body
and does not reliably pose it: a guard who is merely standing is still at his
post facing the right way.

The records are the same five the encounter has always used at this site, and
that is deliberate: the estate detail reads as an elite Arasaka detail and the
compound as ordinary security, entirely through which records each uses.
Changing the roster and the placement in one build would leave a playtest unable
to say which of the two it was reacting to.

What went with the spawn chain: the stagger, the retry budget, the per-anchor
mask and the navmesh query. What replaced it is one `ResolveNodeRef` and one
`GetGameObjectsFromSpawnerEntityID`, then `CCSharedAttitude.Hostile` per body,
because a community NPC arrives with no quarrel with the player and an NPC with
no quarrel never starts looking (gotcha 74).

**The thirty entry names are written out twice**, in the generator and in
`Gig01_Encounter.EstateEntries()`, because redscript cannot import Python. The
generator READS the redscript and refuses to write when the two lists differ,
proved to bite by renaming one post. That is the same guard the bench put on its
slot table, and gotcha 73 is why it is worth the trouble: a lookup naming an
entry that does not exist returns fewer bodies and says nothing.

Not played. The dev panel reports it: `detail:` is whether the lookup worked and
`posts turned: N of 30` is how many are hostile. **The count rising as V walks
in is correct rather than a fault**: a post 90 m away has not streamed in yet,
exactly as the old spawn's far anchors had not.

### THE SECURITY AREA, READ OFF SHIPPED DATA. 2026-08-25

The wiki recipe copied into this item above was written from the World Builder
UI. The cached sectors hold working examples, and they settle the shape.

**Eighteen `worldDeviceNode`s in the cached sectors carry a `CommunityProxyPS`
connection.** Nine of them are `security_system.ent` and four are
`security_area_1.ent`, so both placements ship. The commonest single shape, 7 of
the 18, is the SYSTEM carrying both links:

```
worldDeviceNode  {cs_dragnet_sec_system}
  entityTemplate    base\gameplay\devices\security_systems\security_system.ent
  deviceConnections
    CommunityProxyPS            -> the community's NodeRef
    SecurityAreaControllerPS    -> the area's NodeRef
```

and the AREA carries no connections at all:

```
worldDeviceNode  {cs_dragnet_sec_area}
  entityTemplate    base\gameplay\devices\security_systems\security_area\security_area_1.ent
  deviceConnections []
  instanceData -> buffer -> Chunks
    gameStaticTriggerAreaComponent
      includeMask 1, isEnabled 1, identity localTransform
      outline: AreaShapeOutline, height 9.78, SEVEN Vector3 points, all Z 0
    SecurityAreaController
      persistentState: SecurityAreaControllerPS
        securityAreaType  RESTRICTED
        deviceState       ON
```

**This corrects the wiki reading above**, which put the `CommunityProxyPS` link
on the area. It is on the system in twice as many shipped cases, and the pairing
that makes a whole working unit puts both links there.

`securityAreaType` is **RESTRICTED** on this example, not the Hostile the wiki
gives as the default. Restricted is the trespass case: somebody who is not an
enemy being told to leave, which is the behaviour this item is after.

The outline is a polygon in the node's LOCAL space with a height, so the area is
a prism. The points are the estate's walls in our case, and capturing them is the
same walk that produced the posts.

**What is not yet established**, and it is the thing to settle before building:
whether the trigger area, which is an `entEntityInstanceData` RedPackage buffer
inside a `worldDeviceNode`, can be written by this project's generators at all.
Nothing here has emitted an embedded entity instance buffer. The community
sectors write plain nodes. That is the first question, not the last.

**And it ships behind a flag, off.** The estate conversion above is thirty new
bodies in one build; a security area on top of it would mean a playthrough with
two new things in it, and this project has already paid for stacking once.

### THE CAMERAS. Asked 2026-08-25, and both sites already have them

Playtest asked whether the cameras could be part of the detection, at either
site, because they do not react to V now.

**They are there.** The cached sectors carry 26 camera nodes within 140 m of the
compound and 13 within 140 m of the residence.

**They belong to other quests.** Every one of the compound's is
`q112_infiltration_surveillance_camera_*` and every one of the residence's is
`q113_dvc_arasaka_estate_camera_*`. They are not ignoring V by accident: they
are another quest's security network, and that quest controls their state.

The same two quests own security areas at both sites, which is also why the
residence's minimap already reads AREA: HOSTILE while V stands in it.

**How a camera alerts a community, read off shipped data.** One device node
carries both links, and `{ma_hey_gle_09_ap}` in `exterior_-20_-15_0_0` is the
worked example: an `accesspoint.ent` with

```
SurveillanceCameraControllerPS  -> the camera's NodeRef
CommunityProxyPS                -> the community's NodeRef
```

alongside seven other controller classes for the rest of that room's devices. So
a camera is wired to NPCs exactly the way a security area is, through the same
`CommunityProxyPS` link, and this mod now has two communities with their own
NodeRefs for one to point at.

### AND THE BLOCKER ON ALL OF IT IS GONE

The open question above was whether these generators can write an
`entEntityInstanceData` RedPackage buffer, because the security AREA needs one
for its trigger polygon and nothing here has ever emitted one.

**The node that carries the community link does not need a buffer.** Of the 18
device nodes in the cache with a `CommunityProxyPS` connection, three have
`instanceData: null`, and one of them is
`{q112_infiltration_security_system}` in `exterior_-5_-24_0_0`: a plain
`worldDeviceNode` with an entityTemplate and a list of `deviceConnections`, which
is a shape these generators already write for every other node they ship.

So the wiring is cheap. What still needs the buffer is the polygon that says
WHERE the restricted area is, and only that.

That splits the feature into two, and the cheap half may be the useful one:

  - **Wire an alerting device to our community.** A plain node, no buffer. The
    unknown is whether a mod's device node can name a base-game camera, whose
    NodeRefs in the shipped data are prefab-relative (`~/../name`) rather than
    the absolute form a mod must use (gotcha 34, 39).
  - **Ship our own trigger area.** Needs the buffer, and needs the outline
    captured the way the guard posts were.

**Depending on another quest's cameras is a choice with a cost**, and it should
be made deliberately: q112 and q113 own those devices' state, so a player at a
different point in those quests may find them powered down, already hacked, or
disabled. Shipping our own cameras avoids that and costs a device node per
camera.

### THE SECURITY AREA IS BUILT. 2026-08-25, not yet played

> **SUPERSEDED.** It was played, it did nothing, and it is not in the archive.
> The section below is kept as the working. See the close at the end of this
> item and `gotchas.md` 80.

Playtest asked for it in as many words: *"the whole reason why we did this was
to have this behave like a vanilla gig, and cameras are an important part."*

**The blocker was not one.** This item said for two days that the open question
was whether these generators can write an `entEntityInstanceData` RedPackage
buffer, which is what holds the trigger polygon. Answered by asking the smallest
version: the vanilla node was taken whole, given our names and refs, put in a
sector of our own and handed to the converter the build already uses. It
converted, and a round trip back to JSON returned the buffer intact, down to all
122 fields of the controller state. Gotcha 79.

**And it is ONE node, not the two this item described.** The worked example is
`{q112_infiltration_security_area_civilian_restricted}`, which is at this very
site, and it carries both links itself:

| | |
|---|---|
| `CommunityProxyPS` | the communities it alerts. Vanilla 3, ours 1 |
| `SurveillanceCameraControllerPS` | the cameras that feed it. Vanilla 9, ours 18 |
| `gameStaticTriggerAreaComponent` | outline points in LOCAL space, plus a height |
| `SecurityAreaController` | `securityAreaType: RESTRICTED` |

That corrects the earlier note twice over: the community link does not have to
sit on a security SYSTEM, and there need be no system node at all. Gotcha 80.

`tools/gig01/gen_security.py` builds it, and it rides in the compound
community's own sector so the community and the area are in one group. The
outline is the four corners already walked for `CCGig01Places.InsideCompound`,
so "inside the compound" means the same thing to the objectives and to the
restricted area.

**What is not settled, and only a playthrough answers it:** whether a MOD's
security area alerts a MOD's community at all. Every part is copied from
something that works and no mod here has run one. The test is the warning: walk
in and be told to leave rather than shot.

Also unsettled: whether the prism runs up from the node or is centred on it
(placed low with 40 m of height so it covers the site either way), and whether
one area over the whole compound is the right shape where vanilla uses several
small ones.

### THE SCRIPT ALARM WAS TRIED FIRST AND WITHDRAWN

Worth keeping because it is a good example of a plausible tool being the wrong
shape. The alarm was: watch the cameras, and when one reports `IsDetecting`,
broadcast a combat stimulus at the player.

Playtest within minutes: *"the police also marks me as enemy even if I haven't
done anything"*. A stim broadcast is addressed to nobody. It announces combat at
the player's position to EVERY NPC in range, and it fed itself, because the
fight it started made the cameras legitimately detect the player. A second
report, "the cameras spot me when I am far away", was the same loop from the
other end and sent one debugging session after a distance problem that did not
exist. Gotcha 81.

The camera half of it survives: `IsDetecting()` is the one question a camera
answers about what it can see, and the gig still reports it on the dev panel.

### THE CAMERAS ARE SWITCHED BACK ON, and the reason is other quests

> **SUPERSEDED.** No camera is touched. The pass and the alarm it served were
> both removed at playtest's request. The section below is kept as the working.

Playtest: *"I didn't want people to kill cameras and then break future quests in
the same [way]"*. While the gig is at the compound, all eighteen are walked back
up to ON, one action per camera per pass, using the ladder `Gig01_OfficeDoors`
established. A shot one is left shot on purpose.

The refs come from the shipped data rather than from clicking on cameras: a
device's runtime entity id is the FNV1a64 of its full NodeRef, predicted and
confirmed against one captured in game. Gotcha 82.

**Two risks stated rather than discovered later.** These are q112's cameras, so
a player who does this gig before Gimme Danger arrives at that mission with them
already on; and if both quests are open at the compound at once, our pass would
switch back on what Gimme Danger had just switched off. The mitigation, if it is
ever wanted, is to gate the pass on Gimme Danger's journal state, which the dev
menu can already read.

### THE CLOSE. What shipped, what did not, and what it cost

**SHIPPED.** Both sites are communities. `cc_g01_estate` stands twenty-nine
guards at the residence and `cc_g01_compound` stands thirty at the industrial
park, each at a post somebody walked to and captured, facing the way he was
captured facing. Sixteen of the compound's are off the ground floor and two of
the residence's are on the roof, which the navmesh query this replaced could not
produce at all. The recipe is `gotchas.md` 66, the implementation is
`tools/questkit/community.py`, and each site's generator holds only its roster.

The behaviour question is closed and the answer is two things, not one. A
community entry arrives with no quarrel with the player AND with its senses
switched off as far as the player is concerned, so the encounter applies both on
a tick. Gotchas 74 and 77, and 77 is there because the attitude was applied alone
first and thirty guards stood at their posts ignoring the player.

**NOT SHIPPED: the security area.** It was built whole and every part of it
measured correct in game: found, resolved, ON, attached, not disabled, typed
RESTRICTED exactly as vanilla's is, linked to our community, fed by eighteen
cameras, with its security system present, and reporting the player INSIDE it.
The guards did nothing. Setting its type between RESTRICTED, DANGEROUS and SAFE
at runtime changed nothing either, which is what an area with nothing on the
other end of its wire looks like.

What survived elimination is not proof, it is what is left: every vanilla
community a security area alerts, all 21 that resolve in the cached sectors,
sits in the GAME'S OWN `always_loaded` sectors, and a mod cannot add nodes to
those. The node class was eliminated on the way. The compound shipped the
plain `worldCompiledCommunityAreaNode` that all 21 of those use, rather than the
`_Streamable` class this project had always written, and the area still did
nothing. That run did settle something else worth having: a mod's own sector
spawns from either class.

So the trespass warning is not available to a mod, and what a mod has instead is
a hostile attitude and the base game's own detection ramp. `gen_security.py`
keeps the whole build so it is a one-line change if the picture ever changes.

**NOT SHIPPED: the cameras, and the alarm.** The alarm was a stim broadcast and
it was the wrong shape rather than the wrong size: it announced combat at the
player's position to every NPC in range, so the police turned hostile within
minutes of a playtest. Gotcha 81. Once the alarm was gone the restore pass had
no purpose either, because it was only ever insurance for a player who shot the
cameras out, and paying for that with a permanent change to another quest's
devices is the wrong trade. Two findings from the camera work are kept and are
worth more than the feature: gotcha 82, that any base-game device can be
addressed offline from the FNV1a64 of its NodeRef, and gotcha 83, the full menu
of what a camera will accept.

**NOT SHIPPED: patrol beats.** Four were tried at the compound and none
of them walked. The mechanism is real in the game's own data, 1780 of 32669
cached time periods carry more than one spot, but how a MOD gets it is not
established. Not chased: the cheap version of the question is answered and the
expensive version is a research line the gig does not need.

## 32. The gig is absent from every New Game Plus save. Cause found, FIXED 2026-08-26

Reported against 1.3.0: on a New Game Plus playthrough the gig never starts. The
useful half of the report was the comparison, "if I started a fresh game your mod
would trigger", plus the note that another quest mod had the same problem and
cured it in an update.

Nothing in the mod is broken on such a save. The quest phase is not there.

### New Game Plus runs its own root quest

New Game Plus is a mod, not a game feature. It does not continue a finished save:
it reads one and starts a fresh playthrough with the gear, from the prologue or
from just after the heist.

To do that it ships three root quests of its own,
`mod\quest\newgameplus.quest`, `mod\quest\newgameplus_q001.quest` and
`mod\quest\newgameplus_standalone.quest`. Each runs its own copy of the base
game's root phase, `mod\quest\changedquests\newgameplus_cyberpunk2077.questphase`,
and none of them references `base\quest\cyberpunk2077.quest` at all.

This gig's manifest named that file, and `ep1\quest\ep1_standalone.quest`, as the
two parents of its phase. Both are correct and both are unused in an NG+ session,
so the phase holding the whole gig was never part of the graph being run.

The failure has nothing to read. The mod's sectors stream, its guards stand where
they were put, its redscript arms itself and sets `cc_g01_start` on schedule.
Nothing is waiting on that fact, so nothing happens, and from the player's side
that is identical to a broken install.

### Scopes, which are what makes this a one-line fix

ArchiveXL resolves a phase's `parent:` through a table of named scopes before it
patches anything. It ships the base table itself, in `Bundle\QuestBaseScope.xl`:
`cyberpunk2077.quest` expands to `cyberpunk2077_main.quest` and
`cyberpunk2077_ep1.quest`, and those expand to the two real roots. So on a vanilla
install the scope name and the pair of paths mean the same thing.

The difference is that a mod can add to a scope. New Game Plus registers all three
of its roots into `cyberpunk2077_main.quest` and `cyberpunk2077_ep1.quest`, which
is a compatibility shim offered to every quest mod that uses the name. Nested
scopes are flattened until stable, so declaration order does not matter.

The manifest now carries one entry, `parent: cyberpunk2077.quest`, and the gig
follows every root a session can run, including any registered by a mod written
later. Quest scopes arrived in ArchiveXL 1.22 (2025-04-30), which is the floor
this sets. Full mechanism in `gotchas.md` #84.

### Where the evidence came from

Read on disk rather than inferred, 2026-08-26:

- the New Game Plus 1.3.1 archive and its `.archive.xl`, which declares the three
  roots and registers them into the two base scopes;
- ArchiveXL's shipped `Bundle\QuestBaseScope.xl`;
- ArchiveXL's source, `QuestPhase/Extension.cpp` (a parent is expanded through the
  scope table, then patched) and `ResourceMeta/Extension.cpp` (nested scopes
  flatten until stable);
- the NG+ root quest itself, unbundled and serialised, which names its four
  phases and its own copy of the base root phase.

### The four start conditions were suspected first, and all four survive NG+

`Gig01_Start` holds the trigger behind four conditions, and the first guess was
that one of them reads differently on an NG+ save. None of them does:

- `q101_enable_side_content` is set in an NG+ run. New Game Plus carries its own
  fix that caps it back to 1 when its start sequence pushes it to 2.
- `q115_point_of_no_return` is 0, because an NG+ playthrough is a fresh one and
  not a continuation of the finished save.
- *Heroes* is a real requirement rather than a bug. A post-heist start has not
  done it, El Coyote Cojo is shut for the same reason it is shut in any young
  save (item 18), and the gig says so on screen. It becomes available in the
  normal course of that playthrough.
- The phone and fast-travel conditions are about the moment, not the save.

So no condition changes. Recorded for any future gate that does need to know:
New Game Plus publishes plain quest facts, `ngplus_active`, `ngplus_q001_start`,
`ngplus_standalone_q101_start`, `ngplus_fresh_start_on`,
`ngplus_in_johnny_intro_sequence` and `ngplus_use_new_q101`. Reading
`ngplus_active` is the cheap test for "this is an NG+ save" and costs no
dependency: it is 0 when the mod is not installed. Its scripts also expose
`NewGamePlusSystem` with `IsInNewGamePlusSave()`, `IsInNewGamePlusPrologue()` and
`IsInNewGamePlusHeistOrStandalone()`, but naming that class binds the mod to it
at compile time, and a fact does not.

### CONFIRMED IN GAME 2026-08-26, both halves, with a control group

New Game Plus was installed here and a post-heist run started twice, once on the
released 1.3.0 and once on the fix. The evidence is three lines of ArchiveXL's
own log, written the moment the session loads its quest graph, so neither run
needed a minute of story.

On 1.3.0:

    [QuestPhase] Patching phase "mod\quest\newgameplus.quest"...
    [QuestPhase] Merged phase "base\quest\pride_morgan_blackhand_quest.questphase" ...
    [QuestPhase] Merged phase "mod\quest\phases\pride_david_quest.questphase" ...

Two other quest mods attach to the New Game Plus root and this gig does not
appear at all. Everything else of this mod merged normally in the same session,
the journal, the strings and the voice map, which is why nothing looked wrong.

On the fix, same run, same log:

    [QuestPhase] Patching phase "mod\quest\newgameplus.quest"...
    [QuestPhase] Merged phase "mod\negative_balance\quest\gig01.questphase" from "gig01_negative_balance.archive.xl".
    [QuestPhase] Merged phase "base\quest\pride_morgan_blackhand_quest.questphase" ...
    [QuestPhase] Merged phase "mod\quest\phases\pride_david_quest.questphase" ...

**The two mods in those lines are the independent confirmation.** Both ship a
`.xl` that parents its phase to `cyberpunk2077.quest`, the scope name, which is
the change made here. They were working in New Game Plus before anyone looked at
why this one was not.

Two limits on what this proves. It shows the phase is attached to the session,
not that the gig plays end to end in an NG+ run, which still needs a playthrough
that has finished *Heroes*. And the base-game path was not re-measured in the
same sitting, though it is the same expansion and the same log line.

### Still to do

- The fix is in the manifest only, so it ships with the next release.

---

## 33. Building a whole gig with no way to stand anywhere in it. 2026-08-26

**The question a second gig asked that the first one never had to.** Gig 01 was
built alongside play: thirty guard posts, an NPC's spawn offset, a shard's spot
on a desk and every map-pin target were captured by walking to them in game and
pressing a button. Gig 02 was built in one unattended pass with nobody able to
load a save, so not one coordinate could be captured.

That is not an exotic situation. It is the situation of anyone adapting this
repo who does not own the same save, and it is worth writing down as a
technique rather than as an apology.

### The three answers, in the order they are worth reaching for

**1. Anchor to a base-game node that IS the place, with a zero offset.**

`tools/find_pin_anchors.py` exists to find the nearest always-loaded node to a
target you already know. Turned around, its cache answers a different and more
useful question: **what named nodes are there, and what are they called.** The
three always-loaded sectors hold 5211 globally-named nodes, and a node's name
usually says what it is. `#q005_mrk_afterlife_entrance_mappin` is the base
game's own Afterlife entrance mappin. `#q112_mp_wakakos_pachinko_parlor` is the
parlor. `#wakako_sm_okada_default` is the spot Wakako Okada stands on when
nothing else is going on, which is her office by definition.

Dump the index once and grep it by name:

```python
# tools/find_pin_anchors.py exposes nodes() as (name, pos, sector)
[(n, p) for n, p, _ in nodes() if 'wakako' in n.lower()]
```

A pin anchored to such a node with a zero offset lands on the game's own marker
rather than on the exact doorstep. That is a real loss and it is a small one.

**2. Ask the voice corpus where a place is.**

`tools/vo_corpus.py` was built to answer "how does this character talk". It also
answers **"where is the place whose name I only know from a comic"**, because
the corpus is every spoken line joined to the scene it belongs to.

Searching it for "Dewdrop" returned two lines from
`civ_low_f_04_enus_30_sts_std_arr_01_recepctionist_new`, one of them "Welcome to
the Dewdrop Inn. Where every day begins with a smile." The scene id names the
street story, `sts_std_arr_01`, and the always-loaded index then has
`#sts_sm_std_arr_01_recepctionist_new` with its position. Santo Domingo, not the
Japantown the comic's own location table had assumed.

About a minute, from a name to a coordinate, with no game running.

**3. Spawn onto navmesh instead of onto a coordinate.**

`CCSharedWorld.Scatter` asks `FindPointInSphereOnlyHumanNavmesh` for a point a
human can stand on and drops anyone it cannot place. A body placed that way is
always reachable and always fightable; a body placed at a guessed coordinate is
sometimes inside a wall, and a guard inside a wall cannot be fought, which
stalls a room the player has to clear.

Gig 01 replaced exactly this with thirty walked posts, and the reason is worth
keeping in view: a navmesh query answers "somewhere near here" and keeps giving
nearly the same answer, so a squad huddles. **Scatter is the right tool when
nobody can walk the site and the wrong one when somebody can.**

### What has no answer, and it is the one that matters

**A body that is meant to be LOOKED at cannot be placed this way.** Scatter puts
a fighter somewhere reachable, which is all a fighter needs. A character who
stands in a doorway and talks needs a position, a facing, and usually a workspot,
and all three are judged by eye.

Gig 02's answer is to place nobody: every speaker except Johnny and the two
combatants is an actor a kilometre away with its lines set to play in 2D, and
the body the player looks at is the base game's own NPC already standing in that
room. It works, the words land, the name is over the subtitle, **and the mouths
do not move.**

That is the standing cost of building without a save, and nothing in this
register answers it. The fix is a capture pass, not a technique.

### Also worth knowing

- **The TweakDB string table settles "does this record exist" offline.**
  Decompressing CET's `tweakdbstr.kark` (the route in
  `docs/gameplay-restrictions.md`) answered three questions in one sitting:
  `Character.wakako_okada` exists, `PhoneAvatars.Avatar_Wakako` exists, and
  **there is no Yoko anywhere in it** - no character record, no avatar, no atlas
  part, under either Yoko or Tsuru. A design call that depended on pointing at
  her real avatar was closed as not achievable rather than shipped broken.
- **A quest node's names can be read out of the scene that uses them.**
  `base\quest\holocalls\wakako\wakako_holocall.scene` extracts and serialises in
  a few seconds and carries `#wakako_holocall_setup`, `#wakako_holocall_camera`,
  `wakako_holocall_lights` and `wakako_holocall_setup`. None of those is
  guessable and a wrong one is a silent no-op, so this is the difference between
  a staged holocall and an empty frame.
- **The compiler settles what a method is called.** `IsInCombat` is not on
  `ScriptedPuppet`; a five-function probe file compiled against `scc` found that
  `GetHighLevelStateFromBlackboard()` against `gamedataNPCHighLevelState.Combat`
  is what answers "has this NPC seen the player". `docs/scene-playbook.md`
  already recommends this under "Validating offline" and it is cheaper than any
  amount of reading.

## 34. A god-mode shield with two states needs a three-state flag. 2026-08-26

Gig 02's merc must be beaten and must not die, which is the inverse of gig 01's
Hoshino and needs both of `GodModeSystem`'s settings rather than one:

| when | shield | why |
|---|---|---|
| before V speaks to him | `Invulnerable` | a stray shot cannot open the beat |
| the fight | `Immortal` | damage lands, death does not |
| once he is down | `Invulnerable` | a shotgun cannot end the gig |

Written the obvious way, with a `m_shielded: Bool` beside the `AddGodMode` call,
the middle row never happens: the transition into the fight sees a shield
already on and skips the add, so he keeps `Invulnerable`, takes no damage at
all, his health never falls, the threshold that declares him beaten never fires,
and the gig stops on "Beat the merc down" with a man who cannot be hurt.

**The flag has to record WHICH shield, not WHETHER.** A small integer, compared
against what the facts say it should be right now, with the old type removed by
name before the new one is added. Both are held under the same source, so
removing by source alone is not something this project has measured.

Caught by reading rather than by playing, which is the only way it could have
been caught: the failure needs a save where the merc has been spoken to, and
testing starts from a pre-gig save and goes forward.

## 35. The breach-protocol minigame on a mod's own item. Recipe found, BUILT AND UNPROVEN 2026-08-27

**The question:** can a mod put the game's own hacking minigame, the code grid,
on an object it ships? This register has carried it as research since the gig
was designed, and the answer turns out to be documented in the shipped data
rather than anywhere else.

**The wiki does not know.** No page mentions the minigame. The Device Operations
Container guide states that it cannot perform a device action, which rules out
the one route a reader would try first. So this is a case for source 4, the
shipped data itself.

**`TriggerHackingMinigameEffector` is a real effector class**, and two shipped
items carry an identical shape. `Items.q003_chip` is the Militech chip from The
Pickup; `Items.mq015_wizardbook_encrypted` is Bartmoss's book. Both are built
this way:

| record | what it is |
|---|---|
| `Items.<x>_inline0` | an ObjectAction, with an effector to apply |
| `Items.<x>_inline1` | the effector: `effectorClassName`, `factName`, `factValue`, `journalEntry`, `reward`, `showPopup` |

The item points at the action through `itemSecondaryAction`, which is the same
field a readable shard uses for its Read.

**On a successful breach the effector sets a quest fact and opens a journal
entry.** That is the whole join to a quest: a fact the phase can wait on and a
piece of text the player gets for winning. Nothing has to be scripted.

**How those record names were obtained**, because it is the reusable half: CET
ships `tweakdbstr.kark`, the game ships the Kraken decompressor, and 187 MB of
plain text comes out holding every record id and every flat name.
`docs/gameplay-restrictions.md`, "Reproducing the list", carries the format.

**WHAT IT DOES NOT GIVE IS VALUES.** They stay hashed. So an ObjectAction record
carries both an `effector` flat and an `effectorToApply` flat, and which one the
game reads could not be settled from disk. Gig 02 sets both, to the same record.

**Built, not proven.** `mods/gig-02-dead-ringer/source/tweaks/items.yaml` ships
it on the relay, behind a fallback: if the action never appears in the
inventory, the script raises the item's note after twenty-five seconds and sets
the same fact, so the beat completes either way. Whoever plays it first should
say whether a grid appeared, and this entry gets closed on that answer.

**Closed 2026-09-05: never seen to open, and removed.** In play the action
never appeared and the fallback popup was empty. The relay is a plain readable
shard now (`docs/shard-playbook.md`), which is the route the merc's shard
proved. The recipe above stands as research; nothing in the project uses it.

## 36. Finding one object in a room full of similar ones. SOLVED 2026-08-27

**The problem, in a playtest's words:** "all objects are very near to one
another, and there's no real understanding of what the user should look for."

A search beat driven by proximity cannot work in a dense room, because
everything in it is within any usable radius of everything else. The parlor had
the relay, the counter and the room's own marker inside a handful of metres.

**Proximity is the wrong question. What the player is LOOKING at is the right
one.** `TargetingSystem.GetLookAtObject(player, true, true)` answers it, both
flags mandatory (gotcha 91), sampled on a tick and counted while it keeps
returning the same thing. Holding still for about a second and a half is then
the interaction, which is a verb the player already knows from waiting for an
NPC's name to resolve.

Three things make it a beat rather than a mechanism:

- **Something must tell the player what to look FOR.** A phone call one beat
  earlier gives the test to apply, in this case that a relay has to be
  hardwired, powered and always online.
- **The wrong answers must answer.** Holding on something that is not it says
  so, twice and then never again. Without that a player cannot rule anything
  out, which is the difference between searching and wandering.
- **There must be a floor under it.** Fifteen seconds standing at the object
  finds it whatever the player is looking at. An objective completable exactly
  one way is a stall waiting for the one player who does it differently.

**Identify the object by POSITION, not by entity id.** The id needs the
container's NodeRef to resolve, which is one more thing that can fail quietly; a
coordinate is a number the script already has, and nothing else was within two
and a half metres of it.

**The tick has to run faster while this is live.** At one sample a second a hold
is a coin toss. Gig 02 runs at four a second between arriving at the parlor and
finding the relay, and at one a second everywhere else.

## 37. The breach-protocol minigame on a mod's own ACCESS POINT. SOLVED 2026-09-06

**The question:** can a mod place the game's own physical access point (the
wall box with "Jack in") in a sector of its own and have the code grid play on
it, so a quest can wait for the breach? Item 35 tried the minigame on an item
and it never opened; this is the other route, the device the game itself uses.

**What the shipped data says.** Thirteen `worldDeviceNode`s in the cached
sectors carry `access_points\accesspoint.ent`. Every one has an instance
buffer, and the two that stand alone with no connected devices
(`{q112_01_market_security}`, `{q115_dvc_atrium_alt_access}`) carry a
one-chunk buffer: `AccessPointController` with its `AccessPointControllerPS`.
Both ship `deviceState: DISABLED`, because a quest switches them on;
`hasNetworkBackdoor: 1`, `hasPersonalLinkSlot: 1`, `deviceName: LocKey#138`.

**What the decompiled scripts say** (`cyberpunk/devices/masters/
accessPointController.swift`): the breach is recorded by
`SetIsBreached(true)` on the Succeeded state in `OnNPCBreachEvent`, read back
by `public const quest func IsBreached()`, and `FinalizeNetrunnerDive(state)`
is public and not final, so it can be wrapped. "Jack in" wants clearance 2
and a powered device.

**Built:** gig 02 lifts `{q112_01_market_security}` whole
(`tools/gig02/access_point_node.json`), sets `deviceState`/`cachedDeviceState`
ON and `isAuthorizationModuleOn` 0, gives it the mod's own NodeRef and puts it
on the parlor's wall (gen_sector.py). The script polls `IsBreached()` on the
device nearest the box and wraps `FinalizeNetrunnerDive`, either setting one
fact. Unproven in play: whether the box renders and offers "Jack in", whether
the grid opens, and whether the persistent state a mod node ships is honoured.
The tell is the prompt: if there is none, the state values are the first
suspect.

**Half proven 2026-09-05.** The node renders, the game gives it a persistent
state (the dev menu's probe read it back: ON, initialized, attached to game,
backdoor and personal link slot true, interactive), and with the Arasaka
appearance the "Jack in" prompt appeared. With `router_b` it did not until the node was turned 180 in place, which
is gotcha 98: the prompt volume is placed per appearance. `default` drew
nothing. Still unproven: the grid itself, and the breach reaching
`IsBreached()`.

**The dead prompt, 2026-09-05 evening.** With the small router look the
prompt appeared only with the node turned 180 in place (gotcha 98), and then
read "Install Software" and did nothing. The lifted quest device's stored
state carries `personalLinkCustomInteraction: Interactions.InstallSoftware`,
a personal-link interaction that only its own quest completes. The node is
lifted from the game's own working street router instead
(`{ma_hey_spr_04_ap}`, `tools/gig02/access_point_router_node.json`), which
ships no stored controller state at all, so the game builds the default one.
Unproven until played.

**The daemon's label.** The grid names its programs from
`MinigameAction` records' `objectActionUI` caption and description, and a
device's definition (`m_minigameDefinition`, protected persistent on the
controller state) lists them in `overrideProgramsList`; the game's own
`minigame_v2.Kab08Minigame` is one definition, one program
(`minigame_v2.FindAnna`). `source/tweaks/minigame.yaml` clones those three
shapes as "ACCESS ENCRYPTED DATA", and `Gig02_Encounter` names the
definition on the live device through an added method, since the node has no
state to carry it. Unproven; the dev menu's "TWEAK FLATS" button reads the
records back.

**Played 2026-09-06, and it works.** The box renders on the parlor's south
wall, offers "Jack in", opens the game's own code grid, and the breach reaches
`IsBreached()`, which is what closes the objective. The daemon reads "ACCESS
ENCRYPTED DATA".

**The recipe, in one place.** Lift a node whose buffer holds the ENTITY CHUNK
AND NOTHING ELSE. The game's own street router `{ma_hey_spr_04_ap}`
(exterior_-35_-20_0_0, node 316) is one, and it is what shipped
(`tools/gig02/access_point_router_node.json`, lifted by `gen_sector.py`). Give
it the mod's own long-form NodeRef, place it against a wall, and turn it to
face the wall rather than the room: the prompt volume is placed per appearance
and this look wants yaw 180 from the wall's own facing, which is gotcha 98.
Name the minigame definition on the live controller state from redscript
(`@addMethod(AccessPointControllerPS)` writing `m_minigameDefinition`), because
a node with no stored state cannot carry it. Read the breach two ways, polling
`IsBreached()` and wrapping `FinalizeNetrunnerDive`, and tell our box from
every other access point in the city by where it stands.

**What NOT to lift, and this cost a day.** A standalone QUEST access point such
as `{q112_01_market_security}` carries a one-chunk buffer holding the
controller and its persistent state, and that state carries
`personalLinkCustomInteraction: Interactions.InstallSoftware`, a personal-link
interaction only its own quest completes. Shipped that way the prompt reads
"Install Software" and pressing it does nothing. A lifted state is not neutral
just because every field in it came from the game. The node file was deleted
on 2026-09-06 once the router had shipped.

**The box also asks for Intelligence, and a lifted device brings its own
number.** "Jack in" is a hacking skill check, and the level it demands is the
device's own: the `attribute_checks` curve read at its power level against the
check's difficulty, with no term in it that belongs to the player
(`RPGManager.CheckDifficultyToStatValue`). The router lifted for gig 02 brought
Wellsprings' number with it and asked for 10, so on 2026-09-10 three players
reported the objective unfinishable at 3/10 and 5/10. The gig now writes a
fixed requirement of 3 on the live controller state, next to where it names the
minigame, and gotcha 110 has the shape. Played 2026-09-10: the prompt reads 3,
the grid opens, and a save made standing at the box comes back with the new
number drawn.

Anyone following this recipe wants that line too, and wants to test it on a
character with low attributes. The requirement does not vary with the player, so
a build that can already pass it shows nothing.

## 38. Yoko's and Char's lines are mute after a RELOAD. SOLVED 2026-09-06

**THE REPRODUCTION, 2026-09-06, and it changes the diagnosis.** One build,
installed once, nothing swapped:

1. Start the gig from scratch and finish the Afterlife leg.
2. Save, before fast-travelling to the netrunner.
3. Play straight on. Every line of Yoko's and Char's works, audio and subtitle.
4. Reload that same save.
5. Play the same leg again. Yoko and Char have no audio and no subtitle. Each
   line still takes its time and can be skipped.

**So it is the RELOAD, not the save.** The same save file gives a working leg
when it is played through and a mute one when it is loaded first.

**MORE PRECISELY, and this matters for testing: it is loading a save in which
the cast entries were ALREADY ACTIVE.** Not every load does it. The
playthrough that works also begins with a load, of a pre-gig save, and that one
is fine. The entries are switched on just after the merc, so a save taken
before that point reloads clean and the phase activates them afterwards during
play; a save taken after it reloads broken. That is the shape the registry
theory predicts: the join is built when the entries activate, and restoring a
save with them already on does not rebuild it.

The practical consequence is that a bench save has to be made AFTER the merc
and BEFORE the Inn, and it has to be made under the build being tested
(gotcha 101). That kills
what this entry used to blame, which was saves carrying entities and community
state from older builds while the cast list was still changing. The build did
not change between step 3 and step 5.

**The report it replaces.** Playtest, 2026-09-05, twice: loading a save taken
at Afterlife and playing on to the Dewdrop Inn, every line of Yoko's and
Char's is mute. Wakako's and the merc's lines were not reported mute, and both
mute speakers are acquired from the mod's own spawn set
(`gen_scenes.build_inn`, `build_handover`). The merc is acquired the same way,
but his beat is BEFORE the save point, so he is never tested after a reload:
the innocent-looking exception is just untested.

**What is known.** The loaders' logs are clean. A line with no voice and no
subtitle that still runs its duration is the shape of a scene whose actor was
not acquired (`questkit.scene.add_spawnset_actor`: the actor is found or the
scene has no speaker). The save carries entities from earlier builds: a probe
listed this morning's deleted relay case still standing at its old spot. The
cast list also changed between the builds the save and the test were made
with (entries appended at the end, 2026-09-05), and community state is kept
in the save by list position (gen_community.py, the note on Yoko's place).

**ELIMINATED 2026-09-06, both by evidence rather than by argument.**

- **"The bodies are gone after a load."** They are not. Playtest: after the
  reload Char is in her chair, she is OURS, and her appearance is the pinned
  one. Yoko is ours too, which the design call identified by a tell worth
  keeping: the vanilla Kabuki vendor offers merchant options and ours offers
  none, so the presence of a shop menu says whose body it is without any tool.
- **"There are two of her after a load, and the scene takes the wrong one."**
  There are not. The dev menu's 15 m listing was taken in a session where the
  lines played (2026-09-05 21:15) and in one where they were mute (2026-09-06
  14:23), and the two lists are the same bodies at the same coordinates to the
  centimetre: one body at the chair at (-1184.43, 2045.15, 20.49), one at
  (-1179.40, 2042.25, 20.07), one Street Vendor. Only the distances differ,
  because the player stood somewhere else. The world is identical in the
  working case and the broken one.

**WHAT THE PAIRING RULES OUT, and it is most of the pipeline.** Yoko speaks in
the GAME'S OWN recordings, pointed at by `vanilla_sid`. Char speaks in takes
this mod ships as its own `.wem`. They go silent together. So the cause is not
our audio conversion, not the `locVoiceoverMap`, not the subtitle resource and
not the LocKeys: the game's own audio for the game's own line is not playing
either. The line is not being performed at all.

**WHAT IS LEFT.** A body existing and a body being BOUND to a scene are
different things, and only one of them was measured. The body is world state
and rides in the save. The binding the scene uses is a spawn-set lookup by
NodeRef plus entry name (`acquisitionPlan: spawnSet`), which is community and
quest state. Those can disagree after a load: the woman is standing there, she
is ours, and the scene still cannot take her. That fits every observation
above, including the one still untested below.

**SETTLED 2026-09-06: it is every scene that TAKES its actor from this mod's
own community, and only those.** Playtest after the reload, and the split is
total:

| Scene | How it gets its actor | After a reload |
|---|---|---|
| Yoko at the Inn | our community | mute |
| Char at the chair | our community | mute |
| Wakako in her office | our community | mute |
| Char's holocall | the scene spawns her | **works** |
| Wakako's closing calls | no world actor | **works** |

Not one exception. Every `add_spawnset_actor` scene is silent and every
`add_actor` scene is fine. The gig is otherwise untouched: the objectives move,
the prompts appear, `Skip Ahead` works, and the screenshot of Wakako's office
shows the scene RUNNING with no subtitle under it. So the scene plays and the
actor is not in it.

**Two things this rules out.**

- **It is not the body being absent, and not a duplicate.** The 15 m listing is
  identical in a working session and a broken one, to the centimetre.
- **It is not the body being older than the load.** The entries were cycled off
  and on (dev arms 12 then 11) BEFORE fast-travelling, so the body was spawned
  fresh after the load, and the lines were still mute. Re-activating the
  community entry does not repair it.

**THE MECHANISM, and gotcha 69 names the join.** A scene acquires a community
body through `worldCommunityRegistryNode.spawnSetNameToCommunityID`, a table of
`CName -> community id`. The actor's `spawnSetParams.reference` is matched
against the string registered in that table, and `specRecordId` is 0 on both
paths, so the actor is found through that lookup or the scene has no speaker.
That lookup is the only thing in the chain that a spawnDespawn actor does not
use, and it is the only thing that distinguishes the mute scenes from the
working ones.

So the suspect is the registry join going stale across a load: the row is still
there and the community it names is not the one the entries now belong to.
Cycling the entries does not rebuild the row, which is why arms 12 and 11
changed nothing.

**WHY GIG 01 NEVER SAW THIS.** Its one shipped spawn-set actor, Mama Welles,
is taken from a VANILLA spawn set (`#mama_welles`). Vanilla's registry and
vanilla's communities are both part of the base world and restore together.
Every one of gig 02's is taken from `SPAWNSET_NAME`, this mod's own community.
The bug needs a mod-owned community, which gig 01 never used for a speaker.

**SEVERITY: this blocks a release.** It needs no unusual save, no old build and
no mid-scene reload. Any player who saves and reloads at any point before these
beats gets a silent conversation, which is most players on most playthroughs.
The reason it survived to here is that the whole gig had only ever been played
straight through from a fresh start.

**PREDICTIONS, cheap to confirm and worth confirming before any fix.** Toji is
acquired the same way (`gen_scenes.build_kill`), so his last words should be
mute after a load too; nobody has reported on him. The merc's three scenes are
the same and sit before the usual save point, so a save and reload BEFORE
Afterlife should silence him as well. If either speaks, this diagnosis is
wrong.

**THE RESEARCH, 2026-09-06, and it found a plan this project had never used.**
A scene actor's `acquisitionPlan` has more values than the two this repo
writes. A sample of 108 shipped Kabuki scenes, 187 actors, unbundled and read:

| plan | actors |
|---|---|
| `community` | 62 |
| `findInContext` | 59 |
| `spawnSet` | 45 |
| `findInWorld` | 13 |
| `spawnDespawn` | 7 |
| `spawner` | 1 |

**`community` is vanilla's most common way of taking a body, and it does not
use the registry table at all.** Read off `ma_wat_kab_02.scene`:

```
acquisitionPlan  community
communityParams  entryName = the community entry's name
                 reference = the community NODE's NodeRef
spawnSetParams   empty
specRecordId     0, on both paths, so the actor is found or there is no speaker
```

The reference is resolved as a real world NodeRef rather than matched as a
registered string, so it takes the long spelling for a mod's node (gotcha 34).
That is the whole difference from `spawnSet`, and it skips
`spawnSetNameToCommunityID`, which is the join suspected of going stale.

**THE BENCH, built 2026-09-06.** Two one-line scenes aimed at Yoko, identical
but for the acquisition plan, on dev arms 16 and 17 (`gen_scenes._lab_acquire`).
The subtitle is the entire signal: an actor that acquired speaks, one that did
not is silent while the scene runs its time, which is the symptom itself.

**RUN IT IN THE RIGHT WINDOW, and the first attempt did not.** An actor can be
in one scene at a time, so a bench that asks for a body the gig is already
holding is silent whatever the plan does, and the first run of this bench was
pressed while Yoko was mid-conversation. That result means nothing. There is no
way to see her without entering her 3 m trigger, so the window has to be taken
AFTER her conversation rather than before it:

1. Load a save, go to the Inn, and let Yoko's (mute) conversation finish.
2. Do NOT hand the shard to Char. `cc_g02_trace_done` is what switches her and
   Yoko off, and it only starts 30 in-game minutes after that handover, so
   leaving it undone keeps both bodies in the world indefinitely.
3. Her scene is guarded on `cc_g02_inn_reached == 0` and never fires twice, so
   she is now present, active and unclaimed. Press 16, then 17.

**A silent bench is ambiguous unless the arm is known to have fired.** Each arm
clears `cc_g02_dev_crowd` as its first action, and the menu's bench panel shows
that fact live: 0 means the arm ran, and the value still sitting there means it
never fired.

**THE FIRST TWO RUNS BOTH FIRED NOTHING, and that is gotcha 101.** Playtest
2026-09-06: preconditions perfect (`inn_reached` 1, `trace_done` 0, both bodies
listed within 20 m), both buttons pressed, and the readout showed the fact
still holding 16 when 17 was pressed and still holding 17 afterwards. The arms
are in the built phase, wired and waiting, and they were never entered: the
save's phase passed the node they hang off long before this build existed. A
new quest branch is dead in an old save. So the bench needs a playthrough that
STARTS under the build being tested, and only then a save and a reload at the
Inn.

- **16 silent, 17 speaks.** The plan is the cause and the fix is to move the
  four scenes to `add_community_actor`. One body, no design change.
- **Both silent.** The plan is not the cause; the community itself is not
  reachable after a load by any route, and the next suspect is the registry
  node this project generates.
- **Both speak.** The bench is not reproducing the bug and something about the
  real scenes matters that the bench does not copy.

**THE ANSWER, measured on the bench 2026-09-06.** On a playthrough started
under the build being tested, at the Inn, after a save and a reload, with both
bodies present and Yoko's own conversation already over:

| bench | plan | arm fired | result |
|---|---|---|---|
| 16 | `spawnSet` | yes | **silent** |
| 17 | `community` | yes | **subtitle** |

Both arms were confirmed to have fired by the fact each clears on entry, so the
silence of 16 is a real result rather than an arm that never ran. Repeated
presses afterwards were inert, which is the one-shot-per-load behaviour and is
itself a confirmation.

**So a scene actor taken from a MOD'S OWN community must use the `community`
acquisition plan.** `spawnSet` works until the first load and is silent
afterwards, because it resolves through
`worldCommunityRegistryNode.spawnSetNameToCommunityID` and that join does not
survive a save being restored with the entries already active. `community`
names the community node as a world NodeRef and never consults the table.

**CONFIRMED FIXED IN PLAY, 2026-09-06.** The original reproduction was run
again on the shipped change: start the gig, finish Afterlife, save before
travelling to the netrunner, reload that save, go to the Inn. Yoko and Char
speak, with audio and subtitles.

**SHIPPED.** All twelve of this gig's world-acquired actors moved to
`Scene.add_community_actor` (the two door groups, the merc's three scenes,
Yoko, Char, Wakako and Toji). One body each, no design change, and nothing else
about the scenes was touched. The bench's own control keeps `spawnSet` on
purpose, since it is the thing being compared against.

**Gig 01 is not affected** and needs no change: its one world-acquired speaker,
Mama Welles, comes from a VANILLA spawn set, whose registry and community
restore together.

**TWO ROUTES TO A FIX, neither tried.** Kept for the record; the bench chose
the first before either was built out.

1. **Make the registry join survive**, which keeps the design as it is. This
   needs research rather than a guess: ArchiveXL's community handling, the
   registry node this project generates, and what a load does to a mod
   community's id. `docs/sources.md` says which of those to read first.
2. **Let the scenes spawn their own bodies**, which is proven to work today,
   and switch the community entry off as the scene opens so there is still one
   body. This reverses the 2026-09-03 call that made every speaker a single
   community body, and it risks a visible swap at the moment the conversation
   starts. It is the fallback if route 1 has no answer.

**THE OLD CHECK, now answered.**
After the reload, at the Dewdrop Inn: press "INN BODIES ON: vendor off, our
Yoko and Char on (arm 11)", then talk to her again.

- **She speaks.** The binding is what the load loses, and re-activating the
  community entry restores it. The fix is then re-assertion rather than a node
  that fires once.
- **She is still mute.** The binding is not it either, and the next suspect is
  the scene itself rather than anything around it.

**A second reading worth taking in the same run, because it is free.** Wakako
in her office is acquired the same way from the same community. If she is mute
too, the statement is "every spawn-set actor after a load", which is one clean
thing. If she speaks, something is specific to the two Inn entries, and the
difference between them and her is where to look next.

**The fix, once it is confirmed**, is re-assertion on load, which is the rule
this project already applies to attitudes and shields: the encounter's tick
reads the facts and puts the world into the state those facts imply, every
tick, rather than trusting a node that ran once. What the phase does at a
transition, something has to do again on every load.

## 39. A mod's own trigger area as a quest area on the minimap. SOLVED 2026-09-06

**The question.** The last leg of gig 02 ends when V leaves an area with many
exits. A marker at the top of the stairs says nothing about where the area
ends. The game draws a dotted outline on the minimap for some objectives; can
a mod draw one for its own area?

**What the game does.** The cooked journal (`base\journal\cooked_journal.journal`,
71 MB serialised) holds 4276 quest map pins. 638 of them reference nodes
named `_tr_`, trigger areas, with pin ids such as `mp_area` and `area_mappin`.
The minimap has a controller for these: `MinimapQuestAreaMappinController`
(`UI/mappins/minimapMappins.swift`) owns an `areaShapeWidget`, is chosen when
the pin arrives with `MinimapQuestAreaInitData` (`UI/widgets/minimap/minimap.swift`,
`CreateMappinUIProfile`), and hides itself unless the pin is tracked and
`MappinUIUtils.IsPlayerInArea` says V is inside. So the outline is drawn for a
quest pin whose target is a trigger area, only while V stands in it and the
objective is the tracked one. That matches a "Leave the area" objective
exactly. Nothing in the scripts ties it to a pin variant.

**The shape.** `worldTriggerAreaNode.outline` is an `AreaShapeOutline`: a
`buffer` of count (uint32), then X Y Z W per corner in the node's LOCAL space
(float32, W 1), then the height (float32); `points` repeats the corners as
Vector3. Read off `exterior_-10_18_0_0`'s `{cs_tr_vo}`, whose four `points`
are a unit square while its buffer holds the real 5 to 7 m corners, so the
buffer is the one that counts and both are written.

**What was built.** `tools/gig02/hit_area.py` turns the 23 corners walked in
play (the stairs sit 1 to 4 m outside that walked line, along the edge that
closes it) into the convex hull of the corners, the stairs and the trash pile,
pushed out 6 m: seven corners, every step inside, the top step 10 m outside.
`gen_sector.area_node` writes it as a `worldTriggerAreaNode` in the gig's own
sector, named `$/03_night_city/#c_westbrook/japantown/#cc_g02_hit_area`,
with a `questTriggerNotifier_Quest` notifier, `isVisibleInGame` 1, and the
same finite streaming distance as the access point beside it. The two way-out
pins reference that node with zero offset, and the leaving test in the script
uses the same seven corners with a 2 m margin, so what is drawn is what ends
the leg.

**What the test has to show.** Three outcomes, told apart by the ArchiveXL log
(`red4ext\plugins\ArchiveXL\ArchiveXL.log`, the `[Journal]` lines, see the
map-pins playbook) and the minimap after Toji dies:

- outline on the minimap while V is on the stairs, gone once V is out: the
  answer is yes, and gotcha 34's long-form rule holds for pins too;
- a plain marker at the area's centroid and no outline: the pin resolves but
  the engine does not treat a mod's trigger area as an area. Next knob: the
  pin's variant (vanilla's area pins are mostly `ExclamationMarkVariant`);
- `Can't resolve mappin ... position` or `reference`: the node is not
  resident or not named when the pin activates; the sector's whole-map
  streaming box was supposed to settle the first, and the long-form name the
  second.

**First test, 2026-09-06 09:08.** Outcome three. The ArchiveXL log:
`Can't resolve mappin ... pin_exfil position`. The dev menu's node probe
(`CCLab_NodeEntity`, backlog 11's recipe) on the stairs: the area's name
resolves and NO entity stands behind it; the access point, the control, the
same, but it is 1.3 km away and finitely streamed, so that says nothing. The
map pin report (`CCLab_MappinReport`): the tracked quest pin sat at 0, 0, 0,
`area=false`, 1301 m from V, which is what "the marker moved a kilometre
away" was: a pin whose node yields no position falls to the world origin.
So a bare `worldTriggerAreaNode` in the gig's Exterior sector does not become
an entity, with the shard case's instance flags or with a vanilla trigger
area's (Uk11 65024, Uk12 1, read off 1071 vanilla instances), and gig 01's
generator note that "a trigger area's did not render" was the same finding.

**Second test, built the same morning.** The area is now the one mod-shipped
area known to instantiate: gig 01's security-area DEVICE (backlog 31: found,
resolved, attached, `IsPlayerInside` true), a `worldDeviceNode` of
`security_area_1.ent` whose instance buffer carries a
`gameStaticTriggerAreaComponent` with the outline and a
`SecurityAreaController` state, here with `securityAreaType` DISABLED and no
connections, so it does nothing but exist. It rides as an extra node of the
cast community's always-loaded sector under `$/mod/cc_g02_cast/#cc_g02_hit_area`
(`gen_community.hit_area_node`, borrowing `tools/gig01/gen_security.py`'s
builders), and the two way-out pins point at it. Whether the engine treats a
device's trigger component as a quest AREA is the open half; the pin
resolving to a position at all is the first thing to read.

**Second test, 09:20.** The device resolved: ArchiveXL logged
`resolved to NodeRef` for both way-out pins, and the map pin report put the
tracked pin at the area's centroid, 11 m from V. `area=false`, no outline.
The node probe still said "no entity", so `FindEntityByID` on a resolved
node is not the test of whether a pin can use it; the ArchiveXL log is.

**Why, from the source.** ArchiveXL's journal extension
(`src/App/Extensions/Journal/Extension.cpp`) builds the cooked mappin it
hands the game: position from the node instance plus the pin's offset, and,
in `ResolveMappinVolume` (run for every pin that is not a point of interest),
an outline with height IF the node instance casts to `worldAreaShapeNode`.
A `worldTriggerAreaNode` is one; a `worldDeviceNode` is not, whatever
component it carries. So the device could only ever give a position, and the
first test's trigger node was the right class in the wrong place: the gig's
Exterior sector, with a shard case's instance flags, where ArchiveXL found no
instance at all.

**Third test, built the same morning.** The trigger area node again, as an
extra node of the cast community's always-loaded sector, beside the
crowd-null area node that instantiates there, with the instance flags every
vanilla trigger area carries (MaxStreamingDistance 2760, UkFloat1 90, Uk10
1056, Uk11 65024, Uk12 1; questkit's instance writer learned Uk12 for it).
Same name, so the pins are unchanged. If the pin resolves and `area=true`,
the outline is ArchiveXL's and the question is closed; if it resolves with
`area=false`, the cast is failing on our node and the node's fields are the
next thing to compare against `{cs_tr_vo}` one by one; if it fails on
`position` again, a trigger area in a mod sector is not instantiated by this
route at all.

**Third test, 09:37: it works.** The map pin report: the tracked pin at the
area's centroid, 18 m from V, `area=true`. The minimap drew the seven-corner
hull as a filled yellow polygon around V, which is the game's own quest area
look (MinimapQuestAreaMappinController's root state is `Quest`, so it takes
the quest colour; nothing in the mod chooses it). ArchiveXL logged the pin
as resolved. The probe's "no entity" line for the node stayed the same, and
is not what the pin uses.

**The recipe, in one place** (also in the map-pins playbook): a
`worldTriggerAreaNode` in a mod's ALWAYS-LOADED sector, long-form name, the
outline in `outline.buffer` (count, X Y Z W per corner in the node's local
space, height) with the corners repeated in `points`, a
`questTriggerNotifier_Quest` notifier, `isVisibleInGame` 1, and an instance
carrying a vanilla trigger area's flags (MaxStreamingDistance 2760, UkFloat1
90, Uk10 1056, Uk11 65024, Uk12 1). A `gameJournalQuestMapPin` whose
`reference` is that node, offset zero. The outline shows while the pin's
objective is tracked and the player is inside; it does not need the pin's
variant to be anything in particular (this one is QuestGiverVariant).

**Correction.** A note made on 2026-09-05 said vanilla's dotted areas come
from base-game area nodes "which a mod sector cannot register for pins". That
was the pre-2026-08-17 belief; the map-pins playbook's own-anchors section
records that a long-named node in a mod's always-loaded sector does resolve
for a pin. The claim to test was never "does the node register" but "is it
drawn as an area".

## 40. Paying a gig fee the way the game pays one. SOLVED 2026-09-06

**The question.** Gig 01 pays by handing the player `Items.money` and awarding
Street Cred directly. That works, and it skips everything the game does around
a completed gig: the level XP, the scaling, and the telemetry. What does a
vanilla fixer gig actually hand out, and can a mod hand out the same shape?

**What the shipped data says.** Each of Wakako's nine Westbrook gigs closes on
one `QuestRewards.sts_wbr_*_completion` record, read off the live TweakDB with
a dev-menu probe on 2026-09-06. Every one is the same shape: eddies as a fixed
additive value (3,800 to 16,600 across the nine), 1,000 level XP, and 979 to
1,710 Street Cred XP. The XP is scaled to the player's level by
`CalculateStreetStoryReward`, which the game applies to any reward whose `name`
begins with `sts_`; the eddies are not scaled, so the number in the record is
the number the player sees. One of hers (`sts_wbr_jpn_03`) pays 30,000 for the
peaceful ending against 15,040 for the other through a second record, which is
how a gig with two outcomes does it.

**What ships.** Four records in `mods/gig-02-dead-ringer/source/tweaks/
rewards.yaml`, one per outcome (9,300 / 7,000 / 4,700 / 3,500 eddies by the
merc's fate and whether V was seen), handed to `RPGManager.GiveReward`, which
is what the game's own quest reward node calls. The money notice and the
telemetry are then vanilla's, and the payout draws no text of the mod's own.

**The clone trick, and it is the part worth copying.** A completion record
holds its currency package and that package's quantity modifier as INLINE
records, whose types are not names a modder can spell in YAML. So all three are
cloned by `$base` off `sts_wbr_hil_01_completion` and its `_inline4` and
`_inline5`, and only the money value is overridden. Nothing has to name an
inline record type:

```yaml
QuestRewards.sts_cc_g02_qty_quiet_kill:
  $base: QuestRewards.sts_wbr_hil_01_completion_inline5
  value: 9300
QuestRewards.sts_cc_g02_money_quiet_kill:
  $base: QuestRewards.sts_wbr_hil_01_completion_inline4
  quantityModifiers: [ QuestRewards.sts_cc_g02_qty_quiet_kill ]
QuestRewards.sts_cc_g02_completion_quiet_kill:
  $base: QuestRewards.sts_wbr_hil_01_completion
  name: sts_cc_g02_completion_quiet_kill
  currencyPackage: [ QuestRewards.sts_cc_g02_money_quiet_kill ]
```

**ALL FOUR TIERS CONFIRMED IN PLAY, 2026-09-06.** Each outcome was played and
each paid its own number. Nothing about the fee is outstanding.

**Whether TweakXL resolves a `$base` on an `_inline` record was the unproven
half, and it does.** Read from the loader's own log on 2026-09-06
(`red4ext\plugins\TweakXL\TweakXL-<date>.log`, not `r6\logs\`, which is where
this register said to look): `rewards.yaml` is read, inheritance and mutations
resolve, the import completes, and the record count rises by 35 across the
gig's four YAML files. No line of ours is rejected. The 9,300 tier had already
paid in play; the other three are the same three records with a different
number in one flat.

**KEEP THE NAME BEGINNING WITH `sts_`.** It is what makes the game scale the
XP. A record named anything else pays the raw numbers.

**RESCALED 2026-09-08, and the four values above are the old ones.** The gig
now pays 15,000 / 11,300 / 7,600 / 5,600 for the same four outcomes. The
design call: 9,300 reads as the going rate for a killing, and what Wakako is
buying is silence about a man who forged her authorization, which is worth
more than the killing. The ratios between the four tiers are unchanged, so
the shape of the choice is the same and only the scale moved. The top tier
is now 15,000 against her own range of 3,800 to 16,600, which is where a job
she cannot afford to have talked about belongs. Nothing about the records
changed: same three clones per tier, same one flat overridden.

## 41. An objective whose wording can be swapped by a branch that is racing the main line. NOT REPRODUCED 2026-09-06

**CLOSED 2026-09-06: played for, and not reproduced.** The kill was taken in
front of the den with the Claws watching, as close to simultaneous as a person
can make it, and the objective changed wording correctly every time. The exact
instant is difficult to force by hand, so this is "not reproduced" rather than
"cannot happen": the hole below is still real in the graph, and if the wording
is ever reported as stuck after a kill, this entry is where to start. Nothing
was changed.

**The shape.** Gig 02's hit has two objectives that change wording when V is
seen: "Kill Toji without being seen" becomes "Kill Toji", and "Leave the area
unseen" becomes "Leave the area". Each is a side branch off the main line that
waits on OR(seen, the-thing-is-done), then asks whether the thing is still
undone, and only then closes one objective and opens the other. The branch has
no output; it is expected to resolve because the main line always sets the
second fact.

**The hole, reasoned at the desk and not yet observed.** Both facts can go up
in the same tick of `DeadRingerEncounter.Tick`: `cc_g02_spotted` is set where
the Claws are checked, and `cc_g02_toji_dead` about eighty lines further down
in the same pass. If the quest graph evaluates the branch's condition after
BOTH have landed, the condition reads "Toji is already dead", takes its dead
end, and the loud objective is never opened. The main line then reads
`cc_g02_spotted` on its own, sees it set, and closes `obj_toji_loud`, an
objective that was never opened. The quiet one stays in the journal.

**What the player would see.** "Kill Toji without being seen" still sitting in
the quest log after Toji is dead, with the leaving objective open underneath
it, for the rest of the gig. The same shape applies to the leaving pair.

**Whether it can happen depends on something not measured here:** whether the
quest system evaluates a fact-driven pause the moment the fact is written or
once at the end of the frame. If it is the moment, the branch always sees a
living Toji and there is no bug at all.

**The test.** One shot that kills Toji and alerts a Claw at the same instant,
which in practice means shooting him in front of the den rather than from the
walkway. Read the quest log immediately after: if "without being seen" is
still there once he is dead, this is real.

**The fix if it is real** is to stop asking the branch to decide. Close both
objectives on the main line rather than picking one by the same fact the branch
read, or drive the wording from a single condition node on the main line after
the death, with no branch at all. Do not fix it before the test: closing an
objective that was never Active may itself put a completed line in the journal,
which would be a worse bug than the one being fixed.

## 42. One character, two bodies, two outfits. NOT A BUG 2026-09-06

**CLOSED 2026-09-06 by the design call, on a second look in game: the two are
the same woman and the report is withdrawn.** The entry is kept because the
elimination below is worth having, and because one line of it was wrong for a
day and reached three shipped docs.

**What was and was not measured.** The chair body was read three times and
copied twice, and every reading says `slacker_wa_slacker_wa_03`. THE STUDIO
BODY WAS NEVER READ. So this closes on judgement by eye, not on a measurement,
and if the doubt ever comes back the reading is one button: teleport to the
holocall studio floor spot while the call is up and press the dev menu's "READ
the appearance of the body I'm looking at".

**The report.** Playtest, 2026-09-05 and again 2026-09-06: Char sits in the
netrunner chair at the Dewdrop Inn, and later calls V on video from the holocall
studio. She was reported as dressed differently in the two places.

**The wrong answer, recorded so it is not reached twice.** On 2026-09-05 this
was closed as a lighting difference: the chair room is lit teal, the studio is
lit warm, and two crops of the same knit looked like the same weave. That
cannot be the explanation for a different GARMENT, and the report on 2026-09-06
was explicit that the clothes differ. Light changes colour, not cloth.

**What IS proven, all of it read off disk on 2026-09-06.**

- The appearance name is pinned in all three places a body could pick one: the
  `Character.cc_g02_char` record, the community entry that seats her, and the
  scene actor that stands in the studio. All three say
  `slacker_wa_slacker_wa_03`.
- The shipped scene resource really carries it, in both fields the actor has:
  `spawnDespawnParams.appearance` and `specAppearance`. So this is not a
  generator that failed to write the value.
- That name is real. The entity
  (`base\characters\entities\citizen\citizen__youngster_wa.ent`) lists 20
  appearance names and `slacker_wa_slacker_wa_03` is one of them, mapping to
  `slacker_wa_03` in the `.app` beside it.
- That target is a leaf with no randomness: 18 components, no `partsValues` and
  no `partsOverrides`. Once resolved it is one outfit everywhere.
- The chair body is confirmed to have resolved it. The dev menu's look-at probe
  read `Character.cc_g02_char` / `slacker_wa_slacker_wa_03` off it three times
  on 2026-09-05.

**The suspect, and it is the one thing on this list nobody had looked at.** The
entity's `defaultAppearance` is the literal string `random`. A body of this
entity that does not receive an appearance does not fall back to a fixed look:
it rolls one of the twenty. So a studio body whose appearance never reached it
would be wearing a different outfit, and a different one each time.

**The studio body has never been measured.** Every capture in the log is the
chair body at (-1184.4, 2045.2). Nobody has read what the body in the studio is
actually wearing, because it stands in a sector off the map and is only ever
seen through the phone. The whole disagreement is between a measurement of one
body and an inference about the other.

**The test, and it needs no new tooling.** Play the call twice on two separate
runs and compare the caller's clothes to each other, not to the chair.

- **Different each time**: the appearance is not reaching the studio body and
  `random` is picking. The fix is at the spawn, not in the data.
- **The same wrong outfit every time**: something is applying a fixed
  appearance that is not ours, and the record and the scene actor are then in
  disagreement about which one wins.
- **The same as the chair**: the difference is colour after all, and the
  lighting reading was right.

**THE BENCH, built 2026-09-06 and unplayed.** One CET button, "APPEARANCE A/B",
outside the gig and on any save whose phase has started:

- quest-phase dev arm 15 stages the holocall studio and rings V from Char's
  contact, playing `gig02_lab_call`, a scene with NO dialogue whose only job is
  to hold her in the studio for about 45 seconds. She is staged exactly as the
  real call stages her: same record, same pinned appearance, same offset, same
  yaw. A bench that differs from the thing it tests proves nothing.
- `CCLab_SpawnInFront` puts a second body of `Character.cc_g02_char` three
  metres in front of the player, facing back at him, with NO appearance on the
  spec, so the record alone decides what it wears.

Both arrive together, so the phone and the body beside it are seen under ONE
light. That is the variable the 2026-09-05 reading blamed and never controlled
for. A second button despawns the bodies.

**Three readings, and each names its own cause.**

| What the run shows | What it means |
|---|---|
| the phone and the body in front differ, under one light | the two spawn routes give different looks, and the light was never it |
| they match | the difference is the light after all, and the 2026-09-05 reading was right |
| the phone differs from ITSELF on a second run | nothing is reaching the studio body and `random` is picking one of twenty |

The third is the one worth running twice for, and it is the cheapest to read.

## 43. Three beats gig 02 built and then removed. CLOSED as a record, 2026-09-06

These were designed, some of them built, and taken out again. They are here
because the register is where this project keeps what it tried, and because
each one is a shape another gig will be tempted by. None is a research
question; nothing is open.

**A hold-to-extract progress bar instead of the breach minigame.** The parlor
beat was first designed as a scan of the machines followed by a held
interaction against the big on-screen progress bar, on the reasoning that the
code grid was unknown territory and a held bar reads as breaking into a machine
without needing a puzzle. It was replaced once item 37 proved a mod can ship a
working access point. The bar is still the right answer for a beat that wants
tension without a minigame, and the gig before this one uses it for an upload;
what it is not is a substitute for the game's own grid when the grid is
available.

**The Tyger Claws standing down when the target dropped.** The hit originally
ended with every surviving Claw turning neutral the instant Toji died, on the
reading that they had watched a sanctioned killing and knew better than to
argue with it. It was cut after one playtest and the reason is worth keeping:
they do not know V, they do not know who sent him, and the reaction to bullets
is bullets. A crowd that lowers its guns because the QUEST knows the killing
was sanctioned is the quest's knowledge leaking into the world. What replaced
it is that nobody stands down: unseen, they never learn anything happened;
seen, it stays a firefight.

**Two bodies for every speaker.** Before the community work, each speaking NPC
was a pair: a voice-only scene actor parked a kilometre out and a hundred
metres down, carrying the words and the lipsync, plus a script-spawned body
standing where the player looks. It works, and it is what a mod does before it
can acquire a community body. The costs are that the two can disagree, that the
mouth moves on a body nobody sees, and that the visible body is not owned by
the scene, so its own conversation can win the approach. Gotcha 69 is the
technique that replaced it and gotcha 102 is the acquisition plan that makes it
survive a load.

## 44. A merc three players could not attack, and nothing here could reproduce. SOLVED 2026-09-08

**The question.** Three reports against gig 02's 1.0.1, within a day of each
other: the gig gives the order to take the merc out and he cannot be attacked.
One report said the weapon lowered itself, one said the crosshair would not
hold him, one said only that nothing worked. Every run on the development
machine was fine.

**The report that carried the answer** was the one that said what the player
did next: they reloaded a save from before the gig and did it again without
stopping, and it worked. That is a statement about TIME, not about place or
build, and it points at something that is not persisted.

**Cause one, and it explains the reload.** The shield's dead man's handle
(scene playbook, section 5) was built inverted. It counted ticks while the
kill order was ALREADY given, so it could never fire on the upgrade save it
was written for, and it fired on every healthy run instead: three minutes
after the objective opened, the merc went back to the `friendly` attitude
group, which the game will not lock on to. The counter is a script field, so
loading any save handed back a fresh three minutes. That is exactly the
reported workaround. Reproduced here once the clock was known: take the order,
wait, try to shoot.

Why it never showed in testing: the development route walks out of the third
conversation and shoots him inside ten seconds. Three minutes is only reachable
by a player who does something else first, which is most players and none of
the test runs.

**Cause two, and it explains the reports that read as immediate.** The merc's
health was read with no guard, and a stat pool read on a body still resolving
answers 0 (gotcha 106). The likeliest tick in the gig for that is the one after
the third conversation releases him, which is the same tick the order is given.
On such a tick the mod both declared him beaten, latching `cc_g02_merc_down`
into the save with no shot fired, and stopped writing the attitude that keeps
him targetable. Random, invisible, and not fixed by waiting.

Gig 01 had already found and fixed the identical read on Hoshino three weeks
earlier, and recorded it in a comment in its own encounter file and nowhere a
second gig would look: not in `gotchas.md`, not in a playbook. So gig 02 was
written straight past it. That is the reason this entry exists: a finding
recorded only where it was paid for protects exactly one gig.

**What changed.** The clock now waits on the fact that may never arrive and
gives the kill order itself if it does not, so nothing reads a clock during a
fight. Both health tests carry `hp > 0.0`, and an unreadable value counts as
untouched. Gotcha 106 and a scene-playbook section carry the general form.

**What was NOT the cause, and was the first suspect.** A safe area. The
symptom "V lowers the weapon" is the exact signature of one (gotcha 90), the
third group stands about six metres from the Afterlife door, and a safe area
had already eaten this leg once during development. It was left alone: the two
causes above account for the reports, and the mod's own safe-area check on all
three group spots has never come back positive.

**Closed on the second of those, 2026-09-08.** Playtest: "the merc is well
outside the afterlife safe area". So the check agrees with the ground, and the
signature that made this look strong belongs to the friendly attitude group
instead: an NPC the game will not lock on to reads, from behind the crosshair,
much like a weapon that will not come out.
