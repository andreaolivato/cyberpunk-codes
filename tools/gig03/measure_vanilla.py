r"""Measure every reused vanilla line this gig's scenes point at, and write
the lengths where gen_scenes paces sections from.

    python tools\gig03\measure_vanilla.py

WHY. A scene section is paced by its line durations: each line's event starts
where the previous one ends, and the section (and everything timed off its
end, like Johnny's exit flash) closes at the sum. A line the gig ships a clip
for is paced by that clip's measured length (durations.json). A line pointed
at the game's own recording with `vanilla_sid` was paced by an ESTIMATE from
its text, 1200 ms plus 55 ms a character, and the estimate is short for V:
"Not now, Johnny." estimates at 2.0 s and runs 3.4 s (4.0 s for the male
body), so Johnny's next line started while V was still talking, and in the
bring-it scene V's last line ran on past the section's end, so the exit
flash fired over the words and the body was gone the moment they stopped.
Playtest 2026-09-15: "almost seen him disappear without glitch".

WHAT. Every builder is run, every reused line's stringId collected, and both
bodies' takes pulled out of the voice archive (the ones the game has; Johnny
and Dino have one, V has two). The longer of the two is written, so neither
V overruns. gen_scenes merges this file into MEASURED under the same
'scene/key' the shipped clips use, and line_ms pads it the same 350 ms.

THE FILE IS COMMITTED, like durations.json, so a clone builds without the
game installed. Run this whenever a `vanilla_sid` changes; gen_scenes warns
on a reused line it has no length for and paces that one by the estimate.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
sys.path.insert(0, HERE)

from questkit import splice                                          # noqa: E402
from gig03_config import SOURCE                                      # noqa: E402

OUT = os.path.join(SOURCE, 'audio', 'vanilla_durations.json')


def main():
    import gen_scenes as gs
    if not os.path.exists(splice.vo_corpus.CLI):
        # A clone without the game: the committed file stands.
        print('WolvenKit CLI not found; keeping %s as committed' % OUT)
        return
    wanted, text = {}, {}
    for build in gs.ALL_BUILDERS:
        scene = build()
        for key, sid, t in scene.reused:
            wanted['%s/%s' % (scene.name, key)] = '%016x' % int(sid)
            text['%s/%s' % (scene.name, key)] = t
    hexes = sorted(set(wanted.values()))
    length = {}
    for gender in ('f', 'm'):
        have = splice.vanilla(hexes, gender)
        for h, path in have.items():
            ms = int(round(len(splice.load(path)) * 1000.0 / splice.RATE))
            length[h] = max(length.get(h, 0), ms)
    out, missing = {}, []
    for sk, h in sorted(wanted.items()):
        if h in length:
            out[sk] = length[h]
        else:
            missing.append(sk)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print('wrote %s (%d line(s))' % (OUT, len(out)))
    for sk in out:
        print('   %-28s %5d ms  (the estimate was %d)'
              % (sk, out[sk], gs.estimate_ms(text[sk])))
    if missing:
        print('no take found for: ' + ', '.join(missing))


if __name__ == '__main__':
    main()
