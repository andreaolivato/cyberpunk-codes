r"""The vanilla voice-over corpus: index it, search it, extract clips from it.

WHAT IT IS

Every spoken line in Cyberpunk 2077, joined to its speaker, its text and its
audio file. 61,724 of them. Two facts make this possible and neither is
documented anywhere:

1. A VO filename IS the index:
       base\localization\en-us\vo\johnny_sq031_f_1a589ce2ca2c5000.wem
                                  ^speaker  ^scene ^gender ^stringId, hex
2. `lang_en_text.archive` holds `localizationPersistenceSubtitleEntries`
   resources keyed by that same stringId, in decimal.

So the join is `'%016x' % stringId`. Nothing else is needed - no soundbank
parsing, no `voiceovermap` lookup (although those exist and are what the game
itself uses; see docs/backlog.md 2a).

WHAT IT IS FOR

- **Auditioning a reuse.** A line pointed at a vanilla stringId plays vanilla's
  own recording for free (gen_scenes' `add_line(vanilla_sid=...)`). `search`
  finds candidates; `extract` gets you something to listen to.

  Do not plan around reuse: it does not scale. Measured across
  the whole corpus, exactly 3 of this gig's 59 lines had a verbatim match from
  the right speaker. Writing dialogue in a bark-compatible style and matching it
  afterwards sounds workable and is not.

- **Finding a voice by accent, age and gender.** VANILLA NPC VOICE TAGS ENCODE
  ALL THREE, which is not documented anywhere else:

      civ_high_m_20_jap_40   civilian, wealthy, male, voice #20, JAPANESE, ~40
      gang_val_f_02_mex_25   Valentinos, female, SPANISH, ~25
      civ_low_m_123_arb_30   civilian, poor, male, ARABIC, ~30

  Accent codes by line count: enus 10023, afam 3013, mex 2633, jap 2361,
  bra 1246, rus 1245, chn 1171, nat 973, car 761, arb 529, ind 255, engb 222,
  afr 82. So an accent can be SEARCHED FOR rather than performed:

      python tools\vo_corpus.py voices --accent mex --gender f --min-age 25 --max-age 40

  `voices` lists generic NPC voices only, never named characters, deliberately:
  a generic NPC is less recognisable, carries no performance anyone will miss,
  and there are dozens per accent. The listing shows each voice's longest line,
  which is the fastest way to judge register without listening to anything.

USAGE

    python tools\vo_corpus.py index
    python tools\vo_corpus.py speakers [--like johnny]
    python tools\vo_corpus.py search "how's things"  [--speaker nix]
    python tools\vo_corpus.py extract --speaker mama_welles --out <dir> [--minutes 15]

CACHE

Everything lands in `tools\_vo_cache\`, which is EXTRACTED GAME DATA and is
never committed - same rule as `tools\_anchor_cache\`. `index` rebuilds it in a
few minutes. It is ~40 MB of JSON, not the 4.7 GB of audio; clips are pulled on
demand by `extract`.
"""
import argparse
import collections
import json
import os
import re
import struct
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, '_vo_cache')
CORPUS = os.path.join(CACHE, 'corpus.json')

CLI = os.path.expandvars(r'%LOCALAPPDATA%\Programs\WolvenKit.CLI\WolvenKit.CLI.exe')
GAME = r'C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077'
TEXT_ARCHIVE = os.path.join(GAME, r'archive\pc\content\lang_en_text.archive')
VOICE_ARCHIVE = os.path.join(GAME, r'archive\pc\content\lang_en_voice.archive')

WEM_RE = re.compile(r'^(.*)_([fm])_([0-9a-f]{16})$')


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        sys.stderr.write(r.stdout[-2000:] + '\n' + r.stderr[-2000:] + '\n')
        raise SystemExit('command failed: %s' % ' '.join(str(c) for c in cmd[:3]))
    return r


# ------------------------------------------------------------------------ index
def build_index():
    os.makedirs(CACHE, exist_ok=True)
    raw = os.path.join(CACHE, 'text_raw')
    js = os.path.join(CACHE, 'text_json')
    listing = os.path.join(CACHE, 'voice_files.txt')

    if not os.path.isdir(raw):
        print('extracting subtitle resources...')
        run([CLI, 'unbundle', TEXT_ARCHIVE, '-o', raw, '-v', 'Quiet'])
    if not os.path.isdir(js):
        print('converting them to json (a few minutes)...')
        os.makedirs(js, exist_ok=True)
        run([CLI, 'convert', 'serialize',
             os.path.join(raw, 'base', 'localization', 'en-us', 'subtitles'),
             '-o', js, '-v', 'Quiet'])
    if not os.path.exists(listing):
        print('listing the voice archive...')
        r = run([CLI, 'archiveinfo', VOICE_ARCHIVE, '-l', '-v', 'Quiet'])
        with open(listing, 'w', encoding='utf-8') as fh:
            fh.write(r.stdout)

    # wem side: stringId hex -> [(dir, speaker+scene, gender, depot path)]
    wems = collections.defaultdict(list)
    with open(listing, encoding='utf-8-sig') as fh:
        for line in fh:
            line = line.strip()
            if not line.endswith('.wem'):
                continue
            parts = line.split(chr(92))
            m = WEM_RE.match(parts[-1][:-4])
            if m:
                wems[m.group(3)].append([parts[-2], m.group(1), m.group(2), line])

    # subtitle side
    rows = []
    for dirpath, _dirs, files in os.walk(js):
        for fn in files:
            if not fn.endswith('.json'):
                continue
            try:
                with open(os.path.join(dirpath, fn), encoding='utf-8') as f:
                    doc = json.load(f)
                entries = doc['Data']['RootChunk']['root']['Data']['entries']
            except Exception:
                continue
            for e in entries:
                if 'stringId' not in e:
                    continue
                sid = int(e['stringId'])
                h = '%016x' % sid
                audio = wems.get(h)
                if not audio:
                    continue          # subtitle with no recording; not useful here
                rows.append({
                    'sid': str(sid), 'hex': h,
                    'f': e.get('femaleVariant', ''), 'm': e.get('maleVariant', ''),
                    'audio': audio,
                })

    with open(CORPUS, 'w', encoding='utf-8') as fh:
        json.dump(rows, fh)
    print('indexed %d spoken lines -> %s' % (len(rows), CORPUS))
    return rows


def load():
    if not os.path.exists(CORPUS):
        return build_index()
    with open(CORPUS, encoding='utf-8') as fh:
        return json.load(fh)


# Generic NPC voice tags encode far more than a name:
#
#   civ_high_m_19_jap_30   ->  civilian, wealthy, male, voice #19, JAPANESE
#                              accent, played as ~30 years old
#   gang_val_f_02_mex_25   ->  Valentinos, female, SPANISH accent, ~25
#
# This is how you find "a Japanese-accented English-speaking man in his thirties
# who sounds like he works for Arasaka" without listening to 62,992 clips - and
# it is the answer to accents, which no English TTS voice will give you. The
# accent codes present, by line count: enus 10023, afam 3013, mex 2633, jap 2361,
# bra 1246, rus 1245, chn 1171, nat 973, car 761, arb 529, ind 255, engb 222,
# afr 82.
VOICE_TAG = re.compile(r'^(?P<arch>[a-z]+)_(?P<sub>[a-z]+)_(?P<gender>[fm])_'
                       r'(?P<num>\d+)_(?P<accent>[a-z]+)_(?P<age>\d+)(?:_(?P<ctx>.*))?$')


def voice_id(who):
    """`civ_high_m_19_jap_30_q105` -> `civ_high_m_19_jap_30`, or None if this is
    a named character rather than a generic NPC voice."""
    m = VOICE_TAG.match(who)
    if not m:
        return None
    return '_'.join((m.group('arch'), m.group('sub'), m.group('gender'),
                     m.group('num'), m.group('accent'), m.group('age')))


def speaker_of(who):
    """`johnny_sq031` -> `johnny`. Coarse grouping for browsing only.

    It cannot be more than coarse: the token after the name is a quest, scene or
    context and there is no delimiter separating the two. `mama_welles_sq018`
    groups under `mama`, which is why `matches()` below exists - asking for
    `--speaker mama` and asking for `--speaker mama_welles` must both work.
    """
    return who.split('_')[0]


def matches(who, speaker):
    """Does this VO filename's speaker field name the speaker we asked for?

    Prefix match on an underscore boundary, so `mama_welles` finds
    `mama_welles_sq018` and `mama_welles_finalboards` but never `mama_wellesXYZ`,
    and `johnny` finds every Johnny context. Substring matching would be wrong:
    `nix` would swallow `phoenix`.
    """
    return who == speaker or who.startswith(speaker + '_')


def rows_for(rows, speaker):
    return [r for r in rows if any(matches(a[1], speaker) for a in r['audio'])]


# ----------------------------------------------------------------------- output
def clean(text):
    """Vanilla subtitles carry markup for bilingual delivery
    (`<mothertongue>`, `<kiroshi>`) and Rich colour tags. A line containing them
    is a poor reference clip - the audio is part Spanish or Japanese - so this
    both strips the tags and lets `extract` skip such lines."""
    return re.sub(r'<[^>]*>', ' ', text).strip()


def has_markup(text):
    return '<' in text and '>' in text


def ogg_seconds(path):
    """Duration from the last Ogg page's granule position. No dependencies."""
    data = open(path, 'rb').read()
    i = data.find(b'\x01vorbis')
    j = data.rfind(b'OggS')
    if i < 0 or j < 0:
        return 0.0
    rate = struct.unpack('<I', data[i + 12:i + 16])[0]
    gran = struct.unpack('<q', data[j + 6:j + 14])[0]
    return gran / rate if rate else 0.0


def export(hexes, outdir, gender='f'):
    """Pull the given stringIds out of the voice archive and convert to Ogg.

    `WolvenKit.CLI wwise -w` is BROKEN in 8.20.0 (it dies with "Type
    System.IO.FileInfo cannot be created without a custom binder"), so the
    conversion goes through `export` with `-gp`, which works.
    """
    os.makedirs(outdir, exist_ok=True)
    made = []
    with tempfile.TemporaryDirectory() as tmp:
        # One regex per batch; a 60k-character alternation is not a good idea.
        for i in range(0, len(hexes), 60):
            batch = hexes[i:i + 60]
            run([CLI, 'unbundle', VOICE_ARCHIVE, '-o', tmp,
                 '-r', '(' + '|'.join(batch) + ')', '-v', 'Quiet'])
        run([CLI, 'export', tmp, '-o', outdir, '-gp', GAME, '-v', 'Quiet'])
    # DROP EVERYTHING THAT IS NOT PLAIN `vo`.
    #
    # A stringId can exist in four directories: `vo`, `vo_holocall`,
    # `vo_helmet`, `vo_rewinded`. Only the first is the clean studio recording;
    # the others are the same take with a phone filter, a helmet filter or a
    # rewind effect baked in. Extracting by hash gets all of them, and for
    # reference audio the processed ones are actively harmful - a model trained
    # on them learns the filter as part of the voice.
    #
    # The `_f_` / `_m_` tag is the PLAYER's gender, not the speaker's. For most
    # NPCs only the `f` file exists and the tag means nothing. For V it means
    # everything: `v_q112_f_*` and `v_q112_m_*` are two different actors saying
    # the same line, and a reference set containing both is a reference set for
    # nobody. Hence `--gender`, defaulting to `f`.
    for dirpath, _d, files in os.walk(outdir):
        kind = os.path.basename(dirpath)
        for fn in files:
            if not fn.lower().endswith('.ogg'):
                continue
            path = os.path.join(dirpath, fn)
            m = WEM_RE.match(os.path.splitext(fn)[0])
            keep = kind == 'vo' and (gender == 'both' or (m and m.group(2) == gender))
            if keep:
                made.append(path)
            else:
                os.remove(path)
    return made


def cmd_index(_args):
    build_index()


def cmd_speakers(args):
    """Without --like: coarse groups, for browsing who exists at all.
    With --like: the FULL speaker fields, because that is when you are about to
    pass one to `--speaker` and need to see where the name actually ends."""
    rows = load()
    tally = collections.Counter()
    for r in rows:
        for a in r['audio']:
            tally[a[1] if args.like else speaker_of(a[1])] += 1
    shown = 0
    for name, n in tally.most_common():
        if args.like and args.like.lower() not in name.lower():
            continue
        print('%7d  %s' % (n, name))
        shown += 1
        if shown >= args.limit:
            print('... %d more; narrow --like' % (len(tally) - shown))
            break


def cmd_voices(args):
    """Generic NPC voices, filterable by accent / gender / age.

    For picking a reference voice to clone an accent from. Named characters are
    excluded on purpose: a generic NPC is less recognisable, carries no
    performance anyone will miss, and there are dozens per accent to choose from.
    """
    rows = load()
    lines = collections.Counter()
    chars = collections.Counter()
    longest = {}
    for r in rows:
        text = clean(r['f'] or r['m'])
        if has_markup(r['f'] or r['m']) or len(text) < args.min_chars:
            continue
        for (d, who, g, _p) in r['audio']:
            if d != 'vo' or g != 'f':
                continue          # one variant only; see export()
            vid = voice_id(who)
            if not vid:
                continue
            m = VOICE_TAG.match(who)
            if args.accent and m.group('accent') != args.accent:
                continue
            if args.gender and m.group('gender') != args.gender:
                continue
            age = int(m.group('age'))
            if args.min_age and age < args.min_age:
                continue
            if args.max_age and age > args.max_age:
                continue
            lines[vid] += 1
            chars[vid] += len(text)
            if len(text) > len(longest.get(vid, ('', ''))[0]):
                longest[vid] = (text, r['hex'])

    if not lines:
        print('no voices matched')
        return
    print('%-30s %6s %8s   %s' % ('voice', 'lines', 'est min', 'longest line'))
    for vid, n in sorted(lines.items(), key=lambda kv: -chars[kv[0]])[:args.limit]:
        mins = (0.06 * chars[vid] + 0.6 * n) / 60.0
        print('%-30s %6d %8.1f   %s' % (vid, n, mins, longest[vid][0][:64]))


def cmd_search(args):
    rows = load()
    if args.speaker:
        rows = rows_for(rows, args.speaker)
    needle = args.text.lower()
    hits = 0
    for r in rows:
        text = clean(r['f'] or r['m'])
        if needle in text.lower():
            who = ','.join(sorted({a[1] for a in r['audio']}))[:44]
            dirs = ','.join(sorted({a[0] for a in r['audio']}))
            print('%s  0x%s  %-44s %s' % (r['sid'], r['hex'], who, dirs))
            print('    %s' % text)
            hits += 1
            if hits >= args.limit:
                print('... stopping at %d' % args.limit)
                break
    if not hits:
        print('nothing found')


def cmd_extract(args):
    rows = rows_for(load(), args.speaker)
    if not rows:
        raise SystemExit('no lines for speaker %r - try `speakers --like %s`'
                         % (args.speaker, args.speaker))

    # Longest lines first. Voice conversion wants sustained, connected speech;
    # a corpus of "Hm." and "V?" teaches a model almost nothing, and the short
    # ones are also the most likely to be a grunt with no phonetic content.
    usable = [r for r in rows
              if not has_markup(r['f'] or r['m'])
              and len(clean(r['f'] or r['m'])) >= args.min_chars]
    usable.sort(key=lambda r: -len(clean(r['f'] or r['m'])))
    skipped = len(rows) - len(usable)

    # Rough seconds-per-line so we can stop near the requested budget without
    # extracting everything first. Refined against the real durations after.
    budget = args.minutes * 60.0
    picked, est = [], 0.0
    for r in usable:
        if est >= budget:
            break
        picked.append(r)
        est += 0.06 * len(clean(r['f'] or r['m'])) + 0.6

    print('%s: %d lines total, %d usable (%d skipped: markup or under %d chars)'
          % (args.speaker, len(rows), len(usable), skipped, args.min_chars))
    print('taking %d of them, ~%.1f min estimated' % (len(picked), est / 60.0))

    files = export([r['hex'] for r in picked], args.out, args.gender)

    # Manifest, keyed by the filename that actually landed. Anything expecting a
    # transcript (fine-tuning, forced alignment, or just checking a clip by eye)
    # reads this rather than re-deriving it from the hash.
    by_hex = {r['hex']: r for r in picked}
    total = 0.0
    manifest = []
    for path in sorted(files):
        m = WEM_RE.match(os.path.splitext(os.path.basename(path))[0])
        if not m:
            continue
        r = by_hex.get(m.group(3))
        if not r:
            continue
        secs = ogg_seconds(path)
        total += secs
        manifest.append({
            'file': os.path.relpath(path, args.out),
            'seconds': round(secs, 3),
            'speaker': m.group(1),
            'listener_gender': m.group(2),
            'stringId': r['sid'],
            'hex': r['hex'],
            'text': clean(r['f'] or r['m']),
        })
    mpath = os.path.join(args.out, 'manifest.json')
    with open(mpath, 'w', encoding='utf-8') as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
    print('exported %d clips, %.1f min actual -> %s' % (len(manifest), total / 60.0, args.out))
    print('manifest: %s' % mpath)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)

    sub.add_parser('index', help='build or refresh the cache').set_defaults(fn=cmd_index)

    p = sub.add_parser('speakers', help='list speakers by line count')
    p.add_argument('--like', help='substring filter; also switches to full names')
    p.add_argument('--limit', type=int, default=40)
    p.set_defaults(fn=cmd_speakers)

    p = sub.add_parser('voices', help='generic NPC voices by accent/gender/age')
    p.add_argument('--accent', help='mex, jap, enus, rus, chn, afam, bra, ...')
    p.add_argument('--gender', choices=('f', 'm'))
    p.add_argument('--min-age', type=int)
    p.add_argument('--max-age', type=int)
    p.add_argument('--min-chars', type=int, default=40)
    p.add_argument('--limit', type=int, default=20)
    p.set_defaults(fn=cmd_voices)

    p = sub.add_parser('search', help='find lines containing some text')
    p.add_argument('text')
    p.add_argument('--speaker')
    p.add_argument('--limit', type=int, default=30)
    p.set_defaults(fn=cmd_search)

    p = sub.add_parser('extract', help='export a speaker\'s clips + transcripts')
    p.add_argument('--speaker', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--minutes', type=float, default=15.0)
    p.add_argument('--min-chars', type=int, default=40,
                   help='skip lines shorter than this (default 40)')
    p.add_argument('--gender', choices=('f', 'm', 'both'), default='f',
                   help="which PLAYER-gender variant to keep. For V this picks "
                        "WHICH V - female (f) or male (m) - and they are "
                        "different actors. For everyone else 'f' is usually the "
                        "only file that exists. Default: f")
    p.set_defaults(fn=cmd_extract)

    args = ap.parse_args()
    args.fn(args)


if __name__ == '__main__':
    main()
