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
from questkit.scene import ANCHOR_PLAYER, noderef
from questkit import cr2w

# --------------------------------------------------------------- per-mod config
PHASE_NAME = None


def configure(phase_name):
    """phase_name is the ArchiveFileName header field, e.g. 'gig01.questphase'."""
    global PHASE_NAME
    PHASE_NAME = phase_name


def cname(v):
    """An empty CName is the STRING "None", never a null.

    This returned `$value: null` for an empty name until 2026-08-23, and it
    never bit because every node this builder had ever emitted passed a real
    string. The first node type that needed an empty one, the component toggle,
    whose `gameEntityReference` carries three, produced a field the game cannot
    read, and a node the game cannot read is a PHASE THAT SILENTLY DOES NOT RUN.

    ArchiveXL still logs "Merged phase", because the file went in; the graph
    just never executes. There is no error anywhere, which cost an afternoon.

    `questkit.scene.cname` has always done this correctly. The two were never
    reconciled.
    """
    return {'$type': 'CName', '$storage': 'string', '$value': v if v else 'None'}


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
            'Header': cr2w.header(PHASE_NAME),
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
# A branch that is decided the moment the token arrives, rather than a wait.
# Socket order is read off `nix_holocall.questphase` node 26.
COND = [('CutDestination', 'CutDestination'), ('In', 'Input'),
        ('True', 'Output'), ('False', 'Output')]
# Order read off the same file, node 14.
CUT = [('CutDestination', 'CutDestination'), ('In', 'Input'),
       ('Out', 'Output'), ('CutSource', 'CutSource')]
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
    # EVERY FIELD IS A UInt32. A fractional `seconds` is a WolvenKit conversion
    # error at build time (2026-09-04), so the fraction goes into
    # `miliseconds`, spelled as the class spells it.
    whole = int(seconds)
    ms = int(round((seconds - whole) * 1000))
    nid = next(NID)
    b.node(nid, 'questPauseConditionNodeDefinition', {'condition': {'@handle': {
        '$type': 'questTimeCondition',
        'type': {'@handle': {'$type': 'questRealtimeDelay_ConditionType',
                             'hours': 0, 'miliseconds': ms, 'minutes': 0, 'seconds': whole}},
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


def add_fade(fade_in, duration):
    """Fade the screen to black, or back from it. The game's own way.

    `questRenderFxManagerNodeDefinition` carrying `questSetFadeInOut_NodeType`,
    read off the shipped quest phases on 2026-09-08.

    **`duration` IS SECONDS AND 0 IS AN INSTANT CUT, not a default.** That
    correction cost a playtest. The two Claire races carry four fades between
    them and every one is `duration` 0, so copying them looked like copying
    vanilla; in play it is a black rectangle appearing and vanishing. Playtest,
    2026-09-08: "no animation, no fade... it seemed a bit abrupt".

    Counting across the 30 shipped phases that use the node settles it: the
    durations are 0, 0.25, 0.3, 0.5, 1, 2, 3 and 4, so the field is a real fade
    time. The prologue's `q101_p2_v_room`, which is V waking up in his own
    apartment, uses 1 second each way, and that is the reference for a fade
    that covers a rest rather than a cut.

    A fade is a PAIR and never a single node. The colour is all zeros, black.

    NEVER PUT A PAUSE BETWEEN THE TWO. A fade-out whose fade-in is waiting on
    something that does not happen is a black screen for the rest of the
    playthrough, which is worse than any beat it was hiding.
    """
    nid = next(NID)
    b.node(nid, 'questRenderFxManagerNodeDefinition', {'type': {'@handle': {
        '$type': 'questSetFadeInOut_NodeType',
        'duration': duration,
        'fadeColor': {'$type': 'Color', 'Alpha': 0, 'Blue': 0, 'Green': 0,
                      'Red': 0},
        'fadeIn': 1 if fade_in else 0,
    }}}, STD)
    return nid


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


def add_addvar(fact, amount=1):
    """Add to a fact instead of setting it, which is how the game counts.

    `setExactValue: 0` on the same node type means "add `value`" rather than
    "make it `value`". Vanilla counts rejected holocalls with exactly this:
    `holo_<contact>_calls_v_rejected_count` is incremented by a node with
    setExactValue 0 and value 1 (`nix_holocall.scene` node 422).
    """
    nid = next(NID)
    b.node(nid, 'questFactsDBManagerNodeDefinition', {'type': {'@handle': {
        '$type': 'questSetVar_NodeType', 'factName': fact, 'setExactValue': 0,
        'value': amount}}}, STD)
    return nid


def add_pause_facts(conditions, operation='AND'):
    """Wait until several fact comparisons hold at once.

    conditions is a list of (factName, value, comparisonType). Vanilla gates
    every holocall on three at a time: the caller's own activate fact, plus
    `holo_setup_active < 1` and `holo_setup_started < 1`, which are the studio's
    mutex. It does it with one questLogicalCondition rather than a chain of
    pause nodes. A chain would pass the first check, wait on the second, and by
    then the first may no longer be true.
    """
    nid = next(NID)
    b.node(nid, 'questPauseConditionNodeDefinition', {'condition': {'@handle': {
        '$type': 'questLogicalCondition',
        'conditions': [{'@handle': {
            '$type': 'questFactsDBCondition',
            'type': {'@handle': {'$type': 'questVarComparison_ConditionType',
                                 'comparisonType': cmp, 'factName': fact,
                                 'value': value}},
        }} for fact, value, cmp in conditions],
        'operation': operation,
    }}}, STD)
    return nid


def add_condition_fact(fact, value=0, cmp='Greater'):
    """A fork decided NOW, on the state of a fact: True and False sockets.

    The difference from add_pause_fact matters and it is not stylistic. A pause
    node ARMS and stays armed until its condition becomes true, so two of them
    off one source is two things that may each fire, at different times, and
    possibly both. A condition node reads the fact once, sends the token down
    exactly one of two sockets, and is finished.

    Anywhere a branch must be taken once and only once, this is the node.
    Vanilla uses it for every such decision in the holocall graph.
    """
    nid = next(NID)
    b.node(nid, 'questConditionNodeDefinition', {'condition': {'@handle': {
        '$type': 'questFactsDBCondition',
        'type': {'@handle': {'$type': 'questVarComparison_ConditionType',
                             'comparisonType': cmp, 'factName': fact, 'value': value}},
    }}}, COND)
    return nid


def add_community(action, reference, entry=None, phase=None):
    """Switch a community, or one entry of it, on or off.

    `questSpawnManagerNodeDefinition` holding a `questCommunityTemplate_NodeType`,
    which is what 1394 shipped questphases use. Read field for field off
    `pop_cct_cpz_phase.questphase`.

    THIS IS HOW A MOD'S OWN NPC IS KEPT AWAY UNTIL THE STORY WANTS HIM.
    `entryActiveOnStart: 0` in the community itself is IGNORED (gotcha 69's
    bench, run 14): a mod's community spawns its entries on save load whatever
    that field says. So the phase does it, and it has to do it three times:

        Deactivate  as the phase's first act, before anything can be seen
        Activate    at the beat that wants him
        Deactivate  once he is done, because community state PERSISTS IN SAVES
                    and without it a reload brings a dead man back alive

    `entry` names one entry; leaving it None addresses the whole community,
    which is what 112 of 133 sampled vanilla uses do. A per-entry action leaves
    the other entries alone, measured on the bench.

    `reference` is written LONG FORM, 105 of vanilla's 159 uses, and it is the
    only form a name this mod ships resolves under (gotcha 34).
    """
    nid = next(NID)
    b.node(nid, 'questSpawnManagerNodeDefinition', {
        'actions': [{
            '$type': 'questSpawnManagerNodeActionEntry',
            'type': {'@handle': {
                '$type': 'questCommunityTemplate_NodeType',
                'action': action,
                'communityEntryName': cname(entry),
                'communityEntryPhaseName': cname(phase),
                'spawnerReference': {'$type': 'NodeRef', '$storage': 'string',
                                     '$value': reference},
            }},
        }],
    }, STD)
    return nid


def add_crowd_null_area(reference, enable):
    """Switch a crowd null area on or off: no crowd-system pedestrians inside it.

    `questCrowdManagerNodeDefinition` holding a
    `questCrowdManagerNodeType_EnableNullArea`, read field for field off node 11
    of sts_std_rcr_01.questphase (enable 1) and node 5 of its openworld phase
    (enable 0), which is how The Union Strikes Back clears the street in front
    of its building and gives it back.

    The area is a `worldCrowdNullAreaNode` in a sector; gig 02 ships its own in
    the cast sector (gen_community.crowd_null_area_node) because the crowd
    outside Afterlife is the crowd SYSTEM, not a community, and no community
    switch touches it (2026-09-04). `reference` is the long-form NodeRef.
    """
    nid = next(NID)
    b.node(nid, 'questCrowdManagerNodeDefinition', {
        'type': {'@handle': {
            '$type': 'questCrowdManagerNodeType_EnableNullArea',
            'areaReference': {'$type': 'NodeRef', '$storage': 'string',
                              '$value': reference},
            'enable': 1 if enable else 0,
        }},
    }, STD)
    return nid


def add_loot_access(reference, entry, accessible, tag=None):
    """Turn the loot interaction on a body on or off.

    `questItemManagerNodeDefinition` holding a
    `questSetLootInteractionAccess_NodeType`: `objectRef` (a gameEntityReference)
    and `accessible`. Read off the RED4ext class layout (2026-09-05); no
    cached vanilla phase uses it, so the field values are the class defaults
    and the reference is the same shape every other quest node addresses a
    community body with (names = entry, reference = community node). With
    `tag`, the reference is by tag instead, which is how the pose lab's
    spawned body is addressed.

    Gig 02 switches the merc's loot off on the tick she falls and on when she
    says to take the shard, so the shard can sit in her pocket from the fall
    without being seen.
    """
    nid = next(NID)
    if tag:
        ref = {'$type': 'gameEntityReference',
               'dynamicEntityUniqueName': cname(None), 'names': [cname(tag)],
               'reference': {'$type': 'NodeRef', '$storage': 'uint64', '$value': '0'},
               'sceneActorContextName': cname(None), 'slotName': cname(None),
               'type': 'Tag'}
    else:
        ref = {'$type': 'gameEntityReference',
               'dynamicEntityUniqueName': cname(None), 'names': [cname(entry)],
               'reference': {'$type': 'NodeRef', '$storage': 'string', '$value': reference},
               'sceneActorContextName': cname(None), 'slotName': cname(None),
               'type': 'EntityRef'}
    b.node(nid, 'questItemManagerNodeDefinition', {'type': {'@handle': {
        '$type': 'questSetLootInteractionAccess_NodeType',
        'objectRef': ref,
        'accessible': 1 if accessible else 0,
    }}}, STD)
    return nid


def add_cut_control():
    """Disarm pause nodes that are still waiting, from somewhere else in the graph.

    THIS IS WHAT MAKES A RACE SAFE. Two pause nodes off one source is two armed
    waits; the first to complete carries the token on, and the OTHER ONE IS
    STILL ARMED. It fires later, in the middle of whatever the winner started,
    and sends a second token down the same chain. A scene entered twice is the
    crash gotcha 51 describes.

    Firing this node cuts every socket its `CutSource` is wired to, and the
    convention is to cut all the racers including the one that won. Vanilla's
    holocall phase does exactly that: one cut node wired to all eight of its
    waits, fired the moment any of them completes.

    `permanent: 0` is vanilla's value, and it is what allows the same waits to
    be re-armed when the graph loops back round to them.
    """
    nid = next(NID)
    b.node(nid, 'questCutControlNodeDefinition', {'permanent': 0}, CUT)
    return nid


def add_pause_node_loaded(node_ref, inverted=False):
    """Wait until a world node is actually streamed in.

    The holocall studio is a `category: Quest` sector: showing its prefab
    variant asks for it, and the sector arrives some frames later. Everything
    aimed at it before then, switching the camera on most of all, is a silent
    no-op against an entity that does not exist yet.

    Vanilla waits here rather than guessing a delay
    (`nix_holocall.scene` node 331, on `#nix_holocall_camera`). It waits FOR
    EVER, though, which is fine for the base game and not for a mod: race this
    against a timeout, or a studio that never arrives is a gig that stops.
    """
    nid = next(NID)
    b.node(nid, 'questPauseConditionNodeDefinition', {'condition': {'@handle': {
        '$type': 'questNodeLoadingCondition',
        'inverted': 1 if inverted else 0,
        'objectRef': noderef(node_ref),
    }}}, STD)
    return nid


def _phone_pickup(caller, addressee, release_on_rejection):
    return {'$type': 'questSystemCondition', 'type': {'@handle': {
        '$type': 'questPhonePickUp_ConditionType',
        'addressee': {'@handle': jpath('gameJournalContact', addressee)},
        'caller': {'@handle': jpath('gameJournalContact', caller)},
        'releaseOnRejection': 1 if release_on_rejection else 0,
    }}}


def add_pause_phone_pickup(caller, addressee, release_on_rejection=False):
    """Wait for the player to answer a call, or, optionally, to decline it.

    **IT DOES NOT COMPLETE FOR A CALL A MOD ISSUES FROM A QUEST PHASE.**
    Measured in play 2026-08-23: the player answered, the game wrote
    `phonecall_<caller>_with_<addressee> = 2` on time, and this never fired.
    Both variants, on a `questCallContact_NodeType` call with our own journal
    contact. Kept because it is vanilla's own node and works in vanilla's own
    scene, so the difference is worth someone else finding; do not build on it
    without watching it fire first. Watch the fact instead: `add_pause_fact`
    on the name PhoneSystem writes. See docs/gotchas.md 58.

    `releaseOnRejection` is the whole of the difference:

        0   completes only when the call is ANSWERED
        1   completes when it is answered OR declined

    Neither completes when the phone simply rings out, so a wait built on these
    alone is a wait that can last for ever. Vanilla races both of them against a
    6 second timer and then re-reads the phone with add_condition_phone_pickup
    to find out what actually happened.

    Read off `base\\quest\\holocalls\\nix\\nix_holocall.scene`, nodes 356, 364
    and 370.
    """
    nid = next(NID)
    b.node(nid, 'questPauseConditionNodeDefinition',
           {'condition': {'@handle': _phone_pickup(caller, addressee,
                                                   release_on_rejection)}}, STD)
    return nid


def add_condition_phone_pickup(caller, addressee):
    """Is this call answered, right now? True or False, decided on arrival.

    Same warning as add_pause_phone_pickup above: unproven for a mod-issued
    call, and its pause-node sibling was measured not to work at all. Read the
    fact with `add_condition_fact` instead.

    The re-read that makes a decline safe. Which branch of a race completed is
    not evidence of what the player did: a declined call reports Rejected and
    then reports Talking about a second and a half later (gotcha 10j), so a
    branch that trusted the event it woke on would be wrong half the time. This
    asks the phone instead, at the moment the answer is needed.

    Vanilla does the same thing in the same place (`nix_holocall.scene` node
    444), which is the reason to trust the shape rather than only the reasoning.
    """
    nid = next(NID)
    b.node(nid, 'questConditionNodeDefinition',
           {'condition': {'@handle': _phone_pickup(caller, addressee, False)}}, COND)
    return nid


def add_race2(src, arm_a, arm_b, claim_fact):
    r"""Two waits, one winner, exactly one token out the other side.

    `src` is a (node, socket) pair that enters both waits. Each arm is a
    (node, in_socket, out_socket) triple. The return is a condition node whose
    **True socket is "arm A won"** and whose False socket is "arm B won".

    THE PROBLEM THIS SOLVES, in the order the three parts of it bite:

    1. The loser stays armed. It completes minutes later, in the middle of
       whatever the winner started, and pushes a second token down the chain.
       add_cut_control fixes that, and it is what vanilla uses.
    2. Which arm woke you is not the same question as what is true now. A
       declined call reports Rejected and then Talking a second and a half
       later. So the answer comes from re-reading, not from the branch: this
       returns a CONDITION node, and the caller is free to ignore the claim and
       ask the world instead.
    3. Two arms can complete on the same frame. The cut lands after the first
       one has already left, so both tokens are in flight and both reach the
       far side. The claim fact closes it: each arm checks the fact is still 0
       before writing its own number, so the second token dies at an
       unconnected socket.

    `claim_fact` MUST be reset to 0 before the race is entered, and a graph
    that loops back through a race has to reset it every time round.
    """
    cut = add_cut_control()
    for arm, mark in ((arm_a, 1), (arm_b, 2)):
        nid, in_sock, out_sock = arm
        b.connect(src, (nid, in_sock))
        gate = add_condition_fact(claim_fact, 0, 'Equal')
        b.connect((nid, out_sock), (gate, 'In'))
        claim = add_setvar(claim_fact, mark)
        b.connect((gate, 'True'), (claim, 'In'))
        b.connect((claim, 'Out'), (cut, 'In'))
        b.connect((cut, 'CutSource'), (nid, 'CutDestination'))
    who = add_condition_fact(claim_fact, 1, 'Equal')
    b.connect((cut, 'Out'), (who, 'In'))
    return who


def add_phone_restriction(apply_restriction, source):
    """Lock or UNLOCK the phone, the way the game's own holocall phase does.

    Measured 2026-08-23, and this node exists because of it. A staged video
    holocall puts two restrictions on the player:

        GameplayRestriction.PhoneCallDeviceActionRestrictions   comes off
        GameplayRestriction.PhoneCall                           WILL NOT

    Removing them as status effects takes the first off and leaves the second,
    through either of the two removal APIs, twice each. And the second is the
    one that stops the player skipping a line: our own Elena call carries
    neither and skips exactly as it always has.

    The reason it will not come off is in the shipped data.
    `base\\quest\\graph_templates\\qb_holocall_initializer.questphase` applies it
    through this node type with `forcedApply: 1` and a NAMED SOURCE
    (`NPC_phonecall`, or `nix_phonecall` in the per-contact copy). A forced,
    sourced restriction is tracked by its source, so removing the record does
    not release it. The game's own release is this node again with
    `applyPhoneRestriction: 0` and the SAME source.

    So the source string is load-bearing: get it wrong and this releases
    nothing, silently. Read it out of the contact's own phase rather than
    guessing.

    `b.node` takes the type as a free string, which is what makes emitting a
    node type this gig has never shipped a matter of getting the fields right
    rather than of the builder supporting it.
    """
    nid = next(NID)
    b.node(nid, 'questPhoneManagerNodeDefinition', {'type': {'@handle': {
        '$type': 'questSetPhoneRestriction_NodeType',
        'applyPhoneRestriction': 1 if apply_restriction else 0,
        'forcedApply': 1,
        'forcedApplySource': cname(source)}}}, STD)
    return nid


def add_prefab_variant(prefab_ref, variant, show=True):
    """Show or hide a variant of a world prefab, the way the game stages a set.

    THIS IS WHAT MAKES A QUEST SECTOR EXIST. Measured 2026-08-23: the holocall
    studio is a `category: Quest` sector with no streaming box, and it does NOT
    load by proximity. Standing 2.8 m from the studio spot, its camera still
    probes 3, "a real entity id, nothing streamed". Spawning a body there does
    not pull it in either; the body renders and the room around it does not.

    Only a quest node does. Vanilla's holocall scene toggles two variants on
    the way in, `#holocalls_studio_lighting` and `#<contact>_holocall_setup`,
    and everything per-contact (the camera, the lookat, the workspot) exists
    because of the second one.

    So a mod that wants the studio without vanilla's call has to toggle them
    itself, and this is the node that does it.

    Both names matter and neither is guessable: the PREFAB is addressed by
    NodeRef and the VARIANT by the name inside it. Read both out of the
    contact's own holocall scene.
    """
    nid = next(NID)
    b.node(nid, 'questWorldDataManagerNodeDefinition', {'type': {'@handle': {
        '$type': 'questTogglePrefabVariant_NodeType',
        'params': [{
            '$type': 'questTogglePrefabVariant_NodeTypeParams',
            'prefabNodeRef': noderef(prefab_ref),
            'variantStates': [{
                '$type': 'questVariantState',
                'name': cname(variant),
                'show': 1 if show else 0,
            }],
        }]}}}, STD)
    return nid


def add_call_contact(caller, addressee, phase, video=True, prefab='#holocalls_studio',
                     rejectable=False, show_avatar=False, restrict=True):
    """Ring the phone from the quest graph, the way the game itself does.

    THIS IS THE FIELD A SCRIPT-ISSUED CALL CANNOT HAVE, and after a day of
    measuring it is the only thing left between this mod and a video feed.

    `questTriggerCallRequest`, which `Gig01_Holocall.reds` queues, carries no
    `prefabNodeRef`. Everything else can now be staged by a mod: the studio
    opens (add_prefab_variant), the camera loads and switches on, a body of
    ours stands on the spot, and a Video call issued from script connects
    WITHOUT crashing, which is what gotcha 10 forbade. What it draws is an
    EMPTY FRAME. Measured 2026-08-23 with every one of those confirmed in the
    same run.

    So the missing piece is not staging. It is telling the phone where the feed
    comes from, and this node is the only thing that does.

    `caller` and `addressee` are JOURNAL PATHS, not CNames, which is what makes
    this usable: `contacts/cc_g01_nix` is as valid here as `contacts/nix`. A
    call issued this way is with OUR contact, so it brings none of the base
    game contact's small talk, in either direction. That is the whole reason
    outgoing calls were dead until now (backlog 3d).

    phase is 'IncomingCall', 'StartCall' or 'EndCall'. Vanilla issues all three
    for one call and sets `applyPhoneRestriction` on every one of them.
    """
    nid = next(NID)
    b.node(nid, 'questPhoneManagerNodeDefinition', {'type': {'@handle': {
        '$type': 'questCallContact_NodeType',
        'addressee': {'@handle': jpath('gameJournalContact', addressee)},
        'applyPhoneRestriction': 1 if restrict else 0,
        'caller': {'@handle': jpath('gameJournalContact', caller)},
        'isRejectable': 1 if rejectable else 0,
        'mode': 'Video' if video else 'Audio',
        'phase': phase,
        'prefabNodeRef': noderef(prefab),
        'showAvatar': 1 if show_avatar else 0,
        'visuals': 'Default',
    }}}, STD)
    return nid


def add_toggle_component(object_ref, component, enable=True):
    """Switch a component on or off on a world entity, from the quest graph.

    Written for the holocall camera, which is the only thing that puts a
    picture on the phone: `RenderToTextureCamera` on the studio's camera node,
    shipped disabled, and this is how vanilla turns it on.

    It can be done from redscript instead (`FindComponentByName(...).Toggle()`,
    proven 2026-08-22) but not from a quest phase without this, and the phase is
    where the rest of the staging lives. Keeping them together means one press
    stages everything instead of a script and a graph having to agree on
    timing.
    """
    nid = next(NID)
    b.node(nid, 'questEntityManagerNodeDefinition', {'type': {'@handle': {
        '$type': 'questEntityManagerToggleComponent_NodeType',
        'params': [{
            '$type': 'questEntityManagerToggleComponent_NodeTypeParams',
            'componentName': cname(component),
            'enable': 1 if enable else 0,
            'isPlayer': 0,
            'objectRef': {
                '$type': 'gameEntityReference',
                'dynamicEntityUniqueName': cname(None),
                'names': [],
                'reference': noderef(object_ref),
                'sceneActorContextName': cname(None),
                'slotName': cname(None),
                'type': 'EntityRef',
            },
        }]}}}, STD)
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


