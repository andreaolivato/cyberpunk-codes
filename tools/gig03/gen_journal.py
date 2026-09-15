r"""Acceptable Loss: the journal resource.

    python tools\gig03\gen_journal.py

The quest, its objectives, its briefing paragraph, and Dino's message thread.
Modelled on `tools/gig02/gen_journal.py`; read that file and
`docs/journal-research.md` for the shapes. This header records only what is
different here.

THE PINS AND THEIR ANCHORS. A pin must hang off a base-game NodeRef in one of
the three sectors the engine never unloads, because a quest activates its pins
while the player is on the other side of the city and a node in an ordinary
sector is not there yet. Both anchors below came out of
`tools/find_pin_anchors.py`, which scans only those three sectors, and both
positions are what it read rather than what anyone typed.

The offset from anchor to target is computed by the builder, so the anchor's
distance from the target does not matter. What matters is that its recorded
position is right.

THE THREAD IS SMS, CALL, SMS. Dino texts, V taps a reply which places the
call, and the details arrive as a second message afterwards. That is the shape
Dead Ringer uses and it is what the base game's own fixers do: the spoken part
carries the tone and the written part carries the facts. It matters more here
than it did there, because none of this gig's plot exists in Dino's
recordings and a message is the only place his side of it can be stated.

THE FIXER IS DINO DINOVIC, since 2026-09-15; it was Regina Jones before. The
design call, after reading every fixer's briefs: Regina is the ex-media
crusader who runs the cyberpsycho programme to keep people alive, and a plot
whose fixer shrugs at mercs being farmed fought her on every line. Dino's own
Mausser brief has him ordering a merc killed to placate a corp, his clientele
is corpos, and his rebukes are the ones this gig needed. His texts in the
cooked journal (61 of them, 5 briefs) set the register below: "Yo, V", "detes",
"eds", "preem", "on the down-low", "shoot me a word".

AND THE ARGUMENT AFTER THE SITE IS SMS TOO, and V starts it, BY HAND. Once
V is out of the Badlands and out of the car, the objective says to message
him, and V's two texts are REPLY BUTTONS the player taps, one after the other:
what happened at the site, then what the log says. He answers that the
client wants the data to replicate the results, and V decides on two replies:
bring it, or wipe it.

Playtest, 2026-09-15, on a build where V's texts sent themselves: "the gig
continues without prompt. Not good." Two reply groups back to back is the
game's own shape (94 of its threads do it; Takemura's food thread, Fred's),
and so is a group with two replies (469; the fixers' own gigs use it for
"killed" and "alive"). The quest phase waits on each ENTRY, so it branches on which one
was tapped.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from questkit.journal import (  # noqa: E402
    configure, h, wrap, cname, tweak, noderef, lockey,
    contact, description, message, choice_group, choice, objective, folder,
)
from questkit import cr2w  # noqa: E402

import gig03_config as cfg  # noqa: E402

QUEST_ID = cfg.QUEST_ID
LOCKEY_PREFIX = cfg.LOCKEY_PREFIX

# ------------------------------------------------------------------- the cast
#
# DINO CARRIES HIS REAL FACE. `PhoneAvatars.Avatar_Dino` is a shipped record,
# read out of CET's TweakDB string table with `tools/tweak_names.py` on
# 2026-09-15, the same way Regina's was found. Of the 94 avatars the base
# game ships, his is one, so there is no reason for this gig to show the
# placeholder tile. His own contact in the cooked journal names it.
DINO_CONTACT = 'cc_g03_dino'
DINO_CONV = 'cc_g03_dino_conv'
DINO_AVATAR = 'PhoneAvatars.Avatar_Dino'

# ------------------------------------------------------------- the SMS thread
MSG_01 = 'cc_g03_msg_01'          # he has a job, and it has to be quiet
CHOICE_GROUP = 'cc_g03_ch_01'
CHOICE_CALL = 'cc_g03_ch_01a'     # tapping it places the call
MSG_02 = 'cc_g03_msg_02'          # the brief: where, what, and no trace
# AFTER THE SITE. The trace, the breach and the fact that it leads back to him
# are this gig's own facts, and no recording of his contains any of them. So
# they arrive here, in writing, which is also where the base game puts detail
# this specific.
CHOICE_GROUP_2 = 'cc_g03_ch_02'
CHOICE_RIGGED = 'cc_g03_ch_02a'   # V: rigged, got out with it
CHOICE_GROUP_3 = 'cc_g03_ch_03'
CHOICE_TARGETS = 'cc_g03_ch_03a'  # V: mercs as live targets. Who's the client?
MSG_05 = 'cc_g03_msg_05'          # Dino: doesn't matter. Bring it.
CHOICE_GROUP_4 = 'cc_g03_ch_04'   # THE DECISION, two replies
CHOICE_COMING = 'cc_g03_ch_04a'   # bring it to him
CHOICE_WIPE = 'cc_g03_ch_04b'     # wipe it. The loyal ending
MSG_06 = 'cc_g03_msg_06'          # loyal only: you'll regret this

BRIEF_ID = 'cc_g03_briefing'
BRIEF_PATH = 'quests/street_stories/' + QUEST_ID + '/' + BRIEF_ID

# Counted from the moment the quest phase activates the message, not from any
# clock. A graph timer stalls while a menu is open and the phone IS a menu, so
# pacing a thread from the graph stops it advancing exactly while it is being
# read (gotchas 3).
MSG_DELAY = 3

# ---------------------------------------------------------------- the anchors
#
# TWO PLACES GET A PIN and the middle of the gig gets none. Inside the compound
# the player is finding a room and then a machine, and the base game does not
# pin its own interiors either.
#
# THE COMPOUND. `#ina_05_mp` is 22.3 m from the terminal and sits in
# always_loaded_0. It belongs to the base game's own street story here, which is
# worth knowing but costs nothing: an anchor is a position to measure from, not
# something the pin takes over.
ANCHOR_SITE = '#ina_05_mp'

# DINO'S. `#dyno_sm_default` is the static marker beside the real Dino
# Dinovic's stool at his bar, in always_loaded_1, 9.5 m north of the stool
# itself. The same role `#reggie_sm_default` played for Regina, read out of
# `tools/_anchor_cache/always_loaded_index.json` on 2026-09-15. (A second node
# of the same name sits at 6013, 6114 in always_loaded_2, off the map; the
# index lists both, and this is the one under the city.)
ANCHOR_DINO = '#dyno_sm_default'

# THE BAR AS AN AREA, for the way out: the trigger area gen_community.py
# ships round his stool. A pin on it draws the zone on the minimap while V
# is inside, which is what "leave the bar" wants (gig 02's way out is the
# worked example; docs/map-pins-playbook.md has the recipe).
import gen_community                                                 # noqa: E402
AREA_REF = gen_community.BAR_AREA_REF

ANCHOR_POS = {
    ANCHOR_SITE: (-82.884216, -5223.760740, 95.302239),
    ANCHOR_DINO: (-1967.351, 386.853, 8.041),
    AREA_REF: gen_community.bar_area_position(),
}

# Where each pin must actually end up.
#
# FOUR PINS, and the two inside the compound were missing until 2026-09-10.
# Without them a player is told to find "a terminal" and then "the security
# room" in a walled site with a dozen buildings and no way to know which. The
# base game pins its own objectives inside compounds and so does this.
#
# THE ANCHOR IS THE SAME FOR ALL THREE BADLANDS PINS and that is fine: a pin
# lands at anchor position + offset, and the builder computes the offset, so
# one anchor 22 m from the office serves a target 39 m the other side of it.
# What matters is that the anchor's own recorded position is right.
PIN_POS = {
    # The site itself. On the compound rather than on any one building: the
    # objective is to get there, and the way in is the player's problem.
    'pin_travel': (-101.800, -5215.284, 87.151),
    # The terminal in the north-west corner.
    'pin_terminal': (-133.173, -5193.786, 88.564),
    # The shard on the cabinet in the security room.
    'pin_shard': (-95.621, -5211.431, 87.885),
    # DINO'S STOOL, read out of the sector (gig03_config.DINO_POS).
    'pin_dino': (-1969.884, 377.748, 8.046),
    # THE SAME SPOT, for the loyal ending's objective. A pin is a child of its
    # objective, so a second objective at his bar needs a pin of its own.
    'pin_face': (-1969.884, 377.748, 8.046),
    # THE WAY OUT: a pin ON the area node, zero offset, so the minimap draws
    # the zone rather than a marker. (Regina's was a spot on the street,
    # captured in playtest.)
    'pin_leave': gen_community.bar_area_position(),
}

# One objective per beat the player has to act on, which is the same rule gig 02
# follows. The reading of the three documents is NOT one: the player is at the
# terminal already and that objective would complete itself.
#
# The third element is the pin anchor, and None means no pin.
OBJECTIVES = [
    ('obj_travel', 'obj-travel', ANCHOR_SITE),   # get out to the Badlands site
    ('obj_enter', 'obj-enter', None),            # get inside the wire
    ('obj_terminal', 'obj-terminal', ANCHOR_SITE),  # find the terminal
    ('obj_data', 'obj-data', None),              # read what is on it
    # TWO OBJECTIVES FOR THE SHARD, NOT ONE, which is the shard playbook's rule.
    # The object offers Take as well as Read, so a player can walk away holding
    # something they have not read, and one objective cannot describe both
    # halves. The second carries no pin: by then the shard may be in the
    # backpack and a marker on an empty cabinet points at nothing.
    ('obj_shard', 'obj-shard', ANCHOR_SITE),     # find it in the security room
    ('obj_read', 'obj-read', None),              # read it, wherever they read it
    ('obj_escape', 'obj-escape', None),          # get clear of the compound
    # THE CHASE. The stars stay on until V is out of the Badlands, and this is
    # the objective that says so. No pin: the Badlands is the whole south of
    # the map and every road out of it counts.
    ('obj_badlands', 'obj-badlands', None),      # leave the Badlands
    # ONLY IF V IS STILL IN A VEHICLE when the Badlands line is crossed: the
    # graph reads `cc_g03_mounted` and skips this otherwise. The wording is
    # the base game's own (11 of its quests say "Get out of the car", four
    # "Exit the vehicle"). No pin: it is not a place.
    ('obj_dismount', 'obj-dismount', None),      # get out of the vehicle
    # THE THREAD IS AN OBJECTIVE, in the game's own wording ("Message River
    # about what happened", "Text Claire"): without one the gig sat with
    # nothing on screen until the player thought to open the phone.
    ('obj_brief', 'obj-brief', None),            # message Dino
    # WHILE JOHNNY SPEAKS, on either ending. The design call, 2026-09-15:
    # "Listen to Johnny" (the game's own shape is "Listen to River"; "Talk
    # to Johnny" is its usual wording and was here first). One entry for his
    # line at the decision, and a SECOND for his line at V's door: a journal
    # objective is not reopened once it has succeeded, so each beat gets its
    # own, the way gig 02 numbers its three.
    ('obj_johnny', 'obj-johnny', None),          # listen to Johnny, the decision
    ('obj_johnny_2', 'obj-johnny', None),        # listen to Johnny, V's door
    ('obj_dino', 'obj-dino', ANCHOR_DINO),       # take it to Dino, in person
    # THE LOYAL ENDING'S VERSION of the same trip: V has nothing to hand over
    # and is going to be shouted at. Same pin position, its own entry.
    ('obj_face', 'obj-face', ANCHOR_DINO),       # go and face him
    # AND OUT AGAIN. Putting the game's own Dino back and Johnny's last word
    # both wait until the player is away from the bar, so the player has to
    # be told to go, and the bar is drawn round them while they are in it.
    ('obj_leave', 'obj-leave', AREA_REF),        # get away from his bar
]

# THE SHARD'S TEXT. A shard's words are a journal entry, not an item and not a
# file: the item record points at this path through `itemSecondaryAction`, and
# the reader shows this entry's title and description. See docs/shard-playbook.md
# and source/tweaks/shard.yaml.
SHARD_ID = 'cc_g03_shard_log'


# NO LINKS ON THE OBJECTIVES, checked against the shipped journal rather than
# assumed (2026-09-11): across every street story the objective links are
# codex entries (1,636 of them, background reading) and three Call buttons,
# each on an objective whose action IS "call the fixer". No gig links its own
# brief. This gig's objectives are all places to go and things to do, so a Call
# or a Messages button on them would do nothing for the player. They were
# added and removed the same day; `questkit.journal.codex_link` stays for a
# gig whose objective is to ring somebody.
def links_for(oid):
    return []

configure(lockey_prefix=LOCKEY_PREFIX, anchor_pos=ANCHOR_POS, pin_pos=PIN_POS,
          no_gps=())


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
    """The one thing V reads in this gig. The folder classes are not all the
    same and the leaf is a group rather than a folder; both matter."""
    group = wrap({
        '$type': 'gameJournalOnscreenGroup',
        'entries': [onscreen(SHARD_ID, 'shard-title', 'shard-body')],
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
            contact(DINO_CONTACT, DINO_CONV, 'dino-conv-title',
                    DINO_AVATAR, name_key='dino-name',
                    conv_entries=[
                        message(MSG_01, 'msg-01', delay=MSG_DELAY),
                        choice_group(CHOICE_GROUP, [
                            choice(CHOICE_CALL, 'ch-01a'),
                        ]),
                        # WITH THE GIG CARD, the way his own briefs arrive:
                        # the game's fixers attach the job to the message
                        # that describes it, and the card opens the journal.
                        # AND THE PICTURE, as the card's thumbnail, the way
                        # the real briefs carry one (tools/gig03/gen_photo.py).
                        message(MSG_02, 'msg-02', delay=2,
                                attach_quest='quests/street_stories/' + QUEST_ID,
                                image='UIJournalIcons.cc_g03_site'),
                        # V TEXTS FIRST, twice, and taps to send each one.
                        choice_group(CHOICE_GROUP_2, [
                            choice(CHOICE_RIGGED, 'ch-02a'),
                        ]),
                        choice_group(CHOICE_GROUP_3, [
                            choice(CHOICE_TARGETS, 'ch-03a'),
                        ]),
                        message(MSG_05, 'msg-05', delay=MSG_DELAY),
                        # THE DECISION. Two replies in one group, which is how
                        # the game offers a choice by text.
                        choice_group(CHOICE_GROUP_4, [
                            choice(CHOICE_COMING, 'ch-04a'),
                            choice(CHOICE_WIPE, 'ch-04b'),
                        ]),
                        # Loyal ending only.
                        message(MSG_06, 'msg-06', delay=2),
                    ]),
        ],
        'id': 'contacts',
        'journalEntryOverrideDataList': [],
    })

    quest = wrap({
        '$type': 'gameJournalQuest',
        # BADLANDS, because the job is out there and the compound is the whole
        # middle of the gig. The trip back to Dino is in City Center, and one
        # district has to be picked.
        'districtID': 'Districts.Badlands',
        'entries': [wrap({
            '$type': 'gameJournalQuestPhase',
            'entries': [objective(o, s, a, links_for(o)) for o, s, a in OBJECTIVES],
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

    return {
        'Header': cr2w.header('gig03.journal'),
        'Data': {
            'Version': 195, 'BuildVersion': 0,
            'RootChunk': {
                '$type': 'gameJournalResource',
                'cookingPlatform': 'PLATFORM_PC',
                'entry': wrap({
                    '$type': 'gameJournalRootFolderEntry',
                    'entries': [contacts, quests, onscreens()],
                    # THE ROOT FOLDER'S ID IS EMPTY, AND IT HAS TO BE.
                    #
                    # ArchiveXL merges a mod journal by walking it against the
                    # base game's tree and matching ids at each level. The base
                    # game's root folder is called nothing at all, so a root
                    # called "root" matches nothing and the whole file is
                    # skipped.
                    #
                    # IT FAILS IN COMPLETE SILENCE. There is no error, no
                    # warning, and the archive still loads: the only sign is
                    # that the [Journal] section of ArchiveXL's log has no
                    # "Merging entries from" line for this mod. Shipped for a
                    # day before the shard's title read INVALID and the log was
                    # read properly. Compare against gig 01's or gig 02's, both
                    # of which have always written the empty id.
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
    path = os.path.join(out_dir, 'gig03.journal.json')
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(build(), fh, indent=2)
    print('journal: %d objectives, %d with a pin -> %s'
          % (len(OBJECTIVES), sum(1 for _, _, a in OBJECTIVES if a), path))
