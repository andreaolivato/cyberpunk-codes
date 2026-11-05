r"""Trauma Team: the recruiter's body. An entity and an appearance file made
from the game's own nurse, in the game's own Trauma Team suit.

    python tools\gig05\gen_recruiter.py

Writes, under source\wkit\raw:

  mod\trauma_team\npv\recruiter.ent.json
  mod\trauma_team\npv\recruiter.app.json

THE DESIGN CALL, 2026-11-04: she wears the green suit V is given, helmet off.
No Trauma Team NPC in the game is a woman, but the suit has a woman's cut,
used by nobody: `corp_trauma\unique_trauma` holds the jacket, the pants with
their logo and the chest defibrillator as `_wa_` meshes, on the same rig as a
crowd woman's body. So the nurse keeps her head, hair and body, and her
tunic, skirt, clogs and bracer are replaced. `fixer01/gen_npv.py` is the same
job done on a seed from outside the game; its header has what the converter
requires, and `_keep_handles` here is its `inline_missing_handles`.

THE PROXY IS NURSE 07'S, in dark scrubs and bareheaded. An appearance's proxy is
a low-detail copy of the whole figure drawn at a distance, and a soldier's, the
first tried, gave her a helmet from across the street (playtest 2026-11-04).
Playtest 2026-11-04: with the proxy and the visual controller taken out, she
stood there, could be scanned and spoken to, and nothing was drawn. The
controller stays, its list rewritten to the meshes she wears.

THE VANILLA FILES ARE READ FROM `tools\_ent_cache`, serialised on first use.
"""
import json
import math
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gig05_config as cfg  # noqa: E402

CLI = os.path.expandvars(r'%LOCALAPPDATA%\Programs\WolvenKit.CLI\WolvenKit.CLI.exe')
GAME = os.path.join(r'C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077',
                    'archive', 'pc', 'content', 'basegame_4_appearance.archive')
B = chr(92)
CACHE = os.path.join(cfg.REPO, 'tools', '_ent_cache')
OUT = os.path.join(cfg.RAW_MOD, 'npv')

SOURCE_APPEARANCE = 'nurse_wa_06'
APPEARANCE = 'cc_g05_recruiter'
APP_DEPOT = cfg.DEPOT + B + 'npv' + B + 'recruiter.app'
ENT_DEPOT = cfg.DEPOT + B + 'npv' + B + 'recruiter.ent'
AV_APP_DEPOT = cfg.DEPOT + B + 'npv' + B + 'av.app'
VANILLA_APP = B.join(['base', 'characters', 'appearances', 'service', 'service__medical_wa.app'])
VANILLA_ENT = B.join(['base', 'characters', 'entities', 'service', 'service__medical_wa.ent'])


def depot(*parts):
    return B.join(parts)


TRAUMA = depot('base', 'characters', 'garment', 'corp_trauma', 'unique_trauma')
BOOTS = depot('base', 'characters', 'garment', 'corp_ncpd', 'feet', 's1_022_boot__tactical',
              's1_022_wa_boot__tactical.mesh')
GONE = ('s1_023_wa_shoe__kroks7246', 'i1_045_wa_wrist__bracer3258')
PROXY = depot('base', 'characters', 'appearances', 'service', 'proxy',
              'service__medical_wa_nurse_wa_07', 'service__medical_wa_nurse_wa_07.mesh')
# Component to replace: (new name, mesh, mesh appearance).
SWAP = {
    # V'S CUT OF THE PANTS. Playtest 2026-11-04: the `_wa_` cut, which no NPC
    # wears, draws at a distance and breaks up at arm's length.
    'l1_084_wa_skirt__misty3853': ('l1_077_pwa_pants__trauma_small', depot(
        'base', 'characters', 'garment', 'player_equipment', 'legs',
        'l1_077_pants__trauma_small', 'l1_077_pwa_pants__trauma_small.mesh'), 'default'),
    't2_060_jacket__nurse': ('t2_106_wa_jacket__trauma_small', depot(
        TRAUMA, 'torso', 't2_106_jacket__trauma', 't2_106_wa_jacket__trauma_small.mesh'), 'default'),
}
# New components: (name, copy of, mesh, mesh appearance).
ADD = [
    ('t2_106_wa_jacket__trauma_small_dec_logo', 't2_060_jacket__nurse', depot(
        TRAUMA, 'torso', 't2_106_jacket__trauma', 't2_106_wa_jacket__trauma_small_dec_logo.mesh'),
     'default'),
    ('i1_056_wa_slot__chest_defib', 't2_060_jacket__nurse', depot(
        TRAUMA, 'item', 'i1_056_slot__chest_defib', 'i1_056_wa_slot__chest_defib.mesh'), 'default'),
    ('s1_022_wa_boot__tactical', 's1_023_wa_shoe__kroks7246', BOOTS, 'default'),
]


def vanilla(path):
    """The vanilla file as JSON, from the cache."""
    out = os.path.join(CACHE, path.replace(B, os.sep)) + '.json'
    if not os.path.exists(out):
        os.makedirs(CACHE, exist_ok=True)
        subprocess.run([CLI, 'unbundle', GAME, '-o', CACHE, '-r',
                        path.split(B)[-1].replace('.', B + '.') + '$'],
                       capture_output=True, check=True)
        subprocess.run([CLI, 'convert', 'serialize', out[:-5], '-v', 'Quiet'],
                       capture_output=True, check=True)
    with open(out, encoding='utf-8-sig') as fh:
        return json.load(fh)


def strpath(v):
    return {'$type': 'ResourcePath', '$storage': 'string', '$value': v}


def cname(v):
    return {'$type': 'CName', '$storage': 'string', '$value': v}


def _collect(obj, out):
    if isinstance(obj, dict):
        if 'HandleId' in obj and 'Data' in obj:
            out[str(obj['HandleId'])] = obj['Data']
        for v in obj.values():
            _collect(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _collect(v, out)


def _keep_handles(obj, defs, seen):
    if isinstance(obj, dict):
        if 'HandleId' in obj:
            seen.add(str(obj['HandleId']))
        if 'HandleRefId' in obj and str(obj['HandleRefId']) not in seen:
            hid = str(obj['HandleRefId'])
            seen.add(hid)
            obj.clear()
            obj['HandleId'] = hid
            obj['Data'] = json.loads(json.dumps(defs[hid]))
            _keep_handles(obj['Data'], defs, seen)
            return
        for v in obj.values():
            _keep_handles(v, defs, seen)
    elif isinstance(obj, list):
        for v in obj:
            _keep_handles(v, defs, seen)


def _reuse(comp, name, mesh, look):
    comp['name'] = cname(name)
    comp['mesh']['DepotPath'] = strpath(mesh)
    comp['meshAppearance'] = cname(look)
    return comp


# THE BODY'S CHUNK MASK IS NURSE 05'S, who wears trousers. Nurse 06 wears a
# skirt, so hers draws the legs, and they hid the suit's pants under the skin:
# bare legs with a band of pants at the knees (playtest 2026-11-04).
BODY_MASK = '18446741357964172995'


def build_app():
    doc = vanilla(VANILLA_APP)
    rc = doc['Data']['RootChunk']
    defs = {}
    _collect(doc, defs)
    seed = next(a.get('Data', a) for a in rc['appearances']
                if a.get('Data', a)['name']['$value'] == SOURCE_APPEARANCE)
    comps = [c.get('Data', c) for c in seed['components']]
    by_name = {c['name']['$value']: c for c in comps}
    out = []
    for c in comps:
        name = c['name']['$value']
        if name in GONE:
            continue
        if name.startswith('t0_000_wa__c_base'):
            c['chunkMask'] = BODY_MASK
        out.append(_reuse(json.loads(json.dumps(c)), *SWAP[name]) if name in SWAP else c)
    for i, (name, copy_of, mesh, look) in enumerate(ADD):
        comp = _reuse(json.loads(json.dumps(by_name[copy_of])), name, mesh, look)
        comp['id'] = str(int(comp['id']) + 1 + i)
        out.append(comp)
    # NO GARMENT SUPPORT ON THE PANTS: they fold to nothing at arm's length,
    # where the game runs it and the meshes for her body are not the suit's.
    for c in out:
        if c['name']['$value'] == PANTS:
            c['$type'] = 'entSkinnedMeshComponent'
    inline = not isinstance(seed['components'][0].get('Data'), dict)
    seed['components'] = out if inline else [{'HandleId': str(5000 + i), 'Data': c}
                                             for i, c in enumerate(out)]
    seed['name'] = cname(APPEARANCE)
    seed['proxyMesh']['DepotPath'] = strpath(PROXY)
    for c in out:
        if c['name']['$value'] == 'AppearanceProxyMesh':
            c['mesh']['DepotPath'] = strpath(PROXY)
        if c['$type'] == 'entVisualControllerComponent':
            c['appearanceDependency'] = [{
                '$type': 'entVisualControllerDependency',
                'appearanceName': json.loads(json.dumps(m['meshAppearance'])),
                'componentName': json.loads(json.dumps(m['name'])),
                'mesh': json.loads(json.dumps(m['mesh'])),
            } for m in out if isinstance(m.get('mesh'), dict)
                and m['name']['$value'] != 'AppearanceProxyMesh']
    seen, deps = set(), []
    for c in out:
        m = c['mesh']['DepotPath'].get('$value') if isinstance(c.get('mesh'), dict) else None
        if isinstance(m, str) and m and m not in seen:
            seen.add(m)
            deps.append({'DepotPath': strpath(m), 'Flags': 'Soft'})
    seed['resolvedDependencies'] = deps
    seed.pop('compiledData', None)
    rc['appearances'] = [{'HandleId': '1', 'Data': seed}]
    done = set()
    for k, v in rc.items():
        if k != 'appearances':
            _keep_handles(v, defs, done)
    _keep_handles(rc['appearances'], defs, done)
    doc['Header']['ArchiveFileName'] = 'recruiter.app'
    return doc


def build_ent():
    doc = vanilla(VANILLA_ENT)
    rc = doc['Data']['RootChunk']
    rc['appearances'] = [{
        '$type': 'entTemplateAppearance',
        'appearanceName': cname(APPEARANCE),
        'appearanceResource': {'DepotPath': strpath(APP_DEPOT), 'Flags': 'Soft'},
        'name': cname(APPEARANCE),
    }]
    rc['defaultAppearance'] = cname(APPEARANCE)
    text = json.dumps(doc).replace(VANILLA_APP.replace(B, B * 2), APP_DEPOT.replace(B, B * 2))
    doc = json.loads(text)
    doc['Header']['ArchiveFileName'] = 'recruiter.ent'
    return doc


# THE CREW'S OWN ENTITY: the game's Trauma Team man with the combat lines off.
# Playtest 2026-11-04: in a fight they shouted a street ganger's lines ("I will
# find you"). Those come from the voice set the entity names. Its grunts stay,
# and what the crew say in the scenes is the scenes' own.
VANILLA_CREW = B.join(['base', 'characters', 'entities', 'corpo', 'corpo__traumateam_ma.ent'])


def _silence(obj):
    if isinstance(obj, dict):
        kind = obj.get('$type')
        if kind == 'scnVoicesetComponent':
            obj['combatVoSettingsName'] = cname('None')
        if kind == 'scnVoicesetComponentPS':
            obj['areVoicesetLinesEnabled'] = 0
        for v in obj.values():
            _silence(v)
    elif isinstance(obj, list):
        for v in obj:
            _silence(v)


def build_crew():
    doc = vanilla(VANILLA_CREW)
    _silence(doc['Data']['RootChunk'])
    doc['Header']['ArchiveFileName'] = 'crew.ent'
    return doc


# THE RAILS OVER THE CABIN, for the hands. V's holding-on pose grips a bar this
# Atlus does not have (playtest 2026-11-04: a fist round nothing). A handrail
# off the game's cinema, as a mesh of the AV's own, along the cabin.
VANILLA_AV = B.join(['base', 'quest', 'main_quests', 'prologue', 'q001', 'entities',
                     'av_trauma.ent'])
RAIL = B.join(['base', 'environment', 'architecture', 'common', 'int', 'int_shuttle_a',
               'int_shuttle_a_addon_handle_l100_a.mesh'])
VANILLA_AV_APP = B.join(['base', 'vehicles', 'appearances', 'special', 'zetatech_atlus.app'])
AV_LOOK = 'trama_team'
PANTS = 'l1_077_pwa_pants__trauma_small'
RAILS = [('cc_g05_rail_a', cfg.RAIL_A)]


def _rail(name, spot, i):
    x, y, z = spot
    # The mesh's z along the cabin, its y from the mounts down to the bar, leaning
    # RAIL_LEAN degrees towards the cabin. The quaternion of that turn.
    lean = math.radians(cfg.RAIL_LEAN)
    s, c = math.sin(lean), math.cos(lean)
    r = math.sqrt(1.0 + c) / 2.0
    pos = {'$type': 'WorldPosition'}
    for k, v in zip('xyz', (x, y, z)):
        pos[k] = {'$type': 'FixedPoint', 'Bits': int(round(v * 131072))}
    return {
        '$type': 'entMeshComponent', 'autoHideDistance': 0, 'castLocalShadows': 'Always',
        'castRayTracedGlobalShadows': 'Always', 'castRayTracedLocalShadows': 'Default',
        'castShadows': 'Always', 'chunkMask': '9223372036854775807',
        'forcedLodDistance': 'Default', 'forceLODLevel': -1,
        'id': str(9100000000000000 + i), 'isEnabled': 1, 'isReplicable': 0,
        'LODMode': 'AlwaysVisible',
        'localTransform': {'$type': 'WorldTransform', 'Position': pos, 'Orientation': {
            '$type': 'Quaternion', 'i': -r, 'j': -s / (4.0 * r), 'k': -s / (4.0 * r), 'r': r}},
        'mesh': {'DepotPath': strpath(RAIL), 'Flags': 'Default'},
        'meshAppearance': cname('default'), 'motionBlurScale': 1, 'name': cname(name),
        'navigationImpact': {'$type': 'NavGenNavigationSetting', 'navmeshImpact': 'Ignored'},
        'numInstances': 0, 'objectTypeID': 'ROT_Static', 'order': 0,
        'overrideMeshNavigationImpact': 1, 'parentTransform': None,
        'renderingPlane': 'RPl_Scene', 'renderSceneLayerMask': 'Default', 'version': 0,
        'visualScale': {'$type': 'Vector3', 'X': 1, 'Y': 1, 'Z': 1},
    }


def build_av_app():
    """The AV's look with the two rails in it. A component added to the
    entity's own compiled package crashed the game when the AV spawned
    (playtest 2026-11-04); an appearance built from `components` is the shape
    the recruiter's already has."""
    doc = vanilla(VANILLA_AV_APP)
    rc = doc['Data']['RootChunk']
    defs = {}
    _collect(doc, defs)
    seed = next(a.get('Data', a) for a in rc['appearances']
                if a.get('Data', a)['name']['$value'] == AV_LOOK)
    inline = not isinstance(seed['components'][0].get('Data'), dict)
    for i, (name, spot) in enumerate(RAILS):
        comp = _rail(name, spot, i)
        seed['components'].append(comp if inline else {'HandleId': str(6000 + i), 'Data': comp})
    seed['resolvedDependencies'] = list(seed['resolvedDependencies']) + [
        {'DepotPath': strpath(RAIL), 'Flags': 'Soft'}]
    seed.pop('compiledData', None)
    rc['appearances'] = [{'HandleId': '1', 'Data': seed}]
    done = set()
    for k, v in rc.items():
        if k != 'appearances':
            _keep_handles(v, defs, done)
    _keep_handles(rc['appearances'], defs, done)
    doc['Header']['ArchiveFileName'] = 'av.app'
    return doc


def build_av():
    doc = vanilla(VANILLA_AV)
    rc = doc['Data']['RootChunk']
    rc['appearances'][0]['appearanceResource']['DepotPath'] = strpath(AV_APP_DEPOT)
    rc['resolvedDependencies'] = [d for d in rc['resolvedDependencies']
                                  if d['DepotPath'].get('$value') != VANILLA_AV_APP] + [
        {'DepotPath': strpath(AV_APP_DEPOT), 'Flags': 'Soft'}]
    doc['Header']['ArchiveFileName'] = 'av.ent'
    return doc


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for name, build in (('recruiter.app.json', build_app), ('recruiter.ent.json', build_ent),
                        ('crew.ent.json', build_crew), ('av.app.json', build_av_app),
                        ('av.ent.json', build_av)):
        doc = build()
        with open(os.path.join(OUT, name), 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(doc, fh, indent=1)
    print('recruiter: %s, %s' % (APP_DEPOT, ENT_DEPOT))
