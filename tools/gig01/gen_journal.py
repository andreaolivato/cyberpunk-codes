"""Generates gig01.journal.json, contacts, gig quest, objectives, pins, POI.

Replaces the hand-patched journal. Everything the gig needs is described by the
tables at the top; the builder emits the CR2W-shaped JSON WolvenKit expects.

Map-pin rules (see docs/map-pins-playbook.md):
  * pins must be ACTIVATED by the quest phase, not just their objective;
  * pin.reference must be a base-game NodeRef in an ALWAYS-LOADED sector, and
    pin.offset is the exact vector from that node to the target;
  * the position is then computed by ArchiveXL, not patched into a game file.
"""
import json
import os

import sys

# This gig's generators sit in tools/gig01/, and questkit is in tools/, one
# level up. Nothing else puts it on the path. See backlog.md 21.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# The builder lives in tools/questkit/journal.py. This file is the GIG: its pin
# anchors, its objectives, its contacts and its shard text.
from questkit.journal import (                                      # noqa: F401
    configure, h, wrap, cname, tweak, noderef, lockey, vec3,
    contact, pin_offset, map_pin, objective, folder,
)

_TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(_TOOLS)
OUT = os.path.join(REPO, 'mods', 'gig-01-negative-balance', 'source', 'wkit', 'raw',
                   'mod', 'negative_balance', 'journal', 'gig01.journal.json')

QUEST_ID = 'cc_g01_negative_balance'

# ---------------------------------------------------------------- PIN ANCHORS
# EVERY ANCHOR HERE LIVES IN AN **ALWAYS-LOADED** BASE-GAME SECTOR, and that one
# property is the whole reason the pins work without patching a game file.
#
# ArchiveXL computes a pin's position as `GetNodeTransform(anchor) + offset`.
# `GetNodeTransform` needs the node to exist AS AN INSTANCE - its sector must be
# streamed in. The anchors this file used before were ordinary exterior nodes
# that only stream in when the player is nearby, so every pin failed with
#
#     [Journal] Can't resolve mappin #1684563311 (.../pin_office) position.
#
# ("position", not "reference": the name resolved, the node was not there).
# A quest activates its pins while V is across the city, so that route can never
# place a pin you have not already walked to.
#
# Night City has exactly THREE sectors the engine never unloads -
# `always_loaded_0/1/2.streamingsector`, `category: AlwaysLoaded`, float-max
# streaming box - and they hold 5211 globally-named nodes between them. Every
# pin in this gig has one within 53 m, most within 30 m. Distance is irrelevant
# anyway: the offset below is exact, so the anchor is a fixed origin, not an
# approximation.
#
# HOW TO FIND MORE (gigs 02-04). Do NOT use tools/find_pin_anchors.py - it scans
# `exterior_*` sectors, which is the wrong set. Instead:
#   WolvenKit.CLI unbundle basegame_3_nightcity.archive -w "*always_loaded_*.streamingsector"
#   WolvenKit.CLI convert serialize <each>
# then scan the JSON for nodeData entries whose QuestPrefabRefHash ends in a
# '#name', and take the nearest to your target.
#
# TWO ROUTES WERE TRIED AND FAILED FIRST, both on 2026-08-14; neither is worth
# revisiting. Ordinary base-game anchors fail as above. Shipping our OWN marker
# nodes fails harder - `Can't resolve ... reference`, the name never registers -
# and **playtesting confirmed Californication and OneMoreLight, which do exactly
# that, have broken pins in game too.** They were never the precedent they
# looked like. See docs/architecture.md.
ANCHOR_OFFICE = '#q112_mp_truck_drive_inside'
ANCHOR_TERMINAL = '#q112_05_sm_infiltration'
ANCHOR_SHARD = '#q112_06_sm_warehouse'
ANCHOR_ESTATE = '#q113_03a_sm_haru_kasai_drive_gate'
ANCHOR_ESTATE_MECH = '#q113_estate_mech_movement'
ANCHOR_HANAKO_AV = '#q113_spwn_estate_hanako_av'
ANCHOR_COYOTE = '#coyote_performance_test'
ANCHOR_VICTOR = '#sq018_03b_sm_victor'

# Their world positions, read out of the always-loaded sectors. Load-bearing:
# the pin lands at ANCHOR_POS + offset, so a wrong value here is a wrong pin.
ANCHOR_POS = {
    ANCHOR_OFFICE: (-209.256683, -1454.215090, 7.599944),
    ANCHOR_TERMINAL: (-258.917847, -1484.295040, 7.800000),
    ANCHOR_SHARD: (-264.817932, -1427.495120, 10.300000),
    ANCHOR_ESTATE: (381.207214, 1161.728150, 220.800018),
    ANCHOR_ESTATE_MECH: (320.575073, 1062.156860, 225.929230),
    ANCHOR_HANAKO_AV: (286.031494, 1019.350890, 224.945816),
    ANCHOR_COYOTE: (-1259.712520, -988.872009, 12.037246),
    ANCHOR_VICTOR: (-1258.780270, -1000.007810, 12.037331),
}

# Where each pin must actually end up. The generator subtracts the anchor.
PIN_POS = {
    'pin_office': (-189.371, -1464.500, 7.596),     # compound entry
    'pin_terminal': (-251.915, -1456.364, 14.600),  # office terminal (ledger)
    # The shard on the office desk (comic p23), placed by tools/gig01/gen_sector.py.
    # NOTE a pre-existing 0.9 m disagreement with gen_sector's SHARD_POS
    # (-245.654, -1454.667, 15.400); this is the value that has been shipping.
    'pin_shard': (-244.931, -1454.178, 15.400),
    'pin_estate': (384.181, 1164.724, 220.643),     # Arasaka estate gate
    # THE WAY IN HAS NO JOURNAL PIN AT ALL, WHICH IS THE FIX.
    #
    # It had one (at 273.981, 1084.395, 215.158 - which was the FOOT of the
    # climb, not the way in), then briefly six, one per waypoint, with five held
    # Inactive. playtesting covered that and photographed all six on screen:
    # **setting a quest map pin's entry Inactive does not remove it.** Vanilla
    # never tries - 288 shipped objectives carry two pins and one carries 28,
    # and routes like `q104_02_av_chase/follow_tracks` (six waypoints) show them
    # all at once.
    #
    # So the way-in marker is a runtime mappin owned by Gig01_Encounter
    # (ShowWayInMarker), registered straight at a world position and moved up
    # the hill as V reaches each waypoint. The waypoints live in that file, in
    # CCGig01Places.WayInPoint - there is nothing for this table to hold.
    'pin_hoshino': (300.102, 1054.556, 229.928),    # where Hoshino waits
    'pin_malware': (284.852, 1023.697, 224.928),    # his terminal
    'pin_epilogue': (-1259.598, -989.166, 12.037),  # El Coyote Cojo
    'pin_bar': (-1258.193, -999.521, 12.037),       # the stools
}

# id, LocKey suffix, anchor (None = no pin on this objective)
OBJECTIVES = [
    ('obj_office',   'obj-office',   ANCHOR_OFFICE),
    ('obj_terminal', 'obj-terminal', ANCHOR_TERMINAL),
    # Reading the ledger and unplugging from it are two player actions, and the
    # gig used to silently do the second one for you. the design called for it to be
    # a real marker after the terminal soft-lock: it is what the game is
    # actually waiting on before Johnny appears.
    ('obj_disconnect','obj-disconnect', None),
    # Comic pp. 23-24: the shard in the office desk, and the note that says what
    # the ledger is FOR. Restored 2026-08-13 (playtest: "they make sense"). No
    # IT DOES GET A PIN. The first cut gave it none, on the reasoning that V is
    # standing at the desk when it appears - and it was playtested and could not
    # find the shard: "it's not clearly marked. It should appear as an
    # interactive item, and it should have an objective mark on top so we can
    # identify it." A 20 cm chip on a desk in a dark office is not findable
    # without one. See SHARD_PATH below for the shard itself.
    ('obj_shard',    'obj-shard',    ANCHOR_SHARD),
    ('obj_nix',      'obj-nix',      None),
    # Being clear of the compound and having talked to Nix are two different
    # things, and one objective covering both left the journal saying "keep
    # walking" while the game was waiting for a phone to be answered.
    ('obj_nixcall',  'obj-nixcall',  None),
    # Nix says "that'll take a minute". Without an objective for it the journal
    # goes blank while the player waits, which reads as a broken quest - the
    # same failure mode as obj_nix outliving what it described.
    ('obj_nixwait',  'obj-nixwait',  None),
    ('obj_estate',   'obj-estate',   ANCHOR_ESTATE),
    # Reaching the estate and finding a door into the house are two problems.
    # "Find Hoshino" with no way in is a player standing outside a wall.
    #
    # NO PIN, deliberately - the only objective in the gig with a marker and no
    # pin entry. Its marker is a runtime mappin owned by Gig01_Encounter, which
    # moves it up the hill; see PIN_POS above for why the journal cannot do it.
    #
    # ONE objective either way, not six. Six objectives would put six lines in
    # the quest log for one walk, and would put the route inside the quest
    # graph, where a leg that failed to fire would STALL THE GIG. Guidance and
    # progression stay separate: the objective completes on being inside the
    # compound (Gig01_Encounter.InsideEstate) whatever the marker did.
    ('obj_wayin',    'obj-wayin',    None),
    ('obj_hoshino',  'obj-hoshino',  ANCHOR_ESTATE_MECH),
    # Finding him and dealing with him are separate objectives. Leaving
    # "Find Hoshino" up after the player has already found him and talked to
    # him reads as a stalled quest - the gig has to say what it wants next.
    # No pin: V is standing in front of him.
    ('obj_kill',     'obj-kill',     None),
    ('obj_malware',  'obj-malware',  ANCHOR_HANAKO_AV),
    ('obj_escape',   'obj-escape',   None),
    ('obj_epilogue', 'obj-epilogue', ANCHOR_COYOTE),
    # No pin - V is already standing in the bar by the time it appears.
    ('obj_mama',     'obj-mama',     None),
    # V's own last line to Mama is "Nova. I'll get a drink." - so he goes and
    # gets one, and Johnny is waiting at the counter. This is the beat the gig
    # actually ends on. The pin is the bar marker itself, which is ~10 m from
    # where Mama stands, so it is a real (if short) walk rather than decoration.
    ('obj_bar',      'obj-bar',      ANCHOR_VICTOR),
]

# Pins that get a MARKER BUT NO ROUTE. `enableGPS` is per-pin; every other pin
# in the gig keeps it.
#
# playtest, 2026-08-13, on the way-in pin: it sits off the road network, on a rock
# you climb, so the GPS drew a route along a road BELOW the house - directions to
# somewhere you cannot drive, pointing at the wrong side of the hill. The design
# call was to remove the navigation rather than move the pin, and to check
# whether that is really what vanilla does.
#
# IT IS, AND THE PRECEDENT IS THE SAME SHAPE. Surveyed all 4277 quest map pins in
# `base\journal\cooked_journal.journal` (extract + `WolvenKit.CLI convert
# serialize`): 4145 have enableGPS 1, 131 have 0. The 131 are objectives you are
# already at or cannot drive to - `q005_heist/hide`,
# `wait_jackie_in_elevator`, `sq030_judy_romance/lake/exploration`,
# `explore_church_entrance`, the tutorial's tag-the-guard markers - plus every
# race, where a road route would fight the track.
#
# The closest analogue is exact: street story `sts_cct_dtn_04`, objective
# `clear_out_roof` - a GIG objective on a ROOF - is one of only two street-story
# pins in the whole game with GPS off, and it turns it off on BOTH its pins,
# including a QuestGiverVariant one like ours. A rooftop and a rock you climb are
# the same problem, and CDPR solved it with this flag rather than by moving the
# marker.
# THE WAY-IN PINS ARE NOT IN THIS SET BECAUSE THEY NO LONGER EXIST. Their
# replacement is a runtime mappin, which has no GPS at all - `enableGPS` is a
# journal-pin field and a registered mappin simply never gets a route. The
# no-route decision survives the mechanism change for free.
#
# It was tested one last time first: the road waypoint kept its GPS on the
# reasoning that it stands ON the road, so the solver has a real answer to give.
# it was playtested - *"the GPS doesn't work even for the 3 pins"* - so that is
# now measured twice, in August and again on 2026-08-15. A wrong route is worse
# than none on this hill.
#
# HOSHINO IS HERE BY DESIGN, and he is a real journal pin so he needs the
# flag. That pin is INSIDE the house and the solver snaps to the nearest road,
# so it drew directions to the wrong side of the building.
#
# pin_malware is the same shape - Hoshino's own terminal, deeper into the same
# house - and is deliberately LEFT ALONE: nobody has reported it, and by the
# time it appears the player is already inside and past the problem.
NO_GPS = {'pin_hoshino'}

# ------------------------------------------------------------------- the shard
# Comic pp. 23-24. A SHARD'S TEXT IS A JOURNAL ENTRY, not an item and not a
# document - established 2026-08-13 by reading the game's own code rather than
# guessing, because an earlier plan to fake it as a seventh file on the office
# computer would have been the wrong object entirely.
#
# `cyberpunk/items/actions/readAction.swift` is the whole mechanism, and it is
# four lines long. Reading a shard:
#
#   JournalManager.ChangeEntryState(path, "gameJournalOnscreen",
#                                   gameJournalEntryState.Active, Notify);
#   entry = JournalManager.GetEntryByString(path, "gameJournalOnscreen");
#   evt = new NotifyShardRead();  evt.title/.text/.m_imageId from the entry;
#   UISystem.QueueEvent(evt);
#
# That `NotifyShardRead` IS the reader overlay drawn on p24, and none of it
# needs a TweakDB item record - which is the part that would have needed a live
# probe. Gig01_Shard.reds does exactly those four lines.
#
# Two consequences worth writing down:
#   * the read leaves a REAL journal state, so the quest phase waits on it with
#     the add_pause_journal we already have (state 'Active'), and
#   * the entry stays in the Shards list afterwards, re-readable, exactly like
#     every vanilla shard. That is a property of the journal entry, not of any
#     item.
#
# The shape below is copied from a shipped street story
# (`sts_bls_ina_03_onscreen_01`), folder types included: onscreens is a
# PrimaryFolder, emails/quests/street_stories/<quest> are plain folders, and the
# leaf group is a gameJournalOnscreenGroup. tag None and iconID 0 are what the
# street-story shards use; the tags ('world', 'notes', 'articles'...) only apply
# to the generic collectible shards under onscreens/emails/generic/shards.
SHARD_ID = 'cc_g01_shard_note'
SHARD_PATH = ('onscreens/emails/quests/street_stories/' + QUEST_ID
              + '/onscreens/' + SHARD_ID)

# A CONTACT CARRIES NO MESSAGES. Both opening conversations are holocalls, so
# each contact exists only so the phone can resolve it as a call addressee
# (HudPhoneGameController walks JournalManager.GetContacts), and its
# conversation is an empty shell that supplies the title.
#
# Until 2026-08-15 this file also built two SMS threads: 16 phone messages, 5
# choice groups and 5 choice entries, all shipped in the archive and all inert,
# because the quest phase stopped activating them when the calls replaced them
# in v0.2.0. The technique is written up in docs/journal-research.md under
# "Phone messages and reply choices"; git history has the working code.


configure(lockey_prefix='cc-g01-', anchor_pos=ANCHOR_POS, pin_pos=PIN_POS,
          no_gps=NO_GPS)


def onscreens():
    """The shard's text, as the journal entry the vanilla reader reads."""
    shard = wrap({
        '$type': 'gameJournalOnscreen',
        'description': lockey('shard-body'),
        'iconID': tweak(None),
        'id': SHARD_ID,
        'journalEntryOverrideDataList': [],
        'tag': cname('None'),
        'title': lockey('shard-title'),
    })
    group = wrap({
        '$type': 'gameJournalOnscreenGroup',
        'entries': [shard],
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
            contact('elena_ortega', 'cc_g01_intro', 'conv-title',
                    'PhoneAvatars.Avatar_Unknown'),
            # Nix already exists in the base journal; ArchiveXL merges this
            # conversation into his contact instead of creating a new one.
            # OUR OWN NIX CONTACT, not the base game's.
            #
            # Calling the real `nix` works - he is a base-game callable contact -
            # which is the problem: the phone then offers his ordinary
            # small talk during our call, and hands control back afterwards so V
            # has to hang up on a man who already hung up (playtest, 2026-08-12).
            #
            # A contact we author has none of that, the same way Elena's does
            # not. It carries his REAL avatar (PhoneAvatars.Avatar_Nix, confirmed
            # to exist by the dev-menu probe) and his real name, so it looks
            # identical - it just has no vanilla conversation behind it.
            #
            # Cost, accepted: V ends up with two "Nix" entries in his contacts if
            # the base one is already active. A duplicate in a list beats a call
            # that cannot be ended in character.
            contact('cc_g01_nix', 'cc_g01_nixconv', 'nix-conv-title',
                    'PhoneAvatars.Avatar_Nix', name_key='nix-name'),
        ],
        'id': 'contacts',
        'journalEntryOverrideDataList': [],
    })

    quest = wrap({
        '$type': 'gameJournalQuest',
        'districtID': 'Districts.SantoDomingo',
        'entries': [wrap({
            '$type': 'gameJournalQuestPhase',
            'entries': [objective(o, s, a) for o, s, a in OBJECTIVES],
            'id': 'phase_main',
            'journalEntryOverrideDataList': [],
            'locationPrefabRef': noderef(None),
        })],
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
                # Same rule as a quest pin. The POI's anchor field is
                # `staticNodeRef`, NOT `reference` - that is the one ArchiveXL
                # reads. Lands on the compound entry, where pin_office is.
                'offset': vec3(*pin_offset('pin_office', ANCHOR_OFFICE)),
                'questPath': wrap({
                    '$type': 'gameJournalPath',
                    'className': cname('gameJournalQuest'),
                    'editorPath': '',
                    'fileEntryIndex': 0,
                    'realPath': f'quests/street_stories/{QUEST_ID}',
                }),
                'recommendedLevelID': tweak(None),
                'securityAreaRef': noderef(None),
                'staticNodeRef': noderef(ANCHOR_OFFICE),
            })],
            'id': 'street_stories',
            'journalEntryOverrideDataList': [],
        })],
        'id': 'points_of_interest',
        'journalEntryOverrideDataList': [],
    })

    return {
        'Header': {
            'WolvenKitVersion': '8.20.0', 'WKitJsonVersion': '0.0.9',
            'GameVersion': 2310, 'DataType': 'CR2W',
            'ArchiveFileName': 'gig01.journal',
        },
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


with open(OUT, 'w', encoding='utf-8') as fh:
    json.dump(build(), fh, indent=2)
print(f'wrote {OUT}')
print(f'objectives: {len(OBJECTIVES)}, pins: '
      f'{sum(len(a) if isinstance(a, list) else 1 for _, _, a in OBJECTIVES if a)}')
