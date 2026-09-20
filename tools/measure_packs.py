r"""Measure every vanilla recording the three gigs reuse, in every dubbed
language on this machine, and cache the lengths.

    python tools\measure_packs.py            # every locale with a pack on disk
    python tools\measure_packs.py de-de      # one locale

Writes tools\_lang_cache\durations_<locale>.json, {hex: {'f': ms, 'm': ms}}.
Each gig's measure_vanilla.py then reads those tables and writes the gig's
committed vanilla_durations.json as the shortest dub of each line, which is
what gen_scenes writes into the scene: the game stretches a line's slot to
the take it plays, so the shortest slot gives every language its own take
(docs/scene-playbook.md, "Other languages"; gotcha 120).

The set of hexes is read off the generators rather than passed in, so a new
`vanilla_sid` is picked up by re-running this. The cut takes (splice_takes.py,
take_vanilla.py) are measured whole as well, for the per-language re-cut
work; their shipped clip is paced from durations.json like any other.
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from questkit import packs                                           # noqa: E402


# Takes cut by hand and listened to, whose ids live only in a comment beside
# the line: Mama's "She's a nice girl.", Nix's "Now, let's get this show
# underway." and "Should take me, I dunno... four, five hours?" (gig 01).
EXTRA_HEXES = ['1b20744eb92d2000', '18a798f5cb4ea000', '2e98cf00dc7e1000']


def reused_hexes():
    hexes = set(EXTRA_HEXES)
    files = (glob.glob(os.path.join(HERE, 'gig0*', 'gen_scenes.py'))
             + glob.glob(os.path.join(HERE, 'gig0*', 'splice_takes.py'))
             + glob.glob(os.path.join(HERE, 'gig0*', 'take_vanilla.py')))
    for f in files:
        with open(f, encoding='utf-8') as fh:
            src = fh.read()
        # Every 16-digit hex literal in the file, however it is passed: as a
        # `vanilla_sid=` keyword, positionally through a helper like gig 01's
        # V2(), or quoted in a splice list. A literal that is not a line
        # simply has no take and is reported as such.
        hexes |= set('%016x' % int(x, 16) for x in re.findall(r"0x([0-9a-fA-F]{16})", src))
        hexes |= set(re.findall(r"'([0-9a-f]{16})'", src))
    return sorted(hexes)


def main():
    locales = sys.argv[1:] or packs.available()
    hexes = reused_hexes()
    print('%d distinct vanilla lines across the gigs' % len(hexes))
    for loc in locales:
        base, ep1 = packs.archives(loc)
        if not base:
            print('%s: no pack on disk, skipped' % loc)
            continue
        table = packs.measure(hexes, loc)
        got = sum(1 for h in hexes if table.get(h))
        print('%s: %d of %d measured%s' % (loc, got, len(hexes),
                                          '' if ep1 else ' (no Phantom Liberty pack)'))
        for h in hexes:
            if not table.get(h):
                print('   no take: ' + h)


if __name__ == '__main__':
    main()
