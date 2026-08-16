r"""Generates the world files that put the data shard on the office desk.

  mod\worlds\03_night_city\_compiled\default\cc_g01_world.streamingsector
  mod\worlds\03_night_city\_compiled\default\cc_g01_world.streamingblock

The gig's other sector (`mod\negative_balance\world\gig01.*`) holds two quest
markers, is hand-authored, inert, and is not touched here.

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
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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

# Copied from GeneralShadowsFix, an installed world-edit mod that works.
# Identical on all sixteen of its descriptors, so it is a constant.
GRID_CELL = 129182


def cname(v):
    return {'$type': 'CName', '$storage': 'string', '$value': v}


def vec3(p):
    return {'$type': 'Vector3', 'X': p[0], 'Y': p[1], 'Z': p[2]}


def vec4(p, w=0):
    return {'$type': 'Vector4', 'W': w, 'X': p[0], 'Y': p[1], 'Z': p[2]}


def header(name):
    return {'WolvenKitVersion': '8.20.0', 'WKitJsonVersion': '0.0.9',
            'GameVersion': 2310, 'DataType': 'CR2W', 'ArchiveFileName': name}


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
        'MaxStreamingDistance': 164.710114,
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
                    # +-5000 with W=1, exactly as the working mod writes it.
                    # Night City runs to about +-3000, so this covers it - and
                    # unlike float-max it is a box the engine can reason about.
                    'streamingBox': {'$type': 'Box',
                                     'Max': vec4((5000, 5000, 5000), w=1),
                                     'Min': vec4((-5000, -5000, -5000), w=1)},
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
        with open(os.path.join(RAW, name), 'w', encoding='utf-8') as fh:
            json.dump(doc, fh, indent=2)
        print('wrote', os.path.join(RAW, name))
    print('shard at', SHARD_POS, '- read on PROXIMITY, see Gig01_Encounter')
