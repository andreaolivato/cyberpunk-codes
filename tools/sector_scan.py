r"""Scan the game's streaming sectors for named content, citywide.

    python tools\sector_scan.py extract
    python tools\sector_scan.py scan arasaka
    python tools\sector_scan.py index arasaka

`extract` unbundles every .streamingsector from the base and (when present)
Phantom Liberty world archives. `scan` byte-searches the extracted files for a
needle and lists the sectors that contain it, interiors flagged. `index` goes
the whole way: it converts the hit sectors, decodes every node whose
serialized form mentions the needle, and writes two files next to this tool
in `_sector_cache`:

    index_<needle>.json   every hit node: x, y, z, name, sector, source
    index_<needle>.csv    the same rows, for a spreadsheet

Positions come from each sector's `nodeData` entries, which store PLAIN float
Vector4 positions. (The fixed-point `Bits` encoding exists elsewhere in these
files; applying its divisor here silently zeroes everything, which cost one
whole pass to discover.)

Two more lessons are load-bearing in the implementation:

- The converter pays its full startup cost per invocation, so hit sectors are
  STAGED into one folder per source and converted with a single call each.
  A per-file loop turned a 220-sector pass into an hour.
- Base and Phantom Liberty share sector FILENAMES. Their extractions and
  their conversions are kept in separate directories, or the outputs
  overwrite each other and the source of a finding becomes unknowable.

The extracted sectors are game data: gigabytes, rebuildable on demand, never
committed, and kept OUTSIDE the repo tree, so that a folder sync or a backup
does not try to carry them. Only the small index files land in
`tools\_sector_cache`, which is gitignored like the other caches.
"""
import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys

CLI = os.path.expandvars(r'%LOCALAPPDATA%\Programs\WolvenKit.CLI\WolvenKit.CLI.exe')
GAME = r'C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077'
HERE = os.path.dirname(os.path.abspath(__file__))
INDEX_DIR = os.path.join(HERE, '_sector_cache')
HEAVY = os.path.expandvars(r'%LOCALAPPDATA%\CyberpunkCodes\sector_cache')

SOURCES = [
    ('base', os.path.join(GAME, r'archive\pc\content\basegame_3_nightcity.archive')),
    ('ep1', os.path.join(GAME, r'archive\pc\ep1\ep1_1_nightcity.archive')),
]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write((r.stdout or '')[-800:] + (r.stderr or '')[-800:] + '\n')
        raise SystemExit('command failed: %s' % ' '.join(cmd[:2]))


def sector_dir(tag):
    return os.path.join(HEAVY, 'sectors_' + tag)


def cmd_extract(_args):
    for tag, arc in SOURCES:
        if not os.path.exists(arc):
            print('%s: archive not present, skipped' % tag)
            continue
        out = sector_dir(tag)
        if os.path.isdir(out):
            print('%s: already extracted (%s)' % (tag, out))
            continue
        print('%s: unbundling sectors (several minutes)...' % tag)
        os.makedirs(out, exist_ok=True)
        run([CLI, 'unbundle', arc, '-o', out, '-r', r'\.streamingsector$', '-v', 'Quiet'])
        print('%s: done' % tag)


def iter_sectors(tag):
    root = sector_dir(tag)
    for dp, _d, fs in os.walk(root):
        for f in fs:
            if f.endswith('.streamingsector'):
                yield os.path.join(dp, f), f


def find_hits(needle):
    needles = (needle.encode(), needle.capitalize().encode())
    hits = []
    for tag, _arc in SOURCES:
        if not os.path.isdir(sector_dir(tag)):
            continue
        for p, f in iter_sectors(tag):
            data = open(p, 'rb').read()
            c = sum(data.count(n) for n in needles)
            if c:
                hits.append((c, tag, f, p))
    hits.sort(reverse=True)
    return hits


def cmd_scan(args):
    hits = find_hits(args.needle)
    print('%d sectors contain %r' % (len(hits), args.needle))
    for c, tag, f, _p in hits[:args.limit]:
        kind = 'INTERIOR' if f.startswith('interior_') else 'exterior'
        print('  %5d  [%s] %-10s %s' % (c, tag, kind, f))


def cmd_index(args):
    hits = find_hits(args.needle)
    print('%d sectors contain %r; converting up to %d per source'
          % (len(hits), args.needle, args.cap))
    rows = []
    rx = re.compile(re.escape(args.needle), re.I)
    for tag, _arc in SOURCES:
        mine = [h for h in hits if h[1] == tag][:args.cap]
        if not mine:
            continue
        stage = os.path.join(HEAVY, 'stage_' + tag)
        outj = os.path.join(HEAVY, 'json_' + tag)
        shutil.rmtree(stage, ignore_errors=True)
        os.makedirs(stage, exist_ok=True)
        os.makedirs(outj, exist_ok=True)
        for _c, _t, f, p in mine:
            if not os.path.exists(os.path.join(outj, f + '.json')):
                shutil.copy2(p, os.path.join(stage, f))
        if os.listdir(stage):
            print('%s: converting %d sectors in one batch...' % (tag, len(os.listdir(stage))))
            run([CLI, 'convert', 'serialize', stage, '-o', outj, '-v', 'Quiet'])
        for _c, _t, f, _p in mine:
            oj = os.path.join(outj, f + '.json')
            if not os.path.exists(oj):
                continue
            try:
                doc = json.load(open(oj, encoding='utf-8'))
                root = doc['Data']['RootChunk']
                nodes = root.get('nodes', [])
                nd = root.get('nodeData', [])
                if isinstance(nd, dict):
                    nd = nd.get('Data', nd)
            except Exception:
                continue
            wanted = {}
            for i, n in enumerate(nodes):
                s = json.dumps(n)
                if rx.search(s):
                    names = re.findall(r'[A-Za-z0-9_\.\\-]*%s[A-Za-z0-9_\.\\-]*'
                                       % re.escape(args.needle), s, re.I)
                    wanted[i] = (names[0][-60:] if names else args.needle)
            for e in nd:
                idx = e.get('NodeIndex')
                if idx not in wanted:
                    continue
                pos = e.get('Position') or {}
                try:
                    x = float(pos.get('X')); y = float(pos.get('Y')); z = float(pos.get('Z'))
                except (TypeError, ValueError):
                    continue
                if abs(x) < 5 and abs(y) < 5:
                    continue
                rows.append({'x': round(x, 2), 'y': round(y, 2), 'z': round(z, 2),
                             'name': wanted[idx], 'sector': f, 'source': tag,
                             'interior': f.startswith('interior_')})
    os.makedirs(INDEX_DIR, exist_ok=True)
    slug = re.sub(r'[^a-z0-9]+', '_', args.needle.lower())
    jp = os.path.join(INDEX_DIR, 'index_%s.json' % slug)
    cp = os.path.join(INDEX_DIR, 'index_%s.csv' % slug)
    with open(jp, 'w', encoding='utf-8', newline=chr(10)) as fh:
        json.dump(rows, fh, indent=1)
    with open(cp, 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=['x', 'y', 'z', 'name', 'sector', 'source', 'interior'])
        w.writeheader()
        w.writerows(rows)
    print('%d nodes -> %s and .csv' % (len(rows), jp))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('extract', help='unbundle all streaming sectors').set_defaults(fn=cmd_extract)
    p = sub.add_parser('scan', help='list sectors containing a needle')
    p.add_argument('needle')
    p.add_argument('--limit', type=int, default=40)
    p.set_defaults(fn=cmd_scan)
    p = sub.add_parser('index', help='decode and save every matching node')
    p.add_argument('needle')
    p.add_argument('--cap', type=int, default=400,
                   help='max sectors converted per source (default 400)')
    p.set_defaults(fn=cmd_index)
    args = ap.parse_args()
    args.fn(args)


if __name__ == '__main__':
    main()
