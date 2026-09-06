r"""Dead Ringer's cut vanilla lines: the takes that are trimmed at a pause.

    python tools\gig02\splice_takes.py

Everything Wakako, Yoko, V and Johnny say in this gig is a whole recorded game
line pointed at by `vanilla_sid` in gen_scenes, EXCEPT the five below, where
the wanted words sit inside a longer take and one cut at a pause frees them.
The cutting itself is `questkit.splice`; this file is only the list.

EVERY CUT IS PICKED BY DURATION AND MUST BE LISTENED TO. The pause map gives
several candidate cut points and this picks the one whose remainder is closest
to the length the wanted words should take. That is a guess about where the
pause is, not a proof: gig 01 once cut "Look, I'll pay." down to "Look" and
the waveform looked fine. Each result is written twice: as `trim__<key>.wav`
under tools\_splice_cache\ for listening, and as `<scene>__<key>.wav` in this
gig's audio folder, which is what gen_voice converts.

A V line is cut in BOTH bodies when one is cut: he is a different actor per
body, and a male take can be worded slightly differently, so each cut lands
on its own pause map.
"""
import os
import sys

import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
REPO = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)

from questkit import splice as g1                                    # noqa: E402

AUDIO = os.path.join(REPO, 'mods', 'gig-02-dead-ringer', 'source', 'audio')

# (scene, key, hex, gender, wanted words, mode chain)
#
# A chain is applied left to right. 'drop_head' removes everything before the
# chosen pause; 'keep_head' keeps everything before it. Two of them pull a
# sentence out of the middle of a take.
CUTS = [
    # V's cut for the merc scene (`gig02_merc`, v60) left with that scene on
    # 2026-09-03; the entry outlived it here until 2026-09-05, when a re-run
    # recreated two wavs nothing converts and the build's guard refused.
    # THE HIRE, 2026-09-03: her gig-briefing line begins "V, I need you to
    # acquire something." and this gig retrieves nothing, so the head goes and
    # what is left is this gig in her own words. And the opener is the first
    # sentence of a line that goes on to talk about planting bugs.
    # PAUSE NAMED, 2026-09-03: picked by length this landed one pause late and
    # the clip started at "no client". Playtest heard it. Pause 1 is the one
    # after "acquire something."
    ('gig02_wakako_call', 'w44', '205355685270a000', 'f',
     'Only me, no client – so I expect quick and clean results.', [('drop_head', 1)]),
    ('gig02_wakako_call', 'w45', '2051c518933bb000', 'f',
     'I need someone for a quick and quiet operation.', ['keep_head']),
    # "Putting this one on hold for you. You're the only one I trust with it."
    # loses its first sentence, on the design call of 2026-09-03.
    ('gig02_wakako_call', 'w46', '1ae33bb9ae5f902c', 'f',
     "You're the only one I trust with it.", ['drop_head']),
    # THE OFFICE, REWRITTEN 2026-09-05 (design review): "So tell me." is the
    # head of a line that goes on to threaten with her phone, and the
    # disbelief before "He would not dare go against me." is that line's own
    # first sentence, so the cut keeps two sentences and drops the brief.
    ('gig02_office', 'w47', '1a6c57ad44404000', 'f',
     'So tell me.', ['keep_head']),
    ('gig02_office', 'w41', '20844dc7d7559000', 'f',
     'Something must have happened. He would not dare go against me.', ['keep_head']),
    # THE OFFICE ORDER, 2026-09-05: her praise for a discreet divorce job
    # ends the order as a demand; the cut keeps the head, before the dash.
    ('gig02_office', 'w50', '20510a6152513000', 'f',
     'Discreet and with finesse.', ['keep_head']),
    ('gig02_close_clean', 'w42', '2051cc193b3bb000', 'f',
     'You entered and left like a ghost, V.', ['keep_head']),
    ('gig02_close_loud', 'w43', '2051cc719f3bb000', 'f',
     'You were to do this quietly. It was anything but.', ['keep_head']),
]


def expected_seconds(words):
    return 0.33 * len(words.split()) + 0.35


def best_cut(x, mode, label, expect):
    """Try every internal pause for this mode and keep the remainder whose
    length is closest to what the words should take."""
    total = len(x) / g1.RATE
    sils = [s for s in g1.silences(x) if s[0] > 0.35 and s[1] < total - 0.25]
    if not sils:
        raise SystemExit('%s: no internal pause to cut at' % label)
    want = expected_seconds(expect)
    best = None
    for idx in range(len(sils)):
        if mode == 'drop_tail' and idx:
            break
        y = g1.cut(x, mode, '%s_try%d' % (label, idx), expect, idx=idx)
        secs = len(y) / g1.RATE
        score = abs(secs - want)
        print('    pause %d -> %.2f s (want ~%.2f s)' % (idx, secs, want))
        if best is None or score < best[0]:
            best = (score, idx, y)
    print('    picked pause %d' % best[1])
    return best[2]


def main():
    os.makedirs(AUDIO, exist_ok=True)
    for scene, key, hx, gender, words, chain in CUTS:
        clips = g1.vanilla([hx], gender)
        if hx not in clips:
            raise SystemExit('%s/%s: no %s-body take for %s' % (scene, key, gender, hx))
        x = g1.load(clips[hx])
        label = '%s__%s%s' % (scene, key, '__m' if gender == 'm' else '')
        print('== %s  "%s"' % (label, words))
        for step in chain:
            if isinstance(step, tuple):
                mode, idx = step
                x = g1.cut(x, mode, '%s_%s%d' % (label, mode, idx), words, idx=idx)
                print('    %s at pause %d (named) -> %.2f s' % (mode, idx, len(x) / g1.RATE))
            else:
                x = best_cut(x, step, label, words)
        x = g1.rms_norm(g1.trim_edges(x))
        listen = os.path.join(g1.CACHE, 'trim__%s.wav' % label)
        sf.write(listen, x, g1.RATE, subtype='PCM_16')
        out = os.path.join(AUDIO, label + '.wav')
        sf.write(out, x, g1.RATE, subtype='PCM_16')
        print('    wrote %s (%.2f s)' % (out, len(x) / g1.RATE))
        print('    listen: %s' % listen)


if __name__ == '__main__':
    main()
