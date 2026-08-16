r"""Generates the tiny device entity that lets SCRIPT put an NPC in a workspot.

WHY THIS EXISTS.
`gamePhantomEntityComponent.phantomVisibleStates` is ["RootMotion","Workspot"],
so a spawned Johnny standing in a plain idle renders nothing. A .scene can carry
its own workspot (tools/gen_scenes.py), which covers the two beats that happen at
a known place - Hoshino's lounge and El Coyote. It cannot cover the beat right
after Elena's call, because that happens wherever V is standing and a scene actor
spawns at a FIXED marker.

That beat is a DynamicEntitySystem spawn, so it needs the script route:

    GameInstance.GetWorkspotSystem(game)
        .PlayInDeviceSimple(device, actor, false, n"<component name>")

`device` is a GameObject carrying a named `workWorkspotResourceComponent`. There
is no generic base-game workspot marker entity, so the device has to be shipped -
which is what this file builds. It is the same trick Cyberscript, Smoke
Everywhere and AMM all use; ours is written from the base-game component shape
(base\quest\character_vehicles\johnny_car.ent) rather than copied from a mod.

WHAT IT IS NOT.
This is NOT a modified copy of johnny.ent. Re-authoring that file is the thing
that crashed the game on 2026-08-12 and the cause was never established (see
docs/backlog.md 3b, "CORRECTION"). This entity is built from nothing, has one
component and no meshes, and shares no code path with that attempt.

Nor is it AMM's `workspot_anim.ent`: AMM ships no LICENSE and its README defers
to its Nexus page, so its files carry no redistribution grant. Only the component
SHAPE is reused here, and that shape is engine API, taken from a CDPR file.

The workspot path is imported from gen_scenes so the scene route and the script
route cannot drift apart.
"""
import json
import os

from gen_scenes import WORKSPOT_JOHNNY, cname, resref

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, 'mods', 'gig-01-negative-balance', 'source', 'wkit',
                   'raw', 'mod', 'negative_balance', 'entity',
                   'cc_g01_workspot.ent.json')

# The name redscript passes to PlayInDeviceSimple as actorDataCompName. It has to
# match Gig01_Encounter.reds exactly - a wrong CName is not an error, the actor
# just never enters the workspot.
COMPONENT_NAME = 'cc_g01_johnny_stand'

# Component ids are arbitrary but must be unique and non-zero within the file.
COMPONENT_ID = '2688062543868039169'


def build():
    return {
        'Header': {'WolvenKitVersion': '8.20.0', 'WKitJsonVersion': '0.0.9',
                   'GameVersion': 2310, 'DataType': 'CR2W',
                   'ArchiveFileName': 'cc_g01_workspot.ent'},
        'Data': {
            'Version': 195, 'BuildVersion': 0,
            'RootChunk': {
                '$type': 'entEntityTemplate',
                'appearances': [],
                'backendDataOverrides': [],
                'bindingOverrides': [],
                # DELIBERATELY ABSENT: `compiledData`.
                #
                # It is a RedPackage buffer mirroring `components` - chunk 0 the
                # root entity, chunks 1..N the components in order, plus a
                # CruidDict of chunk index -> CRUID. WolvenKit REGENERATES it
                # from `components` on write (verified by four controlled
                # round-trips, docs/backlog.md 3b), so `components` is the
                # master and hand-writing the buffer is both unnecessary and the
                # documented way to get an ArgumentOutOfRangeException and no
                # output file at all.
                #
                # tools/build-archive.ps1 fails loudly if a converted resource
                # does not appear, so a silently-missing output cannot ship.
                'compiledEntityLODFlags': 0,
                'componentResolveSettings': [],
                # Inline objects, NOT {HandleId, Data} handles - the opposite of
                # `entity` below and of scene events. WolvenKit rejects the file
                # outright if these are wrapped.
                'components': [{
                    '$type': 'workWorkspotResourceComponent',
                    'deviceWorkspotResourceSync': resref(flags='Default'),
                    'id': COMPONENT_ID,
                    'isReplicable': 0,
                    # At the device's own origin. The script spawns the device
                    # exactly where the actor is standing, so any offset here
                    # would show up as Johnny sliding sideways.
                    'localTransform': {
                        '$type': 'WorldTransform',
                        'Orientation': {'$type': 'Quaternion',
                                        'i': 0, 'j': 0, 'k': 0, 'r': 1},
                        'Position': {'$type': 'WorldPosition',
                                     'x': {'$type': 'FixedPoint', 'Bits': 0},
                                     'y': {'$type': 'FixedPoint', 'Bits': 0},
                                     'z': {'$type': 'FixedPoint', 'Bits': 0}}},
                    'name': cname(COMPONENT_NAME),
                    'npcWorkspotResourceSync': resref(flags='Default'),
                    'parentTransform': None,
                    'shouldCrouch': 0,
                    'syncSlotName': cname(None),
                    # Default, not Soft: a workspot that has not streamed in yet
                    # is an animation that does not play.
                    'workspotResource': resref(WORKSPOT_JOHNNY, flags='Default'),
                }],
                'cookingPlatform': 'PLATFORM_PC',
                'defaultAppearance': cname('default'),
                # gameObject, NOT entEntity. `PlayInDeviceSimple` takes a
                # ref<GameObject>, and the script gets its handle by casting
                # DynamicEntitySystem.GetEntity(id) as GameObject - a cast that
                # returns null for a plain entEntity. The device would spawn
                # perfectly and then be unusable.
                #
                # No visuals of any kind: it exists only to carry the component.
                'entity': {'HandleId': '0', 'Data': {'$type': 'gameObject'}},
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


if __name__ == '__main__':
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as fh:
        json.dump(build(), fh, indent=2)
    print('wrote %s (component "%s" -> %s)' % (OUT, COMPONENT_NAME, WORKSPOT_JOHNNY))
