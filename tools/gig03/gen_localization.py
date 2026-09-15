"""Generates the gig's en-us onscreens resource (all LocKey strings).

Keys are bare (no 'LocKey#' prefix) in both the journal and here; ArchiveXL
hashes them and matches the two sides.

WHAT IS AND IS NOT IN THIS FILE. Everything the player READS: the gig title, the
briefing, every objective, the contact name and the SMS thread. Everything the
player HEARS will be in `gen_scenes.py`, because a spoken line carries its text
inside its .scene resource keyed by the RUID its audio is keyed by, and only
that lets one number resolve both.

THE TERMINAL'S THREE DOCUMENTS ARE HERE, and the shard's text is here too. Both
were on one screen in the comic; the gig splits them. The terminal carries the
exercise records and the shard carries the ledger, and the terminal's third file
is what says where the shard is.

WRITING THE MESSAGES. Dino's texting register is his own and it is in the
cooked journal, 61 texts and 5 briefs: "Yo, V", "detes", "eds", "preem",
"biz", "on the down-low", "shoot me a word after the smoke's cleared", a
joke in every brief and a threat in every failure ("The city don't tolerate
mediocrity"). The messages below are written to sound like the ones the base
game already puts in his thread rather than like the comic's captions, which
are dialogue rather than text. The fixer was Regina Jones until 2026-09-15;
gen_journal.py's header has why.
"""
import os
import sys

# questkit is in tools/, one level up from this gig's generators.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gig03_config import RAW_MOD, LOCKEY_PREFIX                     # noqa: E402
from questkit.localization import configure, write_onscreens        # noqa: E402

# One newline, built rather than escaped. See the note on 'shard-body'.
NL = chr(10)
# The en dash the game's own texts pause on. Built from its code point so no
# editor pass can swap it for a hyphen.
DASH = chr(0x2013)

configure(lockey_prefix=LOCKEY_PREFIX)
OUT = os.path.join(RAW_MOD, 'localization', 'en-us.json.json')

STRINGS = {
    # --- the contact --------------------------------------------------------
    #
    # The mod's own contact carrying the base game's display name, which is what
    # makes it indistinguishable from the real one in the phone UI. It carries
    # his real avatar too: `PhoneAvatars.Avatar_Dino` is a shipped record.
    'dino-name': 'Dino Dinovic',
    # THE NAME OVER HIS SUBTITLES, which is a different string from the contact
    # name above. Short, because the long one is a mouthful repeated over every
    # line of a conversation. source/tweaks/characters.yaml hashes this key.
    'dino-speaker': 'Dino',
    # The subject line under a contact in the messages list. His own are wry
    # ("Occupational hazard", "Just desserts", "Got you something spicy").
    'dino-conv-title': 'On the down-low',

    # --- the opening message, and the reply that places the call ------------
    #
    # HIS REGISTER, read off his 61 texts in the cooked journal (2026-09-15):
    # "Yo, V" to open, "got a gig", the job in one clause, and a dash where
    # he pauses. The dash is the game's own en dash, which its texts use
    # 3,414 times; a hyphen is not what he types. "On the down-low" is his
    # own phrase, from the Mausser brief.
    'msg-01': "Yo, V. Got a gig for ya " + DASH + " corpo client, fat payout, "
              "and it's gotta stay on the down-low. Gimme a call, I'll fill "
              "you in.",
    'ch-01a': 'Call Dino.',

    # --- the brief, which is where the job actually gets stated -------------
    #
    # He says on the call that the details are attached. This is them, IN THE
    # GAME'S OWN LAYOUT: every brief a fixer sends is "Gig type / Objective /
    # Location / Details:" and then the job in their words, and the journal
    # paragraph under the gig is the same text (measured across 79 vanilla
    # gigs for gig 01, and read again off Dino's 5 briefs on 2026-09-15). Two
    # of his five are Thievery. His briefs run long, crude and jokey ("I
    # wouldn't sit on any of the furniture if I was you"), and every one ends
    # on how to report back ("Shoot me a word after the smoke's cleared").
    'msg-02': NL.join([
        'Gig type: Thievery',
        "Objective: Steal Militech's combat evaluation data",
        'Location: Militech compound past the Tango Tors motel, Badlands',
        'Details:',
        '',
        "So I got this corpo client " + DASH + " no names, and trust me, you "
        "don't wanna know " + DASH + " with a serious hard-on for Militech's "
        "combat evaluation data. Some training site out in the Badlands, "
        "middle of fuckin' nowhere. Thing is, that data never leaves their "
        "local net, so you're gonna have to get inside the wire and pull it "
        "off one of their terminals yourself.",
        '',
        "Here's the deal: client's paying for a clean pull. No trace, no "
        "bodies, nothing that says anyone was ever inside. Militech don't do "
        "second chances, and neither does my client.",
        '',
        "You bring it to me and nobody else. Shoot me a word when it's done.",
    ]),

    # --- after the site: V texts first ---------------------------------------
    #
    # THE PLOT LIVES HERE, IN V'S OWN WORDS. No recording of V or of Johnny
    # says that mercs are being used as targets, so the one place V can say
    # it is a text, and V sends it unprompted, the way V texts Rogue about the
    # generators. The design call, 2026-09-15, replacing a roadside argument
    # with Johnny that did not carry the point.
    #
    # V'S REGISTER, read off V's 45 replies to Regina and 75 sent texts: a terse
    # report ("Turns out...", "Managed to...", "Got out"), "zero" for kill,
    # a dash where V pauses, and no greeting.
    # Both are REPLY BUTTONS the player taps in turn (playtest 2026-09-15:
    # texts that sent themselves left the gig moving with no prompt).
    'ch-02a': "Data was rigged. Got made mid-pull and half of Militech came "
              "down on me. Managed to get out " + DASH + " with the data.",
    'ch-03a': "But Dino, this is bad. Militech's using mercs as live "
              "targets for their training exercises. And they're zeroing a "
              "lot of them.\n"
              "Who's your client?",
    # His answer, and where to bring it. A fixer's answer, and Dino's in
    # particular: the client is the client. The reason he will be angry in
    # person is already in V's first text: half of Militech knows. "The
    # club" is what his own welcome text calls his bar.
    'msg-05': "Who cares who. They want the data to replicate the results "
              + DASH + " that's all I know, and all I wanna know.\n"
              "Swing by the club. Bring it in person.",
    # THE DECISION. Two replies. The first is the ending the gig always had.
    # The second is the loyal ending: the shard is wiped, Dino gets nothing,
    # and V pays the client's advance back.
    'ch-04a': "On my way.",
    'ch-04b': "Not this one, Dino. I'm wiping it.",
    # Loyal ending only. The advance is stated here, in writing, because it is
    # a number and a number is not something he can say in his own voice.
    # The shouting is his own failure register ("The fuck was that?!",
    # "Hell's wrong with you?!").
    'msg-06': "You WIPED it?! The fuck's wrong with you, V?!\n"
              "Client fronted 5,000 eddies for this. That's coming outta "
              "YOUR account, not mine.\n"
              "Get your ass over here. Now.",

    # --- the quest ----------------------------------------------------------
    'gig-title': 'Acceptable Loss',
    # The paragraph the journal shows above the objectives: THE SAME TEXT AS
    # HIS BRIEF, which is what the game does for every one of his gigs. It
    # states the job and nothing the player has not been told, because a
    # briefing that knows the twist spoils it before the terminal does.
    'gig-brief': None,   # filled in below, from msg-02

    # --- objectives ---------------------------------------------------------
    'obj-travel': 'Get to the Militech site in the Badlands',
    'obj-enter': 'Get inside the compound',
    'obj-terminal': 'Find a terminal',
    'obj-data': 'Read the files on the terminal',
    'obj-shard': 'Find the mission log in the security room',
    'obj-read': 'Read the mission log',
    'obj-escape': 'Get clear of the compound',
    'obj-badlands': 'Leave the Badlands to escape Militech',
    'obj-dismount': 'Get out of the vehicle',
    'obj-brief': 'Message Dino about what happened',
    'obj-johnny': 'Listen to Johnny',
    'obj-dino': "Take the data to Dino, in person",
    'obj-face': "Go and face Dino, in person",
    'obj-leave': "Leave Dino's bar",

    # --- map pin captions ---------------------------------------------------
    #
    # THE LABEL ON A PIN when it is hovered on the map. Every pin the journal
    # ships carries `localizedCaption` under `pin-<id>`, and gigs 01 and 02
    # supply one for each; this gig shipped six pins with none until the
    # audit of 2026-09-15, which `tools/check_strings.py --gig 03` had been
    # reporting as six missing keys. Sentence case, the way gig 02's read
    # ("The stairs", "The way out"); "The way out" is gig 02's own for the
    # leave-the-area pin.
    'pin-pin-travel': 'Militech training site',
    'pin-pin-terminal': 'Terminal',
    'pin-pin-shard': 'Security room',
    'pin-pin-dino': "Dino's bar",
    'pin-pin-face': "Dino's bar",
    'pin-pin-leave': 'The way out',

    # --- the shard ----------------------------------------------------------
    #
    # THE TITLE THE PLAYER SEES ON THE OBJECT IS `shard-title`, not the item's
    # name: the loot line under the crosshair and the scanner panel both read
    # the journal entry. `shard-item` is only the inventory name, and
    # `shard-item-desc` the flavour line under the scanner title.
    'shard-item': 'Militech mission log',
    'shard-item-desc': 'Taken from the security room of a Militech training '
                       'site in the Badlands.',

    'shard-title': 'EXERCISE BLOCK BLAND-07 // CONTRACTOR LEDGER',
    # WHAT THE COMIC PUTS ON THE TERMINAL, moved onto the shard, because this is
    # now the thing Dino sent V for. The numbers are the comic's own.
    #
    # It is written as the site would write it. Nobody in this document thinks
    # they are describing anything but a training exercise, which is the whole
    # point of it: the horror is in the accounting, not in the wording.
    # THE LINE BREAKS ARE `NL`, NOT AN ESCAPE, and that is not fussiness. A
    # backslash-n typed into a quoted string here has twice been turned into a
    # real newline by whatever wrote the file, which leaves an unterminated
    # literal and a generator that will not import. Building the text from a
    # list and joining it cannot go wrong that way. Gotcha 28's family.
    'shard-body': NL.join([
        'PERFORMANCE ANALYTICS // TRAINING OVERSIGHT',
        'EXERCISE BLOCK: BLAND-07',
        'LIVE FIRE AUTHORIZATION: CONFIRMED',
        '',
        'Opposition: external contractors (mercenaries).',
        'Friendly units: Militech trainees.',
        '',
        'Neutralization time: 00:47 avg.',
        'Kill confirmation rate: 94%.',
        'Contractor attrition: 68%. Personnel attrition: 2%.',
        '',
        'Variance remains within parameters.',
        'Recommendation: increase contractor aggression modifiers to improve '
        'realism.',
        '',
        'Contractor source: licensed fixer channels.',
        '',
        'Contractor fatalities are not incidents. They are performance '
        'outcomes.',
        'Do not notify next-of-kin. Do not file external reports.',
        '',
        'Acceptable loss threshold: up to 15 contractor units per cycle.',
        'Losses remain acceptable given dataset value.',
    ]),

    # --- the terminal's files -----------------------------------------------
    #
    # THREE, and the third is the only one that advances the gig. Reading one
    # exercise record is not the discovery; the pattern across all three is, and
    # the third is where the site says out loud what it is doing.
    #
    # Vanilla fires the fact the moment V opens a document whose questInfo names
    # one, so nothing here needs a trigger of its own. See Gig03_Computer.reds.
    'file-folder': 'TRAINING OPERATIONS',
    'file-owner': 'MILITECH // BLAND-07',
    'file-date': '2077',

    'file-1-title': 'LIVE EXERCISE SUMMARY',
    'file-1-body': NL.join([
        'From: Training Operations',
        'To: Facility Command',
        '',
        'Exercise Block: BLAND-07',
        'Status: ACTIVE',
        'Live Fire Authorization: CONFIRMED',
        '',
        'Opposition: external contractors (mercenaries).',
        'Friendly units: Militech trainees.',
        '',
        'Metrics:',
        '  Neutralization time: 00:47 avg.',
        '  Kill confirmation rate: 94%.',
        '  Data quality: HIGH.',
        '',
        'Reminder: results remain on the local network.',
    ]),

    'file-2-title': 'ATTRITION REPORT',
    'file-2-body': NL.join([
        'From: Performance Analytics',
        'To: Training Oversight',
        '',
        'Contractor attrition rate: 68%.',
        'Personnel attrition rate: 2%.',
        '',
        'Variance remains within parameters.',
        '',
        'Recommendation: increase contractor aggression modifiers to improve '
        'realism.',
        '',
        'Contractor source: licensed fixer channels.',
        '',
        'Losses remain acceptable given dataset value.',
    ]),

    # THE ONE THAT MOVES THE GIG ON. It is also the only place the player is
    # told where to go next, so the last line has to carry that plainly.
    'file-3-title': 'ACCEPTABLE VARIANCE',
    'file-3-body': NL.join([
        'From: Oversight Division',
        'To: Facility Command',
        '',
        'Reminder:',
        '',
        'Contractor fatalities are not incidents. They are performance '
        'outcomes.',
        '',
        'Do not notify next-of-kin. Do not file external reports.',
        '',
        'Acceptable Loss Threshold: up to 15 contractor units per cycle.',
        '',
        'Training integrity takes priority.',
        '',
        'Per policy, the cycle ledger is not held on this network. The current '
        'block ledger is on physical media in the security room.',
    ]),

    # --- the trace ----------------------------------------------------------
    #
    # The alert that lands when the bar reaches the end. The bar that runs
    # before it says TRACING YOUR LOCATION; this says what the site has done
    # about it, and the reinforcements it names are already on their way (the
    # graph switches them on the moment the door opens). The design call,
    # 2026-09-11, for the wording.
    'traced-banner': 'MILITECH DETECTED A BREACH. REINFORCEMENTS INCOMING',

    # --- the loyal ending ---------------------------------------------------
    #
    # The shard leaving the backpack is the game's own item removal, which
    # draws nothing; this banner is what the player sees of it. The advance
    # coming out of the wallet gets NO banner of ours: the game's own money
    # readout (the same popup the fee arrives on) shows "-5,000" and the new
    # total for any change to the wallet that is not flagged silent, and
    # removing money cannot be flagged silent. The design call, 2026-09-15:
    # no custom text over the game's own.
    'destroyed-banner': 'MISSION LOG DESTROYED',

    # --- the start gate -----------------------------------------------------
    #
    # SHOWN WHEN THE GIG IS ASKED FOR AND CANNOT START. The condition is that
    # Dino has been in touch at all, read off the journal contact
    # `contacts/dino_dinovic`, and it is there so V is not taking a corporate
    # job from a fixer they have never spoken to.
    #
    # It names what the player has to do rather than the mechanism. Dino makes
    # contact on his own once the player spends time in City Center after the
    # prologue ("Ya don't know me, but you will"), so this is a "not yet"
    # rather than a "go and do this".
    'blocked-no-dino': 'Acceptable Loss is waiting: Dino Dinovic has to have '
                       'been in touch first. He gets in contact on his own '
                       'once you have spent some time in City Center.',
}


STRINGS['gig-brief'] = STRINGS['msg-02']


if __name__ == '__main__':
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    COUNT = write_onscreens(OUT, STRINGS)
    print('wrote %s (%d strings)' % (OUT, COUNT))
