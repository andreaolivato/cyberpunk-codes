r"""The game's voice packs in every dubbed language, read where Steam put them.

    from questkit import packs
    packs.VOICE_LOCALES                  # the ten dubbed locales plus en-us
    packs.archives('de-de')              # (base archive, Phantom Liberty archive)
    packs.measure(hexes, 'de-de')        # {hex: {'f': ms, 'm': ms}}
    packs.listing('de-de')               # every path inside both archives

WHY THIS EXISTS. A scene line that points at a vanilla recording plays that
recording in whatever language the player's voice pack is, and the scene's
timeline is one set of numbers for all of them. Pacing a section needs the
length of the LONGEST dub of each line, which means reading every pack. A
lipsync map per language needs to know that the animation set exists in that
pack. Both are answered from the archives themselves.

WHERE THE PACKS ARE. Steam installs exactly one voice pack, the one the game
is set to. The others are fetched with `download_depot <app> <depot>` in the
Steam client console, which writes each into
`steamapps\content\app_<app>\depot_<depot>\` and leaves the installed game
alone, one archive per depot: a language is two depots, the base game's
and Phantom Liberty's (PACKS below; gotcha 118). English is read from the
installed game.

Nothing here is committed: `tools\_lang_cache\` holds the extracted clips and
the measurements, and the per-gig `vanilla_durations.json` that gen_scenes
reads is what gets committed, so a clone builds without any pack on disk.
"""
import json
import os
import re
import struct
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
CACHE = os.path.join(TOOLS, '_lang_cache')

CLI = os.environ.get('WOLVENKIT_CLI') or os.path.expandvars(
    r'%LOCALAPPDATA%\Programs\WolvenKit.CLI\WolvenKit.CLI.exe')
STEAM = r'C:\Program Files (x86)\Steam'
GAME = os.path.join(STEAM, r'steamapps\common\Cyberpunk 2077')
CONTENT = os.path.join(STEAM, r'steamapps\content')

# locale -> (archive language tag, base depot, Phantom Liberty depot). The tag
# is what the archive's file name carries (lang_<tag>_voice.archive); the
# locale is what the game's localization folders and ArchiveXL use.
PACKS = {
    'pl-pl': ('pl',    1091502, 2138337),
    'ru-ru': ('ru',    1091503, 2138339),
    'fr-fr': ('fr',    1091504, 2138333),
    'it-it': ('it',    1091505, 2138334),
    'de-de': ('de',    1091506, 2138331),
    'es-es': ('es-es', 1091507, 2138332),
    'jp-jp': ('ja',    1091508, 2138335),
    'zh-cn': ('zh-cn', 1091509, 2224070),
    'kr-kr': ('ko',    1460470, 2138336),
    'pt-br': ('pt',    1460471, 2138338),
}
VOICE_LOCALES = ['en-us'] + sorted(PACKS)

# The nineteen text locales the manifest registers. The nine that are not in
# PACKS have no dub: a player on one of them hears whichever voice pack they
# installed, and reads their own language.
TEXT_LOCALES = ['ar-ar', 'cz-cz', 'de-de', 'en-us', 'es-es', 'es-mx', 'fr-fr',
                'hu-hu', 'it-it', 'jp-jp', 'kr-kr', 'pl-pl', 'pt-br', 'ru-ru',
                'th-th', 'tr-tr', 'ua-ua', 'zh-cn', 'zh-tw']

WEM_RE = re.compile(r'^(.*)_([fm])_([0-9a-f]{16})$')


def archives(locale):
    """(base voice archive, Phantom Liberty voice archive) for a locale, or
    None for either that is not on disk."""
    if locale == 'en-us':
        base = os.path.join(GAME, r'archive\pc\content\lang_en_voice.archive')
        ep1 = os.path.join(GAME, r'archive\pc\ep1\lang_en_voice.archive')
    else:
        tag, dbase, dep1 = PACKS[locale]
        base = os.path.join(CONTENT, 'app_1091500', 'depot_%d' % dbase,
                            'archive', 'pc', 'content', 'lang_%s_voice.archive' % tag)
        ep1 = os.path.join(CONTENT, 'app_2138330', 'depot_%d' % dep1,
                           'archive', 'pc', 'ep1', 'lang_%s_voice.archive' % tag)
    return (base if os.path.exists(base) else None,
            ep1 if os.path.exists(ep1) else None)


def available():
    """The voice locales whose base pack is on this machine."""
    return [loc for loc in VOICE_LOCALES if archives(loc)[0]]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit('%s failed:\n%s' % (' '.join(cmd[:2]), (r.stderr or r.stdout)[-2000:]))
    return r.stdout


def listing(locale):
    """Every path inside the locale's two archives, lower-cased, cached."""
    os.makedirs(CACHE, exist_ok=True)
    out = os.path.join(CACHE, 'listing_%s.txt' % locale)
    if not os.path.exists(out):
        lines = []
        for arc in archives(locale):
            if arc:
                lines += [l.strip() for l in run([CLI, 'archiveinfo', '-l', arc]).splitlines()
                          if '\\' in l]
        with open(out, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write('\n'.join(lines))
    with open(out, encoding='utf-8') as fh:
        return set(l.strip().lower() for l in fh if l.strip())


def ogg_seconds(path):
    data = open(path, 'rb').read()
    i = data.find(b'\x01vorbis')
    j = data.rfind(b'OggS')
    if i < 0 or j < 0:
        return 0.0
    rate = struct.unpack('<I', data[i + 12:i + 16])[0]
    gran = struct.unpack('<q', data[j + 6:j + 14])[0]
    return gran / rate if rate else 0.0


def export(hexes, locale, kinds=('vo',)):
    """Pull the plain `vo` take of every hex out of the locale's packs and
    convert it to Ogg under the cache. Returns {(hex, gender): path}.

    Same route as `vo_corpus.export`: unbundle by regex, then `export -gp`,
    because `wwise -w` is broken in the CLI this repo pins. A hex lives in
    exactly one of the two archives, so both are asked and the miss is empty.
    """
    outdir = os.path.join(CACHE, 'clips', locale)
    os.makedirs(outdir, exist_ok=True)
    have = scan(locale, kinds)
    missing = sorted(h for h in set(x.lower() for x in hexes)
                     if not any(k[0] == h for k in have))
    if missing:
        with tempfile.TemporaryDirectory() as tmp:
            for i in range(0, len(missing), 60):
                batch = missing[i:i + 60]
                for arc in archives(locale):
                    if arc:
                        run([CLI, 'unbundle', arc, '-o', tmp,
                             '-r', '(' + '|'.join(batch) + ')', '-v', 'Quiet'])
            run([CLI, 'export', tmp, '-o', outdir, '-gp', GAME, '-v', 'Quiet'])
        have = scan(locale, kinds)
    return have


def scan(locale, kinds=('vo',)):
    outdir = os.path.join(CACHE, 'clips', locale)
    have = {}
    for dirpath, _d, files in os.walk(outdir):
        kind = os.path.basename(dirpath)
        if kind not in kinds:
            continue
        for fn in files:
            if not fn.lower().endswith('.ogg'):
                continue
            m = WEM_RE.match(os.path.splitext(fn)[0])
            if m:
                have[(m.group(3).lower(), m.group(2), kind)] = os.path.join(dirpath, fn)
    return have


def measure(hexes, locale):
    """{hex: {'f': ms, 'm': ms}} for the plain take of each hex in the locale.
    A speaker with one recording has it under 'f' (the tag is the PLAYER's
    body, and means nothing for an NPC line)."""
    os.makedirs(CACHE, exist_ok=True)
    out = os.path.join(CACHE, 'durations_%s.json' % locale)
    table = {}
    if os.path.exists(out):
        with open(out, encoding='utf-8') as fh:
            table = json.load(fh)
    want = sorted(set(h.lower() for h in hexes) - set(table))
    if want:
        have = export(want, locale)
        for (h, g, kind), path in have.items():
            if h in want and kind == 'vo':
                table.setdefault(h, {})[g] = int(round(ogg_seconds(path) * 1000))
        for h in want:
            table.setdefault(h, {})
        with open(out, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(table, fh, indent=1, sort_keys=True)
    return {h: table[h] for h in set(x.lower() for x in hexes) if h in table}
