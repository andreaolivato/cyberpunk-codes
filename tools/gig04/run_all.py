r"""Run every generator this gig has, in dependency order, and fail loudly.

    python tools\gig04\run_all.py

The generators read each other's names through `gig04_config`, and nothing
downstream notices when one of them stops running: `build-archive.ps1` packs
the JSON already on disk, so the last successful output of a broken generator
looks exactly like a current one (gotcha 73).

One command, every generator, non-zero on the first failure. Run it before any
build that touched a generator.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# Dependency order. The journal goes before the phase because the phase names
# its objectives.
ORDER = [
    # THE WORLD FIRST: the journal's pins and the phase read the community
    # and the room for positions and NodeRefs.
    'gen_room.py',
    # THE ROOM'S NAVIGATION MESH, built from the room's frame.
    'gen_navmesh.py',
    'gen_community.py',
    # The clue objects before the sector that places them.
    'gen_clues.py',
    'gen_sector.py',
    'gen_journal.py',
    'gen_localization.py',
    # THE LIPSYNC PICKS GO BEFORE THE SCENES, because gen_scenes reads the
    # file this writes and builds the lipmap out of it. Run the other way
    # round and her mouth is dead, and nothing errors.
    'gen_lipsync.py',
    # The scenes go BEFORE the phase, which names their entry and exit
    # sockets by hand.
    'gen_scenes.py',
    'gen_questphase.py',
    # The translation kit, from the strings and subtitles just written, so
    # a translator's files never drift from what the mod registers.
    '../make_translation_kit.py',
]
# NOT HERE: gen_voice.py. It runs Wwise and is run by hand when the lines or
# the takes change; the .wem it writes are committed.

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
