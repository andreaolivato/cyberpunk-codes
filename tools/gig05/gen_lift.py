#!/usr/bin/env python3
"""THE LIFT, A GAME DEVICE: one lift, a floor terminal and a marker per stop.

The shape is the wiki's "Custom Elevators", manual route, with the terminals'
instance data lifted from the game's own two-floor lift
(`exterior_-14_34_0_0`, {lift_terminal_}1, saved in flights/lift_vanilla.json).
The lift node names its terminals, each terminal names its floor's marker, and
the lift stands at the first stop."""
import copy
import json
import os

from questkit import community

HERE = os.path.dirname(os.path.abspath(__file__))
B = chr(92)
LIFT_ENT = B.join(['base', 'gameplay', 'devices', 'elevators', 'megabuilding_elevator',
                   'megabuilding_lift_1.ent'])
RANGE = (400.0, community.WB['ukfloat'], community.WB['uk10'], community.WB['uk11'])
# THE MARKERS OUTREACH THE LIFT (wiki, "Custom Elevators"), the vanilla lift's own
# distance. At the sector's default of 120 m the far stop of a 111 m shaft was at
# the edge of what is loaded.
MARKER_RANGE = (3849.14111, community.WB['ukfloat'], community.WB['uk10'], community.WB['uk11'])


def _vanilla():
    with open(os.path.join(HERE, 'flights', 'lift_vanilla.json'), encoding='utf-8') as fh:
        return json.load(fh)


def _walk(obj, fn):
    if isinstance(obj, dict):
        fn(obj)
        for v in obj.values():
            _walk(v, fn)
    elif isinstance(obj, list):
        for v in obj:
            _walk(v, fn)


def lift(sector, name, stops, marker, buffer_base, doors=None):
    """`stops` is (spot, terminal spot, yaw, terminal yaw, floor name) per
    floor, lowest first. `marker(name, spot, yaw)` makes a static marker the way the caller
    does. `doors` is {floor: door ref}: a door a floor's terminal locks and unlocks.
    Returns (lift ref, extra nodes)."""
    src = _vanilla()
    out, terminal_refs, stop_refs = [], [], []
    for i, (spot, panel, yaw, panel_yaw, floor_name) in enumerate(stops):
        # THE MARKER'S YAW IS THE WAY V FACES, put in the car: at the door.
        mark_ref, mark = marker('%s_stop_%d' % (name, i), spot, yaw - 90.0)
        mark = mark[:3] + (MARKER_RANGE,) + mark[4:]
        out.append(mark)
        stop_refs.append(mark_ref)
        node = copy.deepcopy(src[1]['n'])
        ref = community.Community.ref(sector, '%s_panel_%d' % (name, i))
        node['debugName'] = community.cname('{%s_panel_%d}' % (name, i))
        node['deviceConnections'] = []
        if doors and i in doors:
            node['deviceConnections'] = [{
                '$type': 'worldDeviceConnections',
                'deviceClassName': community.cname('DoorControllerPS'),
                'nodeRefs': [community.noderef_str(doors[i])]}]
        # THE EXAMPLE'S TERMINALS ARE SWITCHED ON BY ITS QUEST. Copied as they
        # stand, the panel was never there.
        node['isVisibleInGame'] = 1
        node['sourcePrefabHash'] = '0'
        node['instanceData']['Data']['buffer']['BufferId'] = str(buffer_base + i)

        def fix(o, mark_ref=mark_ref, floor_name=floor_name):
            if o.get('$type') == 'ElevatorFloorSetup':
                o['floorMarker'] = community.noderef_str(mark_ref)
                o['doorShouldOpenFrontLeftRight'] = [1, 0, 0]
                o['floorDisplayName'] = community.cname(floor_name)
        _walk(node, fix)
        # THE EXAMPLE'S TERMINALS ARE SWITCHED ON BY ITS QUEST, and locked. As they
        # stand the panel is a black slab and the keypad refuses this floor.
        state = node['instanceData']['Data']['buffer']['Data']['Chunks'][0]['persistentState']['Data']
        state['deviceState'] = 'ON'
        state['hasAuthorizationModule'] = 0
        state['authorizationProperties']['isAuthorizationModuleOn'] = 0
        out.append((node, panel, ref, RANGE, panel_yaw))
        terminal_refs.append(ref)
    node = copy.deepcopy(src[0]['n'])
    ref = community.Community.ref(sector, name)
    node['debugName'] = community.cname('{%s}' % name)
    node['entityTemplate']['DepotPath']['$value'] = LIFT_ENT
    node['instanceData'] = None
    node['isVisibleInGame'] = 1
    node['sourcePrefabHash'] = '0'
    node['deviceConnections'] = [{
        '$type': 'worldDeviceConnections',
        'deviceClassName': community.cname('ElevatorFloorTerminalControllerPS'),
        'nodeRefs': [community.noderef_str(r) for r in terminal_refs]}]
    out.append((node, stops[0][0], ref, RANGE, stops[0][2]))
    return ref, out, stop_refs


def _hash(ref):
    """A node's id is FNV1a64 of its long name with the `#` taken out."""
    h = 0xcbf29ce484222325
    for c in ref.replace('#', '').encode():
        h = ((h ^ c) * 0x100000001b3) & (2 ** 64 - 1)
    return str(h)


def devices(name, lift_ref, lift_pos, terminals, doors=()):
    """The world's device graph, one parent and its children: `.devices`, merged
    by ArchiveXL into 03_night_city's. `terminals` is (ref, position) per floor,
    `doors` is (door ref, position, floor), floor None for a door of no terminal."""
    def entry(cls, ref, pos, children, parents):
        return {'$type': 'gameDeviceResourceData_Cls1', 'children': children,
                'className': community.cname(cls), 'hash': _hash(ref),
                'nodePosition': {'$type': 'Vector3', 'X': pos[0], 'Y': pos[1], 'Z': pos[2]},
                'parents': parents}
    rows = [entry('LiftControllerPS', lift_ref, lift_pos,
                  [_hash(r) for r, _p in terminals], [])]
    rows += [entry('ElevatorFloorTerminalControllerPS', r, p,
                   [_hash(d) for d, _q, f in doors if f == i], [_hash(lift_ref)])
             for i, (r, p) in enumerate(terminals)]
    rows += [entry('DoorControllerPS', d, q, [], [] if f is None else [_hash(terminals[f][0])])
             for d, q, f in doors]
    return {'Header': {'WolvenKitVersion': '8.20.0', 'WKitJsonVersion': '0.0.9',
                       'GameVersion': 2500, 'ExportedDateTime': '2026-11-04T00:00:00Z',
                       'DataType': 'CR2W', 'ArchiveFileName': name},
            'Data': {'Version': 195, 'BuildVersion': 0, 'RootChunk': {
                '$type': 'gameDeviceResource', 'cookingPlatform': 'PLATFORM_PC',
                'data': {'HandleId': '0', 'Data': {
                    '$type': 'gameDeviceResourceData', 'unk1': rows, 'version': 2}}},
                'EmbeddedFiles': []}}


def psrep(name, panels):
    """THE PANELS' SAVED STATE: `.psrep`, merged by ArchiveXL into 03_night_city's.
    Without it a terminal's floor setup is only known while the terminal is
    loaded, and after a load the car's doors stay shut and its keypad does nothing
    (gotcha 162). `panels` is (key, terminal node) per floor; each entry is the
    node's own persistent state, the way World Builder's Persistent box writes it."""
    chunks = [node['instanceData']['Data']['buffer']['Data']['Chunks'][0]['persistentState']['Data']
              for _key, node in panels]
    return {'Header': {'WolvenKitVersion': '8.20.0', 'WKitJsonVersion': '0.0.9',
                       'GameVersion': 2500, 'ExportedDateTime': '2026-11-04T00:00:00Z',
                       'DataType': 'CR2W', 'ArchiveFileName': name},
            'Data': {'Version': 195, 'BuildVersion': 0, 'RootChunk': {
                '$type': 'gamePersistentStateDataResource',
                'buffer': {'BufferId': '0', 'Flags': 7471104,
                           'Type': ('WolvenKit.RED4.Archive.Buffer.RedPackage, WolvenKit.RED4, '
                                    'Version=8.20.0.0, Culture=neutral, PublicKeyToken=null'),
                           'Data': {'Version': 4, 'Sections': 6, 'CruidIndex': 0,
                                    'CruidDict': {str(i): key for i, (key, _n) in enumerate(panels)},
                                    'Chunks': chunks}},
                'cookingPlatform': 'PLATFORM_PC'},
                'EmbeddedFiles': []}}
