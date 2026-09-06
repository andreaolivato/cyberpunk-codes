r"""Every LocKey the gig references, against every LocKey it ships.

    python tools\check_strings.py --gig 02

BOTH DIRECTIONS ARE SILENT IN GAME. A key that is referenced and not shipped
draws as a raw string in the quest log, which is the single most common way a
mod-added gig looks broken; a key that is shipped and not referenced is dead
weight that reads as if something still uses it.

Three referencing sides, and they do not spell a key the same way:

  * the journal resource, bare keys, because ArchiveXL hashes them
  * the redscript, through `GetLocalizedTextByKey(n"...")`
  * the TweakXL yaml, where an Item's `displayName` takes a BARE key and a
    Character's takes `LocKey#<FNV1a64>` of the same string. That difference is
    real and neither side is wrong; this resolves the hash back.

Run it after adding a string, an objective, a pin or a record. It costs a
second, and the thing it catches costs a launch.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from questkit import gigs                                            # noqa: E402
from questkit.scene import fnv1a64                                   # noqa: E402

GIG = gigs.from_argv('02')
cfg = gigs.config(GIG)
PREFIX = cfg.LOCKEY_PREFIX
RAW = cfg.RAW_MOD
STEM = 'gig' + GIG

doc = json.load(open(os.path.join(RAW, 'localization', 'en-us.json.json'),
                     encoding='utf-8'))
shipped = set(e['secondaryKey'] for e in
              doc['Data']['RootChunk']['root']['Data']['entries'])
by_hash = {str(fnv1a64(k)): k for k in shipped}
print('shipped: %d strings' % len(shipped))

used = {}


def note(key, where):
    used.setdefault(key, set()).add(where)


journal = open(os.path.join(RAW, 'journal', STEM + '.journal.json'),
               encoding='utf-8').read()
for m in re.finditer(r'"value": "(' + PREFIX + r'[a-z0-9-]+)"', journal):
    note(m.group(1), 'journal')

for f in sorted(os.listdir(os.path.join(cfg.SOURCE, 'scripts'))):
    if not f.endswith('.reds'):
        continue
    body = open(os.path.join(cfg.SOURCE, 'scripts', f), encoding='utf-8').read()
    for m in re.finditer(r'GetLocalizedTextByKey\(n"(' + PREFIX + r'[a-z0-9-]+)"\)',
                         body):
        note(m.group(1), f)

for f in sorted(os.listdir(os.path.join(cfg.SOURCE, 'tweaks'))):
    if not f.endswith('.yaml'):
        continue
    body = open(os.path.join(cfg.SOURCE, 'tweaks', f), encoding='utf-8').read()
    for m in re.finditer(r':\s*(' + PREFIX + r'[a-z0-9-]+)\s*$', body, re.M):
        note(m.group(1), f)
    for m in re.finditer(r'LocKey#(\d+)', body):
        h = m.group(1)
        if h in by_hash:
            note(by_hash[h], f)
        else:
            note('LocKey#' + h + ' (unknown hash)', f)

missing = sorted(k for k in used if k not in shipped)
unused = sorted(shipped - set(used))

print('referenced: %d keys' % len(used))
for k in missing:
    print('  MISSING  %-34s referenced by %s' % (k, ', '.join(sorted(used[k]))))
for k in unused:
    print('  unused   %s' % k)
print()
print('%d missing, %d unused' % (len(missing), len(unused)))
raise SystemExit(1 if missing else 0)
