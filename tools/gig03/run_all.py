r"""Run every generator this gig has, in dependency order, and fail loudly.

    python tools\gig03\run_all.py

The generators read each other's names through `gig03_config`, and nothing
downstream notices when one of them stops running: `build-archive.ps1` packs the
JSON already on disk, so the last successful output of a broken generator looks
exactly like a current one. That shipped a crash in gig 01 on 2026-08-25.

One command, every generator, non-zero on the first failure. Run it before any
build that touched a generator.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# Dependency order. The journal goes before the phase because the phase names
# its objectives; neither is enforced by an import, so a rename in one is caught
# by reading the other's output rather than by this script. What this script
# does catch is a generator that stops running at all.
ORDER = [
    'gen_journal.py',
    'gen_localization.py',
    # The shard's world object. It lifts the vanilla container out of gig 01's
    # committed copy, so it needs neither the game nor WolvenKit on an ordinary
    # run.
    'gen_sector.py',
    # REGINA HERSELF, in the world rather than spawned by her scene. It has to
    # run before the scene and the phase, both of which name its community.
    'gen_community.py',
    # THE LENGTH OF EVERY REUSED LINE, off the game's own takes, so the
    # scenes are paced by real audio and not by an estimate. Keeps the
    # committed file when the game is not installed.
    'measure_vanilla.py',
    # THE LIPSYNC PICKS GO BEFORE THE SCENES, because gen_scenes reads the file
    # this writes and builds the lipmap out of it. Run the other way round and
    # every mouth in the gig is dead, and nothing errors.
    'gen_lipsync.py',
    # The scenes go BEFORE the phase, because the phase names their entry and
    # exit sockets by hand. Nothing enforces that with an import, so a renamed
    # socket is caught by reading the other file's output rather than by this
    # script; what this catches is a generator that stops running at all.
    'gen_scenes.py',
    'gen_questphase.py',
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
            for line in (result.stderr or result.stdout).strip().splitlines()[-6:]:
                print('            ' + line)
    print()
    if failed:
        raise SystemExit('%d generator(s) failed: %s\n'
                         'The packed archive still holds their LAST GOOD output, '
                         'which is what makes this silent.'
                         % (len(failed), ', '.join(failed)))
    print('every generator ran')
