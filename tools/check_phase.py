r"""Cross-check the quest phase against the scenes it enters.

    python tools\check_phase.py --gig 02

THREE THINGS THAT ARE SILENT IN GAME AND OBVIOUS HERE:

  * A SCENE SOCKET NAME THAT DOES NOT EXIST. A quest scene node's input sockets
    are the scene's entryPoints and its outputs are its exitPoints, BY NAME. Get
    one wrong and the graph simply never continues past that beat: no error, no
    log line, and an objective on screen forever.
  * A SCENE FILE THE PHASE NEVER ENTERS, which is a beat that was written and
    then orphaned, and which ships in the archive doing nothing.
  * TWO NODES POINTING AT ONE SCENE. Gig 01 did that once and the game died on
    load; a scene node also cannot be entered from two places, so the shape is
    doubly wrong. Worth catching mechanically because it looks perfectly
    reasonable in the generator.

Paths are built from chr(92) rather than a typed backslash, because a depot path
written into a generated edit gets eaten (gotcha 28). The chunk format emits
each object once and refers to it by HandleRefId afterwards, so this resolves
the handle map first.

NOT IN run_all.py, on purpose: run_all's job is that every generator still RUNS,
and this asks whether what they wrote agrees. Run it after any change to a
scene's entry or exit names, or to the phase's flow.

It serves any gig: `--gig` picks the paths out of that gig's config module
(questkit.gigs). It lived under tools/gig02/ until 2026-09-06, when the three
gig-02 checkers moved up together.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from questkit import gigs                                            # noqa: E402

B = chr(92)
GIG = gigs.from_argv('02')
cfg = gigs.config(GIG)
RAW = cfg.RAW_MOD
STEM = 'gig' + GIG

have = {}
for f in sorted(os.listdir(os.path.join(RAW, 'scenes'))):
    if not f.endswith('.scene.json'):
        continue
    rc = json.load(open(os.path.join(RAW, 'scenes', f),
                        encoding='utf-8'))['Data']['RootChunk']
    have[f[:-len('.scene.json')]] = (
        set(e['name']['$value'] for e in rc['entryPoints']),
        set(e['name']['$value'] for e in rc['exitPoints']),
    )

doc = json.load(open(os.path.join(RAW, 'quest', STEM + '.questphase.json'),
                     encoding='utf-8'))

handles = {}
nodes = []


def walk(o):
    if isinstance(o, dict):
        if 'HandleId' in o and 'Data' in o:
            handles[o['HandleId']] = o['Data']
        if o.get('$type') == 'questSceneNodeDefinition':
            nodes.append(o)
        for v in o.values():
            walk(v)
    elif isinstance(o, list):
        for v in o:
            walk(v)


walk(doc)


def resolve(sock):
    if 'Data' in sock:
        return sock['Data']
    return handles.get(sock.get('HandleRefId'))


FIXED_IN = {'CutDestination', 'Prefetch'}
FIXED_OUT = {'Default INT', 'Default RET'}
bad = 0
seen = set()
for node in nodes:
    name = node['sceneFile']['DepotPath']['$value'].split(B)[-1]
    if name.endswith('.scene'):
        name = name[:-len('.scene')]
    seen.add(name)
    if name not in have:
        print('  MISSING SCENE FILE  %s' % name)
        bad += 1
        continue
    entries, exits = have[name]
    got_in, got_out = set(), set()
    for s in node.get('sockets', []):
        d = resolve(s)
        if not d:
            continue
        nm = d['name']['$value']
        if d['type'] == 'Input' and nm not in FIXED_IN:
            got_in.add(nm)
        if d['type'] == 'Output' and nm not in FIXED_OUT:
            got_out.add(nm)
    if got_in - entries or got_out - exits:
        print('  SOCKET MISMATCH  %s: phase in=%s out=%s / scene in=%s out=%s'
              % (name, sorted(got_in), sorted(got_out),
                 sorted(entries), sorted(exits)))
        bad += 1
    else:
        print('  ok  %-20s %s -> %s' % (name, sorted(got_in), sorted(got_out)))

print()
print('%d scene node(s), %d scene file(s), %d problem(s)'
      % (len(nodes), len(have), bad))
unused = sorted(set(have) - seen)
if unused:
    print('scenes the phase never enters: %s' % ', '.join(unused))
    bad += 1
dupes = [n for n in seen if sum(
    1 for x in nodes
    if x['sceneFile']['DepotPath']['$value'].split(B)[-1][:-len('.scene')] == n) > 1]
if dupes:
    print('SCENES WITH MORE THAN ONE NODE (this crashes on load): %s'
          % ', '.join(sorted(set(dupes))))
    bad += 1
raise SystemExit(1 if bad else 0)
