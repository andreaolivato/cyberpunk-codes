r"""Gives every line in this gig that has a mouth on screen its lipsync
animation, and writes source/lipsync_picks.json.

    python tools\gig04\gen_lipsync.py            # make what changed, assemble the sets
    python tools\gig04\gen_lipsync.py --remake   # make every new mouth again
    python tools\gig04\gen_lipsync.py --rebuild  # re-extract the catalogue first
    python tools\gig04\gen_lipsync.py --report   # list every line and its animation

The route of tools/gig03/gen_lipsync.py, re-pointed; tools/gig01/gen_lipsync.py
and tools/questkit/lipsync.py carry the whole chain. Every line this gig
ships a clip for (Hodan's, Maricel's, Stamps's and Reynaldo's takes) gets a
mouth made from that clip and its words by the lipsync animator, named
`f_<the line's RUID>` and committed under `source\lipsync\`. A whole vanilla line (Johnny's) keeps the
animation CDPR baked for it, copied out of the vanilla set that holds it.
Until 2026-11-01 every line here was cast by length from a civilian pool.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gen_scenes as gs                                             # noqa: E402
import gen_voice as gv                                              # noqa: E402
from questkit.lipsync import (                                      # noqa: E402
    configure, rebuild_cache, load_catalogue, _check_actor_names,
    mouth_lines, build_mouths, voicetag,
)
from gig04_config import REPO, SOURCE, MOD, RAW, MOD_NAME          # noqa: E402

CACHE = os.path.join(REPO, 'tools', '_lipsync_cache')
# NAMED AFTER THE GIG. See the module docstring: a shared catalogue is a
# rebuild that silently re-casts another gig.
CATALOGUE = os.path.join(CACHE, 'catalogue_gig04.json')
# The small, readable, COMMITTED result: which animation and which set each of our
# lines uses. gen_scenes reads this. Committed because it is a casting
# decision rather than extracted data, and because a fresh clone has to be able
# to build the gig with no game installed.
PICKS = os.path.join(SOURCE, 'lipsync_picks.json')

WK = os.environ.get(
    'WOLVENKIT_CLI',
    os.path.expandvars(r'%LOCALAPPDATA%\Programs\WolvenKit.CLI\WolvenKit.CLI.exe'))
GAME = os.environ.get(
    'CP2077_DIR',
    r'C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077')
VOICE_ARCHIVE = os.path.join(GAME, 'archive', 'pc', 'content',
                             'lang_en_voice.archive')

# ------------------------------------------------------------------ the cast
#
# character (a gen_voice.CAST key) -> how to find its candidate lipsync sets.
#
#   actor    the actorName gen_scenes gives that speaker. gen_scenes looks the
#            pick up by (scene, actorName), so the two strings must agree, and
#            _check_actor_names() fails the run if they ever drift.
#   regex    passed to WolvenKit's `unbundle -r`, matched against the full depot
#            path inside lang_en_voice.archive.
#
# V IS NOT HERE AND MUST NOT BE. He is the player, the camera is behind his
# eyes, and there is no mouth to move.
#
# EVERYONE ELSE IS HERE NOW, and the note that used to sit on this line said
# why they were not: "their bodies are a kilometre away". That was true of the
# arrangement this gig shipped first, where a speaker was an invisible actor
# off-map and the body on screen was a separate script spawn. Six of them are
# the body on screen now, acquired from this gig's community, so six of them
# have a mouth to move. See docs/scene-playbook.md.
#
# THE POOLS ARE ACCENT-AND-GENDER CLASSES, NOT ONE SET EACH, and that is
# deliberate for the reason Wakako's note gives below: casting picks the
# animation nearest each line's length, so a small pool lands long. Borrowing
# across characters is safe - every lipsync anim in the game has the same 344
# joints and 414 tracks.
CHARACTERS = {
    # HER POOL IS EVERY FEMALE CIVILIAN SET WITH AN AMERICAN ACCENT, the same
    # pool gig 02 gave Char, and for the same reason: casting picks the
    # animation nearest each line's length, and a small pool lands long.
    # The trailing `.*` matters: some voice tags carry a district after the
    # age and a pattern ending at `_\d+` misses every one of those.
    'hodan': {
        'actor': gs.ACTOR,
        'regex': r'lipsync.*civ_(low|mid|high)_f_\d+_(enus|afam)_.*\.anims$',
    },
    # THE THREE IN PERSON, the same way: the civilian pools, by body. All
    # three are invented, so nothing vanilla is exact for them.
    'ligaya': {
        'actor': gs.LIGAYA,
        'regex': r'lipsync.*civ_(low|mid|high)_f_\d+_(enus|afam)_.*\.anims$',
    },
    'stamps': {
        'actor': gs.STAMPS,
        'regex': r'lipsync.*civ_(low|mid|high)_m_\d+_(enus|afam)_.*\.anims$',
    },
    'bayani': {
        'actor': gs.BAYANI,
        'regex': r'lipsync.*civ_(low|mid|high)_m_\d+_(enus|afam)_.*\.anims$',
    },
    # JOHNNY, whose two lines are his own recordings: each takes the
    # animation the game baked for it (gig 03's entry, the same regex).
    'johnny': {
        'actor': gs.JOHNNY_ACTOR,
        'regex': r'lipsync.*\\johnny\.anims$',
    },
}

configure(cache=CACHE, catalogue=CATALOGUE, wolvenkit=WK,
          voice_archive=VOICE_ARCHIVE, characters=CHARACTERS)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--rebuild', action='store_true',
                    help='re-extract the catalogue from the game first')
    ap.add_argument('--remake', action='store_true',
                    help='make every new mouth again, even where the clip and '
                         'the words did not change')
    ap.add_argument('--report', action='store_true',
                    help='list every line, made or copied, and its animation')
    args = ap.parse_args()

    if args.rebuild:
        rebuild_cache()
    catalogue = load_catalogue()
    scenes = [build() for build in gs.ALL_BUILDERS]
    actors = {c['actor'] for c in CHARACTERS.values()}
    lines = mouth_lines(scenes, actors, gv.VOMAP_OUT, RAW, catalogue)
    sets, names = build_mouths(lines, MOD, 'mod' + chr(92) + MOD_NAME,
                               {a: voicetag(a) for a in actors},
                               remake=args.remake)
    _check_actor_names(sets, gs.ALL_BUILDERS)
    if args.report:
        for r in lines:
            print('%-22s %-6s %-6s %s' % (r['scene'], r['key'],
                                          'made' if 'audio' in r else 'copied',
                                          r['name']))

    doc = {
        '_comment': 'GENERATED by tools/gig04/gen_lipsync.py. Do not hand-edit. '
                    'Each actor of each scene has its own lipsync set, made from '
                    'the gig\'s clips and copied from vanilla for whole vanilla '
                    'lines.',
        'sets': sets,
        'lines': names,
    }
    os.makedirs(os.path.dirname(PICKS), exist_ok=True)
    with open(PICKS, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(doc, fh, indent=1, sort_keys=True)
    made = sum('audio' in r for r in lines)
    print('wrote %s (%d lines: %d made, %d copied, across %d scene/actor pairs)'
          % (PICKS, len(lines), made, len(lines) - made,
             sum(len(v) for v in sets.values())))


if __name__ == '__main__':
    main()
