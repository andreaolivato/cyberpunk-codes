"""Generates the gig's en-us onscreens resource (all LocKey strings).

Keys are bare (no 'LocKey#' prefix) in both the journal and here; ArchiveXL
hashes them and matches the two sides.
"""
import json
import os

_TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(_TOOLS)
OUT = os.path.join(REPO, 'mods', 'gig-01-negative-balance', 'source', 'wkit', 'raw',
                   'mod', 'negative_balance', 'localization', 'en-us.json.json')

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

    # --- gig + objectives ---------------------------------------------------
    'gig-title': 'Negative Balance',
    'obj-office': 'Get inside the Arasaka compound',
    'obj-terminal': 'Find the terminal and read the ledger',
    'obj-disconnect': 'Disconnect from the terminal',
    'obj-shard': 'Search the office desk',
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
    'obj-nixwait': 'Wait for Nix to call back',
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

    # p21, and the payoff: this is the one that names Hoshino, so it is the one
    # that fires cc_g01_ledger_read. Highlighted in the file list.
    'file-6-title': 'CLEARANCE AUTHORIZATION  (RESTRICTED)',
    'file-6-body': 'CLEARANCE AUTHORIZATION\n'
                   'Policy ID: AFS-LIFE-4471\n\n'
                   'Scope: 41 accounts, current quarter\n\n'
                   'Approved by:\n'
                   '- Node Override: EXEC-7 (Board-level)\n'
                   '- K. Tanaka – Risk Operations\n'
                   '- M. Hoshino – Policy Enforcement\n\n'
                   'Notes:\n'
                   'Expedited resolution authorized.',

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
    'hud-dl-01': 'COPYING RECORDS  24%',
    'hud-dl-02': 'COPYING RECORDS  68%',
    'hud-dl-03': 'RECORDS COPIED',

    # --- the send, in the street, right after Nix agrees (comic pp. 26-27) ----
    # This is where the ledger actually leaves V's hands, and it is the beat the
    # gig was missing entirely. The payment is the comic's own detail: p30 shows
    # a money-transfer toast for E$ -15,000, so V pays up front for the dig.
    'hud-send-01': 'ENCRYPTING LEDGER...',
    'hud-send-02': 'SENDING TO NIX',
    'hud-send-03': 'DELIVERED',
    'hud-paid': 'Transferred to Nix. Fifteen thousand, up front.',

    # --- Johnny on the crosswalk while Nix digs (comic p28) ------------------
    # V asks the question the whole gig is built around and Johnny answers it.
    # This is the gap between the two Nix calls, which would otherwise be dead
    # air with an objective telling the player to wait.
    'legend-01': 'Is this how you become a legend in Night City?',
    'legend-02': "Killing to pad Arasaka's books?",
    'legend-03': 'No.',
    'legend-04': 'A legend picks who pays',

    # --- payout, on gig completion ------------------------------------------
    # Not from Elena: she never learns it was V. This is what V skimmed on the
    # way through Hoshino's payment network.
    'reward': 'Skimmed from the payout account. Nobody left to miss it.',

    # --- speaker labels for the subtitle lines ------------------------------
    # These play through the real subtitle panel (scnDialogLineData), which has
    # a separate speakerName field: so the lines below carry NO "Name: " prefix.
    'spk-v': 'V',
    'spk-johnny': 'Johnny',
    'spk-mama': 'Mama Welles',

    # --- epilogue exchange at El Coyote Cojo (from the comic) ---------------
    'epi-01': 'You look tired, mija.',
    'epi-02': 'Long night.',
    'epi-03': "She okay?",
    'epi-04': "She's in the back.",
    'epi-05': "Nova. I'll get a drink.",
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
    'johnny-arasaka': 'Fucking Arasaka...',

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
    'term-01': "That's not debt collection.",
    'term-02': "It's a production line.",
    'term-03': 'Insure them. Flatline them. Get the eddies.',
    'term-04': 'Welcome to corporate efficiency.',
    'term-05': 'Yeah. With a body count.',
    'term-06': 'Guilty corpos. Sign-offs everywhere. No addresses.',
    'term-07': "That's Arasaka.",
    'term-08': 'I need a netrunner.',
    'term-09': 'We know one.',

    # --- Johnny at the estate terminal, comic p51 ----------------------------
    # V's "No more payouts." is already the last UploadStep beat; this is
    # Johnny's answer to it, on the same page. Ownerless subtitle rather than a
    # spawn: V is plugged into the terminal at this moment, and spawning a puppet
    # on a player locked in a device zoom is what soft-locked the office one.
    'malware-v': 'No more payouts.',
    'malware-johnny': 'No money, no bodies.',

    # --- Johnny, standing over Hoshino's body (comic p45) --------------------
    # In the comic this is his answer to Hoshino reaching for rank, mid-meeting.
    # It plays AFTER the kill here: the design call, and the right one - a visible
    # Johnny loitering through a negotiation reads as a bug, whereas the line
    # over the body is the beat the backlog already wanted to spend him on.
    'johnny-hoshino': 'They always think names beat bullets.',

    # --- Hoshino, when V walks in -------------------------------------------
    'hoshino-01': 'Mmm? You lost, merc?',
    'hoshino-02': 'You know who I am.',
    'hoshino-03': 'I know what you signed. I know who paid for it.',
    'hoshino-04': "Ledger's closed.",

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


def entry(key, value):
    return {
        '$type': 'localizationPersistenceOnScreenEntry',
        'femaleVariant': value,
        'maleVariant': '',
        'primaryKey': '0',
        'secondaryKey': 'cc-g01-' + key,
    }


doc = {
    'Header': {
        'WolvenKitVersion': '8.20.0', 'WKitJsonVersion': '0.0.9',
        'GameVersion': 2310, 'DataType': 'CR2W', 'ArchiveFileName': 'en-us.json',
    },
    'Data': {
        'Version': 195, 'BuildVersion': 0,
        'RootChunk': {
            '$type': 'JsonResource',
            'cookingPlatform': 'PLATFORM_PC',
            'root': {'HandleId': '0', 'Data': {
                '$type': 'localizationPersistenceOnScreenEntries',
                'entries': [entry(k, v) for k, v in STRINGS.items()],
            }},
        },
        'EmbeddedFiles': [],
    },
}

with open(OUT, 'w', encoding='utf-8') as fh:
    json.dump(doc, fh, indent=2)
print(f'wrote {OUT} ({len(STRINGS)} strings)')
