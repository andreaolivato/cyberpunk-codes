"""Find map-pin anchors: base-game nodes in the ALWAYS-LOADED sectors.

Usage:
    python tools/find_pin_anchors.py <x> <y> <z> [count]

Prints the nearest globally-named nodes AND their world positions, which is
what `ANCHOR_POS` in tools/gen_journal.py needs. The pin then sits at
`anchor position + offset`, and the generator computes that offset, so the
anchor's distance from the target does not matter - only that its position is
recorded correctly here.

WHY ONLY THE ALWAYS-LOADED SECTORS, which is the whole point of this tool.

ArchiveXL resolves a pin's position through `GetNodeTransform`, and that needs
the node to exist AS AN INSTANCE - its streaming sector must be loaded. A quest
activates its pins while V is on the other side of the city, so an anchor in an
ordinary `exterior_*` sector is not there yet and the pin never appears:

    [Journal] Can't resolve mappin #1684563311 (.../pin_office) position.

Night City has exactly THREE sectors the engine never unloads -
`always_loaded_0/1/2.streamingsector`, `category: AlwaysLoaded` with a
float-max streaming box - holding 5211 globally-named nodes between them.
Those are the only safe anchors, and they are what this scans.

**This file used to scan `exterior_*` sectors instead, and every anchor it ever
recommended is unusable.** It was written when the position came from a patched
copy of the game's cooked mappin tables, where the anchor was only a gate and
its coordinates were irrelevant. That patch is gone (see
docs/map-pins-playbook.md), so the rules changed underneath it.

Do NOT "fix" a missing pin by shipping a marker node of your own. Tried twice on
2026-08-14: a node in a MOD sector never registers its global name
(`Can't resolve ... reference`), and playtesting confirmed Californication and
OneMoreLight, which both do that, have broken pins in game too.

First run extracts and serializes ~90 MB of sector JSON into tools/_anchor_cache
and takes a couple of minutes; after that it is fast.
"""
import json
import math
import os
import re
import subprocess
import sys

CLI = os.path.expandvars(r'%LOCALAPPDATA%\Programs\WolvenKit.CLI\WolvenKit.CLI.exe')
GAME = r'C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077'
ARCHIVE = os.path.join(GAME, r'archive\pc\content\basegame_3_nightcity.archive')
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_anchor_cache')
SECTORS = os.path.join(CACHE, 'base', 'worlds', '03_night_city', '_compiled', 'default')
NAMES = [f'always_loaded_{i}.streamingsector' for i in range(3)]

# Deliberately tolerant of exponent forms: the sectors contain values like
# "-3.81469727E-06", and a regex that stops at the 'E' silently truncates.
NUM = re.compile(r'"([XYZ])":\s*(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)')


def ensure_cache():
    missing = [n for n in NAMES if not os.path.exists(os.path.join(SECTORS, n + '.json'))]
    if not missing:
        return
    print(f'caching {len(missing)} always-loaded sector(s) - first run takes a minute...')
    os.makedirs(CACHE, exist_ok=True)
    subprocess.run([CLI, 'unbundle', ARCHIVE, '-o', CACHE,
                    '-w', '*always_loaded_*.streamingsector'], capture_output=True)
    for n in NAMES:
        raw = os.path.join(SECTORS, n)
        if os.path.exists(raw) and not os.path.exists(raw + '.json'):
            subprocess.run([CLI, 'convert', 'serialize', raw], capture_output=True)


def nodes():
    """Yield (global_name, position) for every '#'-named node, streaming the
    files line by line - always_loaded_1 serializes to ~344 MB."""
    for n in NAMES:
        path = os.path.join(SECTORS, n + '.json')
        if not os.path.exists(path):
            continue
        pos, cur, state = None, {}, None
        with open(path, encoding='utf-8-sig') as fh:
            for line in fh:
                if '"Position"' in line:
                    state, cur = 'pos', {}
                elif state == 'pos':
                    m = NUM.search(line)
                    if m:
                        cur[m.group(1)] = float(m.group(2))
                    if len(cur) == 3:
                        pos, state = (cur['X'], cur['Y'], cur['Z']), None
                if '"QuestPrefabRefHash"' in line:
                    state = 'qph'
                elif state == 'qph' and '"$value"' in line:
                    value = line.split('"$value"')[1].strip(' :"\n,')
                    state = None
                    seg = value.rsplit('/', 1)[-1]
                    if seg.startswith('#') and pos:
                        yield seg, pos, n


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        return
    x, y, z = (float(v) for v in sys.argv[1:4])
    count = int(sys.argv[4]) if len(sys.argv) > 4 else 8

    ensure_cache()
    target = (x, y, z)
    rows = sorted(((math.dist(p, target), name, p, sec)
                   for name, p, sec in nodes()), key=lambda r: r[0])

    if not rows:
        print('no anchors found - is the cache populated?')
        return

    print(f'\nnearest always-loaded anchors to ({x}, {y}, {z}):\n')
    seen = set()
    shown = 0
    for d, name, p, sec in rows:
        if name in seen:
            continue
        seen.add(name)
        print(f'  {d:8.1f} m  {name}')
        print(f'             ANCHOR_POS: ({p[0]:.6f}, {p[1]:.6f}, {p[2]:.6f})   [{sec}]')
        shown += 1
        if shown >= count:
            break
    print('\nPut the name + position in ANCHOR_POS in tools/gen_journal.py and the')
    print('target in PIN_POS; the generator computes the offset between them.')


if __name__ == '__main__':
    main()
