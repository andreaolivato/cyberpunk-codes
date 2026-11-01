# Translating Hodan Warsame

This guide shows step-by-step instructions on how to translate Hodan Warsame into
one of the officially supported languages of CP2077.

## What is already translated

For known characters (V and Johnny), we are using the game's original
lines either fully or split. So we also already have all the translations
available.

All their voices (audio) and subtitles are already translated and shipped
with the mod.

## What needs to be translated

Everything that is original to the mod needs to be translated:
- her name and the title of her conversation
- her codex entry and the card she sends
- the dialogue buttons.
- the subtitles for the characters invented for this mod: Hodan.
- (optional) the voice of Hodan.

All these texts require a translation and this guide shows how to create
one, use it for yourself and publish it for other players to use.

A translation is a mod of its own, which overwrites some files shipped with
the original mod. It contains all the translated texts and subtitles, and
optionally also the voiceovers for the new NPCs.

## What you need

- [WolvenKit](https://wiki.redmodding.org/wolvenkit), the modding tool the
  whole community uses. Install it and open it once so it finds the game.
- A copy of the original mod installed to test.

Nothing else.

## Making the mod

1. Download [0_fixer01_translation.zip](https://github.com/andreaolivato/cyberpunk-codes/raw/main/mods/fixer-01/translation-kit/0_fixer01_translation.zip),
   unzip it, and double-click the `.cpmodproj` to open the project in
   WolvenKit.
2. In the project explorer, under `archive`, open
   `mod\fixer01_translation\strings.json`. It lists every string. Open an
   entry and type your translation into `femaleVariant` over the English.
   If `maleVariant` is not empty, translate it too. Never ever change
   `secondaryKey`. It must always stay the same. Save.
3. Open `lines.json` in the same folder.
   The dialogue buttons are plain English: type your translation into
   `femaleVariant` and `maleVariant` over it, as in `strings.json`.
   The subtitles of Hodan look like this:

   ```
   <kiroshi l="eng" o="There's a divorce going on upstairs." t="There's a divorce going on upstairs." b="" a=""/>
   ```

   Replace ONLY the text inside `t="..."` with your translation and leave
   `o="..."` alone. To show your language only, replace the whole tag with
   plain text. Save.
4. Under `resources`, open `0_fixer01_translation.archive.xl` and replace
   `<lang>` with your language's code, on every line it appears on:
   `it-it`, `de-de`, `fr-fr`, `es-es`, `es-mx`, `pl-pl`, `ru-ru`, `pt-br`,
   `jp-jp`, `kr-kr`, `zh-cn`, `zh-tw`, `cz-cz`, `hu-hu`, `ar-ar`, `th-th`,
   `tr-tr`, `ua-ua`. Save.
5. When you're all done, click "Install mod" to send it to your game. Then
   start the game and test that your translations are correctly shown.
6. When the test is successful, click "Create zip" to produce the archive
   you'll upload on Nexus Mods, as a translation of the mod.

Keep the archive name and folder structure as they are. Don't change
anything apart from what you see above.

## Recording Hodan

If you are a voice actor, Hodan can also be voiced in your
language. Record each line in `lines.json` and convert the takes to the
`.wem` format (read `BUILDING.md` or "Audio toolchain" to learn how).

Once you have all your .wem files, copy them under
`source\archive\mod\fixer01_translation\vo\` with the names defined in
`vomap.json` (e.g. `fixer01_call__a01.wem`). Then copy
`optional-voice/vomap.json.json` from the kit into the matching folder under
`raw`, right-click `raw` and "Convert from JSON", and uncomment the
`vomaps:` lines in the manifest.

## Publishing

Publish it on Nexus Mods as a translation of the mod. When you upload the
.zip it asks if your mod is a translation of another mod. Just select that
and then your language.

Say in your description which mod version you translated.

## When the mod updates

I try not to change texts when I release a new version, but in case I do,
the translation kit is regenerated with every build, so diff the new
`strings.json.json` against the one you translated from.
