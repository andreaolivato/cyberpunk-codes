"""Generates Return Ticket's en-us onscreens resource (all LocKey strings).

Keys are bare (no 'LocKey#' prefix) in both the journal and here; ArchiveXL
hashes them and matches the two sides.

Everything the player READS: the gig's title, its briefing, its objectives.
What anyone SAYS goes in gen_scenes.py when the scenes are built, because a
spoken line carries its text inside its .scene resource.

THE BRIEFING IS HODAN'S, in the shape of the game's own gig cards (the four
headers, then the details in the fixer's words). Her written register is her
spoken one: whole sentences, the city's words, no swearing, the fact stated
and not argued.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gig04_config import RAW_MOD, LOCKEY_PREFIX                       # noqa: E402
from questkit.localization import configure, write_onscreens        # noqa: E402

configure(lockey_prefix=LOCKEY_PREFIX)
# One newline, built rather than escaped (gotcha 28).
NL = chr(10)
OUT = os.path.join(RAW_MOD, 'localization', 'en-us.json.json')

STRINGS = {
    'gig-title': 'Return Ticket',
    # THE BRIEF, IN THE GAME'S OWN LAYOUT: "Gig type / Objective / Location /
    # Details:" and then the job in her words, the four headers word for word
    # ("Gig type: SOS: Merc Needed" is Regina's card for Max Jones). It is
    # her text message AND the journal paragraph, one string, gig 03's rule
    # (playtest 2026-10-02: "make the SMS from Hodan for the gig more
    # similar to the one from gig03, with real mission brief").
    'gig-brief': None,   # filled in below, from msg-brief
    # --- the objectives, in the game's own wording ("Talk to", "Find",
    # "Read the shard", "Leave the area") ---------------------------------
    'obj-stall': 'Talk to Maricel at her stall',
    # The game's own wording (the design call, 2026-10-13): "Find" the
    # person, the marker says where; the couch's emptiness is the player's
    # to find.
    'obj-couch': 'Find Stamps',
    'obj-read': "Read Stamps' shard",
    'obj-bar': 'Find Stamps at the bar',
    'obj-beat': 'Beat the address out of Stamps',
    'obj-flop': "Find the Tyger Claws' van",
    # The game's own wording for a clue hunt (ma_bls_ina_se1_07, q000).
    'obj-clues': 'Scan the area for clues',
    'obj-flop-take': "Take the Tyger Claws' shard",
    'obj-flop-read': "Read the Tyger Claws' shard",
    'obj-oa': "Fight off Orbital Air's security",
    'obj-room': "Go to the Tyger Claws' hideout",
    'obj-bayani': 'Find Reynaldo',
    'obj-bye': 'Talk to Reynaldo',
    'obj-leave': 'Leave the area',
    'obj-wait': "Wait for Hodan's call",
    # The captions under the map pins. The key is `pin-` + the pin id with
    # its underscore swapped, which is how questkit.journal.map_pin spells it.
    'pin-pin-stall': "Maricel's stall",
    'pin-pin-couch': "Stamps' couch",
    'pin-pin-bar': 'Stamps',
    'pin-pin-flop': "Tyger Claws' van",
    'pin-pin-clues': "Tyger Claws' van",
    'pin-pin-flop-take': "Tyger Claws' shard",
    # The game's own caption for a place to take under a wait (sq024,
    # gig 02).
    'pin-pin-wait': 'Waiting Spot',
    'pin-pin-room': "Tyger Claws' hideout",
    'pin-pin-bayani': 'Reynaldo',
    'pin-pin-bye': 'Reynaldo',
    'pin-pin-beat': 'Stamps',
    'pin-pin-oa': 'Orbital Air',
    'pin-pin-leave': "Tyger Claws' hideout",

    # --- the three people, as the scanner names them. source/tweaks/
    # characters.yaml carries the hash of each key. --------------------
    'ligaya-name': 'Maricel Manalo',
    'stamps-name': 'Stamps',
    'bayani-name': 'Reynaldo Manalo',

    # --- the three clues at the van, as the scanner shows them
    # (source/tweaks/clues.yaml, tools/gig04/gen_clues.py) ---------------
    'clue-blood-name': 'Blood',
    'clue-blood-desc': 'A few drops by the back doors. A split lip or a '
                       'broken nose, not a gunshot.',
    'clue-cuffs-name': 'Handcuffs',
    'clue-cuffs-desc': 'Unlocked, not cut. They took them off him before '
                       'they moved him.',
    'clue-bag-name': 'Duffel bag',
    # WHY IT IS AT THE VAN: the Claws took his things from the stall with
    # him (the design call, 2026-10-15: "If they snatched him at the stall
    # how could he have that?").
    'clue-bag-desc': 'R. MANALO on the tag. They took it from the stall with '
                     "him. Inside, folded, an Orbital Air janitor's coveralls.",

    # --- the shard -------------------------------------------------------
    #
    # THE TITLE THE PLAYER SEES ON THE OBJECT IS `shard-title`, not the
    # item's name: the loot line and the scanner both read the journal
    # entry. `shard-item` is only the inventory name.
    'shard-item': "Stamps' shard",
    'shard-item-desc': "Left on the seat of a couch in the alley behind "
                       "Kabuki Market.",
    'shard-title': 'MESSAGES // STAMPS',
    # WHAT THE PLAYER READS AT HIS COUCH: where he is tonight, and that he
    # came into money the day after Bayani was taken. A hint, not proof
    # (the design call, 2026-10-15): Orbital Air's payment and the Claws'
    # part were here until then, and told the player everything before
    # Stamps could.
    # THE LINE BREAKS ARE `NL`, NOT AN ESCAPE (gotcha 28's family: a
    # backslash-n typed into a quoted string here has become a real newline
    # before).
    'shard-body': NL.join([
        'KAZ: You still owe me for last week. Pay that and the stool is '
        'yours.',
        '',
        'STAMPS: Got paid today. Pour the good stuff. On my way.',
    ]),
    # THE CLAWS' SHARD, on the ground behind their van: they held him in
    # it, moved him, and where to.
    'shard2-item': "Tyger Claws' shard",
    'shard2-item-desc': "Found behind the Tyger Claws' van in Little China.",
    'shard2-title': 'MESSAGES // JUNICHI',
    # STAMPS IS WHY THEY MOVED HIM (the design call, 2026-10-15): he knows
    # the van and sells to anyone, so the tip V bought is already stale.
    'shard2-body': NL.join([
        'JUNICHI: Moving the janitor now. Stamps knows about the van, and '
        'Stamps talks to anyone who pays.',
        '',
        'HIROKI: Where to?',
        '',
        'JUNICHI: The shop in Little China. Shutters down, double doors on '
        'the street. Keep him there till their team comes.',
    ]),
    # HER TEXT after the call, carrying the gig card and Ligaya's picture.
    # The brief in full; "Location attached" is her own closing, and the
    # fixers' ("Info's attached"). Her voice rules: whole sentences, no
    # swearing, no pitch.
    'msg-brief': NL.join([
        'Gig type: SOS: Merc Needed',
        'Objective: Find Reynaldo Manalo and get him out',
        "Location: Maricel Manalo's noodle stall, Kabuki Market",
        'Details:',
        '',
        'Reynaldo Manalo signed with Orbital Air for fifteen years, to clean '
        'rooms on the Crystal Palace. The flight up and the rent in the '
        "workers' hotel come out of the salary. After seven years he owed "
        'more than on the day he signed.',
        '',
        'An old friend of mine, Liban, got him down to Night City in '
        'cargo. He '
        "hid at his sister's stall in Kabuki Market. Last night the Tyger "
        'Claws took him. If Orbital Air gets him, he goes back up.',
        '',
        'His sister Maricel is the client. Her picture is attached. Nobody knows '
        "where he is, so start with her. She knows you're coming.",
        '',
        'Orbital Air will send people for him. Get him out first. I will '
        'call you once he is safe. Location attached.',
    ]),
}


STRINGS['gig-brief'] = STRINGS['msg-brief']

# HER LAST CALL AS A TEXT, for a V who did not take it: her spoken lines,
# word for word, read off the scene so the two cannot drift
# (gen_scenes E01-E03).
import gen_scenes  # noqa: E402
STRINGS['msg-close'] = ' '.join((gen_scenes.E01[1], gen_scenes.E01B[1],
                                 gen_scenes.E03[1]))
STRINGS['msg-close-dead'] = ' '.join((gen_scenes.E01[1], gen_scenes.E01B[1],
                                      gen_scenes.E02[1], gen_scenes.E03[1]))

if __name__ == '__main__':
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    COUNT = write_onscreens(OUT, STRINGS)
    print('wrote %s (%d strings)' % (OUT, COUNT))
