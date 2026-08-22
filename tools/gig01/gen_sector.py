r"""Generates the world files that put the data shard on the office desk.

  mod\worlds\03_night_city\_compiled\default\cc_g01_world.streamingsector
  mod\worlds\03_night_city\_compiled\default\cc_g01_world.streamingblock

WHAT THIS SHIPS: a `worldEntityNode` carrying the game's own shard case
container, holding the gig's own item, standing where the desk's original shard
stood. It renders, it offers "F Take / R Read", and reading it opens the gig's
note. The `.archive.xl` deletes the original so the desk carries one shard.

THE THREE THINGS THAT MAKE IT WORK, each measured against a control on
2026-08-22 after this file spent months saying a prompt was impossible. Full
account in docs/backlog.md 6.

  * THE NODE HAS A NAME. `QuestPrefabRefHash` as a full `$/03_night_city/...`
    path, repeated in the sector's own `nodeRefs`. This is not decoration: a
    node without one DOES NOT LOAD AT ALL. Eight named objects were found and
    three unnamed ones were absent, standing four metres apart in the same row.
    A short-form name is enough to load, but only the long form resolves, so
    the long form is what ships.
  * THE INSTANCE DATA COMES ACROSS WHOLE. All 53 fields of the vanilla node's
    `ShardCaseContainer` chunk, lifted mechanically by this file rather than
    retyped. A slot that omitted it rendered an oversized grey slab and offered
    nothing.
  * THE ITEM'S TEXT HANGS OFF `itemSecondaryAction`, not off any name field.
    See source/tweaks/shard.yaml, which carries that finding in full.

What turned out NOT to matter, each with its own bench slot: `appearanceName`,
`sourcePrefabHash`, `Pivot`, the vanilla `MaxStreamingDistance`, the sector's
`level`, area loot, and writing a name onto the container's own instance data.

WHAT WAS RULED OUT EARLIER AND STAYS RULED OUT:

  * `DynamicEntitySystem` + `templatePath` attaches an entity and never renders
    its mesh. It is an NPC/device spawner, not a prop placer.
  * `exEntitySpawner.Spawn` is a Codeware native for CET LUA ONLY.
    `unresolved reference` from redscript.
  * A mod `.ent` may only name an entity class the game already ships.
  * ArchiveXL can delete and mutate nodes in a shipped sector but not ADD to
    one, so a mod's own sector is the only place a new node can go.
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

_TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(_TOOLS)
RAW = os.path.join(REPO, 'mods', 'gig-01-negative-balance', 'source', 'wkit',
                   'raw', 'mod', 'worlds', '03_night_city', '_compiled', 'default')

SECTOR_DEPOT = r'mod\worlds\03_night_city\_compiled\default\cc_g01_world.streamingsector'
# WHERE THE CONTAINER COMES FROM.
#
# The office desk's own shard is node 527 of `exterior_-4_-23_0_0`, and this
# generator lifts that node and its whole 53-field instance data MECHANICALLY.
# Nothing here is retyped: a copy made by hand is not a copy, which this
# project has proved twice.
#
# The `.archive.xl` deletes the original (instance 591 of 1242, and both of
# those numbers count instances rather than nodes, gotcha 47), so the desk ends
# up carrying one shard: ours.
CLI = os.path.expandvars(r'%LOCALAPPDATA%\Programs\WolvenKit.CLI\WolvenKit.CLI.exe')
GAME = r'C:\Program Files (x86)\Steam\steamapps\common\Cyberpunk 2077'
VANILLA_ARCHIVE = os.path.join(GAME, 'archive', 'pc', 'content',
                               'basegame_3_nightcity.archive')
VANILLA_SECTOR = 'exterior_-4_-23_0_0.streamingsector'
DESK_NODE = 527
CACHE = os.path.join(_TOOLS, '_vanilla_sector_cache')
# The lifted node, COMMITTED. Written by --refresh, read by every ordinary run,
# never edited by hand. See vanilla_container().
SOURCE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      'shard_container_node.json')

# THE NODE CARRIES A NAME, AND THAT IS WHAT MAKES IT WORK.
#
# Measured 2026-08-22 against a deliberate control: named nodes in a mod sector
# load, unnamed ones are not there at all, eight against three with the two
# kinds standing four metres apart. The long `$/...` form, repeated in the
# sector's own `nodeRefs`. backlog.md 6 and 11.
SHARD_REF = '$/03_night_city/#c_santo_domingo/arroyo/#cc_g01_shard_container'

# What the container offers. See source/tweaks/shard.yaml, and read its header
# before changing anything about the item: a shard's title and text hang off
# `itemSecondaryAction`, not off any name field.
SHARD_ITEM = 'Items.cc_g01_shard'

# THE VANILLA SHARD'S OWN SPOT ON THAT DESK, read out of the sector's nodeData
# rather than captured with a look-at ray. Ours stands exactly where the game's
# stood, which is what a shard on that desk should look like.
#
# Keep in step with CCG01Shard.ObjectSpot() in Gig01_Shard.reds.
SHARD_POS = (-244.931305, -1454.17786, 15.3999996)

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
    print('  the .archive.xl must say expectedNodes: %d and index: %d'
          % (doc['expectedNodes'], doc['instance']))


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
    print('  the .archive.xl must say expectedNodes: %d and index: %d'
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


def sector():
    van = vanilla_container()

    node = json.loads(json.dumps(van))
    node['debugName'] = cname('{cc_g01_shard}')
    # The whole 53-field ShardCaseContainer chunk comes across. WITHOUT IT the
    # object renders as an oversized grey slab and offers nothing: measured
    # 2026-08-22 on a bench slot that omitted it.
    node['instanceData'] = renumber(
        json.loads(json.dumps(van['instanceData'])), 2000, [0])
    node['instanceData']['Data']['buffer']['Data']['Chunks'][0]['itemTDBID'] = {
        '$type': 'TweakDBID', '$storage': 'string', '$value': SHARD_ITEM}

    data = {
        'Id': '0',
        'NodeIndex': 0,
        'Position': vec4(SHARD_POS),
        # Upright, as the vanilla node has it. It was briefly laid flat and
        # playtesting asked for it back: flat and chip-sized it is a sliver
        # nobody can pick out of a dark office.
        'Orientation': {'$type': 'Quaternion', 'i': 0, 'j': 0, 'k': 0, 'r': 1},
        'Scale': vec3((1, 1, 1)),
        'Pivot': vec3((0, 0, 0)),
        'Bounds': {'$type': 'Box', 'Max': vec4(SHARD_POS), 'Min': vec4(SHARD_POS)},
        # THE NAME. An unnamed node does not load at all, and a container on an
        # unnamed node was the whole of backlog.md 6.
        'QuestPrefabRefHash': {'$type': 'NodeRef', '$storage': 'string',
                               '$value': SHARD_REF},
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
                # The name again, which is how a sector declares it.
                'nodeRefs': [{'$type': 'NodeRef', '$storage': 'string',
                              '$value': SHARD_REF}],
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
    if '--refresh' in sys.argv:
        refresh_source()
        raise SystemExit(0)
    os.makedirs(RAW, exist_ok=True)
    for name, doc in (('cc_g01_world.streamingsector.json', sector()),
                      ('cc_g01_world.streamingblock.json', block())):
        with open(os.path.join(RAW, name), 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(doc, fh, indent=2)
        print('wrote', os.path.join(RAW, name))
    print('shard at', SHARD_POS, '- named', SHARD_REF)
    print('holding', SHARD_ITEM, '- read with [F]/[R], see Gig01_Shard.reds')
