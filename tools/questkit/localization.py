"""The en-us onscreens resource: every LocKey string a gig ships.

    from questkit.localization import configure, write_onscreens
    configure(lockey_prefix='cc-g01-')
    write_onscreens(path, {'reward': 'Payment received'})

WHAT THIS IS FOR. Journal titles, objective text, map-pin captions, shard and
terminal text: everything the player READS rather than hears. Dialogue is not
here. A spoken line carries its text inside its .scene resource, keyed by the
RUID the audio is keyed by, which is what lets one number resolve both.

Keys are written BARE, with no 'LocKey#' prefix, on both sides: ArchiveXL hashes
the bare key and matches the journal's reference to the entry here.
"""
import json
import os

from questkit import cr2w
from questkit.packs import TEXT_LOCALES
from questkit import translations as _tr

LOCKEY_PREFIX = ''


def configure(lockey_prefix):
    global LOCKEY_PREFIX
    LOCKEY_PREFIX = lockey_prefix


def entry(key, value):
    """One string.

    femaleVariant carries the text and maleVariant is left empty on purpose: the
    game falls back to the female variant when the male one is blank, so a line
    that does not differ by body type is written once. A gendered line is a
    scene line, and scene lines are not in this file.
    """
    return {
        '$type': 'localizationPersistenceOnScreenEntry',
        'femaleVariant': value,
        'maleVariant': '',
        'primaryKey': '0',
        'secondaryKey': LOCKEY_PREFIX + key,
    }


def write_onscreens(path, strings):
    """Write the resource. Returns how many strings went into it."""
    doc = {
        'Header': cr2w.header(os.path.basename(path).replace('.json.json', '.json')),
        'Data': {
            'Version': 195, 'BuildVersion': 0,
            'RootChunk': {
                '$type': 'JsonResource',
                'cookingPlatform': 'PLATFORM_PC',
                'root': {'HandleId': '0', 'Data': {
                    '$type': 'localizationPersistenceOnScreenEntries',
                    'entries': [entry(k, v) for k, v in strings.items()],
                }},
            },
            'EmbeddedFiles': [],
        },
    }
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(doc, fh, indent=2)
    return len(strings)


def write_all_locales(out_dir, strings, tables):
    """The gig's strings, registered for ENGLISH ONLY, and any locale a
    table translates as its own file beside it.

    English is the fallback: a manifest that registers `onscreens:` for
    `en-us` alone has ArchiveXL merge that file for every other language as
    fallback entries, which fill any key nothing else defines and never
    overwrite one that is. So a player on another language reads English
    until a translation exists, never a raw key, and a translation mod that
    registers its own language wins whichever order the two load in
    (measured 2026-09-19; `docs/scene-playbook.md`, "Other languages").
    Registering our own English text under every locale instead, which this
    function did on 2026-09-18, would make ours a real entry in each
    language and beat a translation mod that loads after us.

    A locale whose table carries `onscreens` gets `<locale>.json.json` too,
    every key present with English filling the gaps, for a translation
    contributed into this repo; `update_manifest_locales.py` registers the
    locales that have one. Returns {locale: count of translated keys}.
    """
    done = {}
    for loc in TEXT_LOCALES:
        table = tables.get(loc, {}).get('onscreens', {}) if loc != 'en-us' else {}
        path = os.path.join(out_dir, loc + '.json.json')
        if loc != 'en-us' and not table:
            if os.path.exists(path):
                os.remove(path)
            continue
        merged, missing = {}, []
        for k, v in strings.items():
            if loc != 'en-us' and k in table:
                merged[k] = table[k]
            else:
                merged[k] = v
                if loc != 'en-us':
                    missing.append(k)
        write_onscreens(path, merged)
        if loc != 'en-us':
            _tr.report('onscreens', loc, missing, len(strings))
        done[loc] = len(strings) - len(missing)
    return done
