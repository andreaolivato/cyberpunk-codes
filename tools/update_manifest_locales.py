r"""Rewrite the per-locale lines of a gig's .archive.xl localization block.

    python tools\update_manifest_locales.py gig-02

The manifest is the one hand-authored file in a gig and its comments are the
account of every key, so this touches ONLY the `<locale>:` lines and the
`- mod\...` / `mod\...` values under `onscreens`, `subtitles`, `vomaps` and
`lipmaps`. Everything else in the file is left byte for byte.

What each locale gets, and why:

    onscreens   mod\<name>\localization\en-us.json           English only, the
                fallback for every language; plus any locale with a strings file
    subtitles   mod\<name>\localization\subtitles[_<locale>].json
    vomaps      mod\<name>\localization\vomap[_<locale>].json
                one per dubbed locale, the English map for the rest
    lipmaps     mod\<name>\localization\gigNN[_<locale>].lipmap
                for the ten dubbed locales; the English map for the nine
                text-only ones, which have no voice pack of their own

A dubbed locale's map is the English one with the vanilla cuts swapped for
the same cuts made in that dub; the invented characters keep their actors'
recordings everywhere. docs/scene-playbook.md, "Other languages".
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from questkit.packs import TEXT_LOCALES, PACKS                       # noqa: E402

REPO = os.path.dirname(HERE)


def main():
    mod = sys.argv[1]
    mods = [d for d in os.listdir(os.path.join(REPO, 'mods')) if d.startswith(mod)]
    assert len(mods) == 1, mods
    raw = os.path.join(REPO, 'mods', mods[0], 'source', 'wkit', 'raw')
    xl = [f for f in os.listdir(raw) if f.endswith('.archive.xl')][0]
    path = os.path.join(raw, xl)
    with open(path, encoding='utf-8') as fh:
        lines = fh.read().split('\n')

    # Find the mod's depot folder and lipmap stem from the existing lines.
    text = '\n'.join(lines)
    folder = re.search(r'(mod\\[a-z_]+)\\localization\\en-us\.json', text).group(1)
    lipmap = re.search(r'localization\\([a-z0-9_]+)\.lipmap', text).group(1)
    B = chr(92)

    def value(key, loc):
        base = folder + B + 'localization' + B
        if key == 'onscreens':
            return base + loc + '.json'
        if key == 'subtitles':
            return base + ('subtitles.json' if loc == 'en-us' else 'subtitles_%s.json' % loc)
        if key == 'vomaps':
            return base + ('vomap.json' if loc not in PACKS else 'vomap_%s.json' % loc)
        if key == 'lipmaps':
            return base + (lipmap + ('' if loc not in PACKS else '_' + loc) + '.lipmap')
        raise KeyError(key)

    out, i, key, replaced = [], 0, None, 0
    while i < len(lines):
        ln = lines[i]
        m = re.match(r'^  (onscreens|subtitles|vomaps|lipmaps):\s*$', ln)
        if m:
            key = m.group(1)
            out.append(ln)
            i += 1
            # Skip the existing locale block: comment lines are kept, locale
            # lines and their values are dropped and regenerated.
            kept = []
            while i < len(lines) and (lines[i].startswith('    ') or lines[i].startswith('  #')):
                if lines[i].lstrip().startswith('#'):
                    kept.append(lines[i])
                i += 1
            for loc in TEXT_LOCALES:
                if key == 'onscreens':
                    # English only, plus a locale whose strings file exists:
                    # English is then the fallback for every other language
                    # and a translation mod wins (questkit.localization).
                    if loc != 'en-us' and not os.path.exists(
                            os.path.join(raw, folder, 'localization', loc + '.json.json')):
                        continue
                    out.append('    %s:' % loc)
                    out.append('      - ' + value(key, loc))
                else:
                    out.append('    %s: %s' % (loc, value(key, loc)))
            out.extend(kept)
            replaced += 1
            continue
        out.append(ln)
        i += 1
    assert replaced == 4, replaced
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('\n'.join(out))
    print('rewrote the four locale blocks in %s' % path)


if __name__ == '__main__':
    main()
