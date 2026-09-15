r"""Generates Acceptable Loss's .scene resources: every spoken beat in the gig.

SEVEN SCENES. ALL_BUILDERS at the bottom is the list, and it is the one place
scenes are enumerated.

  gig03_dino_call          the hire, on the phone                     HOLOCALL
  gig03_object             Johnny, one line against bringing it
  gig03_dino_bar           Dino in person at his bar, and the fee he docks
  gig03_door               Johnny's last line, outside V's own door

  and the loyal ending, since 2026-09-11, when V wipes the shard instead:
  gig03_destroy            Johnny, as the shard goes
  gig03_dino_bar_loud      Dino in person, no fee, and the advance back
  gig03_door_loyal         Johnny's last line on that ending

THE FIXER IS DINO DINOVIC since 2026-09-15 (Regina Jones before; the design
call and the reasons are in gen_journal.py). His pool is 77 recordings and
every one was read for this: his hire lines from the Eva Cole and Joanne Koch
gigs carry the call, and his rebukes from the Empathy, Cole and Mausser gigs
carry the bar. Two of his lines are cut (take_vanilla.py); the rest play
whole.

===========================================================================
EVERY LINE IN THIS GIG IS A RECORDING THE GAME ALREADY MADE
===========================================================================

This gig invents nobody. Dino, V and Johnny are the only speakers, all three
are base-game characters, and under the casting rule in `docs/new-gig.md`
section 6 a character the base game voices speaks only in the game's own
recordings. So every line below carries `vanilla_sid=`: the game supplies the
audio, the subtitle and both V bodies from its own registration, and this mod
ships no audio at all. The text passed alongside is the vanilla line VERBATIM
so this file still reads as a script.

There is no casting call for this gig, no voice work, and no placeholder tones.

THE CONSEQUENCE FOR THE WRITING, and it is the whole reason the gig is shaped
the way it is: none of these three can say anything specific about Militech,
the ledger, the breach or the trace, because no recording of them does. So the
plot lives where the base game puts its own: on the terminal, on the shard, and
in Dino's messages. What the scenes carry is tone.

`tools/vo_corpus.py` is what every pick below was searched with.

===========================================================================
THE ARGUMENT IS A TEXT THREAD, NOT A SCENE
===========================================================================

The comic's ride home is five exchanges of Johnny calling V a hired gun. None
of those lines exists in the game, and nothing Johnny recorded says that mercs
are being killed as targets, which is the point the argument has to make. A
roadside scene built from what the corpus does have ("mercs didn't normally
sell out to corps", "people die, it's the way of things") was played on
2026-09-15 and did not read as the argument, so it is gone. V texts Dino
instead, unprompted, and says it in V's own words (gen_journal.py). Johnny
keeps the beats his recordings can carry: the wipe, and the last word at V's
door on either ending.

NOTHING IS CUT except three lines listed in take_vanilla.py: Johnny's "But"
in the wipe scene, and two of Dino's in the loud bar scene, each a take cut
at a pause so the wanted words come free. Everything else is `vanilla_sid`,
which points at a recording and plays it entire.

Two picks were dropped for exactly that. Johnny's "Was it really worth it?" is
the tail of a take that opens on V selling themselves to a megacorp, which is
the wrong way round here. Regina's "put an end to our little arrangement" was
the tail of one that opens on cyberpsychos. Both were replaced by whole takes
that carry the same beat.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from questkit.scene import (                                        # noqa: F401
    Scene, configure, write_subtitles, write_lipmap,
    ANCHOR_PLAYER, JOHNNY_ACTOR, JOHNNY_GHOST, JOHNNY_SOLID,
    WORKSPOT_JOHNNY, WORKSPOT_ENTRY,
    estimate_ms, line_ms, locstring_ruid, resref, cname, fnv1a64,
    yaw_to_face_player,
)

import gen_community                                              # noqa: E402

# THE COMMUNITY NODE ITSELF, long form. A `community` actor resolves this as
# a real world NodeRef, so it takes the long spelling (gotcha 34). The
# spawn-set name is the SHORT registered string and is matched as a string,
# not resolved: they are two different things pointing at one node.
CAST_COMMUNITY_REF = ('$/mod/' + gen_community.SECTOR + '/#'
                      + gen_community.SECTOR + '_com')
from gig03_config import (                                          # noqa: E402
    REPO, SOURCE, RAW_MOD, DEPOT, ANCHOR_STUDIO, DINO_WORKSPOT,
)

OUT_DIR = os.path.join(RAW_MOD, 'scenes')

SUBTITLE_MAP_OUT = os.path.join(RAW_MOD, 'localization', 'subtitles.json.json')
SUBTITLE_OUT = os.path.join(RAW_MOD, 'localization', 'gig03_lines.json.json')
SUBTITLE_DEPOT = DEPOT + chr(92) + 'localization' + chr(92) + 'gig03_lines.json'

# Where the scenes live once packed. gen_questphase.SCENES is the same string
# and has to stay so: the lipmap is keyed by FNV1a64 of exactly this path plus
# the scene name.
SCENE_DEPOT = DEPOT + chr(92) + 'scenes' + chr(92)
LIPMAP_OUT = os.path.join(RAW_MOD, 'localization', 'gig03.lipmap.json')

# DURATIONS, for the two clips this gig ships (gen_voice.py writes the
# sidecar). Every other line is a reused take, paced by the clip vanilla
# already has, and is not in here.
DURATIONS_FILE = os.path.join(SOURCE, 'audio', 'durations.json')
if os.path.exists(DURATIONS_FILE):
    with open(DURATIONS_FILE, encoding='utf-8') as _fh:
        MEASURED = json.load(_fh)
else:
    MEASURED = {}

# AND THE REUSED LINES, measured off the game's own takes by
# tools/gig03/measure_vanilla.py (the longer of V's two bodies). Without
# these a reused line is paced by an estimate from its text, which ran
# short for V by up to two seconds: the next line started over V's, and in
# the bring-it scene the section ended, and Johnny with it, while V was
# still talking (playtest 2026-09-15, "almost seen him disappear without
# glitch"). Same table, same key shape, same 350 ms pad.
VANILLA_DURATIONS_FILE = os.path.join(SOURCE, 'audio', 'vanilla_durations.json')
if os.path.exists(VANILLA_DURATIONS_FILE):
    with open(VANILLA_DURATIONS_FILE, encoding='utf-8') as _fh:
        MEASURED.update(json.load(_fh))

# THE LIPSYNC PICKS, AND THEY ARE NOT OPTIONAL.
#
# This block used to be three empty dicts, on the reasoning that a reused line
# brings its own mouth. It does not. A line with no pick ships with an empty
# animation name and NOTHING ERRORS: the actor is configured, the set resolves,
# and the face sits still. Playtest 2026-09-10, on the holocall: "there's no
# lipsync".
#
# `tools/gig03/gen_lipsync.py` writes the file. Run it before this, which
# `run_all.py` does. Missing, the gig still builds and every mouth is dead, so
# the warning below is the only thing standing between that and a playtest.
LIPSYNC_PICKS = os.path.join(SOURCE, 'lipsync_picks.json')
try:
    with open(LIPSYNC_PICKS, encoding='utf-8') as _fh:
        _picks = json.load(_fh)
    LIPSYNC_SETS = _picks.get('sets', {})
    LIPSYNC_LINES = _picks.get('lines', {})
except (OSError, ValueError):
    LIPSYNC_SETS, LIPSYNC_LINES = {}, {}
    print('  NO LIPSYNC PICKS: run tools' + chr(92) + 'gig03' + chr(92)
          + 'gen_lipsync.py first, or every mouth in this gig is dead')

SCENE_ALIASES = {}

# DINO'S RECORD, for the displayName over his subtitles. See
# source/tweaks/characters.yaml.
R_DINO = 'Character.cc_g03_dino'

# WHERE DINO STANDS IN THE HOLOCALL STUDIO.
STUDIO_OFFSET = (0.0, 0.0, 0.0)
STUDIO_YAW = 0.0

# HIS POSE AND WHAT HIS EYES AIM AT, both read out of the studio's own quest
# sector (`quest_ec82d0423d8f1435`, read again 2026-09-15) rather than
# guessed: `#dino_holocall_workspot` is the AI spot his body is placed on,
# and `#dino_holocall_lookat` is a marker standing exactly where his camera
# is. The sector carries one such set per fixer, and his four nodes are
# spelled `dino_`, not `dyno_` (his community and character are `dyno`).
#
# BOTH ARE REQUIRED AND EACH FAILS DIFFERENTLY. Without the workspot the body
# plays a default idle, standing off-frame. Without the look-at his eyes wander
# past the lens. The call still connects either way, which is what makes them
# easy to leave out.
DINO_POSE = ('#dino_holocall_workspot', '#dino_holocall_lookat')


def face_player(s, actor):
    """Hold an actor's eyes on V for every section of a scene.

    Call it AFTER the section links, the same rule as studio_pose.

    WITHOUT IT THE BODY STARES PAST V. Playtest 2026-09-10, on Regina's flat:
    "she just stares in the void". A placed body has no reason to look anywhere until a
    scene tells it to, and the scene ending is what ends the look, so nothing
    here has to unwind anything.
    """
    player = s.player_performer()
    for sec in s.sections():
        s.look_at(sec, actor, player, start_time=0)


def bar_pose(s, actor, first_section):
    """Play his barstool workspot FROM THE SCENE, where he already sits.

    Call it AFTER the section links, the same rule as studio_pose.

    WITHOUT IT HIS FACE DOES NOTHING. Playtest 2026-09-15, first pass at the
    bar: "no lipsync and no look_at in person". The community places him on
    the stool through the AI's own use of the spot, and a body the AI holds
    in a sitting workspot kept its head and mouth for the workspot; the scene
    spoke through it and moved nothing. Regina's copy stood on a stand-around
    idle and the scene drove her face, so this is the barstool's doing rather
    than the community's.

    The game's own scene at his bar (`dyno_default.scene`, read 2026-09-15)
    registers the same barstool resource and plays it from the scene: entry
    6, jumpToEntry 1, playAtActorLocation 1, teleport 1, on the community
    actor. This is that node, fired at t=0 of the first section, so the scene
    owns the pose for as long as it runs and can look and speak through it.
    The entry number is the one his scene uses; the stand-around helper's
    default (2) belongs to a different resource.
    """
    node = s.add_workspot_node('dino', path=DINO_WORKSPOT, entry=6,
                               community=(CAST_COMMUNITY_REF, 'dino'))
    s.fire_workspot(first_section, node, start_time=0)


def studio_pose(s, actor_name, actor, first_section):
    """Put the holocall body on the contact's spot and on the lens.

    Called AFTER the section links: output sockets are written in order and the
    scene builder's own validation enforces that.
    """
    workspot, lookat_ref = DINO_POSE
    s.fire_workspot(first_section,
                    s.add_world_workspot_node(actor_name, workspot),
                    start_time=0)
    lookat = s.add_lookat_prop('cc_g03_holocall_lookat', lookat_ref)
    for sec in s.sections():
        s.look_at(sec, actor, lookat, start_time=0)

configure(
    out_dir=OUT_DIR,
    scene_depot=SCENE_DEPOT,
    subtitle_out=SUBTITLE_OUT,
    subtitle_map_out=SUBTITLE_MAP_OUT,
    subtitle_depot=SUBTITLE_DEPOT,
    lipmap_out=LIPMAP_OUT,
    lipmap_name='gig03.lipmap',
    durations=MEASURED,
    lipsync_sets=LIPSYNC_SETS,
    lipsync_lines=LIPSYNC_LINES,
    scene_aliases=SCENE_ALIASES,
)


# ============================================================ 1: the hire
def build_dino_call():
    """Dino hires V. His own lines, and V's three replies are V's own.

    EVERY LINE OF HIS ARRIVES THROUGH THE PHONE, and unlike Regina's none of
    it needed a knife: the three lines that describe the job are the Eva
    Cole gig's own hire, and the game recorded a phone version of each (the
    `vo_holocall` twin `Vo_Expression_Phone` plays; gotcha 41). "Scrolls"
    is Night City for recordings and files, and it is the word he uses for
    the Cole footage, so it is the word for a Militech ledger too.

    ALL THREE FROM ONE VANILLA SCENE, on purpose: an actor gets one lipsync
    set per scene, so three lines from one recording session get their own
    mouths exactly, where a third line borrowed from another gig's hire
    ("Anyway, know you like a challenge. Detes attached.") was cast by length
    and 800 ms out. V's replies are the banter that line order asks for.
    """
    # STAGED AT THE STUDIO, NOT AT THE PLAYER, and that is what makes it a
    # holocall rather than a disembodied voice. The first build staged it at
    # the player: the lines played and there was no call on screen at all,
    # because nothing had asked for the studio sector or put a body in it.
    s = Scene('gig03_dino_call', ANCHOR_STUDIO)
    d = s.add_actor('dino', R_DINO, offset=STUDIO_OFFSET, yaw=STUDIO_YAW,
                    force_visible=True)
    v = s.add_player()

    start = s.start('dino_call_in')

    # THE DEFAULT LEAD, the same as gig 02's calls. A 2 s lead stood here for
    # one build (see gen_questphase.dino_call for why it went).
    s1 = s.section([
        s.add_line(d, "Yo, V! I need you to swipe some scrolls, should be "
                      "pretty spicy.", key='d01',
                   vanilla_sid=0x20525dafc170a000),
    ], holocall=True)
    s2 = s.section([
        s.add_line(v, "I'm listening.", key='v01',
                   vanilla_sid=0x1909989a1d4e6000),
    ])
    # ONE LINE PER SECTION, which matches every vanilla gig briefing.
    s3 = s.section([
        s.add_line(d, "Client's feelin' generous, too. Whaddaya say?",
                   key='d02', vanilla_sid=0x206500b2c53bc000),
    ], holocall=True)
    s4 = s.section([
        s.add_line(v, "Sure hope so. Question is, how much?", key='v02',
                   vanilla_sid=0x1b00f48ec744d000),
    ])
    s5 = s.section([
        s.add_line(d, "Intel attached. Don't make me beg.", key='d03',
                   vanilla_sid=0x206500d6763bc000),
    ], holocall=True)
    s6 = s.section([
        s.add_line(v, "All right. I'm in.", key='v03',
                   vanilla_sid=0x1ade2d5d602e3000),
    ])
    out = s.end('dino_call_out')

    s.link(start, s1)
    s.link_section(s1, s2)
    s.link_section(s2, s3)
    s.link_section(s3, s4)
    s.link_section(s4, s5)
    s.link_section(s5, s6)
    s.link_section(s6, out)
    studio_pose(s, 'dino', d, s1)
    return s


# ================================================== 3: Dino, at his bar
def build_dino_bar():
    """Face to face. He is furious, he pays half, and he warns V off.

    WHY THE REASON IS NOT SPOKEN. Militech logging the breach, and the trail
    leading back to him, are this gig's own facts and no recording of his
    contains a word of either. V's text after the site says both, in writing,
    before the player is standing here. What this scene carries is the anger,
    and his own rebukes carry it better than Regina's did: "I didn't say
    'Don't make a complete fuckin' mess', but I didn't think I had to" is the
    Empathy gig's debrief for a loud job, and "I'll count the job as done,
    but technically, just barely" is the Cole gig's for half a job. Every
    line is a whole take.
    """
    s = Scene('gig03_dino_bar', ANCHOR_PLAYER)
    # OUR BODY, SITTING IN THE WORLD BEFORE THE SCENE STARTS.
    #
    # Regina's version went through three wrong answers before this one,
    # and gen_community.py has them: a scene-spawned actor is created when
    # the scene starts and deleted when it exits, so the player watched her
    # appear and vanish. He is a COMMUNITY entry, the way gig 02's Wakako is,
    # and this scene ACQUIRES the man already sitting there. He is on his
    # stool from the moment the player comes within the swap radius until the
    # moment they walk away again, and the scene starting and ending does
    # nothing to him. gen_community.py and gen_questphase.py are the other
    # two thirds.
    d = s.add_community_actor('dino', 'dino', CAST_COMMUNITY_REF)
    v = s.add_player()

    start = s.start('dino_bar_in')

    s1 = s.section([
        s.add_line(d, "Shit, V...", key='d01', vanilla_sid=0x205086b1ab647000),
    ])
    s2 = s.section([
        s.add_line(v, "Here.", key='v01', vanilla_sid=0x1a96bf839e386000),
    ])
    s3 = s.section([
        s.add_line(d, "Y'know, true, I didn't say \"Don't make a complete "
                      "fuckin' mess\" - but I didn't think I had to.",
                   key='d02', vanilla_sid=0x205191532a69e000),
    ])
    s4 = s.section([
        s.add_line(v, "Yeah.", key='v02', vanilla_sid=0x185efbe0fb50203c),
    ])
    # THE MONEY, AND THEN THE PENALTY. All whole takes. The 12,500 lands as
    # the scene ends (the graph sets `cc_g03_pay_due` on its exit), so his
    # "eddies are on their way" is said before they arrive.
    s5 = s.section([
        s.add_line(d, "OK, I'll count the job as done. But technically, just "
                      "barely, and I ain't happy neither.", key='d03',
                   vanilla_sid=0x205252c65b70a000),
    ])
    s6 = s.section([
        s.add_line(d, "Gig's closed. The eddies are on their way.", key='d04',
                   vanilla_sid=0x2061537cc43bc000),
    ])
    s7 = s.section([
        s.add_line(d, "Better be the last time you pull shit like this, V. "
                      "The city don't tolerate mediocrity.", key='d05',
                   vanilla_sid=0x20615662e63bc000),
    ], tail_ms=900)
    out = s.end('dino_bar_out')

    s.link(start, s1)
    s.link_section(s1, s2)
    s.link_section(s2, s3)
    s.link_section(s3, s4)
    s.link_section(s4, s5)
    s.link_section(s5, s6)
    s.link_section(s6, s7)
    s.link_section(s7, out)
    bar_pose(s, d, s1)
    face_player(s, d)
    return s


# ============================================ 5: the shard, wiped (loyal)
def build_destroy():
    """V has just told Dino no, by text. Johnny gets the moment, the shard
    leaves the backpack three seconds in (Gig03_Places.reds, on `cc_g03_loyal`)
    with a banner over his second line, and V gets the last word.

    "Finally, something we agree on" is the whole of his reaction to the
    decision, and "give up your ideals, and no amount of eddies can buy 'em
    back" is the gig's answer to its own question, said by the one person in
    it who would. V's "happy now?" is V not conceding an inch even while doing
    the right thing, which is the V of the ride scene.
    """
    s = Scene('gig03_destroy', ANCHOR_PLAYER)
    j = s.add_johnny(offset=(1.0, 2.1, 0.0),
                     yaw=yaw_to_face_player((1.0, 2.1, 0.0)))
    v = s.add_player()

    start = s.start('destroy_in')
    s1 = s.section([
        s.add_line(j, "Finally, something we agree on.", key='j01',
                   vanilla_sid=0x1a9546648644d000),
    ], inner=True)
    # CUT: the take opens on "But", which answers nothing here. It is a
    # shipped clip from 0.50 s on (take_vanilla.JOINS), dry, cast by length.
    s2 = s.section([
        s.add_line(j, "Give up your ideals, and no amount of eddies can buy "
                      "'em back.", key='j02'),
    ], inner=True)
    # "Hehh... happy now?" stood here and playtest heard it as distraught
    # ("like she's almost dying", 2026-09-15); this is the dry one of the six
    # offered.
    s3 = s.section([
        s.add_line(v, "There you go.", key='v01',
                   vanilla_sid=0x18c709af682fc000),
    ], tail_ms=900)
    out = s.end('destroy_out')

    s.link(start, s1)
    s.link_section(s1, s2)
    s.link_section(s2, s3)
    s.link_section(s3, out)
    s.stage_johnny(s1, s3)
    return s


# ================================================= 5b: Johnny objects (A)
def build_object():
    """V has just told Dino "On my way." Johnny gets two lines against it and
    V shuts him down twice. The design call, 2026-09-15: "as soon as I write
    to Dino": Don't do it / Not now / give up your ideals / shut up, a job's
    a job. V's last two lines are the game's own "I said shut up!" and the
    line V says to a fixer's mark in Glen: "What's there to talk about? Job's
    a job, nothin' personal."

    j02 IS THE SAME CUT the wipe scene uses (take_vanilla.JOINS), shipped
    again under this scene's own line id, because a shipped clip is keyed by
    scene and line.
    """
    s = Scene('gig03_object', ANCHOR_PLAYER)
    j = s.add_johnny(offset=(1.0, 2.1, 0.0),
                     yaw=yaw_to_face_player((1.0, 2.1, 0.0)))
    v = s.add_player()

    start = s.start('object_in')
    s1 = s.section([
        s.add_line(j, "Don't do it, V.", key='j01',
                   vanilla_sid=0x196c622ac1386000),
    ], inner=True)
    s2 = s.section([
        s.add_line(v, "Not now, Johnny.", key='v01',
                   vanilla_sid=0x19b2d7698744d000),
    ])
    # CUT: the take opens on "But". A shipped clip from 0.50 s on, dry,
    # cast by length.
    s3 = s.section([
        s.add_line(j, "Give up your ideals, and no amount of eddies can buy "
                      "'em back.", key='j02'),
    ], inner=True)
    s4 = s.section([
        s.add_line(v, "I said shut up!", key='v02',
                   vanilla_sid=0x2ebdce18b7757000),
        s.add_line(v, "What's there to talk about? Job's a job - nothin' "
                      "personal.", key='v03',
                   vanilla_sid=0x1134fe4a54464000),
    ], tail_ms=900)
    out = s.end('object_out')

    s.link(start, s1)
    s.link_section(s1, s2)
    s.link_section(s2, s3)
    s.link_section(s3, s4)
    s.link_section(s4, out)
    s.stage_johnny(s1, s4)
    return s


# ========================================== 6: Dino, at his bar (loyal)
def build_dino_bar_loud():
    """Face to face, with nothing to hand over. No fee, and the client's
    advance comes out of V's wallet as he finishes: the graph sets
    `cc_g03_docked` on this scene's exit and Gig03_Places.reds takes it.

    TWO CUTS (take_vanilla.JOINS): "You fucked up, V." is the head of his
    Joanne Koch failure debrief, and "Sorry, no cred for that move." is the
    tail of his Mausser one. Both ship dry, cast by length. "Your boy Dino
    needs a drink" is the whole of his Mausser closer, and here it is him
    done with V. The same community body as the calm version, so nothing
    about the bar changes between the two endings but what he says.
    """
    s = Scene('gig03_dino_bar_loud', ANCHOR_PLAYER)
    d = s.add_community_actor('dino', 'dino', CAST_COMMUNITY_REF)
    v = s.add_player()

    start = s.start('dino_loud_in')

    s1 = s.section([
        s.add_line(d, "Shit, V...", key='d01', vanilla_sid=0x205086b1ab647000),
    ])
    s2 = s.section([
        s.add_line(v, "Welp, what's done is done.", key='v01',
                   vanilla_sid=0x1b01e8adb644d000),
    ])
    s3 = s.section([
        s.add_line(d, "You fucked up, V.", key='d02'),
        s.add_line(d, "Sorry, no cred for that move.", key='d03'),
    ])
    s4 = s.section([
        s.add_line(v, "Yeah.", key='v02', vanilla_sid=0x185efbe0fb50203c),
    ])
    s5 = s.section([
        s.add_line(d, "Gig's sealed - and your boy Dino needs a drink. "
                      "Later, V.", key='d04',
                   vanilla_sid=0x20613f444f3bc000),
    ], tail_ms=900)
    out = s.end('dino_loud_out')

    s.link(start, s1)
    s.link_section(s1, s2)
    s.link_section(s2, s3)
    s.link_section(s3, s4)
    s.link_section(s4, s5)
    s.link_section(s5, out)
    bar_pose(s, d, s1)
    face_player(s, d)
    return s


# ================================================ 7: the last line (loyal)
def build_door_loyal():
    """Johnny, outside V's own door, on the ending where V wiped the log,
    got nothing and paid for it. His whole comment is that V is allowed to be
    a little proud, which is the only warm line in the gig and it is earned.
    """
    s = Scene('gig03_door_loyal', ANCHOR_PLAYER)
    j = s.add_johnny(offset=(1.2, 1.8, 0.0),
                     yaw=yaw_to_face_player((1.2, 1.8, 0.0)))
    v = s.add_player()

    start = s.start('door_loyal_in')
    s1 = s.section([
        s.add_line(j, "'S OK, V. You're allowed to be a little proud of "
                      "yourself.", key='j01',
                   vanilla_sid=0x2d55fa9ff63bc000),
    ], inner=True, tail_ms=1200)
    out = s.end('door_loyal_out')

    s.link(start, s1)
    s.link_section(s1, out)
    s.stage_johnny(s1, s1)
    return s


# ======================================================== 4: the last line
def build_door():
    """Johnny, outside V's own door, and the gig ends on him.

    V has just handed a corp the log of how it kills mercs, and been paid for
    it. The design call, 2026-09-15: the line has to be Johnny turning on V
    for that, and "Hope it was expensive at least" did not read as that. This
    is his own dig, whole: the disclaimer that he is not V's conscience, and
    then the verdict. The comic's "Was it really worth it?" is the tail of a
    take that opens on V selling out to a megacorp, and `vanilla_sid` plays a
    take whole.
    """
    s = Scene('gig03_door', ANCHOR_PLAYER)
    j = s.add_johnny(offset=(1.2, 1.8, 0.0),
                     yaw=yaw_to_face_player((1.2, 1.8, 0.0)))
    v = s.add_player()

    start = s.start('door_in')
    s1 = s.section([
        s.add_line(j, "Hate to sound like your conscience, wouldn't ever want "
                      "that job... but dick move, V.", key='j01',
                   vanilla_sid=0x1a05bb60e044d000),
    ], inner=True, tail_ms=1200)
    out = s.end('door_out')

    s.link(start, s1)
    s.link_section(s1, out)
    s.stage_johnny(s1, s1)
    return s


ALL_BUILDERS = (
    build_dino_call,
    build_dino_bar,
    build_door,
    build_object,
    build_destroy,
    build_dino_bar_loud,
    build_door_loyal,
)


def check_every_mouth_is_cast(built):
    """Fail the run if a speaker with a face has no lipsync animation.

    A line with no pick ships with an EMPTY ANIMATION NAME and nothing errors:
    the actor is configured, the set resolves, and the face sits still. It is
    invisible until somebody watches a close-up, which for this gig was a
    holocall in playtest.

    So it is a build failure rather than a warning. `write_lipmap` prints a
    warning too and that warning was ignored four builds running.

    The player is skipped: V is the camera and has no mouth to move.
    """
    missing = []
    for scene in built:
        cast = LIPSYNC_SETS.get(scene.name, {})
        for key in scene.reused_actor:
            idx = scene.reused_actor[key]
            actor = scene.actors[idx] if idx < len(scene.actors) else None
            if not actor or actor.get('$type') == 'scnPlayerActorDef':
                continue
            # THE `actorName` FIELD, which every actor has whatever its
            # acquisition plan is. Reading the spawn params instead works only
            # for an actor the SCENE spawns: a community actor's
            # `dynamicEntityUniqueName` is the literal string "None", so the
            # moment Regina became a community entry this check compared "None"
            # against the cast and failed the build on all six of her lines
            # (Dino is a community entry from the start).
            name = actor.get('actorName')
            if name and name not in cast:
                missing.append('%s/%s (actor %s)' % (scene.name, key, name))
    if missing:
        raise SystemExit(
            'NO LIPSYNC for %d line(s) with a face on screen:\n  %s\n'
            'Run tools%sgig03%sgen_lipsync.py first. run_all.py does this in '
            'order; a bare gen_scenes.py run does not.'
            % (len(missing), ('\n  ').join(sorted(set(missing))),
               chr(92), chr(92)))


if __name__ == '__main__':
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(RAW_MOD, 'localization'), exist_ok=True)
    built = [build() for build in ALL_BUILDERS]
    check_every_mouth_is_cast(built)
    # A reused line with no measured length is paced by the estimate, which
    # is the bug measure_vanilla.py exists to close: say so, loudly.
    for scene in built:
        for key, _sid, text in scene.reused:
            if ('%s/%s' % (scene.name, key)) not in MEASURED:
                print('  ! %s/%s has no measured length (run tools' % (scene.name, key)
                      + chr(92) + 'gig03' + chr(92) + 'measure_vanilla.py); paced '
                      'by estimate')
    for scene in built:
        scene.write()
    write_subtitles(built)
    write_lipmap(built)
    print('scenes: %d' % len(built))
    for scene in built:
        print('   %s' % scene.name)
