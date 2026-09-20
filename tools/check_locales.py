r"""Check every locale a gig registers resolves to a complete, existing file.

    python tools\check_locales.py            # all three gigs
    python tools\check_locales.py gig-02

What is checked, per gig:

- the manifest's `onscreens:` names English only (the fallback for every
  language, so a translation mod's entries win) plus any translated locale;
  the other three blocks name all nineteen text locales
- every onscreens file the manifest names exists and carries every key of
  the English one (a missing key would show raw in that language)
- every subtitle map names a lines file that exists, and every lines file
  carries the same RUIDs as the English one
- the vomap the manifest names exists, and every clip it names is in the
  raw tree (a dubbed locale's map names that language's re-cut clips)
- every lipsync map exists, and for a dubbed locale whose voice pack is on
  this machine, every animation set it names is inside that pack
- how much of each locale is actually translated, from the translation
  tables, so a half-done language is visible before a build
- no HUD text typed straight into a script: every banner, bar header and
  notification the gig's redscript shows reads a key (a literal there shows
  English in every language; the malware bar did until 2026-09-19)

Exit status is non-zero on any missing file or key. The translation
coverage is a report, not a failure: an untranslated locale shows English,
which is the fallback the generators write on purpose.
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from questkit.packs import TEXT_LOCALES, PACKS, listing, archives   # noqa: E402

REPO = os.path.dirname(HERE)
B = chr(92)


def entries(path):
    with open(path, encoding='utf-8') as fh:
        d = json.load(fh)
    root = d['Data']['RootChunk']
    return root['root']['Data']['entries'] if 'root' in root else root.get('entries', [])


def manifest_values(text, key):
    """{locale: value} for one localization block of the manifest."""
    out = {}
    block = re.search(r'^  %s:\n((?:    .*\n|  #.*\n)*)' % key, text, re.M)
    if not block:
        return out
    cur = None
    for ln in block.group(1).split('\n'):
        m = re.match(r'^    ([a-z]{2}-[a-z]{2}):\s*(.*)$', ln)
        if m:
            cur = m.group(1)
            if m.group(2):
                out[cur] = m.group(2).strip()
            continue
        m = re.match(r'^      - (.*)$', ln)
        if m and cur:
            out[cur] = m.group(1).strip()
    return out


def check(mod_dir):
    name = os.path.basename(mod_dir)
    raw = os.path.join(mod_dir, 'source', 'wkit', 'raw')
    xl = glob.glob(os.path.join(raw, '*.archive.xl'))[0]
    with open(xl, encoding='utf-8') as fh:
        text = fh.read()
    problems = []

    def raw_path(depot):
        return os.path.join(raw, depot.replace(B, os.sep))

    def exists(depot, extra=''):
        p = raw_path(depot) + extra
        if not os.path.exists(p):
            problems.append('missing file %s' % depot)
            return None
        return p

    blocks = {k: manifest_values(text, k) for k in ('onscreens', 'subtitles', 'vomaps', 'lipmaps')}
    for k, v in blocks.items():
        if k == 'onscreens':
            # English only, the fallback for every language; a locale
            # registered here must have a strings file that translates it.
            if 'en-us' not in v:
                problems.append('onscreens lacks en-us')
            continue
        missing = sorted(set(TEXT_LOCALES) - set(v))
        if missing:
            problems.append('%s lacks locales: %s' % (k, ', '.join(missing)))

    # onscreens: every locale file complete against English
    en = exists(blocks['onscreens'].get('en-us', ''), '.json')
    en_keys = set(e['secondaryKey'] for e in entries(en)) if en else set()
    for loc, depot in sorted(blocks['onscreens'].items()):
        p = exists(depot, '.json')
        if p and loc != 'en-us':
            keys = set(e['secondaryKey'] for e in entries(p))
            if keys != en_keys:
                problems.append('onscreens %s: keys differ from English (%d vs %d)'
                                % (loc, len(keys), len(en_keys)))

    # subtitles: map -> lines file, same RUIDs as English
    en_map = exists(blocks['subtitles'].get('en-us', ''), '.json')
    en_ruids = set()
    if en_map:
        lines_depot = entries(en_map)[0]['subtitleFile']['DepotPath']['$value']
        en_lines = exists(lines_depot, '.json')
        if en_lines:
            en_ruids = set(e['stringId'] for e in entries(en_lines))
    for loc, depot in sorted(blocks['subtitles'].items()):
        p = exists(depot, '.json')
        if not p:
            continue
        lines_depot = entries(p)[0]['subtitleFile']['DepotPath']['$value']
        lp = exists(lines_depot, '.json')
        if lp and loc != 'en-us':
            ruids = set(e['stringId'] for e in entries(lp))
            if ruids != en_ruids:
                problems.append('subtitles %s: RUIDs differ from English' % loc)

    # vomaps: the file exists and every clip it names is in the raw tree
    for loc, depot in sorted(blocks['vomaps'].items()):
        p = exists(depot, '.json')
        if not p:
            continue
        for e in entries(p):
            for side in ('femaleResPath', 'maleResPath'):
                wem = e[side]['DepotPath']['$value']
                if not os.path.exists(raw_path(wem)):
                    problems.append('vomap %s names a clip that is not in the raw tree: %s' % (loc, wem))
                    break

    # lipmaps: file exists; sets exist in the pack when the pack is here
    checked_packs = []
    for loc, depot in sorted(blocks['lipmaps'].items()):
        p = exists(depot, '.json')
        if not p:
            continue
        if loc in PACKS and archives(loc)[0]:
            L = listing(loc)
            with open(p, encoding='utf-8') as fh:
                sets = re.findall(r'"\$value": "(base[^"]*\.anims)"', fh.read())
            for s in sets:
                if s.replace(B + B, B).lower() not in L:
                    problems.append('lipmap %s names a set not in the %s pack: %s' % (loc, loc, s))
            checked_packs.append(loc)

    # HUD text typed into a script. The shared helpers take a String, so a
    # literal compiles fine and shows English everywhere.
    hud_call = re.compile(r'(RunBar|ShowBar|Notify|NotifyTyped)\s*\(([^;]*?)\)\s*;', re.S)
    # The shared helpers are vendored into every gig, so a literal there shows
    # in all three (the bar's "COMPLETE" did, 2026-09-19).
    for reds in sorted(glob.glob(os.path.join(mod_dir, 'source', 'scripts', '*.reds'))
                       + glob.glob(os.path.join(REPO, 'shared', 'scripts', '*.reds'))):
        with open(reds, encoding='utf-8') as fh:
            code = '\n'.join(l for l in fh.read().split('\n') if not l.lstrip().startswith('//'))
        for m in hud_call.finditer(code):
            args = m.group(2)
            for lit in re.findall(r'(?<![nN])"([^"]*)"', args):   # n"..." is a key
                if re.search(r'[A-Za-z]{2,}', lit):
                    problems.append('%s: %s() shows a typed-in string, not a key: "%s"'
                                    % (os.path.basename(reds), m.group(1), lit))
        # ...and a literal written straight onto a HUD blackboard, which is how
        # the shared bar helper itself sets its texts.
        for m in re.finditer(r'SetString\(\s*[\w.]*(Header|BottomText|CompletedText)\s*,\s*"([^"]*)"', code):
            if re.search(r'[A-Za-z]{2,}', m.group(2)):
                problems.append('%s: the bar %s is a typed-in string, not a key: "%s"'
                                % (os.path.basename(reds), m.group(1), m.group(2)))

    # translation coverage
    gig_tools = glob.glob(os.path.join(HERE, 'gig*', 'translations'))
    tdir = [t for t in gig_tools if name[4:6] in os.path.basename(os.path.dirname(t))]
    coverage = {}
    if tdir and en and en_map:
        for loc in TEXT_LOCALES:
            if loc == 'en-us':
                continue
            tp = os.path.join(tdir[0], loc + '.json')
            if not os.path.exists(tp):
                coverage[loc] = (0, 0)
                continue
            with open(tp, encoding='utf-8') as fh:
                t = json.load(fh)
            coverage[loc] = (len(t.get('onscreens', {})), len(t.get('lines', {})))

    print('%s: %d locale(s) per block, %d packs checked for lipsync sets%s'
          % (name, len(blocks['onscreens']), len(checked_packs),
             ('' if not problems else ', %d PROBLEM(S)' % len(problems))))
    for pr in problems:
        print('   ' + pr)
    if coverage:
        print('   translated (ui strings / spoken lines), English has %d / %d:'
              % (len(en_keys), len(en_ruids)))
        print('   ' + '  '.join('%s %d/%d' % (loc, c[0], c[1]) for loc, c in sorted(coverage.items())))
    return not problems


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else 'gig-'
    mods = sorted(d for d in glob.glob(os.path.join(REPO, 'mods', which + '*'))
                  if os.path.isdir(os.path.join(d, 'source', 'wkit', 'raw')))
    ok = all([check(m) for m in mods])
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
