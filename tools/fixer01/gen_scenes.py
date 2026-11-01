r"""Fixer 01: the scenes. Her introduction call, and her conversation.

    python tools\fixer01\gen_scenes.py

  fixer01_intro   she rings V once, the first time V is near her sofa after
                  the prologue, and says who she is and what she buys.
                  VIDEO HOLOCALL, her lines only. V says nothing, which is how
                  the game's own fixers do it (Dino: "Ya don't know me, but
                  you will. Name's Dino. Deal with downtown, City Center."
                  Regina: "If you're looking for work in Watson, give me a
                  call." Dakota, Mr. Hands, El Capitan: the same two beats,
                  name and district, then "call me").
  fixer01_face    her conversation, IN PERSON: walk up to her on the lobby
                  sofa and the prompt hangs over her. Five options,
                  four questions and a goodbye, each one V's question and
                  her answer, and the hub comes back after each answer.
                  The scene also ends on its own when V walks away.
  fixer01_call    the same conversation ON THE PHONE, when V rings her from
                  the contact list: the hub on the screen, her on the studio
                  floor, her answers through the phone. The goodbye hangs up.

THE CONVERSATION IS THE GAME'S OWN SHAPE. Every fixer's `<name>_default.scene`
(read 2026-09-18: Dino, Wakako, Regina, and the subtitle files of the other
four) is one hub of four or five options serving both the in-person talk and
the call: a district question ("What's up in City Center?", "Tell me about
the Badlands"), one or two about the fixer ("You knew Silverhand?", "Why
'El Capitan'?"), sometimes one about work ("How's biz?"), and a goodbye
("Gotta delta.", "Talk later.", "See you around."). Each option is V's
spoken question, the fixer's answer, and back to the hub. Hers is the same
five: the district, work, business, herself, and leaving.

V'S QUESTIONS ARE RECORDINGS THE GAME ALREADY MADE, whole, cast from the
corpus (docs/conventions.md, the voice rules; `vanilla_sid`). Each was
picked because it is generic enough to be asked of anyone. The hub captions
are short paraphrases, which is
how the game's own hubs work ("You knew Silverhand?" on the button, "You
knew Johnny Silverhand?" spoken). Her answers are written here for the
actor, and until the takes land they are placeholder tones.

ONE SCRIPT, TWO SCENES. The game does it with one scene, two actors (the
body at the bar and the body in the studio) and a fact that pushes the hub
to the screen during a call. Two scenes with the same lines is the same
thing for the player and lets each use the builder's proven route: the
in-person scene acquires her community body (gig 03's bar), the phone scene
spawns her on the studio floor (her introduction). gen_voice reads the phone
scene's masters from the in-person scene's files, so the actor records each
answer once; the phone copy gets the phone treatment.

Modelled on `tools/gig02/gen_scenes.py` (Char's video call is the worked
example of an invented caller on the studio floor) and `tools/gig03/`.
Those files carry the account of the scene builder; this header records
what is different.

WHO SHE IS. Hodan Warsame (the design call, 2026-09-21: Somali; Hodan a
common Somali given name, Warsame a Somali family name. Nzinga Okoro until
then, a name of Angolan and Igbo heritage that a Somali woman would not
carry). In the game's own lore Somalia is a member of the Pan-African
Alliance and the Night City Journal's top vacation destination of 2075, so
she comes from a country on its way up, not out of a war. She does
business from a sofa in the lobby of a Charter Hill tower (the design call,
2026-09-18; a Kabuki lockup until then), and what she trades in is what
the city throws away: footage, ledgers, names, the things people pay to
lose or pay to find. Her gigs are that kind of work: quiet retrievals,
disappearances of evidence, people who need to stop existing on paper. The
mod's own three gigs are all about records already (a ledger, a forged tag,
a training log), so she is the fixer those stories were missing.

SHE DOES NOT WORK FOR THE CORPS, AND SHE HAS DONE THE WORK HERSELF (the
design call, 2026-09-21, hardened 2026-09-26). Canon allows the stance and
has one already: El Capitan, in his own default lines, "Corpo world's a
disease. Power's gotta get back in the hands of the people." The game's
top fixer, Rogue, ran with Silverhand and has the 2023 Arasaka raid on her
record, and the sneer that she "became a glorified corporate matchmaker"
is how far a fixer can drift the other way. Hodan is written to the early
Rogue end of that line.

Her history is a smuggler's, and every piece of it is the game's own
material. Orbital Air is the Kenyan megacorp founded in Nairobi that
"controls most of the world's spaceports, including the largest cosmodrome
in Mogadishu" (its own in-game pages). Space is "controlled by three major
players: Orbital Air, the European Space Council and the Highriders", the
Highriders being the spacers who "live among the stars", many of whom
"emigrated from Africa and, obviously, Kenya". A news item has thieves
docking with a station under cover of a solar storm and breaching an
Orbital Air laboratory, so freight crime in orbit is canon. Orbital Air
also runs Night City's own spaceport, NCX, with its own guards, its
credentials and its datafort (the whole of Phantom Liberty's spaceport
act). So: she loaded rockets on the Mogadishu pads, ran the freight the
company would not carry up to the stations, lost her crew on a pad, and
cannot fly anywhere because the same corporation holds the gate at both
ends. She sends other people instead.

THE STANCE IS A PREFERENCE, NOT A BAN (the design call, 2026-09-26). A
fixer who never touches corp money does not exist in this game, and the
gig calls prove it: El Capitan, whose own default lines call the corpo
world a disease, sells V "a client who needs help with some internal
corpo skullduggery" and a break-in at the Cytech factory; Rogue's client
is "some hotshot from Kang Tao"; Regina's client, once, is China. So most
of Hodan's work is aimed at a corp, she will take one suit's money
against another suit, and she has two limits she states once: Arasaka
money does not reach her couch, and she does not put a person in a corp's
hands. The second is her own history, since the people she used to fly
were the cargo the company wanted back.

In the game's own words the people are "corpos" and "suits" and the
companies "corps"; nobody in Night City says "anti-corporate".

HER REGISTER. Exact, unhurried, no warmth she has not decided to spend.
She does not swear on a first call. WHOLE SENTENCES, THE WAY THE GAME'S
FIXERS TALK (the design call, 2026-09-21: the first draft's fragments, "the
doors tend to have logos on them", "Charter Hill, a tower on Palm Street,
the sofa by the lifts", read as artificial next to "If you're looking for
work in Watson, give me a call"). A corp is called a corp, plainly, as
Regina, Dino, El Capitan and Rogue all do; nobody in the city talks around
the word. Three lines, because the game's fixers use two and she has a job
type to name.

WHERE THE WORDS COME FROM. She is invented, so she is recorded by a voice
actor (docs/conventions.md, the voice rules) and her lines are written freely
here.

THE STUDIO. An invented caller has no setup of her own, so she borrows one
(docs/scene-playbook.md, "The MOD-OWNED recipe"): the five names of a
contact's set are only correct together, and the set decides her pose. She
takes JEFFERSON PERALEZ'S: standing, arms crossed
(`generic__stand_ground_arms_crossed__stand_around__02`), camera at 1.516,
read off the studio's quest sector on 2026-09-18, with the lighting variant
`jefferson_holocall_lights` read off `jefferson_holocall.scene`. Arms crossed
is a fixer sizing somebody up. gen_questphase names the same set.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from questkit.scene import (                                        # noqa: F401
    Scene, configure, write_subtitles, write_lipmap,
    ANCHOR_PLAYER, estimate_ms, line_ms, locstring_ruid, resref, cname,
    fnv1a64, yaw_to_face_player, JOHNNY_ACTOR,
)

from fixer01_config import (                                        # noqa: E402
    SOURCE, RAW_MOD, DEPOT, FIXER_RECORD, ANCHOR_STUDIO, LEAVE_RADIUS,
    FIXER_WORKSPOT, FIXER_WORKSPOT_ENTRY,
)
import gen_npv                                                      # noqa: E402
import gen_community                                                # noqa: E402

OUT_DIR = os.path.join(RAW_MOD, 'scenes')
SUBTITLE_MAP_OUT = os.path.join(RAW_MOD, 'localization', 'subtitles.json.json')
SUBTITLE_OUT = os.path.join(RAW_MOD, 'localization', 'fixer01_lines.json.json')
SUBTITLE_DEPOT = DEPOT + chr(92) + 'localization' + chr(92) + 'fixer01_lines.json'
# Where the scenes live once packed. gen_questphase.SCENES is the same string
# and has to stay so: the lipmap is keyed by FNV1a64 of exactly this path
# plus the scene name.
SCENE_DEPOT = DEPOT + chr(92) + 'scenes' + chr(92)
LIPMAP_OUT = os.path.join(RAW_MOD, 'localization', 'fixer01.lipmap.json')

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

SCENE_ALIASES = {}

configure(
    out_dir=OUT_DIR,
    scene_depot=SCENE_DEPOT,
    subtitle_out=SUBTITLE_OUT,
    subtitle_map_out=SUBTITLE_MAP_OUT,
    subtitle_depot=SUBTITLE_DEPOT,
    lipmap_out=LIPMAP_OUT,
    lipmap_name='fixer01.lipmap',
    durations=MEASURED,
    lipsync_sets=LIPSYNC_SETS,
    lipsync_lines=LIPSYNC_LINES,
    scene_aliases=SCENE_ALIASES,
)

# The actorName her lines carry. gen_voice's CAST and gen_lipsync's
# CHARACTERS name the same string.
ACTOR = 'hodan'

# WHERE SHE STANDS IN THE STUDIO: on the marker, and the workspot node moves
# her onto the contact's spot from there (gig 02's measured pairing).
STUDIO_OFFSET = (0.0, 0.0, 0.0)
STUDIO_YAW = 0.0

# THE BORROWED SET'S POSE HALF. The other three names are in gen_questphase.
STUDIO_POSE = ('#jefferson_holocall_workspot', '#jefferson_holocall_lookat')


def studio_pose(s, actor_name, actor, first_section):
    """Put the caller in the contact's studio spot and on the lens.

    Call it AFTER the section links: output sockets are written in order and
    the scene builder's own validation enforces that. Gig 02's helper, as is.
    """
    workspot, lookat_ref = STUDIO_POSE
    s.fire_workspot(first_section,
                    s.add_world_workspot_node(actor_name, workspot),
                    start_time=0)
    lookat = s.add_lookat_prop('cc_f01_holocall_lookat', lookat_ref)
    for sec in s.sections():
        s.look_at(sec, actor, lookat, start_time=0)


def build_intro():
    """She rings V once, and says who she is.

    One section per line so each paces from its own clip. `tail_ms` on the
    last gives the picture a beat before the call drops, which is what the
    game's own intro calls do.
    """
    s = Scene('fixer01_intro', ANCHOR_STUDIO)
    n = s.add_actor(ACTOR, FIXER_RECORD, offset=STUDIO_OFFSET, yaw=STUDIO_YAW,
                    force_visible=True, appearance=gen_npv.APPEARANCE)
    v = s.add_player()

    start = s.start('intro_in')
    s1 = s.section([
        s.add_line(n, "V, right? Hodan Warsame here. I work in "
                      "Charter Hill, only with the best.", key='n01'),
    ], holocall=True)
    # V'S ONE REPLY, the game's own shape: every fixer's introduction gives
    # V one line in the middle and keeps the last word (Dino, Regina, El
    # Capitan, Mr. Hands, Padre; their default scenes, read 2026-10-14).
    # V's recording from sq025, both voices; her "Heard about you."
    # answers it (the design call, 2026-10-14, option A on the sheet).
    sv = s.section([
        s.add_line(v, "Know my name... how?", key='v_intro',
                   vanilla_sid=0x196f808a1e62a000),
    ])
    s2 = s.section([
        s.add_line(n, "Heard about you. You get in and you get out. "
                      "Some of my work is quiet, some isn't. Most of my "
                      "clients have a problem with a corp.", key='n02'),
    ], holocall=True)
    s3 = s.section([
        s.add_line(n, "I'll send you my number and the address. If you're "
                      "looking for work in Charter Hill, call me.", key='n03'),
    ], holocall=True, tail_ms=600)
    out = s.end('intro_out')

    s.link(start, s1)
    s.link_section(s1, sv)
    s.link_section(sv, s2)
    s.link_section(s2, s3)
    s.link_section(s3, out)
    studio_pose(s, ACTOR, n, s1)
    return s


# ------------------------------------------------------------ her conversation
#
# (caption, V's recorded question, its stringId, her answer, line key).
# The caption is what the hub shows; the question is what V says on picking
# it, VERBATIM the game's text, which is what appears as the subtitle.
#
#   0x1b6d1ca75344d000  v_glen                          a Glen street line
#   0x1af65c10f22d2000  v_scene_rogue_default          asked of Rogue
#   0x1b20a252882ef000  v_scene_muamar_reyes_default   asked of El Capitan
#   0x19ebe38f7b623004  v_kabuki                        a Kabuki street line
#   0x187e45951346b000  v_charter_hill                  a Charter Hill street line
#   0x1b258f89ed2ef000  v_scene_padre_default          Padre's goodbye
#
# All five exist for both bodies (`voice_files.txt`, f_ and m_). None has a
# `vo_holocall` twin, and none needs one: V is the near end of the call, and
# the phone treatment is the far end's (the game's own fixer scenes play these
# same V lines dry inside a call).
# EACH BUTTON IS AN EXCHANGE, NOT A SPEECH. Read off the seven fixers'
# default scenes on 2026-09-21: of their 39 non-goodbye buttons, 28 have V
# follow up with a second recorded line and 11 have the fixer simply keep
# talking, and in all 39 the fixer speaks two to four SHORT lines (median
# 11 words, two of 119 over 25), each its own recording and subtitle. So a
# button here is a list of turns: ('V', text, stringId) is one of V's
# recordings, whole; ('H', text, key) is one line of hers. V's follow-ups
# are the game's short generic ones, present in both voices: "And?"
# (sq031), "What's the catch?" (sts_std_arr_12), "So?" (q112), "Like
# what?" (Kerry's default scene), "Why'd you leave?" (sq026); "And
# you?" (q113), "Meaning?", "How so?", "Why's that?" and "What do you
# mean?" also exist if a line is reworded. The mix of
# follow-up and no-follow-up buttons is the fixers' own.
V_AND = ("And?", 0x194baae8bd351000)
V_CATCH = ("What's the catch?", 0x17119c63ae559000)
V_SO = ("So?", 0x18935d86234e1000)
V_LIKE_WHAT = ("Like what?", 0x1ae7b865a129f000)
V_WHY_LEAVE = ("Why'd you leave?", 0x1a76a73c822fc000)

# THE LINES ARE THE DIALOGUE SHEET'S (the draft of record, 2026-09-28). Every word of hers was checked against the
# recordings, and V's follow-ups are recordings; the sheet's closing notes
# carry the evidence line by line. Her story: a lawyer from a good family,
# hired by Orbital Air at the Mogadishu spaceport, who read the labor
# contracts (the shard "The Long Return: Aftermath of the Great Nomad
# Tragedy" is the canon for them), ran the smugglers who got people off the
# stations, and escaped to Night City when Orbital Air ambushed a run.
TALK = [
    ("What's your story?", 'a04', [
        ('V', "What's your story? Who are you?", 0x19ebe38f7b623004),
        ('H', "Mogadishu. Good family, law school. Then Orbital Air hired "
              "me as a lawyer at the spaceport.", 'a04'),
        ('V',) + V_SO,
        ('H', "So I read the contracts. People signed for years on a "
              "station and never paid off the debt. They were written so "
              "nobody could.", 'a04b'),
        ('H', "I started helping the smugglers who got people out. Inside a "
              "year I was running things.", 'a04c'),
        ('V',) + V_WHY_LEAVE,
        ('H', "Orbital Air found out, ambushed us. Most of my crew and "
              "passengers didn't make it out. I escaped to Night City.",
         'a04d'),
        ('H', "Now I find mercs. Some of my clients are suits fighting other "
              "suits. The rest have a problem with a corp. So do I.", 'a04e'),
    ]),
    # THE DIVORCE UPSTAIRS is the gig this building was built for, "Until
    # Death Do Us Part" (Wakako's: Emilio Gutierrez, a politician, lost the
    # penthouse and his "depository receipts", the gig's own words, to his
    # ex-wife Nina, and wants the receipts back from her apartment). True
    # until V has done it, and she would know either way: once the gig is
    # finished this button's answer is AFTER_THE_GIG's.
    ("What's new around here?", 'a01', [
        ('V', "What's new in the neighborhood?", 0x1b6d1ca75344d000),
        ('H', "There's a divorce going on upstairs.", 'a01'),
        ('V',) + V_AND,
        ('H', "He's a politician. She got the penthouse and his depository "
              "receipts.", 'a01b'),
        ('H', "He's paying somebody in Japantown to get them back. It's got "
              "nothing to do with you.", 'a01c'),
    ]),
    ('Any work?', 'a02', [
        ('V', "I was wondering... wouldn't happen to have any gigs for me?",
         0x1af65c10f22d2000),
        ('H', "When I've got something for you, I'll be in touch.", 'a02'),
        ('V',) + V_CATCH,
        ('H', "No catch. I don't take Orbital Air money. I don't hand "
              "people over to a corp.", 'a02b'),
        ('H', "Anything else, we can talk about.", 'a02c'),
    ]),
    ("How's business?", 'a03', [
        ('V', "How's biz?", 0x1b20a252882ef000),
        ('H', "Can't complain. Somebody's always paying to steal from a "
              "corp.", 'a03'),
        ('V',) + V_LIKE_WHAT,
        ('H', "Data, usually. Sometimes a person.", 'a03b'),
        ('H', "Getting a person out pays more. Taking a suit out pays the "
              "most.", 'a03c'),
    ]),
    # WHY A CORPO TOWER. Charter Hill is the game's own district of
    # mid-level executives' apartment towers (its lore page: "the mid-level
    # executive 'suits' who live in Charter Hill"), and V's Charter Hill
    # street line is the question. No follow-up: she finishes the thought
    # herself, the way Dino answers "Where do I go to party?".
    ('Nice place.', 'a06', [
        ('V', "Nice place, quaintly slick.", 0x187e45951346b000),
        ('H', "The suits upstairs walk past me every day.", 'a06'),
        ('H', "Nobody's ever asked a single question.", 'a06b'),
    ]),
    ('Later.', 'a05', [
        ('V', "Talk later.", 0x1b258f89ed2ef000),
        ('H', "Take care, V.", 'a05'),
    ]),
]

# AN ANSWER THAT DEPENDS ON THE SAVE. The gig upstairs adds 1 to
# `hil_01_finished` at its debrief (`sts_wbr_hil_01_open_world.questphase`,
# the reward phase, node 30; the gig's own top phase waits on the same fact
# being greater than 0 before it cleans up), so on a save where V has done
# it the divorce is over and the line above is stale. The scene forks on
# that fact before her answer, the shape Wakako's own debrief call uses for
# `hil_01_combat` (add_fact_branch_node). Keyed by the button it replaces:
# (fact, comparison, value, the turns after V's question when the
# condition holds). No follow-up here: she keeps talking, the way Wakako
# does over the Sandra Dorsett reward. Nina Gutierrez is dead in the game's
# world (her body is under the Japantown bridge, with a shard of her last
# messages about the receipts), which is why the second line says only that
# Hodan has not seen her since.
AFTER_THE_GIG = {
    'a01': ('hil_01_finished', 'Greater', 0, [
        ('H', "All quiet. Somebody went upstairs and came back down with "
              "the politician's depository receipts.", 'a07'),
        ('H', "He got his receipts back. Japantown got paid. Haven't seen "
              "her since.", 'a07b'),
        ('H', "I kept a copy. Never know when it might come in handy.",
         'a07c'),
    ]),
}


def conversation(s, n, v, start, out, phone, attach_actor=None):
    """The hub, its branches and the loop back, in one scene.

    `phone` is whether her answers go through the call UI. The last option
    is the goodbye: its branch ends the scene instead of returning.
    `attach_actor` pins the hub to her body for the in-person version; the
    phone version leaves it on the screen, which is where the game's own
    fixer hub is forced during a call (`forceAttachToScreenCondition` on
    `dyno_dd_holo`).

    Returns (lead, hub): the silent half-second section the scene opens
    on, which is where a pose and a look-at are fired from so she is posed
    BEFORE the first option is picked (the game's own `enter_idle_in` is a
    one-second section holding a look-at and the workspot), and the hub node,
    so the in-person scene can hang its walk-away wait off the same point.
    """
    lead = s.section([], lead_ms=0, tail_ms=500)
    hub = s.hub()
    options = [s.add_option(caption, key='o%02d' % (i + 1))
               for i, (caption, _key, _turns) in enumerate(TALK)]
    choice = s.choice(options, attach_actor=attach_actor)

    def build_turns(turns, key, last):
        """One section per turn, chained; returns (first, last_section)."""
        secs = []
        for i, turn in enumerate(turns):
            final = last and i == len(turns) - 1
            if turn[0] == 'V':
                _who, text, sid = turn
                secs.append(s.section([s.add_line(v, text,
                                                  key='v_%s_%d' % (key, i),
                                                  vanilla_sid=sid)]))
            else:
                _who, text, lkey = turn
                secs.append(s.section([s.add_line(n, text, key=lkey)],
                                      holocall=phone,
                                      tail_ms=600 if final else 0))
        for x, y in zip(secs, secs[1:]):
            s.link_section(x, y)
        return secs[0], secs[-1]

    branches = []
    for caption, key, turns in TALK:
        last = key == TALK[-1][1]
        # V's question is its own section, so a fork can sit after it.
        vq, _ = build_turns(turns[:1], key, False)
        first, tail = build_turns(turns[1:], key, last)
        alt = None
        if key in AFTER_THE_GIG:
            fact, cmp, value, alt_turns = AFTER_THE_GIG[key]
            alt_first, alt_tail = build_turns(alt_turns, key + '_alt', False)
            alt = (s.add_fact_branch_node(fact, value, cmp), alt_first,
                   alt_tail)
        branches.append((vq, first, tail, last, alt))
    s.link(start, lead)
    s.link_section(lead, hub)
    s.link(hub, choice)
    s.link_choice(choice, [vq for vq, _f, _t, _l, _a in branches])
    for vq, first, tail, last, alt in branches:
        if alt is None:
            s.link_section(vq, first)
        else:
            fork, alt_first, alt_tail = alt
            s.link_section_quest(vq, fork)
            s.link_branch(fork, alt_first, first)
            s.link_section(alt_tail, hub)
        s.link_section(tail, out if last else hub)
    return lead, hub


def face_player(s, actor):
    """Hold her eyes on V for every section. Gig 03's helper: a placed body
    has no reason to look anywhere until a scene tells it to."""
    player = s.player_performer()
    for sec in s.sections():
        s.look_at(sec, actor, player, start_time=0)


def sofa_pose(s, first_section):
    """Play her couch workspot FROM THE SCENE, where she already sits.

    Call it AFTER the section links, the same rule as studio_pose. Gig 03's
    bar lesson (2026-09-15): a body the AI holds in a sitting workspot keeps
    its head and mouth for the workspot, and a scene that speaks through it
    moves nothing; the fix is the scene playing the same resource on the
    community actor at its first beat (`playAtActorLocation`, so she does not
    move). Regina's copy on a stand-around idle never needed it, and neither
    did she in Kabuki; on a sofa she does.
    """
    node = s.add_workspot_node(ACTOR, path=FIXER_WORKSPOT,
                               entry=FIXER_WORKSPOT_ENTRY,
                               community=(gen_community.build().community_ref,
                                          gen_community.ENTRY))
    s.fire_workspot(first_section, node, start_time=0)


def build_face():
    """In person. Walk up to her on the sofa and the prompt is over her.

    HER BODY IS THE COMMUNITY'S, acquired through the community node (gig
    03's bar; gotcha 69 for why not a spawn set), so she is standing there
    before the scene starts and still standing there after it ends. The
    quest phase enters this scene when V is within reach of her and leaves
    it running: the hub is pinned to her, so from further off there is no
    prompt, and the scene ends by itself when V is LEAVE_RADIUS away, the
    way her phone call ends by itself when V walks up to her in the game's
    own version (`dyno_default.scene` node 145). Without that wait a
    conversation V walked out of would stay open until a reload.
    """
    s = Scene('fixer01_face', ANCHOR_PLAYER)
    n = s.add_community_actor(ACTOR, gen_community.ENTRY,
                              gen_community.build().community_ref,
                              appearance=gen_npv.APPEARANCE)
    v = s.add_player()
    start = s.start('face_in')
    out = s.end('face_out')
    lead, hub = conversation(s, n, v, start, out, phone=False, attach_actor=n)
    # THE WALK-AWAY. Fed from the same hub node as the choice (a second
    # destination on the hub's one socket, vanilla's node 159 shape), so it is
    # armed for as long as the prompt is up, and it ends the scene at its own
    # exit. Input ordinal 1: ordinal 0 on a quest node is CutDestination.
    gone = s.add_wait_distance_node(gen_community.build().community_ref,
                                    LEAVE_RADIUS, entry=gen_community.ENTRY,
                                    cmp='Greater')
    left = s.end('face_left')
    s._node(hub)['outputSockets'][0]['destinations'].append(
        {'$type': 'scnInputSocketId',
         'isockStamp': {'$type': 'scnInputSocketStamp', 'name': 0, 'ordinal': 1},
         'nodeId': {'$type': 'scnNodeId', 'id': gone}})
    s.link(gone, left)
    sofa_pose(s, lead)
    face_player(s, n)
    return s


def build_call():
    """On the phone. V rings her from the contact list and she answers.

    Her body is spawned on the studio floor in the borrowed set, exactly as
    her introduction stages her; her answers go through the phone. The hub
    is on the screen, which is what a call shows. "Later." hangs up: the
    branch ends the scene and the quest phase ends the call.
    """
    s = Scene('fixer01_call', ANCHOR_STUDIO)
    n = s.add_actor(ACTOR, FIXER_RECORD, offset=STUDIO_OFFSET, yaw=STUDIO_YAW,
                    force_visible=True, appearance=gen_npv.APPEARANCE)
    v = s.add_player()
    start = s.start('call_in')
    out = s.end('call_out')
    lead, _hub = conversation(s, n, v, start, out, phone=True)
    studio_pose(s, ACTOR, n, lead)
    return s


# JOHNNY AFTER HER INTRODUCTION (the design call, 2026-10-15): beside V and
# facing V, one line from his own recording, the shape of gig 04's two beats
# (tools/gig04/gen_scenes.py, _johnny_beat). q104, recorded once and heard by
# both Vs; "Chick's got taste" was the first pick and is a male V's line only.
J_GET_ALONG = ("Hm. Maybe we CAN just get along.", 0x1859a4551029f000)


def build_johnny():
    """After her introduction call: Johnny's one line about her."""
    s = Scene('fixer01_johnny', ANCHOR_PLAYER)
    j = s.add_johnny(offset=(1.0, 2.1, 0.0),
                     yaw=yaw_to_face_player((1.0, 2.1, 0.0)))
    s.add_player()
    start = s.start('johnny_in')
    # 1.5 s BEFORE HE SPEAKS: he is still appearing until then (gig 04's
    # playtest of 2026-10-14).
    s1 = s.section([s.add_line(j, J_GET_ALONG[0], key='j01',
                               vanilla_sid=J_GET_ALONG[1])],
                   inner=True, tail_ms=600, lead_ms=1500)
    out = s.end('johnny_out')
    s.link(start, s1)
    s.link_section(s1, out)
    s.stage_johnny(s1, s1)
    return s


ALL_BUILDERS = (build_intro, build_face, build_call, build_johnny)


if __name__ == '__main__':
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(RAW_MOD, 'localization'), exist_ok=True)
    built = [build() for build in ALL_BUILDERS]
    for scene in built:
        scene.write()
    write_subtitles(built)
    write_lipmap(built)
