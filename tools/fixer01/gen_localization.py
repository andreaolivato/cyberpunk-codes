"""Generates fixer 01's en-us onscreens resource (all LocKey strings).

Keys are bare (no 'LocKey#' prefix) in both the journal and here; ArchiveXL
hashes them and matches the two sides.

Everything the player READS of hers: her name, her codex entry, the text
that carries her card. What she SAYS is in gen_scenes.py, because a
spoken line carries its text inside its .scene resource.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fixer01_config import RAW_MOD, LOCKEY_PREFIX                     # noqa: E402
from questkit.localization import configure, write_onscreens        # noqa: E402

configure(lockey_prefix=LOCKEY_PREFIX)
OUT = os.path.join(RAW_MOD, 'localization', 'en-us.json.json')

STRINGS = {
    # --- the fixer ----------------------------------------------------------
    #
    # ONE STRING, THREE PLACES: the contact in the phone, the title of her
    # codex entry, and (through source/tweaks/fixer.yaml, which hashes this
    # key) the name over the map icon and over her body when scanned.
    #
    # HODAN WARSAME (the design call, 2026-09-21: she is Somali; Nzinga
    # Okoro until then). gen_scenes.py's header has the reasoning.
    'fixer-name': 'Hodan Warsame',
    # The subject line under the contact in the messages list. The game's
    # own fixers use a wry one-liner ("Occupational hazard", "Got you
    # something spicy"); hers is her trade.
    'fixer-conv-title': 'Lost and found',
    # THE CODEX ENTRY, the game's own "Fixer" character pages in shape: a
    # subtitle and a paragraph. Written for a stranger who has taken one job.
    'codex-subtitle': 'Fixer, Charter Hill',
    'codex-body': 'Hodan Warsame grew up in a good family in Mogadishu, '
                  'beside the Orbital Air spaceport, the largest on Earth. '
                  'The corporation hired her out of law school to write its '
                  'labor contracts, and she read what she was writing: '
                  'people signed for years on an orbital station and '
                  'never paid off the debt, because the contracts were '
                  'written so nobody could. She started helping the '
                  'smugglers who got people off the stations, and within a '
                  'year she was running them. Then Orbital Air found out and '
                  'ambushed a run. Most of her crew and passengers died, and '
                  'she escaped to Night City. Orbital Air runs every '
                  "spaceport, Night City's included, so she does not fly "
                  'now. She works from a couch in the lobby of a Charter '
                  'Hill apartment tower and finds mercs for suits fighting '
                  'other suits and for people who have a problem with a '
                  'corporation. She is one of those people herself. She '
                  'takes no Orbital Air money, and she has never sold a job '
                  'that hands a person to a corp.',

    # --- her card -----------------------------------------------------------
    #
    # The text after the call, in the shape of the game's own welcome texts
    # (Regina: "if you'd like to meet face to face, please drop on by";
    # Dino: "you're welcome to swing by anytime"), in her register. The
    # first wording read oddly in play (2026-09-18: "a bit weird").
    'msg-card': "If you'd rather talk in person: Charter Hill, the tower "
                "on Palm Street. The lobby, the couch by the elevators. "
                "Location attached.",

}


if __name__ == '__main__':
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    COUNT = write_onscreens(OUT, STRINGS)
    print('wrote %s (%d strings)' % (OUT, COUNT))
