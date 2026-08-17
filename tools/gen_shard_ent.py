r"""Generates the physical data shard V picks up off the office desk (comic p23).

WHY THIS EXISTS.
The shard beat shipped as a PROXIMITY trigger: walk to the desk and the reader
opened by itself. Playtest, 2026-08-13: *"the shard, I didn't see it / open it. It
just went near it and it opened. Can we show the physical shard and we need to
open with F to trigger?"* He was not missing anything - there was no object.

THE WORKED EXAMPLE IS `cyberpunk/items/healthConsumable.swift`, 50 lines, and it
is the whole recipe for a scripted world object with an F prompt:

    OnRequestComponents -> RequestComponent(ri, n"interactions",
                                            n"gameinteractionsComponent", true)
    OnTakeControl       -> resolve it into a ref<InteractionComponent>
    OnGameAttached      -> choice.choiceMetaData.tweakDBName = "PickUp";
                           m_interactionComponent.SetSingleChoice(choice)
    OnInteractionChoiceEvent(evt) -> the player pressed it

So the object needs exactly two components, and this file builds an entity that
carries them. The behaviour lives in Gig01_Shard.reds (class CCG01ShardObject),
which is what `entity.$type` below names.

THE MESH IS THE REAL ONE. `base\environment\decoration\electronics\hardware\
id_card_chip\id_card_chip_a_regular_86x54x2.mesh` at visualScale 2.5 is what
`sts_std_arr_01_personel_shard.ent` uses - a shipped street story putting a
readable shard on a desk, i.e. the exact thing this is. Taken from a CDPR file,
not from a mod.

"PickUp", NOT "Read". `tweakDBName` is a string naming a TweakDB interaction, and
"PickUp" is one of only two the decompiled scripts use literally - so it is
confirmed to exist, which "Read" is not (TweakDB record names are not
discoverable from the files on disk). It is also the honest verb: in vanilla you
pick a shard up and the reader opens, which is this beat.

The authoring rules below are not optional:
  * NO `compiledData` - WolvenKit regenerates it from `components` on write, and
    hand-writing the buffer produces no output file at all;
  * components are INLINE objects, `entity` is a {HandleId, Data} handle.
"""
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, 'mods', 'gig-01-negative-balance', 'source', 'wkit',
                   'raw', 'mod', 'negative_balance', 'entity',
                   'cc_g01_shard.ent.json')

# THE ENTITY CLASS IS A BASE-GAME ONE, AND IT HAS TO BE.
#
# The first cut of this file named a redscript class of ours (CCG01ShardObject).
# WolvenKit refuses to convert that: its JSON reader resolves `entity.$type`
# against the game's own type list and dies with "Cannot get the value of a
# token type 'EndObject' as a string" pointing at that line. Verified by probing
# four class names through `convert deserialize` - HealthConsumable,
# ShardCaseContainer, gameItemObject and InteractiveDevice all convert; ours
# does not. A mod .ent can only name a class the game already ships.
#
# HealthConsumable is the right one anyway. It is the minimal scripted
# interactable (cyberpunk/items/healthConsumable.swift, 50 lines): its
# OnGameAttached publishes exactly one choice with tweakDBName "PickUp", and it
# asks for its components by the names `interactions` and `mesh` - which is why
# the two components below carry those names. So the prompt, the component
# wiring and the press callback all come for free, and Gig01_Shard.reds only has
# to WRAP the callback and recognise ours.
#
# Nothing of its own behaviour survives: the wrap does not call wrappedMethod for
# our shard, so it never tries to equip the health item it has no record for.
ENTITY_CLASS = 'HealthConsumable'

# Must match the RequestComponent names in that class. A wrong CName is not an
# error: the component simply never resolves and the shard has no prompt.
INTERACTION_COMPONENT = 'interactions'
MESH_COMPONENT = 'mesh'

SHARD_MESH = (r'base\environment\decoration\electronics\hardware\id_card_chip'
              r'\id_card_chip_a_regular_86x54x2.mesh')

# Arbitrary but unique and non-zero within the file.
INTERACTION_ID = '2688062543868039201'
MESH_ID = '2688062543868039202'
SCANNING_ID = '2688062543868039203'
VISION_ID = '2688062543868039204'
COLLIDER_ID = '2688062543868039205'
TARGETING_ID = '2688062543868039206'


def cname(v):
    return {'$type': 'CName', '$storage': 'string', '$value': v if v else 'None'}


def resref(path=None, flags='Default'):
    if path is None:
        return {'DepotPath': {'$type': 'ResourcePath', '$storage': 'uint64',
                              '$value': '0'}, 'Flags': flags}
    return {'DepotPath': {'$type': 'ResourcePath', '$storage': 'string',
                          '$value': path}, 'Flags': flags}


def transform():
    return {
        '$type': 'WorldTransform',
        'Orientation': {'$type': 'Quaternion', 'i': 0, 'j': 0, 'k': 0, 'r': 1},
        'Position': {'$type': 'WorldPosition',
                     'x': {'$type': 'FixedPoint', 'Bits': 0},
                     'y': {'$type': 'FixedPoint', 'Bits': 0},
                     'z': {'$type': 'FixedPoint', 'Bits': 0}},
    }


def build():
    interaction = {
        '$type': 'gameinteractionsComponent',
        # THE HOTSPOT DEFINITION, and its absence is why the shard had no prompt
        # even though everything else was right.
        #
        # The probe settled the other half first: `cc_g01_dbg_shard_class` came
        # back 1, so HealthConsumable DOES attach in singleplayer, its
        # OnGameAttached ran, and SetSingleChoice was called. The choice existed
        # and nothing displayed it.
        #
        # A `gameinteractionsComponent` with definitionResource 0 has no hotspot
        # rules - nothing that says "show this when the player is looking at it
        # from within so-and-so". The definition is where that lives: the one
        # below is a `gameinteractionsCHotSpotDefinition` whose layers carry
        # predicates like `gameinteractionsDistanceFromScreenCenterPredicate`.
        # The whole game ships FORTY of these; this is the one for a small item
        # you pick up off the floor, which is what a shard on a desk is.
        #
        # Its layers are unnamed, i.e. the default layer - which is the one
        # `SetSingleChoice(choice)` writes to when no layer is passed, as
        # healthConsumable.swift does.
        'definitionResource': resref(
            r'base\gameplay\items\interactions'
            r'\generic_small_loot_drop_interaction.interaction', flags='Soft'),
        'id': INTERACTION_ID,
        # The prompt hovers at the component's origin. The script places the
        # shard ON the desk surface, so no lift is needed here.
        'interactionRootOffset': {'$type': 'Vector3', 'X': 0, 'Y': 0, 'Z': 0},
        'isEnabled': 1,
        'isReplicable': 0,
        'layerOverrides': [],
        'layerOverridesTemp': [],
        'localTransform': transform(),
        'name': cname(INTERACTION_COMPONENT),
        'parentTransform': None,
    }
    mesh = {
        '$type': 'entMeshComponent',
        'autoHideDistance': 0,
        'castLocalShadows': 'Always',
        'castRayTracedGlobalShadows': 'Always',
        'castRayTracedLocalShadows': 'Default',
        'castShadows': 'Always',
        'chunkMask': '9223372036854775807',
        'forcedLodDistance': 'Default',
        'forceLODLevel': -1,
        'id': MESH_ID,
        'isEnabled': 1,
        'isReplicable': 0,
        # AlwaysVisible, copied from the vanilla shard: a chip 86 mm across is
        # exactly the size of thing an LOD system throws away first, and one
        # that vanishes as V walks up to it is worse than no shard at all.
        'LODMode': 'AlwaysVisible',
        'mesh': resref(SHARD_MESH),
        'meshAppearance': cname('default'),
        'motionBlurScale': 1,
        'name': cname(MESH_COMPONENT),
        'navigationImpact': {'$type': 'NavGenNavigationSetting',
                             'navmeshImpact': 'Ignored'},
        'numInstances': 0,
        'objectTypeID': 'ROT_Static',
        'order': 0,
        'overrideMeshNavigationImpact': 1,
        'parentTransform': None,
        'renderingPlane': 'RPl_Scene',
        'renderSceneLayerMask': 'Default',
        'version': 0,
        # 2.5x, as the vanilla shard does it. An 86x54x2 mm chip at 1:1 is
        # nearly invisible on a desk; the shipped street story scales it up and
        # so does this.
        # 2.5x, as the vanilla shard does it. Briefly 1.5 and reverted with
        # the rotation - see gen_sector.py. It is oversized for a real chip and
        # that is the point: this one has to be found.
        'visualScale': {'$type': 'Vector3', 'X': 2.5, 'Y': 2.5, 'Z': 2.5},
    }

    # Scan + focus-mode highlight, so the shard reads as a thing you can pick up
    # rather than as scenery. playtest, 2026-08-13: "it's not clearly marked. It
    # should appear as an interactive item." These two components are what give a
    # vanilla shard its outline in focus mode and its scan entry; both shapes are
    # copied field-for-field from sts_std_arr_01_personel_shard.ent.
    scanning = {
        '$type': 'gameScanningComponent',
        'autoGenerateBoundingSphere': 1,
        'boundingSphere': {'$type': 'Sphere',
                           'CenterRadius2': {'$type': 'Vector4',
                                             'W': -1, 'X': 0, 'Y': 0, 'Z': 0}},
        'BraindanceLayer': 'Default',
        'clues': [],
        'cpoEnableMultiplePlayersScanningModifier': 1,
        'currentBraindanceLayer': 0,
        'currentHighlight': None,
        'id': SCANNING_ID,
        'ignoresScanningDistanceLimit': 0,
        'isBeingScanned': 0,
        'isBraindanceActive': 0,
        'isBraindanceBlocked': 0,
        'isBraindanceClue': 0,
        'isBraindanceLayerUnlocked': 0,
        'isBraindanceTimelineUnlocked': 0,
        'isEntityVisible': 1,
        'isFocusModeActive': 0,
        'isHudManagerInitialized': 0,
        'isReplicable': 0,
        'isScanningCluesBlocked': 0,
        'name': cname('scanning'),
        'objectDescription': None,
        'OnBraindanceFppChangeCallback': None,
        'OnBraindanceVisionModeChangeCallback': None,
        'persistentState': None,
    }
    vision = {
        '$type': 'gameVisionModeComponent',
        'activeForcedHighlight': None,
        'activeRevealRequests': [],
        'currentDefaultHighlight': None,
        'defaultHighlightData': None,
        'forcedHighlights': [],
        'id': VISION_ID,
        'isFocusModeActive': 0,
        'isReplicable': 0,
        'name': cname('vision'),
        'persistentState': None,
        'slaveObjectsToHighlight': [],
        'wasCleanedUp': 0,
    }

    # WHY THE FIRST RENDERED SHARD HAD NO PROMPT.
    #
    # playtest, 2026-08-13: "the new shard appears... it doesn't have any action
    # and pressing F doesn't work." The entity was there and visible, and
    # HealthConsumable was publishing its choice - but **the player could not
    # aim at it**. An interaction prompt is raised against whatever the player
    # is targeting, and a mesh alone is not targetable: it needs a collider on
    # the interaction physics layer.
    #
    # Both components are lifted from `int_medical_001__medkit_stuff_bottle_a`,
    # a shipped interactable pickup. The load-bearing field is the collider's
    # filter preset, **"Interaction Object"** - that is the layer the
    # interaction raycast queries. A collider with any other preset is a
    # physical obstacle rather than something you can look at and press F on.
    collider = {
        '$type': 'entColliderComponent',
        'colliders': [{'HandleId': '10', 'Data': {
            '$type': 'physicsColliderSphere',
            'filterData': None,
            'isImported': 0,
            'isQueryShapeOnly': 0,
            'localToBody': {'$type': 'Transform',
                            'orientation': {'$type': 'Quaternion',
                                            'i': 0, 'j': 0, 'k': 0, 'r': 1},
                            'position': {'$type': 'Vector4',
                                         'W': 0, 'X': 0, 'Y': 0, 'Z': 0}},
            'material': cname('None'),
            'materialApperanceOverrides': [],
            # 0.12 m: the chip is ~0.21 m across at visualScale 2.5, so this is
            # a target you can hit without it swallowing the desk around it.
            'radius': 0.12,
            'tag': cname('None'),
            'volumeModifier': 1,
        }}],
        'comOffset': {'$type': 'Transform',
                      'orientation': {'$type': 'Quaternion',
                                      'i': 0, 'j': 0, 'k': 0, 'r': 1},
                      'position': {'$type': 'Vector4',
                                   'W': 0, 'X': 0, 'Y': 0, 'Z': 0}},
        'dynamicTrafficSetting': {'$type': 'TrafficGenDynamicTrafficSetting',
                                  'impact': 'Ignored'},
        'filterData': {'HandleId': '11', 'Data': {
            '$type': 'physicsFilterData',
            'customFilterData': None,
            'preset': cname('Interaction Object'),
            'queryFilter': {'$type': 'physicsQueryFilter',
                            'mask1': '0', 'mask2': '2097152'},
            'simulationFilter': {'$type': 'physicsSimulationFilter',
                                 'mask1': '0', 'mask2': '0'},
        }},
        'id': COLLIDER_ID,
        'isEnabled': 1,
        'isReplicable': 0,
        'mass': 4.18879032,
        'name': cname('HitPhysicalQueryMesh'),
        # Kinematic: it must not fall off the desk or be shot across the room.
        'simulationType': 'Kinematic',
    }
    targeting = {
        '$type': 'gameTargetingComponent',
        'aimAssistData': [],
        'alwaysInTestRange': 0,
        'id': TARGETING_ID,
        'isDirectional': 0,
        'isEnabled': 1,
        'isPrimary': 1,
        'isReplicable': 0,
        'localTransform': transform(),
        'name': cname('targeting'),
        # No parentTransform: the shipped one binds to a slot on a rigged prop
        # and this entity has no slots. Unbound means "at the entity origin",
        # which is where the shard is.
        'parentTransform': None,
    }

    return {
        'Header': {'WolvenKitVersion': '8.20.0', 'WKitJsonVersion': '0.0.9',
                   'GameVersion': 2310, 'DataType': 'CR2W',
                   'ArchiveFileName': 'cc_g01_shard.ent'},
        'Data': {
            'Version': 195, 'BuildVersion': 0,
            'RootChunk': {
                '$type': 'entEntityTemplate',
                'appearances': [],
                'backendDataOverrides': [],
                'bindingOverrides': [],
                'compiledEntityLODFlags': 0,
                'componentResolveSettings': [],
                'components': [interaction, mesh, collider, targeting, scanning, vision],
                'cookingPlatform': 'PLATFORM_PC',
                'defaultAppearance': cname('default'),
                # See ENTITY_CLASS above - it must be a class the game ships.
                #
                # Gig01_Encounter still keeps a timed proximity fallback behind
                # this: an entity that fails to attach leaves no object, no
                # prompt and no fact, and the gig would sit on "Search the office
                # desk" forever. The fallback is what makes an unproven
                # mechanism safe to ship.
                'entity': {'HandleId': '0', 'Data': {'$type': ENTITY_CLASS}},
                'includeInstanceBuffer': None,
                'includes': [],
                'inplaceResources': [],
                'localData': None,
                # THIS IS WHY THE SHARD WAS INVISIBLE THE FIRST TIME.
                #
                # playtest, 2026-08-13: "I pushed F and it opened but I cannot see
                # it." The interaction was there, so the entity attached and the
                # prompt worked - only the mesh was missing, which narrows it to
                # one thing: the mesh resource was never streamed in.
                #
                # An entity template declares the resources its components need
                # here, and the first cut shipped an empty list. The vanilla
                # shard declares exactly one dependency - its mesh, Flags "Soft"
                # - so this now does the same. Soft, not Default, because that is
                # what the shipped file uses for the same mesh in the same role.
                'resolvedDependencies': [
                    resref(SHARD_MESH, flags='Soft'),
                    # The hotspot definition needs declaring too, for the same
                    # reason the mesh did: an undeclared resource is one the
                    # entity never streams.
                    resref(r'base\gameplay\items\interactions'
                           r'\generic_small_loot_drop_interaction.interaction',
                           flags='Soft'),
                ],
                'visualTagsSchema': None,
            },
            'EmbeddedFiles': [],
        },
    }


if __name__ == '__main__':
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as fh:
        json.dump(build(), fh, indent=2)
    print('wrote %s (class %s, mesh %s)' % (OUT, ENTITY_CLASS, SHARD_MESH))
