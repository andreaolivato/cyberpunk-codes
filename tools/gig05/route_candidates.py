"""Alternative flight paths for the dev menu's path probe to check in one run.

    python tools\\gig05\\route_candidates.py

Each leg is built several ways (flight_paths.route with other headings,
slopes and straight lengths) and every one is written to the dev menu's
`candidates.lua`, with the settings that made it in
`flights/candidates.txt`. The path probe (dev menu fact 7) sweeps them all
at each of its stops and writes the hits to `route_hits.txt`; a path with
no hits past its two end points is clear of the buildings. A restart of the
game costs four minutes and checks one guess; this checks a dozen.
"""
import itertools
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

from questkit import avflight  # noqa: E402
import gig05_config as cfg  # noqa: E402
import flight_paths  # noqa: E402

CET = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'mods', 'gig-05-trauma-team',
                   'source', 'cet-dev', 'candidates2.lua')

LEGS = {
    # Round 2 (2026-11-03): round 1 found every way into the coast street
    # at 0.12 touching the buildings east of the hotel at 40 to 80 m, and
    # b5, c1 to c4 clear. The glide probe has the street open to the east
    # at 28 degrees, so these come in steeper and turn higher.
    'a': ('flight_rec_1.txt', cfg.SITE1, cfg.SITE2,
          dict(sy=[cfg.SITE1_YAW, 180.0, 220.0], ey=[95.0, 100.0], climb=[0.25],
               descent=[0.25, 0.32], out_len=[100.0], in_len=[180.0, 220.0])),
    'b': ('flight_rec_5.txt', cfg.SITE2, cfg.SITE3,
          dict(sy=[-75.0], ey=[-30.0], climb=[0.12], descent=[0.45],
               out_len=[150.0], in_len=[180.0])),
    'c': ('flight_rec_4.txt', cfg.SITE3, cfg.PAD,
          dict(sy=[20.0, 30.0], ey=[cfg.PAD_YAW], climb=[0.36], descent=[0.3],
               out_len=[150.0], in_len=[200.0])),
}


def build():
    out = {}
    for leg, (rec, start, end, grid) in LEGS.items():
        keys = list(grid)
        for n, combo in enumerate(itertools.product(*(grid[k] for k in keys)), 1):
            kw = dict(zip(keys, combo))
            sy, ey = kw.pop('sy'), kw.pop('ey')
            pts = flight_paths.route(rec, start, sy, end, ey, **kw)
            out['%s%d' % (leg, n)] = (dict(sy=sy, ey=ey, **kw), pts)
    return out


def write(paths):
    lines = ['-- Written by tools/gig05/route_candidates.py. Do not edit.', 'return {']
    for name, (_kw, pts) in paths.items():
        curve = [tuple(round(v, 1) for v in p) for p in avflight.sample(pts, 8.0)]
        lines.append('  %s = {%s},' % (name, ', '.join('{%s, %s, %s}' % p for p in curve)))
    lines.append('}')
    with open(CET, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('\n'.join(lines) + '\n')
    with open(os.path.join(HERE, 'flights', 'candidates.txt'), 'w', encoding='utf-8',
              newline='\n') as fh:
        for name, (kw, pts) in paths.items():
            fh.write('%s %s %.0f m\n' % (name, kw, avflight.length(pts)))
    print('wrote', CET, len(paths), 'paths')


if __name__ == '__main__':
    write(build())
