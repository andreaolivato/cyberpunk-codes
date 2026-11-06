r"""Trauma Team: the journal resource.

    python tools\gig05\gen_journal.py

The quest, its objectives and briefing, and the contact that sends the job
ad. Modelled on `tools/gig04/gen_journal.py`; read it and
`docs/journal-research.md` for the shapes. This header records only what is
different.

NO FIXER. The ad comes from a contact of this gig's own, Trauma Team
International, with the game's unknown-caller picture
(`PhoneAvatars.Avatar_Unknown`). It never calls; it exists so the ad has a
sender and the gig card a thread.

EVERY PIN HANGS ON A MARKER OF THE GIG'S OWN with a zero offset, gig 04's
shape (gen_community, the pins' anchors).

THE OBJECTIVES OF A SHIFT ARE REUSED BY EVERY SHIFT. The first shift opens
and closes them in order. A later shift sets them Active again, which no gig
here has done (docs/trauma-team-research.md 3.11); until that is measured,
only the first shift is built.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from questkit.journal import (  # noqa: E402
    configure, wrap, tweak, noderef, lockey,
    description, objective, folder, contact, message,
)
from questkit import cr2w  # noqa: E402

import gig05_config as cfg  # noqa: E402

QUEST_ID = cfg.QUEST_ID
QUEST_PATH = 'quests/street_stories/' + QUEST_ID
BRIEF_ID = QUEST_ID + '_briefing'

CONTACT_ID = 'cc_g05_tti'
CONTACT_CONV = 'cc_g05_tti_conv'
CONTACT_PATH = 'contacts/' + CONTACT_ID
CONV_PATH = CONTACT_PATH + '/' + CONTACT_CONV
MSG_AD = 'cc_g05_msg_ad'
MSG_AD_PATH = CONV_PATH + '/' + MSG_AD
MSG_AD_DELAY = 3
# ONE MESSAGE, ONE PICTURE: the AV on its roof, on the ad's gig card
# (gen_photo.py; the design call, 2026-11-04).
PHOTO_AV = 'UIJournalIcons.cc_g05_av'
# AFTER THE SHIFT: no next shift is built yet, so dispatch says so (the
# design call, 2026-11-03: the objective stayed, with nothing to do).
MSG_DONE = 'cc_g05_msg_done'
MSG_DONE_PATH = CONV_PATH + '/' + MSG_DONE
MSG_REPEAT = 'cc_g05_msg_repeat'
MSG_REPEAT_PATH = CONV_PATH + '/' + MSG_REPEAT

import gen_community as gc  # noqa: E402

# EVERY PIN HANGS ON A MARKER OF THE GIG'S OWN, zero offset (gen_community,
# the pins' anchors). Playtest 2026-11-03: hung off Career Opportunities'
# community node, both pins logged "Can't resolve mappin position" and the
# journal pointed 2 km south.
ANCHOR_POS = {
    gc.RECRUITER_PIN_REF: cfg.RECRUITER[:3],
    gc.LIFT_STOP_REFS[0]: cfg.LIFT_STOPS[0][0],
    gc.LIFT_STOP_REFS[1]: cfg.LIFT_STOPS[1][0],
    gc.PAD_BOARD_REF: cfg.PAD_BOARD,
    gc.LOCKER_REF: cfg.LOCKER,
}
PIN_POS = {
    'pin_recruiter': cfg.RECRUITER[:3],
    'pin_up': cfg.LIFT_STOPS[0][0],
    'pin_down': cfg.LIFT_STOPS[1][0],
    'pin_board': cfg.PAD_BOARD,
    'pin_talk': cfg.PAD_BOARD,
    'pin_change': cfg.LOCKER,
    'pin_back': cfg.LOCKER,
}

# One objective per beat the player acts on. None means no pin: in the air
# V is aboard and a marker would point at the AV under V's feet.
OBJECTIVES = [
    ('obj_recruiter', 'obj-recruiter', gc.RECRUITER_PIN_REF),  # the interview
    ('obj_up', 'obj-up', gc.LIFT_STOP_REFS[0]),                # the way up
    ('obj_change', 'obj-change', gc.LOCKER_REF),               # the locker room
    ('obj_talk', 'obj-talk', gc.PAD_BOARD_REF),                # Brekke, at the AV
    ('obj_board', 'obj-board', gc.PAD_BOARD_REF),              # walk to the AV
    ('obj_ride', 'obj-ride', None),                            # the flight out
    # NO PIN AT A CALL: the AV puts V down beside the client, and a journal
    # pin is one fixed place while there are three calls a shift.
    ('obj_hold', 'obj-hold', None),                            # the fight
    ('obj_board_site', 'obj-board-site', None),                # board again
    ('obj_return', 'obj-return', None),                        # the flight back
    ('obj_down', 'obj-down', gc.LIFT_STOP_REFS[1]),            # the way down
    ('obj_back', 'obj-back', gc.LOCKER_REF),                   # optional, after the shift
    ('obj_wait', 'obj-wait', None),                            # after the shift
]

# EVERY PIN ON THE ROOF IS A MARKER WITH NO ROUTE. The game's route finder has no
# path through the gig's walkway, and after a shift it drew a dotted line that
# went the wrong way (playtest 2026-11-05). The pin to the lift on the street keeps
# its route.
NO_GPS = ('pin_change', 'pin_talk', 'pin_board', 'pin_down', 'pin_back')

configure(lockey_prefix=cfg.LOCKEY_PREFIX, anchor_pos=ANCHOR_POS,
          pin_pos=PIN_POS, no_gps=NO_GPS)


def tti_contact():
    return contact(CONTACT_ID, CONTACT_CONV, 'tti-conv-title',
                   'PhoneAvatars.Avatar_Unknown', name_key='tti-name',
                   conv_entries=[message(MSG_AD, 'msg-ad', delay=MSG_AD_DELAY,
                                         attach_quest=QUEST_PATH, image=PHOTO_AV),
                                 message(MSG_DONE, 'msg-done', delay=4),
                                message(MSG_REPEAT, 'msg-repeat', delay=4)])


def build():
    quest = wrap({
        '$type': 'gameJournalQuest',
        'districtID': 'Districts.Watson',
        'entries': [wrap({
            '$type': 'gameJournalQuestPhase',
            'entries': [objective(o, s, a, optional=1 if o == 'obj_back' else 0) for o, s, a in OBJECTIVES],
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
    contacts = wrap({
        '$type': 'gameJournalPrimaryFolderEntry',
        'entries': [tti_contact()],
        'id': 'contacts',
        'journalEntryOverrideDataList': [],
    })
    return {
        'Header': cr2w.header('gig05.journal'),
        'Data': {
            'Version': 195, 'BuildVersion': 0,
            'RootChunk': {
                '$type': 'gameJournalResource',
                'cookingPlatform': 'PLATFORM_PC',
                'entry': wrap({
                    '$type': 'gameJournalRootFolderEntry',
                    'entries': [contacts, quests],
                    # EMPTY, gotcha 113.
                    'id': '',
                    'journalEntryOverrideDataList': [],
                }),
            },
            'EmbeddedFiles': [],
        },
    }


if __name__ == '__main__':
    out_dir = os.path.join(cfg.RAW_MOD, 'journal')
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, 'gig05.journal.json')
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(build(), fh, indent=2)
    print('journal: %d objectives, %d with a pin -> %s'
          % (len(OBJECTIVES), sum(1 for _, _, a in OBJECTIVES if a), path))
