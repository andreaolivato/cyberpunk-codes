r"""Generates the world files that put the data shard on the office desk.

  mod\worlds\03_night_city\_compiled\default\cc_g01_world.streamingsector
  mod\worlds\03_night_city\_compiled\default\cc_g01_world.streamingblock

WHAT THIS SHIPS, AND WHY IT IS THE SHAPE IT IS.

A `worldEntityNode` pointing at our own `cc_g01_shard.ent`. It RENDERS - that
much is proven in game - and it is read by WALKING UP TO IT, not by pressing a
key. Gig01_Encounter fires the beat on proximity.

THE PROMPT WAS ABANDONED DELIBERATELY, after seven attempts and a lot of
one evening. What was established, in order, and none of it should be
re-derived:

  * `DynamicEntitySystem` + `templatePath` attaches an entity and never renders
    its mesh. It is an NPC/device spawner, not a prop placer.
  * `exEntitySpawner.Spawn` - what CyberScript and friends use to make objects
    appear - is a Codeware native for CET LUA ONLY. `unresolved reference` from
    redscript.
  * A sector node DOES render, once the sector copies a working mod's
    conventions: `mod\worlds\03_night_city\_compiled\default\...`, category
    Exterior, level 1, a REAL streaming box (+-5000, not float-max), and the
    node flags of an entity node rather than a trigger area's.
  * A prompt on a bespoke entity could not be raised at all. The class attached
    (`cc_g01_dbg_shard_class = 1`), the interaction component resolved, the
    hotspot definition loaded, the choice was published on both the default and
    the `Loot` layer, a collider on the "Interaction Object" filter and a
    targeting component were added - and `GetActiveInputLayers` never reported a
    single active layer (`cc_g01_dbg_shard_ui = 3`, every sample, two minutes).
  * A VERBATIM copy of the working container - same template, same appearance,
    all 53 fields of its instance data, same node flags - was equally inert in a
    mod-added sector. That is the unexplained part, and it is where a future
    attempt should start.
  * Swapping the ITEM on the vanilla container, to fix its "Flowers of Silence"
    title, never ran: `cc_g01_dbg_shard_item` stopped at 1, meaning no
    `ShardCaseContainer` ever takes control within 12 m of that desk. Whatever
    that object is at runtime, it is not the class its own sector node names.

So: a shard you can see, walk to, and have V react to. the design call, and the
right one - "let's put back the duplicate shard, and start reading it on
proximity rather than action" beats a tooltip nobody can fix.
"""
import json
import math
import os
import sys

# questkit is in tools/, one level up from this gig's generators. See
# backlog.md 21.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from questkit import cr2w                                            # noqa: E402

_TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(_TOOLS)
RAW = os.path.join(REPO, 'mods', 'gig-01-negative-balance', 'source', 'wkit',
                   'raw', 'mod', 'worlds', '03_night_city', '_compiled', 'default')

SECTOR_DEPOT = r'mod\worlds\03_night_city\_compiled\default\cc_g01_world.streamingsector'
SHARD_ENT = r'mod\negative_balance\entity\cc_g01_shard.ent'

# CAPTURED IN GAME, standing ON the desk ("another desk", 2026-08-13), so z is
# the desk SURFACE. Keep in step with CCG01Shard.ObjectSpot() in
# Gig01_Shard.reds. (It also named tools/patch_cooked_mappins.py, which was
# deleted on 2026-08-14 when ArchiveXL turned out to compute pin positions
# itself; nothing needs keeping in step with it any more).
SHARD_POS = (-245.654, -1454.667, 15.400)

# HOW FAR THE SHARD RENDERS FROM, and therefore how big the sector's streaming
# box has to be. Written here rather than inline because the box below is
# derived from it: the sector must be resident before the node can come into
# range, or the shard pops in.
MAX_STREAMING_DISTANCE = 164.710114
# 50 m of headroom on top of that, so the sector is loaded by the time the node
# is in reach rather than in the same moment.
STREAM_MARGIN = 50.0

# The world grid, and the two values that place this sector in it.
#
# WHAT THESE USED TO BE: a +-5000 box and rldGridCell 129182, both copied
# wholesale from GeneralShadowsFix, an installed world-edit mod that works.
# For a mod that edits the whole map a whole-map box is right. For one shard on
# one desk in Heywood it meant the sector was in range from everywhere in the
# game and stayed resident for the whole session, and the grid cell was a
# spatial bucket belonging to another mod's sectors with ours attached to it.
#
# BOTH ARE DERIVED NOW, from the 23,689 vanilla sector descriptors in
# `all.streamingblock` (2026-08-18). The grid is regular and the packing is
# exact, with no exceptions across the 21,332 descriptors whose sector name
# states their own cell:
#
#   a cell is 64 m across at level 0 and doubles per level, so W = 64 * 2^level
#   a sector's cell index is (floor(x/W), floor(y/W), floor(z/W))
#   rldGridCell = (i + S/2) + S*(j + S/2) + S^2*(k + S/2)
#
# S is how many cells the axis field holds: 2^(8 - level) for an Exterior
# sector, 2^(9 - level) for Interior and Navigation ones, which sit a level
# finer. Ours is Exterior at level 1, so S is 128.
#
# Checked by prediction rather than by pattern-matching: the formula returns the
# rldGridCell that the vanilla sector covering the shard's own position actually
# carries, and does so at all three levels tested (`exterior_-4_-23_0_0`,
# `exterior_-2_-12_0_1`, `exterior_-1_-6_0_2`).
#
# Also established there, and worth having if a future sector needs it:
# rldGridCell 0 is legal. 2,354 shipped Quest sectors carry it, together with a
# float-max streaming box, which is the game's own shape for a sector that is
# not on the exterior grid. It is not ours: this one is Exterior and on the grid.
LEVEL = 1
CELL_METRES = 64.0 * (2 ** LEVEL)
AXIS_CELLS = 2 ** (8 - LEVEL)


def grid_cell(pos, cell_metres=CELL_METRES, axis_cells=AXIS_CELLS):
    """The rldGridCell for a world position, by the packing described above."""
    half = axis_cells // 2
    i, j, k = (int(math.floor(c / cell_metres)) for c in pos)
    return ((i + half) + axis_cells * (j + half)
            + axis_cells * axis_cells * (k + half))


GRID_CELL = grid_cell(SHARD_POS)


def cname(v):
    return {'$type': 'CName', '$storage': 'string', '$value': v}


def vec3(p):
    return {'$type': 'Vector3', 'X': p[0], 'Y': p[1], 'Z': p[2]}


def vec4(p, w=0):
    return {'$type': 'Vector4', 'W': w, 'X': p[0], 'Y': p[1], 'Z': p[2]}


def box_corner(sign):
    """A corner of the sector's streaming box: the shard, reach in every
    direction. `sign` is +1 for Max and -1 for Min."""
    reach = MAX_STREAMING_DISTANCE + STREAM_MARGIN
    return tuple(c + sign * reach for c in SHARD_POS)


def header(name):
    return cr2w.header(name)


def sector():
    node = {
        '$type': 'worldEntityNode',
        'appearanceName': cname('default'),
        'debugName': cname('{cc_g01_shard}'),
        'entityLod': 0,
        'entityTemplate': {'DepotPath': {'$type': 'ResourcePath',
                                         '$storage': 'string',
                                         '$value': SHARD_ENT},
                           'Flags': 'Soft'},
        'instanceData': None,
        'ioPriority': 'Immediate',
        'isHostOnly': 0,
        'isVisibleInGame': 1,
        'proxyScale': None,
        'sourcePrefabHash': '0',
        'tag': 'None',
        'tagExt': 'None',
    }
    data = {
        'Id': '0',
        'NodeIndex': 0,
        'Position': vec4(SHARD_POS),
        # Identity, i.e. standing upright. It was briefly laid flat and playtesting
        # asked for it back: flat and chip-sized it is a sliver nobody can pick
        # out of a dark office. Legibility beats realism for a thing the quest
        # requires you to find.
        'Orientation': {'$type': 'Quaternion', 'i': 0, 'j': 0, 'k': 0, 'r': 1},
        'Scale': vec3((1, 1, 1)),
        'Pivot': vec3((0, 0, 0)),
        'Bounds': {'$type': 'Box', 'Max': vec4(SHARD_POS), 'Min': vec4(SHARD_POS)},
        'QuestPrefabRefHash': {'$type': 'NodeRef', '$storage': 'uint64', '$value': '0'},
        'UkHash1': {'$type': 'NodeRef', '$storage': 'uint64', '$value': '0'},
        'CookedPrefabData': {'DepotPath': {'$type': 'ResourcePath',
                                           '$storage': 'uint64', '$value': '0'},
                             'Flags': 'Default'},
        # A real entity node's flags and a FINITE streaming distance. The first
        # attempt used a trigger area's (Uk10 288 / Uk11 65280, float-max) and
        # that is one of the two reasons nothing appeared.
        'MaxStreamingDistance': MAX_STREAMING_DISTANCE,
        'UkFloat1': 50,
        'Uk10': 1056,
        'Uk11': 10762,
        'Uk12': 0,
        'Uk13': '0',
        'Uk14': '0',
    }
    return {
        'Header': header('cc_g01_world.streamingsector'),
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
                'level': 1,
                'localInplaceResource': [],
                'nodeData': {
                    'BufferId': '0',
                    'Flags': 4063232,
                    'Type': ('WolvenKit.RED4.Archive.Buffer.worldNodeDataBuffer, '
                             'WolvenKit.RED4, Version=8.20.0.0, Culture=neutral, '
                             'PublicKeyToken=null'),
                    'Data': [data],
                },
                'nodeRefs': [],
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
        'Header': header('cc_g01_world.streamingblock'),
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
                    'level': 1,
                    'numNodeRanges': 1,
                    'questPrefabNodeRef': {'$type': 'NodeRef',
                                           '$storage': 'uint64', '$value': '0'},
                    # THE SHARD'S OWN REACH, not the map. A cube centred on the
                    # node and half a metre wider than the distance it renders
                    # from, so the sector is in range while the shard could be
                    # visible and out of range everywhere else.
                    #
                    # For scale, the vanilla level-1 sector covering this same
                    # cell carries a 613 x 583 x 514 m box, so ~430 m a side is
                    # an ordinary size for a neighbourhood rather than a tight
                    # one. W=1 on both corners, as every shipped descriptor has.
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
    os.makedirs(RAW, exist_ok=True)
    for name, doc in (('cc_g01_world.streamingsector.json', sector()),
                      ('cc_g01_world.streamingblock.json', block())):
        with open(os.path.join(RAW, name), 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(doc, fh, indent=2)
        print('wrote', os.path.join(RAW, name))
    print('shard at', SHARD_POS, '- read on PROXIMITY, see Gig01_Encounter')
