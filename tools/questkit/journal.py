r"""Journal builder: contacts, quests, objectives, map pins, POI.

The reusable half of the journal pipeline. A mod supplies its own anchor and
target tables, its own LocKey prefix and its own journal tree; everything here
is the CR2W shape those tables get poured into.

THE MAP-PIN RULES, because they are the reason this file is worth reusing
(docs/map-pins-playbook.md):

  * a pin must be ACTIVATED by the quest phase; activating its objective is
    not enough. An
    inactive pin is invisible and every downstream layer then looks broken;
  * pin.reference must be a base-game NodeRef in an ALWAYS-LOADED sector,
    because a quest activates its pins while the player is across the city;
  * pin.offset is the exact vector from that node to the target. pin_offset()
    computes it, so the anchor's distance from the target does not matter.

The position is then computed by ArchiveXL at load time. Nothing is patched
into a base-game file.
"""
import json  # noqa: F401
import os    # noqa: F401

# --------------------------------------------------------------- per-mod config
LOCKEY_PREFIX = ''
ANCHOR_POS = {}
PIN_POS = {}
NO_GPS = frozenset()


def configure(lockey_prefix, anchor_pos, pin_pos, no_gps=()):
    """Point the builder at one mod's naming and its pin tables.

    lockey_prefix  e.g. 'cc-g01-'. Bare keys, no 'LocKey#': ArchiveXL hashes
                   them and matches the mod's own onscreens resource.
    anchor_pos     {NodeRef: (x, y, z)} world positions of the pin anchors,
                   read out of the always-loaded sectors. LOAD-BEARING: a wrong
                   value here is a wrong pin.
    pin_pos        {pin_id: (x, y, z)} where each pin must actually end up.
    no_gps         pin ids that should NOT route the player. Of 4277 vanilla
                   quest pins, 131 turn GPS off.
    """
    global LOCKEY_PREFIX, ANCHOR_POS, PIN_POS, NO_GPS
    LOCKEY_PREFIX = lockey_prefix
    ANCHOR_POS = anchor_pos
    PIN_POS = pin_pos
    NO_GPS = frozenset(no_gps)


_handle = [0]


def h():
    _handle[0] += 1
    return str(_handle[0])


def wrap(data):
    return {'HandleId': h(), 'Data': data}


def cname(v):
    return {'$type': 'CName', '$storage': 'string', '$value': v}


def tweak(v):
    if v is None:
        return {'$type': 'TweakDBID', '$storage': 'uint64', '$value': '0'}
    return {'$type': 'TweakDBID', '$storage': 'string', '$value': v}


def noderef(v):
    if v is None:
        return {'$type': 'NodeRef', '$storage': 'uint64', '$value': '0'}
    return {'$type': 'NodeRef', '$storage': 'string', '$value': v}


def lockey(suffix):
    # No 'LocKey#' prefix: ArchiveXL hashes bare keys and matches our onscreens.
    return {'unk1': '0', 'value': LOCKEY_PREFIX + suffix}


def vec3(x=0.0, y=0.0, z=0.5):
    return {'$type': 'Vector3', 'X': x, 'Y': y, 'Z': z}


def contact(cid, conv_id, conv_title, avatar, name_key=None):
    # name_key exists because the default derives the LocKey from the id, and
    # cc_g01_nix would derive 'cc-g01-cc-g01-nix-name'. See the note by that
    # contact for why its id is prefixed at all.
    return wrap({
        '$type': 'gameJournalContact',
        'avatarID': tweak(avatar),
        'entries': [wrap({
            '$type': 'gameJournalPhoneConversation',
            'entries': [],
            'id': conv_id,
            'journalEntryOverrideDataList': [],
            'title': lockey(conv_title),
        })],
        'id': cid,
        'isCallableDefault': 0,
        'journalEntryOverrideDataList': [],
        'name': lockey(name_key or (cid.replace('_', '-') + '-name')),
        'type': 'Texter',
        'useFlatMessageLayout': 1,
    })


def pin_offset(pin_id, anchor):
    """Exact vector from the anchor node to the target. ArchiveXL adds it."""
    tx, ty, tz = PIN_POS[pin_id]
    ax, ay, az = ANCHOR_POS[anchor]
    return (round(tx - ax, 4), round(ty - ay, 4), round(tz - az, 4))


def map_pin(pin_id, anchor):
    off = pin_offset(pin_id, anchor)
    return wrap({
        '$type': 'gameJournalQuestMapPin',
        'enableGPS': 0 if pin_id in NO_GPS else 1,
        'entries': [],
        'id': pin_id,
        'journalEntryOverrideDataList': [],
        'mappinData': {
            '$type': 'gamemappinsMappinData',
            'active': 1,
            'debugCaption': '',
            'localizedCaption': lockey('pin-' + pin_id.replace('_', '-')),
            'mappinType': tweak('Mappins.QuestStaticMappinDefinition'),
            'scriptData': None,
            'variant': 'QuestGiverVariant',
            'visibleThroughWalls': 1,
        },
        'offset': vec3(*off),
        'reference': {
            '$type': 'gameEntityReference',
            'dynamicEntityUniqueName': cname('None'),
            'names': [],
            'reference': noderef(anchor),
            'sceneActorContextName': cname('None'),
            'slotName': cname('None'),
            'type': 'EntityRef',
        },
        'slotName': cname('UI_Interaction'),
        'uiAnimation': tweak(None),
    })


def objective(oid, suffix, anchor):
    children = []
    if isinstance(anchor, list):
        # An explicit list of (pin_id, anchor). Used where one objective owns
        # several pins that are revealed in sequence - see obj_wayin.
        children = [map_pin(pid, a) for pid, a in anchor]
    elif anchor:
        children.append(map_pin('pin_' + oid.replace('obj_', ''), anchor))
    return wrap({
        '$type': 'gameJournalQuestObjective',
        'counter': 0,
        'description': lockey(suffix),
        'districtID': '',
        'entries': children,
        'id': oid,
        'itemID': tweak(None),
        'journalEntryOverrideDataList': [],
        'locationPrefabRef': noderef(None),
        'optional': 0,
    })


def folder(fid, entries, primary=False):
    return wrap({
        '$type': ('gameJournalPrimaryFolderEntry' if primary
                  else 'gameJournalFolderEntry'),
        'entries': entries,
        'id': fid,
        'journalEntryOverrideDataList': [],
    })

