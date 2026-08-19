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

from questkit import cr2w

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
        'Header': cr2w.header('en-us.json'),
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
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(doc, fh, indent=2)
    return len(strings)
