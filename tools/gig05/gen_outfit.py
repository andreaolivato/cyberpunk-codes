r"""Trauma Team: V's uniform, the game's own with the crew's real vest.

    python tools\gig05\gen_outfit.py

Writes, under mod\trauma_team\outfit:

  outfit.csv.json   the item factory row, `cc_g05_outfit`
  outfit.ent.json   the game's `player_outfit_item.ent` with the four uniform rows
  outfit.app.json   the game's four `_trauma_*` appearances from `outfit_02.app`

`Items.Trauma_Team_Outfit` has no chest plate. Its `t2_020_p?a_full__armor` is the
shoulder harness alone. The plate the crew wear is `t2_020_ma_full__armor`, with no
version for V. `Items.cc_g05_outfit` (source/tweaks/items.yaml) is the same record on
this entity. The rows keep their vanilla names, so the record's own appearance name
still finds them.

  vest_w.ent.json, vest_w_fpp.ent.json   the crew's vest entities, on the refit meshes

Third person swaps the harness for the vest. First person adds the vest without
shoulder pads. Male V wears the game's entities, whose bones are his. Female V wears
the refit from gen_vest.py.

A WORN ITEM IS BUILT FROM ITS APPEARANCE'S `partsValues`, so that list is what changes.
`components` and the compiled package go: an appearance with only `components` draws
nothing on V, measured in game on 2026-11-07, where photo mode showed her with no
clothes on.

`defaultAppearance` STAYS `default`, as in the game's file and in every item mod. The
item's own entity loads that look, and the real one goes on the player. With a real
appearance there, the item's entity also wore a full male third-person uniform, helmet
included, over the right one (measured in game: the band across the first-person view,
and a male vest over the refit).

THE VANILLA FILES ARE READ FROM `tools\_ent_cache`, the same way as gen_recruiter.py.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gig05_config as cfg  # noqa: E402
from gen_recruiter import CLI, CACHE, B, _collect, _keep_handles, strpath, cname  # noqa: E402

CONTENT = os.path.join(r'C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077',
                       'archive', 'pc', 'content')
OUT = os.path.join(cfg.RAW_MOD, 'outfit')
FOLDER = cfg.DEPOT + B + 'outfit' + B
FACTORY_KEY = 'cc_g05_outfit'

VANILLA_APP = B.join(['base', 'characters', 'appearances', 'player', 'items', 'outfit', 'outfit_02.app'])
VANILLA_ENT = B.join(['base', 'gameplay', 'items', 'equipment', 'outfit', 'player_outfit_item.ent'])
VANILLA_CSV = B.join(['base', 'gameplay', 'factories', 'items', 'clothing.csv'])
UNIFORM = ('_trauma_m', '_trauma_w', '_trauma_m_fpp', '_trauma_w_fpp')
HARNESS = 't2_020_p'
_TORSO = B.join(['base', 'characters', 'garment', 'corp_trauma', 'unique_trauma', 'torso'])
_MESH = _TORSO + B + 't2_020_full__armor' + B
VEST_MALE, VEST_MALE_FPP = 't2_020_ma_full__armor', 't2_020_ma_full__armor_no_shoulder_pads'
VEST = {'_trauma_m': _TORSO + B + VEST_MALE + '.ent',
        '_trauma_w': FOLDER + 'vest_w.ent',
        '_trauma_m_fpp': _TORSO + B + VEST_MALE_FPP + '.ent',
        '_trauma_w_fpp': FOLDER + 'vest_w_fpp.ent'}


def vanilla(path):
    out = os.path.join(CACHE, path.replace(B, os.sep)) + '.json'
    if not os.path.exists(out):
        os.makedirs(CACHE, exist_ok=True)
        subprocess.run([CLI, 'unbundle', CONTENT, '-o', CACHE, '-r',
                        path.split(B)[-1].replace('.', B + '.') + '$'],
                       capture_output=True, check=True)
        subprocess.run([CLI, 'convert', 'serialize', out[:-5], '-v', 'Quiet'],
                       capture_output=True, check=True)
    with open(out, encoding='utf-8-sig') as fh:
        return json.load(fh)


def _name(a):
    return a.get('Data', a)['name']['$value']


def _part(path):
    return {'$type': 'appearanceAppearancePart', 'resource': {'DepotPath': strpath(path), 'Flags': 'Soft'}}


def build_app():
    doc = vanilla(VANILLA_APP)
    rc = doc['Data']['RootChunk']
    defs = {}
    _collect(doc, defs)
    kept = {_name(a): a.get('Data', a) for a in rc['appearances'] if _name(a) in UNIFORM}
    if sorted(kept) != sorted(UNIFORM):
        raise SystemExit('outfit_02.app no longer has %s' % (UNIFORM,))
    for name, a in kept.items():
        parts = [p for p in a['partsValues']
                 if HARNESS not in p['resource']['DepotPath']['$value'].rsplit(B, 1)[-1]]
        parts.append(_part(VEST[name]))
        a['partsValues'] = parts
        a['components'] = []
        a['resolvedDependencies'] = []
        a.pop('compiledData', None)
    rc['appearances'] = [{'HandleId': str(i + 1), 'Data': kept[n]} for i, n in enumerate(UNIFORM)]
    done = set()
    for k, v in rc.items():
        if k != 'appearances':
            _keep_handles(v, defs, done)
    _keep_handles(rc['appearances'], defs, done)
    doc['Header']['ArchiveFileName'] = 'outfit.app'
    return doc


def _swap_mesh(node, old, new):
    if isinstance(node, dict):
        if node.get('DepotPath', {}) and isinstance(node['DepotPath'], dict)                 and node['DepotPath'].get('$value') == old:
            node['DepotPath'] = strpath(new)
        for v in node.values():
            _swap_mesh(v, old, new)
    elif isinstance(node, list):
        for v in node:
            _swap_mesh(v, old, new)


def build_vest(vest, out_name):
    doc = vanilla(_TORSO + B + vest + '.ent')
    _swap_mesh(doc, _MESH + vest + '.mesh', FOLDER + out_name + '.mesh')
    doc['Header']['ArchiveFileName'] = out_name + '.ent'
    return doc


def build_ent():
    doc = vanilla(VANILLA_ENT)
    rc = doc['Data']['RootChunk']
    rows = [a for a in rc['appearances'] if a['appearanceName']['$value'] in UNIFORM]
    if len(rows) != len(UNIFORM):
        raise SystemExit('player_outfit_item.ent no longer has the uniform rows')
    for a in rows:
        a['appearanceResource'] = {'DepotPath': strpath(FOLDER + 'outfit.app'), 'Flags': 'Soft'}
    rc['appearances'] = rows
    rc['defaultAppearance'] = cname('default')
    doc['Header']['ArchiveFileName'] = 'outfit.ent'
    return doc


def build_csv():
    doc = vanilla(VANILLA_CSV)
    rc = doc['Data']['RootChunk']
    sample = next(r for r in rc['compiledData'] if r[0] == 'player_outfit_item')
    rc['compiledData'] = [[FACTORY_KEY, FOLDER + 'outfit.ent'] + sample[2:]]
    rc['data'] = []
    doc['Header']['ArchiveFileName'] = 'outfit.csv'
    return doc


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for name, build in (('outfit.app', build_app), ('outfit.ent', build_ent), ('outfit.csv', build_csv),
                        ('vest_w.ent', lambda: build_vest(VEST_MALE, 'vest_w')),
                        ('vest_w_fpp.ent', lambda: build_vest(VEST_MALE_FPP, 'vest_w_fpp'))):
        path = os.path.join(OUT, name + '.json')
        with open(path + '.tmp', 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(build(), fh, indent=2)
        os.replace(path + '.tmp', path)
        print('wrote %s' % path)
