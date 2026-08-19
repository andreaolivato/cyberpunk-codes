r"""Voice pipeline: WAV -> WEM -> voiceover map, plus the duration sidecar.

WHY THIS EXISTS, and why it is not Audioware.

A scene line resolves BOTH its subtitle text and its audio from one number: the
`scnlocLocstringId.ruid` the scene carries. Text comes from a
`localizationPersistenceSubtitleEntries` resource keyed by that RUID (gen_scenes
writes it). Audio comes from a `locVoiceoverMap` keyed by the SAME RUID in its
`stringId` - a flat, global, un-scoped list of
`{stringId, femaleResPath, maleResPath}`. ArchiveXL merges mod entries into it:
its `localization:` section accepts `vomaps` and `lipmaps` as well as `onscreens`
and `subtitles`.

So a voiced scene line needs no script driver and no Audioware at all. See
`docs/backlog.md` 2a - which used to say the opposite, and was wrong.

**AUDIOWARE IS NOT A DEPENDENCY OF THIS MOD, at all.** This note used to end
"Audioware IS still needed for the scripted subtitle beats in
`Gig01_Encounter.Line()`" - and that stopped being true on 2026-08-13, when the
last caption beat was rebuilt as a scene. `Line()` no longer exists. Every line
in the gig is a scene line, so every line is voiced by the mechanism above and
players install nothing extra.

WHAT THIS SCRIPT DOES

    python tools\gig01\gen_voice.py --placeholder    # tones at the estimated length
    python tools\gig01\gen_voice.py                  # real WAVs from source\audio\

1. For every voiced line, finds `source\audio\<scene>__<key>.wav`. With
   `--placeholder`, synthesises one first: a tone at the length gen_scenes would
   have guessed, pitched by a hash of the key so lines are distinguishable by
   ear. That is the whole point of the placeholder stage - it proves the wiring
   without waiting on a TTS model.
2. Converts them to `.wem` with Wwise (see below).
3. Measures each WAV and writes `source\audio\durations.json`, which gen_scenes
   reads INSTEAD of its 1200ms + 55ms/char estimate. Timing then comes from the
   audio rather than from a guess about it.
4. Emits the voiceover map into the raw tree.

WWISE

`.wem` is Wwise Vorbis in a RIFF container and only Wwise can write it - WolvenKit
answers "Use WolvenKit to import opus" and imports nothing; REDmod's
`resource-import` lists no audio format at all. Version matters: 2019.2.15. The
conversion is headless via `WwiseConsole convert-external-source`, driven by a
generated `.wsources` file, so nobody has to open the GUI. Setting `Destination`
in the wsources also avoids the `_XXXXXXXX` hash suffix the guides tell you to
strip by hand.

Verified against the shipped files: our output and vanilla's are both codec
0xFFFF (Wwise Vorbis), mono, 48 kHz, with a 66-byte `fmt ` chunk. Vanilla
additionally carries a 16-byte `hash` chunk that external-source conversion does
not emit; believed to be a build-cache aid rather than something the runtime
needs, but it is the first thing to suspect if a line plays silent.
"""
import argparse
import hashlib
import json
import math
import os
import struct
import subprocess
import sys
import tempfile
import wave      # writing placeholder tones only; see wav_ms() for why not reading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# questkit is in tools/, one level up from this gig's generators. See
# backlog.md 21.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import argparse
import json
import os

import gen_scenes as gs
# The Wwise conversion and the voiceover map live in tools/questkit/voice.py. This
# file is the GIG: which lines are voiced, by whom, and which have a male take.
from questkit.voice import (                                        # noqa: F401
    configure, stem, line_texts, holocall_lines, write_tone, wav_ms, convert,
    check_wem, write_vomap, WWISE, WWISE_PROJ, CONVERSION,
)
from questkit import phone

_TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(_TOOLS)
MOD = os.path.join(REPO, 'mods', 'gig-01-negative-balance')
AUDIO_SRC = os.path.join(MOD, 'source', 'audio')
# Placeholders live in their own folder and are NOT tracked. They are throwaway
# by definition - regenerating them is one command - and a real take and a beep
# sharing a filename would be a nasty thing to mix up. Which lines have
# real audio is then visible from a directory listing.
PLACEHOLDER_SRC = os.path.join(AUDIO_SRC, 'placeholder')
# Where the phone-filtered copies of the holocall takes are written. Derived
# from the master next to them and gitignored for that reason; the filter is in
# tools/questkit/phone.py and the measurement behind it is docs/backlog.md 15.
HOLOCALL_SRC = os.path.join(AUDIO_SRC, 'holocall')
DURATIONS = os.path.join(AUDIO_SRC, 'durations.json')
WEM_OUT = os.path.join(MOD, 'source', 'wkit', 'raw', 'mod', 'negative_balance',
                       'audio', 'vo')
VOMAP_OUT = os.path.join(MOD, 'source', 'wkit', 'raw', 'mod', 'negative_balance',
                         'localization', 'vomap.json.json')
DEPOT_VO = 'mod\\negative_balance\\audio\\vo'


# ---------------------------------------------------------------- what is voiced
#
# WHO SAYS WHAT. One table, because the alternative was three that could drift:
# gen_voice needs "which lines have audio" and "which are gendered", and
# the speech step needs "which voice reads this line". All three are answers to
# the same question.
#
# The keys are gen_scenes' own line keys; the RUID is derived from
# (scene name, key) exactly as gen_scenes derives it, so the two cannot drift
# without the build failing loudly.
#
# Lines DELIBERATELY absent, and they must stay absent - each one reuses a
# recorded vanilla line, so the game's own registration supplies the audio and
# generating one would override a real performance with a synthetic one:
#   gig01_nix_brief/b01   Nix,  "How's things, V?"
#   gig01_nix_call/on1    V,    "Where."
#   gig01_nix_call/on2    V,    "On my way."
CAST = {
    'elena':   {'gig01_elena_call': ['e01', 'e02', 'e03', 'e04',
                                     'e05', 'e06', 'e07', 'e08']},
    'hoshino': {'gig01_hoshino': ['h01', 'h02']},
    # n02 ("Hoshino's the choke point.") retired 2026-08-13 when the design widened
    # the comic-verbatim exception to Nix - n05/n06 replace it. Its .wem stays
    # in source/audio, unreferenced; the key is not reused.
    'nix':     {'gig01_nix_brief': ['b02', 'b03', 'b04', 'b05'],
                'gig01_nix_call': ['n01', 'n05', 'n06', 'n03', 'n04']},
    'mama':    {'gig01_epilogue': ['m01', 'm02']},
    # Johnny and V arrived 2026-08-13, when the bar ending stopped being a pair
    # of scripted captions and became a real scene, and when V's hub options
    # became spoken lines. Their remaining lines are still captions and still
    # unvoiceable - see BUILDING.md, "Audio toolchain".
    'johnny':  {'gig01_bar': ['j01'],
                'gig01_arasaka': ['ja1'],
                # p30. Moved out of gig01_nix_call into its own beat on
                # 2026-08-14 so it plays AFTER the phone is down - the clips
                # were copied to the new keys, md5-identical, nothing
                # regenerated. See gen_scenes.build_graves().
                'gig01_graves': ['j30a', 'j30b'],
                # p25 moved out of gig01_terminal into gig01_netrunner on
                # 2026-08-13 so it lands AFTER the shard. The clips moved by
                # COPYING, keeping their t0N keys.
                # t09 came home when gig01_netrunner was merged back into
                # gig01_terminal on 2026-08-14 - the split had no gate in it.
                'gig01_terminal': ['t02', 't04', 't09'],
                # closes the shard beat and gives his exit a reason
                'gig01_shard_read': ['j24'],
                'gig01_legend': ['l03', 'l04'],
                'gig01_kill': ['k02'],
                'gig01_malware': ['w02']},
    # gig01_bar v01 ("She'll never know.") retired 2026-08-13 - the gig's last
    # line now recaps. v02 replaces it; the old .wem stays, unreferenced.
    'v':       {'gig01_bar': ['v02'],
                'gig01_elena_call': ['v02', 'v03', 'v04', 'v05'],
                # v06 ("Got it. Wait. That's-") MOVED here from
                # gig01_elena_call on 2026-08-14. It is the line Johnny
                # interrupts, and a scene actor cannot exist before its own
                # scene starts - so with Johnny's body now owned by the arasaka
                # scene, the line had to come to him or he could never be on
                # screen for it. Same take: the WAVs were COPIED to the new key,
                # md5-identical, exactly as p25's were on 2026-08-13. Nothing
                # was regenerated.
                'gig01_arasaka': ['v06'],
                # vb3 ("Need to know where they are.") retired 2026-08-13 and
                # replaced by vb5/vb6 - the one sanctioned break in the
                # comic-verbatim rule, scoped to V's ask. Its .wem is still in
                # source/audio and is simply no longer referenced; do NOT reuse
                # the key, because a key is how audio finds a line.
                'gig01_nix_brief': ['vb1', 'vb2', 'vb5', 'vb6', 'vb4'],
                'gig01_shard_find': ['sf1'],
                # sr1 ("So that's where we fit.") retired 2026-08-13 - playtesting
                # asked for the beat to be explicit about the mercs. sr2 is
                # unchanged and still the comic's own line.
                'gig01_shard_read': ['sr3', 'sr2'],
                # on1/on2 were vanilla reuse until 2026-08-13. The stringId
                # filed as "Where." is actually "Where?!" and no vanilla
                # "Where." exists, so both are ours now - see
                # gen_scenes.build_nix().
                #
                # on2 ("On my way.") CUT 2026-08-14, the design call. Its .wem
                # stays in source/audio unreferenced, like every other retired
                # take; the key is not reused, because a key is how audio finds
                # a line.
                'gig01_nix_call': ['on1'],
                'gig01_hoshino': ['vh1'],
                'gig01_epilogue': ['ve1', 've2'],
                'gig01_terminal': ['t01', 't03', 't05', 't10'],
                # l01 retired 2026-08-13: "you become a legend" -> "a merc
                #  becomes a legend". l05 replaces it.
                'gig01_legend': ['l05', 'l02'],
                'gig01_kill': ['k01'],
                'gig01_malware': ['w01']},
}

VOICED = {}
CHARACTER_OF = {}
for _character, _scenes in CAST.items():
    for _scene, _keys in _scenes.items():
        VOICED.setdefault(_scene, []).extend(_keys)
        for _key in _keys:
            if (_scene, _key) in CHARACTER_OF:
                raise SystemExit('%s/%s is claimed by two characters in CAST'
                                 % (_scene, _key))
            CHARACTER_OF[(_scene, _key)] = _character

# Lines whose audio differs by PLAYER gender.
#
# Mama Welles says "mija" to a female V and "mijo" to a male one - the subtitle
# resource has carried both since the start. If the audio does not, a male V
# reads "mijo" while hearing "mija", which is worse than not voicing her.
#
# EVERY V LINE is gendered too, and for a larger reason than one word: he is a
# different actor depending on the player's body type, so the two takes are
# different VOICES rather than the same read with a swapped syllable.
#
# A second WAV named <stem>__m.wav supplies the male take; the voiceover map
# already has separate femaleResPath and maleResPath, so this costs nothing but
# the file.
GENDERED = ({('gig01_epilogue', 'm01')}
            | {k for k, c in CHARACTER_OF.items() if c == 'v'})



configure(wem_out=WEM_OUT, vomap_out=VOMAP_OUT, depot_vo=DEPOT_VO,
          audio_src=AUDIO_SRC)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--placeholder', action='store_true',
                    help='synthesise tones at the estimated length instead of '
                         'expecting real recordings')
    args = ap.parse_args()

    texts = line_texts(gs.ALL_BUILDERS)
    holocall = holocall_lines(gs.ALL_BUILDERS)
    os.makedirs(AUDIO_SRC, exist_ok=True)

    wavs, durations, vomap = [], {}, []
    phoned = 0
    # (scene, key) -> (female wem, male wem), so an aliased scene can point its
    # own RUIDs at clips that have already been converted.
    emitted = {}
    missing = []
    for scene, keys in sorted(VOICED.items()):
        for key in keys:
            if (scene, key) not in texts:
                raise SystemExit('VOICED names %s/%s, which is not a line in that '
                                 'scene - gen_scenes and gen_voice have drifted'
                                 % (scene, key))
            name = stem(scene, key)
            # A real take always wins over a placeholder, so the two can coexist
            # while the voices are generated a few at a time.
            wav = os.path.join(AUDIO_SRC, name + '.wav')
            if not os.path.exists(wav):
                wav = os.path.join(PLACEHOLDER_SRC, name + '.wav')
                if not os.path.exists(wav):
                    if args.placeholder:
                        write_tone(wav, gs.estimate_ms(texts[(scene, key)]), name)
                    else:
                        missing.append(name + '.wav')
                        continue
                elif not args.placeholder:
                    print('  ! %s is still a PLACEHOLDER tone' % name)
            # THROUGH THE PHONE. A holocall line is not the same recording
            # played differently. Vanilla ships a separately processed take for
            # every line that arrives on V's phone, with the treatment baked
            # into the asset, and the treatment is a phase effect rather than a
            # filter. Ours is baked here, into a copy, so the master stays the
            # clean studio take. See tools/questkit/phone.py.
            if (scene, key) in holocall:
                filtered = os.path.join(HOLOCALL_SRC, name + '.wav')
                phone.filter_file(wav, filtered)
                wav = filtered
                phoned += 1
            wavs.append((wav, name + '.wem'))
            durations['%s/%s' % (scene, key)] = wav_ms(wav)

            # A male-variant WAV, if this line has one, becomes maleResPath.
            male_wem = name + '.wem'
            if (scene, key) in GENDERED:
                male_wav = os.path.join(AUDIO_SRC, name + '__m.wav')
                if os.path.exists(male_wav):
                    if (scene, key) in holocall:
                        male_filtered = os.path.join(HOLOCALL_SRC,
                                                     name + '__m.wav')
                        phone.filter_file(male_wav, male_filtered)
                        male_wav = male_filtered
                        phoned += 1
                    male_wem = name + '__m.wem'
                    wavs.append((male_wav, male_wem))
                    # Pace the section from the LONGER of the two: whichever V
                    # the player is, the line must have finished before the
                    # scene moves on.
                    durations['%s/%s' % (scene, key)] = max(
                        durations['%s/%s' % (scene, key)], wav_ms(male_wav))
                else:
                    print('  ! %s is gendered but %s__m.wav is missing - a male V '
                          'will hear the female take' % (name, name))
            vomap.append((gs.locstring_ruid(scene, key), name + '.wem', male_wem))
            emitted[(scene, key)] = (name + '.wem', male_wem)

    # CHECK THIS FIRST. It used to sit after the alias loop below, so a clone
    # with no WAV masters died on "aliases X, which voiced nothing" instead of
    # on the real problem. That is the first thing a stranger running this repo
    # hits, and it named the wrong cause.
    if missing:
        raise SystemExit(
            'no audio for %d line(s): %s\n\n'
            'The WAV masters are not committed, so a fresh clone has none, and '
            'does not need any: the .wem are shipped and the generated resources '
            r'are committed. To build the mod just run tools\build-archive.ps1.'
            '\n'
            'Re-run this only when changing the dialogue. Then put WAVs in %s, '
            'or pass --placeholder for tones.'
            % (len(missing), ', '.join(missing), AUDIO_SRC))

    # ------------------------------------------------------ aliased scenes
    # A scene that reuses another scene's recordings (gs.SCENE_ALIASES). The
    # epilogue is played by one of two variants depending on whether the real
    # Mama Welles is in the bar, and they say the same four lines - so the
    # stand-in gets no recordings of its own.
    #
    # WHY NOT JUST GENERATE THEM: a re-run of the TTS re-rolls the voice, so the
    # two variants would be two different women. It is also unnecessary - the
    # voiceover map keys stringId -> wem path, so two RUIDs point at one file.
    # Nothing is converted here, nothing is copied on disk; only the map grows.
    for alias, src in sorted(gs.SCENE_ALIASES.items()):
        n = 0
        for (scene, key), (fem_wem, male_wem) in sorted(emitted.items()):
            if scene != src:
                continue
            if (alias, key) not in texts:
                raise SystemExit('%s aliases %s but has no line %s - the two '
                                 'scenes have drifted' % (alias, src, key))
            vomap.append((gs.locstring_ruid(alias, key), fem_wem, male_wem))
            durations['%s/%s' % (alias, key)] = durations['%s/%s' % (src, key)]
            n += 1
        if not n:
            raise SystemExit('%s aliases %s, which voiced nothing' % (alias, src))
        print('  %s reuses %d clip(s) from %s' % (alias, n, src))


    if phoned:
        print('  %d holocall take(s) filtered into %s' % (phoned, HOLOCALL_SRC))

    convert(wavs)
    for _wav, out in wavs:
        check_wem(os.path.join(WEM_OUT, out))

    with open(DURATIONS, 'w', encoding='utf-8') as fh:
        json.dump(durations, fh, indent=2, sort_keys=True)
    print('wrote %s (%d measured durations)' % (DURATIONS, len(durations)))

    write_vomap(vomap)
    print('\nNow re-run gen_scenes.py - it reads durations.json and will re-time '
          'the sections to the real clips.')


if __name__ == '__main__':
    main()
