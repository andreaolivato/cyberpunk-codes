r"""The Trauma Team mask: what Brekke's takes go through before Wwise.

The curve is the game's own helmet treatment. The game ships a `vo_helmet` copy of
some lines, so the difference between 23 matched pairs was measured band by band.
`STRENGTH` makes it heavier, a lift at 1.1 kHz gives the hollow of a hard shell,
and three short reflections put the voice inside it. The master stays dry and the
copy is what gets converted, the way a phone line is treated (questkit.phone).
"""
import numpy as np
import soundfile as sf

SR = 48000
# Centre of each band in Hz, and the helmet copies' level against the plain ones in dB.
BANDS = [
    (150, -9.1), (212, -4.4), (296, -5.2), (418, -0.6), (592, 2.6), (837, 1.5),
    (1183, 0.3), (1673, -1.9), (2366, -4.3), (3347, -8.7), (4733, -13.5),
    (6693, -13.2), (9381, -12.9), (13266, -16.7), (18762, -18.8),
]
STRENGTH = 1.6
HOLLOW_DB = 7.0
HOLLOW_HZ = 1100.0
REFLECTIONS = ((1.7, 0.45), (3.3, 0.3), (5.9, 0.16))    # ms, gain
DRIVE = 2.2
# One plain gain on every line, the loudest peak at -1.2 dB. Playtest 2026-11-05:
# he was too quiet beside Wrona and Raman in the AV.
LEVEL_DB = 7.5
TAPS = 8192


def _fir():
    freqs = np.fft.rfftfreq(TAPS, 1.0 / SR)
    safe = np.maximum(freqs, 30.0)
    hz, level = zip(*BANDS)
    curve = STRENGTH * np.interp(np.log(safe), np.log(hz), level)
    curve += HOLLOW_DB * np.exp(-0.5 * (np.log(safe / HOLLOW_HZ) / 0.35) ** 2)
    fir = np.fft.irfft(10.0 ** (curve / 20.0), TAPS)
    return np.roll(fir, TAPS // 2) * np.hanning(TAPS)


def treat(samples):
    """Same length, about the same loudness plus 10 percent for the lost top, then LEVEL_DB."""
    size = len(samples) + TAPS
    wet = np.fft.irfft(np.fft.rfft(samples, size) * np.fft.rfft(_fir(), size), size)
    wet = wet[TAPS // 2:TAPS // 2 + len(samples)]
    out = wet.copy()
    for ms, gain in REFLECTIONS:
        lag = int(ms / 1000.0 * SR)
        out[lag:] += gain * wet[:-lag]
    top = np.abs(out).max()
    out = np.tanh(out / top * DRIVE) / np.tanh(DRIVE) * top
    return out * np.sqrt((samples ** 2).mean() / (out ** 2).mean()) * 1.1 * 10.0 ** (LEVEL_DB / 20.0)


def treat_file(src, dst):
    samples, rate = sf.read(src)
    if rate != SR:
        raise SystemExit('%s is %d Hz, not %d' % (src, rate, SR))
    sf.write(dst, treat(samples), SR, subtype='PCM_16')
