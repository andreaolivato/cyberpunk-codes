r"""Return Ticket's three scanner clues at the Tyger Claws' van: the blood by
its back doors, the handcuffs, and Bayani's bag.

    python tools\gig04\gen_clues.py              (ordinary run, no game needed)
    python tools\gig04\gen_clues.py --refresh    (re-lift the vanilla clues)

Writes, under source\wkit\raw:

  mod\return_ticket\entity\cc_g04_clue_blood.ent
  mod\return_ticket\entity\cc_g04_clue_cuffs.ent
  mod\return_ticket\entity\cc_g04_clue_bag.ent

THE GAME'S OWN CLUE, COPIED. The NCPD activity `ma_bls_ina_se1_07` (a blood
trail and a case in the Badlands) has two scanner clues, and this file lifts
both entity files whole: `ma_bls_ina_se1_07_trail.ent`, a blood decal, and
`ma_bls_ina_07_case.ent`, a mesh. Each is a `gameObject` with a scanning
component whose `FocusClueDefinition` names a TweakDB clue record (the text
the scanner shows) and a fact it sets once the scan completes. Only four
things change here: the decal or the mesh, the name on the scanner, the clue
record and the fact. The records are source/tweaks/clues.yaml.

THE FACTS ARE THE SIGNAL. `cc_g04_clue_<name>` goes to 1 when V finishes
scanning that clue, which is how the vanilla activity hears it too
(`ma_bls_ina_se1_07_blood_found`, read by a fact pause). The quest phase
counts the three on its objective's counter.

THE LIFT IS COMMITTED (`clue_ents.json`), as gig 01's shard container is: an
ordinary run reads it and needs neither the game nor WolvenKit. `--refresh`
writes it again from the shipped files. The vanilla files carry their
components twice, in `components` by handle reference and in `compiledData`
with the handles defined; the lift keeps the second, inline, the shape
WolvenKit writes back (tools/gig01/gen_shard_ent.py has the rules).
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from questkit import cr2w                                            # noqa: E402
from questkit.community import fnv1a64                              # noqa: E402

import gig04_config as cfg                                           # noqa: E402

B = chr(92)
HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, 'clue_ents.json')
OUT = os.path.join(cfg.RAW, 'mod', 'return_ticket', 'entity')

CLI = os.path.expandvars(r'%LOCALAPPDATA%\Programs\WolvenKit.CLI\WolvenKit.CLI.exe')
CONTENT = r'C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077\archive\pc\content'
VANILLA = {
    'decal': 'ma_bls_ina_se1_07_trail.ent',
    'mesh': 'ma_bls_ina_07_case.ent',
}

# THE CLUES: (name, template, the mesh or None, its look, the clue record).
# The record's text is source/tweaks/clues.yaml; the name on the scanner is
# the record's name. The handcuffs are the game's open pair: it has no zip
# ties.
CUFFS_MESH = B.join(['base', 'environment', 'decoration', 'misc', 'weapons',
                     'handcuffs', 'handcuffs_a.mesh'])
BAG_MESH = B.join(['base', 'items', 'interactive', 'accessories',
                   'int_accessories_001__duffel_bag',
                   'int_accessories_001__duffel_bag.mesh'])
CLUES = [
    ('blood', 'decal', None, None),
    ('cuffs', 'mesh', CUFFS_MESH, 'default'),
    ('bag', 'mesh', BAG_MESH, 'default'),
]


def depot(name):
    return B.join(['mod', 'return_ticket', 'entity', 'cc_g04_clue_%s.ent' % name])


def fact(name):
    return 'cc_g04_clue_' + name


def record(name):
    return 'scanning.cc_g04_clue_' + name


def refresh():
    stage = os.path.join(os.path.dirname(HERE), '_ent_cache', 'gig04_clues')
    os.makedirs(stage, exist_ok=True)
    out = {}
    for kind, ent in VANILLA.items():
        found = [os.path.join(d, f) for d, _s, fs in os.walk(stage) for f in fs if f == ent]
        if not found:
            subprocess.run([CLI, 'unbundle', CONTENT, '-o', stage, '-w', '*' + ent,
                            '-v', 'Quiet'], check=True)
            found = [os.path.join(d, f) for d, _s, fs in os.walk(stage) for f in fs if f == ent]
        if not found:
            raise SystemExit('could not extract %s' % ent)
        subprocess.run([CLI, 'convert', 'serialize', found[0], '-v', 'Quiet'], check=True)
        with open(found[0] + '.json', encoding='utf-8-sig') as fh:
            rc = json.load(fh)['Data']['RootChunk']
        chunks = rc['compiledData']['Data']['Chunks']
        out[kind] = {'source': ent, 'entity': chunks[0], 'components': chunks[1:]}
    with open(SOURCE, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(out, fh, indent=1)
    print('wrote', SOURCE)


def cname(v):
    return {'$type': 'CName', '$storage': 'string', '$value': v}


def resref(path, flags):
    return {'DepotPath': {'$type': 'ResourcePath', '$storage': 'string',
                          '$value': path}, 'Flags': flags}


def build(name, kind, mesh, look, lift):
    t = json.loads(json.dumps(lift[kind]))
    deps = []
    for c in t['components']:
        if c['$type'] == 'gameScanningComponent':
            # ONE CLUE, ITS OWN GROUP, AND ONE EMPTY STEP. The vanilla trail
            # has a step record beside its conclusion; given the same record,
            # the scanner listed the clue twice (playtest 2026-10-14). With no
            # step at all the facts never fire: GameObject
            # .ResolveFocusClueConclusion sets them only when the conclusion's
            # timePct is at least the scan progress, and scanningComponent
            # gives the conclusion 1.0 with a step and 0.0 without one
            # (playtest 2026-10-14, the counter stayed at 0/3). A step with no
            # record keeps the 1.0 and lists nothing, since the tooltip skips
            # an invalid record.
            clue = c['clues'][0]
            clue['clueGroupID'] = cname(fact(name))
            clue['clueRecord']['$value'] = record(name)
            clue['extendedClueRecords'] = [{
                '$type': 'ClueRecordData',
                'clueRecord': {'$type': 'TweakDBID', '$storage': 'uint64',
                               '$value': '0'},
                'facts': [], 'percentage': 0.0, 'wasInspected': 0}]
            clue['facts'] = [{'$type': 'SFactOperationData',
                              'factName': cname(fact(name)),
                              'factValue': 1, 'operationType': 'Set'}]
        if c['$type'] == 'entMeshComponent' and mesh:
            c['mesh'] = resref(mesh, 'Default')
            c['meshAppearance'] = cname(look)
            deps.append(resref(mesh, 'Soft'))
        if c['$type'] == 'entDecalComponent':
            deps.append(resref(c['material']['DepotPath']['$value'], 'Soft'))
    # THE TITLE ON THE SCAN, which a bare key does not reach (playtest
    # 2026-10-14: "CC-G04-CLUE-BAG-NAME"): LocKey# and the FNV1a64 of the
    # bare key, the hash ArchiveXL files our text under, as characters.yaml
    # writes the people's names.
    t['entity']['displayName'] = {'unk1': '0', 'value': 'LocKey#%d' % fnv1a64(
        cfg.LOCKEY_PREFIX + 'clue-%s-name' % name)}
    return {
        'Header': cr2w.header('cc_g04_clue_%s.ent' % name),
        'Data': {
            'Version': 195, 'BuildVersion': 0,
            'RootChunk': {
                '$type': 'entEntityTemplate',
                'appearances': [],
                'backendDataOverrides': [],
                'bindingOverrides': [],
                'compiledEntityLODFlags': 0,
                'componentResolveSettings': [],
                'components': t['components'],
                'cookingPlatform': 'PLATFORM_PC',
                'defaultAppearance': cname('default'),
                'entity': {'HandleId': '900', 'Data': t['entity']},
                'includeInstanceBuffer': None,
                'includes': [],
                'inplaceResources': [],
                'localData': None,
                'resolvedDependencies': deps,
                'visualTagsSchema': None,
            },
            'EmbeddedFiles': [],
        },
    }


if __name__ == '__main__':
    if '--refresh' in sys.argv:
        refresh()
        raise SystemExit(0)
    with open(SOURCE, encoding='utf-8') as fh:
        lift = json.load(fh)
    os.makedirs(OUT, exist_ok=True)
    for name, kind, mesh, look in CLUES:
        path = os.path.join(OUT, 'cc_g04_clue_%s.ent.json' % name)
        with open(path, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(build(name, kind, mesh, look, lift), fh, indent=2)
        print('wrote', path, '(from %s)' % lift[kind]['source'])
