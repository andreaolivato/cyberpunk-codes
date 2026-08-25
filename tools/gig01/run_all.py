r"""Run every generator this gig has, in dependency order, and fail loudly.

===========================================================================
WHY

The generators import from each other. `gen_questphase` and `gen_poselab` both
import names out of `gen_community`, and `gen_scenes` imports the spawn-set name
from it too. Rename one constant and the others stop running, and NOTHING
DOWNSTREAM NOTICES, because `build-archive.ps1` packs the JSON that is already on
disk. The last successful output of a generator that has since broken looks
exactly like the current one.

That shipped a crash on 2026-08-25. `GUARD_ENTRY` was removed from
`gen_community`, `gen_questphase` had been importing it, and the gig's quest
phase went on carrying three references to a community entry that no longer
existed. The game loaded, merged everything without a single warning, and died.

One command, every generator, non-zero on the first failure. Run it before any
build that touched a generator.

    python tools\gig01\run_all.py

The staleness guard in `deploy-dev.ps1` catches the other half of this, raw
files newer than the packed archive, but it cannot know that a file which was
never REGENERATED should have been.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# Dependency order: the communities' names are imported by the phases and the
# scenes, so they go first. The rest are independent of each other.
ORDER = [
    'gen_community.py',
    # The estate detail. Before the phases, which import its community reference,
    # and it cross-checks its entry names against Gig01_Encounter.reds.
    'gen_estate_guards.py',
    'gen_compound_guards.py',
    'gen_journal.py',
    'gen_localization.py',
    'gen_sector.py',
    'gen_shard_ent.py',
    'gen_scenes.py',
    'gen_questphase.py',
    # Dev benches last, so a broken bench cannot hide a broken shipped file.
    'gen_poselab.py',
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
