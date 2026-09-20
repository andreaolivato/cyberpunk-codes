r"""The game's own translation of every vanilla line the gigs reuse, in all
nineteen text languages.

    python tools\vanilla_text.py

Writes tools\_lang_cache\vanilla_text.json: {stringId: {locale: {'f', 'm'}}}
for every 16-digit id named in the generators. Two uses. A native reader
checks that the official translation of a reused line still fits the scene
it now sits in (docs/scene-playbook.md, "Other languages"). And the translation tables for the gigs' own lines are
written against the same vocabulary the player sees in the reused lines
around them: how that language renders "fixer", "gig", "eddies", "choom".

Every text pack is installed with the game (`lang_<x>_text.archive`, about
8 MB each), so nothing has to be downloaded for this. The subtitle files are
found by name from the English cache vo_corpus.py keeps, then the same files
are pulled out of each language's archive.
"""
import glob
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from questkit.packs import CLI, GAME, CACHE, TEXT_LOCALES              # noqa: E402

OUT = os.path.join(CACHE, 'vanilla_text.json')
EN_CACHE = [os.path.join(HERE, '_vo_cache', 'text_json'),
            os.path.join(HERE, '_vo_cache', 'text_json_ep1')]

# locale -> archive language tag, as the text archives are named
TAGS = {'ar-ar': 'ar', 'cz-cz': 'cs', 'de-de': 'de', 'en-us': 'en', 'es-es': 'es-es',
        'es-mx': 'es-mx', 'fr-fr': 'fr', 'hu-hu': 'hu', 'it-it': 'it', 'jp-jp': 'ja',
        'kr-kr': 'ko', 'pl-pl': 'pl', 'pt-br': 'pt', 'ru-ru': 'ru', 'th-th': 'th',
        'tr-tr': 'tr', 'ua-ua': 'ua', 'zh-cn': 'zh-cn', 'zh-tw': 'zh-tw'}


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit('%s failed:\n%s' % (cmd[1], (r.stderr or r.stdout)[-1500:]))


def wanted_ids():
    from measure_packs import EXTRA_HEXES
    sids = set(str(int(h, 16)) for h in EXTRA_HEXES)
    for pat in ('gen_scenes.py', 'splice_takes.py', 'take_vanilla.py'):
        for f in glob.glob(os.path.join(HERE, 'gig0*', pat)):
            with open(f, encoding='utf-8') as fh:
                s = fh.read()
            sids |= set(str(int(x, 16)) for x in re.findall(r"0x([0-9a-fA-F]{16})", s))
            sids |= set(str(int(x, 16)) for x in re.findall(r"'([0-9a-f]{16})'", s))
    return sids


def english_files(sids):
    """basename (without .json.json) -> set of ids it holds."""
    hits = {}
    for root in EN_CACHE:
        for f in glob.glob(os.path.join(root, '**', '*.json'), recursive=True):
            with open(f, encoding='utf-8', errors='replace') as fh:
                t = fh.read()
            for sid in sids:
                if '"' + sid + '"' in t:
                    hits.setdefault(os.path.basename(f).split('.')[0], set()).add(sid)
    return hits


def entries(doc):
    root = doc['Data']['RootChunk']
    return root['root']['Data']['entries'] if 'root' in root else root.get('entries', [])


def main():
    sids = wanted_ids()
    files = english_files(sids)
    rx = '(' + '|'.join(re.escape(b) for b in sorted(files)) + r')\.json$'
    print('%d ids in %d subtitle files' % (len(sids), len(files)))
    out = {}
    if os.path.exists(OUT):
        with open(OUT, encoding='utf-8') as fh:
            out = json.load(fh)
    for loc in TEXT_LOCALES:
        if all(loc in out.get(s, {}) for s in sids):
            continue
        print('%s: extracting' % loc, flush=True)
        tag = TAGS[loc]
        arcs = [os.path.join(GAME, r'archive\pc\content\lang_%s_text.archive' % tag),
                os.path.join(GAME, r'archive\pc\ep1\lang_%s_text.archive' % tag)]
        with tempfile.TemporaryDirectory() as tmp:
            rawdir = os.path.join(tmp, 'raw')
            jsondir = os.path.join(tmp, 'json')
            os.makedirs(rawdir)
            os.makedirs(jsondir)
            for arc in arcs:
                if os.path.exists(arc):
                    run([CLI, 'unbundle', arc, '-o', rawdir, '-r', rx, '-v', 'Quiet'])
            # The serializer flattens its output to bare file names, and two
            # scenes can share one (nix_default.json exists under two
            # folders), so each raw file gets a unique prefix first.
            n = 0
            for root, _d, files in os.walk(rawdir):
                for f in files:
                    n += 1
                    os.rename(os.path.join(root, f), os.path.join(root, '%03d__%s' % (n, f)))
            run([CLI, 'convert', 'serialize', rawdir, '-o', jsondir, '-v', 'Quiet'])
            found = 0
            for f in glob.glob(os.path.join(jsondir, '**', '*.json'), recursive=True):
                with open(f, encoding='utf-8') as fh:
                    try:
                        doc = json.load(fh)
                    except ValueError:
                        continue
                for e in entries(doc):
                    sid = str(e.get('stringId', ''))
                    if sid in sids:
                        out.setdefault(sid, {})[loc] = {'f': e.get('femaleVariant', ''),
                                                        'm': e.get('maleVariant', '')}
                        found += 1
        print('%s: %d of %d' % (loc, found, len(sids)))
        with open(OUT, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(out, fh, indent=1, ensure_ascii=False, sort_keys=True)
    print('wrote %s' % OUT)


if __name__ == '__main__':
    main()
