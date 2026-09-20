"""Generates the gig's en-us onscreens resource (all LocKey strings).

Keys are bare (no 'LocKey#' prefix) in both the journal and here; ArchiveXL
hashes them and matches the two sides.
"""
import os
import sys

# questkit is in tools/, one level up from this gig's generators. See
# backlog.md 21.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gig01_config import RAW_MOD, LOCKEY_PREFIX                     # noqa: E402
from questkit.localization import configure, write_all_locales      # noqa: E402
from questkit import translations                                   # noqa: E402

configure(lockey_prefix=LOCKEY_PREFIX)
# One file per text locale lands here: en-us.json.json is the English table
# of record and the eighteen others are written from tools/gigNN/translations/.
OUT = os.path.join(RAW_MOD, 'localization')
HERE = os.path.dirname(os.path.abspath(__file__))

# A REAL NEWLINE, BUILT RATHER THAN TYPED. Every multi-line string below is a
# display string: the widgets take a finished value and break on real newlines,
# not on the two-character escape. Writing "\n" into this file by hand is safe
# until something rewrites the file, at which point one layer of escaping gets
# eaten and the strings quietly become one long line or the file stops parsing
# (it happened here on 2026-09-03, same family as gotcha 28). Joining on this
# constant cannot be un-escaped, because there is no escape in it.
NL = chr(10)

STRINGS = {
    # --- contacts -----------------------------------------------------------
    'elena-ortega-name': 'Elena Ortega',
    # The name over her SUBTITLES, which is her Character record's displayName
    # (source/tweaks/elena.yaml) - not the phone contact, which stays the full
    # name. "Elena Ortega" over every line was a mouthful once the standard
    # styling started showing speaker names (playtest, 2026-08-12).
    'elena-short': 'Elena',
    'conv-title': "V? It's Elena Ortega. I need your help.",
    'nix-name': 'Nix',
    'nix-conv-title': 'That ledger you sent me.',

    # Elena's and Nix's opening SMS threads used to live here: 15 strings behind
    # 26 journal entries. Both conversations became holocalls in v0.2.0 and the
    # strings shipped unreferenced until they were removed on 2026-08-15. The
    # words survive as spoken lines in tools/gig01/gen_scenes.py, which is where every
    # line in the gig lives now, because only a scene line can carry audio.

    # --- on-screen messages -------------------------------------------------
    # There is no string for the blocked-vehicle message. It uses the base
    # game's own UIInGameNotificationEvent, which reads "ACTION BLOCKED" and
    # carries no text of ours. See Gig01_VehicleLock.reds for why that is the
    # right answer rather than a limitation.
    # Shown when a call to Nix is waiting on V getting off a bike. NOT shown for
    # Elena's opening call: at that point the player is not waiting for anything
    # and has no idea a gig exists, so a nudge out of nowhere would be noise.
    'vehicle-dismount': 'Get off your vehicle to talk to Nix.',

    # --- gig + objectives ---------------------------------------------------
    'gig-title': 'Negative Balance',
    'obj-office': 'Get inside the Arasaka compound',
    'obj-terminal': 'Find the terminal and read the ledger',
    'obj-disconnect': 'Disconnect from the terminal',
    # PLURAL, AND DELIBERATELY. The shard is not on the desk V has just been
    'obj-nix': 'Get clear of the compound',
    # SHORT, for the same reason as obj-nixwait below. This used to read "Call
    # Nix: who signs off on the payouts?", carrying the INTENT of the call in
    # text we own - the cheap half of the 2026-08-13 fix for "he says 'you were
    # right' and we never said anything". The other half was V's reworked ask in
    # gig01_nix_brief, and that one is dialogue the player actually hears, so it
    # carries the intent on its own. Shortened on an explicit instruction, 2026-08-14.
    'obj-nixcall': 'Call Nix',
    # SHORT. playtest, 2026-08-14: *"'wait for nix to find.. etc' should simply be
    # 'wait for nix to call back'."* The intent was already carried by the
    # objective above and by V's ask on the call; repeating it here only made a
    # HUD line longer than it needs to be. What the player is actually waiting
    # for is the phone.
    'obj-nixwait': "Wait for Nix's message",
    'obj-nixread': 'Read the message from Nix',
    'obj-estate': 'Get to the Arasaka estate in North Oak',
    # SHORT, AND IT STAYS SHORT. This briefly read "Find a way into the
    # residence - the rocks below the gate" and it was cut: *"too long."*
    # He is right, and the reason generalises - an objective line is a HUD
    # element, not a hint box, and the directions are the six markers' job now.
    # If the markers do their work the sentence does not need to.
    'obj-wayin': 'Find a way into the residence',
    'obj-hoshino': 'Find Hoshino',
    'obj-kill': 'Take Hoshino out',
    'obj-malware': 'Upload the malware from his terminal',
    'obj-escape': 'Get out',
    'obj-epilogue': 'Stop by El Coyote Cojo',
    'obj-mama': 'Talk to Mama Welles',
    'obj-bar': 'Get a drink',

    # --- the journal briefing ------------------------------------------------
    # The paragraph the quest log shows above the objectives. Vanilla street
    # stories all carry one (`<quest>_briefing`) and this gig shipped without
    # for six versions.
    #
    # WRITTEN IN THE GAME'S OWN GIG-BRIEF LAYOUT, 2026-09-03, and the layout
    # is not a guess: 73 of the 79 street-story briefings in
    # `base\journal\cooked_journal.journal` open exactly this way, and the
    # six types they use are Thievery (18), SOS: Merc Needed (14), Agent
    # Saboteur (9), Search and Recover (9), Gun for Hire (7) and Special
    # Delivery (2). The second line is `Objective:` or, on a kill or a steal,
    # `Target:`. Ours is Agent Saboteur, which is what the job actually is:
    # get into a corporate site, take what proves the scheme, and wreck it.
    #
    # A GIG'S BRIEF NEVER CHANGES AS IT PROGRESSES, which was measured at the
    # same time and answers a real question. Of 80 street stories, 79 carry
    # exactly ONE description and the eightieth's second entry is an
    # alternative for a failed prerequisite, not an update. Main quests are
    # the ones that rewrite (q003_maelstrom carries four, one per outcome).
    # So this text is written to be true from the first objective to the
    # last, and the progression is carried by the objectives and by Nix's
    # messages, exactly as vanilla does it.
    #
    # It also carries the plot in plain words on purpose: with V's dialogue
    # restricted to his own recordings, a player who skims the call has
    # nowhere else to catch up, and the journal is where players of this game
    # look.
    #
    # The voice is Elena's, because she is who called V. She is not a fixer
    # and there is no fixer in this gig, so there is no cut and no client.
    'gig-brief': NL.join([
        'Gig type: Agent Saboteur',
        'Objective: Find out who is clearing the debts of the dead',
        'Location: Arasaka Financial Services office, Arroyo',
        'Details:',
        '',
        "Elena Ortega called out of the blue. Heywood girl, her mother grew "
        "up with Mama Welles, and Jackie used to help the family out.",
        '',
        "She reconciles community accounts at Arasaka Financial Services. "
        "Dead debtors' balances were clearing instead of freezing - no "
        "disputes, no appeals, too many of them, too fast. She reported it, "
        "and by the end of the week her access was revoked and security "
        "walked her out of the building.",
        '',
        "She's scared, and she has nowhere to go but El Coyote Cojo.",
        '',
        "The proof is on a terminal in the office she was thrown out of. "
        "Get in, take it, and find someone who can read it.",
    ]),

    # --- Nix's message, the callback that used to be a second holocall -------
    # THE PLOT LIVES HERE NOW (2026-09-03). The gig used to explain itself in
    # V's and Johnny's mouths at the terminal, and it cannot any more: they
    # speak only in recordings the game already shipped. So the terminal shows
    # data V cannot read, and the netrunner who CAN read it says what it means
    # in writing.
    #
    # Four messages, paced by their own `delay` fields. Written to be read at
    # phone speed: short lines, one idea each, the mechanism in the middle,
    # the name and the place at the end where they are easy to find again.
    # His register is vanilla's ("V, baby", "ya feel", the clipped 'g's), read
    # off his 120 recorded lines.
    'nix-msg-1': "V, baby. Cracked your ledger. Ain't accounting, it's a "
                 "kill list.",
    'nix-msg-2': "Way it works, ya feel? Arasaka writes a life policy on a "
                 "debtor who can't pay. Debtor dies, policy pays out, balance "
                 "clears. Every account ya sent me, same shape.",
    'nix-msg-3': "An' one hand signs 'em all. HOSHINO. Vice President, "
                 "Arasaka Financial Services. Runnin' it off the books, so "
                 "this here's his racket, not theirs.",
    'nix-msg-4': "He's holed up at the Arasaka estate, North Oak. Zippin' "
                 "ya the location. Watch your back, V.",
    # THE LAST MESSAGE, after V has thanked him and the fee has gone out
    # (2026-09-03). It does two jobs the gig needed and had nowhere to put:
    # it explains the malware V uploads at the estate, which until now was an
    # objective with no author, and it explains the payout, which design.md
    # has always framed as what V skims on the way through Hoshino's payment
    # network rather than anything Elena hands over.
    'nix-msg-5': "Ennies received. Throwin' in a lil' somethin' extra: "
                 "malware, attached. Plug it into his terminal at the estate "
                 "and his network eats itself, and we take a taste on the way "
                 "out. Consider it a tip jar.",
    # V's reply, and the only button in the thread: pressing it is how the
    # gig knows the message has been READ rather than merely delivered. It is
    # also the thank-you the fee follows.
    'nix-reply': "Got it. I owe you.",

    # --- characters ---------------------------------------------------------
    'hoshino-name': 'Hoshino',

    # --- the file that appears on the office terminal ------------------------
    # Rendered by the computer's own Files menu (Gig01_OfficeComputer.reds).
    # The widget uses inkTextRef.SetText, so these are plain display strings and
    # real newlines are the line breaks: not the two-character '\n' escape.
    # SIX FILES, not one summary. The comic (p20) shows a LIST of audit-log
    # entries, every one reading ACCOUNT CLOSED, and opening one shows a
    # per-account clearance notice. The pattern IS the evidence: no single
    # document says "we are killing debtors", it is the same notice again and
    # again with a different name on it. A summary hands the player the
    # conclusion and throws away the only thing that makes it land.
    #
    # Five notices modelled line-for-line on p20, then the authorization from
    # p21 - the one that names Hoshino, and the one that fires the read fact.
    #
    # The comic does not show the debtors' names (the panel is a template), so
    # the five names are authored. Everything structural - the field names, the
    # ordering, "SETTLED: E$0.00 (Debtor)", POLICY ACTIVATED before SUBJECT
    # DECEASED - is verbatim from the page. That gap between the two timestamps
    # is the whole gig in two lines.
    'file-folder': 'AUDIT LOGS',
    'file-owner': 'Arasaka Financial Services',
    'file-date': 'CURRENT QUARTER',

    'file-1-title': 'ACCOUNT CLOSED  [ 03:19:22 ]',
    'file-1-body': 'ARASAKA FINANCIAL SERVICES\n'
                   'AUTOMATED CLEARANCE NOTICE\n\n'
                   'From: Debt Resolution Node // AFS-12\n'
                   'To: Internal Ledger (Restricted)\n\n'
                   'SUBJECT: ORTEGA, M.\n'
                   'ACCOUNT STATUS: CLOSED\n'
                   'REASON: SUBJECT DECEASED\n\n'
                   'OUTSTANDING DEBT: €$48,200\n'
                   'SETTLED: €$0.00 (Debtor)\n\n'
                   'CLEARANCE METHOD:\n'
                   'POLICY-BASED TRANSFER\n\n'
                   'POLICY ACTIVATED: 02:19\n'
                   'SUBJECT DECEASED: 03:19',

    'file-2-title': 'ACCOUNT CLOSED  [ 03:16:09 ]',
    'file-2-body': 'ARASAKA FINANCIAL SERVICES\n'
                   'AUTOMATED CLEARANCE NOTICE\n\n'
                   'From: Debt Resolution Node // AFS-12\n'
                   'To: Internal Ledger (Restricted)\n\n'
                   'SUBJECT: BAUTISTA, R.\n'
                   'ACCOUNT STATUS: CLOSED\n'
                   'REASON: SUBJECT DECEASED\n\n'
                   'OUTSTANDING DEBT: €$12,750\n'
                   'SETTLED: €$0.00 (Debtor)\n\n'
                   'CLEARANCE METHOD:\n'
                   'POLICY-BASED TRANSFER\n\n'
                   'POLICY ACTIVATED: 01:44\n'
                   'SUBJECT DECEASED: 03:16',

    'file-3-title': 'ACCOUNT CLOSED  [ 02:31:01 ]',
    'file-3-body': 'ARASAKA FINANCIAL SERVICES\n'
                   'AUTOMATED CLEARANCE NOTICE\n\n'
                   'From: Debt Resolution Node // AFS-12\n'
                   'To: Internal Ledger (Restricted)\n\n'
                   'SUBJECT: OKONKWO, D.\n'
                   'ACCOUNT STATUS: CLOSED\n'
                   'REASON: SUBJECT DECEASED\n\n'
                   'OUTSTANDING DEBT: €$91,400\n'
                   'SETTLED: €$0.00 (Debtor)\n\n'
                   'CLEARANCE METHOD:\n'
                   'POLICY-BASED TRANSFER\n\n'
                   'POLICY ACTIVATED: 00:58\n'
                   'SUBJECT DECEASED: 02:31',

    'file-4-title': 'ACCOUNT CLOSED  [ 02:14:54 ]',
    'file-4-body': 'ARASAKA FINANCIAL SERVICES\n'
                   'AUTOMATED CLEARANCE NOTICE\n\n'
                   'From: Debt Resolution Node // AFS-12\n'
                   'To: Internal Ledger (Restricted)\n\n'
                   'SUBJECT: VARGAS, L.\n'
                   'ACCOUNT STATUS: CLOSED\n'
                   'REASON: SUBJECT DECEASED\n\n'
                   'OUTSTANDING DEBT: €$7,090\n'
                   'SETTLED: €$0.00 (Debtor)\n\n'
                   'CLEARANCE METHOD:\n'
                   'POLICY-BASED TRANSFER\n\n'
                   'POLICY ACTIVATED: 23:02\n'
                   'SUBJECT DECEASED: 02:14',

    'file-5-title': 'ACCOUNT CLOSED  [ 01:55:21 ]',
    'file-5-body': 'ARASAKA FINANCIAL SERVICES\n'
                   'AUTOMATED CLEARANCE NOTICE\n\n'
                   'From: Debt Resolution Node // AFS-12\n'
                   'To: Internal Ledger (Restricted)\n\n'
                   'SUBJECT: MERCADO, A.\n'
                   'ACCOUNT STATUS: CLOSED\n'
                   'REASON: SUBJECT DECEASED\n\n'
                   'OUTSTANDING DEBT: €$63,880\n'
                   'SETTLED: €$0.00 (Debtor)\n\n'
                   'CLEARANCE METHOD:\n'
                   'POLICY-BASED TRANSFER\n\n'
                   'POLICY ACTIVATED: 00:31\n'
                   'SUBJECT DECEASED: 01:55',

    # p21, and it is the file that fires the read fact.
    #
    # REWRITTEN 2026-09-03 with the SMS restructure. It carried
    # "[AUTHORIZATION KEY ENCRYPTED]" until then, which contradicts the beat
    # around it: Johnny's line at this terminal is "you'd think every
    # smart-ass would've encrypted their comms by now... what's the message
    # say?" - a recorded take, so the screen has to match the words rather
    # than the other way round.
    #
    # So nothing here is locked. It is all in the clear and all in internal
    # shorthand: routing codes, a policy series, an authority reference that
    # is a number rather than a name. A merc reading it learns that something
    # systematic is happening and cannot say what. That is exactly the state
    # V is in when he sends it to Nix, and Nix's message is the answer.
    #
    # HOSHINO'S NAME IS NOT ON THIS SCREEN. The only name is the one the
    # player already has, Elena's, in the first notice - a debtor sharing her
    # surname is the family thread, not the reveal.
    'file-6-title': 'CLEARANCE AUTHORIZATION  (RESTRICTED)',
    'file-6-body': NL.join([
        'ARASAKA FINANCIAL SERVICES',
        'CLEARANCE AUTHORIZATION',
        '',
        'Policy series: AFS-LIFE-4471',
        'Scope: 41 accounts, current quarter',
        '',
        'Beneficiary of record:',
        'AFS Contract Liabilities (internal)',
        '',
        'Authority reference: AFS-EXEC-0009',
        'Countersign: on file, off-ledger',
        '',
        'Resolution: EXPEDITED',
        'Third-party enforcement: AUTHORIZED',
        'Routing: 4471-K // do not log to district audit',
        '',
        'Note: policy activation precedes resolution by',
        'standing instruction. No dispute window.',
    ]),

    # --- the shard in the office desk, comic pp. 23-24 ----------------------
    # NOT a computer file: this is a gameJournalOnscreen entry, read through the
    # game's own shard reader (Gig01_Shard.reds). Same string rules as the files
    # above - the reader gets a finished display string and real newlines.
    #
    # VERBATIM from p24, including the two lines the comic renders with emphasis
    # (bold "mercenary", red "DECEASED"), which are plain text here because the
    # reader draws one style.
    # The ITEM's name and tooltip in the loot list - a different thing from
    # the note's title below. Referenced BARE (no LocKey# prefix) by
    # source/tweaks/shard.yaml, which clones the vanilla Hanako shard and
    # overrides only these two.
    'shard-item': 'Data shard',
    'shard-item-desc': 'Recovered from a desk in the Arasaka office in Arroyo.',
    'shard-title': 'INTERNAL FINANCIAL NOTE',
    'shard-body': 'Third-party enforcement utilized for debt resolution.\n'
                  'Internal assets not deployed.\n'
                  'Enforcement executed via fixer-mediated contracts.\n'
                  'Independent mercenary operators.\n'
                  'Outcome logged on contract completion.\n'
                  'Subject status: DECEASED.\n'
                  'Corporate liability: WAIVED.',

    # --- HUD beats after reading the ledger (Gig01_Encounter.DownloadStep) ---
    # V copies the records and nothing more. "SENDING TO NIX / SENT." used to be
    # here and it was invented: in the comic V takes the data out of the building
    # and only decides he needs a netrunner on the way (p25), then calls Nix from
    # the street (p26). Sending it from a terminal inside a guarded Arasaka
    # office was never in the source and is poor tradecraft besides - the gig
    # already delays Nix's call until V is clear of the compound for exactly that
    # reason.
    # The three copy banners are RETIRED: the bottom-of-screen progress bar
    # replaced them, and two progress readouts for one action is noise.
    # Kept as strings only so nothing that still references them breaks.

    # --- the send, in the street, right after Nix agrees (comic pp. 26-27) ----
    # This is where the ledger actually leaves V's hands, and it is the beat the
    # gig was missing entirely. The payment is the comic's own detail: p30 shows
    # a money-transfer toast for E$ -15,000, so V pays up front for the dig.
    # The two banners Gig01_Encounter.reds used to carry as bare strings.
    # Moved here on the translations branch so they follow the player's
    # language like every other string; the script reads them by key.
    'hud-estate-security': 'Estate security on site',
    'hud-arasaka-security': 'Arasaka security on site',
    'hud-shard-missing': 'Shard not found - taking the beat',
    # The copy bar's header (Gig01_Encounter.DownloadStep). The malware bar
    # and gig 03's trace bar use the base game's own strings instead.
    'hud-copy-ledger': 'COPYING LEDGER',
    # Shown once when the gig is gated behind Heroes (Gig01_Start.NotifyBlocked).
    'blocked-heroes': 'Negative Balance is waiting: finish "Heroes" for Jackie first.',
    'hud-send-01': 'ENCRYPTING LEDGER...',
    'hud-send-02': 'SENDING TO NIX',
    'hud-send-03': 'DELIVERED',
    # 'hud-paid' is RETIRED, 2026-09-03. It was a banner of ours over the
    # fee leaving V's account, and the game already animates that: the
    # transaction moves the eddies counter on its own. The string is gone
    # rather than left unreferenced so nobody wires it back by accident.

    # --- Johnny on the crosswalk while Nix digs (comic p28) ------------------
    # V asks the question the whole gig is built around and Johnny answers it.
    # This is the gap between the two Nix calls, which would otherwise be dead
    # air with an objective telling the player to wait.

    # --- payout, on gig completion ------------------------------------------
    # Not from Elena: she never learns it was V. This is what V skimmed on the
    # way through Hoshino's payment network.
    # 'reward' is RETIRED, 2026-09-03, with the notification it carried.
    # The eddies now arrive as the malware goes into Hoshino's terminal,
    # where the game's own currency animation reads as the skim actually
    # happening; the Street Cred at the end draws its own popup. A banner
    # of ours over either was text on top of an animation.

    # --- speaker labels for the subtitle lines ------------------------------
    # These play through the real subtitle panel (scnDialogLineData), which has
    # a separate speakerName field: so the lines below carry NO "Name: " prefix.
    'spk-v': 'V',
    'spk-johnny': 'Johnny',
    'spk-mama': 'Mama Welles',

    # --- epilogue exchange at El Coyote Cojo (from the comic) ---------------
    # epi-06 "She'll never know." and epi-07 "Good. Let her sleep." USED to live
    # here, as the scripted captions Line(15) and Line(16) pushed at the bar.
    # They moved into gig01_bar.scene on 2026-08-13, and a scene carries its own
    # text - so keeping a copy here would be two sources for one comic-verbatim
    # line, which is how a script drifts from its source. Deleted, not
    # commented out.

    # --- Johnny, the moment Elena's location lands (comic p11) ---------------
    # Not in the scene: Johnny has no scene actor (his character record id is
    # not discoverable offline). Plays on the scripted subtitle route when the
    # call scene exits.

    # --- at the terminal, once the ledger is off the screen (comic p22) -------
    # Verbatim from the transcript, in order. V pulls the personal link free and
    # the two of them work out what they have just read; the gig's whole thesis
    # is in "It's a production line."
    #
    # Johnny is STAGED for this one - spawned beside V at the desk - so his two
    # lines resolve through a real GameObject and carry his name. Only after the
    # last line does "get clear of the compound" appear.
    # p22 at the screen, then p25 as they work out what to do with it. All
    # verbatim. p25 is the beat the design called for - they decide to bring in Nix -
    # and it is already in the comic, so it needed finding rather than writing.
    #
    # "Guilty corpos. Sign-offs everywhere. No addresses." is the load-bearing
    # one: names without addresses is exactly why a netrunner is needed, so the
    # decision follows from the evidence instead of being announced.

    # --- Johnny at the estate terminal, comic p51 ----------------------------
    # V's "No more payouts." is already the last UploadStep beat; this is
    # Johnny's answer to it, on the same page. Ownerless subtitle rather than a
    # spawn: V is plugged into the terminal at this moment, and spawning a puppet
    # on a player locked in a device zoom is what soft-locked the office one.

    # --- Johnny, standing over Hoshino's body (comic p45) --------------------
    # In the comic this is his answer to Hoshino reaching for rank, mid-meeting.
    # It plays AFTER the kill here: the design call, and the right one - a visible
    # Johnny loitering through a negotiation reads as a bug, whereas the line
    # over the body is the beat the backlog already wanted to spend him on.

    # --- Hoshino, when V walks in -------------------------------------------

    # --- map pin captions ---------------------------------------------------
    'pin-pin-office': 'Arasaka compound',
    'pin-pin-terminal': 'Terminal',
    'pin-pin-shard': 'Data shard',
    'pin-pin-estate': 'Arasaka estate',
    # No 'pin-pin-wayin' key any more: obj_wayin has no journal pin. Its marker
    # is registered at runtime by Gig01_Encounter, and a runtime mappin carries
    # no localized caption - only a debug one, which players never see.
    'pin-pin-hoshino': 'Hoshino',
    'pin-pin-malware': "Hoshino's terminal",
    'pin-pin-epilogue': 'El Coyote Cojo',
    'pin-pin-bar': 'The bar',
}


os.makedirs(OUT, exist_ok=True)
DONE = write_all_locales(OUT, STRINGS, translations.load(HERE))
print('wrote %d strings in %d locales under %s' % (len(STRINGS), len(DONE), OUT))
