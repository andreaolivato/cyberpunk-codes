# Translating Acceptable Loss

This guide shows step-by-step instructions on how to translate Acceptable Loss into
one of the officially supported languages of CP2077.

## What is already translated

For known characters (Dino, V and Johnny), we are using the game's original
lines either fully or split. So we also already have all the translations
available.

All their voices (audio) and subtitles are already translated and shipped
with the mod.

## What needs to be translated

Everything that is original to the gig needs to be translated:
- the journal entry and briefing
- Dino's messages and V's replies
- the objectives and map captions
- the shard
- the terminal documents
- the notices and alerts on screen

All these texts require a translation and this guide shows how to create
one, use it for yourself and publish it for other players to use.

A translation is a mod of its own, which overwrites some files shipped with
the original mod. It contains all the translated texts and subtitles, and
optionally also the voiceovers for the new NPCs.

## What you need

- [WolvenKit](https://wiki.redmodding.org/wolvenkit), the modding tool the
  whole community uses. Install it and open it once so it finds the game.
- A copy of the original gig mod installed to test.

Nothing else.

## Making the mod

1. Download [0_acceptable_loss_translation.zip](0_acceptable_loss_translation.zip?raw=true),
   unzip it, and double-click the `.cpmodproj` to open the project in
   WolvenKit.
2. In the project explorer, under `archive`, open
   `mod\acceptable_loss_translation\strings.json`. It lists every string. Open an
   entry and type your translation into `femaleVariant` over the English.
   If `maleVariant` is not empty, translate it too. Never ever change
   `secondaryKey`. It must always stay the same. Save.
3. Under `resources`, open `0_acceptable_loss_translation.archive.xl` and replace
   `<lang>` with your language's code, on every line it appears on:
   `it-it`, `de-de`, `fr-fr`, `es-es`, `es-mx`, `pl-pl`, `ru-ru`, `pt-br`,
   `jp-jp`, `kr-kr`, `zh-cn`, `zh-tw`, `cz-cz`, `hu-hu`, `ar-ar`, `th-th`,
   `tr-tr`, `ua-ua`. Save.
4. When you're all done, click "Install mod" to send it to your game. Then
   start the game and test that your translations are correctly shown.
5. When the test is successful, click "Create zip" to produce the archive
   you'll upload on Nexus Mods, as a translation of the gig.

Keep the archive name and folder structure as they are. Don't change
anything apart from what you see above.

## Publishing

Publish it on Nexus Mods as a translation of the gig. When you upload the
.zip it asks if your mod is a translation of another mod. Just select that
and then your language.

Say in your description which gig version you translated.

## When the gig updates

I try not to change texts when I release a new version, but in case I do,
the translation kit is regenerated with every build, so diff the new
`strings.json.json` against the one you translated from.
