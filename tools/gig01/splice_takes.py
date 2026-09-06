r"""Assemble Negative Balance's vanilla voice clips into a scene mock.

    python tools\gig01\splice_takes.py elena_call

Recasting a character out of their own recordings means writing every one of
their lines from the audio the game already shipped: whole takes where one
fits, and a single cut inside a take where the wanted words sit inside a
longer line. `new-gig.md` section 6 has the method; the pick made for each
line here is in the comment beside it in `gen_scenes.py`.

THE CUTTING ITSELF LIVES IN `questkit.splice` since 2026-09-06, because gig 02
needs the same knife. This file is the one assembled mock that is gig 01's.

LISTEN TO EVERY CUT BEFORE YOU USE IT. Each one is written out as
`trim__<label>.wav` for exactly that. A cut point chosen off a silence map can
land one pause early and the mistake is inaudible in the waveform: a clip meant
to say "Look, I'll pay." once came out as "Look", and nothing about the file
looked wrong.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
REPO = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)

from questkit.splice import (                                        # noqa: E402
    CACHE, assemble, cut, load, rms_norm, trim_edges, vanilla,
)

AUDIO = os.path.join(REPO, 'mods', 'gig-01-negative-balance', 'source', 'audio')


# ----------------------------------------------------- the approved elena call
def build_elena_call(gender='f'):
    """The approved v4 mock. Every pick below was auditioned in the scene."""
    clips = vanilla(['197527fc222ef000', '19124b2278623000', '198010978c3bc000',
                     '178629817529f000', '1a58ecd70c2c5000', '196fda3a803bc000',
                     '1ab375df4c44d000', '19d79031063bc000', '168590edca351000'],
                    gender)

    def V(h):
        return rms_norm(trim_edges(load(clips[h])))

    def E(key):
        return rms_norm(trim_edges(load(
            os.path.join(AUDIO, 'gig01_elena_call__%s.wav' % key))))

    like_mama = rms_norm(cut(load(clips['197527fc222ef000']), 'drop_head',
                             'like_mama', 'Like Mama Welles? Thought I recognized the name.'))
    ok_full = cut(load(clips['198010978c3bc000']), 'drop_head', 'ok_didthey',
                  'Are you OK? Did they do anything to you?')
    are_you_ok = rms_norm(cut(ok_full, 'keep_head', 'are_you_ok', 'Are you OK?'))
    gonna_ok = rms_norm(cut(load(clips['178629817529f000']), 'drop_head',
                            'gonna_ok', "Everything's gonna be OK."))

    assemble([
        ('e', E('e01')), ('e', E('e02')),
        ('v', like_mama),
        ('e', E('e03')),
        ('v', V('19124b2278623000')),        # Go on, then. Let's hear it.
        ('e', E('e04')), ('e', E('e05')), ('e', E('e06')),
        ('v', are_you_ok),
        ('e', E('e07')),
        ('v', gonna_ok),
        ('e', E('e07b')),                    # Maybe... maybe I could go to El Coyote?
        ('v', V('1a58ecd70c2c5000')),        # Good idea.
        ('v', V('196fda3a803bc000')),        # I'll see what I can do.
        ('e', E('e08')),
        ('v', V('1ab375df4c44d000')),        # Got it.
        ('v', V('19d79031063bc000')),        # Wait... what?
        ('j', V('168590edca351000')),        # 'Cause it always is Arasaka.
    ], os.path.join(CACHE, 'elena_call_mock_%s.wav' % gender))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('scene', choices=['elena_call'])
    ap.add_argument('--gender', choices=('f', 'm'), default='f',
                    help='which V body reads the vanilla clips (default f)')
    args = ap.parse_args()
    build_elena_call(args.gender)


if __name__ == '__main__':
    main()
