# Cross-mod conventions

Prefix everything with `cc` (Cyberpunk.Codes) + gig number so four installed gigs never collide.

## Quest facts
`cc_g01_<name>`: e.g. `cc_g01_intro_msg_sent`, `cc_g01_hoshino_dead`, `cc_g01_malware_done`.

## redscript
- Module namespace: `CyberpunkCodes.Gig01` (and so on). Shared helpers live in
  `shared/scripts` as `CyberpunkCodes.Shared`, and **`tools/vendor-shared.ps1`
  copies them into each mod at build time under `CyberpunkCodes.Shared.Gig01`**,
  rewriting the matching `import` in the gig's own scripts. Wired into
  `deploy-dev.ps1` and `build-release.ps1`, so it is automatic.
- **The rename is not tidiness.** Tested against `scc` on 2026-08-16:

  | two files declaring the same class name | result |
  |---|---|
  | same module | `[SYM_REDEFINITION]` |
  | different module | compiles clean |

  A redscript failure is also not scoped to the mod that caused it: the compiler
  builds one bundle, so two of our gigs shipping an un-renamed shared file would
  take down every redscript mod the player has installed. Because the module
  rename is sufficient, class names inside `shared/scripts` need no per-gig
  prefix, and the vendoring step touches only the `module` and `import` lines.
- **What belongs in `shared/scripts`**: anything with no gig data in it.
  Spawning, attitude, HUD banners and the progress bar, runtime map markers and
  the payout are there now. A gig's own scripts keep its places, its TweakDB
  records, its facts and its flow. The test is whether a second gig would want
  the code unchanged.
- `tools/check-scripts-repo.ps1 <mod>` compiles the REPO through that vendoring
  without deploying anything, which is what to use while refactoring.
  `check-scripts.ps1` still compiles the DEPLOYED tree and is what to use before
  playing.

## TweakXL records
`cc_g01_<record>`: e.g. `Character.cc_g01_hoshino`, `Character.cc_g01_rcs_guard`.

## Localization keys
`cc-g01-<key>` in a per-mod onscreens resource. The prefix is stated once, in
that gig's config module, and both the generator writing the strings and the one
referencing them read it from there.

## Generators
One subdirectory per gig under `tools/`, `tools/gig01/` and so on, so a second
gig can take the same filenames. Each gig has one config module named after it
(`gig01_config.py`) holding its paths, its prefixes and its scene anchors: a
value any two generators share belongs there rather than in both.

## Journal
Per-mod journal entries under our own path, never editing base game journal files in place.

## Voice
Voices are generated with ElevenLabs and disclosed on the mod page. Subtitles
always. Audio resolves through a mod-supplied `locVoiceoverMap`, so Audioware is
not a dependency. See `architecture.md`, "Voice".
