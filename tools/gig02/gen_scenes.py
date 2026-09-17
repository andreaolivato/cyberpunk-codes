r"""Generates Dead Ringer's .scene resources: every conversation in the gig.

SIXTEEN SCENES. ALL_BUILDERS at the bottom is the list, and gen_voice and
gen_lipsync both read it, so it is the one place scenes are enumerated.

  gig02_wakako_call  the hire, five of her own lines           VIDEO HOLOCALL
  gig02_johnny_open  after the phone is down
  gig02_talk_a       the first group overheard outside Afterlife
  gig02_talk_b       the second one
  gig02_group3       the last group, and the merc is the one talking
  gig02_beaten       on the floor: the begging, and the shard is his to take
  gig02_fate         the choice, once the shard has been read
  gig02_planned      Johnny, after V has messaged Wakako the proof
  gig02_inn          Yoko on the door, in her own recorded lines
  gig02_handover     Char takes the shard
  gig02_char_call    Char tells V what to scan for                VIDEO HOLOCALL
  gig02_office       Wakako in person, and the kill order
  gig02_close_clean  nobody saw. Wakako pays                     VIDEO HOLOCALL
  gig02_close_loud   everybody saw. Wakako pays anyway           VIDEO HOLOCALL
  gig02_end          the last exchange, unseen
  gig02_end_loud     the last exchange, seen

===========================================================================
WHERE THE WORDS COME FROM, and this is the rule the whole file is written to
===========================================================================

REBUILT 2026-09-03 under the casting rule in docs/new-gig.md section 6: a
character the base game voices speaks only in the game's own recordings, and a
character this mod invents is recorded by a person.

  Wakako, Yoko, V, Johnny   `vanilla_sid=` on every line. The game supplies
                            audio, subtitle and both V bodies from its own
                            registration; nothing is shipped for them. The
                            text passed alongside is the vanilla line VERBATIM
                            so this file still reads as a script. SEVEN
                            exceptions are one take cut short at a pause
                            (tools/gig02/splice_takes.py), which ship as our
                            own audio under the keys v60 and w40 to w46.
  the merc, Char            invented and voiced, so their lines are written
                            freely here. Toji is invented too and says nothing.
                            and recorded by voice actors. Until a recording
                            lands, gen_voice ships a placeholder tone.
  the five strangers        the club's own ambient chatter, generic voices,
                            whole takes (see build_talk_a).

THE CONSEQUENCE FOR THE WRITING: V never explains the plot, because no
recording of him does. He asks, presses, and reacts. The merc and Char say
every specific thing, and the text the player reads (the brief, the
messages, the shards) says the rest, which is where the base game puts its
exposition too. `tools/vo_corpus.py` is what the picks were searched with.

A SCENE AT A PERSON OR AN OBJECT OPENS ON A CHOICE HUB, so nothing plays until
the player presses [F]. Proximity decides that a beat is AVAILABLE; it no
longer decides that it has happened.

Line flags, unchanged from before the rebuild:

  holocall=True   2D, through the phone. Wakako on a call.
  inner=True      Johnny's relic register.
  inner_vo=True   2D without the styling, for a speaker with no body of ours.
                  Nobody since 2026-09-05: Wakako in her office is our body.
  default         positional: the merc, Char, Yoko, Toji, all of whom stand
                  in front of V as scene actors acquired from the world.
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

from gen_community import SPAWNSET_NAME, APPEARANCE                 # noqa: E402
import gen_community                                                # noqa: E402

# THE COMMUNITY NODE ITSELF, long form. A `community` actor resolves this as a
# real world NodeRef, so it takes the long spelling (gotcha 34). The spawn-set
# name imported above is the SHORT registered string and is matched as a
# string, not resolved: they are two different things pointing at one node.
CAST_COMMUNITY_REF = ('$/mod/' + gen_community.SECTOR + '/#'
                      + gen_community.SECTOR + '_com')

from gig02_config import (                                          # noqa: E402
    REPO, SOURCE, RAW_MOD, DEPOT,
    ANCHOR_AFTERLIFE, ANCHOR_INN, ANCHOR_PARLOR, ANCHOR_OFFICE, ANCHOR_HIT,
    ANCHOR_STUDIO,
)

OUT_DIR = os.path.join(RAW_MOD, 'scenes')

SUBTITLE_MAP_OUT = os.path.join(RAW_MOD, 'localization', 'subtitles.json.json')
SUBTITLE_OUT = os.path.join(RAW_MOD, 'localization', 'gig02_lines.json.json')
SUBTITLE_DEPOT = DEPOT + chr(92) + 'localization' + chr(92) + 'gig02_lines.json'

# Where the scenes live once packed. gen_questphase.SCENES is the same string
# and has to stay so: the lipmap is keyed by FNV1a64 of exactly this path plus
# the scene name.
SCENE_DEPOT = DEPOT + chr(92) + 'scenes' + chr(92)
LIPMAP_OUT = os.path.join(RAW_MOD, 'localization', 'gig02.lipmap.json')

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

# ------------------------------------------------------------- the records
#
# A voice-only speaker needs a Character record for the displayName over its
# subtitles. See source/tweaks/characters.yaml.
R_WAKAKO = 'Character.cc_g02_wakako'
R_CHAR = 'Character.cc_g02_char'

configure(
    out_dir=OUT_DIR,
    scene_depot=SCENE_DEPOT,
    subtitle_out=SUBTITLE_OUT,
    subtitle_map_out=SUBTITLE_MAP_OUT,
    subtitle_depot=SUBTITLE_DEPOT,
    lipmap_out=LIPMAP_OUT,
    lipmap_name='gig02.lipmap',
    durations=MEASURED,
    lipsync_sets=LIPSYNC_SETS,
    lipsync_lines=LIPSYNC_LINES,
    scene_aliases=SCENE_ALIASES,
)


# WHERE WAKAKO STANDS IN THE HOLOCALL STUDIO. Gig 01's measured pairing with
# `#mama_welles_holocall_camera`, which gen_questphase selects. See the
# 2026-08-26 notes in git history for how to tune it.
STUDIO_OFFSET = (0.0, 0.0, 0.0)
STUDIO_YAW = 0.0


def wakako_studio(s):
    """Wakako as the body on V's phone, forced visible because the studio is
    kilometres from the player."""
    return s.add_actor('wakako', R_WAKAKO, offset=STUDIO_OFFSET,
                       yaw=STUDIO_YAW, force_visible=True)


# THE POSE ON THE PHONE, AND WHY IT COMES FROM A WORLD NODE.
#
# Playtest 2026-09-07: "neither Wakako nor Char looks at V during the
# holocalls, they are just using the standard NPC idle animations". They were,
# and nothing in the scene was telling them otherwise.
#
# READ OFF DISK 2026-09-07, and it settles where a holocall body's pose
# actually comes from. The studio's quest sector (base,
# quest_ec82d0423d8f1435.streamingsector) carries 90 `worldAISpotNode`s, one
# per contact, and node 434 is `{mama_welles_holocall_workspot}`: an AI spot
# playing `generic__stand_bar_lean_front__stand_around__05.workspot`, standing
# where that contact's camera is framed. Vanilla's own holocall scene does
# NOTHING to arrange this. `ma_std_arr_03_holocall_brief.scene` contains three
# dialogue lines, six fact writes and not one camera, look-at or workspot
# event: the whole staging is the spot node, and the body is spawned into it
# by the setup prefab.
#
# This mod spawns its own body instead, because the character has to be ours,
# and it was landing at the marker with no spot and no workspot. So it played
# whatever its record idles as, which is what was seen on the phone.
#
# Pointing the actor at the SAME node vanilla uses takes the position, the
# facing and the pose together, which is why it is a world node rather than a
# workspot resource played in place: the camera we select is
# `#mama_welles_holocall_camera`, and this is the spot that camera is aimed at.
#
# ENTRY 2 is the resource's idle. Its `workspotTree` root is `workSequence`
# id 1 and id 2 is the sequence holding the random loop of anim clips, read
# off the serialized workspot. Both resources named below number it that way.
#
# WAKAKO'S OWN SPOT, 2026-09-07, and the first attempt used Mama Welles's.
# That put the body in a pose but still side-on to the lens and barely lit,
# because it was Mama Welles's pose under Mama Welles's lights in front of a
# camera aimed at her floor spot. A playtest screenshot of the REAL Wakako
# holocall settled what hers looks like: seated behind a desk, leaning
# forward, looking into the lens.
#
# Her three nodes agree with each other and now we agree with them:
#
#   {wakako_holocall_workspot}  (5895.207, 6136.237, 0.000) yaw -65,
#                               generic__sit_chair_table_lean_front__
#                               sit_around__01.workspot
#   {wakako_holocall_camera}    (5896.108, 6136.414, 0.929), aimed at it
#   {wakako_holocall_lookat}    the same point as the camera
#
# The camera height is the giveaway: 0.929 frames a SEATED body, where Mama
# Welles's 1.52 frames a standing one. gen_questphase selects her lights, her
# setup and her camera; this teleports the actor onto her spot. The pose is
# hers, so the frame is hers.
#
# IF IT IS WRONG IN PLAY, the node not resolving means the actor stays at the
# marker, which is a metre off her camera's aim. That is a worse fallback than
# the old pairing had, and it is the price of matching the vanilla frame.

# AND THE EYES, 2026-09-07. The workspot alone was not enough: it put her in
# the chair, in the pose, correctly lit and correctly framed, and she looked
# off past the lens the whole way through (playtest screenshot). A workspot
# fixes the body; the head and the eyes go on playing the idle's own drift.
#
# `wakako_holocall.scene` is where vanilla does it, and none of the shape is
# guessable. The target is declared as a PROP: that scene has one actor and
# one `scnPropDef`, `#wakako_holocall_lookat`, a marker entity standing
# exactly where the camera is, acquired with `findInNode`.
#
# THE FIRST ATTEMPT DECLARED ONLY A DEBUG-SYMBOL ROW for it and changed
# nothing in play. `performersDebugSymbols` is what its name says. The prop is
# the declaration, and the performer id it answers to is encoded rather than
# sequential: `index * 256 + kind`, kind 2 for a prop. See
# `questkit.scene.add_lookat_prop`.
#
# BOTH of that scene's sections carry the same event, `isStart` 1 at t=0, so
# it is fired per section rather than once for the scene. Copied.
#
# ONE PAIR PER SPEAKER, and it has to match the set gen_questphase opens for
# that call: the camera is aimed at the spot, so a body on somebody else's
# spot is out of frame. Char is Blue Moon's (see gen_questphase for why).
#
# ENTRY 2 IS THE IDLE IN BOTH RESOURCES, checked rather than assumed:
# `generic__sit_chair_table_lean_front__sit_around__01` and
# `rogue__sit_bench_lean_back__sit_around__01` both put the root sequence at
# id 1 and the random idle loop at id 2.

# (workspot node, look-at node)
WAKAKO_POSE = ('#wakako_holocall_workspot', '#wakako_holocall_lookat')
CHAR_POSE = ('#blue_moon_holocall_workspot', '#blue_moon_holocall_lookat')


# EYES ON V, for a character standing in front of him rather than on his
# phone. Same event as the holocall and the same per-section firing; only the
# target changes, from a marker in the studio to the player.
#
# VANILLA'S OWN WAKAKO CONVERSATION IS THE MODEL. `wakako_okada_default.scene`
# carries twelve of these and ten point at the player, one per section at t=0
# with `removePreviousAdvancedLookAts` set. The other two are an acting beat
# in the middle of a long section: she looks at NOBODY (performer 4294967040)
# or at herself for about a second, then back to V.
#
# THERE IS NO RELEASE AT THE END, checked rather than assumed: no section in
# that scene clears the look-at on its way out. The scene ending is what ends
# it, so nothing here has to unwind anything.
def face_player(s, actor):
    """Hold an actor's eyes on V for every section of the scene.

    Call it AFTER the section links, the same rule as studio_pose.
    """
    player = s.player_performer()
    for sec in s.sections():
        s.look_at(sec, actor, player, start_time=0)


def studio_pose(s, actor_name, actor, first_section, pose=None):
    """Put a holocall body in that contact's studio spot and on the lens.

    Call it AFTER the section links: output sockets are written in order and
    the scene builder's own validation enforces that.
    """
    workspot, lookat_ref = pose or WAKAKO_POSE
    s.fire_workspot(first_section,
                    s.add_world_workspot_node(actor_name, workspot),
                    start_time=0)
    lookat = s.add_lookat_prop('cc_g02_holocall_lookat', lookat_ref)
    for sec in s.sections():
        s.look_at(sec, actor, lookat, start_time=0)


# ==================================================== 1: the hire
def build_wakako_call():
    """V rings her back and she hires him in five of her own gig lines.

    "Only me, no client" is this gig in her own words: the client is her
    reputation. The premise itself is in the brief she attaches, which
    arrives as her next message and sits in the journal, which is where her
    real gigs put it too. THIS USED TO BE A NINE-LINE CALL and none of those
    nine existed in her voice.
    """
    s = Scene('gig02_wakako_call', ANCHOR_STUDIO)
    w = wakako_studio(s)
    v = s.add_player()

    start = s.start('wakako_call_in')
    s1 = s.section([s.add_line(v, "Wakako. Long time, no see.", key='v01',
                               vanilla_sid=0x1c276e3fd32d2000)])
    # BOTH CUTS. Her gig line opens "V, I need you to acquire something." and
    # this gig retrieves nothing, so the head is dropped; the opener is the
    # first sentence of a line that goes on about planting bugs. See
    # splice_takes.py. THIS IS THE ONE PLACE THE PLOT IS NOT STATED OUT LOUD:
    # she attaches it, and the brief lands as her next message.
    s2 = s.section([
        s.add_line(w, "I need someone for a quick and quiet operation.",
                   key='w45'),
        s.add_line(w, "Only me, no client – so I expect quick and clean "
                      "results.", key='w44'),
    ], holocall=True)
    c1 = s.choice([s.add_option("Listen.", key='o01')])
    # THE COMIC'S OWN LINE, and it exists in his voice.
    s3 = s.section([s.add_line(v, "I'm listening.", key='v02',
                               vanilla_sid=0x1909989a1d4e6000)])
    s4 = s.section([
        s.add_line(w, "It's a... sticky situation.", key='w02',
                   vanilla_sid=0x1ae33bb94e5f9024),
        s.add_line(w, "You're the only one I trust with it.", key='w46'),
        s.add_line(w, "I am attaching more information. Read it. Carefully.",
                   key='w03', vanilla_sid=0x2083d16f55559000),
    ], holocall=True)
    s5 = s.section([s.add_line(v, "Got it.", key='v03',
                               vanilla_sid=0x1ab375df4c44d000)], tail_ms=500)
    out = s.end('wakako_call_out')

    s.link(start, s1)
    s.link_section(s1, s2)
    s.link_section(s2, c1)
    s.link_choice(c1, [s3])
    s.link_section(s3, s4)
    s.link_section(s4, s5)
    s.link_section(s5, out)
    studio_pose(s, 'wakako', w, s1)
    return s


# ================================================ 2: Johnny, after the call
# JOHNNY STANDS 2.3 M OFF, A LITTLE LEFT OF WHERE HE WAS (design calls
# 2026-09-05: at 1.4 m he was too near, then at 1.4 m to the right of V's line
# of sight he was too far to the right; 1.0 m right now. Gig 01's one Johnny
# spot is 1.65 m from V and reads farther in play). The same offset in all
# three of his scenes, facing V.
def build_johnny_open():
    s = Scene('gig02_johnny_open', ANCHOR_PLAYER)
    j = s.add_johnny(offset=(1.0, 2.1, 0.0), yaw=yaw_to_face_player((1.0, 2.1, 0.0)))
    v = s.add_player()

    start = s.start('johnny_open_in')
    s1 = s.section([s.add_line(v, "Shit.", key='v04',
                               vanilla_sid=0x170fd6a6f229f000)])
    s2 = s.section([
        s.add_line(j, "You catch a whiff of that? Smells like shit. Careful "
                      "not to step in it.", key='j01',
                   vanilla_sid=0x1761fc23104e1000),
    ], inner=True, tail_ms=800)
    out = s.end('johnny_open_out')

    s.link(start, s1)
    s.link_section(s1, s2)
    s.link_section(s2, out)
    s.stage_johnny(s1, s2)
    return s


# ==================================== 3: the three groups outside Afterlife
#
# THE TWO CROWDS ARE THE CLUB'S OWN CHATTER, 2026-09-03. The game records a
# set of ambient conversations for the queue outside Afterlife in generic
# civilian voices, and generic voices are allowed under the casting rule. Both
# exchanges below are real ones from that session, whole takes, so four
# voice-actor parts came off the casting call. The five strangers are placed
# bodies now (gen_community), because a mouth the player looks at needs a face
# to move.


def build_talk_a():
    """A merc who crossed a fixer, and the friend explaining what that costs."""
    s = Scene('gig02_talk_a', ANCHOR_AFTERLIFE)
    a = s.add_community_actor('queue_a', 'queue_a', CAST_COMMUNITY_REF)
    b = s.add_community_actor('queue_b', 'queue_b', CAST_COMMUNITY_REF)

    start = s.start('talk_a_in')
    s1 = s.section([
        s.add_line(a, "Seriously thought you'd dick over the fixer? That was "
                      "your best idea for some quick scratch?", key='q01',
                   vanilla_sid=0x1f5fc0bc394e2000),
        s.add_line(b, "Naw, naw, cheddar's fine. Just lookin' for an "
                      "explanation. I mean, that's a big gig you had me botch, "
                      "feel me?", key='q02', vanilla_sid=0x1e87002d514e2000),
    ])
    s2 = s.section([
        s.add_line(a, "Good thing you only tested Regina. She's gentle. Any "
                      "other fixer…? You'da had multiple fractures in both "
                      "legs.", key='q03', vanilla_sid=0x1f6387127542c000),
    ], tail_ms=600)
    out = s.end('talk_a_out')

    s.link(start, s1)
    s.link_section(s1, s2)
    s.link_section(s2, out)
    return s


def build_talk_b():
    """Somebody who wants Wakako on the line, and a man who knows what it is
    like when she stops taking your calls."""
    s = Scene('gig02_talk_b', ANCHOR_AFTERLIFE)
    c = s.add_community_actor('queue_c', 'queue_c', CAST_COMMUNITY_REF)
    d = s.add_community_actor('queue_d', 'queue_d', CAST_COMMUNITY_REF)
    e = s.add_community_actor('queue_e', 'queue_e', CAST_COMMUNITY_REF)

    # ONE ARGUMENT, THREE VOICES (design review 2026-09-05: the pariah line
    # that closed this read as disconnected). The complaint first, the demand
    # to take it up with Wakako, and the friend who finds that funny; all
    # three are the club door's own chatter.
    start = s.start('talk_b_in')
    s1 = s.section([
        s.add_line(e, "Gave us incomplete info again, the bitch.", key='q06',
                   vanilla_sid=0x1e81f174e64e2000),
        s.add_line(c, "No fuckin' way. I wanna talk to Wakako.", key='q04',
                   vanilla_sid=0x1f639275d442c000),
    ])
    s2 = s.section([
        s.add_line(d, "So call 'er, dude. She's sure to wanna know your mind "
                      "on this, heh.", key='q05', vanilla_sid=0x1f63928c5442c000),
    ], tail_ms=600)
    out = s.end('talk_b_out')

    s.link(start, s1)
    s.link_section(s1, s2)
    s.link_section(s2, out)
    return s


def build_group3():
    s = Scene('gig02_group3', ANCHOR_AFTERLIFE)
    m = s.add_community_actor('merc', 'merc', CAST_COMMUNITY_REF)

    start = s.start('group3_in')
    s1 = s.section([
        # THE SUBTITLES FOLLOW THE RECORDING (the actor's delivery of
        # 2026-09-17): the brag opens on a laugh, "even" is in the punchline,
        # the begging opens on "No!" twice, and it is "her words" rather than
        # "her wording". "Pow!" is the actor's own addition after the shotgun
        # line, recorded as a take of its own and kept because it is the
        # brag's flourish.
        s.add_line(m, "Heh. They didn't even make it out of the car.", key='q07'),
        s.add_line(m, "Shotgun through the glass.", key='q08'),
        s.add_line(m, "Pow!", key='q08b'),
    ])
    s2 = s.section([
        # THE WORDS THAT IDENTIFY HIM: the brief names Jig-Jig Street.
        s.add_line(m, "Over before anyone on Jig-Jig Street could even scream.",
                   key='q09'),
    ], tail_ms=600)
    out = s.end('group3_out')

    s.link(start, s1)
    s.link_section(s1, s2)
    s.link_section(s2, out)
    return s


# ============================================ 4: on one knee, begging
#
# THE MERC BEAT IS A KILL ORDER NOW, 2026-09-03. The brief names Jig-Jig Street,
# his own boast names it too, and the objective is to take him out. There is
# no conversation first: V does not chat with a target. The talking happens
# because he is losing.
#
# At a third of his health the fight stops and this scene takes him: he goes
# down on one knee (a vanilla workspot, animated in and out by the workspot
# system, which is NOT the floor state that snapped upright when released),
# begs, hears who sent V, says who hired him, and hands over the proof. The
# reader opens on the shard from inside the scene, and the last thing the
# scene asks is what V does with him: finish it, or let him go.
# THE POSE, 2026-09-04: kneeling, leaning forward, afraid. Picked from the
# 1,394 workspot paths the base game's sectors reference (searched today);
# the kneel-and-inspect-the-ground pose it replaces read as a search, not a
# plea. The other candidates, if this one is wrong in play:
#   generic__kneel_ground__cry__01, generic__kneel_ground__cover__01,
#   generic__stand_ground__hands_up__03, generic__stand_ground__scared__01,
#   quest\main_quests\part1\q101\05_after_crash\takemura__kneel_ground__wounded__01
KNEEL = (chr(92).join(['base', 'workspots', 'common', 'ground',
                       'generic__kneel_ground_lean_front__afraid__01.workspot']))


def build_beaten():
    """The begging, on one knee, and the choice at the end of it.

    V's four words are his own recordings. The merc's are recorded by the actor. The
    fact `cc_g02_merc_talked` fires from an empty section AFTER his last line,
    so the reader the script raises on it does not open over his voice; the
    hub after it waits for [F], so the reader can sit on top of it. The choice
    sets `cc_g02_merc_fate` from inside the scene, 1 to kill and 2 to spare.
    """
    s = Scene('gig02_beaten', ANCHOR_AFTERLIFE)
    m = s.add_community_actor('merc', 'merc', CAST_COMMUNITY_REF)
    v = s.add_player()

    start = s.start('beaten_in')
    # He opens on a grunt: he has just been put on the floor, and the actor
    # recorded the hurt separately from the words. Subtitled the way the game
    # subtitles its own ("Agh!" is a vanilla line), since a scene line always
    # carries one.
    s1 = s.section([s.add_line(m, "Ugh!", key='m29'),
                    s.add_line(m, "No! Wait! Why?", key='m30')])
    s2 = s.section([s.add_line(v, "Wakako sent me.", key='v06',
                               vanilla_sid=0x196b41d47c386000)])
    s3 = s.section([s.add_line(m, "Wakako? She hired me!", key='m31')])
    # NOT "You're lying." (0x1192811a2a47a000): the female take says only
    # "Lying" under a subtitle that says both words, checked 2026-09-05. Both
    # bodies of this one say every word.
    s4 = s.section([s.add_line(v, "You're a shitty liar.", key='v07',
                               vanilla_sid=0x1b2b52f11862a000)])
    s5 = s.section([
        s.add_line(m, "No! I got the messages. Her tag, her words, the "
                      "transfer. Take it. Read it.", key='m32'),
        # The actor's addition, and the last thing he says before the choice.
        s.add_line(m, "Look for yourself.", key='m33'),
    ])
    # `merc_talked` fires here, after his line: the graph opens the objective
    # to take the shard off him. It is already in his pocket.
    s6 = s.section([], tail_ms=400)
    out = s.end('beaten_out')

    s.link(start, s1)
    for a, b in ((s1, s2), (s2, s3), (s3, s4), (s4, s5), (s5, s6)):
        s.link_section(a, b)
    s.link_section(s6, out)
    # ON ONE KNEE from the first word to the last. The workspot plays where he
    # already stands; the scene ending releases it, and the exit animation is
    # the workspot's own.
    # jump_to_entry=0 so the enter animation plays instead of the pose
    # starting on frame one, which is what read as a snap in play.
    # NO POSE FROM THE SCENE, 2026-09-05. He is on the floor already: the
    # script knocked him down with the game's own Defeated fall and holds him
    # there with Bleeding, which the pose lab found to be the one transition
    # that reads as a fall and a body still alive. The lines play over him.
    s.fire_event(s6, s.add_fact_node('cc_g02_merc_talked', 1), start_time=0)
    return s


def build_fate():
    """The choice, after the shard has been read: finish it, or let him go.

    Its own scene (2026-09-05) because the shard is taken and read between
    his last line and this, through the game's own loot list and reader, and
    a scene cannot wait on either. `cc_g02_merc_fate` is 1 to kill, 2 to spare.
    """
    s = Scene('gig02_fate', ANCHOR_AFTERLIFE)
    m = s.add_community_actor('merc', 'merc', CAST_COMMUNITY_REF)
    v = s.add_player()
    start = s.start('fate_in')
    c1 = s.choice([
        s.add_option("Finish it.", key='o20'),
        s.add_option("Let him go.", key='o21'),
    ])
    f1 = s.section([], tail_ms=300)
    # HE STAYS ON THE FLOOR. Letting him go is V not shooting, and one line
    # that says why he lives: keep quiet. His own recording, from a Watson
    # street story (2026-09-05).
    f2 = s.section([s.add_line(v, "Shut your trap if you don't wanna eat lead.",
                               key='v15', vanilla_sid=0x1a4880901d44d000)],
                   tail_ms=400)
    out = s.end('fate_out')
    s.link(start, c1)
    s.link_choice(c1, [f1, f2])
    s.link_section(f1, out)
    s.link_section(f2, out)
    s.fire_event(f1, s.add_fact_node('cc_g02_merc_fate', 1), start_time=0)
    s.fire_event(f2, s.add_fact_node('cc_g02_merc_fate', 2), start_time=0)
    return s


# ======================================= 7: after V has messaged the proof
def build_planned():
    """V has just sent Wakako the merc's messages and she has answered by
    text. Johnny's one line is the doubt the whole middle of the gig runs on."""
    s = Scene('gig02_planned', ANCHOR_PLAYER)
    j = s.add_johnny(offset=(1.0, 2.1, 0.0), yaw=yaw_to_face_player((1.0, 2.1, 0.0)))
    v = s.add_player()

    start = s.start('planned_in')
    # "She might not take you at your word." (0x1b3f57c94d44d000) went on
    # the playtest of 2026-09-05: with the plot as it is now, Wakako's word
    # is not in doubt. The replacement is about the forger, sarcastic
    # admiration for the nerve of using her name (design call, same day).
    s1 = s.section([s.add_line(j, "Can we find whoever did this? I need to "
                                  "shake their hand.",
                               key='j03', vanilla_sid=0x1a915ecb2a62a000)],
                   inner=True)
    # Not "Yeah." (0x185efbe0fb50203c) any more: the design call of
    # 2026-09-05 wanted V to tell him to shut up, and this is the closest
    # answer to a joke in V's recordings.
    s2 = s.section([s.add_line(v, "Fuck off, Johnny. Not even close to funny, "
                                  "that.", key='v17',
                               vanilla_sid=0x30b61db1af46a000)], tail_ms=900)
    out = s.end('planned_out')

    s.link(start, s1)
    s.link_section(s1, s2)
    s.link_section(s2, out)
    s.stage_johnny(s1, s2)
    return s


# ====================================================== 8: the Dewdrop Inn
def build_inn():
    """Yoko, in her own recordings. She is the Kabuki netrunner vendor's
    voice, and two of her Phantom Liberty lines are exactly this doorstep:
    somebody was sent by a mutual acquaintance, and the formalities are done.
    """
    s = Scene('gig02_inn', ANCHOR_INN)
    # OUR OWN YOKO (2026-09-05), from our community, like the merc. The
    # vanilla vendor body is off for the leg; see gen_community.
    y = s.add_community_actor('yoko', 'yoko', CAST_COMMUNITY_REF)
    v = s.add_player()

    start = s.start('inn_in')
    # NO HUB OF OURS (playtest 2026-09-05, screenshot: her three vendor lines
    # and our "Yoko." in one list). Her vendor scene offers its hub to anyone
    # in reach and the game merges hubs on one actor, and her scene has no
    # switch: it is gated on distance and on facts of other quests only, read
    # off wat_kab_netrunner_01.scene. So she speaks first, the moment V is at
    # her counter, the way the game's own vendors greet, and there is nothing
    # of ours for her hub to merge with.
    # A STRANGER'S GREETING (design call 2026-09-05: she must not know V).
    # Her own vendor greeting, and the "mutual acquaintance" line after V's
    # answer is what tells the player Wakako warned her.
    # SHE KNOWS WHO IS AT HER COUNTER (design call 2026-09-05: a stranger's
    # greeting read wrong for somebody Wakako sent ahead), and the
    # confirmation is a beat, not a sentence: her own biometric-scan exchange
    # from the game, with V's "Connect." as the one press in it and her
    # "It will only take a moment." as the wait.
    s1 = s.section([s.add_line(y, "You're V, right?", key='y01',
                               vanilla_sid=0x1e102c550e649000)])
    s2 = s.section([s.add_line(v, "Wakako sent me.", key='v18',
                               vanilla_sid=0x1ab9a78d612c5000)])
    s3 = s.section([s.add_line(y, "First, I'll need confirmation our mutual "
                                  "acquaintance, in fact, sent you. Then we "
                                  "can talk.", key='y02',
                               vanilla_sid=0x2cb52d3ae37df000),
                    s.add_line(y, "Connect here? I'll verify through "
                                  "biometric scan.", key='y04',
                               vanilla_sid=0x2cb52d3ae47df000)])
    c1 = s.choice([s.add_option("Connect.", key='o05')])
    s4 = s.section([s.add_line(y, "It will only take a moment.", key='y05',
                               vanilla_sid=0x2cb52d46d37df03c)], tail_ms=2500)
    s5 = s.section([s.add_line(y, "Small things that help netrunners sleep "
                                  "at night. There – authorization "
                                  "confirmed.", key='y06',
                               vanilla_sid=0x2cb52d46d47df020),
                    s.add_line(y, "Right, with the formalities done, let's "
                                  "begin.", key='y03',
                               vanilla_sid=0x2cb52d3cec7df014)], tail_ms=500)
    out = s.end('inn_out')

    s.link(start, s1)
    s.link_section(s1, s2)
    s.link_section(s2, s3)
    s.link_section(s3, c1)
    s.link_choice(c1, [s4])
    s.link_section(s4, s5)
    s.link_section(s5, out)
    face_player(s, y)
    return s


# ================================================= 8b: handing Char the shard
def build_handover():
    """Char takes it and says how long she needs. The verdict itself arrives
    as her text message half an hour later; there is no second visit."""
    s = Scene('gig02_handover', ANCHOR_INN)
    c = s.add_community_actor('char', 'char', CAST_COMMUNITY_REF)
    v = s.add_player()

    start = s.start('handover_in')
    c1 = s.choice([s.add_option("Hand it over.", key='o04')])
    s1 = s.section([s.add_line(v, "Here.", key='v19',
                               vanilla_sid=0x1a96bf839e386000)])
    s2 = s.section([
        # THE SUBTITLES FOLLOW THE RECORDING (delivery of 2026-09-06): the
        # noise as she takes it is the word "Nova.", and the call opens with
        # "Good," and puts the box "at the back". Both were checked against
        # the audio.
        s.add_line(c, "Nova.", key='c01'),
        s.add_line(c, "Give me half an hour. I'll message you.", key='c02'),
    ], tail_ms=500)
    out = s.end('handover_out')

    s.link(start, c1)
    s.link_choice(c1, [s1])
    s.link_section(s1, s2)
    s.link_section(s2, out)
    face_player(s, c)
    return s


# ======================================================= 10: the Char call
def build_char_call():
    """Char rings V on the parlor floor and says what to do: breach the box.

    THIS IS THE PARLOR'S ANSWER TO "THERE IS NOTHING TO LOOK FOR", and it is
    the same device the base game uses: the specialist on comms tells the
    hero what the room means. Char is invented, so she can say it plainly.

    VIDEO, 2026-09-05 (design call), and the body on the phone is the same
    woman as the one in the chair: the same record, the same pinned
    appearance, on the studio floor spot the way Wakako's calls do it.
    """
    s = Scene('gig02_char_call', ANCHOR_STUDIO)
    c = s.add_actor('char', R_CHAR, offset=STUDIO_OFFSET, yaw=STUDIO_YAW,
                    force_visible=True, appearance=APPEARANCE['char'])
    v = s.add_player()

    start = s.start('char_call_in')
    s1 = s.section([
        s.add_line(c, "Good, you're in. There's a hardline access point on "
                      "the wall at the back. Whatever sent those orders went "
                      "through it.", key='c09'),
        s.add_line(c, "Jack in, breach it, and send me everything it's "
                      "been carrying.", key='c10'),
    ], holocall=True)
    s2 = s.section([s.add_line(v, "Got it.", key='v20',
                               vanilla_sid=0x17ca7fae394d100c)], tail_ms=400)
    out = s.end('char_call_out')

    s.link(start, s1)
    s.link_section(s1, s2)
    s.link_section(s2, out)
    studio_pose(s, 'char', c, s1, pose=CHAR_POSE)
    return s


# ================================================ 12: Wakako, in the room
def build_office():
    """The kill order, in her own lines.

    HER BODY IS OURS, acquired from the cast community (2026-09-05): the
    game's own Wakako is switched off for the leg, so there is no hub of hers
    to merge with ours. REWRITTEN THE SAME EVENING on the design review: she
    expects V, so she greets him by name and asks for the news; her disbelief
    and "He would not dare go against me." are one take of hers cut after
    its second sentence; the order is her own "You eliminate the target, you
    get your pay."; and V closes with "Leave it to me." The example-or-
    understood choice was moot and is gone. Two lines are cuts (w47, w41);
    the rest are whole takes.
    """
    s = Scene('gig02_office', ANCHOR_OFFICE)
    w = s.add_community_actor('wakako', 'wakako', CAST_COMMUNITY_REF)
    v = s.add_player()

    start = s.start('office_in')
    hub = s.choice([s.add_option('Share what you found with Wakako.', key='o12')])
    s1 = s.section([
        s.add_line(w, "V, so nice to see you.", key='w05',
                   vanilla_sid=0x1a6c563aba404000),
        s.add_line(w, "So tell me.", key='w47'),
    ])
    c1 = s.choice([s.add_option("Show her Char's trace.", key='o06')])
    s2 = s.section([
        s.add_line(w, "Something must have happened. He would not dare go "
                      "against me.", key='w41'),
        s.add_line(w, "I don't forget such things, V.", key='w07',
                   vanilla_sid=0x1a6d6c5497404000),
    ])
    s3 = s.section([
        s.add_line(w, "You eliminate the target, you get your pay. I pay "
                      "for results.", key='w48',
                   vanilla_sid=0x1ad3bd0d8d588004),
        # "Everything's on the shards." (0x1b73b4f367404000) went on the
        # playtest of 2026-09-05: nothing is on a shard any more. She has
        # sent the details (a whole take), and she wants it discreet (a cut).
        s.add_line(w, "I have shared the details.", key='w49',
                   vanilla_sid=0x208454e962559000),
        s.add_line(w, "Discreet and with finesse.", key='w50'),
        s.add_line(w, "Then go, be on your way.", key='w10',
                   vanilla_sid=0x1a6c5a07a2404000),
    ])
    s4 = s.section([s.add_line(v, "Leave it to me.", key='v23',
                               vanilla_sid=0x2deb55714d46a000)], tail_ms=900)
    out = s.end('office_out')

    s.link(start, hub)
    s.link_choice(hub, [s1])
    s.link_section(s1, c1)
    s.link_choice(c1, [s2])
    s.link_section(s2, s3)
    s.link_section(s3, s4)
    s.link_section(s4, out)
    face_player(s, w)
    return s


# ============================================================= 14: the kill
# ================================================== 15: the two closing calls
def build_close_clean():
    """Nobody saw. "You entered and left like a ghost, V." is her own line,
    cut at the pause before it goes on about a shrine."""
    s = Scene('gig02_close_clean', ANCHOR_STUDIO)
    w = wakako_studio(s)
    v = s.add_player()

    start = s.start('close_clean_in')
    s1 = s.section([s.add_line(v, "Job's done.", key='v27',
                               vanilla_sid=0x19127c94124e6004)])
    s2 = s.section([s.add_line(w, "You entered and left like a ghost, V.",
                               key='w42')], holocall=True)
    s3 = s.section([s.add_line(w, "Excellent work, V. May it remain so. I am "
                                  "closing the contract and transferring your "
                                  "fee.", key='w11',
                               vanilla_sid=0x208461122f559000)],
                   holocall=True, tail_ms=800)
    out = s.end('close_clean_out')

    s.link(start, s1)
    s.link_section(s1, s2)
    s.link_section(s2, s3)
    s.link_section(s3, out)
    studio_pose(s, 'wakako', w, s1)
    return s


def build_close_loud():
    """Seen, or the street wiped. Paid, and told what it cost."""
    s = Scene('gig02_close_loud', ANCHOR_STUDIO)
    w = wakako_studio(s)
    v = s.add_player()

    start = s.start('close_loud_in')
    s1 = s.section([s.add_line(v, "Job's done.", key='v28',
                               vanilla_sid=0x19127c94124e6004)])
    s2 = s.section([s.add_line(w, "You were to do this quietly. It was "
                                  "anything but.", key='w43')], holocall=True)
    s3 = s.section([
        s.add_line(w, "Your payment will reflect your carelessness. I am "
                      "closing the contract.", key='w12',
                   vanilla_sid=0x2084496fae559000),
        s.add_line(w, "Next time, think before you act – otherwise you "
                      "gamble with my temper. It is a losing game. Talk soon, "
                      "V.", key='w13', vanilla_sid=0x2084119f6c559000),
    ], holocall=True, tail_ms=800)
    out = s.end('close_loud_out')

    s.link(start, s1)
    s.link_section(s1, s2)
    s.link_section(s2, s3)
    s.link_section(s3, out)
    studio_pose(s, 'wakako', w, s1)
    return s


# ============================================================== 16: the end
def build_end():
    s = Scene('gig02_end', ANCHOR_PLAYER)
    j = s.add_johnny(offset=(1.0, 2.1, 0.0), yaw=yaw_to_face_player((1.0, 2.1, 0.0)))
    v = s.add_player()

    start = s.start('end_in')
    s1 = s.section([s.add_line(j, "Easy enough in Night City. Real trick's "
                                  "survivin' long enough to spend it.",
                               key='j13', vanilla_sid=0x1a243da8e044d000)],
                   inner=True)
    s2 = s.section([s.add_line(v, "Yeah.", key='v29',
                               vanilla_sid=0x185efbe0fb50203c)], tail_ms=1200)
    out = s.end('end_out')

    s.link(start, s1)
    s.link_section(s1, s2)
    s.link_section(s2, out)
    # His glitch-out sits on V's answer, not on his own line (playtest
    # 2026-09-06: he glitched after speaking, then vanished when V finished).
    s.stage_johnny(s1, s2)
    return s


# ========================================================= 16b: the loud end
def build_end_loud():
    """Johnny's last word when V was seen (design call 2026-09-06): the quiet
    ending's line about spending the money makes sense only for a clean job;
    a loud one gets his verdict on it."""
    s = Scene('gig02_end_loud', ANCHOR_PLAYER)
    j = s.add_johnny(offset=(1.0, 2.1, 0.0), yaw=yaw_to_face_player((1.0, 2.1, 0.0)))
    v = s.add_player()

    start = s.start('end_loud_in')
    s1 = s.section([s.add_line(j, "What a fuckin' mess.", key='j14',
                               vanilla_sid=0x43dd77c74c3e7000)],
                   inner=True)
    s2 = s.section([s.add_line(v, "Yeah.", key='v30',
                               vanilla_sid=0x185efbe0fb50203c)], tail_ms=1200)
    out = s.end('end_loud_out')

    s.link(start, s1)
    s.link_section(s1, s2)
    s.link_section(s2, out)
    # His glitch-out sits on V's answer, not on his own line (playtest
    # 2026-09-06: he glitched after speaking, then vanished when V finished).
    s.stage_johnny(s1, s2)
    return s


# ==================================================== 17-18: the two waits
#
# THE SHAPE IS THE CLAIRE RACES', and both halves of it are theirs. Four legs
# of `sq024` carry an objective the game names `wait_for_claire`, pinned at a
# place to take: two of them a sit, two of them a lean. The player walks to the
# pin, presses, and the beat moves.
#
# THE WORDING IS THE GAME'S OWN, and it is not "Sit down". Vanilla writes
# this beat out in full every time it uses it: "Sit on the bench and wait
# for Claire.", "Sit on the couch and wait for Claire.", "Lean against the
# wall and wait for Claire.", "Lean on the barrier and wait for Takemura.",
# "Sit and wait for River.". The place and the reason both go in the line,
# so a player reading the prompt knows what pressing it commits him to.
#
# NEITHER SCENE HAS A LINE IN IT, and that is the point rather than an
# omission. V says nothing while he waits, the same way he says nothing on
# Claire's rail. What each one carries is a prompt, a pose and a hold.
#
# HOW THE HOLD WORKS, because a scene cannot run for half an in-game hour:
#
#   1. the choice hub offers the prompt AT THE MARKER, which is what
#      `in_world=True` buys: the default hub attaches to the screen and, in
#      a scene whose only actor is the player, follows him around the city
#      (playtest 2026-09-08, the prompt was up at the Inn)
#      THE RANGE HAS TO REACH THE POSE, NOT JUST THE PROMPT. Playtest
#      2026-09-08: at 1.2 m it appeared on the way in and then vanished as
#      V got to the railing, because the pose is 1.43 m past the marker and
#      he was walking out the far side of the circle. 2.5 m covers the walk
#      up and the spot itself, and the yaw limit is off because a man at a
#      railing is facing the view rather than the marker behind his heels.
#   2. the section fires the pose onto V and sets `cc_g02_*_taken`
#   3. Gig02_Encounter sees that fact, moves the world clock on by what is
#      left of the wait, and sets `cc_g02_*_release`
#   4. the scene has been holding on that fact; it ends, and V stands up
#
# THE POSE IS FIRED ON THE EVENTS SOCKET, which is fire and forget. If it
# never lands, V stands at the railing for a moment and everything else still
# happens; the alternative wiring stalls the scene, and a scene that never
# reaches its exit is a quest phase that waits on that exit for the rest of
# the playthrough.
def build_lean():
    """The railing outside Yoko's stall, while Char runs the trace."""
    s = Scene('gig02_lean', gen_community.LEAN_MARKER_REF)
    s.add_player()

    start = s.start('lean_in')
    c1 = s.choice([s.add_option("Lean on the railing and wait for Char.", key='o10')],
                  in_world=True, radius=2.5, yaw_limit=360)
    s1 = s.section([], tail_ms=1200)
    taken = s.add_fact_node('cc_g02_lean_taken', 1)
    release = s.add_wait_fact_node('cc_g02_lean_release')
    out = s.end('lean_out')

    s.link(start, c1)
    s.link_choice(c1, [s1])
    s.link_section_quest(s1, taken)
    # AFTER the section is linked: sockets are written in (name, ordinal)
    # order and validate() enforces it.
    s.fire_workspot(s1, s.add_world_workspot_node(
        None, gen_community.LEAN_SPOT_REF, player=True), start_time=0)
    s.link_quest(taken, release)
    s.link(release, out)
    return s


def build_sit():
    """The chair outside the parlor, while Char reads the relay dump."""
    s = Scene('gig02_sit', gen_community.SIT_MARKER_REF)
    s.add_player()

    start = s.start('sit_in')
    c1 = s.choice([s.add_option("Sit down and wait for Char.", key='o11')], in_world=True,
                  radius=2.5, yaw_limit=360)
    s1 = s.section([], tail_ms=1200)
    taken = s.add_fact_node('cc_g02_sit_taken', 1)
    release = s.add_wait_fact_node('cc_g02_sit_release')
    out = s.end('sit_out')

    s.link(start, c1)
    s.link_choice(c1, [s1])
    s.link_section_quest(s1, taken)
    s.fire_workspot(s1, s.add_world_workspot_node(
        None, gen_community.SIT_SPOT_REF, player=True), start_time=0)
    s.link_quest(taken, release)
    s.link(release, out)
    return s


ALL_BUILDERS = (
    build_wakako_call, build_johnny_open,
    build_talk_a, build_talk_b, build_group3,
    build_beaten, build_fate,
    build_planned,
    build_inn, build_handover,
    build_char_call,
    build_office,
    build_close_clean, build_close_loud, build_end, build_end_loud,
    build_lean, build_sit,
    # DEV. Reached only by the CET menu's appearance A/B arm, never by the gig.
    # It ships because the quest phase names it and a phase naming a scene that
    # is not there is a graph that stops at that node.
)


if __name__ == '__main__':
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(RAW_MOD, 'localization'), exist_ok=True)
    built = [build() for build in ALL_BUILDERS]
    for scene in built:
        scene.write()
    write_subtitles(built)
    write_lipmap(built)
