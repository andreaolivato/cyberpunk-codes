"""Generates Trauma Team's en-us onscreens resource (all LocKey strings).

Keys are bare (no 'LocKey#' prefix) in both the journal and here; ArchiveXL
hashes them and matches the two sides. What anyone SAYS is in gen_scenes.py.

THE NAMES ARE THE DESIGN'S (2026-11-03): the gig is "Trauma Team", the
recruiter Nisha Rao, the crew Brekke, Wrona and Raman. The records carry the hash of each `-name` key
(source/tweaks/characters.yaml), so a name changes here alone.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gig05_config import RAW_MOD, LOCKEY_PREFIX                      # noqa: E402
from questkit.localization import configure, write_onscreens        # noqa: E402

configure(lockey_prefix=LOCKEY_PREFIX)
NL = chr(10)
OUT = os.path.join(RAW_MOD, 'localization', 'en-us.json.json')

STRINGS = {
    'gig-title': 'Trauma Team Job',
    'gig-brief': None,   # the ad, below
    # --- the objectives, in the game's own wording ("Talk to", "Get in")
    'obj-recruiter': 'Talk to the Trauma Team recruiter',
    'obj-up': 'Take the staff elevator to the roof',
    'obj-change': 'Get changed in the armory',
    'obj-back': 'Change back into your own clothes',
    'obj-talk': 'Talk to the crew leader',
    'obj-down': 'Take the elevator down',
    'obj-board': 'Board the Trauma Team AV',
    'obj-ride': 'Fly to the call',
    'obj-hold': 'Clear the Scavs with Brekke',
    'obj-board-site': 'Board the AV',
    'obj-return': 'Return to the Medical Center',
    'obj-wait': 'Wait for Trauma Team to post the next shift',
    # --- the captions under the map pins (`pin-` + the pin id, its
    # underscores swapped, as questkit.journal.map_pin spells it)
    'pin-pin-recruiter': 'Trauma Team recruiter',
    'pin-pin-up': 'Staff elevator',
    'pin-pin-down': 'Staff elevator',
    'pin-pin-change': 'Armory',
    'pin-pin-back': 'Armory',
    'pin-pin-talk': 'Crew leader',
    'pin-pin-board': 'Trauma Team AV',
    # --- the people, as the scanner names them
    'recruiter-name': 'Nisha Rao',
    'lead-name': 'Brekke',
    'soldier-name': 'Wrona',
    'medic-name': 'Raman',
    'client-name': 'Trauma Team client',
    # --- the contact and the ad
    'tti-name': 'Trauma Team Dispatch',
    'tti-conv-title': 'Trauma Team Dispatch',
    'msg-ad': NL.join([
        'Trauma Team International, Night City.',
        '',
        'Probation crews wanted. Combat experience '
        'required. Paid per call, rank up after five shifts.',
        '',
        'Interviews in person at the Medical Center, Little China. '
        'Ask for intake at the staff entrance.',
    ]),
}
STRINGS['msg-done'] = NL.join([
    'Shift logged. Three calls, fees paid.',
    '',
    'Probation crews are called in as shifts open. The next one will be '
    'posted here.',
])
STRINGS['gig-brief'] = STRINGS['msg-ad']

if __name__ == '__main__':
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    COUNT = write_onscreens(OUT, STRINGS)
    print('wrote %s (%d strings)' % (OUT, COUNT))
