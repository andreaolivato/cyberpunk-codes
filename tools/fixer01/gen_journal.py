r"""Fixer 01: the journal resource. The fixer's map icon, her contact and her
codex entry.

    python tools\fixer01\gen_journal.py

Modelled on `tools/gig03/gen_journal.py`; read that file and
`docs/journal-research.md` for the shapes. This header records what is
different, and all of it is the fixer.

THE MAP ICON IS A POINT OF INTEREST WITH THE FIXER VARIANT. Every gig here
already ships one of these for its own icon (`gameJournalPointOfInterestMappin`
under `points_of_interest/street_stories/<quest>`, `QuestGiverVariant`). The
base game's eight fixer icons are the same entry type under
`points_of_interest/service_points/` with `variant = FixerVariant`, a fixed
spot in `staticNodeRef`, and the fixer's own body in `dynamicEntityRef` so the
icon follows him within `dynamicMappinRadius` (30 m). `wat_fixer` is copied
below field for field, with our names in it.

THE BODY REFERENCE IS THE OPEN QUESTION. The tooltip on the world map asks the
icon which character record it belongs to, and nothing on disk says where
that answer is kept: not the fixed spot (an empty entity in vanilla), not the
cooked table ArchiveXL builds (no such field). The reading is that it comes
from the body in `dynamicEntityRef`, resolved through the community system to
the entry's record. So ours names our community node and entry, the way
`#reggie` / `reggie` names hers. If the tooltip shows the fixer's name and
"0 / 3" on hover, that reading was right. If it shows nothing, the redscript
in source/scripts/Fixer01_Tooltip.reds answers instead (switched on by a fact
from the dev menu, so one build tests both).

THE PORTRAIT ON THE GIG CARD IS A CODEX LINK. The journal takes a gig's first
objective, finds a `gameJournalQuestCodexLink` on it pointing into the group
`codex/characters/fixers`, and draws that entry's `linkImageId` on the gig
card and on the tracked gig's map tooltip. The base game's seven fixers each
have one entry there; ours is merged in beside them, the same way this mod's
contact merges into `contacts/`. This is the first time a codex group has
been merged into; the portrait not appearing on the card is the symptom if
the merge is refused.

THE PORTRAIT IS HERS: an atlas and two records from tools/fixer01/gen_photo.py,
whose header says why a script has to point the picture squares at that
atlas. Johnny's journal picture stood in on the first playtest and drew a
blank square, which is how that was found.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from questkit.journal import (  # noqa: E402
    configure, wrap, cname, tweak, noderef, lockey, vec3,
    contact, folder, message,
)
from questkit import cr2w  # noqa: E402

import fixer01_config as cfg  # noqa: E402
import gen_community  # noqa: E402
import gen_photo  # noqa: E402

FIXER_ID = cfg.FIXER_ID
LOCKEY_PREFIX = cfg.LOCKEY_PREFIX

# ------------------------------------------------------------------- the cast
#
FIXER_CONTACT = FIXER_ID
FIXER_CONV = FIXER_ID + '_conv'
# HER FACE IN THE PHONE. The base game ships 125 avatar records and none is
# hers, so gen_photo.py writes one off her portrait atlas; it was
# `PhoneAvatars.Avatar_Unknown`, gig 02's placeholder for Char, until
# 2026-09-18.
FIXER_AVATAR = gen_photo.AVATAR_RECORD

# HER CARD: the one text after the introduction call, the way the game's own
# fixers follow their call with a welcome text. The quest phase activates it
# once the call has been taken; `delay` is seconds before it arrives, counted
# from that activation (gotcha 3 is why a thread is paced here and not by a
# graph timer).
MSG_CARD = FIXER_ID + '_msg_card'
MSG_CARD_DELAY = 8

# HER PORTRAIT, the two records tools/fixer01/gen_photo.py writes.
PORTRAIT = 'UIJournalIcons.' + FIXER_ID
PORTRAIT_FULL = 'UIJournalIcons.' + FIXER_ID + '_full'

# ----------------------------------------------------------------- the paths
#
# WHERE THE ICON LIVES. Beside the base game's own fixer icons rather than
# under street_stories, because that is where the eight vanilla ones are and
# nothing has been measured about whether the folder matters. The redscript
# fallback hashes this exact path, so gen_journal checks the two agree.
POI_PATH = 'points_of_interest/service_points/' + FIXER_ID
CODEX_PATH = 'codex/characters/fixers/' + FIXER_ID

# THE BODY, as the icon names it: the community node in long form (the only
# form a name this mod ships resolves under, gotcha 34) and the entry name.
CAST_REF = gen_community.build().community_ref
CAST_ENTRY = gen_community.ENTRY

# THE FIXED POINT: the marker gen_community.py ships in the same sector, half
# a metre above his feet. Zero offset, the marker IS the position.
ANCHOR_FIXER = gen_community.MARKER_REF

ANCHOR_POS = {
    ANCHOR_FIXER: gen_community.MARKER_POS,
}

configure(lockey_prefix=LOCKEY_PREFIX, anchor_pos=ANCHOR_POS, pin_pos={},
          no_gps=())


def murmur3_32(data, seed=0x5EEDBA5E):
    """Journal path hash: Murmur3-32 with the RED engine seed. The same
    function the retired cooked-mappin patcher carried, kept here because
    the redscript fallback needs the icon's hash as a constant."""
    key = bytearray(data.encode())
    length = len(key)
    h = seed
    c1, c2 = 0xCC9E2D51, 0x1B873593
    for i in range(length // 4):
        k = int.from_bytes(key[i * 4:i * 4 + 4], 'little')
        k = (k * c1) & 0xFFFFFFFF
        k = ((k << 15) | (k >> 17)) & 0xFFFFFFFF
        k = (k * c2) & 0xFFFFFFFF
        h ^= k
        h = ((h << 13) | (h >> 19)) & 0xFFFFFFFF
        h = (h * 5 + 0xE6546B64) & 0xFFFFFFFF
    tail = key[(length // 4) * 4:]
    k = 0
    if len(tail) >= 3:
        k ^= tail[2] << 16
    if len(tail) >= 2:
        k ^= tail[1] << 8
    if len(tail) >= 1:
        k ^= tail[0]
        k = (k * c1) & 0xFFFFFFFF
        k = ((k << 15) | (k >> 17)) & 0xFFFFFFFF
        k = (k * c2) & 0xFFFFFFFF
        h ^= k
    h ^= length
    h ^= h >> 16
    h = (h * 0x85EBCA6B) & 0xFFFFFFFF
    h ^= h >> 13
    h = (h * 0xC2B2AE35) & 0xFFFFFFFF
    h ^= h >> 16
    return h


POI_HASH = murmur3_32(POI_PATH)


def fixer_poi():
    """`wat_fixer`, field for field, with our names. The one shape difference
    from the gig icons every earlier gig ships is `typedVariant`: a
    `gamemappinsCommonVariant` carrying `FixerVariant`, where a gig icon
    carries `gamemappinsPhaseVariant`."""
    return wrap({
        '$type': 'gameJournalPointOfInterestMappin',
        'dynamicEntityRef': {
            '$type': 'gameEntityReference',
            'dynamicEntityUniqueName': cname('None'),
            'names': [cname(CAST_ENTRY)],
            'reference': noderef(CAST_REF),
            'sceneActorContextName': cname('None'),
            'slotName': cname('None'),
            'type': 'EntityRef',
        },
        'id': FIXER_ID,
        'journalEntryOverrideDataList': [],
        'mappinData': {
            '$type': 'gamemappinsPointOfInterestMappinData',
            'active': 1,
            'dynamicMappinDef': tweak('Mappins.DynamicPointOfInterestMappinDefinition'),
            'dynamicMappinRadius': 30,
            'slotName': cname('UI_Interaction'),
            'slotOffset': vec3(0, 0, 0.5),
            'staticMappinDef': tweak('Mappins.StaticPointOfInterestMappinDefinition'),
            'typedVariant': wrap({
                '$type': 'gamemappinsCommonVariant',
                'variant': 'FixerVariant',
            }),
        },
        'notificationTriggerAreaRef': noderef(None),
        'offset': vec3(0, 0, 0),
        'questPath': None,
        'recommendedLevelID': tweak(None),
        'securityAreaRef': noderef(None),
        'staticNodeRef': noderef(ANCHOR_FIXER),
    })


def fixer_codex():
    """`codex/characters/fixers/dino_dinovic`, in shape. `activatedAtStart`
    is 0 on the vanilla description too; the quest phase activates the entry
    with everything else of his."""
    return wrap({
        '$type': 'gameJournalCodexEntry',
        'entries': [wrap({
            '$type': 'gameJournalCodexDescription',
            'activatedAtStart': 0,
            'id': FIXER_ID + '_desc',
            'journalEntryOverrideDataList': [],
            'subTitle': lockey('codex-subtitle'),
            'textContent': lockey('codex-body'),
        })],
        'id': FIXER_ID,
        'imageId': tweak(PORTRAIT_FULL),
        'journalEntryOverrideDataList': [],
        'linkImageId': tweak(PORTRAIT),
        'title': lockey('fixer-name'),
    })


def build():
    contacts = wrap({
        '$type': 'gameJournalPrimaryFolderEntry',
        'entries': [
            contact(FIXER_CONTACT, FIXER_CONV, 'fixer-conv-title',
                    FIXER_AVATAR, name_key='fixer-name',
                    conv_entries=[
                        message(MSG_CARD, 'msg-card', delay=MSG_CARD_DELAY),
                    ]),
        ],
        'id': 'contacts',
        'journalEntryOverrideDataList': [],
    })
    # V CAN RING HIM. Every vanilla fixer's contact is `isCallableDefault 1`
    # and `type Caller`; the builder's default is a texter who cannot be
    # called, which is right for the earlier gigs' contacts and wrong for a
    # fixer. Nothing answers the call yet: that is a scene, and it is later.
    fixer_contact = contacts['Data']['entries'][0]['Data']
    fixer_contact['isCallableDefault'] = 1
    fixer_contact['type'] = 'Caller'

    poi = wrap({
        '$type': 'gameJournalPrimaryFolderEntry',
        'entries': [wrap({
            '$type': 'gameJournalPointOfInterestGroup',
            'entries': [fixer_poi()],
            'id': 'service_points',
            'journalEntryOverrideDataList': [],
        })],
        'id': 'points_of_interest',
        'journalEntryOverrideDataList': [],
    })

    # THE CODEX TREE, down to the fixers group. Category and group ids are the
    # base game's own so the merge lands inside its group: the tooltip code
    # checks the category is Characters and the group's id is `fixers`.
    # The category and group names are the base game's own LocKeys (read
    # off `codex/characters` and its `fixers` group in the cooked journal),
    # so the merge does not rename either.
    codex = folder('codex', [
        wrap({
            '$type': 'gameJournalCodexCategory',
            'categoryName': {'unk1': '0', 'value': 'LocKey#20667'},
            'entries': [wrap({
                '$type': 'gameJournalCodexGroup',
                'entries': [fixer_codex()],
                'groupName': {'unk1': '0', 'value': 'LocKey#20666'},
                'id': 'fixers',
                'isSorted': 1,
                'journalEntryOverrideDataList': [],
            })],
            'id': 'characters',
            'journalEntryOverrideDataList': [],
        }),
    ], primary=True)

    return {
        'Header': cr2w.header('fixer01.journal'),
        'Data': {
            'Version': 195, 'BuildVersion': 0,
            'RootChunk': {
                '$type': 'gameJournalResource',
                'cookingPlatform': 'PLATFORM_PC',
                'entry': wrap({
                    '$type': 'gameJournalRootFolderEntry',
                    'entries': [contacts, poi, codex],
                    # THE ROOT FOLDER'S ID IS EMPTY, AND IT HAS TO BE. The
                    # merge matches ids level by level and the base game's
                    # root is called nothing; a named root matches nothing
                    # and the file is skipped in silence (gig 03's header).
                    'id': '',
                    'journalEntryOverrideDataList': [],
                }),
            },
            'EmbeddedFiles': [],
        },
    }


def check_reds_hash():
    """The redscript fallback carries POI_HASH as a constant. A drift between
    the two is a fallback that never fires, so the generator refuses to run
    if they disagree."""
    reds = os.path.join(cfg.SOURCE, 'scripts', 'Fixer01_Tooltip.reds')
    if not os.path.exists(reds):
        return
    with open(reds, encoding='utf-8') as fh:
        text = fh.read()
    needle = 'POI_HASH: Uint32 = %du' % POI_HASH
    if needle not in text:
        raise SystemExit('Fixer01_Tooltip.reds does not carry "%s" for %s; '
                         'update the constant' % (needle, POI_PATH))


if __name__ == '__main__':
    check_reds_hash()
    out_dir = os.path.join(cfg.RAW_MOD, 'journal')
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, 'fixer01.journal.json')
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(build(), fh, indent=2)
    print('journal: fixer icon %s (hash %d), codex %s -> %s'
          % (POI_PATH, POI_HASH, CODEX_PATH, path))
