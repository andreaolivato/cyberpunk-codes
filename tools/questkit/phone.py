r"""The holocall treatment: make a line sound like it arrives through V's phone.

WHY THIS EXISTS

Vanilla does not play one recording two ways. It ships FOUR takes of the same
line, in four sibling directories under `base\localization\<lang>\`, and four voiceover
maps to match:

    vo            the clean studio recording
    vo_holocall   the same take as it arrives on the phone
    vo_helmet     ... through a helmet
    vo_rewinded   ... with a rewind effect

Measured across the shipped files: 3,036 of the 78,026 `vo` clips have a
`vo_holocall` twin, every twin shares its filename (so its stringId) with the
`vo` original, and `voiceovermap_holocall.json` holds 2,981 entries whose ids
are all present in the main maps as well. So the treatment is an ASSET, not a
runtime effect, and a mod that wants it has to bake it.

Baking is also the only route open. `volanguagedatamap.json` lists the five
voiceover-map chunks the engine loads per language, and ArchiveXL's
`localization:` section accepts exactly `onscreens`, `subtitles`, `vomaps`,
`lipmaps` and `extend`. There is no key for the holocall map and no way to
patch the language-data map. A mod gets one clip per RUID. That costs nothing
here, because a RUID belongs to one line in one scene, so a line that is a
holocall is never also a world line.

`isHolocallSpeaker` routes a line into the phone UI and makes it play 2D. It
applies no processing of its own.

IT IS NOT AN EQ, AND THAT IS THE WHOLE POINT

Three passes were spent on this and the first two both produced a filter that
measured well and sounded, in a field report, *"just a tad different"*.

Vanilla keeps the source's short-time MAGNITUDE spectrum and throws its phase
away. Coherence between a vanilla clip and its holocall twin is 0.02 above
500 Hz; a known linear filter measured the same way reads 0.20, which is the
control that makes the number mean something. Four properties of the shipped
assets follow from that and have no other explanation: the stereo channels
decorrelate to a sample correlation of 0.04 while their envelopes still track
at 0.96, the file runs about 100 ms long, it starts about 9 ms late, and its
crest factor drops 4 to 5 dB without a limiter being involved.

So this file does two things, in this order, and the second is the one that
matters:

1. `TARGET` and the cascade fitted to it, which get the tone right;
2. `smear`, which discards the phase, and which is what makes it a call.

WHERE THE NUMBERS COME FROM

`TARGET` is a measurement, not a taste. See the comment above it for the two
ways of measuring it that give the wrong answer, both of which were shipped
past before the error was found. `fit()` re-derives the cascade from it, so
`PARAMS_BY_RATE` can be reproduced rather than trusted: 0.98 dB rms at 48 kHz,
1.17 dB at 24 kHz, and the two rates converge on the same filter, which is the
check that the fit is finding the shape and not an artefact.

`SMEAR = 0.35` is the one value here chosen by ear rather than measured. It was
picked against vanilla's own Regina take, filtered and levelled to sit beside
it: 0.5 was too much, 0.25 too little.

Two treatments were tried and dropped, and are not worth trying again. A
drifting delay of a fraction of a millisecond decorrelates the waveform just as
well and leaves the voice completely natural, and it explains something the
smear does not, namely that the best single alignment between a vanilla pair
correlates at only 0.33 to 0.46. It still lost the ear test. So did smearing
only above an 800 Hz crossover, on the theory that an even smear costs the
voice its body.

Not reproduced: vanilla's holocall assets are stereo. Ours stay mono, because a
holocall plays 2D through the phone UI either way and the mid is what `TARGET`
is measured on.

DETERMINISM

The phase rotation is drawn from a fixed seed, so the same master always
produces the same file, verified by md5 across runs. That is what makes it safe
for `gen_voice` to write the filtered takes to a gitignored folder rather than
commit them, and it is the same rule the voice route already follows: a reword
must never roll a fresh effect.

USAGE

    python tools\questkit\phone.py --fit [--rate N]    re-derive PARAMS_BY_RATE
    python tools\questkit\phone.py --check [--rate N]  print the fit against TARGET
    python tools\questkit\phone.py in.wav out.wav      filter one file

Standard library only, on the default Python 3.13, which is the rule the rest of
the voice tooling follows. Full account in docs/backlog.md 15; the findings that
generalise are gotchas 41 and 42.
"""
import cmath
import math
import os
import random
import struct
import sys

# ---------------------------------------------------------------------- target
# (Hz, dB): how much quieter each band is in a vanilla `vo_holocall` clip than
# in its `vo` twin, over seven pairs.
#
# TWO THINGS ABOUT HOW THIS IS MEASURED, and the first version of this file got
# both wrong in the same direction, which made the filter audibly too weak.
#
# It is measured on the STEREO MID, (L+R)/2, not on the left channel. The
# holocall assets are stereo with the two channels decorrelated, sample
# correlation about 0.04 while their envelopes track at 0.96, so summing them
# cancels, and the cancellation is worth 4 to 9 dB through the low mids. A mono
# clip is heard the way that sum is heard, so the sum is what it has to match.
#
# It is ENERGY-WEIGHTED across the clip, not a median of per-frame ratios. The
# median under-weights exactly the frames where the processing bites hardest.
#
# Together those two corrections deepen the scoop by about 10 dB and shrink the
# 1 kHz lift by about 3 dB. Per-clip spread across the seven is 2 to 4 dB from
# 200 Hz up, so the shape is a property of the processing rather than of a
# performance.
#
# The table starts at 100 Hz. Below that the ratio climbs back towards 0 dB,
# which no EQ does: neither clip holds much energy down there, so the ratio
# measures what the holocall version ADDS rather than what it keeps, and the
# per-clip spread goes from 2-4 dB to 8-13 dB. The high-pass carries that
# region instead, and its corner is fitted with everything else.
TARGET = [
    (100, -21.4), (112, -23.0), (126, -23.5), (141, -21.2), (159, -19.2),
    (178, -18.8), (200, -19.1), (224, -16.3), (252, -12.6), (283, -10.7),
    (317, -6.5), (356, -3.8), (400, -4.5), (449, -4.9), (504, -2.9),
    (566, -3.1), (635, -3.1), (713, -3.9), (800, -2.2), (898, 2.7),
    (1008, 4.5), (1131, 4.3), (1270, 3.4), (1425, 0.2), (1600, -1.7),
    (1796, -3.2), (2016, -2.9), (2263, -1.8), (2540, -0.7), (2851, -0.4),
    (3200, -0.5), (3592, -0.4), (4032, 1.1), (4525, 2.9), (5080, 2.7),
    (5702, 3.3), (6400, 2.0), (7184, -0.1), (8063, -0.8), (9051, -1.1),
    (10159, -3.5), (11404, -5.9), (12800, -9.4),
]

FIT_RATE = 48000.0
# Butterworth, so the corner does not resonate. The corner itself is p[15].
HP_Q = 0.7071

# What fit() returns for TARGET. Five sections after the high-pass, each
# (f0, Q, dB); the last is a high shelf and its middle value is S, not Q.
#
# ONE SET PER SAMPLE RATE, and that is not decoration. A biquad's response
# depends on f0/rate, and the top shelf sits at 11.5 kHz, which is 0.24 of
# Nyquist at 48 kHz and 0.96 of it at 24 kHz, where RBJ's formulas flatten out.
# Clamping f0 was tried first and left the filter 2.4 to 4.1 dB bright at
# 7-9 kHz on the 24 kHz masters. Fitting at the target rate instead costs
# nothing, because the fit is cheap and the answer is written down here.
#
#   python tools\questkit\phone.py --fit --rate 24000
PARAMS_BY_RATE = {
    # (f0, Q, dB) per section, then the high-pass corner last. The last section
    # is a high shelf, so its middle value is S rather than Q.
    48000: [203.164, 0.495, -16.491,    # the scoop that takes the chest out
            350.425, 1.502, 7.570,      # fills the scoop's upper shoulder
            1075.835, 2.246, 8.069,     # the lift that puts the voice in the ear
            1857.788, 2.829, -3.736,    # a dip vanilla has just above it
            11605.957, 1.766, -14.061,  # top shelf
            214.651],                   # high-pass corner
    # The 24 kHz WAV masters this gig ships. Fitted separately because a
    # biquad's response depends on f0/rate; both rates land on the same filter,
    # which is the check that the fit is finding the shape and not an artefact.
    24000: [199.713, 0.505, -16.078,
            350.895, 1.625, 7.088,
            1075.066, 2.281, 7.873,
            1852.753, 3.120, -3.705,
            11375.000, 1.178, -22.036,
            215.577],
}


def params_for(rate):
    """The cascade parameters at a sample rate, fitted on demand and cached."""
    key = int(round(rate))
    if key not in PARAMS_BY_RATE:
        PARAMS_BY_RATE[key] = fit(rate=float(key))[0]
    return PARAMS_BY_RATE[key]

# DYNAMICS. The same seven pairs say two things that point at different tools.
#
# Frame by frame the processing is barely a compressor at all: 15 dB of source
# range comes out as 12.8 dB, about 1.17:1 on 85 ms frames. But whole-file crest
# factor falls hard, 19-23 dB down to 15-17.6 dB. Gentle levelling plus fast
# peak limiting, in other words, and the limiting is doing most of the work.
#
# So the compressor here is deliberately mild and the soft clip is what lands
# the crest. TARGET_CREST_DB is an ABSOLUTE target rather than vanilla's -4.5 dB
# delta. These takes arrive pre-compressed, 12 to 23 dB where vanilla's studio
# recordings are 19 to 23, so taking 4.5 dB off an already-squashed take
# squashes it twice.
COMP_THRESHOLD_DB = -26.0
COMP_RATIO = 1.5
COMP_ATTACK_MS = 5.0
COMP_RELEASE_MS = 120.0
COMP_LOOKAHEAD_MS = 4.0
TARGET_CREST_DB = 16.0
MAX_DRIVE = 12.0

# LEVEL. The output is matched back to the source's rms and then trimmed by this.
#
# Matching alone leaves the filtered take 5.5 dB hotter, band for band, than
# vanilla's holocall is against ITS source: the scoop removes a lot of energy
# and putting the broadband level back puts all of it into the bands that are
# left. Vanilla does not do that. Its holocall mid sits about 2.3 dB under its
# source broadband, and 5.5 dB under ours once the removed low end is discounted.
#
# Trimming is the difference between a filtered voice and a voice on a phone,
# because distance is part of what a call sounds like. It is also the one number
# here that is a mix rather than a measurement, so it is a knob.
OUTPUT_TRIM_DB = 0.0

# SMEAR. How much of each frame's phase is replaced with noise, 0 to 1.
#
# This is the part of the effect an EQ cannot do, and leaving it out is why the
# first two attempts sounded like a filtered voice rather than a voice on a
# phone. Vanilla's holocall keeps the source's short-time MAGNITUDE spectrum and
# throws its phase away: coherence between a vanilla clip and its holocall twin
# is 0.02 above 500 Hz, against 0.20 for a known linear filter measured the same
# way. Every other oddity in the assets follows from that one fact: the two
# stereo channels decorrelated while their envelopes track at 0.96 (two draws of
# the phase), the output running about 100 ms long and 9 ms late (the STFT), and
# the crest factor falling (random phase is less peaky than speech).
#
# 1.0 is a whisper. 0.35 is where this landed by ear against vanilla's own
# Regina take, filtered and levelled to sit next to it: 0.5 was too much, 0.25
# too little, and 0.35 was called indistinguishable from the real thing.
SMEAR = 0.35
SMEAR_SEED = 20260819
SMEAR_FFT = 1024

# The EQ'd signal is normalised to this before compression, so the threshold
# means the same thing for a loud take and a quiet one and every line gets the
# same treatment. Level is put back at the end by matching the source.
WORK_RMS_DBFS = -20.0
# Vanilla's holocall takes are digitally silent between words. -55 dBFS relative
# to the clip's own peak is below anything the masters leave in a pause and
# well under the quietest breath in this gig's takes.
GATE_DB = -55.0
GATE_HOLD_MS = 40.0
GATE_FADE_MS = 12.0


# ---------------------------------------------------------------- RBJ biquads
def peaking(f0, q, gain_db, rate):
    A = 10 ** (gain_db / 40.0)
    w = 2 * math.pi * f0 / rate
    a = math.sin(w) / (2 * q)
    c = math.cos(w)
    b0, b1, b2 = 1 + a * A, -2 * c, 1 - a * A
    a0, a1, a2 = 1 + a / A, -2 * c, 1 - a / A
    return (b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0)


def highpass(f0, q, rate):
    w = 2 * math.pi * f0 / rate
    a = math.sin(w) / (2 * q)
    c = math.cos(w)
    b0, b1, b2 = (1 + c) / 2, -(1 + c), (1 + c) / 2
    a0, a1, a2 = 1 + a, -2 * c, 1 - a
    return (b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0)


def highshelf(f0, s, gain_db, rate):
    A = 10 ** (gain_db / 40.0)
    w = 2 * math.pi * f0 / rate
    c, sn = math.cos(w), math.sin(w)
    al = sn / 2 * math.sqrt((A + 1 / A) * (1 / s - 1) + 2)
    tw = 2 * math.sqrt(A) * al
    b0 = A * ((A + 1) + (A - 1) * c + tw)
    b1 = -2 * A * ((A - 1) + (A + 1) * c)
    b2 = A * ((A + 1) + (A - 1) * c - tw)
    a0 = (A + 1) - (A - 1) * c + tw
    a1 = 2 * ((A - 1) - (A + 1) * c)
    a2 = (A + 1) - (A - 1) * c - tw
    return (b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0)


def cascade(params=None, rate=FIT_RATE):
    """The filter at a given sample rate.

    A section is CLAMPED to 0.45 of the sample rate. The top shelf sits at
    11.5 kHz, and the WAV masters this runs on are 24 kHz. RBJ's formulas go
    wrong as f0 approaches Nyquist, so at 24 kHz that shelf lands at 10.8 kHz
    instead. There is nothing above 12 kHz in a 24 kHz file to lose.
    """
    return bells(params, rate) + [shelf(params, rate)]


def bells(params=None, rate=FIT_RATE):
    """Everything except the top shelf: the high-pass and the four bells."""
    p = params_for(rate) if params is None else params
    lim = 0.45 * rate
    out = [highpass(min(p[15], lim), HP_Q, rate)]
    for i in range(0, 12, 3):
        out.append(peaking(min(p[i], lim), p[i + 1], p[i + 2], rate))
    return out


def shelf(params=None, rate=FIT_RATE):
    """The top shelf, which runs AFTER the dynamics rather than with the rest.

    The soft clip generates harmonics, and measurement put them 5 to 6 dB above
    vanilla at 7 to 10 kHz when the shelf ran first. Shelving after the clipper
    takes the clipper's own output down with everything else.
    """
    p = params_for(rate) if params is None else params
    return highshelf(min(p[12], 0.45 * rate), p[13], p[14], rate)


def db_at(sections, f, rate=FIT_RATE):
    z = cmath.exp(-2j * math.pi * f / rate)
    h = 1 + 0j
    for b0, b1, b2, a1, a2 in sections:
        h *= (b0 + b1 * z + b2 * z * z) / (1 + a1 * z + a2 * z * z)
    return 20 * math.log10(max(abs(h), 1e-9))


def biquad(x, coeffs):
    """Direct form I, in place on a new list. One section."""
    b0, b1, b2, a1, a2 = coeffs
    y = [0.0] * len(x)
    x1 = x2 = y1 = y2 = 0.0
    for i, s in enumerate(x):
        o = b0 * s + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        x2, x1 = x1, s
        y2, y1 = y1, o
        y[i] = o
    return y


# --------------------------------------------------------------------- fitting
def fit(target=None, iterations=500, rate=FIT_RATE):
    """Re-derive the cascade from TARGET by coordinate descent.

    Returns (params, rms error in dB). Kept in the file so the numbers can be
    reproduced rather than trusted. Target points at or above 0.45 of the rate
    are dropped, since no biquad can say anything useful about them.
    """
    tgt = [(f, w) for f, w in (TARGET if target is None else target)
           if f < 0.45 * rate]

    def err(p):
        try:
            c = cascade(p, rate)
        except (ValueError, ZeroDivisionError):
            return 1e9
        return sum((db_at(c, f, rate) - w) ** 2 for f, w in tgt) / len(tgt)

    p0 = [140, 1.0, -12, 340, 1.5, 2, 1120, 2.0, 6, 3500, 2.0, -2, 10000, 0.9, -12, 160]
    lo = [100, 0.2, -34, 200, 0.3, -12, 800, 0.5, -6, 1500, 0.3, -16, 5000, 0.3, -34, 80]
    hi = [320, 4.0, 0, 900, 4.0, 22, 1700, 4.0, 20, 7000, 4.0, 14, 16000, 2.0, 8, 450]
    p, best = p0[:], err(p0)
    step = [(b - a) / 8.0 for a, b in zip(lo, hi)]
    for _ in range(iterations):
        moved = False
        for i in range(len(p)):
            for sign in (1, -1):
                q = p[:]
                q[i] = min(hi[i], max(lo[i], p[i] + sign * step[i]))
                e = err(q)
                if e < best - 1e-12:
                    best, p, moved = e, q, True
        if not moved:
            step = [s / 2.0 for s in step]
            if max(step) < 1e-5:
                break
    return p, math.sqrt(best)


# ------------------------------------------------------------------------ wav
def read_wav(path):
    """-> (samples as floats in -1..1, rate, channels). Mono only.

    Walks the RIFF chunks rather than using `wave`, which handles PCM only and
    raises `unknown format: 3` on the IEEE-float WAVs some tools write. Same
    reason questkit.voice.wav_ms does it by hand.
    """
    with open(path, 'rb') as fh:
        data = fh.read()
    if data[:4] != b'RIFF' or data[8:12] != b'WAVE':
        raise SystemExit('%s is not a RIFF/WAVE file' % path)
    fmt = rate = channels = bits = None
    off = 12
    while off + 8 <= len(data):
        cid = data[off:off + 4]
        csz = struct.unpack('<I', data[off + 4:off + 8])[0]
        body = off + 8
        if cid == b'fmt ':
            fmt, channels, rate = struct.unpack('<HHI', data[body:body + 8])
            bits = struct.unpack('<H', data[body + 14:body + 16])[0]
        elif cid == b'data':
            n = min(csz, len(data) - body)
            if channels != 1:
                raise SystemExit('%s has %d channels; this filter is mono only'
                                 % (path, channels))
            if fmt == 1 and bits == 16:
                cnt = n // 2
                raw = struct.unpack('<%dh' % cnt, data[body:body + cnt * 2])
                return [s / 32768.0 for s in raw], rate, channels
            if fmt == 3 and bits == 32:
                cnt = n // 4
                return list(struct.unpack('<%df' % cnt, data[body:body + cnt * 4])), rate, channels
            raise SystemExit('%s is format %s at %s bits; expected 16-bit PCM '
                             'or 32-bit float' % (path, fmt, bits))
        off += 8 + csz + (csz & 1)
    raise SystemExit('%s has no data chunk' % path)


def write_wav(path, samples, rate):
    """16-bit mono PCM, which is what the Wwise conversion expects."""
    frames = bytearray()
    for s in samples:
        v = int(round(max(-1.0, min(1.0, s)) * 32767.0))
        frames += struct.pack('<h', v)
    d = bytes(frames)
    hdr = (b'RIFF' + struct.pack('<I', 36 + len(d)) + b'WAVE'
           + b'fmt ' + struct.pack('<IHHIIHH', 16, 1, 1, rate, rate * 2, 2, 16)
           + b'data' + struct.pack('<I', len(d)))
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, 'wb') as fh:
        fh.write(hdr + d)


# ------------------------------------------------------------------- the smear
def _fft(re, im, inverse=False):
    """In-place iterative radix-2. Lists, so no dependency."""
    n = len(re)
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
        if i < j:
            re[i], re[j] = re[j], re[i]
            im[i], im[j] = im[j], im[i]
    length = 2
    while length <= n:
        ang = (2 if inverse else -2) * math.pi / length
        wr, wi = math.cos(ang), math.sin(ang)
        half = length // 2
        for i in range(0, n, length):
            cr, ci = 1.0, 0.0
            for k in range(i, i + half):
                ur, ui = re[k], im[k]
                vr = re[k + half] * cr - im[k + half] * ci
                vi = re[k + half] * ci + im[k + half] * cr
                re[k], im[k] = ur + vr, ui + vi
                re[k + half], im[k + half] = ur - vr, ui - vi
                cr, ci = cr * wr - ci * wi, cr * wi + ci * wr
        length <<= 1
    if inverse:
        for i in range(n):
            re[i] /= n
            im[i] /= n


def smear(x, amount=None, n=SMEAR_FFT, seed=SMEAR_SEED):
    """Rotate each STFT bin's phase towards noise, keeping its magnitude.

    Hann analysis and synthesis at a quarter-length hop, which sums to unity, so
    with amount=0 this returns the input. The random rotation is drawn from a
    fixed seed, so a rebuild produces the same file: a reword must not roll a
    fresh effect, the same rule the voice route already follows.
    """
    a = SMEAR if amount is None else amount
    if a <= 0:
        return list(x)
    half = n // 2
    hop = n // 4
    win = [0.5 - 0.5 * math.cos(2 * math.pi * i / n) for i in range(n)]
    pad = [0.0] * n + list(x) + [0.0] * (2 * n)
    out = [0.0] * len(pad)
    rng = random.Random(seed)
    for start in range(0, len(pad) - n, hop):
        re = [pad[start + i] * win[i] for i in range(n)]
        im = [0.0] * n
        _fft(re, im)
        for k in range(1, half):
            mag = math.hypot(re[k], im[k])
            ang = math.atan2(im[k], re[k]) + a * rng.uniform(-math.pi, math.pi)
            re[k], im[k] = mag * math.cos(ang), mag * math.sin(ang)
            re[n - k], im[n - k] = re[k], -im[k]      # keep it real
        im[0] = im[half] = 0.0
        _fft(re, im, inverse=True)
        for i in range(n):
            out[start + i] += re[i] * win[i] * (2.0 / 3.0)
    return out[n:n + len(x)]


# ------------------------------------------------------------------ the chain
def _rms(x):
    if not x:
        return 0.0
    return math.sqrt(sum(s * s for s in x) / len(x))


def _peak(x):
    return max((abs(s) for s in x), default=0.0)


def compress(x, rate, threshold_db=COMP_THRESHOLD_DB, ratio=COMP_RATIO,
             attack_ms=COMP_ATTACK_MS, release_ms=COMP_RELEASE_MS,
             lookahead_ms=COMP_LOOKAHEAD_MS):
    """Peak compressor with look-ahead, smoothed gain, log domain.

    The look-ahead is what makes it work. Without it a transient gets through
    at full gain during the attack while everything sustained is pulled down,
    so the crest factor goes UP, measured at +2.7 dB on this gig's takes,
    which is the opposite of what vanilla's holocall assets show. Computing the
    gain from the signal and applying it to a delayed copy puts the reduction
    in place before the transient arrives.
    """
    thr = 10 ** (threshold_db / 20.0)
    ka = math.exp(-1.0 / (rate * attack_ms / 1000.0))
    kr = math.exp(-1.0 / (rate * release_ms / 1000.0))
    la = max(1, int(rate * lookahead_ms / 1000.0))

    env = 0.0
    gain_db = 0.0
    gains = [0.0] * len(x)
    for i, s in enumerate(x):
        a = abs(s)
        env = a if a > env else env * kr + a * (1 - kr)
        want = 0.0
        if env > thr:
            want = -20 * math.log10(env / thr) * (1 - 1.0 / ratio)
        k = ka if want < gain_db else kr
        gain_db = want + (gain_db - want) * k
        gains[i] = gain_db

    out = [0.0] * len(x)
    for i in range(len(x)):
        j = min(len(x) - 1, i + la)
        out[i] = x[i] * 10 ** (min(gains[i], gains[j]) / 20.0)
    return out


def saturate(x, drive):
    """Soft clip. Unity slope through zero, so quiet material is untouched."""
    if drive <= 0:
        return list(x)
    n = math.tanh(drive)
    return [math.tanh(drive * s) / n for s in x]


def gate(x, rate, floor_db=GATE_DB, hold_ms=GATE_HOLD_MS, fade_ms=GATE_FADE_MS):
    """Zero the pauses, the way vanilla's holocall takes are zeroed.

    Level is followed on a short window; the gate opens instantly, holds, and
    then closes over a fade so a decaying word is not chopped.
    """
    pk = _peak(x)
    if pk <= 0:
        return list(x)
    thr = pk * 10 ** (floor_db / 20.0)
    win = max(1, int(rate * 0.005))
    hold = int(rate * hold_ms / 1000.0)
    fade = max(1, int(rate * fade_ms / 1000.0))

    # running max over `win`, cheaply: block maxima, then a 3-block window
    nb = (len(x) + win - 1) // win
    bmax = [max((abs(s) for s in x[b * win:(b + 1) * win]), default=0.0)
            for b in range(nb)]
    openb = [max(bmax[max(0, b - 1):b + 2]) > thr for b in range(nb)]

    env = [0.0] * len(x)
    countdown = 0
    level = 0.0
    stepdown = 1.0 / fade
    for i in range(len(x)):
        if openb[i // win]:
            countdown = hold
        if countdown > 0:
            countdown -= 1
            level = 1.0
        else:
            level = max(0.0, level - stepdown)
        env[i] = level
    return [s * e for s, e in zip(x, env)]


def crest_db(x):
    r = _rms(x)
    return 20 * math.log10(_peak(x) / r) if r > 0 else 0.0


def clip_to_crest(x, target_db=TARGET_CREST_DB, max_drive=MAX_DRIVE):
    """Soft clip just hard enough to land the crest factor on `target_db`.

    Bisects the drive rather than fixing it, because the takes arrive at
    anything from 12 to 23 dB and a fixed drive would leave them just as far
    apart. A take already below the target is returned untouched.
    """
    pk = _peak(x)
    if pk <= 0 or crest_db(x) <= target_db:
        return list(x)
    y = [s / pk for s in x]
    lo, hi = 0.0, max_drive
    best = y
    for _ in range(18):
        mid = (lo + hi) / 2
        cand = saturate(y, mid)
        if crest_db(cand) > target_db:
            lo = mid
        else:
            hi = mid
        best = cand
        if hi - lo < 1e-3:
            break
    return best


def process(samples, rate, match_rms=True, trim_db=None, smear_amount=None):
    """EQ, level, compress, gate, clip, match. Returns a new list."""
    y = samples
    for c in bells(rate=float(rate)):
        y = biquad(y, c)
    y = smear(y, amount=smear_amount)
    work = _rms(y)
    if work > 0:
        g = 10 ** (WORK_RMS_DBFS / 20.0) / work
        y = [s * g for s in y]
    y = compress(y, rate)
    # Gate BEFORE the clipper, so the crest the clipper is aiming at is measured
    # on the same signal the file ends up holding. Silence counts towards rms.
    y = gate(y, rate)
    y = clip_to_crest(y)
    y = biquad(y, shelf(rate=float(rate)))
    if match_rms:
        src, got = _rms(samples), _rms(y)
        if got > 0:
            trim = OUTPUT_TRIM_DB if trim_db is None else trim_db
            y = [s * (src / got) * 10 ** (-trim / 20.0) for s in y]
    pk = _peak(y)
    if pk > 0.99:
        y = [s * (0.99 / pk) for s in y]
    return y


def filter_file(src, dst, trim_db=None, smear_amount=None):
    """-> a dict of before/after measurements, for the record."""
    x, rate, _ch = read_wav(src)
    y = process(x, rate, trim_db=trim_db, smear_amount=smear_amount)
    write_wav(dst, y, rate)

    crest = crest_db
    return {'rate': rate, 'samples': len(x),
            'in_peak': round(_peak(x), 4), 'out_peak': round(_peak(y), 4),
            'in_rms': round(_rms(x), 5), 'out_rms': round(_rms(y), 5),
            'in_crest_db': round(crest(x), 2), 'out_crest_db': round(crest(y), 2)}


# ------------------------------------------------------------------------ cli
def _check(rate=FIT_RATE):
    c = cascade(rate=rate)
    pts = [(f, w) for f, w in TARGET if f < 0.45 * rate]
    worst = 0.0
    print('  at %g Hz, %d of %d target points in band'
          % (rate, len(pts), len(TARGET)))
    print('  %7s %8s %8s %7s' % ('Hz', 'vanilla', 'ours', 'err'))
    for f, want in pts:
        got = db_at(c, f, rate)
        worst = max(worst, abs(got - want))
        print('  %7d %8.1f %8.1f %7.1f' % (f, want, got, got - want))
    rms = math.sqrt(sum((db_at(c, f, rate) - w) ** 2 for f, w in pts) / len(pts))
    print('  rms %.2f dB, worst %.1f dB' % (rms, worst))
    print('  below the fitted band, the high-pass alone:')
    for f in (30, 50, 63, 79):
        print('  %7d %8s %8.1f' % (f, '-', db_at(c, f, rate)))


def main(argv):
    rate = FIT_RATE
    if '--rate' in argv:
        rate = float(argv[argv.index('--rate') + 1])
        argv = [a for a in argv if a != '--rate' and a != repr(rate)]
        argv = [a for a in argv if not a.replace('.', '').isdigit()]
    if '--fit' in argv:
        p, rms = fit(rate=rate)
        print('rate %g, rms error %.2f dB' % (rate, rms))
        print('    %d: %s,' % (int(rate), [round(v, 3) for v in p]))
        return 0
    if '--check' in argv:
        _check(rate)
        return 0
    args = [a for a in argv if not a.startswith('-')]
    if len(args) != 2:
        print(__doc__)
        return 2
    print(filter_file(args[0], args[1]))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
