r"""Voice pipeline for Trauma Team: WAV -> the mask -> WEM -> voiceover map, plus
the duration sidecar.

    python tools\gig05\gen_voice.py

Gig 04's (tools/gig04/gen_voice.py), without the phone and the placeholders. Run
gen_scenes.py before it and again after it: gen_scenes reads durations.json. The
masters in source\audio are not committed; the .wem are.

Brekke's lines go through tools/gig05/mask.py into a copy, because he wears the
mask. Nisha's face is bare. Wrona, Raman and V are the game's own recordings.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gen_scenes as gs                                             # noqa: E402
import mask                                                         # noqa: E402
from questkit.scene import locstring_ruid                           # noqa: E402
from questkit.scene import locstring_ruid                           # noqa: E402
from questkit.voice import (                                        # noqa: E402
    configure, stem, line_texts, holocall_lines, wav_ms, convert, check_wem,
    write_vomap, locale_pass,
)
from gig05_config import SOURCE, RAW_MOD, DEPOT                     # noqa: E402

AUDIO_SRC = os.path.join(SOURCE, 'audio')
# Derived from the masters, so not committed.
MASKED_SRC = os.path.join(AUDIO_SRC, 'masked')
DURATIONS = os.path.join(AUDIO_SRC, 'durations.json')
WEM_OUT = os.path.join(RAW_MOD, 'audio', 'vo')
VOMAP_OUT = os.path.join(RAW_MOD, 'localization', 'vomap.json.json')
DEPOT_VO = DEPOT + chr(92) + 'audio' + chr(92) + 'vo'

# Scene -> line keys. The keys are gen_scenes' own, so a typo stops the run.
NISHA = {'gig05_interview': ['r01', 'r09', 'r02', 'r03', 'r04', 'r05', 'r06', 'r07', 'r08']}
BREKKE = {
    'gig05_welcome': ['l20', 'l21', 'l22', 'l23'],
    'gig05_brief': ['l01', 'l02', 'l03', 'l04', 'l05'],
    'gig05_stable_1': ['l06', 'l07'],
    'gig05_brief2': ['l10', 'l11'],
    'gig05_land_2': ['l14'],
    'gig05_stable_2': ['l16', 'l17'],
    'gig05_brief3': ['l12', 'l13'],
    'gig05_land_3': ['l15'],
    'gig05_stable_3': ['l18', 'l19'],
    'gig05_home': ['l08'],
    'gig05_bye': ['l24', 'l25', 'l26'],
}

configure(wem_out=WEM_OUT, vomap_out=VOMAP_OUT, depot_vo=DEPOT_VO, audio_src=AUDIO_SRC)


def main():
    texts = line_texts(gs.ALL_BUILDERS)
    os.makedirs(WEM_OUT, exist_ok=True)
    os.makedirs(MASKED_SRC, exist_ok=True)
    wavs, durations, vomap, missing = [], {}, [], []
    for cast, masked in ((NISHA, False), (BREKKE, True)):
        for scene, keys in sorted(cast.items()):
            for key in keys:
                if (scene, key) not in texts:
                    raise SystemExit('%s/%s is not a line in that scene' % (scene, key))
                name = stem(scene, key)
                wav = os.path.join(AUDIO_SRC, name + '.wav')
                if not os.path.exists(wav):
                    missing.append(name + '.wav')
                    continue
                if masked:
                    copy = os.path.join(MASKED_SRC, name + '.wav')
                    mask.treat_file(wav, copy)
                    wav = copy
                wavs.append((wav, name + '.wem'))
                durations['%s/%s' % (scene, key)] = wav_ms(wav)
                vomap.append((locstring_ruid(scene, key), name + '.wem', name + '.wem'))
    if missing:
        raise SystemExit('no audio for %d line(s): %s' % (len(missing), ', '.join(missing)))
    convert(wavs)
    for _wav, out in wavs:
        check_wem(os.path.join(WEM_OUT, out))
    with open(DURATIONS, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(durations, fh, indent=2, sort_keys=True)
    write_vomap(vomap)
    # THE DUBBED LANGUAGES get a voice map too, the same as the English one, so the
    # manifest can name them. Nisha and Brekke are English everywhere.
    locale_pass(locstring_ruid, vomap, holocall_lines(gs.ALL_BUILDERS), MASKED_SRC,
                aliases={}, filter_file=None)
    print('wrote %d clips. Now re-run gen_scenes.py.' % len(wavs))


if __name__ == '__main__':
    main()
