r"""Run every generator this gig has, in dependency order, and fail loudly.

    python tools\gig02\run_all.py

===========================================================================
WHY

The generators import from each other. `gen_voice` and `gen_lipsync` both read
`gen_scenes.ALL_BUILDERS`, `gen_questphase` and `gen_journal` both read the
anchors out of `gig02_config`, and `gen_community` reads the hit area's hull out
of `hit_area`. Rename one constant and the others stop running, and NOTHING
DOWNSTREAM NOTICES, because `build-archive.ps1` packs the JSON that is already
on disk. The last successful output of a generator that has since broken looks
exactly like the current one.

That shipped a crash in gig 01 on 2026-08-25: a name was removed from one
generator, another went on referencing it, and the gig's quest phase carried
three references to a community entry that no longer existed. The game loaded,
merged everything without a warning, and died.

One command, every generator, non-zero on the first failure. Run it before any
build that touched a generator.

===========================================================================
WHAT IS NOT IN HERE, AND WHY

`gen_voice.py` is deliberately absent. It converts audio through Wwise, which
takes minutes, needs a tool the rest of the pipeline does not, and is only worth
running when the DIALOGUE has changed. Everything else here is seconds and
should be run every time.

When it IS run, the order is: gen_voice, then gen_lipsync, then this. Both write
sidecars that gen_scenes reads (durations.json for the pacing and
lipsync_picks.json for the mouths), so scenes generated before them hold
estimates rather than measurements.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# Dependency order. The scenes go before the phase because the phase names their
# entry and exit sockets, and the journal goes before the phase because the
# phase names its objectives and pins; neither is enforced by an import, so a
# rename in one is caught by reading the other's output rather than by this
# script. What this script does catch is a generator that stops running at all.
ORDER = [
    # The hit area's corners, which both the trigger area node below and the
    # script's leaving test come from. It writes Gig02_Area.reds, so it goes
    # first: a change to the walked corners has to reach the redscript in the
    # same run that it reaches the sector, or the drawn area and the test
    # disagree.
    'hit_area.py',
    'gen_journal.py',
    'gen_localization.py',
    'gen_sector.py',
    # The cast's community. gen_questphase imports its entry names, so this
    # runs BEFORE the phase that switches them on and off.
    'gen_community.py',
    'gen_scenes.py',
    'gen_questphase.py',
    # The translation kit, from the strings and subtitles just written, so
    # a translator's files never drift from what the gig registers.
    '../make_translation_kit.py',
]

if __name__ == '__main__':
    failed = []
    for name in ORDER:
        path = os.path.join(HERE, name)
        if not os.path.exists(path):
            print('  SKIP    %s (not present)' % name)
            continue
        result = subprocess.run([sys.executable, path], cwd=HERE,
                                capture_output=True, text=True)
        if result.returncode == 0:
            print('  ok      %s' % name)
        else:
            failed.append(name)
            print('  FAILED  %s' % name)
            tail = (result.stderr or result.stdout).strip().splitlines()
            for line in tail[-6:]:
                print('            ' + line)
    print()
    if failed:
        raise SystemExit('%d generator(s) failed: %s\n'
                         'The packed archive still holds their LAST GOOD output, '
                         'which is what makes this silent.'
                         % (len(failed), ', '.join(failed)))
    print('every generator ran')
