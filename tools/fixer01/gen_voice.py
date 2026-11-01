r"""Voice pipeline for Fixer 01: WAV -> phone treatment -> WEM -> voiceover
map, plus the duration sidecar.

    python tools\fixer01\gen_voice.py                # real takes in source\audio
    python tools\fixer01\gen_voice.py --placeholder  # tones at the estimated length

A copy of tools/gig02/gen_voice.py, re-pointed; that file carries the full
account of how a scene line finds its audio. What is different here is the
cast: one invented speaker, Hodan Warsame, recorded by a voice actor (the
voice rules in docs/conventions.md). --placeholder writes a tone for a line
with no take, pitched by a hash of the line key so tones are
distinguishable by ear. A real take always beats a placeholder of the same
name.

Her lines are on a call, so each take is run through the phone treatment
into a copy (tools/questkit/phone.py) and the copy is what Wwise converts.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# questkit is in tools/, one level up from this gig's generators.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gen_scenes as gs                                             # noqa: E402
from questkit.voice import (                                        # noqa: F401,E402
    configure, stem, line_texts, holocall_lines, write_tone, wav_ms, convert,
    check_wem, write_vomap, locale_pass, WWISE, WWISE_PROJ, CONVERSION,
)
from questkit import phone                                          # noqa: E402
from fixer01_config import SOURCE, RAW_MOD, DEPOT                     # noqa: E402

AUDIO_SRC = os.path.join(SOURCE, 'audio')
# Placeholders live in their own folder and are NOT tracked. They are throwaway
# by definition, and a real take and a beep sharing a filename would be a nasty
# thing to mix up.
PLACEHOLDER_SRC = os.path.join(AUDIO_SRC, 'placeholder')
# Where the phone-filtered copies of the holocall takes are written. Derived
# from the master beside it, so gitignored; the filter is questkit/phone.py.
HOLOCALL_SRC = os.path.join(AUDIO_SRC, 'holocall')
DURATIONS = os.path.join(AUDIO_SRC, 'durations.json')
WEM_OUT = os.path.join(RAW_MOD, 'audio', 'vo')
VOMAP_OUT = os.path.join(RAW_MOD, 'localization', 'vomap.json.json')
DEPOT_VO = DEPOT + chr(92) + 'audio' + chr(92) + 'vo'


# ---------------------------------------------------------------- what is voiced
#
# ONE TABLE: which lines ship audio of ours, and which voice reads them. The
# keys are gen_scenes' own line keys, so a typo stops the run instead of
# producing a line that is silently never voiced.
# Her answer keys, read off the conversation table so a line added there
# is voiced here without a second edit.
HER_ANSWERS = sorted(
    {t[2] for _c, _k, turns in gs.TALK for t in turns if t[0] == 'H'}
    | {t[2] for _f, _c, _v, turns in gs.AFTER_THE_GIG.values()
       for t in turns if t[0] == 'H'})

CAST = {
    'hodan': {
        'fixer01_intro': ['n01', 'n02', 'n03'],
        'fixer01_face': HER_ANSWERS,
        'fixer01_call': HER_ANSWERS,
    },
}

# ONE TAKE, TWO SCENES. Her five answers are the same words in person and
# on the phone, so the actor records each once: the phone scene's master
# for a key is the in-person scene's file, and the phone copy is what gets
# the treatment (the dry take plays in person, the filtered one in the
# call, which is how the game ships its own pairs; gotcha 41). Not
# gen_scenes.SCENE_ALIASES, which would point both scenes at ONE clip.
MASTER_SCENE = {
    'fixer01_call': 'fixer01_face',
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

# Nobody here is V, so no line differs by the player's body type.
GENDERED = set()


configure(wem_out=WEM_OUT, vomap_out=VOMAP_OUT, depot_vo=DEPOT_VO,
          audio_src=AUDIO_SRC)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--placeholder', action='store_true',
                    help='synthesise tones at the estimated length instead of '
                         'expecting real recordings')
    args = ap.parse_args()

    texts = line_texts(gs.ALL_BUILDERS)
    holocall = holocall_lines(gs.ALL_BUILDERS)
    os.makedirs(AUDIO_SRC, exist_ok=True)
    os.makedirs(WEM_OUT, exist_ok=True)

    wavs, durations, vomap = [], {}, []
    phoned = 0
    emitted = {}
    missing = []
    for scene, keys in sorted(VOICED.items()):
        for key in keys:
            if (scene, key) not in texts:
                raise SystemExit('CAST names %s/%s, which is not a line in that '
                                 'scene. gen_scenes and gen_voice have drifted'
                                 % (scene, key))
            name = stem(scene, key)
            master = stem(MASTER_SCENE.get(scene, scene), key)
            wav = os.path.join(AUDIO_SRC, master + '.wav')
            if not os.path.exists(wav):
                wav = os.path.join(PLACEHOLDER_SRC, master + '.wav')
                if not os.path.exists(wav):
                    if args.placeholder:
                        write_tone(wav, gs.estimate_ms(texts[(scene, key)]),
                                   master)
                    else:
                        missing.append(master + '.wav')
                        continue
                elif not args.placeholder:
                    print('  ! %s is still a PLACEHOLDER tone' % name)
            # THROUGH THE PHONE. A holocall line is not the clean take played
            # differently: vanilla ships a separately processed recording for
            # every line that arrives on V's phone, with the treatment baked
            # into the asset. Ours is baked here, into a COPY, so the master
            # stays dry. A take that had already been processed would be
            # processed twice and nothing would catch it.
            if (scene, key) in holocall:
                filtered = os.path.join(HOLOCALL_SRC, name + '.wav')
                phone.filter_file(wav, filtered)
                wav = filtered
                phoned += 1
            wavs.append((wav, name + '.wem'))
            durations['%s/%s' % (scene, key)] = wav_ms(wav)

            male_wem = name + '.wem'
            if (scene, key) in GENDERED:
                male_wav = os.path.join(AUDIO_SRC, name + '__m.wav')
                if not os.path.exists(male_wav) and args.placeholder:
                    # A PLACEHOLDER GETS BOTH TAKES, so the gendered route is
                    # exercised rather than assumed. The male tone is written
                    # under its own key, so it is a different pitch and the two
                    # are distinguishable by ear.
                    male_wav = os.path.join(PLACEHOLDER_SRC, name + '__m.wav')
                    if not os.path.exists(male_wav):
                        write_tone(male_wav,
                                   gs.estimate_ms(texts[(scene, key)]),
                                   name + '__m')
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
                    # the player is, the line must finish before the scene moves
                    # on.
                    durations['%s/%s' % (scene, key)] = max(
                        durations['%s/%s' % (scene, key)], wav_ms(male_wav))
                else:
                    print('  ! %s is gendered but %s__m.wav is missing, so a '
                          'male V will hear the female take' % (name, name))
            vomap.append((gs.locstring_ruid(scene, key), name + '.wem', male_wem))
            emitted[(scene, key)] = (name + '.wem', male_wem)

    if missing:
        raise SystemExit(
            'no audio for %d line(s): %s\n\n'
            'The WAV masters are not committed, so a fresh clone has none and '
            'does not need any: the .wem are shipped and the generated '
            r'resources are committed. To build the mod just run '
            r'tools\build-archive.ps1.'
            '\n'
            'Re-run this only when the dialogue changes. Then put WAVs in %s, '
            'or pass --placeholder for tones.'
            % (len(missing), ', '.join(missing), AUDIO_SRC))

    for alias, src in sorted(gs.SCENE_ALIASES.items()):
        n = 0
        for (scene, key), (fem_wem, male_wem) in sorted(emitted.items()):
            if scene != src:
                continue
            if (alias, key) not in texts:
                raise SystemExit('%s aliases %s but has no line %s. The two '
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
    # THE DUBBED LANGUAGES: one voice map per dubbed locale, identical to the
    # English one, so the manifest can name them unconditionally (the shape
    # every gig's manifest has since the translations work; gotcha 121).
    # She has no clip in any other language: V's questions are the game's
    # own lines, which the game dubs itself, and her answers are the
    # actor's, English everywhere. See questkit.voice.locale_pass.
    locale_pass(gs.locstring_ruid, vomap, holocall, HOLOCALL_SRC,
                aliases=getattr(gs, 'SCENE_ALIASES', {}),
                filter_file=phone.filter_file)
    print('\nNow re-run gen_scenes.py. It reads durations.json and will '
          're-time the sections to the real clips.')


if __name__ == '__main__':
    main()
