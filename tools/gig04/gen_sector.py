r"""Generates the world files that put the gig's two shards in the world: Stamps's
on the seat of his couch in the alley behind Kabuki Market, and the Tyger
Claws' on the ground behind their van, with the three scanner clues round
it.

  mod\worlds\03_night_city\_compiled\default\cc_g04_world.streamingsector
  mod\worlds\03_night_city\_compiled\default\cc_g04_van.streamingsector
  mod\worlds\03_night_city\_compiled\default\cc_g04_world.streamingblock

ONE SECTOR PER PLACE, each filed in the grid cell it stands in, and one block
naming both: the couch and the bag in one, the van's in the other. The van
itself is the community's (gen_community, VAN_ENTRY).

A copy of tools/gig03/gen_sector.py, re-pointed; that file and
docs/shard-playbook.md carry the account: the game's own shard case
container, lifted whole from a vanilla sector (the committed
tools/gig01/shard_container_node.json), named in the long form, holding this
gig's item. Nothing of the game's is deleted here.
"""
import json
import math
import os
import subprocess
import sys

# questkit is in tools/, one level up from this gig's generators. See
# backlog.md 21.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from questkit import cr2w                                            # noqa: E402

import gig04_config as cfg                                           # noqa: E402
import gen_room                                                      # noqa: E402
import gen_clues                                                     # noqa: E402

_TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(_TOOLS)
RAW = os.path.join(REPO, 'mods', 'gig-04-return-ticket', 'source', 'wkit',
                   'raw', 'mod', 'worlds', '03_night_city', '_compiled', 'default')



def sector_depot(name):
    return chr(92).join(['mod', 'worlds', '03_night_city', '_compiled', 'default',
                         name + '.streamingsector'])


# WHERE THE CONTAINER COMES FROM.
#
# The office desk's own shard is node 527 of `exterior_-4_-23_0_0`, and this
# generator lifts that node and its whole 53-field instance data MECHANICALLY.
# Nothing here is retyped: a copy made by hand is not a copy, which this
# project has proved twice.
#
# Gig 01's manifest deletes that original from the desk; this gig deletes
# nothing of the game's.
CLI = os.path.expandvars(r'%LOCALAPPDATA%\Programs\WolvenKit.CLI\WolvenKit.CLI.exe')
GAME = r'C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077'
VANILLA_ARCHIVE = os.path.join(GAME, 'archive', 'pc', 'content',
                               'basegame_3_nightcity.archive')
VANILLA_SECTOR = 'exterior_-4_-23_0_0.streamingsector'
DESK_NODE = 527
CACHE = os.path.join(_TOOLS, '_vanilla_sector_cache')
# The lifted node, COMMITTED. Written by --refresh, read by every ordinary run,
# never edited by hand. See vanilla_container().
# THE LIFTED VANILLA CONTAINER IS SHARED WITH GIG 01, DELIBERATELY. It is the
# game's own node with all 53 fields of its instance data, and nothing about it
# belongs to a gig: only `itemTDBID`, the position and the name are ours. A
# second copy would be a second thing to keep in step with the vanilla sector it
# came from, and re-extracting it needs the game and WolvenKit for no gain.
#
# `--refresh` still lives in gig 01, which is where the extraction is written
# down. If this file cannot find the JSON, run that one.
SOURCE = os.path.join(_TOOLS, 'gig01', 'shard_container_node.json')

# THE NODE CARRIES A NAME, AND THAT IS WHAT MAKES IT WORK.
#
# Measured 2026-08-22 against a deliberate control: named nodes in a mod sector
# load, unnamed ones are not there at all, eight against three with the two
# kinds standing four metres apart. The long `$/...` form, repeated in the
# sector's own `nodeRefs`. backlog.md 6 and 11.
SHARD_REF = '$/03_night_city/wat_kab/#cc_g04_couch_shard'

# What the container offers. See source/tweaks/shard.yaml, and read its header
# before changing anything about the item: a shard's title and text hang off
# `itemSecondaryAction`, not off any name field.
SHARD_ITEM = 'Items.cc_g04_shard'

# WHERE THEY STAND: gig04_config.BOOTH_SHARD (the couch's seat; its comment
# has the account of the capture that floated).
SHARD_POS = cfg.BOOTH_SHARD
# THE CLAWS' SHARD, on the ground behind their van (gig04_config,
# VAN_SHARD).
VAN_SHARD_REF = '$/03_night_city/wat_lch/#cc_g04_van_shard'
# The shards in the world, as (name, ref, item, position, handle base).
SHARDS = [('cc_g04_shard', SHARD_REF, SHARD_ITEM, SHARD_POS, 2000),
          ('cc_g04_shard_flop', VAN_SHARD_REF, 'Items.cc_g04_shard_flop',
           cfg.VAN_SHARD, 3000)]
# THE CLUES, as (name, ref, position, yaw): gen_clues writes each entity.
CLUES = [(n, '$/03_night_city/wat_lch/#cc_g04_clue_' + n, pos, yaw)
         for n, pos, yaw in cfg.CLUES]
# THE SECTORS: (name, the shards in it, clues). No bag by the stall: his
# one bag is the clue at the van (the design call, 2026-10-14, P6 of the
# dialogue sheet: two bags of his read as a contradiction).
SECTORS = [('cc_g04_world', [SHARDS[0]], []),
           ('cc_g04_van', [SHARDS[1]], CLUES)]
# A sector this generator no longer writes, removed from the raw folder so
# the archive does not keep packing the last copy (gotcha 73's family).
RETIRED = ['cc_g04_flop.streamingsector.json']

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




def cname(v):
    return {'$type': 'CName', '$storage': 'string', '$value': v}


def vec3(p):
    return {'$type': 'Vector3', 'X': p[0], 'Y': p[1], 'Z': p[2]}


def vec4(p, w=0):
    return {'$type': 'Vector4', 'W': w, 'X': p[0], 'Y': p[1], 'Z': p[2]}


def points(shards, clues):
    return [p for _n, _r, _i, p, _b in shards] + [p for _n, _r, p, _y in clues]


def box_corner(pts, sign):
    """The box round everything a sector holds, the shards' reach out from
    the outermost of them."""
    reach = MAX_STREAMING_DISTANCE + STREAM_MARGIN
    pick = max if sign > 0 else min
    return tuple(pick(p[i] for p in pts) + sign * reach for i in range(3))


def header(name):
    return cr2w.header(name)


def refresh_source():
    r"""Re-extract the container node from the game and commit it to SOURCE.

    `python tools\gig01\gen_sector.py --refresh`. Needs the game and WolvenKit;
    an ordinary run needs neither.
    """
    out = os.path.join(CACHE, 'base', 'worlds', '03_night_city', '_compiled',
                       'default', VANILLA_SECTOR + '.json')
    if not os.path.exists(out):
        print('extracting %s, this takes about a minute...' % VANILLA_SECTOR)
        os.makedirs(CACHE, exist_ok=True)
        subprocess.run([CLI, 'unbundle', VANILLA_ARCHIVE, '-o', CACHE,
                        '-w', '*' + VANILLA_SECTOR], capture_output=True)
        raw = out[:-len('.json')]
        if not os.path.exists(raw):
            raise SystemExit('could not extract %s from %s'
                             % (VANILLA_SECTOR, VANILLA_ARCHIVE))
        subprocess.run([CLI, 'convert', 'serialize', raw], capture_output=True)
        if not os.path.exists(out):
            raise SystemExit('WolvenKit did not serialize %s' % raw)

    with open(out, encoding='utf-8-sig') as fh:
        rc = json.load(fh)['Data']['RootChunk']
    inst = [i for i, e in enumerate(rc['nodeData']['Data'])
            if e['NodeIndex'] == DESK_NODE]
    doc = {
        'sector': VANILLA_SECTOR,
        'node': DESK_NODE,
        'instance': inst[0],
        'nodes': len(rc['nodes']),
        'expectedNodes': len(rc['nodeData']['Data']),
        'data': rc['nodes'][DESK_NODE]['Data'],
    }
    with open(SOURCE, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(doc, fh, indent=2)
    print('wrote', SOURCE)
    print('  %s: %d nodes, %d instances'
          % (VANILLA_SECTOR, doc['nodes'], doc['expectedNodes']))


def vanilla_container():
    """The desk's shard node, out of the committed source file.

    THIS DOES NOT NEED THE GAME. `tools/gig01/shard_container_node.json` is
    committed, so a fresh clone regenerates the sector with nothing installed
    and no archive to read. Every generator here is meant to work that way.

    It is still a MECHANICAL copy. The file is written by `--refresh` off the
    shipped sector and never edited by hand.
    """
    if not os.path.exists(SOURCE):
        raise SystemExit(
            '%s is missing. Run: python tools/gig01/gen_sector.py --refresh\n'
            '(that one needs the game and WolvenKit; ordinary runs do not)'
            % os.path.basename(SOURCE))
    with open(SOURCE, encoding='utf-8') as fh:
        doc = json.load(fh)
    print('container lifted from %s node %d (instance %d of %d)'
          % (doc['sector'], doc['node'], doc['instance'], doc['expectedNodes']))
    # THIS GIG DELETES NOTHING, so those two numbers are not wanted in the
    # manifest. They are printed because gig 01 needs them, and because a lift
    # that silently changed which node it took would show up here.
    print('  (gig 01 needs expectedNodes %d / index %d for its deletion; '
          'this gig has no deletion block)'
          % (doc['expectedNodes'], doc['instance']))
    return doc['data']


def renumber(obj, base, counter):
    """Fresh, file-unique HandleIds for the lifted chunk.

    A handle id resolves WITHIN the file, so the vanilla node's ids cannot be
    reused as they stand. The values mean nothing beyond being distinct.
    """
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


def shard_node(van, name, item, base):
    node = json.loads(json.dumps(van))
    node['debugName'] = cname('{%s}' % name)
    # The whole 53-field ShardCaseContainer chunk comes across. WITHOUT IT the
    # object renders as an oversized grey slab and offers nothing: measured
    # 2026-08-22 on a bench slot that omitted it.
    node['instanceData'] = renumber(
        json.loads(json.dumps(van['instanceData'])), base, [0])
    node['instanceData']['Data']['buffer']['Data']['Chunks'][0]['itemTDBID'] = {
        '$type': 'TweakDBID', '$storage': 'string', '$value': item}
    return node


def shard_instance(index, pos, ref):
    return {
        'Id': str(index),
        'NodeIndex': index,
        'Position': vec4(pos),
        # Upright, as the vanilla node has it. It was briefly laid flat and
        # playtesting asked for it back: flat and chip-sized it is a sliver
        # nobody can pick out of a dark office.
        'Orientation': {'$type': 'Quaternion', 'i': 0, 'j': 0, 'k': 0, 'r': 1},
        'Scale': vec3((1, 1, 1)),
        'Pivot': vec3((0, 0, 0)),
        'Bounds': {'$type': 'Box', 'Max': vec4(pos), 'Min': vec4(pos)},
        # THE NAME. An unnamed node does not load at all, and a container on an
        # unnamed node was the whole of backlog.md 6.
        'QuestPrefabRefHash': {'$type': 'NodeRef', '$storage': 'string',
                               '$value': ref},
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


# A CLUE'S NODE: the vanilla clue's own node shape (`worldEntityNode`, no
# instance data; `ma_bls_ina_se1_07_trail` in exterior_39_-27_1_0), named
# in the long form, with an entity node's flags.
def clue_node(name):
    return {
        '$type': 'worldEntityNode',
        'appearanceName': cname('default'),
        'debugName': cname('{cc_g04_clue_%s}' % name),
        'entityLod': 0,
        'entityTemplate': {'DepotPath': {'$type': 'ResourcePath', '$storage': 'string',
                                         '$value': gen_clues.depot(name)},
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


def sector(sector_name, shards, clues, van):
    nodes, datas, refs = [], [], []
    for i, (name, ref, item, pos, base) in enumerate(shards):
        nodes.append({'HandleId': str(i), 'Data': shard_node(van, name, item, base)})
        datas.append(shard_instance(i, pos, ref))
        refs.append({'$type': 'NodeRef', '$storage': 'string', '$value': ref})
    for name, ref, pos, yaw in clues:
        index = len(nodes)
        nodes.append({'HandleId': str(index), 'Data': clue_node(name)})
        inst = shard_instance(index, pos, ref)
        inst['Orientation'] = gen_room.quat_yaw(yaw)
        datas.append(inst)
        refs.append({'$type': 'NodeRef', '$storage': 'string', '$value': ref})
    return {
        'Header': header(sector_name + '.streamingsector'),
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
                    'Data': datas,
                },
                # The names again, which is how a sector declares them.
                'nodeRefs': refs,
                'nodes': nodes,
                'persistentNodeIndex': 0,
                'persistentNodes': [],
                # ONE ENTRY, however many nodes: the room's sector carries
                # sixty nodes under `[0]` and loads. `[0, 1]` here was the
                # first build with the bag, and neither node appeared
                # (playtest 2026-10-01).
                'variantIndices': [0],
                'variantNodes': [],
                # 62, as every shipped sector carries. Writing 0 here is a
                # silent way to get a sector the engine may not read.
                'version': 62,
            },
            'EmbeddedFiles': [],
        },
    }


def descriptor(sector_name, shards, clues):
    pts = points(shards, clues)
    return {
                    '$type': 'worldStreamingSectorDescriptor',
                    'blockIndex': {'$type': 'worldStreamingBlockIndex',
                                   'oup': 'Base', 'rldGridCell': grid_cell(pts[0])},
                    'category': 'Exterior',
                    'data': {'DepotPath': {'$type': 'ResourcePath',
                                           '$storage': 'string',
                                           '$value': sector_depot(sector_name)},
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
                                     'Max': vec4(box_corner(pts, +1), w=1),
                                     'Min': vec4(box_corner(pts, -1), w=1)},
                    'variants': [],
    }


def block():
    return {
        'Header': header('cc_g04_world.streamingblock'),
        'Data': {
            'Version': 195, 'BuildVersion': 0,
            'RootChunk': {
                '$type': 'worldStreamingBlock',
                'cookingPlatform': 'PLATFORM_PC',
                'descriptors': [descriptor(n, sh, cl) for n, sh, cl in SECTORS],
                'index': {'$type': 'worldStreamingBlockIndex',
                          'oup': 'Base', 'rldGridCell': 0},
            },
            'EmbeddedFiles': [],
        },
    }


if __name__ == '__main__':
    if '--refresh' in sys.argv:
        refresh_source()
        raise SystemExit(0)
    os.makedirs(RAW, exist_ok=True)
    for old in RETIRED:
        if os.path.exists(os.path.join(RAW, old)):
            os.remove(os.path.join(RAW, old))
            print('removed the retired', old)
    van = vanilla_container()
    docs = [(n + '.streamingsector.json', sector(n, sh, cl, van))
            for n, sh, cl in SECTORS]
    docs.append(('cc_g04_world.streamingblock.json', block()))
    for name, doc in docs:
        with open(os.path.join(RAW, name), 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(doc, fh, indent=2)
        print('wrote', os.path.join(RAW, name))
    for name, ref, item, pos, _b in SHARDS:
        print('shard at', pos, '- named', ref, '- holding', item)
