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

Per-locale files are named by the locale: `subtitles_<locale>.json` with
`gigNN_lines_<locale>.json` for the scene lines, `vomap_<locale>.json` and
`gigNN_<locale>.lipmap` for the ten dubbed locales (`en-us` carries no
suffix); the strings are `localization\en-us.json`, registered for English
only, plus `<locale>.json` for a locale a table translates. The tables are
`tools/gigNN/translations/<locale>.json`, one per locale, with `onscreens`
by bare key and `lines` by `scene/key`; a gendered line is `{"f": ...,
"m": ...}`, and what ships in `lines` is the game's own words for the cut
lines. `_actors.json` beside them lists the lines the gig's invented
characters speak. A translation shipped as its own mod uses the gig's
`translation-kit/` folder and the folder name `mod\<gig>_translation\`.
`scene-playbook.md`, "Other languages"; the kit's README is the guide.

## Generators
One subdirectory per gig under `tools/`, `tools/gig01/` and so on, so a second
gig can take the same filenames. Each gig has one config module named after it
(`gig01_config.py`) holding its paths, its prefixes and its scene anchors: a
value any two generators share belongs there rather than in both.

## Journal
Per-mod journal entries under our own path, never editing base game journal files in place.

## Voice

**Two rules, and they hold for every gig.**

1. **A character the base game voices speaks only in the game's own
   recordings**, whole or cut short at a pause. Nothing is generated for them
   and nothing imitates them.
2. **A character a gig invents is recorded by a professional voice actor**,
   and the take ships as recorded. The only thing added is the phone effect
   on a line heard over a call.

Both gigs say so on their pages, in the same words, so that one practice is
not described two ways:

> Every word <the base-game speakers> say in this gig is a voice line from
> Cyberpunk 2077 itself.

> <the invented characters> are new characters, so professional voice actors
> recorded them. Their takes play as recorded, apart from the phone effect on
> <the call>.

Subtitles always. Audio resolves through a mod-supplied `locVoiceoverMap`, so
Audioware is not a dependency. See `architecture.md`, "Voice".
