r"""Fixer 01, dev only: the pose rig, an entity of nothing but workspots.

    python tools\fixer01\gen_poses.py

Writes raw\mod\fixer01\dev\poses.ent.json: an entity with no mesh and one
`workWorkspotResourceComponent` per candidate sitting workspot in the game,
each named after the resource's file stem. The dev menu (source\cet-dev\
init.lua, "Poses") spawns it at her seat and plays any of them on her with
`WorkspotGameSystem.PlayInDeviceSimple`, which is the one route CET has to
put an NPC in an arbitrary workspot: the system takes a DEVICE entity and
the name of a workspot component on it, and this entity exists to be that
device. The same call is what Appearance Menu Mod's pose tab makes, against
an entity of its own that lists every animation in the game; this one lists
the game's sitting WORKSPOTS instead, because a workspot is what her
community entry and her scene play, and a pose chosen here is shipped by
naming the same resource in fixer01_config.FIXER_WORKSPOT.

THE CANDIDATES are every generic sitting workspot under
`base\workspots\common\` (couch, chair, chair_table, bench), read out of
`memoryresident_1_general.archive` on 2026-09-21, where every workspot in
the game lives. The dead, drugged, braindance and child ones are left out;
the ones that hold a prop (a tablet, a bottle, a knife, a gun, a phone) are
in, marked, because whether the prop appears on a body that carries none is
one of the things the rig is for finding out.

THE ENTITY is the shell of a game furniture entity (`int_furniture_002__
bar_lounge_chair_c.ent`, read 2026-09-21) with its components replaced by
the workspot components and its compiled buffer dropped, which WolvenKit
regenerates from the components (the same route as gen_npv.py). A
workspot component's shape is copied off `netrunner_chair.ent`'s
`personalLinkPlayerWorkspot`: `workspotResource` carries the path, the
sync fields are empty, and `localTransform` is the identity, so the
workspot's origin is the rig's position.

A depot path is BUILT from chr(92), never typed (gotcha 28).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from questkit import cr2w                                            # noqa: E402
from fixer01_config import RAW_MOD, DEPOT                             # noqa: E402

B = chr(92)
OUT = os.path.join(RAW_MOD, 'dev', 'poses.ent.json')
ENT_DEPOT = DEPOT + B + 'dev' + B + 'poses.ent'
WS = 'base' + B + 'workspots' + B + 'common' + B

# (component name, folder, file stem, holds a prop)
CANDIDATES = [
    ('couch_01', 'couch', 'generic__sit_couch__sit_around__01', False),
    ('couch_02', 'couch', 'generic__sit_couch__sit_around__02', False),
    ('couch_03_arms_crossed', 'couch', 'generic__sit_couch__sit_around__03', False),
    ('couch_tv_arms_crossed', 'couch', 'generic__sit_couch_tv__watch__01', False),
    ('couch_tablet', 'couch', 'generic__sit_couch_tablet__read__01', True),
    ('couch_champagne', 'couch', 'generic__sit_couch_lean_back_champagne__drink__01', True),
    ('couch_bottle', 'couch', 'generic__sit_couch_lean_back_bottle__drink__01', True),
    ('couch_gun_relax', 'couch', 'big__sit_couch_lean_back_gun__relax__01', True),
    ('chair_01', 'chair', 'generic__sit_chair__sit_around__01', False),
    ('chair_02', 'chair', 'generic__sit_chair__sit_around__02', False),
    ('chair_03', 'chair', 'generic__sit_chair__sit_around__03', False),
    ('chair_04', 'chair', 'generic__sit_chair__sit_around__04', False),
    ('chair_05', 'chair', 'generic__sit_chair__sit_around__05', False),
    ('chair_06', 'chair', 'generic__sit_chair__sit_around__06', False),
    ('chair_07', 'chair', 'generic__sit_chair__sit_around__07', False),
    ('chair_back_01', 'chair', 'generic__sit_chair_lean_back__sit_around__01', False),
    ('chair_back_02', 'chair', 'generic__sit_chair_lean_back__sit_around__02', False),
    ('chair_back_03', 'chair', 'generic__sit_chair_lean_back__sit_around__03', False),
    ('chair_back_04', 'chair', 'generic__sit_chair_lean_back__sit_around__04', False),
    ('chair_back_think', 'chair', 'generic__sit_chair_lean_back__think__01', False),
    ('chair_back_observe', 'chair', 'generic__sit_chair_lean_back__observe__01', False),
    ('chair_back_nails', 'chair', 'generic__sit_chair_lean_back__look_at_nails__01', False),
    ('chair_back_knife', 'chair', 'generic__sit_chair_lean_back_knife__sit_around__01', True),
    ('chair_back_gun', 'chair', 'generic__sit_chair_lean_back_gun__show_off__01', True),
    ('chair_back_smoke', 'chair', 'generic__sit_chair_lean_back_cigarette__smoke__01', True),
    ('chair_front_01', 'chair', 'generic__sit_chair_lean_front__sit_around__01', False),
    ('chair_front_02', 'chair', 'generic__sit_chair_lean_front__sit_around__02', False),
    ('chair_front_think_01', 'chair', 'generic__sit_chair_lean_front__think__01', False),
    ('chair_front_think_02', 'chair', 'generic__sit_chair_lean_front__think__02', False),
    ('chair_front_nervous', 'chair', 'generic__sit_chair_lean_front__nervous__01', False),
    ('chair_front_smoke', 'chair', 'generic__sit_chair_lean_front__smoke__01', True),
    ('chair_front_glass', 'chair', 'generic__sit_chair_lean_front_glass__drink__01', True),
    ('chair_phone_talk', 'chair', 'generic__sit_chair_cellphone__talk__01', True),
    ('chair_phone_check', 'chair', 'generic__sit_chair_cellphone__check__01', True),
    ('chair_tablet', 'chair', 'generic__sit_chair_tablet__read__01', True),
    ('chair_female_back', 'chair', 'female__sit_chair_lean_back__sit_around__01', False),
    ('chair_female_backrest', 'chair', 'female__sit_chair_backrest__sit_around__01', False),
    ('chair_big_back_01', 'chair', 'big__sit_chair_lean_back__sit_around__01', False),
    ('chair_big_back_02', 'chair', 'big__sit_chair_lean_back__sit_around__02', False),
    ('chair_backwards', 'chair', 'generic__sit_chair_lean0__2h_on_backrest__01', False),
    ('table_feet_up', 'chair_table', 'generic__sit_chair_table_lean_back__feet_up__01', False),
    ('bench_back_01', 'bench', 'generic__sit_bench_lean_back__sit_around__01', False),
    ('bench_back_02', 'bench', 'generic__sit_bench_lean_back__sit_around__02', False),
    ('bench_back_hand', 'bench', 'generic__sit_bench_lean_back_l_hand_on_back__talk__01', False),
]


def resource(folder, stem):
    return WS + folder + B + stem + '.workspot'


def cname(v):
    return {'$type': 'CName', '$storage': 'string', '$value': v}


def path(v, flags='Default'):
    return {'DepotPath': {'$type': 'ResourcePath', '$storage': 'string', '$value': v},
            'Flags': flags}


def no_path():
    return {'DepotPath': {'$type': 'ResourcePath', '$storage': 'uint64', '$value': '0'},
            'Flags': 'Default'}


def component(i, name, folder, stem):
    # Components are inline objects in an entity template, not handles (the
    # `entity` field is the one handle); read off the furniture entity.
    return {
        '$type': 'workWorkspotResourceComponent',
        'deviceWorkspotResourceSync': no_path(),
        'id': str(1000000 + i),
        'isReplicable': 0,
        'localTransform': {
            '$type': 'WorldTransform',
            'Orientation': {'$type': 'Quaternion', 'i': 0, 'j': 0, 'k': 0, 'r': 1},
            'Position': {'$type': 'WorldPosition',
                         'x': {'$type': 'FixedPoint', 'Bits': 0},
                         'y': {'$type': 'FixedPoint', 'Bits': 0},
                         'z': {'$type': 'FixedPoint', 'Bits': 0}}},
        'name': cname(name),
        'npcWorkspotResourceSync': no_path(),
        'parentTransform': None,
        'shouldCrouch': 0,
        'syncSlotName': cname('None'),
        'workspotResource': path(resource(folder, stem)),
    }


def build():
    return {
        'Header': cr2w.header(os.path.basename(ENT_DEPOT)),
        'Data': {
            'Version': 195, 'BuildVersion': 0,
            'RootChunk': {
                '$type': 'entEntityTemplate',
                'appearances': [],
                'backendDataOverrides': [],
                'bindingOverrides': [],
                'compiledEntityLODFlags': 0,
                'componentResolveSettings': [],
                'components': [component(i, n, f, s) for i, (n, f, s, _p) in enumerate(CANDIDATES)],
                'cookingPlatform': 'PLATFORM_PC',
                'defaultAppearance': cname('default'),
                # A GAME OBJECT, NOT A PLAIN ENTITY. The workspot system's
                # `PlayInDeviceSimple` takes the device as a `gameObject`, and
                # the furniture shell's `entEntity` was refused in play
                # (2026-09-21: "parameter 1 must be handle:gameObject").
                'entity': {'HandleId': '10', 'Data': {
                    '$type': 'gameObject',
                    'customCameraTarget': 'ECCTV_All',
                    'renderSceneLayerMask': 'Default'}},
                'includeInstanceBuffer': None,
                'includes': [],
                'inplaceResources': [],
                'localData': None,
                'resolvedDependencies': [],
                'visualTagsSchema': None,
            },
            'EmbeddedFiles': [],
        },
    }


def lua_table():
    """The same list for the dev menu, printed so the two cannot drift."""
    rows = ['    { "%s", "%s", %s },' % (n, s, 'true' if p else 'false')
            for n, _f, s, p in CANDIDATES]
    return '\n'.join(rows)


if __name__ == '__main__':
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(build(), fh, indent=2)
    print('wrote %s (%d workspots)' % (OUT, len(CANDIDATES)))
    if '--lua' in sys.argv:
        print(lua_table())
