r"""Quest graph builder: .questphase resources.

The reusable half of the quest-phase pipeline. A quest phase is a node graph
whose sockets and connections cross-link by HandleId / HandleRefId; this builder
emits each object once (full definition at first occurrence, HandleRefId
afterwards), matching the layout of shipped questphases.

USAGE, AND THE ONE THING TO KNOW ABOUT IT. The builder keeps its graph in a
single module-level instance, `b`, and the add_* helpers append to it. That
means ONE GRAPH PER PROCESS, which is how this code has always worked and is
why it can be imported rather than rewritten. A generator builds its graph by
calling the helpers top to bottom, then writes `b.build()`.

    configure(phase_name='mygig.questphase')
    start = add_input()
    gate  = add_pause_fact('my_fact', 0, 'Greater')
    b.connect((start, 'Out'), (gate, 'In'))
    ...
    json.dump(b.build(), fh, indent=2)

Do not hand-edit the JSON this produces. A graph of a hundred-plus nodes is not
a thing anyone should be editing as JSON, which is the reason this file exists.
"""
import json  # noqa: F401  (kept so helpers that grow a json call need no import churn)
import os    # noqa: F401

# The sentinel that stages a scene wherever the player is standing. Defined once
# in the scene builder because that is where the evidence for it is written up;
# add_scene() below turns it into a Tag-type scnWorldMarker rather than a
# NodeRef. Importing it rather than restating it removes a constant that three
# separate comments used to warn had to be "kept in step" by hand.
from questkit.scene import ANCHOR_PLAYER

# --------------------------------------------------------------- per-mod config
PHASE_NAME = None


def configure(phase_name):
    """phase_name is the ArchiveFileName header field, e.g. 'gig01.questphase'."""
    global PHASE_NAME
    PHASE_NAME = phase_name


def cname(v):
    return {'$type': 'CName', '$storage': 'string', '$value': v}


def jpath(class_name, real_path):
    return {'$type': 'gameJournalPath', 'className': cname(class_name),
            'editorPath': '', 'fileEntryIndex': 1, 'realPath': real_path}


class Builder:
    def __init__(self):
        self.next_handle = 10
        self.nodes = []            # (node_id, kind, payload, sockets[(name, sock_type)])
        self.conns = []            # ((nid, sock), (nid, sock)) = (source, destination)
        self.sock_handle = {}
        self.conn_handle = {}
        self.sock_conns = {}       # (nid, sock) -> [conn index]

    def handle(self):
        h = self.next_handle
        self.next_handle += 1
        return str(h)

    def node(self, node_id, kind, payload, sockets):
        self.nodes.append((node_id, kind, payload, sockets))

    def connect(self, src, dst):
        idx = len(self.conns)
        self.conns.append((src, dst))
        self.sock_conns.setdefault(src, []).append(idx)
        self.sock_conns.setdefault(dst, []).append(idx)

    # -- serialization ------------------------------------------------------
    def sock_meta(self, key):
        nid, name = key
        for n_id, _kind, _p, socks in self.nodes:
            if n_id == nid:
                for s_name, s_type in socks:
                    if s_name == name:
                        return s_name, s_type
        raise KeyError(key)

    def emit_socket(self, key):
        if key in self.sock_handle:
            return {'HandleRefId': self.sock_handle[key]}
        hid = self.handle()
        self.sock_handle[key] = hid
        name, sock_type = self.sock_meta(key)
        conns = []
        for cidx in self.sock_conns.get(key, []):
            if cidx in self.conn_handle:
                conns.append({'HandleRefId': self.conn_handle[cidx]})
                continue
            chid = self.handle()
            self.conn_handle[cidx] = chid
            src_key, dst_key = self.conns[cidx]

            def side(k):
                if k == key:
                    return {'HandleRefId': hid}
                return self.emit_socket(k)

            conns.append({'HandleId': chid, 'Data': {
                '$type': 'graphGraphConnectionDefinition',
                'destination': side(dst_key),
                'source': side(src_key),
            }})
        return {'HandleId': hid, 'Data': {
            '$type': 'questSocketDefinition',
            'connections': conns,
            'name': cname(name),
            'type': sock_type,
        }}

    def wrap_handles(self, obj):
        """Assign HandleIds to nested {'@handle': {...}} markers."""
        if isinstance(obj, dict):
            if set(obj.keys()) == {'@handle'}:
                return {'HandleId': self.handle(), 'Data': self.wrap_handles(obj['@handle'])}
            return {k: self.wrap_handles(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self.wrap_handles(v) for v in obj]
        return obj

    def build(self):
        out_nodes = []
        for node_id, kind, payload, socks in self.nodes:
            data = {'$type': kind, 'id': node_id}
            data.update(self.wrap_handles(payload))
            data['sockets'] = [self.emit_socket((node_id, s_name)) for s_name, _ in socks]
            # move type-specific payload after sockets when convention expects it
            out_nodes.append({'HandleId': self.handle(), 'Data': data})
        return {
            'Header': {
                'WolvenKitVersion': '8.20.0', 'WKitJsonVersion': '0.0.9',
                'GameVersion': 2310, 'DataType': 'CR2W',
                'ArchiveFileName': PHASE_NAME,
            },
            'Data': {
                'Version': 195, 'BuildVersion': 0,
                'RootChunk': {
                    '$type': 'questQuestPhaseResource',
                    'cookingPlatform': 'PLATFORM_PC',
                    'graph': {'HandleId': self.handle(), 'Data': {
                        '$type': 'questGraphDefinition',
                        'nodes': out_nodes,
                    }},
                    'inplacePhases': [],
                    'phasePrefabs': [],
                },
                'EmbeddedFiles': [],
            },
        }


b = Builder()
NID = iter(range(1000))

STD = [('CutDestination', 'CutDestination'), ('In', 'Input'), ('Out', 'Output')]
JRN = [('CutDestination', 'CutDestination'), ('Active', 'Input'), ('Inactive', 'Input'),
       ('Succeeded', 'Input'), ('Failed', 'Input'), ('Out', 'Output')]


def add_input(name='In1'):
    nid = next(NID)
    b.node(nid, 'questInputNodeDefinition', {'socketName': cname(name)},
           [('CutDestination', 'CutDestination'), ('Out', 'Output')])
    return nid


def add_output(name='Out1'):
    nid = next(NID)
    b.node(nid, 'questOutputNodeDefinition', {'socketName': cname(name), 'type': 'Terminating'},
           [('CutDestination', 'CutDestination'), ('In', 'Input')])
    return nid


def add_pause_fact(fact, value=0, cmp='Greater'):
    nid = next(NID)
    b.node(nid, 'questPauseConditionNodeDefinition', {'condition': {'@handle': {
        '$type': 'questFactsDBCondition',
        'type': {'@handle': {'$type': 'questVarComparison_ConditionType',
                             'comparisonType': cmp, 'factName': fact, 'value': value}},
    }}}, STD)
    return nid


def add_delay(seconds):
    nid = next(NID)
    b.node(nid, 'questPauseConditionNodeDefinition', {'condition': {'@handle': {
        '$type': 'questTimeCondition',
        'type': {'@handle': {'$type': 'questRealtimeDelay_ConditionType',
                             'hours': 0, 'miliseconds': 0, 'minutes': 0, 'seconds': seconds}},
    }}}, STD)
    return nid


def add_game_delay(hours=0, minutes=0, days=0, seconds=0):
    """A wait measured on the WORLD CLOCK, not on the player's clock.

    Same node as add_delay with the other condition type. The difference is the
    one that matters for a wait the player is meant to feel as elapsed time:

    * questRealtimeDelay STALLS while a menu is open (docs/gotchas.md #3), so a
      player who spends the wait in his inventory or on the map waits longer
      than one who does not, and the wait is invisible - nothing on screen ever
      says why the world has not moved on.
    * questGameTimeDelay runs off the in-game clock, which keeps going through
      menus, is paced far faster than real time, and is READABLE: the player can
      look at the HUD clock and see that two hours have passed since he sent Nix
      the ledger. Skipping time skips the wait, which is the right answer too.

    Field order follows questGameTimeDelay_ConditionType (days, hours, minutes,
    seconds), read off the RED4ext SDK header rather than guessed.
    """
    nid = next(NID)
    b.node(nid, 'questPauseConditionNodeDefinition', {'condition': {'@handle': {
        '$type': 'questTimeCondition',
        'type': {'@handle': {'$type': 'questGameTimeDelay_ConditionType',
                             'days': days, 'hours': hours,
                             'minutes': minutes, 'seconds': seconds}},
    }}}, STD)
    return nid


# add_voiceset() LIVED HERE AND IS DELETED. 2026-08-15, built and reverted the
# same evening. Kept as a warning rather than as code, because the code looked
# right and the failure was silent.
#
# It emitted a `questVoicesetManagerNodeDefinition` carrying
# `questChangeVoicesetState_NodeType` - vanilla's own way to switch an NPC's
# barks off, aimed at Mama Welles via `#mama_welles` - to stop her "Look who it
# is" greeting. **It stalled the quest graph.** Playtest: *"our actions never
# spawn"*. The node never handed control on, so the chain never reached the
# pause on `cc_g01_mama_reached` and the epilogue never played at all.
#
# Most likely because an object-manager node waits for its puppetRef to resolve,
# and `#mama_welles` is a SCENE spawn-set reference - proven to work for scene
# acquisition, which is not the same thing as resolving for a quest node while
# her sector may not even be streamed. That is the same distinction that cost
# three builds on map pins (docs/map-pins-playbook.md): a reference that resolves
# in one system is not thereby resolvable in another.
#
# THREE MECHANISMS HAVE NOW FAILED to mute that greeting - the blanket
# entChangeVoicesetStateEvent, the same event naming the `greeting` input, and
# this node. The shipped answer is the SCENE's 2.6 s lead, which lets her line
# land in the gap and reads as an exchange. the design call, and it needs nothing
# suppressed to work.


def add_pause_journal(class_name, real_path, state='Succeeded'):
    nid = next(NID)
    b.node(nid, 'questPauseConditionNodeDefinition', {'condition': {'@handle': {
        '$type': 'questJournalCondition',
        'type': {'@handle': {'$type': 'questJournalEntryState_ConditionType',
                             'inverted': 0, 'path': {'@handle': jpath(class_name, real_path)},
                             'state': state}},
    }}}, STD)
    return nid


def add_setvar(fact, value):
    nid = next(NID)
    b.node(nid, 'questFactsDBManagerNodeDefinition', {'type': {'@handle': {
        '$type': 'questSetVar_NodeType', 'factName': fact, 'setExactValue': 1, 'value': value}}},
        STD)
    return nid


def add_journal(class_name, real_path, notify=1):
    nid = next(NID)
    b.node(nid, 'questJournalNodeDefinition', {'type': {'@handle': {
        '$type': 'questJournalEntry_NodeType',
        'path': {'@handle': jpath(class_name, real_path)},
        'sendNotification': notify}}}, JRN)
    return nid


def add_scene(scene_file, marker, entries, exits):
    """A questSceneNodeDefinition: plays one of our .scene resources.

    Socket names are not free-form. The node's INPUT sockets are the scene's
    entryPoints and its OUTPUT sockets are the scene's exitPoints, by name, plus
    the fixed set every shipped scene node carries ('Default INT'/'Default RET'
    for interruptions, 'Prefetch' for preloading). Get a name wrong and the
    graph simply never continues.

    sceneLocation must be a NodeRef that RESOLVES - the same rule as map pins.
    It is only a placement origin: the player does not have to be near it, which
    is exactly why a fixed anchor works for a phone call.

    ...OR it is ANCHOR_PLAYER, in which case the marker is Tag-typed and the
    scene stages wherever V is standing. That is what makes a beat like "Johnny
    appears beside V and says one line" a scene rather than an unvoiceable
    caption. Placement only matters when someone has to be SEEN or HEARD from a
    position; a holocall does not care, a man standing next to you does.
    """
    nid = next(NID)
    sockets = [('CutDestination', 'CutDestination')]
    sockets += [(e, 'Input') for e in entries]
    sockets += [(x, 'Output') for x in exits]
    sockets += [('Default INT', 'Output'), ('Default RET', 'Output'),
                ('Prefetch', 'Input')]
    b.node(nid, 'questSceneNodeDefinition', {
        'interruptionOperations': [],
        'notAllowedToBeFrozen': 0,
        'reapplyInterruptionOperationsAfterGameLoad': 0,
        'sceneFile': {'DepotPath': {'$type': 'ResourcePath', '$storage': 'string',
                                    '$value': scene_file},
                      'Flags': 'Soft'},
        'sceneLocation': (
            {'$type': 'scnWorldMarker',
             # Five shipped Tag markers carry nodeRef 0, so the tag alone is
             # sufficient. Writing a node here as well would only invite the
             # question of which one wins.
             'nodeRef': {'$type': 'NodeRef', '$storage': 'uint64', '$value': '0'},
             'tag': cname(ANCHOR_PLAYER), 'type': 'Tag'}
            if marker == ANCHOR_PLAYER else
            {'$type': 'scnWorldMarker',
             'nodeRef': {'$type': 'NodeRef', '$storage': 'string',
                         '$value': marker},
             'tag': cname('None'), 'type': 'NodeRef'}),
        'syncToMusic': 0,
    }, sockets)
    return nid


def add_journal_quest(real_path, track=1):
    nid = next(NID)
    b.node(nid, 'questJournalNodeDefinition', {'type': {'@handle': {
        '$type': 'questJournalQuestEntry_NodeType',
        'optional': 0,
        'path': {'@handle': jpath('gameJournalQuest', real_path)},
        'sendNotification': 1, 'trackQuest': track, 'version': 'Initial'}}}, JRN)
    return nid


