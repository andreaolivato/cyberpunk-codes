r"""Build a community a mod ships: the sectors, the registry and the block.

This is `docs/gotchas.md` 66 as code. It was lifted out of
`tools/gig01/gen_community.py` on 2026-08-25, unchanged, when a SECOND community
was needed (the North Oak estate detail) and the one working recipe had to serve
both. `gen_community.py` remains where the reasoning is written down; this file
is the shape.

The recipe, all six parts, and none of them optional:

  1. ONE name per community. The area node carries it, the sector registers it,
     `sourceObjectId` is its FNV1a64 minus '#', and the registry item repeats
     that hash.
  2. A `worldCommunityRegistryNode` in an AlwaysLoaded level-1 sector with a
     +-99999 box, unnamed uint64 instance, ranges 17.32 / 1e8, uk10 32, uk11 512.
  3. The `_Streamable` area node TOGETHER WITH its AI spots, in their own
     AlwaysLoaded level-1 sector, small local box, grid cell 0.
  4. Every ref rooted `$/mod/<sector>/#<name>`, never `$/03_night_city/`.
  5. `appearances` NON-EMPTY.
  6. ONE time period per phase.

TWO COMMUNITIES ARE TWO SEPARATE STACKS, not two items in one registry. Each
gets its own pair of sectors and its own streaming block. Vanilla does put many
communities in one registry, and doing that here would mean rewriting the file
that already works for the sake of one that does not yet. The cost is one extra
always-loaded sector whose whole content is a single node.

It also keeps a quest phase honest. A phase switches a community by NodeRef, so
two communities can be switched independently without naming entries one at a
time, and the gig cannot reach something it does not own (gotcha 73).
"""
import math

from . import area
from . import cr2w

# Personal Mechanics' own instance values, and the only ones a mod's community
# has ever been seen to work with.
WB = dict(maxdist=120.0, ukfloat=100.0, uk10=1024, uk11=512)

B = chr(92)


def depot(*parts):
    r"""A depot path is BUILT, never typed: `\w`, `\a`, `\0` and `\t` are all
    eaten by something between here and the file. See docs/gotchas.md 28."""
    return B.join(parts)


def fnv1a64(text):
    h = 14695981039346656037
    for byte in text.encode('utf-8'):
        h ^= byte
        h = (h * 1099511628211) % (1 << 64)
    return h


def node_id(node_ref):
    """`worldGlobalNodeID.hash` for a NodeRef: FNV1a64 of it with '#' removed.

    Measured against shipped data twice, and it is gotcha 62. A community's
    identity IS this hash of its own name, which is why part 1 of the recipe
    insists there is only one name.
    """
    return str(fnv1a64(node_ref.replace('#', '')))


def cname(v):
    return {'$type': 'CName', '$storage': 'string', '$value': v if v else 'None'}


def vec3(p):
    return {'$type': 'Vector3', 'X': p[0], 'Y': p[1], 'Z': p[2]}


def vec4(p, w=0):
    return {'$type': 'Vector4', 'W': w, 'X': p[0], 'Y': p[1], 'Z': p[2]}


def noderef_str(v):
    return {'$type': 'NodeRef', '$storage': 'string', '$value': v}


NOREF = {'$type': 'NodeRef', '$storage': 'uint64', '$value': '0'}
NOPATH = {'DepotPath': {'$type': 'ResourcePath', '$storage': 'uint64',
                        '$value': '0'}, 'Flags': 'Default'}


def yaw_quat(degrees):
    """A rotation about Z, which is how a spot node is aimed.

    THIS IS THE FACING, and an identity quaternion here is why Hoshino faced the
    wrong way in the first playtest of the gig build. Settled by dumping a
    vanilla couch spot node by node (`exterior_-19_-17_0_0`,
    `generic__sit_couch__sit_around__004`): its INSTANCE carries a real
    quaternion, k 0.0087 / r -0.99996, about 180 degrees.

    `AISpotPersistentData.yaw` is filled in with the same number. Which of the
    two the game reads is not established; they agree, so it does not matter,
    and disagreeing would be the worst of both. Gotcha 70.
    """
    half = math.radians(degrees) / 2.0
    return {'$type': 'Quaternion', 'i': 0, 'j': 0,
            'k': math.sin(half), 'r': math.cos(half)}


class Entry(object):
    """One person: which record, where, facing which way, in what pose."""

    def __init__(self, name, record, appearance, pos, yaw, workspot,
                 markings=None, spot_name=None, route=None):
        self.name = name
        self.record = record
        self.appearance = appearance
        self.workspot = workspot
        self.markings = markings or []
        # ONE ENTRY MAY HAVE SEVERAL SPOTS, and that is how vanilla walks an
        # NPC around. `communityPhaseTimePeriod.spotNodeRefs` is a list and
        # `isSequence` says whether to take them in order; of 32669 time periods
        # in the cached registries, 1780 carry more than one spot and 964 set
        # isSequence. `#q112_ws_oda_patrol_002` upward is nine of them on one
        # entry, and Panam's four `search_routine` spots are a sequence.
        #
        # `route` is [(pos, yaw), ...]. One point is a post; several are a beat.
        self.points = list(route) if route else [(pos, yaw)]
        # The first point is where he starts, and it is what the single-spot
        # callers have always meant by pos and yaw.
        self.pos = self.points[0][0]
        self.yaw = self.points[0][1]
        # The AI spot's own name. It is derived from the entry's unless one is
        # given, and the only reason to give one is to keep a community that
        # already ships byte-identical through a refactor: the name is hashed
        # into the spot's id, so renaming it rewrites the file for no gain.
        self.spot_name = spot_name

    def patrols(self):
        return len(self.points) > 1


class Community(object):
    """One community: its two sectors, its entries, and its streaming block.

    `spawnset` is the string a SCENE asks for (gotcha 69), and it is None for a
    community no scene has to acquire a body from.
    """

    WORLD = ('mod', 'worlds', '03_night_city', '_compiled', 'default')

    # THE AREA NODE'S CLASS, and BOTH VALUES SPAWN. Measured 2026-08-25.
    #
    # `_Streamable` is what part 3 of gotcha 66 says a mod writes, and seven
    # bench runs established it. The plain class was then shipped at the
    # industrial park to answer a question about security areas, and thirty
    # guards appeared there in play, so a mod's own sector spawns from either.
    #
    # The question it was shipped to answer is closed and the answer is no. Of
    # the 32 `CommunityProxyPS` connections vanilla ships, 21 resolve inside the
    # cached sectors and all 21 point at the plain class rather than at
    # `_Streamable`, which looked like the reason a mod's security area could
    # not alert a mod's community. It is not: the compound ran the plain class
    # WITH an area wired to it and the guards still did nothing. What separates
    # vanilla's alertable communities is that they sit in the GAME'S OWN
    # `always_loaded` sectors, which a mod cannot add to. Gotcha 80.
    #
    # So this parameter no longer decides anything. A new site should leave it
    # alone and take `_Streamable`, because that is the value with the bench
    # behind it. The compound keeps the plain class rather than being rewritten
    # to match: it is a shipped, playtested sector, and changing it would mean
    # regenerating a working file to prove something already proven.
    PLAIN = 'worldCompiledCommunityAreaNode'
    STREAMABLE = 'worldCompiledCommunityAreaNode_Streamable'

    def __init__(self, name, entries, spawnset=None, phase='default',
                 period='Day', extra=None, area_class=None):
        self.name = name
        self.entries = entries
        # NODES THAT RIDE IN THE SAME SECTOR, as (node, position, ref) triples.
        #
        # A security area belongs in the same sector as the community it
        # alerts: the wiki's one constraint on the whole arrangement is that the
        # community, the area and the system are in one group, and a sector is
        # what a group exports to. Passing them here rather than shipping a
        # third sector also keeps them inside the streaming box that is already
        # derived from the spots.
        self.extra = list(extra or [])
        self.area_class = area_class or self.STREAMABLE
        self.spawnset = spawnset
        self.phase = phase
        self.period = period

        self.sector = name
        self.reg_sector = name + '_reg'
        self.sector_depot = depot(*(self.WORLD +
                                    (self.sector + '.streamingsector',)))
        self.reg_depot = depot(*(self.WORLD +
                                 (self.reg_sector + '.streamingsector',)))

        self.community_ref = self.ref(self.sector, name + '_com')
        self.registry_ref = self.ref(self.reg_sector, name + '_registry')
        self.community_id = node_id(self.community_ref)

    @staticmethod
    def ref(sector, item):
        """`$/mod/<sector>/#<name>`, and part 4 of the recipe. Eleven bench runs
        used `$/03_night_city/...` and none of them spawned anybody."""
        return '$/mod/' + sector + '/#' + item

    def spots(self, entry):
        """The AI spot node refs for one entry, one per point on its route.

        A one-point entry keeps the name it has always had, so adding routes to
        this file does not rewrite the two communities that already ship: the
        name is hashed into the spot's id.
        """
        base = entry.spot_name or (self.name + '_' + entry.name)
        if not entry.patrols():
            return [self.ref(self.sector, base)]
        return [self.ref(self.sector, '%s_%02d' % (base, i + 1))
                for i in range(len(entry.points))]

    def spot(self, entry):
        """Where the entry starts. Kept because most callers want one ref."""
        return self.spots(entry)[0]

    # ------------------------------------------------------------------ nodes
    def ai_spot_node(self, label, workspot, markings):
        """World Builder's spot, key for key.

        Its exporter writes ONLY `isWorkspotInfinite`, `isWorkspotStatic`,
        `markings` and the `AIActionSpot` with just the resource; everything
        else falls to class defaults. Infinite matters: a finite workspot is one
        the NPC finishes and then walks away from, which for somebody who is
        supposed to be standing where the story put him is the whole thing
        going wrong.
        """
        return {
            '$type': 'worldAISpotNode',
            'debugName': cname('{%s}' % label),
            'isWorkspotInfinite': 1,
            'isWorkspotStatic': 0,
            'markings': [cname(m) for m in markings],
            'spot': {'HandleId': '1', 'Data': {
                '$type': 'AIActionSpot',
                'resource': {'DepotPath': {'$type': 'ResourcePath',
                                           '$storage': 'string',
                                           '$value': workspot},
                             'Flags': 'Soft'},
            }},
        }

    def marker_node(self, label):
        """`worldStaticMarkerNode`: a named point, and nothing else.

        THE WIKI'S OWN ANSWER to "how do I aim a scene or a quest node at a
        place rather than at a person". Object Spawner's node reference, on
        Static Marker: "Places a static marker node. Useful if you need a
        NodeRef as a reference point. Usually best placed in an AlwaysLoaded
        Sector." The custom fast travel guide then walks the same recipe as
        numbered steps and treats the always-loaded sector as an ordinary
        requirement. `map-pins-playbook.md` carries both, and the game's own
        always-loaded sectors hold 4,500 of these and no entity nodes at all.

        Field for field off `{mikoshi_cs_perf_test}`, node 0 of
        always_loaded_0, minus everything that falls to a class default. The
        inner `worldSpawnPointMarker` owns a HandleId of its own, which is the
        second of the playbook's two traps: handles are file-wide, so this one
        is a placeholder that `renumber_handles` rewrites. The first trap,
        `variantIndices` being `[0]` however many nodes there are, is already
        handled in `sector()`.
        """
        return {
            '$type': 'worldStaticMarkerNode',
            'data': {'HandleId': '1', 'Data': {'$type': 'worldSpawnPointMarker',
                                               'type': 0}},
            'debugName': cname('{%s}' % label),
        }

    def area_node(self):
        """`worldCompiledCommunityAreaNode_Streamable`: the plain cooked class
        plus `streamingDistance`. The cooked one is what the game's own cooker
        emits into always_loaded; the streamable one is what a mod writes, and
        seven bench runs were spent on that difference."""
        node = {
            '$type': self.area_class,
            'area': {'HandleId': '1', 'Data': {
                '$type': 'communityArea',
                'entriesData': [{
                    '$type': 'communityCommunityEntrySpotsData',
                    'entryName': cname(e.name),
                    'phasesData': [{
                        '$type': 'communityCommunityEntryPhaseSpotsData',
                        'entryPhaseName': cname(self.phase),
                        'timePeriodsData': [{
                            '$type': 'communityCommunityEntryPhaseTimePeriodData',
                            'isSequence': 1 if e.patrols() else 0,
                            'periodName': cname(self.period),
                            'spotNodeIds': [{'$type': 'worldGlobalNodeID',
                                             'hash': node_id(ref)}
                                            for ref in self.spots(e)],
                        }],
                    }],
                } for e in self.entries],
            }},
            'debugName': cname('{%s_com}' % self.name),
            'isHostOnly': 0,
            'isVisibleInGame': 1,
            'proxyScale': None,
            # THE JOIN, and it is the hash of this node's OWN name.
            'sourceObjectId': {'$type': 'entEntityID', 'hash': self.community_id},
            'sourcePrefabHash': '0',
            'streamingDistance': 0,
            'tag': 'None',
            'tagExt': 'None',
        }
        # `streamingDistance` belongs to the streamable class only. The plain
        # one does not have the field and WolvenKit refuses a node carrying a
        # field its class does not declare.
        if self.area_class == self.PLAIN:
            node.pop('streamingDistance', None)
        return node

    def registry_node(self):
        """`worldCommunityRegistryNode`, World Builder's shape key for key.

        Its import script writes ONLY `workspotsPersistentData` and
        `communitiesData` onto a default skeleton, so `crowdCreationRegistry`
        stays null and the debug name is the export's literal node name. Bench
        runs 7 to 9 filled those with vanilla-shaped values and spawned nobody.

        `spawnSetNameToCommunityID` is the one thing added to that shape, and it
        is what a scene resolves through. World Builder leaves it empty because
        a World Builder community is scenery.
        """
        spawnsets = []
        if self.spawnset:
            spawnsets.append({
                '$type': 'gameCommunitySpawnSetNameToIDEntry',
                'communityId': {'$type': 'gameCommunityID',
                                'entityId': {'$type': 'entEntityID',
                                             'hash': self.community_id}},
                # A CName, and vanilla writes the '#' INTO it.
                'nameReference': cname(self.spawnset),
            })
        return {
            '$type': 'worldCommunityRegistryNode',
            'communitiesData': [{
                '$type': 'worldCommunityRegistryItem',
                'communityAreaType': 'Regular',
                'communityId': {'$type': 'gameCommunityID',
                                'entityId': {'$type': 'entEntityID',
                                             'hash': self.community_id}},
                'entriesInitialState': [{
                    '$type': 'worldCommunityEntryInitialState',
                    # STATES INTENT AND DOES NOTHING. Bench run 14: a mod's
                    # community spawns its entries on save load whatever this
                    # says. The quest phase is what keeps them away.
                    'entryActiveOnStart': 0,
                    'entryName': cname(e.name),
                    'initialPhaseName': cname(self.phase),
                } for e in self.entries],
                'template': {'HandleId': '2', 'Data': {
                    '$type': 'communityCommunityTemplateData',
                    'entries': [{'HandleId': str(10 + i), 'Data': {
                        '$type': 'communitySpawnEntry',
                        'characterRecordId': {'$type': 'TweakDBID',
                                              '$storage': 'string',
                                              '$value': e.record},
                        'entryName': cname(e.name),
                        'phases': [{'HandleId': str(100 + i), 'Data': {
                            '$type': 'communitySpawnPhase',
                            # NEVER EMPTY. Recipe part 5, and eleven runs.
                            'appearances': [cname(e.appearance)],
                            'phaseName': cname(self.phase),
                            # ONE period. Recipe part 6.
                            'timePeriods': [{
                                '$type': 'communityPhaseTimePeriod',
                                'hour': self.period,
                                # IN ORDER when there is a route to walk. Read
                                # off Panam's `search_routine` and Oda's
                                # `patrol` entries; see Entry.
                                'isSequence': 1 if e.patrols() else 0,
                                'markings': [],
                                'quantity': 1,
                                'spotNodeRefs': [noderef_str(ref)
                                                 for ref in self.spots(e)],
                            }],
                        }}],
                    }} for i, e in enumerate(self.entries)],
                }},
            }],
            'crowdCreationRegistry': None,
            'debugName': cname('registry'),
            'isHostOnly': 0,
            'isVisibleInGame': 1,
            'proxyScale': None,
            'representsCrowd': 0,
            'sourcePrefabHash': '0',
            'spawnSetNameToCommunityID': {
                '$type': 'gameCommunitySpawnSetNameToID',
                'entries': spawnsets,
            },
            'tag': 'None',
            'tagExt': 'None',
            # ONE PER SPOT, not one per entry: a route has a record for every
            # point on it.
            'workspotsPersistentData': [{
                '$type': 'AISpotPersistentData',
                'globalNodeId': {'$type': 'worldGlobalNodeID',
                                 'hash': node_id(ref)},
                'isEnabled': 1,
                # FixedPoint: Bits is the metre value times 131072, checked on
                # all three axes against a vanilla spot.
                'worldPosition': {'$type': 'WorldPosition',
                                  'x': {'$type': 'FixedPoint',
                                        'Bits': int(pos[0] * 131072)},
                                  'y': {'$type': 'FixedPoint',
                                        'Bits': int(pos[1] * 131072)},
                                  'z': {'$type': 'FixedPoint',
                                        'Bits': int(pos[2] * 131072)}},
                'yaw': yaw,
            } for e in self.entries
              for ref, (pos, yaw) in zip(self.spots(e), e.points)],
        }

    # ---------------------------------------------------------------- sectors
    def community_sector(self):
        """The area node and the spots, together, in their own sector. Part 3.

        The box is generous around the spots rather than tight: vanilla's own
        community areas are tens of metres across, and a spot outside its area's
        box is an entry that was never viable (bench run 7).
        """
        nodes, instances, refs = [], [], []
        for e in self.entries:
            for spot, (pos, yaw) in zip(self.spots(e), e.points):
                idx = len(nodes)
                nodes.append(self.ai_spot_node(spot.rsplit('#', 1)[1],
                                               e.workspot, e.markings))
                instances.append(instance(idx, pos, spot, WB['maxdist'],
                                          WB['ukfloat'], WB['uk10'],
                                          WB['uk11'], yaw=yaw))
                refs.append(spot)
        pts = [pos for e in self.entries for pos, _yaw in e.points]
        lo = [min(p[i] for p in pts) for i in range(3)]
        hi = [max(p[i] for p in pts) for i in range(3)]
        centre = tuple((lo[i] + hi[i]) / 2.0 for i in range(3))
        span = tuple(max(hi[i] - lo[i], 10.0) + 40.0 for i in range(3))
        idx = len(nodes)
        nodes.append(self.area_node())
        instances.append(instance(idx, centre, self.community_ref,
                                  WB['maxdist'], WB['ukfloat'], WB['uk10'],
                                  WB['uk11'], scale=span))
        refs.append(self.community_ref)
        for extra in self.extra:
            # (node, pos, ref, inst_args) or, with a facing, a fifth item.
            node, pos, ref, inst_args = extra[:4]
            extra_yaw = extra[4] if len(extra) > 4 else 0.0
            # A fifth instance argument is Uk12, which every vanilla trigger
            # area instance carries as 1 and everything else here as 0.
            inst_args = list(inst_args)
            uk12 = inst_args[4] if len(inst_args) > 4 else 0
            idx = len(nodes)
            nodes.append(node)
            instances.append(instance(idx, pos, ref, *inst_args[:4], yaw=extra_yaw,
                                      uk12=uk12))
            refs.append(ref)
        return sector(self.sector + '.streamingsector', nodes, instances, refs)

    def registry_sector(self):
        """The registry node alone. Recipe part 2.

        Its instance is UNNAMED: World Builder's export leaves `nodeRef` empty
        and its import script hashes the instance JSON into `QuestPrefabRefHash`
        as a bare uint64 registered nowhere, so any stable nonzero number is
        that shape.
        """
        inst = instance(0, (0, 0, 0), self.registry_ref, 17.320507, 99999999,
                        32, 512)
        inst['QuestPrefabRefHash'] = {'$type': 'NodeRef', '$storage': 'uint64',
                                      '$value': node_id(self.registry_ref)}
        return sector(self.reg_sector + '.streamingsector',
                      [self.registry_node()], [inst], [])

    def streaming_box(self, half=200.0):
        """The local box, DERIVED from the spots rather than given.

        A box written around one hand-picked point is a box that stops
        containing the spots the moment an entry is added outside it, and a spot
        outside its box is a body that never streams in. In game that is
        indistinguishable from a community that does not work at all, so it is
        computed and then checked (`self_check`).
        """
        pts = [pos for e in self.entries for pos, _yaw in e.points]
        pts += [e[1] for e in self.extra]
        lo = tuple(min(p[i] for p in pts) - half for i in range(3))
        hi = tuple(max(p[i] for p in pts) + half for i in range(3))
        return lo, hi

    def block(self):
        """One block, both sectors. The registry's box is the whole map and the
        community's is local, which is the pairing Personal Mechanics ships."""
        lo, hi = self.streaming_box()
        return {
            'Header': cr2w.header(self.sector + '.streamingblock'),
            'Data': {'Version': 195, 'BuildVersion': 0, 'RootChunk': {
                '$type': 'worldStreamingBlock',
                'cookingPlatform': 'PLATFORM_PC',
                'descriptors': [
                    descriptor(self.reg_depot, (-99999.0,) * 3, (99999.0,) * 3),
                    descriptor(self.sector_depot, lo, hi),
                ],
                'index': {'$type': 'worldStreamingBlockIndex', 'oup': 'Base',
                          'rldGridCell': 0},
            }, 'EmbeddedFiles': []},
        }

    def block_path(self):
        """What goes in the .archive.xl under `streaming: blocks:`."""
        return depot(*(self.WORLD + (self.sector + '.streamingblock',)))

    # ------------------------------------------------------------- self-check
    def self_check(self, com, reg):
        """The pieces must agree, and nothing in the game says so if they do not.

        Every one of these caught a real fault on the bench, and each cost at
        least one test session before it was written down.
        """
        problems = []
        com_root = com['Data']['RootChunk']
        reg_root = reg['Data']['RootChunk']

        named = {e['QuestPrefabRefHash']['$value']
                 for e in com_root['nodeData']['Data']}
        if self.community_ref not in named:
            problems.append('the area node instance is not named %s'
                            % self.community_ref)
        for e in self.entries:
            for ref in self.spots(e):
                if ref not in named:
                    problems.append('the spot instance is not named %s' % ref)
        registered = {r['$value'] for r in com_root['nodeRefs']}
        if self.community_ref not in registered:
            problems.append('the community name is not in the sector nodeRefs')

        area = [n['Data'] for n in com_root['nodes']
                if n['Data']['$type'].startswith(
                    'worldCompiledCommunityAreaNode')][0]
        if area['sourceObjectId']['hash'] != self.community_id:
            problems.append('sourceObjectId is not the hash of the community name')

        registry = reg_root['nodes'][0]['Data']
        item = registry['communitiesData'][0]
        if item['communityId']['entityId']['hash'] != self.community_id:
            problems.append('the registry item points at a different community')
        for spawn in item['template']['Data']['entries']:
            phase = spawn['Data']['phases'][0]['Data']
            who = spawn['Data']['entryName']['$value']
            if not phase['appearances']:
                problems.append('appearances is EMPTY on %s, which is recipe '
                                'part 5 and eleven failed bench runs' % who)
            if len(phase['timePeriods']) != 1:
                problems.append('more than one time period on %s, which is '
                                'recipe part 6' % who)
        spot_ids = {w['globalNodeId']['hash']
                    for w in registry['workspotsPersistentData']}
        for e in self.entries:
            for ref in self.spots(e):
                if node_id(ref) not in spot_ids:
                    problems.append('%s has no AISpotPersistentData record'
                                    % ref)
        if self.spawnset:
            names = {x['nameReference']['$value']
                     for x in registry['spawnSetNameToCommunityID']['entries']}
            if self.spawnset not in names:
                problems.append('%s is not registered as a spawn set, so no '
                                'scene can acquire a body' % self.spawnset)

        # EVERY NAME UNIQUE. Two entries sharing a name is one entry the spawner
        # can never be asked about separately, and nothing reports it.
        seen = set()
        for e in self.entries:
            if e.name in seen:
                problems.append('two entries are both called %s' % e.name)
            seen.add(e.name)

        # EVERY SPOT INSIDE THE BLOCK'S BOX, checked rather than assumed. See
        # streaming_box for what being outside it looks like in game.
        lo, hi = self.streaming_box()
        for e in self.entries:
            for pos, _yaw in e.points:
                if any(pos[i] < lo[i] or pos[i] > hi[i] for i in range(3)):
                    problems.append('%s is outside the streaming box' % e.name)

        for root in (com_root, reg_root):
            handles = []

            def walk(obj):
                if isinstance(obj, dict):
                    if 'HandleId' in obj:
                        handles.append(obj['HandleId'])
                    for v in obj.values():
                        walk(v)
                elif isinstance(obj, list):
                    for v in obj:
                        walk(v)

            walk(root)
            if len(handles) != len(set(handles)):
                problems.append('duplicate HandleId in a sector')
        return problems

    def files(self):
        """(filename, document) for everything this community ships.

        Self-checked here rather than by the caller, so a generator cannot write
        a community that does not agree with itself by forgetting to ask.
        """
        com, reg = self.community_sector(), self.registry_sector()
        faults = self.self_check(com, reg)
        if faults:
            for fault in faults:
                print('SELF-CHECK: ' + fault)
            raise SystemExit('the community %s does not agree with itself; '
                             'nothing written' % self.name)
        return [(self.sector + '.streamingsector.json', com),
                (self.reg_sector + '.streamingsector.json', reg),
                (self.sector + '.streamingblock.json', self.block())]


# -------------------------------------------------------------- shared pieces
def crowd_null_area_node(label, points, height=4.0):
    """A `worldCrowdNullAreaNode`: the crowd system spawns nobody inside it.

    Read off `{cs_crowd_null}` in exterior_-24_16_0_0 (2026-09-04). The outline
    is written by questkit.area, which carries the buffer format; this node
    keeps the unit square that vanilla ships in its `points` list.
    `permanentlyEnabledByDefault: 0` means a quest turns it on:
    questgraph.add_crowd_null_area.
    """
    return {
        '$type': 'worldCrowdNullAreaNode',
        'color': {'$type': 'Color', 'Alpha': 0, 'Blue': 0, 'Green': 0, 'Red': 0},
        'debugName': cname('{%s}' % label),
        'IsForBlockade': 0,
        'isHostOnly': 0,
        'isVisibleInGame': 1,
        'outline': area.outline(points, height, points=area.UNIT_SQUARE),
        'permanentlyEnabledByDefault': 0,
    }


def instance(index, pos, node_ref, max_dist, uk_float, uk10, uk11,
             scale=(1, 1, 1), yaw=0.0, uk12=0):
    return {
        'Id': '0',
        'NodeIndex': index,
        'Position': vec4(pos),
        'Orientation': yaw_quat(yaw),
        'Scale': vec3(scale),
        'Pivot': vec3((0, 0, 0)),
        'Bounds': {'$type': 'Box', 'Max': vec4(pos), 'Min': vec4(pos)},
        'QuestPrefabRefHash': noderef_str(node_ref),
        'UkHash1': NOREF,
        'CookedPrefabData': NOPATH,
        'MaxStreamingDistance': max_dist,
        'UkFloat1': uk_float,
        'Uk10': uk10,
        'Uk11': uk11,
        'Uk12': uk12,
        'Uk13': '0',
        'Uk14': '0',
    }


def renumber_handles(obj, counter):
    """File-wide-unique HandleIds, in document order.

    HANDLE IDS ARE FILE-WIDE, not per node. WolvenKit then fails inside the
    CName converter of the NEXT node and reports that node's `$type` line, which
    reads like a wrong class name and is nothing of the sort.
    """
    if isinstance(obj, dict):
        if 'HandleId' in obj:
            obj['HandleId'] = str(counter[0])
            counter[0] += 1
        for value in obj.values():
            renumber_handles(value, counter)
    elif isinstance(obj, list):
        for value in obj:
            renumber_handles(value, counter)
    return obj


def sector(name, nodes, instances, refs):
    root = {
        '$type': 'worldStreamingSector',
        'category': 'AlwaysLoaded',
        'cookingPlatform': 'PLATFORM_PC',
        'externInplaceResource': {
            'DepotPath': {'$type': 'ResourcePath', '$storage': 'uint64',
                          '$value': '0'}, 'Flags': 'Soft'},
        'level': 1,
        'localInplaceResource': [],
        'nodeData': {
            'BufferId': '0',
            'Flags': 4063232,
            'Type': ('WolvenKit.RED4.Archive.Buffer.worldNodeDataBuffer, '
                     'WolvenKit.RED4, Version=8.20.0.0, Culture=neutral, '
                     'PublicKeyToken=null'),
            'Data': instances,
        },
        # NOT parallel to the nodes: a name may be listed without being attached
        # to anything, which is how vanilla registers its communities.
        'nodeRefs': [noderef_str(r) for r in refs],
        'nodes': [{'HandleId': str(i), 'Data': n} for i, n in enumerate(nodes)],
        'persistentNodeIndex': 0,
        'persistentNodes': [],
        'variantIndices': [0],
        'variantNodes': [],
        'version': 62,
    }
    return {
        'Header': cr2w.header(name),
        'Data': {'Version': 195, 'BuildVersion': 0,
                 'RootChunk': renumber_handles(root, [0]),
                 'EmbeddedFiles': []},
    }


def descriptor(path, box_min, box_max):
    return {
        '$type': 'worldStreamingSectorDescriptor',
        'blockIndex': {'$type': 'worldStreamingBlockIndex', 'oup': 'Base',
                       'rldGridCell': 0},
        'category': 'AlwaysLoaded',
        'data': {'DepotPath': {'$type': 'ResourcePath', '$storage': 'string',
                               '$value': path}, 'Flags': 'Soft'},
        'level': 1,
        'numNodeRanges': 1,
        'questPrefabNodeRef': NOREF,
        'streamingBox': {'$type': 'Box', 'Max': vec4(box_max, w=1),
                         'Min': vec4(box_min, w=1)},
        'variants': [],
    }
