r"""Return Ticket: the journal resource.

    python tools\gig04\gen_journal.py

The quest, its first objective and its briefing. Modelled on
`tools/gig03/gen_journal.py` and on the stub job in
`tools/fixer01/gen_journal.py`; read those and `docs/journal-research.md` for
the shapes. This header records only what is different here.

THE FIXER IS NOT THIS GIG'S. Hodan Warsame's contact, codex entry and map icon
ship in `mods/fixer-01`, which this gig requires.

HER TEXT HANGS UNDER HER OWN THREAD. ArchiveXL merges a journal by id path:
a container that already exists is descended into, and an entry that does
not is appended to it (`docs/journal-research.md`, "Merge semantics"). So
this file names her contact and her conversation by their own ids and puts
one new message inside. Which of the two journals is merged first is not
ours to decide, so the two containers are written here with HER field values
(avatar, name, title, callable): if this file lands first the contact it
creates is already hers, and her file then descends into it.
`check_fixer()` compares them against her generator's output and stops the
run on any difference. UNPLAYED: no gig here has added a message to another
mod's contact before.

HER FACE ON THE GIG CARD IS A CODEX LINK on the first objective, pointing at
her entry in `codex/characters/fixers`. The journal draws that entry's picture
on the card. Her stub job proved the route, and this is the same link.

THE PINS AND THEIR ANCHORS. A pin hangs off a base-game NodeRef in one of the
three sectors the engine never unloads (docs/map-pins-playbook.md), and the
journal carries the offset from that node to the spot. The first anchors were
found with `tools/find_pin_anchors.py` on 2026-09-30, all in
`always_loaded_2`; the spots are the captures in `tools/gig04/captures/` and
the room's own frame (gig04_config.ROOM_*, tools/gig04/gen_room.py).

THE SHARD'S TEXT IS A JOURNAL ENTRY under onscreens, the shard playbook's
rule: the item record in source/tweaks/shard.yaml points at it, and the
reader shows its title and description.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from questkit.journal import (  # noqa: E402
    configure, wrap, tweak, noderef, lockey, cname,
    description, objective, folder, contact, message, npc_pin, pin_offset,
)
from questkit import cr2w  # noqa: E402

import gig04_config as cfg  # noqa: E402
import gen_community  # noqa: E402
import gen_room  # noqa: E402

QUEST_ID = cfg.QUEST_ID
QUEST_PATH = 'quests/street_stories/' + QUEST_ID
BRIEF_ID = QUEST_ID + '_briefing'

# HER TEXT after the call, with the gig card on it, the way the game's own
# fixers attach the job to the message that describes it. `delay` is seconds
# before it arrives, counted from the moment the quest phase activates it.
MSG_BRIEF = 'cc_g04_msg_brief'
# THE PICTURE ON THE GIG CARD, Ligaya at her stall (gen_photo.py writes the
# record): gig 03's brief carries one the same way, and so do Regina's.
PHOTO = 'UIJournalIcons.cc_g04_ligaya'
MSG_BRIEF_DELAY = 4
MSG_BRIEF_PATH = ('contacts/' + cfg.FIXER_ID + '/' + cfg.FIXER_CONV + '/'
                  + MSG_BRIEF)
# HER LAST CALL AS A TEXT, for a V who did not take it (gen_questphase,
# miss_close): her own spoken lines, the second with the line about Stamps.
MSG_CLOSE = 'cc_g04_msg_close'
MSG_CLOSE_DEAD = 'cc_g04_msg_close_dead'
MSG_CLOSE_PATH = ('contacts/' + cfg.FIXER_ID + '/' + cfg.FIXER_CONV + '/'
                  + MSG_CLOSE)
MSG_CLOSE_DEAD_PATH = ('contacts/' + cfg.FIXER_ID + '/' + cfg.FIXER_CONV + '/'
                       + MSG_CLOSE_DEAD)

# ---------------------------------------------------------------- the pins
#
# THE ANCHORS, base-game nodes in `always_loaded_2`, by the short name an
# always-loaded node is found by, with the position find_pin_anchors.py
# printed for each.
ANCHOR_STALL = '#wat_sm_kab_foodshop_03'
ANCHOR_BOOTH = '#kab_08_spwn'
ANCHOR_ROOM = '#q305_after_quest_sm_homeless_wat_lch_001'
ANCHOR_BAR = '#lch_01_spawnpoint'
# THE CLAWS' VAN: the gig's own marker at its back doors, zero offset, as
# the waiting spot's (gen_community, VAN_MARKER).
ANCHOR_VAN = gen_community.VAN_MARKER_REF
# THE WAY OUT is anchored on the gig's own area node, zero offset, so the
# minimap draws the outline round the room while "leave" is up (gig 03's
# bar; docs/map-pins-playbook.md, "A quest area drawn on the minimap").
AREA_REF = gen_community.AREA_REF
# THE CLUE HUNT on its own drawn area round the three clues.
CLUE_AREA_REF = gen_community.CLUE_AREA_REF
# The community node Bayani's own pin hangs on (questkit.journal.npc_pin).
CAST_REF = gen_community.community.Community.ref(gen_community.SECTOR, 'cc_g04_cast_com')

RAIL_MARKER_REF = gen_community.RAIL_MARKER_REF
ANCHOR_POS = {
    ANCHOR_STALL: (-1234.009770, 1984.539920, 7.970000),
    ANCHOR_BOOTH: (-1220.507080, 1986.650760, 11.981861),
    ANCHOR_ROOM: (-1413.824460, 1537.725710, 18.152161),
    ANCHOR_BAR: (-1414.875980, 1966.201660, 28.136938),
    ANCHOR_VAN: cfg.VAN_PIN,
    RAIL_MARKER_REF: cfg.RAIL_PROMPT,
    AREA_REF: gen_community.area_centre(),
    CLUE_AREA_REF: gen_community.clue_area_centre(),
}

# Where each pin ends up. The pin id is `pin_` + the objective's name after
# `obj_`, which is what questkit.journal.objective builds.
_bx, _by, _ = cfg.ROOM_BAYANI
PIN_POS = {
    'pin_stall': cfg.STALL_LIGAYA[:3],
    'pin_couch': cfg.BOOTH_SHARD,
    'pin_bar': cfg.BAR_STAMPS[:3],
    # The fight starts at his stool, and he no longer runs from it
    # (characters.yaml, NoReaction; audit 2026-10-02: the objective had no
    # marker).
    'pin_beat': cfg.BAR_STAMPS[:3],
    'pin_flop': cfg.VAN_PIN,
    'pin_clues': gen_community.clue_area_centre(),
    'pin_flop_take': cfg.VAN_SHARD,
    # THE DOOR, not the room: the GPS routes to a street address, and the
    # room behind it is the gig's own (tools/gig04/gen_room.py).
    'pin_room': cfg.ROOM_DOOR[:3],
    'pin_bayani': gen_room.room_to_world(_bx, _by),
    # Orbital Air's car on the street, so V in the cell knows where they
    # are (audit 2026-10-02).
    'pin_oa': gen_room.room_to_world(cfg.OA_CARS[0][1], cfg.OA_CARS[0][2])[:2] + (cfg.OA_CARS[0][3],),
    'pin_leave': gen_community.area_centre(),
    # Where his walk to V ends, behind the lobby's opening.
    'pin_bye': gen_room.room_to_world(*cfg.ROOM_BAYANI_BYE[:2]),
    # The waiting spot's marker, which IS the anchor (offset zero, gig 02).
    'pin_wait': cfg.RAIL_PROMPT,
}

# One objective per beat the player has to act on. The third element is the
# pin anchor, and None means no pin.
OBJECTIVES = [
    ('obj_stall', 'obj-stall', ANCHOR_STALL),    # talk to Ligaya at her stall
    # TWO OBJECTIVES FOR EACH SHARD, the shard playbook's rule: a shard
    # offers Take as well as Read, so a player can walk off holding
    # something they have not read. The second carries no pin: by then the
    # shard may be in the backpack and a marker on an empty ledge points at
    # nothing.
    ('obj_couch', 'obj-couch', ANCHOR_BOOTH),    # Stamps's couch, his shard
    ('obj_read', 'obj-read', None),              # read it, wherever
    ('obj_bar', 'obj-bar', ANCHOR_BAR),          # find Stamps at the bar
    ('obj_beat', 'obj-beat', ANCHOR_BAR),        # the fight, at his stool
    ('obj_flop', 'obj-flop', ANCHOR_VAN),        # the false lead: the van
    ('obj_clues', 'obj-clues', CLUE_AREA_REF),   # scan its three clues
    ('obj_flop_take', 'obj-flop-take', ANCHOR_VAN),  # the Claws' shard
    ('obj_flop_read', 'obj-flop-read', None),    # read it
    ('obj_room', 'obj-room', ANCHOR_ROOM),       # go to the Claws' building
    ('obj_bayani', 'obj-bayani', ANCHOR_ROOM),   # find him inside
    ('obj_oa', 'obj-oa', ANCHOR_ROOM),           # Orbital Air at the door
    ('obj_bye', 'obj-bye', ANCHOR_ROOM),         # his goodbye, after the fight
    ('obj_leave', 'obj-leave', AREA_REF),        # get away from the building
    ('obj_wait', 'obj-wait', RAIL_MARKER_REF),   # the railing, then her call
]

# BAYANI'S OWN DOT. An NPC pin (`Mappins.NPCMappinDefinition`, `NPCVariant`,
# the shape of a shipped guard's pin in cooked_journal) on his body, under
# every objective he is about, so the map marks him the way it marks a
# friend and not only while he is the objective (the design call,
# 2026-10-01: "the green dot of friendly"). The quest activates each with
# its objective (gen_questphase.open_objective).
# OFF: in play the pin drew as a red INVALID marker 250 m off (2026-10-01),
# so the body did not resolve through the community reference the way a
# fixer's icon does. Kept as a dict so the quest's opener stays general.
NPC_PINS = {}

# THE COUNTED OBJECTIVE: the van's three clues, "[0/3]" on the tracker.
COUNTERS = {'obj_clues': len(cfg.CLUES)}

# THE SHARDS' TEXT: each item record points at its path through
# `itemSecondaryAction` (source/tweaks/shard.yaml), and Gig04_Shard.reds
# reads each entry's state to know it was taken and read.
SHARD_ID = 'cc_g04_shard_stamps'
SHARD2_ID = 'cc_g04_shard_flop'

configure(lockey_prefix=cfg.LOCKEY_PREFIX, anchor_pos=ANCHOR_POS,
          pin_pos=PIN_POS, no_gps=())


def onscreen(oid, title_key, body_key):
    return wrap({
        '$type': 'gameJournalOnscreen',
        'description': lockey(body_key),
        'iconID': tweak(None),
        'id': oid,
        'journalEntryOverrideDataList': [],
        # tag None and iconID 0 are what the shipped street-story shards use.
        'tag': cname('None'),
        'title': lockey(title_key),
    })


def onscreens():
    """The two things V reads in this gig. The folder classes are not all
    the same and the leaf is a group rather than a folder (gig 03's shape)."""
    group = wrap({
        '$type': 'gameJournalOnscreenGroup',
        'entries': [onscreen(SHARD_ID, 'shard-title', 'shard-body'),
                    onscreen(SHARD2_ID, 'shard2-title', 'shard2-body')],
        'id': 'onscreens',
        'journalEntryOverrideDataList': [],
    })
    return folder('onscreens', [
        folder('emails', [
            folder('quests', [
                folder('street_stories', [folder(QUEST_ID, [group])]),
            ]),
        ]),
    ], primary=True)


def check_fixer():
    """Her ids as this gig's config states them, against her own tools when
    they are in the tree. A drift is a gig card with no face and a counter
    that never moves, both silent."""
    here = os.path.dirname(os.path.abspath(__file__))
    hers = os.path.join(os.path.dirname(here), 'fixer01')
    if not os.path.exists(os.path.join(hers, 'fixer01_config.py')):
        return
    sys.path.insert(0, hers)
    import fixer01_config as fx                                      # noqa: E402
    wrong = []
    if fx.FIXER_ID != cfg.FIXER_ID:
        wrong.append('FIXER_ID %r, hers is %r' % (cfg.FIXER_ID, fx.FIXER_ID))
    if fx.COUNTER_FACT != cfg.FIXER_COUNTER:
        wrong.append('FIXER_COUNTER %r, hers is %r'
                     % (cfg.FIXER_COUNTER, fx.COUNTER_FACT))
    if fx.FACT_PREFIX + 'intro_done' != cfg.FIXER_INTRO_DONE:
        wrong.append('FIXER_INTRO_DONE %r, hers is %r'
                     % (cfg.FIXER_INTRO_DONE, fx.FACT_PREFIX + 'intro_done'))
    if fx.FACT_PREFIX + 'talk_mode' != cfg.FIXER_TALK_MODE:
        wrong.append('FIXER_TALK_MODE %r' % cfg.FIXER_TALK_MODE)
    if wrong:
        raise SystemExit('gig04_config disagrees with fixer01_config: '
                         + '; '.join(wrong))
    # HER CONTACT AND HER THREAD, field for field, against her own generated
    # journal. Children are not compared: hers holds her card, ours our text.
    hers_json = os.path.join(fx.RAW_MOD, 'journal', 'fixer01.journal.json')
    if not os.path.exists(hers_json):
        return
    with open(hers_json, encoding='utf-8') as fh:
        doc = json.load(fh)

    def strip(node):
        return {k: v for k, v in node.items() if k != 'entries'}

    def find(entries, eid):
        for e in entries:
            if e['Data'].get('id') == eid:
                return e['Data']
        raise SystemExit('her journal has no entry %r' % eid)

    root = doc['Data']['RootChunk']['entry']['Data']['entries']
    her_contact = find(find(root, 'contacts')['entries'], cfg.FIXER_ID)
    her_conv = find(her_contact['entries'], cfg.FIXER_CONV)
    mine = fixer_contact()['Data']
    if strip(mine) != strip(her_contact):
        raise SystemExit('her contact differs from the copy in this journal:'
                         ' hers %r, ours %r' % (strip(her_contact), strip(mine)))
    if strip(mine['entries'][0]['Data']) != strip(her_conv):
        raise SystemExit('her conversation differs from the copy in this '
                         'journal: hers %r, ours %r'
                         % (strip(her_conv), strip(mine['entries'][0]['Data'])))


def raw_lockey(key):
    """A LocKey of HERS, written whole: `lockey()` would put this gig's
    prefix on it."""
    return {'unk1': '0', 'value': key}


def fixer_contact():
    """Her contact and her thread, by their own ids and with her own field
    values, holding this gig's one message."""
    c = contact(cfg.FIXER_ID, cfg.FIXER_CONV, 'unused', cfg.FIXER_AVATAR,
                name_key='unused',
                conv_entries=[
                    message(MSG_BRIEF, 'msg-brief', delay=MSG_BRIEF_DELAY,
                            attach_quest=QUEST_PATH, image=PHOTO),
                    message(MSG_CLOSE, 'msg-close', delay=2),
                    message(MSG_CLOSE_DEAD, 'msg-close-dead', delay=2),
                ])
    data = c['Data']
    data['name'] = raw_lockey(cfg.FIXER_NAME_KEY)
    data['isCallableDefault'] = 1
    data['type'] = 'Caller'
    data['entries'][0]['Data']['title'] = raw_lockey(cfg.FIXER_CONV_TITLE_KEY)
    return c


def links_for(oid):
    """Her codex entry on the FIRST objective, which is what puts her face on
    the card. The journal reads the first objective only."""
    if oid == OBJECTIVES[0][0]:
        return [('codex_link_fixer', 'gameJournalCodexEntry', cfg.FIXER_CODEX)]
    return []


def build():
    quest = wrap({
        '$type': 'gameJournalQuest',
        # WATSON: Kabuki, Little China and the walkway west of the market.
        'districtID': 'Districts.Watson',
        'entries': [wrap({
            '$type': 'gameJournalQuestPhase',
            'entries': [objective(o, s, a, links_for(o),
                                  extra=([npc_pin(NPC_PINS[o], CAST_REF, gen_community.BAYANI)]
                                         if o in NPC_PINS else ()),
                                  counter=COUNTERS.get(o, 0))
                        for o, s, a in OBJECTIVES],
            'id': 'phase_main',
            'journalEntryOverrideDataList': [],
            'locationPrefabRef': noderef(None),
        }), description(BRIEF_ID, 'gig-brief')],
        'id': QUEST_ID,
        'journalEntryOverrideDataList': [],
        'recommendedLevelID': tweak(None),
        'title': lockey('gig-title'),
        'type': 'StreetStory',
    })

    quests = wrap({
        '$type': 'gameJournalPrimaryFolderEntry',
        'entries': [folder('street_stories', [quest])],
        'id': 'quests',
        'journalEntryOverrideDataList': [],
    })

    # THE GIG'S ICON ON THE MAP, gig 02's shape (tools/gig02/gen_journal.py).
    # The game's own gigs start in `UndiscoveredPhase` with the variant of
    # their gig type (read off cooked_journal, 2026-10-13: 18
    # ClientInDistress, 20 Thievery, 16 BountyHunt, ...), and the map's label
    # for ClientInDistress is "SOS: Merc Needed" (onscreens,
    # `UI-MappinTypes-ClientinDistress`), which is this gig's type. It stands
    # on Ligaya's stall. The quest switches it on once Hodan's introduction
    # is done; V coming near it is what starts her call (gen_questphase,
    # "THE OFFER").
    poi = wrap({
        '$type': 'gameJournalPrimaryFolderEntry',
        'entries': [wrap({
            '$type': 'gameJournalPointOfInterestGroup',
            'entries': [wrap({
                '$type': 'gameJournalPointOfInterestMappin',
                'dynamicEntityRef': {
                    '$type': 'gameEntityReference',
                    'dynamicEntityUniqueName': cname('None'),
                    'names': [],
                    'reference': noderef(None),
                    'sceneActorContextName': cname('None'),
                    'slotName': cname('None'),
                    'type': 'EntityRef',
                },
                'id': QUEST_ID,
                'journalEntryOverrideDataList': [],
                'mappinData': {
                    '$type': 'gamemappinsPointOfInterestMappinData',
                    'active': 1,
                    'dynamicMappinDef': tweak('Mappins.DynamicPointOfInterestMappinDefinition'),
                    'dynamicMappinRadius': 30,
                    'slotName': cname('UI_Interaction'),
                    'slotOffset': {'$type': 'Vector3', 'X': 0, 'Y': 0, 'Z': 0.5},
                    'staticMappinDef': tweak('Mappins.StaticPointOfInterestMappinDefinition'),
                    'typedVariant': wrap({
                        '$type': 'gamemappinsPhaseVariant',
                        'phase': 'UndiscoveredPhase',
                        'variant': 'ClientInDistressVariant',
                    }),
                },
                'notificationTriggerAreaRef': noderef(None),
                # A POI's anchor field is `staticNodeRef`, the one ArchiveXL
                # reads (gig 02), with the vector to the stall in `offset`.
                'offset': dict(zip(('$type', 'X', 'Y', 'Z'),
                                   ('Vector3',) + pin_offset('pin_stall', ANCHOR_STALL))),
                'questPath': wrap({
                    '$type': 'gameJournalPath',
                    'className': cname('gameJournalQuest'),
                    'editorPath': '',
                    'fileEntryIndex': 0,
                    'realPath': QUEST_PATH,
                }),
                'recommendedLevelID': tweak(None),
                'securityAreaRef': noderef(None),
                'staticNodeRef': noderef(ANCHOR_STALL),
            })],
            'id': 'street_stories',
            'journalEntryOverrideDataList': [],
        })],
        'id': 'points_of_interest',
        'journalEntryOverrideDataList': [],
    })

    contacts = wrap({
        '$type': 'gameJournalPrimaryFolderEntry',
        'entries': [fixer_contact()],
        'id': 'contacts',
        'journalEntryOverrideDataList': [],
    })

    return {
        'Header': cr2w.header('gig04.journal'),
        'Data': {
            'Version': 195, 'BuildVersion': 0,
            'RootChunk': {
                '$type': 'gameJournalResource',
                'cookingPlatform': 'PLATFORM_PC',
                'entry': wrap({
                    '$type': 'gameJournalRootFolderEntry',
                    'entries': [contacts, quests, poi, onscreens()],
                    # THE ROOT FOLDER'S ID IS EMPTY, AND IT HAS TO BE (gotcha
                    # 113): the merge matches ids level by level and the base
                    # game's root is called nothing.
                    'id': '',
                    'journalEntryOverrideDataList': [],
                }),
            },
            'EmbeddedFiles': [],
        },
    }


if __name__ == '__main__':
    check_fixer()
    out_dir = os.path.join(cfg.RAW_MOD, 'journal')
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, 'gig04.journal.json')
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(build(), fh, indent=2)
    print('journal: %d objectives, %d with a pin -> %s'
          % (len(OBJECTIVES), sum(1 for _, _, a in OBJECTIVES if a), path))
