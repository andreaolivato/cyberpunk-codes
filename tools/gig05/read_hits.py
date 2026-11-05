r"""Which flight paths the dev menu's path probe found clear.

    python tools\gig05\read_hits.py [route_hits.txt]

Reads the probe's `route_hits.txt` (from the game's dev menu folder by
default) and prints, for every path it swept, the stretches that hit a
building. A hit within 15 m of either end of a path is the AV's own landing
spot under it and is left out.
"""
import collections
import math
import os
import sys

GAME = r'C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077'
DEFAULT = os.path.join(GAME, 'bin', 'x64', 'plugins', 'cyber_engine_tweaks', 'mods',
                       'trauma_team_dev', 'route_hits.txt')


def load_paths():
    """Every path the probe saw, from routes.lua and candidates.lua."""
    import re
    here = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                        'mods', 'gig-05-trauma-team', 'source', 'cet-dev')
    paths = {}
    for f in ['routes.lua', 'candidates.lua'] + ['candidates%d.lua' % k for k in range(2, 10)]:
        p = os.path.join(here, f)
        if not os.path.exists(p):
            continue
        for m in re.finditer(r'^\s*(\w+) = \{(\{.*\})\},?$', open(p, encoding='utf-8').read(), re.M):
            try:
                pts = [tuple(float(v) for v in t.split(','))
                       for t in re.findall(r'\{([^{}]*)\}', m.group(2))]
            except ValueError:
                continue
            if pts and len(pts[0]) == 3:
                paths[m.group(1)] = pts
    return paths


def main(path):
    paths = load_paths()
    hits = collections.defaultdict(list)
    for line in open(path, encoding='utf-8'):
        parts = line.split()
        if len(parts) != 6:
            continue
        name, i, x, y, z, off = parts[0], int(parts[1]), *map(float, parts[2:5]), parts[5]
        pts = paths.get(name)
        if pts and (math.dist((x, y, z), pts[0]) < 15 or math.dist((x, y, z), pts[-1]) < 15):
            continue
        hits[name].append((i, x, y, z, off))
    for name in sorted(paths, key=lambda n: (n[0], len(n), n)):
        h = hits.get(name, [])
        if not h:
            print('%-6s clear' % name)
            continue
        idx = sorted({e[0] for e in h})
        where = ', '.join('%d (%.0f %.0f %.0f)' % (e[0], e[1], e[2], e[3])
                          for e in sorted({e[0]: e for e in h}.values()))
        print('%-6s %d hits at points %s' % (name, len(h), where))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT)
