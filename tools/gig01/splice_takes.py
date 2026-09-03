r"""Trim and assemble vanilla voice clips into scene mocks.

    python tools\gig01\splice_takes.py elena_call

The corpus-recast route (see `mods/gig-01-negative-balance/docs/
corpus-recast.md`) gives a character back their own voice by writing every one
of their lines out of the recordings the game already shipped: whole takes
where one fits, and a single cut inside a take where the wanted words sit
inside a longer line. This tool makes the cuts.

LISTEN TO EVERY CUT BEFORE YOU USE IT. Each one is written out as
`trim__<label>.wav` for exactly that. A cut point chosen off a silence map can
land one pause early and the mistake is inaudible in the waveform: a clip meant
to say "Look, I'll pay." once came out as "Look", and nothing about the file
looked wrong.

Cut modes, all working from a map of pauses at least 0.15 s long:

  drop_head   remove everything before pause N, keep the rest
  drop_tail   keep everything before the last pause
  keep_head   keep everything before pause N

A two-cut extraction chains them: drop_head then keep_head pulled "Are you
OK?" out of the middle of `0x198010978c3bc000`.

Clips come out of the voice archive via `vo_corpus.export`, land under
`tools\_splice_cache\` (extracted game data, never committed, same rule as
`_vo_cache`), and are level-matched by voiced-frame RMS before assembly.
Needs `soundfile` and `numpy` (pip install --user).
"""
import argparse
import os
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
REPO = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
sys.path.insert(0, HERE)
import vo_corpus

CACHE = os.path.join(TOOLS, '_splice_cache')
AUDIO = os.path.join(REPO, 'mods', 'gig-01-negative-balance', 'source', 'audio')
RATE = 48000
GAP_TURN, GAP_SAME, EDGE, TARGET_RMS = 0.55, 0.35, 0.10, 0.045


# ------------------------------------------------------------------ audio kit
def load(path):
    data, rate = sf.read(path, always_2d=True)
    mono = data.mean(axis=1)
    if rate != RATE:
        n = int(round(len(mono) * RATE / rate))
        mono = np.interp(np.linspace(0, len(mono) - 1, n),
                         np.arange(len(mono)), mono)
    return mono.astype(np.float64)


def _frames(x):
    win = int(0.02 * RATE)
    n = len(x) // win
    return np.sqrt((x[:n * win].reshape(n, win) ** 2).mean(axis=1)), win


def rms_norm(x):
    r, _w = _frames(x)
    voiced = r[r > r.max() * 0.1]
    m = float(voiced.mean()) if len(voiced) else float(r.mean())
    return x * (TARGET_RMS / m) if m > 0 else x


def trim_edges(x):
    r, win = _frames(x)
    idx = np.where(r > r.max() * 0.04)[0]
    if not len(idx):
        return x
    a = max(0, idx[0] * win - int(EDGE * RATE))
    b = min(len(x), (idx[-1] + 1) * win + int(EDGE * RATE))
    return x[a:b]


def silences(x):
    """Internal pauses of at least 0.15 s, as (start, end) seconds."""
    r, _w = _frames(x)
    quiet = r < r.max() * 0.05
    out, start = [], None
    for i, q in enumerate(quiet):
        if q and start is None:
            start = i
        elif not q and start is not None:
            out.append((start * 0.02, i * 0.02))
            start = None
    if start is not None:
        out.append((start * 0.02, len(quiet) * 0.02))
    return [s for s in out if s[1] - s[0] >= 0.15]


def cut(x, mode, label, expect, idx=0):
    """One cut against the pause map. Listen to the result before trusting it."""
    total = len(x) / RATE
    sils = [s for s in silences(x) if s[0] > 0.35 and s[1] < total - 0.25]
    if not sils:
        raise SystemExit('%s: no internal pause to cut at' % label)
    if mode == 'drop_head':
        t = sils[idx][1] - 0.08
        y = x[int(t * RATE):]
    elif mode == 'drop_tail':
        t = sils[-1][0] + 0.05
        y = x[:int(t * RATE)]
    elif mode == 'keep_head':
        t = sils[idx][0] + 0.05
        y = x[:int(t * RATE)]
    else:
        raise SystemExit('unknown cut mode %r' % mode)
    y = trim_edges(y)
    os.makedirs(CACHE, exist_ok=True)
    check = os.path.join(CACHE, 'trim__%s.wav' % label)
    sf.write(check, y, RATE, subtype='PCM_16')
    print('%-16s %s cut %.2fs of %.2fs' % (label, mode, t, total))
    print('%-16s wanted: "%s"' % ('', expect))
    print('%-16s listen: %s' % ('', check))
    return y


def vanilla(hexes, gender='f'):
    """Extract clips for the given stringIds and return {hex: path}.

    ONE extraction pass, not a loop: a hex whose only take is the other body
    or a processed variant can never produce a file, and retrying it reloads
    the whole game depot each time. Such hexes are reported and dropped;
    callers must cope with an absent key.
    """
    outdir = os.path.join(CACHE, 'clips_' + gender)
    want = set(h.lower() for h in hexes)

    def scan():
        have = {}
        for sub in ('base', 'ep1'):
            vodir = os.path.join(outdir, sub, 'localization', 'en-us', 'vo')
            if not os.path.isdir(vodir):
                continue
            for fn in os.listdir(vodir):
                h = os.path.splitext(fn)[0][-16:].lower()
                if h in want:
                    have[h] = os.path.join(vodir, fn)
        return have

    have = scan()
    missing = sorted(want - set(have))
    if missing:
        vo_corpus.export(missing, outdir, gender)
        have = scan()
        still = sorted(want - set(have))
        if still:
            print('unextractable (no %s-body plain-vo take): %s'
                  % (gender, ', '.join(still)))
    return have


def assemble(seq, out):
    """seq is [(speaker, samples)]; speakers only decide the gap length."""
    parts, prev = [], None
    for who, x in seq:
        if prev is not None:
            gap = GAP_SAME if who == prev else GAP_TURN
            parts.append(np.zeros(int(gap * RATE)))
        parts.append(x)
        prev = who
    mix = np.concatenate(parts)
    peak = np.abs(mix).max()
    if peak > 0.98:
        mix *= 0.98 / peak
    sf.write(out, mix, RATE, subtype='PCM_16')
    print('wrote %s  (%.1f s)' % (out, len(mix) / RATE))


# ----------------------------------------------------- the approved elena call
def build_elena_call(gender='f'):
    """The approved v4 mock: see corpus-recast.md, "Approved picks"."""
    clips = vanilla(['197527fc222ef000', '19124b2278623000', '198010978c3bc000',
                     '178629817529f000', '1a58ecd70c2c5000', '196fda3a803bc000',
                     '1ab375df4c44d000', '19d79031063bc000', '168590edca351000'],
                    gender)

    def V(h):
        return rms_norm(trim_edges(load(clips[h])))

    def E(key):
        return rms_norm(trim_edges(load(
            os.path.join(AUDIO, 'gig01_elena_call__%s.wav' % key))))

    like_mama = rms_norm(cut(load(clips['197527fc222ef000']), 'drop_head',
                             'like_mama', 'Like Mama Welles? Thought I recognized the name.'))
    ok_full = cut(load(clips['198010978c3bc000']), 'drop_head', 'ok_didthey',
                  'Are you OK? Did they do anything to you?')
    are_you_ok = rms_norm(cut(ok_full, 'keep_head', 'are_you_ok', 'Are you OK?'))
    gonna_ok = rms_norm(cut(load(clips['178629817529f000']), 'drop_head',
                            'gonna_ok', "Everything's gonna be OK."))

    assemble([
        ('e', E('e01')), ('e', E('e02')),
        ('v', like_mama),
        ('e', E('e03')),
        ('v', V('19124b2278623000')),        # Go on, then. Let's hear it.
        ('e', E('e04')), ('e', E('e05')), ('e', E('e06')),
        ('v', are_you_ok),
        ('e', E('e07')),
        ('v', gonna_ok),
        ('e', E('e07b')),                    # Maybe... maybe I could go to El Coyote?
        ('v', V('1a58ecd70c2c5000')),        # Good idea.
        ('v', V('196fda3a803bc000')),        # I'll see what I can do.
        ('e', E('e08')),
        ('v', V('1ab375df4c44d000')),        # Got it.
        ('v', V('19d79031063bc000')),        # Wait... what?
        ('j', V('168590edca351000')),        # 'Cause it always is Arasaka.
    ], os.path.join(CACHE, 'elena_call_mock_%s.wav' % gender))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('scene', choices=['elena_call'])
    ap.add_argument('--gender', choices=('f', 'm'), default='f',
                    help='which V body reads the vanilla clips (default f)')
    args = ap.parse_args()
    build_elena_call(args.gender)


if __name__ == '__main__':
    main()
