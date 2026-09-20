r"""Write this gig's vanilla_durations.json: the length of every reused
vanilla line, as the LONGEST of its dubs.

    python tools\gig02\measure_vanilla.py

A section is paced by its line durations and the scene has one timeline for
every language, so a reused line is paced from the longest recording the
player might hear. tools\measure_packs.py measures every voice pack on this
machine into tools\_lang_cache\; this takes the maximum over those and both
bodies and writes it where gen_scenes reads it. The file is committed, so a
clone builds without any pack; with no cache on disk the committed file is
kept. questkit/vanilla_durations.py has the account.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
sys.path.insert(0, HERE)

from questkit import vanilla_durations                               # noqa: E402
from gig02_config import SOURCE                                      # noqa: E402

OUT = os.path.join(SOURCE, 'audio', 'vanilla_durations.json')


def main():
    import gen_scenes as gs
    vanilla_durations.write(gs.ALL_BUILDERS, OUT, getattr(gs, 'estimate_ms', None))


if __name__ == '__main__':
    main()
