r"""How the game itself renders a word or a line in every language.

    python tools\vanilla_terms.py "Gig type:" "Gun for Hire" "Afterlife"
    python tools\vanilla_terms.py --key 8529

Extracts each language's `base\localization\<loc>\onscreens\onscreens.json`
(and Phantom Liberty's) once into tools\_lang_cache\onscreens_<loc>.json,
then prints, for every English entry containing the text, the same entry in
every language, matched by primaryKey. The translation tables for the gigs'
own strings are written against this, so a German journal says what a
German journal says: the street-story headers (Gig type, Objective,
Location, Details), the gig types, the district names, and the quest title
a HUD banner names.
"""
import glob
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from questkit.packs import CLI, GAME, CACHE, TEXT_LOCALES              # noqa: E402
from vanilla_text import TAGS                                        # noqa: E402


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit('%s failed:\n%s' % (cmd[1], (r.stderr or r.stdout)[-1500:]))


def onscreens(loc):
    """{primaryKey: femaleVariant} for one locale, cached."""
    out = os.path.join(CACHE, 'onscreens_%s.json' % loc)
    if not os.path.exists(out):
        tag = TAGS[loc]
        table = {}
        with tempfile.TemporaryDirectory() as tmp:
            # ONE FOLDER PER ARCHIVE. The serializer flattens its output to
            # bare file names, and the expansion's onscreens.json would
            # overwrite the base game's, leaving the 10,000-entry expansion
            # table where the 100,000-entry base one should be.
            for i, arc in enumerate((os.path.join(GAME, r'archive\pc\content\lang_%s_text.archive' % tag),
                                     os.path.join(GAME, r'archive\pc\ep1\lang_%s_text.archive' % tag))):
                if not os.path.exists(arc):
                    continue
                rawdir, jsondir = os.path.join(tmp, 'raw%d' % i), os.path.join(tmp, 'json%d' % i)
                os.makedirs(rawdir)
                os.makedirs(jsondir)
                # Both files, onscreens.json and onscreens_final.json.
                run([CLI, 'unbundle', arc, '-o', rawdir, '-r', 'onscreens[a-z_]*[.]json$',
                     '-v', 'Quiet'])
                run([CLI, 'convert', 'serialize', rawdir, '-o', jsondir, '-v', 'Quiet'])
            for f in glob.glob(os.path.join(tmp, 'json*', '**', '*.json'), recursive=True):
                with open(f, encoding='utf-8') as fh:
                    doc = json.load(fh)
                root = doc['Data']['RootChunk']
                ents = root['root']['Data']['entries'] if 'root' in root else root['entries']
                for e in ents:
                    table[str(e['primaryKey'])] = e.get('femaleVariant', '')
        os.makedirs(CACHE, exist_ok=True)
        with open(out, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(table, fh, ensure_ascii=False)
    with open(out, encoding='utf-8') as fh:
        return json.load(fh)


def lookup(keys, locales=TEXT_LOCALES):
    return {loc: {k: onscreens(loc).get(k, '') for k in keys} for loc in locales}


def main():
    args = sys.argv[1:]
    en = onscreens('en-us')
    if args and args[0] == '--key':
        keys = args[1:]
    else:
        keys = []
        for needle in args:
            hits = [k for k, v in en.items() if needle.lower() in v.lower()]
            hits.sort(key=lambda k: len(en[k]))
            keys += hits[:3]
    sys.stdout.reconfigure(encoding='utf-8')
    for k in keys:
        print('== %s: %s' % (k, en.get(k, '')[:100].replace('\n', ' | ')))
        for loc in TEXT_LOCALES:
            if loc == 'en-us':
                continue
            print('   %s  %s' % (loc, onscreens(loc).get(k, '').replace('\n', ' | ')[:120]))


if __name__ == '__main__':
    main()
