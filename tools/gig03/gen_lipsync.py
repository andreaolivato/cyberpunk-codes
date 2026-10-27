r"""Gives every line in this gig that has a mouth on screen its lipsync
animation, and writes source/lipsync_picks.json.

    python tools\gig03\gen_lipsync.py            # make what changed, assemble the sets
    python tools\gig03\gen_lipsync.py --remake   # make every new mouth again
    python tools\gig03\gen_lipsync.py --rebuild  # re-extract the catalogue first
    python tools\gig03\gen_lipsync.py --report   # list every line and its animation

Each actor of each scene gets one lipsync set of the gig's own, at
`mod\acceptable_loss\localization\en-us\lipsync\<scene>\<actor>.anims`:

- MADE. The cut lines (take_vanilla.py) ship a clip of ours, and each gets a
  mouth made from that clip and its words by the lipsync animator, named
  `f_<the line's RUID>`.
- COPIED. Every other line is a whole vanilla line, and plays the animation
  CDPR baked for it, copied out of whichever vanilla set holds it.

Copying from any number of vanilla sets is what ends the old one-set-per-scene
trade. The loud bar scene used to be cast by length alone, because the one set
holding Dino's whole lines exactly had nothing short enough for his cuts.

The made animations are committed under `source\lipsync\`; the assembled sets
carry CDPR's copies, so they are built from the installed game and never
committed. The whole chain is in tools/gig01/gen_lipsync.py and
tools/questkit/lipsync.py, "our own mouths".

WITHOUT THIS FILE THE MOUTHS DO NOT MOVE. A line with no pick goes out with an
empty animation name and nothing errors: playtest, 2026-09-10, "holo works, but
there's no lipsync". gen_scenes stops the build when a speaker on screen has no
pick.

===========================================================================
THREE MOUTHS ARE SEEN, AND V'S IS NOT ONE OF THEM
===========================================================================

Dino on the phone, Dino at his bar, and Johnny beside V and at the door. V IS
NOT HERE AND MUST NOT BE: V is the player, the camera is behind V's eyes, and
there is no mouth to move.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from questkit.lipsync import (                                      # noqa: E402
    configure, load_catalogue, rebuild_cache, _check_actor_names,
    mouth_lines, build_mouths, voicetag,
)
import questkit.scene as qs                                          # noqa: E402

import gen_scenes as gs                                              # noqa: E402
import gen_voice as gv                                               # noqa: E402
from gig03_config import REPO, SOURCE, MOD, RAW, MOD_NAME            # noqa: E402

CACHE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     '_lipsync_cache')
# Named after the gig: a shared catalogue is a rebuild that silently breaks
# another gig (tools/gig02/gen_lipsync.py says how).
CATALOGUE = os.path.join(CACHE, 'catalogue_gig03.json')

GAME = r'C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077'
WK = os.path.expandvars(r'%LOCALAPPDATA%\Programs\WolvenKit.CLI\WolvenKit.CLI.exe')
VOICE_ARCHIVE = os.path.join(GAME, 'archive', 'pc', 'content',
                             'lang_en_voice.archive')
# Johnny at the door on the loyal ending is a Phantom Liberty line, so its
# animation is in the expansion's voice archive (gotcha 118).
EP1_VOICE_ARCHIVE = os.path.join(GAME, 'archive', 'pc', 'ep1',
                                 'lang_en_voice.archive')

PICKS = os.path.join(SOURCE, 'lipsync_picks.json')

# The catalogue these patterns build is where a whole vanilla line's own
# animation is found, so each has to reach the character's own sets.
CHARACTERS = {
    'johnny': {
        'actor': qs.JOHNNY_ACTOR,
        'regex': r'lipsync.*\\johnny\.anims$',
    },
    'dino': {
        'actor': 'dino',
        'regex': r'lipsync.*\\dino_dyno_dinovic\.anims$',
    },
}

configure(cache=CACHE, catalogue=CATALOGUE, wolvenkit=WK,
          voice_archive=VOICE_ARCHIVE, characters=CHARACTERS,
          extra_archives=[EP1_VOICE_ARCHIVE])


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
        '_comment': 'GENERATED by tools/gig03/gen_lipsync.py. Do not hand-edit. '
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
