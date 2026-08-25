r"""A security area for the compound. IT DOES NOT WORK, AND IT IS NOT SHIPPED.

===========================================================================
READ THIS BEFORE FOLLOWING ANY OF IT

The shape below is correct. It is copied field for field off the game's own
data, it converts, it loads, and every part of it was measured right in game on
2026-08-25. What it does not do is anything at all.

Built whole, wired to `cc_g01_compound`, and taken back out the same day. The
area was found and resolved, its device state read ON, attached and not
disabled, `securityAreaType` read RESTRICTED exactly as vanilla's does, the
`CommunityProxyPS` connection pointed at our community, the security system node
was present and linked, eighteen cameras fed it, and `IsPlayerInside()` returned
true while the player stood in the compound. **The guards did nothing.** Setting
the type between RESTRICTED, DANGEROUS and SAFE at runtime changed nothing,
which is what an area with nothing on the other end of its wire looks like.

Nothing calls this module. It is kept so the research is not lost and so
rebuilding it is a one-line change if the picture ever changes. `gotchas.md` 80
is the short version and `backlog.md` 31 has the whole elimination.

===========================================================================
WHAT SURVIVED ELIMINATION, which is not the same as a cause

Eliminated on the way: the node class, the area type, the component ids, the
outline, its winding, the missing system node, and containment.

What is left is that every vanilla community a security area alerts, all 21 that
resolve in the cached sectors, is a `worldCompiledCommunityAreaNode` in the
GAME'S OWN `always_loaded` sectors. ArchiveXL deletes and mutates nodes in a
shipped sector; it does not add them, so a mod cannot put a community there.

The node CLASS was the most promising suspect and it is gone. All 21 of those
use the plain class rather than the `_Streamable` one this project had always
written, so the industrial park shipped the plain class with this area wired to
it. The guards still did nothing. The run did establish that a mod's own sector
spawns from either class, which is now in `gotchas.md` 66 part 3.

===========================================================================
WHAT TO BUILD INSTEAD

Give the guards a hostile attitude and switch their senses on, and let the
ordinary detection ramp do the work (`gotchas.md` 74 and 77). That is what a mod
can have, it runs at base-game rates, and at an Arasaka site under infiltration
it is what the base game does anyway.

The thing this was for is the TRESPASS warning: "you shouldn't be here", the
call-out, the walk over, and a fight only if V stays. That happens to somebody
who is not yet an enemy, which is the opposite of what makes a hostile guard
work, so the two are alternatives rather than a pair. A mod gets the second one.

===========================================================================
THE SCRIPT VERSION WAS TRIED FIRST AND WITHDRAWN, and it is worth knowing why

For one build the alarm was a script: watch the cameras, and when one reports
`IsDetecting`, broadcast a combat stimulus at the player. Playtest inside
minutes: *"the police also marks me as enemy even if I haven't done anything"*.

A stim broadcast is not addressed to anybody. It announces at the player's
position that combat is happening, to EVERY NPC within its radius: police,
civilians, and anybody else passing. It also fed itself, because the fight it
started made the cameras legitimately detect the player.

**The fault was the shape, not the radius.** A smaller broadcast is a smaller
blast, not an aimed one, and the stim system has no way to say who is listening.
A `CommunityProxyPS` connection does name who it alerts, which is the whole
reason this was built rather than the script tuned. Gotcha 81.

===========================================================================
WHAT IT IS MADE OF, read off the game's own data

`{q112_infiltration_security_area_civilian_restricted}` in
`exterior_-4_-23_0_0` is the worked example, and it is at THIS SITE: the
industrial park already has a working security area, so the shape below is not
inferred, it is the neighbours' copied with our names in it.

    worldDeviceNode
      entityTemplate   base\gameplay\devices\security_systems\security_area\
                       security_area_1.ent
      deviceConnections
        CommunityProxyPS                 -> the communities it alerts
        SurveillanceCameraControllerPS   -> the cameras that feed it
      instanceData -> buffer -> Chunks
        gameStaticTriggerAreaComponent   the trigger prism: an outline of
                                         points in LOCAL space, and a height
        SecurityAreaController
          persistentState.securityAreaType  RESTRICTED

Vanilla's carries three communities and nine cameras. Ours carried one community
and eighteen.

RESTRICTED, not Hostile. The wiki gives Hostile as the default; the example at
this site uses RESTRICTED, and restricted is the trespass case. Hostile would
skip the warning, which is the half a hostile attitude already provides.

===========================================================================
THE ONE THING HERE THAT IS GENERALLY USEFUL

Writing an `entEntityInstanceData` RedPackage buffer. This was called the
blocker on the whole feature for two days, because a security area's trigger
polygon lives in such a buffer and nothing this project ships had ever contained
one.

Settled by asking the smallest version of the question: the vanilla node was
taken whole, given our names and our refs, put in a sector of our own, and
handed to the same converter the build uses. It converted, and a round trip back
to JSON returned the buffer intact, both chunks, the outline point for point,
the height and all 122 fields of the controller state.

Any vanilla node type with an instance buffer can be copied this way, and the
round trip is what turns "it converted" into "it converted correctly". Two
fix-ups are needed and both reject the WHOLE FILE with an unhelpful error:
`BufferId` must not be 0, and a CRUID is a SIGNED 64-bit integer. `gotchas.md`
79 has both.

===========================================================================
WHAT WAS NEVER SETTLED, and now never will be here

Whether the prism runs up from the node or is centred on it. Vanilla's sits at
z 11.09 with height 14.93 at a site whose ground is around 7.6, which fits either
reading, so ours was placed low with a generous height to cover the site under
both. And whether one area over the whole compound is the right shape where
vanilla uses several small ones. Neither question can be answered while the
feature itself does nothing.
"""
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from questkit import community                                      # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
# THE VANILLA CONTROLLER STATE, kept as a file rather than written out.
#
# 122 fields, most of them nothing to do with security areas: a device's whole
# saved state, down to whether it has been scanned and how many minigame
# attempts it has had. Taken from
# `{q112_infiltration_security_area_civilian_restricted}` with only the three
# fields that name THAT area cleared. Inventing values for fields nobody has
# read is how eleven bench runs were lost on the community recipe, and the same
# precedent is `shard_container_node.json` beside this file.
PS_TEMPLATE = os.path.join(HERE, 'security_area_ps.json')


def cruid(text):
    """A stable component id that fits in a SIGNED 64-bit integer.

    See the note where this is used: an unmasked FNV1a64 can exceed 2^63 and
    WolvenKit then refuses the whole file.
    """
    return community.fnv1a64(text) & ((1 << 63) - 1)


def load_ps():
    import json
    with io.open(PS_TEMPLATE, encoding='utf-8') as fh:
        return json.load(fh)

# ------------------------------------------------------------ the boundary
#
# THE FOUR CORNERS OF THE COMPOUND, WALKED AND CAPTURED in playtest 2026-08-17
# as `compound_1` to `compound_4`, and already in `Gig01_Encounter.reds` as
# `CCGig01Places.InsideCompound`. Convex, about 38,500 m2, and it contains
# every anchor the gig uses here: all five doors, the terminal, the shard and
# the map pin.
#
# THIS IS THE SITE, MEASURED. A previous build replaced it with a boundary
# derived from where the guards happen to stand, on the reasoning that 38,500 m2
# looked too big next to the 6,900 m2 the posts occupy. That reasoning was
# wrong and the substitution was worse than the thing it replaced: guards are
# posted where they are useful, not around the perimeter, so the ground they
# cover is not the compound. The walked corners are the compound.
#
# Playtest put it plainly: the guards do not encompass the whole compound.
# Deriving a boundary from them shrinks the restricted area to the part that
# happens to be watched, which is the opposite of what a restricted area means.
#
# So: measured ground, from the walk, unchanged. Same rule as the posts
# themselves (gotcha 67), and the same rule this project keeps having to
# relearn: a number somebody walked beats a number somebody inferred.
CORNERS = [
    (-113.001, -1398.983),
    (-282.899, -1299.636),
    (-389.293, -1463.909),
    (-239.160, -1567.924),
]


# WHERE THE NODE SITS, and the outline is measured from it. Low, because the
# prism may run upwards from here: the compound's ground is about 7.6 and its
# top floor about 15.8, and 40 m of height covers both readings of how the
# prism is built.
GROUND_Z = 5.0
HEIGHT = 40.0

# Vanilla's own instance values for a security area node at this site.
INSTANCE = (6794.55029, 100.0, 1024, 10762)


def outline_points(centre, corners):
    """The corners as offsets from the node, which is how vanilla stores them."""
    return [{'$type': 'Vector3', 'X': x - centre[0], 'Y': y - centre[1],
             'Z': 0} for x, y in corners]


def centre(corners):
    xs = [c[0] for c in corners]
    ys = [c[1] for c in corners]
    return (sum(xs) / len(xs), sum(ys) / len(ys), GROUND_Z)


def trigger_area(pos, corners):
    """`gameStaticTriggerAreaComponent`, field for field off the vanilla one.

    `includeMask` 1 and `isEnabled` 1 are what the working example has, and the
    identity `localTransform` is what puts the outline in the node's own space.
    """
    return {
        '$type': 'gameStaticTriggerAreaComponent',
        'color': {'$type': 'Color', 'Alpha': 0, 'Blue': 0, 'Green': 0, 'Red': 0},
        'excludeMask': 0,
        'id': '0',
        'includeMask': 1,
        'isEnabled': 1,
        'isReplicable': 0,
        'localTransform': {
            '$type': 'WorldTransform',
            'Orientation': {'$type': 'Quaternion', 'i': 0, 'j': 0, 'k': 0,
                            'r': 1},
            'Position': {'$type': 'WorldPosition',
                         'x': {'$type': 'FixedPoint', 'Bits': 0},
                         'y': {'$type': 'FixedPoint', 'Bits': 0},
                         'z': {'$type': 'FixedPoint', 'Bits': 0}},
        },
        'name': community.cname('Component'),
        'outline': {'HandleId': '1', 'Data': {
            '$type': 'AreaShapeOutline',
            'buffer': '',
            'height': HEIGHT,
            'points': outline_points(pos, corners),
        }},
        'parentTransform': None,
    }


def controller(template_ps):
    """`SecurityAreaController`, whose persistent state carries the type.

    The state has 122 fields and they are taken from the vanilla node whole
    rather than written out here: it is a device's entire saved state, most of
    it nothing to do with security areas, and inventing values for fields
    nobody has read is how eleven bench runs were lost on the community.
    """
    return {
        '$type': 'SecurityAreaController',
        'id': '0',
        'isReplicable': 0,
        'name': community.cname('Component'),
        'persistentState': {'HandleId': '2', 'Data': template_ps},
    }


def node(name, template_ps, community_ref, camera_refs, corners):
    pos = centre(corners)
    return {
        '$type': 'worldDeviceNode',
        'alphaHackStreamingDistanceOverride': 0,
        'appearanceName': community.cname('default'),
        'debugName': community.cname('{%s}' % name),
        'deviceClassName': community.cname('None'),
        # THE TWO CONNECTIONS, and they are the whole feature. The first says
        # which NPCs this area alerts; the second says which cameras feed it.
        'deviceConnections': [
            {'$type': 'worldDeviceConnections',
             'deviceClassName': community.cname('CommunityProxyPS'),
             'nodeRefs': [community.noderef_str(community_ref)]},
            {'$type': 'worldDeviceConnections',
             'deviceClassName': community.cname('SurveillanceCameraControllerPS'),
             'nodeRefs': [community.noderef_str(r) for r in camera_refs]},
        ],
        'entityLod': 0,
        'entityTemplate': {
            'DepotPath': {'$type': 'ResourcePath', '$storage': 'string',
                          '$value': community.depot(
                              'base', 'gameplay', 'devices', 'security_systems',
                              'security_area', 'security_area_1.ent')},
            'Flags': 'Soft'},
        'instanceData': {'HandleId': '3', 'Data': {
            '$type': 'entEntityInstanceData',
            'buffer': {
                # NOT 0. A sector's `nodeData` is itself a buffer and it is
                # buffer 0, so an instance buffer claiming the same id collides
                # with it and WolvenKit refuses the whole file with
                # `The JSON value could not be converted to RedFileDto`,
                # pointing at the line where the instance buffer ends.
                #
                # The vanilla example is buffer 78 in a sector with many. One is
                # enough here: this is the only instance buffer the file has.
                'BufferId': '1',
                'Flags': 4063232,
                'Type': ('WolvenKit.RED4.Archive.Buffer.RedPackage, '
                         'WolvenKit.RED4, Version=8.20.0.0, Culture=neutral, '
                         'PublicKeyToken=null'),
                'Data': {
                    'Version': 4,
                    'Sections': 6,
                    'CruidIndex': -1,
                    # Two component ids, derived from our own name so they
                    # are stable between runs and cannot collide with the
                    # example's.
                    #
                    # MASKED TO 63 BITS, and that is not decoration. A CRUID is
                    # a SIGNED 64-bit integer, and an FNV1a64 uses the whole
                    # unsigned range: the first attempt produced
                    # 10314632116389077042, which is larger than 2^63, and
                    # WolvenKit's parser refused the entire file with
                    # `The JSON value could not be converted to RedPackage`.
                    #
                    # Vanilla's two are 1508365491801698304 and
                    # 1395159393761816576, both comfortably positive, which is
                    # what a signed id looks like.
                    # VANILLA'S OWN TWO, and this is a FIX rather than a copy.
                    #
                    # Ours were derived from our node's name, and the game then
                    # ignored the state they carry: measured 2026-08-25, our
                    # area reported DANGEROUS at runtime while shipping
                    # RESTRICTED, and a vanilla area fifty metres away reported
                    # the RESTRICTED it ships. The wiki says an area is Hostile
                    # by default, so ours was falling back to the default and
                    # the shipped state was going nowhere.
                    #
                    # A CRUID identifies a component, so an invented one leaves
                    # the persistent state attached to nothing. These are the
                    # two `security_area_1.ent` uses, taken from the same node
                    # the rest of this shape came from.
                    'CruidDict': {
                        '0': '1508365491801698304',
                        '1': '1395159393761816576',
                    },
                    'Chunks': [trigger_area(pos, corners), controller(template_ps)],
                },
            },
        }},
        'ioPriority': 'Immediate',
        'isHostOnly': 0,
        'isVisibleInGame': 1,
        'proxyScale': None,
        'sourcePrefabHash': '0',
        'tag': 'None',
        'tagExt': 'None',
    }


def system_node(name, area_ref, community_ref):
    r"""`security_system.ent`: the piece the wiki calls MANDATORY.

    THIS WAS OMITTED FROM THE FIRST BUILD AND THAT IS WHY IT DID NOTHING.
    The area alone loaded and resolved, and changing its type between
    RESTRICTED, DANGEROUS and SAFE changed nothing in game, which is what an
    area with nothing driving it looks like. The wiki is explicit:

        "you need a security system, linked to the security area"

    NO INSTANCE BUFFER. `{q112_infiltration_security_system}` in
    `exterior_-5_-24_0_0` is a plain `worldDeviceNode` with `instanceData: null`
    and a list of connections, which is a shape these generators already write
    for every other node. Its `SecurityAreaControllerPS` connection names FOUR
    areas at once, so one system to many areas is the normal arrangement.

    The community link is put here as well as on the area, because vanilla has
    it both ways: `{cs_dragnet_sec_system}` carries `CommunityProxyPS` on the
    SYSTEM, and the q112 area carries it on the AREA. Naming it twice costs a
    connection and removes a guess.
    """
    return {
        '$type': 'worldDeviceNode',
        'alphaHackStreamingDistanceOverride': 0,
        'appearanceName': community.cname('default'),
        'debugName': community.cname('{%s}' % name),
        'deviceClassName': community.cname('None'),
        'deviceConnections': [
            {'$type': 'worldDeviceConnections',
             'deviceClassName': community.cname('SecurityAreaControllerPS'),
             'nodeRefs': [community.noderef_str(area_ref)]},
            {'$type': 'worldDeviceConnections',
             'deviceClassName': community.cname('CommunityProxyPS'),
             'nodeRefs': [community.noderef_str(community_ref)]},
        ],
        'entityLod': 0,
        'entityTemplate': {
            'DepotPath': {'$type': 'ResourcePath', '$storage': 'string',
                          '$value': community.depot(
                              'base', 'gameplay', 'devices', 'security_systems',
                              'security_system.ent')},
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


def extra_nodes(sector, area_name, system_name, community_ref, camera_refs):
    """The area AND its system, as the pair `Community` takes.

    Both in the same sector as the community, which is the wiki's one hard
    constraint: *"ensure your community, security area, and security system are
    all in the same group. Otherwise the device connection may not be linked
    properly"*.
    """
    area_ref = community.Community.ref(sector, area_name)
    sys_ref = community.Community.ref(sector, system_name)
    corners = CORNERS
    pos = centre(corners)
    return [
        (node(area_name, load_ps(), community_ref, camera_refs, corners), pos,
         area_ref, INSTANCE),
        (system_node(system_name, area_ref, community_ref), pos, sys_ref,
         INSTANCE),
    ]
