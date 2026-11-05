r"""Trauma Team: the scenes of the first shift.

    python tools\gig05\gen_scenes.py

  gig05_interview    The recruiter outside the Medical Center. Her five
                     lines, V's three, one choice with a Body check.
  gig05_board_pad    "Board" at the AV's open side on the pad. No lines.
  gig05_brief        The lead's briefing, played while the AV climbs out.
  gig05_land         The soldier's call as the AV touches down at the roof.
  gig05_stable       The roof is clear: the lead, the medic, back aboard.
  gig05_board_site   "Board" at the AV's open side on the roof.
  gig05_home         The lead on the flight back.

Modelled on `tools/gig04/gen_scenes.py`; read that file and its fixer's for
the builder. This header records only what is different.

WHO IS RECORDED. The recruiter and the lead are invented, so people record
them (`docs/conventions.md`, tools/gig05/gen_voice.py). V speaks whole lines the game recorded,
each present for both bodies (`tools/_vo_cache/voice_files.txt`). The
soldier and the medic speak whole lines the game recorded for The Rescue's
own Trauma Team crew (`tools/vo_corpus.py`):

  0x1146a035542b1000  ncpd_high_m_01_enus_30_q001  "Landing, stand clear! ..."
  0x1a582b5326627000  ncpd_high_m_01_enus_30_q001  "Place the patient on the stretcher!"
  0x0e4ba87051346000  ncpd_high_m_05_afam_40_q001  "Stimulants being administered ..."
  0x0e4ba5412a346000  ncpd_high_m_05_afam_40_q001  "TT-133 to Control. Patient ..."

THE BRIEFING PLAYS IN THE AIR. The scene is staged at V, who is aboard and
moving, and it acquires the lead from the community while he stands in the
AV. Last Caress plays its conversation the same way, beside the spline that
flies the AV (q113_05, docs/gig05-av-research.md 2).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from questkit.scene import (                                        # noqa: F401
    Scene, configure, write_subtitles, write_lipmap,
    ANCHOR_PLAYER,
)

import gig05_config as cfg                                          # noqa: E402
import gen_community                                                # noqa: E402

OUT_DIR = os.path.join(cfg.RAW_MOD, 'scenes')
SUBTITLE_MAP_OUT = os.path.join(cfg.RAW_MOD, 'localization', 'subtitles.json.json')
SUBTITLE_OUT = os.path.join(cfg.RAW_MOD, 'localization', 'gig05_lines.json.json')
SUBTITLE_DEPOT = cfg.DEPOT + chr(92) + 'localization' + chr(92) + 'gig05_lines.json'
# gen_questphase.SCENES is the same string and has to stay so: the lipmap is
# keyed by FNV1a64 of exactly this path plus the scene name.
SCENE_DEPOT = cfg.DEPOT + chr(92) + 'scenes' + chr(92)
LIPMAP_OUT = os.path.join(cfg.RAW_MOD, 'localization', 'gig05.lipmap.json')

DURATIONS_FILE = os.path.join(cfg.SOURCE, 'audio', 'durations.json')
try:
    with open(DURATIONS_FILE, encoding='utf-8') as _fh:
        MEASURED = json.load(_fh)
except (OSError, ValueError):
    MEASURED = {}

LIPSYNC_PICKS = os.path.join(cfg.SOURCE, 'lipsync_picks.json')
try:
    with open(LIPSYNC_PICKS, encoding='utf-8') as _fh:
        _picks = json.load(_fh)
    LIPSYNC_SETS = _picks.get('sets', {})
    LIPSYNC_LINES = _picks.get('lines', {})
except (OSError, ValueError):
    LIPSYNC_SETS, LIPSYNC_LINES = {}, {}

configure(
    out_dir=OUT_DIR,
    scene_depot=SCENE_DEPOT,
    subtitle_out=SUBTITLE_OUT,
    subtitle_map_out=SUBTITLE_MAP_OUT,
    subtitle_depot=SUBTITLE_DEPOT,
    lipmap_out=LIPMAP_OUT,
    lipmap_name='gig05.lipmap',
    durations=MEASURED,
    lipsync_sets=LIPSYNC_SETS,
    lipsync_lines=LIPSYNC_LINES,
    scene_aliases={},
)

CAST_REF = gen_community.build().community_ref
RECRUITER = gen_community.RECRUITER
LEAD, SOLDIER, MEDIC = gen_community.LEAD, gen_community.SOLDIER, gen_community.MEDIC


def sid(h):
    """A vanilla stringId, written in hex as vo_corpus prints it."""
    return int(h, 16)


# V, in the game's own recordings, all present for both bodies.
V_READY = ("Ready when you are.", sid('157e1b71822fc000'))                   # q105
V_START = ("When do we start?", sid('18c6a2e401502000'))                     # sq024
V_NOVA = ("Nova, thanks.", sid('1ad3167d812c5000'))                          # sts_bls_ina_09
V_NOT_FIRST = ("Not my first time.", sid('18a1856c8629f000'))                  # q004
V_THATS_ME = ("Yeah, that's me.", sid('1a29b9ce4b44d000'))                   # mq035
V_SEE_YOU = ("See you around.", sid('1b25ef28082ef000'))                     # Reggie's

# THE RESCUE'S CREW, in their own voices.
SOLDIER_LANDING = ("Landing, stand clear! Initiating security protocol. "
                   "Follow all instructions.", sid('1146a035542b1000'))
SOLDIER_STRETCHER = ("Place the patient on the stretcher!", sid('1a582b5326627000'))
MEDIC_STIMS = ("Stimulants being administered – 70 milligrams dopamine, 110 "
               "norepinephrine, 800 fibrinogen…", sid('0e4ba87051346000'))
MEDIC_SECURED = ("TT-133 to Control. Patient NC570442 secured…", sid('0e4ba5412a346000'))

# ------------------------------------------------------------ the recruiter
#
# HER REGISTER: intake paperwork read aloud. Short, procedural, not unkind.
# She never sells the job.
R01 = "A new recruit. Hope you're better than the last batch."
R01B = "We need a gun. Protect the client, protect the medic, clear the scene."
R02 = "Each shift is up to three calls, paid per call."
R03 = "Do you have combat experience?"
R04 = "Good. Brekke's the crew leader. He'll evaluate you at the end of the shift."
R05 = "Now. On probation, of course."
R06 = "Remember, we have one rule. The client lives. Everything else comes second."
R07 = "Staff elevator's out in the tank yard, up to the roof."
R08 = "Get changed in the armory, then meet the team on the landing pad. They'll be waiting."

# ------------------------------------------------------------------ the lead
#
# HIS REGISTER: radio habits. Names, numbers, no adjectives. The crew's names are working names
# (gen_localization).
L_HOLD = "Hold on to the rail. Don't lean out."
L_CALL = "The first call is a Platinum client. His biomonitor went flat on a hotel roof four minutes ago."
L_THREAT = "Scavs got to him first. They're cutting his chrome out."
L_PLAN = "We put down on the roof. Wrona holds the bird. Raman works the client."
L_JOB = "You're with me. We clear the roof."
L_CLEAR = "Roof's clear. Raman, talk to me."
L_STABLE = "Client's stable. Everyone back aboard."
L_CALL2 = "Next one is close. Gold client down in the street by the water."
L_PLAN2 = "Same drill. Wrona holds, Raman on the client, you with me."
L_CALL3 = "Last call, Kabuki. Client's down. Scavs all around."
L_PLAN3 = "Clear it fast, then we go home."
L_HOME1 = "Three calls, three clients breathing. Dispatch has it logged."
# ON THE PAD, BEFORE THE FIRST FLIGHT AND AFTER THE LAST (the design call,
# 2026-11-04: V walked up to three silent people, and left them the same way).
# The client's contract before anyone is Trauma Team's own rule in the game.
L_W1 = "You are the probation hire."
L_W2 = "I'm Brekke, crew leader. Wrona, security. Raman, medical. You do what we say."
L_W3 = "Up there the client comes first. Not you, not me."
L_W4 = "Try to keep up, rookie. Get in the AV."
L_B1 = "Not bad for a rookie."
L_B2 = "Pay clears by the time you're downstairs. Dispatch will text you for the next shift."
L_B3 = "You know, if they put you on my crew again, I won't argue."
# EACH CALL ITS OWN LANDING AND ALL-CLEAR (the design call, 2026-11-03: the
# same lines at all three calls). Wrona's landing call is the game's own
# recording and there is one, so the first call keeps it and Brekke calls
# the other two.
L_LAND2 = "Street. Doors open. Go, go, go."
L_LAND3 = "Landed. Out, out, out."
L_CLEAR2 = "Street's clear. Raman?"
L_STABLE2 = "Good. Load him up."
L_CLEAR3 = "And that's the last of them. Raman, he going to make it?"
L_STABLE3 = "Stable. Take us home."


def face_player(s, actor):
    player = s.player_performer()
    for sec in s.sections():
        s.look_at(sec, actor, player, start_time=0)


def chain(s, people, v, seq, tail=600):
    """One section per line. ('N', who, text, key) is one of ours;
    ('V', (text, sid), key) is V; ('G', who, (text, sid), key) is another
    speaker on one of the game's own recordings. Returns (first, last)."""
    secs = []
    for i, t in enumerate(seq):
        final = i == len(seq) - 1
        tail_ms = tail if final else 0
        if t[0] == 'V':
            _w, (text, vsid), key = t
            secs.append(s.section([s.add_line(v, text, key=key, vanilla_sid=vsid)],
                                  tail_ms=tail_ms))
        elif t[0] == 'G':
            _w, who, (text, vsid), key = t
            secs.append(s.section([s.add_line(people[who], text, key=key,
                                              vanilla_sid=vsid)], tail_ms=tail_ms))
        else:
            _w, who, text, key = t
            secs.append(s.section([s.add_line(people[who], text, key=key)],
                                  tail_ms=tail_ms))
    for x, y in zip(secs, secs[1:]):
        s.link_section(x, y)
    return secs[0], secs[-1]


def walk_away(s, hub, entry, left_name):
    """End the scene when V walks off while the prompt is up (gig 04's
    helper, input ordinal 1 on the wait)."""
    gone = s.add_wait_distance_node(CAST_REF, cfg.LEAVE_RADIUS, entry=entry,
                                    cmp='Greater')
    left = s.end(left_name)
    s._node(hub)['outputSockets'][0]['destinations'].append(
        {'$type': 'scnInputSocketId',
         'isockStamp': {'$type': 'scnInputSocketStamp', 'name': 0, 'ordinal': 1},
         'nodeId': {'$type': 'scnNodeId', 'id': gone}})
    s.link(gone, left)


# ============================================================ the interview
def build_interview():
    """The recruiter: a prompt over her, her lines and V's answer, a prompt for
    when, the rule and the way up."""
    s = Scene('gig05_interview', ANCHOR_PLAYER)
    n = s.add_community_actor(RECRUITER, RECRUITER, CAST_REF)
    v = s.add_player()
    who = {RECRUITER: n}
    start = s.start('interview_in')
    lead = s.section([], lead_ms=0, tail_ms=500)
    hub = s.hub()
    opt = s.add_option("Here about the Trauma Team ad.", key='o01')
    c1 = s.choice([opt], attach_actor=n)
    a1, a2 = chain(s, who, v, [('N', RECRUITER, R01, 'r01'),
                               ('N', RECRUITER, R01B, 'r09'),
                               ('N', RECRUITER, R02, 'r02'),
                               ('N', RECRUITER, R03, 'r03'),
                               ('V', V_NOT_FIRST, 'v01'),
                               ('N', RECRUITER, R04, 'r04')], tail=200)
    hub2 = s.hub()
    c2 = s.choice([s.add_option("When do we start?", key='o03')], attach_actor=n)
    e1, e2 = chain(s, who, v, [('V', V_START, 'v02'),
                               ('N', RECRUITER, R05, 'r05'),
                               ('N', RECRUITER, R06, 'r06'),
                               ('N', RECRUITER, R07, 'r07'),
                               ('N', RECRUITER, R08, 'r08'),
                               ('V', V_NOVA, 'v03')])
    s.link(start, lead)
    s.link_section(lead, hub)
    s.link(hub, c1)
    s.link_choice(c1, [a1])
    s.link_section(a2, hub2)
    s.link(hub2, c2)
    s.link_choice(c2, [e1])
    s.link_section(e2, s.end('interview_out'))
    walk_away(s, hub, RECRUITER, 'interview_left')
    face_player(s, n)
    return s


# ============================================================ the prompts
# A PROMPT WITH NOBODY'S NAME STILL DRAWS THE NAME BOX left of the key: a small
# mark with no title, a dark block with one space as the title (playtest
# 2026-11-05, and dialogUI.swift, SetupTitle). The game names the thing: of 171
# prompts pinned to a place in 343 of its scenes, 166 have a title, Couch, Bed,
# Door, Freezer, Clothing. These are the game's own words, so they are translated.
TITLE_AV = 'LocKey#28782'           # "AV"
TITLE_CLOTHING = 'LocKey#23417'     # "Clothing", V's wardrobe in mq000_01_apartment


def _board(name, marker, entry, exit_, text="Board the AV.",
           fact='cc_g05_board_taken', yaw_limit=360, radius=3.0, title=TITLE_AV):
    """A prompt pinned to a marker, and a fact when it is taken: "Board" at the
    AV's open side, "Get changed" and "Change back" at the shelves. Not offered in
    combat (the condition `wait_option` carries, without its wait icon)."""
    s = Scene(name, marker)
    s.add_player()
    start = s.start(entry)
    c1 = s.choice([s.add_option(text, key='o10')],
                  in_world=True, radius=radius, yaw_limit=yaw_limit, no_look=True,
                  checks=[_not_in_combat()], title=title)
    s1 = s.section([], tail_ms=200)
    taken = s.add_fact_node(fact, 1)
    out = s.end(exit_)
    s.link(start, c1)
    s.link_choice(c1, [s1])
    s.link_section_quest(s1, taken)
    s.link(taken, out)
    return s


# SKIP THE FLIGHT, the way a taxi or Delamain ride offers it (the design
# call, 2026-11-03), once the briefing has been said: a wait, then a choice
# on screen. Taking it writes `cc_g05_skip`; the quest fades and the clock runs
# fast until the AV nears its landing (gen_questphase.py, fly).
# The scene is cut if the flight gets near that stretch first. One file per flight: one scene file
# entered from two quest nodes is the shape that crashed loads.
SKIP_AFTER_S = {1: 32, 2: 14, 3: 14, 4: 18}


def build_skip(n):
    s = Scene('gig05_skip_%d' % n, ANCHOR_PLAYER)
    s.add_player()
    start = s.start('skip_in')
    wait = s.section([], tail_ms=SKIP_AFTER_S[n] * 1000)
    c1 = s.choice([s.add_option("Skip the flight.", key='o20')], title=TITLE_AV)
    s1 = s.section([], tail_ms=200)
    taken = s.add_fact_node('cc_g05_skip', 1)
    out = s.end('skip_out')
    s.link(start, wait)
    s.link_section(wait, c1)
    s.link_choice(c1, [s1])
    s.link_section_quest(s1, taken)
    s.link(taken, out)
    return s


def _not_in_combat():
    from questkit.scene import wait_option
    opt = wait_option()
    opt['iconTagIds'] = []
    return opt


def build_locker():
    return _board('gig05_locker', gen_community.LOCKER_REF, 'locker_in', 'locker_out',
                  text="Get changed.", fact='cc_g05_changed', radius=2.5, title=TITLE_CLOTHING)


def build_locker_back():
    return _board('gig05_locker_back', gen_community.LOCKER_REF, 'locker_in', 'locker_out',
                  text="Change back.", fact='cc_g05_changed_back', radius=2.5, title=TITLE_CLOTHING)


def build_board_pad():
    return _board('gig05_board_pad', gen_community.PAD_BOARD_REF,
                  'board_in', 'board_out')


def _board_site(k):
    return lambda: _board('gig05_board_s%d' % (k + 1), gen_community.SITE_BOARD[k][0],
                          'board_in', 'board_out')


build_board_s1, build_board_s2, build_board_s3 = (_board_site(k) for k in range(3))


# ============================================================ in the air
def _aboard(name, entry, exit_, seq, speakers, bodies=None):
    """`bodies` maps a speaker to the community entry that plays him: on the
    ground at a call that is the roof crew (gen_community.ROOF_CREW)."""
    s = Scene(name, ANCHOR_PLAYER)
    bodies = bodies or {}
    who = {w: s.add_community_actor(bodies.get(w, w), bodies.get(w, w), CAST_REF)
           for w in speakers}
    v = s.add_player()
    start = s.start(entry)
    first, last = chain(s, who, v, seq)
    s.link(start, first)
    s.link_section(last, s.end(exit_))
    return s


def _on_pad(name, entry, exit_, seq):
    """The lead on the roof, turned to V."""
    s = Scene(name, ANCHOR_PLAYER)
    n = s.add_community_actor(LEAD, LEAD, CAST_REF)
    v = s.add_player()
    start = s.start(entry)
    first, last = chain(s, {LEAD: n}, v, seq)
    s.link(start, first)
    s.link_section(last, s.end(exit_))
    face_player(s, n)
    return s


def build_welcome():
    return _on_pad('gig05_welcome', 'welcome_in', 'welcome_out', [
        ('N', LEAD, L_W1, 'l20'),
        ('V', V_THATS_ME, 'v12'),
        ('N', LEAD, L_W2, 'l21'),
        ('N', LEAD, L_W3, 'l22'),
        ('N', LEAD, L_W4, 'l23'),
    ])


def build_bye():
    return _on_pad('gig05_bye', 'bye_in', 'bye_out', [
        ('N', LEAD, L_B1, 'l24'),
        ('N', LEAD, L_B2, 'l25'),
        ('N', LEAD, L_B3, 'l26'),
        ('V', V_SEE_YOU, 'v13'),
    ])


def build_brief():
    """The lead, while the AV climbs out over Little China."""
    return _aboard('gig05_brief', 'brief_in', 'brief_out', [
        ('N', LEAD, L_HOLD, 'l01'),
        ('N', LEAD, L_CALL, 'l02'),
        ('N', LEAD, L_THREAT, 'l03'),
        ('N', LEAD, L_PLAN, 'l04'),
        ('N', LEAD, L_JOB, 'l05'),
        ('V', V_READY, 'v10'),
    ], [LEAD])


# ONE SCENE FILE PER CALL for the landing and the all-clear. The same file
# entered from two quest nodes is the shape that crashed the game on load in
# August (backlog.md, the gig 01 epilogue stand-in; tools/check_phase.py
# fails on it). The copies differ only in name.
CALLS = (1, 2, 3)


def build_land(n):
    """The landing call at call `n`: Wrona at the first, Brekke after."""
    seq = {1: [('G', SOLDIER, SOLDIER_LANDING, 'g01')],
           2: [('N', LEAD, L_LAND2, 'l14')],
           3: [('N', LEAD, L_LAND3, 'l15')]}[n]
    return _aboard('gig05_land_%d' % n, 'land_in', 'land_out', seq,
                   [SOLDIER] if n == 1 else [LEAD])


def build_stable(n):
    """Call `n` is clear. The lead asks, the medic works, the lead calls it."""
    clear, stable = {1: (L_CLEAR, L_STABLE), 2: (L_CLEAR2, L_STABLE2),
                     3: (L_CLEAR3, L_STABLE3)}[n]
    keys = {1: ('l06', 'l07'), 2: ('l16', 'l17'), 3: ('l18', 'l19')}[n]
    # A DIFFERENT CALL AT EACH CLIENT. Playtest 2026-11-04: the same stimulants
    # line three times. The game has two lines in the medic's voice and this one
    # in the soldier's, all from The Rescue's crew.
    who, line, key = {1: (MEDIC, MEDIC_STIMS, 'g02'), 2: (MEDIC, MEDIC_SECURED, 'g03'),
                      3: (SOLDIER, SOLDIER_STRETCHER, 'g04')}[n]
    return _aboard('gig05_stable_%d' % n, 'stable_in', 'stable_out', [
        ('N', LEAD, clear, keys[0]),
        ('G', who, line, key),
        ('N', LEAD, stable, keys[1]),
    ], [LEAD, who], bodies=gen_community.ROOF_CREW)


def build_brief2():
    """The lead, between the first call and the second."""
    return _aboard('gig05_brief2', 'brief_in', 'brief_out', [
        ('N', LEAD, L_CALL2, 'l10'),
        ('N', LEAD, L_PLAN2, 'l11'),
    ], [LEAD])


def build_brief3():
    """The lead, between the second call and the third."""
    return _aboard('gig05_brief3', 'brief_in', 'brief_out', [
        ('N', LEAD, L_CALL3, 'l12'),
        ('N', LEAD, L_PLAN3, 'l13'),
    ], [LEAD])


def build_home():
    """The lead on the flight back."""
    return _aboard('gig05_home', 'home_in', 'home_out', [
        ('N', LEAD, L_HOME1, 'l08'),
    ], [LEAD])


# THE CREW STANDING IN THE CABIN for a flight: the game's plain standing pose
# (the one the community spots use), anchored on three of the AV's own
# occupant slots the way q115_05_halo_jump anchors V's pose on
# `player_standing`. Playtests 2026-11-03: mounted on the seats with no
# pose the men floated; the seat names are map-pin bones and anchor
# nothing (all three under the floor); `tt_1` is V's own spot; a rifle pose
# with no rifle held the arms out.
CREW_POSE_ENTRY = 2     # the standing loop, sequence 2
CREW_PLACE = 'tt_2'
# TWO SIT ON THE FAR WALL'S SEATS, FACING THE DOOR. BREKKE STANDS IN THE MIDDLE
# OF THE CABIN, arms folded, on V's place moved across (gig05_config.py,
# BOSS_OFFSET). `player_standing` is at the floor; `tt_2` is 0.3 m above it,
# which put a standing man's head through the roof. The pose has to be on the
# man_base rig: Rogue's, V's twin, bent him double.
#
# Offsets are in the place's own frame. `tt_2` is turned 90 degrees: its own x
# runs forward along the cabin and its own -y runs in from the door, so AV x =
# -1.22 - own y and AV y = 0.19 + own x. The seats are 0.55 m apart.
SIT = chr(92).join(['base', 'workspots', 'common', 'bench',
                    'generic__sit_bench_lean_back__sit_around__%02d.workspot'])
# THE BEST OF TEN IN A POSE LAB ON THE ROOF (2026-11-05): a veteran at ease. Holding
# a rail with one hand read as stiff.
HOLD = chr(92).join(['base', 'workspots', 'quest', 'side_quests', 'sq006', 'sq006_02b_investigation',
                     'sq006__johnny__stand__stand_around__01.workspot'])
SEAT_Y = -2.45
CREW_SEATS = {LEAD: (HOLD, 'player_standing', cfg.BOSS_OFFSET),
              MEDIC: (SIT % 2, CREW_PLACE, (-0.59, SEAT_Y, 0.0)),
              SOLDIER: (SIT % 1, CREW_PLACE, (-0.04, SEAT_Y, 0.0))}


# V HOLDS ON AT THE DOOR by the seat node, the AV's own `player_standing`. A pose on
# that slot (q115_05_halo_jump's shape) crashed the game as V boarded at a call
# (playtest 2026-11-03, three runs, bisected).
def _crew_aboard(name, entry, exit_):
    s = Scene(name, ANCHOR_PLAYER)
    for w in (LEAD, SOLDIER, MEDIC):
        s.add_community_actor(w, w, CAST_REF)
    start = s.start(entry)
    hold = s.section([], tail_ms=600000)
    s.link(start, hold)
    s.link_section(hold, s.end(exit_))
    for w in (LEAD, SOLDIER, MEDIC):
        path, place, offset = CREW_SEATS[w]
        ws = s.add_workspot_node('cc_g05_' + w, path=path, entry=CREW_POSE_ENTRY,
                                 community=(CAST_REF, w),
                                 on_slot=(CAST_REF, gen_community.AV, place),
                                 offset=offset)
        s.fire_workspot(hold, ws, 0)
    return s


def build_crew_1():
    return _crew_aboard('gig05_crew_1', 'crew_in', 'crew_out')


def build_crew_2():
    return _crew_aboard('gig05_crew_2', 'crew_in', 'crew_out')


def build_crew_3():
    return _crew_aboard('gig05_crew_3', 'crew_in', 'crew_out')


def build_crew_4():
    return _crew_aboard('gig05_crew_4', 'crew_in', 'crew_out')


ALL_BUILDERS = (build_interview, build_welcome, build_bye, build_locker, build_locker_back, build_board_pad,
                build_board_s1, build_board_s2, build_board_s3,
                build_brief, build_home,
                build_brief2, build_brief3,
                build_crew_1, build_crew_2, build_crew_3, build_crew_4) + tuple(
    (lambda n=n, f=f: f(n)) for f in (build_land, build_stable) for n in CALLS) + tuple(
    (lambda n=n: build_skip(n)) for n in (1, 2, 3, 4))


if __name__ == '__main__':
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(cfg.RAW_MOD, 'localization'), exist_ok=True)
    built = [build() for build in ALL_BUILDERS]
    for scene in built:
        scene.write()
    write_subtitles(built)
    write_lipmap(built)
