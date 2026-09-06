"""Generates the gig's en-us onscreens resource (all LocKey strings).

Keys are bare (no 'LocKey#' prefix) in both the journal and here; ArchiveXL
hashes them and matches the two sides.

WHAT IS AND IS NOT IN THIS FILE. Everything the player READS: the gig title,
every objective, the map-pin captions, the contact names, the SMS thread, and
the text of the three things V looks at. Everything the player HEARS is in
tools/gig02/gen_scenes.py, because a spoken line carries its text inside its
.scene resource keyed by the RUID its audio is keyed by, and only that lets one
number resolve both.
"""
import os
import sys

# questkit is in tools/, one level up from this gig's generators. See
# backlog.md 21.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gig02_config import RAW_MOD, LOCKEY_PREFIX                     # noqa: E402
from questkit.localization import configure, write_onscreens        # noqa: E402

configure(lockey_prefix=LOCKEY_PREFIX)
OUT = os.path.join(RAW_MOD, 'localization', 'en-us.json.json')

STRINGS = {
    # --- contacts -----------------------------------------------------------
    # The names on the phone. Both are the mod's own contacts carrying the base
    # game's own display names, which is what makes them indistinguishable from
    # the real ones in the phone UI. See gen_journal.py for why a mod cannot
    # simply ring the real contact.
    'wakako-name': 'Wakako Okada',
    # The subject line under a contact in the messages list.
    'wakako-conv-title': 'I have a job for you.',
    'char-conv-title': 'Trace is done.',

    # --- the opening message, and the reply that places the call ------------
    #
    # Wakako's canonical briefing register: formal, unhurried, no contractions,
    # "my dear".
    # REWRITTEN 2026-09-03: the call is short now and the brief follows it as
    # a message, so the text no longer hints at the plot. It asks for the call.
    'msg-01': 'V, my dear. I have a job for you, and it is one that will not '
              'keep. Call me the moment you read this.',
    # THE REPLY IS A BUTTON, so it is short. Picking it is what issues the call:
    # the quest phase pauses on this choice entry, and V is dialling on the
    # frame it is chosen. Nothing is said out loud here, so it is written as an
    # action rather than as a line of dialogue.
    'ch-01a': 'Call her.',

    # --- the attachment: her message after the call, and the journal brief --
    #
    # THE ONE PLACE THE PREMISE IS STATED. Nothing she or V can say out loud
    # covers it, so it is written, in her register, the way her real gigs put
    # their details "in the attachment". The journal paragraph is the game's
    # own street-story layout (Gig type / Objective / Location / Details),
    # measured across 79 vanilla gigs for gig 01.
    # WHAT SHE KNOWS AT THIS POINT, and it is the comic's opening call (pp.
    # 4-6) and nothing more: a merc killed people under her protection, and
    # people say the order came from her. She thinks the merc is wrong. The
    # tag, the wording and the money are things V finds; she must not know
    # them yet.
    'msg-04': "The details, as promised. A merc killed people under my "
              "protection on Jig-Jig Street, and now claims the order came "
              "from me. It did not. This creates uncertainty, and my clients "
              "rely on my word. The merc drinks outside Afterlife and boasts "
              "about the job to anyone who will listen. I will not have my "
              "name in a liar's mouth. Eliminate them.",
    'gig-brief': chr(10).join([
        'Gig type: Gun for Hire',
        'Objective: Eliminate the merc who claims Wakako Okada ordered the hit',
        'Location: Afterlife, Watson',
        'Details:',
        '',
        "A merc killed people under my protection on Jig-Jig Street. They "
        "claim the order came from me. It did not.",
        '',
        "This creates uncertainty. My clients rely on my word, and doubt "
        "spreads quickly.",
        '',
        "The merc drinks outside Afterlife and boasts about the job to anyone "
        "who will listen. I will not have my name in a liar's mouth. "
        "Eliminate them. Only me, no client. Quick, and quiet.",
    ]),

    # --- the report, after the merc: a reply and her answer, no call ------
    #
    # V TELLS HER WHAT THE SHARD SAYS BY PRESSING A BUTTON, which is the one
    # place in the gig he states the plot, and it is text because no recording
    # of him does. Her answer is in her briefing register.
    # TWO REPORTS, ONE PER FATE (2026-09-05): the merc is dead, or he lives
    # and has been told to keep quiet. Wakako's answer matches, and so does
    # the fee at the end: the kill was the job, so it pays double.
    'ch-02a': "Merc's dead. Thing is, he had proof on him: a shard with the "
              "order and the payment. Your tag on it, your wording, your "
              "accounts.",
    'msg-02': "Then the merc is no longer my concern. The shard is. Someone "
              "has used my name and my accounts, and I intend to know who. "
              "Take it to my netrunner in Kabuki. I am sending the location. "
              "Not a word of this to anyone.",
    # THE DETAILS SHE SAYS SHE HAS SHARED (design call 2026-09-06): the office
    # scene ends on "I have shared the details", and this is them. She knows
    # his name because he is one of hers; Char only ever had his face. The
    # name the objectives use is given here and nowhere earlier.
    'msg-09': "The details. His name is Toji. He works my floor at night, and "
              "he keeps to a staircase in Japantown with Tyger Claw company. "
              "The location is attached. No one is to hear of this, V. Not "
              "the Claws, not my people. Quietly.",
    'ch-02b': "Merc's alive, and he won't be talking. Thing is, he had "
              "proof on him: a shard with the order and the payment. Your "
              "tag on it, your wording, your accounts.",
    'msg-02b': "Alive is not what I asked for. We will speak of it. The shard "
               "is my concern now: someone has used my name and my accounts, "
               "and I intend to know who. Take it to my netrunner in Kabuki. "
               "I am sending the location. Not a word of this to anyone.",

    # --- Char's verdict, half an hour after the handover -------------------
    #
    # THE WHOLE TRACE IS A TEXT. Char is invented, so she could be recorded
    # saying all this, and she is not, because a netrunner reporting a trace
    # by message is what the game's own netrunners do and it lets the player
    # read it twice.
    'msg-03': "Packets are clean. Not a street spoof. The authorization "
              "checks out. Origin is local and it's hardwired: a relay. "
              "Trace ends at the pachinko parlor on Jig-Jig Street. Wakako's "
              "own floor. I'll call you when you're in.",

    # --- the relay's upload, 2026-09-05 -----------------------------------
    #
    # WHAT THE RELAY SAYS IS CHAR'S TO SAY. A note the player reads off the
    # machine was an explanation addressed to the player; a netrunner who
    # took the upload and texts back what she found is the game's own way,
    # and it is the same voice that traced the shard. Two texts: the
    # acknowledgement the moment the bar ends, and the answer.
    # V SENDS THE DUMP HIMSELF (design call 2026-09-05): an objective, and a
    # pick in Char's thread, before her acknowledgement.
    'ch-05a': "Here's the dump of data from the relay. Let me know what you "
              "find.",
    'msg-05': "Got the dump. Give me half an hour.",
    # THE VERDICT IN THREE TEXTS AND A REPLY (design call 2026-09-05, the
    # wording reviewed then): what the box is, who touches it, what it means.
    'msg-06': "Decrypted the dump. Hardwired, own line, live every night for "
              "a month. Every packet signed with Wakako's tag, spoofed clean: "
              "it listens on her line, copies the tag, and sends new orders "
              "in her name.",
    # HIS LOOK IS THE RECORD'S (characters.yaml pins gang__tyger_ma_gangster
    # __lvl3_04, approved in play 2026-09-05): green hair slicked back, a
    # visor across the eyes, a black suit coat buttoned to the collar, red
    # gloves. The comic's pink hair and oni mask went with the random look.
    'msg-07': "Pulled the parlor's cams for the nights it was live. Same guy "
              "at the port every time: a Tyger Claw, green hair slicked back, "
              "visor over the eyes, black suit coat, red gloves.",
    'msg-08': "V. One of her own people is doing this. She won't like "
              "hearing it.",
    'ch-04a': "Got it. Thanks, Char.",

    # --- the breach's daemon, 2026-09-05 -----------------------------------
    # What the code grid offers on the parlor's access point (source/tweaks/
    # minigame.yaml). The caption is the grid's daemon name, upper case like
    # the game's own; the description is the line under it.
    # CANON WORDING (design call 2026-09-05): the game's own data-extraction
    # daemons are all DATAMINE (DATAMINE_V1, "Extract eurodollars"), and the
    # grid's frame says "upload daemon" whatever the daemon does, because in
    # the game's terms a daemon is uploaded and then extracts.
    'daemon-name': 'DATAMINE: RELAY LOG',
    'daemon-desc': "Extract the relay's traffic log and send the dump to Char.",

    # --- gig + objectives ---------------------------------------------------
    'gig-title': 'Dead Ringer',
    'obj-johnny': 'Hear Johnny out',
    'obj-afterlife': 'Get to Afterlife',
    # THREE GROUPS, TWO OF THEM ON SCREEN AT ONCE. The player picks which of the
    # first two to walk to, so neither can be called "the first": the wording
    # has to read correctly in either order, which is why it is "a group",
    # "another group" and then "the last group".
    #
    # THESE ARE PLACEHOLDER WORDINGS UNTIL THE THREE SPOTS ARE CAPTURED. Naming
    # each group by what is actually there ("the pair on the steps") reads far
    # better than counting them, and cannot be written before somebody has
    # stood outside the club and looked.
    'obj-group1': 'Listen in on a group outside Afterlife',
    'obj-group2': 'Listen in on another group outside Afterlife',
    # NOT "find the merc". The man talking in this group IS the merc, so
    # listening to it and finding him are one action. The gig used to hide the
    # lead in anonymous chatter and then ask the player to pick a stranger out
    # of a crowd, and nobody could.
    'obj-group3': 'Listen in on the last group outside Afterlife',
    # A KILL ORDER, and he cannot die until he has begged: the objective
    # says what Wakako asked for, and the fight ends where the scene needs it.
    'obj-take-out': 'Take the merc out',
    'obj-kill-merc': 'Kill the merc',
    'obj-listen-merc': 'Listen to the merc',
    # TAKE AND READ IN ONE LINE (design call 2026-09-05): a player who only
    # takes it walks off with the objective apparently done.
    'obj-get-shard': "Take the merc's shard and read it",
    'obj-decide': 'Decide what to do with the merc',
    'obj-proof': 'Read the messages on his shard',
    # A reply in the thread, not a call.
    'obj-report': 'Tell Wakako what the shard says',
    'obj-inn': "Take the shard to Wakako's netrunner",
    'obj-shard': 'Give the shard to Char',
    # NAME HER AND NAME THE WAIT. Playtesting asked both questions out loud
    # when the wording was vaguer: what am I waiting for, and how long.
    'obj-wait': "Wait for Char's message",
    'obj-parlor': "Get to Wakako's pachinko parlor",
    # ONE ACTION, THE GAME'S OWN (design call 2026-09-05): the box on the
    # wall, the code grid. A marker sits on the box while this is up.
    'obj-relay': "Breach the access point in the parlor",
    'obj-reply-char': "Reply to Char",
    'obj-send-dump': "Send the relay dump to Char",
    'obj-wakako-met': 'Talk to Wakako',
    # THE SAME WORDS AS THE KILL OBJECTIVE (playtest 2026-09-05): the marker
    # stays on the stairs, but the job is the job from the moment she gives
    # it. Only the marker moves when V arrives.
    'obj-hit': 'Kill Toji without being seen',
    # THE CONDITION IS THE OBJECTIVE, and the condition changed on 2026-08-27.
    # Wakako's order is no longer to make the killing seen: it is that nobody
    # is ever to know it happened. Both objectives say the same word, "seen",
    # so the player reads one instruction rather than two.
    'obj-toji': 'Kill Toji without being seen',
    # Once V has been seen (playtest 2026-09-05).
    'obj-toji-loud': 'Kill Toji',
    'obj-exfil': 'Leave without being seen',
    'obj-exfil-loud': 'Leave the area',
    'obj-call-wakako': 'Call Wakako',
    'obj-johnny': 'Listen to Johnny',

    # --- map pin captions ---------------------------------------------------
    'pin-pin-afterlife': 'Afterlife',
    # THE SAME CAPTION ON ALL THREE, on purpose. They are three knots of
    # people standing within sight of each other, and a caption naming the
    # third one would give away which group the merc is in.
    'pin-pin-group1': 'Crowd outside Afterlife',
    'pin-pin-group2': 'Crowd outside Afterlife',
    'pin-pin-group3': 'Crowd outside Afterlife',
    'pin-pin-inn': "Wakako's netrunner",
    'pin-pin-shard': 'Char',
    'pin-pin-parlor': 'Pachinko parlor',
    'pin-pin-wakako-met': "Wakako's office",
    'pin-pin-hit': 'The stairs',
    'pin-pin-toji': 'Toji',
    'pin-pin-toji-loud': 'Toji',
    'pin-pin-exfil-loud': 'The way out',
    'pin-pin-exfil': 'The way out',

    # --- speaker names, over the subtitles ----------------------------------
    # These are the displayName on each Character record in source/tweaks/, so
    # they are what appears over a line rather than in the phone. Wakako's is
    # the short form for the same reason gig 01 shortened Elena's: the full name
    # over every line of a long conversation is a mouthful.
    'wakako-short': 'Wakako',
    'yoko-short': 'Yoko',
    'char-name': 'Char',
    'ideka-name': 'Ideka',
    # HE IS NEVER NAMED. The comic never names him and neither does the gig:
    # he is a man who took a job, and the point of the beat is that he does not
    # think he did anything wrong.
    'merc-name': 'Merc',
    # THE CROWD OUTSIDE AFTERLIFE. "Voice" is the comic's own label for every
    # one of these speakers (pp. 11-15), and it is the right one: they are
    # people V overhears and never meets. Both strangers carry it, so a
    # two-line exchange reads as two people in a crowd rather than as anybody
    # the story is introducing.
    'queue-a-name': 'Voice',
    'queue-b-name': 'Voice',
    'queue-c-name': 'Voice',
    'queue-d-name': 'Voice',
    'queue-e-name': 'Voice',
    # WAKAKO'S DOORMAN, who says "Mh." and nothing else. A role rather than a
    # name, like the merc: the player is never told what he is called.
    'huscle-name': 'Doorman',
    # NAMED ONLY AT THE END in the comic, on the one page he speaks. The
    # objective names him earlier because a HUD line cannot hold a mystery, and
    # by then Wakako has told V who he is.
    'toji-name': 'Toji',

    # --- the merc's shard, comic pp. 27 and 29 ------------------------------
    #
    # VERBATIM, including the missing full stop on "Payment will be transferred
    # on completion", which is how the page renders it. Two threads, in the
    # order V reads them: the contract, then the payment.
    #
    # It is a real item as well as a journal entry, because Wakako asks V to
    # carry it to her netrunner. See source/tweaks/shard.yaml.
    'shard-item': 'Communication shard',
    'shard-item-desc': 'Pulled off a merc outside Afterlife. Two threads on it, '
                       'both signed with Wakako Okada\'s tag.',
    # A COMMS RECORD, not two speech bubbles: the design call of 2026-09-03
    # was that the proof has to look like something a fixer's system emits.
    # The two message bodies are still the comic's, verbatim.
    'shard-title': 'COMMS RECORD // AUTH: OKADA-W',
    'shard-body': 'CHANNEL: contract-relay/wbr-jpn-04\n'
                  'AUTH TAG: OKADA-W (verified)\n'
                  'PARTY: [redacted] (contractor)\n\n'
                  '[ 22:41:07 ] OKADA-W >> contractor\n'
                  'The matter in Jig-Jig Street is approved.\n'
                  'Proceed as discussed. Keep collateral minimal.\n'
                  'Payment will be transferred on completion\n\n'
                  '[ 03:12:55 ] OKADA-W >> contractor\n'
                  'Proof received.\n'
                  'Funds are in your account.\n'
                  'Arrangement concluded.\n\n'
                  'TRANSFER: 8,000 ED, ref 4C-77-KO, cleared 03:13:02\n'
                  'ORIGIN ACCOUNT: Okada holdings, Japantown\n'
                  'SIGNATURE CHECK: PASS',

    # --- HUD banners --------------------------------------------------------
    # Shown once, when a Claw sees V. The gig does not fail here: what is lost
    # is the quiet exit Wakako asked for, and the closing call is the cold one.
    # See design.md, "The redesign of 2026-08-27".
    'hud-spotted': 'Seen. This will not stay quiet now.',
    # The payout. Wakako closes every contract she offers by saying she is
    # closing it and transferring the fee, so unlike the previous gig there is
    # nothing awkward about the money.
    # Shown once per save if the gig is holding itself back. It is the one gate
    # a player can act on: see Gig02_Start.reds.
    'blocked-side-content': 'Dead Ringer is waiting: finish the prologue first.',
}


if __name__ == '__main__':
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    COUNT = write_onscreens(OUT, STRINGS)
    print('wrote %s (%d strings)' % (OUT, COUNT))
