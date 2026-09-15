r"""Voice pipeline for Acceptable Loss: WAV -> phone treatment -> WEM ->
voiceover map, plus the duration sidecar.

    python tools\gig03\gen_voice.py

The pipeline itself is tools/questkit/voice.py and the treatment is
tools/questkit/phone.py; gig 02's copy of this file carries the full account
of how a scene line finds its audio. What is here is THE GIG: which lines ship
a clip of ours, and take_vanilla.py is the one list of them.

NEARLY NOTHING IN THIS GIG SHIPS AUDIO OF OURS. Dino, V and Johnny speak in
the game's own recordings, pointed at by `vanilla_sid` in gen_scenes, and
those keys are deliberately absent here. The exceptions are take_vanilla.py's
cuts: a take cut at a pause so the wanted words come free, shipped dry under
this gig's own line id. A line on the call would get the holocall treatment
here (the route Regina's joined job line took until 2026-09-15); none of the
cuts is on the call today, so each is reported as shipped dry, which is
right.

Run this only when those lines change. The WAVs and the .wem are both
committed, so a clone builds the mod without Wwise or the game installed.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gen_scenes as gs                                             # noqa: E402
import take_vanilla                                                 # noqa: E402
from questkit.voice import (                                        # noqa: E402
    configure, stem, line_texts, holocall_lines, wav_ms, convert, write_vomap,
)
from questkit import phone                                          # noqa: E402
from gig03_config import SOURCE, RAW_MOD, DEPOT                     # noqa: E402

AUDIO_SRC = os.path.join(SOURCE, 'audio')
# The phone-filtered copies. Derived from the master beside them, so gitignored.
HOLOCALL_SRC = os.path.join(AUDIO_SRC, 'holocall')
DURATIONS = os.path.join(AUDIO_SRC, 'durations.json')
WEM_OUT = os.path.join(RAW_MOD, 'audio', 'vo')
VOMAP_OUT = os.path.join(RAW_MOD, 'localization', 'vomap.json.json')
DEPOT_VO = DEPOT + chr(92) + 'audio' + chr(92) + 'vo'

# ONE SOURCE OF TRUTH for which lines ship: take_vanilla.shipped(), which is
# its whole takes and its joins together.
VOICED = {}
for _scene, _key in take_vanilla.shipped():
    VOICED.setdefault(_scene, []).append(_key)

configure(wem_out=WEM_OUT, vomap_out=VOMAP_OUT, depot_vo=DEPOT_VO,
          audio_src=AUDIO_SRC)


def main():
    texts = line_texts(gs.ALL_BUILDERS)
    holocall = holocall_lines(gs.ALL_BUILDERS)
    os.makedirs(WEM_OUT, exist_ok=True)
    os.makedirs(HOLOCALL_SRC, exist_ok=True)

    wavs, durations, vomap = [], {}, []
    for scene, keys in sorted(VOICED.items()):
        for key in keys:
            if (scene, key) not in texts:
                raise SystemExit('%s/%s is in take_vanilla.TAKES but is not a '
                                 'line in that scene, or it still carries a '
                                 'vanilla_sid' % (scene, key))
            name = stem(scene, key)
            wav = os.path.join(AUDIO_SRC, name + '.wav')
            if not os.path.exists(wav):
                raise SystemExit('%s is missing; run tools\\gig03\\'
                                 'take_vanilla.py first' % wav)
            # THROUGH THE PHONE, into a COPY, so the master stays the game's
            # own dry take. Every line here is a holocall line by construction;
            # the check is kept so a line moved out of the call is not filtered
            # by habit.
            if (scene, key) in holocall:
                filtered = os.path.join(HOLOCALL_SRC, name + '.wav')
                phone.filter_file(wav, filtered)
                wav = filtered
            else:
                print('  ! %s is not a holocall line; shipping it dry' % name)
            wavs.append((wav, name + '.wem'))
            durations['%s/%s' % (scene, key)] = wav_ms(wav)
            # The speaker is one voice whatever body V has, so both columns
            # carry the same clip.
            vomap.append((gs.locstring_ruid(scene, key), name + '.wem',
                          name + '.wem'))

    convert(wavs)
    write_vomap(vomap)
    with open(DURATIONS, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(durations, fh, indent=1, sort_keys=True)
    print('wrote %s (%d line(s))' % (DURATIONS, len(durations)))


if __name__ == '__main__':
    main()
