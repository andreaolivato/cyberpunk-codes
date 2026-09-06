r"""Generates gig02.journal.json: contacts, the opening SMS thread, the gig
quest, its objectives, its map pins, the POI, and the three things V reads.

The builder is tools/questkit/journal.py. This file is the GIG.

TWO THINGS HERE THAT GIG 01 DOES NOT HAVE.

AN SMS THREAD, and it is how the gig opens. The recipe is in
docs/journal-research.md, "Phone messages and reply choices": a message, then a
choice group holding one reply, and the quest phase pauses on the choice ENTRY.
Gig 01 shipped one of these in v0.2.0 and replaced it with a holocall; this gig
opens on a message on purpose, because a message queues and a call does not.
Two mods that both ring the phone collide.

PINS WHOSE ANCHOR IS ALSO THEIR TARGET. Gig 01's pins sit at
`anchor + offset`, where the offset was measured by standing on the spot in
game. Nobody could walk this gig's five sites, so every pin here anchors to a
base-game node that IS the place, and the offset is zero. gig02_config.py
carries which node and why for each of the five.
"""
import json
import os

import sys

# This gig's generators sit in tools/gig02/, and questkit is in tools/, one
# level up. Nothing else puts it on the path. See backlog.md 21.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from questkit.journal import (                                      # noqa: F401
    configure, h, wrap, cname, tweak, noderef, lockey, vec3,
    contact, pin_offset, map_pin, objective, folder,
    message, choice_group, choice, description,
)

from gig02_config import (                                          # noqa: E402
    RAW_MOD, LOCKEY_PREFIX, QUEST_ID, ANCHOR_POS, GROUP_POS, CHAR_POS,
    STAIR, TRASH,
    ANCHOR_AFTERLIFE, ANCHOR_INN, ANCHOR_PARLOR, ANCHOR_OFFICE, ANCHOR_HIT,
)
from questkit import cr2w                                           # noqa: E402
import hit_area                                                     # noqa: E402

# THE WAY-OUT PINS POINT AT THE HIT AREA NODE (test, 2026-09-06): a quest pin
# on a trigger area is what vanilla draws as a dotted area on the minimap
# while the objective is tracked and V is inside. Zero offset: the node sits
# at the area's centroid. See backlog 39 for what the test has to show.
AREA_REF = hit_area.AREA_REF
ANCHOR_POS[AREA_REF] = hit_area.position()

OUT = os.path.join(RAW_MOD, 'journal', 'gig02.journal.json')

# Every pin sits ON its anchor. See the module docstring and gig02_config.py.
PIN_POS = {
    'pin_afterlife': ANCHOR_POS[ANCHOR_AFTERLIFE],
    # THE THREE GROUPS. Walked positions rather than the entrance marker, so
    # these use the anchor-and-offset scheme: the Afterlife marker is the
    # origin and each offset is the vector from it to the spot people stand on.
    # gig02_config.GROUP_POS is the single copy of the numbers.
    'pin_group1': GROUP_POS['group1'],
    'pin_group2': GROUP_POS['group2'],
    'pin_group3': GROUP_POS['group3'],
    # THE ONE PIN WITH A CAPTURED TARGET. Everything else here sits on its
    # anchor because nobody had stood on it; this one was walked to in game, so
    # it uses the scheme gig 01 uses throughout - the anchor is an origin and
    # the offset is the exact vector from it to the spot.
    'pin_inn': (-1179.864, 2037.655, 20.087),
    # Char's chair, 9 m in from Yoko and captured in game.
    'pin_shard': CHAR_POS,
    'pin_parlor': ANCHOR_POS[ANCHOR_PARLOR],
    # Named after the objective it hangs off: questkit derives a pin's id
    # from its objective's, so `obj_wakako_met` owns `pin_wakako_met`.
    'pin_wakako_met': ANCHOR_POS[ANCHOR_OFFICE],
    # THE STAIRCASE. Three pins in sequence down one flight: the top, the trash
    # pile V drops onto, and Toji at the bottom. All captured in game.
    'pin_hit': STAIR[0],
    'pin_toji': STAIR[7],
    # The same spot under the objective that replaces obj_toji once V is
    # seen (2026-09-05).
    'pin_toji_loud': STAIR[7],
    # The way out is the way in: the top of the stairs.
    'pin_exfil': hit_area.position(),
    'pin_exfil_loud': hit_area.position(),
}

# NO PIN TURNS ITS GPS OFF. All five sites are street-level places on the road
# network, so the solver has a real answer for every one of them. Gig 01's
# exceptions were a rock you climb and a room inside a house.
NO_GPS = set()

# id, LocKey suffix, anchor (None = no pin on this objective)
#
# FIFTEEN OBJECTIVES FOR SIXTEEN BEATS, and the split follows one rule: an
# objective must not outlive the thing it describes. Where a beat is a place to
# travel to it gets a pin; where it is a thing to do once you are standing
# there it does not, because a marker on the spot the player is already on
# points at nothing.
OBJECTIVES = [
    # THE FIRST OBJECTIVE IS JOHNNY, 2026-09-03. The gig goes into the journal
    # the moment her brief lands, and the first thing it asks is to hear him
    # out; Afterlife opens when his scene ends. No pin: he is beside V.
    ('obj_johnny',    'obj-johnny',    None),
    # Beat 3.
    ('obj_afterlife', 'obj-afterlife', ANCHOR_AFTERLIFE),
    # Beat 4, three groups, the first two on screen at once.
    ('obj_group1',    'obj-group1',    ANCHOR_AFTERLIFE),
    ('obj_group2',    'obj-group2',    ANCHOR_AFTERLIFE),
    ('obj_group3',    'obj-group3',    ANCHOR_AFTERLIFE),
    # Beat 5. A kill order. He is unkillable until he has begged, and the
    # second objective only exists if the player chose to finish him.
    ('obj_take_out',  'obj-take-out',  None),
    ('obj_kill_merc', 'obj-kill-merc', None),
    # Beat 6. Reading the shard can happen from the inventory.
    # Off his body, through the game's own loot list (2026-09-05).
    ('obj_listen_merc', 'obj-listen-merc', None),
    ('obj_get_shard', 'obj-get-shard', None),
    ('obj_decide',    'obj-decide',    None),
    ('obj_proof',     'obj-proof',     None),
    # Beat 7. THE REPORT IS A TEXT MESSAGE: V picks a reply in the thread and
    # Wakako answers by message. No call, no voice.
    ('obj_report',    'obj-report',    None),
    # Johnny again, the moment the reply is sent (2026-09-04).
    ('obj_johnny_2',  'obj-johnny',    None),
    # Beat 8.
    ('obj_inn',       'obj-inn',       ANCHOR_INN),
    # Beat 9, in two objectives: hand the shard to Char, then wait for her
    # message. There is no second visit to the chair; the verdict is a text.
    ('obj_shard',     'obj-shard',     ANCHOR_INN),
    ('obj_wait',      'obj-wait',      None),
    # Beat 10.
    ('obj_parlor',    'obj-parlor',    ANCHOR_PARLOR),
    # Beat 11, in three: scan, pull out, crack. THE PIN IS ON THE PARLOR AND
    # NEVER ON THE MACHINE. Cracking the relay is also where the face comes
    # from now: its note carries the servicing record, so there is no
    # attendant and no camera log any more.
    # Beat 11 is ONE objective since 2026-09-05: breach the access point on
    # the parlor's wall. Then Char's answer by text.
    ('obj_relay',     'obj-relay',     None),
    ('obj_send_dump', 'obj-send-dump', None),
    ('obj_wait2',     'obj-wait',      None),
    ('obj_reply_char', 'obj-reply-char', None),
    # Beat 13.
    ('obj_wakako_met', 'obj-wakako-met', ANCHOR_OFFICE),
    # Beats 14-16.
    ('obj_hit',       'obj-hit',       ANCHOR_HIT),
    ('obj_toji',      'obj-toji',      ANCHOR_HIT),
    ('obj_toji_loud', 'obj-toji-loud', ANCHOR_HIT),
    ('obj_exfil',     'obj-exfil',     AREA_REF),
    ('obj_exfil_loud', 'obj-exfil-loud', AREA_REF),
    # Beat 17 (design call 2026-09-06): the call home and Johnny's last word
    # are objectives too, so the journal never sits empty while they play.
    ('obj_call_wakako', 'obj-call-wakako', None),
    # obj_johnny and obj_johnny_2 are the earlier beats; a third id, or the
    # journal shows two entries under one name (playtest 2026-09-06).
    ('obj_johnny_3',   'obj-johnny',     None),
]

# ------------------------------------------------------------- the two reads
#
# Both are gameJournalOnscreen entries, which is what a shard's text IS. See
# docs/shard-playbook.md and Gig02_Shard.reds; the mechanism is four lines of
# `readAction.swift` and needs no TweakDB item to raise.
#
# THE PROOF is a real item as well, because Wakako asks V to carry it to her
# netrunner, so it has to exist in the inventory. THE CAMERA LOG is not: it is
# a laptop on a counter that belongs to the parlor, and V reads it where it
# lies.
SHARD_ID = 'cc_g02_shard_note'
ONSCREEN_BASE = ('onscreens/emails/quests/street_stories/' + QUEST_ID
                 + '/onscreens/')
SHARD_PATH = ONSCREEN_BASE + SHARD_ID

# --------------------------------------------------------------- the contacts
#
# BOTH ARE THE MOD'S OWN, carrying the same display names and avatars as the
# base game's. docs/scene-playbook.md is explicit about why: a mod cannot make
# V call a base-game contact, because that contact's own default conversation
# owns the outgoing direction and a mod cannot branch a base-game scene. Ringing
# a contact this mod merged in has no such conversation behind it.
WAKAKO_CONTACT = 'cc_g02_wakako'
WAKAKO_CONV = 'cc_g02_wakako_conv'
CHAR_CONTACT = 'cc_g02_char'
CHAR_CONV = 'cc_g02_char_conv'

# WAKAKO'S AVATAR IS THE REAL ONE. `PhoneAvatars.Avatar_Wakako` is a shipped
# record, confirmed by decompressing CET's TweakDB string table on 2026-08-26
# (docs/gameplay-restrictions.md, "Reproducing the list").
WAKAKO_AVATAR = 'PhoneAvatars.Avatar_Wakako'

# CHAR IS INVENTED, so she carries the placeholder tile. The base game ships
# 125 avatar records and none is hers, and authoring one is separate work.
CHAR_AVATAR = 'PhoneAvatars.Avatar_Unknown'

# ------------------------------------------------------------- the SMS thread
#
# Two entries, and only two. The message is Wakako's, verbatim from design.md;
# the reply is the player's, and picking it is what places the call.
MSG_01 = 'cc_g02_msg_01'
CHOICE_GROUP = 'cc_g02_ch_01'
CHOICE_CALL = 'cc_g02_ch_01a'
# THE REPORT, 2026-09-03. After the merc, V tells Wakako what the shard says by
# picking a reply, and she answers by message with the netrunner's location.
# This used to be a video call, and none of its nine lines existed in her
# voice; a text is also what she does in her own gigs.
CHOICE_GROUP_2 = 'cc_g02_ch_02'
CHOICE_REPORT = 'cc_g02_ch_02a'
MSG_02 = 'cc_g02_msg_02'
# The spared-her variants (2026-09-05).
CHOICE_GROUP_3 = 'cc_g02_ch_03'
CHOICE_REPORT_B = 'cc_g02_ch_03a'
MSG_02B = 'cc_g02_msg_02b'
# CHAR'S VERDICT, half an hour after the handover, as a message. There is no
# second visit to the chair.
MSG_03 = 'cc_g02_msg_03'
# THE RELAY'S UPLOAD (2026-09-05): her acknowledgement, then the man's name.
MSG_05 = 'cc_g02_msg_05'
MSG_06 = 'cc_g02_msg_06'
MSG_07 = 'cc_g02_msg_07'
MSG_08 = 'cc_g02_msg_08'
# V's reply to the verdict, a pick in Char's thread.
CHOICE_GROUP_4 = 'cc_g02_ch_04'
CHOICE_REPLY_CHAR = 'cc_g02_ch_04a'
# V sends the relay dump: a pick before her "Got the dump".
CHOICE_GROUP_5 = 'cc_g02_ch_05'
CHOICE_SEND_DUMP = 'cc_g02_ch_05a'
# THE BRIEF, 2026-09-03. She says "I am attaching more information" on the
# call, and this is the attachment: her message after the phone is down, and
# the same premise as the journal's briefing paragraph. It is the one place the
# premise is stated, because no recording of hers or V's states it.
MSG_04 = 'cc_g02_msg_04'
# The details after the office (2026-09-06): name, place, the rule.
MSG_09 = 'cc_g02_msg_09'
BRIEF_ID = 'cc_g02_briefing'
BRIEF_PATH = 'quests/street_stories/' + QUEST_ID + '/' + BRIEF_ID

# DELAY 3 SECONDS, counted from the moment the quest phase activates the
# message. The gig's start trigger already waits for a moment when the phone is
# usable, so this is a beat rather than a gate.
MSG_DELAY = 3


configure(lockey_prefix=LOCKEY_PREFIX, anchor_pos=ANCHOR_POS, pin_pos=PIN_POS,
          no_gps=NO_GPS)


def onscreen(oid, title_key, body_key):
    return wrap({
        '$type': 'gameJournalOnscreen',
        'description': lockey(body_key),
        'iconID': tweak(None),
        'id': oid,
        'journalEntryOverrideDataList': [],
        # tag None and iconID 0 are what the shipped street-story shards use.
        # The tags ('world', 'notes', 'articles') only apply to the generic
        # collectible shards under onscreens/emails/generic/shards.
        'tag': cname('None'),
        'title': lockey(title_key),
    })


def onscreens():
    """The one piece of text V reads, as the journal entry the vanilla shard
    reader reads. The relay's note was the second until 2026-09-05."""
    group = wrap({
        '$type': 'gameJournalOnscreenGroup',
        'entries': [
            onscreen(SHARD_ID, 'shard-title', 'shard-body'),
        ],
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


def build():
    contacts = wrap({
        '$type': 'gameJournalPrimaryFolderEntry',
        'entries': [
            contact(WAKAKO_CONTACT, WAKAKO_CONV, 'wakako-conv-title',
                    WAKAKO_AVATAR, name_key='wakako-name',
                    conv_entries=[
                        message(MSG_01, 'msg-01', delay=MSG_DELAY),
                        choice_group(CHOICE_GROUP, [
                            choice(CHOICE_CALL, 'ch-01a'),
                        ]),
                        choice_group(CHOICE_GROUP_2, [
                            choice(CHOICE_REPORT, 'ch-02a'),
                        ]),
                        message(MSG_02, 'msg-02', delay=2),
                        choice_group(CHOICE_GROUP_3, [
                            choice(CHOICE_REPORT_B, 'ch-02b'),
                        ]),
                        message(MSG_02B, 'msg-02b', delay=2),
                        message(MSG_04, 'msg-04', delay=1),
                        message(MSG_09, 'msg-09', delay=MSG_DELAY),
                    ]),
            contact(CHAR_CONTACT, CHAR_CONV, 'char-conv-title',
                    CHAR_AVATAR, name_key='char-name',
                    conv_entries=[
                        message(MSG_03, 'msg-03', delay=MSG_DELAY),
                        choice_group(CHOICE_GROUP_5, [
                            choice(CHOICE_SEND_DUMP, 'ch-05a'),
                        ]),
                        message(MSG_05, 'msg-05', delay=2),
                        message(MSG_06, 'msg-06', delay=2),
                        message(MSG_07, 'msg-07', delay=6),
                        message(MSG_08, 'msg-08', delay=5),
                        choice_group(CHOICE_GROUP_4, [
                            choice(CHOICE_REPLY_CHAR, 'ch-04a'),
                        ]),
                    ]),
        ],
        'id': 'contacts',
        'journalEntryOverrideDataList': [],
    })

    quest = wrap({
        '$type': 'gameJournalQuest',
        # WESTBROOK, because four of the five sites are in Japantown and the
        # gig is Wakako's. The Afterlife and Dewdrop Inn legs are trips out.
        'districtID': 'Districts.Westbrook',
        'entries': [wrap({
            '$type': 'gameJournalQuestPhase',
            'entries': [objective(o, s, a) for o, s, a in OBJECTIVES],
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
        'entries': [wrap({
            '$type': 'gameJournalFolderEntry',
            'entries': [quest],
            'id': 'street_stories',
            'journalEntryOverrideDataList': [],
        })],
        'id': 'quests',
        'journalEntryOverrideDataList': [],
    })

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
                    'slotOffset': vec3(),
                    'staticMappinDef': tweak('Mappins.StaticPointOfInterestMappinDefinition'),
                    'typedVariant': wrap({
                        '$type': 'gamemappinsPhaseVariant',
                        'phase': 'UndiscoveredPhase',
                        'variant': 'BountyHuntVariant',
                    }),
                },
                'notificationTriggerAreaRef': noderef(None),
                # A POI's anchor field is `staticNodeRef`, NOT `reference`:
                # that is the one ArchiveXL reads. It lands on the parlor,
                # which is the building the whole gig is about.
                'offset': vec3(*pin_offset('pin_parlor', ANCHOR_PARLOR)),
                'questPath': wrap({
                    '$type': 'gameJournalPath',
                    'className': cname('gameJournalQuest'),
                    'editorPath': '',
                    'fileEntryIndex': 0,
                    'realPath': 'quests/street_stories/' + QUEST_ID,
                }),
                'recommendedLevelID': tweak(None),
                'securityAreaRef': noderef(None),
                'staticNodeRef': noderef(ANCHOR_PARLOR),
            })],
            'id': 'street_stories',
            'journalEntryOverrideDataList': [],
        })],
        'id': 'points_of_interest',
        'journalEntryOverrideDataList': [],
    })

    return {
        'Header': cr2w.header('gig02.journal'),
        'Data': {
            'Version': 195, 'BuildVersion': 0,
            'RootChunk': {
                '$type': 'gameJournalResource',
                'cookingPlatform': 'PLATFORM_PC',
                'entry': wrap({
                    '$type': 'gameJournalRootFolderEntry',
                    'entries': [contacts, quests, poi, onscreens()],
                    'id': '',
                    'journalEntryOverrideDataList': [],
                }),
            },
            'EmbeddedFiles': [],
        },
    }


if __name__ == '__main__':
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(build(), fh, indent=2)
    print('wrote %s' % OUT)
    print('objectives: %d, pins: %d'
          % (len(OBJECTIVES), sum(1 for _, _, a in OBJECTIVES if a)))
