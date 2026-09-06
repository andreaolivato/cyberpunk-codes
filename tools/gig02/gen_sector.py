r"""Generates the world files that put an ACCESS POINT on the wall of Wakako's
pachinko parlor: the box V jacks into for the breach-protocol minigame.

    python tools\gig02\gen_sector.py

WHAT THIS SHIPS: one `worldDeviceNode` carrying the game's own physical access
point (`base\gameplay\devices\masters\access_points\accesspoint.ent`), in a
sector and streaming block of the mod's own, at a point on the parlor's wall.
The device is the game's: its "Jack in" prompt, the code grid, the datamine
rewards. What the gig adds is watching for the breach (Gig02_Encounter).

WHERE THE NODE COMES FROM (design call 2026-09-05: "a box, one of those where
you need to do the number hacking, in one of the walls of the parlor"). Every
physical access point placed in the cached sectors carries an instance buffer,
so one is lifted whole and re-anchored, the way gig 01 lifted its shard case
off a desk, which is the only proven route this project has for an instance
buffer. The one lifted is the game's own working street router,
`{ma_hey_spr_04_ap}` (exterior_-35_-20_0_0, node 316), kept beside this script
as `access_point_router_node.json`. Its buffer holds the entity chunk and no
stored controller state, so the game builds the default state, which is what
every open-world router runs on.

A QUEST DEVICE WAS LIFTED FIRST AND DID NOT WORK. `{q112_01_market_security}`
(exterior_-7_10_1_0, node 914) is a standalone access point whose one-chunk
buffer carries the controller and its persistent state. It shipped with
`deviceState` and `cachedDeviceState` forced DISABLED -> ON and
`authorizationProperties.isAuthorizationModuleOn` 1 -> 0; in play the prompt
read "Install Software" and pressing it did nothing, because the stored state
carries a personal-link interaction only its own quest completes. Backlog 37
and gotcha 98 hold the finding.

THE WALL SPOT WAS ESTIMATED AND THEN CAPTURED. The estimate came off the
parlor's own sector (`interior_-11_12_0_1`), which puts a 3 m wall piece
facing into the room at (-662.84, 822.01) yaw 10, the south wall beside the
corridor to Wakako's office. It was replaced on 2026-09-05 by the dev menu's
"CAPTURE THE SURFACE I'M LOOKING AT" against that wall, then lowered to chest
height and nudged 0.25 m west out of the wall's edge: see `AP_POS` below.
`AP_POS` IS THE AUTHORITY and `CCGig02Places.AccessPoint()` is a copy of it,
so change both together.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from questkit import cr2w                                           # noqa: E402
from gig02_config import (                                          # noqa: E402
    REPO, RAW, ANCHOR_POS, ANCHOR_PARLOR,
)

OUT_DIR = os.path.join(RAW, 'mod', 'worlds', '03_night_city', '_compiled',
                       'default')
SECTOR_DEPOT = (r'mod\worlds\03_night_city\_compiled\default'
                r'\cc_g02_world.streamingsector')

# The access point node lifted off the game's own sector. Read, never written.
# THE GAME'S OWN WORKING WALL ROUTER, `{ma_hey_spr_04_ap}` (exterior_-35_-20_0_0
# node 316), lifted whole on 2026-09-05. It replaces the quest device lifted
# first (`{q112_01_market_security}`), whose stored state carried a quest-only
# personal-link interaction: in play the prompt read "Install Software" and did
# nothing. The router carries no stored state at all (the entity chunk only),
# so the game builds the default one, which is what every open-world router
# runs on.
SOURCE = os.path.join(REPO, 'tools', 'gig02', 'access_point_router_node.json')

# THE NAME. A NodeRef path uses forward slashes, so no backslash is built.
AP_REF = '$/03_night_city/#c_westbrook/japantown/#cc_g02_access_point'

# CAPTURED 2026-09-05 (the surface capture on the south wall, at eye height,
# then lowered to chest height): the wall's face is at y 822.21 here.
# Nudged 0.25 m to V's right (west) on 2026-09-05: the box stood half
# inside the wall's edge.
AP_POS = (-663.50, 822.33, 20.90)
# FACING THE WALL, NOT THE ROOM (measured 2026-09-05 with the dev menu's
# turn buttons on the shipped node): the wall faces yaw 10 into the room, the
# Arasaka panel offered "Jack in" at yaw 10, and the small router offered it
# only turned 180 from that. Gotcha 98.
AP_YAW = -170.0
# The point the streaming box and the grid cell are computed from.
RELAY_POS = AP_POS

# HOW FAR THE OBJECT RENDERS FROM, and therefore how big the sector's streaming
# box has to be: the sector must be resident before the node can come into range
# or the object pops in. Gig 01's value, which came off the vanilla node.
MAX_STREAMING_DISTANCE = 164.710114
STREAM_MARGIN = 50.0

# The world grid. A cell is 64 m across at level 0 and doubles per level, so
# W = 64 * 2^level; a sector's cell index is (floor(x/W), floor(y/W),
# floor(z/W)) and rldGridCell packs it as (i + S/2) + S*(j + S/2) +
# S^2*(k + S/2), where S is 2^(8 - level) for an Exterior sector. Derived from
# all 23,689 vanilla sector descriptors and checked by prediction at three
# levels; gig 01's gen_sector.py carries the full account.
LEVEL = 1
CELL_METRES = 64.0 * (2 ** LEVEL)
AXIS_CELLS = 2 ** (8 - LEVEL)


def grid_cell(pos, cell_metres=CELL_METRES, axis_cells=AXIS_CELLS):
    half = axis_cells // 2
    i, j, k = (int(math.floor(c / cell_metres)) for c in pos)
    return ((i + half) + axis_cells * (j + half)
            + axis_cells * axis_cells * (k + half))


GRID_CELL = grid_cell(RELAY_POS)


def cname(v):
    return {'$type': 'CName', '$storage': 'string', '$value': v}


def vec3(p):
    return {'$type': 'Vector3', 'X': p[0], 'Y': p[1], 'Z': p[2]}


def vec4(p, w=0):
    return {'$type': 'Vector4', 'W': w, 'X': p[0], 'Y': p[1], 'Z': p[2]}


def box_corner(sign):
    """A corner of the sector's streaming box: the object, plus its reach in
    every direction. `sign` is +1 for Max and -1 for Min."""
    reach = MAX_STREAMING_DISTANCE + STREAM_MARGIN
    return tuple(c + sign * reach for c in RELAY_POS)


def vanilla_access_point():
    """The game's own standalone access point, out of the committed excerpt."""
    if not os.path.exists(SOURCE):
        raise SystemExit('%s is missing' % SOURCE)
    with open(SOURCE, encoding='utf-8') as fh:
        doc = json.load(fh)
    print('access point lifted from %s node %d' % (doc['sector'], doc['node']))
    return doc['data']


def renumber(obj, base, counter):
    """Fresh, file-unique HandleIds for the lifted chunk. A handle id resolves
    WITHIN the file, so the vanilla node's ids cannot be reused as they stand.
    The values mean nothing beyond being distinct."""
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k == 'HandleId':
                counter[0] += 1
                out[k] = str(base + counter[0])
            elif k == 'BufferId':
                out[k] = str(base)
            else:
                out[k] = renumber(v, base, counter)
        return out
    if isinstance(obj, list):
        return [renumber(v, base, counter) for v in obj]
    return obj


def quat_yaw(deg):
    """A rotation about Z by `deg` degrees, the convention every other yaw in
    this gig uses (counter-clockwise from +Y seen from above)."""
    h = math.radians(deg) / 2.0
    return {'$type': 'Quaternion', 'i': 0, 'j': 0, 'k': math.sin(h), 'r': math.cos(h)}


def sector():
    van = vanilla_access_point()

    node = json.loads(json.dumps(van))
    node['debugName'] = cname('{cc_g02_access_point}')
    # The router look, which is the lifted node's own. Its prompt side is the
    # opposite of the Arasaka panel's (gotcha 98), which AP_YAW carries.
    node['appearanceName'] = cname('access_point_router_b')
    # Nothing of the Heywood street's network rides along.
    node['deviceConnections'] = []
    node['instanceData'] = renumber(
        json.loads(json.dumps(van['instanceData'])), 2000, [0])
    chunks = node['instanceData']['Data']['buffer']['Data']['Chunks']
    ap = chunks[0]
    assert ap['$type'] == 'AccessPoint', ap['$type']
    # THE NAME THE BREACH SCREEN SHOWS for the network. The lifted value is
    # "Local Network 1"; this is Wakako's floor.
    ap['networkName'] = 'PARLOR FLOOR NET'
    # The loot table of a Heywood street is not this parlor's; the field is
    # emptied so the datamine rewards fall back to the default scaling.
    ap['contentScale'] = {'$type': 'TweakDBID', '$storage': 'uint64', '$value': '0'}

    data = {
        'Id': '0',
        'NodeIndex': 0,
        'Position': vec4(AP_POS),
        'Orientation': quat_yaw(AP_YAW),
        'Scale': vec3((1, 1, 1)),
        'Pivot': vec3((0, 0, 0)),
        'Bounds': {'$type': 'Box', 'Max': vec4(AP_POS), 'Min': vec4(AP_POS)},
        # THE NAME. An unnamed node does not load at all.
        'QuestPrefabRefHash': {'$type': 'NodeRef', '$storage': 'string',
                               '$value': AP_REF},
        'UkHash1': {'$type': 'NodeRef', '$storage': 'uint64', '$value': '0'},
        'CookedPrefabData': {'DepotPath': {'$type': 'ResourcePath',
                                           '$storage': 'uint64', '$value': '0'},
                             'Flags': 'Default'},
        # The shard case's flags and a FINITE streaming distance, which is the
        # combination gig 01 found renders (a trigger area's did not).
        'MaxStreamingDistance': MAX_STREAMING_DISTANCE,
        'UkFloat1': 50,
        'Uk10': 1056,
        'Uk11': 10762,
        'Uk12': 0,
        'Uk13': '0',
        'Uk14': '0',
    }
    return {
        'Header': cr2w.header('cc_g02_world.streamingsector'),
        'Data': {
            'Version': 195, 'BuildVersion': 0,
            'RootChunk': {
                '$type': 'worldStreamingSector',
                'category': 'Exterior',
                'cookingPlatform': 'PLATFORM_PC',
                'externInplaceResource': {'DepotPath': {'$type': 'ResourcePath',
                                                        '$storage': 'uint64',
                                                        '$value': '0'},
                                          'Flags': 'Soft'},
                'level': LEVEL,
                'localInplaceResource': [],
                'nodeData': {
                    'BufferId': '0',
                    'Flags': 4063232,
                    'Type': ('WolvenKit.RED4.Archive.Buffer.worldNodeDataBuffer, '
                             'WolvenKit.RED4, Version=8.20.0.0, Culture=neutral, '
                             'PublicKeyToken=null'),
                    'Data': [data],
                },
                # The name again, which is how a sector declares it.
                'nodeRefs': [{'$type': 'NodeRef', '$storage': 'string',
                              '$value': AP_REF}],
                'nodes': [{'HandleId': '0', 'Data': node}],
                'persistentNodeIndex': 0,
                'persistentNodes': [],
                'variantIndices': [0],
                'variantNodes': [],
                # 62, as every shipped sector carries. Writing 0 here is a
                # silent way to get a sector the engine may not read.
                'version': 62,
            },
            'EmbeddedFiles': [],
        },
    }


def block():
    return {
        'Header': cr2w.header('cc_g02_world.streamingblock'),
        'Data': {
            'Version': 195, 'BuildVersion': 0,
            'RootChunk': {
                '$type': 'worldStreamingBlock',
                'cookingPlatform': 'PLATFORM_PC',
                'descriptors': [{
                    '$type': 'worldStreamingSectorDescriptor',
                    'blockIndex': {'$type': 'worldStreamingBlockIndex',
                                   'oup': 'Base', 'rldGridCell': GRID_CELL},
                    'category': 'Exterior',
                    'data': {'DepotPath': {'$type': 'ResourcePath',
                                           '$storage': 'string',
                                           '$value': SECTOR_DEPOT},
                             'Flags': 'Soft'},
                    'level': LEVEL,
                    'numNodeRanges': 1,
                    'questPrefabNodeRef': {'$type': 'NodeRef',
                                           '$storage': 'uint64', '$value': '0'},
                    # THE OBJECT'S OWN REACH, not the map. A cube centred on the
                    # node and a little wider than the distance it renders from,
                    # so the sector is in range while the object could be
                    # visible and out of range everywhere else. A whole-map box
                    # keeps the sector resident for the entire session.
                    'streamingBox': {'$type': 'Box',
                                     'Max': vec4(box_corner(+1), w=1),
                                     'Min': vec4(box_corner(-1), w=1)},
                    'variants': [],
                }],
                'index': {'$type': 'worldStreamingBlockIndex',
                          'oup': 'Base', 'rldGridCell': 0},
            },
            'EmbeddedFiles': [],
        },
    }


if __name__ == '__main__':
    os.makedirs(OUT_DIR, exist_ok=True)
    for name, doc in (('cc_g02_world.streamingsector.json', sector()),
                      ('cc_g02_world.streamingblock.json', block())):
        with open(os.path.join(OUT_DIR, name), 'w', encoding='utf-8',
                  newline='\n') as fh:
            json.dump(doc, fh, indent=2)
        print('wrote', os.path.join(OUT_DIR, name))
    print('access point at %.3f, %.3f, %.3f, yaw %.1f, named %s'
          % (AP_POS + (AP_YAW, AP_REF)))
