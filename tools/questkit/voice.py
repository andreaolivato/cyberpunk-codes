r"""Voice pipeline: WAV to WEM through Wwise, and the voiceover map.

The reusable half of the audio pipeline. The steps are the same whatever
produced the WAV, including a microphone, and they are the answer to "how do
I get any custom sound into Cyberpunk 2077".

HOW A SCENE LINE FINDS ITS AUDIO, because nothing here makes sense without it.
A scene line carries a scnlocLocstringId RUID. The game resolves BOTH its
subtitle and its voiceover from that one number: the subtitle through a
localizationPersistenceSubtitleEntries resource, the audio through a
locVoiceoverMap. A voiceover map is a flat global registry of
locVoLineEntry { stringId, femaleResPath, maleResPath } with no scene, quest or
actor scoping at all, so a mod supplies its own and ArchiveXL merges it under
`localization: vomaps:`.

The consequence is that Audioware is not needed and never was: there is no
playback layer and no script driver, the engine resolves the clip natively and
picks the gender variant itself. Players install nothing extra.

The other consequence is that a line can only be voiced IF IT LIVES IN A SCENE.
Text pushed from redscript is a caption with no RUID, so no voiceover map can
ever key on it. See docs/architecture.md.
"""
import hashlib  # write_tone pitches a placeholder by a hash of its line key
import json  # noqa: F401
import math    # write_tone
import os
import struct  # noqa: F401
import subprocess  # noqa: F401
import tempfile  # noqa: F401
import wave  # noqa: F401

# The CR2W primitives are defined once, in the scene builder.
from questkit import cr2w
from questkit.scene import resref

# --------------------------------------------------------------- per-mod config
WEM_OUT = None
VOMAP_OUT = None
DEPOT_VO = None
AUDIO_SRC = None


def configure(wem_out, vomap_out, depot_vo, audio_src):
    r"""Point the pipeline at one mod's audio tree.

    wem_out    where converted .wem files are written
    vomap_out  the locVoiceoverMap resource
    depot_vo   their path once packed, e.g. 'mod\<name>\audio\vo'
    audio_src  where the WAV masters live
    """
    global WEM_OUT, VOMAP_OUT, DEPOT_VO, AUDIO_SRC
    WEM_OUT, VOMAP_OUT, DEPOT_VO, AUDIO_SRC = wem_out, vomap_out, depot_vo, audio_src


WWISE = os.environ.get(
    'WWISE_CONSOLE',
    r'C:\Audiokinetic\Wwise_2019.2.15.7667\Authoring\x64\Release\bin\WwiseConsole.exe')
# Created on demand and kept out of the repo - it is a tool cache, not source.
WWISE_PROJ = os.path.join(tempfile.gettempdir(), 'cc-wwise', 'CCVoice', 'CCVoice.wproj')
# A factory ShareSet. Vorbis is core Wwise, not a plug-in, so a bare install has
# this without anything extra being ticked in the launcher.
CONVERSION = 'Vorbis Quality High'


def stem(scene, key):
    return '%s__%s' % (scene, key)


def line_texts(builders):
    """(scene, key) -> text, taken from the scenes themselves rather than a
    second copy of the script that could drift out of step."""
    out = {}
    for build in builders:
        scene = build()
        for key, text in scene.line_text.items():
            out[(scene.name, key)] = text
    return out


def holocall_lines(builders):
    """{(scene, key)} for every line spoken through the phone.

    Same source as line_texts and for the same reason: the scene builder already
    says which sections are holocalls, so nothing here has to be listed twice.
    These are the takes that get the phone filter baked in - questkit/phone.py.
    """
    out = set()
    for build in builders:
        scene = build()
        for key in scene.holocall_keys:
            out.add((scene.name, key))
    return out


# ------------------------------------------------------------------ placeholders
def write_tone(path, ms, key):
    """A tone of the right length, pitched by the key so you can tell lines
    apart by ear. 220-660 Hz, faded at both ends so it is not a click."""
    rate = 48000
    n = max(1, int(rate * ms / 1000.0))
    freq = 220.0 + (int(hashlib.md5(key.encode()).hexdigest()[:4], 16) % 440)
    fade = min(n // 8, int(rate * 0.05))
    frames = bytearray()
    for i in range(n):
        amp = 9000.0
        if i < fade:
            amp *= i / fade
        elif i > n - fade:
            amp *= (n - i) / fade
        frames += struct.pack('<h', int(amp * math.sin(2 * math.pi * freq * i / rate)))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(bytes(frames))


def wav_ms(path):
    """Duration of a WAV, by reading the RIFF chunks directly.

    NOT `wave.open`. The stdlib module handles PCM only and raises
    `unknown format: 3` on the IEEE-float WAVs some tools write. That failure
    once passed silently: the build carried on and packed the PREVIOUS run's
    audio.
    """
    data = open(path, 'rb').read(1024 * 1024)
    if data[:4] != b'RIFF' or data[8:12] != b'WAVE':
        raise SystemExit('%s is not a RIFF/WAVE file' % path)
    rate = channels = bits = 0
    off, size = 12, os.path.getsize(path)
    while off + 8 <= len(data):
        cid = data[off:off + 4]
        csz = struct.unpack('<I', data[off + 4:off + 8])[0]
        if cid == b'fmt ':
            _fmt, channels, rate = struct.unpack('<HHI', data[off + 8:off + 16])
            bits = struct.unpack('<H', data[off + 22:off + 24])[0]
        elif cid == b'data':
            # The header may claim a size the file does not have (streamed
            # writers leave it at 0 or 0xFFFFFFFF); trust the file.
            actual = min(csz, size - (off + 8))
            frame = max(1, channels * (bits // 8))
            return int(round(1000.0 * actual / frame / rate))
        off += 8 + csz + (csz & 1)
    raise SystemExit('%s has no data chunk' % path)


# ------------------------------------------------------------------------ wwise
def ensure_project():
    if os.path.exists(WWISE_PROJ):
        return
    if not os.path.exists(WWISE):
        raise SystemExit(
            'WwiseConsole not found at %s.\nInstall Wwise 2019.2.15 (Authoring + '
            'Windows platform) or set WWISE_CONSOLE.' % WWISE)
    os.makedirs(os.path.dirname(os.path.dirname(WWISE_PROJ)), exist_ok=True)
    # Wwise insists the .wproj sit in a folder of the same name.
    subprocess.run([WWISE, 'create-new-project', WWISE_PROJ,
                    '--platform', 'Windows', '--quiet'], check=True)
    print('created Wwise project %s' % WWISE_PROJ)


def convert(wavs):
    """wavs: [(abs wav path, output .wem name)] -> writes into WEM_OUT."""
    if not wavs:
        return
    ensure_project()
    os.makedirs(WEM_OUT, exist_ok=True)
    # One Root with relative paths under it, because real takes and placeholders
    # live in sibling folders and a wsources file has only one Root.
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<ExternalSourcesList SchemaVersion="1" Root="%s">' % AUDIO_SRC]
    for wav, out in wavs:
        rel = os.path.relpath(wav, AUDIO_SRC)
        lines.append('    <Source Path="%s" Conversion="%s" Destination="%s"/>'
                     % (rel, CONVERSION, out))
    lines.append('</ExternalSourcesList>')

    # Wwise writes into <output>\<platform>\, so convert into a temp dir and
    # lift the files out - the depot path has no platform folder in it. The
    # wsources goes in there too; it is scratch, not something to keep.
    with tempfile.TemporaryDirectory() as tmp:
        ws = os.path.join(tmp, 'generated.wsources')
        with open(ws, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write('\n'.join(lines) + '\n')
        subprocess.run([WWISE, 'convert-external-source', WWISE_PROJ,
                        '--source-file', ws, '--output', tmp,
                        '--platform', 'Windows', '--quiet'], check=True)
        produced = os.path.join(tmp, 'Windows')
        made = 0
        for _wav, out in wavs:
            src = os.path.join(produced, out)
            if not os.path.exists(src):
                    raise SystemExit('Wwise produced no %s from %s' % (out, ws))
            with open(src, 'rb') as a, open(os.path.join(WEM_OUT, out), 'wb') as b:
                b.write(a.read())
            made += 1
    print('converted %d wav -> wem in %s' % (made, WEM_OUT))


def check_wem(path):
    """Cheap sanity check: it must be RIFF/WAVE with a Wwise Vorbis fmt chunk.
    A silent line in game is expensive to diagnose; a wrong codec is not."""
    d = open(path, 'rb').read(96)
    if d[:4] != b'RIFF' or d[8:12] != b'WAVE':
        raise SystemExit('%s is not a RIFF/WAVE file' % path)
    if d[12:16] != b'fmt ':
        raise SystemExit('%s has no fmt chunk where one is expected' % path)
    codec, channels, rate = struct.unpack('<HHI', d[20:28])
    if codec != 0xFFFF:
        raise SystemExit('%s is codec 0x%04X, not Wwise Vorbis (0xFFFF) - the '
                         'conversion ShareSet is wrong' % (path, codec))
    return channels, rate


# ------------------------------------------------------------------------ vomap
def write_vomap(entries, out=None):
    """entries: [(stringId, female wem, male wem)].

    The two paths are usually the same file - most speakers here are NPCs and
    the split exists for V, who is recorded twice. Mama Welles is the exception
    that makes it earn its keep (see GENDERED). `out` overrides VOMAP_OUT for
    the per-language maps locale_pass writes."""
    out = out or VOMAP_OUT
    doc = {
        'Header': cr2w.header(os.path.basename(out).replace('.json.json', '.json')),
        'Data': {
            'Version': 195, 'BuildVersion': 0,
            'RootChunk': {
                '$type': 'JsonResource',
                'cookingPlatform': 'PLATFORM_PC',
                'root': {'HandleId': '0', 'Data': {
                    '$type': 'locVoiceoverMap',
                    'entries': [
                        {
                            '$type': 'locVoLineEntry',
                            'femaleResPath': resref(DEPOT_VO + '\\' + fem),
                            'maleResPath': resref(DEPOT_VO + '\\' + male),
                            'stringId': sid,
                        }
                        for sid, fem, male in entries
                    ],
                }},
            },
            'EmbeddedFiles': [],
        },
    }
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(doc, fh, indent=2)
    print('wrote %s (%d voiceover entries)' % (out, len(entries)))


# ------------------------------------------------------- the dubbed languages
def locale_pass(ruid_of, vomap, holocall, holocall_src, aliases=None, filter_file=None):
    r"""One voice map per dubbed language, from the clips under
    `<audio_src>\<locale>\`.

    A line the game's own characters say is a vanilla take cut short, and the
    English cut is what ships until a cut of the same take in that language
    has been made and listened to. Each such
    cut is a WAV under the locale's folder, named exactly like the English
    one (`<scene>__<key>.wav`, `__m` for a second body). This converts them,
    writes `durations_<locale>.json` beside `durations.json` so gen_scenes can
    pace a section from the longest clip in any language, and writes
    `vomap_<locale>.json` as the English map with those lines swapped for the
    locale's clips. Every dubbed locale gets a map, identical to English where
    it has no clips, so the manifest can name them unconditionally.

    ruid_of(scene, key)  -> the line's RUID string, from gen_scenes
    vomap                the English entries [(ruid, fem wem, male wem)]
    holocall             {(scene, key)} of lines heard down a phone
    aliases              {alias scene: source scene}, as gen_scenes.SCENE_ALIASES
    filter_file          questkit.phone.filter_file, applied to holocall clips
    """
    from questkit.packs import PACKS
    aliases = aliases or {}
    by_ruid = {}
    for sid, fem, male in vomap:
        by_ruid[sid] = (fem, male)
    for loc in sorted(PACKS):
        folder = os.path.join(AUDIO_SRC, loc)
        clips = {}
        if os.path.isdir(folder):
            for fn in sorted(os.listdir(folder)):
                if not fn.lower().endswith('.wav'):
                    continue
                stem_g = fn[:-4]
                male = stem_g.endswith('__m')
                base = stem_g[:-3] if male else stem_g
                scene, key = base.split('__', 1)
                clips.setdefault((scene, key), {})['m' if male else 'f'] = os.path.join(folder, fn)
        wavs, durations, entries = [], {}, dict(by_ruid)
        for (scene, key), bodies in sorted(clips.items()):
            wems = {}
            k = '%s/%s' % (scene, key)
            for g, wav in bodies.items():
                if (scene, key) in holocall and filter_file:
                    filtered = os.path.join(holocall_src, loc, os.path.basename(wav))
                    os.makedirs(os.path.dirname(filtered), exist_ok=True)
                    filter_file(wav, filtered)
                    wav = filtered
                name = '%s__%s__%s%s.wem' % (loc, scene, key, '__m' if g == 'm' else '')
                wavs.append((wav, name))
                wems[g] = name
                durations[k] = max(durations.get(k, 0), wav_ms(wav))
            sid = ruid_of(scene, key)
            if sid not in entries:
                raise SystemExit('%s has a clip for %s/%s, which the English map '
                                 'does not voice' % (loc, scene, key))
            en_fem, en_male = entries[sid]
            # A body without a clip of its own keeps the English one. A line
            # with a single recording (the English map names one file for
            # both bodies) gives that recording to both.
            fem = wems.get('f') or en_fem
            if 'm' in wems:
                male = wems['m']
            elif en_fem == en_male and 'f' in wems:
                male = wems['f']
            else:
                male = en_male
            entries[sid] = (fem, male)
            for alias, src in aliases.items():
                if src == scene:
                    entries[ruid_of(alias, key)] = (fem, male)
                    durations['%s/%s' % (alias, key)] = durations[k]
        convert(wavs)
        for _wav, out_name in wavs:
            check_wem(os.path.join(WEM_OUT, out_name))
        dpath = os.path.join(AUDIO_SRC, 'durations_%s.json' % loc)
        if durations:
            with open(dpath, 'w', encoding='utf-8', newline='\n') as fh:
                json.dump(durations, fh, indent=2, sort_keys=True)
        elif os.path.exists(dpath):
            os.remove(dpath)
        write_vomap([(sid, fem, male) for sid, (fem, male) in entries.items()],
                    out=VOMAP_OUT.replace('.json.json', '_%s.json.json' % loc))
        if clips:
            print('  %s: %d line(s) in that language, %d clip(s)' % (loc, len(clips), len(wavs)))


