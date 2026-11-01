r"""Lift the scavengers' own props out of the game, for the room.

    python tools\gig04\lift_props.py

Writes tools/gig04/props_scav.json: for each prop and each floor decal the
room is dressed with, the node as the game ships it (mesh, appearance,
material, size, every flag) and the instance flags it was placed with. The
sources are the prologue's scavenger apartment (`interior_-8_6_2_1`) and a
bar the game dresses with blood (`interior_-12_14_0_0`), read from the
sector cache (`%LOCALAPPDATA%\CyberpunkCodes\sector_cache\json_interiors`,
tools/sector_scan.py). gen_room.py places the copies; nothing here is
invented beyond where each one stands.

The file is committed so a fresh clone regenerates the room with nothing
installed. Re-run only to add a prop.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'CyberpunkCodes',
                     'sector_cache', 'json_interiors')
OUT = os.path.join(HERE, 'props_scav.json')

# mesh file name -> the sector to lift it from
PROPS = {
    'poor_sofa_a_old.mesh': 'interior_-8_6_2_1',
    'diner_sofa_01_c.mesh': 'interior_-8_6_2_1',
    'poor_braindance_a_base.mesh': 'interior_-8_6_2_1',
    'medical_cart_c.mesh': 'interior_-8_6_2_1',
    'medical_jar_b.mesh': 'interior_-8_6_2_1',
    'industrial_shelf_a.mesh': 'interior_-8_6_2_1',
    'industrial_shelf_c.mesh': 'interior_-8_6_2_1',
    'industrial_shelf_f.mesh': 'interior_-8_6_2_1',
    'gas_tank_d.mesh': 'interior_-8_6_2_1',
    'military_case_i.mesh': 'interior_-8_6_2_1',
    'cardboard_box_b_closed.mesh': 'interior_-8_6_2_1',
    'garbage_bag_l_pile.mesh': 'interior_-8_6_2_1',
    'garbage_bag_c.mesh': 'interior_-8_6_2_1',
    'barrel_drum_e_destroyed.mesh': 'interior_-8_6_2_1',
    'floor_carpet_b.mesh': 'interior_-8_6_2_1',
    'floor_carpet_c.mesh': 'interior_-8_6_2_1',
    'plastic_floor_mat_a.mesh': 'interior_-8_6_2_1',
    'cardboard_trash_a.mesh': 'interior_-8_6_2_1',
    'newspaper_b_full.mesh': 'interior_-8_6_2_1',
    'newspaper_k_pile.mesh': 'interior_-8_6_2_1',
    'street_trash_d.mesh': 'interior_-8_6_2_1',
    'drink_bottle_b_wine.mesh': 'interior_-8_6_2_1',
    'cable_coil_c.mesh': 'interior_-8_6_2_1',
    'postal_box_e.mesh': 'interior_-8_6_2_1',
    'cleaning_rag_c_bloody.mesh': 'interior_-12_14_0_0',
    'cleaning_rag_b.mesh': 'interior_-12_14_0_0',
    'drink_bottle_e_beer.mesh': 'interior_-12_14_0_0',
    'braindance_cable_set_b.mesh': 'interior_-12_14_0_0',
    'ceiling_lamp_long_a.mesh': 'interior_-12_14_0_0',
    # THE CLAWS' COUCHES AND CHAIRS, for the bigger room (2026-10-01): the
    # scavengers' own sofa family and the cheap chairs, from whichever
    # interior carries a static copy.
    'poor_sofa_b_old.mesh': 'interior_-8_6_2_1',
    'poor_sofa_a.mesh': 'interior_-8_6_2_1',
    'poor_sofa_b.mesh': 'interior_-8_6_2_1',
    'poor_residential_chair_c.mesh': 'interior_-8_6_2_1',
    'poor_utility_chair_c_dst.mesh': 'interior_-8_6_2_1',
    'diner_sofa_02_d.mesh': 'interior_-8_6_2_1',
}
# decal material -> sector; floor decals only, so the orientation lifted
# with each one (projecting down onto a floor) is the right one here too.
DECALS = {
    'blood_g.mi': 'interior_-12_14_0_0',
    'blood_b.mi': 'interior_-12_14_0_0',
    'blood_f.mi': 'interior_-12_14_0_0',
    'blood_decal_06.mi': 'interior_-12_14_0_0',
    'dirt_f.mi': 'interior_-8_6_2_1',
    'dirt_l.mi': 'interior_-8_6_2_1',
    'decal_trash_06.mi': 'interior_-8_6_2_1',
}

FLAG_KEYS = ('MaxStreamingDistance', 'UkFloat1', 'Uk10', 'Uk11', 'Uk12',
             'Uk13', 'Uk14')


def load(sector):
    p = os.path.join(CACHE, sector + '.streamingsector.json')
    if not os.path.exists(p):
        raise SystemExit('%s is not in the sector cache; run tools/sector_scan.py '
                         'index first' % sector)
    with open(p, encoding='utf-8') as fh:
        return json.load(fh)['Data']['RootChunk']


def lift_mesh(doc, name):
    """The first static mesh node carrying this mesh, and its first
    instance's flags. A static node only: an instanced node's placements
    live in a buffer and are not what a single copy wants."""
    for inst in doc['nodeData']['Data']:
        nd = doc['nodes'][inst['NodeIndex']]['Data']
        if nd['$type'] != 'worldStaticMeshNode':
            continue
        m = (nd.get('mesh') or {}).get('DepotPath', {}).get('$value', '')
        if m.split(chr(92))[-1] == name:
            return nd, {k: inst[k] for k in FLAG_KEYS}, inst['Orientation']
    return None, None, None


def lift_decal(doc, name):
    """A floor decal: a decal node on this material whose orientation is
    a plain yaw (no tilt), which is one lying on a floor."""
    for inst in doc['nodeData']['Data']:
        nd = doc['nodes'][inst['NodeIndex']]['Data']
        if nd['$type'] != 'worldStaticDecalNode':
            continue
        m = (nd.get('material') or {}).get('DepotPath', {}).get('$value', '')
        if m.split(chr(92))[-1] != name:
            continue
        o = inst['Orientation']
        if abs(o['i']) < 0.02 and abs(o['j']) < 0.02:
            return nd, {k: inst[k] for k in FLAG_KEYS}, o
    return None, None, None


def anywhere(name, finder, docs):
    """The named sector lacks a static copy (its own is instanced); the
    first sector in the cache that has one."""
    for fn in sorted(os.listdir(CACHE)):
        if not fn.endswith('.json'):
            continue
        with open(os.path.join(CACHE, fn), encoding='utf-8') as fh:
            if name not in fh.read():
                continue
        sector = fn.replace('.streamingsector.json', '')
        doc = docs.setdefault(sector, load(sector))
        nd, flags, orient = finder(doc, name)
        if nd is not None:
            return sector, nd, flags, orient
    return None, None, None, None


def main():
    docs = {}
    out = {'props': {}, 'decals': {}}
    missing = []
    for name, sector in PROPS.items():
        doc = docs.setdefault(sector, load(sector))
        nd, flags, orient = lift_mesh(doc, name)
        if nd is None:
            sector, nd, flags, orient = anywhere(name, lift_mesh, docs)
        if nd is None:
            missing.append(name)
            continue
        # The source instance's orientation too: a prop authored on its
        # side (the diner sofa lay like a drum in the room, playtest
        # 2026-10-01) carries its tilt there, and gen_room keeps the tilt
        # under its own yaw.
        out['props'][name] = {'sector': sector, 'node': nd, 'flags': flags,
                              'orientation': orient}
    for name, sector in DECALS.items():
        doc = docs.setdefault(sector, load(sector))
        nd, flags, orient = lift_decal(doc, name)
        if nd is None:
            sector, nd, flags, orient = anywhere(name, lift_decal, docs)
        if nd is None:
            missing.append(name)
            continue
        out['decals'][name] = {'sector': sector, 'node': nd, 'flags': flags,
                               'orientation': orient}
    with open(OUT, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(out, fh, indent=1)
    print('wrote %s: %d props, %d decals' % (OUT, len(out['props']), len(out['decals'])))
    if missing:
        print('NOT FOUND as a static node (instanced only?):', ', '.join(missing))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
