r"""Return Ticket: the scenes.

    python tools\gig04\gen_scenes.py

  gig04_brief        Hodan rings V with the job, a day after her
                     introduction. VIDEO HOLOCALL, her on the studio floor.
                     Five lines of hers, three of V's.
  gig04_close        Her last call: he is out, the fee is on its way.
  gig04_close_dead   The same call with one more line, for a V who killed
                     Stamps. The quest phase picks which of the two to play.
  gig04_stall        Ligaya at her stall, in person. Her four lines, V's two.
  gig04_booth        Stamps on his couch. His three lines, then Body,
                     Intelligence, 1,000 eddies or a fight; four exits, one
                     per choice, and a fifth for walking off.
  gig04_beaten       Stamps on the floor after the fight, giving the
                     address.
  gig04_room         Bayani at the back of the room. His four lines, V's two.

Modelled on `tools/fixer01/gen_scenes.py`, which is her own introduction call
and her phone conversation; read that file for the studio, the pose and the
builder. This header records only what is different.

THE LINES ARE THE DIALOGUE SHEET'S, the draft of record. Every phrase of hers
on it was searched in the game's recordings before it stayed. She is
invented, so an actor records her (`docs/conventions.md`, the voice rules).

V SPEAKS IN HER CALL, in recordings the game already made, whole
(`vanilla_sid`), the way V speaks in her phone conversation. All four exist
for both bodies (`tools/_vo_cache/voice_files.txt`, f_ and m_):

  0x1909989a1d4e6000  v_mq038   "I'm listening."
  0x185e47720d29f000  v_q104    "Where're they holding him?"
  0x174f0ffbce2e3000  v_q005    "On it."
  0x199875c34744d000  v_mq012   "Thanks."

None has a `vo_holocall` twin and none needs one: V is the near end of the
call (her own scenes play V's lines dry inside a call).

HER BODY AND HER STUDIO ARE HERS. The record `Character.cc_f01_fixer` and the
appearance `fixer01` ship in `mods/fixer-01`; the studio set is the one her
introduction borrows (Jefferson Peralez's, `tools/fixer01/gen_scenes.py`
"THE STUDIO"). This gig names them and ships no copy
(`mods/fixer-01/docs/design.md`, "What a gig of hers does").

TWO CLOSING SCENES, NOT ONE WITH A FORK IN IT. The extra line sits in the
middle of the call, and a fork that rejoins inside a scene is a shape this
repo has not played (her conversation forks and returns to a hub, never to a
line). Two scenes and a condition node in the quest phase is every piece
already proven. The lines the two share are recorded once: gen_voice reads
the second scene's masters for them from the first scene's files
(`MASTER`), the way her phone conversation reads her in-person takes.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from questkit.scene import (                                        # noqa: F401
    Scene, configure, write_subtitles, write_lipmap,
    ANCHOR_PLAYER, estimate_ms, line_ms, locstring_ruid, resref, cname,
    fnv1a64, attribute_check, payment_check, wait_option, yaw_to_face_player,
    JOHNNY_ACTOR,
)

from gig04_config import (                                          # noqa: E402
    SOURCE, RAW_MOD, DEPOT, FIXER_RECORD, FIXER_APPEARANCE, ANCHOR_STUDIO,
    LEAVE_RADIUS,
)
import gen_community                                                # noqa: E402

OUT_DIR = os.path.join(RAW_MOD, 'scenes')
SUBTITLE_MAP_OUT = os.path.join(RAW_MOD, 'localization', 'subtitles.json.json')
SUBTITLE_OUT = os.path.join(RAW_MOD, 'localization', 'gig04_lines.json.json')
SUBTITLE_DEPOT = DEPOT + chr(92) + 'localization' + chr(92) + 'gig04_lines.json'
# Where the scenes live once packed. gen_questphase.SCENES is the same string
# and has to stay so: the lipmap is keyed by FNV1a64 of exactly this path
# plus the scene name.
SCENE_DEPOT = DEPOT + chr(92) + 'scenes' + chr(92)
LIPMAP_OUT = os.path.join(RAW_MOD, 'localization', 'gig04.lipmap.json')

DURATIONS_FILE = os.path.join(SOURCE, 'audio', 'durations.json')
try:
    with open(DURATIONS_FILE, encoding='utf-8') as _fh:
        MEASURED = json.load(_fh)
except (OSError, ValueError):
    MEASURED = {}

LIPSYNC_PICKS = os.path.join(SOURCE, 'lipsync_picks.json')
try:
    with open(LIPSYNC_PICKS, encoding='utf-8') as _fh:
        _picks = json.load(_fh)
    LIPSYNC_SETS = _picks.get('sets', {})
    LIPSYNC_LINES = _picks.get('lines', {})
except (OSError, ValueError):
    LIPSYNC_SETS, LIPSYNC_LINES = {}, {}

# NOT USED: an alias points a whole scene at another's clips AND its lipsync
# set, and `gig04_close_dead` has a line of its own. gen_voice.MASTER shares
# the takes instead.
SCENE_ALIASES = {}

configure(
    out_dir=OUT_DIR,
    scene_depot=SCENE_DEPOT,
    subtitle_out=SUBTITLE_OUT,
    subtitle_map_out=SUBTITLE_MAP_OUT,
    subtitle_depot=SUBTITLE_DEPOT,
    lipmap_out=LIPMAP_OUT,
    lipmap_name='gig04.lipmap',
    durations=MEASURED,
    lipsync_sets=LIPSYNC_SETS,
    lipsync_lines=LIPSYNC_LINES,
    scene_aliases=SCENE_ALIASES,
)

# The actorName her lines carry. gen_voice's CAST and gen_lipsync's
# CHARACTERS name the same string.
ACTOR = 'hodan'

# WHERE SHE STANDS IN THE STUDIO, and the borrowed set's pose half: her own
# introduction's numbers (`tools/fixer01/gen_scenes.py`).
STUDIO_OFFSET = (0.0, 0.0, 0.0)
STUDIO_YAW = 0.0
STUDIO_POSE = ('#jefferson_holocall_workspot', '#jefferson_holocall_lookat')

V_LISTENING = ("I'm listening.", 0x1909989a1d4e6000)
V_WHERE = ("Where're they holding him?", 0x185e47720d29f000)
V_ON_IT = ("On it.", 0x174f0ffbce2e3000)
V_THANKS = ("Thanks.", 0x199875c34744d000)


def studio_pose(s, actor_name, actor, first_section):
    """Put the caller in the contact's studio spot and on the lens.

    Call it AFTER the section links: output sockets are written in order and
    the scene builder's own validation enforces that. Her introduction's
    helper, as is.
    """
    workspot, lookat_ref = STUDIO_POSE
    s.fire_workspot(first_section,
                    s.add_world_workspot_node(actor_name, workspot),
                    start_time=0)
    lookat = s.add_lookat_prop('cc_g04_holocall_lookat', lookat_ref)
    for sec in s.sections():
        s.look_at(sec, actor, lookat, start_time=0)


def call_scene(name, entry, exit_, turns):
    """One video call of hers: a chain of one-line sections.

    `turns` is a list of ('H', text, key) for a line of hers and
    ('V', text, stringId, key) for one of V's recordings. One section per
    line, so each paces from its own clip; the last gets a beat before the
    call drops, which is what the game's own calls do.
    """
    s = Scene(name, ANCHOR_STUDIO)
    n = s.add_actor(ACTOR, FIXER_RECORD, offset=STUDIO_OFFSET, yaw=STUDIO_YAW,
                    force_visible=True, appearance=FIXER_APPEARANCE)
    v = s.add_player()

    start = s.start(entry)
    secs = []
    for i, turn in enumerate(turns):
        final = i == len(turns) - 1
        if turn[0] == 'V':
            _who, text, sid, key = turn
            secs.append(s.section([s.add_line(v, text, key=key,
                                              vanilla_sid=sid)],
                                  tail_ms=600 if final else 0))
        else:
            _who, text, key = turn
            secs.append(s.section([s.add_line(n, text, key=key)],
                                  holocall=True, tail_ms=600 if final else 0))
    out = s.end(exit_)

    s.link(start, secs[0])
    for x, y in zip(secs, secs[1:]):
        s.link_section(x, y)
    s.link_section(secs[-1], out)
    studio_pose(s, ACTOR, n, secs[0])
    return s


# ---------------------------------------------------------------- the lines
BRIEF = [
    ('H', "V, I got a job for you. There's a man in Kabuki. The Tyger "
          "Claws took him last night.", 'c01'),
    ('V',) + V_LISTENING + ('v_listening',),
    # THE CONTRACT IS THE TRAP, not his breaking it (the design call,
    # 2026-10-15: "seems like it's his fault"). The game's own Crystal
    # Palace job advert takes the flight up and the rent out of the pay.
    ('H', "Reynaldo Manalo. He cleaned rooms on an Orbital Air station. They "
          "charged him for the flight up, the bed he slept in, even the "
          "scraps of food he ate.", 'c02'),
    ('H', "After seven years of painful work, he owed more than the day he "
          "signed up. So he ran.", 'c02b'),
    # HOW HE GOT HERE, AND THAT HE WAS SOLD (the design call, 2026-10-15:
    # "He came here to NC, but someone found him"). The old friend moved up
    # from c04; "somebody" is Stamps, whom she cannot name yet.
    # NAMED HERE, so Ligaya's "Liban said..." names someone the player has
    # heard of (the design call, 2026-10-15).
    ('H', "An old friend of mine, Liban, got him down to Night City. "
          "Somebody here sold him out.", 'c02c'),
    ('V',) + V_WHERE + ('v_where',),
    ('H', "Nobody knows. They took him from his sister's stall in the "
          "market.", 'c03'),
    # c04 AND c05 ARE ONE LINE (the design call, 2026-10-15).
    ('H', "My friend sent his sister to me. She's the client. Talk to her. "
          "Details attached.", 'c04'),
    ('V',) + V_ON_IT + ('v_on_it',),
]

E01 = ('H', "His sister called. He's out of Night City.", 'e01')
# HOW HE LEFT: the old friend of c04 drove him out (dialogue sheet P4).
E01B = ('H', "My friend drove him out tonight.", 'e01b')
# HER REASON IS THE CLIENT, not the dead man (the design call, 2026-10-15:
# "does hodan know that guy? Why would she care?"). She never met Stamps.
E02 = ('H', "Stamps is dead. Maricel still has to live in that market.", 'e02')
# "TAKE CARE.": the read picked on 2026-11-01 (recording 43 at 303.4) says
# "Take care, V." and is cut before the name, the design call.
E03 = ('H', "Well done, V. Your fee will be in your account shortly. Take "
            "care.", 'e03')
V_END = ('V',) + V_THANKS + ('v_thanks',)

CLOSE = [E01, E01B, E03, V_END]
CLOSE_DEAD = [E01, E01B, E02, E03, V_END]


def build_brief():
    return call_scene('gig04_brief', 'brief_in', 'brief_out', BRIEF)


def build_close():
    return call_scene('gig04_close', 'close_in', 'close_out', CLOSE)


def build_close_dead():
    return call_scene('gig04_close_dead', 'close_dead_in', 'close_dead_out',
                      CLOSE_DEAD)


# =================================================== the three in person
#
# Each has the shape of the fixer's in-person conversation
# (tools/fixer01/gen_scenes.py build_face): the body is the community's,
# acquired through the community node (gotcha 102); the hub is pinned to the
# body, so the prompt shows only at arm's length; the scene ends on its last
# line or when V walks LEAVE_RADIUS away (a second destination on the hub's
# socket, dyno_default.scene node 145); every section holds the speaker's
# eyes on V. The lines are the dialogue sheet's.
#
# V'S RECORDINGS, all present for both bodies (tools/_vo_cache/voice_files.txt):
#
#   0x193253064e2e3000  v_mq037  "What happened?"
#   0x15554f0eea405000  v_q110   "I'll find him."
#   0x1af6c9ae9d404000  v_mq025  "How much?"
#   0x1a96bf839e386000  v_mq033  "Here."
#   0x17587813ec4e1000  v_q115   "Go on. Talk."
#   0x19ff37cd2e44d000  v_mq003  "Don't make me repeat myself."
#   0x18e468205a4e1000  v_q112   "C'mon, think about it."
#   0x19dc745e3d44d000  v_mq005  "Wrong answer."
#   0x1a2eccad502d2000  v_sq004  "Can you walk?"
#   0x19dc8ba4a344d000  v_mq005  "Go on, get outta here."

V_WHAT_HAPPENED = ("What happened?", 0x193253064e2e3000)
V_ILL_FIND_HIM = ("I'll find him.", 0x15554f0eea405000)
V_HOW_MUCH = ("How much?", 0x1af6c9ae9d404000)
V_HERE = ("Here.", 0x1a96bf839e386000)
V_GO_ON_TALK = ("Go on. Talk.", 0x17587813ec4e1000)
V_DONT_REPEAT = ("Don't make me repeat myself.", 0x19ff37cd2e44d000)
V_THINK_ABOUT_IT = ("C'mon, think about it.", 0x18e468205a4e1000)
V_WRONG_ANSWER = ("Wrong answer.", 0x19dc745e3d44d000)
V_CAN_YOU_WALK = ("Can you walk?", 0x1a2eccad502d2000)
# V answers his "Did Ligaya send you?" first (the design call, 2026-10-15).
# q105, both voices, said quietly at the Clouds front desk. Both "Yeah."
# recordings (sq024, q115) were too intense, and gigs 01 to 03 use them.
V_YEAH = ("That's right.", 0x1777c1a6b02b6000)
# V hears Orbital Air pull up outside (v_mq003, the game's own recording).
V_COMPANY = ("Looks like we got company...", 0x18e03de88b623000)
# V sends Bayani off after the fight (v_mq005, the game's own recording).
V_GET_OUTTA = ("Go on, get outta here.", 0x19dc8ba4a344d000)

# The actorNames the in-person lines carry; gen_voice and gen_lipsync name
# the same three strings, and gen_community's entries have the same names.
LIGAYA = gen_community.LIGAYA
STAMPS = gen_community.STAMPS
BAYANI = gen_community.BAYANI
CAST_REF = gen_community.build().community_ref

# WHAT STAMPS SAYS WHEN HE GIVES BAYANI UP, in both branches. The room is
# the one gen_room builds: a shuttered shop front in Little China, north of
# the market, its double door on the street.
# THE VAN, NOT THE SHOP: Stamps knows where the Claws put him first
# (the design call, 2026-10-13: an investigation at the Claws' van at the
# south end of Little China, further from the market).
# "THE CLAWS", NAMED: his shard no longer ties him to them, so "They" here
# could read as Orbital Air (the design call, 2026-10-15). PRESENT TENSE:
# he thinks Bayani is still in the van, and does not know the Claws have
# moved him (the design call, 2026-10-15); the empty van is the turn.
S05 = ("The Claws are keeping him in their van. Back of a yard in south "
       "Little China.")
# NO TIME OF DAY: Orbital Air arrives when V reaches Bayani, at any hour
# (audit 2026-10-13; the design call: "you've got a few hours").
S06 = "Orbital Air's coming for him. You've got a few hours."


def face_player(s, actor):
    """Hold the speaker's eyes on V for every section (gig 03's helper)."""
    player = s.player_performer()
    for sec in s.sections():
        s.look_at(sec, actor, player, start_time=0)


def chain(s, n, v, seq):
    """One section per line, chained: ('N', text, key) is the NPC, ('V',
    text, stringId, key) is one of V's recordings. Returns (first, last)."""
    secs = []
    for i, t in enumerate(seq):
        final = i == len(seq) - 1
        if t[0] == 'V':
            _w, text, sid, key = t
            secs.append(s.section([s.add_line(v, text, key=key, vanilla_sid=sid)],
                                  tail_ms=400 if final else 0))
        else:
            _w, text, key = t
            secs.append(s.section([s.add_line(n, text, key=key)],
                                  tail_ms=600 if final else 0))
    for x, y in zip(secs, secs[1:]):
        s.link_section(x, y)
    # Kept for a builder that hangs an event off one line (build_room).
    s.__dict__['_chain_secs'] = secs
    return secs[0], secs[-1]


def walk_away(s, hub, entry, left_name):
    """End the scene when V walks off while the prompt is up. Input ordinal 1
    on the wait: ordinal 0 on a quest node is CutDestination.

    Every hub of a conversation needs one. Playtest review 2026-10-01: the
    booth's second hub had none, so a V who could pick none of its buttons
    could not leave the conversation either. Called again for a second hub,
    it reuses the scene's one exit of that name."""
    gone = s.add_wait_distance_node(CAST_REF, LEAVE_RADIUS, entry=entry,
                                    cmp='Greater')
    ends = s.__dict__.setdefault('_walk_away_ends', {})
    if left_name not in ends:
        ends[left_name] = s.end(left_name)
    left = ends[left_name]
    s._node(hub)['outputSockets'][0]['destinations'].append(
        {'$type': 'scnInputSocketId',
         'isockStamp': {'$type': 'scnInputSocketStamp', 'name': 0, 'ordinal': 1},
         'nodeId': {'$type': 'scnNodeId', 'id': gone}})
    s.link(gone, left)


def in_person(name, entry, actor_name, prompt, seq, exit_name, left_name,
              workspot=None):
    """A prompt over a placed body, then a chain of lines, then out.

    Returns (scene, actor, lead, hub, last_section) so a builder can hang
    more off it (the booth's second choice)."""
    s = Scene(name, ANCHOR_PLAYER)
    n = s.add_community_actor(actor_name, actor_name, CAST_REF,
                              appearance=gen_community.APPEARANCE[actor_name])
    v = s.add_player()
    start = s.start(entry)
    lead = s.section([], lead_ms=0, tail_ms=500)
    hub = s.hub()
    opt = s.add_option(prompt, key='o01')
    choice = s.choice([opt], attach_actor=n)
    first, last = chain(s, n, v, seq)
    s.link(start, lead)
    s.link_section(lead, hub)
    s.link(hub, choice)
    s.link_choice(choice, [first])
    if exit_name is not None:
        s.link_section(last, s.end(exit_name))
    walk_away(s, hub, actor_name, left_name)
    if workspot is not None:
        # THE BODY STAYS IN ITS SITTING POSE while it talks: the scene plays
        # the same workspot on the community actor at its first beat (the
        # fixer's sofa lesson, tools/fixer01/gen_scenes.py sofa_pose).
        path, ws_entry = workspot
        node = s.add_workspot_node(actor_name, path=path, entry=ws_entry,
                                   community=(CAST_REF, actor_name))
        s.fire_workspot(lead, node, start_time=0)
    return s, n, v, lead, hub, last


STALL = [
    ('N', "Ay, Liban said she'd send somebody. Don't talk so loud.", 'l01'),
    ('N', "Reynaldo, Rey, is my brother. He came here three nights ago. I "
          "hadn't seen him in seven years.", 'l02'),
    ('V',) + V_WHAT_HAPPENED + ('v_happened',),
    ('N', "Two Tyger Claws came last night. They knew his name. They took "
          "him out the back.", 'l03'),
    # SHE POINTS AT STAMPS AND DOES NOT CONVICT HIM (the design call,
    # 2026-10-15: "must cast doubt without conclusion"). Her question is
    # the one his first line at the bar answers. "New identity" is the
    # game's own phrase; nobody in it says "new name" or "fake ID".
    ('N', "Only three people knew he was here. Me, Liban, and a man called "
          "Stamps.", 'l04'),
    ('N', "Stamps sells new identities. Rey went to him for one. Ask him "
          "who else he told.", 'l05'),
    ('N', "He's always on a couch in the alley behind the market.", 'l06'),
    ('V',) + V_ILL_FIND_HIM + ('v_find',),
]

# STAMPS. V asks for the janitor; he says what he did and that Orbital Air
# has already paid him, so selling the address again costs him nothing,
# and that it is not free. Then the choice, three ways to the same two
# lines: Body to scare it out of him, Intelligence to sell him on Hodan's
# custom, or 1,000 eddies (the design call, 2026-10-01: "options based on
# the level of the user, check how vanilla does"; "he must explain he
# already got paid so got nothing to lose").
BOOTH = [
    # HIS OWN WORDS, the design call of 2026-10-15. s02 answers Ligaya's
    # "Ask him who else he told."
    # THE SUBTITLES FOLLOW THE TAKES (the actors' delivery of 2026-10-24):
    # s01, s02, s06, s07 and s08 as said.
    ('N', "Ah, the janitor. He wanted a new name.", 's01'),
    ('N', "I ask everybody who they're running from. He said Orbital Air. "
          "Orbital Air paid better for a tip.", 's02'),
    ('N', "They paid me already. I got nothing to lose telling you. "
          "But I don't tell for free.", 's03'),
]
BOOTH_PAY = [
    ('V',) + V_HERE + ('v_here',),
    ('N', "Pleasure.", 's04'),
    ('N', S05, 's05'),
    ('N', S06, 's06'),
]
BOOTH_THREAT = [
    ('V',) + V_DONT_REPEAT + ('v_repeat',),
    ('N', "Okay! Okay. Hands where I can see them.", 's07'),
    ('N', S05, 's05t'),
    ('N', S06, 's06t'),
]
BOOTH_DEAL = [
    ('V',) + V_THINK_ABOUT_IT + ('v_think',),
    ('N', "Warsame. Her people pay on time. Fine.", 's08'),
    ('N', S05, 's05i'),
    ('N', S06, 's06i'),
]
# THE FOURTH WAY, which needs nothing and always works: V starts a fight.
# He cannot die in it; at a third of his health he goes down, and the
# beaten scene below has him give the address from the floor (gig 02's
# merc; the design call, 2026-10-01: "shoot him until he's down, but not
# allowed to kill, and get the info").
BOOTH_FIGHT = [
    ('V',) + V_WRONG_ANSWER + ('v_wrong',),
]
BEATEN = [
    ('N', "Stop! Stop! Okay!", 's09'),
    ('N', S05, 's05f'),
    ('N', S06, 's06f'),
]

# THE CHECKS ARE THE GAME'S OWN, read off the Kabuki street stories
# (questkit.scene.attribute_check has the account). One content assignment
# and one difficulty for both, so Body and Intelligence ask for the same
# number: `sts_wat_kab_03`'s, the Kabuki gig whose Body check is MEDIUM.
CHECK_ASSIGNMENT = 'DeviceContentAssignment.sts_wat_kab_03'
CHECK_DIFFICULTY = 'MEDIUM'
PRICE = 1000

ROOM = [
    ('N', "Who are you? Did Maricel send you?", 'b01'),
    ('V',) + V_YEAH + ('v_right',),
    ('V',) + V_CAN_YOU_WALK + ('v_walk',),
    ('N', "Yes. I can walk.", 'b02'),
    ('N', "Seven years up there. I owed more at the end than the day I "
          "signed.", 'b03'),
    ('N', "I'm not going back up.", 'b04'),
    # V HEARS THEM PULL UP: Orbital Air's car arrives during the talk
    # (gen_questphase), and V says so in the game's own words. The design
    # call, 2026-10-13, on a warning from Bayani: "how would he know?".
    ('V',) + V_COMPANY + ('v_company',),
]
# AFTER THE FIGHT, his goodbye (the design call, 2026-10-14: "he says
# goodbye and thanks, and then runs"). V sends him off in the game's own
# words; he runs as the scene ends (gen_questphase).
BYE = [
    ('N', "Thank you. I thought I'd be back in that hell by morning.", 'b05'),
    ('N', "I'm going to say goodbye to Maricel. Then I'm gone.", 'b06'),
    ('V',) + V_GET_OUTTA + ('v_go',),
]
# NO "GO ON, GET OUTTA HERE" DURING THE FIRST TALK. Orbital Air arrives as this ends and
# he stays in the cell until they are down, so V's line had him sit through
# the fight after being told to go (audit 2026-10-02, on the playtest
# "the brother takes too much time from when we say to go"). He runs as the
# last guard falls.


def build_stall():
    """Ligaya at her stall: one prompt, her four lines, V's two."""
    s, n, _v, _lead, _hub, _last = in_person(
        'gig04_stall', 'stall_in', LIGAYA, "Maricel Manalo?", STALL,
        'stall_out', 'stall_left')
    face_player(s, n)
    return s


def build_booth():
    """Stamps on his couch. A prompt, his three lines, then the choice:
    Body, Intelligence, or pay. All three say the same two lines and end at
    their own exit, so the quest phase knows which V chose. The shared
    lines are recorded once (gen_voice.MASTER_KEY). The game takes the
    money itself when the payment is picked."""
    s, n, v, _lead, _hub, last = in_person(
        'gig04_booth', 'booth_in', STAMPS, "Looking for the janitor.", BOOTH,
        None, 'booth_left', workspot=(gen_community.BARSTOOL, 2))
    # THE CHOICE, a second hub pinned to him, in the receptionist's order
    # (sts_wat_kab_04, node 56): the checks, then the payment. A check V
    # fails is drawn red and cannot be picked; V without the money sees
    # the payment red. A V who can pick none walks off, and the prompt
    # comes back (the quest re-arms on `booth_left`), or kills him, and
    # Hodan texts the address.
    hub2 = s.hub()
    fight = s.add_option("Then I'll beat it out of you.", key='o05')
    threat = s.add_option("Tell me where he is.", key='o03')
    deal = s.add_option("Hodan Warsame sends work to people who help her.",
                        key='o04')
    pay = s.add_option("Pay for the address.", key='o02')
    choice2 = s.choice(
        [threat, deal, pay, fight], attach_actor=n,
        checks=[attribute_check('PlayerBuilds.Solo', CHECK_ASSIGNMENT,
                                CHECK_DIFFICULTY),
                attribute_check('PlayerBuilds.Netrunner', CHECK_ASSIGNMENT,
                                CHECK_DIFFICULTY,
                                icon='ChoiceCaptionParts.HackingIcon'),
                payment_check(PRICE),
                None])
    t_first, t_last = chain(s, n, v, BOOTH_THREAT)
    f_first, f_last = chain(s, n, v, BOOTH_FIGHT)
    d_first, d_last = chain(s, n, v, BOOTH_DEAL)
    p_first, p_last = chain(s, n, v, BOOTH_PAY)
    s.link_section(last, hub2)
    s.link(hub2, choice2)
    s.link_choice(choice2, [t_first, d_first, p_first, f_first])
    s.link_section(t_last, s.end('booth_threat'))
    s.link_section(f_last, s.end('booth_fight'))
    # THE WAY OUT OF THE SECOND HUB, the same exit as the first's.
    walk_away(s, hub2, STAMPS, 'booth_left')
    # WHICH BUTTON, written as its first line starts (`cc_g04_booth_picked`):
    # a V who walks off during the answer leaves by the walk-away exit, and
    # the quest reads this to treat the walk-off as the pick (gen_questphase,
    # "WALKED OFF"). 1 Body, 2 Intelligence, 3 paid, 4 the fight. AFTER every
    # link: an event added before a section's links puts its socket first,
    # which the builder refuses (Scene.write's socket-order check).
    for _sec, _n in ((t_first, 1), (d_first, 2), (p_first, 3), (f_first, 4)):
        s.fire_event(_sec, s.add_fact_node('cc_g04_booth_picked', _n), start_time=0)
    s.link_section(d_last, s.end('booth_deal'))
    s.link_section(p_last, s.end('booth_paid'))
    # BACK FOR THE BUTTONS: a second way in, `booth_again`, straight to the
    # choice, for a V who walked off after his three lines (to fetch the
    # money, or because every check was red). Through `booth_in` he said
    # them again on every approach (audit 2026-10-02). The quest picks the
    # entry on `cc_g04_booth_heard`, written as his third line ends.
    again = s.start('booth_again')
    lead2 = s.section([], lead_ms=0, tail_ms=500)
    s.link(again, lead2)
    s.link_section(lead2, hub2)
    ws2 = s.add_workspot_node(STAMPS, path=gen_community.BARSTOOL,
                              entry=2, community=(CAST_REF, STAMPS))
    s.fire_workspot(lead2, ws2, start_time=0)
    s.fire_event(last, s.add_fact_node('cc_g04_booth_heard', 1), start_time=0)
    face_player(s, n)
    return s


def build_beaten():
    """Stamps on the floor, beaten: his three lines and out. No prompt; the
    quest plays it three seconds after he goes down (gig 02's merc, whose
    fall and settle take that long). He stays where the fight left him: the
    script holds him down with the game's own Defeated fall and Bleeding,
    so the scene plays no pose."""
    s = Scene('gig04_beaten', ANCHOR_PLAYER)
    n = s.add_community_actor(STAMPS, STAMPS, CAST_REF,
                              appearance=gen_community.APPEARANCE[STAMPS])
    v = s.add_player()
    start = s.start('beaten_in')
    first, last = chain(s, n, v, BEATEN)
    s.link(start, first)
    s.link_section(last, s.end('beaten_out'))
    face_player(s, n)
    return s


def build_bye():
    """Bayani after the fight, come out of the cell to V: thanks, goodbye."""
    s, n, _v, _lead, _hub, _last = in_person(
        'gig04_bye', 'bye_in', BAYANI, "Time to go.", BYE,
        'bye_out', 'bye_left')
    face_player(s, n)
    return s


def build_room():
    """Bayani at the back of the room, once the Claws are dealt with."""
    s, n, _v, _lead, _hub, _last = in_person(
        'gig04_room', 'room_in', BAYANI, "Reynaldo Manalo?", ROOM,
        'room_out', 'room_left')
    face_player(s, n)
    # HE GETS UP ON "Yes. I can walk." (the design call, 2026-10-14: "make
    # him get up while he talks with V the first time"). The line raises
    # `cc_g04_bayani_up` as it starts, a side event the talk does not wait
    # on, and Gig04_Places.reds sends his sitting pose its fast exit: the
    # get-up the game plays when a seated NPC is pulled out. A standing
    # idle played on him from here snapped him up with no animation
    # (playtest 2026-10-14).
    can_walk = [i for i, t in enumerate(ROOM) if t[-1] == 'b02'][0]
    s.fire_event(s._chain_secs[can_walk], s.add_fact_node('cc_g04_bayani_up'),
                 start_time=0)
    # ORBITAL AIR COMES ON "Looks like we got company...", not after the
    # talk has ended (the design call, 2026-10-14: "too much delay between
    # when he says we got company and when Orbital Air starts attacking"):
    # the line raises `cc_g04_oa_armed` as it starts. They wait out of sight
    # on the street beside the door (gig04_config OA_GUARDS); on this the
    # quest sends them in along their paths at a sprint, and
    # Gig04_Places.reds turns each on V once he is inside (the design call,
    # 2026-10-25: "they appear where the player cannot see them, then become
    # hostile and ... run inside"). Nothing holds V any more. The quest sets
    # the fact again after the talk, which changes nothing.
    company = [i for i, t in enumerate(ROOM) if t[-1] == 'v_company'][0]
    s.fire_event(s._chain_secs[company], s.add_fact_node('cc_g04_oa_armed'),
                 start_time=0)
    return s


# THE WAITING SPOT, gig 02's `build_lean` (tools/gig02/gen_scenes.py, "the
# two waits"): a prompt at the marker, in the game's own wording for the
# beat ("Lean on the barrier and wait for Takemura."), the lean fired onto
# V at the spot, `cc_g04_rail_taken` written, and a hold on
# `cc_g04_rail_release`, which the quest writes behind a fade. No line is
# spoken. The prompt's range reaches the pose, and the yaw limit is off,
# because V at a railing faces the view rather than the marker.
def build_rail():
    """The railing west of the building, while V waits for Hodan."""
    s = Scene('gig04_rail', gen_community.RAIL_MARKER_REF)
    s.add_player()
    start = s.start('rail_in')
    # THE WAIT ICON, AND NOT IN COMBAT, the big Claire race's lean
    # (questkit.scene.wait_option, read 2026-11-01).
    c1 = s.choice([s.add_option("Lean on the railing and wait for Hodan's call.",
                                key='o20')],
                  in_world=True, radius=2.5, yaw_limit=360,
                  checks=[wait_option()])
    s1 = s.section([], tail_ms=1200)
    taken = s.add_fact_node('cc_g04_rail_taken', 1)
    release = s.add_wait_fact_node('cc_g04_rail_release')
    out = s.end('rail_out')
    s.link(start, c1)
    s.link_choice(c1, [s1])
    s.link_section_quest(s1, taken)
    # AFTER the section is linked: sockets are written in (name, ordinal)
    # order and validate() enforces it.
    s.fire_workspot(s1, s.add_world_workspot_node(
        None, gen_community.RAIL_SPOT_REF, player=True), start_time=0)
    s.link_quest(taken, release)
    s.link(release, out)
    return s


# ============================================================ Johnny
#
# TWO LINES OF HIS, each its own short scene staged at V, the shape gig 03's
# `build_destroy` uses (docs/scene-playbook.md, "STAGING A CHARACTER WHO
# SPEAKS, LIPSYNCS AND STANDS BESIDE V"): Johnny beside V and facing him, a
# line from his own recording, in V's head. Both are base-game recordings, so
# a V without Phantom Liberty hears them too.

# AT THE VAN, before the clue hunt (the design call, 2026-10-14: "Johnny
# popup when we find the van"). mq036. His first line here, "Nothing here
# ... swept the place clean", was said over three clues (dialogue sheet P1).
J_NOTHING = ("Look around and connect the dots.", 0x192802b3002e3000)
# AFTER HER LAST CALL, once Bayani is out (the design call, 2026-10-14:
# "something that brings us back to earth"). q112.
J_ALONE = ("Doesn't matter how good you are in Night City. On your own, "
           "you're fucked.", 0x1897e763a14e1000)


def _johnny_beat(name, line, key):
    s = Scene(name, ANCHOR_PLAYER)
    j = s.add_johnny(offset=(1.0, 2.1, 0.0),
                     yaw=yaw_to_face_player((1.0, 2.1, 0.0)))
    s.add_player()
    start = s.start(name.replace('gig04_', '') + '_in')
    # 1.5 s BEFORE HE SPEAKS, not the default 0.7: he is still appearing
    # until then (playtest 2026-10-14: "he starts talking before he
    # appears, while still glitching").
    s1 = s.section([s.add_line(j, line[0], key=key, vanilla_sid=line[1])],
                   inner=True, tail_ms=600, lead_ms=1500)
    out = s.end(name.replace('gig04_', '') + '_out')
    s.link(start, s1)
    s.link_section(s1, out)
    s.stage_johnny(s1, s1)
    return s


def build_johnny_van():
    """At the Claws' van, as V reaches it: Johnny says there is nothing here."""
    return _johnny_beat('gig04_johnny_van', J_NOTHING, 'j01')


def build_johnny_end():
    """After Hodan's last call: Johnny on Orbital Air."""
    return _johnny_beat('gig04_johnny_end', J_ALONE, 'j02')


ALL_BUILDERS = (build_brief, build_close, build_close_dead,
                build_stall, build_booth, build_beaten, build_room, build_bye, build_rail,
                build_johnny_van, build_johnny_end)


if __name__ == '__main__':
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(RAW_MOD, 'localization'), exist_ok=True)
    built = [build() for build in ALL_BUILDERS]
    for scene in built:
        scene.write()
    write_subtitles(built)
    write_lipmap(built)
