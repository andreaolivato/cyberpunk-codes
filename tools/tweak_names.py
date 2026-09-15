r"""Every TweakDB record id and flat name, read off disk without starting the game.

    python tools\tweak_names.py "^PhoneAvatars\.Avatar_"
    python tools\tweak_names.py "^GameplayRestriction\.[A-Za-z0-9_]+$"
    python tools\tweak_names.py --all > names.txt

WHY THIS EXISTS. `tweakdb.bin` holds no plain strings, so "what is this record
called" cannot be answered from the game's own files. It can be answered from
this machine: Cyber Engine Tweaks ships its own string table, and the game ships
the decompressor for it.

  * the table is `tweakdbstr.kark` in CET's `tweakdb` folder
  * the format is the four bytes `KARK`, the uncompressed size as a
    little-endian uint32, then Kraken-compressed data
  * `oo2ext_7_win64.dll`, in the game's `bin\x64` folder, decompresses it
    through `OodleLZ_Decompress`

About 187 MB of text comes out. `docs/gameplay-restrictions.md` records the same
route in prose; this is that route as a tool, because it has now been wanted
twice: once for the 100 GameplayRestriction records, once to find out whether
Regina Jones has a phone avatar of her own.

IT GIVES NAMES ONLY. Values stay hashed, so what a record actually does still
has to be measured in game.

The decompressed table is cached next to the other extracted game data, in
`tools\_tweak_cache\`, which is gitignored: it is game data, not ours.
"""
import argparse
import ctypes
import os
import re
import struct
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(REPO, 'tools', '_tweak_cache')
PLAIN = os.path.join(CACHE, 'tweakdbstr.txt')

GAME = r'C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077'
KARK = os.path.join(GAME, 'bin', 'x64', 'plugins', 'cyber_engine_tweaks',
                    'tweakdb', 'tweakdbstr.kark')
OODLE = os.path.join(GAME, 'bin', 'x64', 'oo2ext_7_win64.dll')


def decompress():
    """KARK -> plain text, cached. Returns the path to the cached text."""
    if os.path.exists(PLAIN) and os.path.getsize(PLAIN) > 0:
        return PLAIN
    for p in (KARK, OODLE):
        if not os.path.exists(p):
            raise SystemExit('not found: %s' % p)

    with open(KARK, 'rb') as fh:
        blob = fh.read()
    if blob[:4] != b'KARK':
        raise SystemExit('%s does not start with KARK' % KARK)
    size = struct.unpack('<I', blob[4:8])[0]
    payload = blob[8:]

    lib = ctypes.WinDLL(OODLE)
    fn = lib.OodleLZ_Decompress
    fn.restype = ctypes.c_int64
    out = ctypes.create_string_buffer(size)
    # The long tail of zeros is OodleLZ_Decompress's optional arguments, which
    # the header declares with defaults C cannot express through ctypes. This
    # is the call shape the CET community uses and it is what works.
    got = fn(ctypes.c_char_p(payload), ctypes.c_int64(len(payload)),
             out, ctypes.c_int64(size),
             0, 0, 0, None, None, None, None, None, None, 3)
    if got != size:
        raise SystemExit('decompressed %d bytes, expected %d' % (got, size))

    os.makedirs(CACHE, exist_ok=True)
    with open(PLAIN, 'wb') as fh:
        fh.write(out.raw)
    return PLAIN


def names():
    """Every printable run in the table, deduplicated and sorted.

    The table is length-prefixed strings rather than one per line, so it is
    split on anything unprintable rather than parsed.
    """
    path = decompress()
    with open(path, 'rb') as fh:
        data = fh.read()
    found = set()
    for m in re.finditer(rb'[ -~]{3,200}', data):
        found.add(m.group().decode('ascii'))
    return sorted(found)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pattern', nargs='?', help='python regex, matched case-sensitively')
    ap.add_argument('--all', action='store_true', help='print every name')
    ap.add_argument('--limit', type=int, default=200)
    args = ap.parse_args()

    all_names = names()
    print('%d names in the table' % len(all_names), file=sys.stderr)

    if args.all:
        for n in all_names:
            print(n)
        return
    if not args.pattern:
        raise SystemExit('give a regex, or --all')

    rx = re.compile(args.pattern)
    hits = [n for n in all_names if rx.search(n)]
    print('%d match %r' % (len(hits), args.pattern), file=sys.stderr)
    for n in hits[:args.limit]:
        print(n)
    if len(hits) > args.limit:
        print('... %d more' % (len(hits) - args.limit), file=sys.stderr)


if __name__ == '__main__':
    main()
