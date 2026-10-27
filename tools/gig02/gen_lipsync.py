r"""Gives every line in this gig that has a mouth on screen its lipsync
animation, and writes source/lipsync_picks.json.

    python tools\gig02\gen_lipsync.py            # make what changed, assemble the sets
    python tools\gig02\gen_lipsync.py --remake   # make every new mouth again
    python tools\gig02\gen_lipsync.py --rebuild  # re-extract the catalogue first
    python tools\gig02\gen_lipsync.py --report   # list every line and its animation

Each actor of each scene gets one lipsync set of the gig's own, at
`mod\dead_ringer\localization\en-us\lipsync\<scene>\<actor>.anims`:

- MADE. A line the gig ships a clip for (Wakako's cut lines, the merc, Char,
  the three outside the car) gets a mouth made from that clip and its words
  by the lipsync animator, named `f_<the line's RUID>`.
- COPIED. A whole vanilla line plays the animation CDPR baked for it, copied
  out of whichever vanilla set holds it.

The made animations are committed under `source\lipsync\`; the assembled sets
carry CDPR's copies, so they are built from the installed game and never
committed. The whole chain is in tools/gig01/gen_lipsync.py and
tools/questkit/lipsync.py, "our own mouths".

Run it AFTER gen_voice.py (it reads the clips and the voiceover map) and BEFORE
gen_scenes.py (which reads the picks file).

===========================================================================
THIS GIG HAS ITS OWN CATALOGUE FILE, AND THAT MATTERS
===========================================================================

`rebuild_cache()` extracts exactly the sets the CAST's regexes match and writes
them over whatever the catalogue held before. A gig 02 rebuild into a file
shared with gig 01 would replace gig 01's catalogue with one built from this
cast, and gig 01's whole vanilla lines would lose the sets their animations
are copied from. Silently, on the next run of a generator nobody thought they
had touched.

So the file is named after the gig, exactly as the config module is. Both
catalogues are extraction scratch: gitignored, and about forty seconds to
rebuild.
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
    mouth_lines, build_mouths, voicetag, LIPMAP_DEPOT,
)
from gig02_config import REPO, SOURCE, MOD, RAW, MOD_NAME           # noqa: E402

CACHE = os.path.join(REPO, 'tools', '_lipsync_cache')
# NAMED AFTER THE GIG. See the module docstring: a shared catalogue is a
# rebuild that silently breaks another gig.
CATALOGUE = os.path.join(CACHE, 'catalogue_gig02.json')
# The small, readable, COMMITTED result: which animation and which set each
# line uses. gen_scenes reads this, so a clone can generate the scenes with no
# game installed. Packing the archive still needs the assembled sets.
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
# character -> who gets a mouth, and where their vanilla animations are.
#
#   actor    the actorName gen_scenes gives that speaker. gen_scenes looks the
#            pick up by (scene, actorName), so the two strings must agree, and
#            _check_actor_names() fails the run if they ever drift.
#   regex    passed to WolvenKit's `unbundle -r`, matched against the full depot
#            path inside lang_en_voice.archive. The catalogue it builds is where
#            a whole vanilla line's own animation is found, so it has to reach
#            every set that holds one of this gig's whole lines.
#
# V IS NOT HERE AND MUST NOT BE. He is the player, the camera is behind his
# eyes, and there is no mouth to move.
#
# The civilian pools below date from length casting, when a bigger pool meant a
# closer length. They are kept because they also reach the sets that hold the
# whole lines; a narrower pattern would need a --rebuild and a check that
# every copied line is still found.
CHARACTERS = {
    'johnny': {
        'actor': gs.JOHNNY_ACTOR,
        'regex': r'lipsync.*\\johnny\.anims$',
    },
    # The game ships a `wakako_okada.anims` per scene she speaks in, and her
    # reused lines were baked in sets named for whoever else was in the room,
    # so the pattern admits `wakako.*`.
    'wakako': {
        'actor': 'wakako',
        'regex': r'lipsync.*(civ_(low|mid|high)_f_\d+_(jap|chn)_\d+|wakako.*)\.anims$',
    },

    # The five strangers outside Afterlife. Each one is a real vanilla voice
    # speaking one of its own recorded lines, so the pool is that voice's own
    # sets and the exact animation is in it.
    'queue_a': {'actor': 'queue_a', 'regex': r'lipsync.*civ_mid_m_21_enus_25\.anims$'},
    'queue_b': {'actor': 'queue_b', 'regex': r'lipsync.*civ_mid_m_34_afam_25\.anims$'},
    'queue_c': {'actor': 'queue_c', 'regex': r'lipsync.*civ_mid_m_04_enus_30\.anims$'},
    'queue_d': {'actor': 'queue_d', 'regex': r'lipsync.*civ_high_f_09_afam_30\.anims$'},
    'queue_e': {'actor': 'queue_e', 'regex': r'lipsync.*civ_mid_m_42_mex_40\.anims$'},

    # The six acquired from the community. The trailing `.*` matters: some
    # voice tags carry a district after the age (`civ_mid_f_62_jap_40_kabuki`)
    # and a pattern ending at `_\d+` misses every one of those.
    'merc': {
        'actor': 'merc',
        'regex': r'lipsync.*civ_(low|mid|high)_m_\d+_(enus|afam)_.*\.anims$',
    },
    'char': {
        'actor': 'char',
        'regex': r'lipsync.*civ_(low|mid|high)_f_\d+_(enus|afam)_.*\.anims$',
    },
    'yoko': {
        'actor': 'yoko',
        'regex': r'lipsync.*civ_(low|mid|high)_f_\d+_(jap|chn)_.*\.anims$',
    },
    'ideka': {
        'actor': 'ideka',
        'regex': r'lipsync.*civ_(low|mid|high)_f_\d+_(jap|chn)_.*\.anims$',
    },
    'huscle': {
        'actor': 'huscle',
        'regex': r'lipsync.*civ_(low|mid|high)_m_\d+_(jap|chn)_.*\.anims$',
    },
    'toji': {
        'actor': 'toji',
        'regex': r'lipsync.*civ_(low|mid|high)_m_\d+_(jap|chn)_.*\.anims$',
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
        '_comment': 'GENERATED by tools/gig02/gen_lipsync.py. Do not hand-edit. '
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
