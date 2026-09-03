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
   without waiting on a recording session.
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
# THE SPLICED-VOICES RECAST (2026-09-02). Most V and Johnny lines now REUSE
# RECORDED GAME LINES whole via `vanilla_sid` in gen_scenes, so the game's own
# registration supplies audio, text and both bodies, and those keys are
# DELIBERATELY ABSENT here - generating one would override a real performance
# with a stand-in. What remains in CAST is only what ships produced audio:
#
#   elena / hoshino        invented characters, recorded by people
#   nix                     one line cut from his OWN vanilla recordings (n01)
#   mama                    one line cut from HER own vanilla recordings (m03);
#                           everything else she says is a whole vanilla take
#   v                       three lines CUT from V's vanilla recordings (trims;
#                           both bodies), never joined fragments
#
# The full pick table with source stringIds and cut recipes is
# mods/gig-01-negative-balance/docs/corpus-recast.md.
CAST = {
    'elena':   {'gig01_elena_call': ['e01', 'e02', 'e03', 'e04',
                                     'e05', 'e06', 'e07', 'e07b', 'e08']},
    'hoshino': {'gig01_hoshino': ['h01', 'h02']},
    # NIX SPEAKS ONLY IN HIS OWN RECORDINGS as of 2026-09-03. His generated
    # takes (b02, b05) went with the minimal brief call, and his callback
    # went entirely: it is a text message now. What is left is n01, a verified
    # HEAD-TRIM of his own line "Should take me, I dunno... four, five
    # hours? Le'ss say we meet in six at the Arasaka Memorial" - cut at the
    # pause, read back before promotion. The video twin is byte-identical,
    # enforced by check_holo_twins below.
    'nix':     {'gig01_nix_brief': ['n01', 'n02'],
                'gig01_nix_brief_holo': ['n01', 'n02']},
    # MAMA WELLES IS HER OWN VOICE as of 2026-09-03, which retires the last
    # imitation of a real performer in this gig. m01/m02 were generated and
    # are gone; m03 is a head-trim of her own "She's a nice girl. We exchanged
    # numbers." and everything else she says is a whole vanilla take through
    # vanilla_sid, which needs no entry here.
    'mama':    {'gig01_epilogue': ['m03']},
    # V keeps exactly three produced lines, all in Elena's call, each a
    # verified TRIM of one of his own recordings, each in both bodies. Every
    # other V and Johnny line in the gig is a whole vanilla take.
    'v':       {'gig01_elena_call': ['v02', 'v04', 'v05']},
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


def check_holo_twins():
    """A video-call take must be the same recording as its voice-call twin.

    The two Nix calls exist twice, `<scene>` and `<scene>_holo`, because a scene
    is what carries audio and the video route needs its own. Same words, same
    order, and the audio is meant to be a straight copy: see CAST above.

    NOTHING ENFORCED THAT, and it broke silently. The voice-actor takes were
    installed under the voice-call names only, so for weeks Nix and V spoke in
    the actor's voice everywhere in the gig EXCEPT during his two calls, which
    are the route the quest tries first. 21 of 22 twins had diverged before
    anyone looked, and the give-away was a comment claiming they were identical.

    Fatal rather than a warning, because the symptom is a voice change mid-gig
    that a build reports as success. If a video take is ever meant to differ,
    change this function and say why.
    """
    holo = [f for f in os.listdir(AUDIO_SRC)
            if f.endswith('.wav') and '_holo__' in f]
    drifted = []
    for f in sorted(holo):
        twin = os.path.join(AUDIO_SRC, f.replace('_holo__', '__'))
        if not os.path.exists(twin):
            continue
        with open(os.path.join(AUDIO_SRC, f), 'rb') as a, open(twin, 'rb') as b:
            if a.read() != b.read():
                drifted.append(f)
    if drifted:
        lines = ['These video-call takes are not copies of their voice-call twin:']
        lines += ['  ' + f for f in drifted]
        lines += ['',
                  'A new take was installed under one name and not the other, so',
                  'the two Nix calls would use different voices. Copy each one',
                  'over from the name without `_holo`.']
        raise SystemExit(chr(10).join(lines))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--placeholder', action='store_true',
                    help='synthesise tones at the estimated length instead of '
                         'expecting real recordings')
    args = ap.parse_args()

    texts = line_texts(gs.ALL_BUILDERS)
    holocall = holocall_lines(gs.ALL_BUILDERS)
    os.makedirs(AUDIO_SRC, exist_ok=True)
    check_holo_twins()

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
    # WHY NOT RECORD THEM TWICE: two takes of the same words are two different
    # performances, so the two variants would not match. It is also unnecessary - the
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

    with open(DURATIONS, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(durations, fh, indent=2, sort_keys=True)
    print('wrote %s (%d measured durations)' % (DURATIONS, len(durations)))

    write_vomap(vomap)
    print('\nNow re-run gen_scenes.py - it reads durations.json and will re-time '
          'the sections to the real clips.')


if __name__ == '__main__':
    main()
