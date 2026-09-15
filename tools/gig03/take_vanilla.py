r"""Acceptable Loss's shipped clips: three lines cut out of recordings the
game already made, one of Johnny's and two of Dino's.

    python tools\gig03\take_vanilla.py

Everything Dino says in this gig is one of his own recordings. Most lines
point at the game's clip directly with `vanilla_sid`, and the game plays it.
The ones below are takes that carry the wanted words after or before words
that belong to another gig ("Joanne Koch's still breathin'", "Supposed to
end Mausser"), so each is cut at a pause and shipped as a clip of ours, under
this gig's own line id.

THE CALL NEEDS NO CLIP OF OURS ANY MORE. Regina's job line had to be joined
from two open-world barks and phone-treated by hand, because the game never
recorded a phone version of a bark (gotcha 41). Dino's three call lines are
gig hires with a `vo_holocall` twin each, so `vanilla_sid` plays them
filtered for free. The join route (level-matched pieces, CALL_RMS_DBFS, the
phone treatment in gen_voice.py) stays in this file for the next line that
needs it.

A cut line gets NO exact lipsync animation. Vanilla baked one per whole
recording, and a clip cut short is not that recording; gen_lipsync casts it
by length like a recorded take (gotcha 59).

LISTEN TO EVERY CUT before shipping it: a cut off a silence map can land one
pause early and the waveform gives nothing away (questkit/splice writes each
piece out as `trim__<label>.wav` for exactly that).

This file copies the takes into source/audio/ under the names gen_voice
expects. The clip comes out of the voice archive through `vo_corpus.export`
and lands under tools\_splice_cache\ first, which is extracted game data and
never committed; the WAV written here IS committed, the same as any recorded
take, so a clone builds without the game installed.
"""
import os
import sys

import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
sys.path.insert(0, HERE)

from questkit import splice                                          # noqa: E402
from gig03_config import SOURCE                                      # noqa: E402

AUDIO = os.path.join(SOURCE, 'audio')

# (scene, key, stringId) for every WHOLE vanilla take this gig ships as its
# own clip. None today; the list stays so a whole take can come back without
# rebuilding the route. gen_lipsync.WHOLE_TAKES reads it for the exact
# animation names.
TAKES = [
]

# (scene, key, [(stringId, cut, words), ...]) for every line CUT from a take
# or JOINED from pieces of several. `cut` is a questkit.splice mode: keep_head
# keeps everything before the first pause, drop_head everything after it;
# ('at', seconds) keeps everything AFTER a fixed time, and ('to', seconds)
# everything BEFORE one, for a cut the pause map cannot place on its own.
#
# A join of several pieces is levelled to CALL_RMS_DBFS below and joined with
# the same-speaker gap. A single-piece trim is NOT levelled: it plays beside
# vanilla lines in the flat, and the game's own level is the level to keep.
#
# EVERY ONE OF THESE WAS LISTENED TO before it shipped. The cut times are
# written beside each so the next person can check them against the piece
# without re-deriving the pause map.
JOINS = [
    # THE WIPE. Johnny's line opens on "But", which answers nothing here. No
    # pause follows it, so the cut is at a fixed 0.50 s, in the dip between
    # "But" (0.33 to 0.48 s on the envelope) and "give" (from 0.53 s).
    ('gig03_destroy', 'j02', [
        (0x1a585e1a493bc000, ('at', 0.50),
         "Give up your ideals, and no amount of eddies can buy 'em back."),
    ]),
    # THE SAME CUT AGAIN for the other ending's Johnny scene (the design
    # call, 2026-09-15): a shipped clip is keyed by scene and line, so the
    # bring-it scene gets its own copy.
    ('gig03_object', 'j02', [
        (0x1a585e1a493bc000, ('at', 0.50),
         "Give up your ideals, and no amount of eddies can buy 'em back."),
    ]),
    # HIS BAR, ending B. The Joanne Koch failure debrief opens "You fucked
    # up, V." and then names her; the pause map of the take (8.66 s) has a
    # 0.8 s silence at 1.34 to 2.14 s after the name, so the head is kept to
    # 1.9 s and the edges trimmed. The Mausser failure debrief ends "Sorry,
    # no cred for that move." after its one internal pause (3.16 to 3.76 s),
    # so drop_head takes the tail.
    ('gig03_dino_bar_loud', 'd02', [
        (0x2051128efd69e000, ('to', 1.90), "You fucked up, V."),
    ]),
    ('gig03_dino_bar_loud', 'd03', [
        (0x206142349f3bc000, 'drop_head', "Sorry, no cred for that move."),
    ]),
]


# THE LEVEL A JOINED CALL LINE IS BROUGHT TO, measured 2026-09-15 off the
# game's own phone versions of three of Regina's call lines: voiced rms
# -24.0, -24.4 and -26.9 dBFS, mean -25.1. The phone treatment matches its
# output to the source's rms and lands about 0.7 dB under it, and a join's
# gaps pull the whole-file reading down a further 0.8 dB, so pieces are
# levelled to -23.6 here and the treated line comes out at -25.1. The first
# build levelled a join to the splice tool's fixed target (-27 dBFS), and
# playtest heard it, 3.3 dB under the lines around it. No join ships today;
# the number stays for the next one.
CALL_RMS_DBFS = -23.6


def level_to(x, dbfs):
    """Scale so the voiced-frame rms sits at `dbfs`."""
    r, _w = splice._frames(x)
    voiced = r[r > r.max() * 0.1]
    m = float(voiced.mean()) if len(voiced) else float(r.mean())
    return x * (10 ** (dbfs / 20.0) / m) if m > 0 else x


def shipped():
    """Every (scene, key) that ships a clip of ours, whole or joined. gen_voice
    and gen_lipsync both read this, so the three cannot drift."""
    return [(s, k) for s, k, _sid in TAKES] + [(s, k) for s, k, _p in JOINS]


def main():
    os.makedirs(AUDIO, exist_ok=True)
    hexes = ['%016x' % sid for _s, _k, sid in TAKES]
    hexes += ['%016x' % sid for _s, _k, pieces in JOINS for sid, _m, _t in pieces]
    have = splice.vanilla(hexes, 'f')
    missing = []
    for scene, key, sid in TAKES:
        src = have.get('%016x' % sid)
        if not src:
            missing.append('%s/%s' % (scene, key))
            continue
        # WHOLE. No edge trim and no level match: this is the game's take as
        # the game plays it, and the phone treatment matches level itself.
        x = splice.load(src)
        out = os.path.join(AUDIO, '%s__%s.wav' % (scene, key))
        sf.write(out, x, splice.RATE, subtype='PCM_16')
        print('wrote %s  (%.2f s)' % (out, len(x) / splice.RATE))
    for scene, key, pieces in JOINS:
        seq = []
        for i, (sid, mode, words) in enumerate(pieces):
            src = have.get('%016x' % sid)
            if not src:
                missing.append('%s/%s piece %d' % (scene, key, i))
                continue
            x = splice.load(src)
            if len(pieces) > 1:
                x = level_to(x, CALL_RMS_DBFS)
            label = '%s_%s_%d' % (scene, key, i)
            if isinstance(mode, tuple) and mode[0] in ('at', 'to'):
                if mode[0] == 'at':
                    y = splice.trim_edges(x[int(mode[1] * splice.RATE):])
                else:
                    y = splice.trim_edges(x[:int(mode[1] * splice.RATE)])
                check = os.path.join(splice.CACHE, 'trim__%s.wav' % label)
                sf.write(check, y, splice.RATE, subtype='PCM_16')
                print('%-16s %s %.2fs of %.2fs' % (label, mode[0], mode[1],
                                                   len(x) / splice.RATE))
                print('%-16s wanted: "%s"' % ('', words))
                print('%-16s listen: %s' % ('', check))
            else:
                y = splice.cut(x, mode, label, words)
            seq.append(('one', y))
        if len(seq) == len(pieces):
            splice.assemble(seq, os.path.join(AUDIO, '%s__%s.wav' % (scene, key)))
    if missing:
        raise SystemExit('no plain take found for: ' + ', '.join(missing))


if __name__ == '__main__':
    main()
