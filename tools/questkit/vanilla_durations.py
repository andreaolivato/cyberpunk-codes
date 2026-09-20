r"""The committed slot of every reused vanilla line: the SHORTEST dub.

    from questkit import vanilla_durations
    vanilla_durations.write(gen_scenes.ALL_BUILDERS, out_path, gen_scenes.estimate_ms)

WHY THE SHORTEST. A dialogue line's slot in a scene is one number for every
language, and the game stretches it to the take it plays but never shrinks
it (measured 2026-09-19: a reused line given a 1 s slot still finished
before the next line started, inside a section and across a section
boundary; a line given a slot longer than its Italian take left the
Italian player waiting). The game knows every language's length of its own
lines from the length table each voice pack carries (`lengthMapReport` in
`volanguagedatamap.json`). So a reused line is written at the shortest dub
and every language gets exactly its own take. Writing the longest instead,
which this module did on 2026-09-18, was what put pauses after every short
dub's line.

The stretch does not apply to a clip the mod ships: those are not in any
length table, and a shipped clip given a 0.5 s slot was talked over. So a
shipped clip's slot is written at its measured length, and a line that
ships one clip per dub (a vanilla take cut short, remade in each dub) is
written at the longest of them (`merge_locale_clips`).

WHERE THE LENGTHS COME FROM. tools\measure_packs.py reads every voice pack
on this machine and caches {hex: {'f': ms, 'm': ms}} per locale under
tools\_lang_cache\. The cache is not committed; the per-gig
vanilla_durations.json this writes is, so a clone builds without any pack.
When no cache exists the committed file is left as it is.
"""
import glob
import json
import os

from questkit.packs import CACHE



def merge_locale_clips(measured, audio_dir):
    """Raise each shipped clip's slot in `measured` (the English
    durations.json, by scene/key) to the longest clip any dubbed locale
    ships for it. The game does not stretch a slot for a shipped clip, so
    the slot has to cover the longest dub's cut or that dub is talked over;
    the shorter dubs wait for the difference on these lines, and the way to
    shrink that is a tighter cut in the long dub, not a shorter slot.

    The dubbed lengths are `durations_<locale>.json` beside durations.json,
    written by gen_voice's locale pass.
    """
    for path in sorted(glob.glob(os.path.join(audio_dir, 'durations_*.json'))):
        with open(path, encoding='utf-8') as fh:
            for key, ms in json.load(fh).items():
                measured[key] = max(measured.get(key, 0), ms)
    return measured


def caches():
    """{locale: {hex: {'f': ms, 'm': ms}}} for every measured locale."""
    out = {}
    for path in sorted(glob.glob(os.path.join(CACHE, 'durations_*.json'))):
        loc = os.path.basename(path)[len('durations_'):-len('.json')]
        with open(path, encoding='utf-8') as fh:
            out[loc] = json.load(fh)
    return out


def write(builders, out, estimate_ms=None):
    tables = caches()
    if not tables:
        print('no measured packs under %s; keeping %s as committed' % (CACHE, out))
        return
    wanted, text = {}, {}
    for build in builders:
        scene = build()
        for key, sid, t in scene.reused:
            wanted['%s/%s' % (scene.name, key)] = '%016x' % int(sid)
            text['%s/%s' % (scene.name, key)] = t
    result, shortest, missing = {}, {}, []
    en = tables.get('en-us', {})
    for sk, h in sorted(wanted.items()):
        best, where = 0, None
        for loc, table in tables.items():
            for g, ms in table.get(h, {}).items():
                if ms and (not best or ms < best):
                    best, where = ms, '%s/%s' % (loc, g)
        if best:
            result[sk] = best
            shortest[sk] = where
        else:
            missing.append(sk)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(result, fh, indent=1, sort_keys=True)
    print('wrote %s (%d line(s), shortest of %d locale(s): %s)'
          % (out, len(result), len(tables), ', '.join(sorted(tables))))
    for sk in result:
        h = wanted[sk]
        en_ms = max(en.get(h, {}).values() or [0])
        est = ('  (estimate %d)' % estimate_ms(text[sk])) if estimate_ms else ''
        print('   %-30s %5d ms  %-9s english %5d%s'
              % (sk, result[sk], shortest[sk], en_ms, est))
    if missing:
        print('no take found for: ' + ', '.join(missing))
