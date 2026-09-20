r"""One translation table per locale per gig, and the locales a gig ships.

    from questkit import translations
    t = translations.load(os.path.dirname(__file__))   # this gig's tables
    t['de-de']['onscreens']['gig-title']                # a UI string
    t['de-de']['lines']['gig02_office/w47']             # a spoken line

THE FILES. `tools\gigNN\translations\<locale>.json`, one per locale, shaped

    {
      "onscreens": {"<key>": "<text>", ...},
      "lines": {"<scene>/<line key>": "<text>" | {"f": "...", "m": "..."}, ...}
    }

`onscreens` keys are the bare keys of the gig's STRINGS table (no LocKey
prefix). `lines` keys are the scene name and the line or option key exactly
as `add_line` / `add_option` name them; a gendered line carries both bodies.
A key the file does not have falls back to English, and the generator prints
the gap, so a half-translated locale still shows the gig in full.

Where a spoken line is one the game recorded (`vanilla_sid`), the game
supplies its own translation and nothing here is consulted for it.

All nineteen text locales are written whether or not a table exists, because
a locale that is registered against an incomplete file shows raw keys, and
registering only the translated ones is the half-broken state gig 01 shipped
for a fortnight (backlog.md 0b). English is the table of record: what is in
the generator's STRINGS and in gen_scenes is what every other locale falls
back to.
"""
import json
import os

from questkit.packs import TEXT_LOCALES, PACKS

VOICE_LOCALES = sorted(PACKS)


def load(gig_dir):
    """{locale: {'onscreens': {}, 'lines': {}, 'actors': set}} for every
    text locale. `actors` is the same set in every locale: the lines of the
    gig's invented characters, from `translations/_actors.json`, whose
    recordings stay English and whose subtitles are therefore written with
    the game's translation effect in every other language."""
    out = {}
    tdir = os.path.join(gig_dir, 'translations')
    actors = set()
    apath = os.path.join(tdir, '_actors.json')
    if os.path.exists(apath):
        with open(apath, encoding='utf-8') as fh:
            actors = set(json.load(fh).get('lines', []))
    for loc in TEXT_LOCALES:
        table = {'onscreens': {}, 'lines': {}, 'actors': actors}
        path = os.path.join(tdir, loc + '.json')
        if os.path.exists(path):
            with open(path, encoding='utf-8') as fh:
                data = json.load(fh)
            table['onscreens'] = data.get('onscreens', {})
            table['lines'] = data.get('lines', {})
        out[loc] = table
    return out


def report(name, locale, missing, total):
    if locale == 'en-us' or not missing:
        return
    print('  %s %s: %d of %d untranslated, English shown for: %s'
          % (name, locale, len(missing), total,
             ', '.join(sorted(missing)[:8]) + (' ...' if len(missing) > 8 else '')))


def kiroshi(original, translated):
    """The game's own markup for speech the player's cyberware is
    translating: `<kiroshi l="eng" o="<what is said>" t="<what it means>"
    b="" a=""/>`. The subtitle shows the original and resolves to the
    translation with the translation effect, the way a Japanese or Creole
    line does in the base game. 2,922 vanilla lines carry the tag, with
    language codes such as jpn, mex, creo and rus; `eng` is the code the
    Cosmopolitan Night City tool uses for English audio in a dubbed game.
    """
    def esc(t):
        return (t.replace('&', '&amp;').replace('"', '&quot;')
                 .replace('<', '&lt;').replace('>', '&gt;'))
    return '<kiroshi l="eng" o="%s" t="%s" b="" a=""/>' % (esc(original), esc(translated))
