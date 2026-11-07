r"""Run every generator this gig has, in dependency order, and fail loudly.

    python tools\gig05\run_all.py

Gig 04's runner (tools/gig04/run_all.py), with this gig's list:
`build-archive.ps1` packs the JSON already on disk, so a generator that
stopped running looks exactly like a current one (gotcha 73).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

ORDER = [
    # THE WORLD FIRST: the journal's pins and the phase read the community's
    # markers and flight paths.
    'gen_recruiter.py',
    'gen_vest.py',
    'gen_outfit.py',
    'gen_community.py',
    'gen_journal.py',
    'gen_localization.py',
    # The scenes go BEFORE the phase, which names their entry and exit
    # sockets by hand.
    'gen_scenes.py',
    'gen_lipsync.py',
    'gen_scenes.py',
    'gen_questphase.py',
]

# NOT HERE: gen_voice.py. It runs Wwise and is run by hand when a take changes.

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
